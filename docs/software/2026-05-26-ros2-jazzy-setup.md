# ROS2 Jazzy setup

**Date:** <font style="color:tomato; font-family:Consolas;">26-05-2026</font>

**Duration:** 5hr

**People:** Ming

**Subsystem:** _e.g. 🧠 Compute & Mainboard

**Outcome:** ✅ Pass

**Objective:**
>Upgrade Ubuntu 22.04 with ROS2 Humble env dual-boot to Ubuntu 24.04 with ROS2 Jazzy env

**Resources:**
>[Ubuntu in-place upgrade and ROS2 Jazzy setup workflow](/data/software/jazzysetup.md)

****
## TL;DR

Did in-place upgrade of current Ubuntu 22.04 & ROS2 Humble setup to Ubuntu 24.04 with ROS2 Jazzy in preparation for future robotic sequence development. 

## Work done
Step-by-step instructions can be found in jazzysetup.md linked above. In-place upgrade chosen over clean install for convenience sake.

#### Phase 0: Back up ROS2 Humble Workspaces on Github
- Back up src folder of ros2 humble workspace onto github
- .gitignore all build, install, log folders

#### Phase 1: Pre-upgrade demolition
- Purge Legacy ROS2 Humble packages
- Purge NVIDIA Drivers

#### Phase 2: OS Upgrade
- Update Current System
- Start Release Upgrade

#### Phase 3: Boot Rescue
Fixing `initramfs` and UUID Mismatch in bootloader resulting in freeze on logo screen and drop into an `(initramfs)` shell.
- Bypass boot freeze
- Lock in permanent fix by rebuilding bootloader once logged in
- Reinstall NVIDIA drivers

#### Phase 4: Native ROS2 Jazzy Installation
- Add repositories and install
- source the environment

#### Phase 5: Docker setup for legacy ROS2 Humble workspace containerisation
Set up Docker to run old `turtlebot3_ws` in an isolated ROS 2 Humble environment with full GPU and GUI support.
- Clean legacy workspace
- Install docker and NVIDIA container toolkit
- setup `.bashrc` Shortcut

## Findings & data
- —

## Decisions
- **Decision:** In-place upgrade to Ubuntu 24.04
  **Why:** Lack of USB drive flashed with Ubuntu 24.04, convenience sake to not have to config setup again and preserve data.
  **Alternatives considered:** Clean install of Ubuntu 24.04

## Roadblocks
- —

## Next steps
- —

## Media
- —
