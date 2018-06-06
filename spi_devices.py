import pigpio

pi = pigpio.pi()
bus = pi.spi_open(0,1000000,0) #slave 0, spi bus 0, 1MHz
mic = pi.spi_open(1,48000,0)
adcrefvoltage = 3.3
#(a,b) = pi.spi_read(bus,count)
#(byte_count, rx_data) = pi.spi_xfer(bus,tx_data)
#pi.spi_write(bus,data)
def close_bus():
    pi.spi_close(bus)
    pi.spi_close(mic)
    pi.stop()
def adc_init(): #Try to figure out availability, should be some noise if connected
    if (read_adc_raw(0) <= 2):
        return 0
    return 1
def mic_init():
    if(estimate_noise(300) == 2048.0): #If absolutely silent, mic probably not connected
        return 0
    return 1
def read_mic():
    (count,buf) = pi.spi_read(mic,2)
    sample = 2048.0 -((buf[0]<< 8) + buf[1])
    return sample #*3.3/23
def estimate_noise(sample_count = 100):
    sample = 0
    for i in range(sample_count):
        sample += abs(read_mic())
    return round(sample/sample_count,2)
def read_adc_voltage(channel): #returned as percentage of ref
    if (channel > 1) or (channel < 0):
        raise ValueError('read_adc_voltage: channel out of range')
    raw = read_adc_raw(channel)
    return raw*(adcrefvoltage / 4095)
def read_adc_raw(channel):
    (count,raw) = pi.spi_xfer(bus,[1,(2 + channel)<<6,0])
    ret = ((raw[1] << 8) + raw[2])

    return ret
