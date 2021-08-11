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
from smbus2 import SMBus, i2c_msg


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
CCS811_APP_START_ADDR = 0xf4 # from boot to application mode
CCS811_MEAS_MODE_ADDR = 0x01
# 0: write, 001: every second, 0: nINT interrupt disable, 0: operate normally, 00: nothing
CCS811_MEAS_MODE_CMD = 0b0001_0000
CCS811_RESULT_ADDR = 0x02


#================================================
# Create bus and initialize
bus = SMBus(DEVICE_BUS)

# For AHT10
bus.write_byte_data(
        AHT10_ADDR,
        0x00, # Read R : '1' , write W : '0'
        AHT10_INIT_CMD
        )

time.sleep(.1) # .1 s

# For CCS811
bus.write_byte_data(
        CCS811_ADDR,
        0, # write
        CCS811_APP_START_ADDR)
bus.write_i2c_block_data(
        CCS811_ADDR,
        0, # write
        [CCS811_MEAS_MODE_ADDR, CCS811_MEAS_MODE_CMD])

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

    # ------------------------------------------------
    # Read data

    # AHT10, read 6 bytes of data
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


    # CCS811, read total 8 bytes of data
    # Select result register address
    read_data = i2c_msg.read(CCS811_ADDR, 8) # 8 bytes
    bus.i2c_rdwr(
            i2c_msg.write(CCS811_ADDR, [CCS811_RESULT_ADDR]),
            read_data
            )
    read_data = [ int(data) for data in read_data ]
    # Convert i2c_msg to integer
    #bus.write_byte_data(
    #        CCS811_ADDR,
    #        0, # write
    #        CCS811_RESULT_ADDR
    #        )
    #read_data = bus.read_i2c_block_data(
    #        CCS811_ADDR,
    #        1, # read
    #        8 # 8 bytes
    #        )

    # Fill data
    eCO2 = (read_data[0] << 8) + read_data[1] # equivalent CO2. from 400 ppm to 8192 ppm
    TVOC = (read_data[2] << 8) + read_data[3] # Total Volatile Organic Compound. from 0 ppb to 1187 ppb
    status = read_data[4]
    error_id = read_data[5]
    current = read_data[6] & 0b1111_1100
    raw_adc = (read_data[6] & 0b0000_0011) + read_data[7]

    # Treat status
    if not status & 2**0 == 0:
        print('Error')
    else:
        print('{0}, eCO2: {1} ppm, TVOC: {2} ppb'.format(current_datetime_str, eCO2, TVOC))

    # Wait till next second
    sleep_time = 10**6 - datetime.utcnow().microsecond # in micro second
    time.sleep(sleep_time/10**6) # in second
