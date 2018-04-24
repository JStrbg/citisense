import subprocess
from time import sleep
from pybtooth import BluetoothManager
bm=BluetoothManager()
wifipower = True
while(1):
    devicelist=bm.getConnectedDevices()
    if devicelist == []:
        if wifipower:
            subprocess.call("sudo service hostapd stop", shell=True)
            subprocess.call("sudo ifdown wlan0", shell=True)
            wifipower = False
    else:
        if not wifipower:
            subprocess.call("sudo ifup wlan0", shell=True)
            subprocess.call("sudo service hostapd start", shell=True)
            wifipower = True
    sleep(1)
