# spot_ros2 wrapper

`rai-opensource/spot_ros2` bridges the Boston Dynamics Spot SDK into ROS 2. It exposes topics, services and actions for control and state, and it is our natural ROS 2 entry point once Spot is repaired. It has one important limitation: it does not wrap GraphNav autonomy. This page covers the technical details, the functionality, and all the packages and topics.

For the underlying SDK it sits on, see [Spot SDK](spot-sdk.md). For the autonomy stack it does not reach, see [GraphNav and Autowalk](graphnav-autowalk.md).

## Technical details

A ROS 2 package suite that wraps the SDK so Spot can be driven and observed from the ROS 2 ecosystem. It targets teleoperation, perception, state and low-level control, not mapped autonomy.

| Attribute | Value |
|---|---|
| Repo | github.com/rai-opensource/spot_ros2 |
| ROS 2 distro | Humble (Ubuntu 22.04) |
| Architectures | ARM64 and AMD64 |
| Spot SDK compatibility | 5.0.1 |
| Maintainers | MASKOR (FH Aachen) and the RAI Institute, with contributions from Linkoping University, derived in part from Clearpath's earlier driver |
| License | Dual: BSD-3 (Clearpath-derived) and MIT (ROS 2 specific) |

We run it via Docker (Ubuntu 22.04 with ROS 2 Humble) because our host is now Ubuntu 24.04 with ROS 2 Jazzy. See the [Jazzy and Humble Docker setup guide](jazzysetup.md).

## Packages

| Package | Role |
|---|---|
| `spot_driver` | Main package. Exposes core Spot functionality over ROS 2. |
| `spot_msgs` | Custom messages, services and interfaces. |
| `bosdyn_msgs` | ROS wrappers of Boston Dynamics protobufs. |
| `spot_description` | URDF and visualization launchfiles. |
| `spot_ros2_control`, `spot_hardware_interface`, `spot_controllers` | Joint-level control through `ros2_control`. |
| `spot_examples`, `spot_common` | Control examples and shared utilities. |

Pulled in as submodules: `spot_wrapper` (the Python layer over the BD SDK that the driver calls), `ros_utilities` (shared ROS helpers), and `spot_description` (URDF). Each package documents its own interfaces in its README.

## Functionality

- Image streams (with compression and stitching options)
- Joint states and joint-level control (`ros2_control`)
- Body movement commands
- Robot state
- E-stop
- Docking

> [!WARNING]
> Autonomy is not wrapped. The driver does not expose GraphNav map recording, localization or mission execution over ROS 2. The autonomy stack (record-then-replay, Autowalk, Missions) is driven through the Boston Dynamics Python SDK directly, or the tablet's Autowalk. A ROS 2 autonomy stack on top of GraphNav would need a bridge layer beyond this driver. A practical alternative is to run our own Nav2 stack on the driver's sensor and odometry feeds.

## Topics, services and actions

ROS 2 nodes communicate in three ways, and the driver uses all three. **Topics** are continuous streams (publish and subscribe), used for sensor feeds and state. **Services** are instant request-and-reply calls, used for one-shot commands like sit or stand. **Actions** are long-running commands that report progress and can be cancelled, used for behaviors like walking to a goal.

All interfaces are namespaced under the robot's name (for example `/<robot>/camera/...`), or sit at the root when the robot is launched unnamed. The exhaustive live list comes from `ros2 topic list`, `ros2 service list` and `ros2 action list` against a running driver. The stable, documented set:

| Category | Representative interfaces |
|---|---|
| **Cameras (topics)** | `camera/<location>/image` (uncompressed), `camera/<location>/compressed`, matching `depth/<location>/image` and `camera_info`. `<location>` is `frontleft`, `frontright`, `left`, `right`, `back` (plus `hand` with an arm). Optional `camera/frontmiddle_virtual/image` (stitched front view). |
| **Lidar (topic, optional)** | `velodyne/points` (only with the EAP lidar module). |
| **State (topics)** | `joint_states`, `odometry`, `tf` and `tf_static`, and the robot health on the `status/` namespace (battery, e-stop, power, system and behavior faults, wifi, feet, mobility params). |
| **Body control (topic)** | `cmd_vel` for velocity teleop of the body. |
| **Simple commands (services)** | `sit`, `stand`, `undock`, `claim`, `release`, `power_on`, `power_off`, plus e-stop and, with an arm, `arm_stow`, `arm_unstow`, `arm_carry`, `open_gripper`, `close_gripper`. |
| **Docking and long commands (services and actions)** | docking and undocking, and longer-running behaviors (robot command, trajectory, and with an arm manipulation) surfaced as ROS 2 actions so they can report feedback and be cancelled. |

Exact names and the full set shift a little with driver version and with which payloads (arm, EAP lidar) are present, so treat the live `ros2 ... list` output as authoritative.

## References

- spot_ros2 driver: https://github.com/rai-opensource/spot_ros2
- spot_driver interfaces README: https://github.com/rai-opensource/spot_ros2/blob/main/spot_driver/README.md
