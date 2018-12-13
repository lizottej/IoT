#!/usr/bin/python

import bme680
import bluetooth
import time

#Wia Setup
from wia import Wia
wia = Wia()
wia.access_token = "d_sk_APtVoYG6uaLRqQOJzHlhJfAO"   # Change to whatever secret key for your wia

# Temperature Sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

sensor.set_temperature_oversample(bme680.OS_8X)

print ("================================================")
print ("     Vehicle Interior Safety System Check       ")
print ("================================================")

# Loop to continuously check variable status values
while True:
    #Bluetooth Proximity
    nearby_devices = bluetooth.discover_devices()
    result = bluetooth.lookup_name("04:C2:3E:B6:33:DA", timeout=30)    # Enter MAC address of the BT device to lookout for
    #Temperature Sensor
    check_sensors = sensor.get_sensor_data()
    temp = sensor.data.temperature
    temp_display = "{0:.2f}".format(sensor.data.temperature)

    print (" ")
    print ("Checking " + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
    print ("...")    if (temp > 25 and result == None):
        print ("----------------------------------------------------------------------------")
        print ("    Passenger Seat: Occupied | Parent: Absent | Status: Unsafe [CAUTION]    ")
        print ("----------------------------------------------------------------------------")

        alert = 'Unsafe'
        wia.Event.publish(name="Alert", data=alert)

    else:
        print ("-------------------------------------------------------------")
        print ("             Vehicle Status | Under control                  ")
        print ("-------------------------------------------------------------")

    print ("")
    print ("Temperature Sensor:")
    print (temp_display)
    wia.Event.publish(name="Temperature", data=temp_display)
    print ("")
    print ("Bluetooth Device:")
    print (result)
    time.sleep(8)


	