 # -*- coding: iso-8859-15 -*-
'''
CameraApplication.py
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

from PIL import Image, ImageTk

NoRequire = False
try:
	from pkg_resources import require
except ImportError:
	print "Cannot import 'require' from 'pkg_resources'"
	NoRequire = True	

class AboutDialog ( Dialog ):
	def Build ( self ):
		self.MainFrame.columnconfigure(0,weight=1)
		self.MainFrame.rowconfigure(1,weight=1)

		image = Image.open('Assets/camera.gif') #.resize((64,64),Image.ANTIALIAS)
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
		
		l4 = Label(self.MainFrame,text='PiCameraApp ver 0.1',font=('Helvetica',22,'bold italic'), \
			foreground='blue',anchor='e')
		l4.grid(row=0,column=1,sticky='NSEW',pady=10)

		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=1,column=0,columnspan=2,sticky='NSEW')
		n.columnconfigure(0,weight=1) 
		n.rowconfigure(0,weight=1)
		
		##-------------------- About -------------------------------
		f1 = Frame(n,padding=(5,30,5,30))
		f1.grid(row=0,column=0,sticky='NEWS')
		f1.columnconfigure(0,weight=1)
		l = Label(f1,text='Demonstrate the PiCamera\'s abilities',
			anchor='center',font=('Helvetica',14),foreground='blue')
		l.grid(row=0,column=0,)
			
		l = Label(f1,text='Copyright © 2015',
			anchor='center',font=('Helvetica',12))
		l.grid(row=1,column=0,)
		l = Label(f1,text='Bill Williams',
			anchor='center',font=('Helvetica',12))
		l.grid(row=2,column=0,)	
			
		Separator(f1,orient='horizontal').grid(row=3,column=0,
			columnspan=2,sticky='NSEW',pady=10)
					
		# see if Windows, Mac, or Linux
		# Why???? Only on PI for PiCamera!
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
		l = Label(f1,text=os,font=('Helvetica',14))
		l.grid(row=4,column=0,sticky='NSEW')
		l = Label(f1,text='Python Version: %s'%python_version())
		l.grid(row=5,column=0,sticky='NSEW')

		if NoRequire:
			PiVer = "Picamera ver ??"
		else:
			PiVer = "PiCamera ver %s" % require('picamera')[0].version

		l = Label(f1,text=PiVer)
		l.grid(row=6,column=0,sticky='NSEW')
				
		s = processor()
		if s:
			txt = 'Processor: %s (%s)' % (processor(), machine())
		else:
			txt = 'Processor: %s' % machine()
		l = Label(f1,text=txt)
		l.grid(row=7,column=0,sticky='NSEW')
		l = Label(f1,text='Platform: %s'%platform())
		l.grid(row=8,column=0,sticky='NSEW')
		#----------------------------------------------------------		
		
		##------------------ Credits -------------------------------
		f2 = Frame(n,padding=(5,5,5,5))
		f2.grid(row=0,column=0,sticky='NEWS')
		
		# http://www.picgifs.com/clip-art
		
		##----------------------------------------------------------
		
		#-------------- GPL License -------------------------------
		f3 = Frame(n,padding=(5,5,5,5))
		f3.grid(row=0,column=0,sticky='NEWS')
		f3.columnconfigure(0,weight=1)
		f3.rowconfigure(0,weight=1)		
		self.sb = Scrollbar(f3,orient='vertical')
		self.sb.grid(row=0,column=1,sticky='NS')
		self.text = Text(f3,height=30,width=50,wrap='word',
			yscrollcommand=self.sb.set)
		self.text.grid(row=0,column=0,sticky='NSEW')
		self.text.bind("<Key>",lambda e : "break")	# ignore all keypress
		# Note: return "break" from event handler to ignore
		self.sb.config(command=self.text.yview)
		try:
			with open('Assets/gpl.txt') as f: self.text.insert(END,f.read())
		except IOError: 
			self.text.insert(END,"\n\n\n\t\tError reading file 'gpl.txt'")
		#-----------------------------------------------------------
		
		n.add(f1,text='About',underline=0)
		n.add(f2,text='Credits',underline=0)
		n.add(f3,text='License',underline=0)
