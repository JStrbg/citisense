from bluetooth import *
import subprocess
import os
import signal

from time import sleep

def send_file(s,dir):
    size = os.path.getsize(dir)
    file = open(dir,'rb')
    s.send(dir)
    s.send('\n')
    packet = 1
    while(packet):
        packet = file.read(1024)
        try:
            s.send(packet)
        except BluetoothError:
            packet = None
            print("Disconnected")

    file.close()

def is_connected(s):
    try:
        s.getpeername()
        return True
    except:
        return False

pisocket = BluetoothSocket( RFCOMM )

pisocket.bind(("", PORT_ANY))
pisocket.listen(1)
wifipower = True
webapp = subprocess.Popen("sudo python3 /home/pi/citisense/webappl.py",shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
#webapp = subprocess.Popen(['sudo',"python3","/home/pi/citisense/webappl.py"],shell=False)
#subprocess.call("sudo ifconfig wlan0 down",shell=True)
#sleep(1)
# subprocess.call("sudo service hostapd stop",shell=True)

while(1):

    client_socket,adr = pisocket.accept()
    while(is_connected(client_socket)):
        description = '\n'
        try:
            while(description[0] == '\n' and is_connected(client_socket)):
                description = client_socket.recv(1)
        except BluetoothError:
            print("Client disconnected")
        if description[0] == 84: #ASCII T
            print(str(description))
            subprocess.call("sudo service hostapd restart",shell=True)
            client_socket.send("T\n")
            print("Done")
        elif description[0] == 83: #ASCII S
            print(str(description))
            send_file(client_socket, "/home/pi/citisense/logs/data_log.csv")
            print("Done")
        elif description[0] == 80:
            print(str(description))
            #send_file(client_socket, "/home/pi/citisense/logs/rpi.png")
            print("Done")
            subprocess.call("sudo sync",shell=True)
            subprocess.call("sudo reboot",shell=True)
        if wifipower and description[0] == 119:
            os.killpg(os.getpgid(webapp.pid), signal.SIGTERM)
            subprocess.call("sudo service hostapd stop",shell=True)
            sleep(1)
            subprocess.call("sudo ifconfig wlan0 down",shell=True)
            wifipower = False
        if not wifipower and description[0] == 87: 
            subprocess.call("sudo ifconfig wlan0 up",shell=True)
            subprocess.call("sudo service hostapd start",shell=True)
            sleep(4)
            subprocess.call("sudo service hostapd restart",shell=True)
            sleep(2)
            subprocess.call("sudo service hostapd restart",shell=True)
            webapp = subprocess.Popen("sudo python3 /home/pi/citisense/webappl.py", shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
            wifipower = True
        elif description[0] != 70:
            print(str(description))
            try:
                client_socket.send("E\n")
            except BluetoothError:
                print("Disconnected")

    client_socket.close()
pisocket.close()
