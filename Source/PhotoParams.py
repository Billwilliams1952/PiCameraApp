#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  PhotoParams.py
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
	import 	tkFileDialog
except ImportError:
	import	tkinter.filedialog
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

from 	Dialog	import *
from 	Mapping	import *
from	NotePage	import *
from	Utils		import *
from	Tooltip	import *

# Handle all Photo parameters
'''
Certain file formats accept additional options which can be specified as
keyword arguments. Currently, only the 'jpeg' encoder accepts additional
 options, which are:

quality	Defines the quality of the JPEG encoder as an integer ranging
			from 1 to 100. Defaults to 85. Please note that JPEG quality is not a
			percentage and definitions of quality vary widely.
restart	Defines the restart interval for the JPEG encoder as a number
			of JPEG MCUs. The actual restart interval used will be a multiple of the
			number of MCUs per row in the resulting image.
thumbnail	Defines the size and quality of the thumbnail to embed in
			the Exif metadata. Specifying None disables thumbnail generation.
			Otherwise, specify a tuple of (width, height, quality).
			Defaults to (64, 48, 35).
bayer		If True, the raw bayer data from the camera’s sensor is included
			in the Exif metadata.
'''

class PhotoParamsDialog ( Dialog ):
	def BuildDialog ( self ):
		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=0,column=0,sticky='NSEW')
		#n.columnconfigure(0,weight=1)
		#n.rowconfigure(0,weight=1)

		self.JPEGpage = JPEG(n,cancel=self.CancelButton,ok=self.OkButton)
		self.OtherFormatspage = OtherFormats(n,cancel=self.CancelButton,
			ok=self.OkButton)

		n.add(self.JPEGpage,text='JPEG',underline=0)
		n.add(self.OtherFormatspage,text='Other formats',underline=0)

	def OkPressed ( self ):
		self.JPEGpage.SaveChanges()
		self.OtherFormatspage.SaveChanges()
		return True

	def CancelPressed ( self ):
		return MessageBox.askyesno("Photo Params","Exit without saving changes?")

class JPEG ( BasicNotepage ):
	Quality = 85
	Restart = None
	Thumbnail = (64, 48, 40) # (width, height, quality) or None
	Bayer = False
	IncludeEXIF = True
	UserComment = ""
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		Quality = 85
		Restart = None
		Thumbnail = (64, 48, 40)  # or None or (width, height, quality)
		Bayer = False
		IncludeEXIF = True
		UserComment = ""
	def BuildPage ( self ):
		frame = MyLabelFrame(self, "JPEG Parameters", 0, 0)
		Label(frame,text="Quality:").grid(row=0,column=0,sticky='W');
		self.Quality = ttk.Scale(frame,from_=1,to=100,orient='horizontal')
		self.Quality.grid(row=0,column=1,sticky='W',pady=5)
		self.Quality.set(JPEG.Quality)
		ToolTip(self.Quality,2000)

		self.QualityAmt = IntVar()
		self.QualityAmt.set(JPEG.Quality)
		l = ttk.Label(frame,textvariable=self.QualityAmt,style='DataLabel.TLabel')
		l.grid(row=0,column=2,sticky='W')
		ToolTip(l,2001)
		# NOW enable callback - else we get an error on self.QualityAmt
		self.Quality.config(command=self.QualityChanged)

		Label(frame,text="Restart:").grid(row=1,column=0,sticky='W');
		l = Label(frame,text="Unclear what to do here!")
		l.grid(row=1,column=1,columnspan=2,sticky='W');
		ToolTip(l,2010)

		f = ttk.Frame(frame)
		f.grid(row=2,column=0,columnspan=3,sticky='EW')

		Label(f,text="Thumbnail:").grid(row=0,column=0,sticky='W');
		self.ThumbnailNone = MyBooleanVar(JPEG.Thumbnail == None)
		r = MyRadio(f,"None",True,self.ThumbnailNone,self.ThumbnailChanged,
			0,1,'W',tip=2015)
		MyRadio(f,"Set size/quality",False,self.ThumbnailNone,self.ThumbnailChanged,
			0,2,'W',tip=2020)

		self.ThumbnailEditFrame = ttk.Frame(f,padding=(15,0,0,0))
		self.ThumbnailEditFrame.grid(row=1,column=0,columnspan=3,sticky='EW')
		Label(self.ThumbnailEditFrame,text="Width:").grid(row=0,column=0,sticky='E');
		self.WidthCombo = Combobox(self.ThumbnailEditFrame,state='readonly',width=3)
		self.WidthCombo.bind('<<ComboboxSelected>>',self.SomethingChanged)
		self.WidthCombo.grid(row=0,column=1,sticky='W')
		self.WidthComboList = [16,32,48,64,80,96,112,128]
		self.WidthCombo['values'] = self.WidthComboList
		if JPEG.Thumbnail is None:
			self.WidthCombo.current(0)
		else:
			self.WidthCombo.current(int(JPEG.Thumbnail[0]/16) - 1)
		ToolTip(self.WidthCombo,2021)

		ttk.Label(self.ThumbnailEditFrame,text="Height:",padding=(5,0,0,0)).grid(row=0,column=2,sticky='E');
		self.HeightCombo = Combobox(self.ThumbnailEditFrame,state='readonly',width=3)
		self.HeightCombo.bind('<<ComboboxSelected>>',self.SomethingChanged)
		self.HeightCombo.grid(row=0,column=3,sticky='W')
		self.HeightCombo['values'] = self.WidthComboList
		if JPEG.Thumbnail is None:
			self.HeightCombo.current(0)
		else:
			self.HeightCombo.current(int(JPEG.Thumbnail[1]/16) - 1)
		ToolTip(self.HeightCombo,2022)

		ttk.Label(self.ThumbnailEditFrame,text="Quality:",padding=(5,0,0,0)).grid(row=0,column=4,sticky='E');
		self.QualityCombo = ttk.Combobox(self.ThumbnailEditFrame,state='readonly',width=3)
		self.QualityCombo.bind('<<ComboboxSelected>>',self.SomethingChanged)
		self.QualityCombo.grid(row=0,column=5,sticky='W')
		self.QualityComboList = [30,40,50,60,70,80,90]
		self.QualityCombo['values'] = self.QualityComboList
		if JPEG.Thumbnail is None:
			self.QualityCombo.current(0)
		else:
			self.QualityCombo.current(int((JPEG.Thumbnail[2]-30) / 10))
		ToolTip(self.QualityCombo,2023)

		Label(f,text="Bayer:").grid(row=2,column=0,sticky='W');
		self.Bayer = MyBooleanVar(JPEG.Bayer)
		MyRadio(f,"Off (default)",False,self.Bayer,self.SomethingChanged,
			2,1,'W',tip=2030)
		MyRadio(f,"On",True,self.Bayer,self.SomethingChanged,2,2,'W',
			tip=2031)

		frame = MyLabelFrame(self, "EXIF Metadata", 1, 0)
		self.AddExifBoolean = MyBooleanVar(JPEG.IncludeEXIF)
		self.AddExifButton = ttk.Checkbutton(frame,
			text='Add EXIF metadata when saving photo',
			variable=self.AddExifBoolean,
			command=lambda e=None:self.SomethingChanged(e))
		self.AddExifButton.grid(row=0,column=0,columnspan=2,sticky='W',padx=5)
		ToolTip(self.AddExifButton,msg=2100)

		Label(frame,text="Add a user comment to the EXIF metadata") \
			.grid(row=1,column=0,sticky='W')
		self.AddCommentStr = MyStringVar(JPEG.UserComment)
		okCmd = (self.register(self.SomethingChanged),'%P')
		e = Entry(frame,textvariable=self.AddCommentStr,validate='key',
			validatecommand=okCmd)
		e.grid(row=2,column=0,columnspan=2,sticky='EW')
		ToolTip(e,msg=2110)

		self.ThumbnailChanged(None)
	def QualityChanged ( self, val ):
		self.QualityAmt.set(int(float(val)))
		self.SomethingChanged(None)
	def ThumbnailChanged ( self, val ):
		if self.ThumbnailNone.get() is True:
			self.ThumbnailEditFrame.grid_remove()
		else:
			self.ThumbnailEditFrame.grid()
		self.SomethingChanged(None)
	def SaveChanges ( self ):
		JPEG.Quality = self.QualityAmt.get()
		JPEG.Bayer = self.Bayer.get()
		JPEG.IncludeEXIF = self.AddExifBoolean.get()
		JPEG.UserComment = self.AddCommentStr.get()
		if self.ThumbnailNone.get() == True:
			JPEG.Thumbnail = None
		else:
			JPEG.Thumbnail = ( \
				int(self.WidthCombo.get()) ,
				int(self.HeightCombo.get()) ,
				int(self.QualityCombo.get()) )

class OtherFormats ( BasicNotepage ):
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		pass
	def SaveChanges ( self ):
		pass

