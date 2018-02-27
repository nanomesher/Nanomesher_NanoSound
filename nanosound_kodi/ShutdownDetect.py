#!/usr/bin/env python
##Copyright [2017] [Nanomesher Limited]
##
##Licensed under the Apache License, Version 2.0 (the "License");
##you may not use this file except in compliance with the License.
##You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
##Unless required by applicable law or agreed to in writing, software
##distributed under the License is distributed on an "AS IS" BASIS,
##WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##See the License for the specific language governing permissions and
##limitations under the License.

import RPi.GPIO as GPIO
import os
import time

def ShutdownPressed(arg):
	os.system("sudo shutdown -h now")

GPIO_ButtonShutdown = 7
GPIO.setmode(GPIO.BOARD)


GPIO.setup(GPIO_ButtonShutdown, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #system shutdown button


while(True):
	GPIO.wait_for_edge(GPIO_ButtonShutdown, GPIO.RISING)
	start = time.time()

	time.sleep(0.05)
	while GPIO.input(GPIO_ButtonShutdown) == GPIO.HIGH:
		time.sleep(0.01)
	length = time.time()-start
	
	if(length > 0.25):
		ShutdownPressed(True)
