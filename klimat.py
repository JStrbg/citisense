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
        display.putstring("Temp: ",ccs.calculateTemperature())
        if not ccs.readData(): # should be 0 if read successfull
            display.settextpos(1,0)
            display.putstring("CO2: ",ccs.geteCO2())
            display.settextpos(2,0)
            display.putstring("TVOC: ",ccs.getTVOC())
        else:
            error = 1
            while(1):
                pass
    sleep(2)
