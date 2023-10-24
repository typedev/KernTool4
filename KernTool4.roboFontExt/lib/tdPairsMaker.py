# -*- coding: utf-8 -*-

from vanilla import *

from fontParts.world import CurrentFont

from vanilla.dialogs import getFile, putFile, ask
from defconAppKit.controls.glyphCollectionView import GlyphCollectionView

#0108
import importlib

import tdKernToolEssentials4
importlib.reload(tdKernToolEssentials4)
from tdKernToolEssentials4 import *

import tdSpaceControl
importlib.reload(tdSpaceControl)
from tdSpaceControl import *

import tdGlyphparser
importlib.reload(tdGlyphparser)

import tdGlyphsMerzView
importlib.reload(tdGlyphsMerzView)
from tdGlyphsMerzView import *

class PairsBuilderDialogWindow(object):
	# nsViewClass = NSView

	def __init__ (self, parentWindow, font=None, kernhash = None,
	              callback=None,
	              leftList = [],
	              rightList = [],
	              patternLeft = [],
	              patternRight = []):
		wW = 1155
		hW = 680
		cellSize = (56,62)
		self.w = Sheet((wW, hW), parentWindow, minSize = (wW,hW), maxSize = (2000,2000))

		self.callback = callback
		self.font = font
		self.leftList = leftList
		self.rightList = rightList
		self.patternLeft = patternLeft
		self.patternRight = patternRight
		# self.pairsPerLine = None
		self.flipLeft = False
		self.flipRight = False
		pLefttext = ''
		pRighttext = ''
		if patternLeft:
			pLefttext = '/'+'/'.join(patternLeft)
		if patternRight:
			pRighttext = '/'+'/'.join(patternRight)
		self.hashKernDic = kernhash
		dropSettings = dict(callback = self.groupsDropCallback)

		glyphCollectionShiftY = 760
		groupsYgap = -70
		self.w.gl = Group((10,32,355,groupsYgap))
		self.w.gl.leftGlyphList = GlyphCollectionView((0, 0, -0, -180),

		# self.w.leftGlyphList = GlyphCollectionView((10, 32, (wW / 3) - 12, hW - glyphCollectionShiftY),
		                                           showModePlacard = False,
		                                           cellRepresentationName = "doodle.GlyphCell",
		                                           # initialMode = "cell",
		                                           listColumnDescriptions = None,
		                                           listShowColumnTitles = False,
		                                           showPlacard = False,
		                                           placardActionItems = None,
		                                           allowDrag = True,
		                                           selfWindowDropSettings = dropSettings,
		                                           selfApplicationDropSettings = dropSettings,
		                                           selfDropSettings = dropSettings,
		                                           otherApplicationDropSettings = dropSettings,
		                                           enableDelete = True,
		                                           selectionCallback = self.glyphsListCallback
		                                           )
		self.w.gl.leftGlyphList.id = 'leftgroup'
		self.w.gl.leftGlyphList.setCellRepresentationArguments(drawHeader = True)  # , drawMetrics = True
		self.w.gl.leftGlyphList.setCellSize(cellSize)
		# self.setContent(content)
		# self.w.leftGlyphList.getNSScrollView().setHasVerticalScroller_(True)
		# self.w.leftGlyphList.getNSScrollView().setAutohidesScrollers_(False)
		# # self.w.leftGlyphList.getNSScrollView().setBackgroundColor_(NSColor.whiteColor())
		# self.w.leftGlyphList.getNSScrollView().setBorderType_(NSNoBorder)
		# GlyphCollectionView

		self.w.gc = Group((372, 32, -372, groupsYgap))
		self.w.gc.fontGlyphList = GlyphCollectionView((0 , 0, -0 , -180),

		# self.w.gc.fontGlyphList = GlyphCollectionView(((wW / 3) + 2 , 32, (wW / 3)-4 , hW - glyphCollectionShiftY+75),
		                                            showModePlacard = False,
		                                            cellRepresentationName = "doodle.GlyphCell",
		                                            # initialMode = "cell",
		                                            listColumnDescriptions = None,
		                                            listShowColumnTitles = False,
		                                            showPlacard = False,
		                                            placardActionItems = None,
		                                            allowDrag = True,
		                                            selfWindowDropSettings = dropSettings,
		                                            selfApplicationDropSettings = dropSettings,
		                                            selfDropSettings = dropSettings,
		                                            otherApplicationDropSettings = dropSettings,
		                                            # enableDelete = True,
		                                            selectionCallback = self.glyphsListCallback
		                                            )
		self.w.gc.fontGlyphList.id = 'fontview'
		self.w.gc.fontGlyphList.setCellRepresentationArguments(drawHeader = True)  # , drawMetrics = True
		self.w.gc.fontGlyphList.setCellSize(cellSize)

		self.w.gr = Group((-365, 32, 355, groupsYgap))
		self.w.gr.rightGlyphList = GlyphCollectionView((0, 0, -0, -180),

		# self.w.gr.rightGlyphList = GlyphCollectionView(((wW / 3) + 2 + (wW/3), 32, -10, hW - glyphCollectionShiftY),
		                                            showModePlacard = False,
		                                            cellRepresentationName = "doodle.GlyphCell",
		                                            # initialMode = "cell",
		                                            listColumnDescriptions = None,
		                                            listShowColumnTitles = False,
		                                            showPlacard = False,
		                                            placardActionItems = None,
		                                            allowDrag = True,
		                                            selfWindowDropSettings = dropSettings,
		                                            selfApplicationDropSettings = dropSettings,
		                                            selfDropSettings = dropSettings,
		                                            otherApplicationDropSettings = dropSettings,
		                                            enableDelete = True,
		                                            selectionCallback = self.glyphsListCallback,
		                                            )
		self.w.gr.rightGlyphList.id = 'rightgroup'
		self.w.gr.rightGlyphList.setCellRepresentationArguments(drawHeader = True)  # , drawMetrics = True
		self.w.gr.rightGlyphList.setCellSize(cellSize)
		# self.setContent(content)
		# self.w.rightGlyphList.getNSScrollView().setHasVerticalScroller_(True)
		# self.w.rightGlyphList.getNSScrollView().setAutohidesScrollers_(False)
		# # self.w.rightGlyphList.getNSScrollView().setBackgroundColor_(NSColor.whiteColor())
		# self.w.rightGlyphList.getNSScrollView().setBorderType_(NSNoBorder)

		# self.w.lblMessage = TextBox((10, 10, -10, 17), text = 'Make pairs from selection', sizeStyle = 'regular')
		self.w.b = Box((10, -170, -10, -35))
		self.w.b.linesPreview = TDGlyphsMerzView(
			delegate = self,
			posSize = (0,0,0,-2),#(10, -155, -10, -40), #(5, 35, -5, -290)
			backgroundColor=COLOR_BACKGROUND,#(1, 1, 1, 1),#(.75, .73, .7, .8),
			# selectionCallback = self.glyphsViewSelectionCallback,
			fontsHashKernLib = {font: self.hashKernDic}
		)
		self.w.b.linesPreview.scaleFactor = pt2Scale(46)
		self.w.b.linesPreview.setStatus('single line preview',True)
		# self.topGap = -350
		# self.w.b.linesPreview.lineGap = - 100

		wW = 355
		shY = -30
		hW = -180
		posYcontrols = -40
		elemH = 19
		leftX = 0
		leftHalfX = (wW / 2) + 4
		wx1 = (wW / 2) - 12
		wx2 = (wW / 2) - 6
		wxfull1 = (wW ) - 2
		# rightX = (wW / 3) + 2 + (wW/3)
		# rightHalfX = (wW / 3) + (wW/3) + (wW / 6) - 4
		wxfull2 = wxfull1 #-10

		blockStep = 23
		blockY1 = hW - posYcontrols + shY
		posYcontrols -= blockStep
		blockY2 = hW - posYcontrols + shY
		posYcontrols -= blockStep
		blockY3 = hW - posYcontrols + shY
		posYcontrols -= blockStep
		blockY4 = hW - posYcontrols + shY
		posYcontrols -= blockStep
		blockY5 = hW - posYcontrols + shY
		posYcontrols -= blockStep
		blockY6 = hW - posYcontrols + shY
		posYcontrols -= blockStep
		blockY7 = hW - posYcontrols + shY



		self.w.gl.btnCompressGroupsLeft = Button((leftX, blockY1, wx1, elemH),
		                           "Compress selected",
		                           callback = self.btnCompressExpandCallback,
		                           sizeStyle = 'small')
		self.w.gl.btnExpandGroupsLeft = Button((leftHalfX, blockY1, wx2, elemH),
		                                      "Expand selected",
		                                      callback = self.btnCompressExpandCallback,
		                                      sizeStyle = 'small')
		# self.w.gl.btnAutoFillLeftList = Button((leftX, blockY2, wxfull1, elemH),
		#                                         'Fill the list by selection on the Right side',
		#                                         callback = self.autoFillListCallback,
		#                                         sizeStyle = 'small')



		self.w.gr.btnCompressGroupsRight = Button((leftX, blockY1, wx1, elemH),
		                            "Compress selected",
		                            callback = self.btnCompressExpandCallback,
		                            sizeStyle = 'small')
		self.w.gr.btnExpandGroupsRight = Button((leftHalfX, blockY1, wx2, elemH),
		                                       "Expand selected",
		                                       callback = self.btnCompressExpandCallback,
		                                       sizeStyle = 'small')
		# self.w.gr.btnAutoFillRightList = Button((leftX, blockY2, wxfull1, elemH),
		#                                    'Fill the list by selection on the left side',
		#                                    callback = self.autoFillListCallback,
		#                                         sizeStyle = 'small')




		self.w.gl.btnLeftSaveSet = Button((leftX, blockY3, wx1, elemH), "Save Left set...",
		                          callback = self.btnLeftSaveSetCallback, sizeStyle = 'small')
		self.w.gl.btnLeftLoadSet = Button((leftHalfX, blockY3, wx2, elemH), "Load Left set...",
		                         callback = self.btnLeftLoadSetCallback, sizeStyle = 'small')

		self.w.gr.btnRightSaveSet = Button((leftX, blockY3, wx1, elemH), "Save Right set...",
		                          callback = self.btnRightSaveSetCallback, sizeStyle = 'small')
		self.w.gr.btnRightLoadSet = Button((leftHalfX, blockY3, wx2, elemH), "Load Right set...",
		                         callback = self.btnRightLoadSetCallback, sizeStyle = 'small')


		gcW = 411
		gcwx1 = gcW/2-12

		gcleftHalfX = (gcW / 2) + 4

		self.w.gc.textPatternLeft = EditText((leftX, blockY1, gcwx1-2, elemH),
		                                     text = pLefttext, #placeholder = 'enter glyphs or text',
		                                     sizeStyle = 'small', callback = self.edittextcallback)
		# self.w.gc.lbltb = TextBox((150, blockY1, 30, elemH), '_::_',sizeStyle = 'small', alignment = 'center')
		self.w.gc.textPatternRight = EditText((gcleftHalfX , blockY1, gcwx1-2, elemH),
		                                      text = pRighttext, #placeholder = 'enter glyphs or text',
		                                      sizeStyle = 'small', callback = self.edittextcallback)

		wSeg = gcwx1 / 3 - 2
		segmentsGrp2 = [{'width': wSeg, 'title': 'Flip Left'},
		               {'width': wSeg, 'title': 'No flip'},
		               {'width': wSeg, 'title': 'Flip Right'}]
		self.w.gc.btnFlip = SegmentedButton((leftX, blockY2, gcwx1 , elemH), #*2+12
		                                     segmentDescriptions = segmentsGrp2,
		                                     selectionStyle = 'one',
		                                     sizeStyle = 'small',
		                                    callback = self.btnFlipCallback)
		self.w.gc.btnFlip.set(1)

		wSeg = gcwx1/9+5 # ширина сегмента
		segmentsGrp = [{'width': wSeg, 'title': '∞'},
		               {'width': wSeg, 'title': '1'},
		               {'width': wSeg, 'title': '2'},
		               {'width': wSeg, 'title': '3'},
		               {'width': wSeg, 'title': '4'},
		               {'width': wSeg, 'title': '5'},
		               {'width': wSeg, 'title': '6'},
		               # можно сврободно добавлять еще сегменты
		               ]
						# {'width': wx1 - (wSeg)*4+20 , 'title': 'Pairs/Line'}]
		self.w.gc.btnPairsPerLine = SegmentedButton((gcleftHalfX, blockY2, gcwx1, elemH),
		                                     segmentDescriptions = segmentsGrp,
		                                     selectionStyle = 'one',
		                                     sizeStyle = 'small',
		                                    callback = self.btnPairsPerLineCallback)
		self.w.gc.btnPairsPerLine.set(4)
		self.pairsPerLine = 4


		self.w.gc.checkTouchesOnly = CheckBox((gcleftHalfX+2, blockY3, gcwx1, elemH),
		                                      title = 'Find Touches only',
		                                      value = False, sizeStyle = 'small',
		                                      callback = self.edittextcallback)

		# self.w.gc.autoFixTouches = CheckBox((gcleftHalfX+120, blockY3, gcwx1, elemH),
		#                                       title = 'auto fix',
		#                                       value = False, sizeStyle = 'small',
		#                                       callback = self.edittextcallback)

		self.w.gbl = Group((10,-40,355,-0))
		self.w.gbl.btnCancel = Button((leftX, 10, gcwx1, elemH), "Cancel",
		                          callback = self.btnCloseCallback, sizeStyle = 'small')
		# self.w.btnTouches = Button((rightX, blockY5, wx1, elemH), "Touches only",
		#                          callback = self.btnCloseCallback, sizeStyle = 'small')
		self.w.gbr = Group((-365, -40, 355, -0))
		self.w.gbr.btnSaveMix = Button((leftX, 10, wx1, elemH), "Save Mix as file",
		                         callback = self.btnSaveMixCallback, sizeStyle = 'small')

		self.w.gbr.btnApply = Button((leftHalfX, 10, wx2, elemH), "Apply",
		                         callback = self.btnCloseCallback, sizeStyle = 'small')
		# self.w.progressBar = ProgressBar(((wW / 3) + 12 + (wW/6), blockY7, wx1-8, elemH),sizeStyle = 'small')
		self.setViewGlyphsCell(self.leftList,direction = 'L')
		self.setViewGlyphsCell(self.rightList,direction = 'R')
		self.setFontViewCell(CurrentFont())
		self.w.open()

	# def exceptionSelectorCallback (self, sender):
	# 	print self.listExt[sender.get()]

	def acceptsFirstResponder (self, info):
		return True
	def sizeChanged(self, sender):
		sender.eventResizeView()
	def mouseUp(self, sender, event):
		sender.eventMouseUp(event)
	def mouseDragged(self, sender, event):
		sender.eventMouseDragged(event)
	def scrollWheel (self, sender, event):
		sender.eventScrollWheel(event)
	# def magnifyWithEvent (self, sender, event):
	# 	sender.eventMagnify(event)
	def mouseDown (self, sender, event):
		sender.eventMouseDown(event)

	def edittextcallback(self, sender):
		self.showPreview()


	def glyphsListCallback(self, sender):
		# print(self.getLeftList())
		# print(self.getRightList())
		selectedLeftGlyph = None
		if sender.id == 'leftgroup':
			self.w.gr.rightGlyphList.setSelection([])
			selectedidx = self.w.gl.leftGlyphList.getSelection()
			if selectedidx:
				selectedLeftGlyph = self.w.gl.leftGlyphList[selectedidx[0]].name


		if sender.id == 'rightgroup':
			self.w.gl.leftGlyphList.setSelection([])
		if sender.id == 'fontview':
			self.w.gr.rightGlyphList.setSelection([])
			self.w.gl.leftGlyphList.setSelection([])
		self.showPreview(byGlyph = selectedLeftGlyph)

	def btnPairsPerLineCallback(self, sender):
		ppl = sender.get()
		if ppl == 0:
			self.pairsPerLine = None
		else:
			self.pairsPerLine = ppl #+1
		self.showPreview()

	def btnFlipCallback(self, sender):
		tflip = sender.get()
		if tflip == 0:
			self.flipLeft = True
			self.flipRight = False
		elif tflip == 1:
			self.flipLeft = False
			self.flipRight = False
		elif tflip == 2:
			self.flipLeft = False
			self.flipRight = True
		self.showPreview()


	def btnCompressExpandCallback(self, sender):
		if sender == self.w.gl.btnCompressGroupsLeft:
			self.compressGlyphsList(direction = 'L')
		elif sender == self.w.gr.btnCompressGroupsRight:
			self.compressGlyphsList(direction = 'R')
		elif sender == self.w.gl.btnExpandGroupsLeft:
			self.expandGlyphsList(direction = 'L')
		elif sender == self.w.gr.btnExpandGroupsRight:
			self.expandGlyphsList(direction = 'R')
		self.showPreview()

	def getLeftList(self):
		return [glyph.name for glyph in self.w.gl.leftGlyphList.get()]

	def getRightList(self):
		return [glyph.name for glyph in self.w.gr.rightGlyphList.get()]

	def compressGlyphsList(self, direction):
		glyphs = []
		groups = []
		groupdic = {}
		self.leftList = self.getLeftList()
		self.rightList = self.getRightList()
		if direction == 'L':
			for idx in self.w.gl.leftGlyphList.getSelection():
				glyphs.append((self.leftList[idx],idx))
			# for name in glyphs:
			# 	self.leftList.remove(name)
		elif direction == 'R':
			for idx in self.w.gr.rightGlyphList.getSelection():
				glyphs.append((self.rightList[idx],idx))
			# for name in glyphs:
			# 	self.rightList.remove(name)

		for (name,idx) in glyphs:
			groupname = self.hashKernDic.getGroupNameByGlyph(name, direction)
			if self.hashKernDic.isKerningGroup(groupname):
				if direction == 'L':
					tl = []
					if self.font.groups[groupname][0] in self.leftList:
						idx = self.leftList.index(self.font.groups[groupname][0])
					for rn in self.leftList:
						if groupname == self.hashKernDic.getGroupNameByGlyph(rn, direction):
							tl.append(rn)
					for rn in tl:
						if self.font.groups[groupname][0]!=rn:
							self.leftList.remove(rn)
				if direction == 'R':
					tl = []
					if self.font.groups[groupname][0] in self.rightList:
						idx = self.rightList.index(self.font.groups[groupname][0])
					for rn in self.rightList:
						if groupname == self.hashKernDic.getGroupNameByGlyph(rn, direction):
							tl.append(rn)
					for rn in tl:
						if self.font.groups[groupname][0] != rn:
							self.rightList.remove(rn)
				if groupname not in groupdic and len(self.font.groups[groupname])>0:
					groupdic[groupname] = (self.font.groups[groupname][0],idx)
			else:
				if name not in groupdic:
					groupdic[name] = (name,idx)

		if direction == 'L':
			for key, (name,idx) in groupdic.items():
				if name not in self.leftList:
					self.leftList.insert(idx, name)
			# self.leftList = sorted(self.leftList)
			self.setViewGlyphsCell(self.leftList, direction = direction)
		elif direction == 'R':
			for key, (name,idx) in groupdic.items():
				if name not in self.rightList:
					self.rightList.insert(idx, name)
			# self.rightList = sorted(self.rightList)
			self.setViewGlyphsCell(self.rightList, direction = direction)

	def expandGlyphsList(self, direction):
		glyphs = []
		groups = []
		self.leftList = self.getLeftList()
		self.rightList = self.getRightList()

		if direction == 'L':
			for idx in self.w.gl.leftGlyphList.getSelection():
				glyphs.append(self.leftList[idx])
		elif direction == 'R':
			for idx in self.w.gr.rightGlyphList.getSelection():
				glyphs.append(self.rightList[idx])

		for name in glyphs:
			groupname = self.hashKernDic.getGroupNameByGlyph(name, direction)
			if self.hashKernDic.isKerningGroup(groupname):
				groups.append(groupname)

		for groupname in groups:
			content = self.font.groups[groupname]
			if direction == 'L':
				for gname in content:
					if gname not in self.leftList:
						self.leftList.append(gname)
			elif direction == 'R':
				for gname in content:
					if gname not in self.rightList:
						self.rightList.append(gname)

		if direction == 'L':
			self.setViewGlyphsCell(self.leftList, direction = direction)
		elif direction == 'R':
			self.setViewGlyphsCell(self.rightList, direction = direction)

	def setFontViewCell(self, font):
		self.w.gc.fontGlyphList.set([font[glyphname] for glyphname in self.font.glyphOrder])

	# def autoFillListCallback(self, sender):
	# 	if sender == self.w.gl.btnAutoFillLeftList:
	# 		side = SIDE_2
	# 	elif sender == self.w.gr.btnAutoFillRightList:
	# 		side = SIDE_1
	# 	if side == SIDE_1:
	# 		leftList = self.getLeftList()
	# 		rightlist = []
	# 		for glyphname in leftList:
	# 			groupname = self.hashKernDic.getGroupNameByGlyph(glyphname, side = SIDE_1)
	# 			if self.hashKernDic.isKerningGroup(groupname):
	#







	def setViewGlyphsCell(self, glyphslist, direction):
		glyphs = []

		for name in glyphslist:
			if name in self.font:
				glyphs.append(self.font[name])

		if direction == 'L':
			self.w.gl.leftGlyphList.set([])
			self.w.gl.leftGlyphList.set(glyphs)
		elif direction == 'R':
			self.w.gr.rightGlyphList.set([])
			self.w.gr.rightGlyphList.set(glyphs)
		self.showPreview()


	# def btnAddGlyphs2ListCallback (self, sender):
	# 	self.leftList = self.getLeftList()
	# 	self.rightList = self.getRightList()
	#
	# 	if sender == self.w.btnGetLeft:
	# 		for name in self.font.selection:
	# 			if name not in self.leftList:
	# 				self.leftList.append(name)
	# 		self.setViewGlyphsCell(self.leftList, direction = 'L')
	# 	elif sender == self.w.btnGetRight:
	# 		for name in self.font.selection:
	# 			if name not in self.rightList:
	# 				self.rightList.append(name)
	# 		self.setViewGlyphsCell(self.rightList, direction = 'R')

	# def btnDeleteGlyphsFromListCallback(self, sender):
	# 	glyphs = []
	# 	self.leftList = self.getLeftList()
	# 	self.rightList = self.getRightList()
	# 	if sender == self.w.btnDelLeft:
	# 		for idx in self.w.gl.leftGlyphList.getSelection():
	# 			glyphs.append(self.leftList[idx])
	# 		for name in glyphs:
	# 			self.leftList.remove(name)
	# 		self.setViewGlyphsCell(self.leftList, direction = 'L')
	# 	elif sender == self.w.btnDelRight:
	# 		for idx in self.w.gr.rightGlyphList.getSelection():
	# 			glyphs.append(self.rightList[idx])
	# 		for name in glyphs:
	# 			self.rightList.remove(name)
	# 		self.setViewGlyphsCell(self.rightList, direction = 'R')


	def groupsDropCallback (self, sender, dropInfo):
		if dropInfo['isProposal']: pass
		else:
			# print sender, dropInfo
			dest = sender.id
			source = dropInfo['source']
			try:
				source = source.id
			except:
				print ('except', source)
				return True
			# print '='*80
			idx = dropInfo['rowIndex']

			glyphlist = [glyph.name for glyph in dropInfo['data']]
			# print glyphlist
			if not glyphlist: return True

			self.leftList = self.getLeftList()
			self.rightList = self.getRightList()

			if source == dest and source == 'leftgroup':
				direction = 'L'
				# print 'for left group, insert before', self.leftList[idx]
				glyphIdxName = self.leftList[idx]
				for name in glyphlist:
					self.leftList.remove(name)
				idx = 0
				for i, name in enumerate(self.leftList):
					if name == glyphIdxName:
						idx = i
				for name in glyphlist:
					self.leftList.insert(idx, name)
					idx +=1
				self.setViewGlyphsCell(self.leftList,direction = direction)

			if source == dest and source == 'rightgroup':
				direction = 'R'
				# print 'for right group, insert before', self.rightList[idx]
				glyphIdxName = self.rightList[idx]
				for name in glyphlist:
					self.rightList.remove(name)
				idx = 0
				for i, name in enumerate(self.rightList):
					if name == glyphIdxName:
						idx = i
				for name in glyphlist:
					self.rightList.insert(idx, name)
					idx += 1
				self.setViewGlyphsCell(self.rightList, direction = direction)

			if source != dest:
				if source == 'fontview' and dest == 'leftgroup':
					direction = 'L'
					for name in glyphlist:
						if name not in self.leftList:
							self.leftList.insert(idx,name)
							idx+=1
					self.setViewGlyphsCell(self.leftList, direction = direction)
				if source == 'fontview' and dest == 'rightgroup':
					direction = 'R'
					for name in glyphlist:
						if name not in self.rightList:
							self.rightList.insert(idx,name)
							idx+=1
					self.setViewGlyphsCell(self.rightList, direction = direction)
				if source == 'leftgroup' and dest == 'rightgroup':
					direction = 'R'
					for name in glyphlist:
						if name not in self.rightList:
							self.rightList.insert(idx, name)
							idx += 1
					self.setViewGlyphsCell(self.rightList, direction = direction)
				if source == 'rightgroup' and dest == 'leftgroup':
					direction = 'L'
					for name in glyphlist:
						if name not in self.leftList:
							self.leftList.insert(idx, name)
							idx += 1
					self.setViewGlyphsCell(self.leftList, direction = direction)
		return True


	def mixPairs (self, prefix=None, left=None, right=None, postfix=None,
	              pairsperline = None, flipLeft = False, flipRight = False, checkTouches = False):
		# self.leftselection = left
		# self.rightselection = right
		lines = []
		idxLine = 0
		countpairs = 1

		# totalpairs = len(left) * len(right)
		# perc = 100 / totalpairs
		# pairsCountProgress = 0

		# print (totalpairs, perc)

		for leftglyph in left:
			line = []
			for rightglyph in right:

				# pairsCountProgress += perc
				# print (round(pairsCountProgress,0))
				# if round(pairsCountProgress,0) == 1.0:
				# 	self.w.progressBar.increment()
				# 	pairsCountProgress = 0

				if not checkTouches:
					if prefix:
						for prefixglyph in prefix:
							if prefixglyph != '':
								line.append(prefixglyph)
					if flipRight:
						line.append(rightglyph)

					line.append(leftglyph)
					line.append(rightglyph)
					if flipLeft:
						line.append(leftglyph)

					if postfix:
						for postfixglyph in postfix:
							if postfixglyph != '':
								line.append(postfixglyph)
					if pairsperline:
						if countpairs == pairsperline:
							countpairs = 1
							lines.append(line)
							line = []
						else:
							countpairs += 1
				else: # checking Touches

					pairinfo = researchPair(self.font, self.hashKernDic, (leftglyph, rightglyph))
					kernValue = pairinfo['kernValue']
					if kernValue == None:
						kernValue = 0
					if checkOverlapingGlyphs(self.font, self.font[leftglyph], self.font[rightglyph],
					                         kernvalue = kernValue):
						if prefix:
							for prefixglyph in prefix:
								if prefixglyph != '':
									line.append(prefixglyph)

						line.append(leftglyph)
						line.append(rightglyph)

						if postfix:
							for postfixglyph in postfix:
								if postfixglyph != '':
									line.append(postfixglyph)
						if pairsperline:
							if countpairs == pairsperline:
								countpairs = 1
								if line:
									lines.append(line)
								line = []
							else:
								countpairs += 1

			if pairsperline:
				if line:
					lines.append(line)
				countpairs = 1
				idxLine += 1
			if not pairsperline:
				idxLine += 1
				if line:
					lines.append(line)

		return {'lines': lines,
                'leftList': left,
                'rightList': right,
                'patternLeft': prefix,
                'patternRight': postfix,
                'ppl': pairsperline
                }
		# if self.callback:
		# 	self.callback( {'lines': lines,
		# 	                'leftList': left,
		# 	                'rightList': right,
		# 	                'patternLeft': prefix,
		# 	                'patternRight': postfix,
		# 	                'ppl': pairsperline
		# 	                } )


	def setLines(self):
		self.patternLeft = tdGlyphparser.translateText(font = self.font,
		                                               text = self.w.gc.textPatternLeft.get())
		self.patternRight = tdGlyphparser.translateText(font = self.font,
		                                                text = self.w.gc.textPatternRight.get())

		self.leftList = self.getLeftList()
		self.rightList = self.getRightList()
		checkTouches = self.w.gc.checkTouchesOnly.get()

		mix = self.mixPairs(self.patternLeft, self.leftList, self.rightList, self.patternRight,
		              pairsperline = self.pairsPerLine, flipLeft = self.flipLeft, flipRight = self.flipRight,
		              checkTouches = checkTouches)
		if self.callback:
			self.callback(mix)


	def showPreview(self, byGlyph = None):
		patternLeft = tdGlyphparser.translateText(font = self.font,
		                                               text = self.w.gc.textPatternLeft.get())
		patternRight = tdGlyphparser.translateText(font = self.font,
		                                                text = self.w.gc.textPatternRight.get())
		leftglyph = None
		rightList = self.getRightList()
		if byGlyph:
			leftglyph = byGlyph
		else:
			l = self.getLeftList()
			if l:
				leftglyph = l[0]

		checkTouches = self.w.gc.checkTouchesOnly.get()
		if leftglyph and rightList:
			mix = self.mixPairs(patternLeft, [leftglyph], rightList, patternRight,
			                    pairsperline = self.pairsPerLine, flipLeft = self.flipLeft, flipRight = self.flipRight,
			                    checkTouches = checkTouches)
			# if mix['lines']:
			matrix = prepareGlyphsMatrix(mix['lines'], [self.font])
			if matrix:
				self.w.b.linesPreview.startDrawGlyphsMatrix([matrix[0]], animatedStart = False)
			else:
				self.w.b.linesPreview.startDrawGlyphsMatrix([], animatedStart = False)
			# else:
			# 	self.w.b.linesPreview.startDrawGlyphsMatrix(['glyphs':[]], animatedStart = False)





	def btnCloseCallback (self, sender):
		if sender == self.w.gbr.btnApply:
			self.setLines()
		self.w.gl.leftGlyphList.set([])
		self.w.gr.rightGlyphList.set([])
		self.w.gc.fontGlyphList.set([])
		self.w.close()


	def btnSaveMixCallback(self, sender):
		# self.showPreview()
		bt = [
            dict(title="Save as text", returnCode=1),
            dict(title="Save as list of glyphs", returnCode=2),
            dict(title="Cancel", returnCode=0)
            ]
		ask(messageText="Choose type of file", informativeText="the file can be saved as text, or as a list of glyph names", alertStyle="informational", buttonTitles=bt, parentWindow=self.w, resultCallback=self.saveMix, icon=None, accessoryView=None, showsHelpCallback=None)


	def saveMix(self, info):
		if info == 0: return
		self.patternLeft = tdGlyphparser.translateText(font = self.font,
		                                               text = self.w.gc.textPatternLeft.get())
		self.patternRight = tdGlyphparser.translateText(font = self.font,
		                                                text = self.w.gc.textPatternRight.get())

		self.leftList = self.getLeftList()
		self.rightList = self.getRightList()
		checkTouches = self.w.gc.checkTouchesOnly.get()

		mix = self.mixPairs(self.patternLeft, self.leftList, self.rightList, self.patternRight,
		              pairsperline = self.pairsPerLine, flipLeft = self.flipLeft, flipRight = self.flipRight,
		              checkTouches = checkTouches)
		if mix:
			lines = mix['lines']
			g = []
			txt = ''
			if info == 1:
				for line in lines:
					g = [convertGlyphName2unicode(self.font, gn) for gn in line]
					if g:
						txt += ''.join(g) + '\n'
				# print (txt)
			if info == 2:
				for line in lines:
					txt += '/'+ ' /'.join(line) + '\n'
				# print (txt)

			if txt:
				filename = putFile(messageText = 'Save Mix as file', title = 'title')
				if filename:
					gfile = codecs.open(filename, 'w', encoding = 'utf-8')
					gfile.write(txt)
					gfile.close()
					print('File saved.')


	def loadSetOfGlyphs (self, filename, direction):
		print ('Loading glyph set from', filename)
		glyphset = []
		gfile = open(filename, mode = 'r')
		for line in gfile:
			line = line.strip()
			line = line.split(' ')
			glyphset.extend(line)
		gfile.close()
		glyphs = []
		self.leftList = []#self.getLeftList()
		self.rightList = []#self.getRightList()

		for gname in glyphset:
			if gname in self.font:
				if direction == 'L':
					self.leftList.append(gname)
				else:
					self.rightList.append(gname)
				glyphs.append(self.font[gname])
			if direction == 'L':
				self.w.gl.leftGlyphList.set(glyphs)
			else:
				self.w.gr.rightGlyphList.set(glyphs)


	def saveSetOfGlyphs(self, filename, direction):
		glyphs = []
		print ('Saving glyphs set to', filename)

		if direction == 'L':
			for glyph in self.w.gl.leftGlyphList.get():
				glyphs.append(glyph.name)
		else:
			for glyph in self.w.gr.rightGlyphList.get():
				glyphs.append(glyph.name)			# glyphset = ' '.join(self.w.rightGlyphList.get())
		glyphset = ' '.join(glyphs)

		gfile = open(filename, mode = 'w')
		gfile.write(glyphset)
		gfile.close()
		print ('File saved.')


	def btnLeftSaveSetCallback(self, sender):
		filename = putFile(messageText = 'Save glyphs set file', title = 'title')
		if filename:
			self.saveSetOfGlyphs(filename = filename, direction = 'L')

	def btnLeftLoadSetCallback(self, sender):
		filename = getFile(messageText = 'Select text file', title = 'title')
		if filename and filename[0]:
			self.loadSetOfGlyphs(filename = filename[0], direction = 'L')

	def btnRightSaveSetCallback(self, sender):
		filename = putFile(messageText = 'Save glyphs set file', title = 'title')
		if filename:
			self.saveSetOfGlyphs(filename = filename, direction = 'R')

	def btnRightLoadSetCallback(self, sender):
		filename = getFile(messageText = 'Select text file', title = 'title')
		if filename and filename[0]:
			self.loadSetOfGlyphs(filename = filename[0], direction = 'R')


	# def draw (self):
	# 	self.w.rightGlyphList.preloadGlyphCellImages()
	# 	self.w.leftGlyphList.preloadGlyphCellImages()
