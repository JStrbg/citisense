#!/bin/sh
sleep 5
sudo hciconfig hci0 name 'Citisense'
sudo hciconfig hci0 noauth
sudo sdptool add SP
sudo hciconfig hci0 piscan
sudo python3 /home/pi/citisense/logger.py &
#sudo python3 /home/pi/citisense/webappl.py &
#sudo python /home/pi/citisense/bluetooth_autoaccept.py &
sudo python3 /home/pi/citisense/bt_transfer_agent.py &
#sudo python /home/pi/citisense/ap_controller.py &
#sudo sh /home/pi/citisense/hub-off.sh &
#sudo hciconfig hci0 leadv 0
#sudo python3 /home/pi/citisense/gatt_server.py &
sleep 1
#sudo hciconfig hci0 leadv 0
sudo service xrdp restart
sleep 2
sudo service xrdp restart
#iptables-restore < /home/pi/citisense/iptables.ipv4.nat
