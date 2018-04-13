import pigpio
import math
from time import sleep
CCS811_ADDRESS  =  0x5b

CCS811_STATUS = 0x00
CCS811_MEAS_MODE = 0x01
CCS811_ALG_RESULT_DATA = 0x02
CCS811_RAW_DATA = 0x03
CCS811_ENV_DATA = 0x05
CCS811_NTC = 0x06
CCS811_THRESHOLDS = 0x10
CCS811_BASELINE = 0x11
CCS811_HW_ID = 0x20
CCS811_HW_VERSION = 0x21
CCS811_FW_BOOT_VERSION = 0x23
CCS811_FW_APP_VERSION = 0x24
CCS811_ERROR_ID = 0xE0
CCS811_SW_RESET = 0xFF

CCS811_BOOTLOADER_APP_ERASE = 0xF1
CCS811_BOOTLOADER_APP_DATA = 0xF2
CCS811_BOOTLOADER_APP_VERIFY = 0xF3
CCS811_BOOTLOADER_APP_START = 0xF4

CCS811_DRIVE_MODE_IDLE = 0x00
CCS811_DRIVE_MODE_1SEC = 0x01
CCS811_DRIVE_MODE_10SEC = 0x02
CCS811_DRIVE_MODE_60SEC = 0x03
CCS811_DRIVE_MODE_250MS = 0x04

CCS811_HW_ID_CODE = 0x81
CCS811_REF_RESISTOR = 100000

pi = pigpio.pi()
gas = pi.bb_i2c_open(20,21,10000) #SDA = gpio20 scl = gpio21

def send(mode,data):
    (s, buffy) = pi.bb_i2c_zip(20,[4, 0x5b, 2, 7, 1, mode, 2 , 7, 1, data, 3, 0])
    print("sent, and returned was: " + str(buffy) + str(s))
def recieve(mode,count):
    (s, buffy) =pi.bb_i2c_zip(20,[4, 0x5b, 2, 7, 1, mode, 2, 6, count, 3, 0])
    #print("Instructed what to recieve, and returned was: " + str(buffy) + str(s))
    #(s,buffy) = pi.bb_i2c_zip(20,[4, 0x5b, 2, 6, count, 3, 0])
    print("Raw recieved: " + str(buffy) + "S: " + str(s))
   # if s >= 0:
    return buffy
    #else:
        #raise ValueError('returned s < 0 on recieve')

def init():
    send(CCS811_BOOTLOADER_APP_START,0x00) #gå till application mode
    sleep(.1)
    status = recieve(CCS811_STATUS,1)
    #if status is not 0x10 or not 0x90:
        #error init
       # raise ValueError('status wrong')
    #set drive mode to 1s updates interrupts disabled
    send(CCS811_MEAS_MODE, 0x10)
    
def dataready():
    datardy = recieve(CCS811_STATUS,1)
    if datardy == '':
        return False
    if (int(datardy) & 0x03) == 0x03:
        return True
    else:
        return False
    
def readsensors():
    #while(not dataready()):
     #   pass
    buf = recieve(CCS811_ALG_RESULT_DATA,4)
    cleaned_buf = [0] * 4
    for i in range(len(buf)):
        if buf[i] is '':
            cleaned_buf[i] = 0
        else:
            cleaned_buf[i] = int(buf[i])
    co = (cleaned_buf[0] << 8) | (cleaned_buf[1])
    tvc = (cleaned_buf[2] << 8) | (cleaned_buf[3])
    print(co)
    print(tvc)
    return [co,tvc]

    

init()
for i in range(100):
    print("read " + str(i))
    (b,a) = readsensors()
    #print(b)
    #print(a)
    sleep(1)
pi.bb_i2c_close(20)
pi.stop()
