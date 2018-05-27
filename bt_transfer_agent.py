from bluetooth import *
import os

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
    
#uuid = "00001101-0000-1000-8000-00805F9B34FB"
#advertise_service(pisocket, "SerialPortService", service_id = uuid, service_classes = [uuid, SERIAL_PORT_CLASS], profiles = [ SERIAL_PORT_PROFILE ], protocols = [OBEX_UUID])

while(1):
    
    client_socket,adr = pisocket.accept()
    while(is_connected(client_socket)):
        description = '\n'
        try:
            while(description[0] == '\n'):
                description = client_socket.recv(1)
        except BluetoothError:
            print("Client disconnected")
        if description[0] == 84: #ASCII T
            print(str(description))
            client_socket.send("T\n")
            print("Done")
        elif description[0] == 83: #ASCII S
            print(str(description))
            send_file(client_socket, "/home/pi/citisense/logs/data_log.csv")
            print("Done")
        elif description[0] == 80:
            print(str(description))
            send_file(client_socket, "/home/pi/citisense/logs/rpi.png")
            print("Done")
        elif description[0] != 70:
            print(str(description))
            try:
                client_socket.send("E\n")
            except BluetoothError:
                print("Disconnected")
            

    client_socket.close()
pisocket.close()
