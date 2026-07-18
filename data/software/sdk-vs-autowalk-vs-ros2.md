# SDK vs Autowalk vs spot_ros2

Three ways to drive Spot, all sitting on one gRPC and protobuf API. This page is the high-level comparison and the capability matrix. The depth for each surface lives in [Spot SDK](spot-sdk.md), [GraphNav and Autowalk](graphnav-autowalk.md), and [spot_ros2 wrapper](spot-ros2-wrapper.md).

## High-level comparison

| | **Spot SDK (Python/gRPC)** | **spot_ros2 (ROS 2 driver)** | **Autowalk (tablet / CompileAutowalk)** |
|---|---|---|---|
| Level | Lowest and full | Mid, ROS 2 integration | Highest, low-code |
| Motion | Raw command, trajectory, velocity, pose | Body movement and `ros2_control` joints | Walks a pre-recorded route |
| Perception and state | All images, robot and joint state, world objects | Image streams, `/joint_states`, robot state | Used internally |
| **Autonomy** | **Full.** GraphNav record and replay, Missions, Autowalk compile, docking | **None.** GraphNav and missions not wrapped | **Is** autonomy. Record then replay plus actions |
| Logic | Arbitrary code plus behavior-tree Missions | Whatever we code in ROS 2 | Linear "go here, do this" plus failure behaviors |
| Best for | Custom sequences, autonomy, arm, payloads | Reusing the ROS 2 and Nav2 ecosystem | Fastest repeatable inspection, no code |

All three run on the same base: the mandatory auth, time-sync, E-Stop, lease, power-on flow (see [Spot SDK](spot-sdk.md)). Autowalk and spot_ros2 just hide it.

## Capability matrix

> [!NOTE]
> Our robot has the **Spot Enterprise** license, so the self-charging dock, GraphNav autonomy, and Orbit remote fleet and inspection ops are all available. Enterprise is a purchase tier. It does not grant the two controlled-access APIs (Joint Control, Choreography), which still need a separate special-permission license.

Legend: ✅ full · ⚠ partial or indirect · ❌ not available.

| Capability | SDK (Python/gRPC) | spot_ros2 (ROS 2) | Autowalk (tablet) |
|---|:---:|:---:|:---:|
| Basic mobility (stand, sit, pose, walk) | ✅ programmatic | ✅ teleop and body cmds | ⚠ recorded route only |
| Precise trajectory, velocity, body pose | ✅ | ✅ | ❌ |
| Low-level joint control (Joint Control API) | ✅ special-perm | ⚠ `ros2_control` may route through it | ❌ |
| Cameras and images (5 fisheye and 5 depth) | ✅ | ✅ streams | ⚠ image-capture actions |
| Robot and joint state | ✅ | ✅ `/joint_states`, state | ❌ |
| E-Stop, lease, power, time-sync | ✅ | ✅ | ✅ implicit |
| Docking and self-charge (Enterprise dock) | ✅ `DockingClient` | ✅ | ✅ dock config and auto-charge |
| GraphNav map recording | ✅ | ❌ | ✅ tablet record |
| GraphNav navigation (replay) | ✅ `NavigateTo`, `Route`, `Anchor` | ❌ | ✅ replay |
| Missions (behavior trees) | ✅ full BT and `RemoteGrpc` | ❌ | ⚠ linear only (compiled) |
| Area callbacks (doors, elevators, crosswalks) | ✅ implement the service | ❌ | ✅ attach if a callback service exists |
| Hazard avoidance and no-go regions | ✅ | ❌ | ⚠ some via tablet |
| AutoReturn (comms loss) | ✅ | ❌ | ✅ enable |
| Directed exploration | ✅ toggle | ❌ | ✅ "drive around obstacles" |
| Arm manipulation (arm hardware) | ✅ | ⚠ partial | ⚠ arm actions |
| Custom perception and ML (network compute bridge) | ✅ | ⚠ our own ROS 2 nodes | ❌ |
| Data acquisition and logging | ✅ | ⚠ | ✅ capture actions |
| Reactive and closed-loop logic | ✅ | ✅ our code | ❌ fixed sequence |
| Choreography | ✅ special-perm | ❌ | ❌ (separate Choreographer app) |
| ROS 2 ecosystem (Nav2, rviz, tf2) | ❌ | ✅ native | ❌ |
| Coding required | Python or C++ | ROS 2 (Py or C++) | none (tablet) |

**How to read it.** The SDK is the superset. Every column that is ✅ here is reachable in the SDK, since it is what the others are built on. spot_ros2 covers base control plus perception and state and adds the ROS 2 ecosystem (Nav2, rviz, tf2), but exposes no GraphNav autonomy. Autowalk is the no-code path to linear autonomous inspection (record, then replay plus actions plus dock), but cannot do reactive logic, branching missions, or raw programmatic control. Orbit (Enterprise) sits above all three for remote operation and data review, and is a separate web product rather than one of these client interfaces.

## Licensing: an allowlist, not tiers

The SDK docs flag exactly two controlled-access APIs that need a special-permissions license from Boston Dynamics: the **Joint Control API** and the **Choreography service**. Everything else, including the whole autonomy stack (GraphNav, Autowalk, Missions), carries no license or permission statement and is standard. So Autowalk is not a way to get autonomy the SDK cannot do. It is just the no-code front end to the same capability.

The one caveat for us is that spot_ros2's `ros2_control` joint-level control may route through the Joint Control API. That is the only place a special license might affect our work, and it is worth checking on the robot. A robot's actually-enabled features can be read at runtime with `LicenseClient.get_feature_enabled([...])`.

## Running an autonomous inspection routine

Both routes run on our license with no special permissions needed.

- **Route A, Autowalk (fastest working inspection).** Healthy walking robot, place AprilTag fiducials (146 mm) at the start and feature-poor areas, drive and record the route on the tablet, attach inspection actions and area callbacks, optionally add dock and AutoReturn, then initialize to a fiducial and replay. Maps are not persistent across reboot, so download them.
- **Route B, SDK-programmed (full control).** The mandatory client flow, then either simple `RobotCommandBuilder` sequences, or mapped autonomy through the GraphNav recording service plus `GraphNavClient` (localize, then `NavigateTo` or `NavigateRoute`) plus `MissionClient` (`LoadMission`, `PlayMission`).

Cross-cutting needs: good localization (features or fiducials), initialization before navigation, "lost" handling, and version alignment (spot_ros2 tracks SDK 5.0.1, robot firmware was 5.1.6).

## References

- Joint Control API (special-permissions license): https://dev.bostondynamics.com/docs/concepts/joint_control/README.html
- Choreography service (special-permissions license): https://dev.bostondynamics.com/docs/concepts/choreography/README
- GraphNav autonomy concepts (no license mention): https://dev.bostondynamics.com/docs/concepts/autonomy/readme
