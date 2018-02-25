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
try:
	from 		tkColorChooser import askcolor
except ImportError:
	from		tkinter.colorchooser import askcolor
try:
	import 	tkFileDialog
except ImportError:
	import	tkinter.filedialog
try:
	import 	tkMessageBox
except ImportError:
	import	tkinter.messagebox
try:
	import 	ttk
	from 		ttk import *
except ImportError:
	from tkinter import ttk
	#from 		ttk import *
try:
	import 	tkFont
except ImportError:
	import	tkinter.font

import PIL
from PIL import Image, ImageTk, ExifTags

from Utils import OnOff, EvenOdd
from PreferencesDialog import *

#
# Class to handle formatting and otuputting the camera settings and EXIF tags
#
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
		textbox.tag_configure("Title",font=("Arial",12,"bold"))
		textbox.tag_configure("Section",font=("Arial",11,"bold italic"))
		textbox.tag_configure("KeyboardCommand",font=boldFont,foreground='blue')
		textbox.tag_configure("CmdKey",font=boldUnderlineFont)
		textbox.tag_configure("odd",background='white')
		textbox.tag_configure("even",background='#f0f0ff')
		self.text = textbox

	def AddCmdKey ( self, text ):
		if self.outfile:
			self.outfile.write(text)
			self.outfile.write('\n')
		else:
			strs = text.split(':')
			bg = EvenOdd(self.even)
			self.text.insert(END,"  ",("KeyboardCommand",bg))
			self.text.insert(END,strs[0],("KeyboardCommand",bg))
			self.text.insert(END,strs[1],(bg))
			self.text.insert(END,'\n',(bg))
			self.even = not self.even

	def WriteString ( self, string, formatstring = "" ):
		if self.outfile:
			self.outfile.write(string)
			self.outfile.write('\n')
		else:
			self.text.insert(END,string,formatstring)
			self.text.insert(END,'\n',formatstring)

	def FillCameraSettingTextBox ( self, parent, writetofile = False ):
		if writetofile:
			# Get file to write, create it (delete if exist)
			self.outfile = tkFileDialog.asksaveasfile(mode='w',defaultextension="*.txt")
			if not self.outfile:
				self.ClearTextBox()
		else:
			self.outfile = None

		self.WriteString("Camera setups","Title")

		self.WriteString("Preferences","Section")

		self.AddCmdKey('Photo format:\t\t\'%s\'' % PreferencesDialog.DefaultPhotoFormat)
		# Output params based on photo format type....
		if PreferencesDialog.DefaultPhotoFormat == 'jpeg':
			pass

		self.WriteString("Basic","Section")

		self.AddCmdKey('Use video port:\t\t%s' % OnOff(self.BasicControls.UseVidPort.get()))
		self.AddCmdKey('Stabilization:\t\t%s' % OnOff(self.camera.video_stabilization))
		self.AddCmdKey('Video denoise:\t\t%s' % OnOff(self.camera.video_denoise))
		self.AddCmdKey('Image denoise:\t\t%s' % OnOff(self.camera.image_denoise))
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
		self.AddCmdKey('Brightness:\t\t%d' % self.camera.brightness)
		self.AddCmdKey('Contrast:\t\t%d' % self.camera.contrast)
		self.AddCmdKey('Saturation:\t\t%d' % self.camera.saturation)
		self.AddCmdKey('Sharpness:\t\t%d' % self.camera.sharpness)
		self.AddCmdKey('Image effect:\t\t%s' % self.camera.image_effect)
		params = self.camera.image_effect_params
		if params == None:
			self.AddCmdKey('Image params:\t\tnone')
		else:
			self.AddCmdKey('Image params:\t\t<WORK ON>')
		self.AddCmdKey('Rotation:\t\t%d degrees' % self.camera.rotation)
		self.AddCmdKey('Flash mode:\t\t%s' % self.camera.flash_mode)

		self.WriteString("Exposure","Section")

		self.AddCmdKey('Metering mode:\t\t%s' % self.camera.meter_mode)
		self.AddCmdKey('Exposure mode:\t\t%s' % self.camera.exposure_mode)
		effiso = int(100.0 * self.camera.analog_gain/self.camera.digital_gain)
		if self.camera.iso == 0:
			self.AddCmdKey('ISO:\t\tAuto (Effective %d)' % effiso)
		else:
			self.AddCmdKey('ISO:\t\t%d (Effective %d)' % (self.camera.iso,effiso))
		self.AddCmdKey('Analog gain:\t\t%.3f' % self.camera.analog_gain)
		self.AddCmdKey('Digital gain:\t\t%.3f' % self.camera.digital_gain)
		self.AddCmdKey('Exposure comp:\t\t%s' % self.camera.exposure_compensation)
		self.AddCmdKey('Shutter speed:\t\t%d usec' % \
			(self.camera.exposure_speed if self.camera.shutter_speed == 0 \
									   else self.camera.shutter_speed) )
		self.AddCmdKey('Exposure speed:\t\t%d usec' % self.camera.exposure_speed)
		self.AddCmdKey('Frame rate:\t\t%.3f fps' % self.camera.framerate)

		self.WriteString("Advanced","Section")

		self.AddCmdKey('AWB mode:\t\t%s' % self.camera.awb_mode)
		self.AddCmdKey('AWB Gains:\t\tRed %.3f Blue %.3f' % self.camera.awb_gains)
		self.AddCmdKey('DRC strength:\t\t%s' % self.camera.drc_strength)
		if self.camera.color_effects == None:
			self.AddCmdKey('Color effects:\t\tnone')
		else:
			self.AddCmdKey('Color effects:\t\t(U %d V %d)' % self.camera.color_effects)
		self.AddCmdKey('Sensor mode:\t\t%d' % self.camera.sensor_mode)


		self.WriteString("Annotate/EXIF metadata","Section")

		text = self.camera.annotate_text
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
		self.AddCmdKey('Annotate frame num:\t\t%s'% \
			OnOff(self.camera.annotate_frame_num))

		# Don't close file here (if open), wait to write EXIF tags

	def AddEXIFTags ( self, currentImage ):
		if self.EXIFAdded or not currentImage: return

		self.even = True
		self.WriteString("\nEXIF Tags","Title")
		# ExifTool reads correctly..... should we call that?
		# import exifread ????
		#----------- This does not read all tags --------------
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
			self.WriteString('Exif tags not supported!')

		self.CloseFile()
		self.EXIFAdded = True

	def ClearTextBox ( self ):
		self.text.delete("1.0",END)
		self.EXIFAdded = False

	def CloseFile ( self ):
		if self.outfile:
			self.outfile.close()
			self.outfile = None
