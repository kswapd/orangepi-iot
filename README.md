# orangepi-iot

## Description
We use an orangepi zero and a LCD to fetch and display realtime crypto currency market info by wifi, and with an additional sht30 sensor to add to orangepi i2c driver, we can also get realtime temperature and humidity.


## Introduction
We have to target currently:  
* 1. Get realtime crypto currency market info from remote http server.
* 2. Get weather forcast report from remote http server, we also want to use a sensor to capture local  temperature and humidity.
Now we have a development kit orangepi zero and a 1.8 inch(resolution 128x160) LCD with st7735 driver. Orangepi zero supports wifi module and one SPI bus.   

## Preparation

1. Orangepi zero development kit with ubuntu 20.04 server installed.
2. A 1.8 inch(resolution 128x160) LCD with st7735 driver
3. sht30 temperature and humidity sensor, we use GT-HT30 to replace it as their pins are compatible.

## Steps

1. Install python dependence.
   ```bash
   sudo python3 -m pip install OPi.GPIO spidev Pillow numpy
   sudo python3 -m pip install st7735
   ```
if installing numpy has error, you can use following cmd:
```
apt-get install python3-numpy
```

2. Modify st7735 __init__.py code in pip packages , as it only supports Raspi berry.  
   
   import RPi.GPIO as GPIO    ->   import OPi.GPIO as GPIO

3. Run python file to test.
   ```bash
   python3 lcd_demo.py
   ```

4. Test all code.
    
```bash
   python3 orangepi-iot.py
   ```


