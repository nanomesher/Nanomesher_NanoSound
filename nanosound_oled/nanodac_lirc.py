#!/usr/bin/env python
from __future__ import unicode_literals
PYTHONIOENCODING="UTF-8"
from socketIO_client import SocketIO, LoggingNamespace
import lirc
import urllib2
import json


playlist=[]
playing_index=0


def on_getState_response(*args):
    global playlist
    alist = args
    playlist = alist[0]
    
def playNextPlaylist():
    global playing_index
    playing_index = playing_index + 1
    if(playing_index >= len(playlist)):
        playing_index = 0
    playPlaylist(playing_index)

def playPrevPlaylist():
    global playing_index
    playing_index = playing_index - 1
    if(playing_index < 0):
        playing_index = (len(playlist)-1)
    playPlaylist(playing_index)


def listPlayList():
    with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
        socketIO.on('pushListPlaylist', on_getState_response)
        socketIO.emit('listPlaylist','')
        socketIO.wait(seconds=2)
		
def playPlaylist(playlist_index):
	playlistname = playlist[playlist_index]
	urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=playplaylist&name=' + playlistname)


	
def mute():
  #urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&value=mute')

  with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
    socketIO.emit('mute','')
	

def unmute():
  #urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=volume&value=unmute')
  with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
    socketIO.emit('unmute','')


def unrandom():
  urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=random&value=false')


def randomset():
  urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=random&value=true')


def repeat():
  urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=repeat&value=true')

def unrepeat():
  urllib2.urlopen('http://127.0.0.1:3000/api/v1/commands/?cmd=repeat&value=false')


listPlayList()
sockid = lirc.init("nanosound","/home/volumio/nanosound_oled/lircrc", blocking=True)

muted=False
randomed=False
repeated=False  #0-no repeat , 1-repeat one, 2-repeat

volstatus = json.load(urllib2.urlopen('http://127.0.0.1:3000/api/v1/getstate'))
				
if('repeat' in volstatus):
	if(volstatus['repeat']):
		repeated = True
	else:
		repeated = False
else:
	repeated = False
					
if('random' in volstatus):
	if(volstatus['random']):
		randomed = True
	else:
		randomed = False
else:
	randomed = False

if('mute' in volstatus):
	if(volstatus['mute']):
		muted = True
	else:
		muted = False
else:
	muted = False	

while(True):

   button = lirc.nextcode()
   if(len(button)>0):
     command=button[0]
	 	
     if(command=="listup"):
		playNextPlaylist()
     elif(command=="listdown"):
		playPrevPlaylist()					
     elif(not muted) and (command=="mute"):
       muted=True
       mute()
     elif(muted) and (command=="mute"):
       muted=False
       unmute()
     elif(not randomed) and (command=="random"):
       randomed=True
       randomset()
     elif(randomed) and (command=="random"):
       randomed=False
       unrandom()
     elif(not repeated) and (command=="repeat"):
       repeated=True
       repeat()
     elif(repeated) and (command=="repeat"):
       repeated=False
       unrepeat()
