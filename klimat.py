from time import sleep
import display
import gas_sensor
import adc
import math
from flask import Flask
#https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/4
#https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md
# pot : http://www.instructables.com/id/Raspberry-Pi-Web-Server-Wireless-Access-Point-WAP/

#globals
co = 0
tvoc = 0
temp = 0.0
mic = 0
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

    #webapp

def spam_mic():
    mic = adc.read_mic()
    mictext = "Mic: " + str(mic) + "  "
    if val <= 0:
        display.settextpos(5,0)
    else:
        display.settextpos(6,0)
    display.putstring(mictext)
def meas_to_display():
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
    return temptext + "  " + cotext + "  " + tvoctext + "  " + regntext + "  " + mictext

initiate()
app = Flask(__name__)
@app.route('/')
def index():
    return meas_to_display()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

gas_sensor.close_bus()
display.close_bus()
adc.close_bus()
