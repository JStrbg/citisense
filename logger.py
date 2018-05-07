import os
import time
import i2c_devices
import gas_sensor
import spi_devices
import math
import subprocess
from time import sleep
from datetime import datetime
ccs11_available = False
mic_available = False
display_available = False
adc_available = False
temp_available = False
def initiate():
    if(spi_devices.mic_init()):
        global mic_available
        mic_available = True
    if(i2c_devices.display_init()):
        global display_available
        display_available = True
        i2c_devices.clearDisplay()
    if(gas_sensor.init(0x10)):# mode = 0x10 #0x10 = 1_sec_meas, 0x00 idle, 0x20 10_sec_meas, 0x30 60_sec_meas
        global ccs11_available
        ccs11_available = True
        temp = gas_sensor.calctemp()
        gas_sensor.tempOffset = temp - 25.0
        #gas_sensor.set_environment(21,50)
    if(spi_devices.adc_init()):
        global adc_available
        adc_available = True

def append_log(temp, co, tvoc, regn, mic):
    if os.path.isdir("/home/pi/citisense/logs/"):
        if(display_available):
            i2c_devices.settextpos(12,-2)
            i2c_devices.putstring("Logging..")
        try:
            file = open("/home/pi/citisense/logs/data_log.csv", "a")
        except IOError:
            if(display_available):
                i2c_devices.settextpos(7,-1)
                i2c_devices.putstring("IO-Err log")
            print("IO-Err logger")
            return 2
        if os.stat("/home/pi/citisense/logs/data_log.csv").st_size == 0:
            file.write('Time, Temp, CO2, TVOC, Rain, Noise\n')
        file.write(datetime.now().strftime('%H:%M:%S') + ", " + str(temp) + ", " + str(co) + ", " + str(tvoc) + ", " + str(regn) + ", " + str(mic) + "\n")
        file.close()
        if(display_available):
            i2c_devices.settextpos(12,-2)
            sleep(0.1)
            i2c_devices.putstring("          ")
    else:
        print("Io error logger")
        if(display_available):
            i2c_devices.settextpos(12,-2)
            i2c_devices.putstring("io error logger         ")
        sleep(1)
def update_sensors(Log, Backup):
    temp = None
    co = None
    tvoc = None
    regnraw = None
    regn = None
    mic = None
    if(ccs11_available):
        (co,tvoc) = gas_sensor.readsensors()
        temp = round(gas_sensor.calctemp(),3)
    if(adc_available):
        regnraw = spi_devices.read_adc_raw(0,0)
        regn = round(spi_devices.read_adc_voltage(0,0),4) #channel, mode = 0, 0
    if(mic_available):
        mic = spi_devices.estimate_noise()
    if(display_available):
        temptext = "Temp: " + str(temp) + "C   "
        cotext = "CO2:  "+  str(co) + " ppm  "
        tvoctext = "TVOC: " + str(tvoc) + " ppm   "
        regntext = "Regn: " + str(regn) + "V "
        regnrawtext = "RegnRaw: " + str(regnraw) + "  "
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

    if Log == True:
        append_log(temp, co, tvoc, regn, mic)
    if Backup == True:
        if(display_available):
            i2c_devices.settextpos(9,-2)
            i2c_devices.putstring("WRITING TO USB")
        subprocess.call(['sudo', 'sh', '/home/pi/citisense/camera.sh'])
        subprocess.call(['sudo', 'sh', '/home/pi/citisense/cp_to_usb.sh'])
        if(display_available):
            i2c_devices.putstring("                    ")

initiate()
i = 0
while(1):
    i += 1
    update_sensors(False, False)
    if i == 60:
        update_sensors(True, False) #log local
        #update_sensors(True,True) #usb-backup + pic
        i = 0
    sleep(0.9)

gas_sensor.close_bus()
i2c_devices.close_bus()
spi_devices.close_bus()
