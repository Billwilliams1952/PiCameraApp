#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  Exposure.py
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
	import 	ttk
	from 		ttk import *
except ImportError:
	from		tkinter import ttk
	from 		tkinter.ttk import *

from	PiCameraApp import *
from 	Dialog import *
from 	Mapping import *
from	NotePage import *
from	Utils import *

class Exposure ( BasicNotepage ):
	def BuildPage ( self ):
		f = ttk.Frame(self)
		f.grid(row=0,column=0,sticky='NSEW')
		f.columnconfigure(1,weight=1)

		#------------------- Metering Mode --------------------
		l = Label(f,text='Metering mode:')
		l.grid(row=0,column=0,sticky='W',pady=5)
		self.MeteringModeCombo = Combobox(f,state='readonly',width=20)
		self.MeteringModeCombo.grid(row=0,column=1,columnspan=3,sticky='W')
		l = list(self.camera.METER_MODES.keys())
		l.sort()
		self.MeteringModeCombo['values'] = l
		self.MeteringModeCombo.current(0)
		self.MeteringModeCombo.bind('<<ComboboxSelected>>',self.MeteringModeChanged)
		ToolTip(self.MeteringModeCombo,200)

		#------------------- Exposure Mode --------------------
		self.ExposureModeText = None
		f = ttk.LabelFrame(self,text='Exposure mode (Equivalent film ISO)',padding=(5,5,5,5))
		f.grid(row=1,column=0,sticky='NSW',pady=5) # was 4, columnspan=3,
		#f.columnconfigure(1,weight=1)

		self.ExposureModeVar = MyStringVar('auto')
		self.AutoExposureRadio = MyRadio(f,'Full auto (Default)','auto',
			self.ExposureModeVar,
			self.ExposureModeButton,0,0,'W',tip=205)
		MyRadio(f,'Preset exposures:','set',self.ExposureModeVar,
					self.ExposureModeButton,1,0,'W',tip=206)
		MyRadio(f,'Manually set ISO:','iso',self.ExposureModeVar,
					self.ExposureModeButton,2,0,'W',tip=207)
		MyRadio(f,'Off (Gains set at current value)','off',self.ExposureModeVar,
					self.ExposureModeButton,3,0,'W',span=2,tip=208) #was 2

		self.ExpModeCombo = Combobox(f,state='readonly',width=10)
		ToolTip(self.ExpModeCombo,209)
		self.ExpModeCombo.grid(row=1,column=1,sticky='W') #sticky='EW')
		self.ExpModeCombo.bind('<<ComboboxSelected>>',self.ExpModeChanged)
		exp = list(self.camera.EXPOSURE_MODES.keys())
		exp.remove('off')		# these two are handled by radio buttons
		exp.remove('auto')
		exp.sort() #cmp=lambda x,y: cmp(x.lower(),y.lower()))
		self.ExpModeCombo['values'] = exp
		self.ExpModeCombo.current(1)

		self.IsoCombo = Combobox(f,state='readonly',width=10)
		ToolTip(self.IsoCombo,210)
		self.IsoCombo.grid(row=2,column=1,sticky='W') #sticky='EW')
		self.IsoCombo.bind('<<ComboboxSelected>>',self.IsoChanged)
		self.IsoCombo['values'] = [100,200,320,400,500,640,800]
		self.IsoCombo.current(3)

		Separator(f,orient=HORIZONTAL).grid(pady=5,row=4,column=0,
			columnspan=2,sticky='EW') # was 3

		f1 = ttk.Frame(f)
		f1.grid(row=5,column=0,sticky='NS',columnspan=2) # was 2
		l = Label(f1,text='Analog gain:').grid(row=0,column=0,sticky='W')
		self.AnalogGain = ttk.Label(f1,style='DataLabel.TLabel')
		self.AnalogGain.grid(row=0,column=1,sticky=W,pady=2,padx=5)
		ToolTip(self.AnalogGain,211)
		l = Label(f1,text='Digital gain:').grid(row=0,column=2,sticky='W')
		self.DigitalGain = ttk.Label(f1,style='DataLabel.TLabel')
		self.DigitalGain.grid(row=0,column=3,sticky=W,pady=2,padx=5)
		ToolTip(self.DigitalGain,212)
		l = Label(f1,text='Actual ISO:').grid(row=1,column=0,sticky='W')
		self.EffIso = ttk.Label(f1,style='DataLabel.TLabel')
		self.EffIso.grid(row=1,column=1,sticky=W,pady=2,padx=5)
		ToolTip(self.EffIso,213)
		l = Label(f1,text='Apparent ISO:').grid(row=1,column=2,sticky='W')
		self.MeasIso = ttk.Label(f1,style='DataLabel.TLabel')
		self.MeasIso.grid(row=1,column=3,sticky=W,pady=2,padx=5)
		ToolTip(self.MeasIso,214)

		# -------------- Right frame ---------------
		f = ttk.LabelFrame(self,text='Exposure Compensation / DRC',
			padding=(5,5,5,5),width=150)
		f.grid(row=1,column=2,sticky='NS',pady=5) # was 4, columnspan=3,
		b = MyBooleanVar(True)
		self.AutoExposureRadio = MyRadio(f,'None (Default)',True,b,
					self.ExposureCompButton,0,0,'W',span=2,tip=231)
		MyRadio(f,'Amount:',False,b,
					self.ExposureCompButton,1,0,'W',tip=232)
		self.fstop = ttk.Label(f,width=16,padding=(5,5,5,5),style='DataLabel.TLabel')
		self.fstop.grid(row=2,column=1,sticky='W')
		self.ExpCompSlider = ttk.Scale(f,from_=-25,to=25,length=100,
				command=self.ExpComboSliderChanged,orient='horizontal')
		self.ExpCompSlider.grid(row=1,column=1,sticky='EW',pady=5)
		self.ExpCompSlider.set(0)
		ToolTip(self.ExpCompSlider,230)

		Separator(f,orient=HORIZONTAL).grid(pady=5,row=3,column=0,
			columnspan=2,sticky='EW') # was 3

		l = Label(f,text='Dynamic Range Compression') \
			.grid(row=4,column=0,sticky='W',columnspan=2)
		b = MyBooleanVar(False)
		self.DisableDRCRadio = MyRadio(f,'Disabled (Default)',False,b,
			self.DrcChecked,5,0,'W',pad=(0,5,10,5),tip=233,span=2)
		MyRadio(f,'Enabled',True,b,self.DrcChecked,6,0,'W',
			pad=(0,5,10,5),tip=234)
		self.DrcCombo = Combobox(f,state='readonly',width=5)
		self.DrcCombo.grid(row=6,column=1,sticky='EW')
		ToolTip(self.DrcCombo,235)
		vals = self.camera.DRC_STRENGTHS
		vals = list(vals.keys())
		vals.remove('off')		# Handled by radio button
		self.DrcCombo['values'] = vals
		self.DrcCombo.current(0)
		self.DrcCombo.bind('<<ComboboxSelected>>',self.DrcStrengthChanged)

		#------------------- Auto White Balance --------------------
		f = ttk.LabelFrame(self,text='Auto white balance settings',padding=(5,5,5,5))
		f.grid(row=2,column=0,columnspan=5,sticky='NEWS',pady=5)
		#f.columnconfigure(2,weight=1)
		#f.columnconfigure(4,weight=1)

		self.AWBText = None
		self.AutoAWB = MyStringVar('auto')
		self.AWBRadio = MyRadio(f,'Auto','auto',self.AutoAWB,self.AutoAWBChecked,
			0,0,'NW',tip=250)
		MyRadio(f,'Select:','sel',self.AutoAWB,self.AutoAWBChecked,1,0,'NW',tip=251)
		MyRadio(f,'Off','off',self.AutoAWB,self.AutoAWBChecked,2,0,'NW',tip=252)

		Label(f,text='Default').grid(row=0,column=1,sticky='E')
		Label(f,text='Mode:').grid(row=1,column=1,sticky='E',pady=5)
		self.awb = Combobox(f,state='readonly',width=12)
		ToolTip(self.awb,253)
		self.awb.grid(row=1,column=2,columnspan=1,sticky='W')
		self.awb.bind('<<ComboboxSelected>>',self.AWBModeChanged)
		modes = list(self.camera.AWB_MODES.keys())
		modes.sort() #cmp=lambda x,y: cmp(x.lower(),y.lower()))
		modes.remove('off')	# these two are handled by the radiobuttons
		modes.remove('auto')
		self.awb['values'] = modes
		self.awb.current(0)

		okCmd = (self.register(self.ValidateGains),'%P')
		Label(f,text='Red gain:').grid(row=2,column=1,sticky=E)
		self.RedGain = StringVar()
		self.RedEntry = Entry(f,textvariable=self.RedGain,width=10,
			validate='all',validatecommand=okCmd)
		self.RedEntry.grid(row=2,column=2,sticky='W')
		ToolTip(self.RedEntry,254)

		Label(f,text='Blue gain:').grid(row=2,column=3,sticky=W)
		self.BlueGain = StringVar()
		self.BlueEntry = Entry(f,textvariable=self.BlueGain,width=10,
			validate='all',validatecommand=okCmd)
		self.BlueEntry.grid(row=2,column=4,sticky='W')
		ToolTip(self.BlueEntry,255)

		#------------------- Shutter Speed --------------------
		self.ShutterSpeedText = None
		self.Multiplier = 1
		f = ttk.LabelFrame(self,text='Shutter speed',padding=(5,5,5,5))
		f.grid(row=3,column=0,columnspan=4,sticky='NEWS',pady=5)
		#f.columnconfigure(2,weight=1)
		self.ShutterSpeedAuto = MyBooleanVar(True)
		self.AutoShutterRadio = MyRadio(f,'Auto (Default)',True,self.ShutterSpeedAuto,
			self.ShutterSpeedButton,0,0,'W',span=2,tip=300)
		l = Label(f,text='Current Exposure:')
		l.grid(row=0,column=1,sticky=W,pady=5)
		self.ExposureSpeed = ttk.Label(f,style='DataLabel.TLabel')
		self.ExposureSpeed.grid(row=0,column=2,sticky=W)
		ToolTip(self.ExposureSpeed,301)
		MyRadio(f,'Set shutter speed:',False,self.ShutterSpeedAuto,
			self.ShutterSpeedButton,1,0,'W',tip=302)
		okCmd = (self.register(self.ValidateShutterSpeed),'%P')
		self.ShutterSpeed = StringVar()
		self.ShutterSpeedEntry = Entry(f,textvariable=self.ShutterSpeed,width=7,
			validate='all',validatecommand=okCmd)
		self.ShutterSpeedEntry.grid(row=1,column=1,sticky='EW')
		ToolTip(self.ShutterSpeedEntry,303)
		self.ShutterSpeedCombo = Combobox(f,state='readonly',width=6)
		self.ShutterSpeedCombo.grid(row=1,column=2,columnspan=1,sticky='W')
		self.ShutterSpeedCombo['values'] = ['usec','msec','sec']
		self.ShutterSpeedCombo.current(0)
		self.ShutterSpeedCombo.bind('<<ComboboxSelected>>',self.ShutterSpeedComboChanged)
		ToolTip(self.ShutterSpeedCombo,304)
		self.SlowestShutterSpeed = ttk.Label(f,style='RedMessage.TLabel')
		self.SlowestShutterSpeed.grid(row=2,column=0,columnspan=4,sticky='W')

		#------------------- Frame Rate --------------------
		self.FPSText = None
		f = MyLabelFrame(self,'Frame rate',4,0,span=4)
		#f.columnconfigure(2,weight=1)

		l = Label(f,text='Current frame rate:').grid(row=0,column=0,sticky='W')
		self.FrameRate = ttk.Label(f,style='DataLabel.TLabel')
		self.FrameRate.grid(row=0,column=1,columnspan=3,sticky='W')
		ToolTip(self.FrameRate,310)

		self.FixedFrameRateBool = MyBooleanVar(True)
		self.ffr = MyRadio(f,'Fixed frame rate:',True,self.FixedFrameRateBool,
			self.FixedFrameRateChecked,1,0,'W',tip=311)
		okCmd = (self.register(self.ValidateFixedRange),'%P')
		self.FixedFramerateText = MyStringVar("30.0")
		self.FixedFramerateEntry = Entry(f,width=6,validate='all',
			validatecommand=okCmd,textvariable=self.FixedFramerateText)
		self.FixedFramerateEntry.grid(row=1,column=1,sticky='W')
		ToolTip(self.FixedFramerateEntry,312)
		l = Label(f,text='FPS').grid(row=1,column=2,sticky='W')

		Label(f,text='Delta:').grid(row=1,column=3,sticky='E',padx=(5,0))
		okCmd = (self.register(self.ValidateFramerateDelta),'%P')
		self.FramerateDeltaText = MyStringVar("0.0")
		self.FramerateDelta = Entry(f,width=6,validate='all',
			validatecommand=okCmd,textvariable=self.FramerateDeltaText)
		self.FramerateDelta.grid(row=1,column=4,sticky='W')
		ToolTip(self.FramerateDelta,315)
		Label(f,text='FPS').grid(row=1,column=5,sticky='W')

		MyRadio(f,'Frame rate range:',False,
			self.FixedFrameRateBool,
			self.FixedFrameRateChecked,2,0,'W',tip=313)
		#Label(f,text='Frame rate range:').grid(row=2,column=0,sticky='W')
		ok1Cmd = (self.register(self.ValidateFramerateRangeFrom),'%P')
		self.FramerateRangeFromText = MyStringVar("1/6")
		self.FramerateFrom = Entry(f,width=6,validate='all',
			textvariable=self.FramerateRangeFromText)
		self.FramerateFrom.grid(row=2,column=1,sticky='W')
		ToolTip(self.FramerateFrom,314)
		Label(f,text='FPS').grid(row=2,column=2,sticky='W')
		Label(f,text='To:').grid(row=2,column=3,sticky='E')
		self.FramerateRangeToText = MyStringVar("30.0")
		ok2Cmd = (self.register(self.ValidateFramerateRangeTo),'%P')
		self.FramerateTo = Entry(f,width=6,validate='all',
			validatecommand=ok2Cmd,textvariable=self.FramerateRangeToText)
		self.FramerateTo.grid(row=2,column=4,sticky='W')
		ToolTip(self.FramerateTo,316)
		l = Label(f,text='FPS').grid(row=2,column=5,sticky='W')

		self.FramerateFrom.config(validatecommand=ok1Cmd)

		self.AutoExposureRadio.invoke()
		self.DrcChecked(False)
		self.CheckGains()
		self.ExposureModeButton('auto')
		self.AutoAWBChecked('auto')
		self.ShowAWBGains()
		self.AutoShutterRadio.invoke()
		self.ExpModeCombo.focus_set()
		self.ffr.invoke()
		self.UpdateFrameRate()

	#### TODO: Implement Reset IN WORK
	def Reset ( self ):
		self.MeteringModeCombo.current(0)
		self.ExposureModeVar.set('auto')
		self.ExposureModeButton('auto')		# invoke not working here??
		self.AWBRadio.invoke()
		self.AutoShutterRadio.invoke()
		self.ExpCompSlider.set(0)
		self.ShutterSpeedCombo.current(0)
		self.MeteringModeCombo.focus_set()
		self.DisableDRCRadio.invoke()
		self.DisableDRCRadio.focus_set()
		self.FixedFramerateText.set("30")
		self.FramerateDeltaText.set("0")
		self.FramerateRangeFromText.set("1/6")
		self.FramerateRangeToText.set("30")
		self.ffr.invoke()
	def SetVariables ( self, ExposureModeText, AWBText,
			ShutterSpeedText, FPSText):
		self.ExposureModeText = ExposureModeText
		self.AWBText = AWBText
		self.ShutterSpeedText = ShutterSpeedText
		self.FPSText = FPSText
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
			self.ExpModeCombo.focus_set()
			self.IsoCombo.config(state='disabled')
			self.ExpModeChanged(None)
		else:	# mode = 'iso'
			self.ExpModeCombo.config(state='disabled')
			self.IsoCombo.config(state='readonly')
			self.IsoCombo.focus_set()
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
		if self.ExposureModeText:
			self.ExposureModeText.set('AG: %.3f DG: %.3f' % (ag, dg))
		if not dg == 0:
			self.EffIso.config(text='%d' % int(ag / dg * 100.0))
		else:
			self.EffIso.config(text="Unknown! Digital Gain is 0")
		self.MeasIso.config(text= \
			'Auto' if self.camera.iso == 0 else str(self.camera.iso) )
		self.after(300,self.CheckGains)
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
	def DrcChecked ( self, DrcEnabled ):
		if DrcEnabled == False:
			self.camera.drc_strength = 'off'
			self.DrcCombo.config(state = 'disabled')
		else:
			self.DrcStrengthChanged(None)
			self.DrcCombo.config(state = 'readonly')
			self.DrcCombo.focus_set()
	def DrcStrengthChanged ( self, event ):
		self.camera.drc_strength = self.DrcCombo.get()
	def AutoAWBChecked ( self, AwbMode ):
		if AwbMode == 'auto' or AwbMode == 'sel':
			self.camera.awb_mode = 'auto' if AwbMode == 'auto' else self.awb.get()
			self.ShowAWBGains()
			if AwbMode == 'sel': self.awb.focus_set()
		else:	# 'off'
			gains = self.camera.awb_gains
			self.camera.awb_mode = 'off'
			self.RedGain.set('%.3f' % gains[0])
			self.RedEntry.focus_set()
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
			if self.AWBText:
				self.AWBText.set('RG: %.3f BG: %.3f' % (gains[0],gains[1]))
		else:
			self.UpdateGains()
		self.after(300,self.ShowAWBGains)
	def AWBModeChanged ( self, event ):
		self.camera.awb_mode = self.awb.get()
	def ExposureCompButton ( self, val ):
		if val is True:
			self.ExpCompSlider.state(['disabled'])
			self.camera.exposure_compensation = 0
		else:
			self.ExpCompSlider.state(['!disabled'])
			self.ExpCompSlider.focus_set()
			self.camera.exposure_compensation = int(self.ExpCompSlider.get())
	def ExpComboSliderChanged ( self, newVal ):
		val = float(newVal)
		if val == 0.0:
			self.fstop.config(text = 'None (Default)')
		else:
			self.fstop.config(text = '%s %.2f fstops' % (
				'Close' if val < 0.0 else 'Open', abs(val) / 6.0) )
		self.camera.exposure_compensation = int(val)
		self.ExpCompSlider.focus_set()
	def ShutterSpeedButton ( self, val ):
		if self.ShutterSpeedAuto.get() == True:
			self.camera.shutter_speed = 0
			self.ShutterSpeedEntry.config(state='disabled')
			self.ShutterSpeedCombo.state(['disabled'])
			self.ShutterSpeedCombo.current(0)
			self.after(300,self.CheckShutterSpeed)
		else:
			self.camera.shutter_speed = int(self.ShutterSpeed.get())
			self.ShutterSpeedEntry.config(state='normal') #'!disabled')
			self.ShutterSpeedCombo.state(['!disabled'])
			self.ShutterSpeedEntry.focus_set()
	def CheckShutterSpeed ( self ):
		val = self.camera.exposure_speed
		txt = USECtoSec(val)
		self.ExposureSpeed.config(text=txt)
		self.ShutterSpeed.set(str(val))
		if self.ShutterSpeedText:
			self.ShutterSpeedText.set('ES: '+txt)
		if self.ShutterSpeedAuto.get() is True:
			self.after(300,self.CheckShutterSpeed)
	def ValidateShutterSpeed ( self, EntryIfAllowed ):
		if self.ShutterSpeedAuto.get() is True:
			return True
		try:	val = int(self.Multiplier * float(EntryIfAllowed))
		except:	val = -1
		if self.camera.framerate == 0:
			r = self.camera.framerate_range
			ul = int(1.0e6 / r[0])		# Lower limit on range
			ll = 1 # int(1.0e6 / r[1])
		else:
			ul = int(1.0e6 / (self.camera.framerate + self.camera.framerate_delta))
			ll = 1	# 1 usec is the fastest speed
		if val >= ll and val <= ul:
			self.camera.shutter_speed = val
			txt = USECtoSec(val)
			self.ExposureSpeed.config(text=txt)
			if self.ShutterSpeedText:
				self.ShutterSpeedText.set('ES: '+txt)
		return True
	def ShutterSpeedComboChanged (self, event ):
		self.Multiplier = int(pow(10,3 * self.ShutterSpeedCombo.current()))
		self.ValidateShutterSpeed(self.ShutterSpeedEntry.get())
	def FixedFrameRateChecked ( self, val ):
		if val is True:	# Fixed frame rate
			state = 'normal'
			state1 = 'disabled'
			self.FixedFramerateEntry.focus_set()
			self.ValidateFixedRange(self.FixedFramerateText.get())
		else:		# Frame rate range
			state = 'disabled'
			state1 = 'normal'
			self.ValidateFramerateRangeFrom(self.FramerateRangeFromText.get())
			self.ValidateFramerateRangeTo(self.FramerateRangeToText.get())
			self.FramerateFrom.focus_set()
		self.FixedFramerateEntry.config(state=state)
		self.FramerateDelta.config(state=state)
		self.FramerateFrom.config(state=state1)
		self.FramerateTo.config(state=state1)
	def ValidateEntry ( self, entry, minVal, maxVal ):
		'''
		Change how the edit fields work. Allow a '/' in the edit field to
		denote a fraction.
		Split on '/' and evaluate each side. Note, if '<num> /' then
		num is evalulated since 'den' is empty
		'''
		vals = entry.split('/',1)	# entry is text
		val = vals[0].strip()
		try:		num = float(val)
		except:	num = None
		else:
			if len(vals) > 1:
				val = vals[1].strip()
				if val:
					try:			den = float(val)
					except:		num = None
					else:
						if den > 0:	num = num / den
						else:			num = None
		if num is not None:
			num = num if num >= minVal and num <= maxVal else None
		self.FrameRate.config(style='RedMessage.TLabel' if num is None \
									  else 'DataLabel.TLabel')
		return num
	def ValidateFixedRange ( self, EntryIfAllowed ):
		rate = self.ValidateEntry(EntryIfAllowed, 1.0/6.0, 90.0 )
		if rate != None:
			self.camera.framerate = rate
			self.ValidateShutterSpeed(None)
		return True
	def ValidateRange ( self, fromText, toText ):
		fromVal = self.ValidateEntry(fromText, 1.0/6.0, 90.0 )
		toVal = self.ValidateEntry(toText, 1.0/6.0, 90.0 )
		if fromVal != None and toVal != None and \
			fromVal >= 1.0/6.0 and fromVal < toVal and toVal <= 90.0:
			self.camera.framerate_range = (fromVal,toVal)
			self.ValidateShutterSpeed(None)
			self.FrameRate.config(style='DataLabel.TLabel')
		else:
			self.FrameRate.config(style='RedMessage.TLabel')
	def ValidateFramerateRangeFrom ( self, text ):
		self.ValidateRange(text,self.FramerateRangeToText.get())
		return True
	def ValidateFramerateRangeTo ( self, text ):
		self.ValidateRange(self.FramerateRangeFromText.get(),text)
		return True
	def ValidateFramerateDelta ( self, text ):
		# Can delta be negative - YEP!!
		delta = self.ValidateEntry(text, -10.0, 10.0 )
		if delta != None:
			self.camera.framerate_delta = delta
			self.ValidateShutterSpeed(None)
		return True
	def UpdateFrameRate ( self ):
		if self.camera.framerate == 0:
			r = self.camera.framerate_range
			txt = 'Auto fps'
			txt1 = '%.3f to %.3f fps' % (r[0],r[1])
			t = USECtoSec(int(1.0e6 / r[0]))
		else:
			r = self.camera.framerate + self.camera.framerate_delta
			txt = '%.3f fps' % r
			txt1 = txt
			t = USECtoSec(int(1.0e6 / r))
		self.FrameRate.config(text=txt1)
		if self.FPSText:	self.FPSText.set(txt)
		self.SlowestShutterSpeed.config(text='Slowest shutter speed: %s' % t)
		self.after(300,self.UpdateFrameRate)
