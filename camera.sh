#!/bin/bash
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
sudo raspistill --timeout 1 -vf -hf -n -awb auto -drc med --exposure auto -o /media/pi/KINGSTON/$DATE.jpg
#https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
