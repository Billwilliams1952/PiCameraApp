#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  VideoParams.py
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
	import 	tkMessageBox as MessageBox
except ImportError:
	import	tkinter.messagebox as MessageBox
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

import	os

from 	Dialog	import *
from 	Mapping	import *
from	NotePage	import *
from	Utils		import *
from	Tooltip	import *
from	NotePage import BasicNotepage

# Handle all Video parameters
'''
Thanks to: picamera.readthedocs.io/en/release-1.13/api_camera.html
Certain formats accept additional options which can be specified as
keyword arguments. The 'h264' format accepts the following additional
options:

profile - The H.264 profile to use for encoding. Defaults to ‘high’,
but can be one of ‘baseline’, ‘main’, ‘extended’, ‘high’, or ‘constrained’.

level - The H.264 level to use for encoding. Defaults to ‘4’, but can
be any H.264 level up to ‘4.2’.

intra_period - The key frame rate (the rate at which I-frames are
inserted in the output). Defaults to None, but can be any 32-bit
integer value representing the number of frames between successive
I-frames. The special value 0 causes the encoder to produce a single
initial I-frame, and then only P-frames subsequently. Note that
split_recording() will fail in this mode.

intra_refresh - The key frame format (the way in which I-frames will be
inserted into the output stream). Defaults to None, but can be one
of ‘cyclic’, ‘adaptive’, ‘both’, or ‘cyclicrows’.

inline_headers - When True, specifies that the encoder should output
SPS/PPS headers within the stream to ensure GOPs (groups of pictures)
are self describing. This is important for streaming applications
where the client may wish to seek within the stream, and enables the
use of split_recording(). Defaults to True if not specified.

sei - When True, specifies the encoder should include
“Supplemental Enhancement Information” within the output stream.
Defaults to False if not specified.

sps_timing - When True the encoder includes the camera’s framerate in
the SPS header. Defaults to False if not specified.

motion_output - Indicates the output destination for motion vector
estimation data. When None (the default), motion data is not output.
Otherwise, this can be a filename string, a file-like object, or a
writeable buffer object (as with the output parameter).

All encoded formats accept the following additional options:

bitrate - The bitrate at which video will be encoded. Defaults to
17000000 (17Mbps) if not specified. The maximum value depends on the
selected H.264 level and profile. Bitrate 0 indicates the encoder
should not use bitrate control (the encoder is limited by the quality
only).

quality - Specifies the quality that the encoder should attempt to
maintain. For the 'h264' format, use values between 10 and 40 where 10
is extremely high quality, and 40 is extremely low (20-25 is usually
a reasonable range for H.264 encoding). For the mjpeg format, use JPEG
quality values between 1 and 100 (where higher values are higher
quality). Quality 0 is special and seems to be a “reasonable quality”
default.

quantization - Deprecated alias for quality.
'''

from Mapping import *
from PreferencesDialog import *

class VideoParamsDialog ( Dialog ):
	def BuildDialog ( self ):
		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=0,column=0,sticky='NSEW')
		#n.columnconfigure(0,weight=1)
		#n.rowconfigure(0,weight=1)

		self.H264page = H264(n,cancel=self.CancelButton,ok=self.OkButton,
			colconfig=False,data=self.data)
		self.AllFormatspage = AllFormats(n,cancel=self.CancelButton,
			ok=self.OkButton,colconfig=False)

		n.add(self.H264page,text='H264',underline=0)
		n.add(self.AllFormatspage,text='All formats',underline=0)

	def OkPressed ( self ):
		self.H264page.SaveChanges()
		self.AllFormatspage.SaveChanges()
		return True

	def CancelPressed ( self ):
		return MessageBox.askyesno("Video Params","Exit without saving changes?")

class H264 ( BasicNotepage ):
	Profile = 'high'
	Level = '4'
	IntraPeriod = None		# or a 32 bit integer, 0 is special
	IntraRefresh = None		# Need to check for None and select text
	InlineHeaders = True
	SEI = False
	SPSTiming = False
	MotionOutput = None		# or a filename
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		Profile = 'high'
		Level = '4'
		IntraPeriod = None	# or integer between 0 to 32767 ???
		IntraRefresh = None
		InlineHeaders = True
		SEI = False
		SPSTiming = False
		MotionOutput = None
	def BuildPage ( self ):
		Label(self,text="Profile:").grid(row=0,column=0,sticky='W');
		self.Profiles = Combobox(self,state='readonly',width=12)
		self.Profiles.bind('<<ComboboxSelected>>',self.SomethingChanged)
		self.Profiles.grid(row=0,column=1,sticky='W',columnspan=2,pady=3)
		self.profileList = ['high (default)','baseline','main','extended','constrained']
		self.Profiles['values'] = self.profileList
		if H264.Profile == 'high':
			self.Profiles.current(0)
		else:
			self.Profiles.current(self.profileList.index(H264.Profile))
		ToolTip(self.Profiles,3000)

		Label(self,text="Level:").grid(row=1,column=0,sticky='W');
		self.Levels = Combobox(self,state='readonly',width=12)
		self.Levels.bind('<<ComboboxSelected>>',self.SomethingChanged)
		self.Levels.grid(row=1,column=1,sticky='W',columnspan=2)
		self.LevelsList = ['1','1b','1.1','1.2','1.3','2','2.1',
								 '2.2', '3', '3.1', '3.2', '4 (default)','4.1','4.2']
		self.Levels['values'] = self.LevelsList
		if H264.Level == '4':
			self.Levels.current(11)
		else:
			self.Levels.current(self.LevelsList.index(H264.Level))
		ToolTip(self.Levels,3001)

		f = MyLabelFrame(self,"Intra-Period:",row=2,col=0,span=3,pad=(5,10,5,10));
		self.FrameCount = StringVar()
		self.FrameCount.set('')
		okCmd = (self.register(self.ValidateFrameCount),'%P')
		Label(f,text="Count:").grid(row=0,column=2,sticky='W',padx=5);
		self.FrameCountEdit = Entry(f,textvariable=self.FrameCount,width=6,
			validate='all',validatecommand=okCmd)
		self.FrameCountEdit.grid(row=0,column=3,sticky='W')
		ToolTip(self.FrameCountEdit,3003)
		self.IntraPeriod = Combobox(f,state='readonly',width=33)
		self.IntraPeriod.bind('<<ComboboxSelected>>',self.IntraPeriodChanged)
		self.IntraPeriod.grid(row=0,column=0,sticky='W',columnspan=2)
		self.IntraPeriodList = ['None (default)','Initial I Frame, then P frames',
										'Specify framecount between each I frame']
		self.IntraPeriod['values'] = self.IntraPeriodList
		# Check if None, select 0, else select matching text
		self.FrameCount.set('1')
		if H264.IntraPeriod == None:
			self.IntraPeriod.current(0)
		elif H264.IntraPeriod == 0:
			self.IntraPeriod.current(1)
		else:
			self.IntraPeriod.current(2)
			self.FrameCount.set(str(H264.IntraPeriod))
		ToolTip(self.IntraPeriod,3002)
		# Check if None (select radio), or 0, (select radio)
		# or put integer value into edit field

		Label(self,text="Intra-Refresh:").grid(row=3,column=0,sticky='W')
		self.IntraRefresh = Combobox(self,state='readonly',width=12)
		self.IntraRefresh.bind('<<ComboboxSelected>>',self.SomethingChanged)
		self.IntraRefresh.grid(row=3,column=1,sticky='W',columnspan=2)
		self.IntraRefreshList = ['None (default)','cyclic', 'adaptive',
										 'both', 'cyclicrows']
		self.IntraRefresh['values'] = self.IntraRefreshList
		# Check if None, select 0, else select matching text
		if H264.IntraRefresh == None:
			self.IntraRefresh.current(0)
		else:
			self.IntraRefresh.current(self.IntraRefreshList.index(H264.IntraRefresh))
		ToolTip(self.IntraRefresh,3004)

		Label(self,text="Inline Headers:").grid(row=4,column=0,sticky='W')
		self.InlineHeaders = MyBooleanVar(H264.InlineHeaders)
		MyRadio(self,"On (default)",True,self.InlineHeaders,self.SomethingChanged,4,1,'W',
			tip=3005)
		MyRadio(self,"Off",False,self.InlineHeaders,self.SomethingChanged,4,2,'W',
			tip=3006)

		Label(self,text="SEI:").grid(row=5,column=0,sticky='W');
		self.SEI = MyBooleanVar(H264.SEI)
		MyRadio(self,"On",True,self.SEI,self.SomethingChanged,5,1,'w',
			tip=3007)
		MyRadio(self,"Off (default)",False,self.SEI,self.SomethingChanged,5,2,'w',
			tip=3008)

		Label(self,text="SPS Timing:").grid(row=6,column=0,sticky='W');
		self.SPSTiming = MyBooleanVar(H264.SPSTiming)
		MyRadio(self,"On",True,self.SPSTiming,self.SomethingChanged,6,1,'W',
			tip=3009)
		MyRadio(self,"Off (default)",False,self.SPSTiming,self.SomethingChanged,6,2,'W',
			tip=3010)

		Label(self,text="Motion Output:").grid(row=7,column=0,sticky='W');
		# Check if None, select radio, else place filename text field.
		# Have a button to select file
		self.MotionOutputFile = MyBooleanVar(H264.MotionOutput is None)
		r = MyRadio(self,"None",True,self.MotionOutputFile,self.MotionOutputChanged,7,1,'W',
			tip=3011)
		MyRadio(self,"To file:",False,self.MotionOutputFile,self.MotionOutputChanged,7,2,'W',
			tip=3012)
		self.SelectMotionOutputFile = ttk.Button(self,text='File...',
			command=self.SelectMotionOutputFilePressed,
			underline=0,padding=(5,3,5,3),width=8)
		self.SelectMotionOutputFile.grid(row=7,column=3,sticky='W',padx=5)
		ToolTip(self.SelectMotionOutputFile,3013)
		if H264.MotionOutput == None:
			self.MotionOutputFilename = ""
		else:
			self.MotionOutputFilename = H264.MotionOutput
		self.MotionFilename = ttk.Label(self,text=self.MotionOutputFilename,
			style='DataLabel.TLabel')
		self.MotionFilename.grid(row=8,column=2,sticky='W')
		ToolTip(self.MotionFilename,3014)

		self.IntraPeriodChanged(None)
		self.MotionOutputChanged(None)

	def IntraPeriodChanged ( self, val ):
		if self.IntraPeriod.current() == 2:
			self.FrameCountEdit.config(state='normal')
			self.ValidateFrameCount(self.FrameCount.get())
			self.FrameCountEdit.focus_set()
		else: self.FrameCountEdit.config(state='disabled')
		self.SomethingChanged(None)
	def ValidateFrameCount ( self, textToValidate ):
		try:		val = int(textToValidate)
		except:	return False
		self.SomethingChanged(None)
		return True
	def MotionOutputChanged ( self, val ):
		self.SelectMotionOutputFile.config(state='disabled' \
			if self.MotionOutputFile.get() else 'normal')
		self.SomethingChanged(None)
	def SelectMotionOutputFilePressed ( self ):
		if self.MotionOutputFilename == "":
			path = self.data
			filename = "Motion.mot"
		else:
			drive, path = os.path.splitdrive(self.MotionOutputFilename)
			path, filename = os.path.split(path)
		path = FileDialog.asksaveasfilename(title="Save motion data",
			initialdir=path,initialfile=filename,
			filetypes=[('Motion files', '.mot')] )
		if path:
			self.MotionOutputFilename = path
			self.MotionFilename.config(text=path)
			self.SomethingChanged(None)
	def SaveChanges ( self ):
		H264.Profile = self.Profiles.get().replace('(default)','').strip()
		H264.Level = self.Levels.get().replace('(default)','').strip()

		H264.IntraPeriod = self.IntraPeriod.current()
		if H264.IntraPeriod == 0:	H264.IntraPeriod = None
		elif H264.IntraPeriod == 1: H264.IntraPeriod = 0
		else:
			try:		val = int(self.FrameCount.get())
			except:	val = 1			# Force a good number. Not the best...
			if val < 1:	val = 1
			H264.IntraPeriod = val

		H264.IntraRefresh = self.IntraRefresh.current()
		if H264.IntraRefresh == 0: H264.IntraRefresh = None
		else:
			H264.IntraRefresh = self.IntraRefreshList[H264.IntraRefresh]

		H264.SEI = self.SEI.get()
		H264.SPSTiming = self.SPSTiming.get()
		H264.InlineHeaders = self.InlineHeaders.get()

		if self.MotionOutputFile.get() is True or not self.MotionOutputFilename:
			H264.MotionOutput = None
		else:
			H264.MotionOutput = self.MotionOutputFilename

class AllFormats ( BasicNotepage ):
	BitRate = 17000000	# what are valid numbers?
	QualityH264 = 0 # 'reasonable' quality - H264 10-40 10 high, 20-25 ok
	QualityOther = 0 # 'reasonable' quality - MJPEG 1 to 100, 100 highest
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		BitRate = 17000000
		QualityH264 = 0
		QualityOther = 0
	def BuildPage ( self ):
		Label(self,text="Bitrate:").grid(row=0,column=0,sticky='W');
		Label(self,text="Quality:").grid(row=1,column=0,sticky='W');
	def SaveChanges ( self ):
		pass

