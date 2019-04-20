#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from oled.render import canvas
from oled.device import ssd1306, sh1106
from subprocess import *

import socket
import time
import datetime
import os
import RPi.GPIO as GPIO
import json
import urllib2
from PIL import ImageFont
from subprocess import check_output


class Screen:
    icons = {
      'spotify':   "\uf1bc",
      'webradio':  "\uf1be",
      'musicfile': "\uf1c7",
      'headphone': "\uf001",
      'repeat':    "\uf021",
      'repeatSingle': "\uf01e",
      'random':    "\uf074",
      'volumeup':  "\uf028",
      'volumedown':"\uf027",
      'volumeoff': "\uf026",
      'updatedb':  "\uf013",
      'play':      "\uf04b",
      'pause':     "\uf04c",
      'stop':      "\uf04d",
    }

    artistScroll = None
    titleScroll  = None
    enabled = True

    class Scroll:
        text = ''
        font = None
        border = 3
        space  = 30
        width = 0
        height= 0
        x = 0
        y = 0

        def __init__(self, width, height, text, font, y, speed=3):
            self.width = width
            self.height = height
            self.text = text
            self.font = font
            self.x = self.border
            self.y = y
            self.speed = speed

        def draw(self, draw):
            (w, h) = draw.textsize(self.text, self.font)
            if w < self.width-6:
                draw.text((self.border, self.y), self.text, font=self.font, fill='white')
                return

            draw.text((self.x, self.y), self.text, font=self.font, fill='white')
            if (self.x + w) < (self.width - self.space):
                draw.text((self.x + w + self.space, self.y), self.text, font=self.font, fill='white')
            draw.rectangle((0, self.y, 3, self.y+h), outline='black', fill='black')
            draw.rectangle((self.width-3, self.y, self.width-1, self.y+h), outline='black', fill='black')

            self.x -= self.speed
            if self.x + w + self.space <= self.border:
                self.x = self.border

    def __init__(self, dev):
        self.device = dev
        self.fonts  = {
          'awesmall':self.make_font('fontawesome-webfont.ttf', 8),
          'awesome': self.make_font('fontawesome-webfont.ttf', 10),
          'tiny':    self.make_font('DejaVuSansMono.ttf', 4),
          'small':   self.make_font('DejaVuSansMono.ttf', 8),
          'medium':  self.make_font('DejaVuSansMono.ttf', 10),
          'big':     self.make_font('DejaVuSansMono.ttf', 16),
          'medium_u':  self.make_font('simhei.ttf', 10),
          'big_u':     self.make_font('simhei.ttf', 15)
        }


    def make_font(self, name, size):
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', name))
        return ImageFont.truetype(font_path, size)

    def enable(self):
        self.enabled = True

    def disable(self):
        with canvas(device) as draw:
            draw.rectangle((0, 0, self.device.width - 1, self.device.height - 1), outline='black', fill='black')
        self.enabled = False

    def logo(self, lanip="", wlanip=""):
        text = [
            '               ___',
            '              /\\_ \\                        __',
            ' __  __    ___\\//\\ \\    __  __    ___ ___ /\\_\\    ___',
            '/\\ \\/\\ \\  / __`\\\\ \\ \\  /\\ \\/\\ \\ /\' __` __`\\/\\ \\  / __`\\',
            '\\ \\ \\_/ |/\\ \\L\\ \\\\_\\ \\_\\ \\ \\_\\ \\/\\ \\/\\ \\/\\ \\ \\ \\/\\ \\L\\ \\',
            ' \\ \\___/ \\ \\____//\\____\\\\ \\____/\\ \\_\\ \\_\\ \\_\\ \\_\\ \\____/',
            '  \\/__/   \\/___/ \\/____/ \\/___/  \\/_/\\/_/\\/_/\\/_/\\/___/',
        ]
        with canvas(device) as draw:
            draw.rectangle((0, 0, self.device.width - 1, self.device.height - 1), outline='black', fill='black')

            for i, line in enumerate(text):
                draw.text((8, 5+i*4), line, font=self.fonts['tiny'], fill='white')

            if lanip != '':
                ip = lanip
            elif wlanip != '':
                ip = wlanip
            else:
                ip = "volumio"

            draw.text((3, 40), 'NanoSound v1.6.3', font=self.fonts['small'], fill='white')
            draw.text((3, 50), ip, font=self.fonts['small'], fill='white')

    def draw(self, data):
        global ampon
        if not self.enabled:
            return

        with canvas(device) as draw:
            draw.rectangle((0, 0, self.device.width - 1, self.device.height - 1), outline='black', fill='black')

            # Status bar
            if data['status'] == 'play':
                txt = self.icons['play']
            elif data['status'] == 'pause':
                txt = self.icons['pause']
            else:
                txt = self.icons['stop']
            draw.text((3, 1), txt, font=self.fonts['awesome'], fill='white')

            if data['repeat']:
                txt = self.icons['repeat']
            elif data['repeatSingle']:
                txt = self.icons['repeatSingle']
            else:
                txt = ' '
            draw.text((13, 1), txt, font=self.fonts['awesome'], fill='white')

            if data['random']:
                txt = self.icons['random']
            else:
                txt = ' '
            draw.text((23, 2), txt, font=self.fonts['awesome'], fill='white')

            if 'updatedb' in data and data['updatedb']:
                txt = self.icons['updatedb']
            else:
                txt = ' '
            draw.text((33, 1), txt, font=self.fonts['awesome'], fill='white')

            if data['volume'] > 50:
                txt = self.icons['volumeup']
            elif data['volume'] > 0:
                txt = self.icons['volumedown']
            else:
                txt = self.icons['volumeoff']

            (w, h) = draw.textsize('000', font=self.fonts['medium'])
            if ampon:
                draw.text((self.device.width-w-24, 2), self.icons['headphone'],
                          font=self.fonts['awesome'], fill='white')
            draw.text((self.device.width-w-13, 2), txt, font=self.fonts['awesome'], fill='white')

            txt = "%02d" % data['volume']
            (w, h) = draw.textsize(txt, font=self.fonts['medium'])
            draw.text((self.device.width-w-3, 1), txt, font=self.fonts['medium'], fill='white')

            # Artist & Track
            txt = data['artist']
            if 'album' in data and data['album'] != None:
                txt += " - " + data['album']

            if self.artistScroll == None or txt != self.artistScroll.text:
                self.artistScroll = self.Scroll(self.device.width, self.device.height, txt, self.fonts['medium_u'], 11, 5)
            if self.titleScroll == None or data['title'] != self.titleScroll.text:
                self.titleScroll  = self.Scroll(self.device.width, self.device.height, data['title'], self.fonts['big_u'], 20, 5)
            self.artistScroll.draw(draw)
            self.titleScroll.draw(draw)

            if('trackType' in data):
                trackType = data['trackType']
            else:
                trackType = '-'

            # Track data
            if trackType != 'webradio' and trackType != 'spotify':
                txt = trackType + ' '
            else:
                txt = ''

            if 'samplerate' in data and 'bitdepth' in data:
                if str(data['samplerate']) == 'Volspotconnect2':
                    txt += str(data['bitdepth'])
                elif data['bitdepth']:
                    txt += data['bitdepth'].replace(" bit", '').replace("bit", '') + '/' \
                         + data['samplerate'].replace(" KHz", '').replace("kHz", '').replace("44.1->", '')

            (w, h) = draw.textsize(txt, font=self.fonts['small'])
            if trackType == 'webradio':
                draw.text(((self.device.width-w)/2-6, 40), self.icons['webradio'], font=self.fonts['awesmall'], fill='white')
                draw.text(((self.device.width-w)/2+6, 38), txt, font=self.fonts['small'], fill='white')
            elif trackType == 'spotify':
                draw.text(((self.device.width-w)/2-6, 40), self.icons['spotify'], font=self.fonts['awesmall'], fill='white')
                draw.text(((self.device.width-w)/2+6, 38), txt, font=self.fonts['small'], fill='white')
            else:
                draw.text(((self.device.width-w)/2, 38), txt, font=self.fonts['small'], fill='white')

            # Elapsed / Duration
            if trackType == 'webradio' or trackType == 'spotify':
                return

            if 'seek' in data:
                elapsed  = str(datetime.timedelta(seconds=round(float(data['seek'])/1000)))
                draw.text((3, 46), elapsed, font=self.fonts['medium'], fill='white')
                if 'duration' in data and data['duration'] > 0:
                    el_pct   = data['seek'] / data['duration'] / 10
                    duration = str(datetime.timedelta(seconds=data['duration']))
                    (w, h) = draw.textsize(duration, font=self.fonts['medium'])
                    draw.text(((self.device.width - w - 3), 46), duration, font=self.fonts['medium'], fill='white')
                    draw.rectangle((3, 58, 122*el_pct/100, 60), outline='white', fill='white')
                    draw.rectangle((122*el_pct/100, 59, 125, 59), outline='white', fill='black')

def GetLANIP():
    cmd = \
        "ip addr show eth0 | grep inet  | grep -v inet6 | awk '{print $2}' | cut -d '/' -f 1"
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output[:-1]


def GetWLANIP():
    cmd = \
        "ip addr show wlan0 | grep inet  | grep -v inet6 | awk '{print $2}' | cut -d '/' -f 1"
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output[:-1]

def toggleAmp(value):
    global ampon
    if ampon == True:
        GPIO.output(27, GPIO.LOW)
        ampon = False
    elif ampon == False:
        GPIO.output(27, GPIO.HIGH)
        ampon = True


def toggleShowIP():
    global showip
    if showip == False:
        showip = True
    elif showip == True:
        showip = False


def optionButPress(value):
    global startt, endt, idle, screen
    if GPIO.input(16) == 1:
        startt = time.time()
    if GPIO.input(16) == 0:
        idle = 0
        if not screen.enabled:
            screen.enable()
        endt = time.time()
        elapsed = endt - startt
        if elapsed < 1:
            toggleAmp(1)
        else:
            toggleShowIP()

def get_pid(name):
    return check_output(['pidof', name])

def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

time.sleep(1)

hasOLED = False
showip  = False
ampon   = False
try:
    display = '1'
    with open('/data/configuration/miscellanea/nanosound/config.json') as f:
        data = json.load(f)
        display = data['oledDisplay']['value']
except:
    display = '1'

try:
    if display == '2':
        device = ssd1306(port=1, address=0x3C)
    else:
        device = sh1106(port=1, address=0x3C)

    hasOLED = True
except:
    hasOLED = False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(16, GPIO.BOTH, callback=optionButPress,
                      bouncetime=200)

if(hasOLED):
    screen = Screen(device)
    data_stub = {"status":"stop","title":"(No data)","artist":"","samplerate":"","bitdepth":"","random":False,"repeat":False,"repeatSingle":False,"volume":0}
    spotify_stub = {'logged_in': False, 'playing': False, 'active': False}
    spotifyProcess = False
# Switch ampon

toggleAmp(1)

while not hasOLED:
    time.sleep(0.1)

try:
    if hasOLED:
        screen.logo(GetLANIP(), GetWLANIP())

    time.sleep(3)
except:
    pass

counter = 0
idle    = 0
volume  = 0

while hasOLED:
    if counter == 0:
        try:
            get_pid('spotify-connect-web')
            spotifyProcess = True
        except:
            spotifyProcess = False

    if counter % 4 == 0:
        try:
            data = json.load(urllib2.urlopen('http://127.0.0.1:3000/api/v1/getstate'))
            data = merge_dicts(data_stub, data)
        except:
            data = data_stub

        if data['volume'] != volume:
            volume = data['volume']
            if not screen.enabled:
                screen.enable()
                idle  = 0

        if data['status'] == 'play' and not screen.enabled:
            screen.enable()
            idle  = 0

        if data['status'] != 'play' and screen.enabled:
            idle += 1

        if screen.enabled and idle > 300:
            screen.disable()

        if spotifyProcess:
            try:
                spotify = json.load(urllib2.urlopen('http://127.0.0.1:4000/api/info/status'))
                spotify = merge_dicts(spotify_stub, spotify)
            except:
                spotifyProcess = False
                spotify = spotify_stub

            if (data['status'] == 'pause' or data['status'] == 'stop') and spotify['logged_in']:
                data['title']  = 'Spotify Connect Ready'
                data['artist'] = socket.gethostname()
                data['bitdepth'] = ''

            if spotify['logged_in'] and spotify['playing'] and spotify['active']:
                try:
                    spotdata = json.load(urllib2.urlopen('http://127.0.0.1:4000/api/info/metadata'))
                    data['title']  = spotdata['track_name']
                    data['artist'] = spotdata['artist_name']
                except:
                    pass

        if showip:
            data['artist'] = GetLANIP()
            data['title']  = GetWLANIP()
    else:
        if('trackType' in data):
            trackType = data['trackType']
        else:
            trackType = '-'

        if data['status'] == 'play' and (trackType != 'webradio' or trackType != 'spotify'):
            data['seek'] += 250

    counter += 1
    if counter == 121:
        counter = 0

    try:
        screen.draw(data)
        time.sleep(0.25)
    except:
        time.sleep(0.25)
