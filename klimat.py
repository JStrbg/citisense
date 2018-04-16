from time import sleep
import display
import gas_sensor

def initiate():
    display.init()
    mode = 0x10 #0x10 = 1_sec_meas, 0x00 idle, 0x20 10_sec_meas, 0x30 60_sec_meas
    gas_sensor.init(mode)
    display.clearDisplay()

    temp = gas_sensor.calctemp()
    gas_sensor.tempOffset = temp - 25.0
    gas_sensor.set_environment(23,40)

def meas_to_display():
    (co,tvoc) = gas_sensor.readsensors()
    temptext = "Temp: " + str("%.2f" % gas_sensor.calctemp() + "C  ")
    cotext = "CO2:  "+  str(co) + " ppm  "
    tvoctext = "TVOC: " + str(tvoc) + " ppm   "
    display.settextpos(0,0)
    display.putstring(temptext)
    display.settextpos(1,0)
    display.putstring(cotext)
    display.settextpos(2,0)
    display.putstring(tvoctext)
    err = gas_sensor.checkerror()
    if err:
        display.settextpos(3,0)
        display.putstring("sens_gas err: " + err)

initiate()
time = 0
while(True):
    meas_to_display()
    time = time + 1
gas_sensor.close_bus()
display.close_bus()

