import pigpio

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

pi = pigpoi.pi()
gas = pi.i2c_open(1,CCS811_ADDRESS)

def send(mode,data):
    pi.i2c_write_block_data(gas,mode,data)
def recieve(mode):
    return pi.i2c_read_block_data(gas,mode)

def init():
    send(CCS811_BOOTLOADER_APP_START,[0]) #gå till application mode
    sleep(.1)
    status = recieve(CCS811_STATUS)
    if status is not 0x10 or not 0x90:
        #error init
        return 2
    #set drive mode to 1s updates interrupts disabled
    send(CCS811_MEAS_MODE, 0x10)
def readsensors():
    buf = recieve(CCS811_ALG_RESULT_DATA)
    co = (buf[0] << 8) | (buf[1])
    tvc = (buf[2] << 8) | (buf[3])
    return [co,tvc]

init()
b = readsensors()
print b[0]
print b[1]    
