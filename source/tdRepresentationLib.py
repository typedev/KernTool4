
import merz
import importlib
import tdSpaceControl
importlib.reload(tdSpaceControl)
from tdSpaceControl import *


def tdGroupSymbolImageFactory( size, color = None, **kwargs ):
	w, h = 15, 15
	# if not color:
	# 	r, g, b, a = (0,0,0,1)
	# else:
	# 	r, g, b, a = color
	# x, y = position
	x,y = 0,0
	# y = 5
	bot = NSImageDrawingTools((w,h))
	bot.fill(1,1,1,1)
	bot.strokeWidth(2)
	bot.stroke(*color)
	# bot.text('@',(x,y))
	# width -= 5
	# height -= 5
	# _w = width / 2
	# _h = height / 2
	# stepX = (width / 2) / 3
	# stepY = (height / 2) / 3
	# stepX = 3
	# stepY = 3
	# for i in range(0,3):
	bot.roundedRect(x, y, w, h, 2)
	# x += stepX
	# y += stepY
	image = bot.getImage()
	return image

TDPairsListGroupSymbol = "com.typedev.PairsListGroupSymbol"
merz.SymbolImageVendor.registerImageFactory(TDPairsListGroupSymbol, tdGroupSymbolImageFactory)

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
	keyGlyphName = None
	Xright, Xleft = 0, 0
	emptyGroup = False
	Xcenter = layerWidth / 2
	# groupName = groupsIdx[index]
	if len(font.groups[groupName]) != 0:
		if font.groups[groupName][0] in font:
			keyGlyph = font[font.groups[groupName][0]]
			markColor = keyGlyph.markColor
			keyGlyphName = keyGlyph.name
			klm, krm = getMargins(keyGlyph)
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
						if glyph.name == keyGlyphName:
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
						if langSet and not crosslang and keyGlyphName:
							if not langSet.checkPairBaseScriptCompatibility(font, (keyGlyphName, glyph.name)):
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


def drawKernPairListed( container, font, columns, hashKernDic, pairInfo, mode = None, pointSize = 11):
	pair = pairInfo[0]
	info = pairInfo[1]
	sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs, hasError = info
	# print (info)
	l, r = pair
	_pair = pair
	if pair not in font.kerning: return
	layerWidth, layerHeight = container.getSize()
	pointSize1, pointSize2 = pointSize+3, pointSize
	l = sortL
	r = sortR

	btnWidth = 0
	btnXpos = 0
	btnValue = False
	layersXpos = []
	layersWidth = []
	for idx, button in enumerate(columns):
		btnWidth = int(round(layerWidth * (button['widthperсent'] / 100), 0) )
		layersWidth.append(btnWidth)
		layersXpos.append(btnXpos)
		btnXpos += btnWidth # + 5

	if not container.getSublayers():
		with container.sublayerGroup():
			baselayer = container.appendBaseSublayer(
				name = 'base',
				position = (0, 0),
				size = (layerWidth, layerHeight),
				backgroundColor = (0, 0, 0, 0),
				cornerRadius = 0
			)
			yoffset = pointSize

			if grouppedL:
				baselayer.appendTextLineSublayer(
					name = 'side1g',
					# font = 'Apple Symbols',
					position = (layersXpos[0], 5), # - 15
					fillColor = (.3, .3, .7, .6),
					pointSize = pointSize1,
					text = '@',  # % ('@'), 􀚓 􀚈 ◧
					horizontalAlignment = "left",
					offset = (0, yoffset+3)  # -(self.pointSize/2)+2
				)

			baselayer.appendTextLineSublayer(
				name = 'side1',
				position = (layersXpos[0] + 15 , 5),
				fillColor = (0, 0, 0, 1),
				pointSize = pointSize2,
				text = l,
				horizontalAlignment = "left",
				offset = (0, yoffset)  # -(self.pointSize/2)+2
			)

			if grouppedR:
				baselayer.appendTextLineSublayer(
					name = 'side2g',
					# font = 'Apple Symbols',
					position = (layersXpos[1], 5), #  - 15
					fillColor = (.3, .3, .7, .6),
					pointSize = pointSize1,
					text = '@',  # % (r), 􀚔 􀚈 ◨
					horizontalAlignment = "left",
					offset = (0, yoffset+3),
					# backgroundColor = (1,1,1,.8)
				)

			baselayer.appendTextLineSublayer(
				name = 'side2',
				position = (layersXpos[1] + 15, 5),
				fillColor = (0, 0, 0, 1),
				pointSize = pointSize2,
				text = r,
				horizontalAlignment = "left",
				offset = (0, yoffset),
				# backgroundColor = (1, 1, 1, .8)
			)

			v = font.kerning[pair]
			if v < 0:
				colorvalue = (.6, .1, .1, 1)
			else:
				colorvalue = (.3, .5, .3, 1)
			if note == 1:
				baselayer.appendSymbolSublayer(
					name = 'kernValue.exception',
					position = ((layersXpos[3] + layersWidth[3]/2, 12)), # - 7
					imageSettings = dict(
						name = KernToolExceptionSymbolLeftSide,
						size = (23, 15),
						color = colorvalue,
					)
				)
			elif note == 2:
				baselayer.appendSymbolSublayer(
					name = 'kernValue.exception',
					position = ((layersXpos[3] + layersWidth[3]/2 , 12)),
					imageSettings = dict(
						name = KernToolExceptionSymbolRightSide,
						size = (23, 15),
						color = colorvalue,
					)
				)
			elif note == 3:
				baselayer.appendSymbolSublayer(
					name = 'kernValue.exception',
					position = ((layersXpos[3] + layersWidth[3]/2 , 12)),
					imageSettings = dict(
						name = KernToolExceptionSymbolOrphan,
						size = (23, 15),
						color = colorvalue,
					)
				)

			baselayer.appendTextLineSublayer(
				name = 'value',
				position = (layersXpos[3] - 12, 5), #  + 15
				fillColor = colorvalue,
				pointSize = pointSize,
				text = '%i' % v,
				horizontalAlignment = "right",
				offset = (0, yoffset),
				# backgroundColor = (1, 1, 1, .8)
			)
			# if langs == 1:
			# 	drawCrossMark(baselayer, position = (layersXpos[4] + layersWidth[4]/2, 9), size = 10, color = (.6, .1, .1, 1) ) #  - 10
			# if langs == 2:
			# 	drawCrossMark(baselayer, position = (layersXpos[4] + layersWidth[4]/2, 9), size = 10, color = (.3, .5, .3, 1) )
			if langs == 1:
				langscolor = (.6, .1, .1, 1)
			elif langs == 2:
				langscolor = (.3, .5, .3, 1)
			if langs:
				baselayer.appendTextLineSublayer(
					name = 'kernValue.cross',
					# font = 'Apple Symbols',
					position = (layersXpos[4] + layersWidth[4] / 2, 5),  # +
					fillColor = langscolor,
					pointSize = pointSize1,
					text = '􀆪', # 􀆪 ⁕
					horizontalAlignment = "center",
					offset = (2, yoffset+3),
					# backgroundColor = (1, 1, 1, .8)
				)

			if hasError:
				baselayer.appendTextLineSublayer(
					name = 'errormark',
					# font = 'Apple Symbols',
					position = (layersXpos[5] + layersWidth[5] / 2, 5),  # + 15
					fillColor = (.6, .1, .1, 1),
					pointSize = pointSize1,
					text = 'X', # 􀇿 ⊗ X
					horizontalAlignment = "left",
					offset = (-1, yoffset+2),
					# backgroundColor = (1, 1, 1, .8)
				)

			baselayer.appendLineSublayer(
				name = 'baseline',
				startPoint = (0, 0),
				endPoint = (layerWidth, 0),
				strokeWidth = 1,
				strokeColor = (.9, .9, .9, .6)
			)
	with container.sublayerGroup():
		base = container.getSublayers()[0] #('base')
		# bw, bh = base.getSize()
		if base:
			lt = base.getSublayer('side1')
			# if mode == 2: # DRAWING_BASE_MODE_RESIZE

			# w, h = lt.getTextSize()
			# if w > layersWidth[0] - 25:
			# 	lt.setPointSize(pointSize - 2)
			# else:
			# 	lt.setPointSize(pointSize)
			x , y = lt.getPosition()
			if x != layersXpos[0] + 15:
				lt.setPosition((layersXpos[0] + 15, 5))

			rt = base.getSublayer('side2')
			# if mode == 2: # DRAWING_BASE_MODE_RESIZE

			# w, h = rt.getTextSize()
			# if w > layersWidth[1] - 25:
			# 	rt.setPointSize(pointSize - 2)
			# else:
			# 	rt.setPointSize(pointSize)
			x, y = rt.getPosition()
			if x != layersXpos[1] + 15:
				rt.setPosition((layersXpos[1] + 15, 5))

			# if mode == 2: # DRAWING_BASE_MODE_RESIZE

			baseline = base.getSublayer('baseline')
			x, y = baseline.getEndPoint()
			if x != layerWidth:
				baseline.setEndPoint((layerWidth,0))

			ltg = base.getSublayer('side1g')
			if ltg:
				x, y = ltg.getPosition()
				if x != layersXpos[0]:
					ltg.setPosition((layersXpos[0] , 5))

			rtg = base.getSublayer('side2g')
			if rtg:
				x, y = rtg.getPosition()
				if x != layersXpos[1]:
					rtg.setPosition((layersXpos[1] , 5))

			vt = base.getSublayer('value')
			x, y = vt.getPosition()
			if x != layersXpos[3] - 12:
				vt.setPosition((layersXpos[3] - 12, 5))

			et = base.getSublayer('kernValue.exception')
			if et:
				x, y = et.getPosition()
				if x != layersXpos[3] + layersWidth[3]/2:
					et.setPosition((layersXpos[3] + layersWidth[3]/2 , 12))

			lnt = base.getSublayer('kernValue.cross')
			if lnt:
				x, y = lnt.getPosition()
				if x != layersXpos[4] + layersWidth[4] / 2 : #+ layersWidth[4]/3
					lnt.setPosition((layersXpos[4] + layersWidth[4] / 2, 5)) # 9

			err = base.getSublayer('errormark')
			if err:
				x, y = err.getPosition()
				if x != layersXpos[5] + layersWidth[5] / 2:
					err.setPosition((layersXpos[5] + layersWidth[5] / 2, 5))


def drawKernListSortButton (container, nameButton, selectedButton, direction, schemaButtons):
	if not container: return
	buttonLayer = container.getSublayer(nameButton)
	(layerWidth, layerHeight) = container.getSize()
	ypos = layerHeight - 20
	btnWidth = 0
	btnXpos = 20
	btnValue = False
	for idx, button in enumerate(schemaButtons):
		btnWidth = (layerWidth - 60) * (button['widthperсent'] / 100)
		if button['name'] == nameButton:
			btnValue = button['value']
			break
		else:
			btnXpos += btnWidth + 5

	if not buttonLayer:
		if btnValue:
			colorBack = (.3, .3, .3, .8)
			colorSelect = (.8, .8, .8, .8)
		else:
			colorBack = (.8, .8, .8, .8)
			colorSelect = (.3, .3, .3, .8)
		with container.sublayerGroup():
			baselayer = container.appendBaseSublayer(
				name = nameButton,
				position = (btnXpos, ypos),  # * (btn['width'] * layerWidth/15)
				size = (btnWidth, 14),  # * layerWidth/15
				backgroundColor = colorBack,
				cornerRadius = 4,
				acceptsHit = True,
			)
			symbolLayer = baselayer.appendSymbolSublayer(
				name = 'sortpoint',
				position = (btnWidth / 2, 7)
			)
			symbolLayer.setImageSettings(
				dict(
					name = "triangle",
					size = (7, 10),
					fillColor = colorSelect
				)
			)
			symbolLayer.setRotation(-90)
			# self.kernListButtons[nameButton] = baselayer
	else:
		with container.sublayerGroup():
			buttonLayer.setPosition((btnXpos, ypos))
			buttonLayer.setSize((btnWidth, 14))

			if selectedButton != nameButton:
				# print('unselected button', name)
				buttonLayer.setBackgroundColor((.8, .8, .8, .8))
				symbolLayer = buttonLayer.getSublayer('sortpoint')
				symbolLayer.setImageSettingsValue('fillColor', (.3, .3, .3, .8))
				symbolLayer.setRotation(-90)
				symbolLayer.setPosition((btnWidth / 2, 7))
			else:
				# print('selected button', name)
				buttonLayer.setBackgroundColor((.3, .3, .3, .8))
				symbolLayer = buttonLayer.getSublayer('sortpoint')
				if direction:
					symbolLayer.setRotation(90)
				else:
					symbolLayer.setRotation(-90)
				symbolLayer.setImageSettingsValue('fillColor', (.8, .8, .8, .8))
				symbolLayer.setPosition((btnWidth / 2, 7))


def drawKernListBottomControlButton(container, nameButton, schemaButtons):
	buttonLayer = container.getSublayer(nameButton)
	(layerWidth, layerHeight) = container.getSize()
	ypos = 0
	if not buttonLayer:
		(layerWidth, layerHeight) = container.getSize()
		btn = schemaButtons[nameButton]
		if btn['ypos'] == 'bottom':
			ypos = 6
		# if btn['value']:
		# 	colorBack = (.3, .3, .3, .8)
		# 	colorSelect = (.8, .8, .8, .8)
		# else:
		# 	colorBack = (.8, .8, .8, .8)
		# 	colorSelect = (.3, .3, .3, .8)
		with container.sublayerGroup():
			baselayer = container.appendBaseSublayer(
				name = nameButton,
				position = (btn['xpos'], ypos),  # * (btn['width'] * layerWidth/15)
				size = (btn['width'], 14),  # * layerWidth/15
				backgroundColor = (.3, .3, .3, .8),
				cornerRadius = 4,
				acceptsHit = True,
			)
			baselayer.appendTextLineSublayer(
				name = 'value',
				position = (10, ypos+7),
				fillColor = (1,1,1,1),
				pointSize = 9,
				text = btn['value'],
				horizontalAlignment = "left",
				# offset = (0, yoffset)
			)
	else:
		btn = schemaButtons[nameButton]
		if btn['ypos'] == 'bottom':
			ypos = 6
		buttonLayer.setPosition((btn['xpos'], ypos))
		buttonLayer.setSize((btn['width'], 14))
