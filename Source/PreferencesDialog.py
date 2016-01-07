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
try:
	from Tkinter import *
except ImportError:
	from tkinter import *
import 	ttk
from 	ttk import *
import 	tkFont
import 	tkMessageBox
from 	Dialog import *
from 	Mapping import *
from	NotePage import *

import PIL
from PIL import Image, ImageTk

# All PiCameraApp global preferences ae handled here		
class PreferencesDialog ( Dialog ):
	def BuildDialog ( self ):		
		self.MainFrame.columnconfigure(0,weight=1)
		self.MainFrame.rowconfigure(0,weight=1)
		n = Notebook(self.MainFrame,padding=(5,5,5,5),width=30,height=200)
		n.grid(row=0,column=0,sticky='NEWS')
		
		GeneralPage = General(n,self.camera)
		InterfacePage = Interface(n,self.camera)
		OtherPage = Other(n,self.camera)
		
		n.add(GeneralPage,text='General',underline=0)
		n.add(InterfacePage,text='Interface',underline=0)
		n.add(OtherPage,text='Other',underline=0)

# Handle PiCameraApp General preferences
class General ( BasicNotepage ):
	pass

# Handle PiCameraApp Interface preferences
class Interface ( BasicNotepage ):
	def BuildPage ( self ):
		self.iconMonitor = ImageTk.PhotoImage(PIL.Image.open("Assets/computer-monitor.png"))
		Label(self,image=self.iconMonitor).grid(row=0,column=0,sticky='W')
		f = LabelFrame(self,text='Interface themes',padding=(5,5,5,5))
		f.grid(row=1,column=0,sticky='NEWS',pady=5)
		f.columnconfigure(1,weight=1)
		Label(f,text='Set theme').grid(row=0,column=0,sticky='W')
		self.themes = Combobox(f,height=10,state='readonly')
		self.themes.grid(row=0,column=1,sticky='W')
		self.themes['values'] = Style().theme_names()
		self.themes.set(Style().theme_use())
		self.themes.bind('<<ComboboxSelected>>',self.ThemesSelected)
	def ThemesSelected ( self, event ):
		Style().theme_use(self.themes.get())
		
# Handle PiCameraApp Other preferences		
class Other ( BasicNotepage ):
	pass
