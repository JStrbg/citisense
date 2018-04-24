import subprocess
from time import sleep
from pybtooth import BluetoothManager
bm=BluetoothManager()
wifipower = True
subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
while(1):
    devicelist=bm.getConnectedDevices()
    if devicelist == []:
        if wifipower:
            subprocess.call(["sudo service hostapd stop",shell=True])
            subprocess.call(["sudo ifconfig wlan0 down",shell=True])
            wifipower = False
    else:
        if not wifipower:
            subprocess.call(["sudo ifconfig wlan0 up",shell=True])
            subprocess.call(["sudo service hostapd start",shell=True])
            wifipower = True
    sleep(1)
