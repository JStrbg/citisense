#!/bin/sh
sleep 5
sudo python3 /home/pi/citisense/logger.py &
sudo python3 /home/pi/citisense/webappl.py &
sudo python /home/pi/citisense/bluetooth_autoaccept.py &
sudo python /home/pi/citisense/bt_transfer_agent.py &
#sudo python /home/pi/citisense/ap_controller.py &
sudo sh /home/pi/citisense/hub-off.sh &
sudo service xrdp restart
sleep 2
sudo service xrdp restart
#iptables-restore < /home/pi/citisense/iptables.ipv4.nat
