# Spot Software Stack: Literature Review

| | |
|---|---|
| **Subsystem** | 🧠 Compute & Mainboard / Software |
| **Status** | 🔧 Living document, current focus is software SDK exploration |
| **Scope** | Boston Dynamics Python SDK, GraphNav and Autowalk autonomy, and the `spot_ros2` ROS 2 wrapper |
| **Authors** | Ming |

---

## Summary

This is the concise summary of what we have reviewed so far on Spot's software, and it is the entry point for the detailed knowledge pages in [`data/`](../). Spot is a black box with no SSH, so everything we do goes over the network as gRPC calls to services the robot runs. There are three ways to drive it, all sitting on that one API: the Python SDK (lowest level and full capability), the tablet's Autowalk and GraphNav autonomy stack (no-code, built on the SDK's services), and the `spot_ros2` ROS 2 wrapper (a subset for teleop, perception and state, with no GraphNav autonomy). Our robot carries the Spot Enterprise license, so the self-charging dock, GraphNav autonomy and Orbit are available, and only the Joint Control and Choreography APIs would need a separate special-permission license.

Each numbered section below is a short overview. Follow the link at the end of the section for the full treatment.

## 1. Software stack and architectural overview

Everything is gRPC services defined by Protocol Buffer messages under `bosdyn/api`. The robot runs the services, and each consumer is a gRPC client of those services. The Python SDK is the reference client, but the protocol is language agnostic.

```
Spot (onboard): gRPC services (bosdyn/api protos)
   RobotCommand, RobotState, Image, Lease, Estop, GraphNav, Mission, Docking, ...
        ^              ^                         ^
        |              |                         |
   Python SDK     spot_ros2 driver        Tablet Autowalk / GraphNav
   (full)         (subset over ROS 2)     (no-code autonomy)
        ^
        |
   Orbit (Enterprise remote ops) sits above all three
```

- The **SDK** is the full, lowest-level surface. Everything Spot can do is reachable here.
- **spot_ros2** wraps a subset of the SDK into ROS 2 topics, services and actions.
- **Autowalk and GraphNav** is the tablet-facing autonomy layer, built on the same services.
- **Orbit** is the Enterprise remote-operations web product above all three.

Full detail: [data/software/spot-sdk.md](spot-sdk.md).

## 2. Key terms

| Term | Meaning | Spot example |
|---|---|---|
| **gRPC** | Google Remote Procedure Call. Robot is the server, our app is the client. | robot on WiFi at `192.168.80.3` |
| **RPC / method** | One callable operation on a service. A client method that is really a remote call. | `GetRobotState` |
| **Protobuf (`.proto`)** | Interface definition. Declares services and messages, fixes the interface not the implementation. | `bosdyn/api/*.proto` |
| **Service** | A named group of RPCs the robot offers. | `RobotState`, `Image` |
| **Message** | Typed input or output of an RPC, built from fields. | `RobotStateRequest`, `BatteryState` |
| **Client** | SDK class that talks to one service, obtained from the `Robot` object. | `RobotStateClient` |
| **Object** | A built message instance we pass around. | a `RobotCommand` from `RobotCommandBuilder` |

The whole model in three lines: a `.proto` declares a service and its RPCs, the SDK gives us a client for that service, and calling a method on the client runs the RPC. Boston Dynamics splits each area into a `*_service.proto` (the service and RPCs) and a data `.proto` (the message types). Term-by-term detail with the Greeter example and code: [data/software/spot-sdk.md](spot-sdk.md).

## 3. Mandatory startup procedure

Order matters. Each step gates the next, and nothing moves until all are done.

| Step | Why it is mandatory |
|---|---|
| Create SDK and Robot | build the SDK object, point it at the robot IP |
| Authenticate | username, password and robot IP unlock most services |
| Time-sync | commands carry validity windows keyed to the robot clock |
| E-Stop | gates motor power, has to move from cut to none before power-on |
| Lease | exclusive-control token, taken with `acquire` or stolen with `take` |
| Power on | motors are off until explicitly powered |

The lease and E-Stop keepalives have to stay in scope for the whole session. If either falls out of scope the robot times out and control is lost. This is the most common cause of a program appearing to randomly lose Spot. Full flow with code: [data/software/spot-sdk.md](spot-sdk.md).

## 4. One full worked example (hello_spot)

`hello_spot` is the smallest example that runs the whole flow end to end:

1. **Connect** (create SDK, create robot at the IP, authenticate, time-sync).
2. **E-Stop** endpoint plus keepalive.
3. **Lease** acquire plus keepalive.
4. **Power on** the motors.
5. **Command** motion: build a command object with `RobotCommandBuilder`, send it through the command client (the `RobotCommand` RPC, which returns a command id to poll).
6. **Read a sensor**: capture from a camera through `ImageClient`.
7. **Shut down**: sit, then power off. Keepalives release as they leave scope.

Every step maps back to a key term in section 2. The gripper-open case is the same shape with a different builder (build a gripper command, set the open fraction to 1.0, send it). Multiple simultaneous actions are wrapped into one synchronized command. Annotated source: [data/software/spot-sdk.md](spot-sdk.md).

## 5. GraphNav and Autowalk

GraphNav is Spot's mapping, localization and autonomous-navigation system. The model is record-then-replay: an operator drives Spot to record a map, and any robot can then replay it autonomously.

- **Map structure.** A locally consistent graph, not a global metric map. Waypoints (about every 2 m), edges (directed transforms with annotations like stair mode), snapshots (sensor data on a waypoint), and anchorings (waypoint poses in a seed frame). Maps are not persistent across reboot and have to be downloaded before power-cycling.
- **Localization and initialization.** Initialization sets the first pose, easiest via 146 mm AprilTag fiducials, also search-based or scan-match. Localization then maintains it at 2 Hz or more. In feature deserts it degrades and can go `STATUS_LOST`.
- **Navigation.** Three RPCs: `NavigateTo` (fewest-edges route), `NavigateRoute` (client-specified path), `NavigateToAnchor` (approximate seed-frame or GPS coordinates).
- **Service layer.** Missions are behavior trees (sequence, selector, retry, blackboard variables, `BosdynNavigateTo`, `RemoteGrpc` for custom logic). Autowalk is a higher, linear "go here, do this" abstraction compiled into a mission, and is what the tablet produces.
- **Safety and integrations.** Area callbacks (doors, elevators), hazard avoidance, AutoReturn on comms loss, directed exploration as a last resort, docking and self-charge, and GPS via a payload.

Full detail: [data/software/graphnav-autowalk.md](graphnav-autowalk.md).

## 6. spot_ros2 wrapper

`rai-opensource/spot_ros2` bridges the SDK into ROS 2 for teleoperation, perception, state and low-level control. It does not wrap GraphNav autonomy.

- **Target.** ROS 2 Humble (Ubuntu 22.04), ARM64 and AMD64, tracking Spot SDK 5.0.1. Maintained by MASKOR and the RAI Institute. We run it via Docker because our host is Ubuntu 24.04 and ROS 2 Jazzy.
- **Packages.** `spot_driver` (core), `spot_msgs`, `spot_common`, `spot_examples`, and the `ros2_control` trio (`spot_ros2_control`, `spot_hardware_interface`, `spot_controllers`). Submodules `spot_wrapper`, `ros_utilities`, `spot_description`.
- **Interfaces.** ROS 2 nodes talk in three ways, and the driver uses all three:
  - *Topics* (continuous streams): camera images (raw and compressed), depth and `camera_info` (calibration), an optional stitched front view, and `velodyne/points` if the EAP lidar is fitted. Robot state comes as `joint_states` (joint angles), `odometry` (estimated position), `tf` (coordinate frames), and health streams under `status/` (battery, e-stop, power, faults). The driver also listens on `cmd_vel` for velocity commands to walk the body.
  - *Services* (instant request and reply): `sit`, `stand`, `claim` and `release` (grab or drop the control lease), `power_on` and `power_off`, e-stop, docking, and arm and gripper commands if an arm is fitted.
  - *Actions* (long-running, with progress feedback and cancel): walking to a goal, trajectories, and manipulation.

  Every name is prefixed with the robot's name (for example `/spot/joint_states`), and the exact set depends on driver version and payloads, so the source of truth is `ros2 topic list`, `ros2 service list` and `ros2 action list` on the running robot. Full breakdown: [data/software/spot-ros2-wrapper.md](spot-ros2-wrapper.md).
- **Key gap.** No GraphNav map recording, localization or missions over ROS 2. A ROS 2 autonomy stack would run its own Nav2 on the driver's sensor and odom feeds, or need a bridge to GraphNav.

Full detail: [data/software/spot-ros2-wrapper.md](spot-ros2-wrapper.md).

## 7. SDK vs Autowalk vs spot_ros2

| Surface | Best for | Autonomy | Coding |
|---|---|---|---|
| **SDK** | the superset, custom missions, arm, reactive control | full (GraphNav, Missions, Autowalk) | Python or C++ |
| **spot_ros2** | reusing the ROS 2 and Nav2 ecosystem, base control and perception | none over ROS 2 (bring our own Nav2) | ROS 2 |
| **Autowalk** | fastest no-code linear inspection with dock and self-charge | linear replay only, no branching | none |

Bottom line for our robot (Enterprise license): Autowalk gets a fiducial-anchored inspection loop running with no code and no special license, and we drop to the SDK when we need branching, reactive behavior or custom perception. spot_ros2 is the route to reuse ROS 2 and Nav2 experience but does not give us GraphNav. Full capability matrix and the license detail: [data/software/sdk-vs-autowalk-vs-ros2.md](sdk-vs-autowalk-vs-ros2.md).

## References

- Spot Python SDK docs: https://dev.bostondynamics.com/docs/python/readme
- spot-sdk repo: https://github.com/boston-dynamics/spot-sdk
- Concepts > Autonomy (GraphNav): https://dev.bostondynamics.com/docs/concepts/autonomy/readme
- spot_ros2 driver: https://github.com/rai-opensource/spot_ros2
- Spot Robot Development Tutorial (gRPC, proto and lease walkthrough): https://www.youtube.com/watch?v=KDvh__1Y0fI
