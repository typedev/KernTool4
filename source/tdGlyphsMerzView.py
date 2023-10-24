
import merz

from merz import *
from fontParts import *
# from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber, registerRoboFontSubscriber, registerCurrentFontSubscriber
from merz.tools.drawingTools import NSImageDrawingTools
from mojo.pens import DecomposePointPen
import AppKit
import math
import importlib
import tdKernToolEssentials4
importlib.reload(tdKernToolEssentials4)
from tdKernToolEssentials4 import *

import tdGlyphsMatrix
importlib.reload(tdGlyphsMatrix)


# import tdCanvasKeysDecoder
# importlib.reload(tdCanvasKeysDecoder)
# from tdCanvasKeysDecoder import *

# import tdPairsMaker
# importlib.reload(tdPairsMaker)
# from tdPairsMaker import PairsBuilderDialogWindow

import tdSpaceControl
importlib.reload(tdSpaceControl)
from tdSpaceControl import *

import tdKeyCommander
importlib.reload(tdKeyCommander)
from tdKeyCommander import *

import tdGlyphparser




def italicShift (angle, Ypos):
	if angle:
		return Ypos * math.tan(abs(angle) * 0.0175)
	else:
		return 0

def getGlyphName_fromBoxLayer(layer):
	if not layer: return None
	glypboxname = layer.getName()
	if glypboxname and 'glyphbox.' in glypboxname:
		return glypboxname.replace('glyphbox.','')
	return None

def getGlyphsNames_fromGlyphsLineLayer(glyphsLineLayer):
	### version 1
	# _g = []
	# for boxlayer in glyphsLineLayer.getSublayers():
	# 	glyphname = getGlyphName_fromBoxLayer(boxlayer)
	# 	if glyphname:
	# 		_g.append(glyphname)

	### version 2
	glyphs = glyphsLineLayer.getInfoValue('uniqnames')

	## test indexes
	# _g = glyphsLineLayer.getInfoValue('uniqnames')
	# print ('checkin indexes')
	# for idx, gg in enumerate(_g):
	# 	if gg != glyphs[idx]:
	# 		print ('ERROR 1', '+'*80)
	# 		print('inbox', glyphs)
	# 		print ('inlayer', glyphsLineLayer.getInfoValue('uniqnames'))
	# if len(_g) != len(glyphs):
	# 	print('ERROR 2', '+' * 80)
	# 	print('inbox', glyphs)
	# 	print('inlayer', glyphsLineLayer.getInfoValue('uniqnames'))
	return glyphs

def convertGlyphName2unicode(font, glyphName):
	glyphName = cutUniqName(glyphName)
	# if not font: return
	if font[glyphName].unicode:
		return chr(int("%04X" % (font[glyphName].unicode), 16))
	else:
		return '/%s ' % glyphName

def prepareGlyphsMatrix(glyphslines, fonts, lineinfo = None):
	matrix = []
	idx = 0
	for glist in glyphslines:
		link = getUniqName()
		for font in fonts:
			gline = []
			idx += 1
			for gn in glist:
				if gn in font:
					gline.append(font[gn])
			if len(fonts) != 1:
				# lineinfo = '%s %s\n\n%i:%i' % (font.info.familyName, font.info.styleName, idx, len(fonts) * len(glyphslines))
				lineinfo = '%s %s' % (font.info.familyName, font.info.styleName)

			else:
				lineinfo = lineinfo
				# lineinfo = '%i:%i' % ( idx, len(glyphslines))
			matrix.append({'glyphs': gline, 'info': lineinfo, 'link': link})
			# matrix.append({'glyphs': gline, 'info': lineinfo, 'link': link, 'scale': .5})
	return matrix


def tdDragTableImageFactory( size, **kwargs ):
	width, height = size
	x = 5
	y = 5
	bot = NSImageDrawingTools(size)
	bot.fill(1,1,1,1)
	bot.strokeWidth(1)
	bot.stroke(0,0,0,1)
	width -= 5
	height -= 5
	_w = width / 2
	_h = height / 2
	stepX = (width / 2) / 3
	stepY = (height / 2) / 3
	for i in range(0,3):
		bot.roundedRect(x , y , _w, _h, 2)
		x += stepX
		y += stepY
	image = bot.getImage()
	return image

KernToolDragTableSymbol = "com.typedev.KernToolDragTableSymbol"
merz.SymbolImageVendor.registerImageFactory(KernToolDragTableSymbol, tdDragTableImageFactory)


def tdExceptionImageFactoryOrphan( size, position = (0,0), color=(0, 0, 0, 1), **kwargs ):
	width, height = size
	x, y = position
	bot = NSImageDrawingTools(size)
	s = 1.2
	bot.fill(*color)
	bot.newPath()
	bot.moveTo((x + s * 4, y + s * 8))
	bot.lineTo((x + s * 1, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 0))
	bot.lineTo((x + s * 7, y + s * 5))
	bot.lineTo((x + s * 4, y + s * 5))
	bot.closePath()
	bot.drawPath()
	x = x + 6*s
	bot.newPath()
	bot.moveTo((x + s * 4, y + s * 8))
	bot.lineTo((x + s * 1, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 0))
	bot.lineTo((x + s * 7, y + s * 5))
	bot.lineTo((x + s * 4, y + s * 5))
	bot.closePath()
	bot.drawPath()

	image = bot.getImage()
	return image

KernToolExceptionSymbolOrphan = "com.typedev.KernToolExceptionOrphan"
merz.SymbolImageVendor.registerImageFactory(KernToolExceptionSymbolOrphan, tdExceptionImageFactoryOrphan)

def tdExceptionImageFactoryRightSide( size, position = (0,0), color=(0, 0, 0, 1), **kwargs ):
	width, height = size
	x, y = position
	bot = NSImageDrawingTools(size)
	s = 1.2
	bot.fill(*color)
	bot.newPath()
	bot.moveTo((x + s * 4, y + s * 8))
	bot.lineTo((x + s * 1, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 0))
	bot.lineTo((x + s * 7, y + s * 5))
	bot.lineTo((x + s * 4, y + s * 5))
	bot.closePath()
	bot.drawPath()

	# fill(1, 0, 0, 1)

	bot.stroke(*color)
	bot.strokeWidth(s)
	bot.rect(x + s * 8, y + s * 3.5, 1 * s, 1 * s)
	bot.polygon((x + s * 10, y + s * 6), (x + s * 12, y + s * 4), (x + s * 10, y + s * 2))

	# bot.fill(1, 1, 1, 1)
	# bot.stroke(*color)
	# bot.strokeWidth(s)
	# bot.oval(x + s * 8, y + s * 2, 4 * s, 4 * s)
	image = bot.getImage()
	return image

KernToolExceptionSymbolRightSide = "com.typedev.KernToolExceptionSymbolRightSide"
merz.SymbolImageVendor.registerImageFactory(KernToolExceptionSymbolRightSide, tdExceptionImageFactoryRightSide)

def tdExceptionImageFactoryLeftSide( size, position = (0,0), color=(0, 0, 0, 1), **kwargs ):
	width, height = size
	x, y = position

	bot = NSImageDrawingTools(size)
	s = 1.2
	x = x + 6*s
	bot.fill(*color)
	bot.newPath()
	bot.moveTo((x + s * 4, y + s * 8))
	bot.lineTo((x + s * 1, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 3))
	bot.lineTo((x + s * 4, y + s * 0))
	bot.lineTo((x + s * 7, y + s * 5))
	bot.lineTo((x + s * 4, y + s * 5))
	bot.closePath()
	bot.drawPath()

	# bot.fill(1, 1, 1, 1)
	# bot.stroke(*color)
	# bot.strokeWidth(s)
	# bot.oval(x - s * 4, y + s * 2, 4 * s, 4 * s)

	bot.stroke(*color)
	bot.strokeWidth(s)
	x = x + s*8
	bot.rect(x - s * 9, y + s * 3.5, 1 * s, 1 * s)
	bot.polygon((x - s * 10, y + s * 6), (x - s * 12, y + s * 4), (x - s * 10, y + s * 2))

	image = bot.getImage()
	return image

KernToolExceptionSymbolLeftSide = "com.typedev.KernToolExceptionSymbolLeftSide"
merz.SymbolImageVendor.registerImageFactory(KernToolExceptionSymbolLeftSide, tdExceptionImageFactoryLeftSide)

SELECTION_MODE_GLYPH = 1
SELECTION_MODE_PAIR = 2
SELECTION_MODE_LINE = 3


SHOWTITLES_GLYPH_NAME = 0
SHOWTITLES_GLYPH_WIDTH = 1
SHOWTITLES_GLYPH_INDEX = 100

def pt2Scale(pt):
	if CurrentFont().info.unitsPerEm == 2048:
		return pt / (CurrentFont().info.unitsPerEm / 2)
	if CurrentFont().info.unitsPerEm == 1000:
		return pt / CurrentFont().info.unitsPerEm

def scale2pt(scale):
	if CurrentFont().info.unitsPerEm == 2048:
		scale = scale /2

	return round( CurrentFont().info.unitsPerEm * scale, 1 )

def calculateLineHeight(font):
	if font:
		if font.info.unitsPerEm == 1000:
			return 2000
		if font.info.unitsPerEm == 2048:
			return 3400
	return 2000

LEFT_SYMBOL_MARGIN = chr(int('25C2', 16)) # 25C0
RIGHT_SYMBOL_MARGIN = chr(int('25B8', 16)) # 25B6
TITLE_SYMBOL = '\n' + chr(int('25BC', 16))

# class TDView(vanilla.Group):
# 	def __init__(self, posSize, backgroundColor=None, delegate=None,
# 	             selectionCallback=None,  glyphsLineWillDrawCallback = None,
# 	             fontsHashKernLib = None, showKerning = True):
#
# 		dropSettings = dict(
# 			pasteboardTypes = ["plist"],
# 			# dropCandidateEnteredCallback = self.stringDestViewDropCandidateEnteredCallback,
# 			dropCandidateCallback = self.stringDestViewDropCandidateCallback,
# 			# dropCandidateEndedCallback = self.stringDestViewDropCandidateEndedCallback,
# 			# dropCandidateExitedCallback = self.stringDestViewDropCandidateExitedCallback,
# 			performDropCallback = self.stringDestViewPerformDropCallback
# 		)
#
# 		self.g = TDGlyphsMerzView(posSize,backgroundColor,delegate,selectionCallback,glyphsLineWillDrawCallback,fontsHashKernLib,showKerning)

	# def stringDestViewPerformDropCallback(self, info):
	# 	return True
	#
	# def stringDestViewDropCandidateCallback(self, info):
	# 	print (info)
	#
	# def draggingEntered(self):
	# 	print ('draggingEntered_')

class TDGlyphsMerzView (MerzView):
	# dropSettings = dict(
	# 	pasteboardTypes = ["plist"],
	# 	dropCandidateEnteredCallback = self.stringDestViewDropCandidateEnteredCallback,
	# 	dropCandidateCallback = self.stringDestViewDropCandidateCallback,
	# 	# dropCandidateEndedCallback = self.stringDestViewDropCandidateEndedCallback,
	# 	# dropCandidateExitedCallback = self.stringDestViewDropCandidateExitedCallback,
	# 	performDropCallback = self.stringDestViewPerformDropCallback
	# )
	def __init__(self, posSize, backgroundColor=None, delegate=None,
	             selectionCallback=None,  doubleClickCallback = None,
	             glyphsLineWillDrawCallback = None,
	             fontsHashKernLib = None, showKerning = True):
		super().__init__(posSize)
		view = self.getNSView()
		self._buildView(view, delegate, backgroundColor)

		self.id = getUniqName()
		self.posSize = posSize
		self.merzW = 1000 # start width of container
		self.scaleFactor = pt2Scale(72)#0.096
		self.topGap = 50
		self.bottomGap = 400
		self.lineHeight = 2000 # height of glyphsline
		self.lineGap = 0 # lineGap between of glyphslines
		self.maxGlyphSize = 250
		self.startXpos = 500

		self.displayFontName = 'Menlo'#'.SFNSMono-Medium'  # font drawing margins, titles, kerning etc.
		self.pointSizeMargins = 9 # font size margins (titles +2)
		self.showMargins = False
		self.modeTitles = SHOWTITLES_GLYPH_NAME
		self.showToolbar = False
		self.toolbarImage = None
		self.showMetrics = False
		self.showSkeleton = False
		self.showBlueZones = False
		self.showFamilyZones = False

		self.colorTitles = COLOR_TITLES
		self.colorGlyphs = (0,0,0,0)
		self.colorBackground = COLOR_BACKGROUND

		self.selectionMode = SELECTION_MODE_PAIR
		self.separatePairs = False  # separate pairs mode for groups mix
		self.separatorWidth = 300

		self.checkLanguageCompatibility = True

		self.controlsElements = {}
		self.statuses = {} # {'mode_name': (False/True, Value) } # {'kerning': (True, None), 'linked': (True, None), 'size': (True, 72) }

		self.lightMode = False
		self.showKerning = showKerning # TODO need rename
		if not showKerning:
			self.selectionMode = SELECTION_MODE_GLYPH
		self.fontsHashKernLib = fontsHashKernLib

		self.selectionCallback = selectionCallback # selection
		self.doubleClickCallback = doubleClickCallback
		self.glyphsLineWillDrawCallback = glyphsLineWillDrawCallback # before drawing glyphsline

		self.selectedGlyphs = [] # selected glyphs [glyphsname.uuidXXXXXXX... ]
		self.selectedGlyphsLine = [] # list of glyphs from selected glyphsline layer
		self.ghostGlyphs = []
		self.selectedFont = None # .getParent() for first glyph in selected glyohsline layer
		self.currentPair = None # RAW data from researchPair()
		self.selectedGlyphsLineLayer = None # selected glyphsline layer
		self.selectedGlyphLayer = None # selected glyphbox layer
		self.selectedLink = None # selected uniq link
		self.linkedMode = True
		self.lastSelectedGlyphsLineLayer = None
		self.useRayBeam = False
		self.rayBeamPosition = 300
		self.useRayStems = False
		self.canUseVerticalRayBeam = True
		self.useVerticalRayBeam = False
		self.rayBeamVerticalPosition = None
		# self.animatedRayBeamStart = True

		self.cursorLayers = []

		# indexes
		self.placedGlyphLinesDic = {} # uniq_glyph_name: [glyphsLine, glyphsLine ... ]
		# self.placedGlyphLinesList = [] # all glyphsline layers
		self.linkedGlyphLinesDic = {} # link: [glyphsLine, glyphsLine ... ]
		self.visibleGlyphLinesLayer = [] # list of visible glyphsLines
		self.placedGlyphUniqNames = []

		# scrollbars control
		self.VRscrollheight = 0
		self.VRscrollcursor = 0
		self.VRscrollHit = False
		self.HZscrollHit = False

		self.scrollAnimation = False
		self.scrollPhase = []

		self.addControlElement(name = 'scrollbarVr.base', callback = self.scrollBarVRcallback)
		self.addControlElement(name = 'scrollbarHz.base', callback = self.scrollBarHZcallback)

		self.keyCommander = TDKeyCommander()

		self.keyCommander.registerKeyCommand(KEY_PLUS, callback = self.zoomInCallback)
		self.keyCommander.registerKeyCommand(KEY_MINUS, callback = self.zoomOutCallback)

		self.keyCommander.registerKeyCommand(KEY_B, callback = self.switchRayBeamCallback, callbackValue = None)
		self.keyCommander.registerKeyCommand(KEY_B, alt = True, callback = self.switchRayBeamCallback, callbackValue = 'alt')
		self.keyCommander.registerKeyCommand(KEY_B, cmd = True, callback = self.switchVertRayBeamCallback)

		self.keyCommander.registerKeyCommand(KEY_UP, callback = self.keyUpPressedCallback) # move beam or goto prev line
		self.keyCommander.registerKeyCommand(KEY_DOWN, callback = self.keyDownPressedCallback) # move beam or goto next line
		self.keyCommander.registerKeyCommand(KEY_UP, alt = True, callback = self.moveRayBeamCallback, callbackValue = 1)
		self.keyCommander.registerKeyCommand(KEY_UP, shift = True, callback = self.moveRayBeamCallback, callbackValue = 100)
		self.keyCommander.registerKeyCommand(KEY_DOWN, alt = True, callback = self.moveRayBeamCallback, callbackValue = -1)
		self.keyCommander.registerKeyCommand(KEY_DOWN, shift = True, callback = self.moveRayBeamCallback, callbackValue = -100)

		self.keyCommander.registerKeyCommand(KEY_LEFT, cmd = True, callback = self.moveVertRayBeamCallback, callbackValue = -10)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, cmd = True, callback = self.moveVertRayBeamCallback, callbackValue = 10)
		self.keyCommander.registerKeyCommand(KEY_LEFT, cmd = True, alt = True, callback = self.moveVertRayBeamCallback, callbackValue = -1)
		self.keyCommander.registerKeyCommand(KEY_LEFT, cmd = True, shift = True, callback = self.moveVertRayBeamCallback, callbackValue = -100)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, cmd = True, alt = True, callback = self.moveVertRayBeamCallback, callbackValue = 1)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, cmd = True, shift = True, callback = self.moveVertRayBeamCallback, callbackValue = 100)

		self.keyCommander.registerKeyCommand(KEY_TAB, callback = self.gotoNextSelectionCallback)
		self.keyCommander.registerKeyCommand(KEY_TAB, alt = True, callback = self.gotoPreviousSelectionCallback)



# ==============================================================================================
	def drawBlueZones(self, container, glyph, familyBlues = False, showDimentions = False):
		def pairingzones (t, size=2):
			it = iter(t)
			return zip(*[it] * size)

		font = glyph.font
		width = glyph.width
		fontname = self.displayFontName
		pointsize = self.pointSizeMargins
		color = (0.5,0.5,1,1)
		blues = dict(
			postscriptBlueValues = font.info.postscriptOtherBlues + font.info.postscriptBlueValues,
			postscriptFamilyBlues = font.info.postscriptFamilyOtherBlues + font.info.postscriptFamilyBlues,
		)
		if not familyBlues:
			listblues = list(pairingzones(blues['postscriptBlueValues']))
		else:
			listblues = list(pairingzones(blues['postscriptFamilyBlues']))
			color = (.7,.5,0,1)

		for idx, (y1, y2) in enumerate(listblues):
			rb = container.appendRectangleSublayer(
				name = 'blues.%i' % idx,
				position = (0 + italicShift(font.info.italicAngle, y1), y1 + 600 ),
				size = (width , (y2 - y1) ),
				fillColor = color,
				acceptsHit = False
			)
			if showDimentions:
				shiftx = 0
				container.appendTextLineSublayer(
					name = 'blues.label.%s' % idx,
					font = fontname,
					position = (width + italicShift(font.info.italicAngle, y1 + shiftx) +50 , y2 + 580),
					fillColor = color,
					pointSize = pointsize,
					text = '%i/%i:%i' % (y1, y2, (y2-y1)),
					verticalAlignment = 'top',
					horizontalAlignment = "left"
				)




	def drawMetrics (self, container, glyph = None, font = None, width = 0, showDimentions = False):
		font = glyph.font
		width = glyph.width
		fontname = self.displayFontName
		pointsize = self.pointSizeMargins

		dimensions = dict(
			descender = font.info.descender,
			baseline = 0,
			xHeight = font.info.xHeight,
			caps = font.info.capHeight,
			ascender = font.info.ascender,
		)
		for name, position in dimensions.items():
			rb = container.appendLineSublayer(
				name = 'metrics.%s' % name,
				startPoint = (0 + italicShift(font.info.italicAngle, position), position+600),
				endPoint = (width + italicShift(font.info.italicAngle, position), position+600),
				strokeWidth = 1,
				strokeColor = (.2,.5,.2,1),  # (0,0,0,1),#(.3,.3,.3,.3),
				# strokeDash = (3, 3)
			)
			if showDimentions:
				shiftx = 0
				verticalAlignment = 'top'
				if name == 'ascender':
					verticalAlignment = 'bottom'
					shiftx = 120
				container.appendTextLineSublayer(
					name = 'metrics.label.%s' % name,
					font = fontname,
					position = (-50 + italicShift(font.info.italicAngle, position + shiftx)  , position + 580),
					fillColor = (.2,.5,.2,1),
					pointSize = pointsize,
					text = '%s:%i' % (name[0], position),
					verticalAlignment = verticalAlignment,
					horizontalAlignment = "right"
				)


	def drawRayBeam (self, container, width, position, animate = False):
		# w,h = container.getSize()
		endp = width + 500
		if animate:
			endp = 200
		rb = container.appendLineSublayer(
			name = 'raybeam',
			startPoint = (200, position + 600),
			endPoint = (endp, position + 600),
			strokeWidth = 1,
			strokeColor = COLOR_KERN_VALUE_NEGATIVE,  # (0,0,0,1),#(.3,.3,.3,.3),
			strokeDash = (3, 3)  # hM / clines)
		)
		rb.setStartSymbol(dict(name = "oval", size = (5, 5), fillColor = COLOR_KERN_VALUE_NEGATIVE))
		rb.setEndSymbol(dict(name = "oval", size = (5, 5), fillColor = COLOR_KERN_VALUE_NEGATIVE))
		if animate:
			with rb.propertyGroup(
					duration = .5,
			):
				rb.setEndPoint((width + 200, position + 600))

		fontname = self.displayFontName
		# fontsize = self.pointSizeMargins
		pointsize = self.pointSizeMargins
		container.appendTextLineSublayer(
			name = 'raybeam.left',
			font = fontname,
			position = (200 , position + 600),
			fillColor = COLOR_KERN_VALUE_NEGATIVE,
			pointSize = pointsize,
			text = str(position),
			verticalAlignment = 'bottom',
			horizontalAlignment = "center"
		)

	def drawXRayBeam(self, container, glyph, rayBeamPosition):
		intersection = getIntersectGlyphWithHorizontalBeam(glyph, rayBeamPosition = rayBeamPosition)
		fontname = self.displayFontName
		pointsize = self.pointSizeMargins
		if not intersection: return
		for idx, item in enumerate(intersection):
			x1,x2 = item['points']
			widthstem = item['width']
			container.appendSymbolSublayer(
				name = 'stem.point',
				position = (x1, rayBeamPosition+600),
				imageSettings = dict(
					name = 'oval',
					size = (5, 5),
					fillColor = COLOR_KERN_VALUE_NEGATIVE,
				)
			)
			t = container.appendTextLineSublayer(
				name = 'stem.width',
				font = fontname,
				position = (x1 + ((x2-x1)/2), rayBeamPosition+600),
				fillColor = COLOR_KERN_VALUE_NEGATIVE,
				pointSize = pointsize,
				text = str(widthstem),
				horizontalAlignment = "center"
			)
			if (idx % 2 == 0):
				t.setVerticalAlignment("bottom")
			else:
				t.setVerticalAlignment("top")
				t.setOffset((0,-5)) # correction upper

			container.appendSymbolSublayer(
				name = 'stem.point',
				position = (x2, rayBeamPosition+600),
				imageSettings = dict(
					name = 'oval',
					size = (5, 5),
					fillColor = COLOR_KERN_VALUE_NEGATIVE,
				)
			)

	def drawYRayBeam(self, container, glyph, rayBeamPosition):
		intersection = getIntersectGlyphWithVerticalBeam(glyph, rayBeamPosition = rayBeamPosition)

		if not intersection: return
		fontname = self.displayFontName
		pointsize = self.pointSizeMargins
		xshift = 600
		rb = container.appendLineSublayer(
			name = 'raybeamV',
			startPoint = (rayBeamPosition, -340 + xshift),
			endPoint = (rayBeamPosition, 1200+ xshift),
			strokeWidth = 1,
			strokeColor = COLOR_KERN_VALUE_NEGATIVE,  # (0,0,0,1),#(.3,.3,.3,.3),
			strokeDash = (3, 3)  # hM / clines)
		)
		rb.setStartSymbol(dict(name = "oval", size = (5, 5), fillColor = COLOR_KERN_VALUE_NEGATIVE))
		rb.setEndSymbol(dict(name = "oval", size = (5, 5), fillColor = COLOR_KERN_VALUE_NEGATIVE))

		fontname = self.displayFontName
		pointsize = self.pointSizeMargins
		container.appendTextLineSublayer(
			name = 'raybeamV.left',
			font = fontname,
			position = (rayBeamPosition, -340+ xshift),
			fillColor = COLOR_KERN_VALUE_NEGATIVE,
			pointSize = pointsize,
			text = str(rayBeamPosition),
			verticalAlignment = 'top',
			horizontalAlignment = "center",
			offset = (0,-5)
		)

		for idx, item in enumerate(intersection):
			y1, y2 = item['points']
			height = item['height']
			container.appendSymbolSublayer(
				name = 'stem.point',
				position = (rayBeamPosition, y1+ xshift),
				imageSettings = dict(
					name = 'oval',
					size = (5, 5),
					fillColor = COLOR_KERN_VALUE_NEGATIVE,
				)
			)
			t = container.appendTextLineSublayer(
				name = 'stem.width',
				font = fontname,
				position = (rayBeamPosition, y1 + ((y2-y1) / 2)+ xshift),
				fillColor = COLOR_KERN_VALUE_NEGATIVE,
				pointSize = pointsize,
				text = str(height),
				# horizontalAlignment = "center"
			)
			if (idx % 2 == 0):
				t.setHorizontalAlignment("left")
				t.setOffset((5, 5))
			else:
				t.setHorizontalAlignment("right")
				t.setOffset((-5, 5))
				# t.setOffset((0, -5))  # correction upper

			container.appendSymbolSublayer(
				name = 'stem.point',
				position = (rayBeamPosition, y2+ xshift),
				imageSettings = dict(
					name = 'oval',
					size = (5, 5),
					fillColor = COLOR_KERN_VALUE_NEGATIVE,
				)
			)


	def drawGlyphTitle (self, container, width, displayName = '', color = None, italicAngle=0):
		if not color:
			color = COLOR_TITLES
		# if not displayName:
		# 	displayName = glyph.name
		# width,h = container.getSize()

		container.appendTextBoxSublayer(
			name = 'glyphTitle',
			position = (italicShift(italicAngle, 600), -50),
			size = ( width , self.lineHeight - 50), #glyph.width * self.scaleFactor
			backgroundColor = (0, 0, 0, 0),
			font = self.displayFontName,
			text = displayName + TITLE_SYMBOL,
			pointSize = self.pointSizeMargins, #+ 2,
			fillColor = color,
			horizontalAlignment = 'center',
			visible = self.showMargins,
			padding = (0, 3)
		)

	def drawGlyphMargins (self, container, width, margins = (0,0), italicAngle=0, color = COLOR_TITLES):
		yctrl = 200
		hctrl = 100#0 * self.scaleFactor
		ygap = 500 * self.scaleFactor
		# if self.scaleFactor < 0.051:
		# 	ygap = 70
		color_text = color
		offsetX_text = 10
		fontname = self.displayFontName
		pointsize = self.pointSizeMargins

		leftMargin, rightMargin = margins
		itshift = italicShift(italicAngle, yctrl)

		container.appendTextLineSublayer(
			name = 'margin.left',
			font = fontname,
			position = (-offsetX_text - itshift, yctrl),# - ygap),
			fillColor = color_text,
			pointSize = pointsize,
			text = LEFT_SYMBOL_MARGIN + str(leftMargin),
			horizontalAlignment = "left",
			verticalAlignment = 'bottom',
			offset = (0,-4),
 			visible = self.showMargins,
		)
		container.appendTextLineSublayer(
			name = 'margin.right',
			font = fontname,
			position = ( width + offsetX_text - itshift, yctrl),# - hctrl - ygap), #glyph.width
			fillColor = color_text,
			pointSize = pointsize,
			text = str(rightMargin) + RIGHT_SYMBOL_MARGIN,
			horizontalAlignment = "right",
			verticalAlignment = 'top',
			offset = (0, 4),
			visible = self.showMargins,
		)
		# drawMarginsStrokes = True
		# if drawMarginsStrokes:
		# 	sbleft = container.appendLineSublayer(
		# 		name = 'margin.stroke.left',
		# 		startPoint = (0, 0),
		# 		endPoint = (0, 50),
		# 		strokeWidth = 1,
		# 		strokeColor = COLOR_TITLES,  # (0,0,0,1),#(.3,.3,.3,.3),
		# 		# strokeDash = (1, 3)  # hM / clines)
		# 	)
		# 	sbleft.setStartSymbol(dict(name = "triangle", size = (5, 5), fillColor = COLOR_TITLES))
		#
		# 	sbrigth = container.appendLineSublayer(
		# 		name = 'margin.stroke.right',
		# 		startPoint = (width, 0),
		# 		endPoint = (width, 50),
		# 		strokeWidth = 1,
		# 		strokeColor = COLOR_TITLES,  # (0,0,0,1),#(.3,.3,.3,.3),
		# 		# strokeDash = (1, 3)  # hM / clines)
		# 	)
		# 	sbrigth.setStartSymbol( dict( name="triangle", size=(5, 5), fillColor= COLOR_TITLES ) )
		#
		# 	h, w = container.getSize()
		# 	sblefttop = container.appendLineSublayer(
		# 		name = 'margin.stroke.lefttop',
		# 		startPoint = (0, self.lineHeight-20),
		# 		endPoint = (0, self.lineHeight-70),
		# 		strokeWidth = 1,
		# 		strokeColor = COLOR_TITLES,  # (0,0,0,1),#(.3,.3,.3,.3),
		# 		# strokeDash = (1, 3)  # hM / clines)
		# 	)
		# 	sblefttop.setStartSymbol(dict(name = "triangle", size = (5, 5), fillColor = COLOR_TITLES))
		#
		# 	sbrigthtop = container.appendLineSublayer(
		# 		name = 'margin.stroke.righttop',
		# 		startPoint = (width, self.lineHeight-20),
		# 		endPoint = (width, self.lineHeight-70),
		# 		strokeWidth = 1,
		# 		strokeColor = COLOR_TITLES,  # (0,0,0,1),#(.3,.3,.3,.3),
		# 		# strokeDash = (1, 3)  # hM / clines)
		# 	)
		# 	sbrigthtop.setStartSymbol(dict(name = "triangle", size = (5, 5), fillColor = COLOR_TITLES))

		# uniqname= container.getName().replace('glyphbox.','')
		# if uniqname in self.selected:
		# 	print ('sizemargins', container.getSublayer('margin.left').textLayerSize, container.getSublayer('margin.right').textLayerSize)

	def drawSelectionCursor(self, container, position, color):
		# stroke = 0
		fillColor = color
		# strokeColor = (0,0,0,0)
		if self.lightMode:
			# strokeColor = (.7,.7,.7,1)
			# stroke = 1
			fillColor = (.9,.9,.9,.5)
		cursorlayer = container.appendSymbolSublayer(
			name = 'kernValue.cursor',
			position = position,
			imageSettings = dict(
				name = 'triangle',  # KernToolCursorSymbol,
				size = (8, 15),
				fillColor = fillColor,
				# strokeWidth = stroke,
				# strokeColor = strokeColor,
			)
		)
		cursorlayer.setRotation(90)

		self.cursorLayers.append(cursorlayer)
		if len(self.cursorLayers) > 2:
			self.cursorLayers = self.cursorLayers[1:]


	def animateCursorStart(self):
		d = .1
		for cursorlayer in self.cursorLayers:
			_x, _y = cursorlayer.getPosition()
			with cursorlayer.propertyGroup (
				duration = .3,
				repeatCount = "loop",
				reverse = True,
				delay = d
			):
				cursorlayer.setPosition((_x, _y - 70))
				d += .1


	def drawMarkGlyph(self, container, xpos, color = COLOR_KERN_VALUE_NEGATIVE):
		container.appendSymbolSublayer(
			name = 'mark',
			position = (xpos, 400),
			imageSettings = dict(
				name = 'star',
				size = (10, 10),
				fillColor = color,
				pointCount = 8
			)
		)

	def drawCrossMark(self, container, position, color = COLOR_BLACK):
		cross = container.appendSymbolSublayer(
			name = 'kernValue.cross',
			position = position,
			imageSettings = dict(
				name = "star",
				size = (8, 8),
				fillColor = color,
				pointCount = 4,
				inner = 0.1,
				outer = 2,
				# strokeWidth = stroke,
				# strokeColor = strokeColor,
			)
		)
		cross.setRotation(45)

	def drawSkeleton (self, container, glyph):
		yshift = 600
		opaq = .7
		with container.sublayerGroup():
			for contour in glyph.contours:
				for point in contour.points:
					if point.type == "move":
						container.appendSymbolSublayer(
							position = (point.x, point.y + yshift),
							imageSettings = dict(
								name = "star",
								pointCount = 8,
								size = (5, 5),
								fillColor = (.5, .5, 0, opaq)
							)
						)
					elif point.type == "line":
						container.appendSymbolSublayer(
							position = (point.x, point.y + yshift),
							imageSettings = dict(
								name = "rectangle",
								size = (5, 5),
								fillColor = (0, 0, .5, opaq)
							)
						)
					elif point.type == "curve":
						container.appendSymbolSublayer(
							position = (point.x, point.y + yshift),
							imageSettings = dict(
								name = "oval",
								size = (5, 5),
								fillColor = (0.5, 0, 0, opaq)
							)
						)
					elif point.type == "qcurve":
						container.appendSymbolSublayer(
							position = (point.x, point.y + yshift),
							imageSettings = dict(
								name = "triangle",
								size = (5, 5),
								fillColor = (0, 0.5, 0, opaq)
							)
						)
					# elif point.type == "offcurve":
					# 	container.appendSymbolSublayer(
					# 		position = (point.x, point.y + yshift),
					# 		imageSettings = dict(
					# 			name = "oval",
					# 			size = (5, 5),
					# 			fillColor = (.7,0,.5,opaq),
					# 			# strokeColor = (0, 0, 0, opaq),
					# 			# strokeWidth = 1
					# 		)
					# 	)

	def drawGlyph (self, container, glyph, uniqname=None, position=(0, 0), italicAngle=0,
	               drawMargins = True,
	               color_glyph = (0, 0, 0, 1), color_box = (0, 0, 0, 0), color_titles = COLOR_TITLES,
	               mark = None, scale = 1, showDimentionsMetrics = False, showDimentionsBlues = False):

		def drawGlyphPath(container, glyph, fillColor = (0,0,0,1), strokeColor = None, strokeWidth = 0):
			glyphLayer = container.appendPathSublayer(
				name = 'path.' + glyph.name,
				fillColor = fillColor,
				position = (0, 600),
				strokeColor = strokeColor,
				strokeWidth = strokeWidth,
				# acceptsHit = True,
			)
			glyphPath = _glyph.getRepresentation("merz.CGPath")
			glyphLayer.setPath(glyphPath)


		xpos, ypos = position
		(leftMargin, rightMargin) = getMargins(glyph)
		width = glyph.width

		_glyph = glyph
		# scaling glyphs
		# TODO needs rewrite for new sublayers transformation model
		if scale != 1:
			font = glyph.font
			# font = glyph.getParent()
			_glyph = glyph.copy()
			if glyph.components != None:
				dstGlyphL = RGlyph()
				dstGlyphL.width = glyph.width
				dstPenL = dstGlyphL.getPointPen()
				decomposePenL = DecomposePointPen(font, dstPenL)
				glyph.drawPoints(decomposePenL)
				_glyph = dstGlyphL
				_glyph.name = glyph.name
			_glyph.scale(scale)
			_glyph.width *= scale
			width = _glyph.width
		# =========================
		strokeWidth = 0
		strokeColor = None
		with container.sublayerGroup():
			baselayer = container.appendRectangleSublayer(
				name = 'glyphbox.' + uniqname, #glyph.name,
				position = (xpos, ypos),
				size = (width, self.lineHeight),
				fillColor = color_box,
				acceptsHit = True
			)
			if self.showMetrics and not self.lightMode:
				self.drawMetrics(container = baselayer, glyph = glyph, showDimentions = showDimentionsMetrics)
			if self.showBlueZones and not self.lightMode:
				self.drawBlueZones(container = baselayer, glyph = glyph, showDimentions = showDimentionsBlues)
			if self.showFamilyZones and not self.lightMode:
				self.drawBlueZones(container = baselayer, glyph = glyph, familyBlues = self.showFamilyZones, showDimentions = showDimentionsBlues)


			selcolor = color_titles
			if uniqname in self.selectedGlyphs and self.selectionMode != SELECTION_MODE_LINE:
				selcolor = COLOR_CURSOR
				self.drawSelectionCursor(container = baselayer, position = (width / 2 - 15, 170), color = COLOR_CURSOR)
				if self.showSkeleton:
					color_glyph = None
					strokeWidth = 1
					strokeColor = (0,0,0,1)
					drawGlyphPath(baselayer, glyph, fillColor = color_glyph, strokeColor = strokeColor, strokeWidth = strokeWidth)
					self.drawSkeleton(baselayer,glyph)
				else:
					drawGlyphPath(baselayer, glyph, fillColor = color_glyph, strokeColor = strokeColor, strokeWidth = strokeWidth)
			else:
				drawGlyphPath(baselayer, glyph, fillColor = color_glyph, strokeColor = strokeColor, strokeWidth = strokeWidth)

			if self.lightMode: return
			if drawMargins:
				if self.modeTitles == SHOWTITLES_GLYPH_NAME:
					displayName = glyph.name
					# displayName = str(self.placedGlyphUniqNames.index(uniqname))
				elif self.modeTitles == SHOWTITLES_GLYPH_WIDTH:
					displayName = str(glyph.width)
				# elif self.modeTitles == SHOWTITLES_GLYPH_INDEX:
				# 	displayName = str(self.placedGlyphUniqNames.index(uniqname))
				self.drawGlyphTitle(container = baselayer, width = width,
				                    displayName = displayName, italicAngle = italicAngle, color = selcolor)
			if drawMargins:
				if self.useRayBeam:
					(leftMargin, rightMargin) = getMargins(glyph, useRayBeam = True, rayBeamPosition = self.rayBeamPosition)
					# print (glyph.name, getIntersectGlyphWithBeam(glyph, rayBeamPosition = self.rayBeamPosition))
					if self.useRayStems:
						self.drawXRayBeam(container = baselayer, glyph = glyph, rayBeamPosition = self.rayBeamPosition)
					if self.useVerticalRayBeam:
						if self.rayBeamVerticalPosition == None:
							self.rayBeamVerticalPosition = glyph.width/2
						self.drawYRayBeam(container = baselayer, glyph = glyph, rayBeamPosition = self.rayBeamVerticalPosition)
				self.drawGlyphMargins(container = baselayer, width = width,
				                      margins = (leftMargin, rightMargin), italicAngle = italicAngle, color = color_titles)
			# marklayer = baselayer.getSublayer('mark')
			# if marklayer:
			# 	baselayer.removeSublayer('mark')
			if mark:
				self.drawMarkGlyph(container = baselayer, xpos = width/2 - 15)


	def drawGlyphsLineInfo(self, container, xpos, lineinfo):
		colorLine = COLOR_TITLES  # (.5, .5, .5, 1)
		colorBack = (.1, .1, .1, .1)
		colorBorder = (0, 0, 0, 0)
		stroke = 0
		colorStroke = (0, 0, 0, 0)
		if container == self.selectedGlyphsLineLayer:
			colorLine = (1, 1, 1, 1)  # (1,.6,.2,1)
			colorBack = (.1, .1, .1, .7)
			stroke = 1
			colorStroke = COLOR_TITLES

		container.appendTextLineSublayer(
			name = 'lineinfo',
			font = self.displayFontName,
			position = (xpos + 1000, (self.lineHeight + self.lineGap) - self.lineHeight / 4),  # + 1500
			fillColor = colorLine,
			backgroundColor = colorBack,
			borderColor = colorBorder,
			borderWidth = 1,
			pointSize = 9,
			padding = (5, 5),
			text = lineinfo,
			cornerRadius = 5,
		)
		# container.appendTextBoxSublayer(
		# 	name = 'lineinfo',
		# 	font = self.displayFontName,
		# 	position = (xpos + 1000, ((self.lineHeight+self.lineGap) - self.lineHeight/3)-1000 ), # + 1500
		# 	size = (2500,1000),
		# 	fillColor = colorLine,
		# 	backgroundColor = colorBack,
		# 	borderColor = colorBorder,
		# 	borderWidth = 1,
		# 	pointSize = 9,
		# 	padding = (5,-15),
		# 	text = lineinfo,
		# 	cornerRadius = 5,
		# )
		link = container.getInfoValue('link')
		if self.linkedMode and link == self.selectedLink:
			lm = container.appendSymbolSublayer(
				name = 'marklink',
				position = (xpos + 1000, (self.lineHeight + self.lineGap) - self.lineHeight / 4),
				imageSettings = dict(
					name = 'star',  # KernToolCursorSymbol,
					size = (15, 15),
					fillColor = colorLine,  # (1,.6,.2,1),
					pointCount = 8,
					strokeWidth = stroke,
					strokeColor = COLOR_TITLES
				)
			)

	def moveGlyphs (self, container):
		# just move glyphs when kerning or margins did change (faster render)
		if self.glyphsLineWillDrawCallback:
			self.glyphsLineWillDrawCallback(self, container)
		glyphs = container.getInfoValue('glyphs')
		uniqnames = container.getInfoValue('uniqnames')
		marks = container.getInfoValue('marks')
		# print (marks)
		scale = container.getInfoValue('scale')
		data = container.getInfoValue('data')
		# print('moving')
		# print ([cutUniqName(uniqname) for uniqname in uniqnames])
		# print (data)
		if 'leftmargins' in data:
			leftMargins = data['leftmargins']
		else:
			leftMargins = []

		xpos = self.startXpos
		countpairs = 0

		kernline = container.getSublayer('kernline')
		if kernline:
			kernline.clearSublayers()

		for idx, glyph in enumerate(glyphs):
			glyphbox = container.getSublayer('glyphbox.' + uniqnames[idx])
			if glyphbox:

				marklayer = glyphbox.getSublayer('mark')
				if marklayer:
					glyphbox.removeSublayer('mark')
				if marks and marks[idx]:
					self.drawMarkGlyph(container = glyphbox, xpos = glyph.width / 2 - 15)

				delta = 0
				(lm, rm) = getMargins(glyph)

				if len(leftMargins) == len(glyphs):
					if lm != leftMargins[idx]:
						delta =  lm - leftMargins[idx]
				else:
					print ('index error in leftmargins list')
					print ([cutUniqName(uniqname) for uniqname in uniqnames])
					print (data)

				glyphpath = glyphbox.getSublayer('path.' + glyph.name)
				glyphpath.setPosition((delta,600))

				glyphbox.setPosition((xpos, 0))
				glyphbox.setSize((glyph.width, self.lineHeight))

				# leftsymbol = chr(int('25C0', 16)) + ' '
				# rightsymbol = ' ' + chr(int('25B6', 16))

				if self.useRayBeam:
					(lm, rm) = getMargins(glyph, useRayBeam = True, rayBeamPosition = self.rayBeamPosition)

				l = glyphbox.getSublayer('margin.left')
				if l:
					l.setText(LEFT_SYMBOL_MARGIN+str(lm))
				r = glyphbox.getSublayer('margin.right')
				if r: #TODO need reposition right margins layer
					r.setText(str(rm)+RIGHT_SYMBOL_MARGIN)

				n = glyphbox.getSublayer('glyphTitle')
				if n:
					n.setSize(( glyph.width , self.lineHeight - 50 ))
					if self.modeTitles == SHOWTITLES_GLYPH_WIDTH:
						n.setText(str(glyph.width) + TITLE_SYMBOL)


				if self.selectionMode == SELECTION_MODE_PAIR:
					countpairs += 1
					if self.separatePairs and countpairs == 2:
						countpairs = 0
						xpos += glyph.width*scale + self.separatorWidth
					else:
						kernValue = 0
						if self.showKerning:
							kernValue = self.drawKerningLine(container, kernline, idx, xpos)
						xpos += glyph.width*scale + kernValue
				elif self.selectionMode == SELECTION_MODE_GLYPH:
					kernValue = 0
					if self.showKerning:
						kernValue = self.drawKerningLine(container, kernline, idx, xpos)
					xpos += glyph.width * scale + kernValue

		container.setInfoValue('visible', True)

		w, h = container.getSize()
		if xpos > w:
			container.setSize((xpos + 500, h))
			base = container.getSuperlayer()
			wb, hb = base.getSize()
			if xpos > wb:
				base.setSize((xpos + 500, hb))
		# w, h = container.getSize()
		lineinfo = container.getSublayer('lineinfo') # marklink
		if lineinfo:
			lineinfo.setPosition((xpos + 1000, (self.lineHeight+self.lineGap) - self.lineHeight/4 ))
		marklink = container.getSublayer('marklink')
		if marklink:
			marklink.setPosition((xpos + 1000, (self.lineHeight+self.lineGap) - self.lineHeight/4 ))



	def drawKerningLine(self, container, kernlayer, idxglyph, xpos):
		kernValue = 0
		font = container.getInfoValue('font')
		if not font: return 0
		if font not in self.fontsHashKernLib: return 0
			# print ('ERROR in fontsHashKernLib, font not found')

		hashKernDic = self.fontsHashKernLib[font]
		italicAngle = font.info.italicAngle
		glyphs = container.getInfoValue('glyphs')
		scale = container.getInfoValue('scale')
		glyph = glyphs[idxglyph]
		uniqname = container.getInfoValue('uniqnames')[idxglyph]
		xpos_ = xpos - italicShift(italicAngle, 30) / self.scaleFactor

		if idxglyph + 1 < len(glyphs):
			pair = researchPair(font, hashKernDic, (glyph.name, glyphs[idxglyph + 1].name))
			# for item in pair.items():
			# 	print (item)
			if pair['kernValue'] or pair['kernValue'] ==0:
				kernValue = pair['kernValue'] * scale

				if self.lightMode: return kernValue

				if kernValue > 0:
					colorKern = COLOR_KERN_VALUE_POSITIVE
				else:
					colorKern = COLOR_KERN_VALUE_NEGATIVE
				kernLineWidth = kernValue
				if abs(kernValue) < 60:
					kernLineWidth = 60
				ygap = 800*self.scaleFactor
				# if self.scaleFactor < 0.051:
				# 	ygap = 100
				shifttxt = 0
				# if pair['exception']:


				kernlayer.appendRectangleSublayer(
					name = 'kernValue.rect',
					position = (xpos_ + glyph.width*scale  + kernValue, 100-ygap),
					size = (abs(kernLineWidth), 60),
					fillColor = colorKern,
				)


				if pair['exception']:
					shifttxt = 30
					if pair['L_realName'] != pair['L_nameForKern'] and pair['R_realName'] == pair['R_nameForKern']:
						kernlayer.appendSymbolSublayer(
							name = 'kernValue.exception',
							position = (
							(xpos_ + glyph.width * scale + kernValue + abs(kernLineWidth) / 2 + 10, 60 - ygap)),
							imageSettings = dict(
								name = KernToolExceptionSymbolLeftSide,
								size = (23, 15),
								color = colorKern,
							)
						)

					elif pair['R_realName'] != pair['R_nameForKern'] and pair['L_realName'] == pair['L_nameForKern']:
						kernlayer.appendSymbolSublayer(
							name = 'kernValue.exception',
							position = (
								(xpos_ + glyph.width * scale + kernValue + abs(kernLineWidth) / 2 + 40, 60 - ygap)),
							imageSettings = dict(
								name = KernToolExceptionSymbolRightSide,
								size = (23, 15),
								color = colorKern,
							)
						)
						shifttxt = 50

					else:
						kernlayer.appendSymbolSublayer(
							name = 'kernValue.exception',
							position = (
								(xpos_ + glyph.width*scale  + kernValue + abs(kernLineWidth) / 2 + 10, 60-ygap)),
							imageSettings = dict(
								name = KernToolExceptionSymbolOrphan,
								size = (23, 15),
								color = colorKern,
							)
						)

				if self.checkLanguageCompatibility:
					if not hashKernDic.checkPairLanguageCompatibility( (glyph.name, glyphs[idxglyph + 1].name) ):
						self.drawCrossMark(kernlayer, position = (xpos_ + glyph.width*scale  + kernValue + abs(kernLineWidth) / 2 + 10, ygap - 200))

				kernlayer.appendTextLineSublayer(
					name = 'kernValue.text',
					font = self.displayFontName,
					position = (xpos_ + glyph.width * scale + kernValue + abs(kernLineWidth) + 30 + shifttxt, 100 - ygap),
					fillColor = colorKern,
					pointSize = self.pointSizeMargins,
					text = str(int(round(kernValue / scale, 0)))
				)

		return kernValue


	def drawGlyphsLine (self, container, justmoveglyphs = False):
		visible = container.getInfoValue('visible')
		if justmoveglyphs:
			self.moveGlyphs(container)
			return
		if not visible and not justmoveglyphs:
			if self.glyphsLineWillDrawCallback:
				self.glyphsLineWillDrawCallback(self, container)
			# if self.selectionMode == SELECTION_MODE_LINE:
			# 	print ('selected line', container)
			# 	with container.propertyGroup(duration = .5):
			# 		container.setFillColor((1, 0, 0, 1))

			glyphs = container.getInfoValue('glyphs')
			uniqnames = container.getInfoValue('uniqnames')
			lineinfo = container.getInfoValue('lineinfo')
			marks = container.getInfoValue('marks')
			inverse = container.getInfoValue('inverse')
			scale = container.getInfoValue('scale')
			data = container.getInfoValue('data')

			xpos = self.startXpos
			countpairs = 0

			w, h = container.getSize()
			kernline = container.appendRectangleSublayer(
				name = 'kernline',
				position = (0, 20),
				size = (w, self.lineHeight),
				fillColor = (0, 0, 0, 0),
			)

			if inverse:
				container.setBackgroundColor((0, 0, 0, 1))
				glyphColor = self.colorBackground, #COLOR_BACKGROUND,
				color_titles = COLOR_TITLES_INVERSE #(.5,.6,.65,1)
			else:
				container.setBackgroundColor((0,0,0,0))
				glyphColor = (0, 0, 0, 1)
				color_titles = COLOR_TITLES

			lmargins = []
			for idx, glyph in enumerate(glyphs): # glyphname
				font = glyph.font

				# font = glyph.getParent()
				italicAngle = None
				if font:
					italicAngle = font.info.italicAngle
				mark = None
				if marks:
					try: #TODO sometimes something wrong with indexes
						mark = marks[idx]
					except:
						print ('error in marks indexes ', idx, marks)
				showDimentionsMetrics = False
				showDimentionsBlues = False
				if idx == 0: showDimentionsMetrics = True
				if idx == len(glyphs)-1: showDimentionsBlues = True
				self.drawGlyph(container, glyph, uniqname = uniqnames[idx], position = (xpos, 0),
				               color_glyph = glyphColor, color_titles = color_titles,
				               italicAngle = italicAngle, drawMargins = self.showMargins,
				               mark = mark, scale = scale, showDimentionsMetrics = showDimentionsMetrics, showDimentionsBlues = showDimentionsBlues )
				countpairs +=1
				if self.separatePairs and countpairs == 2:
					countpairs = 0
					xpos += glyph.width*scale + self.separatorWidth
				else:
					kernValue = 0
					if self.showKerning and self.selectionMode != SELECTION_MODE_LINE:
						kernValue = self.drawKerningLine(container, kernline, idx, xpos)
					xpos += glyph.width*scale + kernValue

				(lm,rm) = getMargins(glyph)
				lmargins.append(lm)

			container.setInfoValue('visible', True)
			data['leftmargins'] = lmargins
			container.setInfoValue('data', data )
			# recalculate base layers
			if xpos > w:
				fix = 500
				if lineinfo:
					fix = 2500
				container.setSize((xpos + fix, h))
				kernline.setSize(((xpos + fix,  self.lineHeight)))

				base = container.getSuperlayer()
				wb, hb = base.getSize()
				if xpos > wb:
					base.setSize((xpos + fix, hb))

			if lineinfo:
				self.drawGlyphsLineInfo(container, xpos, lineinfo)
			if self.useRayBeam:
				self.drawRayBeam(container, width = xpos, position = self.rayBeamPosition )



	def placeGlyphsLine(self, container, font, glyphs, position=(0, 0),
	                    lineinfo = None, link = None, marks = None, scale = 1, inverse = False, data = None):
		with container.sublayerGroup():
			baselayer = container.appendBaseSublayer(
				name = 'glyphsline',
				position = position,
				size = (self.merzW , self.lineHeight),
				# fillColor = COLOR_BACKGROUND#(0, 0, 0, 1),
				backgroundColor = (0,0,0,0), #COLOR_BACKGROUND, #
				acceptsHit = False

			)
			uniqnames = []
			for glyph in glyphs:
				uniqname = '%s.%s' % (glyph.name, getUniqName())
				uniqnames.append(uniqname)
				self.placedGlyphLinesDic[uniqname] = baselayer
				self.placedGlyphUniqNames.append(uniqname)

			baselayer.setInfoValue('glyphs', glyphs)
			baselayer.setInfoValue('uniqnames', uniqnames )
			baselayer.setInfoValue('font', font)
			baselayer.setInfoValue('visible', False)
			baselayer.setInfoValue('lineinfo', lineinfo)
			baselayer.setInfoValue('link', link)
			baselayer.setInfoValue('marks', marks)
			baselayer.setInfoValue('inverse', inverse)
			baselayer.setInfoValue('scale', scale)
			baselayer.setInfoValue('data', data)
		return baselayer


	def drawScrollBars(self):
		self.drawHorizontalScrollBar()
		self.drawVerticalScrollBar()


	def drawToolbar(self):
		# print ('calling toolbar')
		if self.showToolbar and self.toolbarImage:
			# print('drawig toolbar', self.toolbarImage)
			container = self.getMerzContainer()
			tb = container.getSublayer('toolbar')
			xpos = 20
			ypos = 20
			if tb:
				# print('moving toolbar')
				tb.setPosition((xpos, ypos))
				tb.setImage(self.toolbarImage)
			else:
				# print('drawig toolbar', self.toolbarImage)
				imageLayer = container.appendImageSublayer(
					name = 'toolbar',
					position = (xpos, ypos),
					size = (700, 55),
					backgroundColor = (0, 0, 0, 0),
					# alignment = "left"
				)
				imageLayer.setImage(self.toolbarImage)
		else:
			container = self.getMerzContainer()
			tb = container.getSublayer('toolbar')
			if tb:
				# print('moving toolbar')
				container.removeSublayer('toolbar')


	def drawStatuses(self):
		#TODO instead of deleting and redrawing, you need to think about changing the status text and repositioning.
		# maybe one text layer is needed to display formatted status text
		container = self.getMerzContainer()
		hM = self.height()
		wM = self.width()
		xpos = wM / self.scaleFactor - 17 / self.scaleFactor
		ypos = 35 / self.scaleFactor
		# print ('draw status')
		for mode, (status, value) in self.statuses.items():
			layer = container.getSublayer('status.'+mode)
			# layerremoved = True
			if not value:
				value = ''
			if layer:# and not status:
				# print ('removing status')
				container.removeSublayer(layer)
				# layerremoved = True
			# elif layer and status:
				# print ('setting text to status')
				# layer.setText('[' +mode+value+ ']')
				# layerremoved = False
			if status: # and layerremoved:
				l = container.appendTextLineSublayer(
					name = 'status.'+mode,
					font = self.displayFontName,
					position = (xpos ,  ypos), # + 1500
					# size = (100,100),
					fillColor = COLOR_TITLES, #(.2,.2,0,1),
					# backgroundColor = (1,1,1,.5),
					# borderColor = colorBorder,
					# borderWidth = 1,
					pointSize = 12,
					# padding = (5,0),
					horizontalAlignment = 'right',
					# verticalAlignment = 'bottom',
					text = '[' +mode+value+ ']',
					cornerRadius = 5, )
				ypos += 18/self.scaleFactor
				# print('noscale',mode, l.getSize())
				l.addScaleTransformation(self.scaleFactor)
				# print ('scale',mode, l.getSize())

			# self.statuses[mode] = l

	def setStatus(self, name, status=False, value=None):
		self.statuses[name] = (status, value)


	def clearGlyphsLine(self, container):
		visible = container.getInfoValue('visible')
		if visible:
			container.clearSublayers()
			container.setInfoValue('visible', False)


	def drawGlyphsMatrix(self, refresh = False, layer = None, justmoveglyphs = False):
		# print ('draw matrix', self.id)
		container = self.getMerzContainer()
		self.drawToolbar()
		self.drawScrollBars()
		self.drawStatuses()

		if layer and refresh:
			if not justmoveglyphs:
				self.clearGlyphsLine(layer)
				self.drawGlyphsLine(layer)
			else:
				self.drawGlyphsLine(layer, justmoveglyphs = True)
			return

		w, h = container.getSize()
		tolerance = -100

		# draw the glyphsline only if it is visible within the window
		hits = container.findSublayersIntersectedByRect((0-w, tolerance , w*2, h - tolerance), onlyLayers = ['glyphsline'])
		self.visibleGlyphLinesLayer = []
		for layer in hits:
			if refresh and not justmoveglyphs:
				self.clearGlyphsLine(layer)
			self.drawGlyphsLine(layer, justmoveglyphs = justmoveglyphs)
			self.visibleGlyphLinesLayer.append(layer)

		# clear bottom layers
		hits = container.findSublayersIntersectedByRect((0, -1000, w, 800))
		for layer in hits:
			self.clearGlyphsLine(layer)

		# clear top layers
		hits = container.findSublayersIntersectedByRect((0, h + 200, w, 800))
		for layer in hits:
			self.clearGlyphsLine(layer)
		#
		# x = container.getSublayer('XXX')
		# if x:
		# 	container.removeSublayer(x)
		# container.appendBaseSublayer(
		# 	name = 'XXX',
		# 	size = (500 / self.scaleFactor, 200 / self.scaleFactor),  # self.merzW
		# 	backgroundColor = (1, 0, 0, .3),  # self.colorBackground,
		# 	# COLOR_BACKGROUND,COLOR_BACKGROUND,#(.75, .73, .7, 1),#(1, 1, 1, 1),
		# 	position = (100, 100)
		# )


	def setScaleGlyphsMatrix (self, scale):
		container = self.getMerzContainer()
		self.scaleFactor = scale
		if scale < 0.03:
			self.scaleFactor = 0.03
		if scale > self.maxGlyphSize/1000:
			self.scaleFactor = self.maxGlyphSize/1000

		# container.setSublayerScale(self.scaleFactor) #addSublayerScaleTransformation
		self.setStatus('size:', True, str(scale2pt(self.scaleFactor))+'pt')
		baselayer = container.getSublayer('base')
		# baselayer.addScaleTransformation(self.scaleFactor)

		for layer in container.getSublayers():
			if layer.getName() and layer.getName() == 'toolbar': pass
				# print ('skip toolbar')
			else:
				layer.addScaleTransformation(self.scaleFactor)

		# if self.showMargins:
		# 	if self.scaleFactor < 0.1:
		# 		self.pointSizeMargins = 6
		# 	elif self.scaleFactor > 0.1:
		# 		self.pointSizeMargins = 9
		#
		# 	for glyphslinelayer in baselayer.getSublayers():
		# 		for glyphlayer in glyphslinelayer.getSublayers():
		# 			l = glyphlayer.getSublayer('margin.left')
		# 			if l:
		# 				l.setPointSize(self.pointSizeMargins)
		# 			r = glyphlayer.getSublayer('margin.right')
		# 			if r:
		# 				r.setPointSize(self.pointSizeMargins)
		# 			n = glyphlayer.getSublayer('glyphTitle')
		# 			if n:
		# 				n.setPointSize(self.pointSizeMargins + 2)


	def selectGlyphLayer (self, layer, selectionMode=SELECTION_MODE_GLYPH):
		glyphname = getGlyphName_fromBoxLayer(layer)
		# print (glyphname, layer)
		if glyphname and layer and glyphname in self.placedGlyphLinesDic:
			self.selectedGlyphsLineLayer = self.placedGlyphLinesDic[glyphname] #layer.getSuperlayer()
			self.selectedFont = self.selectedGlyphsLineLayer.getInfoValue('font')
			glyphs = getGlyphsNames_fromGlyphsLineLayer(self.selectedGlyphsLineLayer)
			self.selectedGlyphsLine = glyphs
			if selectionMode == SELECTION_MODE_PAIR:
				if glyphs and glyphs[0] == glyphname and len(glyphs) > 1:
					self.selectedGlyphs.append(glyphs[0])
					self.selectedGlyphs.append(glyphs[1])
				elif glyphs and len(glyphs) > 1:
					# for idx, gname in enumerate(glyphs):
					# 	if gname == glyphname:
					idx = glyphs.index(glyphname)
					if self.separatePairs and (idx % 2 == 0) and idx+1 < len(glyphs):
						self.selectedGlyphs.append(glyphs[idx])
						self.selectedGlyphs.append(glyphs[idx + 1])
					else:
						self.selectedGlyphs.append(glyphs[idx - 1])
						self.selectedGlyphs.append(glyphs[idx])

			elif selectionMode == SELECTION_MODE_GLYPH:
				self.selectedGlyphs.append(glyphname)
			elif selectionMode == SELECTION_MODE_LINE:
				#TODO something wrong
				self.selectedGlyphs = glyphs
				# self.selectedGlyphs.append(glyphname)

			link = self.selectedGlyphsLineLayer.getInfoValue('link')
			if self.linkedMode and link != self.selectedLink:
				self.selectedLink = link
				self.drawGlyphsMatrix(refresh = True)
			else:
				self.selectedLink = link
				self.drawGlyphsMatrix(refresh = True, layer = self.lastSelectedGlyphsLineLayer)
				self.drawGlyphsMatrix(refresh = True, layer = self.selectedGlyphsLineLayer)

			self.lastSelectedGlyphsLineLayer = self.selectedGlyphsLineLayer

			if self.visibleGlyphLinesLayer:
				if self.selectedGlyphsLineLayer == self.visibleGlyphLinesLayer[0]:
					self.scrollMoving((0,+self.lineHeight),scaleScroll = 1, animate = True)
				elif self.selectedGlyphsLineLayer == self.visibleGlyphLinesLayer[-2]:
					self.scrollMoving((0,-self.lineHeight),scaleScroll = 1, animate = True)

			if self.selectionCallback:
				self.selectionCallback(self)

	def selectGlyphsLayerByIndexInLine(self, glyphsLineLayer, index = 0, selectionMode = SELECTION_MODE_GLYPH):
		# idx = 0
		# for boxlayer in glyphsLineLayer.getSublayers():
		# 	glyphname = getGlyphName_fromBoxLayer(boxlayer)
		# 	if glyphname:
		# 		if idx == index:
		# 			self.selectedGlyphs = []
		# 			self.selectGlyphLayer(boxlayer, selectionMode = selectionMode)
		# 			return
		# 		idx +=1
		glyphs = getGlyphsNames_fromGlyphsLineLayer(glyphsLineLayer)
		if index <= len(glyphs)-1:
			boxlayer = glyphsLineLayer.getSublayer('glyphbox.%s' % glyphs[index])
			self.selectedGlyphs = []
			self.selectGlyphLayer(boxlayer, selectionMode = selectionMode)
		else:
			print ('ERROR: wrong selection index', index, glyphs)

	def selectGlyphsLayerByUniqGlyphName(self, uniqGlyphname, selectionMode = SELECTION_MODE_GLYPH):
		if uniqGlyphname in self.placedGlyphLinesDic:
			glyphsLinelayer = self.placedGlyphLinesDic[uniqGlyphname]
			self.selectedGlyphs = []
			self.selectGlyphLayer(glyphsLinelayer.getSublayer('glyphbox.%s' % uniqGlyphname), selectionMode = selectionMode)


	def modifyGlyphsLine (self, glyphsLineLayer, glyphs=None, marks = None):
		# baselayer = glyphsLineLayer  # .getSuperlayer()
		uniqnames = glyphsLineLayer.getInfoValue('uniqnames')
		# if not data:
		idx_1_Glyph = 0
		data = glyphsLineLayer.getInfoValue('data')
		if uniqnames and uniqnames[0] in self.placedGlyphUniqNames:
			idx_1_Glyph = self.placedGlyphUniqNames.index(uniqnames[0])
		# else:
		# 	print ('ERROR cant find first index', uniqnames)

		for uniqname in uniqnames:
			if uniqname in self.placedGlyphLinesDic:
				self.placedGlyphLinesDic.pop(uniqname)
			# else:
			# 	print ('ERROR - no glyphsline for', uniqname)
			if uniqname in self.placedGlyphUniqNames:
				self.placedGlyphUniqNames.remove(uniqname)
			# else:
			# 	print('ERROR - no Index for', uniqname)

		uniqnames = []
		lmargins = []
		for idx, glyph in enumerate(glyphs):
			uniqname = '%s.%s' % (glyph.name, getUniqName())
			uniqnames.append(uniqname)
			self.placedGlyphLinesDic[uniqname] = glyphsLineLayer

			(lm, rm) = getMargins(glyph)
			lmargins.append(lm)
			self.placedGlyphUniqNames.insert(idx_1_Glyph+idx, uniqname)

		glyphsLineLayer.setInfoValue('glyphs', glyphs)
		glyphsLineLayer.setInfoValue('uniqnames', uniqnames)
		glyphsLineLayer.setInfoValue('marks', marks)
		# baselayer.setInfoValue('data', data)
		data['leftmargins'] = lmargins
		glyphsLineLayer.setInfoValue('data', data)
		# print (data)
		self.drawGlyphsMatrix(refresh = True, layer = glyphsLineLayer)


	def setGlyphNamesListToCurrentLine(self, glyphsNamesList):
		# link = self.selectedGlyphsLineLayer.getInfoValue('link')
		if self.linkedMode:
			if not self.selectedGlyphsLineLayer: return
			link = self.selectedGlyphsLineLayer.getInfoValue('link')
			for linkedlayer in self.linkedGlyphLinesDic[link]:
				font = linkedlayer.getInfoValue('font')
				glyphs = []
				for gn in glyphsNamesList:
					if gn in font:
						glyphs.append(font[gn])
				self.modifyGlyphsLine(linkedlayer, glyphs = glyphs)
		else:
			if not self.selectedGlyphsLineLayer: return
			font = self.selectedGlyphsLineLayer.getInfoValue('font')
			glyphs = []
			for gn in glyphsNamesList:
				if gn in font:
					glyphs.append(font[gn])
			self.modifyGlyphsLine(self.selectedGlyphsLineLayer, glyphs = glyphs)


	def setTextToCurrentLine (self, text, font = None):
		# if self.selectedFont:
		# if not font and not self.selectedFont:
		# 	font = CurrentFont()
		# elif not font and self.selectedFont:
		# 	font = self.selectedFont
		glyphsNamesList = tdGlyphparser.translateText(font = CurrentFont(), text = text)
		self.setGlyphNamesListToCurrentLine(glyphsNamesList)
		return glyphsNamesList

	def getGlyphsMatrixState(self):
		container = self.getMerzContainer()
		baselayer = container.getSublayer('base')
		matrix = []
		position = (0,0)
		if baselayer:
			position = baselayer.getPosition()
			for layer in baselayer.getSublayers():
				if layer.getName() and 'glyphsline' in layer.getName():
					# layer.getInfoValue('glyphs', glyphs)
					names = layer.getInfoValue('uniqnames')
					# font = layer.getInfoValue('font')
					# visible = layer.getInfoValue('visible')
					# lineinfo = layer.getInfoValue('lineinfo')
					# link = layer.getInfoValue('link')
					# marks = layer.getInfoValue('marks')
					inverse = layer.getInfoValue('inverse')
					scale = layer.getInfoValue('scale')
					data = layer.getInfoValue('data')

					matrix.append(getGlyphsNames_fromGlyphsLineLayer(layer))
		return (position, matrix)


	def gotoNextSelectionCallback(self, sender, value):
		if self.selectedGlyphs:
			idxSelected = self.placedGlyphUniqNames.index(self.selectedGlyphs[0])
			if idxSelected +1 > len(self.placedGlyphUniqNames)-1:return
			if self.selectionMode == SELECTION_MODE_PAIR:
				if idxSelected + 2 > len(self.placedGlyphUniqNames)-1:
					i = self.placedGlyphUniqNames[ idxSelected + 1]
				else:
					i = self.placedGlyphUniqNames[ idxSelected + 2]
			else:
				i = self.placedGlyphUniqNames[ idxSelected + 1]
			self.selectGlyphsLayerByUniqGlyphName(i,selectionMode = self.selectionMode)

	def gotoPreviousSelectionCallback(self, sender, value):
		if self.selectedGlyphs:
			idxSelected = self.placedGlyphUniqNames.index(self.selectedGlyphs[0])
			if idxSelected == 0: return
			if self.selectionMode == SELECTION_MODE_PAIR:
				i = self.placedGlyphUniqNames[ idxSelected ]
				firstGlyph = self.selectedGlyphsLine[0]
				if i == firstGlyph: #getGlyphName_fromBoxLayer(self.placedGlyphLinesDic[self.selectedGlyphs[0]].getSublayers()[1]):
					i = self.placedGlyphUniqNames[idxSelected-1]
				if self.separatePairs:
					i = self.placedGlyphUniqNames[idxSelected - 2]
			else:
				i = self.placedGlyphUniqNames[ idxSelected - 1 ]
			self.selectGlyphsLayerByUniqGlyphName(i,selectionMode = self.selectionMode)


	def stepToLine(self, step):
		if self.visibleGlyphLinesLayer and self.selectedGlyphsLineLayer and self.selectedGlyphs:
			idxLine = self.visibleGlyphLinesLayer.index(self.selectedGlyphsLineLayer)
			if idxLine == 0 and step < 0:return
			glyphs = getGlyphsNames_fromGlyphsLineLayer(self.selectedGlyphsLineLayer)
			if not self.selectedGlyphs[0] in glyphs: return
			idxSelected = glyphs.index(self.selectedGlyphs[0])
			if idxLine not in range(0, len(self.visibleGlyphLinesLayer)-1) and step>=1: return
			next_glyphsline = getGlyphsNames_fromGlyphsLineLayer(self.visibleGlyphLinesLayer[idxLine + step])
			if idxSelected >= len(next_glyphsline)-1:
				idxSelected = -1
			next_selectedglyph = next_glyphsline[idxSelected]
			if self.selectionMode == SELECTION_MODE_PAIR:
				# print('idxSelected', idxSelected)
				next_selectedglyph = next_glyphsline[idxSelected + 1]
			self.selectGlyphsLayerByUniqGlyphName(next_selectedglyph, selectionMode = self.selectionMode)


	def gotoNextLine(self):
		self.stepToLine(+1)

	def gotoPreviousLine(self):
		self.stepToLine(-1)


	def insertGlyphsLine(self):
		#TODO the indexes are destroyed, it is necessary to rewrite
		if not self.selectedGlyphsLineLayer: return
		container = self.getMerzContainer()
		doc = container.getSublayer('base')
		if self.linkedMode:
			link = self.selectedGlyphsLineLayer.getInfoValue('link')
			for linkedlayer in self.linkedGlyphLinesDic[link]:
				print('linked pos', linkedlayer.getPosition())

		else:
			pos = self.selectedGlyphsLineLayer.getPosition()
			font = self.selectedGlyphsLineLayer.getInfoValue('font')
			glyphs = self.selectedGlyphsLineLayer.getInfoValue('glyphs')
			link = self.selectedGlyphsLineLayer.getInfoValue('link')
			data = self.selectedGlyphsLineLayer.getInfoValue('data')
			info = self.selectedGlyphsLineLayer.getInfoValue('lineinfo')
			marks = self.selectedGlyphsLineLayer.getInfoValue('marks')
			x, y = pos
			for idx, layer in enumerate(doc.getSublayers()):
				_pos = layer.getPosition()
				_x, _y = _pos
				if _y > y:
					layer.setPosition((_x, _y + self.lineHeight))
					# self.placedGlyphLinesList.append(layer)
				if _y == y:
					layer.setPosition((_x, _y + self.lineHeight))
					glyphslinelayer = self.placeGlyphsLine(doc, font, glyphs, position = (_x, _y),
					                                       link = link, data = data, lineinfo = info, marks = marks)
					glyphslinelayer.setInfoValue('visible', False)
					# if link not in self.linkedGlyphLinesDic:
					# 	self.linkedGlyphLinesDic[link] = []

					if link:
					# self.linkedGlyphLinesDic[link] = []
						self.linkedGlyphLinesDic[link].append(glyphslinelayer)

					self.selectedGlyphsLineLayer = glyphslinelayer  # self.placedGlyphLinesList[0]
					self.selectedFont = self.selectedGlyphsLineLayer.getInfoValue('font')
					self.selectedGlyphsLine = getGlyphsNames_fromGlyphsLineLayer(self.selectedGlyphsLineLayer)

					(w,h) = doc.getSize()
					h += self.lineHeight
					doc.setSize((w,h))
					self.refreshView()
					return
				# if _y < y:
				# 	self.placedGlyphLinesList.append(layer)


	def startDrawGlyphsMatrix(self, glyphslines, animatedStart = False):
		# print (self, len(self.placedGlyphLinesDic), len(self.placedGlyphLinesList))
		container = self.getMerzContainer()
		container.clearSublayers()
		self.lineHeight = calculateLineHeight(CurrentFont())
		xpos = 0
		heightMatrix = len(glyphslines) * (self.lineHeight + self.lineGap) + self.bottomGap
		hM = self.height()
		ypos = heightMatrix - self.topGap

		base = container.appendBaseSublayer(
			name = 'base',
			size = (self.merzW, heightMatrix ),  # self.merzW
			backgroundColor = self.colorBackground, #COLOR_BACKGROUND,COLOR_BACKGROUND,#(.75, .73, .7, 1),#(1, 1, 1, 1),
			position = (0, 0)
		)

		self.placedGlyphLinesDic = {} # uniq_glyph_name: [glyphsLine, glyphsLine ... ]
		# self.placedGlyphLinesList = [] # all glyphsline layers
		self.linkedGlyphLinesDic = {} # link: [glyphsLine, glyphsLine ... ]
		self.visibleGlyphLinesLayer = [] # list of visible glyphsLines
		self.placedGlyphUniqNames = []

		for idx, glyphsline in enumerate(glyphslines):
			glyphs = glyphsline['glyphs']

			font = None
			info = None
			link = getUniqName()
			marks = None
			scale = 1
			inverse = False
			data = {}

			if 'info' in glyphsline:
				info = glyphsline['info']
			if 'link' in glyphsline and glyphsline['link']:
				link = glyphsline['link']
			if 'marks' in glyphsline and glyphsline['marks']:
				marks = glyphsline['marks']
			if 'scale' in glyphsline and glyphsline['scale']:
				scale = glyphsline['scale']
			if 'inverse' in glyphsline:
				inverse = glyphsline['inverse']
			if 'data' in glyphsline and glyphsline['data']:
				data = glyphsline['data']
			if glyphs and glyphs[0].font:
			# if glyphs and glyphs[0].getParent():
				font = glyphs[0].font

			ypos -= self.lineHeight
			glyphslinelayer = self.placeGlyphsLine(base, font, #hashKernDic,
			                                 glyphs = glyphs, position = (xpos, ypos),
			                                 lineinfo = info, link = link, marks = marks,
			                                    scale = scale, inverse = inverse,
			                                       data = data
			                                 )
			if link not in self.linkedGlyphLinesDic:
				self.linkedGlyphLinesDic[link] = []
			self.linkedGlyphLinesDic[link].append(glyphslinelayer)
			# self.placedGlyphLinesList.append(glyphslinelayer)
			ypos -= self.lineGap

		self.setScaleGlyphsMatrix(self.scaleFactor)

		w, h = container.getSize()
		base.setPosition((0, - heightMatrix))
		hits = container.findSublayersIntersectedByRect((0, -h, w, h), onlyLayers = ['glyphsline'])
		for layer in hits:
			self.drawGlyphsLine(layer)
			self.visibleGlyphLinesLayer.append(layer)

		duration = 0
		if animatedStart:
			duration = .7
		with base.propertyGroup(duration = duration):
			base.setPosition((0, hM / self.scaleFactor - heightMatrix))

		self.drawScrollBars()
		self.drawStatuses()
		self.drawToolbar()

		if self.placedGlyphLinesDic:
			# self.selectGlyphsLayerByIndex(self.placedGlyphLinesList[0],selectionMode = self.selectionMode)
			self.selectedGlyphsLineLayer = base.getSublayers()[0]#self.placedGlyphLinesList[0]
			self.selectedFont = self.selectedGlyphsLineLayer.getInfoValue('font')
			self.selectedGlyphsLine = getGlyphsNames_fromGlyphsLineLayer(self.selectedGlyphsLineLayer)


			# for layer in base.getSublayers():
			# 	print (layer)

	def addControlElement(self, name, callback = None):
		self.controlsElements[name] = callback

	def switchMargins (self, showMargins=False):
		self.showMargins = showMargins
		# self.setStatus('margins', showMargins)
		if not self.showMargins:
			self.useRayBeam = False
			self.setStatus('show:beam', self.useRayBeam)

		self.drawGlyphsMatrix( refresh = True)

	def switchMetrics (self, showMetrics = False):
		self.showMetrics = showMetrics
		self.drawGlyphsMatrix(refresh = True)

	def switchBluesZones (self, showBluesZones = False):
		self.showFamilyZones = False
		self.showBlueZones = showBluesZones
		self.drawGlyphsMatrix(refresh = True)
	def switchFamilyZones (self, showFamilyZones = False):
		self.showBlueZones = False
		self.showFamilyZones = showFamilyZones
		self.drawGlyphsMatrix(refresh = True)

	def switchSkeletonMode (self, showSkeleton = False):
		self.showSkeleton = showSkeleton
		self.drawGlyphsMatrix(refresh = True)

	def switchGlyphsInfoMode(self, glyphsInfo = SHOWTITLES_GLYPH_NAME):
		self.modeTitles = glyphsInfo
		self.drawGlyphsMatrix(refresh = True)

	def switchLightMode(self, lightMode = False):
		self.lightMode = lightMode
		self.drawGlyphsMatrix( refresh = True)

	def switchToolbar(self, enable = False, imagePath = None):
		self.showToolbar = enable
		self.toolbarImage = imagePath
		# if enable:
		self.drawGlyphsMatrix(refresh = True)

	def switchLinkedMode(self, linked=False):
		if len(self.fontsHashKernLib) > 1:
			self.linkedMode = linked
			self.setStatus('linked', linked)
			self.drawGlyphsMatrix(refresh = True)
		else:
			self.linkedMode = False
			self.setStatus('linked', False)
			self.drawGlyphsMatrix(refresh = True)

	def switchRayBeam(self, useRayBeam = False):
		if self.showMargins: # and self.selectionMode == SELECTION_MODE_GLYPH:
			self.useRayBeam = useRayBeam
			self.setStatus('show:beam', self.useRayBeam)
			self.drawGlyphsMatrix(refresh = True)

	def switchVerticalRayBeam(self, useRayBeam = False):
		if self.showMargins and self.useRayBeam and self.canUseVerticalRayBeam: # and self.selectionMode == SELECTION_MODE_GLYPH:
			self.setStatus('show:v-beam', useRayBeam)
			self.drawGlyphsMatrix(refresh = True)


	def moveRayBeam(self, moveto = 0):
		if self.useRayBeam and self.rayBeamPosition >= -500 - moveto and self.rayBeamPosition <= 1200 - moveto:
			self.rayBeamPosition += moveto
			self.drawGlyphsMatrix(refresh = True)

	def moveVerticalRayBeam(self, moveto = 0):
		if self.useVerticalRayBeam:# and self.rayBeamVerticalPosition >= -200 - moveto and self.rayBeamVerticalPosition <= 1200 - moveto:
			self.rayBeamVerticalPosition += moveto
			self.drawGlyphsMatrix(refresh = True)

	def setBackgroundColor(self, color):
		# COLOR_BACKGROUND = color
		self.colorBackground = color
		container = self.getMerzContainer()
		container.setBackgroundColor(color)

		base = container.getSublayer('base')
		if base:
			base.setBackgroundColor(color)
		self.drawGlyphsMatrix(refresh = True)


	def refreshView(self, onlyLayer = None, justmoveglyphs = False):
		if onlyLayer:
			self.drawGlyphsMatrix(refresh = True, layer = onlyLayer,  justmoveglyphs = justmoveglyphs)
		else:
			self.drawGlyphsMatrix(refresh = True, justmoveglyphs = justmoveglyphs)

	def getCurrentFont(self, fromLayer = None):
		if not fromLayer:
			return self.selectedGlyphsLineLayer.getInfoValue('font')
		return fromLayer.getInfoValue('font')

	def zoomInCallback(self, sender, value):
		scale = scale2pt( self.scaleFactor )
		self.scaleFactor = pt2Scale( round((round((scale + 6) / 6.0) * 6.0), 1))
		self.setScaleGlyphsMatrix(self.scaleFactor)
		self.drawGlyphsMatrix(refresh = True)

	def zoomOutCallback(self, sender, value):
		scale = scale2pt(self.scaleFactor)
		self.scaleFactor = pt2Scale( round((round((scale - 6) / 6.0) * 6.0), 1))
		self.setScaleGlyphsMatrix(self.scaleFactor)
		self.drawGlyphsMatrix(refresh = True)

	# SCROLLBARS STUFF ==============================================
	def drawHorizontalScrollBar(self):
		# TODO instead of removing layers, think about reposition
		container = self.getMerzContainer()
		sbb = container.getSublayer('scrollbarHz.base')
		if sbb:
			container.removeSublayer(sbb)

		hM = self.height()
		wM = self.width()

		controlwidth = 7

		doc = container.getSublayer('base')
		if not doc: return
		bw , bh = doc.getSize()
		bx , by = doc.getPosition()

		if (bw)*self.scaleFactor < wM: return

		sbcolor = (0, 0, 0, 1)
		pcolor = (0,0,0,1)

		baseY = 10

		startX = 20  / self.scaleFactor
		startY = baseY / self.scaleFactor
		endX = ( wM - 20 ) / self.scaleFactor
		endY = baseY / self.scaleFactor

		base = container.appendBaseSublayer(
			name = 'scrollbarHz.base',
			position = (startX , startY - baseY/self.scaleFactor),
			size = ((wM - 40)/self.scaleFactor, (20/self.scaleFactor) ),
			# fillColor = (0, 0, 0, 0),
			backgroundColor = (0, 0, 0, 0),#(.5,0,0,.3),
			# fillColor = (1,.1,.1,.3),
			acceptsHit = True
		)
		wS, hS = base.getSize()
		sb = base.appendLineSublayer(
			name = 'scrollbarHz.line',
			startPoint = (0, startY),
			endPoint = (wS, endY),
			strokeWidth = 1,
			strokeColor = COLOR_TITLES, #(0,0,0,1),#(.3,.3,.3,.3),
			strokeDash = (1, 3) #hM / clines)
		)
		sb.setStartSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= COLOR_TITLES  ) )
		sb.setEndSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= COLOR_TITLES ) )

		wS, hS = sb.getSize()

		p = (bw + 60/self.scaleFactor)  / wS
		cursorWidth = (wS / p) * self.scaleFactor
		position = ( 0 - bx/p + (cursorWidth/2)/self.scaleFactor, startY)

		base.appendSymbolSublayer(
			name = 'scrollbarHz.cursor',
			position = position,
			imageSettings = dict(
				name = 'rectangle',
				size = ( cursorWidth , controlwidth ), #(hM/clines)*p), #hS*self.scaleFactor - ((bh*self.scaleFactor)/(hS*self.scaleFactor))),
				fillColor = self.colorBackground, #COLOR_BACKGROUND,
				strokeWidth = 1,
				strokeColor = COLOR_TITLES, #(0, 0, 0, 1),
				acceptsHit = True,
				# cornerRadius = 5
			)
		)
		base.addScaleTransformation(self.scaleFactor)


	def drawVerticalScrollBar(self):
		# TODO instead of removing layers, think about reposition
		container = self.getMerzContainer()
		sbb = container.getSublayer('scrollbarVr.base')
		if sbb:
			container.removeSublayer(sbb)

		hM = self.height()
		wM = self.width()
		controlwidth = 7
		doc = container.getSublayer('base')
		if not doc: return
		bw , bh = doc.getSize()
		bx , by = doc.getPosition()

		if bh*self.scaleFactor < hM: return

		sbcolor = (0, 0, 0, 1)
		pcolor = (0,0,0,1)

		startX = ( wM - 10 ) / self.scaleFactor
		startY = 20 / self.scaleFactor
		endX = startX
		endY = ( hM - 20 ) / self.scaleFactor

		base = container.appendBaseSublayer(
			name = 'scrollbarVr.base',
			position = (startX-(10/self.scaleFactor), startY),
			size = ((20/self.scaleFactor), endY-(20/self.scaleFactor)),
			# fillColor = (0, 0, 0, 0),
			backgroundColor = (0, 0, 0, 0),#(.5,0,0,.3),
			# fillColor = (.1,.1,.1,.3),
			acceptsHit = True
		)
		wS, hS = base.getSize()
		sb = base.appendLineSublayer(
			name = 'scrollbarVr.line',
			startPoint = ((10/self.scaleFactor), 0),
			endPoint = ((10/self.scaleFactor), hS),
			strokeWidth = 1,
			strokeColor = COLOR_TITLES, #(0,0,0,1),#(.3,.3,.3,.3),
			strokeDash = (1, 3) #hM / clines)
		)
		sb.setStartSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= COLOR_TITLES ) )
		sb.setEndSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= COLOR_TITLES ) )

		wS, hS = sb.getSize()

		p = (bh - 60 / self.scaleFactor) / hS
		cursorWidth = ((hS-20 / self.scaleFactor) / p) * self.scaleFactor

		self.VRscrollheight = hS
		self.VRscrollcursor = cursorWidth
		fix = 0
		if cursorWidth < 3:
			cursorWidth = 3
			# fix = 3/2
		position = ((10/self.scaleFactor), (hS) - ((hS) + by / p - (cursorWidth / 2) / self.scaleFactor)  - fix/self.scaleFactor)

		base.appendSymbolSublayer(
			name = 'scrollbarVr.cursor',
			position = position,
			imageSettings = dict(
				name = 'rectangle',
				size = (controlwidth,  cursorWidth ),
				fillColor = self.colorBackground, #COLOR_BACKGROUND,
				strokeWidth = 1,
				strokeColor = COLOR_TITLES, #(0, 0, 0, 1),
				acceptsHit = True
			)
		)
		base.addScaleTransformation(self.scaleFactor)

	def scrollBarVRcallback(self, eventname, point):
		dX, dY = point
		if eventname == 'mouseDragged' and self.VRscrollHit:
			self.scrollMoving((0, -dY/((self.VRscrollcursor)/(self.VRscrollheight*self.scaleFactor))/3))
		elif eventname == 'mouseDown' and not self.HZscrollHit:
			self.VRscrollHit = True

	def scrollBarHZcallback(self, eventname, point):
		dX, dY = point
		if eventname == 'mouseDragged' and self.HZscrollHit:
			self.scrollMoving((-dX, 0))
		elif eventname == 'mouseDown' and not self.VRscrollHit:
			self.HZscrollHit = True




	# EVENTS STUFF ==============================================
	def eventMouseUp(self, event):
		self.VRscrollHit = False
		self.HZscrollHit = False

		X_mouse_pos = int(round(event.locationInWindow().x, 0))
		Y_mouse_pos = int(round(event.locationInWindow().y, 0))
		container = self.getMerzContainer()
		point = self.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))
		hits = container.findSublayersContainingPoint((point), onlyAcceptsHit = True)
		for layer in hits:
			n = layer.getName()
			if n and n in self.controlsElements and self.controlsElements[n]:
				self.controlsElements[n]('mouseUp', point)


	def eventMouseDragged(self, event):
		dragOnlyWithinLayer = False
		deltaX = int(round(event.deltaX(), 0))
		deltaY = int(round(event.deltaY(), 0))
		X_mouse_pos = int(round(event.locationInWindow().x, 0))
		Y_mouse_pos = int(round(event.locationInWindow().y, 0))
		location = self.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))

		delta = (deltaX, deltaY)
		controlHit = False

		if not dragOnlyWithinLayer:
			for n in self.controlsElements.keys():
				self.controlsElements[n]('mouseDragged', delta)
		else:
			container = self.getMerzContainer()
			_x, _y = location
			hits = container.findSublayersIntersectedByRect((_x, _y, 1, 1), onlyAcceptsHit = True)
			for layer in hits:
				n = layer.getName()
				if n and n in self.controlsElements and self.controlsElements[n]:
					self.controlsElements[n]('mouseDragged', delta)
					controlHit = True

		if not controlHit and not self.HZscrollHit and not self.VRscrollHit and self.selectedGlyphs:
			item = dict(
				typesAndValues = {
					"plist": dict(letters = self.selectedGlyphs, index = 0, idView = self.id)
				},
				image = tdDragTableImageFactory((27,32)),#image,
				location = location
			)
			vanilla.startDraggingSession(
				view = self,
				event = event,
				items = [item],
				formation = "default"
			)


	def eventMouseDown(self, event):
		self.VRscrollHit = False
		self.HZscrollHit = False

		X_mouse_pos = int(round(event.locationInWindow().x, 0))
		Y_mouse_pos = int(round(event.locationInWindow().y, 0))
		container = self.getMerzContainer()
		point = self.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))
		_x, _y = point
		hits = container.findSublayersIntersectedByRect((_x, _y, 1, 1),onlyAcceptsHit = True)
		# hits = container.findSublayersContainingPoint((point), onlyAcceptsHit = True)
		# print(hits)

		# if len(hits) > 1:
		# 	_n = hits[-1].getName()
		# 	if _n and _n in self.controlsElements and self.controlsElements[_n]:
		# 		hits = [hits[-2]]
		# 	else:
		# 		hits = [hits[-1]]
		controlHit = False
		for layer in hits:
			n = layer.getName()
			if n and n in self.controlsElements and self.controlsElements[n]:
				controlHit = True
				self.controlsElements[n]('mouseDown', point)
		if not controlHit:
			for layer in hits:
				self.selectedGlyphs = []
				self.selectGlyphLayer(layer, selectionMode = self.selectionMode)
			if event.clickCount() == 2 and self.selectedGlyphs and self.doubleClickCallback:
				self.doubleClickCallback(self)


	def srollFinishedCallback(self, sender):
		self.scrollAnimation = False


	def scrollMoving(self, delta, scaleScroll = 40, animate = False):
		deltaX, deltaY = delta
		# scaleScroll = 40
		# if self.scrollAnimation: return
		deltaX = deltaX * scaleScroll
		deltaY = deltaY * scaleScroll
		# print (deltaX, deltaY)
		container = self.getMerzContainer()
		hM = self.height()
		wM = self.width()

		layer = container.getSublayer('base')
		if not layer: return
		x, y = layer.getPosition()
		w2, h2 = layer.getSize()
		_x = x + deltaX
		_y = y - deltaY

		# for i in range(0,abs(deltaY)):
		# 	self.scrollAnimation = True
			#(i*d)/abs(d)
			# _y = y - deltaY
			# _y = y - (i*deltaY)/abs(deltaY)

		d = 0
		if animate:
			d = .3
			# self.scrollAnimation = True
		with layer.propertyGroup(duration = d): #, animationFinishedCallback = self.srollFinishedCallback): #): #
			if _y > 0:
				_y = 0
			if _y < hM / self.scaleFactor - h2:
				_y = hM / self.scaleFactor - h2
			if wM > w2 * self.scaleFactor:
				_x = 0
			else:
				if _x >= 0:  # return
					_x = 0
				if w2 * self.scaleFactor + _x * self.scaleFactor + 100 < wM: return
			layer.setPosition((_x , _y ))
		# else:
		# 	self.scrollAnimation = False
		# with layer.propertyGroup(duration = d):
		# 	layer.setPosition((_x , _y ))

		self.drawGlyphsMatrix()


	def eventScrollWheel(self, event):
		# print (event.phase(), event.momentumPhase())
		deltaX = int(round(event.deltaX(), 0))
		deltaY = int(round(event.deltaY(), 0))
		if deltaX == 0 and deltaY == 0: return
		# # print (deltaX, deltaY)
		# if event.phase() == 32:
		# 	print ('start')
		# 	self.scrollPhase = []
		# if event.phase() == 4:
		# 	print ('moving',deltaX,deltaY)
		# 	self.scrollPhase.append((deltaX,deltaY))
		# if event.phase() == 8:
		# 	xm = 0
		# 	ym = 0
		# 	print ('ended')
		# 	for item in self.scrollPhase:
		# 		xm += item[0]
		# 		ym += item[1]
		# 	self.scrollMoving((xm,ym), animate = True)

		self.scrollMoving((deltaX,deltaY))

	def eventMagnify(self, event):
		X_mouse_pos = int(round(event.locationInWindow().x, 0))
		Y_mouse_pos = int(round(event.locationInWindow().y, 0))
		container = self.getMerzContainer()
		point = self.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))

		scale = self.scaleFactor
		scale += event.magnification() / 50
		self.setScaleGlyphsMatrix(scale)

		base = container.getSublayer('base')
		x, y = base.getPosition()
		_x, _y = point
		with base.propertyGroup():
			base.setPosition((0, y - _y))  # ((wM/self.scaleFactor - w2)/2)
		self.drawGlyphsMatrix(refresh = True)


	def keyUpPressedCallback(self, sender, value):
		if self.useRayBeam:
			self.moveRayBeam(+10)
		else:
			self.gotoPreviousLine()

	def keyDownPressedCallback(self, sender, value):
		if self.useRayBeam:
			self.moveRayBeam(-10)
		else:
			self.gotoNextLine()

	def moveRayBeamCallback(self, sender, value):
		self.moveRayBeam(moveto = value)

	def moveVertRayBeamCallback(self, sender, value):
		self.moveVerticalRayBeam(moveto = value)

	def switchRayBeamCallback(self, sender, value):
		if value == 'alt':
			self.useRayStems = not self.useRayStems
		self.switchRayBeam(not self.useRayBeam)

	def switchVertRayBeamCallback(self, sender, value):
		self.useVerticalRayBeam = not self.useVerticalRayBeam
		self.switchVerticalRayBeam(self.useVerticalRayBeam)

	def eventKeyDown(self, sender, event):
		self.keyCommander.checkCommand(sender, event)

	def eventResizeView(self):
		self.drawToolbar()
		self.drawScrollBars()
		self.drawStatuses()
		container = self.getMerzContainer()
		hM = self.height()
		wM = self.width()
		# print (hM, wM)


		#
		layer = container.getSublayer('base')
		if not layer: return
		x, y = layer.getPosition()
		# print(hM, wM, x, y)
		w2, h2 = layer.getSize()
		if x < 0:
			with layer.propertyGroup( duration = .2):
				layer.setPosition((0, y))
		# _x = x * self.scaleFactor#+ deltaX
		# _y = y * self.scaleFactor#- deltaY
		# w2 = w2 * self.scaleFactor
		# h2 = h2 * self.scaleFactor
		# print (hM, wM, x, y, w2, h2)
		# with layer.propertyGroup():  # , animationFinishedCallback = self.srollFinishedCallback): #): #
		# 	if _y > 0:
		# 		_y = 0
		# 	if _y < hM / self.scaleFactor - h2:
		# 		_y = hM / self.scaleFactor - h2
		# 	if wM > w2 * self.scaleFactor:
		# 		_x = 0
		# 	else:
		# 		if _x >= 0:  # return
		# 			_x = 0
		# 		if w2 * self.scaleFactor + _x * self.scaleFactor + 100 < wM: return
		# 	layer.setPosition((_x, _y))
		# # self.drawGlyphsMatrix(refresh = True)

	# def closing(self):
	# 	merz.SymbolImageVendor.unregister


