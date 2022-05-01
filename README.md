# Use python smbus2 to I2C between Pi and I2C device


## 1. I2C

### 1.0 I2C Devices
- AHT10: measures humidity in % and temperature in Celcius. Not use anymore.
- AHT21: measures humidity in % and temperature in Celcius.
- CCS811(board name is CJMCU-811): measures equivalent CO2 in ppm and Total Volatile Organic Compound in ppb. Not use anymore.
  - Notice: nWAKE should be LOW
- BME680: measure temperature, humidity, pressure, air quarity.
- MCP9808: measure temperature
- SSD1306: 128x64 pixel OLED display



### 1.1 Install linux i2c tools
```
sudo apt install i2c-tools
```
then, try
```
i2cdetect -y 0


#### Trouble shooter
```
If there is error,
```
Error: Could not open file `/dev/i2c-3': Permission denied
Run as root?
```
add your user to `i2c` group,
```
sudo usermod -aG i2c your_username
```
and reboot.



### 1.2 Preperation
#### 1.2.1 Install python3 pakages
Used python packages:
- `pyi2c`: to communicate with I2C devices. This includes `smbus2`
- `influxdb_client`: to save measurement data to InfluxDB server

Install python packages
```
pip install -r requirements.txt
```
or
```
pip3 install pyi2c influxdb_client
```


#### 1.2.2 Get InfluxDB token
In shell, type this to add new environment variable.
```
export INFLUXDB_TOKEN=your_token_here
```

Or, create a script file, such as `env.sh`
```
#!/bin/bash
# env.sh

export INFLUXDB_TOKEN=your_token_here
```
and type in the shell
```
source env.sh
```


### 1.3 Run
```
python3 i2c.py
```

Run in background
```
nohup 2>&1 python3 i2c.py &
# nohup python3 i2c.py > logs/i2c.out &
```



### 2. Data visualization by using InfluxDB




## 3. Webserver (Not use anymore)

### 3.1 Preperation
- django
```
pip3 install django
```


### 3.2 Run
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
- [CCS811 for v2.x.x](https://cdn.sparkfun.com/assets/2/c/c/6/5/CN04-2019_attachment_CCS811_Datasheet_v1-06.pdf)
- [CCS811 for v1.x.x](https://cdn.sparkfun.com/assets/learn_tutorials/1/4/3/CCS811_Datasheet-DS000459.pdf)



## Reference
- [CJMCU-811](https://revspace.nl/CJMCU-811)
