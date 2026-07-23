# How to decode a Spot GraphNav autowalk and stitch the waypoint clouds

This documents the exact procedure used to decode `lt6 inspection.walk` and reconstruct
the global point cloud in `map_overview.png`. Everything here is reproducible with the
Spot SDK; nothing is proprietary tooling.

The one idea to hold onto: **each waypoint stores a small local cloud in a *sensor* frame.
To place it in the global map you chain three transforms — `seed ← waypoint ← ko(odom) ← sensor`.**
`ko` is BD's kinematic-odometry frame and equals `odom`. Get that chain right and stitching is trivial.

A single runnable script (`decode_and_stitch.py`) is included at the end; the sections below
are that script broken into the steps I actually ran, with the reasoning.

---

## 0. Environment

```bash
pip install bosdyn-api bosdyn-client protobuf numpy matplotlib
python3 -c "import bosdyn.api; print('bosdyn', __import__('bosdyn.api').api.__name__)"
```

I used `bosdyn-api` / `bosdyn-client` **5.1.4** on Python 3.12. The protobuf backend is `upb`,
which matters for one gotcha (see §7).

An autowalk is just a **directory of raw serialized protobufs** — no framing, no header, each
file is one `message.SerializeToString()`. The extension tells you the type:

| Path | Protobuf type | Module |
|---|---|---|
| `graph` | `Graph` | `bosdyn.api.graph_nav.map_pb2` |
| `waypoint_snapshots/snapshot_*` | `WaypointSnapshot` | `bosdyn.api.graph_nav.map_pb2` |
| `edge_snapshots/edge_snapshot_id_*` | `EdgeSnapshot` | `bosdyn.api.graph_nav.map_pb2` |
| `missions/*.walk` | `Walk` | `bosdyn.api.autowalk.walks_pb2` |
| `autowalk_metadata` | small params proto | (wire-scanned) |

```bash
unzip -l lt6_inspection_walk.zip | head          # inspect, don't auto-extract huge archives
unzip -q lt6_inspection_walk.zip -d .            # then extract
```

---

## 1. Decode the graph (the topological map)

The `graph` file holds the pose graph: `waypoints`, `edges`, and `anchoring` (the global frame).

```python
from bosdyn.api.graph_nav import map_pb2

g = map_pb2.Graph()
with open("lt6 inspection.walk/graph", "rb") as f:
    g.ParseFromString(f.read())

print(len(g.waypoints), "waypoints")          # 77
print(len(g.edges), "edges")                   # 76
print(len(g.anchoring.anchors), "anchors")     # 77  (waypoint pose in the seed frame)
print(len(g.anchoring.objects), "objects")     # 4   (fiducials in the seed frame)
```

Two fields on each **waypoint** matter for stitching:

- `waypoint.snapshot_id` — a string that is **literally the filename** of the perception
  snapshot in `waypoint_snapshots/`. This is the join key between the graph and the payload.
- `waypoint.waypoint_tform_ko` — an `SE3Pose`: the waypoint frame expressed relative to `ko`
  (kinematic odometry = `odom`) at record time. This is transform #2 in the chain.

Absolute positions live **only** in `anchoring`, never in `waypoints` (GraphNav is relative-pose
SLAM — the graph stores relative edge transforms and the anchoring is a derived global solution):

```python
for a in g.anchoring.anchors[:2]:
    p = a.seed_tform_waypoint.position      # waypoint pose in the global "seed" frame
    print(a.id[:20], p.x, p.y, p.z)
```

---

## 2. Decode one waypoint snapshot (the perception payload)

```python
import os, glob
snaps = sorted(glob.glob("lt6 inspection.walk/waypoint_snapshots/snapshot_*"),
               key=os.path.getsize, reverse=True)

s = map_pb2.WaypointSnapshot()
with open(snaps[0], "rb") as f:
    s.ParseFromString(f.read())

for fld, val in s.ListFields():             # list only populated fields
    try:    print(fld.name, "len", len(val))
    except TypeError: print(fld.name, "(message)")
# images(10) point_cloud objects(1) robot_state robot_local_grids(5) payloads(5) robot_id id ...
```

### 2a. Point cloud → XYZ

`encoding == ENCODING_XYZ_32F` means the payload is tightly packed little-endian float32,
3 per point (12 bytes/point). Decode is one line:

```python
import numpy as np
pc  = s.point_cloud
pts = np.frombuffer(pc.data, np.float32).reshape(-1, 3)   # (N, 3) in the sensor frame
print(pc.source.frame_name_sensor)                         # "sensor_origin_generated"
```

The frame name (`sensor_origin_generated`) and the transform tree you need live in
`pc.source.transforms_snapshot` — that is transform #3 in the chain.

### 2b. Local grids → cost maps (fixed-point decode)

Five 128×128 @ 3 cm grids. Universal decode is `raw * cell_value_scale + cell_value_offset`,
reshaped row-major; `terrain_valid` (uint8) is the mask:

```python
from bosdyn.api import local_grid_pb2
def decode_grid(lg):
    dt = {5: np.int16, 4: np.uint8, 1: np.float32}[lg.cell_format]   # 5=INT16 4=UINT8 1=F32
    nx, ny = lg.extent.num_cells_x, lg.extent.num_cells_y
    raw = np.frombuffer(lg.data, dt).reshape(ny, nx).astype(np.float32)
    return raw * lg.cell_value_scale + lg.cell_value_offset

grids = {lg.local_grid_type_name: lg for lg in s.robot_local_grids}
terrain = decode_grid(grids["terrain"])            # height map (m)
sdf     = decode_grid(grids["obstacle_distance"])  # signed distance field: >0 free, <0 inside
valid   = np.frombuffer(grids["terrain_valid"].data, np.uint8).reshape(terrain.shape)
terrain = np.where(valid > 0, terrain, np.nan)
```

### 2c. Images (raw, not JPEG)

```python
for im in s.images:
    img = im.shot.image
    print(im.source.name, img.cols, img.rows, img.format, img.pixel_format)
# *_fisheye_image 640x480 FORMAT_RAW GREYSCALE_U8 ;  *_depth 424x240 FORMAT_RAW DEPTH_U16
gray  = np.frombuffer(img.data, np.uint8).reshape(img.rows, img.cols)          # fisheye
depth = np.frombuffer(img.data, np.uint16).reshape(img.rows, img.cols).astype(float)
depth[depth == 0] = np.nan; depth *= 0.001                                     # mm → m
```

(The two front fisheyes are physically mounted rotated ~90°; raw frames look tilted — see §7.)

---

## 3. The frame math (the crux of stitching)

I need each point in the global **seed** frame. The chain, per waypoint:

```
seed_tform_cloud = seed_tform_waypoint      # from graph.anchoring
                 · waypoint_tform_ko        # from graph.waypoints  (ko == odom)
                 · ko_tform_cloud           # from the snapshot's own transform tree
```

Use the SDK's `get_a_tform_b` to walk the snapshot's transform tree (it handles inversions and
multi-hop paths so you never touch quaternion math by hand), and `SE3Pose` for composition:

```python
from bosdyn.client.math_helpers import SE3Pose
from bosdyn.client.frame_helpers import get_a_tform_b, ODOM_FRAME_NAME

ko_tform_cloud   = get_a_tform_b(pc.source.transforms_snapshot,
                                 ODOM_FRAME_NAME, pc.source.frame_name_sensor)
wp_tform_ko      = SE3Pose.from_proto(waypoint.waypoint_tform_ko)
seed_tform_wp    = SE3Pose.from_proto(anchor.seed_tform_waypoint)   # anchor for this waypoint id
seed_tform_cloud = seed_tform_wp * wp_tform_ko * ko_tform_cloud

M = seed_tform_cloud.to_matrix()                       # 4x4 homogeneous
world = (M @ np.c_[pts, np.ones(len(pts))].T).T[:, :3] # (N,3) in the seed frame
```

**Why `ko == odom`:** `waypoint_tform_ko` names the "kinematic odometry" frame, and the snapshot's
transform tree exposes that same frame as `odom`. Empirically it's the only reading under which
77 independent local clouds line up into a continuous corridor — the reconstruction *is* the proof
the identity is correct.

---

## 4. The stitch loop

Build a `{waypoint_id: seed_tform_waypoint}` map from the anchoring, then iterate the waypoints,
join to the snapshot by `snapshot_id`, transform, and accumulate. I subsample each cloud
(≤3000 pts) so the merged array stays a few hundred k points instead of ~940 k:

```python
seed_tform_wp = {a.id: SE3Pose.from_proto(a.seed_tform_waypoint) for a in g.anchoring.anchors}
rng = np.random.default_rng(0)
all_pts = []

for w in g.waypoints:
    snap_path = f"lt6 inspection.walk/waypoint_snapshots/{w.snapshot_id}"
    if not os.path.exists(snap_path) or w.id not in seed_tform_wp:
        continue
    s = map_pb2.WaypointSnapshot(); s.ParseFromString(open(snap_path, "rb").read())
    pc = s.point_cloud
    if pc.num_points == 0:
        continue

    pts = np.frombuffer(pc.data, np.float32).reshape(-1, 3).astype(np.float64)
    ko_tform_cloud = get_a_tform_b(pc.source.transforms_snapshot,
                                   ODOM_FRAME_NAME, pc.source.frame_name_sensor)
    seed_tform_cloud = seed_tform_wp[w.id] * SE3Pose.from_proto(w.waypoint_tform_ko) * ko_tform_cloud

    M = seed_tform_cloud.to_matrix()
    world = (M @ np.c_[pts, np.ones(len(pts))].T).T[:, :3]
    if len(world) > 3000:
        world = world[rng.choice(len(world), 3000, replace=False)]
    all_pts.append(world)

P = np.vstack(all_pts)      # (225759, 3) in the seed frame
```

Real traversed length is the **sum of edge lengths**, not the sum over the anchor array (the anchors
aren't in traversal order — summing them naively gives a nonsense ~1.5 km; the edge sum gives 99.4 m):

```python
wp_pos = {a.id: np.array([a.seed_tform_waypoint.position.x,
                          a.seed_tform_waypoint.position.y,
                          a.seed_tform_waypoint.position.z]) for a in g.anchoring.anchors}
path_len = sum(np.linalg.norm(wp_pos[e.id.to_waypoint] - wp_pos[e.id.from_waypoint])
               for e in g.edges if e.id.from_waypoint in wp_pos and e.id.to_waypoint in wp_pos)
```

---

## 5. Render

Top-down scatter coloured by height, with the edge graph and fiducials overlaid, plus a side
elevation. Sort points by `z` so higher points draw last (readable overlap):

```python
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

wp_xy = {a.id: (a.seed_tform_waypoint.position.x, a.seed_tform_waypoint.position.y)
         for a in g.anchoring.anchors}
segs = [[wp_xy[e.id.from_waypoint], wp_xy[e.id.to_waypoint]] for e in g.edges
        if e.id.from_waypoint in wp_xy and e.id.to_waypoint in wp_xy]

fig, ax = plt.subplots(figsize=(16, 7))
order = np.argsort(P[:, 2])
ax.scatter(P[order, 0], P[order, 1], c=P[order, 2], s=0.6, cmap="turbo", alpha=0.75, linewidths=0)
ax.add_collection(LineCollection(segs, colors="#00e5ff", linewidths=1.6))
ax.set_aspect("equal"); plt.savefig("map_overview.png", dpi=130, bbox_inches="tight")
```

The grids (`grids.png`) and camera ring (`cameras.png`) were rendered the same way from the
decodes in §2b/§2c — `imshow` the decoded grid arrays and the greyscale/depth image arrays.

---

## 6. Run it

The included `decode_and_stitch.py` is §1–§5 wrapped into one script:

```bash
python3 decode_and_stitch.py "lt6 inspection.walk"
# stitched 77 waypoints (skipped 0); 225,759 points
# path length (edge sum): 99.4 m over 76 edges
# wrote map_overview.png
```

It writes `merged_points.npy` (the stitched cloud), `wp_seed.npy`, `fiducials.npy`, and
`map_overview.png`. Load the cloud into any viewer, e.g. Open3D:

```python
import numpy as np, open3d as o3d
pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(np.load("merged_points.npy")))
o3d.visualization.draw_geometries([pc])
```

---

## 7. Gotchas that cost time (so you don't repeat them)

1. **`PointCloud` is not in `map_pb2`.** The `WaypointSnapshot.point_cloud` field's type lives in
   `bosdyn.api.point_cloud_pb2`; the enum names come from there, not `map_pb2`. (`local_grid`
   enums are in `bosdyn.api.local_grid_pb2` likewise.)
2. **The `upb` protobuf backend has no `FieldDescriptor.label`.** To list populated fields use
   `msg.ListFields()` (returns only set fields) instead of iterating `DESCRIPTOR.fields` and
   checking `.label == LABEL_REPEATED`.
3. **`HasField` throws on no-presence fields.** `proto3` scalars without explicit presence
   (e.g. `Walk.mission_name`) raise `ValueError` on `HasField` — just read the value directly.
4. **`FootState.foot_position_rt_body` is a bare `Vec3`, not an `SE3Pose`** — there's no `.position`.
   (The stance body pose `ko_tform_body` *is* an `SE3Pose`.) Field name is `foot_position_rt_body`,
   not `..._rt_load_leg`.
5. **Anchors are not in traversal order.** Summing distances across the anchor array to get "path
   length" is wrong — sum edge lengths (§4).
6. **Front fisheyes are mounted rotated ~90°.** Raw frames look tilted; apply the per-camera image
   rotation before display if you care about orientation. Depth is also very sparse outdoors
   (6–43 % valid pixels here) — expect holes.
7. **The cloud is downsampled and fused, not raw depth.** ~12 k points/waypoint already merged
   across all 5 cameras into `sensor_origin_generated`; don't expect per-camera clouds.
8. **`autowalk_metadata` has no public message class handy** — I wire-scanned it (varint/len-delim
   walk) rather than binding a type; it's just session timestamps + a few record params, not needed
   for stitching.
