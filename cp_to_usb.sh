#!/bin/bash.sh
sudo /home/pi/citisense/hub-ctrl -h 0 -P 2 -p 1 #power on USB
sudo mkdir /media/pi/KINGSTON/
sudo mount /dev/sda1 /media/pi/KINGSTON/
sudo cp /home/pi/citisense/logs/* /media/pi/KINGSTON/
sudo umount /media/pi/KINGSTON
sudo /home/pi/citisense/hub-ctrl -h 0 -P 2 -p 0 #power off usb
