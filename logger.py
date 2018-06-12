import os
import time
import math
import subprocess
import sys
from time import sleep
from datetime import datetime
#Sensordevices
import i2c_devices
import i2c_bb_devices
import spi_devices
#Initiate availabilities for plugNplay functionality
ccs811_available = False
mic_available = False
display_available = False
adc_available = False
arduino_available = False
temperature_available = False
#Keep sensor values global for ease of access
temp = None
co = None
tvoc = None
rain = None
mic = None
wind = None
sun = None
battery = None
current = None
watt = None
arduino_Vref = 5.0
local_timer = 0
usb_timer= 0

#Figure out available devices at launch, also set certain settings
def initiate():
    if(spi_devices.mic_init()):
        global mic_available
        mic_available = True

    if(i2c_devices.display_init()):
        global display_available
        display_available = True
        i2c_devices.clearDisplay()

    mode = 0x10
    # mode: 0x10 = 1_sec_meas, 0x00 idle, 0x20 10_sec_meas, 0x30 60_sec_meas
    if(i2c_bb_devices.init_ccs811(mode)):
        #Init returns 2 if newly booted and should wait 20min before accurate read
        #Not finnished implementing yet though
        global ccs811_available
        ccs811_available = True

    if(spi_devices.adc_init()):
        global adc_available
        adc_available = True

    if(i2c_devices.temp_init()):
        global temperature_available
        temperature_available = True

    if(i2c_bb_devices.arduino_init()):
        global arduino_available
        arduino_available = True
        update_time()

def update_time():
    offset_raw = i2c_bb_devices.recieve(0x04, 0x03, 4)
    offset = (int(offset_raw[3]) << 24) | (int(offset_raw[2]) << 16) | (int(offset_raw[1]) << 8) | int(offset_raw[0])
    while (offset > 65535):
        subprocess.call("sudo date -s '65535 seconds'",shell=True)
        offset = offset - 65535
    subprocess.call("sudo date -s '" + str(offset) + " seconds'",shell=True)
    
#Write current measurement values to the log file
def append_log():
    if os.path.isdir("/home/pi/citisense/logs/"):
        if(display_available):
            i2c_devices.settextpos(12,-2)
            i2c_devices.putstring("Logging..")

        try:
            #Open log file
            file = open("/home/pi/citisense/logs/data_log.csv", "a")
        except IOError as e:
            #Some error logging
            if(display_available):
                i2c_devices.settextpos(10,-1)
                i2c_devices.putstring("IO-Err log")
            print("IO-Err logger")
            log_error(str(e) + " Opening data_log.csv ERR")
            return 2

        if os.stat("/home/pi/citisense/logs/data_log.csv").st_size == 0:
            #If log file empty, fill out header
            file.write('Time, Temp[C], CO2[ppm], TVOC[ppm], Rain[V], Noise[dBV], Wind[mV], Sun[V], Battery[V], Current[mA], Watt[mW]\n')
        #Then the sensor values separated by commas (.csv-format)
        file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + ", " + str(temp) + ", " + str(co) + ", " + str(tvoc) + ", " + str(rain) + ", " + str(mic) + ", " + str(wind) + ", " + str(sun) + ", " + str(battery) + ", " + str(current) + ", " + str(watt) + "\n" )
        file.close()

        if(display_available):
            i2c_devices.settextpos(12,-2)
            sleep(0.1)
            i2c_devices.putstring("          ")
    else:
        #Error tracking
        print("Log dir not present")
        if(display_available):
            i2c_devices.settextpos(12,-2)
            i2c_devices.putstring("io error logger         ")
        log_error("Log directory not found")

def update_sensors(Log, Backup):
    #Specify globals
    global ccs811_available
    global mic_available
    global display_available
    global adc_available
    global arduino_available
    global temperature_available
    global temp
    global co
    global tvoc
    global rain
    global mic
    global wind
    global sun
    global battery
    global current
    global watt

    if(mic_available):
        #Use 30 samples, very cpu and energy-intense
        mic = spi_devices.estimate_noise(20)
        #convert to dBV
        mic = round(20*math.log10(mic),3)

    if(arduino_available):
        try:
            (sun, battery, current) = i2c_bb_devices.read_arduino()
            if(battery < 640 and battery > 0):
                #Battery too low, arduino about to cut power
                shutdown()
            #Convert from raw values to voltage
            
            sun = round(float(sun*arduino_Vref/1023),3) #V
            battery = round(float(battery*arduino_Vref/1023),3) #V
            current = round(float(current*arduino_Vref*1000/(1023*4.74)),3) #mA
            #Calculate power drawn from solar panel to charge battery
            watt = round(current*sun,3) #mW
        except Exception as e:
            #Catch error and set arduino as unavailable in case of hardware failure
            arduino_available = False
            sun = None
            battery = None
            current = None
            watt = None
            log_error(str(e) + " ARDUINO ERR, disabling")

    if(ccs811_available):
        try:
            #Check if sample available
            if(i2c_bb_devices.dataready()):
                (co,tvoc) = i2c_bb_devices.read_gas()
                #If co2 less than 400ppm, sample not valid yet
                if (co < 400):
                    co = None
                    tvoc = None
        except Exception as e:
            #Catch sensor error and disable it
            ccs811_available = False
            log_error(str(e) + " CCS811 ERR, disabling")

    if(temperature_available):
        try:
            temp = i2c_devices.get_temperature()
            if (ccs811_available):
                #Send temperature to CCS811 for compensation
                i2c_bb_devices.set_environment(temp)
        except Exception as e:
            #Catch sensor error and disable it
            temp = None
            temperature_available = False
            log_error(str(e) +  " TEMP_SENS ERR, disabling")

    if(adc_available):
        try:
            rain = round(spi_devices.read_adc_voltage(0),2) #V
            wind = round(spi_devices.read_adc_voltage(1)*1000,2) # mV
        except Exception as e:
            log_error(str(e) + " ADC ERR, disabling")

    if(display_available):
        #Print current values to display if available
        temptext = "Temp:" + str(temp) + "C   "
        cotext = "CO2: "+  str(co) + "ppm   "
        tvoctext = "TVOC:" + str(tvoc) + "ppm    "
        raintext = "Rain:" + str(rain) + "V  "
        windtext = "Wind:" + str(wind) + "mV   "
        mictext = "Mic: " + str(mic) + "dBV"
        suntext = "Sun: " + str(sun) + "V   "
        battext = "Batt:" + str(battery) + "V   "
        curtext = "Curr:" + str(current) + "mA "
        wattext = "Pwr: " + str(watt) + "mW  "
        i2c_devices.settextpos(0,-2)
        i2c_devices.putstring(temptext)
        i2c_devices.settextpos(1,-2)
        i2c_devices.putstring(cotext)
        i2c_devices.settextpos(2,-2)
        i2c_devices.putstring(tvoctext)
        i2c_devices.settextpos(3,-2)
        i2c_devices.putstring(raintext)
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
        i2c_devices.settextpos(10,-2)
        i2c_devices.putstring("L: " + str(local_timer))
        i2c_devices.settextpos(11,-2)
        i2c_devices.putstring("B: " + str(usb_timer))

    if Log == True:
        #Log to local .csv file
        append_log()

    if Backup == True:
        #Backup all logs + picture to USB
        if(display_available):
            i2c_devices.settextpos(10,-2)
            i2c_devices.putstring("WRITING TO USB")
        #Run pic + copy scripts, return errors
        err = subprocess.call(['sudo', 'sh', '/home/pi/citisense/camera.sh'])
        err += subprocess.call(['sudo', 'sh', '/home/pi/citisense/cp_to_usb.sh'])
        if err != 0:
            log_error(str(err) + " USB_mem or camera error")
        if(display_available):
            i2c_devices.putstring(" " + str(err) + "                        ")

def shutdown():
    #Shutdown procedure, closes buses and syncs OS to SD-card
    print("exiting")
    log_error("Shutting down due to low battery")
    i2c_bb_devices.close_bus()
    i2c_devices.close_bus()
    spi_devices.close_bus()
    subprocess.call(['sudo', 'sync'])
    subprocess.call(['sudo', 'shutdown', '-h', 'now'])
    sys.exit()

def log_error(e):
    #Error logging
    file = open("/home/pi/citisense/logs/error.txt", "a")
    file.write(datetime.now().strftime('%Y-%m-%d_%H:%M') + " Msg: " + e + "\n")
    file.close()

initiate()

#Store values locally every 200 seconds, and on USB 200*5 seconds
while(1):
    local_timer +=1
    if local_timer == 300:
        local_timer = 0
        if usb_timer == 6:
            update_sensors(True, True) #log USB
            usb_timer = 0
        else:
            usb_timer += 1
            update_sensors(True, False) #log local
    else:
        update_sensors(False, False)
    sleep(0.8)
