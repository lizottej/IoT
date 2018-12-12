#!/usr/bin/env python
import bme680
import time
import RPi.GPIO as GPIO
from wia import Wia
from gpiozero import Buzzer

print("""Estimate indoor air quality

Runs the sensor for a burn-in period, then uses a
combination of relative humidity and gas resistance
to estimate indoor air quality as a percentage.

Press Ctrl+C to exit

""")

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# start_time and curr_time ensure that the
# burn_in_time (in seconds) is kept track of.

start_time = time.time()
curr_time = time.time()
burn_in_time = 60

burn_in_data = []


buzzer = Buzzer(13)

wia = Wia()
wia.access_token = "d_sk_gcivxeyYB2F3ZjT88GszHkt6" #Access token

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # to use Raspberry Pi board pin numbers
GPIO.setup(29, GPIO.OUT) # set up GPIO output channel
GPIO.setup(31, GPIO.OUT) # set up GPIO output channel
GPIO.output(31, False)
GPIO.output(29, False)

try:
    # Collect gas resistance burn-in values, then use the average
    # of the last 50 values to set the upper limit for calculating
    # gas_baseline.
    print('Collecting gas resistance burn-in data for 1 mins\n')
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)

    gas_baseline = sum(burn_in_data[-50:]) / 50.0

    # Set the humidity baseline to 40%, an optimal indoor humidity.
    hum_baseline = 40.0

    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    hum_weighting = 0.25

    print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
        gas_baseline,
        hum_baseline))

    while True:
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            gas_offset = gas_baseline - gas

            hum = sensor.data.humidity
            hum_offset = hum - hum_baseline
            
            temp = sensor.data.temperature

            # Calculate hum_score as the distance from the hum_baseline.
            if hum_offset > 0:
                hum_score = (100 - hum_baseline - hum_offset)
                hum_score /= (100 - hum_baseline)
                hum_score *= (hum_weighting * 100)

            else:
                hum_score = (hum_baseline + hum_offset)
                hum_score /= hum_baseline
                hum_score *= (hum_weighting * 100)

            # Calculate gas_score as the distance from the gas_baseline.
            if gas_offset > 0:
                gas_score = (gas / gas_baseline)
                gas_score *= (100 - (hum_weighting * 100))

            else:
                gas_score = 100 - (hum_weighting * 100)
                
            # Calculate air_quality_score.
            air_quality_score = hum_score + gas_score

            print('Temp:{0:.2f} C,Gas: {1:.2f} Ohms,Humidity: {2:.2f} %RH,Air Quality: {3:.2f}'.format(
                temp,
                gas,
                hum,
                air_quality_score))

            wia.Event.publish(name="Temperature", data=temp)
            wia.Event.publish(name="Gas", data=gas)
            wia.Event.publish(name="Humidity", data=hum)
            wia.Event.publish(name="Air Quality Score", data=air_quality_score)
            
            if temp > 20:
                GPIO.output(29, True) #Blue light  
            elif temp < 0:
                GPIO.output(31, True) #Red light
            else:
                GPIO.output(31, False) #Red light
                GPIO.output(29, False) #Blue light
                
            if air_quality_score > 70:
               buzzer.on()
               time.sleep(1)
            else :
                buzzer.off()
                time.sleep(1)
            
                        
            time.sleep(1)
            
   
          
except KeyboardInterrupt:
    pass
