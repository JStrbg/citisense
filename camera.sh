#!/bin/bash
DATE=$(date +"%Y-%m-%d_%H-%M")
sudo raspistill --timeout 1  -rot 270 -n -awb auto -drc med --exposure auto -o /home/pi/citisense/logs/$DATE.jpg
#https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
