from time import sleep
import display
import gas_sensor

display.init(0x3c)
gas_sensor.init()
display.clearDisplay()

temp = gas_sensor.calctemp()
gas_sensor.tempOffset = temp - 25.0
gas_sensor.set_environment(22,40)

while(1):
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

#pi.bb_i2c_close(SDA)
#pi.stop()
