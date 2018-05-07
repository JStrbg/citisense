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
SDA = 22
SCL = 27
pi = pigpio.pi()
tempOffset = 0
try:
    pi.bb_i2c_close(SDA)
    sleep(0.2)
except pigpio.error as e:
    print(str(e) + " Startar om bb i2c port " + str(SDA))
gas = pi.bb_i2c_open(SDA,SCL,350000)
def close_bus():
    pi.bb_i2c_close(SDA)
    pi.stop()
def send(mode,data):
    (s, buf) = pi.bb_i2c_zip(SDA,[4, 0x5b, 2, 7, 2, mode, data, 3, 0])
def recieve(mode,count):
    (s, buf) = pi.bb_i2c_zip(SDA,[4, 0x5b, 2, 7, 1, mode, 3, 0])
    (s, buf) = pi.bb_i2c_zip(SDA,[4, 0x5b, 2, 6, count, 3, 0])
    if s >= 0:
        return buf
    else:
        raise ValueError('i2c error returned s < 0 on recieve')

def init(meas_mode):
    #Starta applikationen
    pi.bb_i2c_zip(SDA,[4, 0x5b, 2, 7, 1, CCS811_BOOTLOADER_APP_START, 3, 0])
    sleep(0.1)
    status = recieve(CCS811_STATUS,1)
    if status[0] == 0x00 :
        return 0
    send(CCS811_MEAS_MODE, meas_mode) #Välj mode
    return 1

def dataready():
    status = recieve(CCS811_STATUS,1)
    if status == '':
        return False
    if (int(status[0]) & 0x08) == 0x08:
        return True
    else:
        return False

def readsensors():
    while(not dataready()):
        sleep(0.2)
        pass
    buf = recieve(CCS811_ALG_RESULT_DATA,4)
    co = (buf[0] << 8) | buf[1]
    tvc = (buf[2] << 8) | buf[3]
    if co < 400:
        (co,tvc) = readsensors()
    return [co,tvc]

def checkerror():
    buf = recieve(CCS811_STATUS,1)
    if  (int(buf[0]) & 0x01) == 0x01: #Error reported by sensor
        buf = recieve(CCS811_ERROR_ID, 1)
        print("Error is: " + str(buf))
        return str(buf)

def calctemp():
    buf = recieve(CCS811_NTC, 4)
    vref = (buf[0] << 8) | buf[1]
    vrntc = (buf[2] << 8) | buf[3]
    rntc = (float(vrntc) * float(CCS811_REF_RESISTOR) / float(vref) )

    ntc_temp = math.log(rntc / 10000.0)
    ntc_temp /= 3380.0
    ntc_temp += 1.0 / (25 + 273.15)
    ntc_temp = 1.0 / ntc_temp
    ntc_temp -= 273.15
    #print(str(tempOffset) + "  ntc: " + str(ntc_temp))
    return ntc_temp - tempOffset

def set_environment(temperature, humidity = 50 ):
    if temperature < -25:
        temperature = -25
    if humidity < 0 or humidity > 100:
        humidity = 50
    hum_perc = int(round(humidity)) << 1
    parts = math.modf(temperature)
    fractional = math.fabs(parts[0])
    temp_int = int(parts[1])
    temp_high = ((temp_int + 25) << 9)
    temp_low = (int(fractional / 0.001953125) & 0x1FF)
    temp_conv = (temp_high | temp_low)
    buf = [hum_perc, 0x00,((temp_conv >> 8) & 0xFF), (temp_conv & 0xFF)]
    (s, buffy) = pi.bb_i2c_zip(SDA,[4, 0x5b, 2, 7, 4, CCS811_ENV_DATA, buf[0], buf[1], buf[2], 3, 0])
