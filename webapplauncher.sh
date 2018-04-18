#!/bin/sh
sleep 5
sudo python3 /home/pi/citisense/klimat.py &
sudo service xrdp restart
sleep 2
sudo service xrdp restart
