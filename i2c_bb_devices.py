import pigpio
import math
from time import sleep
arduino_addr = 0x04
CCS811_ADDRESS  =  0x5b
#Registers on CCS811
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

#bitbanging i2c pins on GPIO
SDA = 22
SCL = 27
pi = pigpio.pi()

#Close bus if already open
try:
    pi.bb_i2c_close(SDA)
    sleep(0.2)
except pigpio.error as e:
    print(str(e) + " Startar om bb i2c port " + str(SDA))

#Open bus on GPIO pins, 300KHz
bus = pi.bb_i2c_open(SDA,SCL,300000)

def close_bus():
    pi.bb_i2c_close(SDA)
    pi.stop()

def send(addr,mode,data):
    #Bit-baning array
    (s, buf) = pi.bb_i2c_zip(SDA,[4, addr, 2, 7, 2, mode, data, 3, 0])

def recieve(addr,mode,count):
    #Specify register address
    (s, buf) = pi.bb_i2c_zip(SDA,[4, addr, 2, 7, 1, mode, 3, 0])
    #Read specified register
    (s, buf) = pi.bb_i2c_zip(SDA,[4, addr, 2, 6, count, 3, 0])
    if s >= 0:
        return buf
    else:
        #S should be positive if recieved correctly
        raise ValueError('i2c error returned s < 0 on recieve')

def init_ccs811(meas_mode):
    try:
        if not dataready():
            # Boot command
            (s, buf) = pi.bb_i2c_zip(SDA,[4, CCS811_ADDRESS, 2, 7, 1, CCS811_BOOTLOADER_APP_START, 3, 0])
            sleep(0.1) # Let device boot for 0.1s
            # Choose measuring mode
            send(CCS811_ADDRESS, CCS811_MEAS_MODE, meas_mode)
            return 2 # Return 2 to indicate newly booted device
        return 1 # Return 1 to indicate device already booted
    except pigpio.error:
        return 0 # Return 0 to indicate device not responding

def dataready():
    status = recieve(CCS811_ADDRESS, CCS811_STATUS,1)
    # 0x08 equals the data_ready bit
    if (int(status[0]) & 0x08) == 0x08:
        return True
    else:
        return False

def read_gas():
    buf = recieve(CCS811_ADDRESS, CCS811_ALG_RESULT_DATA,4)
    #Values arrive split
    co = (buf[0] << 8) | buf[1]
    tvc = (buf[2] << 8) | buf[3]
    return [co,tvc]

def arduino_init():
    try:
        (tmp,tmp2,tmp3) = read_arduino()
        return 1
    except pigpio.error:
        #Arduino not connected
        return 0

def read_arduino():
    #Get energy values from arduino, indexes 0, 1 and 2
    #Arrives on split form, lower byte first
    sun_v_raw = recieve(arduino_addr, 0x00, 2)
    sun_v = (int(sun_v_raw[1]) << 8) | int(sun_v_raw[0])
    batt_v_raw = recieve(arduino_addr, 0x01, 2)
    batt_v = (int(batt_v_raw[1]) << 8) | int(batt_v_raw[0])
    current_raw = recieve(arduino_addr, 0x02, 2)
    current = (int(current_raw[1]) << 8) | int(current_raw[0])
    return (sun_v, batt_v, current)

def checkerror():
    #Check for gas_sensor error
    buf = recieve(CCS811_ADDRESS, CCS811_STATUS,1)
    if  (int(buf[0]) & 0x01) == 0x01: #Error reported by sensor
        #Check error ID
        buf = recieve(CCS811_ADDRESS, CCS811_ERROR_ID, 1)
        print("Gas sensor error is: " + str(buf))
        return str(buf)

def set_environment(temperature, humidity = 50 ):
    # Minimum enterable temperature
    if temperature < -25.0:
        temperature = -25.0
    # Check humidity bounds
    if humidity < 0 or humidity > 100.0:
        humidity = 50
    # LSB is worth 0.5C and so on
    hum_perc = int(round(humidity)) << 1
    # Split fractionals and integers
    parts = math.modf(temperature)
    # Remove sign bit from fractional part
    fractional = math.fabs(parts[0])
    temp_int = int(parts[1])
    # Add offset and shift 9
    temp_high = ((temp_int + 25) << 9)
    # LSB of fractional is worth 1/512, but must be sent as integer
    temp_low = (int(fractional / 0.001953125) & 0x1FF)
    # Merge result
    temp_conv = (temp_high | temp_low)
    # Complete bytearray with humidity
    buf = [hum_perc, 0x00,((temp_conv >> 8) & 0xFF), (temp_conv & 0xFF)]
    # Custom send larger bytearray
    (s, buffy) = pi.bb_i2c_zip(SDA,[4, CCS811_ADDRESS, 2, 7, 5, CCS811_ENV_DATA, buf[0], buf[1], buf[2], buf[3], 3, 0])
