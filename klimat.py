from time import sleep
import display 
from Adafruit_CCS811 import Adafruit_CCS811


display.init(0x3c)
display.clearDisplay()
ccs = Adafruit_CCS811()

while not ccs.available():
    pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0

while(1):
    if ccs.available():
        temptext = "Temp: " + str("%.2f" % ccs.calculateTemperature() + "C  ")
        if not ccs.readData(): # should be 0 if read successfull
            cotext = "CO2:  "+  str(ccs.geteCO2()) + " ppm  "
            tvoctext = "TVOC: " + str(ccs.getTVOC()) + " ppm   "

            display.settextpos(0,0)
            display.putstring(temptext)
            display.settextpos(1,0)
            display.putstring(cotext)
            display.settextpos(2,0)
            display.putstring(tvoctext)
        else:
            error = 1
            display.putstring("Ccs unavailable")
            while(1):
                pass
    sleep(2)
