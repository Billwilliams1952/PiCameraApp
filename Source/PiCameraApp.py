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

########### TODO: Standaardize variable, class, member cases

import time
import webbrowser		# display the Picamera documentation
import io
import time
import os
from   collections import OrderedDict

# If no RPi.GPIO, then disable the ability to toggle the camera LED
RPiGPIO = True
try:
	import RPi.GPIO
except ImportError:
	RPiGPIO = False

# This we cannot allow since the entire program demoands ther PiCamera
# Close here
try:
	import picamera
	from picamera import *
	import picamera.array
except ImportError:
	raise ImportError("You do not seem to have PiCamera installed")

try:
	from Tkinter import *
except ImportError:
	from tkinter import *

from tkColorChooser import askcolor
import tkFileDialog

import 	tkMessageBox
import 	ttk
from 	ttk import *
import 	tkFont

try:
	import PIL
	from PIL import Image, ImageTk, ExifTags
except ImportError:
	raise ImportError("You do not seem to have the Python Imaging Library (PIL) installed")

from 	AboutDialog import *
from 	PreferencesDialog import *
from	KeyboardShortcuts import *
from	Mapping import *
from	NotePage import *
from	CameraUtils import *

#
# Main PiCameraApp Window
#
class PiCameraApp ( Frame ):
	def __init__(self, root, camera, title):
		Frame.__init__(self, root)

		self.grid(padx=5,pady=5)
		self.root = root

		self.ControlMapping = ControlMapping()

		self.camera = camera
		self.camera.start_preview(fullscreen=False,window=(0,0,10,10))

		self.title = title
		self.root.title(title)

		master = root

		master.rowconfigure(0,weight=1)
		master.columnconfigure(1,weight=1)
		master.config(padx=5,pady=5)
		
		#----------- Icons for Menu and Buttons ------------------------
		self.iconClose = ImageTk.PhotoImage(PIL.Image.open("Assets/window-close.png"))
		self.iconPrefs = ImageTk.PhotoImage(PIL.Image.open('Assets/prefs1_16x16.png'))
		self.iconWeb = ImageTk.PhotoImage(PIL.Image.open('Assets/web_16x16.png'))
		self.iconCamera = ImageTk.PhotoImage(PIL.Image.open('Assets/camera_16x16.gif'))
		self.iconCameraBig = ImageTk.PhotoImage(PIL.Image.open('Assets/camera_22x22.png'))
		self.iconVideo = ImageTk.PhotoImage(PIL.Image.open('Assets/video_16x16.gif'))
		self.iconVideoBig = ImageTk.PhotoImage(PIL.Image.open('Assets/video_22x22.gif'))
		#---------------------------------------------------------------

		#user = expanduser('~')
		## Make a subdirectory
		#self.photoDirectory = '%s/Documents/PiCameraDemo/Photos/' % user
		#if not os.path.exists(self.photoDirectory):
			#os.makedirs(self.photoDirectory)
			#print '%s created' % self.photoDirectory
	
		#self.videoDirectory = '%s/Documents/PiCameraDemo/Videos/' % user
		#if not os.path.exists(self.videoDirectory):
			#os.makedirs(self.videoDirectory)
			#print '%s created' % self.videoDirectory
		##---------------------------------------------------------

		frame1 = Frame(master,padding=(5,5,5,5))
		frame1.grid(row=0,column=0,sticky="NSEW")
		frame1.rowconfigure(2,weight=1)
		frame1.columnconfigure(0,weight=1)

		self.AlwaysPreview = False
			
		n = Notebook(frame1,padding=(5,5,5,5))
		n.grid(row=1,column=0,rowspan=2,sticky=(N,E,W,S))
		n.columnconfigure(0,weight=1)

		self.BasicControlsFrame = BasicControls(n,camera)
		self.ExposureFrame = Exposure(n,camera)
		self.FinerControlFrame = FinerControl(n,camera)
		self.AnnotateFrame = Annotate(n,camera)

		n.add(self.BasicControlsFrame ,text='Basic')
		n.add(self.ExposureFrame,text='Exposure')
		n.add(self.FinerControlFrame,text='Finer control')
		n.add(self.AnnotateFrame,text='Annotate/EXIF Metadata')

		# ----------------------Paned Window ---------------------------
		# Start of Image Canvas preview, camera captures,
		#	Paned Window VERTICAL
		#		TopFrame
		#			Preview ImageCanvas	row Weight=1
		#			ButtonFrame
		#				Preview Buttons
		#		BottomFrame
		#			PanedWindow HORIZONTAL row 0, col 0
		#				LeftFrame
		#					Cameera setups, EXIF Text
		#				RightFrame
		#					Current Photo Canvas
		#			ButtonFrame
		#				Picture / Video buttons
		
		self.pw = PanedWindow(master,orient=VERTICAL)
		self.pw.grid(row=0,column=1,sticky="NSEW")
		self.pw.rowconfigure(0,weight=1)
		self.pw.columnconfigure(0,weight=1)
		
		TopFrame = Frame(self.pw,padding=(5,5,5,5))
		TopFrame.grid(row=0,column=0,sticky="NEWS")
		TopFrame.rowconfigure(0,weight=1)
		TopFrame.columnconfigure(1,weight=1)

		###### TODO: Create Canvas Class to handle generic cursors, etc
		self.ImageCanvas = Canvas(TopFrame,width=256,height=256,
			background=self.ControlMapping.FocusColor,cursor='diamond_cross')
		self.ImageCanvas.grid(row=0,column=0,columnspan=2,sticky="NEWS")
		self.CursorX = self.ImageCanvas.create_line(0,0,320,0,
			fill='red',tags=('cursors'))
		self.CursorY = self.ImageCanvas.create_line(0,0,0,240,
			fill='red',tags=('cursors'))
		self.ImageCanvas.create_text((256,256),text="Preview off",fill='blue',
			activefill='gray',font=('Helveticar',36,"bold italic"),
			tags=("nopreview"))
		self.ImageCanvas.itemconfigure('nopreview',state='hidden')
		self.ImageCanvas.bind("<Motion>",self.CanvasMouseMove)
		self.ImageCanvas.bind("<ButtonPress>",self.CanvasMouseMove)
		self.ImageCanvas.bind("<Enter>",self.CanvasEnterLeave)
		self.ImageCanvas.bind("<Leave>",self.CanvasEnterLeave)

		ButtonFrame = Frame(TopFrame,padding=(5,5,5,5),relief=SUNKEN)
		ButtonFrame.grid(row=1,column=0,columnspan=2,sticky="NEWS")

		self.PreviewOn = BooleanVar()
		self.PreviewOn.set(True)
		Checkbutton(ButtonFrame,text='Enable preview',variable=self.PreviewOn,
			command=self.SetPreviewOn).grid(row=0,column=0,padx=5,sticky='W')

		l2 = Label(ButtonFrame,text="Alpha:")
		l2.grid(column=1,row=0,sticky='W')
		self.alpha = Scale(ButtonFrame,from_=0,to=255,
				command=self.AlphaChanged,orient='horizontal',length=100)
		self.alpha.grid(row=0,column=2,sticky='E')
		self.alpha.set(255)

		self.VFlipState = False
		self.flipVgif = ImageTk.PhotoImage(file='Assets/flipV.gif')
		self.Vflip = Button(ButtonFrame,image=self.flipVgif,width=10,
			command=self.ToggleVFlip,padding=(2,2,2,2))
		self.Vflip.grid(row=0,column=3,padx=5)
		self.HFlipState = False
		self.flipHgif = ImageTk.PhotoImage(file='Assets/flipH.gif')
		self.Hflip = Button(ButtonFrame,image=self.flipHgif,width=10,
			command=self.ToggleHFlip,padding=(2,2,2,2))
		self.Hflip.grid(row=0,column=4)

		#------------------ Photo / Video Section ----------------------
		self.pictureStream = io.BytesIO()
		
		BottomFrame = Frame(self.pw,padding=(5,5,5,5))
		BottomFrame.grid(row=1,column=0,sticky="NEWS")
		BottomFrame.rowconfigure(0,weight=1)
		BottomFrame.columnconfigure(0,weight=1)
		
		self.photoPanedWindow = PanedWindow(BottomFrame,orient=HORIZONTAL)
		self.photoPanedWindow.grid(row=0,column=0,sticky="NSEW")
		self.photoPanedWindow.rowconfigure(0,weight=1)
		self.photoPanedWindow.columnconfigure(0,weight=1)	
		self.photoPanedWindow.columnconfigure(1,weight=1)	
		
		self.LeftFrame = Frame(self.photoPanedWindow,padding=(5,5,5,5))
		self.LeftFrame.grid(row=0,column=0,sticky="NEWS")
		self.LeftFrame.rowconfigure(0,weight=1)
		self.LeftFrame.columnconfigure(0,weight=1)
		
		sb = Scrollbar(self.LeftFrame,orient='vertical')
		sb.grid(row=0,column=1,sticky='NS')
		sb1 = Scrollbar(self.LeftFrame,orient='horizontal')
		sb1.grid(row=1,column=0,sticky='EW')		
		text = Text(self.LeftFrame,width=37,wrap='none',
			yscrollcommand=sb.set,xscrollcommand=sb1.set)
		text.bind('<Configure>',self.TextboxResize)
		text.grid(row=0,column=0,sticky='NSEW')
		sb.config(command=text.yview)
		sb1.config(command=text.xview)
		text.bind("<Key>",lambda e : "break")	# ignore all keypress		
		self.CameraUtils = CameraUtils(self.camera,self.BasicControlsFrame)
		self.CameraUtils.SetupCameraSettingsTextbox(text)
		
		RightFrame = Frame(self.photoPanedWindow,padding=(5,5,5,5))
		RightFrame.grid(row=0,column=1,sticky="NEWS")
		RightFrame.rowconfigure(0,weight=1)
		RightFrame.columnconfigure(0,weight=1)
		
		self.CurrentImage = None
		self.photoCanvas = Canvas(RightFrame,width=50,height=50,
			background=self.ControlMapping.FocusColor,cursor='diamond_cross')
		self.photoCanvas.grid(row=0,column=0,sticky="NEWS")
		self.photoCanvas.create_line(0,0,320,0,
			fill='red',tags=('cursors','objs','cursorx'))
		self.photoCanvas.create_line(0,0,0,240,
			fill='red',tags=('cursors','objs','cursory'))
		self.photoCanvas.create_line(0,0,320,0,
			fill='lightgray',activefill='darkgray',tags=('cross','cross1'))
		self.photoCanvas.create_line(0,0,0,240,
			fill='lightgray',activefill='darkgray',tags=('cross','cross2'))
		self.photoCanvas.create_text(0,0,
			tags=('capture'),text='',
			fill='blue',activefill='gray',anchor='center',
			font=('Helveticar',18,"bold italic"))
		self.photoCanvas.itemconfigure('capture',state='hidden')
		self.photoCanvas.create_text(0,0,
			fill='red',tags=('text','objs'),anchor='nw')

		self.photoCanvas.bind('<Configure>',self.PhotoCanvasResize)
		self.photoCanvas.bind("<ButtonPress-1>",self.photoCanvasScrollStart)
		self.photoCanvas.bind("<B1-Motion>",self.photoCanvasScrollMove)
		self.photoCanvas.bind("<Motion>",self.photoCanvasMove)
		self.photoCanvas.bind("<ButtonRelease-1>",self.photoCanvasButtonUp)
		self.photoCanvas.bind("<Enter>",self.photoCanvasEnterLeave)
		self.photoCanvas.bind("<Leave>",self.photoCanvasEnterLeave)
		self.InPhotoZoom = False 	# hack - 
		# self.PhotoState = 'none', 'picture', 'zoom', 'video' ???

		vsbar = Scrollbar(RightFrame,orient=VERTICAL)
		vsbar.grid(row=0,column=1,sticky='NS')
		vsbar.config(command=self.photoCanvas.yview)
		self.photoCanvas.config(yscrollcommand=vsbar.set)
						
		hsbar = Scrollbar(RightFrame,orient=HORIZONTAL)
		hsbar.grid(row=1,column=0,sticky='EW')
		hsbar.config(command=self.photoCanvas.xview)
		self.photoCanvas.config(xscrollcommand=hsbar.set)	
		self.photoCanvas.bind("<5>",self.WheelScrollPhotoCanvas) #MouseWheel
		self.photoCanvas.bind("<4>",self.WheelScrollPhotoCanvas) #MouseWheel
		self.photoZoomScale	= 1.0

		self.photoPanedWindow.add(self.LeftFrame)
		self.photoPanedWindow.add(RightFrame)
		self.photoPanedWindow.forget(self.LeftFrame)

		ButtonFrame = Frame(BottomFrame,padding=(5,5,5,5))
		ButtonFrame.grid(row=1,column=0,columnspan=3,sticky="NEWS")
		b = Button(ButtonFrame,text='Picture',underline=0,image=self.iconCameraBig,
			compound='left',command=lambda e=None:self.TakePicture(e),width=7)
		b.grid(row=0,column=0,sticky='W')
		self.InCaptureVideo = False  # hack ----
		self.TakeVideo = Button(ButtonFrame,text='Video',underline=0,
			image=self.iconVideoBig,compound='left',
			command=lambda e=None:self.ToggleVideo(e),width=7)
		self.TakeVideo.grid(row=0,column=1,sticky='W')
		self.clearImage = ImageTk.PhotoImage(file='Assets/cancel_22x22.png')
		b = Button(ButtonFrame,command=lambda e=None:self.ClearPicture(e),
			image=self.clearImage,padding=(0,1,0,1))
		b.grid(row=0,column=2,sticky='W',padx=5)
		
		self.pw.add(TopFrame)
		self.pw.add(BottomFrame)

		#-------------------------- Status Bar -------------------------
		self.statusText = StringVar()
		lbl = Label(master,textvariable=self.statusText,style='StatusBar.TLabel')
		lbl.grid(row=1,column=0,columnspan=3,sticky="EW")

		# Catch all focus events to the Top Window. Use to control
		# whether the camera preview_window overlay is visible or not.
		# I'm sure this will fail with Topmost windows... :(
		self.root.bind('<FocusOut>',self.LoseFocus)
		self.root.bind('<FocusIn>',self.GotFocus)

		#--------------------------- Menu ------------------------------
		menubar = Menu(root,
			foreground='black',background='#F0F0F0',activebackground='#86ABD9',
			activeforeground='white')
		
		filemenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		filemenu.add_command(label="Save",underline=2,compound='left',
			command=lambda e=None:self.SavePictureorVideo(e),accelerator='Ctrl+S')
		self.DefineAccelerators('c','s',lambda e=None:self.SavePictureorVideo(e))
		filemenu.add_separator()
		filemenu.add_command(label="System preferences...",underline=7,
			image=self.iconPrefs, compound='left',
			command=lambda e=None:self.SystemPreferences(e))
		filemenu.add_separator()
		filemenu.add_command(label="Quit",underline=0,image=self.iconClose,
			compound='left',accelerator='Ctrl+Q',
			command=lambda e=None:self.quitProgram(e))
		self.DefineAccelerators('c','q',lambda e=None:self.quitProgram(e))
		menubar.add("cascade",label='File',underline=0,menu=filemenu)
		
		viewmenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		
		self.viewImageAttributesPane = BooleanVar()
		self.viewImageAttributesPane.set(True)
		viewmenu.add_checkbutton(label="Image attribute pane",underline=6,
			accelerator='Ctrl+Shift+A',
			onvalue=True,offvalue=False,variable=self.viewImageAttributesPane,
			command=lambda e='Menu':self.ViewImageAttributesPane(e))
		self.DefineAccelerators('cs','a',self.ViewImageAttributesPane)
		
		viewmenu.add_command(label="Properties...",underline=0,accelerator='Ctrl+Alt+P',
			image=self.iconPrefs,compound='left',
			command=lambda e=None:self.ViewProperties(e))
		self.DefineAccelerators('ca','p',lambda e=None:self.ViewProperties(e))
		menubar.add("cascade",label='View',underline=0,menu=viewmenu)
		
		photomenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		photomenu.add_command(label="Take picture",underline=5,
		image=self.iconCamera,compound='left',
			command=lambda e=None:self.TakePicture(e),accelerator='Ctrl+P')
		self.DefineAccelerators('c','p',lambda e=None:self.TakePicture(e))
		photomenu.add_command(label="Toggle video",underline=7,
			image=self.iconVideo,compound='left',
			command=lambda e=None:self.ToggleVideo(e),accelerator='Ctrl+V')
		self.DefineAccelerators('c','v',lambda e=None:self.ToggleVideo(e))
		photomenu.add_command(label="Clear picture",underline=0,
			image=self.iconClose,compound='left',
			command=lambda e=None:self.ClearPicture(e),accelerator='Ctrl+C')
		self.DefineAccelerators('c','c',lambda e=None:self.ClearPicture(e))
		menubar.add("cascade",label='Photo',underline=0,menu=photomenu)
		
		helpmenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		helpmenu.add_command(label="Keyboard shortcuts...",underline=0,
			command=lambda e=None:self.KeyboardShortcuts(e))
		helpmenu.add_command(label="Picamera documentation...",underline=0,
			command=lambda e=None:self.PiCameraDocs(e),image=self.iconWeb,compound='left')
		helpmenu.add_separator()
		helpmenu.add_command(label="About...",underline=0,command=lambda e=None:self.HelpAbout(e))
		menubar.add("cascade",label='Help',underline=0,menu=helpmenu)
		
		root.config(menu=menubar)
		#--------------------------- End Menu --------------------------
		
		# We want to catch window movements to show/hide preview window
		root.bind( '<Configure>', self.OnFormEvent )
		
		root.protocol("WM_DELETE_WINDOW", lambda e=None:self.quitProgram(e))
		
	def ShowHideImageAttributesPane ( self, ShowIt):
		if ShowIt:
			if self.CurrentImage: self.photoPanedWindow.insert(0,self.LeftFrame)
		else: 
			try:
				self.photoPanedWindow.forget(self.LeftFrame)
			except TclError: pass	# Already forgotten!	
			
	def ViewImageAttributesPane ( self, event ):
		if not event == 'Menu':	# Must change variable state ourselves
			self.viewImageAttributesPane.set(not self.viewImageAttributesPane.get())
		self.ShowHideImageAttributesPane(self.viewImageAttributesPane.get())
		
	def TextboxResize ( self, event ):
		pass #print event.width
		
	def SavePictureorVideo ( self, event ):
		# Create a picture class that maintains the state of the current 
		# image. This would include the state of the camera programming
		# just before the image was taken.
		# Store on a PictureStack. In most cases, only one picture on
		# the stack, but can hold more - such as a series of pictures
		# taken in rapid sequence.
		tkFileDialog.asksaveasfile(mode='w',defaultextension='*.jpg')
		
	def photoCanvasScrollStart ( self, event ):
		if self.CurrentImage:
			if event.state & 0x0004 == 0x0004:		# Ctrl key
				self.InPhotoZoom = True
				self.Image = self.CurrentImage
				x = self.photoCanvas.canvasx(event.x)
				y = self.photoCanvas.canvasy(event.y)
				self.photoCanvas.create_rectangle(x,y,x+1,y+1,tags=('zoom','objs'),outline='red')
				self.photoCanvas.config(cursor='sizing')
			else:
				self.photoCanvas.config(cursor='hand1')
				self.photoCanvas.scan_mark(event.x,event.y)
				
	def photoCanvasScrollMove ( self, event ):
		if self.CurrentImage:
			if not self.InPhotoZoom: 
				self.photoCanvas.scan_dragto(event.x,event.y,gain=3)
			self.photoCanvasMove(event)	
			
	def photoCanvasButtonUp ( self, event ):
		self.photoCanvas.config(cursor='diamond_cross')
		if self.InPhotoZoom:
			self.InPhotoZoom = False
			coords = self.photoCanvas.coords('zoom')
			# Set zoom of window.....
			# We should account for previous levels of zoom
			x = float(coords[0]) / float(self.CurrentImageSize[0])
			y = float(coords[1]) /  float(self.CurrentImageSize[1]) 
			width = float(coords[2] - coords[0]) / float(self.CurrentImageSize[0])
			height = float(coords[3] - coords[1]) / float(self.CurrentImageSize[1])
			self.BasicControlsFrame.SetZoom (x,y,width,height)
			#imageself.CurrentImage
			#self.photoCanvas.config(scrollregion=(int(coords[0]),
				#int(coords[1]),int(coords[2]),int(coords[3])))
			self.photoCanvas.delete("zoom")
			
	def photoCanvasMove ( self, event ):
		if not self.CurrentImage: return

		x = self.photoCanvas.canvasx(event.x)
		y = self.photoCanvas.canvasy(event.y)
		self.statusText.set('X: %d Y: %d' % (x, y))		
			
		size = self.CurrentImage.size
		if x >= 0 and x <= size[0] and y >= 0 and y <= size[1]:
			self.photoCanvas.itemconfigure('text',state='normal')
			self.photoCanvas.coords('text',x+5,y+5)
			self.photoCanvas.itemconfigure('text',text='(%d,%d)'%(x,y))
		else:
			self.photoCanvas.itemconfigure('text',state='hidden')

		x0 = self.photoCanvas.canvasx(0)
		x1 = x0 + self.photoCanvas.winfo_width()
		y0 = self.photoCanvas.canvasy(0)
		y1 = y0 + self.photoCanvas.winfo_height()
		self.photoCanvas.coords('cursorx',x,y0,x,y1)
		self.photoCanvas.coords('cursory',x0,y,x1,y)
		if self.InPhotoZoom:
			########### BUGGY - LOOK AT RECT TOTAL TO ANALYZE
			coords = self.photoCanvas.coords('zoom')
			if x < coords[0]:
				x1 = x
				x2 = coords[2]
			else:
				x1 = coords[0]
				x2 = x
			if y < coords[1]:
				y1 = y
				y2 = coords[3]
			else:
				y1 = coords[1]
				y2 = y
			self.photoCanvas.coords('zoom',x1,y1,x2,y2)	
			
	def WheelScrollPhotoCanvas ( self, event ):
		if event.state & 0x0004 == 0x0004:		# Ctrl key
			if not self.CurrentImage: return
			size = self.CurrentImage.size
			if event.num == 4:
				self.photoZoomScale *= 1.1
			else:
				self.photoZoomScale *= (1.0/1.1)
			self.LoadImageFromStream(self.photoZoomScale)
			
	def TakePicture ( self, event ):
		if self.InCaptureVideo: return
		
		photoFormat = self.BasicControlsFrame.GetPhotoCaptureFormat() 
		if photoFormat not in ['jpeg', 'png', 'bmp']:
			tkMessageBox.showwarning("Image view not supported",
				"Cannot directly view images in %s format"%photoFormat)
			return
			
		self.ClearPicture(None)
		self.CameraUtils.FillCameraSettingTextBox(self)
		self.photoCanvas.itemconfigure('cross',state='hidden')
		self.pictureStream.seek(0)	# Use to reload / resize image
		
		try:
			self.camera.capture(self.pictureStream,format=photoFormat,
				use_video_port=self.BasicControlsFrame.UseVideoPort.get(),
				resize=self.BasicControlsFrame.GetResizeAfter())
		except PiCameraRuntimeError:
			raise 'Camera capture error' # Something really bad happened

		self.LoadImageFromStream ( 1.0 )
		self.photoCanvas.itemconfigure('objs',state='normal')
		self.photoCanvas.tag_raise("objs") # raise Z order to topmost
		
	def LoadImageFromStream ( self, zoom ):
		if self.photo: del self.photo
		
		self.pictureStream.seek(0)
		self.CurrentImage = PIL.Image.open(self.pictureStream)
		
		self.CameraUtils.AddEXIFTags(self.CurrentImage)
		self.ShowHideImageAttributesPane(self.viewImageAttributesPane.get())
		
		# resize what's displayed if user used Ctrl+mousewheel
		size = self.CurrentImage.size
		if size[0] <= 1024 and size[1] <= 768:	# hold max zoom level
			width = int(zoom*size[0])
			height = int(zoom*size[1])
			if width <= 1024 and height <= 768:
				self.CurrentImage = self.CurrentImage.resize((width,height),PIL.Image.ANTIALIAS)
		self.CurrentImageSize = self.CurrentImage.size
		
		# Convert to canvas compatible format and store on canvas
		self.photo = ImageTk.PhotoImage(self.CurrentImage)
		self.photoCanvas.delete("pic")
		self.photoCanvas.create_image(0,0,image=self.photo,anchor='nw',tags=('pic'))
		self.photoCanvas.config(scrollregion=self.photoCanvas.bbox(ALL))
		self.photoCanvas.tag_raise("objs") # raise Z order of cursors to topmost
		
	def ToggleVideo ( self, event ):
		self.ClearPicture(None)
		self.InCaptureVideo = not self.InCaptureVideo
		
		if self.InCaptureVideo:
			self.TakeVideo.config(text='Stop')
			self.time = time.time()
			###### TODO - do this as a stream. Can we then play it in
			###### 'realtime' to the user as it's being recorded?
			self.camera.start_recording('__TMP__.h264')
			self.photoCanvas.itemconfigure('capture',state='normal')
			self.after(50,self.UpdateCaptureInProgress)
		else:
			self.TakeVideo.config(text='Video')
			self.camera.stop_recording()
			self.photoCanvas.itemconfigure('capture',state='hidden')
			cmd = 'MP4Box -fps %d -add __TMP__.h264 __TMP__.mp4'%int(self.camera.framerate)
			print cmd
			os.system(cmd)
			os.remove('__TMP__.h264')
			print 'Done'
			
	def UpdateCaptureInProgress ( self ):
		if not self.InCaptureVideo: return
		
		# keep updating video capture time
		delta = time.time() - self.time
		self.photoCanvas.itemconfigure('capture',text='Recording %.2f sec'%delta)
		self.after(50,self.UpdateCaptureInProgress)	# call again
		
	def ClearPicture ( self, event ):
		self.ShowHideImageAttributesPane(False)
		self.CameraUtils.ClearTextBox()
		self.photoCanvas.delete("pic")
		if self.CurrentImage:
			del self.CurrentImage
			del self.photo
		self.CurrentImage = None
		self.photo = None
		self.photoCanvas.itemconfigure('cross',state='normal')
		self.photoCanvas.itemconfigure('objs',state='hidden')
		self.photoCanvas.config(scrollregion=(0,0,1,1))
		
	def ViewProperties ( self, event ):
		pass
		
	def PhotoCanvasResize ( self, event ):
		size = (event.width,event.height)
		x = self.photoCanvas.canvasx(event.x)
		y = self.photoCanvas.canvasy(event.y)
		# either scroll if acxtual size, or size image to fit
		# if sizing to fit, must maintain aspect ratio
		#try:
			#self.photoCanvas.delete("pic")
			## Check which is bigger, width or height
			#if self.CurrentImage[0] <= size[0] and self.CurrentImage[1] <= size[1]:
				#self.photo = ImageTk.PhotoImage(self.CurrentImage)
			#elif self.CurrentImage[0] >= self.CurrentImage[1]:
				## width greater than height
				#resized = self.CurrentImage.resize(size)
				#self.photo = ImageTk.PhotoImage(resized)
			#else:
				#resized = self.CurrentImage.resize(size)
				#self.photo = ImageTk.PhotoImage(resized)

			#self.photoCanvas.create_image(0,0,image=self.photo,anchor='nw')
		#except: print 'Error'
		self.photoCanvas.coords('cross1',0,0,0+size[0],0+size[1])
		self.photoCanvas.coords('cross2',0+size[0],0,0,0+size[1])	
		self.photoCanvas.coords('capture',0+size[0]/2,0+size[1]/2)	
		
	def photoCanvasEnterLeave ( self, event ):
		if not self.CurrentImage: return
		
		state1 = 'normal'		# 7/8 leave enter - getname instead
		if int(event.type) == 8:
			state1 = 'hidden'
			self.statusText.set("")
		self.photoCanvas.itemconfigure('objs',state=state1)

	def CanvasMouseMove ( self, event ):
		res = self.camera.resolution
		canvas = self.CanvasSize
		deltaX = 0
		if res[0] > self.ImageCanvas.winfo_width():
			deltaX = (res[0] - self.ImageCanvas.winfo_width()) / 2
		elif res[0] < self.ImageCanvas.winfo_width():
			deltaX = (self.ImageCanvas.winfo_width() - res[0]) / 2
		else:
			deltaX = 0

		self.statusText.set('%d X: %d Y: W: %d H: %d' % \
			(event.x,event.y,canvas[2],canvas[3]))
		self.ImageCanvas.coords(self.CursorX,0,event.y,
							    self.ImageCanvas.winfo_width(),event.y)
		self.ImageCanvas.coords(self.CursorY,event.x,0,
								event.x,self.ImageCanvas.winfo_height())

	def CanvasEnterLeave ( self, event ):
		state1 = 'normal'		# 7/8 leave enter - getname instead
		if int(event.type) == 8:
			state1 = 'hidden'
			self.statusText.set("")
		self.ImageCanvas.itemconfigure('cursors',state=state1)

	def SetPreviewOn ( self ):
		if self.PreviewOn.get() == False:
			self.camera.stop_preview()
			state = 'disabled'
			self.ImageCanvas.itemconfigure('nopreview',state='normal')
		else:
			self.camera.start_preview(alpha=int(self.alpha.get()), \
				fullscreen=False,window=self.CanvasSize, \
				vflip=self.VFlipState, hflip=self.HFlipState)
			self.ImageCanvas.itemconfigure('nopreview',state='hidden')
			state = '!disabled'
		self.alpha.state([state])
		self.Hflip.config(state=state)
		self.Vflip.config(state=state)

	def AlphaChanged(self, newVal):
		val = int(float(newVal))
		self.camera.preview.alpha = val
		self.alpha.focus_set()
		
	def ToggleHFlip ( self ):
		self.HFlipState = not self.HFlipState
		self.camera.preview.hflip = not self.camera.preview.hflip
		
	def ToggleVFlip ( self ):
		self.VFlipState = not self.VFlipState
		self.camera.preview.vflip = not self.camera.preview.vflip

	def LoseFocus ( self, event ):
		'''
		The Combobox is a problem.
		could save last two entries... if Combobox, Labelframe, Tk...
		NO! this could be the Topwindow losing focus while the
		Combobox has the focus.  The same effect
		Also, the nesting may vary based on where the Combobox is in
		the hierarcy. What I really want is to capture the <B1-Motion>
		on the TopWindow titlebar - OR - get the widget ID to the
		Combobox Toplevel dropdown window.
		'''
		if self.camera.preview and not self.AlwaysPreview and \
			event.widget.winfo_class().lower() == 'tk' and \
			self.root.attributes("-topmost") == 0: # TopMost window hack
			self.camera.preview.alpha = 0
			self.ImageCanvas.itemconfigure('nopreview',state='normal')
			
	def GotFocus ( self, event ):
		if self.camera.preview and not self.AlwaysPreview and \
			event.widget.winfo_class().lower() == 'tk' and \
			self.PreviewOn.get() and self.ImageCanvas.winfo_height() > 50:
			self.camera.preview.alpha = int(self.alpha.get())
			self.ImageCanvas.itemconfigure('nopreview',state='hidden')

	# We're catching the main form event to tell when a window has moved.
	# The preview window can be blanked during this time.
	def OnFormEvent ( self, event ):
		# hack fix for PI running on HDTV. Related to overscan?
		screenwidth = self.ImageCanvas.winfo_screenwidth()
		screenheight = self.ImageCanvas.winfo_screenheight()
		deltaWidth = 0
		deltaHeight = 0
		if screenwidth > 1800 and screenwidth <= 1920:
			deltaWidth = (1920 - screenwidth) / 2
			deltaHeight = (1080 - screenheight) / 2
			
		# get size and lopcation of preview window canvas ...
		self.CanvasSize = (self.ImageCanvas.winfo_rootx()+deltaWidth,
			  self.ImageCanvas.winfo_rooty()+deltaHeight,
			  self.ImageCanvas.winfo_width(),
			  self.ImageCanvas.winfo_height())
		# ... and reset preview window to this position
		if self.camera.preview != None:
			self.camera.preview.window = self.CanvasSize
			# Hide preview window if too small
			if self.CanvasSize[3] <= 50:
				self.camera.preview.alpha = 0
			elif self.PreviewOn.get():
				self.camera.preview.alpha = int(self.alpha.get())
		# Not sure this should be here... could place inside the
		# preview window canvas form event. Cleaner approach. 
		self.ImageCanvas.coords("nopreview",self.ImageCanvas.winfo_width()/2,
								self.ImageCanvas.winfo_height()/2)

	def SystemPreferences ( self, event ):
		PreferencesDialog(self,title='System Preferences',camera=self.camera,
			minwidth=300,minheight=500)
		self.ControlMapping.SetControlMapping()

	def KeyboardShortcuts ( self, event ):
		KeyboardShortcutsDialog(self,title='Keyboard shortcuts')
		
	def PiCameraDocs ( self, event ):
		webbrowser.open_new('http://picamera.readthedocs.org/en/release-1.10/')

	def HelpAbout ( self, event ):
		AboutDialog(self,title="About PiCamera Demonstration")

	def quitProgram ( self, event ):
		if tkMessageBox.askyesno("Quit program","Exit %s?" % self.title):
			self.master.destroy()
			
	def GPIOError ( self ):
		if not RPiGPIO:
			tkMessageBox.showerror("GPIO Error",
				"GPIO library not found\n" + \
				"Please install RPi.GPIO and run this program as root.")
		else: 
			tkMessageBox.showerror("GPIO Error",
				"To control the PiCamera LED, you must run this program as 'root'")	 
				
	def DefineAccelerators ( self, keys, char, callFunc ):
		commandDic = {'c':'Control-','a':'Alt-','s':'Shift-','f':''}
		cmd = '<'
		for c in keys.lower():	# need to handle function keys too...
			cmd = cmd + commandDic[c]
		cmd1 = cmd
		cmd = cmd + char.upper() + ">"
		self.root.bind(cmd,callFunc)
		if len(char) == 1:
			cmd1 = cmd1 + char.lower() + ">"
			self.root.bind(cmd1,callFunc)
	
class BasicControls ( BasicNotepage ):
	def BuildPage ( self ):
		f1 = Labelframe(self,text='Test',padding=(5,5,5,5))
		f1.grid(row=0,column=0,columnspan=2,sticky='NSEW')

		self.UseVideoPort = BooleanVar()
		self.UseVideoPort.set(False)
		Checkbutton(f1,text='Use video port',variable=self.UseVideoPort,
			padding=(0,0,10,0)).grid(row=0,column=0,sticky='NW')

		self.LedOn = BooleanVar()
		self.LedOn.set(True)
		b1 = Checkbutton(f1,text='Led On',variable=self.LedOn,
			padding=(0,0,10,0),command=self.LedOnChecked)
		b1.grid(row=0,column=1,sticky='NW')
		# Latest version (not Wheezy) doesn't need to be 'root' to access
		# GPIO. Need test for this. Try toggling Led state, if error, then
		# we show the error message, else assume all OK.
		if not RPiGPIO or not (os.getenv("USER") == 'root'):
			b1.config(state='disabled')
			self.after(1000,self.GPIOError)	# Post message		
		
		f = LabelFrame(self,text='Picture/Video capture size in pixels',
			padding=(5,5,5,5))
		f.grid(row=1,column=0,sticky='NEWS',pady=5)
		f.columnconfigure(0,weight=1)

		f1 = Frame(f)
		f1.grid(row=1,column=0,sticky='NSEW')
		f1.columnconfigure(1,weight=1)
		self.UseFixedResolutions = BooleanVar()
		self.UseFixedResolutions.set(True)
		b1 = Radiobutton(f1,text='Use fixed:',variable=self.UseFixedResolutions,
			value=True,command=self.UseFixedResRadios,padding=(5,5,5,5))
		b1.grid(row=0,column=0,sticky='NW')
		self.FixedResolutionsCombo = Combobox(f1,state='readonly')
		self.FixedResolutionsCombo.bind('<<ComboboxSelected>>',self.FixedResolutionChanged)
		self.FixedResolutionsCombo.grid(row=0,column=1,sticky='EW')
		#------------ Capture Width and Height ----------------
		# OrderedDict is used to ensure the keys stay in the same order as
		# entered. I want the combobox to display in this order
		# ---- Must check resolution and framerate and disable the Video
		# button if we exceed limits of the modes
		# Framerate 1-30 fps up to 1920x1080		16:9 aspect ratio
		# Framerate 1-15 fps up to 2592 x 1944		 4:3 aspect ratio
		# Framerate 0.1666 to 1 fps up to 2592 x 1944 4:3 aspect ratio
		# Framerate 1-42 fps up t0 1296 x 972 		 4:3 aspect ratio
		# Framerate 1-49 fps up to 1296 x 730		16:9 aspect ratio
		# Framerate 42.1 - 60 fps to 640 x 480		 4:3 aspect ratio
		# Framerate 60.1 - 90 fps to 640 x 480		 4:3 aspect ratio  
		self.StandardResolutions = OrderedDict([ \
			('CGA', (320,200)),			('QVGA', (320,240)),
			('VGA', (640,480)),			('PAL', (768,576)),
			('480p', (720,480)),		('576p', (720,576)),
			('WVGA', (800,480)),		('SVGA', (800,600)),
			('FWVGA', (854,480)),		('WSVGA', (1024,600)),
			('XGA', (1024,768)),		('HD 720', (1280,720)),
			('WXGA_1', (1280,768)),		('WXGA_2', (1280,800)),
			('SXGA', (1280,1024)),		('SXGA+', (1400,1050)),
			('UXGA', (1600,1200)),		('WSXGA+', (1680,1050)),
			('HD 1080', (1920,1080)), 	('WUXGA', (1920,1200)),
			('2K', (2048,1080)),		('QXGA', (2048, 1536)),
			('WQXGA', (2560,1600)),		('MAX Resolution', (2592,1944)),
		   ])
		vals = []
		for key in self.StandardResolutions.keys():
			vals.append('%s:    	\t (%dx%d)' % (key,
										self.StandardResolutions[key][0],
										self.StandardResolutions[key][1]))
		self.FixedResolutionsCombo['values'] = vals
		self.FixedResolutionsCombo.current(10)

		f2 = Frame(f)
		f2.grid(row=2,column=0,sticky='NSEW')
		f2.columnconfigure(2,weight=1)
		f2.columnconfigure(4,weight=1)
		b2 = Radiobutton(f2,text='Roll your own:',variable=self.UseFixedResolutions,
			value=False,command=self.UseFixedResRadios,padding=(5,5,5,5))
		b2.grid(row=1,column=0,sticky='NW')

		l2 = Label(f2,text="Width:",anchor=E)
		l2.grid(column=1,row=1,sticky='E',ipadx=3,ipady=3)
		self.cb = Combobox(f2,state='disabled',width=5)
		self.cb.bind('<<ComboboxSelected>>',self.ResolutionChanged)
		self.cb.grid(row=1,column=2,sticky='EW')
		Widths = []
		for i in xrange(1,82):
			Widths.append(32 * i) # Widths can be in 32 byte increments
		self.cb['values'] = Widths
		self.cb.current(10)

		l2 = Label(f2,text="Height:",anchor=E)
		l2.grid(column=3,row=1,sticky='W',ipadx=5,ipady=3)
		self.cb1 = Combobox(f2,state='disabled',width=5)
		self.cb1.bind('<<ComboboxSelected>>',self.ResolutionChanged)
		self.cb1.grid(row=1,column=4,sticky='EW')
		Heights = []
		for i in xrange(1,123):
			Heights.append(16 * i)	# heights in 16 byte increments
		self.cb1['values'] = Heights
		self.cb1.current(10)

		Label(f2,text='Actual:').grid(row=2,column=1,sticky='E')
		self.WidthLabel = Label(f2,style='DataLabel.TLabel')
		self.WidthLabel.grid(row=2,column=2,sticky='W')
		Label(f2,text='Actual:').grid(row=2,column=3,sticky='E')
		self.HeightLabel = Label(f2,style='DataLabel.TLabel')
		self.HeightLabel.grid(row=2,column=4,sticky='W')

		Separator(f,orient=HORIZONTAL).grid(pady=5,row=3,column=0,
			columnspan=3,sticky='EW')

		f4 = LabelFrame(f,text='Zoom region of interest before taking '+
			'picture/video',padding=(10,5,10,5))
		f4.grid(row=4,column=0,sticky='NSEW',padx=10)
		f4.columnconfigure(1,weight=1)
		f4.columnconfigure(3,weight=1)
		Label(f4,text='X:').grid(row=0,column=0,sticky='E')
		self.Xzoom = Scale(f4,from_=0.0,to=0.94,orient='horizontal')
		self.Xzoom.grid(row=0,column=1,sticky='NSEW',padx=5,pady=3)
		self.Xzoom.set(0.0)
		Label(f4,text='Y:').grid(row=0,column=2,sticky='E')
		self.Yzoom = Scale(f4,from_=0.0,to=0.94,orient='horizontal')
		self.Yzoom.grid(row=0,column=3,sticky='NSEW',padx=5,pady=3)
		self.Yzoom.set(0.0)
		Label(f4,text='Width:').grid(row=1,column=0,sticky='E')
		self.Widthzoom = Scale(f4,from_=0.05,to=1.0,orient='horizontal')
		self.Widthzoom.grid(row=1,column=1,sticky='NSEW',padx=5,pady=3)
		self.Widthzoom.set(1.0)
		Label(f4,text='Height:').grid(row=1,column=2,sticky='E')
		self.Heightzoom = Scale(f4,from_=0.05,to=1.0,orient='horizontal')
		self.Heightzoom.grid(row=1,column=3,sticky='NSEW',padx=5,pady=3)
		self.Heightzoom.set(1.0)
		b = Button(f4,text='Reset',width=5,command=self.ZoomReset)
		b.grid(row=0,column=4,rowspan=2,sticky='W')

		self.Xzoom.config(command=lambda newval,widget=self.Xzoom:self.Zoom(newval,widget))
		self.Yzoom.config(command=lambda newval,widget=self.Yzoom:self.Zoom(newval,widget))
		self.Widthzoom.config(command=lambda newval,widget=self.Widthzoom:self.Zoom(newval,widget))
		self.Heightzoom.config(command=lambda newval,widget=self.Heightzoom:self.Zoom(newval,widget))

		Separator(f,orient=HORIZONTAL).grid(pady=10,row=5,column=0,
			columnspan=3,sticky='EW')

		f4 = LabelFrame(f,text='Resize image after taking picture/video',
			padding=(10,5,10,5))
		f4.grid(row=6,column=0,sticky='NSEW',padx=10)
		f4.columnconfigure(3,weight=1)
		f4.columnconfigure(5,weight=1)		
		
		ResizeAfter = BooleanVar()
		ResizeAfter.set(False)
		b1 = Radiobutton(f4,text='None (Default)',variable=ResizeAfter,
			value=False,command=lambda : self.AllowImageResizeAfter(False),
			padding=(0,5,0,5))
		b1.grid(row=0,column=0,sticky='W')
		b2 = Radiobutton(f4,text='Resize',variable=ResizeAfter,
			value=True,command=lambda : self.AllowImageResizeAfter(True),
			padding=(5,5,0,5))
		b2.grid(row=0,column=1,sticky='W')
		
		l2 = Label(f4,text="Width:",anchor=E)
		l2.grid(column=2,row=0,sticky='E',ipadx=3,ipady=3)
		self.resizeWidthAfterCombo = Combobox(f4,state='disabled',width=5)
		self.resizeWidthAfterCombo.bind('<<ComboboxSelected>>',self.ResizeAfterChanged)
		self.resizeWidthAfterCombo.grid(row=0,column=3,sticky='EW')
		self.resizeWidthAfterCombo['values'] = Widths
		self.resizeWidthAfterCombo.current(10)

		l2 = Label(f4,text="Height:",anchor=E)
		l2.grid(column=4,row=0,sticky='W',ipadx=5,ipady=3)
		self.resizeHeightAfterCombo = Combobox(f4,state='disabled',width=5)
		self.resizeHeightAfterCombo.bind('<<ComboboxSelected>>',self.ResizeAfterChanged)
		self.resizeHeightAfterCombo.grid(row=0,column=5,sticky='EW')
		self.resizeHeightAfterCombo['values'] = Heights
		self.resizeHeightAfterCombo.current(10)
		
		self.resizeAfter = None

		f = LabelFrame(self,text='Quick adjustments',padding=(5,5,5,5))
		f.grid(row=2,column=0,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)
		#------------ Brightness ----------------
		self.brightLabel, self.brightness, val = \
			self.SetupLabelCombo(f,'Brightness:',1,0, 100,
				self.CameraBrightnessChanged, self.camera.brightness )
		self.CameraBrightnessChanged(val)
		#------------ Contrast ----------------
		self.contrastLabel, self.contrast, val = \
			self.SetupLabelCombo(f,'Contrast:',2,-100, 100,
				self.ContrastChanged, self.camera.contrast )
		self.ContrastChanged(val)
		#------------ Saturation ----------------
		self.saturationLabel, self.saturation, val = \
			self.SetupLabelCombo(f,'Saturation:',3,-100, 100,
				self.SaturationChanged, self.camera.saturation )
		self.SaturationChanged(val)
		#------------ Sharpness ----------------
		self.sharpnessLabel, self.sharpness, val = \
			self.SetupLabelCombo(f,'Sharpness:',4,-100, 100,
				self.SharpnessChanged, self.camera.sharpness )
		self.SharpnessChanged(val)
		#------------ Reset ----------------
		self.ResetGeneral = Button(f,text='Set defaults',underline=4,
			command=self.ResetGeneralSliders,padding=(0,3,0,3))
		self.ResetGeneral.grid(row=5,column=2,columnspan=2,sticky=EW,padx=5)

		f = LabelFrame(self,text='Preprogrammed image effects',padding=(5,5,5,5))
		f.grid(row=3,column=0,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)

		v = BooleanVar()
		v.set(False)
		b1 = Radiobutton(f,text='None (Default)',variable=v,value=False,
			command=lambda:self.EffectsChecked(False),padding=(5,5,5,5))
		b1.grid(row=0,column=0,sticky='W')

		b2 = Radiobutton(f,text='Select effect:',variable=v,value=True,
			command=lambda:self.EffectsChecked(True),padding=(5,5,5,5))
		b2.grid(row=0,column=1,sticky='W')

		self.effects = Combobox(f,height=15,width=10,state='readonly')#,width=15)
		self.effects.grid(row=0,column=2,sticky='EW')
		effects = self.camera.IMAGE_EFFECTS.keys()
		effects.remove('none')
		effects.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()))
		self.effects['values'] = effects
		self.effects.current(0)
		self.effects.bind('<<ComboboxSelected>>',self.EffectsChanged)
		self.ModParams = Button(f,text='Params...',command=self.ModifyParamPressed,
			underline=0,padding=(5,3,5,3),width=8)
		self.ModParams.grid(row=0,column=3,sticky=EW,padx=5)
		self.EffectsChecked(False)

		f = LabelFrame(self,text='Image/Video enables',padding=(5,5,5,5))
		f.grid(row=4,column=0,sticky='NEWS',pady=5)
		
		self.VideoStab = BooleanVar()
		self.VideoStab.set(False)
		Checkbutton(f,text='Video stabilzation',variable=self.VideoStab,
			command=self.VideoStabChecked).grid(row=0,column=0,sticky='NW')

		self.VideoDenoise = BooleanVar()
		self.VideoDenoise.set(True)
		Checkbutton(f,text='Video denoise',variable=self.VideoDenoise,
			command=self.VideoDenoiseChecked).grid(row=0,column=1,sticky='NW')

		self.ImageDenoise = BooleanVar()
		self.ImageDenoise.set(True)
		Checkbutton(f,text='Image denoise',variable=self.ImageDenoise,
			command=self.ImageDenoiseChecked).grid(row=0,column=2,sticky='NW',padx=10)
		
		Label(f,text='Photo capture format',padding=(5,5,5,5)).grid(row=1,column=0,sticky='W')
		self.photoCaptureFormat = 'jpeg'
		self.photoCaptureFormatCombo = Combobox(f,height=15,width=3,state='readonly')#,width=15)
		self.photoCaptureFormatCombo.grid(row=1,column=1,sticky='EW')
		self.photoCaptureFormatCombo['values'] = ['jpeg','png','bmp',
			'gif','yuv','rgb','rgba','bgr','bgra','raw']
		self.photoCaptureFormatCombo.current(0)
		self.photoCaptureFormatCombo.bind('<<ComboboxSelected>>',self.photoCaptureFormatChanged)

		self.FixedResolutionChanged(None)
		
	# NEEDS LOTS OF WORK!!
	def Reset ( self ):
		# Use widget.invoke() to simulate a button/radiobutton press
		self.VideoStab.set(False)		# Doesn't call the function!
		self.VideoDenoise.set(True)
		self.ImageDenoise.set(True)
		self.ResetGeneralSliders()
	def LedOnChecked ( self ):
		self.camera.led = self.LedOn.get()
	def photoCaptureFormatChanged ( self, event ):
		self.photoCaptureFormat = self.photoCaptureFormatCombo.get()
	def GetPhotoCaptureFormat ( self ):
		return self.photoCaptureFormat
	def SetupLabelCombo ( self, parent, textname, rownum, minto, maxto,
						  callback, cameraVal ):
		l = Label(parent,text=textname)
		l.grid(row=rownum,column=0,sticky=W,pady=2)#,padx=2)
		label = Label(parent,width=4,anchor=E)#,relief=SUNKEN, background='#f0f0ff')
		label.grid(row=rownum,column=1)
		label.config(font=('Helvetica',12))
		# create the scale WITHOUT a callback. Then set the scale.
		scale = Scale(parent,from_=minto,to=maxto,orient='horizontal')
		scale.grid(row=rownum,column=2,columnspan=2,sticky='NSEW',padx=5,pady=3)
		val = cameraVal
		scale.set(val)		# this would attempt to call any callback
		scale.config(command=callback)	# now supply the callback
		return label, scale, val
	def UpdateMe( self, newVal, label ):
		val = int(float(newVal))
		label.config(text='%d' % val,
			foreground='red' if val < 0 else 'blue' if val > 0 else 'black' )
		return val
	def CameraBrightnessChanged ( self, newVal ):
		self.brightness.focus_set()
		self.camera.brightness = self.UpdateMe(newVal,self.brightLabel)
	def ContrastChanged ( self, newVal ):
		self.contrast.focus_set()
		self.camera.contrast = self.UpdateMe(newVal,self.contrastLabel)
	def SaturationChanged ( self, newVal ):
		self.saturation.focus_set()
		self.camera.saturation = self.UpdateMe(newVal,self.saturationLabel)
	def SharpnessChanged ( self, newVal ):
		self.sharpness.focus_set()
		self.camera.sharpness = self.UpdateMe(newVal,self.sharpnessLabel)
	def ResetGeneralSliders ( self ):
		self.brightness.set(50)
		self.contrast.set(0)
		self.saturation.set(0)
		self.sharpness.set(0)
		self.ResetGeneral.focus_set()
	def UpdateWidthHeightLabels ( self ):
		res = self.camera.resolution # in case a different default value
		self.WidthLabel.config(text='%d' % int(res[0]))
		self.HeightLabel.config(text='%d' % int(res[1]))		
	def ResolutionChanged(self,event):
		self.camera.resolution = (int(self.cb.get()),
								  int(self.cb1.get()))
		self.UpdateWidthHeightLabels()
	def FixedResolutionChanged ( self, event ):
		key = self.FixedResolutionsCombo.get().split(':')[0]
		self.camera.resolution = self.StandardResolutions[key]
		self.UpdateWidthHeightLabels()
	def UseFixedResRadios ( self ):
		states = {False:'disabled', True:'readonly'}
		useFixedRes = self.UseFixedResolutions.get()
		if useFixedRes:
			self.FixedResolutionChanged(None)
		else:
			self.ResolutionChanged(None)
		self.FixedResolutionsCombo.config(state=states[useFixedRes])
		self.cb.config(state=states[not useFixedRes])
		self.cb1.config(state=states[not useFixedRes])
	def Zoom ( self, newVal, scale ):
		self.camera.zoom = (float(self.Xzoom.get()),float(self.Yzoom.get()),
			float(self.Widthzoom.get()),float(self.Heightzoom.get()))
		scale.focus_set()
	def SetZoom ( self, x, y, w, h ):
		self.Xzoom.set(x)
		self.Yzoom.set(y)
		self.Widthzoom.set(w)
		self.Heightzoom.set(h)		
	def ZoomReset ( self ):
		self.Xzoom.set(0.0)
		self.Yzoom.set(0.0)
		self.Widthzoom.set(1.0)
		self.Heightzoom.set(1.0)
	def AllowImageResizeAfter ( self, allowResizeAfter ):
		if allowResizeAfter:
			state = 'readonly'
			self.ResizeAfterChanged(None)
		else:
			self.resizeAfter = None
			state = 'disabled'	
		self.resizeWidthAfterCombo.config(state=state)
		self.resizeHeightAfterCombo.config(state=state)		
	def ResizeAfterChanged ( self, event ):
		self.resizeAfter = ( int(self.resizeWidthAfterCombo.get()),
							 int(self.resizeHeightAfterCombo.get()) )
	def GetResizeAfter ( self ):
		return self.resizeAfter
	def EffectsChecked ( self, EffectsEnabled ):
		if EffectsEnabled == True:
			self.effects.config(state='readonly')
			self.EffectsChanged(None)
		else:
			self.effects.config(state='disabled')
			self.ModParams.config(state='disabled')
			self.camera.image_effect = 'none'
	def EffectsChanged ( self, event ):
		self.camera.image_effect = self.effects.get()
		if self.camera.image_effect_params == None:
			self.ModParams.config(state='disabled')
		else:
			self.ModParams.config(state='normal')
	def ModifyParamPressed ( self ):
		''' If available, bring up a dialog that allows the user to change
		 values. The dialog will be different for each entry '''
		pass
	def ImageDenoiseChecked ( self ):
		self.camera.image_denoise = self.ImageDenoise.get()
	def VideoDenoiseChecked ( self ):
		self.camera.video_denoise = self.VideoDenoise.get()
	def VideoStabChecked ( self ):
		self.camera.video_stabilization = self.VideoStab.get()

class FinerControl ( BasicNotepage ):
	def BuildPage ( self ):
		f = LabelFrame(self,text='Auto white balance settings',padding=(5,5,5,5))
		f.grid(row=0,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)
		f.columnconfigure(4,weight=1)

		modes = [('Auto','auto'),('Select:','sel'),('Off','off')]
		self.AutoAWB = StringVar()
		self.AutoAWB.set(modes[0][1])
		for i, mode in enumerate(modes):
			b1 = Radiobutton(f,text=mode[0],variable=self.AutoAWB,value=mode[1],
				command=lambda val=mode[1]:self.AutoAWBChecked(val),padding=(5,5,5,5))
			b1.grid(row=i,column=0,sticky='NW')

		Label(f,text='Default').grid(row=0,column=1,sticky='E')
		Label(f,text='Mode:').grid(row=1,column=1,sticky=E,pady=5)
		self.awb = Combobox(f,state='readonly')#,width=10)
		self.awb.grid(row=1,column=2,columnspan=3,sticky='EW')
		self.awb.bind('<<ComboboxSelected>>',self.AWBModeChanged)
		modes = self.camera.AWB_MODES.keys()
		modes.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()))
		modes.remove('off')	# these two are handled by the radiobuttons
		modes.remove('auto')
		self.awb['values'] = modes
		self.awb.current(0)

		okCmd = (self.register(self.ValidateGains),'%P')
		Label(f,text='Red gain:').grid(row=2,column=1,sticky=E)
		self.RedGain = StringVar()
		self.RedEntry = Entry(f,textvariable=self.RedGain,width=5,
			validate='all',validatecommand=okCmd)
		self.RedEntry.grid(row=2,column=2,sticky='EW')
		
		Label(f,text='Blue gain:').grid(row=2,column=3,sticky=W)
		self.BlueGain = StringVar()
		self.BlueEntry = Entry(f,textvariable=self.BlueGain,width=5,
			validate='all',validatecommand=okCmd)
		self.BlueEntry.grid(row=2,column=4,sticky='EW')

		# Change this to a text field... then it can easily be scrolled
		# if needed.
		l = Label(f,text="Adjust the camera's Auto White Balance gains.\n" +
			"Each gain must be between 0.0 and 8.0\n" +
			"Typical values are between 0.9 and 1.9.",style='RedMessage.TLabel')
		l.grid(row=3,column=1,columnspan=4,sticky='EW')

		f = LabelFrame(self,text='Dynamic range compression',padding=(5,5,5,5))
		f.grid(row=1,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)

		DrcEnable = BooleanVar()
		DrcEnable.set(False)
		b1 = Radiobutton(f,text='Disabled (Default)',variable=DrcEnable,
			value=False,command=lambda:self.DrcChecked(False),padding=(0,5,10,5))
		b1.grid(row=0,column=0,sticky='W')
		b2 = Radiobutton(f,text='Enabled',variable=DrcEnable,
			value=True,command=lambda:self.DrcChecked(True),padding=(0,5,10,5))
		b2.grid(row=0,column=1,sticky='W')
		self.DrcCombo = Combobox(f,state='readonly')#,width=10)
		self.DrcCombo.grid(row=0,column=2,sticky='EW')
		vals = self.camera.DRC_STRENGTHS
		vals = vals.keys()
		vals.remove('off')
		self.DrcCombo['values'] = vals
		self.DrcCombo.current(0)
		self.DrcCombo.bind('<<ComboboxSelected>>',self.DrcStrengthChanged)

		f = LabelFrame(self,text='Color effects (Luminance and Chrominance - YUV420)',
			padding=(5,5,5,5))
		f.grid(row=2,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(1,weight=1)

		AddColorEffect = BooleanVar()
		AddColorEffect.set(False)
		b1 = Radiobutton(f,text='No added color effect (Default)',variable=AddColorEffect,
			value=False,command=lambda:self.AddColorEffect(False),padding=(5,5,5,5))
		b1.grid(row=0,column=0,columnspan=2,sticky=W)
		b2 = Radiobutton(f,text='Add color effect',variable=AddColorEffect,
			value=True,command=lambda:self.AddColorEffect(True),padding=(5,5,5,5))
		b2.grid(row=1,column=0,sticky=W)

		self.luminance = Label(f,text='Luminance is changed through the Brightness slider',
			style='RedMessage.TLabel')
		self.luminance.grid(row=4,column=0,columnspan=3,sticky='W')
		self.YUV = Label(f,width=20,style='DataLabel.TLabel')
		self.YUV.grid(row=5,column=0,sticky='W')
		self.RGB = Label(f,style='DataLabel.TLabel')
		self.RGB.grid(row=5,column=1,columnspan=2,sticky='W')

		self.Color = Canvas(f,width=10,height=32)
		self.Color.grid(row=6,column=0,columnspan=3,sticky="NEWS")
		self.colorbg = self.Color.cget('background')

		self.uLabel = Label(f,text='U chrominance:',padding=(20,2,0,2))
		self.uLabel.grid(row=2,column=0,sticky='W')
		self.uScale = Scale(f,from_=0,to=255, \
				orient='horizontal',length=50)
		self.uScale.grid(row=2,column=1,sticky='NSEW',pady=2)
		self.uScale.set(128)
		self.uScale.config(command=self.uValueChanged)
		self.vLabel = Label(f,text='V chrominance:',padding=(20,2,0,2))
		self.vLabel.grid(row=3,column=0,sticky='W')
		self.vScale = Scale(f,from_=0,to=255, \
				orient='horizontal',length=50)
		self.vScale.grid(row=3,column=1,sticky='NSEW',pady=2)
		self.vScale.set(128)
		self.vScale.config(command=self.vValueChanged)

		f = LabelFrame(self,text='Sensor mode',padding=(5,5,5,5))
		f.grid(row=3,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(1,weight=1)

		# See PiCamera documentation - nothing happens unless the camera
		# is already initialized to a value other than 0 (Auto)
		l = Label(f,text='Sensor mode changes may not work! Some bugs',
			style='RedMessage.TLabel')
		l.grid(row=3,column=0,columnspan=2,sticky='W')

		AutoSensorMode = BooleanVar()
		AutoSensorMode.set(True)
		# Select input mode based of Resolution and framerate:',
		b1 = Radiobutton(f,text='Auto (Default mode 0)',variable=AutoSensorMode,
			value=True,command=lambda:self.AutoSensorModeRadio(True),
			padding=(5,5,5,5))
		b1.grid(row=1,column=0,columnspan=2,sticky='NW')

		b2 = Radiobutton(f,text='Select Mode:',variable=AutoSensorMode,
			value=False,command=lambda:self.AutoSensorModeRadio(False),
			padding=(5,5,5,5))
		b2.grid(row=2,column=0,sticky='NW')

		self.SensorModeCombo = Combobox(f,state='disabled')#,width=30)
		self.SensorModeCombo.grid(row=2,column=1,sticky='EW')
		self.SensorModeCombo['values'] = [ \
			'Mode 1: to 1920x1080 1-30 fps ',
			'Mode 2: to 2592x1944 1-15 fps Image',
			'Mode 3: to 2592x1944 0.1666-1 fps Image',
			'Mode 4: to 1296x972  1-42 fps',
			'Mode 5: to 1296x730  1-49 fps',
			'Mode 6: to 640x480   42.1-60 fps',
			'Mode 7: to 640x480   60.1-90 fps',
			]
		self.SensorModeCombo.current(0)
		self.SensorModeCombo.bind('<<ComboboxSelected>>',self.SensorModeChanged)

		f = LabelFrame(self,text='Flash mode',padding=(5,5,5,5))
		f.grid(row=4,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(3,weight=1)

		self.FlashModeButtons = []	# Not really needed, just Default radio
		modes = [('Off (Default)','off'),('Auto','auto'),('Select:','set')]
		FlashMode = StringVar()
		FlashMode.set(modes[0][1])
		for i, mode in enumerate(modes):
			b = Radiobutton(f,text=mode[0],variable=FlashMode,value=mode[1],
				command=lambda val=mode[1]:self.FlashModeButton(val),
				padding=(5,5,5,5))
			b.grid(row=0,column=i,sticky='W')
			self.FlashModeButtons.append(b)
		# Use invoke() on radio button to force a command
		self.FlashModeCombo = Combobox(f,state='readonly',width=10)
		self.FlashModeCombo.grid(row=0,column=3,sticky='EW')
		self.FlashModeCombo.bind('<<ComboboxSelected>>',self.FlashModeChanged)
		modes = self.camera.FLASH_MODES.keys()
		modes.remove('off')		# these two are handled by radio buttons
		modes.remove('auto')
		modes.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()))
		self.FlashModeCombo['values'] = modes
		self.FlashModeCombo.current(0)
		self.FlashModeCombo.config(state='disabled')

		self.AddColorEffect(False)
		self.DrcChecked(False)
		self.AutoAWBChecked('auto')
		self.ShowAWBGains()
	def ValidateGains ( self, EntryIfAllowed ):
		if EntryIfAllowed == '' or EntryIfAllowed == '.':
			val = 0.0	# special cases handled here
		else:
			try:	val = float(EntryIfAllowed)
			except:	val = -1.0
		return val >= 0.0 and val <= 8.0
	def UpdateGains ( self ):
		def ToFloat ( val ): return float(0.0 if val == '' or val == '.' else val)
		self.camera.awb_gains = (ToFloat(self.RedEntry.get()),
								 ToFloat(self.BlueEntry.get()))
	def AutoAWBChecked ( self, AwbMode ):
		if AwbMode == 'auto' or AwbMode == 'sel':
			self.camera.awb_mode = 'auto' if AwbMode == 'auto' else self.awb.get()
			self.ShowAWBGains()
		else:	# 'off'
			gains = self.camera.awb_gains
			self.camera.awb_mode = 'off'
			self.RedGain.set('%.3f' % gains[0])
			self.BlueGain.set('%.3f' % gains[1])
			self.camera.awb_gains = gains
		self.awb.config(state='readonly' if AwbMode == 'sel' else 'disabled')
		self.RedEntry.config(state='normal' if AwbMode == 'off' else 'disabled')
		self.BlueEntry.config(state='normal' if AwbMode == 'off' else 'disabled')
	def ShowAWBGains ( self ):
		if not self.AutoAWB.get() == 'off':
			gains = self.camera.awb_gains
			self.RedGain.set('%.3f' % gains[0])
			self.BlueGain.set('%.3f' % gains[1])
		else:
			self.UpdateGains()
		self.after(300,self.ShowAWBGains)
	def AWBModeChanged ( self, event ):
		self.camera.awb_mode = self.awb.get()
	def DrcChecked ( self, DrcEnabled ):
		if DrcEnabled == False:
			self.camera.drc_strength = 'off'
			self.DrcCombo.config(state = 'disabled')
		else:
			self.DrcStrengthChanged(None)
			self.DrcCombo.config(state = 'readonly')
	def DrcStrengthChanged ( self, event ):
		self.camera.drc_strength = self.DrcCombo.get()
	def AddColorEffect ( self, EnableColorEffect ):
		if EnableColorEffect == True:
			self.uvValueChanged()
			s = '!disabled'
			self.Color.grid()	# show them
			self.YUV.grid()
			self.RGB.grid()
			self.luminance.grid()
		else:
			self.camera.color_effects = None
			s = 'disabled'
			self.Color.grid_remove()	# hide them
			self.YUV.grid_remove()
			self.RGB.grid_remove()
			self.luminance.grid_remove()
		self.uScale.state([s])	# why is this different?
		self.vScale.state([s])
	def uvValueChanged ( self ):
		def Clamp ( color ):
			return 0 if color <= 0 else 255 if color >= 255 else int(color)
		y = int(255 * float(self.camera.brightness) / 100.0)
		u = int(self.uScale.get())
		v = int(self.vScale.get())
		self.camera.color_effects = (u,v)
		# Y'UV420 to RGB - see Wikipedia  - conversion for Android
		red = Clamp(y + 1.370705 * (v-128))
		green = Clamp(y - 0.337633 * (u-128) - 0.698001 * (v-128))
		blue = Clamp(y + 1.732446 * (u-128))
		self.YUV.config(text='Y: %03d U: %03d V: %03d' % (y,u,v))
		self.RGB.config(text='R: %03d G: %03d B: %03d' % (red, green, blue))
		self.Color.config(background='#%02x%02x%02x' % (red,green,blue))
	def uValueChanged ( self, newVal ):
		self.uScale.focus_set()
		self.uvValueChanged()
	def vValueChanged ( self, newVal ):
		self.vScale.focus_set()
		self.uvValueChanged()
	def AutoSensorModeRadio ( self, AutoSensor ):
		if AutoSensor == True:
			# Bug in the firmware. Cannot seem to get back to mode 0
			# after changing to any other mode!
			self.camera.sensor_mode = 0
			self.camera.sensor_mode = 0		# doesn't work!
			self.SensorModeCombo.config(state='disabled')
		else:
			self.SensorModeCombo.config(state='readonly')
			self.SensorModeChanged(None)
	def SensorModeChanged ( self, event ):
		mode = int(self.SensorModeCombo.current()) + 1
		self.camera.sensor_mode = mode
	def FlashModeButton ( self, FlashMode ):
		if FlashMode == 'set':
			self.FlashModeCombo.config(state='readonly')
			self.FlashModeChanged(None)
		else:
			self.FlashModeCombo.config(state='disabled')
			self.camera.flash_mode = FlashMode
	def FlashModeChanged ( self, event ):
		self.camera.flash_mode = self.FlashModeCombo.get()

class Exposure ( BasicNotepage ):
	def BuildPage ( self ):
		f = Frame(self)
		f.grid(row=0,column=0,sticky='NSEW')
		f.columnconfigure(1,weight=1)
		l = Label(f,text='Metering mode:')
		l.grid(row=0,column=0,sticky=W,pady=5)
		self.MeteringModeCombo = Combobox(f,state='readonly',width=10)
		self.MeteringModeCombo.grid(row=0,column=1,columnspan=3,sticky=E+W)
		self.MeteringModeCombo['values'] = self.camera.METER_MODES.keys()
		self.MeteringModeCombo.current(0)
		self.MeteringModeCombo.bind('<<ComboboxSelected>>',self.MeteringModeChanged)

		f = LabelFrame(self,text='Exposure mode (Equivalent film ISO)',padding=(5,5,5,5))
		f.grid(row=1,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(1,weight=1)

		modes = [('Full auto (Default)','auto',2),('Preset exposures:','set',1),\
				 ('Manually set ISO:','iso',1),
				 ('Off (Analog/Digital gains set at current value)','off',2)]
		ExposureMode = StringVar()
		ExposureMode.set(modes[0][1])
		for i, mode in enumerate(modes):
			b1 = Radiobutton(f,text=mode[0],variable=ExposureMode,
				value=mode[1],command=lambda val=mode[1]:self.ExposureModeButton(val),
				padding=(5,5,5,5))
			b1.grid(row=i,column=0,sticky='W',columnspan=mode[2])

		self.ExpModeCombo = Combobox(f,state='readonly',width=10)
		self.ExpModeCombo.grid(row=1,column=1,sticky='EW')
		self.ExpModeCombo.bind('<<ComboboxSelected>>',self.ExpModeChanged)
		exp = self.camera.EXPOSURE_MODES.keys()
		exp.remove('off')		# these two are handled by radio buttons
		exp.remove('auto')
		exp.sort(cmp=lambda x,y: cmp(x.lower(),y.lower()))
		self.ExpModeCombo['values'] = exp
		self.ExpModeCombo.current(1)

		self.IsoCombo = Combobox(f,state='readonly',width=10)
		self.IsoCombo.grid(row=2,column=1,sticky='EW')
		self.IsoCombo.bind('<<ComboboxSelected>>',self.IsoChanged)
		self.IsoCombo['values'] = [100,200,320,400,500,640,800]
		self.IsoCombo.current(3)

		Separator(f,orient=HORIZONTAL).grid(pady=5,row=4,column=0,
			columnspan=3,sticky='EW')

		f1 = Frame(f)
		f1.grid(row=5,column=0,sticky='NSEW',columnspan=2)
		l = Label(f1,text='Analog gain:').grid(row=0,column=0,sticky='W')
		self.AnalogGain = Label(f1,style='DataLabel.TLabel')
		self.AnalogGain.grid(row=0,column=1,sticky=W,pady=5,padx=5)
		l = Label(f1,text='Digital gain:').grid(row=0,column=2,sticky='W')
		self.DigitalGain = Label(f1,style='DataLabel.TLabel')
		self.DigitalGain.grid(row=0,column=3,sticky=W,pady=5,padx=5)
		l = Label(f1,text='Actual ISO:').grid(row=1,column=0,sticky='W')
		self.EffIso = Label(f1,style='DataLabel.TLabel')
		self.EffIso.grid(row=1,column=1,sticky=W,pady=5,padx=5)
		l = Label(f1,text='Apparent ISO:').grid(row=1,column=2,sticky='W')
		self.MeasIso = Label(f1,style='DataLabel.TLabel')
		self.MeasIso.grid(row=1,column=3,sticky=W,pady=5,padx=5)
		#---------------- End Exposure Mode Settings ----------------

		f = LabelFrame(self,text='Exposure compensation (Equivalent to camera lens fstop)',
			padding=(5,5,5,5))
		f.grid(row=2,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)
		l = Label(f,text='Compensation:',padding=(5,5,5,5))
		l.grid(row=0,column=0,sticky='W')
		self.fstop = Label(f,width=14,padding=(5,5,5,5),style='DataLabel.TLabel')
		self.fstop.grid(row=0,column=1,sticky='W')
		self.ExpCompSlider = Scale(f,from_=-25,to=25,length=50,
				command=self.ExpComboSliderChanged,orient='horizontal')
		self.ExpCompSlider.grid(row=0,column=2,sticky='NSEW',pady=5)
		self.ExpCompSlider.set(0)

		f = LabelFrame(self,text='Shutter speed',padding=(5,5,5,5))
		f.grid(row=3,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)
		self.ShutterSpeedAuto = BooleanVar()
		self.ShutterSpeedAuto.set(True)
		b1 = Radiobutton(f,text='Auto (Default)',variable=self.ShutterSpeedAuto,
			value=True,command=self.ShutterSpeedButton,padding=(5,5,5,5))
		b1.grid(row=0,column=0,sticky='W',columnspan=2)
		l = Label(f,text='Exposure speed:')
		l.grid(row=0,column=1,sticky=W,pady=5)
		self.ExposureSpeed = Label(f,style='DataLabel.TLabel')
		self.ExposureSpeed.grid(row=0,column=2,sticky=W)

		b2 = Radiobutton(f,text='Set shutter speed:',variable=self.ShutterSpeedAuto,
			value=False,command=self.ShutterSpeedButton,padding=(5,5,5,5))
		b2.grid(row=1,column=0,sticky='W')
		okCmd = (self.register(self.ValidateShutterSpeed),'%P')
		self.ShutterSpeed = StringVar()
		self.ShutterSpeedEntry = Entry(f,textvariable=self.ShutterSpeed,width=8,
			validate='all',validatecommand=okCmd)
		self.ShutterSpeedEntry.grid(row=1,column=1,sticky='EW')
		self.SlowestShutterSpeed = Label(f,style='RedMessage.TLabel')
		self.SlowestShutterSpeed.grid(row=2,column=0,columnspan=3,sticky='W')

		f = LabelFrame(self,text='Frame rate',padding=(5,5,5,5))
		f.grid(row=4,column=0,columnspan=4,sticky='NEWS',pady=5)
		f.columnconfigure(2,weight=1)

		l = Label(f,text='Frame rate:').grid(row=0,column=0,sticky='W')
		self.FrameRate = Label(f,style='DataLabel.TLabel')
		self.FrameRate.grid(row=0,column=1,sticky='W')

		self.CheckGains()
		self.ExposureModeButton('auto')
		self.ShutterSpeedButton()
		self.ExpModeCombo.focus_set()
		self.UpdateFrameRate()
	def MeteringModeChanged ( self, event ):
		self.camera.meter_mode = self.MeteringModeCombo.get()
	def ExposureModeButton ( self, ExposureMode ):
		self.ExpCompSlider.state(['!disabled'])
		if ExposureMode == 'auto' or ExposureMode == 'off':
			self.ExpModeCombo.config(state='disabled')
			self.IsoCombo.config(state='disabled')
			self.camera.iso = 0				# auto ISO
			if ExposureMode == 'off':
				self.ExpCompSlider.state(['disabled'])
			self.camera.exposure_mode = ExposureMode
		elif ExposureMode == 'set':
			self.camera.iso = 0				# auto ISO
			self.ExpModeCombo.config(state='readonly')
			self.IsoCombo.config(state='disabled')
			self.ExpModeChanged(None)
		else:	# mode = 'iso'
			self.ExpModeCombo.config(state='disabled')
			self.IsoCombo.config(state='readonly')
			self.IsoChanged(None)
	def ExpModeChanged ( self, event ):
		self.camera.exposure_mode = self.ExpModeCombo.get()
	def IsoChanged	( self, event ):
		val = int(self.IsoCombo.get())
		self.camera.iso = val
	def CheckGains ( self ):
		ag = self.camera.analog_gain
		dg = self.camera.digital_gain
		self.AnalogGain.config(text= '%.3f' % ag)
		self.DigitalGain.config(text= '%.3f' % dg)
		self.EffIso.config(text='%d' % int(ag / dg * 100.0))
		self.MeasIso.config(text= \
			'AUTO' if self.camera.iso == 0 else str(self.camera.iso) )
		self.after(300,self.CheckGains)
	def ExpComboSliderChanged ( self, newVal ):
		val = float(newVal)
		if val == 0.0:
			self.fstop.config(text = 'None (Default)')
		else:
			self.fstop.config(text = '%s %.2f fstops' % (
				'Close' if val < 0.0 else 'Open', abs(val) / 6.0) )
		self.camera.exposure_compensation = int(val)
		self.ExpCompSlider.focus_set()
	def ShutterSpeedButton ( self ):
		if self.ShutterSpeedAuto.get() == True:
			self.camera.shutter_speed = 0
			self.ShutterSpeedEntry.config(state='disabled')
			self.after(300,self.CheckShutterSpeed)
		else:
			self.camera.shutter_speed = int(self.ShutterSpeed.get())
			self.ShutterSpeedEntry.config(state='!disabled')
	def CheckShutterSpeed ( self ):
		val = self.camera.exposure_speed
		txt = '%d usec' % val
		self.ExposureSpeed.config(text=txt)
		self.ShutterSpeed.set(str(val))
		if self.ShutterSpeedAuto.get() == True:
			self.after(300,self.CheckShutterSpeed)
	def ValidateShutterSpeed ( self, EntryIfAllowed ):
		if self.ShutterSpeedAuto.get() == True:
			return True
		try:	val = int(EntryIfAllowed)
		except:	val = -1
		if val >= 1 and val <= int(1.0e6 / self.camera.framerate):
			self.camera.shutter_speed = val
			txt = '%d usec' % int(self.camera.exposure_speed)
			self.ExposureSpeed.config(text=txt)
			return True
		return False
	def UpdateFrameRate ( self ):
		self.FrameRate.config(text='%.1f fps' % self.camera.framerate)
		self.SlowestShutterSpeed.config(text=\
			'Slowest shutter speed limited by Framerate to %d usec' % \
			int(1.0e6 / self.camera.framerate))
		self.after(300,self.UpdateFrameRate)

class Annotate ( BasicNotepage ):
	def BuildPage ( self ):
		f = LabelFrame(self,text='Annotation background color',padding=(5,5,5,5))
		f.grid(row=0,column=0,sticky='NEWS',pady=5)
		AddBackgroundColor = BooleanVar()
		AddBackgroundColor.set(False)
		b1 = Radiobutton(f,text='None (Default)',variable=AddBackgroundColor,
			value=False,command=lambda:self.AnnotationBackgroundColor(False),padding=(5,5,5,5))
		b1.grid(row=0,column=0,sticky='W')
		b2 = Radiobutton(f,text='Use color',variable=AddBackgroundColor,
			value=True,command=lambda:self.AnnotationBackgroundColor(True),padding=(5,5,5,5))
		b2.grid(row=0,column=1,sticky='W')
		self.chooseBackColor = Button(f,text='Color',command=self.ChooseBackcolorClick)
		self.chooseBackColor.grid(row=0,column=2,sticky='EW')

		f = LabelFrame(self,text='Annotation foreground color',padding=(5,5,5,5))
		f.grid(row=1,column=0,sticky='NEWS',pady=5)
		AddForegroundColor = BooleanVar()
		AddForegroundColor.set(False)
		b1 = Radiobutton(f,text='White (Default)',variable=AddForegroundColor,
			value=False,command=lambda:self.AnnotationForegroundColor(False),padding=(5,5,5,5))
		b1.grid(row=0,column=0,sticky='W')
		b2 = Radiobutton(f,text='Use color',variable=AddForegroundColor,
			value=True,command=lambda:self.AnnotationForegroundColor(True),padding=(5,5,5,5))
		b2.grid(row=0,column=1,sticky='W')
		self.chooseForeColor = Button(f,text='Color',command=self.ChooseForecolorClick)
		self.chooseForeColor.grid(row=0,column=2,sticky='EW')

		f = LabelFrame(self,text='Annotation text',padding=(5,5,5,5))
		f.grid(row=2,column=0,sticky='NEWS',pady=5)
		AddAnnotationText = BooleanVar()
		AddAnnotationText.set(False)
		b1 = Radiobutton(f,text='None (Default)',variable=AddAnnotationText,
			value=False,command=lambda:self.AnnotationText(False),padding=(5,5,5,5))
		b1.grid(row=0,column=0,sticky='W')
		b2 = Radiobutton(f,text='Text:',variable=AddAnnotationText,
			value=True,command=lambda:self.AnnotationText(True),padding=(5,5,5,5))
		b2.grid(row=0,column=1,sticky='W')
		okCmd = (self.register(self.ValidateText),'%P')
		self.AnnotateText = Entry(f,width=30,validate='all',validatecommand=okCmd)
		self.AnnotateText.grid(row=0,column=2,sticky='EW')
		Label(f,text='Size:').grid(row=1,column=1,sticky='E')
		self.AnnotateTextSize = Scale(f,from_=6,to=160,length=50,
				command=self.AnnotateTextSizeChanged,orient='horizontal')
		self.AnnotateTextSize.grid(row=1,column=2,sticky='NSEW')
		self.AnnotateTextSize.set(32)

		self.AnnotationBackgroundColor(False)
		self.AnnotationForegroundColor(False)
	def AnnotationBackgroundColor ( self, AddColor ):
		if AddColor:
			self.camera.annotate_background = picamera.Color('black')
			self.chooseBackColor.config(state='!disabled')
			self.chooseBackColor.focus_set()
		else:
			self.camera.annotate_background = None
			self.chooseBackColor.config(state='disabled')
	def ChooseBackcolorClick ( self ):
		result = askcolor(parent=self,color=self.camera.annotate_background,
				 title='Background color')
		if result[0] == None: return
		self.camera.annotate_background = picamera.Color(result[1])
	def AnnotationForegroundColor ( self, AddColor ):
		if AddColor:
			self.camera.annotate_foreground = picamera.Color('white')
			self.chooseForeColor.config(state='!disabled')
			self.chooseForeColor.focus_set()
		else:
			self.chooseForeColor.config(state='disabled')
			self.camera.annotate_foreground = picamera.Color('white')
	def ChooseForecolorClick ( self ):
		result = askcolor(parent=self,color=self.camera.annotate_foreground,
				 title='Foreground color')
		if result[0] == None: return
		self.camera.annotate_foreground = picamera.Color(result[1])
	def AnnotationText ( self, AddText ):
		if AddText:
			self.camera.annotate_text = self.AnnotateText.get()
			self.AnnotateText.config(state='normal')
			self.AnnotateText.focus_set()
		else:
			self.camera.annotate_text = ''
			self.AnnotateText.config(state='disabled')
	def ValidateText ( self, EntryIfOk ):
		self.camera.annotate_text = EntryIfOk
		return True
	def AnnotateTextSizeChanged ( self, newVal ):
		self.camera.annotate_text_size = int(float(newVal))
		self.AnnotateTextSize.focus_set()

def Run ():
	try:
		win = Tk()
	except:
		print "Error initializing Tkinter!\n\nShutting down\n\nPress any key"
		raw_input()
		return
		
	Style().theme_use('clam')	# I like this theme, so sue me.

	try:
		# Bug in firmware? Must initialize to a value other than 0 to
		# allow changing to other modes later...
		camera = picamera.PiCamera(sensor_mode=1)
		camera.sensor_mode = 0	# go back to auto mode
	except PiCameraError:
		tkMessageBox.showerror("PiCamera initialization error",
				"Error creating PiCamera instance!\n\n" + \
				"Check that the PiCamera is installed correctly.\n\nShutting down.")
		print "Error creating PiCamera instance! Shutting down.\n\nPress any key..."
		raw_input()
		return

	win.minsize(1024,768)
	app = PiCameraApp(win,camera,title="PiCamera")
	win.mainloop()

	camera.close()

if __name__ == '__main__':
	Run()

