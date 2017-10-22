#!/usr/bin/env python
from __future__ import unicode_literals

from oled.render import canvas
from oled.device import ssd1306, sh1106
from subprocess import *

import socket
import mpd
import time
import os
import  RPi.GPIO as GPIO
import json
import urllib2
from PIL import ImageFont
from subprocess import check_output
time.sleep(1)
#serial = i2c(port=1, address=0x3C)

hasOLED=True

#device = ssd1306(serial, rotate=0)
try:
	device = sh1106(port=1, address=0x3C)
	hasOLED = True
except:
	hasOLED = False
	

client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600)

def GetLANIP():
   cmd = "ip addr show eth0 | grep inet  | grep -v inet6 | awk '{print $2}' | cut -d '/' -f 1"
   p = Popen(cmd, shell=True, stdout=PIPE)
   output = p.communicate()[0]
   return output[:-1]

def GetWLANIP():
   cmd = "ip addr show wlan0 | grep inet  | grep -v inet6 | awk '{print $2}' | cut -d '/' -f 1"
   p = Popen(cmd, shell=True, stdout=PIPE)
   output = p.communicate()[0]
   return output[:-1]


def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)

ampon=False;

def toggleAmp(value):
    global ampon
    if(ampon==True):
	GPIO.output(27,GPIO.LOW)
	ampon=False
    elif(ampon==False):
	GPIO.output(27,GPIO.HIGH)
	ampon=True

def get_pid(name):
    return check_output(["pidof",name])


font1 = make_font("code2000.ttf",12)
awesomefont = make_font("fontawesome-webfont.ttf",12)

webradio="\uf1be"
musicfile="\uf1c7"
headphone="\uf001"

check=0;

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(16, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(16, GPIO.RISING, callback=toggleAmp, bouncetime=200)
spotConRunning = False
spotConActive = False
spotConProcessRunning = False

#Switch ampon
toggleAmp(1)

while(not hasOLED):
   time.sleep(0.1)

   
try:
   if(hasOLED):
      with canvas(device) as draw:
         draw.text((5, 2), "NanoSound v1.0",font=font1, fill="white")
         draw.text((1, 18), GetLANIP(),font=font1, fill="white")
         draw.text((1, 36), GetWLANIP(),font=font1, fill="white")

   time.sleep(3)
except:
   pass
   
   
#only fetch when is 0
fetch=0
refresh=False

while(hasOLED):
   
  

   try:

	pid = get_pid("spotify-connect-web")
	spotConProcessRunning = True
   except:
	spotConProcessRunning = False
	
   try:        	
	for x in range(-10,80):
			
			if(fetch==0):
				refresh=True
			else:
				refresh=False
	
	
			if(spotConProcessRunning and refresh):	
				try:
					
						status = json.load(urllib2.urlopen('http://localhost:4000/api/info/status'))
						#print(status)

						if(status["logged_in"]):
								spotConRunning = True
						else:
								spotConRunning = False

						if(status["playing"]):
								spotConActive = True
						else:
								spotConActive = False

				except Exception as inst:
						spotConProcessRunning = False
						spotConRunning = False
						spotConActive = False


			if(refresh):

				currentsong = client.currentsong()
				status = client.status()

					
				if('title' in currentsong):
					title = currentsong['title']
				else:
					if('name' in currentsong):
						title = currentsong['name']
					else:
						if('file' in currentsong):
							
							title = currentsong['file'].split('/')[-1:][0]
						else:
							title = ' '

				if('artist' in currentsong):
					artist = currentsong['artist']
				else:
					artist=' '

				if('file' in currentsong):
					file = currentsong['file']
					if "http://" in file:
						filetype=webradio
					elif "://" in file:
						filetype=webradio
					else:
						filetype=musicfile
				else:
					filetype=' '

				if('bitrate' in status):
					bitrate = status['bitrate'] + "kbps"	
				else:
					bitrate = ' '

				if(bitrate == "0kbps"):
					bitrate = ' '

				if('elapsed' in status):
					elapsed = time.strftime('%H:%M:%S', time.gmtime(float(status['elapsed'])))
				else:
					elapsed = ' '
				volume = status['volume']
				state = status['state']
				


				if (state=="pause" or state=="stop") and spotConRunning and (not spotConActive):
						title = "Spotify Connect Ready"
						artist = socket.gethostname()
						check = 3		
						filetype = '\uf1bc'
						bitrate = ' '
						elapsed = ' '
						if spotConRunning and spotConActive:
										spotconmeta = json.load(urllib2.urlopen('http://localhost:4000/api/info/metadata'))
										title = spotconmeta["track_name"]
										artist = spotconmeta["artist_name"]
										check = 3
										filetype = '\uf1bc'
										bitrate = ' '
										elapsed = ' '

			time.sleep(0.1)
			fetch=fetch+1
			if(fetch==5):
				fetch=0
		
			with canvas(device) as draw:
				draw.rectangle((0, 0, device.width-1, device.height-1), outline="white", fill="black")
				draw.text((x, 2), title,font=font1, fill="white")
				w3, h3 = draw.textsize(text="\uf177", font=awesomefont)			
				w, h = draw.textsize(text=artist,font=font1)
				w2,h2 = draw.textsize(text=bitrate)
				left = (device.width - w) / 2
				left2 = (device.width - w2) / 2
				draw.text((left, 18), artist,font=font1, fill="white")
				draw.text((10,36), filetype, font=awesomefont,fill="white")
				if(ampon):
					draw.text((device.width - 20,36), headphone, font=awesomefont,fill="white")
				else:
					draw.text((device.width - 20,36), " ", font=awesomefont,fill="white")
				draw.text((left2, 36), bitrate, fill="white")
				draw.text((10, 50), elapsed, fill="white")
				draw.text((87, 50), text="\uf028", font=awesomefont,fill="white")
				draw.text((100, 50), volume, fill="white")
   finally:		
		time.sleep(0.1)	

