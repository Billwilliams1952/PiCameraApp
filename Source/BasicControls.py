#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  BasicControls.py
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

import os
from   collections import OrderedDict
import RPi.GPIO

# If no RPi.GPIO, then disable the ability to toggle the camera LED
RPiGPIO = True

try:
	import 	ttk
	from 		ttk import *
except ImportError:
	from		tkinter import ttk
	from 		tkinter.ttk import *

# We are running PILLOW, the fork of PIL
import PIL
from PIL import Image, ImageTk, ExifTags

from 	Dialog			import *
from 	Mapping			import *
from	NotePage			import *
from	Utils				import *
from	VideoParams		import *
from	PhotoParams		import *
from	ImageEffects	import *

class BasicControls ( BasicNotepage ):
	def BuildPage ( self ):
		#### TODO: 	Add Rotation. Cleanup and organize controls
		#			Add handling of Image Effect Params

		#----------- Select port for image captures ------------
		f1 = MyLabelFrame(self,'Select port for image captures',0,0,span=2)
		self.UseVidPort = MyBooleanVar(False)
		self.UseRadio = MyRadio(f1,'Use Still Port',False,self.UseVidPort,
					self.UseVideoPort,0,0,'W',tip=100)
		MyRadio(f1,'Use Video Port',True,self.UseVidPort,
					self.UseVideoPort,0,1,'W',tip=101)
		f2 = ttk.Frame(f1)			# Sub frame
		f2.grid(row=1,column=0,columnspan=4,sticky='NSEW')
		self.VideoDenoise = MyBooleanVar(True)
		b = ttk.Checkbutton(f2,text='Video denoise',variable=self.VideoDenoise,
			command=self.VideoDenoiseChecked)
		b.grid(row=1,column=0,sticky='NW',padx=5)
		ToolTip(b,msg=103)
		self.VideoStab = MyBooleanVar(False)
		b = ttk.Checkbutton(f2,text='Video stabilization',variable=self.VideoStab,
			command=self.VideoStabChecked)
		b.grid(row=1,column=1,sticky='NW')
		ToolTip(b, msg=105)
		self.ImageDenoise = MyBooleanVar(True)
		b = ttk.Checkbutton(f2,text='Image denoise',variable=self.ImageDenoise,
			command=self.ImageDenoiseChecked)
		b.grid(row=1,column=2,sticky='NW',padx=10)
		ToolTip(b, msg=104)

		#--------------- Picture/Video Capture Size ---------------
		f = MyLabelFrame(self,'Picture/Video capture size in pixels',1,0)
		#f.columnconfigure(0,weight=1)
		f1 = ttk.Frame(f)			# Sub frames to frame f
		f1.grid(row=1,column=0,sticky='NSEW')
		f1.columnconfigure(1,weight=1)
		self.UseFixedResolutions = BooleanVar()
		self.UseFixedResolutions.set(True)
		self.UseFixedResRadio = ttk.Radiobutton(f1,text='Use fixed:',
			variable=self.UseFixedResolutions,
			value=True,command=self.UseFixedResRadios,padding=(5,5,5,5))
		ToolTip(self.UseFixedResRadio,120)
		self.UseFixedResRadio.grid(row=0,column=0,sticky='NW')
		self.FixedResolutionsCombo = Combobox(f1,state='readonly',width=25)
		self.FixedResolutionsCombo.bind('<<ComboboxSelected>>',
			self.FixedResolutionChanged)
		self.FixedResolutionsCombo.grid(row=0,column=1,columnspan=3,sticky='W')
		ToolTip(self.FixedResolutionsCombo,121)
		#------------ Capture Width and Height ----------------
		# OrderedDict is used to ensure the keys stay in the same order as
		# entered. I want the combobox to display in this order
		#### TODO: 	Must check resolution and framerate and disable the Video
		# 			button if we exceed limits of the modes
		# Framerate 1-30 fps up to 1920x1080		16:9 aspect ratio
		# Framerate 1-15 fps up to 2592 x 1944		 4:3 aspect ratio
		# Framerate 0.1666 to 1 fps up to 2592 x 1944 4:3 aspect ratio
		# Framerate 1-42 fps up t0 1296 x 972 		 4:3 aspect ratio
		# Framerate 1-49 fps up to 1296 x 730		16:9 aspect ratio
		# Framerate 42.1 - 60 fps to 640 x 480		 4:3 aspect ratio
		# Framerate 60.1 - 90 fps to 640 x 480		 4:3 aspect ratio
		self.StandardResolutions = OrderedDict([ \
			('CGA', (320,200)),			('QVGA', (320,240)),
			('VGA', (640,480)),			('PAL', (768,576)),
			('480p', (720,480)),		('576p', (720,576)),
			('WVGA', (800,480)),		('SVGA', (800,600)),
			('FWVGA', (854,480)),		('WSVGA', (1024,600)),
			('XGA', (1024,768)),		('HD 720', (1280,720)),
			('WXGA_1', (1280,768)),		('WXGA_2', (1280,800)),
			('SXGA', (1280,1024)),		('SXGA+', (1400,1050)),
			('UXGA', (1600,1200)),		('WSXGA+', (1680,1050)),
			('HD 1080', (1920,1080)), 	('WUXGA', (1920,1200)),
			('2K', (2048,1080)),		('QXGA', (2048, 1536)),
			('WQXGA', (2560,1600)),		('MAX Resolution', (2592,1944)),
		   ])
		vals = []
		for key in self.StandardResolutions.keys():
			vals.append('%s: (%dx%d)' % (key, # Tabs not working?!!
							self.StandardResolutions[key][0],
							self.StandardResolutions[key][1]))
		self.FixedResolutionsCombo['values'] = vals
		self.FixedResolutionsCombo.current(10)

		f2 = ttk.Frame(f)		# subframe to frame f
		f2.grid(row=2,column=0,sticky='NSEW')
		f2.columnconfigure(2,weight=1)
		f2.columnconfigure(4,weight=1)
		b2 = ttk.Radiobutton(f2,text='Roll your own:',
			variable=self.UseFixedResolutions,
			value=False,command=self.UseFixedResRadios,padding=(5,5,5,5))
		b2.grid(row=1,column=0,sticky='NW')
		ToolTip(b2,122)

		Label(f2,text="Width:",anchor=E).grid(column=1,row=1,sticky='E',ipadx=3,ipady=3)
		Widths = []
		for i in range(1,82):
			Widths.append(32 * i) # Widths can be in 32 byte increments
		self.cb = MyComboBox ( f2, Widths, current=10,
			callback=self.ResolutionChanged, width=5, row=1, col=2,
			sticky='W', state='disabled', tip=123)

		Label(f2,text="Height:",anchor=E).grid(column=3,row=1,sticky='W',ipadx=5,ipady=3)
		Heights = []
		for i in range(1,123):
			Heights.append(16 * i)	# heights in 16 byte increments
		self.cb1 = MyComboBox ( f2, Heights, current=10,
			callback=self.ResolutionChanged, width=5, row=1, col=4,
			sticky='W', state='disabled', tip=124)

		ttk.Label(f2,text='Actual:').grid(row=2,column=1,sticky='E')
		self.WidthLabel = ttk.Label(f2,style='DataLabel.TLabel')
		self.WidthLabel.grid(row=2,column=2,sticky='W')
		ToolTip(self.WidthLabel,125)
		ttk.Label(f2,text='Actual:').grid(row=2,column=3,sticky='E')
		self.HeightLabel = ttk.Label(f2,style='DataLabel.TLabel')
		self.HeightLabel.grid(row=2,column=4,sticky='W')
		ToolTip(self.HeightLabel,126)

		Separator(f,orient=HORIZONTAL).grid(pady=5,row=3,column=0,
			columnspan=4,sticky='EW')

		#--------------- Zoom Region Before ----------------
		f4 = MyLabelFrame(f,'Zoom region of interest before taking '+
			'picture/video',4,0)
		#f4.columnconfigure(1,weight=1)
		#f4.columnconfigure(3,weight=1)
		Label(f4,text='X:').grid(row=0,column=0,sticky='E')
		self.Xzoom = ttk.Scale(f4,from_=0.0,to=0.94,orient='horizontal')
		self.Xzoom.grid(row=0,column=1,sticky='W',padx=5,pady=3)
		self.Xzoom.set(0.0)
		ToolTip(self.Xzoom,130)
		Label(f4,text='Y:').grid(row=0,column=2,sticky='E')
		self.Yzoom = ttk.Scale(f4,from_=0.0,to=0.94,orient='horizontal')
		self.Yzoom.grid(row=0,column=3,sticky='W',padx=5,pady=3)
		self.Yzoom.set(0.0)
		ToolTip(self.Yzoom,131)
		Label(f4,text='Width:').grid(row=1,column=0,sticky='E')
		self.Widthzoom = ttk.Scale(f4,from_=0.05,to=1.0,orient='horizontal')
		self.Widthzoom.grid(row=1,column=1,sticky='W',padx=5,pady=3)
		self.Widthzoom.set(1.0)
		ToolTip(self.Widthzoom,132)
		Label(f4,text='Height:').grid(row=1,column=2,sticky='E')
		self.Heightzoom = ttk.Scale(f4,from_=0.05,to=1.0,orient='horizontal')
		self.Heightzoom.grid(row=1,column=3,sticky='W',padx=5,pady=3)
		self.Heightzoom.set(1.0)
		ToolTip(self.Heightzoom,133)
		# WLW THIS IS A PROBLEM
		image = PIL.Image.open('Assets/reset.png') #.resize((16,16))
		self.resetImage = GetPhotoImage(image.resize((16,16)))
		self.ResetZoomButton = ttk.Button(f4,image=self.resetImage,
			command=self.ZoomReset)
		self.ResetZoomButton.grid(row=0,column=4,rowspan=2,sticky='W')
		ToolTip(self.ResetZoomButton,134)

		self.Xzoom.config(command=lambda newval,
			widget=self.Xzoom:self.Zoom(newval,widget))
		self.Yzoom.config(command=lambda newval,
			widget=self.Yzoom:self.Zoom(newval,widget))
		self.Widthzoom.config(command=lambda newval,
			widget=self.Widthzoom:self.Zoom(newval,widget))
		self.Heightzoom.config(command=lambda newval,
			widget=self.Heightzoom:self.Zoom(newval,widget))

		Separator(f,orient=HORIZONTAL).grid(pady=5,row=5,column=0,
			columnspan=3,sticky='EW')

		#--------------- Resize Image After ----------------
		f4 = MyLabelFrame(f,'Resize image after taking picture/video',6,0)
		#f4.columnconfigure(3,weight=1)
		#f4.columnconfigure(5,weight=1)

		b = MyBooleanVar(False)
		self.ResizeAfterNone = MyRadio(f4,'None (Default)',False,b,
			self.AllowImageResizeAfter,0,0,'W',pad=(0,5,0,5), tip=140)
		MyRadio(f4,'Resize',True,b,self.AllowImageResizeAfter,
					0,1,'W',pad=(5,5,0,5),tip=141)

		Label(f4,text="Width:",anchor=E).grid(column=2,row=0,sticky='E',ipadx=3,ipady=3)
		self.resizeWidthAfterCombo = MyComboBox ( f4, Widths, current=10,
			callback=self.ResizeAfterChanged, width=5, row=0, col=3,
			sticky='W', state='disabled', tip=142)

		Label(f4,text="Height:",anchor=E).grid(column=4,row=0,sticky='W',ipadx=5,ipady=3)
		self.resizeHeightAfterCombo = MyComboBox ( f4, Heights, current=10,
			callback=self.ResizeAfterChanged, width=5, row=0, col=5,
			sticky='W', state='disabled', tip=143)

		self.resizeAfter = None

		#--------------- Quick Adjustments ----------------
		f = MyLabelFrame(self,'Quick adjustments',2,0)
		#f.columnconfigure(2,weight=1)
		#-Brightness
		self.brightLabel, self.brightness, val = \
			self.SetupLabelCombo(f,'Brightness:',0,0,0, 100,
				self.CameraBrightnessChanged, self.camera.brightness )
		self.CameraBrightnessChanged(val)
		ToolTip(self.brightness,msg=150)
		#-Contrast
		self.contrastLabel, self.contrast, val = \
			self.SetupLabelCombo(f,'Contrast:',0,3,-100, 100,
				self.ContrastChanged, self.camera.contrast )
		self.ContrastChanged(val)
		ToolTip(self.contrast,msg=151)
		#-Saturation
		self.saturationLabel, self.saturation, val = \
			self.SetupLabelCombo(f,'Saturation:',1,0,-100, 100,
				self.SaturationChanged, self.camera.saturation, label='Sat' )
		self.SaturationChanged(val)
		ToolTip(self.saturation,msg=152)
		#-Sharpness
		self.sharpnessLabel, self.sharpness, val = \
			self.SetupLabelCombo(f,'Sharpness:',1,3,-100, 100,
				self.SharpnessChanged, self.camera.sharpness )
		self.SharpnessChanged(val)
		ToolTip(self.sharpness,msg=153)
		#-Reset
		#self.ResetGeneralButton = Button(f,image=self.resetImage,width=5,
			#command=self.ResetGeneralSliders)
		#self.ResetGeneralButton.grid(row=4,column=2,sticky='W',padx=5)
		#ToolTip(self.ResetGeneralButton,msg=154)

		#--------------- Image Effects ----------------
		f = MyLabelFrame(self,'Preprogrammed image effects',3,0)
		#f.columnconfigure(2,weight=1)

		v = MyBooleanVar(False)
		self.NoEffectsRadio = MyRadio(f,'None (Default)',False,v,
			self.EffectsChecked,0,0,'W',tip=160)
		MyRadio(f,'Select effect:',True,v,self.EffectsChecked,0,1,'W',
			tip=161)

		self.effects = Combobox(f,height=15,width=10,state='readonly')#,width=15)
		self.effects.grid(row=0,column=2,sticky='W')
		effects = list(self.camera.IMAGE_EFFECTS.keys())	# python 3 workaround
		effects.remove('none')
		effects.sort() #cmp=lambda x,y: cmp(x.lower(),y.lower())) # not python 3
		self.effects['values'] = effects
		self.effects.current(0)
		self.effects.bind('<<ComboboxSelected>>',self.EffectsChanged)
		ToolTip(self.effects, msg=162)

		self.ModParams = ttk.Button(f,text='Params...',
			command=self.ModifyEffectsParamsPressed,underline=0,padding=(5,3,5,3),width=8)
		self.ModParams.grid(row=0,column=3,sticky=EW,padx=5)
		ToolTip(self.ModParams, msg=163)
		self.EffectsChecked(False)
		'''
				Add additional controls if JPG is selected
				Certain file formats accept additional options which can be specified as keyword
				arguments. Currently, only the 'jpeg' encoder accepts additional options, which are:

				quality - Defines the quality of the JPEG encoder as an integer ranging from 1 to 100.
							 Defaults to 85. Please note that JPEG quality is not a percentage and
							 definitions of quality vary widely.
				restart - Defines the restart interval for the JPEG encoder as a number of JPEG MCUs.
							 The actual restart interval used will be a multiple of the number of MCUs per row in the resulting image.
				thumbnail - Defines the size and quality of the thumbnail to embed in the Exif
								metadata. Specifying None disables thumbnail generation. Otherwise,
								specify a tuple of (width, height, quality). Defaults to (64, 48, 35).
				bayer - If True, the raw bayer data from the camera’s sensor is included in the
							Exif metadata.
		'''
		#--------------- Flash Mode ---------------
		f = MyLabelFrame(self,'LED and Flash mode',4,0,span=4)
		#f.columnconfigure(3,weight=1)
		self.LedOn = MyBooleanVar(True)
		self.LedButton = ttk.Checkbutton(f,text='Led On (via GPIO pins)',
			variable=self.LedOn, command=self.LedOnChecked)
		self.LedButton.grid(row=0,column=0,sticky='NW',pady=5, columnspan=2)
		ToolTip(self.LedButton,msg=102)
		Label(f,text='Flash Mode:').grid(row=1,column=0,sticky='W')
		b = MyStringVar('off')
		self.FlashModeOffRadio = MyRadio(f,'Off (Default)','off',b,
			self.FlashModeButton,1,1,'W',tip=180)
		MyRadio(f,'Auto','auto',b,self.FlashModeButton,1,2,'W',tip=181)
		MyRadio(f,'Select:','set',b,self.FlashModeButton,1,3,'W',tip=182)
		# Use invoke() on radio button to force a command
		self.FlashModeCombo = Combobox(f,state='readonly',width=10)
		self.FlashModeCombo.grid(row=1,column=4,sticky='W')
		self.FlashModeCombo.bind('<<ComboboxSelected>>',self.FlashModeChanged)
		modes = list(self.camera.FLASH_MODES.keys())
		modes.remove('off')		# these two are handled by radio buttons
		modes.remove('auto')
		modes.sort() #cmp=lambda x,y: cmp(x.lower(),y.lower()))
		self.FlashModeCombo['values'] = modes
		self.FlashModeCombo.current(0)
		self.FlashModeCombo.config(state='disabled')
		ToolTip(self.FlashModeCombo,183)

		self.FixedResolutionChanged(None)

	def Reset ( self ):
		# Use widget.invoke() to simulate a button/radiobutton press
		self.UseRadio.invoke()
		self.LedOn.set(True)
		self.VideoStab.set(False)		# Doesn't call the function!
		self.VideoDenoise.set(True)
		self.ImageDenoise.set(True)
		self.ResetGeneralSliders()
		self.UseFixedResRadio.invoke()
		self.FixedResolutionsCombo.current(10) # Set to 1280 x 1024
		self.ResetZoomButton.invoke()
		self.ResizeAfterNone.invoke()
		self.NoEffectsRadio.invoke()
		self.effects.current(0)
		self.UseRadio.focus_set()
		self.FlashModeOffRadio.invoke()
	def UseVideoPort ( self , val):
		pass #self.camera.use_video_port = val
	def LedOnChecked ( self ):
		self.camera.led = self.LedOn.get()
	def SetupLabelCombo ( self, parent, textname, rownum, colnum,
								minto, maxto, callback, cameraVal, label=''):
		l = Label(parent,text=textname)
		l.grid(row=rownum,column=colnum*3,sticky='E',pady=2)#,padx=2)
		label = Label(parent,width=4,anchor=E)#,relief=SUNKEN, background='#f0f0ff')
		label.grid(row=rownum,column=colnum*3+1)
		#label.config(font=('Helvetica',12))
		# create the scale WITHOUT a callback. Then set the scale.
		scale = ttk.Scale(parent,from_=minto,to=maxto,orient='horizontal')
		scale.grid(row=rownum,column=colnum*3+2,sticky='W',padx=5,pady=3)
		val = cameraVal
		scale.set(val)		# this would attempt to call any callback
		scale.config(command=callback)	# now supply the callback
		return label, scale, val
	def UpdateMe( self, newVal, label ):
		val = int(float(newVal))
		label.config(text='%d' % val,
			foreground='red' if val < 0 else 'blue' if val > 0 else 'black' )
		return val
	def CameraBrightnessChanged ( self, newVal ):
		self.brightness.focus_set()
		self.camera.brightness = self.UpdateMe(newVal,self.brightLabel)
	def ContrastChanged ( self, newVal ):
		self.contrast.focus_set()
		self.camera.contrast = self.UpdateMe(newVal,self.contrastLabel)
	def SaturationChanged ( self, newVal ):
		self.saturation.focus_set()
		self.camera.saturation = self.UpdateMe(newVal,self.saturationLabel)
	def SharpnessChanged ( self, newVal ):
		self.sharpness.focus_set()
		self.camera.sharpness = self.UpdateMe(newVal,self.sharpnessLabel)
	def ResetGeneralSliders ( self ):
		self.brightness.set(50)
		self.contrast.set(0)
		self.saturation.set(0)
		self.sharpness.set(0)
		#self.ResetGeneralButton.focus_set()
	def UpdateWidthHeightLabels ( self ):
		res = self.camera.resolution # in case a different default value
		self.WidthLabel.config(text='%d' % int(res[0]))
		self.HeightLabel.config(text='%d' % int(res[1]))
	def ResolutionChanged(self,event):
		self.camera.resolution = (int(self.cb.get()),int(self.cb1.get()))
		self.UpdateWidthHeightLabels()
	def FixedResolutionChanged ( self, event ):
		key = self.FixedResolutionsCombo.get().split(':')[0]
		self.camera.resolution = self.StandardResolutions[key]
		self.UpdateWidthHeightLabels()
	def UseFixedResRadios ( self ):
		states = {False:'disabled', True:'readonly'}
		useFixedRes = self.UseFixedResolutions.get()
		if useFixedRes:
			self.FixedResolutionChanged(None)
			self.FixedResolutionsCombo.focus_set()
		else:
			self.ResolutionChanged(None)
			self.cb.focus_set()
		self.FixedResolutionsCombo.config(state=states[useFixedRes])
		self.cb.config(state=states[not useFixedRes])
		self.cb1.config(state=states[not useFixedRes])
	def Zoom ( self, newVal, scale ):
		self.camera.zoom = (float(self.Xzoom.get()),float(self.Yzoom.get()),
			float(self.Widthzoom.get()),float(self.Heightzoom.get()))
		scale.focus_set()
	def SetZoom ( self, x, y, w, h ):
		self.Xzoom.set(x)
		self.Yzoom.set(y)
		self.Widthzoom.set(w)
		self.Heightzoom.set(h)
	def ZoomReset ( self ):
		self.Xzoom.set(0.0)
		self.Yzoom.set(0.0)
		self.Widthzoom.set(1.0)
		self.Heightzoom.set(1.0)
	def AllowImageResizeAfter ( self, allowResizeAfter ):
		if allowResizeAfter:
			state = 'readonly'
			self.ResizeAfterChanged(None)
			self.resizeWidthAfterCombo.focus_set()
		else:
			self.resizeAfter = None
			state = 'disabled'
		self.resizeWidthAfterCombo.config(state=state)
		self.resizeHeightAfterCombo.config(state=state)
	def ResizeAfterChanged ( self, event ):
		self.resizeAfter = ( int(self.resizeWidthAfterCombo.get()),
									int(self.resizeHeightAfterCombo.get()) )
	def GetResizeAfter ( self ):
		return self.resizeAfter
	def EffectsChecked ( self, EffectsEnabled ):
		if EffectsEnabled == True:
			self.effects.config(state='readonly')
			self.EffectsChanged(None)
			self.effects.focus_set()
		else:
			self.effects.config(state='disabled')
			self.ModParams.config(state='disabled')
			self.camera.image_effect = 'none'
	def EffectsChanged ( self, event ):
		self.camera.image_effect = self.effects.get()
		if self.camera.image_effect in ['solarize', 'colorpoint',
				'colorbalance', 'colorswap', 'posterise', 'blur', 'film',
				'watercolor']:
			self.ModParams.config(state='!disabled')
			params = Effects1Page.EffectParam[self.camera.image_effect]
			if params != -1:	# We have something to program
				self.camera.image_effect_params = \
					Effects1Page.EffectParam[self.camera.image_effect]
		else:
			self.ModParams.config(state='disabled')
	def ModifyEffectsParamsPressed ( self ):
		ImageEffectsDialog(self,title='Image Effects Parameters',
			camera=self.camera,okonly=False)
	def ImageDenoiseChecked ( self ):
		self.camera.image_denoise = self.ImageDenoise.get()
	def VideoDenoiseChecked ( self ):
		self.camera.video_denoise = self.VideoDenoise.get()
	def VideoStabChecked ( self ):
		self.camera.video_stabilization = self.VideoStab.get()
	def FlashModeButton ( self, FlashMode ):
		if FlashMode == 'set':
			self.FlashModeCombo.config(state='readonly')
			self.FlashModeCombo.focus_set()
			self.FlashModeChanged(None)
		else:
			self.FlashModeCombo.config(state='disabled')
			self.camera.flash_mode = FlashMode
	def FlashModeChanged ( self, event ):
		self.camera.flash_mode = self.FlashModeCombo.get()

