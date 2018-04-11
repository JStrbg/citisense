from time import sleep
from Adafruit_CCS811 import Adafruit_CCS811
import display
ccs = Adafruit_CCS811()


display.init(0x3c)
display.clearDisplay()


while not ccs.available():
    pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0

while(1):
    if ccs.available():
        display.settextpos(0,0)
        outtext = "Temp: " + str("%.2f" % ccs.calculateTemperature())
        display.putstring(outtext)
        if not ccs.readData(): # should be 0 if read successfull
            display.settextpos(1,0)
            outtext = "CO2:  "+  str(ccs.geteCO2())
            display.putstring(outtext)
            display.settextpos(2,0)
            outtext = "TVOC: " + str(ccs.getTVOC())
            display.putstring(outtext)
        else:
            error = 1
            display.putstring("Ccs unavailable")
            while(1):
                pass
    sleep(2)
