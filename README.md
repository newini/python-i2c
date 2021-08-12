# Use python smbus2 to I2C between Pi and I2C device


## I2C Devices
- AHT10: measures Humidity in % and temperature in Celcius.
- CCS811(board name is CJMCU-811): measures equivalent CO2 in ppm and Total Volatile Organic Compound in ppb.


## Preperation
Used python packages:
- smbus2

Install python packages
```
pip3 install smbus2
```


## Run
```
python3 main.py
```


## Datasheets
- [AHT10](https://server4.eca.ir/eshop/AHT10/Aosong_AHT10_en_draft_0c.pdf)
- [CCS811](https://cdn.sparkfun.com/assets/learn_tutorials/1/4/3/CCS811_Datasheet-DS000459.pdf)


## Reference
- [CJMCU-811](https://revspace.nl/CJMCU-811)
