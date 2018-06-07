import pigpio

pi = pigpio.pi()
bus = pi.spi_open(0,1000000,0) #slave 0, spi bus 0, 1MHz
mic = pi.spi_open(1,48000,0) #slave 1, spi bus 0, 48KHz
refvoltage = 3.3

#Peacefully close buses
def close_bus():
    pi.spi_close(bus)
    pi.spi_close(mic)
    pi.stop()
#Try to figure out availability, should be some noise if connected
def adc_init():
    if (read_adc_raw(0) <= 2):
        #Not present
        return 0
    #Probably present
    return 1

def mic_init():
    #If absolutely silent, mic probably not connected
    if(estimate_noise(300) == 2048.0):
        return 0
    return 1

def read_mic():
    (count,buf) = pi.spi_read(mic,2)
    #Arrives on split form, with 2048.0 offset (half maximum)
    sample = 2048.0 -((buf[0]<< 8) + buf[1])
    #Sample is on raw form from an internal adc on the mic, convert with known Vref 3.3V
    return sample*refvoltage/4095

def estimate_noise(sample_count = 100):
    sample = 0
    #Calculate an avarage soundlevel over [sample_count] samples
    for i in range(sample_count):
        sample += abs(read_mic())
    return sample/sample_count

def read_adc_voltage(channel):
    if (channel > 1) or (channel < 0):
        raise ValueError('read_adc_voltage: channel out of range')
    raw = read_adc_raw(channel)
    #Convert raw value to voltage with known reference value 3.3V
    return raw*(refvoltage / 4095)

def read_adc_raw(channel):
    #Channel 0 is rain sensor, 1 anemometer
    (count,raw) = pi.spi_xfer(bus,[1,(2 + channel)<<6,0])
    #Sample arrives split in 3 bytes, first is empty, second is upper byte, last lower
    return ((raw[1] << 8) + raw[2])
