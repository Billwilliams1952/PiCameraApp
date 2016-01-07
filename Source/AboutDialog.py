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
from 	platform import *
try:
	from Tkinter import *
except ImportError:
	from tkinter import *
import 	ttk
from 	ttk import *
import 	tkFont
from tkFont import *
from 	Dialog import *

import PIL
from PIL import Image, ImageTk

NoRequire = False
try:
	from pkg_resources import require
except ImportError:
	print "Cannot import 'require' from 'pkg_resources'"
	NoRequire = True	
	
from NotePage import BasicNotepage
			
class AboutDialog ( Dialog ):
	def BuildDialog ( self ):
		self.MainFrame.columnconfigure(0,weight=1)
		self.MainFrame.rowconfigure(1,weight=1)

		image = PIL.Image.open('Assets/camera.gif')
		photo = ImageTk.PhotoImage(image)
		try:
			img = Label(self.MainFrame,image=photo)
		except:
			print "Do you have the latest Pillow installed?\n\n" + \
				  "sudo apt-get install python-imaging-tk\n" + \
				  "sudo pip uninstall Pillow" \
				  "sudo pip install Pillow\n\n" \
				  "see: github.com/python-pillow/Pillow/issues/322"
		finally:
			img.image = photo
		img.grid(row=0,column=0,sticky='W')
		
		l4 = Label(self.MainFrame,text='PiCameraApp ver 0.1',
			font=('Helvetica',20,'bold italic'), \
			foreground='blue',anchor='center')
		l4.grid(row=0,column=1,sticky='EW')

		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=1,column=0,columnspan=2,sticky='NSEW')
		n.columnconfigure(0,weight=1) 
		n.rowconfigure(0,weight=1)
		
		AboutPage = About(n,None)
		CreditsPage = Credits(n,None)
		LicensePage = License(n,None)

		n.add(AboutPage,text='About',underline=0)
		n.add(CreditsPage,text='Credits',underline=0)
		n.add(LicensePage,text='License',underline=0)
		
# Handle PiCameraApp About
class About ( BasicNotepage ):
	def BuildPage ( self ):
		l = Label(self,text='Demonstrate the PiCamera\'s abilities',
			anchor='center',font=('Helvetica',14),foreground='blue')
		l.grid(row=0,column=0,)
			
		l = Label(self,text='Copyright © 2015',
			anchor='center',font=('Helvetica',12))
		l.grid(row=1,column=0,)
		l = Label(self,text='Bill Williams',
			anchor='center',font=('Helvetica',12))
		l.grid(row=2,column=0,)	
			
		Separator(self,orient='horizontal').grid(row=3,column=0,
			columnspan=2,sticky='NSEW',pady=10)
					
		# See if Windows, Mac, or Linux. Why???? Only on PI for PiCamera!
		txt = win32_ver()[0]
		if txt:
			os = 'Windows OS: %s' % txt
		else:
			txt = mac_ver()[0]
			if txt:
				os = 'Mac OS: %s' % txt
			else:
				txt = linux_distribution()
				if txt[0]:
					os = 'Linux OS: %s %s' % ( txt[0].title(), txt[1] )
				else:
					os = 'Unknown OS'
		l = Label(self,text=os,font=('Helvetica',14))
		l.grid(row=4,column=0,sticky='NSEW')
		l = Label(self,text='Python Version: %s'%python_version())
		l.grid(row=5,column=0,sticky='NSEW')
	
		if NoRequire:
			PiVer = "Picamera ver ??"
		else:
			PiVer = "PiCamera ver %s" % require('picamera')[0].version
	
		l = Label(self,text=PiVer)
		l.grid(row=6,column=0,sticky='NSEW')
				
		s = processor()
		if s:
			txt = 'Processor: %s (%s)' % (processor(), machine())
		else:
			txt = 'Processor: %s' % machine()
		l = Label(self,text=txt)
		l.grid(row=7,column=0,sticky='NSEW')
		l = Label(self,text='Platform: %s'%platform())
		l.grid(row=8,column=0,sticky='NSEW')

# Handle PiCameraApp License	
class License ( BasicNotepage ):
	def BuildPage ( self ):			
		self.sb = Scrollbar(self,orient='vertical')
		self.sb.grid(row=0,column=1,sticky='NS')
		self.text = Text(self,height=30,width=50,wrap='word',
			yscrollcommand=self.sb.set)
		self.text.grid(row=0,column=0,sticky='NSEW')
		self.text.bind("<Key>",lambda e : "break")	# ignore all keypress
		# Note: return "break" from event handler to ignore
		self.sb.config(command=self.text.yview)
		try:
			with open('Assets/gpl.txt') as f: self.text.insert(END,f.read())
		except IOError: 
			self.text.insert(END,"\n\n\n\t\tError reading file 'Assets/gpl.txt'")

# Handle PiCameraApp Credits
class Credits ( BasicNotepage ):
	pass
