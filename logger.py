import os
import time
import i2c_devices
import i2c_bb_devices
import spi_devices
import math
import subprocess
import sys

from time import sleep
from datetime import datetime
ccs811_available = False
mic_available = False
display_available = False
adc_available = False
arduino_available = False
temperature_available = False

temp = None
co = None
tvoc = None
regnraw = None
regn = None
mic = None
wind = None
sun = None
battery = None
current = None
watt = None

def initiate():
    if(spi_devices.mic_init()):
        global mic_available
        mic_available = True
    if(i2c_devices.display_init()):
        global display_available
        display_available = True
        i2c_devices.clearDisplay()
    if(i2c_bb_devices.init_ccs811(0x10)):# mode = 0x10 #0x10 = 1_sec_meas, 0x00 idle, 0x20 10_sec_meas, 0x30 60_sec_meas
        #returns 2 if newly booted and should wait 20min before accurate read
        global ccs811_available
        ccs811_available = True
        #temp = i2c_devices.get_temperature()
        #i2c_bb_devices.set_environment(21,50)
    if(spi_devices.adc_init()):
        global adc_available
        adc_available = True
    if(i2c_devices.temp_init()):
        global temperature_available
        temperature_available = True
    try:
        (tmp,tmp2,tmp3) = i2c_bb_devices.read_arduino()
        global arduino_available
        arduino_available = True
    except:
        arduino_available = False

def append_log():
    if os.path.isdir("/home/pi/citisense/logs/"):
        if(display_available):
            i2c_devices.settextpos(12,-2)
            i2c_devices.putstring("Logging..")
        try:
            file = open("/home/pi/citisense/logs/data_log.csv", "a")
        except IOError:
            if(display_available):
                i2c_devices.settextpos(10,-1)
                i2c_devices.putstring("IO-Err log")
            print("IO-Err logger")
            return 2
        if os.stat("/home/pi/citisense/logs/data_log.csv").st_size == 0:
            file.write('Time, Temp, CO2, TVOC, Rain, Noise, Wind, Sun, Battery, Current, Watt\n')
        file.write(datetime.now().strftime('%H:%M:%S') + ", " + str(temp) + ", " + str(co) + ", " + str(tvoc) + ", " + str(regn) + ", " + str(mic) + ", " + str(wind) + ", " + str(sun) + ", " + str(battery) + ", " + str(current) + ", " + str(watt) + "\n" )
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
    global ccs811_available
    global mic_available
    global display_available
    global adc_available
    global arduino_available
    global temperature_available
    global temp
    global co
    global tvoc
    global regnraw
    global regn
    global mic
    global wind
    global sun
    global battery
    global current
    global watt

    if(mic_available):
        mic = spi_devices.estimate_noise(20)
        #convert to dB
        mic = round(20*math.log10(math.fabs(mic/3.3),3))

    if(arduino_available):
        try:
            (sun, battery, current) = i2c_bb_devices.read_arduino()
            if(battery < 640): #Battery too low, arduino about to cut power
                shutdown()
            sun = round(float(sun*4.95/1023),3)
            battery = round(float(battery*4.95/1023),3)
            current = round(float(current*4.95/(1023*4.74)),3)
            watt = round(current*sun,3)
        except Exception as e:
            arduino_available = False
            sun = None
            battery = None
            current = None
            watt = None
            log_error(str(e) + " ARDUINO ERR, disabling")

    if(ccs811_available):
        try:
            if(i2c_bb_devices.dataready()):
                (co,tvoc) = i2c_bb_devices.read_gas()
                #temp = round(i2c_bb_devices.calctemp(),3)
        except Exception as e:
            ccs811_available = False
            log_error(str(e) + " CCS811 ERR, disabling")

    if(temperature_available):
        try:
            temp = i2c_devices.get_temperature()
            if (ccs811_available):
                i2c_bb_devices.set_environment(temp)
        except Exception as e:
            temp = None
            temperature_available = False
            log_error(str(e) +  " TEMP_SENS ERR, disabling")

    if(adc_available):
        try:
            regn = round((spi_devices.read_adc_raw(0)*3.3/4095),2) #divide by 2^(12-2) and mult 3.3 to get V
            #regn = round(spi_devices.read_adc_voltage(0,0),4) #channel, mode = 0, 0
            wind = round(spi_devices.read_adc_raw(1)*3300/4095,2) #estimering för rpm: x4, omvandlas till mV
        except Exception as e:
            log_error(str(e) + " ADC ERR, disabling")

    if(display_available):
        temptext = "Temp: " + str(temp) + "C  "
        cotext = "CO2:  "+  str(co) + "ppm  "
        tvoctext = "TVOC: " + str(tvoc) + "ppm   "
        regntext = "Regn: " + str(regn) + "V "
        windtext = "Wind: " + str(wind) + "mV   "
        mictext = "Mic:  " + str(mic) + "dB   "
        suntext = "Sun: " + str(sun) + "V   "
        battext = "Batt: " + str(battery) + "V   "
        curtext = "Curr: " + str(current*1000) + "mA   "
        wattext = "Power: " + str(watt) + "W   "
        i2c_devices.settextpos(0,-2)
        i2c_devices.putstring(temptext)
        i2c_devices.settextpos(1,-2)
        i2c_devices.putstring(cotext)
        i2c_devices.settextpos(2,-2)
        i2c_devices.putstring(tvoctext)
        i2c_devices.settextpos(3,-2)
        i2c_devices.putstring(regntext)
        i2c_devices.settextpos(4,-2)
        i2c_devices.putstring(windtext)
        i2c_devices.settextpos(5,-2)
        i2c_devices.putstring(mictext)
        i2c_devices.settextpos(6,-2)
        i2c_devices.putstring(suntext)
        i2c_devices.settextpos(7,-2)
        i2c_devices.putstring(battext)
        i2c_devices.settextpos(8,-2)
        i2c_devices.putstring(curtext)
        i2c_devices.settextpos(9,-2)
        i2c_devices.putstring(wattext)
    if Log == True:
        append_log()
    if Backup == True:
        if(display_available):
            i2c_devices.settextpos(10,-2)
            i2c_devices.putstring("WRITING TO USB")
        subprocess.call(['sudo', 'sh', '/home/pi/citisense/camera.sh'])
        subprocess.call(['sudo', 'sh', '/home/pi/citisense/cp_to_usb.sh'])
        if(display_available):
            i2c_devices.putstring("                    ")
def shutdown():
    print("exiting")
    i2c_bb_devices.close_bus()
    i2c_devices.close_bus()
    spi_devices.close_bus()
    log_error("Shutting down due to low battery")
    subprocess.call(['sudo', 'sync'])
    subprocess.call(['sudo', 'shutdown', '-h', 'now'])
    sys.exit()
def log_error(e):
    file = open("/home/pi/citisense/logs/error.txt", "a")
    file.write(datetime.now().strftime('%H:%M:%S') + "Msg: " + e + "\n")
    file.close()
initiate()
count1 = 0
count2 = 0
while(1):
    count1 +=1
    if count1 == 300: #logga var 5e minut
        count1 = 0
        if count2 == 5:
            update_sensors(True, False) #log local
            count2 = 0
        else:
            count2 += 1
            update_sensors(True, False) #usb-backup + pic
    else:
        update_sensors(False, False)
    sleep(0.6)
