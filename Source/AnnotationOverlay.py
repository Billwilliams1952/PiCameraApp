#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  AnnotationOverlay.py
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
	import 	tkFont			as Font
except ImportError:
	import	tkinter.font	as Font

import datetime as dt
from 	Dialog	import *
from 	Mapping	import *
from	NotePage	import *
from	Utils		import *
from	Tooltip	import *
from	NotePage import BasicNotepage
from	PreferencesDialog import *

try:
	import 	picamera
	from 		picamera import *
	import 	picamera.array
except ImportError:
	raise ImportError("You do not seem to have picamera installed")

class AnnotationOverlayDialog ( Dialog ):
	def BuildDialog ( self ):
		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=0,column=0,sticky='NSEW')
		n.columnconfigure(0,weight=1)
		n.rowconfigure(0,weight=1)

		self.Annotation = AnnotationPage(n,camera=self._camera,cancel=self.CancelButton)
		self.Overlay = OverlayPage(n,camera=self._camera,cancel=self.CancelButton)
		#self.EXIF = EXIFPage(n,camera=self._camera,cancel=self.CancelButton)

		n.add(self.Annotation,text='Annotation',underline=0)
		n.add(self.Overlay,text='Overlay',underline=0)
		#n.add(self.EXIF,text='EXIF',underline=0)

	def OkPressed ( self ):
		self.Annotation.SaveChanges()
		self.Overlay.SaveChanges()
		return True

	def CancelPressed ( self ):
		return tkMessageBox.askyesno("Annotation/Overlay","Exit without saving changes?")

class AnnotationPage ( BasicNotepage ):
	UseText = False
	Text = 'Text'
	Timestamp = False
	FrameNum = False
	Textsize = 32
	ColorYValue = 1.0
	UseForeColor = False
	ForeColor = picamera.Color('white')
	UseBackColor = False
	BackColor = None
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		UseText = False
		Text = 'Text'
		Timestamp = False
		FrameNum = False
		Textsize = 32
		ColorYValue = 1.0
		UseForeColor = False
		ForeColor = picamera.Color('white')
		UseBackColor = False
		BackColor = None
	def BuildPage ( self ):
		f = MyLabelFrame(self,'Annotation text',0,0)
		self.EnableAnnotateText = MyBooleanVar(AnnotationPage.UseText)
		self.NoAnnotateTextRadio = MyRadio(f,'None (Default)',False,self.EnableAnnotateText,
			self.AnnotationTextRadio,0,0,'W',tip=400)
		MyRadio(f,'Text:',True,self.EnableAnnotateText,self.AnnotationTextRadio,
					0,1,'W',tip=401)

		self.AddTimestamp = MyBooleanVar(AnnotationPage.Timestamp)
		self.AddTimestampButton = ttk.Checkbutton(f,text='Add Timestamp to overlay',
			variable=self.AddTimestamp,command=self.AddTimestampButtonChecked)
		self.AddTimestampButton.grid(row=2,column=0,padx=5,columnspan=3,sticky='W')
		ToolTip(self.AddTimestampButton, msg=402)

		okCmd = (self.register(self.ValidateAnnotationText),'%P')
		self.AnnotateTextEntry = Entry(f,width=30,validate='all',validatecommand=okCmd)
		self.AnnotateTextEntry.insert(0, AnnotationPage.Text)
		self.AnnotateTextEntry.grid(row=0,column=2,sticky='W')
		ToolTip(self.AnnotateTextEntry, msg=403)

		self.AnnotateFrame = MyBooleanVar(AnnotationPage.FrameNum)
		self.AnnotateFrameButton = ttk.Checkbutton(f,text='Add Frame Number to overlay',
			variable=self.AnnotateFrame,command=self.AnnotateFrameButtonChecked)
		self.AnnotateFrameButton.grid(row=1,column=0,columnspan=3,sticky='W',padx=5)
		ToolTip(self.AnnotateFrameButton,msg=411)

		f1 = ttk.Frame(f)
		f1.grid(row=3,column=0,columnspan=3,sticky='W')
		Label(f1,text='Text size:').grid(row=0,column=0,sticky='W',padx=5,pady=3)
		self.Size = ttk.Label(f1,text='%d' % AnnotationPage.Textsize,
			style='DataLabel.TLabel')
		self.Size.grid(row=0,column=2,sticky='W',padx=5)
		self.AnnotateTextSize = ttk.Scale(f1,from_=6,to=160,length=175,
				command=self.AnnotateTextSizeChanged,orient='horizontal')
		self.AnnotateTextSize.grid(row=0,column=1,sticky='W')
		self.AnnotateTextSize.set(AnnotationPage.Textsize)
		ToolTip(self.AnnotateTextSize, msg=404)

		f = MyLabelFrame(self,'Foreground / background colors',2,0)#,'NEWS',5)
		b = MyBooleanVar(AnnotationPage.UseBackColor)
		self.NoBackColorRadio = MyRadio(f,'Background (None default)',False,b,
			self.AnnotationBackgroundColor,1,0,'W',tip=405)
		MyRadio(f,'Set:',True,b,self.AnnotationBackgroundColor,1,1,'W',tip=406)
		image = PIL.Image.open('Assets/ColorPicker1.png')
		self.colorimage = ImageTk.PhotoImage(image.resize((16,16),Image.ANTIALIAS))
		self.chooseBackColor = ttk.Button(f,text='Color',image=self.colorimage,
			command=self.ChooseBackcolorClick,width=7,padding=(5,5,5,5))
		self.chooseBackColor.grid(row=1,column=2,sticky='W')
		ToolTip(self.chooseBackColor,407)

		b = MyBooleanVar(AnnotationPage.UseForeColor)
		self.WhiteDefaultRadio = MyRadio(f,'Foreground (White default)',False,b,
			self.AnnotationForegroundColor,0,0,'W',tip=408)
		MyRadio(f,'Set:',True,b,self.AnnotationForegroundColor,0,1,'W',tip=409)
		self.Ylabel = ttk.Label(f,text='Y: %f' % AnnotationPage.ColorYValue,
			style='DataLabel.TLabel')
		self.Ylabel.grid(row=0,column=3,sticky='W',padx=5)
		self.Ycolor = ttk.Scale(f,from_=0.0,to=1.0,orient='horizontal',
							command=self.YValueChanged)
		self.Ycolor.grid(row=0,column=2,sticky='W',pady=5)
		self.Ycolor.set(AnnotationPage.ColorYValue)
		ToolTip(self.Ycolor,410)

		self.AnnotationBackgroundColor(False)
		self.AnnotationForegroundColor(False)
		self.BackColor = picamera.Color('Black')
	def AnnotationTextRadio ( self, EnableAddText ):
		if EnableAddText:
			self.AnnotateTextEntry.config(state='normal')
			self.AnnotateTextEntry.focus_set()
			state = '!disabled'
			self.camera.annotate_text = self.AnnotateTextEntry.get()
		else:
			state = 'disabled'
			self.camera.annotate_text = ''
			self.AnnotateTextEntry.config(state=state)
		AnnotationPage.UseText = EnableAddText
	def ValidateAnnotationText ( self, TextToAdd ):
		# A Hack because I want to continuously update the timestamp
		# if displayed
		if self.EnableAnnotateText.get() is False: TextToAdd = ""
		AnnotationPage.Text = TextToAdd
		if self.AddTimestamp.get():
			try:	# in case a formatting error...
				t = dt.datetime.now().strftime(PreferencesDialog.DefaultTimestampFormat)
			except:
				t = "Bad format" # Should never get here...
			if TextToAdd == "":	TextToAdd = t
			else:						TextToAdd = TextToAdd + " (" + t + ")"
		self.camera.annotate_text = TextToAdd
		return True
	def AnnotateFrameButtonChecked ( self ):
		self.camera.annotate_frame_num = self.AnnotateFrame.get()
		AnnotationPage.AnnotateFrameNum = self.AnnotateFrame.get()
		self.ValidateAnnotationText(self.AnnotateTextEntry.get())
		AnnotationPage.FrameNum = self.AnnotateFrame.get()
	def AddTimestampButtonChecked ( self ):
		AnnotationPage.Timestamp = self.AddTimestamp.get()
		self.ValidateAnnotationText(self.AnnotateTextEntry.get())
		if self.AddTimestamp.get():
			self.after(1000,self.AddTimestampButtonChecked)
	def AnnotationBackgroundColor ( self, AddColor ):
		if AddColor:
			self.camera.annotate_background = self.BackColor
			self.chooseBackColor.config(state='!disabled')
			self.chooseBackColor.focus_set()
		else:
			self.camera.annotate_background = None
			self.chooseBackColor.config(state='disabled')
	def ChooseBackcolorClick ( self ):
		# pass a String for the color - not a Value!
		result = askcolor(parent=self,color=str(self.BackColor),
				 title='Annotation Background color')
		# [0] is (R,G,B) tuple, [1] is hex value of color
		if result[0] == None: return 	# Cancel
		self.BackColor = picamera.Color(result[1])
		self.camera.annotate_background = picamera.Color(result[1])
	def AnnotationForegroundColor ( self, AddColor ):
		if AddColor:
			self.camera.annotate_foreground = \
				picamera.Color(y=float(self.Ycolor.get()), u=0, v=0)
			self.Ycolor.state(['!disabled'])
			self.Ycolor.focus_set()
		else:
			self.Ycolor.state(['disabled'])
			self.camera.annotate_foreground = picamera.Color('white')
	def YValueChanged ( self, val ):
		self.camera.annotate_foreground = picamera.Color(y=float(val), u=0, v=0)
		AnnotationPage.YValue = float(val)
		self.Ylabel.config(text='Y: %.2f' % float(val))
	def AnnotateTextSizeChanged ( self, newVal ):
		self.camera.annotate_text_size = int(float(newVal))
		self.Size.config(text='%d' % int(float(newVal)))
		AnnotationPage.Textsize = int(float(newVal))
		self.AnnotateTextSize.focus_set()
	def SaveChanges ( self ):
		pass

class OverlayPage ( BasicNotepage ):
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		pass
	def BuildPage ( self ):
		Label(self,text="NOTHING HERE YET!!").grid(row=0,column=0,sticky='W');
	def SaveChanges ( self ):
		pass
