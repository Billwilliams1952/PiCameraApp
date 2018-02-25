'''
PreferencesDialog.py
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
import os
import datetime
import webbrowser		# display the Picamera documentation
try:
	from Tkinter import *
except ImportError:
	from tkinter import *
try:
	from 		tkColorChooser import askcolor
except ImportError:
	from		tkinter.colorchooser import askcolor
try:
	import 	tkFileDialog as FileDialog
except ImportError:
	import	tkinter.filedialog as FileDialog
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

from 	Dialog	import *
from 	Mapping	import *
from	NotePage	import *
from	Utils		import *
from	Tooltip	import *
from	PhotoParams import *
from	VideoParams import *

try:
	import PIL
	from PIL import Image, ImageTk
except ImportError:
	import PIL
	from PIL import Image	#, ImageTk

#
# All PiCameraApp global preferences ae handled here
#
class PreferencesDialog ( Dialog ):
	# Static variables
	DefaultPhotoDir = "/home/pi/Pictures"
	DefaultVideoDir = "/home/pi/Videos"
	DefaultFilesDir = "/home/pi/Documents"
	DefaultPhotoFormat = 'jpeg'
	DefaultVideoFormat = 'h264'
	DefaultTimestampFormat = "%m-%d-%Y-%H:%M:%S"
	PhotoTimestamp = False
	VideoTimestamp = False
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		DefaultPhotoDir = "/home/pi/Pictures"
		DefaultVideoDir = "/home/pi/Videos"
		DefaultFilesDir = "/home/pi/Documents"
		DefaultPhotoFormat = 'jpeg'
		DefaultVideoFormat = 'h264'
		DefaultTimestampFormat = "%m-%d-%Y-%H:%M:%S"
		PhotoTimestamp = False
		VideoTimestamp = False

	def BuildDialog ( self ):
		self.MainFrame.columnconfigure(0,weight=1)
		self.MainFrame.rowconfigure(0,weight=1)
		n = Notebook(self.MainFrame,padding=(5,5,5,5),width=30,height=200)
		n.grid(row=0,column=0,sticky='NEWS')

		self.GeneralPage = General(n,camera=self._camera,cancel=self.CancelButton,data=self)
		self.InterfacePage = Interface(n,camera=self._camera,cancel=self.CancelButton)
		self.OtherPage = Other(n,camera=self._camera,cancel=self.CancelButton)

		n.add(self.GeneralPage,text='General',underline=0)
		n.add(self.InterfacePage,text='Interface',underline=0)
		n.add(self.OtherPage,text='Other',underline=0)

	def OkPressed ( self ):
		#self.GeneralPage.SaveChanges()
		#self.InterfacePage.SaveChanges()
		#self.OtherPage.SaveChanges()
		return True

	def CancelPressed ( self ):
		if tkMessageBox.askyesno("PiCamera Preferences","Exit without saving changes?"):
			return True

# Handle PiCameraApp General preferences
class General ( BasicNotepage ):
	def BuildPage ( self ):
		# Setup default folder to save pictures and videos
		f = MyLabelFrame(self,'Set default directories',0,0)

		self.iconCameraBig = PIL.Image.open('Assets/camera-icon.png')
		self.iconCameraBig = ImageTk.PhotoImage(self.iconCameraBig.resize((22,22),Image.ANTIALIAS))
		self.iconVideoBig = PIL.Image.open('Assets/video-icon-b.png')
		self.iconVideoBig = ImageTk.PhotoImage(self.iconVideoBig.resize((22,22),Image.ANTIALIAS))
		self.iconFiles = PIL.Image.open('Assets/files.png')
		self.iconFiles = ImageTk.PhotoImage(self.iconFiles.resize((22,22),Image.ANTIALIAS))

		b = ttk.Button(f,text="Photos...",image=self.iconCameraBig,compound='left',
			command=self.SelectPhotoDirectory,width=7)
		b.grid(row=0,column=0,sticky='W',pady=(5,5))
		ToolTip(b,6000)
		self.PhotoDirLabel = Label(f,foreground='#0000FF',
			text=PreferencesDialog.DefaultPhotoDir,anchor=W)
		self.PhotoDirLabel.grid(row=0,column=1,sticky='EW',padx=10);
		ToolTip(self.PhotoDirLabel,6001)

		b = ttk.Button(f,text="Videos...",image=self.iconVideoBig,compound='left',
			command=self.SelectVideoDirectory,width=7)
		b.grid(row=1,column=0,sticky='W')
		ToolTip(b,6002)
		self.VideoDirLabel = Label(f,foreground='#0000FF',
			text=PreferencesDialog.DefaultVideoDir,anchor=W)
		self.VideoDirLabel.grid(row=1,column=1,sticky='EW',padx=10);
		ToolTip(self.VideoDirLabel,6003)

		b = ttk.Button(f,text="Files...",image=self.iconFiles,compound='left',
			command=self.SelectFilesDirectory,width=7)
		b.grid(row=2,column=0,sticky='W',pady=(5,5))
		ToolTip(b,6004)
		self.FilesDirLabel = Label(f,foreground='#0000FF',
			text=PreferencesDialog.DefaultFilesDir,anchor=W)
		self.FilesDirLabel.grid(row=2,column=1,sticky='EW',padx=10);
		ToolTip(self.FilesDirLabel,6005)

		f = MyLabelFrame(self,'Photo/Video capture formats',1,0)

		ttk.Label(f,text='Photo capture format',padding=(5,5,5,5)) \
			.grid(row=0,column=0,sticky='W')
		self.photoCaptureFormatCombo = Combobox(f,height=15,width=8,
			state='readonly')#,width=15)
		self.photoCaptureFormatCombo.grid(row=0,column=1,sticky='EW')
		self.photoFormats = ['jpeg','png','bmp',
			'gif','yuv','rgb','rgba','bgr','bgra','raw']
		self.photoCaptureFormatCombo['values'] = self.photoFormats
		self.photoCaptureFormatCombo.current( \
			self.photoFormats.index(PreferencesDialog.DefaultPhotoFormat))
		self.photoCaptureFormatCombo.bind('<<ComboboxSelected>>',
			self.photoCaptureFormatChanged)
		ToolTip(self.photoCaptureFormatCombo, msg=6010)
		self.ModFormatParams = ttk.Button(f,text='Params...',
			command=self.ModifyFormatParamPressed,
			underline=0,padding=(5,3,5,3),width=8)
		self.ModFormatParams.grid(row=0,column=2,sticky='W',padx=5)
		ToolTip(self.ModFormatParams, msg=6011)

		ttk.Label(f,text='Video capture format',padding=(5,5,5,5)) \
			.grid(row=1,column=0,sticky='W')
		self.VideoCaptureFormatCombo = Combobox(f,height=15,width=8,
			state='readonly')#,width=15)
		self.VideoCaptureFormatCombo.grid(row=1,column=1,sticky='EW')
		self.videoFormats = ['h264','mjpeg','yuv',
			'rgb','rgba','bgr','bgra']
		self.VideoCaptureFormatCombo['values'] = self.videoFormats
		self.VideoCaptureFormatCombo.current( \
			self.videoFormats.index(PreferencesDialog.DefaultVideoFormat))
		self.VideoCaptureFormatCombo.bind('<<ComboboxSelected>>',
			self.VideoCaptureFormatChanged)
		ToolTip(self.VideoCaptureFormatCombo,6020)
		self.ModVideoFormatParams = ttk.Button(f,text='Params...',
			command=self.ModifyVideoFormatParamPressed,
			underline=0,padding=(5,3,5,3),width=8)
		self.ModVideoFormatParams.grid(row=1,column=2,sticky='W',padx=5)
		ToolTip(self.ModVideoFormatParams,6021)
		# Save / Restore camera settings? This may be a bit to do

		f = MyLabelFrame(self,'Photo/Video naming',2,0)
		Label(f,text='Timestamp format:') \
			.grid(row=0,column=0,sticky='W')
		okCmd = (self.register(self.ValidateTimestamp),'%P')
		self.TimeStamp = MyStringVar(PreferencesDialog.DefaultTimestampFormat)
		e = Entry(f,width=20,validate='all',
			textvariable=self.TimeStamp)
		e.grid(row=0,column=1,sticky='W')
		ToolTip(e,6050)

		image = PIL.Image.open('Assets/help.png')
		self.helpimage = ImageTk.PhotoImage(image.resize((16,16)))
		b = ttk.Button(f,image=self.helpimage,width=10,
			command=self.FormatHelp,padding=(2,2,2,2))
		b.grid(row=0,column=2,padx=5)
		ToolTip(b,6052)

		Label(f,text='Sample timestamp:').grid(row=1,column=0,sticky='W')
		self.TimestampLabel = MyStringVar(datetime.datetime.now() \
			.strftime(PreferencesDialog.DefaultTimestampFormat))
		self.tsl = Label(f,textvariable=self.TimestampLabel,foreground='#0000FF')
		self.tsl.grid(row=1,column=1,columnspan=2,sticky='W')
		ToolTip(self.tsl,6051)
		self.after(1000,self.UpdateTimestamp)

		self.PhotoTimestampVar = MyBooleanVar(PreferencesDialog.PhotoTimestamp)
		self.PhotoTimestamp = Checkbutton(f,text='Include timestamp in photo name',
			variable=self.PhotoTimestampVar, command=self.PhotoTimestampChecked)
		self.PhotoTimestamp.grid(row=2,column=0,columnspan=2,sticky='W')
		ToolTip(self.PhotoTimestamp,6060)

		self.VideoTimestampVar = MyBooleanVar(PreferencesDialog.VideoTimestamp)
		self.VideoTimestamp = Checkbutton(f,text='Include timestamp in video name',
			variable=self.VideoTimestampVar, command=self.VideoTimestampChecked)
		self.VideoTimestamp.grid(row=3,column=0,columnspan=2,sticky='W')
		ToolTip(self.VideoTimestamp,6061)

		e.config(validatecommand=okCmd)
		'''
		Configuration files in python
		There are several ways to do this depending on the file format required.
		ConfigParser [.ini format]
		Write a file like so:
			from ConfigParser import SafeConfigParser
			config = SafeConfigParser()
			config.read('config.ini')
			config.add_section('main')
			config.set('main', 'key1', 'value1')
			config.set('main', 'key2', 'value2')
			config.set('main', 'key3', 'value3')
		'''
		self.photoCaptureFormatChanged(None)
		self.VideoCaptureFormatChanged(None)
	def ChangeDirectory ( self, defaultDir, label, text ):
		oldDir = os.getcwd()
		try:
			os.chdir(defaultDir)
			# I hate that it doesn't allow you set set the initial directory!
			dirname = FileDialog.askdirectory()#self, initialdir="/home/pi/Pictures",
						 #title='Select Photo Directory')
			if dirname:
				defaultDir = dirname
				label.config(text=dirname)
		except:	print ( "Preferences dialog error setting %s directory" % text)
		finally:	os.chdir(oldDir)
	def SelectPhotoDirectory ( self ):
		self.ChangeDirectory(PreferencesDialog.DefaultPhotoDir,self.PhotoDirLabel,"Photo")
	def SelectVideoDirectory ( self ):
		self.ChangeDirectory(PreferencesDialog.DefaultVideoDir,self.VideoDirLabel,"Video")
	def SelectFilesDirectory ( self ):
		self.ChangeDirectory(PreferencesDialog.DefaultFilesDir,self.FilesDirLabel,"Files")
	def photoCaptureFormatChanged ( self, val ):
		photoformat = self.photoCaptureFormatCombo.get()
		PreferencesDialog.DefaultPhotoFormat = photoformat
		self.ModFormatParams.config(state = \
			'normal' if photoformat == 'jpeg' else 'disabled' )
	def ModifyFormatParamPressed ( self ):
		PhotoParamsDialog(self,title='Photo Capture Parameters',
			minwidth=350,minheight=100,okonly=False)
		# Hack. The modal flag is corrupted when calling another dialog?
		if self.data.modal is True:
			self.data._window.grab_set()
			self.data._parent.wait_window(self.data._window)
	def VideoCaptureFormatChanged ( self, val ):
		videoformat = self.VideoCaptureFormatCombo.get()
		PreferencesDialog.DefaultVideoFormat = videoformat
	def ModifyVideoFormatParamPressed ( self ):
		VideoParamsDialog(self,title='Video Capture Parameters',
			okonly=False, data=PreferencesDialog.DefaultFilesDir)
		# Hack. The modal flag is corrupted when calling another dialog?
		if self.data.modal is True:
			self.data._window.grab_set()
			self.data._parent.wait_window(self.data._window)
	def ValidateTimestamp ( self, text ):
		self.CheckTimestamp(text)
		return True
	def CheckTimestamp ( self, text ):
		try:
			self.TimestampLabel.set(datetime.datetime.now().strftime(text))
			self.tsl.config(foreground='#0000FF')
			PreferencesDialog.DefaultTimestampFormat = text
		except:
			self.TimestampLabel.set("Error in format string")
			self.tsl.config(foreground='#FF0000')
	def UpdateTimestamp ( self ):
		self.CheckTimestamp(self.TimeStamp.get())
		self.after(1000,self.UpdateTimestamp)
	def PhotoTimestampChecked ( self ):
		PreferencesDialog.PhotoTimestamp = self.PhotoTimestampVar.get()
	def VideoTimestampChecked ( self ):
		PreferencesDialog.VideoTimestamp = self.VideoTimestampVar.get()
	def FormatHelp ( self ):
		webbrowser.open_new_tab('https://docs.python.org/2/library/datetime.html')
	def SaveChanges ( self ):
		pass

# Handle PiCameraApp Interface preferences
class Interface ( BasicNotepage ):
	def BuildPage ( self ):
		self.iconMonitor = ImageTk.PhotoImage( \
			PIL.Image.open("Assets/computer-monitor.png").resize((64,64),Image.ANTIALIAS))
		Label(self,image=self.iconMonitor).grid(row=0,column=0,sticky='W')

		f = MyLabelFrame(self,'Interface themes',0,1)
		f.columnconfigure(1,weight=1)
		Label(f,text='Set theme').grid(row=0,column=0,sticky='W',pady=(5,5))
		self.themes = Combobox(f,height=10,state='readonly')
		self.themes.grid(row=0,column=1,sticky='W',padx=(10,0))
		self.themes['values'] = Style().theme_names()
		self.themes.set(Style().theme_use())
		self.themes.bind('<<ComboboxSelected>>',self.ThemesSelected)
		ToolTip(self.themes,6100)

		f = MyLabelFrame(self,'Tooltips',1,0,span=2)
		self.ShowTooltips = MyBooleanVar(ToolTip.ShowToolTips)
		self.ShowTipsButton = ttk.Checkbutton(f,text='Show those annoying tooltips',
			variable=self.ShowTooltips, command=self.ShowTooltipsChecked)#,padding=(5,5,5,5))
		self.ShowTipsButton.grid(row=1,column=0,columnspan=2,sticky='W')
		ToolTip(self.ShowTipsButton,6110)

		self.ShowTipNumber = MyBooleanVar(ToolTip.ShowTipNumber)
		self.ShowTipNumButton = ttk.Checkbutton(f,text='Show tip number in tip (debug)',
			variable=self.ShowTipNumber, command=self.ShowTooltipNumChecked,
			padding=(25,5,5,5))
		self.ShowTipNumButton.grid(row=2,column=0,columnspan=2,sticky='W')
		ToolTip(self.ShowTipNumButton,6111)

		ttk.Label(f,text='Delay before tip',padding=(25,0,0,0)).grid(row=3,column=0,sticky='W')
		scale = ttk.Scale(f,value=ToolTip.ShowTipDelay,
			from_=0.1,to=5.0,orient='horizontal',
			command=self.TipDelayChanged)
		scale.grid(row=3,column=1,sticky='W')
		ToolTip(scale,6112)
		self.DelayText = MyStringVar("")
		l = Label(f,textvariable=self.DelayText,foreground='#0000FF')
		l.grid(row=3,column=2,sticky='W')
		ToolTip(l,6113)

		self.TipDelayChanged(ToolTip.ShowTipDelay)	# Force display update
	def ThemesSelected ( self, event ):
		Style().theme_use(self.themes.get())
	def ShowTooltipsChecked ( self ):
		ToolTip.ShowToolTips = self.ShowTooltips.get()
	def ShowTooltipNumChecked ( self ):
		ToolTip.ShowTipNumber = self.ShowTipNumber.get()
	def TipDelayChanged (self, val ):
		ToolTip.ShowTipDelay = float(val)
		self.DelayText.set('{:.1f} sec'.format(float(val)))
	def SaveChanges ( self ):
		pass

# Handle PiCameraApp Other preferences
class Other ( BasicNotepage ):
	pass


