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
from datetime import datetime
import argparse, logging, sqlite3, os, time, sys
from logging.handlers import TimedRotatingFileHandler

# Devices
from devices.aht10 import AHT10
from devices.aht21 import AHT21
from devices.ccs811 import CCS811
import bme680

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
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            TimedRotatingFileHandler(logging_filename, when='W0')
            ]
        )

# AHT10
aht10 = AHT10(DEVICE_BUS0)
aht10.initialize()

# AHT21
aht21 = AHT21(DEVICE_BUS1)
#aht21.initialize()

# CCS811
ccs811 = CCS811(DEVICE_BUS1)
ccs811.initialize()

# BME680
bme680_ = bme680.BME680(0x77)
bme680_.set_humidity_oversample(bme680.OS_2X)
bme680_.set_pressure_oversample(bme680.OS_4X)
bme680_.set_temperature_oversample(bme680.OS_8X)
bme680_.set_filter(bme680.FILTER_SIZE_3)
bme680_.set_gas_status(bme680.ENABLE_GAS_MEAS)
bme680_.set_gas_heater_temperature(320)
bme680_.set_gas_heater_duration(150)
bme680_.select_gas_heater_profile(0)
bme680_burn_in_time = 300
bme680_gas_res_list = []
bme680_humidity_list = []
bme680_gas_res_baseline = 0
bme680_humidity_baseline = 0
bme680_humidity_weight = 0.25

#================================================
# Influx DB
idc = InfluxDBClient()


#================================================
# Loop
start_time = time.time()
error_cnt = 0
while (True):
    current_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # AHT10
    humidity_aht10, temperature_aht10 = aht10.getHumidityTemperature()
    # AHT21
    humidity_aht21, temperature_aht21 = aht21.getHumidityTemperature()
    # CCS811
    eCO2, eTVOC = ccs811.getECO2ETVOC() # Not use eCO2 value
    # BME680
    humidity_bme680 = temperature_bme680 = pressure_bme680 = iaq = -1
    if bme680_.get_sensor_data():
        temperature_bme680 = bme680_.data.temperature
        pressure_bme680 = bme680_.data.pressure
        humidity_bme680 = bme680_.data.humidity
        if bme680_.data.heat_stable:
            gas_resistance = bme680_.data.gas_resistance
            curr_time = time.time()
            if curr_time - start_time < bme680_burn_in_time:
                bme680_humidity_list.append(humidity_bme680)
                bme680_gas_res_list.append(gas_resistance)
            else:
                if bme680_gas_res_baseline == 0:
                    bme680_gas_res_baseline = sum(bme680_gas_res_list)/len(bme680_gas_res_list)
                if bme680_humidity_baseline == 0:
                    bme680_humidity_baseline = sum(bme680_humidity_list)/len(bme680_humidity_list)
                humidity_score = humidity_bme680/bme680_humidity_baseline * bme680_humidity_weight * 100
                gas_res_score = gas_resistance/bme680_gas_res_baseline * (1-bme680_humidity_weight) * 100
                iaq = humidity_score + gas_res_score

    logging.info("""AHT10: Humi: {0:.0f}±2%, Temp: {1:.1f}±0.3C,
            \tAHT21: Humi: {2:.0f}±2%, Temp: {3:.1f}±0.3C,
            \tCCS811: eTVOC: {4} ppb,
            \tBME680: Humi: {5:.0f}±3%, Temp: {6:.1f}±1C, Pres: {7}, IAQ: {8}""".format(
        humidity_aht10, temperature_aht10,
        humidity_aht21, temperature_aht21,
        eTVOC,
        humidity_bme680, temperature_bme680, pressure_bme680, iaq)
        )


    # Save to Influx DB
    if temperature_aht10 != -1 and humidity_aht10 != -1:
        idc.write('aht10', 'temperature', temperature_aht10)
        idc.write('aht10', 'humidity', humidity_aht10)

        # Write environment data to CCS811
        ccs811.writeEnvironmentData(humidity_aht10, temperature_aht10)

    if eTVOC != -1:
        idc.write('ccs811', 'eTVOC', eTVOC)

    if humidity_aht21 != -1 and temperature_aht21 != -1:
        idc.write('aht21', 'temperature', temperature_aht21)
        idc.write('aht21', 'humidity', humidity_aht21)

    if humidity_bme680 != -1 and temperature_bme680 != -1 and pressure_bme680 != -1:
        idc.write('bme680', 'temperature', temperature_bme680)
        idc.write('bme680', 'humidity', humidity_bme680)
        idc.write('bme680', 'pressure', pressure_bme680)

    if iaq != -1:
        idc.write('bme680', 'iaq', iaq)


    # Wait till next interval second
    sleep_time = INTERVAL_SECOND * 10**6 - datetime.utcnow().microsecond # in micro second
    time.sleep(sleep_time/10**6) # in second
