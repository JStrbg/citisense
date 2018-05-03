import os
import time
import i2c_devices
import gas_sensor
import adc
import math
import subprocess
from time import sleep
from datetime import datetime

def initiate():
    i2c_devices.init()
    mode = 0x10 #0x10 = 1_sec_meas, 0x00 idle, 0x20 10_sec_meas, 0x30 60_sec_meas
    gas_sensor.init(mode)
    i2c_devices.clearDisplay()

    temp = gas_sensor.calctemp()
    gas_sensor.tempOffset = temp - 25.0
    #gas_sensor.set_environment(21,50)
def append_log(temp, co, tvoc, regn, mic):
    if os.path.isdir("/home/pi/citisense/logs/"):
        i2c_devices.settextpos(12,-2)
        i2c_devices.putstring("Logging..")
        try:
            file = open("/home/pi/citisense/logs/data_log.csv", "a")
        except IOError:
            i2c_devices.settextpos(7,-1)
            i2c_devices.putstring("IO-Err log")
            print("IO-Err logger")
            return 2
        if os.stat("/home/pi/citisense/logs/data_log.csv").st_size == 0:
            file.write('Time, Temp, CO2, TVOC, Rain, Noise\n')
        file.write(datetime.now().strftime('%H:%M:%S') + ", " + str("%.2f" % temp) + ", " + str(co) + ", " + str(tvoc) + ", " + str(round(regn,3)) + ", " + str(mic) + "\n")
        file.close()
        i2c_devices.settextpos(12,-2)
        i2c_devices.putstring("Logged   ")
    else:
        print("Io error logger")
        i2c_devices.settextpos(12,-2)
        i2c_devices.putstring("io error logger         ")
        sleep(1)
def update_sensors(Log, Backup):
    (co,tvoc) = gas_sensor.readsensors()
    regnraw = adc.read_adc_raw(0,0)
    regn = adc.read_adc_voltage(0,0) #channel, mode = 0, 0
    temp = gas_sensor.calctemp()
    mic = adc.estimate_noise()
    temptext = "Temp: " + str("%.2f" % temp + "C   ")
    cotext = "CO2:  "+  str(co) + " ppm  "
    tvoctext = "TVOC: " + str(tvoc) + " ppm   "
    regntext = "Regn: " + str(round(regn,4)) + "V "
    regnrawtext = "RegnRaw: " + str(round(regnraw,2)) + "  "
    mictext = "Mic:  " + str(mic) + "   "
    i2c_devices.settextpos(0,-2)
    i2c_devices.putstring(temptext)
    i2c_devices.settextpos(1,-2)
    i2c_devices.putstring(cotext)
    i2c_devices.settextpos(2,-2)
    i2c_devices.putstring(tvoctext)
    i2c_devices.settextpos(3,-2)
    i2c_devices.putstring(regntext)
    i2c_devices.settextpos(4,-2)
    i2c_devices.putstring(regnrawtext)
    i2c_devices.settextpos(5,-2)
    i2c_devices.putstring(mictext)
    err = gas_sensor.checkerror()
    if err:
        i2c_devices.settextpos(7,-2)
        i2c_devices.putstring("sens_gas err: " + err)
    if Log == True:
        append_log(temp, co, tvoc, regn, mic)
    if Backup == True:
        i2c_devices.settextpos(9,-2)
        i2c_devices.putstring("WRITING TO USB")
        subprocess.call(['sudo', 'sh', '/home/pi/citisense/camera.sh'])
        subprocess.call(['sudo', 'sh', '/home/pi/citisense/cp_to_usb.sh'])
        i2c_devices.putstring("                    ")

initiate()
i = 0
while(1):
    i += 1
    update_sensors(False, False)
    sleep(0.9)
    if i == 60:
        update_sensors(True, False) #log local
        #update_sensors(True,True) #usb-backup + pic
        i = 0
gas_sensor.close_bus()
i2c_devices.close_bus()
adc.close_bus()
