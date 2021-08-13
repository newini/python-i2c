#!/bin/env python3
# -*- coding: utf-8 -*-
# devices/aht10.py

import logging, time
# https://pypi.org/project/smbus2/
from smbus2 import SMBus


# AHT10 address
AHT10_ADDR = 0x38
# commands
AHT10_INIT_CMD      = 0b1110_0001 # 0xe1. Initialization command
AHT10_TRIG_MEAS     = 0b1010_1100 # 0xac. Trigger measurement. need to wait at least 75 ms
AHT10_SOFT_RESET    = 0b1011_1010 # Restart the sensor system. need to wait at least 20 ms
AHT10_DATA0         = 0b0011_0011 # 0x33
AHT10_DATA1         = 0b0000_0000 # 0x00


class AHT10:
    """
    AHT10 Class to get humidity and temperature
    """
    def __init__(self, bus_n=0, addr=0x38):
        self._bus = SMBus(bus_n)
        self._addr = addr
        logging.info('AHT10 created.')

    def initialize(self):
        self._bus.write_byte_data(
                self._addr,
                0x00, # Read R : '1' , write W : '0'
                AHT10_INIT_CMD
                )
        # Sleep
        time.sleep(.1) # .1 s
        logging.info('AHT10 initialized.')

    def getHumidityTemperature(self):
        write_data = [
            AHT10_TRIG_MEAS,
            AHT10_DATA0,
            AHT10_DATA1
            ]

        # Write trigger measurement
        self._bus.write_i2c_block_data(
                AHT10_ADDR,
                0x00, # Read R : '1' , write W : '0'
                write_data
                )

        # Sleep at least 75 ms
        time.sleep(.1) # .1 s

        # AHT10, read 6 bytes of data
        read_data = self._bus.read_i2c_block_data(
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

        return humidity, temperature


# Test main
def main():
    logging.basicConfig(
            format='%(asctime)s %(message)s',
            level=logging.DEBUG
            )
    aht10 = AHT10()
    aht10.initialize()
    humidity, temperature = aht10.getHumidityTemperature()
    logging.info('Humidity: {0:.2f}%, Temperature: {1:.2f}'.format(humidity, temperature))


if __name__ == "__main__":
    # execute only if run as a script
    main()
