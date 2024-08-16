"""
Resets connection to biotracker 
"""

def reset_biotrack():
     import RPi.GPIO as GPIO
     import time

     Relay_Ch1 = 26
     #Relay_Ch2 = 20
     #Relay_Ch3 = 21

     GPIO.setwarnings(False)
     GPIO.setmode(GPIO.BCM)
     GPIO.setup(Relay_Ch1,GPIO.OUT)
     GPIO.output(Relay_Ch1,GPIO.HIGH)
     time.sleep(0.25)
     GPIO.output(Relay_Ch1,GPIO.LOW)

