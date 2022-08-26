from fontParts.world import *

import vanilla
import importlib
from mojo.events import addObserver, removeObserver

import tdMerzMatrix
importlib.reload(tdMerzMatrix)
from tdMerzMatrix import *

import tdRepresentationLib
importlib.reload(tdRepresentationLib)
from tdRepresentationLib import *

import tdGlyphparser

class TDTestView(object):  # , WindowController
	def __init__ (self):
		print ('TDTestView')
		self.w = vanilla.Window((1242, 600), minSize = (200, 100), title = 'test')

		self.w.itemsView = TDMerzMatrixView('auto',
		                                    # dropSettings = dropSettings,
		                                    delegate = self
		                                    )
		rules = [
			"H:|[itemsView]|", # -space-[groupView(==fontView)]
			"V:|[itemsView]|",
			# "V:|[groupView]|"
		]
		metrics = {
			"border": 1,
			"space": 1
		}
		self.w.addAutoPosSizeRules(rules, metrics)

		self.glyphsPointSize = 72
		s2 = self.w.itemsView.setupScene(
			# position = (20,20), size = (400,400),
			layerWillDrawCallback = self.layerFontWillDrawCallback,
			selectLayerCallback = self.selectLayerCallback,
			# dropCallback = self.dropContentCallback,
			clearHash = True,
			# dropStyle = DROP_STYLE_SCENE,
			elementSize = (0, 0),
			elementMargins = (0, 0),
			backgroundColor = (1, 1, 1, 1),
			selectionColor = (0, 0, 0, 0),
			selectedBorderColor = (0,0,1,.1),
			controlsColor = (.2, .3, .4, 1),
			cornerRadius = 0,
			focusColor = (1, 1, 1, .5),
			# fitWidth = False
		)

		self.font = CurrentFont()
		self.w.bind('close', self.windowCloseCallback)
		addObserver(self, "drawGlyphsLineObserver", "currentGlyphChanged")
		self.w.open()
		# self.w.fontView.setSceneItems(items = [glyph.name for glyph in self.font], animated = 'left')
		self.showGlyphsLine()


	def layerFontWillDrawCallback (self, sender, info):
		layer = info['layer']
		index = info['index']
		# glyphname = info['item']
		# if not layer.getSublayers():
		# 	drawFontGlyph(layer, self.font, glyphname)
		glyphline = info['item']
		# if not layer.getSublayers():
		self.drawGlyphsLine(layer, glyphline)
		# 	print('draw layer', layer, glyphline)
		# else:
		# 	print('just show layer', layer, glyphline)
			# for g in glyphline:
			# 	drawFontGlyph(layer, self.font, g.name)

	def drawGlyphBox (self, container, glyph, xpos, backgroundColor = (0,0,0,0), color=(0, 0, 0, 1)):
		w, h = container.getSize()
		scale = pt2Scale(h / 2)
		yshift = h / 3 / scale
		wbox = glyph.width * scale

		baselayer = container.appendBaseSublayer(
			name = 'glyphbox.%s' % glyph.name,
			position = (xpos, 0),
			size = (wbox, h),
			acceptsHit = True,
			backgroundColor = backgroundColor,
		)

		glyphLayer = baselayer.appendPathSublayer(
			name = 'path.%s' % glyph.name,
			fillColor = color,
			position = (0, yshift),
			strokeColor = None,
			strokeWidth = 0,
		)
		glyphPath = glyph.getRepresentation("merz.CGPath")
		glyphLayer.setPath(glyphPath)
		glyphLayer.addScaleTransformation(scale)

		leftMargin, rightMargin = getMargins(glyph)
		# itshift = italicShift(italicAngle, yctrl)

		baselayer.appendTextLineSublayer(
			name = 'margin.left',
			# font = fontname,
			position = (0, 10),  # - ygap),
			fillColor = (0,0,0,1),
			pointSize = 8,
			text = LEFT_SYMBOL_MARGIN + str(leftMargin),
			horizontalAlignment = "left",
			verticalAlignment = 'bottom',
			# offset = (0, -4),
			# visible = self.showMargins,
		)
		baselayer.appendTextLineSublayer(
			name = 'margin.right',
			# font = fontname,
			position = (wbox, 10),  # - hctrl - ygap), #glyph.width
			fillColor = (0,0,0,1),
			pointSize = 8,
			text = str(rightMargin) + RIGHT_SYMBOL_MARGIN,
			horizontalAlignment = "right",
			verticalAlignment = 'top',
			# offset = (0, 4),
			# visible = self.showMargins,
		)
		baselayer.appendTextBoxSublayer(
			name = 'glyphTitle',
			position = (0, h / 2),
			size = (wbox, h / 2),  # glyph.width * self.scaleFactor
			backgroundColor = (0, 0, 0, 0),
			# font = self.displayFontName,
			text = glyph.name + TITLE_SYMBOL,
			pointSize = 8,  # + 2,
			fillColor = (0,0,0,1),
			horizontalAlignment = 'center',
			# visible = self.showMargins,
			padding = (1, 3)
		)

		return wbox

	def drawGlyphsLine(self, container, glyphs):
		layerGlyphWidth, layerGlyphHeight = container.getSize()
		if not container.getSublayer('base'):

			with container.sublayerGroup():
				baselayer = container.appendBaseSublayer(
					name = 'base',
					position = (0, 0),
					size = (layerGlyphWidth, layerGlyphHeight),
					backgroundColor = (1,1,1,1),
					# cornerRadius = 5
				)
				markColor = None
				xpos = 0
				for glyph in glyphs:
					# lm, rm = getMargins(glyph)
					markColor = glyph.markColor
					if not markColor:
						markColor = (1, 1, 1, .7)
					wbox = self.drawGlyphBox(baselayer, glyph, xpos) #, backgroundColor = markColor
					xpos += wbox
				baselayer.setSize((xpos,layerGlyphHeight))
				# container.setSize((xpos,layerGlyphHeight))
				# print(baselayer, xpos, layerGlyphHeight)
		else:
			baselayer = container.getSublayer('base')
			print('just need redraw', baselayer) # , baselayer.getSublayers()
			for glyph in glyphs:
				if glyph != self.font[glyph.name]:
					print('changes detect', glyph.name)

	def drawGlyphsLineObserver(self, info):
		self.w.itemsView.updateSceneItems(cleanBefore = False)
		print ('drawGlyphsLineObserver',info)

	def showGlyphsLine(self):
		txt = 'Приведенный состав алфавита отражает\nего состояние\nдо реформы\n1917–18 г.г.\nи включает 35 знаков,\nчетыре из которых\nне сохранились\nв современном русском\nалфавите (выделены красным).\nБуквы Ё, Й использовались в языке, хотя и не считались отдельными буквами алфавита.\nЗеленым выделены знаки, представленные\nв лексикографических источниках.'.split('\n')
		idx = 0
		glyphslines = []
		scale = pt2Scale(self.glyphsPointSize * 2 )
		h = scale2pt( scale )
		print (h)
		listw = []
		for line in txt:
			glyphslinenames = tdGlyphparser.translateText(CurrentFont(), line)
			glyphsline = []
			wline = 0
			for name in glyphslinenames:
				glyph = self.font[name]
				glyphsline.append(glyph)
				wline += (glyph.width * scale / 2)
			print(wline, glyphslinenames)
			listw.append(wline)
			glyphslines.append(glyphsline)
		ew = max(listw)
		# print()
		# print(glyphslines)
		self.w.itemsView.setSceneItems(items = glyphslines, animated = 'bottom', elementWidth = ew, elementHeight = h) #, animated = 'bottom'
		# self.w.itemsView.updateSceneItems()




	def selectLayerCallback (self, sender, info):
		layer = info['layer']
		index = info['index']
		item = info['item']
		hits = info['hits']

		print('selected', sender, layer, index, layer.getPosition(), item, hits)  # self.w.view.getIdLayer(layers[0]) , self.font.glyphOrder[index]
		print('all selection', sender, sender.getSelectedSceneItems())

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

	def windowCloseCallback(self, sender):
		removeObserver(self, 'currentGlyphChanged')
		self.w.itemsView.clearScene()


def main ():
	TDTestView()


if __name__ == "__main__":
	main()
