#!/bin/env python3
# -*- coding: utf-8 -*-
# devices/bme680.py

from datetime import datetime
import logging, time
from pyi2c import I2CDevice, getBit


class BME680:
    """
    BME680 Class to get humidity and temperature.
    Address is 0x77
    Accuracy:
    - IAQ gas: 0 ~ 500 +- 1
    - humidity: 0 ~ 100 +- 3%
    - pressure: 300 ~ 1100 +- 0.6 hPa
    - temperature: -40 ~ 85 +- 0.5 C (max +- 1 C)
    """
    def __init__(self, bus_n=0, addr=0x77):
        self._i2cdevice         = I2CDevice(bus_n, addr)
        self._INIT_CMD_LIST     = [0x1B, 0x1C, 0x1E]
        self._GET_STATUS        = 0x71 # to get a Status word
        self._TRIG_MEAS_LIST    = [0xAC, 0x33, 0x00] # Trigger measurement. need to wait at least 80 ms

        logging.info('BME680 created.')

    def initialize(self):
        self._i2cdevice.write(self._INIT_CMD_LIST)
        time.sleep(.1) # .1 s
        logging.info('BME680 initialized.')

    def getStatus(self):
        status = self._i2cdevice.writeread(self._GET_STATUS, 1)
        return status

    def checkStatus(self, status):
        is_ok = False
        if getBit(status, 7) == 1:
            logging.warning('BME680 is busy')
        elif getBit(status, 3) == 0:
            logging.warning('BME680 calibration is not enabled')
            self.initialize()
        else:
            is_ok = True
        return is_ok

    def getHumidityTemperature(self):
        # Write trigger measurement
        self._i2cdevice.write(self._TRIG_MEAS_LIST)

        # Sleep at least 80 ms
        time.sleep(.1) # .1 s

        # read 6 bytes of data
        read_data = self._i2cdevice.read(7)
        #print(read_data)

        # Prepare variables
        humidity = temperature = -1

        # Check i2c status code is success
        if self._i2cdevice.status_code.value == 0:

            # Treat status code
            status = read_data[0]
            if self.checkStatus(status):
                # Fill data
                humidity_data = (read_data[1] << 12) + (read_data[2] << 4) + (read_data[3] & 0xf0)
                temperature_data = ((read_data[3] & 0x0f) << 16) + (read_data[4] << 8) + read_data[5]

                # Convert
                humidity = humidity_data/(2**20)*100 # Relative humidity in %
                temperature = temperature_data/(2**20)*200 - 50 # in C

                # My calibration
                # Cause, the value is higher than other sensor
                temperature -= 1

                # Check value
                if (temperature < -40 or 120 < temperature
                        or humidity < 0 or 100 < humidity):
                    logging.warning('BME680 humidity/temperature value is fake.')
                    self.softReset()
                    humidity = temperature = -1

        return humidity, temperature


# Test main
def main():
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            level=logging.DEBUG
            )
    BME680 = BME680()
    while(True):
        humidity, temperature = BME680.getHumidityTemperature()
        logging.info('Humidity: {0:.2f}%, Temperature: {1:.2f}'.format(humidity, temperature))
        sleep_time = 10**6 - datetime.utcnow().microsecond # in micro second
        time.sleep(sleep_time/10**6) # in second


if __name__ == "__main__":
    # execute only if run as a script
    main()
