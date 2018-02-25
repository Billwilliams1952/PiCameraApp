'''
KeyboardShortcuts.py
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
	from		tkFont import Font
except ImportError:
	import	tkinter.font
	from		tkinter.font import Font

from 	Dialog import *

import PIL
from PIL import Image, ImageTk, ExifTags

from Utils import EvenOdd

#
# Display formatted textbox of supported keyboard shortcuts
#
class KeyboardShortcutsDialog ( Dialog ):
	def BuildDialog ( self ):
		def AddCmdKey ( text ):
			bg = EvenOdd(self.even)
			strs = text.split(':')
			self.text.insert(END,strs[0],("KeyboardCommand","Indent",bg))
			strs = strs[1].split('~')
			self.text.insert(END,strs[0],bg)
			if len(strs) > 1:
				self.text.insert(END,strs[1][0],("CmdKey",bg))
				self.text.insert(END,strs[1][1:],(bg))
			self.even = not self.even

		self.MainFrame.rowconfigure(0,weight=1)
		self.MainFrame.columnconfigure(0,weight=1)

		self.iconKeyboard = ImageTk.PhotoImage(PIL.Image.open("Assets/keyboard.gif"))
		Label(self.MainFrame,image=self.iconKeyboard).grid(row=0,column=0,sticky='W')

		self.sb = Scrollbar(self.MainFrame,orient='vertical')
		self.sb.grid(row=1,column=1,sticky='NS')
		self.text = Text(self.MainFrame,height=30,width=60,wrap='word',
			yscrollcommand=self.sb.set)
		self.text.grid(row=1,column=0,sticky='NSEW')
		self.text.bind("<Key>",lambda e : "break")	# ignore all keypress
		self.sb.config(command=self.text.yview)

		## Tags for various text formats
		boldFont = Font(self.text,self.text.cget("font"))
		boldFont.configure(weight="bold")
		boldUnderlineFont = Font(self.text,self.text.cget("font"))
		boldUnderlineFont.configure(weight="bold",underline=True)
		self.text.tag_configure("Bold",font=boldFont)
		self.text.tag_configure("Title",font=("Arial",14,"bold"))
		self.text.tag_configure("KeyboardCommand",font=boldFont,foreground='blue')
		self.text.tag_configure("Center",justify = CENTER)
		self.text.tag_configure("Indent",lmargin1='1c',lmargin2='1c')
		self.text.tag_configure("CmdKey",font=boldUnderlineFont)
		self.text.tag_configure("odd",background='white')
		self.text.tag_configure("even",background='#f0f0ff')
		self.even = True

		self.text.insert(END,"\nKeyboard shortcuts\n\n",("Center","Title"))

		self.text.insert(END,"Photo viewer pane\n\n","Bold")
		self.even = True
		AddCmdKey("LeftMouse:\t\t\t\tPan image\n")
		AddCmdKey("Ctrl+MouseWheel Up/Down:\t\t\t\tZoom in/out\n")
		AddCmdKey("Ctrl+LeftMouse:\t\t\t\tShow zoomed area on preview\n")

		self.text.insert(END,"\nNotepad traversal shorcuts\n\n","Bold")
		self.even = True
		AddCmdKey("Ctrl+TAB:\t\tSelects the next tab.\n")
		AddCmdKey("Ctrl+SHIFT+TAB:\t\t\tSelects the previous tab.\n")
		AddCmdKey("ALT+B:\t\tSelect ~Basic commands tab\n")
		AddCmdKey("ALT+E:\t\tSelect ~Exposure commands tab\n")
		AddCmdKey("ALT+C:\t\tSelect Finer ~Control commands tab\n")
		AddCmdKey("ALT+A:\t\tSelect ~Annotate/EXIF Metadata commands tab\n")
		AddCmdKey("ALT+T:\t\tSelect ~Time lapse commands tab\n")

		self.text.insert(END,"\nPhoto / Video commands\n\n","Bold")
		self.even = True
		AddCmdKey("Right Click:\tPopup menu\n")
		AddCmdKey("Ctrl+P:\t\tTake ~picture\n")
		AddCmdKey("Ctrl+V:\t\tToggle capture ~video on/off\n")
		AddCmdKey("Ctrl+C:\t\t~Clear picture or video in pane\n")
		AddCmdKey("Ctrl+R:\t\t~Reset all camera setups to defaults\n")

		self.text.insert(END,"\nUser Interface\n\n","Bold")
		self.even = True
		AddCmdKey("TAB:\t\tSelects the next active control.\n")
		AddCmdKey("Shift+TAB:\t\tSelects the previous active control.\n")
		AddCmdKey("Alt+F:\t\tDrop down ~File menu\n")
		AddCmdKey("Alt+V:\t\tDrop down ~View menu\n")
		AddCmdKey("Alt+P:\t\tDrop down ~Photo menu\n")
		AddCmdKey("Alt+H:\t\tDrop down ~Help menu\n")
		AddCmdKey("Ctrl+Shift+C:\t\tShow/hide ~Cursors\n")
		AddCmdKey("Ctrl+Shift+A:\t\tShow/hide Image ~Attributes pane\n")
		AddCmdKey("Ctrl+Shift+P:\t\tShow/hide ~Preview pane\n")

		self.text.insert(END,"\nGeneral commands\n\n","Bold")
		self.even = True
		AddCmdKey("Ctrl+Q:\t\t~Quit program\n")
