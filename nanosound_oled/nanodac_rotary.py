#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from socketIO_client import SocketIO, LoggingNamespace
from RPi import GPIO
from time import sleep


def volup():
    # urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&value=mute')
    with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
        socketIO.emit('volume', '+')


def voldown():
    # urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&value=unmute')
    with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
        socketIO.emit('volume', '-')


clk = 22
dt = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

clkLastState = GPIO.input(clk)

try:

        while True:
                clkState = GPIO.input(clk)
                dtState = GPIO.input(dt)
                if clkState != clkLastState:
                        if dtState != clkState:
				#print("+")
                                volup()
                        else:
				#print("-")
                                voldown()
                clkLastState = clkState
                sleep(0.01)
finally:
        GPIO.cleanup()

