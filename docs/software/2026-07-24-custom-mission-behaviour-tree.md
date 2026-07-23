# Custom mission behaviour tree from a recorded autowalk

**Date:** <font style="color:tomato; font-family:Consolas;">24-07-2026</font>

**Duration:** 7h

**People:** Ming

**Subsystem:** 🧠 Compute & Mainboard (autonomy / software)

**Outcome:** ✅ Complete — a hand-built Mission behaviour tree, with operator-chosen branching and scripted actions, runs on Spot from a recorded autowalk.

**Objective:**
>Turn a recorded Spot autowalk into a Mission behaviour tree we fully control — navigate the route, branch on operator input, inject custom body-pose actions — and run it via the Mission service.

**Resources:**
>[Behaviour-tree build write-up](../../data/software/autowalk-mission-behaviour-tree.md)
>[elab_behavior_tree.py](../../spot-autowalk-collections/elab_behavior_tree.py)
>[Spot SDK architecture](../../data/software/spot-sdk.md)

****
## TL;DR

We converted the recorded `elab test 2` autowalk into a **hand-built Mission behaviour tree** that navigates the route, asks the operator which dance to perform (Prompt + Switch), performs scripted body poses, and loops — and ran it on Spot. The load-bearing finding: **recorded body poses are stored in the GraphNav map edges, not the Walk elements**, which explains why some poses reproduced from navigation and others did not.

## Work done

#### Built the mission behaviour tree
- Wrote `spot-autowalk-collections/elab_behavior_tree.py`: node helpers (`command_node`, `navigate_node`, `pose_node`, `sleep_node`, `sequence_node`), two scripted dances, a Prompt+Switch conditional, hand-built `BosdynNavigateTo` navigation, GraphNav map upload + fiducial localisation, and load/play through `MissionClient`.
- Chose to **hand-build the navigation** rather than `CompileAutowalk`, because a compiled autowalk is one opaque block we cannot splice branching into. Hand-building let us interleave the operator prompt and the custom actions.
- Wrapped the patrol in a `Repeat` loop; the operator answers the dance prompt from the console (or the tablet).

#### Debugged the full pipeline
Worked through every failure from connection to a running mission: registering `MissionClient` (not a standard client), extracting destination waypoints from `navigate_route` targets, the empty-`default_child` compile error, `Sleep.seconds` units, and `footprint_R_body` taking an `EulerZXY`.

#### Investigated the recorded-pose behaviour
The recorded crawl-under-table reproduced from navigation, but the recorded pitch-back did not, and no pose could be read out of the elements. Decoding the walk and the graph explained why (Findings).

## Findings & data

- **`MissionClient` must be registered explicitly** (`create_standard_sdk(name, [MissionClient])`) — it lives in `bosdyn-mission`, not the standard client set.
- **Recorded targets use `navigate_route`** (a list of waypoints), so the destination is the last waypoint; `.navigate_to.destination_waypoint_id` returns empty and the mission fails to compile.
- **Every element's `robot_body_pose.target_tform_body` is identity** (rotation w≈1, others ≈1e-5). The Walk elements do **not** store the recorded poses.
- **The recorded body poses live in the GraphNav map edges**, in `Edge.Annotations.mobility_params.body_control.base_offset_rt_footprint`:
  - three edges around the Pose-1 waypoint set body height **z = −0.125 m** (the crawl) and disable body-obstacle avoidance (`obstacle_params.disable_vision_body_obstacle_avoidance`) — which is why replay goes under the table instead of refusing it;
  - one edge sets a body **pitch of ~41°** (rotation quaternion y = 0.351);
  - every other edge is identity.
- **An edge's body pose only fires when the robot traverses that edge.** `BosdynNavigateTo` reproduced the crawl (our route crossed those edges) but not the pitch (its edge was off-route). The full autowalk reproduces everything because it follows the exact recorded edge sequence.
- **Fix:** `edge_pose_node` reads a pose straight off the edge's `body_control` (position z + rotation quaternion → `EulerZXY`) and commands it as a stand, so a recorded pose can be struck at any waypoint without running the route.

Full explanation, behaviour-tree diagrams, code walkthrough, and the Element/Edge field appendices: [behaviour-tree write-up](../../data/software/autowalk-mission-behaviour-tree.md). The build itself: [elab_behavior_tree.py](../../spot-autowalk-collections/elab_behavior_tree.py).

## Decisions

>**Decision:** Hand-build the navigation with `BosdynNavigateTo` nodes and script the body-pose actions, rather than compiling the autowalk.

**Why:** A compiled autowalk is one opaque block that cannot be spliced, so it cannot carry the operator prompt / conditional branching we want. Hand-building gives full control of the tree; scripting the poses (or extracting them with `edge_pose_node`) sidesteps the fact that the elements store no usable pose.

**Alternatives considered:** `CompileAutowalk` (reproduces everything exactly but no branching); running the recorded route via `BosdynNavigateRoute` to reproduce the edge poses (works, but ties the demo to the exact recorded path).

## Media

Custom behaviour tree running on Spot (navigate → operator-chosen dance → crawl → pitch → loop):

<div style="display: flex; justify-content: center; margin: 2em 0;">
  <video width="360" height="480" controls>
    <source src="../assets/elab-custom-mission.mov" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>

The recorded `elab test 2` autowalk this was built from is at `../assets/autowalk-elab-indoor.mov`.
