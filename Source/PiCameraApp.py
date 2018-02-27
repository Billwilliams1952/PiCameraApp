#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
PiCameraApp.py
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

'''
	1.)	LED control no longer works on RPI 3 Model B
		The camera LED cannot currently be controlled when the module is
		attached to a Raspberry Pi 3 Model B as the GPIO that controls the
		LED has moved to a GPIO expander not directly accessible to the
		ARM processor.
	2.)
'''

########### TODO: Standardize variable, class, member cases

import time
import datetime
import webbrowser		# display the Picamera documentation
import io
import time
import os
from time import time, sleep
from Tooltip	import *
from	AnnotationOverlay	import *

#~ try:
import RPi.GPIO
#~ except ImportError:
	#~ RPiGPIO = False
'''
From PiCamera ver 1.3 documentation
https://picamera.readthedocs.io/en/release-1.13/recipes1.html
Be aware when you first use the LED property it will set the GPIO
library to Broadcom (BCM) mode with GPIO.setmode(GPIO.BCM) and disable
warnings with GPIO.setwarnings(False). The LED cannot be controlled when
the library is in BOARD mode.
'''

try:
	import 	picamera
	from 		picamera import *
	import 	picamera.array
except ImportError:
	raise ImportError("You do not seem to have picamera installed")

try:
	from Tkinter import *	# Python 2.X
except ImportError:
	from tkinter import *	# Python 3.X
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
	from		tkinter import ttk
	from 		tkinter.ttk import *
try:
	import 	tkFont
except ImportError:
	import	tkinter.font

# sudo apt-get install python3-pil.imagetk
import PIL
from PIL import Image, ExifTags
try:
	from PIL import ImageTk
except ImportError:
	raise ("ImageTk not installed. If running Python 3.x\n" \
			 "Use: sudo apt-get install python3-pil.imagetk")

from 	AboutDialog import *
from 	PreferencesDialog import *
from	AnnotationOverlay import *
from	KeyboardShortcuts import *
from	Mapping import *
from	NotePage import *
from	CameraUtils import *
from	BasicControls import *
from	FinerControl import *
from	Exposure import *
from	Timelapse import *
from	Utils import *

#
# Main PiCameraApp Window
#
class PiCameraApp ( Frame ):
	# Some statics used elsewhere
	ExposureModeText = None

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

		ToolTip.LoadToolTips()

		#----------- Icons for Menu and Buttons ------------------------
		self.iconClose = GetPhotoImage("Assets/window-close.png")
		#self.iconClose = ImageTk.PhotoImage(PIL.Image.open("Assets/window-close.png"))
		self.iconPrefs = GetPhotoImage('Assets/prefs1_16x16.png')
		self.iconWeb = GetPhotoImage('Assets/web_16x16.png')
		image = PIL.Image.open('Assets/camera-icon.png')
		self.iconCameraBig = GetPhotoImage(image.resize((22,22)))
		self.iconCamera = GetPhotoImage(image.resize((16,16)))
		image = PIL.Image.open('Assets/video-icon-b.png')
		self.iconVideoBig = GetPhotoImage(image.resize((22,22)))
		self.iconVideo = GetPhotoImage(image.resize((16,16)))

		#------------ Notebook with all camera control pages -----------
		frame1 = ttk.Frame(master,padding=(5,5,5,5))
		frame1.grid(row=0,column=0,sticky="NSEW")
		frame1.rowconfigure(2,weight=1)
		frame1.columnconfigure(0,weight=1)

		self.AlwaysPreview = False

		n = Notebook(frame1,padding=(5,5,5,5))
		n.grid(row=1,column=0,rowspan=2,sticky=(N,E,W,S))
		n.columnconfigure(0,weight=1)
		n.enable_traversal()

		self.BasicControlsFrame = BasicControls(n,camera)
		self.ExposureFrame = Exposure(n,camera)
		self.FinerControlFrame = FinerControl(n,camera)
		#self.TimelapseFrame = Timelapse(n,camera)

		n.add(self.BasicControlsFrame ,text='Basic',underline=0)
		n.add(self.ExposureFrame,text='Exposure',underline=0)
		n.add(self.FinerControlFrame,text='Advanced',underline=0)
		#n.add(self.TimelapseFrame,text='Time lapse',underline=0)

		self.FinerControlFrame.PassControlFrame(self.BasicControlsFrame)

		# ----------------------Paned Window ---------------------------
		# Start of Image Canvas preview, camera captures,
		#	Paned Window VERTICAL
		#		TopFrame
		#			Preview ImageCanvas	row Weight=1
		#			ButtonFrame
		#				Preview Buttons
		#		BottomFrame
		#### TODO:	Add title to BottomFrame 'Captured Image/Video'
		#			PanedWindow HORIZONTAL row 0, col 0
		#				LeftFrame
		#					Camera setups, EXIF Text
		#### TODO:			ButtonFrame
		#### TODO:				Clear, Save as File, Save as Python
		#				RightFrame
		#					Current Photo Canvas
		#			ButtonFrame
		#				Picture / Video buttons

		self.pw = ttk.PanedWindow(master,orient=VERTICAL,style='TPanedwindow',
			takefocus=True)
		self.pw.grid(row=0,column=1,sticky="NSEW")
		self.pw.rowconfigure(0,weight=1)
		self.pw.columnconfigure(0,weight=1)

		self.TopFrame = ttk.Frame(self.pw,padding=(5,5,5,5))
		self.TopFrame.grid(row=0,column=0,sticky="NEWS")
		self.TopFrame.rowconfigure(0,weight=1)
		self.TopFrame.columnconfigure(1,weight=1)

		#### TODO: Create Canvas Class to handle generic cursors, etc
		self.ImageCanvas = Canvas(self.TopFrame,width=256,height=256,
			background=self.ControlMapping.FocusColor,cursor='diamond_cross')
		self.ImageCanvas.grid(row=0,column=0,columnspan=2,sticky="NEWS")
		self.ImageCanvas.itemconfigure('nopreview',state='hidden')
		self.ImageCanvas.bind("<Motion>",self.CanvasMouseMove)
		self.ImageCanvas.bind("<ButtonPress>",self.CanvasMouseMove)
		self.ImageCanvas.bind("<Enter>",self.CanvasEnterLeave)
		self.ImageCanvas.bind("<Leave>",self.CanvasEnterLeave)

		ButtonFrame = ttk.Frame(self.TopFrame,padding=(5,5,5,5),relief=SUNKEN)
		ButtonFrame.grid(row=1,column=0,columnspan=2,sticky="NEWS")

		self.PreviewOn = MyBooleanVar(True)
		self.enablePrev = ttk.Checkbutton(ButtonFrame,text='Preview',variable=self.PreviewOn,
			command=self.SetPreviewOn)
		self.enablePrev.grid(row=0,column=0,padx=5,sticky='W')
		ToolTip(self.enablePrev, msg=1)
		l2 = Label(ButtonFrame,text="Alpha:")
		l2.grid(column=1,row=0,sticky='W')
		self.alpha = ttk.Scale(ButtonFrame,from_=0,to=255,
				command=self.AlphaChanged,orient='horizontal',length=75)
		self.alpha.grid(row=0,column=2,sticky='E')
		self.alpha.set(255)
		ToolTip(self.alpha, msg=2)

		self.VFlipState = False
		image = PIL.Image.open('Assets/flip.png')
		image1 = image.rotate(90)
		image1 = image1.resize((16,16))
		self.flipVgif = ImageTk.PhotoImage(image1)
		self.Vflip = ttk.Button(ButtonFrame,image=self.flipVgif,width=10,
			command=self.ToggleVFlip,padding=(2,2,2,2))
		self.Vflip.grid(row=0,column=3,padx=5)
		ToolTip(self.Vflip, msg=3)

		self.HFlipState = False
		self.flipHgif = ImageTk.PhotoImage(image.resize((16,16)))
		self.Hflip = ttk.Button(ButtonFrame,image=self.flipHgif,width=10,
			command=self.ToggleHFlip,padding=(2,2,2,2))
		self.Hflip.grid(row=0,column=4)
		ToolTip(self.Hflip, msg=4)

		image = PIL.Image.open('Assets/rotate.png')
		self.RotateImg = ImageTk.PhotoImage(image.resize((16,16)))
		self.Rotate = ttk.Button(ButtonFrame,image=self.RotateImg,width=10,
			command=self.RotateCamera,padding=(2,2,2,2))
		self.Rotate.grid(row=0,column=5)
		ToolTip(self.Rotate, msg=14)

		self.ShowOnScreen = MyBooleanVar(True)
		self.ShowOnMonitorButton = ttk.Checkbutton(ButtonFrame, \
			text='Overlay',variable=self.ShowOnScreen, \
			command=self.SetPreviewLocation)
		self.ShowOnMonitorButton.grid(row=0,column=6,padx=5,sticky='W')
		ToolTip(self.ShowOnMonitorButton, msg=5)

		l5 = Label(ButtonFrame,text="Size:")
		l5.grid(column=7,row=0,sticky='W')
		self.WindowSize = ttk.Scale(ButtonFrame,from_=100,to=800,
				command=self.WindowSizeChanged,orient='horizontal',length=75)
		self.WindowSize.grid(row=0,column=8,sticky='E')
		self.WindowSize.set(255)
		ToolTip(self.WindowSize, msg=6)

		#------------------ Photo / Video Section ----------------------
		self.pictureStream = io.BytesIO()

		BottomFrame = ttk.Frame(self.pw,padding=(5,5,5,5))
		BottomFrame.grid(row=1,column=0,sticky="NEWS")
		BottomFrame.rowconfigure(0,weight=1)
		BottomFrame.columnconfigure(0,weight=1)

		self.photoPanedWindow = ttk.PanedWindow(BottomFrame,orient=HORIZONTAL,
			style='Pan.TPanedwindow')
		self.photoPanedWindow.grid(row=0,column=0,sticky="NSEW")
		self.photoPanedWindow.rowconfigure(0,weight=1)
		self.photoPanedWindow.columnconfigure(0,weight=1)
		self.photoPanedWindow.columnconfigure(1,weight=1)

		self.LeftFrame = ttk.Frame(self.photoPanedWindow,padding=(5,5,5,5))
		self.LeftFrame.grid(row=0,column=0,sticky="NEWS")
		self.LeftFrame.rowconfigure(0,weight=1)
		self.LeftFrame.columnconfigure(0,weight=1)

		sb = Scrollbar(self.LeftFrame,orient='vertical')
		sb.grid(row=0,column=1,sticky='NS')
		ToolTip(sb, msg=7)

		sb1 = Scrollbar(self.LeftFrame,orient='horizontal')
		sb1.grid(row=1,column=0,sticky='EW')
		ToolTip(sb, msg=8)
		text = Text(self.LeftFrame,width=37,wrap='none',
			yscrollcommand=sb.set,xscrollcommand=sb1.set)
		text.bind('<Configure>',self.TextboxResize)
		text.grid(row=0,column=0,sticky='NSEW')
		sb.config(command=text.yview)
		sb1.config(command=text.xview)
		text.bind("<Key>",lambda e : "break")	# ignore all keypress
		self.CameraUtils = CameraUtils(self.camera,self.BasicControlsFrame)
		self.CameraUtils.SetupCameraSettingsTextbox(text)

		RightFrame = ttk.Frame(self.photoPanedWindow,padding=(5,5,5,5))
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
			fill='lightgray',activefill='blue',tags=('cross','cross1'))
		self.photoCanvas.create_line(0,0,0,240,
			fill='lightgray',activefill='blue',tags=('cross','cross2'))
		self.photoCanvas.create_text(0,0,
			tags=('capture'),text='',
			fill='lightgray',activefill='blue',anchor='center',
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
		self.photoCanvas.bind("<5>",self.WheelScrollPhotoCanvas)
		self.photoCanvas.bind("<4>",self.WheelScrollPhotoCanvas)
		self.photoZoomScale	= 1.0

		self.photoPanedWindow.add(self.LeftFrame)
		self.photoPanedWindow.add(RightFrame)
		self.photoPanedWindow.forget(self.LeftFrame)

		ButtonFrame = ttk.Frame(BottomFrame,padding=(5,5,5,5))
		ButtonFrame.grid(row=1,column=0,columnspan=3,sticky="NEWS")
		b = ttk.Button(ButtonFrame,text='Picture',underline=0,image=self.iconCameraBig,
			compound='left',command=lambda e=None:self.TakePicture(e),width=7)
		b.grid(row=0,column=0,sticky='W',padx=5)
		ToolTip(b, msg=9)

		self.InCaptureVideo = False  # hack ----
		self.TakeVideo = ttk.Button(ButtonFrame,text='Video',underline=0,
			image=self.iconVideoBig,compound='left',
			command=lambda e=None:self.ToggleVideo(e),width=7)
		self.TakeVideo.grid(row=0,column=1,sticky='W')
		ToolTip(self.TakeVideo, msg=10)

		self.clearImage = ImageTk.PhotoImage(file='Assets/cancel_22x22.png')
		b = ttk.Button(ButtonFrame,command=lambda e=None:self.ClearPicture(e),
			image=self.clearImage,padding=(0,1,0,1))
		b.grid(row=0,column=2,sticky='W',padx=5)
		ToolTip(b, msg=11)

		image = PIL.Image.open('Assets/flip.png').resize((22,22))
		self.FlipHorzImage = ImageTk.PhotoImage(image)
		b = ttk.Button(ButtonFrame,command=lambda e=None:self.FlipPictureH(e),
			image=self.FlipHorzImage,padding=(0,1,0,1))
		b.grid(row=0,column=3,sticky='W')
		b.config(state='disabled')
		ToolTip(b, msg=12)

		self.FlipVertImage = ImageTk.PhotoImage(image.rotate(90))
		b = ttk.Button(ButtonFrame,command=lambda e=None:self.FlipPictureV(e),
			image=self.FlipVertImage,padding=(0,1,0,1))
		b.grid(row=0,column=4,sticky='W',padx=5)
		b.config(state='disabled')
		ToolTip(b, msg=13)

		self.pw.add(self.TopFrame)
		self.pw.add(BottomFrame)

		#-------------------------- Status Bar -------------------------
		self.StatusBarFrame = ttk.Frame(master)
		self.StatusBarFrame.grid(row=1,column=0,columnspan=2,sticky='NSEW')
		self.StatusBarFrame.columnconfigure(5,weight=1)
		self.XYText = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,font=('Arial',9),
			textvariable=self.XYText,style='StatusBar.TLabel', width=13)
		l.grid(row=0,column=0,sticky='W')
		ToolTip(l,40)
		self.ExposureModeText = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,textvariable=self.ExposureModeText,
			style='StatusBar.TLabel',width=18,font=('Arial',9))
		l.grid(row=0,column=1,sticky='W')
		ToolTip(l,41)
		self.AWBText = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,textvariable=self.AWBText,
			style='StatusBar.TLabel',width=18,font=('Arial',9))
		l.grid(row=0,column=2,sticky='W')
		ToolTip(l,42)
		self.ShutterSpeedText = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,textvariable=self.ShutterSpeedText,
			style='StatusBar.TLabel',width=15,font=('Arial',9))
		l.grid(row=0,column=3,sticky='W')
		ToolTip(l,43)
		self.FPSText = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,textvariable=self.FPSText,
			style='StatusBar.TLabel',width=10,font=('Arial',9))
		l.grid(row=0,column=4,sticky='W')
		ToolTip(l,44)
		self.StatusText = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,textvariable=self.StatusText,
			style='StatusBar.TLabel',width=10,font=('Arial',9))
		l.grid(row=0,column=5,sticky='EW')
		ToolTip(l,45)

		self.ExposureFrame.SetVariables(self.ExposureModeText, self.AWBText,
					self.ShutterSpeedText, self.FPSText)

		#--------------------------- Menu ------------------------------
		menubar = Menu(root,
			foreground='black',background='#F0F0F0',activebackground='#86ABD9',
			activeforeground='white')

		filemenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		#filemenu.add_command(label="Save Camera setups...",underline=0,
			#command=lambda e=None:self.SaveCameraSetups(e))
		#filemenu.add_separator()
		filemenu.add_command(label="Preferences...",underline=0,
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

		self.viewImageCursor = MyBooleanVar(False)
		viewmenu.add_checkbutton(label="Image cursors",underline=7,
			accelerator='Ctrl+Shift+C',
			onvalue=True,offvalue=False,variable=self.viewImageCursor,
			command=lambda e='Menu':self.ViewImageCursor(e))
		self.DefineAccelerators('cs','c',self.ViewImageCursor)

		self.viewImageAttributesPane = BooleanVar()
		self.viewImageAttributesPane.set(False)
		viewmenu.add_checkbutton(label="Image Attribute pane",underline=6,
			accelerator='Ctrl+Shift+A',
			onvalue=True,offvalue=False,variable=self.viewImageAttributesPane,
			command=lambda e='Menu':self.ViewImageAttributesPane(e))
		self.DefineAccelerators('cs','a',self.ViewImageAttributesPane)

		self.viewPreviewPane = BooleanVar()
		self.viewPreviewPane.set(True)
		viewmenu.add_checkbutton(label="Preview pane",underline=0,
			accelerator='Ctrl+Shift+P',
			onvalue=True,offvalue=False,variable=self.viewPreviewPane,
			command=lambda e='Menu':self.ViewPreviewPane(e))
		self.DefineAccelerators('cs','p',self.ViewPreviewPane)

		self.ViewStatusBarBoolean = MyBooleanVar(True)
		viewmenu.add_checkbutton(label="Status bar",underline=0,
			onvalue=True,offvalue=False,variable=self.ViewStatusBarBoolean,
			command=lambda e='Menu':self.ViewStatusBar(e))

		#viewmenu.add_command(label="Properties...",underline=0,accelerator='Ctrl+Alt+P',
			#image=self.iconPrefs,compound='left',
			#command=lambda e=None:self.ViewProperties(e))
		#self.DefineAccelerators('ca','p',lambda e=None:self.ViewProperties(e))
		menubar.add("cascade",label='View',underline=0,menu=viewmenu)

		photomenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		photomenu.add_command(label="Take picture",underline=5,
			image=self.iconCamera,compound='left',
			command=lambda e=None:self.TakePicture(e),accelerator='Ctrl+P')
		self.DefineAccelerators('c','p',lambda e=None:self.TakePicture(e))
		photomenu.add_command(label="Save Image...",underline=0,compound='left',
			command=lambda e=None:self.SavePictureorVideo(e),accelerator='Ctrl+S')
		self.DefineAccelerators('c','s',lambda e=None:self.SavePictureorVideo(e))
		photomenu.add_command(label="Clear picture",underline=0,
			image=self.iconClose,compound='left',
			command=lambda e=None:self.ClearPicture(e),accelerator='Ctrl+C')
		self.DefineAccelerators('c','c',lambda e=None:self.ClearPicture(e))
		photomenu.add_command(label="Reset Camera setups",underline=0,
			compound='left',
			command=lambda e=None:self.ResetCameraSetups(e),accelerator='Ctrl+R')
		self.DefineAccelerators('c','r',lambda e=None:self.ResetCameraSetups(e))
		photomenu.add_separator()
		photomenu.add_command(label="Annotation/Overlay",underline=0,
			compound='left',
			command=lambda e=None:self.AnnotationOverlay(e))#,accelerator='Ctrl+A')
		#self.DefineAccelerators('c','a',lambda e=None:self.AnnotationOverlay(e))
		menubar.add("cascade",label='Photo',underline=0,menu=photomenu)

		videomenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
			activebackground='#86ABD9',activeforeground='white')
		videomenu.add_command(label="Toggle video",underline=7,
			image=self.iconVideo,compound='left',
			command=lambda e=None:self.ToggleVideo(e),accelerator='Ctrl+V')
		self.DefineAccelerators('c','v',lambda e=None:self.ToggleVideo(e))
		menubar.add("cascade",label='Video',underline=0,menu=videomenu)

		helpmenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		helpmenu.add_command(label="Keyboard shortcuts...",underline=0,
			command=lambda e=None:self.KeyboardShortcuts(e))
		helpmenu.add_command(label="Picamera Documentation...",underline=9,
			command=lambda e=None:self.PiCameraDocs(e),image=self.iconWeb,compound='left')
		helpmenu.add_command(label="Picamera Recipies...",underline=9,
			command=lambda e=None:self.PiCameraRecipies(e),image=self.iconWeb,compound='left')

		helpmenu.add_separator()
		helpmenu.add_command(label="About...",underline=0,command=lambda e=None:self.HelpAbout(e))
		menubar.add("cascade",label='Help',underline=0,menu=helpmenu)

		root.config(menu=menubar)

		# infohost.nmt.edu/tcc/help/pubs/tkinter/web/menu.html
		# colors : wiki.tcl.tk/37701
		self.CanvasPopup = Menu(root, title='Popup',tearoff=0, background='snow',
			foreground = 'black', activeforeground='white',
			activebackground='cornflowerblue',relief=FLAT)
		self.CanvasPopup.add_command(label='---Picture Menu---',command=None)
		self.CanvasPopup.add_separator()
		self.CanvasPopup.add_command(label='Save picture',
			command=lambda e=None:self.SavePictureorVideo(e))
		self.CanvasPopup.add_command(label='Clear picture',
			command=lambda e=None:self.ClearPicture(e))
		self.CanvasPopup.add_separator()
		self.CanvasPopup.add_command(label='Reset preview zoom',
			command=self.BasicControlsFrame.ZoomReset)
		# Selections are also bound to right mouse!! That sucks.
		self.photoCanvas.bind("<Button-3>", self.DoPictureWindowPopup)
		#--------------------------- End Menu --------------------------

		# Catch all focus events to the Top Window. Use to control
		# whether the camera preview_window overlay is visible or not.
		# I'm sure this will fail with Topmost windows... :(
		self.root.bind('<FocusOut>',self.LoseFocus)
		self.root.bind('<FocusIn>',self.GotFocus)
		# We want to catch window movements to show/hide preview window
		root.bind( '<Configure>', self.OnFormEvent )
		root.protocol("WM_DELETE_WINDOW", lambda e=None:self.quitProgram(e))

		self.UpdateAnnotationText()
	def ResetCameraSetups ( self, event ):
		if MessageBox.askyesno("PiCamera", \
										 "Reset camera settings to default values?"):
			self.BasicControlsFrame.Reset()
			self.ExposureFrame.Reset()
			self.FinerControlFrame.Reset()
	def SaveCameraSetups ( self, val ):
		pass
	def ShowHideImageAttributesPane ( self, ShowIt):
		if ShowIt:
			if self.CurrentImage: self.photoPanedWindow.insert(0,self.LeftFrame)
		else:
			try:
				self.photoPanedWindow.forget(self.LeftFrame)
			except TclError: pass	# Already forgotten!
	def ViewImageCursor ( self, event ):
		if self.viewImageCursor.get() is True:
			self.photoCanvas.itemconfigure('cursors',state='normal')
		else:
			self.photoCanvas.itemconfigure('cursors',state='hidden')
	def ViewImageAttributesPane ( self, event ):
		if not event == 'Menu':	# Must change variable state ourselves
			self.viewImageAttributesPane.set(not self.viewImageAttributesPane.get())
		self.ShowHideImageAttributesPane(self.viewImageAttributesPane.get())
	def ViewPreviewPane ( self, event ):
		if not event == 'Menu':	# Must change variable state ourselves
			self.viewPreviewPane.set(not self.viewPreviewPane.get())
		# Take care of preview window. If its not on the screen, but enabled, then
		# disable it.
		if self.PreviewOn.get() and not self.ShowOnScreen.get():
			self.PreviewOn.set(False)
			self.SetPreviewOn()
		# Now show/hide pane
		if self.viewPreviewPane.get():
			self.pw.insert(0,self.TopFrame)
		else:
			self.pw.forget(self.TopFrame)
	def TextboxResize ( self, event ):
		pass #print event.width
	def SavePictureorVideo ( self, event ):
		#### TODO: Create a picture class that maintains the state of
		# the current image. This would include the state of the camera
		# programming just before the image was taken.
		# Store on a PictureStack. In most cases, only one picture on
		# the stack, but can hold more - such as a series of pictures
		# taken in rapid sequence.
		if self.CurrentImage:
			if PreferencesDialog.PhotoTimestamp is True:
				initialFile = 'Image_' + \
				 datetime.datetime.now(). \
				 strftime(PreferencesDialog.DefaultTimestampFormat)
			else: initialFile = 'Image'
			path = FileDialog.asksaveasfilename(title="Save captured image",
				initialdir=PreferencesDialog.DefaultPhotoDir,
				#defaultextension="."+PreferencesDialog.DefaultPhotoFormat,
				initialfile=initialFile,
				filetypes=[('JPEG files', '.jpeg'),('Bitmap files', '.bmp'),
					('PNG files', '.png'), ('GIF files', '.gif'),
					('RAW files', '.raw')] )
			if path:
				if ".jpeg" in path:
					if JPEG.IncludeEXIF:
						# Quality of image was determined by picamera capture
						# So we want to save the image at the highest quality
						self.CurrentImage.save(path,quality=95,
							exif=self.RawEXIFData)
						print ("Save EXIF")
					else:
						self.CurrentImage.save(path,quality=95)
						print ("Dont save EXIF")
				else:	# Not JPEG - just save the image as captured by picamera.
					# What options are available from PILLOW?
					self.CurrentImage.save(path)
					print ("Not JPEG save")
	def photoCanvasScrollStart ( self, event ):
		if self.CurrentImage:
			if event.state & 0x0004 == 0x0004:		# Ctrl key
				self.InPhotoZoom = True
				self.Image = self.CurrentImage
				x = self.photoCanvas.canvasx(event.x)
				y = self.photoCanvas.canvasy(event.y)
				self.photoCanvas.create_rectangle(x,y,x+1,y+1,tags=('zoom','objs'),outline='red')
				#self.photoCanvas.config(cursor='sizing') # Why is this screwed up?
			else:
				#self.photoCanvas.config(cursor='hand1')
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
			#### TODO: We should account for previous levels of zoom
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
		self.XYText.set('X: %04d Y: %04d' % (x, y))

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
			#### TODO: BUGGY - look at rect total to analyze
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

		photoFormat = PreferencesDialog.DefaultPhotoFormat
		if photoFormat not in ['jpeg', 'png', 'bmp']:
			MessageBox.showwarning("Image view not supported",
				"Cannot directly view images in %s format" % photoFormat)
			return

		self.ClearPicture(None)
		self.CameraUtils.FillCameraSettingTextBox(self)
		self.photoCanvas.itemconfigure('cross',state='hidden')
		self.pictureStream.seek(0)	# Use to reload / resize image
		self.photoCanvas.itemconfigure('capture',state='normal')
		self.photoCanvas.itemconfigure('capture',text='Capture in progress...')
		self.after(500,self.CapturePicture(photoFormat))
	def CapturePicture ( self, photoFormat ):
		try:
			if photoFormat == 'jpeg':  #'/home/pi/Pictures/Image.jpeg'
				self.camera.exif_tags['EXIF.UserComment'] = JPEG.UserComment
				self.camera.capture(self.pictureStream, format=photoFormat,
					use_video_port=self.BasicControlsFrame.UseVidPort.get(),
					resize=self.BasicControlsFrame.GetResizeAfter(),
					quality=JPEG.Quality,bayer=JPEG.Bayer,
					thumbnail=JPEG.Thumbnail) # restart =WHAT??
			else:
				self.camera.capture(self.pictureStream,format=photoFormat,
					use_video_port=self.BasicControlsFrame.UseVidPort.get(),
					resize=self.BasicControlsFrame.GetResizeAfter())
		except PiCameraRuntimeError:
			raise 'Camera capture error' # Something really bad happened
		self.photoCanvas.itemconfigure('capture',state='hidden')
		self.LoadImageFromStream ( 1.0 )
		self.photoCanvas.itemconfigure('objs',state='normal')
		self.photoCanvas.tag_raise("objs") # raise Z order to topmost
	def LoadImageFromStream ( self, zoom ):
		if self.photo: del self.photo

		self.pictureStream.seek(0)
		self.CurrentImage = PIL.Image.open(self.pictureStream)
		# https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#the-image-class
		self.RawEXIFData = None
		if PreferencesDialog.DefaultPhotoFormat == 'jpeg':
			self.RawEXIFData = self.CurrentImage.info['exif']	# Works!!!!
			#print ( self.RawEXIFData )
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
		'''
			Implement Record Sequence
		'''
	def ToggleVideo ( self, event ):
		if self.camera.framerate == 0 and \
			PreferencesDialog.DefaultVideoFormat == 'h264':
			MessageBox.showwarning("Warning","Can't use framerate_range with .h264"\
				" format videos for some reason. An exception is generated stating "\
				"framerate_delta cannot be used with framerate_range.\n" \
				"Switch to fixed framerate or change the video type to e.g. MPEG.")
			return
		self.ClearPicture(None)
		self.InCaptureVideo = not self.InCaptureVideo

		if self.InCaptureVideo:
			self.TakeVideo.config(text='Stop')
			self.time = time()
			#### TODO: do this as a stream. Can we then play it in
			#### 	'realtime' to the user as it's being recorded?
			# Check what format the video is processed as. Change the
			# parameters accordingly.
			self.VidFormat = PreferencesDialog.DefaultVideoFormat
			self.TempFile = PreferencesDialog.DefaultVideoDir + '/__TMP__.' + \
									 self.VidFormat
			if self.VidFormat == 'h264':
				self.camera.start_recording(output=self.TempFile,
					format=self.VidFormat,profile=H264.Profile,level=H264.Level,
					intra_period=H264.IntraPeriod,intra_refresh=H264.IntraRefresh,
					inline_headers=H264.InlineHeaders,sei=H264.SEI,
					sps_timing=H264.SPSTiming,motion_output=H264.MotionOutput)
			else:	# generic - we can use anything
				self.camera.start_recording(output=self.TempFile,
					format=self.VidFormat)
			self.photoCanvas.itemconfigure('capture',state='normal')
			self.after(50,self.UpdateCaptureInProgress)
		else:
			self.TakeVideo.config(text='Video')
			self.camera.stop_recording()
			self.photoCanvas.itemconfigure('capture',state='hidden')
			if PreferencesDialog.VideoTimestamp is True:
				filename = 'Video_' + \
				 datetime.datetime.now(). \
					strftime(PreferencesDialog.DefaultTimestampFormat) + \
				 '.' + self.VidFormat
			else:
				filename = 'Video.' + self.VidFormat
			filename = FileDialog.asksaveasfilename(title='Save Video File',
				defaultextension = "*." + self.VidFormat,
				initialdir = PreferencesDialog.DefaultVideoDir,
				initialfile = filename )
			# This is wrong. I should rework this
			if filename:
				os.rename(self.TempFile,filename)
			else:
				try:		os.remove(self.TempFile)
				except:	pass
	def UpdateCaptureInProgress ( self ):
		if not self.InCaptureVideo: return
		# keep updating video capture time
		delta = time() - self.time
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
	def FlipPictureH ( self, event ):
		if self.CurrentImage:
			pass
			#self.CurrentImage.transpose(ImageTk.FLIP_LEFT_RIGHT)
	def FlipPictureV ( self, event ):
		if self.CurrentImage:
			pass
			#self.CurrentImage.transpose(ImageTk.FLIP_TOP_BOTTOM)
	def ViewProperties ( self, event ):
		pass
	def PhotoCanvasResize ( self, event ):
		size = (event.width,event.height)
		x = self.photoCanvas.canvasx(event.x)
		y = self.photoCanvas.canvasy(event.y)
		#### TODO: Allow size to fit, or actual size
		# either scroll if actual size, or size image to fit
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
		self.XYText.set('X:   Y:')
		if not self.CurrentImage: return
		if self.viewImageCursor.get() is True:
			state1 = 'normal'		# 7/8 leave enter - getname instead
			if int(event.type) == 8:
				state1 = 'hidden'
				#self.statusText.set("")
			self.photoCanvas.itemconfigure('objs',state=state1)
		else:
			self.photoCanvas.itemconfigure('objs',state='hidden')
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

		#self.statusText.set('%d X: %d Y: W: %d H: %d' % \
			#(event.x,event.y,canvas[2],canvas[3]))
	def CanvasEnterLeave ( self, event ):
		pass
	def SetPreviewOn ( self ):
		if self.PreviewOn.get() == False:
			self.camera.stop_preview()
			state = 'disabled'
			self.ImageCanvas.itemconfigure('nopreview',state='normal')
			self.ImageCanvas.grid_remove();
		else:
			self.camera.stop_preview()
			state = '!disabled'
			if self.ShowOnScreen.get() == False:
				self.camera.start_preview(alpha=int(self.alpha.get()), \
					fullscreen=False,window=self.CanvasSize, \
					vflip=self.VFlipState, hflip=self.HFlipState)
				self.ImageCanvas.itemconfigure('nopreview',state='hidden')
				self.ImageCanvas.grid()
			else:
				self.camera.start_preview(alpha=int(self.alpha.get()), \
					fullscreen=False,window=(0,0,(int)(self.WindowSize.get()), \
					(int)(self.WindowSize.get())), \
					vflip=self.VFlipState, hflip=self.HFlipState)
				self.ImageCanvas.itemconfigure('nopreview',state='normal')
				self.ImageCanvas.grid_remove()
		self.alpha.state([state])
		self.Hflip.config(state=state)
		self.Vflip.config(state=state)
		self.Rotate.config(state=state)
		#WLW self.ShowOnMonitorButton.config(state=state)
		self.WindowSize.state(['disabled'] \
			if not ( self.PreviewOn.get() and self.ShowOnScreen.get() ) \
			else ['!disabled'])
	def AlphaChanged(self, newVal):
		val = int(float(newVal))
		self.camera.preview.alpha = val
		self.alpha.focus_set()
	def ToggleHFlip ( self ):
		self.HFlipState = not self.HFlipState
		#self.camera.preview.hflip = not self.camera.preview.hflip
		self.camera.hflip = not self.camera.hflip
	def ToggleVFlip ( self ):
		self.VFlipState = not self.VFlipState
		self.camera.vflip = not self.camera.vflip
		#self.camera.preview.vflip = not self.camera.preview.vflip
	def RotateCamera ( self ):
		r = (self.camera.rotation + 90) % 360
		self.camera.rotation = r
	def SetPreviewLocation ( self ):
		self.SetPreviewOn();
	def WindowSizeChanged ( self, newVal ):
		self.SetPreviewOn();
	def LoseFocus ( self, event ):
		'''
							The Combobox is a problem.
		Could save last two entries... if Combobox, Labelframe, Tk...
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
			if self.ShowOnScreen.get() == False:
				self.camera.preview.alpha = 0
			self.ImageCanvas.itemconfigure('nopreview',state='normal')
	def GotFocus ( self, event ):
		if self.camera.preview and not self.AlwaysPreview and \
			event.widget.winfo_class().lower() == 'tk' and \
			self.PreviewOn.get() and self.ImageCanvas.winfo_height() > 50:
			self.camera.preview.alpha = int(self.alpha.get())
			self.ImageCanvas.itemconfigure('nopreview',state='hidden')
	# We're catching the main form event to tell when a window has moved.
	# The preview window can be blanked during this time. This is STILL
	# buggy - that is why I added a Preview Overlay.
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
		self.CanvasSize = (int(self.ImageCanvas.winfo_rootx()+deltaWidth),
			  int(self.ImageCanvas.winfo_rooty()+deltaHeight),
			  int(self.ImageCanvas.winfo_width()),
			  int(self.ImageCanvas.winfo_height()))
		# ... and reset preview window to this position
		if self.camera.preview != None:
			if self.ShowOnScreen.get() == False:
				self.camera.preview.window = self.CanvasSize
			# Hide preview window if too small
			if self.CanvasSize[3] <= 50 and self.ShowOnScreen.get() == False:
				self.camera.preview.alpha = 0
			elif self.PreviewOn.get():
				self.camera.preview.alpha = int(self.alpha.get())
		# Not sure this should be here... could place inside the
		# preview window canvas form event. Cleaner approach.
		self.ImageCanvas.coords("nopreview",self.ImageCanvas.winfo_width()/2,
								self.ImageCanvas.winfo_height()/2)
	def UpdateAnnotationText ( self ):
		# Update annotation every second. Frame number is done automatically
		# Here we check if Annotation text is enabled, what the text is, and
		# whether time stamp is enabled.
		#AnnotationOverlayDialog.UseText = False
		#AnnotationOverlayDialog.Text = 'Text'
		#AnnotationOverlayDialog.Timestamp = False
		#AnnotationOverlayDialog.FrameNum = False
		#AnnotationOverlayDialog.Textsize = 32
		#AnnotationOverlayDialog.ColorYValue = 1.0
		if AnnotationPage.UseText is True:
			text = AnnotationPage.Text
		else:
			text = ""
		if AnnotationPage.Timestamp is True:
			try:	# in case a formatting error...
				t = dt.datetime.now().strftime(PreferencesDialog.DefaultTimestampFormat)
			except:
				t = "Bad format" # Should never get here...
			if text == "":		text = t
			else:					text = text + " (" + t + ")"
		self.camera.annotate_text = text
		self.after(1000,self.UpdateAnnotationText)
	def SystemPreferences ( self, event ):
		PreferencesDialog(self,title='PiCamera Preferences',camera=self.camera,
			minwidth=400,minheight=550,okonly=False)
		self.ControlMapping.SetControlMapping()
	def AnnotationOverlay ( self, event ):
		AnnotationOverlayDialog(self,title='Annotation / Overlay',
			camera=self.camera,okonly=False)
	def ViewStatusBar ( self, event ):
		if self.ViewStatusBarBoolean.get() is True:
			self.StatusBarFrame.grid()
		else:
			self.StatusBarFrame.grid_remove()
	def KeyboardShortcuts ( self, event ):
		KeyboardShortcutsDialog(self,title='Keyboard shortcuts', \
			resizable=True,minwidth=400,minheight=300) # minwidth does not work by itself, minwidth=300)
	# Must update as docs update ??
	def PiCameraDocs ( self, event ):
		webbrowser.open_new_tab('https://picamera.readthedocs.org/en/release-1.13/')
	# Must update as docs update ??
	def PiCameraRecipies ( self, event ):
		webbrowser.open_new_tab('https://picamera.readthedocs.io/en/release-1.13/recipes1.html')
	def HelpAbout ( self, event ):
		AboutDialog(self,title="About PiCamera",camera=self.camera)
	def quitProgram ( self, event ):
		if MessageBox.askyesno("Quit PiCamera","Exit %s?" % self.title):
			self.master.destroy()
	def GPIOError ( self ):
		if not RPiGPIO:
			MessageBox.showerror("GPIO Error",
				"GPIO library not found\n" + \
				"Please install RPi.GPIO and run this program as root.")
		else:
			MessageBox.showerror("GPIO Error",
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
	def DoPictureWindowPopup ( self, event ):
		if self.CurrentImage is None: return	# nothing to see here...
		try:
			# The popup menu is REALLY ugly
			# I don't like the way the popup interfacce works. You should
			# be able to right-click to bring up the popup, but then only
			# a left click selects a menu item. Not a right-click! Is there
			# a fix / workaround for this?
			self.CanvasPopup.tk_popup(event.x_root, event.y_root, 0)
		finally:
			# make sure to release the grab (Tk 8.0a1 only)
			self.CanvasPopup.grab_release()

def Run ():
	try:
		win = Tk()
	except:
		print ( "Error initializing Tkinter!\n\nShutting down\n\nPress any key" )
		raw_input()
		return

	Style().theme_use('clam')	# I like this theme, so sue me.

	try:
		# Bug in firmware? Must initialize to a value other than 0 to
		# allow changing to other modes later...
		camera = picamera.PiCamera(sensor_mode=1)
		camera.sensor_mode = 0	# go back to auto mode
	except PiCameraError:
		print ( "Error creating PiCamera instance! Shutting down.\n\nPress any key..." )
		raw_input()
		return

	win.minsize(1024,768)
	app = PiCameraApp(win,camera,title="PiCamera")
	win.mainloop()

	camera.close()

if __name__ == '__main__':
	print ( 'running....' )
	Run()

