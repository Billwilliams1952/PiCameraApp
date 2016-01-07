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

try:
	from Tkinter import *
except ImportError:
	from tkinter import *
import 	ttk
from 	ttk import *
import 	tkFont
from tkFont import *
from 	Dialog import *
	
# General utility functions	
	
def UnderConstruction ( window ):
	Label(window,text='UNDER CONSTRUCTION',font=('Arial',14,('bold')),
		anchor='center').grid(row=0,column=0,sticky='EW')
