from fontParts.world import *

import vanilla
import importlib

import tdMerzMatrix
importlib.reload(tdMerzMatrix)
from tdMerzMatrix import *

import tdRepresentationLib
importlib.reload(tdRepresentationLib)
from tdRepresentationLib import *

class TDTestView(object):  # , WindowController
	def __init__ (self):
		print ('TDTestView')
		self.w = vanilla.Window((1242, 400), minSize = (200, 100), title = 'test')

		# self.w.fontView = TDMerzMatrixView('auto',
		#                                    # dropSettings = dropSettings,
		#                                    delegate = self
		#                                    )
		self.w.groupView = TDMerzMatrixView('auto',
		                                    # dropSettings = dropSettings,
		                                    delegate = self
		                                    )
		rules = [
			"H:|[groupView]|", # -space-[groupView(==fontView)]
			"V:|[groupView]|",
			# "V:|[groupView]|"
		]
		metrics = {
			"border": 1,
			"space": 1
		}
		self.w.addAutoPosSizeRules(rules, metrics)

		# s1 = self.w.fontView.setupScene(
		# 	# position = (20,20), size = (300,400),
		# 	layerWillDrawCallback = self.layerFontWillDrawCallback,
		# 	# selectLayerCallback = self.fontViewSelectionCallback,
		# 	# dropCallback = self.dropContentCallback,
		# 	clearHash = True,
		# 	# dropStyle = DROP_STYLE_SCENE,
		# 	elementSize = (1000, 65),
		# 	elementMargins = (2, 2),
		# 	backgroundColor = (.5, .6, .7, 1),
		# 	selectionColor = (0, 0, 1, .5),
		# 	controlsColor = (.2, .3, .4, 1),
		# 	cornerRadius = 5,
		# 	focusColor = (1, 1, 1, .5)
		# )

		s2 = self.w.groupView.setupScene(
			# position = (20,20), size = (400,400),
			layerWillDrawCallback = self.layerFontWillDrawCallback,
			# selectLayerCallback = self.fontViewSelectionCallback,
			# dropCallback = self.dropContentCallback,
			clearHash = True,
			# dropStyle = DROP_STYLE_SCENE,
			elementSize = (65, 65),
			elementMargins = (2, 2),
			backgroundColor = (.5, .6, .7, 1),
			selectionColor = (0, 0, 1, .5),
			controlsColor = (.2, .3, .4, 1),
			cornerRadius = 5,
			focusColor = (1, 1, 1, .5)
		)

		self.font = CurrentFont()
		self.kern = self.font.kerning.items()

		self.w.open()
		# self.w.fontView.setSceneItems(items = [glyph.name for glyph in self.font], animated = 'left')
		self.w.groupView.setSceneItems(items = [glyph for glyph in self.font.glyphOrder], animated = 'bottom') #, animated = 'bottom'


	def layerFontWillDrawCallback (self, sender, info):
		layer = info['layer']
		index = info['index']
		glyphname = info['item']
		if not layer.getSublayers():
			drawFontGlyph(layer, self.font, glyphname)
		# with layer.sublayerGroup():
		# sender.documentLayer.clearSublayers()
		# with sender.documentLayer.sublayerGroup():
		# layer.clearSublayers()

		# if not layer.getSublayers():
		# 	drawFontGlyph(layer, CurrentFont(), )
		# 	b = layer.getSublayer('base')
		# 	ytxt = self.layerHeight
		# # (l,r),v = self.kern[index]
		#
		# # if not b:
		# 	markColor = None
		# 	if self.mode == 'glyphs':
		# 		glyph = self.font[self.font.glyphOrder[index]]
		# 		# markColor = (1, 1, 1, 1)
		# 		markColor = glyph.markColor
		#
		# 	elif self.mode == 'kern':
		# 		if index < len(self.kern):
		# 			(l, r), v = self.kern[index]
		# 		else:
		# 			print('wrong index', index, len(self.kern), layer)
		# 			return
		# 	# else:
		# 	# 	(r, g, b, a) = markColor
		# 	# 	markColor = (r,g,b,.7)
		# 	if not markColor:
		# 		markColor = (1, 1, 1, .7)
		# 	with layer.sublayerGroup():
		# 		b = layer.appendBaseSublayer(
		# 			name = 'base',
		# 			position = (0, 0),
		# 			size = (self.layerWidth, self.layerHeight),
		# 			backgroundColor = markColor,
		# 			cornerRadius = 3
		# 		)
		# 		# b.setOpacity(.7)
		# 		# b.setCompositingMode("multiply")
		# 		# x,y = layer.getPosition()
		# 		idx = sender.getIndexOfLayer(layer)
		# 		lbl = b.appendTextLineSublayer(
		# 			position = (3, 8),
		# 			text = '%i' % (idx),
		# 			pointSize = 5,
		# 			fillColor = (0, 0, 0, 1),
		#
		# 		)
		#
		# 		if self.mode == 'glyphs':
		# 			title = b.appendTextBoxSublayer(
		# 				# font = 'Menlo',
		# 				# name = 'side1',
		# 				size = (self.layerWidth, self.layerHeight),
		# 				position = (0, 0),
		# 				fillColor = (0, 0, 0, 1),
		# 				pointSize = self.pointSize,
		# 				# text = '%i %s %s %i' % (c, l, r, v),
		# 				# text = glyph.name,
		# 				horizontalAlignment = "center",
		# 				padding = (3, 3)
		# 				# offset = (0, yoffset) # -(self.pointSize/2)+2
		# 			)
		# 			glyphname = glyph.name
		# 			if len(glyphname) > self.pointSize - 1:
		# 				title.setPointSize(self.pointSize * .7)
		# 				if '.' in glyphname:
		# 					glyphname = '%s\n.%s' % (glyph.name.split('.')[0], '.'.join(glyph.name.split('.')[1:]))
		#
		# 			title.setText(glyphname)
		#
		# 			glyphLayer = b.appendPathSublayer(
		# 				name = 'path.' + glyph.name,
		# 				fillColor = (0, 0, 0, 1),
		# 				position = ((self.layerWidth / scale - (glyph.width)) / 2, 400),
		# 				strokeColor = None,
		# 				strokeWidth = 0,
		# 			)
		# 			glyphPath = glyph.getRepresentation("merz.CGPath")
		# 			glyphLayer.setPath(glyphPath)
		# 			glyphLayer.addScaleTransformation(scale)
		# 			b.setMaskToFrame(True)


	def selectLayerCallback (self, sender, info):
		layer = info['layer']
		index = info['index']

		print('selected', sender, layer, index, layer.getPosition())  # self.w.view.getIdLayer(layers[0]) , self.font.glyphOrder[index]
		print('all selection', sender, sender.selection)

	# this section is required for Merz
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
		sender.eventKeyDown(event)


def main ():
	TDTestView()


if __name__ == "__main__":
	main()
