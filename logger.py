import os
import time
import display
import gas_sensor
import adc
import math
import subprocess
from datetime import datetime

#globals
co = 0
tvoc = 0
temp = 0.0
mic = 0.0
regn = 0.0
regnraw = 0
temptext = "Temp: " + str("%.2f" % temp + "C  ")
cotext = "CO2:  "+  str(co) + " ppm  "
tvoctext = "TVOC: " + str(tvoc) + " ppm   "
regntext = "Regn: " + str(round(regn,4)) + "V "
regnrawtext = "RegnRaw: " + str(round(regnraw,2)) + "  "
mictext = "Mic:  " + str(mic) + "   "

def initiate():
    display.init()
    mode = 0x10 #0x10 = 1_sec_meas, 0x00 idle, 0x20 10_sec_meas, 0x30 60_sec_meas
    gas_sensor.init(mode)
    display.clearDisplay()

    temp = gas_sensor.calctemp()
    gas_sensor.tempOffset = temp - 25.0
    #gas_sensor.set_environment(21,50)
def append_log():
    try:
        file = open("/media/pi/KINGSTON/data_log.csv")
    except IOError:
        display.settextpos(7,0)
        display.putstring("USB-mem IO-Err log")
        print("USB-mem IO-Err logger")
        return 2
    if os.stat("/media/pi/KINGSTON/data_log.csv").st_size == 0:
        file.write('Time, Temp, CO2, TVOC, Rain, Noise\n')
    file.write(str(datetime.now()) + ',' + str("%.2f" % temp) + ',' + str(co) + ',' + str(tvoc) + ',' + str(round(regn,3)) + ',' + str(mic) + "\n"')
    file.close()
def update_sensors(Log):
    (co,tvoc) = gas_sensor.readsensors()
    regnraw = adc.read_adc_raw(0,0)
    regn = adc.read_adc_voltage(0,0) #channel, mode = 0, 0
    temp = gas_sensor.calctemp()
    mic = adc.estimate_noise()
    temptext = "Temp: " + str("%.2f" % temp + "C  ")
    cotext = "CO2:  "+  str(co) + " ppm  "
    tvoctext = "TVOC: " + str(tvoc) + " ppm   "
    regntext = "Regn: " + str(round(regn,4)) + "V "
    regnrawtext = "RegnRaw: " + str(round(regnraw,2)) + "  "
    mictext = "Mic:  " + str(mic) + "   "
    display.settextpos(0,0)
    display.putstring(temptext)
    display.settextpos(1,0)
    display.putstring(cotext)
    display.settextpos(2,0)
    display.putstring(tvoctext)
    display.settextpos(3,0)
    display.putstring(regntext)
    display.settextpos(4,0)
    display.putstring(regnrawtext)
    display.settextpos(5,0)
    display.putstring(mictext)
    err = gas_sensor.checkerror()
    if err:
        display.settextpos(7,0)
        display.putstring("sens_gas err: " + err)
    if Log:
        append_log()
        subprocess.call(['sudo', 'sh', 'camera.sh'])

initiate()
while(1):
    update_sensors(True)
    sleep(10)
gas_sensor.close_bus()
display.close_bus()
adc.close_bus()
