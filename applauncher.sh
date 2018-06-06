#!/bin/sh
sleep 5
sudo hciconfig hci0 name 'Citisense'
sudo hciconfig hci0 noauth
sudo hciconfig hci0 piscan
sleep  1
sudo sdptool add SP
sudo python3 /home/pi/citisense/logger.py &
sudo python3 /home/pi/citisense/webappl.py &
#sudo python /home/pi/citisense/bluetooth_autoaccept.py &
sleep 2
sudo python3 /home/pi/citisense/bt_transfer_agent.py &
sleep 1
sudo sdptool add SP
sudo sh /home/pi/citisense/hub-off.sh &
#sudo python3 /home/pi/citisense/gatt_server.py &
sleep 1
#sudo hciconfig hci0 leadv 0
#iptables-restore < /home/pi/citisence/iptables.ipv4.nat
sudo service xrdp restart
sleep 2
sudo service xrdp restart
sudo sdptool add SP
