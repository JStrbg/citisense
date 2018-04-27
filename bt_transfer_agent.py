import bluetooth
import os

def send_file(s,dir):
    size = os.path.getsize(dir)
    file = open(dir,'rb')
    s.send(dir)
    packet = 1
    while(packet):
        packet = file.read(1024)
        s.send(packet)
    file.close()

def is_connected(s):
    try:
        s.getpeername()
        return True
    except:
        return False


while(1):
    pisocket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    port = 1
    pisocket.bind(("",port))
    pisocket.listen(1)

    client_socket,adr = pisocket.accept()
    description = client_socket.recv(1) #log_type, amount of logs
    if description == 'S':
        send_file(client_socket, "/home/pi/citisense/logs/data_log.csv")
    if description == 'P':
        send_file(client_socket, "/home/pi/citisense/logs/rpi.png")

    client_socket.close()
    pisocket.close()
