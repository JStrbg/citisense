import smbus
bus = smbus.SMBus(1)
cmd_mod = 0x80
dat_mod = 0x40
def send(addr, mode, data):

    bus.write_i2c_block_data(addr, mode, data)

def init(ADDRESS):
    send(ADDRESS, cmd_mod, [0xae])
    send(ADDRESS, cmd_mod, [0xd5])
    send(ADDRESS, cmd_mod, [0x50])
    send(ADDRESS, cmd_mod, [0x20])
    send(ADDRESS, cmd_mod, [0x81])
    send(ADDRESS, cmd_mod, [0x80])
    send(ADDRESS, cmd_mod, [0xa0])
    send(ADDRESS, cmd_mod, [0xa4])
    send(ADDRESS, cmd_mod, [0xa6])
    send(ADDRESS, cmd_mod, [0xad])
    send(ADDRESS, cmd_mod, [0x80])
    send(ADDRESS, cmd_mod, [0xc0])
    send(ADDRESS, cmd_mod, [0xd9])
    send(ADDRESS, cmd_mod, [0x1f])
    send(ADDRESS, cmd_mod, [0xdb])
    send(ADDRESS, cmd_mod, [0x27])
    send(ADDRESS, cmd_mod, [0xaf])
    send(ADDRESS, cmd_mod, [0xb0])
    send(ADDRESS, cmd_mod, [0x00])
    send(ADDRESS, cmd_mod, [0x11])

def clearDisplay():
    for j in range (0,16):
        send(0x3c, cmd_mod, [0xb0 + j])
        send(0x3c, cmd_mod, [0x0])
        send(0x3c, cmd_mod, [0x10])
        for i in range (0,128):
            send(0x3c, dat_mod, [0x00])

init(0x3c)
clearDisplay()
