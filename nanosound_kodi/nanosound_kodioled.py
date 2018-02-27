#!/usr/bin/env python
from __future__ import unicode_literals

from oled.render import canvas
from oled.device import ssd1306, sh1106
from subprocess import *

import socket

import time
import datetime
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
#try:
device = sh1106(port=1, address=0x3C)
hasOLED = True
#except:
#	hasOLED = False



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




showip=False;
ampon=False;

def toggleAmp(value):
    global ampon
    if(ampon==True):
	GPIO.output(27,GPIO.LOW)
	ampon=False
    elif(ampon==False):
	GPIO.output(27,GPIO.HIGH)
	ampon=True

def toggleShowIP():
    global showip
    if(showip==False):
	showip=True
    elif(showip==True):
	showip=False



def optionButPress(value):
    global startt,endt
    if GPIO.input(16) == 1:
        startt = time.time()
    if GPIO.input(16) == 0:
        endt = time.time()
        elapsed = endt - startt
        if(elapsed)<1:
		toggleAmp(1)
	else:
		toggleShowIP()

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
GPIO.add_event_detect(16, GPIO.BOTH, callback=optionButPress, bouncetime=200)

#Switch ampon
toggleAmp(1)

while(not hasOLED):
   time.sleep(0.1)

   
try:
   if(hasOLED):
      with canvas(device) as draw:
         draw.text((5, 2), "NanoSound for Kodi",font=font1, fill="white")
         draw.text((5, 18), "v0.1",font=font1, fill="white")
		 
         draw.text((1, 36), GetLANIP(),font=font1, fill="white")
         draw.text((1, 50), GetWLANIP(),font=font1, fill="white")

   time.sleep(10)
except:
   pass
   
   
#only fetch when is 0
fetch=0
refresh=False

lastupdate = datetime.datetime.now()

while(hasOLED):
   
  
   try:        	
	for x in range(100,-10,-3):
					
			if(fetch==0):
				refresh=True
			else:
				refresh=False
		
			
			# #print(datetime.datetime.now()-lastupdate)

				
			if(refresh):
				playeridstatus = json.load(urllib2.urlopen('http://127.0.0.1/jsonrpc?request={%22jsonrpc%22:%20%222.0%22,%20%22method%22:%20%22Player.GetActivePlayers%22,%20%22id%22:%201}'))
				playstate = ' '
				title = ' ' 
				artist = ' '
				filetype = ' '
				repeat = ' '
				random = ' '


				if(len(playeridstatus['result'])>0):
			
					playerid=playeridstatus['result'][0]['playerid']
					
					playstatus= json.load(urllib2.urlopen('http://127.0.0.1/jsonrpc?request={%22jsonrpc%22:%20%222.0%22,%20%22method%22:%20%22Player.GetItem%22,%20%22params%22:%20{%20%22properties%22:%20[%22title%22,%20%22album%22,%20%22artist%22,%20%22duration%22,%20%22thumbnail%22,%20%22file%22,%20%22fanart%22,%20%22streamdetails%22],%20%22playerid%22:%20' + str(playerid) + '%20},%20%22id%22:%20%22AudioGetItem%22}'))
					if(playstatus['result']['item']['file']!=''):
						playstate='Playing..'
	
				
					
					if('label' in playstatus['result']['item']):
						title = playstatus['result']['item']['label']				
					elif('title' in playstatus['result']['item']):
						title = playstatus['result']['item']['title']
					else:
						if('file' in playstatus['result']['item']):
							title = playstatus['result']['item']['file'].split('/')[-1:][0]
						else:
							title = ' '
							
					if(title is None):
						title = ' '	

					if('artist' in playstatus['result']['item']):
						if(len(playstatus['result']['item']['artist'])>0):
							artist = playstatus['result']['item']['artist'][0]
						else:
							artist=' '
					else:
						artist=' '

					if(artist is None):
						artist = ' '		
						
					if('type' in playstatus['result']['item']):
						trackType = playstatus['result']['item']['type']
						if (trackType == "webradio"):
							filetype=webradio
						elif (trackType == "spotify"):
							filetype = '\uf1bc'
						else:
							filetype=musicfile
					else:
						filetype=' '

					#volume = str(volstatus['volume'])
					
					

				
			fetch=fetch+1
			if(fetch==2):
				fetch=0

			if(showip):
				artist = GetLANIP()
				title = GetWLANIP()
		
			with canvas(device) as draw:
				draw.rectangle((0, 0, device.width-1, device.height-1), outline="white", fill="black")
				draw.text((x, 2), title,font=font1, fill="white")
				w3, h3 = draw.textsize(text="\uf177", font=awesomefont)
				w, h = draw.textsize(text=artist,font=font1)
				w2,h2 = draw.textsize(text=playstate)
				left = (device.width - w) / 2
				left2 = (device.width - w2) / 2
				draw.text((left, 18), artist,font=font1, fill="white")
				draw.text((5,36), filetype, font=awesomefont,fill="white")
				if(ampon):
					draw.text((device.width - 17,36), headphone, font=awesomefont,fill="white")
				else:
					draw.text((device.width - 17,36), " ", font=awesomefont,fill="white")
				draw.text((left2, 36), playstate, fill="white")
				draw.text((10, 50), ' ', fill="white")
				draw.text((60, 50), repeat, font=awesomefont, fill="white")
				draw.text((75, 50), random, font=awesomefont, fill="white")
				draw.text((92, 50), text="\uf028", font=awesomefont,fill="white")
				draw.text((105, 50), ' ', fill="white")
				time.sleep(0.35)
   finally:		
		time.sleep(0.35)	

