# Diagnostics script development
**Date:** <font style="color:tomato; font-family:Consolas;">2026-06-10</font>

**Duration:** 8hr

**People:** Ming

**Subsystem:** 🧠 Compute & Mainboard

**Outcome:** ✅ Pass

**Objective:**
>Roll the dev environment back to ROS2 Humble (the `rai-opensource` Spot wrapper targets Humble, not Jazzy), then build a ROS2 node to visualise Spot's joint feedback and pinpoint the frozen `left_hind_x` joint.

**Resources:**
>[`spot_diagnostics` package repo](https://github.com/Kmyming/spot_diagnostics)
>[ROS2 Jazzy setup (the upgrade this reverses)](2026-05-26-ros2-jazzy-setup.md)
>[rai-opensource spot_ros2 wrapper](https://github.com/rai-opensource/spot_ros2)

****
## TL;DR

The earlier in-place upgrade to ROS2 Jazzy (24.04) was a wrong turn — the `rai-opensource` `spot_ros2` wrapper runs on ROS2 Humble. Reverting meant standing up a Humble environment, which forced a drawn-out fight to free disk space on the Ubuntu partition (no spare USB stick, UEFI/Secure Boot blocking every workaround). Once the environment was back, wrote the `spot_diagnostics` package: a single ROS2 node that subscribes to `/joint_states` and serves a self-contained web dashboard plotting all 12 leg joints, so a frozen/no-feedback joint shows up at a glance.

## Work done

#### Environment re-setup (Jazzy → Humble)
The Spot wrapper needs Humble, so the Jazzy box had to make room for a Humble setup. Windows refused to give up the space cleanly, and with no USB stick on hand every recovery route hit a wall:

- **Phase 1 — Forced the Windows shrink.** ~200 GB was free but Windows Disk Management wouldn't shrink the partition (unmovable system files parked at the end). Bypassed it with **MiniTool Partition Wizard**, which relocated the locked files and ran the shrink pre-boot, freeing the unallocated space.
- **Phase 2 — Architecture clash.** Needed GParted to grow the ext4 Ubuntu partition but had no physical USB. Tried a local live env via **UNetbootin**; the ASUS Vivobook threw `0xc000007b` (`ubnldr.mbr`) — modern UEFI rejecting UNetbootin's Legacy BIOS/MBR boot.
- **Phase 3 — Dependency catch-22.** Pivoted to booting a GParted ISO via Ubuntu's GRUB, but the Ubuntu drive was so full it had broken a background `spot-cpp-sdk` install, which jammed `apt` and blocked installing the rescue tool. Force-removed the broken Spot SDK and purged caches to claw back enough space for the ~620 MB GParted Live ISO.
- **Phase 4 — GRUB loop.** Installed `grml-rescueboot`, placed the ISO, ran `update-grub` — but selecting the rescue entry looped straight back to the menu (GRUB chainloader couldn't map the ISO into memory; Secure Boot likely intercepting the chain-load).
- **Phase 5 — "Fake USB" checkmate.** Carved a small 2 GB FAT32 partition out of the unallocated space from within Windows and extracted the GParted files into it, so the motherboard saw it as a UEFI boot drive. Booted into it from the ASUS boot menu (bypassing GRUB entirely), and GParted finally stretched the Ubuntu partition into the remaining ~198 GB.
- **Phase 6 — Cleanup.** Deleted the temp FAT32 partition, removed the GParted ISO from the boot folder, and uninstalled the rescue tool to restore the normal GRUB menu.

#### Wrote the `spot_diagnostics` ROS2 package
A single-node `ament_python` package (`ros2 run spot_diagnostics diagnostics`, entry point `spot_diagnostics.diagnostics:main`) that turns Spot's joint feedback into a live visual. Deliberately built to run with **no dependencies beyond `rclpy`/`sensor_msgs`** — the dashboard is served by Python's stdlib `http.server` and all plotting is done client-side on an HTML canvas, so it drops onto the robot or any dev box with nothing extra to install.

**Data path.** Subscribes to a `JointState` topic (default `/joint_states`, override with `--joint-state-topic` or a `robot_name` that builds `/{robot}/joint_states`) and tracks the 12 leg joints — 4 legs × (`hip_x`, `hip_y`, `knee`). Joint names are normalised (namespace prefix before the last `/` is stripped) and matched through an index map built from each message's `name` array, so it tolerates re-ordered fields, extra joints, and namespaced names. Anything in the expected set that's absent from a message is reported as **missing** rather than crashing.

**Threading model.** The ROS node and the HTTP server run on separate threads and communicate through one lock-guarded snapshot object (`_DashboardState`) that holds the latest JSON payload — the node writes, the web handler reads, no shared mutable state otherwise. The server thread is a daemon, so Ctrl-C cleanly tears everything down. Two ROS timers drive it: a **0.1 s sampler** that appends a position sample to a rolling buffer (capped to the plot window) and refreshes the dashboard snapshot, and a configurable **report timer** (default 0.5 s) that prints a formatted text report to the ROS console — so the tool is also useful headless (`--no-ui`), and `--quiet` silences the console lines if you only want the web view.

**Web dashboard** (daemon thread, default `:8080`; browser polls `/data` every 150 ms):
- Four per-leg **time-series plots** — one canvas per leg, three lines (hip_x / hip_y / knee) over a 30 s rolling window, Y-axis autoscaling to the data in view, redrawn via `requestAnimationFrame`. Each leg header shows the latest value per joint in the line colour.
- A per-joint **feedback table** showing position (rad), velocity, effort, and Δ-from-reference, plus a "changed Xs ago" age and a centre-zero position bar.

**Fault surfacing — the point of the tool.** The reference is captured automatically from the first complete `JointState` message (or supplied via the `reference_positions` param), and each joint is classified live:
- **stale / no-feedback** — position hasn't moved ≥ `change_eps` (`0.01 rad`) within `stale_threshold_s` (`1.0 s`): flagged red, the headline signal that a joint isn't reporting.
- **missing** — joint absent from the message entirely.
- **warn / offset** — |Δ from reference| ≥ `offset_threshold` (`0.25 rad`).
A summary banner lists any missing or no-feedback joints so the failure is unmissable.

**How it's used:** jog each leg by hand and watch which traces move and which stay flat — the frozen `left_hind_x` (in the wrapper's naming, `rear_left_hip_x`) shows up as a flat line with a climbing "changed Xs ago" timer and a red stale flag while its neighbours respond normally. That visually confirms the fault is isolated to one joint's feedback rather than the whole leg or the comms.

**Knobs.** CLI: `--robot-name`, `--joint-state-topic`, `--report-period-s`, `--offset-threshold`, `--ui-host`, `--ui-port`, `--no-ui`, `--quiet`; the same plus `stale_threshold_s`, `change_eps`, and `reference_positions` are exposed as ROS parameters.

## Findings & data
- The Jazzy upgrade was incompatible with the toolchain we actually need — `rai-opensource`'s `spot_ros2` wrapper is a Humble package. The right environment for this robot is **ROS2 Humble**, not Jazzy.
- Root cause of the boot-media struggle: a modern UEFI + Secure Boot laptop with **no physical USB drive** rejects every Legacy/MBR and GRUB-chainload workaround; the only reliable path was presenting a FAT32 partition as a UEFI boot volume.

## Decisions
>**Decision:** Revert from ROS2 Jazzy back to ROS2 Humble for Spot development.

**Why:** The `rai-opensource` `spot_ros2` wrapper targets Humble; staying on Jazzy meant the wrapper (and therefore `/joint_states`) wouldn't run.

**Alternatives considered:** Containerising Humble under Docker on the Jazzy host (as done for the legacy `turtlebot3_ws`) — deferred in favour of a native Humble environment for the Spot work.

>**Decision:** Build the diagnostics tool as a stdlib-only web dashboard rather than a desktop GUI (e.g. rqt/matplotlib).

**Why:** Zero extra dependencies, runs headless on the robot/dev box, and viewable from any browser (including a phone) on the network — convenient for jogging legs by hand at the bench while watching the plots.

## Roadblocks
- Windows would not shrink its partition (unmovable system files) — solved with MiniTool Partition Wizard.
- No physical USB stick + UEFI/Secure Boot blocked UNetbootin (`0xc000007b`) and the GRUB ISO chainload — solved with the FAT32 "fake USB" UEFI boot.
- A full Ubuntu disk had broken `spot-cpp-sdk` and jammed `apt` — cleared by force-removing the broken SDK and purging caches.

## Next steps
- [x] Run `spot_diagnostics` against live `/joint_states` to confirm the frozen `left_hind_x` reads as stale/no-feedback.

## Media
- —
