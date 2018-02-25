#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  Timelapse.py
#
#  Copyright 2018  Bill Williams
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
'''
from time import sleep
from 	Dialog import *
from 	Mapping import *
from	NotePage import *

class Timelapse ( BasicNotepage ):
	def BuildPage ( self ):
		f = ttk.LabelFrame(self,text='Time lapse settings',padding=(5,5,5,5))
		f.grid(row=0,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)
		f.columnconfigure(4,weight=1)

		Label(f,text='Default').grid(row=0,column=0,sticky='E')
		self.LowLightCaptureButton = Button(f,text='Low Light',width=15, \
			command=self.CaptureLowLight)
		self.LowLightCaptureButton.grid(row=1,column=0,sticky='W')
		self.StartDelayCaptureButton = Button(f,text='Delay Capture',width=15, \
			command=self.StartDelayCapture)
		self.StartDelayCaptureButton.grid(row=2,column=0,sticky='W')

	def CaptureLowLight ( self ):
		self.camera.capture('foo.jpg')
		pass
	def StartDelayCapture ( self ):
		pass
	#### TODO: Implement Reset NEEDS LOTS OF WORK!!
	def Reset ( self ):
		pass

'''
	What controls are needed for this page?
	Photo captures:
		Type of Time lapse
			Burst
			Timed
			etc
		Whether the image settings stay the same for each picture - Checkbox
		Whether the Video port is used or not (faster) - Checkbox
		Filename		(Textbox entry)
		Start
			Immediately
			Delay XXX YYY SEC, MIN HR
			On a specific date/time
		Delay between each shot.... or at a specific time each day, etc....
			e.g., Every XX YYY where XX is a number YYY is SEC, MIN, HR, DAY
			e.g., On every MIN, 1/2 HR, HOUR
			e.g., Every Day at XX:XX Time
		When does the capture end
			After XXX shots		XXX from 1 to 1000?
			After XXX minutes, Hours, Days
			On XXXX date
		Append a number or a date/time to 'Filename' - or both
			Use Drop down ComboBox
			e.g.	Bill_1.jpg, Bill_2.jpg, ... etc
			or		Bill_Date_Time.jpg, Bill_Date_Time.jpg, ... etc
			or both Bill_Date_Time_1.jpg, Bill_Date_Time_2.jpg, ... etc
	What about video captures?
'''


'''
	Examples from the picamera documentation
	https://picamera.readthedocs.io/en/release-1.13/recipes1.html

The following script provides a brief example of configuring these settings:

from time import sleep
from picamera import PiCamera

camera = PiCamera(resolution=(1280, 720), framerate=30)
# Set ISO to the desired value
camera.iso = 100
# Wait for the automatic gain control to settle
sleep(2)
# Now fix the values
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
# Finally, take several photos with the fixed settings
camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])

from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.start_preview()
sleep(2)
for filename in camera.capture_continuous('img{counter:03d}.jpg'):
    print('Captured %s' % filename)
    sleep(300) # wait 5 minutes
'''

'''
from time import sleep
from picamera import PiCamera
from datetime import datetime, timedelta

def wait():
    # Calculate the delay to the start of the next hour
    next_hour = (datetime.now() + timedelta(hour=1)).replace(
        minute=0, second=0, microsecond=0)
    delay = (next_hour - datetime.now()).seconds
    sleep(delay)

camera = PiCamera()
camera.start_preview()
wait()
for filename in camera.capture_continuous('img{timestamp:%Y-%m-%d-%H-%M}.jpg'):
    print('Captured %s' % filename)
    wait()


3.7. Capturing in low light
Using similar tricks to those in Capturing consistent images, the Pi’s
camera can capture images in low light conditions. The primary objective
is to set a high gain, and a long exposure time to allow the camera to
gather as much light as possible. However, the shutter_speed attribute
is constrained by the camera’s framerate so the first thing we need to
do is set a very slow framerate. The following script captures an image
with a 6 second exposure time (the maximum the Pi’s V1 camera module is
capable of; the V2 camera module can manage 10 second exposures):

from picamera import PiCamera
from time import sleep
from fractions import Fraction

# Force sensor mode 3 (the long exposure mode), set
# the framerate to 1/6fps, the shutter speed to 6s,
# and ISO to 800 (for maximum gain)
camera = PiCamera(
    resolution=(1280, 720),
    framerate=Fraction(1, 6),
    sensor_mode=3)
camera.shutter_speed = 6000000
camera.iso = 800
# Give the camera a good long time to set gains and
# measure AWB (you may wish to use fixed AWB instead)
sleep(30)
camera.exposure_mode = 'off'
# Finally, capture an image with a 6s exposure. Due
# to mode switching on the still port, this will take
# longer than 6 seconds
camera.capture('dark.jpg')
'''
