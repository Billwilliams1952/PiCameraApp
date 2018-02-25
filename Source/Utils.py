'''
Utils.py
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

Python2x = True

try:
	from Tkinter import *
except ImportError:
	from tkinter import *
	Python2x = False

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
	from	tkFont	import *
except ImportError:
	import	tkinter.font
	from	tkinter.font	import *

import PIL
from PIL import Image, ImageTk, ExifTags

from 	Dialog	import *
from	Tooltip	import *

#
# General utility functions
#
def UnderConstruction ( window ):
	Label(window,text='UNDER CONSTRUCTION',font=('Arial',14,('bold')),
		anchor='center').grid(row=0,column=0,sticky='EW')

def OnOff ( val ): return 'On' if val else 'Off'

def EvenOdd ( val ): return 'even' if val else 'odd'

# Add BooleanVar in here
def MyRadio ( f, txt, varValue, varName, cmd=None, row=0, col=0, stick='W',
				  span=1, pad=(5,5,5,5), tip='No Tip number provided'):
#def MyRadio ( f, txt, varValue, varName = None, cmd=None, row=0, col=0, stick='W',
#				  span=1, pad=(5,5,5,5), tip='No Tip number provided'):
	# if varName is None:
	#		# Determine type of var from varValue and create one
	#		if type(varValue) is int:
	# 			varName = MyIntVar(varValue)
	#		elif type(varValue) is boolean:
	# 			varName = MyBooleanVar(varValue)
	#		elif type(varValue) is str:
	# 			varName = MyStringVar(varValue)
	if cmd is None:
		r = ttk.Radiobutton(f,text=txt,value=varValue,variable=varName,
			 padding=pad)
	else:
		r = ttk.Radiobutton(f,text=txt,value=varValue,variable=varName,
			command=lambda:cmd(varValue),padding=pad)
	r.grid(row=row,column=col,sticky=stick, columnspan=span)
	ToolTip(r,msg=tip)
	return r # , varName		# return RadioButton and BooleanVar

'''
	params = [ ['text', True or False, row, col, sticky, rowspan, tipNum]
				  ['text', True or False, row, col, sticky, rowspan, tipNum] ]
	Command = the function to call if pressed, pass True or False
	Create two radio buttons, return the first one, and the BooleanVar
	associated with the two. If command is not None, then call the command
	with the same value passed in the list

	Return, first radio created, BooleanVar created
'''
def CreateRadioButtonBoolean ( parent, params, command=None ):
	pass

'''
	params = [ ['text', 'value', row, col, sticky, rowspan, tipNum]
				  ['text', 'value', row, col, sticky, rowspan, tipNum] ]
	Command = the function to call if pressed, pass True or False
	Create two radio buttons, return the first one, and the BooleanVar
	associated with the two. If command is not None, then call the command
	with the same value passed in the list

	Return, first radio created, StringVar created
'''
def CreateRadioButtonSet ( parent, params, command=None ):
	pass

def MyComboBox ( parent, values, current, callback, width=5, row=0, col=0,
					  sticky='EW', state='disabled', tip='No Tip number provided' ):
	combo = ttk.Combobox(parent,state=state,width=width)
	combo.grid(row=row,column=col,sticky=sticky)
	combo.bind('<<ComboboxSelected>>',callback)
	combo['values'] = values
	combo.current(current)
	ToolTip(combo,tip)
	return combo

def MySliderBar ( parent ):
	pass

def MyEditField ( parent ):
	pass

def MyLabel ( parent, text, row, col, span ):
	pass

def MyButton ( parent ):
	pass

def MyLabelFrame ( f, txt, row, col, stick='NEWS', py=5, span=1, pad=(5,5,5,5)):
	l = ttk.LabelFrame(f,text=txt,padding=pad)
	l.grid(row=row,column=col,sticky=stick,columnspan=span,pady=py)
	return l

def MyBooleanVar ( setTo ):
	b = BooleanVar()
	b.set(setTo)
	return b

def MyIntVar ( setTo ):
	b = IntVar()
	b.set(setTo)
	return b

def MyStringVar ( setTo ):
	s = StringVar()
	s.set(setTo)
	return s

def GetPhotoImage ( filename ):
	# Get the image - test whether python 2x or 3x
	if Python2x:
		if isinstance(filename,basestring):
			return ImageTk.PhotoImage(PIL.Image.open(filename))
		else:
			return ImageTk.PhotoImage(filename)
	else:
		if isinstance(filename,str):
			return ImageTk.PhotoImage(PIL.Image.open(filename))
		else:
			return ImageTk.PhotoImage(filename)

def USECtoSec ( usec ):
	# return a text value formatted
	if usec < 1000:
		return '%d usec' % usec
	elif usec < 1000000:
		return '%.3f msec' % (float(usec) / 1000.0)
	else:
		return '%.3f sec' % (float(usec) / 1000000.0)
