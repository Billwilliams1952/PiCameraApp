#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  ImageEffects.py
#
#  Copyright 2018  Bill Williams
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
	import 	tkFileDialog as FileDialog
except ImportError:
	import	tkinter.filedialog as FileDialog
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

import datetime as dt
from 	Dialog	import *
from 	Mapping	import *
from	NotePage	import *
from	Utils		import *
from	Tooltip	import *
from	NotePage import BasicNotepage

try:
	import 	picamera
	from 		picamera import *
	import 	picamera.array
except ImportError:
	raise ImportError("You do not seem to have picamera installed")

'''
When queried, the image_effect_params property either returns None
(for effects which have no configurable parameters, or if no parameters
have been configured), or a tuple of numeric values up to six elements long.

When set, the property changes the parameters of the current effect as
a sequence of numbers, or a single number. Attempting to set parameters
on an effect which does not support parameters, or providing an
incompatible set of parameters for an effect will raise a
PiCameraValueError exception.

The effects which have parameters, and what combinations those
parameters can take is as follows:

Effect	Parameters	Description
'solarize'	yuv, x0, y1, y2, y3		yuv controls whether data is processed
				as RGB (0) or YUV(1). Input values from 0 to x0 - 1 are
				remapped linearly onto the range 0 to y0. Values from x0 to
				255 are remapped linearly onto the range y1 to y2.
				x0, y0, y1, y2				Same as above, but yuv defaults to 0
												(process as RGB).
				yuv							Same as above, but x0, y0, y1, y2
				default to 128, 128, 128, 0 respectively.

'colorpoint'	quadrant	quadrant specifies which quadrant of the U/V
					space to retain chroma from: 0=green, 1=red/yellow,
					2=blue, 3=purple. There is no default; this effect does
					nothing until parameters are set.

'colorbalance'	lens, r, g, b, u, v	lens specifies the lens shading
					strength (0.0 to 256.0, where 0.0 indicates lens shading
					has no effect). r, g, b are multipliers for their
					respective color channels (0.0 to 256.0). u and v are
					offsets added to the U/V plane (0 to 255).
					lens, r, g, b			Same as above but u are defaulted to 0.
					lens, r, b				Same as above but g also defaults to to 1.0.

'colorswap'		dir	If dir is 0, swap RGB to BGR. If dir is 1, swap RGB to BRG.

'posterise'		steps		Control the quantization steps for the image.
					Valid values are 2 to 32, and the default is 4.

'blur'			size	Specifies the size of the kernel. Valid values are 1 or 2.

'film'			strength, u, v	strength specifies the strength of effect.
					u and v are offsets added to the U/V plane (0 to 255).

'watercolor'	u, v		u and v specify offsets to add to the U/V plane (0 to 255).
					No parameters indicates no U/V effect.
'''

class ImageEffectsDialog ( Dialog ):
	def BuildDialog ( self ):
		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=0,column=0,sticky='NSEW')
		n.columnconfigure(0,weight=1)
		n.rowconfigure(0,weight=1)

		self.Effects1 = Effects1Page(n,camera=self._camera,cancel=self.CancelButton)
		self.Effects2 = Effects2Page(n,camera=self._camera,cancel=self.CancelButton)

		n.add(self.Effects1,text='Effects Page 1',underline=0)
		n.add(self.Effects2,text='Effects Page 2',underline=0)

	def OkPressed ( self ):
		self.Effects1.SaveChanges()
		self.Effects2.SaveChanges()
		return True

	def CancelPressed ( self ):
		return MessageBox.askyesno("Effects Parameters","Exit without saving changes?")

class Effects1Page ( BasicNotepage ):
	# -1 means I haven't done anything with the values yet...
	EffectParam = { 'posterise' : 4, 'blur' : 1, 'colorpoint' : 0,
					'colorswap' : 0, 'solarize' : -1, 'colorbalance' : -1,
					'film' : -1, 'watercolor' : -1 }
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		EffectParam = { 'posterise' : 4, 'blur' : 1, 'colorpoint' : 0,
					'colorswap' : 0, 'solarize' : -1, 'colorbalance' : -1,
					'film' : -1, 'watercolor' : -1 }
	def BuildPage ( self ):
		Label(self,text="Blur kernel size:").grid(row=0,column=0,sticky='W',pady=5);
		self.BlurAmt = ttk.Label(self,text="%d" % Effects1Page.EffectParam['blur'],
			style='DataLabel.TLabel')
		self.BlurAmt.grid(row=0,column=2,sticky='W')
		ToolTip(self.BlurAmt,4011)
		self.BlurKernelSize = ttk.Scale(self,from_=1,to=2,orient='horizontal',
							command=self.BlurKernelSizeChanged)
		self.BlurKernelSize.grid(row=0,column=1,sticky='W',pady=5)
		self.BlurKernelSize.set(Effects1Page.EffectParam['blur'])
		ToolTip(self.BlurKernelSize,4010)

		Label(self,text="Colorbalance:").grid(row=1,column=0,sticky='W',pady=5);
		Label(self,text="IN WORK").grid(row=1,column=1,sticky='W',pady=5);

		Label(self,text="Colorpoint U/V quadrant:").grid(row=2,column=0,sticky='W');
		self.Quadrant = Combobox(self,state='readonly',width=15)
		self.Quadrant.bind('<<ComboboxSelected>>',self.QuadrantChanged)
		self.Quadrant.grid(row=2,column=1,sticky='W',columnspan=2)
		self.QuadrantList = ['Green','Red/Yellow','Blue','Purple']
		self.Quadrant['values'] = self.QuadrantList
		self.Quadrant.current(Effects1Page.EffectParam['colorpoint'])
		ToolTip(self.Quadrant,4020)

		Label(self,text="Colorswap direction:").grid(row=3,column=0,sticky='W',pady=5);
		self.Direction = Combobox(self,state='readonly',width=15)
		self.Direction.bind('<<ComboboxSelected>>',self.DirectionChanged)
		self.Direction.grid(row=3,column=1,sticky='W',columnspan=2)
		self.DirectionList = ['Swap RGB to BGR', 'Swap BGR to RGB']
		self.Direction['values'] = self.DirectionList
		self.Direction.current(Effects1Page.EffectParam['colorswap'])
		ToolTip(self.Direction,4030)

		Label(self,text="Film:").grid(row=4,column=0,sticky='W',pady=5);
		Label(self,text="IN WORK").grid(row=4,column=1,sticky='W',pady=5);

		Label(self,text="Posterize quantization steps:").grid(row=5,column=0,sticky='W',pady=5);
		self.PosterizeAmt = ttk.Label(self,text="%d" % Effects1Page.EffectParam['posterise'],
			style='DataLabel.TLabel')
		self.PosterizeAmt.grid(row=5,column=2,sticky='W')
		ToolTip(self.PosterizeAmt,4001)
		self.Posterize = ttk.Scale(self,from_=2,to=32,orient='horizontal',
							command=self.PosterizeChanged)
		self.Posterize.grid(row=5,column=1,sticky='W',pady=5)
		self.Posterize.set(Effects1Page.EffectParam['posterise'])
		ToolTip(self.Posterize,4000)

		Label(self,text="Solarize:").grid(row=6,column=0,sticky='W',pady=5);
		Label(self,text="IN WORK").grid(row=6,column=1,sticky='W',pady=5);

		Label(self,text="Watercolor:").grid(row=7,column=0,sticky='W',pady=5);
		Label(self,text="IN WORK").grid(row=7,column=1,sticky='W',pady=5);

	def PosterizeChanged ( self, val ):
		if self.camera.image_effect == 'posterise':
			self.camera.image_effect_params = ( int(float(val)) )
		Effects1Page.EffectParam['posterise'] = int(float(val))
		self.PosterizeAmt.config(text="%d" % Effects1Page.EffectParam['posterise'])
	def BlurKernelSizeChanged ( self, val ):
		if self.camera.image_effect == 'blur':
			self.camera.image_effect_params = ( int(float(val)) )
		Effects1Page.EffectParam['blur'] = int(float(val))
		self.BlurAmt.config(text="%d" % Effects1Page.EffectParam['blur'])
	def QuadrantChanged ( self, val ):
		if self.camera.image_effect == 'colorpoint':
			self.camera.image_effect_params = ( self.Quadrant.current() )
		Effects1Page.EffectParam['colorpoint'] = self.Quadrant.current()
	def DirectionChanged ( self, val ):
		if self.camera.image_effect == 'colorswap':
			self.camera.image_effect_params = ( self.Direction.current() )
		Effects1Page.EffectParam['colorswap'] = self.Direction.current()
	def SaveChanges ( self ):
		pass

class Effects2Page ( BasicNotepage ):
	@staticmethod
	# Called if Reset Camera is clicked
	def Reset ():
		pass
	def BuildPage ( self ):
		Label(self,text="NOTHING HERE YET!!").grid(row=0,column=0,sticky='W');
	def SaveChanges ( self ):
		pass
