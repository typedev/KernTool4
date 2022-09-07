
# import merz

from merz import *
# from fontParts import *
# from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber, registerRoboFontSubscriber, registerCurrentFontSubscriber
from merz.tools.drawingTools import NSImageDrawingTools
# from mojo.pens import DecomposePointPen
# import AppKit
# import math
import vanilla
from vanilla.dragAndDrop import dropOperationMap

import importlib

import tdLibEssentials
importlib.reload(tdLibEssentials)
from tdLibEssentials import *
# import tdKernToolEssentials4
# importlib.reload(tdKernToolEssentials4)
# from tdKernToolEssentials4 import *

#
#
# import tdSpaceControl
# importlib.reload(tdSpaceControl)
# from tdSpaceControl import *

import tdKeyCommander
importlib.reload(tdKeyCommander)
from tdKeyCommander import *


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

# KernToolDragTableSymbol = "com.typedev.KernToolDragTableSymbol"
# merz.SymbolImageVendor.registerImageFactory(KernToolDragTableSymbol, tdDragTableImageFactory)

DROP_STYLE_INSERT = 1
DROP_STYLE_DROPIN = 2
DROP_STYLE_SCENE  = 3

DRAWING_BASE_MODE_NONE = 0
DRAWING_BASE_MODE_SCROLL = 1
DRAWING_BASE_MODE_RESIZE = 2



class TDMerzMatrixDesigner (object): #MerzView

	def __init__(self, container=None,
	             layerWillDrawCallback = None,
	             selectLayerCallback = None,
	             startDraggingSessionCallback = None,
	             dropStyle=None,
	             clearHash = False):
		# super().__init__(posSize)
		# view = self.getNSView()
		# self._buildView(view, delegate, (0,0,0,0))

		self.id = getUniqName()

		self.backgroundColor = (0,0,0,0)
		self.selectionColor = (1,0,0,1)
		self.selectedBorderColor = (0,0,0,1)
		self.borderColor = (0,0,0,0)
		self.controlsColor = (1,1,1,1)
		self.cornerRadius = 0
		self.focusColor = (0,0,1,1)
		self.focusMargin = 0
		# self.animatedStart = False
		# self.animatedDirection = None

		self.statuses = {}

		self.windowWidth = 0 #self.width()
		self.windowHeight = 0 #self.height()
		self.sceneMarginX = 20
		self.sceneMarginY = 20
		self.sceneMarginYTop = 30
		self.baseWidth = 0
		self.baseHeight = 0
		self.elementWidth = 0
		self.elementHeight = 0
		self.elementXshift = 0
		self.elementYshift = 0
		self.elementsQuantity = 0
		self.fitWidth = True
		self.listOfwidths = []
		# if not container:
		# 	print ('error, no container')
		# 	return
		self.container = container #self.getMerzContainer()
		self.documentLayer = None
		self.dropsLayer = None
		self.focusLayer = None
		self.controlsLayer = None
		self.selectedLayer = None

		self.items = []
		self.selection = []
		self.visibleLayers = []
		self.indexLayers = []
		self.clearHash = clearHash
		self.indexYpos = {}

		self.dropStyle = dropStyle
		self.focused = True

		# scrollbars control
		self.controlsElements = {}
		self.controlsElementsDrawingMethods = {}

		self.VRscrollheight = 0
		self.VRscrollcursor = 0
		self.VRscrollHit = False
		self.HZscrollHit = False

		self.momentY = 0
		self.momentX = 0

		self.scrollAnimation = False
		self.scrollPhase = []
		self.layerWillDrawCallback = layerWillDrawCallback
		self.selectLayerCallback = selectLayerCallback
		self.startDraggingSessionCallback = startDraggingSessionCallback

		self.addControlElement(name = 'scrollbarVr.base', callback = self.scrollBarVRcallback, drawingMethod = self.drawVerticalScrollBar)
		self.addControlElement(name = 'scrollbarHz.base', callback = self.scrollBarHZcallback, drawingMethod = self.drawHorizontalScrollBar)
		# self.drawBase()

	def setupScene(self, size = None, elementSize = (0, 0), elementMargins = (0, 0),
	               backgroundColor=None, selectionColor = None, controlsColor = None,
	               selectedBorderColor = None, borderColor = None,
	                cornerRadius = 0, focusColor = None, fitWidth = True): # animatedStart = False,
		self.drawBase()
		if not size:
			size = (1,1)
		self.setViewSize(size)

		welem, helem = elementSize
		xshift, yshift = elementMargins
		self.elementWidth = welem
		self.elementHeight = helem
		self.elementXshift = xshift
		self.elementYshift = yshift
		self.fitWidth = fitWidth

		if backgroundColor:
			self.backgroundColor = backgroundColor
		if selectionColor:
			self.selectionColor = selectionColor
		if controlsColor:
			self.controlsColor = controlsColor
		if selectedBorderColor:
			self.selectedBorderColor = selectedBorderColor
		if borderColor:
			self.borderColor = borderColor
		if focusColor:
			self.focusColor = focusColor
		# if animatedStart:
		# 	self.animatedStart = animatedStart
		# if animatedDirection:
		# 	self.animatedDirection = animatedDirection
		self.cornerRadius = cornerRadius
		self.setBackgroundColor(self.backgroundColor)


	def drawControlsElements(self):
		for name in self.controlsElementsDrawingMethods.keys():
			if self.controlsElementsDrawingMethods[name]:
				self.controlsElementsDrawingMethods[name](self.controlsLayer, name)
		# self.drawHorizontalScrollBar()
		# self.drawVerticalScrollBar()

	def addControlElement(self, name, callback = None, drawingMethod = None):
		self.controlsElements[name] = callback
		self.controlsElementsDrawingMethods[name] = drawingMethod

	def setBackgroundColor(self, color):
		self.backgroundColor = color
		self.container.setBackgroundColor(color)
		if self.documentLayer:
			self.documentLayer.setBackgroundColor(color)
		self.drawBase()


	def fillHash(self, deep = 3):
		w, h = self.container.getSize()
		x, y = self.documentLayer.getPosition()
		if deep: # and deep != 'full':
			self.visibleLayers = sum([ self.indexYpos[s] for s in list(filter(lambda p: p > (-y-100) and p < (-y + h*deep), self.indexYpos.keys())) ], [])
		elif deep == 0:
			self.visibleLayers = self.documentLayer.getSublayers()
		with self.documentLayer.sublayerGroup():
			for layer in self.visibleLayers: #self.documentLayer.getSublayers():
				index = self.getIndexOfLayer(layer)
				# if not index and index != 0: return
				if not layer.getSublayers():
					self.layerWillDrawCallback(self, dict(layer = layer, index = index, item = self.items[index]))


	def moveSceneToStartPosition(self, animated = False, direction ='bottom', duration = .4):
		w, h = self.container.getSize()
		dw, dh = self.documentLayer.getSize()
		# drw, drh = self.dropsLayer.getSize()

		# w, h = self.container.getSize()
		# dw, dh = self.documentLayer.getSize()
		# dx, dy = self.documentLayer.getPosition()
		# if dy + dh > 0:
		with self.documentLayer.propertyGroup():  # duration = .5
			self.documentLayer.setPosition((0, h - dh))  # - (dy + dh)
			self.dropsLayer.setPosition((0, h - dh))  # - (dy + dh)

		if direction == 'bottom' and animated:
			self.documentLayer.setPosition((0, - dh))
			self.dropsLayer.setPosition((0, - dh))
			with self.documentLayer.propertyGroup(duration = duration):
				self.documentLayer.setPosition((0, h - dh))
				self.dropsLayer.setPosition((0, h - dh))
		elif direction == 'left' and animated:
			self.documentLayer.setPosition((-dw, h - dh))
			self.dropsLayer.setPosition((-dw, h - dh))
			with self.documentLayer.propertyGroup(duration = duration):
				self.documentLayer.setPosition((0, h - dh))
				self.dropsLayer.setPosition((0, h - dh))
		elif direction == 'right' and animated:
			self.documentLayer.setPosition((dw * 2, h - dh))
			self.dropsLayer.setPosition((dw * 2, h - dh))
			with self.documentLayer.propertyGroup(duration = duration):
				self.documentLayer.setPosition((0, h - dh))
				self.dropsLayer.setPosition((0, h - dh))
		elif direction == 'shake' and animated:
			w, h = self.container.getSize()
			dw, dh = self.documentLayer.getSize()
			with self.documentLayer.propertyGroup():  # duration = .5
				self.documentLayer.setPosition((0, h - dh))  # - (dy + dh)
				self.dropsLayer.setPosition((0, h - dh))  # - (dy + dh)
			with self.documentLayer.propertyGroup():
				d = .07
				for layer in self.documentLayer.getSublayers():
					with layer.propertyGroup(duration = .03, restore = True, delay = d):
						_x,_y = layer.getPosition()
						layer.setPosition((_x, _y + 10))
						d += .02

		elif not animated:
			w, h = self.container.getSize()
			dw, dh = self.documentLayer.getSize()
			# dx, dy = self.documentLayer.getPosition()
			# if dy + dh > 0:
			with self.documentLayer.propertyGroup():  # duration = .5
				self.documentLayer.setPosition((0, h - dh))  # - (dy + dh)
				self.dropsLayer.setPosition((0, h - dh))  # - (dy + dh)
				self.drawBase()




	def drawBase(self, mode = None): #, testrun = False
		if not self.documentLayer:
			self.documentLayer = self.container.appendBaseSublayer(
				name = 'base',
				size = (self.baseWidth, self.baseHeight),  # self.merzW
				position = (0, 0)
			)
			self.dropsLayer = self.container.appendBaseSublayer(
				name = 'drops',
				size = (self.baseWidth, self.baseHeight),  # self.merzW
				position = (0, 0)
			)
			hM = self.windowHeight
			wM = self.windowWidth
			self.controlsLayer = self.container.appendBaseSublayer(
				name = 'controls',
				size = (wM, hM),
				position = (0, 0)
			)
			self.focusLayer = self.container.appendBaseSublayer(
				name = 'focus',
				size = (wM-self.focusMargin*2,hM-self.focusMargin*2),
				cornerRadius = 7,
				position = (self.focusMargin,self.focusMargin)
			)
		if not self.layerWillDrawCallback: return
		# check if the contentLayer is visible, create a callback to draw it
		w, h = self.container.getSize()
		x, y = self.documentLayer.getPosition()

		# self.visibleLayers = sum([ self.indexYpos[s] for s in list(filter(lambda p: p > (-y-200) and p < (-y + h + 100), self.indexYpos.keys())) ], [])
		self.visibleLayers = sum([ self.indexYpos[s] for s in list(filter(lambda p: p > (-y - self.elementHeight) and p < (-y + h + self.elementHeight), self.indexYpos.keys())) ], [])

		with self.documentLayer.sublayerGroup():
			for layer in self.visibleLayers:
				# to speed up the work, the rendering function, having received a callback,
				# must check the layers of the content layer, and decide whether to draw it,
				# just update it or do nothing
				index = self.getIndexOfLayer(layer)
				if not index and index != 0 : break # or index>=len(self.items)
				# if not layer.getSublayers():
				self.layerWillDrawCallback(self, dict( layer = layer, index = index, item = self.items[index], drawmode = mode )) # self.documentLayer.getSublayers().index(layer)

			# clear the layers of contentLayers that are not included in the visibility zone
			if self.clearHash:
				for layer in list( set(self.visibleLayers) ^ set(self.documentLayer.getSublayers()) ):
					layer.clearSublayers()

		self.drawControlsElements()


	# SCROLLBARS STUFF ==============================================
	def drawHorizontalScrollBar(self, container, name):
		# TODO instead of removing layers, think about reposition
		if not container: return # or not self.documentLayer
		# container = self.controlsLayer # self.getMerzContainer()
		sbb = container.getSublayer('scrollbarHz.base')
		if sbb:
			container.removeSublayer(sbb)

		# hM = self.windowHeight
		wM = self.windowWidth

		controlwidth = 7

		doc = self.documentLayer # container.getSublayer('base')
		# if not doc: return
		bw , bh = doc.getSize()
		bx , by = doc.getPosition()

		if bw < wM: return

		baseY = self.sceneMarginY/2
		startX = self.sceneMarginX
		startY = baseY
		endX = ( wM - self.sceneMarginX )
		endY = baseY

		base = container.appendBaseSublayer(
			name = 'scrollbarHz.base',
			position = (startX , startY - baseY),
			size = ((wM - self.sceneMarginX*2), (self.sceneMarginY) ),
			backgroundColor = (0, 0, 0, 0),#(.5,0,0,.3),
			acceptsHit = True
		)
		wS, hS = base.getSize()
		sb = base.appendLineSublayer(
			name = 'scrollbarHz.line',
			startPoint = (0, startY),
			endPoint = (wS, endY),
			strokeWidth = 1,
			strokeColor = self.controlsColor, #(0,0,0,1),#(.3,.3,.3,.3),
			strokeDash = (1, 3) #hM / clines)
		)
		sb.setStartSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= self.controlsColor  ) )
		sb.setEndSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= self.controlsColor ) )

		wS, hS = sb.getSize()

		p = (bw + self.sceneMarginX*3) / wS
		cursorWidth = (wS / p)
		position = ( 0 - bx/p + (cursorWidth/2), startY)

		base.appendSymbolSublayer(
			name = 'scrollbarHz.cursor',
			position = position,
			imageSettings = dict(
				name = 'rectangle',
				size = ( cursorWidth , controlwidth ),
				fillColor = self.backgroundColor, #COLOR_BACKGROUND,
				strokeWidth = 1,
				strokeColor = self.controlsColor, #(0, 0, 0, 1),
				acceptsHit = True,
				# cornerRadius = 5
			)
		)

	def drawVerticalScrollBar(self, container, name):
		# TODO instead of removing layers, think about reposition
		if not container: return #or not self.documentLayer: return
		# container = self.controlsLayer
		# container = self.getMerzContainer()
		sbb = container.getSublayer('scrollbarVr.base')
		if sbb:
			container.removeSublayer(sbb)

		hM = self.windowHeight
		wM = self.windowWidth
		controlwidth = 7
		doc = self.documentLayer # container.getSublayer('base')
		# if not doc: return
		bw , bh = doc.getSize()
		bx , by = doc.getPosition()

		if bh < hM: return

		startX = ( wM - self.sceneMarginX/2 )
		startY = self.sceneMarginY
		endX = startX
		endY = ( hM - self.sceneMarginY )

		base = container.appendBaseSublayer(
			name = 'scrollbarVr.base',
			position = (startX-(self.sceneMarginX/2), startY),
			size = (self.sceneMarginX, endY-self.sceneMarginY),
			backgroundColor = (0, 0, 0, 0),#(.5,0,0,.3),
			acceptsHit = True
		)
		wS, hS = base.getSize()
		sb = base.appendLineSublayer(
			name = 'scrollbarVr.line',
			startPoint = (self.sceneMarginX/2, 0),
			endPoint = (self.sceneMarginX/2, hS),
			strokeWidth = 1,
			strokeColor = self.controlsColor, #(0,0,0,1),#(.3,.3,.3,.3),
			strokeDash = (1, 3) #hM / clines)
		)
		sb.setStartSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= self.controlsColor ) )
		sb.setEndSymbol( dict( name="rectangle", size=(1, controlwidth), fillColor= self.controlsColor ) )

		wS, hS = sb.getSize()

		p = (bh - self.sceneMarginY*3 ) / hS
		cursorWidth = ((hS-self.sceneMarginX ) / p)

		self.VRscrollheight = hS
		self.VRscrollcursor = cursorWidth
		fix = 0
		if cursorWidth < 3:
			cursorWidth = 3
			# fix = 3/2
		position = (self.sceneMarginX/2, hS - (hS + by / p - (cursorWidth / 2) )  - fix)

		base.appendSymbolSublayer(
			name = 'scrollbarVr.cursor',
			position = position,
			imageSettings = dict(
				name = 'rectangle',
				size = (controlwidth,  cursorWidth ),
				fillColor = self.backgroundColor, #COLOR_BACKGROUND,
				strokeWidth = 1,
				strokeColor = self.controlsColor, #(0, 0, 0, 1),
				acceptsHit = True
			)
		)

	def scrollBarVRcallback(self, eventname, point, name):
		dX, dY = point
		if eventname == 'mouseDragged' and self.VRscrollHit:
			self.scrollMoving((0, -dY/(self.VRscrollcursor/self.VRscrollheight)/5), scaleScroll = 5)
		elif eventname == 'mouseDown' and not self.HZscrollHit:
			self.VRscrollHit = True

	def scrollBarHZcallback(self, eventname, point, name):
		dX, dY = point
		if eventname == 'mouseDragged' and self.HZscrollHit:
			self.scrollMoving((-dX, 0), scaleScroll = 5)
		elif eventname == 'mouseDown' and not self.VRscrollHit:
			self.HZscrollHit = True

	def drawSelectedLayer(self, index, selected = False):
		layer = self.documentLayer.getSublayers()[index]
		if selected:
			backgroundColor = self.selectionColor
			borderColor = self.selectedBorderColor
			layer.appendFilter(
				dict(
					name = "saturation",
					filterType = "colorControls",
					saturation = 3.8,
					brightness = 0,
				)
			)
		else:
			backgroundColor = (0,0,0,0)
			borderColor = self.borderColor
			filters = layer.getFilters()
			for filter in filters:
				if filter['name'] == 'saturation':
					layer.removeFilter('saturation')
			# layer.clearAnimation()
			# layer.setOpacity(1)
		layer.setBackgroundColor((backgroundColor))
		layer.setBorderColor(borderColor)

	def removeDraggedCursor(self):
		if self.dropStyle == DROP_STYLE_INSERT:
			if self.dropsLayer.getSublayer('draggCursor'):
				self.dropsLayer.removeSublayer('draggCursor')
		elif self.dropStyle == DROP_STYLE_DROPIN:
			for idx, layer in enumerate(self.documentLayer.getSublayers()):
				if idx in self.selection:
					layer.setBorderWidth(1)
					layer.setBorderColor(self.selectedBorderColor)
				else:
					layer.setBorderWidth(1)
					layer.setBorderColor((0,0,0,0))


	def drawDraggedCursor(self, layerOver):
		dropColor = (1,0,0,1)
		xshift = self.elementXshift / 2
		yshift = self.elementYshift / 2
		if not self.dropStyle: return
		elif self.dropStyle == DROP_STYLE_INSERT:
			x,y = layerOver.getPosition()
			w,h = layerOver.getSize()

			with self.dropsLayer.sublayerGroup():
				self.removeDraggedCursor()

				cursorLayer = self.dropsLayer.appendLineSublayer(
					name = 'draggCursor',
					startPoint = (x-xshift, y - yshift),
					endPoint = (x-xshift, y+h + yshift),
					strokeWidth = 3,
					strokeColor = (1,0,0,1),
				)
				cursorLayer.setStartSymbol( dict( name="oval", size=(10+xshift, 10+yshift), fillColor= dropColor ) )
				cursorLayer.setEndSymbol( dict( name="oval", size=(10+xshift, 10+yshift), fillColor= dropColor ) )
		elif self.dropStyle == DROP_STYLE_DROPIN:
			# layerOver = self.documentLayer.getSublayers()[index]
			with self.documentLayer.sublayerGroup():
				self.removeDraggedCursor()
				layerOver.setBorderWidth(3)
				layerOver.setBorderColor(dropColor)


	# EVENTS STUFF ==============================================
	def eventMouseUp(self, event, hits, point, modifier):
		self.VRscrollHit = False
		self.HZscrollHit = False
		# hits = self.container.findSublayersContainingPoint((point), onlyAcceptsHit = True)
		controlHit = False
		for layer in hits:
			n = layer.getName()
			if n and n in self.controlsElements and self.controlsElements[n]:
				self.controlsElements[n]('mouseUp', point, n)
				self.controlsElementsDrawingMethods[n](self.controlsLayer, n)
				controlHit = True
		if not controlHit:
			if self.selectLayerCallback and hits:
				selectedIndex = self.getIndexOfLayer(hits[0])
				alt, shift, cmd, ctrl, caps = modifier
				with self.documentLayer.sublayerGroup():
					if cmd:
						if selectedIndex not in self.selection:
							self.selection.append(selectedIndex)
							self.drawSelectedLayer(selectedIndex, True)
						else:
							self.selection.remove(selectedIndex)
							self.drawSelectedLayer(selectedIndex,False)
					elif shift:
						if self.selection and selectedIndex > self.selection[-1]:
							for i in range(self.selection[-1] , selectedIndex + 1):
								if i not in self.selection:
									self.selection.append(i)
									self.drawSelectedLayer(i,True)
						elif self.selection and selectedIndex < self.selection[-1]:
							for i in range(selectedIndex , self.selection[-1]):
								if i not in self.selection:
									self.selection.append(i)
									self.drawSelectedLayer(i,True)
					else:
						for i in self.selection:
							self.drawSelectedLayer(i,False)
						self.selection = [selectedIndex]
						self.drawSelectedLayer(selectedIndex,True)

				self.selectLayerCallback(self, dict(layer = hits[0], index = selectedIndex, item = self.items[selectedIndex], hits = hits)) # , modifiers = modifiers


	def eventMouseDragged(self, event, hits, delta, location):
		controlHit = False
		dragOnlyWithinLayer = False
		_x, _y = location
		# hits = self.container.findSublayersIntersectedByRect((_x, _y, 1, 1), onlyAcceptsHit = True)
		if not dragOnlyWithinLayer:
			for n in self.controlsElements.keys():
				self.controlsElements[n]('mouseDragged', delta, n)
		else:
			for layer in hits:
				n = layer.getName()
				if n and n in self.controlsElements and self.controlsElements[n]:
					self.controlsElements[n]('mouseDragged', delta, n)
					controlHit = True

		if not controlHit and not self.HZscrollHit and not self.VRscrollHit and hits: # and hits: # self.selectedGlyphs:
			# print ('start dragging layer', hits)
			layerDragged = hits[0]
			if self.getIndexOfLayer(layerDragged) in self.selection:
				idScene = self.documentLayer.getSuperlayer().getInfoValue('idScene')
				# print (scene)
				item = dict(
					typesAndValues = {
						"plist": dict(indexes = sorted(self.selection), idScene = idScene)
					},
					image = tdDragTableImageFactory((27,32)),#image,
					location = location
				)
				if self.startDraggingSessionCallback:
					self.startDraggingSessionCallback(event, item)



	def eventMouseDown(self, event, hits, point, modifier):
		_x, _y = point
		self.VRscrollHit = False
		self.HZscrollHit = False
		controlHit = False
		for layer in hits:
			n = layer.getName()
			if n and n in self.controlsElements and self.controlsElements[n]:
				controlHit = True
				self.controlsElements[n]('mouseDown', point, n)


	def scrollMoving(self, delta, scaleScroll = 1, animate = False, duration = .0):
		deltaX, deltaY = delta
		deltaX = deltaX * scaleScroll
		deltaY = deltaY * scaleScroll
		hM = self.windowHeight
		wM = self.windowWidth

		layer = self.documentLayer# container.getSublayer('base')
		drops = self.dropsLayer
		if not layer: return
		x, y = layer.getPosition()
		w2, h2 = layer.getSize()
		_x = x + deltaX
		_y = y - deltaY

		# self.scrollAnimation = True
		# if animate:
		# 	d = duration
			# self.scrollAnimation = True
		with layer.propertyGroup(duration = duration): #, animationFinishedCallback = self.srollFinishedCallback):
			if _y > 0:
				_y = 0
			if _y < hM  - h2:
				_y = hM  - h2
			if wM > w2 :
				_x = 0
			else:
				if _x >= 0:  # return
					_x = 0
				if w2 + _x + 100 < wM: return
			layer.setPosition((_x , _y))
			drops.setPosition((_x , _y))
		# self.drawScrollBars()
		self.drawBase(mode = DRAWING_BASE_MODE_SCROLL)


	def eventScrollWheel(self, event, delta, momentumPhase):
		deltaX, deltaY = delta
		scaleScroll = 2
		if  momentumPhase == 0:
			scaleScroll = 10
			self.scrollMoving((deltaX, deltaY), scaleScroll = scaleScroll, duration = .08)
		elif momentumPhase == 4:

			# if not self.documentLayer.getFilter('motionBlur'):
			# 	self.documentLayer.appendFilter(
			# 		    dict(
			# 		        name="motionBlur",
			# 		        filterType="motionBlur",
			# 		        radius=1.0,
			# 		        angle=90
			# 		        )
			# 			)

			self.momentY += deltaY
			scaleScroll = 10
			self.scrollMoving((deltaX, self.momentY), scaleScroll = scaleScroll, duration = .1)
			self.momentY = 0
		elif momentumPhase == 8:
			# self.documentLayer.removeFilter('motionBlur')
			pass
			# self.fillHash()

	# def eventMagnify(self, event):
	# 	X_mouse_pos = int(round(event.locationInWindow().x, 0))
	# 	Y_mouse_pos = int(round(event.locationInWindow().y, 0))
	# 	container = self.getMerzContainer()
	# 	point = self.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))
	#
	# 	scale = self.scaleFactor
	# 	scale += event.magnification() / 50
	# 	self.setScaleGlyphsMatrix(scale)
	#
	# 	base = container.getSublayer('base')
	# 	x, y = base.getPosition()
	# 	_x, _y = point
	# 	with base.propertyGroup():
	# 		base.setPosition((0, y - _y))  # ((wM/self.scaleFactor - w2)/2)
	# 	self.drawBase(refresh = True)

	def eventKeyDown(self, sender, event):
		pass
		# print ('key down',self, sender, event)
		# self.keyCommander.checkCommand(sender, event)

	def eventResizeView(self):
		self.windowWidth, self.windowHeight = self.container.getSize()
		hM = self.windowHeight
		wM = self.windowWidth

		layer = self.documentLayer # container.getSublayer('base')
		drops = self.dropsLayer
		if not layer: return
		x, y = layer.getPosition()
		w2, h2 = layer.getSize()
		if x < 0:
			with layer.propertyGroup( duration = .2):
				layer.setPosition((0, y))
				drops.setPosition((0, y))
		if (y + h2) + hM < hM:
			with layer.propertyGroup():
				layer.setPosition((0, y + abs(y + h2) + hM))
				drops.setPosition((0, y + abs(y + h2) + hM))
		c = self.controlsLayer
		# c.setPosition((0,0))
		c.setSize((wM, hM))
		f = self.focusLayer
		f.setSize((wM-self.focusMargin*2, hM-self.focusMargin*2))
		f.setPosition((self.focusMargin,self.focusMargin))
		self.resizeScene(positiontozero = False)
		# self.drawControlsElements()
		w, h = self.container.getSize()
		dw, dh = self.documentLayer.getSize()
		dx, dy = self.documentLayer.getPosition()
		if h - dh - dy > 0:
			with self.documentLayer.propertyGroup(): #duration = .5
				self.documentLayer.setPosition((0, h - dh )) # - (dy + dh)
				self.dropsLayer.setPosition((0, h - dh )) #- (dy + dh)
		self.drawBase(mode = DRAWING_BASE_MODE_RESIZE)

	def setViewSize(self, size = None, positiontozero = True):
		hM = self.windowHeight
		wM = self.windowWidth
		if size:
			self.baseWidth, self.baseHeight = size
		else:
			size = (self.baseWidth, self.baseHeight + self.sceneMarginY)

		layer = self.documentLayer
		drops = self.dropsLayer
		if not layer: return
		layer.setSize(size)
		drops.setSize(size)
		c = self.controlsLayer
		c.setSize((wM, hM))
		f = self.focusLayer
		f.setSize((wM-self.focusMargin*2,hM-self.focusMargin*2))
		f.setPosition((self.focusMargin,self.focusMargin))

		w, h = self.container.getSize()
		dw, dh = self.documentLayer.getSize()
		dx, dy = self.documentLayer.getPosition()
		# if h - dh - dy > 0:
		if positiontozero:
			with self.documentLayer.propertyGroup():  # duration = .5
				self.documentLayer.setPosition((0, h - dh))  # - (dy + dh)
				self.dropsLayer.setPosition((0, h - dh))  # - (dy + dh)

		# self.drawBase(refresh = True)
	def checkWidthElement(self):
		if self.elementWidth == 0 and self.fitWidth:
			return self.baseWidth - self.elementXshift*2
		# elif self.elementWidth == 0 and not self.fitWidth:
		# 	m = None
		# 	if self.listOfwidths:
		# 		m = max(self.listOfwidths)
		# 	if m:
		# 		print ('return real width', m)
		# 		return m
		# 	else:
		# 		print ('return basewidth', self.baseWidth - self.elementXshift * 2)
		# 		return self.baseWidth - self.elementXshift * 2
		else:
			return self.elementWidth

	def reCalculateSizeScene(self, positiontozero = True):
		xshift = self.elementXshift
		yshift = self.elementYshift
		# welem = self.elementWidth
		helem = self.elementHeight
		quantityElements = len(self.items)
		wM = self.windowWidth

		self.baseWidth = wM - self.sceneMarginX * 2
		welem = self.checkWidthElement()
		if self.baseWidth <= welem + xshift:
			qline = 1
		else:
			qline = self.baseWidth // (welem + xshift)
		# print ('basewidth', self.baseWidth, qline, welem)
		self.baseWidth = (welem + xshift) * qline
		self.baseHeight = (quantityElements // qline) * (helem + yshift) + (helem + yshift) + self.sceneMarginY
		self.setViewSize(positiontozero = positiontozero)


	def appendContentLayer(self, container, position, size, backgroundColor = (0, 0, 0, 0), acceptsHit = True): #, **kwargs
		w, h = size
		x, y = position

		b = container.appendBaseSublayer(
			name = 'contentLayer',
			position = (x, y),
			size = size,
			backgroundColor = backgroundColor,
			acceptsHit = acceptsHit,
			borderWidth = 1,
			borderColor = (0,0,0,0),
			cornerRadius = self.cornerRadius,
			# **kwargs
		)
		if y not in self.indexYpos:
			self.indexYpos[y] = [b]
		else:
			self.indexYpos[y].append(b)
		if x+w > self.baseWidth:
			self.baseWidth = x+w
		if y+h > self.baseHeight:
			self.baseHeight = y+h

	def getIndexOfLayer(self, layer):
		if layer in self.documentLayer.getSublayers():
			return self.documentLayer.getSublayers().index(layer)

	def clearScene(self):
		self.selection = []
		# self.visibleLayers = []
		if self.dropsLayer:
			self.dropsLayer.clearSublayers()
		if self.documentLayer:
			self.documentLayer.clearSublayers()
		if self.controlsLayer:
			self.controlsLayer.clearSublayers()
		if self.focusLayer:
			self.focusLayer.clearSublayers()

	def setSceneItems(self, items, animated = None, elementWidth = None, elementHeight = None):
		#TODO before update scene, need save selected items and restore selection after update
		if elementWidth:
			self.elementWidth = elementWidth
		if elementHeight:
			self.elementHeight = elementHeight
		if len(items) > len(self.items):
			self.updateSceneItems()
			items2insert = items[len(self.items):]
			self.insertSceneItems(items = items2insert, elementWidth = elementWidth, elementHeight = elementHeight)
			self.items = items
			self.reloadSceneItems(items)
		elif len(items) < len(self.items):
			self.updateSceneItems()
			s = [ self.items.index(x) for x in self.items[len(items):] ]
			self._removeSceneItems(itemsIndexes = s)
			self.items = items
			self.reloadSceneItems(items)
		elif len(items) == len(self.items):
			self.reloadSceneItems(items)
		# self.reCalculateSizeScene(positiontozero = True)
		self.resizeScene(positiontozero = True)
		animatedStart = False
		if animated == 'bottom' or animated == 'left' or animated == 'right' or animated == 'shake':
			animatedStart = True
		self.moveSceneToStartPosition(animated = animatedStart, direction = animated)
		self.drawControlsElements()


	def resizeScene(self, positiontozero = True):
		# if not self.documentLayer: return
		# welem = self.elementWidth
		helem = self.elementHeight
		xshift = self.elementXshift
		yshift = self.elementYshift
		self.reCalculateSizeScene(positiontozero = positiontozero)
		welem = self.checkWidthElement()
		ypos = self.baseHeight - helem
		xpos = self.sceneMarginX
		self.indexYpos = {}
		# self.listOfwidths = []
		with self.documentLayer.sublayerGroup():
			for layer in self.documentLayer.getSublayers():
				# layer = self.documentLayer.getSublayers()[index]
				_w,_h = layer.getSize()
				# self.listOfwidths.append(_w)
				if _w != welem:
					# TODO need more light version of redraw, instead of clearing sublayers
					# layer.clearSublayers()
					# layer.setInfoValue('update', 'size')
					layer.setSize((welem,_h))
				layer.setPosition((xpos, ypos))
				if ypos not in self.indexYpos:
					self.indexYpos[ypos] = [layer]
				else:
					self.indexYpos[ypos].append(layer)
				xpos += (welem + xshift)
				if xpos >= self.baseWidth:
					ypos -= (helem + yshift)
					xpos = self.sceneMarginX


	def getSceneItems(self):
		return self.items

	def getSelectedSceneItems(self):
		return sorted(self.selection)

	def _insertSceneItems(self, items, index = None, elementWidth = None, elementHeight = None):
		xshift = self.elementXshift
		yshift = self.elementYshift
		# welem = self.elementWidth
		welem = self.checkWidthElement()
		# helem = elementHeight
		# if not elementHeight:
		helem = self.elementHeight

		ypos = self.baseHeight - helem
		xpos = self.sceneMarginX
		with self.documentLayer.sublayerGroup():
			for item in items:
				self.appendContentLayer(container = self.documentLayer, position = (xpos, ypos), size = (welem, helem))  # , **kwargs
				xpos += (welem + xshift)
				if xpos >= self.baseWidth:
					ypos -= (helem + yshift)
					xpos = self.sceneMarginX
		self.resizeScene()


	def insertSceneItems(self, items, index = None, elementWidth = None, elementHeight = None):
		if index == None:
			self.items.extend(items)
		else:
			for idx, item in enumerate(items):
				self.items.insert(index + idx, item)
			with self.documentLayer.sublayerGroup():
				for layer in self.documentLayer.getSublayers()[index:]:
					layer.clearSublayers()
		self.reCalculateSizeScene()
		self._insertSceneItems(items, index, elementWidth = elementWidth, elementHeight = elementHeight)

		self.drawBase()
		# if quantityElements <= 1500:
		# 	self.fillHash(deep = 0)  # load all items
		# else:
		# 	self.fillHash(deep = 3)  #
		# if self.animatedStart:
		# 	self.drawAnimatedStart(self.animatedDirection)
		# self.drawScrollBars()

	def setSelection(self, itemsIndexes = None, selected = True, animate = False):
		if itemsIndexes == None and selected: # Select ALL
			# self.selection = itemsIndexes
			for idx, layer in enumerate(self.documentLayer.getSublayers()):
				self.selection.append(idx)
				self.drawSelectedLayer(idx, True)
		elif itemsIndexes == None and not selected: # Deselect ALL
			self.selection = []
			for idx, layer in enumerate(self.documentLayer.getSublayers()):
				self.drawSelectedLayer(idx, False)
		elif itemsIndexes and selected: # Select some items
			self.selection = itemsIndexes
			for idx, layer in enumerate(self.documentLayer.getSublayers()):
				if idx not in itemsIndexes:
					self.drawSelectedLayer(idx, False)
				else:
					self.drawSelectedLayer(idx, True)

			w, h = self.container.getSize()
			layer = self.documentLayer.getSublayers()[itemsIndexes[0]]
			dx, dy = layer.getPosition()
			lw, lh = layer.getSize()
			dw, dh = self.documentLayer.getPosition()
			yp = (h - lh) - (dh + dy) # self.elementHeight -> lh
			d = 0
			if animate:
				d = .3
			self.scrollMoving((0, -yp + (h - lh)/2), duration = d) #self.elementHeight -> lh
			if animate:
				with layer.propertyGroup(duration = .05, restore = True, delay = 0.5):
					_x, _y = layer.getPosition()
					layer.setPosition((_x, _y + 20))
			# with layer.propertyGroup(duration = .05, restore = True, delay = 0.5):
			# 	_x, _y = layer.getPosition()
			# 	layer.setPosition((_x, _y - 20))
			# with self.documentLayer.propertyGroup(duration = .4):  # duration = .5
			# 	yp = (h- self.elementHeight) - (dh - dy)
			# 	self.documentLayer.setPosition((0, yp ))  # - (dy + dh)
			# 	self.dropsLayer.setPosition((0,   yp ))  # - (dy + dh)
			# self.drawBase()
		# elif itemsIndexes and not selected: # Deselect some items
		# 	for idx in itemsIndexes:
		# 		if idx in self.selection:
		# 			self.selection.pop(idx)
		# 			self.drawSelectedLayer(idx, False)

	def _removeSceneItems(self, itemsIndexes):
		self.setSelection(selected = False)
		layersToRemove = []
		with self.documentLayer.sublayerGroup():
			# for idx in itemsIndexes:
			# 	self.drawSelectedLayer(idx, False)
			for idx in itemsIndexes:
				# print (self.items, idx)
				# self.items.pop(idx)
				layer = self.documentLayer.getSublayers()[idx]
				layer.clearSublayers()
				layersToRemove.append(layer)
			for layer in layersToRemove:
				self.documentLayer.removeSublayer(layer)
		self.reCalculateSizeScene()
		self.resizeScene()


	def removeSceneItems(self, itemsIndexes):
		for idx in itemsIndexes:
			# print(self.items, idx)
			self.items.pop(idx)
		self._removeSceneItems(itemsIndexes)
		self.drawBase()
		# self.drawScrollBars()

	def updateSceneItems(self, itemsIndexes = None, cleanBefore = True):
		if cleanBefore:
			with self.documentLayer.sublayerGroup():
				if itemsIndexes:
					for idx in itemsIndexes:
						layer = self.documentLayer.getSublayers()[idx]
						layer.clearSublayers()
				else:
					for layer in self.documentLayer.getSublayers():
						layer.clearSublayers()
		self.drawBase()

	def reloadSceneItems(self, items):
		if len(items) != len(self.items): return
		self.items = items
		self.updateSceneItems()

	def setFocus(self, focused):
		if focused:
			self.focusLayer.setBorderWidth(4)
			self.focusLayer.setBorderColor((self.focusColor))
		else:
			self.focusLayer.setBorderWidth(0)
			self.focusLayer.setBorderColor((0, 0, 0, 0))





# ======================================================================================================================================
def getMouseHitLocation(merzView, event):
	X_mouse_pos = int(round(event.locationInWindow().x, 0))
	Y_mouse_pos = int(round(event.locationInWindow().y, 0))
	modifier = decodeModifiers(event.modifierFlags())
	point = merzView.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))
	return (dict( point = point, modifier = modifier))

def getMouseDeltaMoving(event):
	deltaX = int(round(event.deltaX(), 0))
	deltaY = int(round(event.deltaY(), 0))
	return (deltaX, deltaY)


class TDMerzMatrixScenery(MerzView):
	def __init__(self, posSize, delegate=None):
		super().__init__(posSize)
		view = self.getNSView()
		self._buildView(view, delegate, (0,0,0,0))
		self.container = self.getMerzContainer()
		self.matrix = None
		self.statuses = None
		self.scenes = {}
		self.scenesRules = {}
		self.dropStyle = None
		self.dropCallback = None

	def setupScene(self, position = None, size = None, layerWillDrawCallback = None, selectLayerCallback = None, clearHash = False,
	               dropStyle = None, dropCallback = None, **kwargs):
		if not size:
			size = 0,0
		if not position:
			position = 0,0
		self.dropStyle = dropStyle
		self.dropCallback = dropCallback

		scene = self.container.appendBaseSublayer(
			name = 'scene',
			position = position,
			size = size,
			cornerRadius = 5,
			acceptsHit = True,
		)
		scene.setMaskToFrame(True)
		scene.setInfoValue('idScene', getUniqName())
		matrix = TDMerzMatrixDesigner(container = scene, # layer
		                              layerWillDrawCallback = layerWillDrawCallback,
		                              selectLayerCallback = selectLayerCallback,
		                              startDraggingSessionCallback = self.startDraggingSessionCallback,
		                              clearHash = clearHash,
		                              dropStyle = dropStyle)
		self.scenes[scene] = matrix
		self.scenesRules[scene] = (position, size)
		matrix.setupScene(**kwargs)
		return scene

	def getDefaultScene(self):
		return list(self.scenes.keys())[0]

	def clearScene(self, scene = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			# self.scenes[scene].clearScene()
			self.scenes[scene].clearScene()

	def setSceneItems(self, scene=None, **kwargs):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			# self.scenes[scene].clearScene()
			self.scenes[scene].setSceneItems(**kwargs)

	def removeSceneItems(self, scene=None, **kwargs):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].removeSceneItems(**kwargs)

	def setSelection(self, scene=None, **kwargs):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].setSelection(**kwargs)

	def updateSceneItems(self, scene=None, **kwargs):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].updateSceneItems(**kwargs)

	def startDraggingSessionCallback(self, event, item):
		if not self.dropStyle: return
		vanilla.startDraggingSession(
			view = self,
			event = event,
			items = [ item ],
			formation = "default"
		)

	def getIndexOfLayer(self, scene = None, layer = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			return self.scenes[scene].getIndexOfLayer(layer)

	def drawDraggedCursor(self, scene = None, index = 0):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].drawDraggedCursor(index)

	def removeDraggedCursor(self):
		for scene in self.scenes:
			scene.setBorderWidth(0)
			scene.setBorderColor((0, 0, 0, 0))
			self.scenes[scene].removeDraggedCursor()

	def moveScene(self, scene = None, delta = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].scrollMoving(delta)

	def drawSelectedScene(self, scene = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes and self.dropStyle:
			scene.setBorderWidth(2)
			scene.setBorderColor((1,0,0,1))

	def setFocus(self, scene = None, focused = False):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].setFocus(focused)

	def getSceneById(self, idScene):
		for scene in self.scenes:
			_idScene = scene.getInfoValue('idScene')
			if _idScene == idScene:
				return scene

	def insertSceneItems(self, scene = None, items = None, index = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].insertSceneItems(items = items, index = index)

	def getSceneItems(self, scene = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			return self.scenes[scene].getSceneItems()

	def getSelectedSceneItems(self, scene = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			return self.scenes[scene].getSelectedSceneItems()

	def reloadSceneItems(self, scene = None, items = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].reloadSceneItems(items)

	def eventDrop(self, scene, dropInfo):
		# print ('dropped into scene', scene)
		# print (dropInfo)
		destinationScene = scene
		sourceScene = dropInfo['sourceScene']
		layerOver = dropInfo['layerOver']
		itemsIndexes = dropInfo['indexes']
		if self.dropCallback:
			self.dropCallback(self.scenes[scene], dict(sourceScene = sourceScene, destinationScene = destinationScene,
			                                           layerOver = layerOver, itemsIndexes = itemsIndexes))

	# def removeSelectedScenes(self):
	# 	pass
		# for scene in self.scenes:
		# 	# self.scenes[scene].removeDraggedCursor()
		# 	scene.setBorderWidth(0)
		# 	scene.setBorderColor((0, 0, 0, 0))

	def addControlElement(self, scene=None, name=None, callback = None, drawingMethod = None):
		if not scene:
			scene = self.getDefaultScene()
		if self.scenes and scene in self.scenes:
			self.scenes[scene].addControlElement(name=name, callback = callback, drawingMethod = drawingMethod)

	def eventResizeView (self):
		if self.scenes:
			for scene in self.scenes:
				#TODO need more rules...
				position, size = self.scenesRules[scene]
				if position != (0,0):
					scene.setPosition(position)
				if size == (0,0):
					size = self.width(), self.height()
				scene.setSize(size)

				self.scenes[scene].eventResizeView()

	def eventMouseUp (self, event):
		hitlocation = getMouseHitLocation(merzView = self, event = event)
		layers = self.container.findSublayersContainingPoint((hitlocation['point']), onlyAcceptsHit = True)
		for scene in layers:
			if scene in self.scenes:
				layers.remove(scene)
				self.scenes[scene].eventMouseUp(event, layers, hitlocation['point'], hitlocation ['modifier'])

	def eventMouseDragged (self, event):
		delta = getMouseDeltaMoving(event)
		hitlocation = getMouseHitLocation(merzView = self, event = event)
		layers = self.container.findSublayersContainingPoint((hitlocation['point']), onlyAcceptsHit = True)
		for scene in layers:
			if scene in self.scenes:
				layers.remove(scene)
				self.scenes[scene].eventMouseDragged(event, layers, delta, hitlocation['point'])

	def eventScrollWheel (self, event):
		delta = getMouseDeltaMoving(event)
		momentumPhase = event.momentumPhase()
		hitlocation = getMouseHitLocation(merzView = self, event = event)
		layers = self.container.findSublayersContainingPoint((hitlocation['point']), onlyAcceptsHit = True)
		for scene in layers:
			if scene in self.scenes:
				self.scenes[scene].eventScrollWheel(event, delta, momentumPhase)

	def eventMouseDown (self, event):
		hitlocation = getMouseHitLocation(merzView = self, event = event)
		layers = self.container.findSublayersContainingPoint((hitlocation['point']), onlyAcceptsHit = True)
		for scene in layers:
			if scene in self.scenes:
				layers.remove(scene)
				self.scenes[scene].eventMouseDown(event, layers, hitlocation['point'], hitlocation ['modifier'])

	def eventKeyDown (self, sender, event):
		if self.scenes:
			for scene in self.scenes:
				self.scenes[scene].eventKeyDown(sender, event)

	# def eventMagnify (self, event):
	# 	self.matrix.eventMagnify(event)


	# dropOperationMap = dict(
	# 	none = AppKit.NSDragOperationNone,
	# 	copy = AppKit.NSDragOperationCopy,
	# 	link = AppKit.NSDragOperationLink,
	# 	generic = AppKit.NSDragOperationGeneric,
	# 	private = AppKit.NSDragOperationPrivate,
	# 	move = AppKit.NSDragOperationMove,
	# 	delete = AppKit.NSDragOperationDelete,
	# 	drag = AppKit.NSDragOperationEvery
	# )

class TDMerzMatrixView(vanilla.Group):

	def __init__(self, posSize, **kwargs):
		dropSettings = dict(
			pasteboardTypes = ["plist"],
			dropCandidateEnteredCallback = self.plistDestViewDropCandidateEnteredCallback,
			dropCandidateCallback = self.plistDestViewDropCandidateCallback,
			dropCandidateEndedCallback = self.plistDestViewDropCandidateEndedCallback,
			dropCandidateExitedCallback = self.plistDestViewDropCandidateExitedCallback,
			performDropCallback = self.plistDestViewPerformDropCallback
		)
		super().__init__(posSize = posSize, dropSettings = dropSettings)
		self.view = TDMerzMatrixScenery((0, 0, -0, -0), **kwargs) #TDMerzMatrixView((0,0,-0,-0), **kwargs)#TDMerzContainer((0,0,-0,-0), **kwargs)#

	def setupScene(self, **kwargs):
		return self.view.setupScene(**kwargs)

	def clearScene(self, **kwargs):
		self.view.clearScene(**kwargs)

	def reloadSceneItems(self, **kwargs):
		self.view.reloadSceneItems(**kwargs)

	def setSceneItems(self, **kwargs):
		self.view.setSceneItems(**kwargs)

	def setSelection(self, **kwargs):
		self.view.setSelection(**kwargs)

	def updateSceneItems(self, **kwargs):
		self.view.updateSceneItems(**kwargs)

	def removeSceneItems(self, **kwargs):
		self.view.removeSceneItems(**kwargs)

	def insertSceneItems(self, scene = None, items = None, index = None):
		self.view.insertSceneItems(scene = scene, items = items, index = index)

	def getSceneItems(self, scene = None):
		return self.view.getSceneItems(scene)

	def getSelectedSceneItems(self, scene = None):
		return self.view.getSelectedSceneItems(scene)

	def addControlElement(self, **kwargs):
		self.view.addControlElement(**kwargs)

	def setFocus(self, **kwargs):
		self.view.setFocus(**kwargs)

	def plistDestViewDropCandidateEnteredCallback (self, info):
		self.view.removeDraggedCursor()
		return dropOperationMap['copy']

	def plistDestViewDropCandidateCallback (self, info):
		location = info['draggingInfo'].draggingLocation()
		# Merz using NSPoint window coordinates, instead of vanilla.Group
		x, y = self.view.convertWindowCoordinateToViewCoordinate((location.x,location.y))
		hit = self.view.getMerzContainer().findSublayersIntersectedByRect((x, y, 1, 1),onlyAcceptsHit = True)

		for layer in hit:
			layerName = layer.getName()
			if layerName and layerName == 'contentLayer':
				scene = layer.getSuperlayer().getSuperlayer() # TODO there might be a problem
				wscene, hscene = scene.getSize()
				self.view.drawDraggedCursor(scene, layer)

				_x, _y = info['location']
				if _y > 0 and _y < 50:
					self.view.moveScene(scene, (0, 10))
				elif _y > hscene-50 and _y < hscene:
					self.view.moveScene(scene, (0, -10))
			elif layerName and layerName == 'scene':
				self.view.drawSelectedScene(layer)

		return dropOperationMap['copy']

	def plistDestViewDropCandidateExitedCallback (self, info):
		self.view.removeDraggedCursor()

	def plistDestViewDropCandidateEndedCallback (self, info):
		sender = info["sender"]
		source = info["source"]
		items = info["items"]
		if not source: return
		# print (info)
		items = sender.getDropItemValues(
			items,
			"plist"
		)
		location = info['draggingInfo'].draggingLocation()
		x, y = self.view.convertWindowCoordinateToViewCoordinate((location.x, location.y))
		hit = self.view.getMerzContainer().findSublayersIntersectedByRect((x, y, 1, 1), onlyAcceptsHit = True)
		# print ('HIT', hit)
		# for layer in hit:
		if len(hit) == 2:
			layer = hit[1] # ignore Scene if contentLayer hitted
			layerName = layer.getName()
			if layerName and layerName == 'contentLayer':
				scene = layer.getSuperlayer().getSuperlayer()  # TODO there might be a problem
				self.view.eventDrop(scene, dropInfo = dict(
															sourceScene = source.getSceneById(items[0]['idScene']),
				                                           # sourceView = (sender, source),
				                                           layerOver = self.view.getIndexOfLayer( scene, layer ),
				                                           indexes = list(items[0]['indexes'])))
		elif len(hit) == 1:
			layer = hit[0]
			layerName = layer.getName()
			if layerName and layerName == 'scene':
				self.view.eventDrop(layer, dropInfo = dict(sourceScene = source.getSceneById(items[0]['idScene']),
				                                           # sourceView = (sender, source),
				                                           layerOver = 'scene', indexes = list(items[0]['indexes'])))

		self.view.removeDraggedCursor()

	def plistDestViewPerformDropCallback (self, info):
		return True


class TDScenesSelector(object):
	def __init__(self):
		self.scenes = {}
		self.selectedScene = None

	def addScene(self, scene, view):
		if scene not in self.scenes:
			self.scenes[scene] = view

	# def addScene(self, scene):
	# 	if scene not in self.scenes:
	# 		self.scenes.append(scene)

	def setSelectedScene(self, scene):
		if scene in self.scenes:
			self.selectedScene = scene
			self.scenes[scene].setFocus(scene = scene, focused = True)
			for _scene, view in self.scenes.items():
				if _scene != scene:
					view.setFocus(scene = _scene, focused = False)

	def getSelectedScene(self):
		return self.selectedScene









