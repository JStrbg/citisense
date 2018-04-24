#!/bin/sh
sleep 5
sudo python3 /home/pi/citisense/klimat.py &
sudo python /home/pi/citisense/bluetooth_autoaccept.py &
sudo python /home/pi/citisense/ap_controller.py &
sudo service xrdp restart
sleep 2
sudo service xrdp restart
iptables-restore < /home/pi/citisense/iptables.ipv4.nat
