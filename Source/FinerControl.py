#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  FinerControl.py
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

from 	Dialog import *
from 	Mapping import *
from	NotePage import *
from	Utils import *

class FinerControl ( BasicNotepage ):
	def BuildPage ( self ):
		#--------------- Color Effects ---------------
		f = MyLabelFrame(self,'Color effects (Luminance and Chrominance - YUV420)',
			2,0,span=4)
		f.columnconfigure(1,weight=1)
		b = MyBooleanVar(False)
		self.NoColorEffectsRadio = MyRadio(f,'No added color effect (Default)',
			False,b,self.AddColorEffect,0,0,'W',span=2,tip=370)
		MyRadio(f,'Add color effect',True,b,self.AddColorEffect,1,0,'W',tip=371)
		# Added Luminance (Brightness)
		self.lLabel = ttk.Label(f,text='Luminance:',padding=(20,2,0,2))
		self.lLabel.grid(row=2,column=0,sticky='W')
		self.lScale = ttk.Scale(f,from_=0,to=100, \
				orient='horizontal',length=100)
		self.lScale.grid(row=2,column=1,sticky='W',pady=2)
		self.lScale.set(self.camera.brightness)
		self.lScale.config(command=self.lValueChanged)
		ToolTip(self.lScale,372)
		self.uLabel = ttk.Label(f,text='U chrominance:',padding=(20,2,0,2))
		self.uLabel.grid(row=3,column=0,sticky='W')
		self.uScale = ttk.Scale(f,from_=0,to=255, \
				orient='horizontal',length=100)
		self.uScale.grid(row=3,column=1,sticky='W',pady=2)
		self.uScale.set(128)
		ToolTip(self.uScale,373)
		self.uScale.config(command=self.uValueChanged)
		self.vLabel = ttk.Label(f,text='V chrominance:',padding=(20,2,0,2))
		self.vLabel.grid(row=4,column=0,sticky='W')
		self.vScale = ttk.Scale(f,from_=0,to=255, \
				orient='horizontal',length=100)
		self.vScale.grid(row=4,column=1,sticky='W',pady=2)
		self.vScale.set(128)
		self.vScale.config(command=self.vValueChanged)
		ToolTip(self.vScale,374)
		self.YUV = ttk.Label(f,width=20,style='DataLabel.TLabel')
		self.YUV.grid(row=5,column=0,sticky='W')
		ToolTip(self.YUV,375)
		self.RGB = ttk.Label(f,style='DataLabel.TLabel')
		self.RGB.grid(row=5,column=1,columnspan=2,sticky='W')
		ToolTip(self.RGB,376)

		self.Color = Canvas(f,width=10,height=32)
		self.Color.grid(row=6,column=0,columnspan=2,sticky="EW")
		self.colorbg = self.Color.cget('background')
		ToolTip(self.Color,377)

		#--------------- Sensor Mode ---------------
		f = MyLabelFrame(self,'Sensor mode',3,0,span=4)
		f.columnconfigure(1,weight=1)
		# See PiCamera documentation - nothing happens unless the camera
		# is already initialized to a value other than 0 (Auto)
		l = ttk.Label(f,text='Sensor mode changes may not work! Some bugs',
			style='RedMessage.TLabel')
		l.grid(row=3,column=0,columnspan=2,sticky='W')

		b = MyBooleanVar(True)
		# Select input mode based of Resolution and framerate:',
		self.SensorModeAutoRadio = MyRadio(f,'Auto (Default mode 0)',
			True,b,self.AutoSensorModeRadio,1,0,'NW',span=2,tip=350)
		MyRadio(f,'Select Mode:',False,b,
			self.AutoSensorModeRadio,2,0,'NW',tip=351)
		self.SensorModeCombo = Combobox(f,state='disabled',width=35)
		self.SensorModeCombo.grid(row=2,column=1,sticky='W')
		self.SensorModeCombo['values'] = [ \
			'Mode 1: to 1920x1080 1-30 fps ',
			'Mode 2: to 2592x1944 1-15 fps Image',
			'Mode 3: to 2592x1944 0.1666-1 fps Image',
			'Mode 4: to 1296x972  1-42 fps',
			'Mode 5: to 1296x730  1-49 fps',
			'Mode 6: to 640x480   42.1-60 fps',
			'Mode 7: to 640x480   60.1-90 fps',
			]
		self.SensorModeCombo.current(0)
		self.SensorModeCombo.bind('<<ComboboxSelected>>',self.SensorModeChanged)
		ToolTip(self.SensorModeCombo,352)

		f = MyLabelFrame(self,'Clock Mode',4,0,span=4)
		b = MyStringVar('reset')
		self.ClockReset = MyRadio(f,'Reset (default)',
			'reset',b,self.ClockResetRadio,0,0,'W',tip=360)
		MyRadio(f,'Raw','raw',b,self.ClockResetRadio,0,1,'W',tip=361)

		f = MyLabelFrame(self,'Timestamp',5,0)
		ttk.Label(f,text="Current Timestamp:").grid(row=0,column=0,sticky='W')
		self.Timestamp = MyStringVar(int(self.camera.timestamp))
		l = ttk.Label(f,textvariable=self.Timestamp,foreground='#0000FF')
		l.grid(row=0,column=1,sticky='W')
		ToolTip(l,362)

		f = MyLabelFrame(self,'Still Stats',6,0)
		self.StillStats = MyBooleanVar(self.camera.still_stats)
		MyRadio(f,'Off (default)',
			False,b,self.StillStatsChanged,0,0,'NW',tip=363)
		MyRadio(f,'On',True,b,self.StillStatsChanged,0,1,'NW',tip=364)

		self.AddColorEffect(False)
		self.UpdateTimestamp()

	#### TODO: Implement Reset - IN WORK
	def Reset ( self ):
		self.lScale.set(50)
		self.uScale.set(128)
		self.vScale.set(128)
		self.NoColorEffectsRadio.invoke()
		self.SensorModeAutoRadio.invoke()
	def PassControlFrame ( self, BasicControlsFrame ):
		self.BasicControlsFrame = BasicControlsFrame
	def AddColorEffect ( self, EnableColorEffect ):
		if EnableColorEffect == True:
			self.uvValueChanged()
			s = '!disabled'
			self.Color.grid()	# show them
			self.YUV.grid()
			self.RGB.grid()
			self.lScale.focus_set()
		else:
			self.camera.color_effects = None
			s = 'disabled'
			self.Color.grid_remove()	# hide them
			self.YUV.grid_remove()
			self.RGB.grid_remove()
		self.uScale.state([s])	# why is this different?
		self.vScale.state([s])
		self.lScale.state([s])
	def uvValueChanged ( self ):
		def Clamp ( color ):
			return 0 if color <= 0 else 255 if color >= 255 else int(color)
		y = int(255 * float(self.camera.brightness) / 100.0)
		u = int(self.uScale.get())
		v = int(self.vScale.get())
		self.camera.color_effects = (u,v)
		# Y'UV420 to RGB - see Wikipedia  - conversion for Android
		red = Clamp(y + 1.370705 * (v-128))
		green = Clamp(y - 0.337633 * (u-128) - 0.698001 * (v-128))
		blue = Clamp(y + 1.732446 * (u-128))
		self.YUV.config(text='Y: %03d U: %03d V: %03d' % (y,u,v))
		self.RGB.config(text='R: %03d G: %03d B: %03d' % (red, green, blue))
		self.Color.config(background='#%02x%02x%02x' % (red,green,blue))
	def lValueChanged ( self, newVal ):
		self.lScale.focus_set()
		self.camera.brightness = (int)((float)(newVal))
		self.BasicControlsFrame.brightness.set(newVal)
		self.uvValueChanged()
	def uValueChanged ( self, newVal ):
		self.uScale.focus_set()
		self.uvValueChanged()
	def vValueChanged ( self, newVal ):
		self.vScale.focus_set()
		self.uvValueChanged()
	def AutoSensorModeRadio ( self, AutoSensor ):
		if AutoSensor == True:
			# Bug in the firmware. Cannot seem to get back to mode 0
			# after changing to any other mode!
			self.camera.sensor_mode = 0
			self.camera.sensor_mode = 0		# doesn't work!
			self.SensorModeCombo.config(state='disabled')
		else:
			self.SensorModeCombo.config(state='readonly')
			self.SensorModeCombo.focus_set()
			self.SensorModeChanged(None)
	def SensorModeChanged ( self, event ):
		mode = int(self.SensorModeCombo.current()) + 1
		self.camera.sensor_mode = mode
	def ClockResetRadio ( self, val ):
		print (val)
		self.camera.clock_mode = val
	def UpdateTimestamp ( self ):
		self.Timestamp.set(int(self.camera.timestamp))
		self.after(1000,self.UpdateTimestamp)
	def StillStatsChanged ( self, val ):
		print(val)
		self.camera.still_stats = val


