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
import logging, time

# Devices
from devices.aht10 import AHT10
from devices.ccs811 import CCS811


#================================================
# Static variables
DEVICE_BUS = 0

# Logging
logging.basicConfig(
        format='%(asctime)s %(message)s',
        level=logging.DEBUG
        )

# AHT10
aht10 = AHT10(DEVICE_BUS)
aht10.initialize()

# CCS811
ccs811 = CCS811(DEVICE_BUS)
ccs811.initialize()


#================================================
# Loop
while (True):
    current_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    humidity, temperature = aht10.getHumidityTemperature()
    logging.info('Humidity: {0:.2f} %, Temperature: {1:.2f} C'.format(humidity, temperature) )

    eCO2, TVOC = ccs811.getECO2TVOC()
    logging.info('eCO2: {0} ppm, TVOC: {1} ppb'.format(eCO2, TVOC))

    # Wait till next second
    sleep_time = 10**6 - datetime.utcnow().microsecond # in micro second
    time.sleep(sleep_time/10**6) # in second
