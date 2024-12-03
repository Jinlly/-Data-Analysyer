#!/usr/bin/python3

from signal import signal, SIGTERM, SIGHUP, SIGINT, pause
from time import sleep
from threading import Thread
from gpiozero import DistanceSensor, Buzzer, LED, RGBLED, Button

led = RGBLED(13, 19, 26)
sensor = DistanceSensor(echo=20, trigger=21)
buzzer = Buzzer(24)
button = Button(12)

reading = True
sound_on = 1

def control_button():
    global sound_on

    if sound_on:
        if buzzer.on() or buzzer.beep(0.1, 0.1):
            buzzer.off()
    else:
        if float('{:1.2f}'.format(sensor.value)) < 0.20:
            if float('{:1.2f}'.format(sensor.value)) > 0.05:
                buzzer.on()

        if float('{:1.2f}'.format(sensor.value)) <= 0.05:
            buzzer.beep(0.1, 0.1)
            sleep(0.5)

    sound_on = 0

def read_distance():
    while reading:
        print("Distance: " + '{:1.2f}'.format(sensor.value) + " m")
        sleep(0.1)

        if float('{:1.2f}'.format(sensor.value)) >= 0.20:
            led.color = (0, 1, 0)
            buzzer.off()

        if float('{:1.2f}'.format(sensor.value)) < 0.20:
            if float('{:1.2f}'.format(sensor.value)) > 0.05:
                led.color = (1, 1, 0)
                buzzer.on()

        if float('{:1.2f}'.format(sensor.value)) <= 0.05:
            led.color = (1, 0, 0)
            buzzer.beep(0.1, 0.1)
            sleep(0.5)

def safe_exit(signum, frame):
    exit(1)

try:
    reader = Thread(target=read_distance, daemon=True)
    reader.start()

    button.when_pressed = control_button

    pause()

    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    signal(SIGINT, safe_exit)

except KeyboardInterrupt:
    pass

finally:
    reading = False
    sensor.close()
    buzzer.close()
    led.close()
