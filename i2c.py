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
__version__     = "1.0.1"
__maintainer__  = "Eunchong Kim"
__email__       = "chariskimec@gmail.com"
__status__      = "Production"



# ================================================
import argparse, json, logging, sqlite3, os, time, smbus, sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# InfluxDB client
from helpers.influxdbclient import InfluxDBClient

# Device
from devices.aht10 import AHT10
from devices.aht21 import AHT21
from devices.ccs811 import CCS811
import bme680 as BME680
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306 as SSD1306


# -------------------------
# Parser for arguments
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--INFLUXDB_TOKEN', help='InfluxDB token')
parser.add_argument('--logging_filename', help='Logging output file name')
args = parser.parse_args()
if args.INFLUXDB_TOKEN:
    os.environ['INFLUXDB_TOKEN'] = args.INFLUXDB_TOKEN


# -------------------------
# Logging
Path('log').mkdir(parents=True, exist_ok=True)
logging_filename = args.logging_filename if args.logging_filename else 'log/i2c.log'
logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            TimedRotatingFileHandler(logging_filename, when='W0')
            ]
        )


# -------------------------
# Important (static) variables
INTERVAL_SECOND = 5.0
TIMEOUT_SECOND = 60.0


# -------------------------
# Load config
json_file = open('config.json')
config = json.load(json_file)


# ================================================
# Initialize
# -------------------------
# Influx DB
idc = InfluxDBClient()


# -------------------------
# I2C
device_list = []
for config_device in config['devices']:
    # AHT10
    if config_device['name'] == 'AHT10':
        aht10 = AHT10(config_device['bus'])
        aht10.initialize()

    # AHT21
    elif config_device['name'] == 'AHT21':
        aht21 = AHT21(config_device['bus'])
        #aht21.initialize()

    # CCS811
    elif config_device['name'] == 'CCS811':
        ccs811 = CCS811(config_device['bus'])
        ccs811.initialize()

    # BME680
    elif config_device['name'] == 'BME680':
        bme680 = BME680.BME680(int(config_device['address'], 16), smbus.SMBus(config_device['bus']))
        bme680.set_humidity_oversample(BME680.OS_2X)
        bme680.set_pressure_oversample(BME680.OS_4X)
        bme680.set_temperature_oversample(BME680.OS_8X)
        bme680.set_filter(BME680.FILTER_SIZE_3)
        bme680.set_gas_status(BME680.ENABLE_GAS_MEAS)
        bme680.set_gas_heater_temperature(320)
        bme680.set_gas_heater_duration(150)
        bme680.select_gas_heater_profile(0)
        bme680_burn_in_time = 300
        bme680_gas_res_list = []
        bme680_humidity_list = []
        bme680_gas_res_baseline = 0
        bme680_humidity_baseline = 0
        bme680_humidity_weight = 0.25

    # SSD1306
    elif config_device['name'] == 'SSD1306':
        serial = i2c(port=config_device['bus'], address=int(config_device['address'], 16))
        ssd1306 = SSD1306(serial)


# ================================================
# Loop
start_time = time.time()
error_cnt = 0
while (True):
    now_dt_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    result_list = []
    for config_device in config['devices']:
        # AHT10
        if config_device['name'] == 'AHT10':
            humidity, temperature = aht10.getHumidityTemperature()
            temp_dict = {
                    'name': config_device['name'],
                    'measures': {'humidity': humidity, 'temperature': temperature}
                    }
            result_list.append(temp_dict)
            logging.info(f'AHT10: Humid: {humidity:.0f}±2%, Tempe: {temperature:.1f}±0.3°C')

        # AHT21
        if config_device['name'] == 'AHT21':
            humidity, temperature = aht21.getHumidityTemperature()
            temp_dict = {
                    'name': config_device['name'],
                    'measures': {'humidity': humidity, 'temperature': temperature}
                    }
            result_list.append(temp_dict)
            logging.info(f'AHT21: humidity: {humidity:.0f}±2%, Tempe: {temperature:.1f}±0.3°C')

        # CCS811
        if config_device['name'] == 'CCS811':
            eCO2, eTVOC = ccs811.getECO2ETVOC() # Not use eCO2 value
            temp_dict = {
                    'name': config_device['name'],
                    'measures': {'eTVOC': eTVOC}
                    }
            result_list.append(temp_dict)
            logging.info(f'CCS811: eTVOC: {eTVOC} ppb')

        # BME680
        if config_device['name'] == 'BME680':
            humidity = temperature = pressure = iaq = -1
            if bme680.get_sensor_data():
                temperature = bme680.data.temperature
                pressure = bme680.data.pressure
                humidity = bme680.data.humidity
                if bme680.data.heat_stable:
                    gas_resistance = bme680.data.gas_resistance
                    curr_time = time.time()
                    if curr_time - start_time < bme680_burn_in_time:
                        bme680_humidity_list.append(humidity)
                        bme680_gas_res_list.append(gas_resistance)
                    else:
                        if bme680_gas_res_baseline == 0:
                            bme680_gas_res_baseline = sum(bme680_gas_res_list)/len(bme680_gas_res_list)
                        if bme680_humidity_baseline == 0:
                            bme680_humidity_baseline = sum(bme680_humidity_list)/len(bme680_humidity_list)
                        humidity_score = humidity/bme680_humidity_baseline * bme680_humidity_weight * 100
                        gas_res_score = gas_resistance/bme680_gas_res_baseline * (1-bme680_humidity_weight) * 100
                        iaq = humidity_score + gas_res_score
            temp_dict = {
                    'name': config_device['name'],
                    'measures': {
                        'humidity': humidity, 'temperature': temperature,
                        'pressure': pressure, 'iaq': iaq
                        }
                    }
            result_list.append(temp_dict)
            logging.info(f"""BME680:
                    Humid: {humidity:.0f}±3%, Tempe: {temperature:.1f}±1°C,
                    Press: {pressure}hPa, IAQ: {iaq}"""
                    )

        # SSD1306
        if config_device['name'] == 'SSD1306':
            with canvas(ssd1306) as draw:
                draw.rectangle(ssd1306.bounding_box, outline="white", fill="black")
                draw.text((10, 0), f'{now_dt_str}', fill="white")
                draw.text((10, 20), f'{temperature:.1f}°C, {humidity:.1f}%', fill="white")
                draw.text((10, 40), f'{pressure:.0f}hPa, {iaq:.0f}IAQ', fill="white")


    # --------------------------
    # Save to Influx DB
    for result in result_list:

        for k, v in result['measures'].items():
            if v != -1:
                idc.write(result['name'], k, v)
                #print(result['name'], k, v)


    # Write environment data to CCS811
    #if result['name'] == 'CCS811':
    #    ccs811.writeEnvironmentData(humidity, temperature)


    # --------------------------
    # Wait till next interval second
    sleep_time = INTERVAL_SECOND * 10**6 - datetime.utcnow().microsecond # in micro second
    time.sleep(sleep_time/10**6) # in second
