#!/bin/bash

source ../env_i2c_monitor.sh

nohup 2>&1 python3 i2c.py &
