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

# Devices
from devices.aht10 import AHT10



#================================================
# Static variables
DEVICE_BUS = 0

# For CCS811 (CJMCU-811)
CCS811_ADDR = 0x5a
# commands
CCS811_APP_START_ADDR = 0xf4 # from boot to application mode
CCS811_MEAS_MODE_ADDR = 0x01
# 0: write, 001: every second, 0: nINT interrupt disable, 0: operate normally, 00: nothing
CCS811_MEAS_MODE_CMD = 0b0001_0000
CCS811_RESULT_ADDR = 0x02

# AHT10
aht10 = AHT10(DEVICE_BUS)
aht10.initialize()

#================================================
# Create bus and initialize
bus = SMBus(DEVICE_BUS)

# For CCS811
# Start application mode
bus.write_byte_data(
        CCS811_ADDR,
        0, # write
        CCS811_APP_START_ADDR
        )
time.sleep(.1) # .1 s

# Set measurement mode
bus.write_i2c_block_data(
        CCS811_ADDR,
        0, # write
        [CCS811_MEAS_MODE_ADDR, CCS811_MEAS_MODE_CMD]
        )
time.sleep(.1) # .1 s


#================================================
# Loop
while (True):
    current_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    # ------------------------------------------------
    humidity, temperature = aht10.getHumidityTemperature()

    print('{0}, Humidity: {1:.2f} %, Temperature: {2:.2f} C'.format(current_datetime_str, humidity, temperature) )


    # CCS811, read total 8 bytes of data
    # Select result register address
    i2c_read = i2c_msg.read(CCS811_ADDR, 8) # 8 bytes
    bus.i2c_rdwr(
            i2c_msg.write(CCS811_ADDR, [CCS811_RESULT_ADDR]),
            i2c_read
            )
    read_data = list(i2c_read) # Convert i2c_msg to integer

    # Fill data
    eCO2 = (read_data[0] << 8) + read_data[1] # equivalent CO2. from 400 ppm to 8192 ppm
    TVOC = (read_data[2] << 8) + read_data[3] # Total Volatile Organic Compound. from 0 ppb to 1187 ppb
    status = read_data[4]
    error_id = read_data[5]
    current = read_data[6] & 0b1111_1100
    raw_adc = (read_data[6] & 0b0000_0011) + read_data[7]

    # Treat status
    #if not status & 2**0 == 0:
    if not status == 0x98:
        print('CCS811 Status Warning')
    else:
        print('{0}, eCO2: {1} ppm, TVOC: {2} ppb'.format(current_datetime_str, eCO2, TVOC))

    # Wait till next second
    sleep_time = 10**6 - datetime.utcnow().microsecond # in micro second
    time.sleep(sleep_time/10**6) # in second
