# Use python smbus2 to I2C between Pi and I2C device


## 1. I2C

### 1.1 I2C Devices
- AHT10: measures Humidity in % and temperature in Celcius.
- CCS811(board name is CJMCU-811): measures equivalent CO2 in ppm and Total Volatile Organic Compound in ppb.


### 1.2 Preperation
Used python packages:
- pyi2c
- smbus2

Install python packages
```
pip3 install pyi2c
```


### 1.3 Run
```
python3 start_measurement.py
```

Data will be saved to `db.sqlite3`.


## 2. Webserver

### 2.1 Preperation
- django
- plotly
- dash
```
pip3 install django plotly dash
```


### 2.2 Run
```
./runserver.sh
```


## For developers
### Reset
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
