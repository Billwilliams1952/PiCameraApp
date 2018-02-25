#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Tooltip.py
#
#  Copyright 2018  Bill Williams
#
#	Tooltip implementation courtesy of
#	https://code.activestate.com/recipes/576688-tooltip-for-tkinter/
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
#
from time import time, localtime, strftime
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
except ImportError:
	import	tkinter.font

class ToolTip( Toplevel ):
	ShowToolTips = True
	ShowTipNumber = False
	ShowTipDelay = 1.0		# 1 second initial delay
	TipLines = []				# All the tip text in lines
	@staticmethod
	def LoadToolTips ( ):	# Perhaps allow a reload of tips?
		tipsFile = open("Assets/Tooltips.txt", "r")
		if tipsFile:
			ToolTip.TipLines = tipsFile.read().split('\n')
			tipsFile.close()
		else:
			print ( "Error opening file 'Assets/Tooltips.txt'" )
	@staticmethod
	def GetTooltipText ( ID ):
		append = False
		tip = ""
		for text in ToolTip.TipLines:
			text = text.strip()
			text = text.replace('(C)',
				'\n\nThanks to: picamera.readthedocs.io/en/release-1.13/api_camera.html')
			if append:
				# Buggy - spaces are being lost in the text
				if text.endswith('\\n') is True: tip = tip + text
				else:	tip = tip + ' ' + text	# add a space for next line
				if tip.endswith('$') is True:
					return tip.replace('$','').replace("\\n","\n")
			else:
				if len(text) is 0 or text[0] is '#': continue
				ID_Tip = text.split(':',1) # only the first colon is a split
				try:
					if int(ID_Tip[0].strip()) == ID: # find a better way
						# We have a match
						# Check if the text continues on multiple lines
						tip = ID_Tip[1].strip()
						append = False if tip.endswith('$') else True
						if append is False:
							return tip.replace("\\n","\n").replace('$','')
				except: pass
		return 'Tooltip text for ID %d not found.' % ID
	"""
	Provides a ToolTip widget for Tkinter.
	To apply a ToolTip to any Tkinter widget, simply pass the widget to the
	ToolTip constructor
	"""
	def __init__( self, wdgt, msg=None, msgFunc=None, follow=1 ):
		"""
		Initialize the ToolTip
		Arguments:
			wdgt: The widget to which this ToolTip is assigned
			msg:  A static string message assigned to the ToolTip
					if msg istype integer - search for text in TipLines
			msgFunc: A function that retrieves a string to use as the ToolTip text
			delay:   The delay in seconds before the ToolTip appears(may be float)
			follow:  If True, the ToolTip follows motion, otherwise hides
		"""
		self.wdgt = wdgt
		# The parent of the ToolTip is the parent of the ToolTips widget
		self.parent = self.wdgt.master
		# Initalise the Toplevel
		Toplevel.__init__( self, self.parent, bg='black', padx=1, pady=1 )
		self.withdraw()  # Hide initially
		# The ToolTip Toplevel should have no frame or title bar
		self.overrideredirect( True )
		# The msgVar will contain the text displayed by the ToolTip
		self.msgVar = StringVar()
		self.TipID = None
		self.TipNumText = ""
		try:
			if msg is None:
				self.msgVar.set('No tooltip provided')
			elif type(msg) is int:	# lookup tooltip text in file
				self.TipID = msg
				self.msgVar.set(ToolTip.GetTooltipText(msg))
				self.TipNumText = "Tip number %d\n\n" % self.TipID
			else:	# assume a string is passed
				self.msgVar.set( msg )
		except:
			self.msgVar.set('ERROR getting tooltip')
		self.msgFunc = msgFunc		# call this function to return tip text
		self.follow = follow			# move tip if mouse moves
		self.visible = 0
		self.lastMotion = 0
		# The test of the ToolTip is displayed in a Message widget
		Message( self, textvariable=self.msgVar, bg='#FFFFDD',
					aspect=250 ).grid()
		# Add bindings to the widget.  This will NOT override bindings
		# that the widget already has
		self.wdgt.bind( '<Enter>', self.spawn, '+' )
		self.wdgt.bind( '<Leave>', self.hide, '+' )
		self.wdgt.bind( '<Motion>', self.move, '+' )

	def spawn( self, event=None ):
		"""
		Spawn the ToolTip.  This simply makes the ToolTip eligible for display.
		Usually this is caused by entering the widget
		Arguments:
			event: The event that called this funciton
		"""
		self.visible = 1
		# The after function takes a time argument in miliseconds
		self.after( int( ToolTip.ShowTipDelay * 1000 ), self.show )

	def show( self ):
		"""
		Displays the ToolTip if the time delay has been long enough
		"""
		if ToolTip.ShowToolTips is False: return
		text = self.msgVar.get()
		if ToolTip.ShowTipNumber is True and self.TipID is not None:
			# check if text is not there, if so add it
			if self.TipNumText not in text:
				self.msgVar.set(self.TipNumText+text)
		else:
			text.replace(self.TipNumText,"")
			self.msgVar.set(text)

		if self.visible == 1 and time() - self.lastMotion > ToolTip.ShowTipDelay:
			self.visible = 2
		if self.visible == 2:
			self.deiconify()

	def move( self, event ):
		"""
		Processes motion within the widget.
		Arguments:
		event: The event that called this function
		"""
		self.lastMotion = time()
		# If the follow flag is not set, motion within the widget will
		# make the ToolTip dissapear
		if self.follow == False:
			self.withdraw()
			self.visible = 1
		# Offset the ToolTip 10x10 pixels southeast of the pointer
		self.geometry( '+%i+%i' % ( event.x_root+10, event.y_root+10 ) )
		# Try to call the message function.  Will not change the message
		# if the message function is None or the message function fails
		try:		self.msgVar.set( self.msgFunc() )
		except:	pass
		self.after( int( ToolTip.ShowTipDelay * 1000 ), self.show )

	def hide( self, event=None ):
		"""
		Hides the ToolTip.  Usually this is caused by leaving the widget
		Arguments:
			event: The event that called this function
		"""
		self.visible = 0
		self.withdraw()
