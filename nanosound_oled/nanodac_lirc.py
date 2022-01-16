#!/usr/bin/env python3
from __future__ import unicode_literals

PYTHONIOENCODING = "UTF-8"
from socketIO_client import SocketIO, LoggingNamespace
from time import time
import RPi.GPIO as GPIO

import urllib.request
import json
import configparser
import os.path

playlist = []
playing_index = 0


def on_getState_response(*args):
    global playlist
    alist = args
    playlist = alist[0]


def playNextPlaylist():
    listPlayList()
    global playing_index
    playing_index = playing_index + 1
    if (playing_index >= len(playlist)):
        playing_index = 0
    playPlaylist(playing_index)


def playPrevPlaylist():
    listPlayList()
    global playing_index
    playing_index = playing_index - 1
    if (playing_index < 0):
        playing_index = (len(playlist) - 1)
    playPlaylist(playing_index)


def listPlayList():
    with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
        socketIO.on('pushListPlaylist', on_getState_response)
        socketIO.emit('listPlaylist', '')
        socketIO.wait(seconds=1)


def playPlaylist(playlist_index):
    if (len(playlist) > 1):
        playlistname = playlist[playlist_index]
        urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=playplaylist&name=' + playlistname)


def mute():
    # urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&value=mute')

    with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
        socketIO.emit('mute', '')


def unmute():
    # urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&value=unmute')
    with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
        socketIO.emit('unmute', '')


def unrandom():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=random&value=false')


def randomset():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=random&value=true')


def repeat():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=repeat&value=true')


def unrepeat():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=repeat&value=false')


def toggle():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=toggle')


def songprev():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=prev')


def songnext():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=next')


def volup():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&volume=plus')


def voldown():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&volume=minus')


def stop():
    urllib.request.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=stop')


# listPlayList()

def setup():
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def binary_aquire(pin, duration):
    # aquires data as quickly as possible
    t0 = time()
    results = []
    while (time() - t0) < duration:
        results.append(GPIO.input(pin))
    return results


def on_ir_receive(pinNo, bouncetime=150):
    # when edge detect is called (which requires less CPU than constant
    # data acquisition), we acquire data as quickly as possible
    data = binary_aquire(pinNo, bouncetime / 1000.0)
    if len(data) < bouncetime:
        return
    rate = len(data) / (bouncetime / 1000.0)
    pulses = []
    i_break = 0
    # detect run lengths using the acquisition rate to turn the times in to microseconds
    for i in range(1, len(data)):
        if (data[i] != data[i - 1]) or (i == len(data) - 1):
            pulses.append((data[i - 1], int((i - i_break) / rate * 1e6)))
            i_break = i
    # decode ( < 1 ms "1" pulse is a 1, > 1 ms "1" pulse is a 1, longer than 2 ms pulse is something else)
    # does not decode channel, which may be a piece of the information after the long 1 pulse in the middle
    outbin = ""
    for val, us in pulses:
        if val != 1:
            continue
        if outbin and us > 2000:
            break
        elif us < 1000:
            outbin += "0"
        elif 1000 < us < 2000:
            outbin += "1"
    try:
        return int(outbin, 2)
    except ValueError:
        # probably an empty code
        return None


def destroy():
    GPIO.cleanup()


muted = False
randomed = False
repeated = False  # 0-no repeat , 1-repeat one, 2-repeat


config = configparser.ConfigParser()

if(os.path.isfile('/home/volumio/nanosound_keys.ini')):
    config.read('/home/volumio/nanosound_keys.ini')
else:
    config.read('/home/volumio/nanosound_oled/conf/nanosound_keys.ini')
MUTE_BUTTON = config.get('Default','MUTE_BUTTON')
PREV_BUTTON = config.get('Default','PREV_BUTTON')
NEXT_BUTTON = config.get('Default','NEXT_BUTTON')
TOGGLE_BUTTON = config.get('Default','TOGGLE_BUTTON')
VOLUP_BUTTON = config.get('Default','VOLUP_BUTTON')
VOLDOWN_BUTTON = config.get('Default','VOLDOWN_BUTTON')
NEXTPLAYLIST_BUTTON = config.get('Default','NEXTPLAYLIST_BUTTON')
PREVPLAYLIST_BUTTON = config.get('Default','PREVPLAYLIST_BUTTON')
RANDOM_BUTTON = config.get('Default','RANDOM_BUTTON')
REPEAT_BUTTON = config.get('Default','REPEAT_BUTTON')
STOP_BUTTON = config.get('Default','STOP_BUTTON')

volstatus = json.load(urllib.request.urlopen('http://127.0.0.1:3000/api/v1/getstate'))

if ('repeat' in volstatus):
    if (volstatus['repeat']):
        repeated = True
    else:
        repeated = False
else:
    repeated = False

if ('random' in volstatus):
    if (volstatus['random']):
        randomed = True
    else:
        randomed = False
else:
    randomed = False

if ('mute' in volstatus):
    if (volstatus['mute']):
        muted = True
    else:
        muted = False
else:
    muted = False

if __name__ == "__main__":
    setup()

    print("Starting IR Listener")
    while True:

        print("Waiting for signal")
        GPIO.wait_for_edge(11, GPIO.FALLING)
        code = on_ir_receive(11)
        if code:
            hexcode = str(hex(code))
            if (hexcode == MUTE_BUTTON) and (not muted):
                muted = True
                mute()
            elif (hexcode == MUTE_BUTTON) and (muted):
                muted = False
                unmute()
            elif (hexcode == PREV_BUTTON):
                songprev()
            elif (hexcode == NEXT_BUTTON):
                songnext()
            elif (hexcode == TOGGLE_BUTTON):
                toggle()
            elif (hexcode == VOLUP_BUTTON):
                volup()
            elif (hexcode == VOLDOWN_BUTTON):
                voldown()
            elif (hexcode == NEXTPLAYLIST_BUTTON):
                playNextPlaylist()
            elif (hexcode == PREVPLAYLIST_BUTTON):
                playPrevPlaylist()
            elif (not randomed) and (hexcode == RANDOM_BUTTON):
                randomed = True
                randomset()
            elif (randomed) and (hexcode == RANDOM_BUTTON):
                randomed = False
                unrandom()
            elif (not repeated) and (hexcode == REPEAT_BUTTON):
                repeated = True
                repeat()
            elif (repeated) and (hexcode == REPEAT_BUTTON):
                repeated = False
                unrepeat()
            elif (hexcode == STOP_BUTTON):
                stop()

#    destroy()

# while(True):

#    button = lirc.nextcode()
#    if(len(button)>0):
#      command=button[0]

#      if(command=="listup"):
# 		playNextPlaylist()
#      elif(command=="listdown"):
# 		playPrevPlaylist()					
#      elif(not muted) and (command=="mute"):
#        muted=True
#        mute()
#      elif(muted) and (command=="mute"):
#        muted=False
#        unmute()
#      elif(not randomed) and (command=="random"):
#        randomed=True
#        randomset()
#      elif(randomed) and (command=="random"):
#        randomed=False
#        unrandom()
#      elif(not repeated) and (command=="repeat"):
#        repeated=True
#        repeat()
#      elif(repeated) and (command=="repeat"):
#        repeated=False
#        unrepeat()
