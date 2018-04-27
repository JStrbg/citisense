#!/bin/bash.sh
echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/bind #power on USB
sleep 8
sudo cp -n /home/pi/citisense/logs/* /media/pi/KINGSTON/
sudo umount /media/pi/KINGSTON/
echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/unbind  #power off usb
sleep 2
