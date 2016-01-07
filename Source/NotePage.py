try:
	from Tkinter import *
except ImportError:
	from tkinter import *

from tkColorChooser import askcolor

import 	tkMessageBox
import 	ttk
from 	ttk import *
import 	tkFont

class BasicNotepage ( Frame ):
	def __init__(self, parent, camera ):
		Frame.__init__(self, parent,padding=(10,10,10,10))
		self.grid(sticky='NSEW')
		self.columnconfigure(0,weight=1)
		self.camera = camera
		self.BuildPage()
	def BuildPage ( self ): print "No BuildPage" # override this
	def Reset ( self ):	print "No reset" # override this

