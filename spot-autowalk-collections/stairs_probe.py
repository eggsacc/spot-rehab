#!/usr/bin/env python3
"""
Locate the staircase in a Spot GraphNav autowalk, then dump the perception the
robot saw and the foot placements it actually chose.

Two subcommands:

  python3 stairs_probe.py find ROOT
      Ranks the walk for a stair signature and prints candidate waypoint ids +
      the spanning edge + a ready-to-paste `dump` command. Graph-only pass is
      near-instant; it decodes at most a handful of snapshots to confirm.

  python3 stairs_probe.py dump ROOT WAYPOINT_ID [NEXT_WAYPOINT_ID]
      Decodes ONE waypoint snapshot -> fisheye images, depth heatmaps,
      terrain / obstacle_distance(SDF) / no_step grids, cloud side elevation.
      If NEXT_WAYPOINT_ID is given, also decodes the edge WAYPOINT_ID->NEXT and
      plots the recorded footfalls (position, contact, ground_mu_est, slip).
      Writes PNGs to ./stairs_out/.

ROOT is the extracted walk directory (contains graph, waypoint_snapshots/,
edge_snapshots/). Requires bosdyn-api / bosdyn-client (tested 5.1.4), numpy,
matplotlib. Nothing proprietary.

WHY foot placement lives in two files: the WAYPOINT snapshot holds the cost
maps the local planner reasons over (no_step / terrain / SDF) plus depth; the
EDGE snapshot holds the gait+traction trace it committed to (per-foot position,
contact, ground_mu_est, slip). To see "how it decides where to step on uneven
terrain" you want both, which is why `dump` takes an optional edge.
"""
import os
import sys
import glob
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from google.protobuf import text_format

from bosdyn.api.graph_nav import map_pb2
from bosdyn.client.math_helpers import SE3Pose


# --------------------------------------------------------------------------- #
# shared decode helpers
# --------------------------------------------------------------------------- #
def load_graph(root):
    g = map_pb2.Graph()
    with open(os.path.join(root, "graph"), "rb") as f:
        g.ParseFromString(f.read())
    return g


def load_waypoint_snapshot(root, snapshot_id):
    s = map_pb2.WaypointSnapshot()
    with open(os.path.join(root, "waypoint_snapshots", snapshot_id), "rb") as f:
        s.ParseFromString(f.read())
    return s


def decode_grid(lg):
    """raw * scale + offset, reshaped row-major. cell_format: 5=INT16 4=U8 1=F32."""
    dt = {5: np.int16, 4: np.uint8, 1: np.float32}[lg.cell_format]
    nx, ny = lg.extent.num_cells_x, lg.extent.num_cells_y
    expect = nx * ny * np.dtype(dt).itemsize
    if len(lg.data) != expect:                       # RLE-encoded grid; skip
        return None
    raw = np.frombuffer(lg.data, dt).reshape(ny, nx).astype(np.float32)
    return raw * lg.cell_value_scale + lg.cell_value_offset


def terrain_span(root, snapshot_id):
    """Vertical relief (m) of the terrain grid at a waypoint; NaN if unavailable."""
    try:
        s = load_waypoint_snapshot(root, snapshot_id)
        grids = {lg.local_grid_type_name: lg for lg in s.robot_local_grids}
        if "terrain" not in grids:
            return float("nan")
        t = decode_grid(grids["terrain"])
        if t is None:
            return float("nan")
        if "terrain_valid" in grids:
            m = np.frombuffer(grids["terrain_valid"].data, np.uint8).reshape(t.shape) > 0
            t = np.where(m, t, np.nan)
        return float(np.nanmax(t) - np.nanmin(t))
    except Exception:
        return float("nan")


def order_chain(g):
    """Waypoint ids in traversal order (assumes the single open chain in this walk)."""
    adj = defaultdict(list)
    deg = defaultdict(int)
    for e in g.edges:
        a, b = e.id.from_waypoint, e.id.to_waypoint
        adj[a].append(b)
        adj[b].append(a)
        deg[a] += 1
        deg[b] += 1
    ends = [w for w in deg if deg[w] == 1]
    start = ends[0] if ends else g.waypoints[0].id
    order, seen, cur = [], set(), start
    while cur is not None and cur not in seen:
        order.append(cur)
        seen.add(cur)
        cur = next((n for n in adj[cur] if n not in seen), None)
    # append any waypoints not reached (branches / islands)
    for w in g.waypoints:
        if w.id not in seen:
            order.append(w.id)
    return order


# --------------------------------------------------------------------------- #
# find
# --------------------------------------------------------------------------- #
def cmd_find(root):
    g = load_graph(root)
    snap = {w.id: w.snapshot_id for w in g.waypoints}
    zc = {a.id: a.seed_tform_waypoint.position.z for a in g.anchoring.anchors}
    order = order_chain(g)

    print(f"{len(g.waypoints)} waypoints, {len(g.edges)} edges, "
          f"{len(g.anchoring.objects)} anchored fiducials\n")

    # per-step seed-frame body-height change along the traversal order
    dz = np.array([zc.get(order[i], np.nan) - zc.get(order[i - 1], np.nan)
                   for i in range(1, len(order))])

    # sliding window: contiguous run with the largest |cumulative climb|
    best = (0, 0, 0.0)
    for w in range(1, min(12, len(dz)) + 1):
        c = np.convolve(np.nan_to_num(dz), np.ones(w), "valid")
        k = int(np.argmax(np.abs(c)))
        if abs(c[k]) > abs(best[2]):
            best = (k, k + w, float(c[k]))
    i0, i1, climb = best

    print(f"Steepest sustained body-height change: {climb:+.2f} m "
          f"across chain positions {i0}->{i1}.")
    print("Candidate waypoints (chain idx : waypoint_id : snapshot_id : z[m]):")
    for j in range(i0, i1 + 1):
        wid = order[j]
        print(f"  {j:3d}  {wid[:14]}  {snap.get(wid,'?')}  z={zc.get(wid,float('nan')):+.2f}")

    # version-proof: dump edge annotations to text and grep for stair-ish hints
    print("\nEdges whose annotations mention stair / grated / mu / incline:")
    ann_hit = False
    for e in g.edges:
        txt = text_format.MessageToString(e.annotations).lower()
        keys = [k for k in ("stair", "grated", "incline") if k in txt]
        if "ground_mu_hint" in txt:
            # only interesting if it's actually set to something non-default
            for line in txt.splitlines():
                if "ground_mu_hint" in line and line.strip().split(":")[-1].strip() not in ("0", "0.0"):
                    keys.append("ground_mu_hint")
        if keys:
            ann_hit = True
            print(f"  {e.id.from_waypoint[:12]} -> {e.id.to_waypoint[:12]}  [{','.join(sorted(set(keys)))}]")

    if not ann_hit:
        print("  (none) -- no edge carries a stair/grated/incline annotation.")

    # confirm with terrain-grid relief at the candidates
    print("\nTerrain-grid vertical relief at candidates (larger = more 3D structure):")
    spans = []
    for wid in order[i0:i1 + 1]:
        sp = terrain_span(root, snap.get(wid, ""))
        spans.append(sp)
        tag = f"{sp:.3f} m" if sp == sp else "(no terrain grid)"
        print(f"  {wid[:14]}  span={tag}")

    # verdict
    max_climb = np.nanmax(np.abs(dz)) if dz.size else 0.0
    flat = (abs(climb) < 0.20) and (max_climb < 0.08) and not ann_hit
    print()
    if flat:
        print("VERDICT: no stair-like segment. The walk is essentially level "
              "(matches a flat covered walkway). Double-check this recording "
              "actually contains a staircase -- it may not.")
    else:
        mid = order[(i0 + i1) // 2]
        nxt = order[min((i0 + i1) // 2 + 1, len(order) - 1)]
        print(f"VERDICT: stairs most likely around waypoint {mid[:14]} "
              f"(snapshot {snap.get(mid,'?')}).")
        print("Dump it and the spanning edge with:\n")
        print(f'  python3 stairs_probe.py dump "{root}" {mid} {nxt}')


# --------------------------------------------------------------------------- #
# dump
# --------------------------------------------------------------------------- #
def _is_depth(img, name):
    n = img.rows * img.cols
    return len(img.data) == 2 * n or "depth" in name.lower()


def dump_waypoint(root, wp_id, outdir):
    g = load_graph(root)
    snap = {w.id: w.snapshot_id for w in g.waypoints}
    if wp_id not in snap:
        sys.exit(f"waypoint {wp_id} not in graph")
    s = load_waypoint_snapshot(root, snap[wp_id])
    os.makedirs(outdir, exist_ok=True)

    # ---- images: fisheye + depth heatmap ----
    for im in s.images:
        img = im.shot.image
        name = im.source.name
        if _is_depth(img, name):
            d = np.frombuffer(img.data, np.uint16).reshape(img.rows, img.cols).astype(float)
            d[d == 0] = np.nan
            d *= 0.001
            plt.figure(figsize=(5, 3))
            plt.imshow(d, cmap="turbo")
            plt.colorbar(label="depth (m)")
            plt.title(name)
            plt.tight_layout()
            plt.savefig(f"{outdir}/depth_{name}.png", dpi=130)
            plt.close()
        else:
            gr = np.frombuffer(img.data, np.uint8).reshape(img.rows, img.cols)
            if "front" in name.lower():           # front fisheyes mounted ~90 deg
                gr = np.rot90(gr)
            plt.figure(figsize=(4, 3))
            plt.imshow(gr, cmap="gray")
            plt.title(name)
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(f"{outdir}/fisheye_{name}.png", dpi=130)
            plt.close()

    # ---- local grids: terrain / SDF / no_step ----
    grids = {lg.local_grid_type_name: lg for lg in s.robot_local_grids}
    for key, cmap, label in [("terrain", "turbo", "height (m)"),
                             ("obstacle_distance", "coolwarm", "SDF (m, >0 free)"),
                             ("no_step", "magma", "no-step cost")]:
        if key not in grids:
            continue
        a = decode_grid(grids[key])
        if a is None:
            continue
        if key == "terrain" and "terrain_valid" in grids:
            m = np.frombuffer(grids["terrain_valid"].data, np.uint8).reshape(a.shape) > 0
            a = np.where(m, a, np.nan)
        plt.figure(figsize=(4.2, 4))
        plt.imshow(a, origin="lower", cmap=cmap)
        plt.colorbar(label=label)
        plt.title(f"{key}  (128x128 @3cm = 3.84 m)")
        plt.tight_layout()
        plt.savefig(f"{outdir}/grid_{key}.png", dpi=130)
        plt.close()

    # ---- point cloud side elevation ----
    pc = s.point_cloud
    if pc.num_points:
        pts = np.frombuffer(pc.data, np.float32).reshape(-1, 3)
        plt.figure(figsize=(6, 3))
        plt.scatter(pts[:, 0], pts[:, 2], s=0.5, c=pts[:, 2], cmap="turbo")
        plt.xlabel("x (m)")
        plt.ylabel("z (m)")
        plt.title("cloud side elevation (sensor frame)")
        plt.tight_layout()
        plt.savefig(f"{outdir}/cloud_side.png", dpi=130)
        plt.close()

    print(f"waypoint {wp_id[:14]} -> {snap[wp_id]}: "
          f"{len(s.images)} images, {len(grids)} grids, {pc.num_points} cloud pts")


def dump_feet(root, from_wp, to_wp, outdir):
    g = load_graph(root)
    esid = None
    for e in g.edges:
        if e.id.from_waypoint == from_wp and e.id.to_waypoint == to_wp:
            esid = e.snapshot_id
            break
        if e.id.from_waypoint == to_wp and e.id.to_waypoint == from_wp:
            esid = e.snapshot_id       # edges are undirected for our purposes
            break
    if esid is None:
        print(f"no edge between {from_wp[:12]} and {to_wp[:12]}; skipping feet")
        return

    es = map_pb2.EdgeSnapshot()
    with open(os.path.join(root, "edge_snapshots", esid), "rb") as f:
        es.ParseFromString(f.read())

    rows = []   # x_odom, y_odom, z_odom, mu, contact_made
    for st in es.stances:
        M = SE3Pose.from_proto(st.ko_tform_body).to_matrix()   # ko == odom
        for fs in st.foot_states:
            v = fs.foot_position_rt_body                       # bare Vec3, no .position
            p = (M @ np.array([v.x, v.y, v.z, 1.0]))[:3]
            mu = float("nan")
            if fs.HasField("terrain"):
                mu = fs.terrain.ground_mu_est
            made = (fs.contact == 1)                            # 1 = CONTACT_MADE
            rows.append((p[0], p[1], p[2], mu, made))

    if not rows:
        print(f"edge {esid}: no stance/foot data recorded")
        return
    R = np.array([r[:4] for r in rows], float)
    made = np.array([r[4] for r in rows], bool)
    os.makedirs(outdir, exist_ok=True)

    # top-down footfalls colored by estimated ground friction
    plt.figure(figsize=(6, 5))
    good = ~np.isnan(R[:, 3])
    sc = plt.scatter(R[good, 0], R[good, 1], c=R[good, 3], cmap="viridis",
                     s=18, marker="o", label="mu_est")
    if (~good).any():
        plt.scatter(R[~good, 0], R[~good, 1], c="0.6", s=14, marker="x", label="no mu")
    plt.colorbar(sc, label="ground_mu_est")
    plt.gca().set_aspect("equal")
    plt.xlabel("x_odom (m)")
    plt.ylabel("y_odom (m)")
    plt.title("footfalls, top-down (colour = est. friction)")
    plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{outdir}/feet_topdown.png", dpi=130)
    plt.close()

    # side view: foot height vs travel -> the step-up profile; marker = contact
    travel = R[:, 0] - R[:, 0].min()
    plt.figure(figsize=(7, 3.5))
    plt.scatter(travel[made], R[made, 2], s=16, marker="o", label="contact made")
    plt.scatter(travel[~made], R[~made, 2], s=16, marker="^", label="in swing")
    plt.xlabel("travel along x_odom (m)")
    plt.ylabel("foot z_odom (m)")
    plt.title("foot height along the edge (step-up shows as a staircase)")
    plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{outdir}/feet_side.png", dpi=130)
    plt.close()

    dz = R[:, 2].max() - R[:, 2].min()
    print(f"edge {esid}: {len(es.stances)} stances, {len(rows)} footfalls, "
          f"foot-z span {dz:.3f} m, mu range "
          f"{np.nanmin(R[:,3]):.2f}-{np.nanmax(R[:,3]):.2f}")


def cmd_dump(root, wp_id, next_wp=None):
    outdir = "stairs_out"
    dump_waypoint(root, wp_id, outdir)
    if next_wp:
        dump_feet(root, wp_id, next_wp, outdir)
    print(f"wrote PNGs to ./{outdir}/")


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    mode, root = sys.argv[1], sys.argv[2]
    if mode == "find":
        cmd_find(root)
    elif mode == "dump":
        cmd_dump(root, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        sys.exit(f"unknown mode {mode!r}; use find or dump")
