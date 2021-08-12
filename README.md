# Use python smbus2 to I2C between Pi and I2C device

Used I2C devices
- AHT10: measures Humidity in % and temperature in Celcius.
- CCS811(board name is CJMCU-811): measures equivalent CO2 in ppm and Total Volatile Organic Compound in ppb.

Used python packages:
- smbus2


## Preperation
Install python packages
```
pip3 install smbus2
```

## Run
```
python3 main.py
```
