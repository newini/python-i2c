# https://pypi.org/project/smbus2/
import smbus2

import time

# About device
DEVICE_BUS = 0
DEVICE_ADDRESS = 0x38

# commands
INIT_CMD    = 0b1110_0001
TRIGGER_MEAS = 0b1010_1100 # Trigger measurement
SOFTRESET = 0b1011_1010
DATA0 = 0b0011_0011
DATA1 = 0b0000_0000


# Create bus
bus = smbus2.SMBus(DEVICE_BUS)

# Initialize
bus.write_byte_data(
        DEVICE_ADDRESS,
        0x00, # Read R : '1' , write W : '0'
        INIT_CMD
        )

time.sleep(.5) # .5s

# Write to trigger measurement
write_data = [
        TRIGGER_MEAS,
        DATA0,
        DATA1
        ]

while (True):
    bus.write_i2c_block_data(
            DEVICE_ADDRESS,
            0x00, # Read R : '1' , write W : '0'
            write_data)

    time.sleep(1) # 1s

    read_data = bus.read_i2c_block_data(
            DEVICE_ADDRESS,
            0x01, # Read R : '1' , write W : '0'
            6 # 6 bytes
            )

    status = read_data[0]

    # Fill data
    humidity_data = (read_data[1] << 12) + (read_data[2] << 4) + (read_data[3] & 0xf0)
    temperature_data = ((read_data[3] & 0x0f) << 16) + (read_data[4] << 8) + read_data[5]

    # Convert
    humidity = humidity_data/(2**20)*100 # in %
    temperature = temperature_data/(2**20)*200 - 50 # in C

    print('Humidity: {0:.2f} %, Temperature: {1:.2f} C'.format(humidity, temperature) )

