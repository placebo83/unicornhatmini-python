#!/usr/bin/env python3
import sys
import os
import time, datetime
import RPi.GPIO as GPIO

from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini

unicornhatmini = UnicornHATMini()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP) # A
GPIO.setup(6, GPIO.IN, pull_up_down = GPIO.PUD_UP) # B
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP) # X
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Y

X = 0
Y = 3
B = 0.5

def Dim(channel):
    global B
    B = B - 0.1

    if B <= 0.1:
        B = 0.1

    unicornhatmini.set_brightness(B)

def Bright(channel):
    global B
    B = B + 0.1

    if B >= 1.0:
        B = 1.0

    unicornhatmini.set_brightness(B)

def Shutdown(channel):
    global X
    X = 1

def Color(channel):
    global Y
    Y = Y + 1

GPIO.add_event_detect(5, GPIO.FALLING, callback = Dim, bouncetime = 2000)
GPIO.add_event_detect(6, GPIO.FALLING, callback = Bright, bouncetime = 2000)
GPIO.add_event_detect(16, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)
GPIO.add_event_detect(24, GPIO.FALLING, callback = Color, bouncetime = 2000)

rotation = 180
if len(sys.argv) > 1:
    try:
        rotation = int(sys.argv[1])
    except ValueError:
        print("Usage: {} <rotation>".format(sys.argv[0]))
        sys.exit(1)

unicornhatmini.set_rotation(rotation)
display_width, display_height = unicornhatmini.get_shape()

#print("{}x{}".format(display_width, display_height))

unicornhatmini.set_brightness(B)

font = ImageFont.truetype("/home/pi/unicornhatmini-python/examples/5x7.ttf", 8)

offset_x = 0

while True:

    if Y > 4:
        Y = 0

    if Y == 0:
        r, g, b = (255, 0, 0)   # Red
    elif Y == 1:
        r, g, b = (255, 255, 0) # Yellow
    elif Y == 2:
        r, g, b = (0, 255, 0)   # Green
    elif Y == 3:
        r, g, b = (0, 0, 255)   # Blue
    elif Y == 4:
        r, g, b = (0, 255, 255) # Aqua

    if offset_x == 0:
        text = time.strftime("%a, %d-%m-%Y %H:%M:%S")
        text_width, text_height = font.getsize(text)
        image = Image.new('P', (text_width + display_width + display_width, display_height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((display_width, -1), text, font=font, fill=255)
    else:

        for y in range(display_height):
            for x in range(display_width):
                if image.getpixel((x + offset_x, y)) == 255:
                    unicornhatmini.set_pixel(x, y, r, g, b)
                else:
                    unicornhatmini.set_pixel(x, y, 0, 0, 0)

    offset_x += 1
    if offset_x + display_width > image.size[0]:
        offset_x = 0

    if X == 1:
        unicornhatmini.set_all(0, 0, 0)
        unicornhatmini.show()
        os.system("sudo shutdown now -P")
        time.sleep(30)

    unicornhatmini.show()
    time.sleep(0.05)

# Last edited on June 13th 2020
# added color chnage function to Y button
# run sudo crontab -e
# add
# @reboot python3 /home/pi/scroll_clock.py &
# "%a, %d-%m-%Y %H:%M:%S"
