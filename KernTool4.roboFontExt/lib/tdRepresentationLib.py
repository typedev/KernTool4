
import merz
import importlib
import tdSpaceControl
importlib.reload(tdSpaceControl)
from tdSpaceControl import *

def drawSideMask (container, side, angle, backgroundColor, maskColor):
	def drawLeftPolygon (container, angle, backgroundColor):
		w, h = container.getSize()
		pathLayer = container.appendPathSublayer(
			fillColor = backgroundColor
		)
		pen = pathLayer.getPen()
		pen.moveTo((0, 0))
		pen.lineTo((0, h))
		pen.lineTo((w / 2 + italicShift(angle, h) / 2, h))
		pen.lineTo((w / 2 - italicShift(angle, h) / 2, 0))
		pen.closePath()
		return pathLayer

	def drawRightPolygon (container, angle, backgroundColor):
		w, h = container.getSize()
		pathLayer = container.appendPathSublayer(
			fillColor = backgroundColor
		)
		pen = pathLayer.getPen()
		pen.moveTo((w / 2 - italicShift(angle, h) / 2, 0))
		pen.lineTo((w / 2 + italicShift(angle, h) / 2, h))
		pen.lineTo((w, h))
		pen.lineTo((w, 0))
		pen.closePath()
		return pathLayer

	if side == SIDE_1:
		coloredMaskLayer = drawLeftPolygon(container, angle, backgroundColor)
		maskLayer = drawLeftPolygon(container, angle, maskColor)
		coloredMaskLayer.setOpacity(.7)

	if side == SIDE_2:
		coloredMaskLayer = drawRightPolygon(container, angle, backgroundColor)
		maskLayer = drawRightPolygon(container, angle, maskColor)
		coloredMaskLayer.setOpacity(.7)


def drawMarkGlyph (container, position, size=10, color=COLOR_KERN_VALUE_NEGATIVE):
	container.appendSymbolSublayer(
		name = 'mark',
		position = position,
		imageSettings = dict(
			name = 'star',
			size = (size, size),
			fillColor = color,
			pointCount = 8
		)
	)


def drawGlyphPath (container, glyph, xpos=None, color=(0, 0, 0, 1)):
	w, h = container.getSize()
	scale = pt2Scale(h / 2)
	yshift = h / 4 / scale
	if xpos == None and xpos != 0:
		xpos = -glyph.width / 2

	glyphLayer = container.appendPathSublayer(
		name = 'path.' + glyph.name,
		fillColor = color,
		position = ((w / scale / 2 + xpos), yshift),
		strokeColor = None,
		strokeWidth = 0,
	)
	glyphPath = glyph.getRepresentation("merz.CGPath")
	glyphLayer.setPath(glyphPath)
	glyphLayer.addScaleTransformation(scale)
	return glyphLayer


def drawCrossMark (container, position=None, size=None, color=COLOR_BLACK):
	w, h = container.getSize()
	if not position:
		position = (w / 2, h / 2)
	if not size:
		_size = (w / 4, h / 4)
	else:
		_size = (size, size)
	cross = container.appendSymbolSublayer(
		name = 'kernValue.cross',
		position = position,
		imageSettings = dict(
			name = "star",
			size = _size,
			fillColor = color,
			pointCount = 4,
			inner = .1,
			outer = 3,
			# strokeWidth = stroke,
			# strokeColor = strokeColor,
		)
	)
	cross.setRotation(45)


def drawGroupStack (container, font, groupName, pointSize = 10, langSet = None):
	if groupName not in font.groups.keys(): return
		# print ('group %s not found' % groupName)
		# return
	layerWidth, layerHeight = container.getSize()
	angle = font.info.italicAngle
	if not angle:
		angle = 0
	scale = .05
	hl = layerHeight
	scale = pt2Scale(hl / 2)
	yshift = hl / 4 / scale
	markColor = None
	klm, krm = 0, 0

	maskColor = (.4, .4, .6, .5)
	keyGlyph = None
	Xright, Xleft = 0, 0
	emptyGroup = False
	# groupName = groupsIdx[index]
	if len(font.groups[groupName]) != 0:
		keyGlyph = font[font.groups[groupName][0]]
		markColor = keyGlyph.markColor
		klm, krm = getMargins(keyGlyph)
		Xcenter = layerWidth / 2
		keyWidth = keyGlyph.width
		Xleft = Xcenter - keyWidth / 2 - 30
		Xright = Xleft + keyWidth - 30
	else:
		emptyGroup = True
	side = getDirection(groupName)

	if not markColor:
		markColor = (1, 1, 1, .7)
	with container.sublayerGroup():
		baselayer = container.appendBaseSublayer(
			name = 'base',
			position = (0, 0),
			size = (layerWidth, layerHeight),
			backgroundColor = (1, 1, 1, 1),  # markColor
			cornerRadius = 5
		)
		# b.setOpacity(.7)
		# baselayer.setCompositingMode("multiply")
		# x,y = layer.getPosition()
		# idx = sender.getIndexOfLayer(layer)
		# lbl = baselayer.appendTextLineSublayer(
		# 	position = (3, 8),
		# 	text = '%i' % (idx),
		# 	pointSize = 5,
		# 	fillColor = (0, 0, 0, 1),
		# )

		drawSideMask(baselayer, side, angle, backgroundColor = markColor, maskColor = maskColor)
		horizontalAlignment = 'center'
		if side == SIDE_1:
			horizontalAlignment = 'right'
			margintxt = str(krm)
		elif side == SIDE_2:
			horizontalAlignment = 'left'
			margintxt = str(klm)
		else:
			margintxt = ''

		title = baselayer.appendTextBoxSublayer(
			size = (layerWidth, layerHeight),
			position = (0, 0),
			fillColor = (0, 0, 0, 1),
			pointSize = pointSize,
			horizontalAlignment = horizontalAlignment,
			padding = (5, 3)
		)
		titletxt = getDisplayNameGroup(groupName)
		# if len(titletxt) > pointSize - 1:
		# 	title.setPointSize(pointSize * .8)
		if '.' in titletxt and not titletxt.startswith('.'):
			titletxt = '%s\n.%s' % (titletxt.split('.')[0], '.'.join(titletxt.split('.')[1:]))
		title.setText(titletxt)

		margintitle = baselayer.appendTextBoxSublayer(
			size = (layerWidth, 20),
			position = (0, 0),
			fillColor = (0, 0, 0, 1),
			pointSize = pointSize,
			horizontalAlignment = horizontalAlignment,
			padding = (5, 3),
			text = margintxt
		)
		gmax = None
		alpha = .2
		# if len(font.groups[groupName]) > 9:
		# 	gmax = 9

		markMarginsWarning = False
		markMarginsWarningXpos = layerWidth / 2
		if emptyGroup:
			drawCrossMark(baselayer, color = (1, 0, 0, 1))
		else:
			with baselayer.sublayerGroup():
				crosslang = False
				for idx, glyphName in enumerate(font.groups[groupName][0:gmax]):  # [0:gmax]
					if glyphName in font:
						glyph = font[glyphName]
						lm, rm = getMargins(glyph)
						a = alpha
						if len(font.groups[groupName]) > 5 and idx > 5:
							a = .07
						xpos = None
						if glyph.name == keyGlyph.name:
							a = 1
						if side == SIDE_1:
							xpos = Xright - glyph.width  # + italicShift(angle,400)
							markMarginsWarningXpos = layerWidth - 10
							if rm != krm:
								markMarginsWarning = True

						elif side == SIDE_2:
							xpos = Xleft - italicShift(angle, yshift)
							markMarginsWarningXpos = 10
							if lm != klm:
								markMarginsWarning = True
						# else:
						# 	xpos =  -glyph.width / 2
						if langSet and not crosslang:
							if not langSet.checkPairBaseScriptCompatibility(font, (keyGlyph.name, glyph.name)):
								crosslang = True

						drawGlyphPath(baselayer, glyph, xpos = xpos, color = (0, 0, 0, a))
					else:
						drawCrossMark(baselayer, (layerWidth / 2, 10), size = 12, color = (1, 0, 0, 1))

				if markMarginsWarning:
					drawMarkGlyph(baselayer, (markMarginsWarningXpos, 25), size = 12)
				if crosslang:
					drawCrossMark(baselayer, (markMarginsWarningXpos, 40), size = 10, color = COLOR_KERN_VALUE_NEGATIVE)
		baselayer.setMaskToFrame(True)


def drawGroupedGlyph (container, font, groupName, glyphname, pointSize = 10, langSet = None):
	layerGlyphWidth, layerGlyphHeight = container.getSize()

	hl = layerGlyphHeight
	scale = pt2Scale(hl / 2)
	yshift = hl / 4 / scale

	with container.sublayerGroup():
		markColor = (1, 1, 1, .7)

		baselayer = container.appendBaseSublayer(
			name = 'base',
			position = (0, 0),
			size = (layerGlyphWidth, layerGlyphHeight),
			backgroundColor = markColor,
			cornerRadius = 5
		)
		title = baselayer.appendTextBoxSublayer(
			size = (layerGlyphWidth, layerGlyphHeight),
			position = (0, 0),
			fillColor = (0, 0, 0, 1),
			pointSize = pointSize,
			horizontalAlignment = "center",
			padding = (3, 3)
		)
		displayname = glyphname
		if len(glyphname) > pointSize - 1:
			title.setPointSize(pointSize * .7)
			if '.' in glyphname and not glyphname.startswith('.'):
				displayname = '%s\n.%s' % (glyphname.split('.')[0], '.'.join(glyphname.split('.')[1:]))
		title.setText(displayname)
		try:
			keyGlyph = font[font.groups[groupName][0]]
			klm, krm = getMargins(keyGlyph)
			glyph = font[glyphname]  # font.groups[selectedGroup][index]
			lm, rm = getMargins(glyph)
			side = getDirection(groupName)
			markColor = glyph.markColor
			if not markColor:
				markColor = (1, 1, 1, .7)
			baselayer.setBackgroundColor(markColor)
			# print (keyGlyph.name, glyphname, side, groupName)
			drawGlyphPath(baselayer, glyph)  # , xpos = -glyph.width / 2

			markposX = 10
			if side == SIDE_1:
				markposX = layerGlyphWidth - markposX
				if rm != krm:
					drawMarkGlyph(baselayer, (layerGlyphWidth - 10, 10), size = 10)
			elif side == SIDE_2:
				if lm != klm:
					drawMarkGlyph(baselayer, (markposX, 10), size = 10)
			if langSet:
				# checking latin/cyrillic/greek etc
				if not langSet.checkPairBaseScriptCompatibility(font, (keyGlyph.name, glyphname)):
					drawCrossMark(baselayer, (markposX, 20),size = 8, color = (0, 0, 0, 1))
		except:
			drawCrossMark(baselayer, color = (1, 0, 0, 1))


		baselayer.setMaskToFrame(True)


def drawFontGlyph (containder, font, glyphname, pointSize  =10):
	# if not layer or not index and index != 0: return
	layerGlyphWidth, layerGlyphHeight = containder.getSize()

	hl = layerGlyphHeight
	scale = pt2Scale(hl / 2)
	yshift = hl / 4 / scale

	with containder.sublayerGroup():
		markColor = None
		glyph = font[glyphname]  # font.groups[selectedGroup][index]
		lm, rm = getMargins(glyph)

		markColor = glyph.markColor

		if not markColor:
			markColor = (1, 1, 1, .7)

		baselayer = containder.appendBaseSublayer(
			name = 'base',
			position = (0, 0),
			size = (layerGlyphWidth, layerGlyphHeight),
			backgroundColor = markColor,
			cornerRadius = 5
		)
		title = baselayer.appendTextBoxSublayer(
			size = (layerGlyphWidth, layerGlyphHeight),
			position = (0, 0),
			fillColor = (0, 0, 0, 1),
			pointSize = pointSize,
			horizontalAlignment = "center",
			padding = (3, 3)
		)
		if len(glyphname) > pointSize - 1:
			title.setPointSize(pointSize * .7)
			if '.' in glyphname and not glyphname.startswith('.'):
				glyphname = '%s\n.%s' % (glyph.name.split('.')[0], '.'.join(glyph.name.split('.')[1:]))
		title.setText(glyphname)

		drawGlyphPath(baselayer, glyph)  # , xpos = -glyph.width / 2

		baselayer.setMaskToFrame(True)


def drawKernPairListed( container, font, columns, hashKernDic, pairX, pointSize = 11):
	# print (pair, pair[0])
	pair = pairX[0]
	info = pairX[1]
	sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs = info
	l, r = pair
	_pair = pair
	if pair not in font.kerning: return
	layerWidth, layerHeight = container.getSize()
	pointSize1, pointSize2 = pointSize, pointSize
	# gl = False
	# gr = False
	kgl, kgr = l, r
	l = getDisplayNameGroup(l)
	if '@' in l:
		# kgl = hashKernDic.getKeyGlyphByGroupname(kgl)
		l = l.replace('@ ', '')
		# gl = True
	r = getDisplayNameGroup(r)
	if '@' in r:
		# kgr = hashKernDic.getKeyGlyphByGroupname(kgr)
		r = r.replace('@ ', '')
		# gr = True
	if len(l) > 15:
		pointSize1 = pointSize - 1.5
	if len(r) > 15:
		pointSize2 = pointSize - 1.5
	if not container.getSublayers():
		with container.sublayerGroup():
			baselayer = container.appendBaseSublayer(
				name = 'base',
				position = (0, 0),
				size = (layerWidth, layerHeight),
				backgroundColor = (0, 0, 0, 0),
				cornerRadius = 0
			)
			yoffset = pointSize  # layerWidth - 10#(self.pointSize / 2) - (layerHeight - self.pointSize)
			# baselayer.appendBaseSublayer(
			# 	position = (self.schema['buttonSide1']['xpos'] - 20, 0),
			# 	size = (self.schema['buttonSide1']['width']+5, layerHeight),
			# 	backgroundColor = (1, 1, 1, 0.6),
			# )

			if grouppedL:
				baselayer.appendTextLineSublayer(
					name = 'side1g',
					position = (columns['buttonSide1']['xpos'] - 15, 5),
					fillColor = (.3, .3, .7, 1),
					pointSize = pointSize1,
					text = '@',  # % ('@'),
					horizontalAlignment = "left",
					offset = (0, yoffset)  # -(self.pointSize/2)+2

				)
			baselayer.appendTextLineSublayer(
				name = 'side1',
				position = (columns['buttonSide1']['xpos'] - 3, 5),
				fillColor = (0, 0, 0, 1),
				pointSize = pointSize1,
				text = '%s' % (l),
				horizontalAlignment = "left",
				offset = (0, yoffset)  # -(self.pointSize/2)+2

			)
			# baselayer.appendBaseSublayer(
			# 	position = (self.schema['buttonSide2']['xpos'] - 20, 0),
			# 	size = (self.schema['buttonSide2']['width']+5, layerHeight),
			# 	backgroundColor = (1, 1, 1, 0.6),
			# )
			if grouppedR:
				baselayer.appendTextLineSublayer(
					name = 'side2',
					position = (columns['buttonSide2']['xpos'] - 15, 5),
					fillColor = (.3, .3, .7, 1),
					pointSize = pointSize2,
					text = '@',  # % (r),
					horizontalAlignment = "left",
					offset = (0, yoffset)
				)

			baselayer.appendTextLineSublayer(
				name = 'side2',
				position = (columns['buttonSide2']['xpos'] - 3, 5),
				fillColor = (0, 0, 0, 1),
				pointSize = pointSize2,
				text = '%s' % (r),
				horizontalAlignment = "left",
				offset = (0, yoffset)
			)
			# baselayer.appendBaseSublayer(
			# 	position = (self.schema['buttonValue']['xpos'] - 20, 0),
			# 	size = (self.schema['buttonValue']['width']+100, layerHeight),
			# 	backgroundColor = (1, 1, 1, 0.6),
			# )
			v = font.kerning[pair]
			if v < 0:
				colorvalue = (.6, .1, .1, 1)
			else:
				colorvalue = (.3, .5, .3, 1)
			# pair = researchPair(font, hashKernDic, (kgl, kgr))
			# if pair['exception']:
			# 	if pair['L_realName'] != pair['L_nameForKern'] and pair['R_realName'] == pair['R_nameForKern']:
			if note == 1:
				baselayer.appendSymbolSublayer(
					name = 'kernValue.exception',
					position = ((columns['buttonExcpt']['xpos'] - 7, 12)),
					imageSettings = dict(
						name = KernToolExceptionSymbolLeftSide,
						size = (23, 15),
						color = colorvalue,
					)
				)

			elif note == 2:
				baselayer.appendSymbolSublayer(
					name = 'kernValue.exception',
					position = ((columns['buttonExcpt']['xpos'] - 7, 12)),
					imageSettings = dict(
						name = KernToolExceptionSymbolRightSide,
						size = (23, 15),
						color = colorvalue,
					)
				)

			elif note == 3:
				baselayer.appendSymbolSublayer(
					name = 'kernValue.exception',
					position = ((columns['buttonExcpt']['xpos'] - 7, 12)),
					imageSettings = dict(
						name = KernToolExceptionSymbolOrphan,
						size = (23, 15),
						color = colorvalue,
					)
				)

			baselayer.appendTextLineSublayer(
				name = 'value',
				position = (columns['buttonValue']['xpos'] + 15, 5),
				fillColor = colorvalue,
				pointSize = pointSize,
				text = '%i' % (v),
				horizontalAlignment = "right",
				offset = (0, yoffset)
			)
			# print (_pair)
			# if not hashKernDic.checkPairLanguageCompatibilityGroupped(_pair, level = 1):
			if langs == 1:
				drawCrossMark(container, position = (columns['buttonLangs']['xpos'] - 10, 9), size = 10, color = (.6, .1, .1, 1) )
			# elif not hashKernDic.checkPairLanguageCompatibilityGroupped(_pair, level = 2):
			if langs == 2:
				drawCrossMark(container, position = (columns['buttonLangs']['xpos'] - 10, 9), size = 10, color = (.3, .5, .3, 1) )

			baselayer.appendLineSublayer(
				name = 'baseline',
				startPoint = (0, 0),
				endPoint = (layerWidth, 0),
				strokeWidth = 1,
				strokeColor = (.9, .9, .9, .6)
			)

#
# def drawKernPairListed2( container, font, columns, hashKernDic, pairX, pointSize = 11):
# 	# print (pair, pair[0])
# 	pair = pairX[0]
# 	info = pairX[1]
# 	sortL, sortR, grouppedL, grouppedR, v, note, keyGlyphL, keyGlyphR, langs = info
# 	l, r = pair
# 	_pair = pair
# 	if pair not in font.kerning: return
# 	layerWidth, layerHeight = container.getSize()
# 	pointSize1, pointSize2 = pointSize, pointSize
# 	gl = False
# 	gr = False
# 	kgl, kgr = l, r
# 	l = getDisplayNameGroup(l)
# 	if '@' in l:
# 		kgl = hashKernDic.getKeyGlyphByGroupname(kgl)
# 		l = l.replace('@ ', '')
# 		gl = True
# 	r = getDisplayNameGroup(r)
# 	if '@' in r:
# 		kgr = hashKernDic.getKeyGlyphByGroupname(kgr)
# 		r = r.replace('@ ', '')
# 		gr = True
# 	if len(l) > 15:
# 		pointSize1 = pointSize - 1.5
# 	if len(r) > 15:
# 		pointSize2 = pointSize - 1.5
# 	if not container.getSublayers():
# 		with container.sublayerGroup():
# 			baselayer = container.appendBaseSublayer(
# 				name = 'base',
# 				position = (0, 0),
# 				size = (layerWidth, layerHeight),
# 				backgroundColor = (0, 0, 0, 0),
# 				cornerRadius = 0
# 			)
# 			yoffset = pointSize  # layerWidth - 10#(self.pointSize / 2) - (layerHeight - self.pointSize)
# 			# baselayer.appendBaseSublayer(
# 			# 	position = (self.schema['buttonSide1']['xpos'] - 20, 0),
# 			# 	size = (self.schema['buttonSide1']['width']+5, layerHeight),
# 			# 	backgroundColor = (1, 1, 1, 0.6),
# 			# )
#
# 			if gl:
# 				baselayer.appendTextLineSublayer(
# 					name = 'side1g',
# 					position = (columns['buttonSide1']['xpos'] - 15, 5),
# 					fillColor = (.3, .3, .7, 1),
# 					pointSize = pointSize1,
# 					text = '@',  # % ('@'),
# 					horizontalAlignment = "left",
# 					offset = (0, yoffset)  # -(self.pointSize/2)+2
#
# 				)
# 			baselayer.appendTextLineSublayer(
# 				name = 'side1',
# 				position = (columns['buttonSide1']['xpos'] - 3, 5),
# 				fillColor = (0, 0, 0, 1),
# 				pointSize = pointSize1,
# 				text = '%s' % (l),
# 				horizontalAlignment = "left",
# 				offset = (0, yoffset)  # -(self.pointSize/2)+2
#
# 			)
# 			# baselayer.appendBaseSublayer(
# 			# 	position = (self.schema['buttonSide2']['xpos'] - 20, 0),
# 			# 	size = (self.schema['buttonSide2']['width']+5, layerHeight),
# 			# 	backgroundColor = (1, 1, 1, 0.6),
# 			# )
# 			if gr:
# 				baselayer.appendTextLineSublayer(
# 					name = 'side2',
# 					position = (columns['buttonSide2']['xpos'] - 15, 5),
# 					fillColor = (.3, .3, .7, 1),
# 					pointSize = pointSize2,
# 					text = '@',  # % (r),
# 					horizontalAlignment = "left",
# 					offset = (0, yoffset)
# 				)
#
# 			baselayer.appendTextLineSublayer(
# 				name = 'side2',
# 				position = (columns['buttonSide2']['xpos'] - 3, 5),
# 				fillColor = (0, 0, 0, 1),
# 				pointSize = pointSize2,
# 				text = '%s' % (r),
# 				horizontalAlignment = "left",
# 				offset = (0, yoffset)
# 			)
# 			# baselayer.appendBaseSublayer(
# 			# 	position = (self.schema['buttonValue']['xpos'] - 20, 0),
# 			# 	size = (self.schema['buttonValue']['width']+100, layerHeight),
# 			# 	backgroundColor = (1, 1, 1, 0.6),
# 			# )
# 			v = font.kerning[pair]
# 			if v < 0:
# 				colorvalue = (.6, 0.1, 0.1, 1)
# 			else:
# 				colorvalue = (0.1, 0.6, .1, 1)
# 			pair = researchPair(font, hashKernDic, (kgl, kgr))
# 			if pair['exception']:
# 				if pair['L_realName'] != pair['L_nameForKern'] and pair['R_realName'] == pair['R_nameForKern']:
# 					baselayer.appendSymbolSublayer(
# 						name = 'kernValue.exception',
# 						position = ((columns['buttonExcpt']['xpos'] - 5, 12)),
# 						imageSettings = dict(
# 							name = KernToolExceptionSymbolLeftSide,
# 							size = (23, 15),
# 							color = colorvalue,
# 						)
# 					)
#
# 				elif pair['R_realName'] != pair['R_nameForKern'] and pair['L_realName'] == pair['L_nameForKern']:
# 					baselayer.appendSymbolSublayer(
# 						name = 'kernValue.exception',
# 						position = ((columns['buttonExcpt']['xpos'] - 5, 12)),
# 						imageSettings = dict(
# 							name = KernToolExceptionSymbolRightSide,
# 							size = (23, 15),
# 							color = colorvalue,
# 						)
# 					)
#
# 				else:
# 					baselayer.appendSymbolSublayer(
# 						name = 'kernValue.exception',
# 						position = ((columns['buttonExcpt']['xpos'] - 5, 12)),
# 						imageSettings = dict(
# 							name = KernToolExceptionSymbolOrphan,
# 							size = (23, 15),
# 							color = colorvalue,
# 						)
# 					)
#
# 			baselayer.appendTextLineSublayer(
# 				name = 'value',
# 				position = (columns['buttonValue']['xpos'] + 15, 5),
# 				fillColor = colorvalue,
# 				pointSize = pointSize,
# 				text = '%i' % (v),
# 				horizontalAlignment = "right",
# 				offset = (0, yoffset)
# 			)
# 			# print (_pair)
# 			if not hashKernDic.checkPairLanguageCompatibilityGroupped(_pair, level = 1):
# 				drawCrossMark(container, position = (columns['buttonLangs']['xpos'] - 10, 9), size = 10, color = (.6, 0.1, 0.1, 1) )
# 			elif not hashKernDic.checkPairLanguageCompatibilityGroupped(_pair, level = 2):
# 				drawCrossMark(container, position = (columns['buttonLangs']['xpos'] - 10, 9), size = 10, color = (0.1, 0.6, .1, 1) )
#
# 			baselayer.appendLineSublayer(
# 				name = 'baseline',
# 				startPoint = (0, 0),
# 				endPoint = (layerWidth, 0),
# 				strokeWidth = 1,
# 				strokeColor = (.9, .9, .9, .6)
# 			)