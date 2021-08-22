# Use python smbus2 to I2C between Pi and I2C device


## 1. I2C

### 1.1 I2C Devices
- AHT10: measures Humidity in % and temperature in Celcius.
- CCS811(board name is CJMCU-811): measures equivalent CO2 in ppm and Total Volatile Organic Compound in ppb.


### 1.2 Preperation
Used python packages:
- `pyi2c`: to communicate with I2C devices. This includes `smbus2`
- `influxdb_client`: to save measurement data to InfluxDB server

Install python packages
```
pip3 install pyi2c influxdb_client
```


### 1.3 Run
```
python3 i2c.py
```

Run in background
```
nohup python3 i2c.py > logs/i2c.out &
```


## 2. Webserver (Not use anymore)

### 2.1 Preperation
- django
```
pip3 install django
```


### 2.2 Run
```
./runserver.sh
```


## For developers
### Reset SQLite3 django model
```
python3 manage.py migrate --fake monitor zero
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
python3 manage.py makemigrations
python3 manage.py migrate --fake-initial
```
[How to Reset Migrations](https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html)


## Datasheets
- [AHT10](https://server4.eca.ir/eshop/AHT10/Aosong_AHT10_en_draft_0c.pdf)
- [CCS811](https://cdn.sparkfun.com/assets/learn_tutorials/1/4/3/CCS811_Datasheet-DS000459.pdf)


## Reference
- [CJMCU-811](https://revspace.nl/CJMCU-811)
