#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Use misc draw commands to create a simple image.

Ported from:
https://github.com/adafruit/Adafruit_Python_SSD1306/blob/master/examples/shapes.py
"""

import os
import time
import threading
import schedule
from datetime import datetime
from datetime import date
from demo_opts import get_device
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from luma.core.render import canvas
from PIL import ImageFont
import socket
from subprocess import *
from PIL import Image

import datetime
import os
import RPi.GPIO as GPIO
import json
import urllib.request

def primitives(device, draw):
    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = 2
    shape_width = 20
    top = padding
    bottom = device.height - padding - 1
    # Move left to right keeping track of the current x position for drawing shapes.
    x = padding
    # Draw an ellipse.
    draw.ellipse((x, top, x + shape_width, bottom), outline="red", fill="black")
    x += shape_width + padding
    # Draw a rectangle.
    draw.rectangle((x, top, x + shape_width, bottom), outline="blue", fill="black")
    x += shape_width + padding
    # Draw a triangle.
    draw.polygon([(x, bottom), (x + shape_width / 2, top), (x + shape_width, bottom)], outline="green", fill="black")
    x += shape_width + padding
    # Draw an X.
    draw.line((x, bottom, x + shape_width, top), fill="yellow")
    draw.line((x, top, x + shape_width, bottom), fill="yellow")
    x += shape_width + padding
    # Write two lines of text.
    size = draw.textsize('World!')
    x = device.width - padding - size[0]
    draw.rectangle((x, top + 4, x + size[0], top + size[1]), fill="black")
    draw.rectangle((x, top + 16, x + size[0], top + 16 + size[1]), fill="black")
    draw.text((device.width - padding - size[0], top + 4), 'Hello', fill="cyan")
    draw.text((device.width - padding - size[0], top + 16), 'World!', fill="purple")
    # Draw a rectangle of the same size of screen
    draw.rectangle(device.bounding_box, outline="white")

data_stub = {"status": "stop", "title": "(No data)", "artist": "", "samplerate": "", "bitdepth": "",
                 "random": False,
                 "repeat": False, "repeatSingle": False, "volume": 0}

def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def refreshData():
    global showip,data

    try:
        data = json.load(urllib.request.urlopen('http://127.0.0.1:3000/api/v1/getstate'))
        data = merge_dicts(data_stub, data)        
    except:        
        data = data_stub

    return data

def refreshScreen(screen):
    
    mydither = False
    bgd = None
    
    if (screen.isColour):
        if ('albumart' in data):
            if data['albumart'].find("http") == -1:
                albumarturl = 'http://127.0.0.1:3000' + data['albumart']
            else:
                albumarturl = data['albumart']

            albumarturl = albumarturl.replace(" ", "%20")
            if albumarturl in screen.albumartcache.keys():
                albumartimage = screen.albumartcache[albumarturl]
            else:
                albumartimage = Image.open(urllib.request.urlopen(albumarturl)).resize((60, 60), Image.ANTIALIAS).transform(screen.device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR).convert(screen.device.mode)

            screen.albumartcache[albumarturl] = albumartimage
            bgd = Image.new("RGBA", screen.device.size, "black")
            
            
            #bgd.paste(albumartimage,  round(screen.device.width / 2 - 30), 63)
            bgd.paste(albumartimage,(30,63))
            mydither = True
    
    with canvas(screen.device, background=bgd, dither=mydither) as draw:
        now = datetime.datetime.now()
        
        #play/pause
        if data['status'] == 'play':
            txt = screen.icons['play']
        elif data['status'] == 'pause':
            txt = screen.icons['pause']
        else:
            txt = screen.icons['stop']
        draw.text((3, 1), txt, font=screen.fonts['awesome'], fill=screen.getPlayPauseIconColour())

        #repeat
        if data['repeat']:
            txt = self.icons['repeat']
        elif data['repeatSingle']:
            txt = self.icons['repeatSingle']
        else:
            txt = ' '
        draw.text((13, 1), txt, font=screen.fonts['awesome'], fill='white')

        #random
        if data['random']:
            txt = screen.icons['random']
        else:
            txt = ' '
        draw.text((23, 2), txt, font=screen.fonts['awesome'], fill='white')

        if 'updatedb' in data and data['updatedb']:
            txt = screen.icons['updatedb']
        else:
            txt = ' '
            
            
        draw.text((33, 1), txt, font=screen.fonts['awesome'], fill='white')
        if data['volume'] > 50:
            txt = screen.icons['volumeup']
        elif data['volume'] > 0:
            txt = screen.icons['volumedown']
        else:
            txt = screen.icons['volumeoff']

        (w, h) = draw.textsize('000', font=screen.fonts['medium'])
        if ampon:
            draw.text((screen.device.width - w - 24, 2), screen.icons['headphone'],
                         font=screen.fonts['awesome'], fill='white')
        draw.text((screen.device.width - w - 13, 2), txt, font=screen.fonts['awesome'], fill='white')

        txt = "%02d" % data['volume']
        (w, h) = draw.textsize(txt, font=screen.fonts['medium'])
        draw.text((screen.device.width - w - 3, 1), txt, font=screen.fonts['medium'], fill='white')

        # Artist & Track
        txt = data['artist']
        if 'album' in data and data['album'] != None:
            txt += " - " + data['album']

        if screen.artistScroll == None or txt != screen.artistScroll.text:
            if (screen.isScroll):
                screen.artistScroll = screen.Scroll(screen.device.width, screen.device.height, txt, screen.fonts['medium_u'],
                                                    11, screen.getArtistColour(), 4)
            else:
                draw.text((1, 11), txt, font=screen.fonts['medium_u'], fill='white')

        if screen.titleScroll == None or data['title'] != screen.titleScroll.text:
                if (screen.isScroll):
                    screen.titleScroll = screen.Scroll(screen.device.width, screen.device.height, data['title'],
                                                   screen.fonts['big_u'], 20, screen.getTitleColour(), 4)
                else:         
                    (w, h) = draw.textsize(data['title'], font=screen.fonts['big_u'])
                    if (w <= screen.device.width):
                        if (screen.isColour):
                            draw.text((1, 20), data['title'], font=screen.fonts['big_u'], fill=screen.getArtistColour())
                        else:
                            draw.text((1, 20), data['title'], font=screen.fonts['big_u'], fill='white')
                    else:
                        if (screen.isColour):
                            draw.text((1, 20), data['title'], font=screen.fonts['medium_u'], fill=screen.getTitleColour())
                        else:
                            draw.text((1, 20), data['title'], font=screen.fonts['medium_u'], fill='white')

        if (screen.isScroll):
            screen.artistScroll.draw(draw)
            screen.titleScroll.draw(draw)        

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

        (w, h) = draw.textsize(txt, font=screen.fonts['small'])
        if data['trackType'] == 'webradio':
            draw.text(((screen.device.width - w) / 2 - 6, 40), screen.icons['webradio'], font=screen.fonts['awesmall'],
                        fill='white')
            draw.text(((screen.device.width - w) / 2 + 6, 38), txt, font=screen.fonts['small'], fill='white')
        elif data['trackType'] == 'spotify':
            draw.text(((screen.device.width - w) / 2 - 6, 40), screen.icons['spotify'], font=screen.fonts['awesmall'],
                        fill='white')
            draw.text(((screen.device.width - w) / 2 + 6, 38), txt, font=screen.fonts['small'], fill='white')
        else:
            draw.text(((screen.device.width - w) / 2, 38), txt, font=screen.fonts['small'], fill='white')

        if data['trackType'] == 'webradio' or data['trackType'] == 'spotify':
            return

        if ('seek' in data) and (screen.isScroll):
            elapsed = str(datetime.timedelta(seconds=round(float(data['seek']) / 1000)))
            draw.text((3, 46), elapsed, font=screen.fonts['medium'], fill='white')
            if 'duration' in data and data['duration'] > 0:
                el_pct = data['seek'] / data['duration'] / 10
                duration = str(datetime.timedelta(seconds=data['duration']))
                (w, h) = draw.textsize(duration, font=screen.fonts['medium'])
                draw.text(((screen.device.width - w - 3), 46), duration, font=screen.fonts['medium'], fill='white')

                draw.rectangle((3, 58, 122 * el_pct / 100, 60), outline='white', fill=screen.getProgressBarColour())
                draw.rectangle((122 * el_pct / 100, 59, 125, 59), outline='white', fill='black')




class Screen:

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
    
    def enable(self):
        self.enabled = True

    def enableClock(self):
        self.enableClock = True

    def disable(self):
        with canvas(device) as draw:
            draw.rectangle((0, 0, self.device.width - 1, self.device.height - 1), outline='black', fill='black')
        self.enabled = False    
    
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

    def make_font(self,name, size):
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', name))
        return ImageFont.truetype(font_path, size)
        
    def __init__(self, dev, isColour, isScroll):
        self.device = dev
        self.enabled = True
        self.isColour = isColour
        self.isScroll = isScroll
        self.artistScroll = None
        self.titleScroll = None
        self.albumartcache = {}
        self.icons = {
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

    def logo(self, lanip="", wlanip=""):

        if (self.isColour):
            albumartimage = Image.open("logo/splash.png") \
                .transform(self.device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
                .convert(self.device.mode)

            bgd = Image.new("RGBA", self.device.size, "black")
            bgd.paste(albumartimage, (5, 1))
            mydither = True

            with canvas(self.device, background=bgd, dither=mydither) as draw:

                if lanip != '':
                    ip = lanip
                elif wlanip != '':
                    ip = wlanip
                else:
                    ip = "volumio.local"

                draw.text((3, 65), 'NanoSound v2.0', font=self.fonts['small'], fill='white')
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
        
def make_font(name, size):
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)

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
    global startt, endt, idle, screen,GPIOButtonNo

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


# Invoke the arguments while scheduling.
def run_threaded(job_func, *args, **kwargs):   
   job_thread = threading.Thread(target=job_func, args=args, kwargs=kwargs)
   job_thread.start()
    
data={}

hasOLED = False
isColour = False
isScroll = False
GPIOButtonNo=0
ampon = False
screen = None

def main():
    global GPIOButtonNo,hasOLED,isColour,isScroll,ampon,screen,display,device
    
    try:
        with open('/sys/firmware/devicetree/base/model') as f:
            if 'Raspberry Pi 4' in f.read():
                isScroll = False
            else:
                isScroll = True
        
    except:
        isScroll = True

    #readconfig    
    try:
        with open('/data/configuration/miscellanea/nanosound/config.json') as f:
            data = json.load(f)
            display = data['oledDisplay']['value']
            model = data['model']['value']
            print(display)
    except:
        display = '3'
        model = 'DAC2'
        

    print(display)

    if display == '2':
        device = ssd1306(port=1, address=0x3C)
        isColour = False
        hasOLED = True
    elif display == '3':
        actual_args = ['-f', '/home/volumio/nanosound_oled/ssd1351.conf']        
        isScroll = True
        isColour = True      
        hasOLED = True  
        device = get_device(actual_args)
    elif display == 'N':
        isColour = False
        hasOLED = False
    else:
        device = sh1106(port=1, address=0x3C)        
        isColour = False
        hasOLED = True

    
    #Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(27, GPIO.OUT)
    
    
    
    if(model =="DAC2"):
        GPIOButtonNo = 6
    elif (model == "DAC3"):
        GPIOButtonNo = 9
    
    GPIO.setup(GPIOButtonNo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(GPIOButtonNo, GPIO.BOTH, callback=optionButPress, bouncetime=30)

    
    if (hasOLED):
        screen = Screen(device,isColour,isScroll)
        screen.logo()
        time.sleep(0.5)
        schedule.every(0.5).seconds.do(run_threaded,refreshData)
        schedule.every(1).seconds.do(run_threaded,refreshScreen,screen)
    
    
    
    while 1:
        schedule.run_pending()
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
