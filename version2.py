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
critical_distance = 0.05  # Default critical distance

def get_user_input():
    global critical_distance
    while True:
        try:
            user_input = float(input("Enter the critical distance in meters (0-20): "))
            if 0 <= user_input <= 20:
                critical_distance = user_input
                break
            else:
                print("Please enter a value between 0 and 20 meters.")
        except ValueError:
            print("Invalid input. Please enter a numeric value between 0 and 20.")

def control_button():
    global sound_on

    if sound_on:
        if buzzer.on() or buzzer.beep(0.1, 0.1):
            buzzer.off()
    else:
        if float('{:1.2f}'.format(sensor.value)) < 0.20:
            if float('{:1.2f}'.format(sensor.value)) > critical_distance:
                buzzer.on()

        if float('{:1.2f}'.format(sensor.value)) <= critical_distance:
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
            if float('{:1.2f}'.format(sensor.value)) > critical_distance:
                led.color = (1, 1, 0)
                buzzer.on()

        if float('{:1.2f}'.format(sensor.value)) <= critical_distance:
            led.color = (1, 0, 0)
            buzzer.beep(0.1, 0.1)
            sleep(0.5)

def safe_exit(signum, frame):
    exit(1)

try:
    get_user_input()  # Get user input for critical distance

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

