'''
NotePage.py
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

from Utils import UnderConstruction

#
# Base Class for all NotePad pages.
#
class BasicNotepage ( Frame ):
	def __init__(self, parent, camera=None, cancel=None, ok=None,
					 rowconfig=False, colconfig=True, data = None ):
		ttk.Frame.__init__(self, parent,padding=(10,10,10,10))
		self.grid(sticky='NSEW')
		if colconfig is True:
			self.columnconfigure(0,weight=1)
		if rowconfig is True:
			self.rowconfigure(0,weight=1)
		self.camera = camera
		self.parent = parent
		self.CancelButton = cancel
		self.OkButton = ok
		self.data = data
		self.init = True	# disable SomethingChanged
		self.BuildPage()
		self.init = False
		self.Changed = False
	def BuildPage ( self ): 				# MUST Overide this!
		UnderConstruction(self)
	def SomethingChanged ( self, val ):	# Can override but call super!
		if self.init: return
		self.Changed = True
		if self.CancelButton != None:
			self.CancelButton.config(state='normal') #'!disabled')
			if self.OkButton != None:
				self.OkButton.config(text='Save')
	def SaveChanges ( self ):				# MUST override this!
		MessageBox.showwarning("SaveChanges", "SaveChanges not implemented!")
