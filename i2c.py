#!/bin/env python3
# -*- coding: utf-8 -*-
# i2c.py
"""
Use I2C to read humidity and temperature data, by using smbus2
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
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=+9), 'JST') # Timezone
import argparse, logging, sqlite3, os, time

# Devices
from devices.aht10 import AHT10
from devices.ccs811 import CCS811

# InfluxDB client
from helpers.influxdbclient import InfluxDBClient


#================================================
# Parser for arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--INFLUXDB_TOKEN', help='InfluxDB token')
parser.add_argument('--logging_filename', help='Logging output file name')
args = parser.parse_args()
if args.INFLUXDB_TOKEN:
    os.environ['INFLUXDB_TOKEN'] = args.INFLUXDB_TOKEN


#================================================
# Important (static) variables
INTERVAL_SECOND = 5.0
TIMEOUT_SECOND = 60.0


#================================================
# I2C
DEVICE_BUS0 = 0
DEVICE_BUS1 = 1

# Logging
logging_filename = args.logging_filename if args.logging_filename else 'logs/i2c.log'
logging.basicConfig(
        filename=logging_filename,
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG
        )

# AHT10
aht10 = AHT10(DEVICE_BUS0)
aht10.initialize()

# CCS811
ccs811 = CCS811(DEVICE_BUS1)
ccs811.initialize()


#================================================
# Influx DB
idc = InfluxDBClient()


#================================================
# Loop
error_cnt = 0
while (True):
    current_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # AHT10
    humidity, temperature = aht10.getHumidityTemperature()
    # CCS811
    eCO2, eTVOC = ccs811.getECO2ETVOC() # Not use eCO2 value

    logging.info('Humidity: {0:.0f} ± 2%, Temperature: {1:.1f} ± 0.3 C, eTVOC: {2} ppb'.format(
        humidity, temperature, eTVOC)
        )

    # Check data
    if humidity == temperature == -1 or eTVOC == -1:
        error_cnt += 1

        # Stop if emits wrong data continously
        if error_cnt >= TIMEOUT_SECOND/INTERVAL_SECOND:
            logging.error('Something wrong. Stop')
            break

    else:
        if error_cnt > 0:
            error_cnt = 0

        # Write environment data to CCS811
        ccs811.writeEnvironmentData(humidity, temperature)

        # Save to Influx DB
        idc.write('aht10', 'temperature', temperature)
        idc.write('aht10', 'humidity', humidity)
        idc.write('ccs811', 'eTVOC', eTVOC)

    # Wait till next interval second
    sleep_time = INTERVAL_SECOND * 10**6 - datetime.utcnow().microsecond # in micro second
    time.sleep(sleep_time/10**6) # in second
