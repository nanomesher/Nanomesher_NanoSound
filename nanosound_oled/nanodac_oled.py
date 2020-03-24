#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from luma.core import cmdline, error
from subprocess import *
from PIL import Image

import socket

import time
import datetime
import os
import RPi.GPIO as GPIO
import json
import urllib2
# import nanosoundcd_status

from PIL import ImageFont
from subprocess import check_output


class Screen:
    icons = {
        'spotify': "\uf1bc",
        'webradio': "\uf1be",
        'musicfile': "\uf1c7",
        'headphone': "\uf001",
        'repeat': "\uf021",
        'repeatSingle': "\uf01e",
        'random': "\uf074",
        'volumeup': "\uf028",
        'volumedown': "\uf027",
        'volumeoff': "\uf026",
        'updatedb': "\uf013",
        'play': "\uf04b",
        'pause': "\uf04c",
        'stop': "\uf04d",
    }

    artistScroll = None
    titleScroll = None
    enabled = True
    isColour = False
    isScroll = False
    enableClock = False

    albumartwidth = 50
    albumartheight = 50
    albumartcache = {}

    class Scroll:
        text = ''
        font = None
        border = 3
        space = 30
        width = 0
        height = 0
        x = 0
        y = 0
        color = 'white'

        def __init__(self, width, height, text, font, y, color, speed=3):
            self.width = width
            self.height = height
            self.text = text
            self.font = font
            self.x = self.border
            self.y = y
            self.speed = speed
            self.color = color

        def draw(self, draw):
            (w, h) = draw.textsize(self.text, self.font)
            if w < self.width - 6:
                draw.text((self.border, self.y), self.text, font=self.font, fill=self.color)
                return

            draw.text((self.x, self.y), self.text, font=self.font, fill=self.color)
            if (self.x + w) < (self.width - self.space):
                draw.text((self.x + w + self.space, self.y), self.text, font=self.font, fill=self.color)
            draw.rectangle((0, self.y, 3, self.y + h), outline='black', fill='black')
            draw.rectangle((self.width - 3, self.y, self.width - 1, self.y + h), outline='black', fill='black')

            self.x -= self.speed
            if self.x + w + self.space <= self.border:
                self.x = self.border

    def __init__(self, dev, isColour, isScroll):
        self.device = dev
        self.isColour = isColour
        self.isScroll = isScroll

        self.fonts = {
            'awesmall': self.make_font('fontawesome-webfont.ttf', 8),
            'awesome': self.make_font('fontawesome-webfont.ttf', 10),
            'tiny': self.make_font('DejaVuSansMono.ttf', 4),
            'small': self.make_font('DejaVuSansMono.ttf', 8),
            'medium': self.make_font('DejaVuSansMono.ttf', 10),
            'big': self.make_font('DejaVuSansMono.ttf', 16),
            'medium_u': self.make_font('simhei.ttf', 10),
            'big_u': self.make_font('simhei.ttf', 14)
        }

    def make_font(self, name, size):
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', name))
        return ImageFont.truetype(font_path, size)

    def enable(self):
        self.enabled = True

    def enableClock(self):
        self.enableClock = True

    def disable(self):
        with canvas(device) as draw:
            draw.rectangle((0, 0, self.device.width - 1, self.device.height - 1), outline='black', fill='black')
        self.enabled = False

    def logo(self, lanip="", wlanip=""):

        if (self.isColour):
            albumartimage = Image.open("logo/splash.png") \
                .transform(device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
                .convert(device.mode)

            bgd = Image.new("RGBA", device.size, "black")
            bgd.paste(albumartimage, (5, 1))
            mydither = True

            with canvas(device, background=bgd, dither=mydither) as draw:

                if lanip != '':
                    ip = lanip
                elif wlanip != '':
                    ip = wlanip
                else:
                    ip = "volumio.local"

                draw.text((3, 65), 'NanoSound v1.8.5', font=self.fonts['small'], fill='white')
                draw.text((3, 80), ip, font=self.fonts['small'], fill='white')
                draw.text((3, 95), "http://nanomesher.com/", font=self.fonts['small'], fill='white')

        else:

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
                # draw.rectangle((0, 0, self.device.width - 1, self.device.height - 1), outline='black', fill='black')

                for i, line in enumerate(text):
                    draw.text((8, 5 + i * 4), line, font=self.fonts['tiny'], fill='white')

                if lanip != '':
                    ip = lanip
                elif wlanip != '':
                    ip = wlanip
                else:
                    ip = "volumio"

                draw.text((3, 40), 'NanoSound v1.8.5', font=self.fonts['small'], fill='white')
                draw.text((3, 50), ip, font=self.fonts['small'], fill='white')

    def getTitleColour(self):
        if (self.isColour == False):
            return "white"
        else:
            return "gold"

    def getArtistColour(self):
        if (self.isColour == False):
            return "white"
        else:
            return "white"

    def getProgressBarColour(self):
        if (self.isColour == False):
            return "white"
        else:
            return "gold"

    def getPlayPauseIconColour(self):
        if (self.isColour == False):
            return "white"
        else:
            return "GreenYellow"

    def drawalert(self, line1, line2):

        # print(line1)
        with canvas(device) as draw:
            draw.text((13, 10), line1, font=self.fonts['medium_u'], fill='white')

            if (len(line2) <= 20):
                draw.text((2, 30), line2, font=self.fonts['medium_u'], fill='white')
            else:
                draw.text((2, 30), line2[:20], font=self.fonts['medium_u'], fill='white')
                draw.text((2, 50), line2[20:], font=self.fonts['medium_u'], fill='white')

    def draw(self, data):
        global ampon
        if not self.enabled:
            return

        mydither = False
        bgd = None

        if (self.isColour):
            if ('albumart' in data):
                if data['albumart'].find("http") == -1:
                    albumarturl = 'http://127.0.0.1:3000' + data['albumart']
                else:
                    albumarturl = data['albumart']

                albumarturl = albumarturl.replace(" ", "%20")

                if albumarturl in self.albumartcache.keys():
                    albumartimage = self.albumartcache[albumarturl]
                else:
                    albumartimage = Image.open(urllib2.urlopen(albumarturl)).resize((60, 60), Image.ANTIALIAS) \
                        .transform(device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
                        .convert(device.mode)

                self.albumartcache[albumarturl] = albumartimage

                bgd = Image.new("RGBA", device.size, "black")
                bgd.paste(albumartimage, (device.width / 2 - 30, 63))
                mydither = True

        with canvas(device, background=bgd, dither=mydither) as draw:
            # draw.rectangle((0, 0, self.device.width - 1, self.device.height - 1), outline='black', fill='black')

            # Status bar
            if data['status'] == 'play':
                txt = self.icons['play']
            elif data['status'] == 'pause':
                txt = self.icons['pause']
            else:
                txt = self.icons['stop']
            draw.text((3, 1), txt, font=self.fonts['awesome'], fill=self.getPlayPauseIconColour())

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
                draw.text((self.device.width - w - 24, 2), self.icons['headphone'],
                          font=self.fonts['awesome'], fill='white')
            draw.text((self.device.width - w - 13, 2), txt, font=self.fonts['awesome'], fill='white')

            txt = "%02d" % data['volume']
            (w, h) = draw.textsize(txt, font=self.fonts['medium'])
            draw.text((self.device.width - w - 3, 1), txt, font=self.fonts['medium'], fill='white')

            # Artist & Track
            txt = data['artist']
            if 'album' in data and data['album'] != None:
                txt += " - " + data['album']

            if self.artistScroll == None or txt != self.artistScroll.text:
                if (screen.isScroll):
                    self.artistScroll = self.Scroll(self.device.width, self.device.height, txt, self.fonts['medium_u'],
                                                    11, self.getArtistColour(), 4)
                else:
                    draw.text((1, 11), txt, font=self.fonts['medium_u'], fill='white')

            if self.titleScroll == None or data['title'] != self.titleScroll.text:
                if (screen.isScroll):
                    self.titleScroll = self.Scroll(self.device.width, self.device.height, data['title'],
                                                   self.fonts['big_u'], 20, self.getTitleColour(), 4)
                else:
                    (w, h) = draw.textsize(data['title'], font=self.fonts['big_u'])
                    if (w <= self.device.width):
                        if (self.isColour):
                            draw.text((1, 20), data['title'], font=self.fonts['big_u'], fill=self.getArtistColour())
                        else:
                            draw.text((1, 20), data['title'], font=self.fonts['big_u'], fill='white')
                    else:
                        if (self.isColour):
                            draw.text((1, 20), data['title'], font=self.fonts['medium_u'], fill=self.getTitleColour())
                        else:
                            draw.text((1, 20), data['title'], font=self.fonts['medium_u'], fill='white')

            if (screen.isScroll):
                self.artistScroll.draw(draw)
                self.titleScroll.draw(draw)

            # Track data
            if data['trackType'] != 'webradio' and data['trackType'] != 'spotify':
                txt = data['trackType'] + ' '
            else:
                txt = ''

            if 'samplerate' in data and 'bitdepth' in data:
                if str(data['samplerate']) == 'Volspotconnect2':
                    txt += str(data['bitdepth'])
                elif data['bitdepth']:
                    txt += data['bitdepth'].replace(" bit", '').replace("bit", '') + '/' \
                           + data['samplerate'].replace(" KHz", '').replace("kHz", '').replace("44.1->", '')

            (w, h) = draw.textsize(txt, font=self.fonts['small'])
            if data['trackType'] == 'webradio':
                draw.text(((self.device.width - w) / 2 - 6, 40), self.icons['webradio'], font=self.fonts['awesmall'],
                          fill='white')
                draw.text(((self.device.width - w) / 2 + 6, 38), txt, font=self.fonts['small'], fill='white')
            elif data['trackType'] == 'spotify':
                draw.text(((self.device.width - w) / 2 - 6, 40), self.icons['spotify'], font=self.fonts['awesmall'],
                          fill='white')
                draw.text(((self.device.width - w) / 2 + 6, 38), txt, font=self.fonts['small'], fill='white')
            else:
                draw.text(((self.device.width - w) / 2, 38), txt, font=self.fonts['small'], fill='white')

            if (not screen.isScroll):
                lanip = GetLANIP()
                wanip = GetWLANIP()
                if (lanip == "" and wanip != ""):
                    ip = wanip
                elif (lanip != ""):
                    ip = lanip
                else:
                    ip = "no ip"

                (w, h) = draw.textsize(ip, font=self.fonts['medium'])
                draw.text(((self.device.width - w) / 2 + 6, 54), ip, font=self.fonts['small'], fill='white')

            # Elapsed / Duration
            if data['trackType'] == 'webradio' or data['trackType'] == 'spotify':
                return

            if ('seek' in data) and (screen.isScroll):
                elapsed = str(datetime.timedelta(seconds=round(float(data['seek']) / 1000)))
                draw.text((3, 46), elapsed, font=self.fonts['medium'], fill='white')
                if 'duration' in data and data['duration'] > 0:
                    el_pct = data['seek'] / data['duration'] / 10
                    duration = str(datetime.timedelta(seconds=data['duration']))
                    (w, h) = draw.textsize(duration, font=self.fonts['medium'])
                    draw.text(((self.device.width - w - 3), 46), duration, font=self.fonts['medium'], fill='white')

                    draw.rectangle((3, 58, 122 * el_pct / 100, 60), outline='white', fill=self.getProgressBarColour())
                    draw.rectangle((122 * el_pct / 100, 59, 125, 59), outline='white', fill='black')


def GetCompareString(data, isScroll):
    if (isScroll):
        return str(data['volume']) + str(data['status']) + data['title'] + data['artist'] + str(data['seek']) + str(
            ampon)
    else:
        return str(data['volume']) + str(data['status']) + data['title'] + data['artist'] + str(ampon)


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
    if GPIO.input(GPIOButtonNo) == 1:
        startt = time.time()
    if GPIO.input(GPIOButtonNo) == 0:
        idle = 0
        if (hasOLED and not screen.enabled):
            screen.enable()
        endt = time.time()
        elapsed = endt - startt
        if elapsed < 2:
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


def refreshData():
    global showip

    try:
        data = json.load(urllib2.urlopen('http://127.0.0.1:3000/api/v1/getstate'))
        data = merge_dicts(data_stub, data)
    except:
        data = data_stub

    if showip:
        data['artist'] = GetLANIP()
        data['title'] = GetWLANIP()

    return data


with open('/boot/config.txt') as myfile:
    if 'i2c_baudrate' not in myfile.read():
        cmd = "sudo sed -i 's/dtparam=i2c_arm=on.*/dtparam=i2c_arm=on,i2c_baudrate=400000/' /boot/config.txt"
        p = Popen(cmd, shell=True, stdout=PIPE)

time.sleep(1)

hasOLED = False
isColour = False
isScroll = True
showip = False
ampon = False
model = 'DAC'
display = '1'

try:
    with open('/sys/firmware/devicetree/base/model') as f:
        if 'Raspberry Pi 4' in f.read():
            isScroll = False
        else:
            isScroll = True
except:
    isScroll = True

try:
    with open('/data/configuration/miscellanea/nanosound/config.json') as f:
        data = json.load(f)
        display = data['oledDisplay']['value']
        model = data['model']['value']
except:
    display = '1'
    model = 'DAC'

try:
    if display == '2':
        device = ssd1306(port=1, address=0x3C)
        isScroll = False
        isColour = False
    elif display == '3':
        actual_args = ['-f', '/home/volumio/nanosound_oled/ssd1351.conf']
        parser = cmdline.create_parser(description='luma.examples arguments')
        args = parser.parse_args(actual_args)
        config = cmdline.load_config(args.config)
        args = parser.parse_args(config + actual_args)
        device = cmdline.create_device(args)
        isColour = True
    elif display == 'N':
        isColour = False
        hasOLED = False
    else:
        device = sh1106(port=1, address=0x3C)
        isScroll = False
        isColour = False

    hasOLED = True
except:
    hasOLED = False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)

GPIOButtonNo = 16
GPIOSWMenuButtonNo = 0

if (model == "DAC2"):
    GPIOButtonNo = 6
    GPIO.setup(GPIOSWMenuButtonNo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(GPIOSWMenuButtonNo, GPIO.BOTH, callback=optionButPress, bouncetime=30)

GPIO.setup(GPIOButtonNo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(GPIOButtonNo, GPIO.BOTH, callback=optionButPress, bouncetime=30)

if (hasOLED):
    screen = Screen(device, isColour, isScroll)
    data_stub = {"status": "stop", "title": "(No data)", "artist": "", "samplerate": "", "bitdepth": "",
                 "random": False,
                 "repeat": False, "repeatSingle": False, "volume": 0}
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
idle = 0
volume = 0

# has_nanosoundcd = nanosoundcd_status.is_nanosoundcd_installed()

while hasOLED:
    if counter == 0:
        try:
            get_pid('spotify-connect-web')
            spotifyProcess = True
        except:
            spotifyProcess = False

    if counter % 4 == 0:
        data = refreshData()

        if (data['volume'] != volume) and (screen.isColour):
            volume = data['volume']
            if not screen.enabled:
                screen.enable()
                idle = 0

        if spotifyProcess:
            try:
                spotify = json.load(urllib2.urlopen('http://127.0.0.1:4000/api/info/status'))
                spotify = merge_dicts(spotify_stub, spotify)
            except:
                spotifyProcess = False
                spotify = spotify_stub

            if (data['status'] == 'pause' or data['status'] == 'stop') and spotify['logged_in']:
                data['title'] = 'Spotify Connect Ready'
                data['artist'] = socket.gethostname()
                data['bitdepth'] = ''

            if spotify['logged_in'] and spotify['playing'] and spotify['active']:
                try:
                    spotdata = json.load(urllib2.urlopen('http://127.0.0.1:4000/api/info/metadata'))
                    data['title'] = spotdata['track_name']
                    data['artist'] = spotdata['artist_name']
                except:
                    pass

        if showip:
            data['artist'] = GetLANIP()
            data['title'] = GetWLANIP()

    else:
        if data['status'] == 'play' and (data['trackType'] != 'webradio' or data['trackType'] != 'spotify'):
            data['seek'] += 250

    counter += 1
    if counter == 121:
        counter = 0

        try:

            screen.draw(data)

            beforecompst = GetCompareString(data, screen.isScroll)
            aftercompst = GetCompareString(data, screen.isScroll)

            while (beforecompst == aftercompst):

                # Check if play status is checked
                data = refreshData()
                aftercompst = GetCompareString(data, screen.isScroll)

                # Check if anything to be reported from NanoSound CD
                # if (has_nanosoundcd):
                #     cd_to_display = nanosoundcd_status.to_display()
                #     if (cd_to_display is not None):
                #
                #         if(isinstance(cd_to_display,list)):
                #             aftercompst = ""
                #             if(cd_to_display[0]):
                #                 screen.drawalert("Extracting...", cd_to_display[1])
                #             else:
                #                 screen.drawalert("Extraction stopped", cd_to_display[1])
                #             time.sleep(5)

                if data['status'] == 'play' and not screen.enabled:
                    screen.enable()
                    idle = 0

                if data['status'] != 'play' and screen.enabled:
                    idle += 1

                if screen.enabled and idle > 300:
                    screen.disable()

                time.sleep(0.2)

            time.sleep(0.25)
        except:
            time.sleep(0.25)
