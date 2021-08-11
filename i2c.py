#!/bin/env python3
# -*- coding: utf-8 -*-
# i2c.py
"""
Use I2C to read huminity and temperature data, by using smbus2
"""

__author__      = "Eunchong Kim"
__copyright__   = "Copyright 2021, Eunchong Kim"
__credits__     = ["Eunchong Kim"]
__license__     = "GPL"
__version__     = "1.0.0"
__maintainer__  = "Eunchong Kim"
__email__       = "chariskimec@gmail.com"
__status__      = "Production"


#================================================
from datetime import datetime
import time
# https://pypi.org/project/smbus2/
import smbus2


#================================================
# Static variables
DEVICE_BUS = 0

# For AHT10
AHT10_ADDR = 0x38
# commands
AHT10_INIT_CMD      = 0b1110_0001 # Initialization command
AHT10_TRIG_MEAS     = 0b1010_1100 # Trigger measurement. need to wait at least 75 ms
AHT10_SOFT_RESET    = 0b1011_1010 # Restart the sensor system. need to wait at least 20 ms
AHT10_DATA0         = 0b0011_0011
AHT10_DATA1         = 0b0000_0000

# For CCS811 (CJMCU-811)
CCS811_ADDR = 0x5a
# commands


#================================================
# Create bus and initialize
bus = smbus2.SMBus(DEVICE_BUS)

# For AHT10
bus.write_byte_data(
        AHT10_ADDR,
        0x00, # Read R : '1' , write W : '0'
        AHT10_INIT_CMD
        )

time.sleep(.1) # .1 s

# For CCS811


#================================================
# Loop
aht10_write_data = [
        AHT10_TRIG_MEAS,
        AHT10_DATA0,
        AHT10_DATA1
        ]

while (True):
    # Write trigger measurement
    bus.write_i2c_block_data(
            AHT10_ADDR,
            0x00, # Read R : '1' , write W : '0'
            aht10_write_data)

    current_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Sleep at least 75 ms
    time.sleep(.1) # .1 s

    # Read 6 bytes of data
    read_data = bus.read_i2c_block_data(
            AHT10_ADDR,
            0x01, # Read R : '1' , write W : '0'
            6 # 6 bytes
            )

    # Treat status code
    status = read_data[0]

    # Fill data
    humidity_data = (read_data[1] << 12) + (read_data[2] << 4) + (read_data[3] & 0xf0)
    temperature_data = ((read_data[3] & 0x0f) << 16) + (read_data[4] << 8) + read_data[5]

    # Convert
    humidity = humidity_data/(2**20)*100 # in %
    temperature = temperature_data/(2**20)*200 - 50 # in C

    print('{0}, Humidity: {1:.2f} %, Temperature: {2:.2f} C'.format(current_datetime_str, humidity, temperature) )

    # Wait till next second
    sleep_time = 10**6 - datetime.utcnow().microsecond # in micro second
    time.sleep(sleep_time/10**6) # in second
