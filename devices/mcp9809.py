#!/bin/env python3
# -*- coding: utf-8 -*-
# devices/mcp9808.py

from datetime import datetime
import logging, time
from pyi2c import I2CDevice, getBit


class MCP9808:
    """
    MCP9808 Class to measure temperature.
    Address is 0x18
    Accuracy:
        +-0.25 (typical) from -40 C to +125 C
        +-0.5 (maximum) from -20 C to +100 C
        +- 1 C (maximum) from -40 C to +125 C
    """
    def __init__(self, bus_n=0, addr=0x18):
        self._i2cdevice         = I2CDevice(bus_n, addr)
        self._CONFIG_ADDR       = 0x01
        self._ENABLE_EVENT_LIST = [0x00, 0x08] # Enable event output
        self._T_A_POINTER_ADDR  = 0x05
        logging.info('MCP9808 created.')

    def initialize(self):
        self._i2cdevice.write([self._CONFIG_ADDR]+self._ENABLE_EVENT_LIST)
        # Sleep
        #time.sleep(.1) # .1 s
        logging.info('MCP9808 initialized.')

    #def softReset(self):
    #    self._i2cdevice.write(self._SOFT_RESET)
    #    # Sleep at lease 20 ms
    #    time.sleep(.1) # .1 s
    #    logging.info('MCP9808 did soft reset.')

    #def checkStatus(self, status):
    #    is_ok = False
    #    if getBit(status, 7) == 1:
    #        logging.warning('MCP9808 is busy')
    #    elif getBit(status, 3) == 0:
    #        logging.warning('MCP9808 calibration is not enabled')
    #        self.softReset()
    #    else:
    #        is_ok = True
    #    return is_ok

    def getTemperature(self):
        # Write trigger measurement
        #self._i2cdevice.write(self._TRIG_MEAS_LIST)

        # Sleep at least 75 ms
        #time.sleep(.1) # .1 s

        # Read 2 bytes of data
        read_data = self._i2cdevice.writeread(self._T_A_POINTER_ADDR, 2)

        # Init variables
        temperature = -1

        # Check i2c status code is success
        if self._i2cdevice.status_code.value == 0:

            # Fill data
            temperature = ((read_data[0] & 0x0f) * 2**4) + (read_data[1] * 2**-4)

            # Check value
            if temperature < -40 or 125 < temperature:
                logging.warning('MCP9808 temperature value is fake.')
                #self.softReset()
                temperature = -1

        return temperature


# Test main
def main():
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            level=logging.DEBUG
            )
    mcp9808 = MCP9808(bus_n=3)
    mcp9808.initialize()
    while(True):
        temperature = mcp9808.getTemperature()
        logging.info('Temperature: {:.2f} +- 0.25 C'.format(temperature))
        sleep_time = 10**6 - datetime.utcnow().microsecond # in micro second
        time.sleep(sleep_time/10**6) # in second


if __name__ == "__main__":
    # execute only if run as a script
    main()
