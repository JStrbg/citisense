import pigpio

pi = pigpio.pi()
bus = pi.spi_open(0,1000000,0) #slave 0, spi bus 0, 1MHz
mic = pi.spi_open(1,48000,0)
adcrefvoltage = 5.0
#(a,b) = pi.spi_read(bus,count)
#(byte_count, rx_data) = pi.spi_xfer(bus,tx_data)
#pi.spi_write(bus,data)
def close_bus():
    pi.spi_close(bus)
    pi.spi_close(mic)
    pi.stop()
def adc_init(): #Try to figure out availability, should be some noise if connected
    if (read_adc_raw(0,0) <= 2):
        return 0
    return 1
def mic_init():
    if(estimate_noise(300) == 2048.0):
        return 0
    return 1
def read_mic():
    (count,buf) = pi.spi_read(mic,2)
    #print(count)
    sample = (buf[0]<< 8) + buf[1]
    if sample & 0x800 == 0x800:    #check sign bit
        sample = -1*sample + 2048
    else:
        sample = 2048 - sample
    return sample #*3.3/23
def estimate_noise(sample_count = 100):
    sample = 0
    for i in range(sample_count):
        sample += abs(read_mic())
    return round(sample/sample_count,2)
def read_adc_voltage(channel, mode):
    """
    Read the voltage from the selected channel on the ADC
     Channel = 1 or 2, MODE = 0 för enkanals-läs, 1 för differential
    """
    if (channel > 1) or (channel < 0):
        raise ValueError('read_adc_voltage: channel out of range')
    if (mode > 1) or (mode < 0):
        raise ValueError('read_adc_voltage: mode out of range')
    raw = read_adc_raw(channel, mode)
    voltage = (adcrefvoltage / 4096) * raw
    return voltage
def read_adc_raw(channel, mode):
    """
    Read the raw value from the selected channel on the ADC
    Channel = 1 or 2
    """
    if (channel > 1) or (channel < 0):
        raise ValueError('read_adc_voltage: channel out of range')
    if (mode > 1) or (mode < 0):
        raise ValueError('read_adc_voltage: mode out of range')
    if mode == 0:
        (count,raw) = pi.spi_xfer(bus,[1,(8+channel)<<4,0])
        ret = ((raw[1] & 0x0F) << 8) + (raw[2])
    if mode == 1:
        if channel == 1:
            (count,raw) = pi.spi_xfer(bus,[1, 0x00, 0])
        else:
            (count,raw) = pi.spi_xfer(bus,[1, 0x40, 0])
        ret = ((raw[1]) << 8) + (raw[2])
    return ret
