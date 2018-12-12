import RPi.GPIO as GPIO, time, os
import time
from wia import Wia

wia = Wia()
wia.access_token = "d_sk_gcivxeyYB2F3ZjT88GszHkt6" #Access token

DEBUG = 1
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

def RCtime (RCpin):
    reading = 0
    GPIO.setup(RCpin, GPIO.OUT)
    GPIO.output(RCpin, GPIO.LOW)
    time.sleep(1)
    
    GPIO.setup(RCpin, GPIO.IN)
    while (GPIO.input(RCpin) == GPIO.LOW):
        reading += 1
    return reading

while True:
    sensorvalue = RCtime(13)
    
    if sensorvalue < 500:
        print "passenger present"
        GPIO.output(11, True) #switch on
        lightstate = "On"
        time.sleep(1)
    else:
        print "no passenger"
        GPIO.output(11, False) #switch off
        lightstate="Off"
        time.sleep(1)
    
    print sensorvalue

    wia.Event.publish(name="Weight", data=sensorvalue)
    
