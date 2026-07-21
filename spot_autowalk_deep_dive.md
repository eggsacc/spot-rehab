# Anatomy of a Spot GraphNav Autowalk — Low-Level Deep Dive

Decoded from `lt6 inspection.walk` (Boston Dynamics Spot, `bosdyn-api` 5.1.4).
Focus: how Spot stores perception + odometry and turns it into a re-traversable, globally-consistent map.

---

## 0. Provenance (what this recording actually is)

| Field | Value | Source |
|---|---|---|
| Robot nickname | `SPOT67` | `robot_id.nickname` |
| Serial | `spot-BD-20660007` | `robot_id.serial_number` |
| Platform | Spot **V3**, species `spot` | `robot_id` |
| Robot software | 5.1 | `robot_id.software_release` |
| Recorded from | Tablet app "Spot 5.1.9", `client_type: Tablet` | waypoint `annotations.client_metadata` |
| Session | `lt6 inspection` | mission + waypoint metadata |
| Waypoints / edges | **77 / 76** (a single open chain — no loop closures) | `graph` |
| Fiducials anchored | 4 (AprilTags 2, 3, 4, 5) | `anchoring.objects` |
| Perimeter walked | **≈ 99.4 m** (sum of edge lengths) | edges in seed frame |
| Site footprint | ≈ 70 m (x) × 34 m (y), ≈ 7 m vertical spread | anchoring bbox |
| Recording duration | ≈ 4.9 min | point-cloud acquisition timestamps |
| On-disk size | 13.7 MB zip → ~28.5 MB expanded (waypoint snapshots dominate) | filesystem |

The camera imagery shows a **covered outdoor campus walkway** (tiled floor, columns, trees, a fire-hosereel cabinet, pedestrians) — an inspection loop, not a lab. "lt6" reads as a building/lecture-theatre tag.

> **Note on 4 fiducials but no loop closures:** the graph is a linear chain, yet it renders as a globally consistent site. That consistency comes from the *anchoring optimisation* (§6), not from graph loop closures — the AprilTags are the global glue.

---

## 1. Container format

An autowalk is a plain directory (zipped for transport). Every file with no "readable" extension is a **serialized protobuf** — no framing, no header, just `message.SerializeToString()` bytes.

```
lt6 inspection.walk/
├── graph                         # bosdyn.api.graph_nav.Graph          (the topological map)
├── autowalk_metadata             # session timestamps + record params  (small proto)
├── waypoint_snapshots/
│   └── snapshot_<hash>           # bosdyn.api.graph_nav.WaypointSnapshot  ×77  (perception)
├── edge_snapshots/
│   └── edge_snapshot_id_<hash>   # bosdyn.api.graph_nav.EdgeSnapshot      ×76  (foot-falls)
├── missions/
│   ├── lt6 inspection.walk       # bosdyn.api.autowalk.Walk            (newer format)
│   ├── lt6 inspectio.walk        # truncated-name duplicate
│   └── readme.txt                # BD's own note on mission formats
└── topography.png                # a top-down thumbnail render
```

`readme.txt` (verbatim intent): extensionless mission files = old `bosdyn.api.mission.Node`; `.walk` = newer `bosdyn.api.autowalk.Walk` (must be expanded to `Node`s by the *autowalk service* before the mission service runs them); `.node` files stopped being saved as of software 3.3. Load precedence on the tablet: `.walk` → `.node` → extensionless.

### Decoding recipe (drop-in for the repo)

```python
from bosdyn.api.graph_nav import map_pb2
from bosdyn.api.autowalk  import walks_pb2

g = map_pb2.Graph();            g.ParseFromString(open("graph","rb").read())
w = walks_pb2.Walk();           w.ParseFromString(open("missions/lt6 inspection.walk","rb").read())
s = map_pb2.WaypointSnapshot(); s.ParseFromString(open("waypoint_snapshots/snapshot_...","rb").read())
e = map_pb2.EdgeSnapshot();     e.ParseFromString(open("edge_snapshots/edge_snapshot_id_...","rb").read())
```

The snapshot IDs in `graph` are exactly the filenames in the two `*_snapshots/` folders — that's the join key. The IDs are base64-with-`+/=` of an internal hash; nothing to decode, just match strings.

---

## 2. The GraphNav data model (topology, not a global grid)

The core insight: **Spot does not store one big global map.** It stores a *pose graph* of small, locally-accurate submaps. Global metric consistency is derived on demand.

### 2.1 Waypoint — a node in the pose graph

```
Waypoint {
  id                 : "chaffy-mouse-Ys9bBS6c..."       # stable node id
  snapshot_id        : "snapshot_tardy-koala-..."       # → the perception payload
  waypoint_tform_ko  : SE3Pose                           # waypoint frame ← "ko" (kinematic odometry = odom)
  annotations {
    name             : "waypoint_42"
    icp_variance     : {yaw_variance, cov_xx..cov_zz}    # 3×3 position covariance + yaw var
    scan_match_region: {empty|circle|...}                # where ICP is allowed to match
    creation_time, client_metadata, loop_closure_settings
  }
}
```

Two things worth dwelling on:

- **`waypoint_tform_ko`** — `ko` is BD's *kinematic odometry* frame, i.e. the `odom` frame at the instant the waypoint was dropped. This single stored transform is the hinge that lets you place the waypoint's snapshot (which is expressed in `odom`) into the waypoint's own frame. (Verified: my reconstruction only lines up if `ko ≡ odom`.)
- **`icp_variance`** — a full 3×3 translational covariance plus a yaw variance, in units of m² / rad². Example from `waypoint_42`:

  ```
  cov_xx=7.1e-6  cov_xy=-4.5e-6  cov_xz=-6.1e-6
  cov_yy=2.1e-5  cov_yz=1.7e-5   cov_zz=1.7e-5   yaw_var=2.4e-6
  ```

  This is the *localisation confidence* of ICP scan-matching against this waypoint. Sub-mm σ here (√7e-6 ≈ 2.7 mm) means this waypoint has geometrically rich structure to lock onto. A waypoint in a bare corridor would show a large covariance along the corridor axis — the classic "sliding" degeneracy. The pose-graph optimiser weights edges by the inverse of these covariances.

### 2.2 Edge — a traversable connection with baked-in gait policy

```
Edge {
  id            : {from_waypoint, to_waypoint}
  snapshot_id   : "edge_snapshot_id_..."          # → foot-fall breadcrumbs
  from_tform_to : SE3Pose                           # relative transform (the "measurement")
  annotations {
    direction_constraint            : NONE|...      # forwards-only, etc.
    override_mobility_params {paths: [...]}          # which mobility fields to force on replay
    mobility_params { vel_limit, body_control, terrain_params, stairs_mode, ... }
  }
}
```

`from_tform_to` is the relative-pose *measurement* that the pose graph is built from — GraphNav is fundamentally a relative-pose SLAM system. Absolute positions never appear in `graph.waypoints`; they only exist in `anchoring` (§6).

The **payload here that most systems don't have** is `annotations.mobility_params`: the edge remembers *how the robot was told to walk it*. Observed `override_mobility_params.paths` on a single edge:

```
terrain_params.grated_surfaces_mode      obstacle_params.disable_vision_*_avoidance (×5)
terrain_params.ground_mu_hint            stairs_mode / disallow_stair_tracker
body_control                             swing_height / locomotion_hint
hazard_detection_mode                    disable_missing_data_cliffs / disable_nearmap_cliff_avoidance
obstacle_params.obstacle_avoidance_padding
```

with concrete values, e.g. `vel_limit.max_vel.linear = (1.6, 0.5) m/s`, `angular = 1.13 rad/s`, plus a full `body_control` pose spline. **Path planning here is not just geometry — the map carries a per-edge locomotion configuration.** Replaying an edge across grating, or with cliff-avoidance disabled, is a property of the edge, recorded once and reused.

---

## 3. The frame graph — Spot's odometry model

This is the part most relevant to "how they capture odometry." Every snapshot embeds a `transforms_snapshot`: a **tree of SE(3) edges** (`child → parent_frame_name + parent_tform_child`). Spot's estimator maintains several frames simultaneously:

| Frame | Meaning | Why it exists |
|---|---|---|
| `body` | Robot body frame (tree root here) | The thing being controlled |
| `odom` | **Kinematic/inertial odometry** — dead-reckoned from leg kinematics + IMU | Smooth, continuous, *drifts* over distance |
| `vision` | **Visual-inertial odometry** — corrected by cameras/fiducials | Less drift, but can *jump* on correction |
| `flat_body` | Body position, orientation gravity-aligned (roll/pitch zeroed) | Terrain-relative reasoning |
| `gpe` | **Ground Plane Estimate** — the fitted local ground plane | Foot placement / step height |
| `feet_center` | Centroid of the four foot contacts | Support-polygon / balance |
| `sensor_origin_generated` | Synthetic origin for the fused point cloud | Where the depth points live |

**The `odom` vs `vision` distinction is the whole game.** From this recording, at one waypoint the body has translated ~53 m from where `odom` was initialised. Two truths BD bakes into the API:

- **`odom` is smooth but drifts.** Never teleports. Good for short-horizon control and integrating velocity. Over 99 m of walking it will have accumulated metric error.
- **`vision` is drift-corrected but discontinuous.** When VIO or a fiducial fixes the estimate, `vision` snaps. Good for "where am I really," bad for anything that differentiates position.

GraphNav layers a **third** correction on top: ICP scan-matching of the *current* fused cloud against the *nearest waypoint's* stored cloud (§5.1), which is what actually re-localises you into the map. So the localisation stack is a cascade: leg-kinematics+IMU (`odom`) → VIO/fiducials (`vision`) → per-waypoint ICP (`graph`) → global anchoring (`seed`).

To compose transforms across a snapshot, use the SDK helper rather than hand-rolling quaternion math:

```python
from bosdyn.client.frame_helpers import get_a_tform_b, ODOM_FRAME_NAME
from bosdyn.client.math_helpers  import SE3Pose
ko_tform_cloud = get_a_tform_b(pc.source.transforms_snapshot,
                               ODOM_FRAME_NAME, pc.source.frame_name_sensor)
```

Rotations are stored as **quaternions `(w,x,y,z)`, translations in metres** — no Euler anywhere, which sidesteps gimbal/ordering ambiguity. Every pose is a `bosdyn.api.SE3Pose`.

---

## 4. WaypointSnapshot — the perception payload

This is where the bytes are (≈ 361 KB average, up to 2.8 MB). One snapshot per waypoint, containing everything the robot sensed there. Populated fields on a representative snapshot:

```
images            ×10   (5 fisheye greyscale + 5 stereo depth)
point_cloud       1     (7,619 pts here; 12,174 avg; 937,442 total across the map)
robot_local_grids ×5    (terrain / terrain_valid / obstacle_distance / fixed_obstacle_distance / no_step)
robot_state       1     (kinematic state, 12 joints, transforms) — 3.1 KB
objects           ×1    (a detected AprilTag as a full WorldObject)
robot_id, recording_started_on, payloads ×5, id
```

### 4.1 Point cloud — `bosdyn.api.PointCloud`

```
source.frame_name_sensor : "sensor_origin_generated"
num_points               : 7619
encoding                 : ENCODING_XYZ_32F            # 1
data                     : 91,428 bytes  == 7619 × 12  # 3 × float32, tightly packed
```

Decode is a one-liner because it's raw interleaved little-endian float32:

```python
import numpy as np
pts = np.frombuffer(pc.data, np.float32).reshape(-1, 3)   # (N,3) XYZ in the sensor frame
```

Encoding options the format supports (this map uses the first):

| enum | meaning | bytes/pt |
|---|---|---|
| `ENCODING_XYZ_32F` | full float32 XYZ | 12 |
| `ENCODING_XYZ_4SC` | 4-byte packed signed-char with scale | 4 |
| `ENCODING_XYZ_5SC` | 5-byte packed | 5 |

That BD chose **uncompressed 12 B/pt** for a stored map (rather than the 4 B/pt packed form) is a deliberate accuracy-over-size call — the cloud is the ICP reference, so quantisation noise directly degrades re-localisation. With only ~12 k points/waypoint the cloud is anyway tiny next to the imagery (89 KB vs 2.5 MB), so there's nothing to gain by packing it.

The cloud is a **fused, downsampled** product (fisheye stereo from all sides merged into one `sensor_origin_generated` cloud), not a raw single-camera depth image — hence the clean 360° coverage in the reconstruction.

### 4.2 Images — raw, not compressed

All 10 images are `FORMAT_RAW` (uncompressed):

| Source (×5 each) | Size | Pixel format | Bytes |
|---|---|---|---|
| `*_fisheye_image` | 640×480 | `PIXEL_FORMAT_GREYSCALE_U8` | 307,200 |
| `*_depth` | 424×240 | `PIXEL_FORMAT_DEPTH_U16` | 203,520 |

Depth decode is `uint16` **millimetres** (0 = invalid/no-return):

```python
d = np.frombuffer(im.shot.image.data, np.uint16).reshape(rows, cols).astype(float)
d[d == 0] = np.nan            # holes
d *= 0.001                    # → metres
```

Two hardware realities visible in the imagery (see `cameras.png`):

- **The two front fisheyes are physically mounted rotated ~90°** — a well-known Spot trait. Raw frames look tilted; production code applies the per-camera rotation from the image source's transform before display.
- **Stereo depth is sparse outdoors** — measured valid-pixel fractions per camera here: front-left 39%, front-right 28%, left **6%**, right 43%, back 16%. Sky, distant geometry, specular tile and low-texture surfaces defeat active/passive stereo, so most valid returns are < 4 m. This is *why* GraphNav leans on the fused cloud + ICP rather than trusting any single depth frame, and why the covariance bookkeeping in §2.1 matters.

### 4.3 robot_local_grids — **the path-planning cost maps** ⭐

This is the crown jewel for exploration/planning. Each waypoint stores **five co-registered 128×128 grids at 3 cm/cell** — a **3.84 m × 3.84 m** ego-centric map:

| `local_grid_type_name` | cell_format | encoding | scale | offset | meaning |
|---|---|---|---|---|---|
| `terrain` | INT16 | RAW | 0.001 | −2.985 | **height map** (metres) |
| `terrain_valid` | UINT8 | RAW | — | — | validity mask (0 = no data) |
| `obstacle_distance` | INT16 | RAW | 0.001 | +1.329 | **signed distance field**: >0 free, <0 inside obstacle |
| `fixed_obstacle_distance` | INT16 | RAW | 0.001 | 0.0 | second SDF (persistent-obstacle variant) |
| `no_step` | INT16 | RAW | 0.001 | +1.139 | **steppability cost**: low = don't place a foot |

**Universal decode** (fixed-point → float, then reshape to the grid corner frame, row-major):

```python
nx, ny = lg.extent.num_cells_x, lg.extent.num_cells_y          # 128, 128
raw   = np.frombuffer(lg.data, np.int16).reshape(ny, nx)        # (or uint8 for terrain_valid)
value = raw.astype(np.float32) * lg.cell_value_scale + lg.cell_value_offset
value = np.where(valid_mask > 0, value, np.nan)                 # apply terrain_valid
```

Low-level design notes:

- **Fixed-point, not float.** Storing INT16 with a per-grid `scale`+`offset` halves the bytes vs float32 while keeping **1 mm resolution** over a ±32 m span. The offset is re-centred per grid to keep the interesting range inside INT16 — that's why `obstacle_distance` offset (+1.329) differs from `fixed_obstacle_distance` (0.0); the *decoded* quantity is a distance either way, the offset is just an encoding dial to maximise dynamic range.
- **Two encodings exist:** `ENCODING_RAW` (used here) and `ENCODING_RLE` (run-length, via a parallel `rle_counts` array). On dense terrain RAW wins; on sparse masks RLE would. This map ships RAW (`rle_counts` empty), i.e. BD optimised for decode simplicity over the marginal size saving.
- **The obstacle grid is a *signed distance field*, not a binary occupancy grid.** SDFs are the right primitive for a planner: the value *is* the clearance to the nearest obstacle, the gradient *is* the direction to push away, and the zero-level-set is the obstacle boundary — all without a separate distance transform at plan time. In `grids.png` the black contour is exactly that 0-crossing.
- **`no_step` separates "can't stand there" from "can't be there."** A grating gap or a curb edge may be traversable by the body but not a valid *foothold*; the no-step grid encodes that as a continuous cost, which the footstep planner consumes independently of the body-level obstacle SDF.
- Each grid carries **its own `transforms_snapshot`** (`..._local_grid_corner ← odom/vision/body`) and `acquisition_time`, so grids from different waypoints (captured at slightly different instants) can be placed correctly and never assume a shared clock.

### 4.4 robot_state — proprioception at the waypoint

```
kinematic_state.joint_states  ×12 : fl/fr/hl/hr × {hx, hy, kn}
  each: {position [rad], velocity [rad/s], load [Nm], acceleration}
velocity_of_body_in_vision        : linear + angular
transforms_snapshot               : flat_body, feet_center, odom, gpe, vision, body
```

Example (standing, velocities ≈ 0): knees `kn ≈ −1.57 rad` under **15–18 Nm** load; hips `hy ≈ 0.87 rad`. **The stored `load` is the joint torque estimated from motor current through the gearbox** — the exact proprioceptive channel that gearbox drag and grease viscosity bias. (Directly relevant to your actuator-telemetry work: an autowalk snapshot is a free, timestamped, per-joint torque sample at a known posture.)

### 4.5 objects — AprilTags as first-class world objects

Detected fiducials are stored as full `WorldObject`s inside the snapshot:

```
world_obj_apriltag_5 { apriltag_properties {
    tag_id: 5, dimensions: 0.146 × 0.146 m, frame_name_fiducial: "fiducial_5", ... } }
```

so the snapshot records not just "I saw tag 5" but its measured pose and physical size — the input to the anchoring solve.

---

## 5. EdgeSnapshot — how the edge gets *walked*

Tiny (avg ~1.5 KB, 112 KB for all 76). No perception — instead, a list of **`stances`** (foot-fall breadcrumbs), 15 in the largest:

```
Stance {
  timestamp
  ko_tform_body, vision_tform_body      # body pose at this footfall, in both odom frames
  planar_ground                          # ground-plane scalar
  foot_states ×4 {
     foot_position_rt_body : Vec3         # where each foot was planted
     contact               : CONTACT_MADE | CONTACT_LOST | UNKNOWN
     terrain {                            # per-foot ground characterisation ⭐
        ground_mu_est                     # estimated friction coefficient
        foot_slip_distance_rt_frame, foot_slip_velocity_rt_frame
        ground_contact_normal_rt_frame    # local surface normal
        visual_surface_ground_penetration_mean / _std   # how far the foot sank vs the visual surface
     }
  }
}
```

This is a **recorded gait trace**: the exact foot placements and the *measured terrain response* (friction, slip, surface normal, penetration) at each step. On replay it gives the controller a proven foothold sequence and a ground model, so it can reproduce a gait that already worked over this stretch instead of re-solving footholds blind. `ground_mu_est` and `foot_slip_*` are effectively a per-step traction log — the empirical counterpart to the `terrain_params.ground_mu_hint` *override* stored on the edge in §2.2.

---

## 6. Anchoring — turning a relative pose-graph into a global map

`graph.anchoring` is what makes the whole thing metric and globally consistent:

```
anchoring {
  anchors ×77  { id, seed_tform_waypoint : SE3Pose }   # every waypoint's pose in ONE global "seed" frame
  objects ×4   { id, seed_tform_object   : SE3Pose }   # every fiducial's pose in the seed frame
}
```

The **`seed` frame** is the single global reference. It's *derived*, not measured: an optimiser takes all the relative edge measurements (`from_tform_to`), weights them by the ICP covariances (§2.1), and pins the solution using the shared fiducial observations (§4.5). The output is one consistent `seed_tform_waypoint` per node. Fiducials 2/3/4/5 land at seed positions (61.9, 1.8), (28.5, −10.8), (−0.02, 0.01), (12.3, 0.5) — with tag 4 essentially at the seed origin, i.e. the map was gauge-fixed there.

**Reconstructing the global cloud** (what `map_overview.png` is) is then a clean chain per waypoint:

```
seed_tform_cloud = seed_tform_waypoint            # from anchoring
                 · waypoint_tform_ko              # from graph (ko = odom)
                 · ko_tform_cloud                 # from the snapshot's own frame tree
```

```python
seed_T_cloud = SE3Pose.from_proto(anchor.seed_tform_waypoint) \
             * SE3Pose.from_proto(wp.waypoint_tform_ko) \
             * get_a_tform_b(pc.source.transforms_snapshot, "odom", pc.source.frame_name_sensor)
world_pts = (seed_T_cloud.to_matrix() @ np.c_[pts, np.ones(len(pts))].T).T[:, :3]
```

Stitching all 77 clouds this way produces a spatially coherent 70 m corridor with the fiducials in sensible places — **empirical proof the frame math and the anchoring solve are self-consistent**. (225 k points shown; 937 k available.)

---

## 7. How it composes end-to-end

| Phase | Mechanism | Data used |
|---|---|---|
| **Record** | Walk under teleop; drop a waypoint when the robot has moved "enough"; snapshot perception + odometry; log foot-falls per edge | writes `graph` + snapshots |
| **Localise (live)** | Fuse current cloud → ICP-match against nearest waypoint snapshot; weight by `icp_variance`; cascade `odom`→`vision`→graph | `point_cloud`, `icp_variance`, `scan_match_region` |
| **Anchor** | Pose-graph optimise relative edges + fiducials → global `seed_tform_waypoint` | `edges.from_tform_to`, `anchoring`, fiducial `objects` |
| **Plan** | Route over the *topological* graph (which edges), then local motion over the *SDF/no-step grids* (how to move) | edges + `robot_local_grids` |
| **Replay edge** | Drive `from_waypoint → to_waypoint` applying the edge's stored `mobility_params`; reproduce the recorded foothold sequence + ground model | `EdgeSnapshot.stances`, edge `mobility_params` |

Planning is explicitly **two-layer**: a coarse topological search over waypoints/edges (cheap, global) feeding a fine local planner over the ego-centric cost grids (dense, short-horizon). That's the standard way to keep global planning tractable while retaining metric obstacle avoidance — and the file format mirrors it exactly.

---

## 8. Design & efficiency observations (the low-level "why")

1. **Topology-first SLAM.** No monolithic global occupancy grid; the map is a graph of locally-accurate submaps and global consistency is *computed* (§6). Scales to large sites; robust to drift; loop closures and fiducials just add edges/constraints.
2. **Relative measurements are the source of truth.** `graph` stores only relative poses; absolute poses live solely in the (regenerable) anchoring. You can re-run the anchoring solve without re-recording.
3. **Byte budget is dominated by raw imagery, not geometry.** Largest snapshot: images **2494 KB** vs cloud 89 KB vs grids 144 KB vs state 3 KB. The cloud stays uncompressed *because* it's the ICP reference and it's cheap anyway; the images are the thing you'd compress/prune if size mattered (they're kept raw here for fidelity + speed).
4. **Fixed-point grids with per-grid scale+offset** — INT16 @ 1 mm over a re-centred range: half the size of float32, no meaningful precision loss for a 3 cm-cell map, trivial decode.
5. **SDF > occupancy for the obstacle layer.** Clearance value + gradient + zero-level-set in one grid; no plan-time distance transform.
6. **Foothold vs body obstacles are separate layers** (`no_step` vs `obstacle_distance`) — legged locomotion needs both, and conflating them loses grating/curb behaviour.
7. **Every payload is self-describing in time and frame.** Each cloud/grid/state carries its own `acquisition_time` and `transforms_snapshot`; nothing assumes a global clock or a single frame — essential when fusing asynchronous sensors.
8. **Quaternions + metres throughout.** No Euler, no ambiguity; poses are uniformly `SE3Pose`.
9. **Locomotion policy travels with the map.** Per-edge `mobility_params` + recorded stances mean "how to walk here" is data, recorded once, replayed deterministically — not re-derived each run.

---

## 9. Reproduce / extend

```bash
pip install bosdyn-api bosdyn-client protobuf numpy matplotlib
# then: parse graph → join snapshots by snapshot_id → decode per §4 → anchor per §6
```

Figures generated here (in this folder):
- `map_overview.png` — stitched global cloud (top-down height-coloured + side elevation) with waypoint graph & fiducials.
- `grids.png` — one waypoint's terrain / obstacle-SDF / no-step cost grids.
- `cameras.png` — the 5-fisheye + 5-depth perception ring at one waypoint.

Ideas that fall straight out of this data model:
- **Traversability learning:** regress `no_step`/`ground_mu_est` from the fisheye/terrain grids.
- **Global occupancy export:** rasterise all `obstacle_distance` grids into the seed frame → a site-wide 2.5D cost map for an external planner.
- **Loop-closure injection:** you have 4 fiducials on a linear chain; adding a manual loop-closure edge and re-running anchoring would visibly tighten the seed-frame solution (measurable via the covariance-weighted residual).
- **Actuator telemetry mining (your project):** every waypoint is a timestamped 12-joint torque/position sample at a known posture — a free dataset for characterising gearbox drag / grease effects on the `load` estimate across the fleet.

---

*Decoded with `bosdyn-api` 5.1.4. Field names/enums verified against the installed protobuf descriptors, not from memory. Inferences (e.g. `fixed_obstacle_distance` semantics, exact `no_step` units) are flagged as such in-line.*
