# Complete Guide: Ubuntu 24.04 In-Place Upgrade, ROS 2 Jazzy, and Humble Docker

This guide covers the end-to-end process of upgrading an existing Ubuntu 22.04 (Jammy) system to 24.04 (Noble), fixing common NVIDIA/NVMe boot errors, installing ROS 2 Jazzy natively, and containerizing a legacy ROS 2 Humble workspace (`turtlebot3_ws`).

---

## Phase 1: Pre-Upgrade Demolition (On Ubuntu 22.04)

To prevent the OS upgrade from failing, you must strip out legacy ROS packages and proprietary graphics drivers before upgrading.

**1. Backup your Workspace**
Push your `~/turtlebot3_ws/src` folder to GitHub or copy it to a physical USB drive. 

**2. Purge Legacy ROS 2 Packages**
```bash
sudo apt-get remove --purge '^ros-humble-.*'
sudo apt-get autoremove
```

**3. Purge NVIDIA Drivers**
```bash
sudo apt-get remove --purge '^nvidia-.*'
sudo apt-get autoremove
```
*Reboot your laptop. The screen resolution will be degraded; this is normal.*

---

## Phase 2: The OS Upgrade

Trigger the core system upgrade to Ubuntu 24.04.

**1. Update Current System**
```bash
sudo apt update
sudo apt upgrade -y
sudo apt dist-upgrade -y
```

**2. Start the Release Upgrade**
```bash
sudo do-release-upgrade
```
*Follow on-screen prompts. Accept defaults to keep current configuration files when asked. Reboot when prompted.*

---

## Phase 3: The Boot Rescue (Fixing `initramfs` and UUID Mismatch)

After upgrading laptops with NVIDIA GPUs and NVMe drives, the system may freeze on the logo screen or drop into an `(initramfs)` shell due to a UUID mismatch in the bootloader.

**1. Bypass the Boot Freeze**
* Force shutdown the laptop by holding the power button.
* Turn it on and repeatedly tap **`Esc`** to enter the GNU GRUB menu.
* Highlight **`Ubuntu`** and press **`e`** to edit.
* Scroll to the line starting with `linux`.
* Delete the `UUID=...` string and replace it with your actual root partition (e.g., `root=/dev/nvme0n1p6`).
* Add `nomodeset` to the end of that same line.
* Press **`Ctrl + X`** to boot.

**2. Lock in the Permanent Fix**
Once logged into the Ubuntu 24.04 desktop, open a terminal and rebuild the bootloader:
```bash
sudo update-grub
sudo update-initramfs -u
```

**3. Reinstall NVIDIA Drivers**
```bash
sudo apt update
sudo ubuntu-drivers autoinstall
```
*Reboot normally. The freeze will be gone, and resolution will be restored.*

---

## Phase 4: Native ROS 2 Jazzy Installation

Install the new ROS distribution directly onto your host system.

**1. Add Repositories and Install**
```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL [https://raw.githubusercontent.com/ros/rosdistro/master/ros.key](https://raw.githubusercontent.com/ros/rosdistro/master/ros.key) -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] [http://packages.ros.org/ros2/ubuntu](http://packages.ros.org/ros2/ubuntu) $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install ros-jazzy-desktop
```

**2. Source the Environment**
Add Jazzy to your `.bashrc` so it loads automatically for new, native projects:
```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Phase 5: Containerizing the Legacy Workspace

Set up Docker to run your old `turtlebot3_ws` in an isolated ROS 2 Humble environment with full GPU and GUI support.

**1. Clean the Legacy Workspace**
You must delete the old Ubuntu 22.04 compiled binaries, or the Docker container will fail to build.
```bash
cd ~/turtlebot3_ws
rm -rf build/ install/ log/
```

**2. Install Docker and NVIDIA Container Toolkit**
```bash
sudo apt install docker.io
sudo usermod -aG docker $USER
# Log out and log back in here to apply the group change

curl -fsSL [https://nvidia.github.io/libnvidia-container/gpgkey](https://nvidia.github.io/libnvidia-container/gpgkey) | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L [https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list](https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list) | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**3. Set Up the `.bashrc` Shortcut**
Add a Bash function to quickly launch your containerized workspace. Run `nano ~/.bashrc`, scroll to the bottom, and paste this:

```bash
# TurtleBot3 ROS 2 Humble Docker Environment
tb3_docker() {
    xhost +local:root
    docker run -it --rm \
      --net=host \
      --gpus all \
      -e DISPLAY=$DISPLAY \
      -e QT_X11_NO_MITSHM=1 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v ~/turtlebot3_ws:/workspace \
      -w /workspace \
      osrf/ros:humble-desktop bash
}
```
**Note:** The `--rm` flag means this container is destroyed when you type `exit`. However, because your workspace is mounted as a volume (`-v`), all your code and compiled files are saved safely to your laptop's hard drive.

Save, exit, and run `source ~/.bashrc`.

---

## Phase 6: Daily Workflow

**1. Launch the Container**
Open a terminal and type:
```bash
tb3_docker
```

**2. Working Inside the Container**

Once the container boots, your terminal will change to a root prompt (`root@hostname:/workspace#`). 

Before running any ROS commands, you must source your workspace:
```bash
source install/setup.bash
```

If you modify C++ files, `setup.py`, or package dependencies, rebuild using:
```bash
colcon build
source install/setup.bash
```

**3. Opening Additional Terminals**

ROS workflows often require multiple terminals. **Do not** run the `docker run` command again, as that will create a completely separate container. Instead, join the existing one:

1. Open a new terminal on your Ubuntu desktop.
2. Find the name of your running container:
   ```bash
   docker ps
   ```
3. Exec into the container using its name (e.g., `cool_hopper`):
   ```bash
   docker exec -it <container_name> bash
   ```
4. Remember to run `source install/setup.bash` in this new terminal.

**4. Workspace Management (Jazzy vs. Humble)**

**The Golden Rule:** One workspace per ROS distribution. Never run a Jazzy build inside your Humble workspace, or it will corrupt the files.

* **For New Native Jazzy Projects:** Create an entirely new workspace on your Ubuntu 24.04 system (e.g., `mkdir -p ~/jazzy_ws/src`) and run `colcon build` natively. Do not use Docker for these.
* **For New Legacy Humble Projects:** If you need a completely separate Humble project (unrelated to TurtleBot3), create a new folder (e.g., `mkdir -p ~/other_humble_ws/src`). To run it, use the same Docker command from Step 1, but update the volume mount flag to `-v ~/other_humble_ws:/workspace`.

