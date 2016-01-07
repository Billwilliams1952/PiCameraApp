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
try:
	from Tkinter import *
except ImportError:
	from tkinter import *
import 	ttk
from 	ttk import *

class ControlMapping ( ):
	def __init__ ( self ):
		self.FocusColor = '#f0f0ff'
		self.NoFocusMouseOverColor = 'lightyellow'
		self.NoFocusNoMouseOverColor = 'white'
		self.SetControlMapping()
	def SetControlMapping ( self ):
		Style().configure('RedMessage.TLabel',font=('Arial',10,"italic"),foreground='red')
		Style().configure('DataLabel.TLabel',foreground='blue',font=('Arial',10))
		Style().configure('StatusBar.TLabel',background=self.FocusColor,relief=SUNKEN)
		Style().configure('TPanedwindow',background='gray',showhandle=True,handlepad=30,sashwidth=20,sashpad=20)
		
		Style().map('TPanedwindow',
			background = [
						  ('active',self.FocusColor),
						  ('!active','lightgray'),
						  ],
				   )	# close map
		'''
		Can't seem to get a foucs highlight around some of the controls. 
		So I'm using color changes to show focus/tab stops.
		Also, the Scale does not seem to get focus by clicking on it
		Need to force focus when the user clicks on it
		'''		
		Style().map('TCombobox',
			fieldbackground = [
							  ('focus','!disabled',self.FocusColor), 
							  ('!focus','active','!disabled',self.NoFocusMouseOverColor),
							  ('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
							 #('disabled','lightgray'), # Use foreground
							  ],
			foreground = [
						 ('disabled','gray'),
						 ('!disabled', 'black') 
						 ],
			selectbackground = [
							   ('focus','!disabled',self.FocusColor),
							   ('!focus','active','!disabled',self.NoFocusMouseOverColor),
							   ('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
							  #('disabled','lightgray'),
							   ],
			selectforeground = [
							   ('!focus','black'),
							   ('readonly','black'),
							   ('focus','black'),
							   ('disabled','black'),
							   ('!disabled', 'black')
							   ],
				   )	# close map
					
		Style().map('TEntry',# This one is just for 'look and feel'
			fieldbackground = [
							  ('focus','!disabled',self.FocusColor),
							  ('!focus','active','!disabled',self.NoFocusMouseOverColor),
							  ('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
							 #('disabled','lightgray'),
							  ],
			foreground = [
						 ('disabled','gray'),
						 ('!disabled', 'black') 
						 ],
			#background = [
						  #('focus','!disabled',self.FocusColor),
						  #('!focus','active','!disabled',self.NoFocusMouseOverColor'),
						  #('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
						 ##('disabled','lightgray'),
						  #],
			#selectbackground = [
							   #('focus','!disabled',self.FocusColor),
							   #('!focus','active','!disabled',self.NoFocusMouseOverColor),
							   #('!focus','!active','!disabled',self.NoFocusNoMouseOverColor).
							  ##('disabled','lightgray'),
							   #],
			selectforeground = [
							   ('!focus','black'),
							   ('focus','white'),
							   ],
				   ) # close map
				   
		#Style().map('TMenubutton',# This one is just for 'look and feel'
			#fieldbackground = [
							  #('focus','!disabled',self.FocusColor),
							  #('!focus','active','!disabled',self.NoFocusMouseOverColor),
							  #('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
							 ##('disabled','lightgray'),
							  #],
			#foreground = [
						 #('disabled','gray'),
						 #('!disabled', 'black') 
						 #],
			#background = [
						  #('focus','!disabled',self.FocusColor),
						  #('!focus','active','!disabled',self.NoFocusMouseOverColor),
						  #('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
						 ##('disabled','lightgray'),
						  #],
			#selectbackground = [
							   #('focus','!disabled',self.FocusColor),
							   #('!focus','active','!disabled',self.NoFocusMouseOverColor),
							   #('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
							  ##('disabled','lightgray'),
							   #],
			#selectforeground = [
							   #('!focus','black'),
							   #('focus','white'),
							   #],
				   #) # close map
				   
		Style().map("Horizontal.TScale", 
			troughcolor = [
						  ('focus','!disabled',self.FocusColor),
						  ('!focus','active','!disabled',self.NoFocusMouseOverColor),
						  ('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
						  ('disabled','lightgray'),
						  ],
				   ) # close map
					
		Style().map("Vertical.TScale", 
			troughcolor = [
						  ('focus','!disabled',self.FocusColor),
						  ('!focus','active','!disabled',self.NoFocusMouseOverColor),
						  ('!focus','!active','!disabled',self.NoFocusNoMouseOverColor),
						  ('disabled','lightgray'),
						  ],
				   ) # close map	

