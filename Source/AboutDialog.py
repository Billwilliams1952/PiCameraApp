# -*- coding: iso-8859-15 -*-
'''
AboutDialog.py
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
from	platform	import *
try:
	from Tkinter import *
except ImportError:
	from tkinter import *
try:
	import 	ttk
	from 		ttk import *
except ImportError:
	from tkinter import ttk

from	Dialog	import *
from	Utils		import *
from	Mapping	import *

import PIL
from PIL import Image, ImageTk, ExifTags

NoRequire = False
try:
	from pkg_resources import require
except ImportError:
	print ( "Cannot import 'require' from 'pkg_resources'" )
	NoRequire = True

from NotePage import BasicNotepage

#
# General About Dialog.
#
class AboutDialog ( Dialog ):
	def BuildDialog ( self ):
		#self.MainFrame.columnconfigure(0,weight=1)
		#self.MainFrame.rowconfigure(1,weight=1)

		image = PIL.Image.open('Assets/PiCamera.png')
		image = image.resize((50,106), Image.ANTIALIAS)
		photo = ImageTk.PhotoImage(image)
		img = Label(self.MainFrame,image=photo)
		img.image = photo
		img.grid(row=0,column=0,sticky='W')

		l4 = Label(self.MainFrame,text='PiCamera ver 0.2  ',
			font=('Helvetica',20,'bold italic'), \
			foreground='blue') #,anchor='center')
		l4.grid(row=0,column=1,sticky='W') #'EW')

		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=1,column=0,columnspan=2,sticky='NSEW')
		n.columnconfigure(0,weight=1)
		n.rowconfigure(0,weight=1)

		AboutPage = About(n, camera=self._camera)
		LicensePage = License(n)
		CreditsPage = Credits(n)

		n.add(AboutPage,text='About',underline=0)
		n.add(LicensePage,text='License',underline=0)
		n.add(CreditsPage,text='Credits',underline=0)

# Handle PiCameraApp About
class About ( BasicNotepage ):
	def BuildPage ( self ):
		Label(self,text='PiCamera Application',
			anchor='center',font=('Helvetica',14),foreground='blue') \
			.grid(row=0,column=0,)

		Label(self,text='Copyright (C) 2015 - 2018',
			anchor='center',font=('Helvetica',12)).grid(row=1,column=0,)
		Label(self,text='Bill Williams (github.com/Billwilliams1952/)',
			anchor='center',font=('Helvetica',12)).grid(row=2,column=0,)

		Separator(self,orient='horizontal').grid(row=3,column=0,
			columnspan=2,sticky='NSEW',pady=10)

		rev = self.camera.revision
		if rev == "ov5647": camType = "V1"
		elif rev == "imx219" : camType = "V2"
		else: camType = "Unknown"
		Label(self,text="Camera revision: " + rev + " (" + camType + \
			" module)",font=('Helvetica',14)).grid(row=4,column=0,sticky='NSEW')

		# Only on PI for PiCamera!
		txt = linux_distribution()
		if txt[0]:
			os = 'Linux OS: %s %s' % ( txt[0].title(), txt[1] )
		else:
			os = 'Unknown Linux OS'
		Label(self,text=os).grid(row=5,column=0,sticky='NSEW')

		l = Label(self,text='Python version: %s' % python_version())
		l.grid(row=6,column=0,sticky='NSEW')

		if NoRequire:
			PiVer = "Picamera library version unknown"
			PILVer = "Pillow (PIL) library version unknown"
			RPIVer = "GPIO library version unknown"
		else:
			PiVer = "PiCamera library version %s" % require('picamera')[0].version
			PILVer = "Pillow (PIL) library version %s" % require('Pillow')[0].version
			RPIVer = "GPIO library version %s" % require('rpi.gpio')[0].version

		Label(self,text=PiVer).grid(row=7,column=0,sticky='NSEW')
		Label(self,text=PILVer).grid(row=8,column=0,sticky='NSEW')
		Label(self,text=RPIVer).grid(row=9,column=0,sticky='NSEW')
		s = processor()
		if s:
			txt = 'Processor type: %s (%s)' % (processor(), machine())
		else:
			txt = 'Processor type: %s' % machine()
		Label(self,text=txt).grid(row=10,column=0,sticky='NSEW')
		Label(self,text='Platform: %s' % platform()).grid(row=11, \
				column=0,sticky='NSEW')

# Handle GPL License
class License ( BasicNotepage ):
	def BuildPage ( self ):
		self.sb = Scrollbar(self,orient='vertical')
		self.sb.grid(row=0,column=1,sticky='NEWS')
		self.text = Text(self,height=15,width=50,wrap='word',
			yscrollcommand=self.sb.set)
		self.text.grid(row=0,column=0,sticky='NEWS')
		self.text.bind("<Key>",lambda e : "break")	# ignore all keypress
		# Note: return "break" from event handler to ignore
		self.sb.config(command=self.text.yview)
		try:
			with open('Assets/gpl.txt') as f: self.text.insert(END,f.read())
		except IOError:
			self.text.insert(END,"\n\n\n\t\tError reading file 'Assets/gpl.txt'")

# Handle Credits
class Credits ( BasicNotepage ):
	def BuildPage ( self ):
		f = MyLabelFrame(self,'Thanks To',0,0)
		string = \
		"Tooltip implementation courtesy of:\n" \
		"    code.activestate.com/recipes/576688-tooltip-for-tkinter/\n" \
		"Tooltip information courtesy of:\n" \
		"    picamera.readthedocs.io/en/release-1.13/api_camera.html\n" \
		"Various free icons courtesy of:\n" \
		"    iconfinder.com/icons/ and icons8.com/icon/\n" \
		""
		Label(f,text=string,style='DataLabel.TLabel').grid(row=0,column=0,sticky='NSEW')
