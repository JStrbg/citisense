from bluetooth import *
import subprocess
import os
import signal

from time import sleep

def send_file(s,dir):

    size = os.path.getsize(dir)
    file = open(dir,'rb')
    #Send filename
    s.send(dir)
    s.send('\n')
    packet = 1
    #Send file in 1KB-parts, maximum for bluetooth.send()
    while(packet):
        packet = file.read(1024)
        try:
            s.send(packet)
        except BluetoothError:
            #Exit if client disconnect
            packet = None
            print("Disconnected")
    file.close()

def is_connected(s):
    try:
        #If client connected, this does not throw error
        s.getpeername()
        return True
    except:
        return False

#Create blutoothsocket with RFCOMM protocol
pisocket = BluetoothSocket( RFCOMM )
#Bind socket to any port
pisocket.bind(("", PORT_ANY))
#Listen for 1 client
pisocket.listen(1)

#Instantiate webapp
webapp = None
#webapp = subprocess.Popen("sudo python3 /home/pi/citisense/webappl.py", shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
#Start with wifi-ap off
wifipower = False
subprocess.call("sudo service hostapd stop",shell=True)
sleep(1)
subprocess.call("sudo ifconfig wlan0 down",shell=True)

def recieve(sock,cnt):
    data = 10 # ASCII \n
    ret = bytearray()
    try:
        #Wait for command as long as client is connected
        while(is_connected(client_socket) and cnt>0):
            data = client_socket.recv(1)
            if data[0] != 10:
                ret.extend(data)
                cnt = cnt - 1
    except BluetoothError:
        print("Client disconnected")
        ret = None
    return ret.decode("ASCII")

while(1):
    #Accept connection, get client socket
    client_socket,adr = pisocket.accept()
    while(is_connected(client_socket)):
        description = recieve(client_socket,1)
        print(str(description))
        if description == 'S': #ASCII S
            # 'S' means send data logs
            
            send_file(client_socket, "/home/pi/citisense/logs/data_log.csv")
            print("Done")

        elif description == 'P':
            # 'P' means send picture
            
            #send_file(client_socket, "/home/pi/citisense/logs/pic.jpg")
            subprocess.call("sudo reboot",shell=True)
            print("Done")
                
        elif description == 'D' : #Ascii D
            year = recieve(client_socket,2)
            print(year)
            month = recieve(client_socket,2)
            print(month)
            day = recieve(client_socket,2)
            print(day)
            hour = recieve(client_socket,2)
            print(hour)
            minute = recieve(client_socket,2)
            print(minute)
            subprocess.call('sudo date +%Y%m%d -s "20'+str(year)+str(month)+str(day)+'"',shell=True)
            subprocess.call('sudo date +%T -s "'+str(hour)+':'+str(minute)+':00"',shell=True)

        elif wifipower and description == 'w': #ASCII w
            # w means turn off wifi and webserver
            os.killpg(os.getpgid(webapp.pid), signal.SIGTERM)
            subprocess.call("sudo service hostapd stop",shell=True)
            sleep(1)
            subprocess.call("sudo ifconfig wlan0 down",shell=True)
            wifipower = False
            
        elif not wifipower and description == 'W': #ASCII W
            # W means start wifi and webserver
            subprocess.call("sudo ifconfig wlan0 up",shell=True)
            subprocess.call("sudo service hostapd start",shell=True)
            sleep(4)
            subprocess.call("sudo service hostapd restart",shell=True)
            sleep(2)
            subprocess.call("sudo service hostapd restart",shell=True)
            webapp = subprocess.Popen("sudo python3 /home/pi/citisense/webappl.py", shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid) 
                
            #subprocess.call("sudo service xrdp restart",shell=True)
            wifipower = True

        else:
            #Unrecognized command
            try:
                client_socket.send("E\n")
            except BluetoothError:
                print("Disconnected")

    client_socket.close()
pisocket.close()
