#!/usr/bin/env python3
"""
decode_and_stitch.py
Decode a Boston Dynamics Spot GraphNav autowalk and stitch every waypoint's
local point cloud into one globally-consistent cloud in the anchoring ("seed") frame.

Usage:
    python3 decode_and_stitch.py "lt6 inspection.walk"

Requires:
    pip install bosdyn-api bosdyn-client protobuf numpy matplotlib

Outputs (written next to the script):
    merged_points.npy   (N,3) float32  stitched cloud in seed frame
    wp_seed.npy         (W,3) float32  waypoint positions in seed frame
    fiducials.npy       (F,4) float32  [x,y,z,tag_id]
    map_overview.png    top-down + side-elevation render
"""
import sys, os, glob
import numpy as np
from bosdyn.api.graph_nav import map_pb2
from bosdyn.client.math_helpers import SE3Pose
from bosdyn.client.frame_helpers import get_a_tform_b, ODOM_FRAME_NAME


def load_graph(walk_dir):
    g = map_pb2.Graph()
    with open(os.path.join(walk_dir, "graph"), "rb") as f:
        g.ParseFromString(f.read())
    return g


def stitch(walk_dir, per_wp_cap=6000, seed=0):
    """Transform every waypoint's cloud into the seed frame and concatenate."""
    rng = np.random.default_rng(seed)
    g = load_graph(walk_dir)

    # waypoint pose in the global seed frame, keyed by waypoint id
    seed_tform_wp = {a.id: SE3Pose.from_proto(a.seed_tform_waypoint)
                     for a in g.anchoring.anchors}

    all_pts, wp_seed = [], []
    ok = skipped = 0
    for w in g.waypoints:
        snap_path = os.path.join(walk_dir, "waypoint_snapshots", w.snapshot_id)
        if not os.path.exists(snap_path) or w.id not in seed_tform_wp:
            skipped += 1
            continue

        s = map_pb2.WaypointSnapshot()
        with open(snap_path, "rb") as f:
            s.ParseFromString(f.read())
        pc = s.point_cloud
        if pc.num_points == 0:
            skipped += 1
            continue

        # 1) raw XYZ float32 in the sensor frame
        pts = np.frombuffer(pc.data, np.float32).reshape(-1, 3).astype(np.float64)

        # 2) frame chain:  seed <- waypoint <- ko(odom) <- sensor cloud
        ko_tform_cloud = get_a_tform_b(pc.source.transforms_snapshot,
                                       ODOM_FRAME_NAME, pc.source.frame_name_sensor)
        wp_tform_ko = SE3Pose.from_proto(w.waypoint_tform_ko)  # ko == odom
        seed_tform_cloud = seed_tform_wp[w.id] * wp_tform_ko * ko_tform_cloud

        # 3) apply the 4x4 homogeneous transform
        M = seed_tform_cloud.to_matrix()
        homog = np.hstack([pts, np.ones((len(pts), 1))])
        world = (M @ homog.T).T[:, :3]

        # 4) optional per-waypoint subsample to bound memory
        if per_wp_cap and len(world) > per_wp_cap:
            world = world[rng.choice(len(world), per_wp_cap, replace=False)]

        all_pts.append(world)
        p = seed_tform_wp[w.id].position
        wp_seed.append([p.x, p.y, p.z])
        ok += 1

    P = np.vstack(all_pts)
    WP = np.array(wp_seed)

    # fiducials (AprilTags) in the seed frame
    fid = [[o.seed_tform_object.position.x,
            o.seed_tform_object.position.y,
            o.seed_tform_object.position.z,
            int(o.id)] for o in g.anchoring.objects]
    FID = np.array(fid, dtype=np.float32) if fid else np.zeros((0, 4), np.float32)

    # real traversed path length (sum of edge lengths in the seed frame)
    wp_pos = {a.id: np.array([a.seed_tform_waypoint.position.x,
                              a.seed_tform_waypoint.position.y,
                              a.seed_tform_waypoint.position.z])
              for a in g.anchoring.anchors}
    path_len = sum(np.linalg.norm(wp_pos[e.id.to_waypoint] - wp_pos[e.id.from_waypoint])
                   for e in g.edges
                   if e.id.from_waypoint in wp_pos and e.id.to_waypoint in wp_pos)

    print(f"stitched {ok} waypoints (skipped {skipped}); {len(P):,} points")
    print(f"path length (edge sum): {path_len:.1f} m over {len(g.edges)} edges")
    return P.astype(np.float32), WP.astype(np.float32), FID, g


def render(P, WP, FID, g, outdir="."):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    wp_xy = {a.id: (a.seed_tform_waypoint.position.x, a.seed_tform_waypoint.position.y)
             for a in g.anchoring.anchors}
    segs = [[wp_xy[e.id.from_waypoint], wp_xy[e.id.to_waypoint]]
            for e in g.edges
            if e.id.from_waypoint in wp_xy and e.id.to_waypoint in wp_xy]

    plt.style.use("dark_background")
    fig = plt.figure(figsize=(16, 11)); fig.patch.set_facecolor("#0d1117")

    ax = fig.add_subplot(2, 1, 1); ax.set_facecolor("#0d1117")
    order = np.argsort(P[:, 2])                       # draw high points last
    sc = ax.scatter(P[order, 0], P[order, 1], c=P[order, 2],
                    s=0.6, cmap="turbo", alpha=0.75, linewidths=0)
    ax.add_collection(LineCollection(segs, colors="#00e5ff", linewidths=1.6, alpha=0.9, zorder=5))
    ax.scatter(WP[:, 0], WP[:, 1], s=22, c="white", edgecolors="#00e5ff",
               linewidths=0.8, zorder=6, label=f"{len(WP)} waypoints")
    for f in FID:
        ax.scatter(f[0], f[1], marker="*", s=420, c="#ffd400", edgecolors="k", zorder=8)
        ax.annotate(f"tag {int(f[3])}", (f[0], f[1]), color="#ffd400", fontsize=10,
                    fontweight="bold", xytext=(6, 6), textcoords="offset points", zorder=9)
    ax.set_aspect("equal")
    ax.set_title("Reconstructed global point cloud (seed frame) — top-down, colour = height",
                 fontsize=14, pad=10)
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
    plt.colorbar(sc, ax=ax, fraction=0.025, pad=0.01).set_label("z [m]")
    ax.legend(loc="upper right", framealpha=0.3)

    ax2 = fig.add_subplot(2, 1, 2); ax2.set_facecolor("#0d1117")
    ax2.scatter(P[:, 0], P[:, 2], c=P[:, 2], s=0.5, cmap="turbo", alpha=0.55, linewidths=0)
    ax2.plot(WP[:, 0], WP[:, 2], "o-", c="#00e5ff", ms=4, lw=1.2, alpha=0.9,
             label="waypoint trail (elevation)")
    ax2.set_aspect("equal")
    ax2.set_title("Side elevation (x–z)", fontsize=13, pad=8)
    ax2.set_xlabel("x [m]"); ax2.set_ylabel("z [m]"); ax2.legend(loc="upper right", framealpha=0.3)

    plt.tight_layout()
    out = os.path.join(outdir, "map_overview.png")
    plt.savefig(out, dpi=130, facecolor="#0d1117", bbox_inches="tight")
    print("wrote", out)

if __name__ == "__main__":
    parent = sys.argv[1] if len(sys.argv) > 1 else "."

    matches = glob.glob(os.path.join(parent, "*.walk"))
    if not matches:
        sys.exit(f"no .walk folder found in {parent}")
    if len(matches) > 1:
        print("warning: multiple .walk folders, using first:", matches)
    walk_dir = matches[0]
    print("using", walk_dir)

    P, WP, FID, g = stitch(walk_dir)

    np.save(os.path.join(parent, "merged_points.npy"), P)
    np.save(os.path.join(parent, "wp_seed.npy"), WP)
    np.save(os.path.join(parent, "fiducials.npy"), FID)
    render(P, WP, FID, g, parent)
