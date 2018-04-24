import subprocess
from pybtooth import BluetoothManager
bm=BluetoothManager()
while(1):
    devicelist=bm.getConnectedDevices()
    if devicelist == None:
        #subprocess.call(["echo "]
        print("Yo not mama connectus patronum")
    else:
        pritn("Ludde connectish mby")
        print(str(devicelist))
    sleep(1)
