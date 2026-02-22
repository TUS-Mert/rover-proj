# How to build rpicam

Run the following commands


`sudo apt install clang meson ninja-build pkg-config libyaml-dev python3-yaml python3-ply python3-jinja2 openssl`
`sudo apt install libdw-dev libunwind-dev libudev-dev libudev-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libpython3-dev pybind11-dev libevent-dev libtiff-dev qt6-base-dev qt6-tools-dev-tools liblttng-ust-dev python3-jinja2 lttng-tools libexif-dev libjpeg-dev pybind11-dev libevent-dev libgtest-dev abi-compliance-checker`

## `libcamera`

`git clone https://github.com/raspberrypi/libcamera.git`

`cd libcamera`

`meson setup build --buildtype=release -Dpipelines=rpi/vc4,rpi/pisp -Dipas=rpi/vc4,rpi/pisp -Dv4l2=true -Dgstreamer=enabled -Dtest=false -Dlc-compliance=disabled -Dcam=disabled -Dqcam=disabled -Ddocumentation=disabled -Dpycamera=enabled`

`ninja -C build install -j2`

**NOTE:** `-j2` means that only 2 cores will be used to build. The RPI5 I'm using has only 2GB RAM which gets overwhelmed easily and closes SSH daemon. This is to prevent that

`sudo ninja -C build install -j2`


## `rpicam-apps`

`git clone https://github.com/raspberrypi/rpicam-apps.git`

`cd rpicam-apps/`

`sudo apt install cmake libboost-program-options-dev libdrm-dev libexif-dev`

`sudo apt install ffmpeg libavcodec-extra libavcodec-dev libavdevice-dev libpng-dev libpng-tools libepoxy-dev `

`sudo apt install qt5-qmake qtmultimedia5-dev`

`meson setup build -Denable_libav=enabled -Denable_drm=enabled -Denable_egl=enabled -Denable_qt=enabled -Denable_opencv=disabled -Denable_tflite=disabled -Denable_hailo=disabled`

`meson compile -C build -j2`

`sudo meson install -C build`


## Updating configs

`sudo ldconfig`


To check if everything is installed correctly:
`rpicam-still --version`


## Updating `/boot/firmware/config.txt`

Add these lines to the bottom of the file:
`dtoverlay=imx219,cam0`
`dtoverlay=imx219,cam1`

Also change `camera-auto-detect=1` to `camera-auto-detect=0`


# References


- Camera manufacutrer:
`If using the latest Bookworm system, you need to configure sudo nano /boot/firmware/config.txt After entering sudo nano /boot/firmware/config.txt, find: Step 1: camera-auto-detect=1 statement, modify to camera_auto_detect=0 If used for Raspberry Pi 4B and Zero series, ignore the first step of modification. Try directly entering the command libcamera-jpeg -o test.jpg to test. If it doesn't work, continue with the second step. ﻿ Step 2: Add at the end of the file: dtoverlay=ov5647 or dtoverlay=imx219 Attention: Choose to add OV5647, IMX219, or IMx708 based on your own camera chip If it cannot be used, you can add dtoverlay=ov5647,cam0 to try it out ctrl+o Enter, then ctrl+x Exit, and enter reboot to restart`

- Askubuntu.com:
`https://askubuntu.com/questions/1542652/getting-rpicam-tools-rpicam-apps-working-on-ubuntu-22-04-lts-for-the-raspber`