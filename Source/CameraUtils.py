'''
CameraUtils.py
Copyright (C) 2015 - Bill Williams

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
import picamera
from picamera import *
import picamera.array
try:	
	from Tkinter import *
except ImportError:
	from tkinter import *
import 	ttk
from 	ttk import *
import 	tkFont
from tkFont import *

try:
	import PIL
	from PIL import Image, ImageTk, ExifTags
except ImportError:
	raise ImportError("You do not seem to have the Python Imaging Library (PIL) installed")

class CameraUtils:
	def __init__ ( self, camera, BasicControls):
		self.camera = camera
		self.TextBox = None
		self.BasicControls = BasicControls	
		self.EXIFAdded = False
		self.even = True
	def SetupCameraSettingsTextbox ( self, textbox ):
		boldFont = Font(textbox,textbox.cget("font"))
		boldFont.configure(weight="bold")
		boldUnderlineFont = Font(textbox,textbox.cget("font"))
		boldUnderlineFont.configure(weight="bold",underline=True)
		textbox.tag_configure("Bold",font=boldFont)
		textbox.tag_configure("Title",font=("Arial",14,"bold"))
		textbox.tag_configure("KeyboardCommand",font=boldFont,foreground='blue')
		textbox.tag_configure("Center",justify = CENTER)
		textbox.tag_configure("Indent",lmargin1='1c',lmargin2='1c')
		textbox.tag_configure("CmdKey",font=boldUnderlineFont)
		textbox.tag_configure("odd",background='white')
		textbox.tag_configure("even",background='#f0f0ff')
		self.text = textbox	
	def AddCmdKey ( self, text ):
		strs = text.split(':')
		bg = 'even' if self.even else 'odd'  
		self.text.insert(END,strs[0],("KeyboardCommand",bg))
		self.text.insert(END,strs[1],(bg))
		self.text.insert(END,'\n',(bg))
		self.even = not self.even
	def FillCameraSettingTextBox ( self, parent ):		
		def OnOff ( val ): return 'On' if val else 'Off'
		self.text.insert(END,"Camera setups\n","Title")
		self.AddCmdKey('Use video port:\t\t%s' % OnOff(self.BasicControls.UseVideoPort.get()))
		self.AddCmdKey('Format:\t\t\'%s\''%self.BasicControls.GetPhotoCaptureFormat())
		self.AddCmdKey('Resolution:\t\t%d x %d pixels'%self.camera.resolution)
		zoom = self.camera.zoom
		if zoom[0] == 0 and zoom[1] == 0 and zoom[2] == 1.0 and zoom[3] == 1.0:
			self.AddCmdKey('Zoom:\t\tnone')
		else:
			self.AddCmdKey('Zoom:\t\t(X %.3f Y %.3f W %.3f H %.3f)'%zoom)
		resize = self.BasicControls.GetResizeAfter()
		if resize == None:
			self.AddCmdKey('Resize:\t\tnone')
		else:
			self.AddCmdKey('Resize:\t\t%d x %d pixels' % resize)
			 
		self.AddCmdKey('Image denoise:\t\t%s' % OnOff(self.camera.image_denoise))
		self.AddCmdKey('Video denoise:\t\t%s' % OnOff(self.camera.video_denoise))
		self.AddCmdKey('Stabilization:\t\t%s' % OnOff(self.camera.video_stabilization))
		self.AddCmdKey('AWB mode:\t\t%s' % self.camera.awb_mode)
		self.AddCmdKey('AWB Gains:\t\tRed %.3f Blue %.3f' % self.camera.awb_gains)
		self.AddCmdKey('Brightness:\t\t%d' % self.camera.brightness)
		self.AddCmdKey('Contrast:\t\t%d' % self.camera.contrast)
		self.AddCmdKey('Saturation:\t\t%d' % self.camera.saturation)
		self.AddCmdKey('Sharpness:\t\t%d' % self.camera.sharpness)
		if self.camera.color_effects == None:
			self.AddCmdKey('Color effects:\t\tnone')
		else:
			self.AddCmdKey('Color effects:\t\t(U %d V %d)' % self.camera.color_effects)
		self.AddCmdKey('Analog gain:\t\t%.3f' % self.camera.analog_gain)
		self.AddCmdKey('Digital gain:\t\t%.3f' % self.camera.digital_gain)
		effiso = int(100.0 * self.camera.analog_gain/self.camera.digital_gain)
		if self.camera.iso == 0:
			self.AddCmdKey('ISO:\t\tAuto (Effective %d)' % effiso)
		else:
			self.AddCmdKey('ISO:\t\t%d (Effective %d)' % (self.camera.iso,effiso))
		self.AddCmdKey('DRC strength:\t\t%s' % self.camera.drc_strength)
		self.AddCmdKey('Exposure comp:\t\t%s' % self.camera.exposure_compensation)
		self.AddCmdKey('Exposure mode:\t\t%s' % self.camera.exposure_mode)
		self.AddCmdKey('Exposure speed:\t\t%d usec' % self.camera.exposure_speed)
		self.AddCmdKey('Shutter speed:\t\t%d usec' % \
			(self.camera.exposure_speed if self.camera.shutter_speed == 0 \
									   else self.camera.shutter_speed) )
		self.AddCmdKey('Frame rate:\t\t%.3f fps' % self.camera.framerate)
		self.AddCmdKey('Image effect:\t\t%s' % self.camera.image_effect)
		params = self.camera.image_effect_params
		if params == None:
			self.AddCmdKey('Image params:\t\tnone')
		else:
			self.AddCmdKey('Image params:\t\t<WORK ON>')
		self.AddCmdKey('Metering mode:\t\t%s' % self.camera.meter_mode)
		self.AddCmdKey('Rotation:\t\t%d degrees' % self.camera.rotation)
		self.AddCmdKey('Sensor mode:\t\t%d' % self.camera.sensor_mode)
		self.AddCmdKey('Flash mode:\t\t%s' % self.camera.flash_mode)
		text = self.camera.annotate_text
		self.AddCmdKey('Annotate frame num:\t\t%s'% OnOff(self.camera.annotate_frame_num))
		if len(text) == 0:
			self.AddCmdKey('Annotation:\t\tnone')
		else:
			self.AddCmdKey('Annotate text:\t\'%s\'' % text)
			self.AddCmdKey('Annotate text size:\t\t%d' % \
				self.camera.annotate_text_size)
			self.AddCmdKey( \
				'Annotate foreground color:\tR %d G %d B %d' % \
				self.camera.annotate_foreground.rgb_bytes)
			if self.camera.annotate_background == None:
				self.AddCmdKey('Annotate background color:\tnone')
			else:
				self.AddCmdKey(\
					'Annotate background color:\tR %d G %d B %d' % \
					self.camera.annotate_background.rgb_bytes)	
	def AddEXIFTags ( self, currentImage ):
		if self.EXIFAdded: return
		self.even = True
		self.text.insert(END,"\nEXIF Tags\n","Title")
		try:
			exif = {
				PIL.ExifTags.TAGS[k] : v
				for k, v in currentImage._getexif().items()
				if k in PIL.ExifTags.TAGS
			}
			for key in exif.keys():
				text = '%s:\t\t%s' % (key,exif[key])
				self.AddCmdKey(text)
		except:
			self.text.insert(END,'Exif tags not supported!\n')
		self.EXIFAdded = True
	def ClearTextBox ( self ):
		self.text.delete("1.0",END)
		self.EXIFAdded = False
