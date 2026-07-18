# Spot software stack literature review (SDK, GraphNav/Autowalk, spot_ros2)

**Date:** <font style="color:tomato; font-family:Consolas;">18-07-2026</font>

**Duration:** 6hr

**People:** Ming

**Subsystem:** 🧠 Compute & Mainboard

**Outcome:** ✅ Complete (living document)

**Objective:**
>Review and document Spot's software stack so we know what each interface can do and what an autonomous inspection routine needs. Cover the Boston Dynamics Python SDK, the GraphNav and Autowalk autonomy stack, and the `spot_ros2` ROS 2 wrapper, then write it up as reference docs in the repo.

**Resources:**
>[Consolidated review](../subsystems/software/spot-software-litreview.md)
>[data/spot-sdk.md](../../data/spot-sdk.md) · [data/graphnav-autowalk.md](../../data/graphnav-autowalk.md) · [data/spot-ros2-wrapper.md](../../data/spot-ros2-wrapper.md) · [data/sdk-vs-autowalk-vs-ros2.md](../../data/sdk-vs-autowalk-vs-ros2.md)
>[Spot Python SDK docs](https://dev.bostondynamics.com/docs/python/readme)
>[Concepts > Autonomy (GraphNav)](https://dev.bostondynamics.com/docs/concepts/autonomy/readme)
>[rai-opensource spot_ros2](https://github.com/rai-opensource/spot_ros2)
>[Spot Robot Development Tutorial (video)](https://www.youtube.com/watch?v=KDvh__1Y0fI)

****
## TL;DR

Reviewed the three ways to drive Spot, all sitting on one gRPC and protobuf API: the Python SDK (lowest level, full capability), the tablet's Autowalk and GraphNav autonomy (no-code, built on the same services), and the `spot_ros2` wrapper (a subset for teleop, perception and state, with no GraphNav autonomy). Confirmed the licensing model is an allowlist, not tiers: only the Joint Control and Choreography APIs need a special-permission license, and everything else including autonomy is standard. Our Enterprise license covers the dock, GraphNav and Orbit. Wrote it up as four `data/` knowledge pages plus a consolidated report in `docs/subsystems/software/`.

## Work done

#### Ingested the Spot development tutorial video
Watched three segments (gRPC and proto definitions, protobuf implementation, and using the SDK) from the Boston Dynamics community tutorial. The video gave a clean plain-language framing of gRPC, RPCs, protobufs, services, messages, clients and the lease acquire-versus-take idea, which cross-checked cleanly against the official SDK docs. Will continue watching the next session and see what we can do with the SDK.

#### Reviewed the SDK, autonomy and ROS 2 sources
Went through the BD Python SDK docs and repo (architecture, the mandatory client flow, the example catalog, licensing), the full Concepts > Autonomy section (GraphNav map model, localization and initialization, missions and Autowalk, safety and integrations), and the `spot_ros2` driver plus `spot_driver` READMEs (packages, submodules, and the topics, services and actions it exposes).

#### Wrote the reference docs
Summarised findings and produced four `data/` knowledge pages following the existing data-page style (`spot-sdk.md`, `graphnav-autowalk.md`, `spot-ros2-wrapper.md`, `sdk-vs-autowalk-vs-ros2.md`) and a concise seven-section consolidated report (`docs/subsystems/software/spot-software-litreview.md`) that summarises each area and links out to the data pages for depth using my trusted buddy claude. The SDK page carries a full annotated `hello_spot` worked example that shows the entire code flow from connect to motion to shutdown.

## Findings & data
- **One API under everything.** Spot runs gRPC services defined by protobufs under `bosdyn/api`. The SDK is the superset, `spot_ros2` and Autowalk are consumers of the same services.
- **Mandatory flow before motion:** create SDK and robot, authenticate, time-sync, E-Stop to none, acquire lease, power on. The lease and E-Stop keepalives have to stay in scope for the whole session or control is lost.
- **Licensing is an allowlist.** Only Joint Control and Choreography need a special-permission license. Autonomy (GraphNav, Autowalk, Missions) is standard. Our robot has the Spot Enterprise license (dock, GraphNav, Orbit).
- **spot_ros2 gap.** It exposes teleop, images, `/joint_states`, state, e-stop and docking, but does not wrap GraphNav autonomy. A ROS 2 autonomy stack would run its own Nav2 on the driver feeds or need a GraphNav bridge.
- **GraphNav maps are not persistent across reboot** and have to be downloaded before power-cycling. Initialization is easiest with 146 mm AprilTag fiducials.

## Decisions
>**Decision:** For an autonomous inspection routine, plan Autowalk first, then drop to the SDK when needed.

**Why:** We have very little time left in the project so developing an entire custom autonomy sequence using the SDK may not be possible. Will focus more on creating a linear autonomous routine with the AutoWalk, and perharps running a modified example as proof of repair first, and scope custon autonomous routine development using the SDK as a future scope and application of our project.

## Roadblocks
- Time left for this project is limited and may not be able to develop a custom autonomy sequence using the SDK.

## Next steps
- [ ] Once the hind hip-X faults settle, record a fiducial-anchored Autowalk inspection loop (place 146 mm fiducials, drive and record, attach actions, dock).
- [ ] Run a modified SDK example to demonstrate a simple autonomous routine (e.g., drive to a waypoint, take a picture, return to dock).

## Media
- [Spot Robot Development Tutorial](https://www.youtube.com/watch?v=KDvh__1Y0fI) (source for the gRPC, proto and lease walkthrough)
