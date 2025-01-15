# –– coding: utf-8 –
#!/usr/bin/python
"""
BMPセンサーから気圧情報をとりだし、ファイル保存する

press_data.txt
BMP180_dataSave.py  python2で実行のこと
BMP180_dataSave3.py  python3で実行のこと

by.kawabata

20230812    BMP180 と BMP280 を意識せずに使えるようにしたい。
 
"""

# 補正値
hosei = 0

import datetime
import time

import i2c_BMP
# BMPセンサーの確認
BMPsesorName = i2c_BMP.BMP_sensor()
print(BMPsesorName)

if BMPsesorName == 'BMP180' :
    import Adafruit_BMP.BMP085 as BMP085
    try:
        sensor = BMP085.BMP085()
        press = ((sensor.read_pressure()+ 50)/ 100 )
    except:
        try:
            time.sleep(1)
            sensor = BMP085.BMP085()
            press = ((sensor.read_pressure()+ 50)/ 100 )
        except:
            try:
                time.sleep(1.5)
                sensor = BMP085.BMP085()
                press = ((sensor.read_pressure()+ 50)/ 100 )
            except:
                time.sleep(3)
                sensor = BMP085.BMP085()
                press = ((sensor.read_pressure()+ 50)/ 100 )

if BMPsesorName == 'BMP280' :
    from bmp280 import BMP280
    try:
        from smbus2 import SMBus
    except ImportError:
        from smbus import SMBus
    # Initialise the BMP280
    bus = SMBus(1)
    bmp280 = BMP280(i2c_dev=bus)
    # 計測
    try:
        press = bmp280.get_pressure()
    except:
        try:
            time.sleep(1)
            press = bmp280.get_pressure()
        except:
            try:
                time.sleep(1.5)
                press = bmp280.get_pressure()
            except:
                time.sleep(3)
                press = bmp280.get_pressure()
    # 初回だけ異常値が出る場合があるので、補正
    if press < 900:
        time.sleep(1)
        press = bmp280.get_pressure()
    # print('{:05.2f}hPa'.format(press))
    press = int(press * 100)/100

print('測定値',end='', flush=True)
print('Pressure = ',press,'hPa' )

print('補正値',end='', flush=True)
print(hosei)

print('補正後',end='', flush=True)
press = press + hosei
print('Pressure = ',press,'hPa' )

print('補正後int ',end='', flush=True)
press = int(press + 0.5)
print('Pressure = ',press,'hPa' )


time.sleep(0.5)
path = '/home/pi/tft_THP/'
dt_now = datetime.datetime.now()
################## press ###################
# # 最新のデータを一つだけ入れたファイルを作る
press_s = str(dt_now) + "  :" + str(press) + '\n' 
# press_s = str(press)
with open(path + 'press_data.txt', mode='a') as f:
    f.write(press_s)
with open(path + 'press_data_last.txt', mode='w') as f:
    f.write(str(press))
############################################

