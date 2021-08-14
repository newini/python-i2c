#!/bin/env python3
# -*- coding: utf-8 -*-
# devices/ccs811.py

import logging, time
# https://pypi.org/project/smbus2/
from smbus2 import SMBus, i2c_msg


# CCS811 (CJMCU-811) address
CCS811_ADDR = 0x5a
# commands
CCS811_APP_START_ADDR = 0xf4 # from boot to application mode
CCS811_MEAS_MODE_ADDR = 0x01
# 0: write, 001: every second, 0: nINT interrupt disable, 0: operate normally, 00: nothing
CCS811_MEAS_MODE_CMD = 0b0001_0000
CCS811_RESULT_ADDR = 0x02


class CCS811:
    """
    CCS811 -- the board name is CJMCU-811 --
    can measure equivalent CO2 (eCO2) in ppm
    and Total Volatile Organic Compound (TVOC) in ppb.

    CAUTION
    DO NOT USE single transaction such as bus.write_byte, it doew not work.
    Use bus.i2c_rdwr( i2c_msg ), instead.
    """
    def __init__(self, bus_n=0, addr=0x5a):
        self._bus = SMBus(bus_n)
        self._addr = addr
        logging.info('CCS811 created.')

    def initialize(self):
        # Start application mode
        write_msg = i2c_msg.write(
                self._addr,
                [CCS811_APP_START_ADDR]
                )
        self._bus.i2c_rdwr(write_msg)
        time.sleep(.1) # .1 s
        logging.info('CCS811 initialized.')

        # Set measurement mode
        write_msg = i2c_msg.write(
                self._addr,
                [
                    CCS811_MEAS_MODE_ADDR,
                    CCS811_MEAS_MODE_CMD
                    ]
                )
        self._bus.i2c_rdwr(write_msg)
        time.sleep(.1) # .1 s
        logging.info('CCS811 set to measurement mode.')

    def getECO2TVOC(self):
        # Select result register address
        # and read 8 bytes data rapidly
        write = i2c_msg.write(self._addr, [CCS811_RESULT_ADDR])
        read = i2c_msg.read(self._addr, 8) # 8 bytes
        self._bus.i2c_rdwr(write, read)
        # Convert i2c_msg list to integer list
        read_data = list(read)

        # Fill data
        eCO2 = (read_data[0] << 8) + read_data[1] # equivalent CO2. from 400 ppm to 8192 ppm
        TVOC = (read_data[2] << 8) + read_data[3] # Total Volatile Organic Compound. from 0 ppb to 1187 ppb
        status = read_data[4]
        error_id = read_data[5]
        current = read_data[6] & 0b1111_1100
        raw_adc = (read_data[6] & 0b0000_0011) + read_data[7]

        # Treat status
        is_valid_data = False
        if not status & 2**0 == 0:
            logging.warning('CCS811 has error')
            if not error_id & 2**0 == 0:
                logging.warning(' -- WRITE_REG_INVALID.')
            elif not error_id & 2**1 == 0:
                logging.warning(' -- READ_REG_INVALID.')
            elif not error_id & 2**2 == 0:
                logging.warning(' -- MEASMODE_INVALID.')
            elif not error_id & 2**3 == 0:
                logging.warning(' -- MAX_RESISTANCE. The sensor resistance measurement has reached or exceeded the maximum range.')
            elif not error_id & 2**4 == 0:
                logging.warning(' -- HEATER_FAULT. The Heater current in the CCS811 is not in range')
            elif not error_id & 2**5 == 0:
                logging.warning(' -- HEATER_SUPPLY. The Heater voltage is not being applied correctly')
        elif status & 2**3 == 0:
            logging.info('CCS811 has no new data')
        elif status & 2**4 == 0:
            logging.info('CCS811 did not load valid application firmware')
        elif status & 2**7 == 0:
            logging.info('CCS811 is not in application mode')
        else:
            is_valid_data = True

        if is_valid_data:
            return eCO2, TVOC
        else:
            return -1, -1


# Test main
def main():
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            level=logging.DEBUG
            )
    ccs811 = CCS811()
    ccs811.initialize()
    eCO2, TVOC = ccs811.getECO2TVOC()
    logging.info('eCO2: {0} ppm, TVOC: {1} ppb'.format(eCO2, TVOC))


if __name__ == "__main__":
    # execute only if run as a script
    main()
