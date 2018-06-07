#Start sequence, carefully timed
sudo sh /home/pi/citisense/hub-off.sh &
sleep 7
sudo hciconfig hci0 name 'Citisense'
sudo hciconfig hci0 noauth
sleep 1
sudo hciconfig hci0 piscan
sleep  1
sudo sdptool add SP
sudo python3 /home/pi/citisense/logger.py &
sleep 2
sudo python3 /home/pi/citisense/wireless_handler.py &
sleep 1
sudo sdptool add SP
sleep 1
#sudo hciconfig hci0 leadv 0
#iptables-restore < /home/pi/citisence/iptables.ipv4.nat
sudo service xrdp restart
sleep 2
sudo service xrdp restart
sudo sdptool add SP
