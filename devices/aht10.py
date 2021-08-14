#!/bin/env python3
# -*- coding: utf-8 -*-
# devices/aht10.py

import logging, time
from pyi2c import I2CDevice, getBit


# AHT10 address
# commands


class AHT10:
    """
    AHT10 Class to get humidity and temperature.
    Address is 0x38
    """
    def __init__(self, bus_n=0, addr=0x38):
        self._i2cdevice     = I2CDevice(bus_n, addr)
        self._INIT_CMD      = 0b1110_0001 # 0xe1. Initialization command
        self._TRIG_MEAS     = 0b1010_1100 # 0xac. Trigger measurement. need to wait at least 75 ms
        self._SOFT_RESET    = 0b1011_1010 # Restart the sensor system. need to wait at least 20 ms
        self._DATA0         = 0b0011_0011 # 0x33
        self._DATA1         = 0b0000_0000 # 0x00

        logging.info('AHT10 created.')

    def initialize(self):
        self._i2cdevice.write(self._INIT_CMD)
        # Sleep
        time.sleep(.1) # .1 s
        logging.info('AHT10 initialized.')

    def softReset(self):
        self._i2cdevice.write(self._SOFT_RESET)
        # Sleep at lease 20 ms
        time.sleep(.1) # .1 s
        logging.info('AHT10 did soft reset.')

    def getHumidityTemperature(self):
        # Write trigger measurement
        write_data = [
            self._TRIG_MEAS,
            self._DATA0,
            self._DATA1
            ]
        self._i2cdevice.write(write_data)

        # Sleep at least 75 ms
        time.sleep(.1) # .1 s

        # AHT10, read 6 bytes of data
        read_data = self._i2cdevice.read(6)

        # Treat status code
        status = read_data[0]
        is_valid = True
        if getBit(status, 7) == 1:
            logging.warning('AHT10 is busy')
            is_valid = False

        # Fill data
        humidity_data = (read_data[1] << 12) + (read_data[2] << 4) + (read_data[3] & 0xf0)
        temperature_data = ((read_data[3] & 0x0f) << 16) + (read_data[4] << 8) + read_data[5]

        # Convert
        humidity = humidity_data/(2**20)*100 # in %
        temperature = temperature_data/(2**20)*200 - 50 # in C

        # Check value
        if temperature > 85:
            logging.warning('AHT10 temperature value is too hish.')
            self.softReset()
            is_valid = False

        if is_valid:
            return humidity, temperature
        else:
            return -1, -1


# Test main
def main():
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            level=logging.DEBUG
            )
    aht10 = AHT10()
    aht10.initialize()
    humidity, temperature = aht10.getHumidityTemperature()
    logging.info('Humidity: {0:.2f}%, Temperature: {1:.2f}'.format(humidity, temperature))


if __name__ == "__main__":
    # execute only if run as a script
    main()
