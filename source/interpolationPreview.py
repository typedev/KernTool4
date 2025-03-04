"""
Interpolation Preview @typedev
inspired by
Interpolation Slider
by Andy Clymer, June 2018
"""

import vanilla
from vanilla.dialogs import getFile
import os
from merz import *
from fontParts import *
import AppKit
import mojo
from mojo.subscriber import Subscriber, registerCurrentGlyphSubscriber
from mojo.events import addObserver, removeObserver
from lib.eventTools.eventManager import postEvent, publishEvent
from mojo.pens import DecomposePointPen
import designspaceProblems as DP
import importlib

import tdGlyphparser
# import tdKernToolEssentials4
# importlib.reload(tdKernToolEssentials4)
# from tdKernToolEssentials4 import *

# import tdGlyphsMatrix
#
# importlib.reload(tdGlyphsMatrix)
# from tdGlyphsMatrix import *

# import tdCanvasKeysDecoder
# importlib.reload(tdCanvasKeysDecoder)
# from tdCanvasKeysDecoder import *


import tdGlyphsMerzView
importlib.reload(tdGlyphsMerzView)
from tdGlyphsMerzView import *

import tdKeyCommander
importlib.reload(tdKeyCommander)
from tdKeyCommander import *

from tdGlyphparser import *
EVENT_REFRESHVIEW = 'typedev.interpolationPreview.refresh'



class TDInterpolationPreview(Subscriber):  # , WindowController

	debug = True

	def build (self):

		self.w = vanilla.Window((600, 800), minSize = (300, 300), title = 'Interpolation Preview')  # , autosaveName = PREFKEY_WindowSize)

		self.fontNames = []
		self.id = getUniqName()
		
		self.w.g = vanilla.Group((0, 120, -0, -0))#, dropSettings = dropSettings) (0, 150, -0, -0)

		self.w.g.glyphsView = TDGlyphsMerzView(
			delegate = self,
			posSize = (0, 0, -0, -0),  # (5, 35, -5, -290)
			backgroundColor = COLOR_BACKGROUND,  # (1, 1, 1, 1),#(.75, .73, .7, .8),
		)
		self.w.g.glyphsView.selectionMode = SELECTION_MODE_GLYPH
		self.w.g.glyphsView.showKerning = False
		self.w.g.glyphsView.switchMargins(True)
		self.w.g.glyphsView.scaleFactor = pt2Scale(250)
		self.w.g.glyphsView.maxGlyphSize = 1000
		self.w.g.glyphsView.pointSizeMargins = 12
		self.w.g.glyphsView.useRayBeam = True
		self.w.g.glyphsView.useVerticalRayBeam = True
		self.w.g.glyphsView.useRayStems = True


		self.w.fontA = vanilla.PopUpButton((10, 15, -10, 25), [], callback = self.optionsChanged, sizeStyle = "regular")
		self.w.fontB = vanilla.PopUpButton((10, 40, -10, 25), [], callback = self.optionsChanged, sizeStyle = "regular")
		self.w.interpolationSliderX = vanilla.Slider((10, 65, -10, 25), callback = self.optionsChanged, minValue = 0, maxValue = 1) # (10, 65, -70, 25)
		# self.w.interpolationSliderY = vanilla.Slider((10, 90, -70, 25), callback = self.optionsChanged, minValue = 0, maxValue = 1)
		# self.w.checkLinked = vanilla.CheckBox((-60,80,50,25), title = '􀉤',value = True, callback = self.optionsChanged)
		self.w.textLineEdit = vanilla.EditText((10,90,-10,22), '/?', callback = self.optionsChanged) # (10,120,-10,22)

		self.interpolationFactorX = 500
		self.w.interpolationSliderX.set(0.5)
		self.interpolationFactorY = 500
		# self.w.interpolationSliderY.set(0.5)
		self.linkedSliders = True

		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_LEFT, callback = self.setInterpolationFactorCallbackX, callbackValue = -10)
		self.keyCommander.registerKeyCommand(KEY_LEFT, alt = True, callback = self.setInterpolationFactorCallbackX, callbackValue = -1)
		self.keyCommander.registerKeyCommand(KEY_LEFT, shift = True, callback = self.setInterpolationFactorCallbackX, callbackValue = -100)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, callback = self.setInterpolationFactorCallbackX, callbackValue = 10)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, alt = True, callback = self.setInterpolationFactorCallbackX, callbackValue = 1)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, shift = True, callback = self.setInterpolationFactorCallbackX, callbackValue = 100)

		self.keyCommander.registerKeyCommand(KEY_DOWN, cmd = True, callback = self.setInterpolationFactorCallbackY, callbackValue = -10)
		self.keyCommander.registerKeyCommand(KEY_DOWN, cmd = True, alt = True, callback = self.setInterpolationFactorCallbackY, callbackValue = -1)
		self.keyCommander.registerKeyCommand(KEY_DOWN, cmd = True, shift = True, callback = self.setInterpolationFactorCallbackY, callbackValue = -100)
		self.keyCommander.registerKeyCommand(KEY_UP, cmd = True, callback = self.setInterpolationFactorCallbackY, callbackValue = 10)
		self.keyCommander.registerKeyCommand(KEY_UP, cmd = True, alt = True, callback = self.setInterpolationFactorCallbackY, callbackValue = 1)
		self.keyCommander.registerKeyCommand(KEY_UP, cmd = True, shift = True, callback = self.setInterpolationFactorCallbackY, callbackValue = 100)

		self.keyCommander.registerKeyCommand(KEY_M, cmd = True, shift = True, callback = self.interpolateInstanceCallback)

		if CurrentDesignspace():
			print('Designspace found', CurrentDesignspace())
			self.dsChecker = DP.DesignSpaceChecker(CurrentDesignspace())
		else:
			self.dsChecker = None	



	def windowClose (self, sender):
		removeObserver(self, EVENT_REFRESHVIEW)

	def started (self):
		addObserver(self, 'refreshFromOutside', EVENT_REFRESHVIEW)
		self.w.open()
		self.w.bind('close', self.windowClose)
		self.collectFonts()

	def glyphDidChange (self, info):
		self.showPreview()
		postEvent(EVENT_REFRESHVIEW, idsender = self.id)

	def roboFontDidSwitchCurrentGlyph (self, info):
		self.showPreview()
		postEvent(EVENT_REFRESHVIEW, idsender = self.id)

	def optionsChanged (self, sender):
		if sender == self.w.interpolationSliderX and self.linkedSliders:
			# self.w.interpolationSliderY.set(self.w.interpolationSliderX.get())
			self.interpolationFactorX = self.w.interpolationSliderX.get() * 1000
			# self.interpolationFactorY = self.w.interpolationSliderY.get() * 1000
		elif sender == self.w.interpolationSliderX and not self.linkedSliders:
			self.interpolationFactorX = self.w.interpolationSliderX.get() * 1000
			# self.interpolationFactorY = self.w.interpolationSliderY.get() * 1000
		# elif sender == self.w.interpolationSliderY and self.linkedSliders:
		# 	self.w.interpolationSliderX.set(self.w.interpolationSliderY.get())
		# 	self.interpolationFactorX = self.w.interpolationSliderX.get() * 1000
		# 	self.interpolationFactorY = self.w.interpolationSliderY.get() * 1000
		# elif sender == self.w.interpolationSliderY and not self.linkedSliders:
		# 	self.interpolationFactorX = self.w.interpolationSliderX.get() * 1000
		# 	self.interpolationFactorY = self.w.interpolationSliderY.get() * 1000
		self.showPreview()

	def refreshFromOutside (self, info):
		if 'idsender' in info and info['idsender'] != self.id:
			self.showPreview()

	def showPreview (self):
		textline = self.w.textLineEdit.get()
		if textline and '/?' in textline:
			try:
				gName = CurrentGlyph().name
				textline = textline.replace('/?', '/%s' % gName)
			except:
				return
		elif textline:
			pass
		else:
			try:
				gName = CurrentGlyph().name
				textline = textline.replace('/?', '/%s' % gName)
			except:
				return
		glyphsLineNames = tdGlyphparser.translateText(CurrentFont(), textline)

		iscaleX = self.interpolationFactorX / 1000
		# iscaleY = self.interpolationFactorY / 1000

		fontA = self.fonts[self.w.fontA.get()]
		fontB = self.fonts[self.w.fontB.get()]

		glyphsPreview = []
		for glyphName in glyphsLineNames:

			if glyphName not in fontA or glyphName not in fontB: return
			glyphA = fontA[glyphName]
			glyphB = fontB[glyphName]

			tempLeftGlyph = glyphA.copy()
			tempRightGlyph = glyphB.copy()

			if glyphA.components != None and glyphB.components != None:
				dstGlyphL = RGlyph()
				dstGlyphL.width = glyphA.width
				dstPenL = dstGlyphL.getPointPen()
				decomposePenL = DecomposePointPen(fontA, dstPenL)
				glyphA.drawPoints(decomposePenL)
				tempLeftGlyph = dstGlyphL
	
				dstGlyphR = RGlyph()
				dstGlyphR.width = glyphB.width
				dstPenR = dstGlyphR.getPointPen()
				decomposePenR = DecomposePointPen(fontB, dstPenR)
				glyphB.drawPoints(decomposePenR)
				tempRightGlyph = dstGlyphR

			g = RGlyph()
			if self.linkedSliders:
				g.interpolate(iscaleX, tempLeftGlyph, tempRightGlyph)
			else:
				g.interpolate(iscaleX, tempLeftGlyph, tempRightGlyph) # (iscaleX,iscaleY)
			g.name = glyphName
			glyphsPreview.append(g)
			self.w.g.glyphsView.setStatus('factor:', value = str(int(round(iscaleX * 1000, 0))), status = True)
			# self.w.g.glyphsView.setStatus('factorY:', value = str(int(round(iscaleY * 1000, 0))), status = True)
			if self.dsChecker:
				print('Checking glyphs...')
				self.dsChecker.checkGlyphs()
				report = []
				for problem in self.dsChecker.problems:
					cat, desc = problem.getDescription()
					if cat == 'glyphs' and desc == 'incompatible glyph':
						if 'glyphName' in problem.data:
							report.append(problem.data['glyphName'])
				if report:
					if glyphName in report:
						self.w.g.glyphsView.setStatus('compatibility:', value = 'incompatible', status = True)
					else:
						self.w.g.glyphsView.setStatus('compatibility:', value = 'Ok', status = True)


		matrix = dict(glyphs = glyphsPreview)
		self.w.g.glyphsView.startDrawGlyphsMatrix( [ matrix ] )

	def interpolateInstance(self):
		iscaleX = self.interpolationFactorX / 1000
		# iscaleY = self.interpolationFactorY / 1000

		fontA = self.fonts[self.w.fontA.get()]
		fontB = self.fonts[self.w.fontB.get()]

		fontI = NewFont()
		if self.linkedSliders:
			fontI.interpolate(iscaleX, fontA, fontB)
		else:
			fontI.interpolate(iscaleX, fontA, fontB) # (iscaleX,iscaleY)
		fontI.kerning.interpolate(iscaleX, fontA.kerning, fontB.kerning)
		fontI.lib['public.glyphOrder'] = fontA.lib['public.glyphOrder']
		fontI.glyphOrder = fontA.lib['public.glyphOrder']


	def interpolateInstanceCallback(self, sender, value):
		self.interpolateInstance()

	def setInterpolationFactorCallbackX(self, sender, value):
		self.setInterpolationFactor(factorX = value)
	def setInterpolationFactorCallbackY(self, sender, value):
		self.setInterpolationFactor(factorY = value)

	def setInterpolationFactor (self, factorX=None, factorY=None):
		if factorX == None and self.linkedSliders:
			self.interpolationFactorY += factorY
			self.interpolationFactorX = self.interpolationFactorY
		elif factorX == None and not self.linkedSliders:
			self.interpolationFactorY += factorY
			self.interpolationFactorX = self.w.interpolationSliderX.get() * 1000
		if factorY == None and self.linkedSliders:
			self.interpolationFactorX += factorX
			# self.interpolationFactorY = self.interpolationFactorX
		elif factorY == None and not self.linkedSliders:
			self.interpolationFactorX += factorX
			# self.interpolationFactorY = self.w.interpolationSliderY.get() * 1000
		self.w.interpolationSliderX.set(self.interpolationFactorX / 1000)
		# self.w.interpolationSliderY.set(self.interpolationFactorY / 1000)
		self.showPreview()

	def acceptsFirstResponder (self, info):
		return True
	def sizeChanged (self, sender):
		sender.eventResizeView()
	def mouseUp (self, sender, event):
		sender.eventMouseUp(event)
	def mouseDragged (self, sender, event):
		sender.eventMouseDragged(event)
	def scrollWheel (self, sender, event):
		sender.eventScrollWheel(event)
	def magnifyWithEvent (self, sender, event):
		sender.eventMagnify(event)
	def mouseDown (self, sender, event):
		sender.eventMouseDown(event)

	def keyDown (self, sender, event):
		self.keyCommander.checkCommand(sender,event)
		sender.eventKeyDown(sender,event)

# =========================================================================================
	def getFontName (self, font, fonts):
		# by Andy Clymer, June 2018
		# A helper to get the font name, starting with the preferred name and working back to the PostScript name
		# Make sure that it's not the same name as another font in the fonts list
		if font.info.openTypeNamePreferredFamilyName and font.info.openTypeNamePreferredSubfamilyName:
			name = "%s %s" % (font.info.openTypeNamePreferredFamilyName, font.info.openTypeNamePreferredSubfamilyName)
		elif font.info.familyName and font.info.styleName:
			name = "%s %s" % (font.info.familyName, font.info.styleName)
		elif font.info.fullName:
			name = font.info.fullName
		elif font.info.fullName:
			name = font.info.postscriptFontName
		else: name = "Untitled"
		# Add a number to the name if this name already exists
		if name in fonts:
			i = 2
			while name + " (%s)" % i in fonts:
				i += 1
			name = name + " (%s)" % i
		return name

	def collectFonts (self):
		# by Andy Clymer, June 2018
		# Hold aside the current font choices
		font0idx = self.w.fontA.get()
		font1idx = self.w.fontB.get()
		if not font0idx == -1:
			font0name = self.fontNames[font0idx]
		else: font0name = None
		if not font1idx == -1:
			font1name = self.fontNames[font1idx]
		else: font1name = None
		# Collect info on all open fonts
		self.fonts = AllFonts()
		self.fontNames = []
		for font in self.fonts:
			self.fontNames.append(self.getFontName(font, self.fontNames))
		# Update the popUpButtons
		self.w.fontA.setItems(self.fontNames)
		self.w.fontB.setItems(self.fontNames)
		# If there weren't any previous names, try to set the first and second items in the list
		if font0name == None:
			if len(self.fonts):
				self.w.fontA.set(0)
		if font1name == None:
			if len(self.fonts) >= 1:
				self.w.fontB.set(1)
		# Otherwise, if there had already been fonts choosen before new fonts were loaded,
		# try to set the index of the fonts that were already selected
		if font0name in self.fontNames:
			self.w.fontA.set(self.fontNames.index(font0name))
		if font1name in self.fontNames:
			self.w.fontB.set(self.fontNames.index(font1name))

def main():
	registerCurrentGlyphSubscriber(TDInterpolationPreview)

if __name__ == "__main__":
	main()
