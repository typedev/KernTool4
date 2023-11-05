
import vanilla
from vanilla.dialogs import getFile, putFile, ask
import os
from merz import *
from fontParts import *
import AppKit
import mojo
from mojo.subscriber import Subscriber, registerCurrentFontSubscriber, unregisterCurrentFontSubscriber
from mojo.events import addObserver, removeObserver
from vanilla.vanillaBase import osVersionCurrent, osVersion10_14
import re, codecs
import importlib
import tdKernToolEssentials4
importlib.reload(tdKernToolEssentials4)
from tdKernToolEssentials4 import *

import tdGlyphsMatrix
importlib.reload(tdGlyphsMatrix)
from tdGlyphsMatrix import *

# import tdCanvasKeysDecoder
# importlib.reload(tdCanvasKeysDecoder)
# from tdCanvasKeysDecoder import *

import tdPairsMaker
importlib.reload(tdPairsMaker)
from tdPairsMaker import PairsBuilderDialogWindow

import tdGlyphsMerzView
importlib.reload(tdGlyphsMerzView)
from tdGlyphsMerzView import *

import tdSpaceControl
importlib.reload(tdSpaceControl)
from tdSpaceControl import *

import tdGlyphparser

import tdKeyCommander
importlib.reload(tdKeyCommander)
from tdKeyCommander import *

import tdFontSelectorUI
importlib.reload(tdFontSelectorUI)
from tdFontSelectorUI import *

# import tdOverSubcriber
# import tdTXTPatterns
# importlib.reload(tdTXTPatterns)
# from tdTXTPatterns import *

import tdLangSet
importlib.reload(tdLangSet)
from tdLangSet import *


# =================================
# KERN MULTI TOOL =================

DEVELOP = True

if DEVELOP:
	pathForBundle = os.path.dirname(__file__)
	resourcePathForBundle = os.path.join(pathForBundle, "resources")
	kernToolBundle = mojo.extensions.ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)

else:
	kernToolBundle = mojo.extensions.ExtensionBundle("KernTool4")

# print (pathForBundle, resourcePathForBundle, kernToolBundle.resourcesPath())

class TDKernMultiTool(Subscriber): #, WindowController

	debug = True
	fontDocumentDidSaveDelay = 5.0
	# fontDidChangeDelay = 0

	def build (self):
		KERNTOOL_UI_GLYPHS_VIEW_FONTSIZE = getExtensionDefault(PREFKEY_GlyphsViewFontSize, fallback = 72)
		KERNTOOL_UI_GROUPS_VIEW_FONTSIZE = getExtensionDefault(PREFKEY_GroupsViewFontSize, fallback = 48)
		KERNTOOL_UI_GROUPS_VIEW_PANEL_SIZE = getExtensionDefault(PREFKEY_GroupsViewPanelSize, fallback = 230)
		darkm = ''
		KERNTOOL_UI_DARKMODE = False

		if osVersionCurrent >= osVersion10_14:
			dark = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameDarkAqua)
			if AppKit.NSApp().appearance() == dark:
				KERNTOOL_UI_DARKMODE = True
			if hasattr(mojo.UI, 'inDarkMode'):
				if mojo.UI.inDarkMode():
					KERNTOOL_UI_DARKMODE = True

		if KERNTOOL_UI_DARKMODE:
			darkm = '-dark'

		self.idName = 'KernTool4'

		self.w = vanilla.Window((1000,800), minSize = (200, 100), title = 'KernTool4', autosaveName = PREFKEY_WindowSize)

		toolbarItems = [
			{
				'itemIdentifier': "toolbarSelectFonts",
				'label': 'Select Fonts',
				'callback': self.fontsCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_selectfonts%s.pdf' % darkm),
			},
			{
				'itemIdentifier': "toolbarMakePairs",
				'label': 'Make Pairs',
				'callback': self.pairsBuilderCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_makepairs%s.pdf' % darkm),
			},
			{
				'itemIdentifier': "toolbarLoadFile",
				'label': 'Load Text',
				'callback': self.loadTextCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_loadfile%s.pdf' % darkm),
			},
			{
				'itemIdentifier': "toolbarSaveFile",
				'label': 'Save Text',
				'callback': self.saveTextCallbak,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_savefile%s.pdf' % darkm),
			},
			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},

			{
				'itemIdentifier': "toolbarLinked",
				'label': 'Link Fonts',
				'callback': self.switchLinkedModeCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_linked%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Link or unlink fonts [L]'
			},
			{
				'itemIdentifier': "toolbarEditKerning",
				'label': 'Edit Kerning',
				'callback': self.switchKerningModeCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_editkerning%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Switch to Kerning edit mode [M]'
			},
			{
				'itemIdentifier': "toolbarEditMargins",
				'label': 'Edit Margins',
				'callback': self.switchMarginsModeCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_editmargins%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Switch to Margins edit mode [M]'
			},

			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},

			{
				'itemIdentifier': "toolbarShowName",
				'label': 'Show Margins',
				'callback': self.showNamesCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_showname%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Show glyph names and margins'
			},
			{
				'itemIdentifier': "toolbarShowWidth",
				'label': 'Show Width',
				'callback': self.showWidthCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_showwidth%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Show glyph widths and margins'
			},

			{
				'itemIdentifier': "toolbarLightMode",
				'label': 'Light Mode',
				'callback': self.ligthModeCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_lightmode%s.pdf' % darkm),
				'toolTip': 'Hide all and show only glyphs as plain text'
			},

			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},

			{
				'itemIdentifier': "toolbarLangSet",
				'label': 'Check Language',
				'callback': self.langSetCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_langset%s.pdf' % darkm),
				'toolTip': 'Check language compatibility'
			},

			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},
			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},
			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},
			{
				'itemIdentifier': "toolbarShowToolbar",
				'label': 'Show Hints',
				'callback': self.switchToolbarCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_show_toolbar%s.pdf' % darkm),
				# 'toolTip': 'Warm Grey background'
			},
			{
				'itemIdentifier': "toolbarWarmBack",
				'label': 'Night Work',
				'callback': self.switchBackgroundColorCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_warmback%s.pdf' % darkm),
				'toolTip': 'Warm Grey background'
			},
		]
		self.w.addToolbar("KernTool4Toolbar", toolbarItems)
		# self.w.getNSWindow().toolbar().setSelectedItemIdentifier_('toolbarEditKerning')

		self.langSet = TDLangSet()
		self.fontsHashKernLib = makeFontsHashGroupsLib(AllFonts(),self.langSet)
		self.glyphsInMatrix = []
		self.fontList = AllFonts()
		self.fontListScales = {}
		self.currentDS = None
		# self.txtPatterns = TD_txtPatterns()
		# self.txtPatterns.makeLibPatterns(self.fontList)



		self.w.glyphsView = TDGlyphsMerzView(
			delegate = self,
			posSize = (0, 0, -0, -0), #(5, 35, -5, -290)
			backgroundColor=COLOR_BACKGROUND,#(1, 1, 1, 1),#(.75, .73, .7, .8),
			selectionCallback = self.glyphsViewSelectionCallback,
			fontsHashKernLib = self.fontsHashKernLib
		)
		# self.w.glyphsView.lineGap = 50
		# self.w.glyphsView.selectionMode = SELECTION_MODE_LINE
		self.w.glyphsView.setStatus('mode:kerning', True)
		self.w.glyphsView.setStatus('linked', True)
		self.w.glyphsView.setStatus('check language', True)

		self.w.glyphsView.id = 'glyphs view'
		self.w.glyphsView.scaleFactor = pt2Scale(KERNTOOL_UI_GLYPHS_VIEW_FONTSIZE)
		self.w.glyphsView.canUseVerticalRayBeam = False



		self.w.groupsView = TDGlyphsMerzView(
			delegate = self,
			posSize = (0, 0, -0, -0), #(5, -289, -5, 240)
			backgroundColor = COLOR_BACKGROUND,#(1, 1, 1, 1),
			fontsHashKernLib = self.fontsHashKernLib,
			glyphsLineWillDrawCallback = self.glyphsLineWillDrawCallback
		)
		# self.w.groupsView.showToolbar = True
		paneDescriptors = [
			dict(view = self.w.glyphsView, identifier = "pane1",  minSize = (230), canCollapse = False),
			dict(view = self.w.groupsView, identifier = "pane2", size = (KERNTOOL_UI_GROUPS_VIEW_PANEL_SIZE), minSize = (160), canCollapse = False),
		]
		self.w.splitView = vanilla.SplitView((0, 30, -0, -0), paneDescriptors,
		                                     isVertical = False,
		                                     dividerStyle = 'thin',
		                                     dividerThickness = 5)

		self.w.groupsView.scaleFactor = pt2Scale(KERNTOOL_UI_GROUPS_VIEW_FONTSIZE)
		self.w.groupsView.canUseVerticalRayBeam = False
		self.w.groupsView.separatePairs = True
		self.w.groupsView.lineGap = 180
		self.w.groupsView.linkedMode = False

		self.w.groupsView.setStatus('mode:kerning', True)
		self.w.groupsView.setStatus('mode:exceptions', True)
		# self.w.groupsView.setStatus('check language', True)
		self.w.groupsView.id = 'groups view'

		self.PB_leftList = []
		self.PB_rightList = []
		self.PB_patternLeft = ''
		self.PB_patternRight = ''

		self.showInfo = False
		self.titlesMode = None
		self.checkLanguageCompatibility = True
		# self.showWidth = False
		self.linkedMode = True
		self.lightMode = False
		self.warmGreyBackground = False

		self.showToolbarGroupsView = False
		self.imageToolbar_KernMode = os.path.join(kernToolBundle.resourcesPath(), 'toolbar_kern.pdf' )
		self.imageToolbar_MarginsMode = os.path.join(kernToolBundle.resourcesPath(), 'toolbar_margins.pdf' )

		self.spaceControl = TDSpaceControl(self.fontsHashKernLib, self.w.glyphsView, self.w.groupsView, mode = EDITMODE_KERNING)

		self.w.edit = vanilla.EditText((5, 5, -5, 21), callback = self.editCallback) #-120
		# self.w.btnInsertLine = vanilla.Button((-110, 4, 100, 21), 'insert line',  callback = self.insertLineCallback)

		self.blockEventFontChange = False

		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_F, callback = self.flipPair)
		self.keyCommander.registerKeyCommand(KEY_S, callback = self.switchPair)
		self.keyCommander.registerKeyCommand(KEY_L, callback = self.switchLinkedMode)

		self._saveInProcess = False
		# self.keyCommander.registerKeyCommand(KEY_S, alt = True, ctrl = True, callback = self.getStateCallbak)



	def started (self):
		addObserver(self, 'refreshKernViewFromOtherObserver', EVENT_REFRESH_ALL_OBSERVERS)
		addObserver(self, 'setTextFromOutside', EVENT_OBSERVER_SETTEXT)

		glist = 'H A T A O T O A V A Y A K O X O Y O V O H'.split(' ')
		self.glyphsInMatrix = [glist]
		matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
		if len(self.fontList)==1:
			self.linkedMode = False
			self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)

		self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)
		self.w.bind('close', self.windowClose)
		self.w.open()

	# def destroy(self):
	# 	print ('destroed')

	def saveTextCallbak(self, sender):
		bt = [
			dict(title = "Save as text", returnCode = 1),
			dict(title = "Save as list of glyphs", returnCode = 2),
			dict(title = "Cancel", returnCode = 0)
		]
		ask(messageText = "Choose type of file", informativeText = "The file can be saved as text, or as a list of glyph names.\nThe file will be saved only for the current font in the view:\n%s %s" % (self.w.glyphsView.getCurrentFont().info.familyName, self.w.glyphsView.getCurrentFont().info.styleName),
		    alertStyle = "informational", buttonTitles = bt, parentWindow = self.w, resultCallback = self.saveMix, icon = None, accessoryView = None,
		    showsHelpCallback = None)

	def saveMix (self, info):
		if info == 0: return

		pos, lines = self.w.glyphsView.getGlyphsMatrixState(onlyCurrentFont = True)
		if not lines: return
		g = []
		txt = ''
		if info == 1:
			for line in lines:
				g = [convertGlyphName2unicode(self.fontList[0], cutUniqName(gn)) for gn in line]
				if g:
					txt += ''.join(g) + '\n'
		if info == 2:
			for line in lines:
				txt += '/' + ' /'.join( [cutUniqName(gn) for gn in line] ) + '\n'

		if txt:
			filename = putFile(messageText = 'Save Mix as file', title = 'title')
			if filename:
				gfile = codecs.open(filename, 'w', encoding = 'utf-8')
				gfile.write(txt)
				gfile.close()
				print('File saved.')


	def refreshKernViewFromOtherObserver(self,info):
		# print ('OBSERVER', info)
		if 'target' in info:
			if info['target'] == 'font':
				# print ('target FONT')
				self.w.glyphsView.refreshView(justmoveglyphs = True)  # , justmoveglyphs = True)
				self.w.groupsView.refreshView(justmoveglyphs = True)
				return
			if info['target'] == 'glyph.refresh':
				print('target GLYPH')
				self.w.glyphsView.refreshView()  # , justmoveglyphs = True)
				self.w.groupsView.refreshView()
				return


	def refreshViews(self):
		self.spaceControl.refreshViews()

	def fontDidChange(self, info):
		if not self.blockEventFontChange: # receive fontDidChange for external tools only
			self.refreshViews()
		self.blockEventFontChange = False

	def glyphDidChange(self, info):
		print ('glyph did change')
		self.w.glyphsView.refreshView()
		self.w.groupsView.refreshView()

	def fontGroupsDidChange(self, info):
		# if self._saveInProcess: return
		# print ('KT4: groups did change. Reloaded...')
		# self.fontListCallback(None)
		pass

	def fontDocumentWillSave (self, info):
		self._saveInProcess = True

	def fontDocumentDidSave (self, info):
		self._saveInProcess = False

	# def fontKerningDidChange(self, info):
	# 	print ('kerning changed')
		# self.drawGlyphsMatrix(refresh = True)
	# def fontDocumentBecameCurrent(self, info):
	# 	print (info)
	# 	self.glyphDidChange(None)


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
	def magnifyWithEvent (self, sender, event):
		sender.eventMagnify(event)
	def mouseDown (self, sender, event):
		sender.eventMouseDown(event)


	def keyDown (self, sender, event):
		self.blockEventFontChange = True # block fontDidChande for CurrentFont

		self.spaceControl.checkCommand(sender, event)
		self.keyCommander.checkCommand(sender, event)
		sender.eventKeyDown(sender, event)


	def flipPair(self, sender, value):
		if sender == self.w.glyphsView:
			l = sender.selectedGlyphs[0]
			r = sender.selectedGlyphs[1]
			glyphs = sender.selectedGlyphsLine
			idx = glyphs.index(r)
			glyphs.insert(idx - 1, r)
			glyphs.pop(idx + 1)
			_glyphs = []
			for g in glyphs:
				_glyphs.append(cutUniqName(g))
			sender.setGlyphNamesListToCurrentLine(_glyphs)
			sender.selectGlyphsLayerByIndexInLine(sender.selectedGlyphsLineLayer, idx, selectionMode = SELECTION_MODE_PAIR)

	def switchPair(self, sender, value):
		ls = None
		rs = None
		lt = None
		rt = None
		if sender == self.w.groupsView:
			try:
				ls = sender.selectedGlyphs[0]
				rs = sender.selectedGlyphs[1]
				lt = self.w.glyphsView.selectedGlyphs[0]
				rt = self.w.glyphsView.selectedGlyphs[1]
			except: pass
		elif sender == self.w.glyphsView:
			try:
				lt = sender.selectedGlyphs[0]
				rt = sender.selectedGlyphs[1]
				ls = self.w.groupsView.selectedGlyphs[0]
				rs = self.w.groupsView.selectedGlyphs[1]
			except: pass
		if ls and rs and lt and rt:
			glyphsLine = self.w.glyphsView.selectedGlyphsLine
			idx = glyphsLine.index(rt)
			glyphsLine.remove(lt)
			glyphsLine.remove(rt)
			glyphsLine.insert(idx-1, rs)
			glyphsLine.insert(idx-1, ls)
			sender.selectedGlyphs = []
			_glyphsLine = []
			for g in glyphsLine:
				_glyphsLine.append(cutUniqName(g))
			self.w.glyphsView.setGlyphNamesListToCurrentLine(_glyphsLine)
			self.w.glyphsView.selectGlyphsLayerByIndexInLine(self.w.glyphsView.selectedGlyphsLineLayer, idx, selectionMode = SELECTION_MODE_PAIR)


	def loadTextFile(self, pathfile):
		if pathfile:
			lines = []
			filetxt = codecs.open(pathfile, 'r', encoding = 'utf-8')
			for idxLine, line in enumerate(filetxt):
				line = line.rstrip()  # .split('/')'\n\r'
				if not line.startswith('#') and line != '':
					tline = []
					for glyphName in tdGlyphparser.translateText(self.w.glyphsView.getCurrentFont(), line):
						if '00AD' not in glyphName:
							tline.append(glyphName)
					if tline:
						# lines.append(tline)
						lines.extend(tline)
						lines.append('{break}')
			filetxt.close()

			tm = TDGlyphsMatrix(self.w.glyphsView.getCurrentFont(), width = 25000)
			tm.setGlyphs(lines, insertVirtual = True)
			tm.buildMatrix()

			self.glyphsInMatrix = tm.get()
			matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
			if len(self.fontList) == 1:
				self.linkedMode = False
				self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
			self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)


	def loadTextCallback (self, sender):
		pairsfile = getFile(messageText = 'Select text file', title = 'title')
		if pairsfile:
			pairsfile = pairsfile[0]
			self.loadTextFile(pairsfile)

	def setTextFromOutside(self, notification):
		# if notification['fontID'] != self.fontID: return
		# self.setFont(self._font, hashKernDic = self.hashKernDic)
		need_covertion = True
		if 'glyphsready' in notification and notification['glyphsready']:
			need_covertion = False
		# if 'lines' in notification and notification['lines']:
		# 	self.PB_leftList = notification['leftList']
		# 	self.PB_rightList = notification['rightList']
		# 	self.PB_patternLeft = notification['patternLeft']
		# 	self.PB_patternRight = notification['patternRight']
		# 	self.setLines(prefix = self.PB_patternLeft,
		# 	              left = self.PB_leftList,  # CurrentFont().selection,
		# 	              right = self.PB_rightList,  # CurrentFont().selection,
		# 	              postfix = self.PB_patternRight,
		# 	              pairsperline = notification['pairsperline'])
		# 	return

		text = notification['glyphsLine']
		if not text: return
		self._currentLinesState = []
		lines = text.split('\\n')

		tline = []
		for idxLine, line in enumerate(lines):

			if need_covertion:
				for glyphName in tdGlyphparser.translateText(self.w.glyphsView.getCurrentFont(), line):
					if glyphName and '00AD' not in glyphName:
						tline.append(glyphName)
				if tline:
					tline.append('{break}')
			else:
				for glyphName in line.split('/'):
					if glyphName and '00AD' not in glyphName:
						tline.append(glyphName)
				if tline:
					tline.append('{break}')

		if tline:
			tm = TDGlyphsMatrix(self.w.glyphsView.getCurrentFont(), width = 25000)
			tm.setGlyphs(tline, insertVirtual = True)
			tm.buildMatrix()

			self.glyphsInMatrix = tm.get()
			matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
			if len(self.fontList) == 1:
				self.linkedMode = False
				self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
			self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)

	def editCallback (self, info):
		self.w.glyphsView.setTextToCurrentLine(text = info.get())

	def glyphsLineWillDrawCallback(self, sender, container):
		if sender != self.w.groupsView: return
		# if self.w.groupsView.selectionMode != SELECTION_MODE_GLYPH: return
		if not self.w.glyphsView.selectedGlyphs: return

		glyphs = container.getInfoValue('glyphs')
		side = container.getInfoValue('link')
		marks = container.getInfoValue('marks')
		data = container.getInfoValue('data')

		ray = self.w.groupsView.useRayBeam
		raypos = self.w.groupsView.rayBeamPosition

		if 'mask' in data and data['mask']:
			masks = data['mask']
			startIdx = 1
		else:
			# masks = [False for i in glyphs]
			startIdx = 0
			if side == 'left':
				# for idx, glyph in enumerate(glyphs):
				# 	if idx % 2 == 0:
				# 		masks[idx] = (True)
				masks = [ True, False ] * (int(len(glyphs)/2))

			if side == 'right':
				# for idx, glyph in enumerate(glyphs):
				# 	if not(idx % 2 == 0):
				# 		masks[idx] = True
				masks = [ False, True ] * (int(len(glyphs)/2))

		if side == 'left':
			(lm, rm) = getMargins(glyphs[startIdx], useRayBeam = ray, rayBeamPosition = raypos)
			for idx, glyph in enumerate(glyphs):
				# mark = marks[idx]
				mask = masks[idx]
				(_lm, _rm) = getMargins(glyph, useRayBeam = ray, rayBeamPosition = raypos)
				if mask and rm != _rm:
					marks[idx] = True
				elif mask and rm == _rm and marks:
					marks[idx] = False
			container.setInfoValue('marks', marks)
		if side == 'right':
			(lm, rm) = getMargins(glyphs[1], useRayBeam = ray, rayBeamPosition = raypos)
			for idx, glyph in enumerate(glyphs):
				# mark = marks[idx]
				mask = masks[idx]
				(_lm, _rm) = getMargins(glyph, useRayBeam = ray, rayBeamPosition = raypos)
				if mask and lm != _lm:
					marks[idx] = True
				elif mask and lm == _lm and marks:
					marks[idx] = False
			container.setInfoValue('marks', marks)


	def glyphsViewSelectionCallback(self, sender):
		if sender == self.w.glyphsView and self.w.glyphsView.selectionMode == SELECTION_MODE_PAIR:
			l = cutUniqName(sender.selectedGlyphs[0])
			r = cutUniqName(sender.selectedGlyphs[1])
			font = sender.getCurrentFont()
			hashKernDic = self.fontsHashKernLib[font]
			pair = researchPair(font, hashKernDic, (l,r))
			gL = pair['L_nameForKern']
			gR = pair['R_nameForKern']
			ggL = []
			ggR = []
			Llabel = None
			Rlabel = None
			ggLmarks = []
			ggRmarks = []

			ray = self.w.groupsView.useRayBeam
			raypos = self.w.groupsView.rayBeamPosition

			if hashKernDic.isKerningGroup(gL):
				Llabel = '%s // %s\n\n*Exception [E] can be made\nfor glyphs on the Left side. \nOr press [⌥E] for both sides' % ( gL, r )
				(lm, rm) = getMargins(font[font.groups[gL][0]], useRayBeam = ray, rayBeamPosition = raypos)
				margin = rm

				for ggname in font.groups[gL]:
					if ggname in font:
						(_lm,_rm) = getMargins(font[ggname], useRayBeam = ray, rayBeamPosition = raypos)
						if margin != _rm:
							ggLmarks.append(True)
						else:
							ggLmarks.append(False)
						ggL.append(font[ggname])
						ggL.append(font[r])
						ggLmarks.append(False)
			else:
				Llabel = '%s // %s' % (l, r)
				ggL.append(font[l])
				ggL.append(font[r])
			if hashKernDic.isKerningGroup(gR):
				Rlabel = '%s // %s\n\n*Exception [E] can be made\nfor glyphs on the Right side. \nOr press [⌥E] for both sides' % ( l, gR )
				(lm, rm) = getMargins(font[font.groups[gR][0]], useRayBeam = ray, rayBeamPosition = raypos)
				margin = lm

				for ggname in font.groups[gR]:
					if l in font and ggname in font:
						ggR.append(font[l])
						ggRmarks.append(False)
						ggR.append(font[ggname])
						(_lm, _rm) = getMargins(font[ggname], useRayBeam = ray, rayBeamPosition = raypos)
						if margin != _lm:
							ggRmarks.append(True)
						else:
							ggRmarks.append(False)
			else:
				Rlabel = '%s // %s' % (l, r)
				ggR.append(font[l])
				ggR.append(font[r])

			matrix = []
			matrix.append({'glyphs': ggL, 'link': 'left', 'info': Llabel, 'marks': ggLmarks })
			matrix.append({'glyphs': ggR, 'link': 'right', 'info': Rlabel, 'marks': ggRmarks})
			self.w.groupsView.startDrawGlyphsMatrix(matrix)

		if sender == self.w.glyphsView and self.w.glyphsView.selectionMode == SELECTION_MODE_GLYPH:
			currglyph = cutUniqName(sender.selectedGlyphs[0])
			font = sender.getCurrentFont()
			mapGlyphs = font.getReverseComponentMapping()
			ray = self.w.groupsView.useRayBeam
			raypos = self.w.groupsView.rayBeamPosition

			ggLmarks = []
			glyphslineL = []
			gL = self.fontsHashKernLib[font].getGroupNameByGlyph(currglyph, 'L')
			Llabel = '%s \n+composites \n+parents \n\n*Check the Right side,\nuse a Beam [B] for more accuracy' % (gL)

			if self.fontsHashKernLib[font].isKerningGroup(gL):
				# Llabel = '%s \n+composites \n+parents \n*Check the Right side' % (gL)
				(lm, rm) = getMargins(font[font.groups[gL][0]], useRayBeam = ray, rayBeamPosition = raypos)
				margin = rm
				for ggname in font.groups[gL]:
					if ggname in font:
						glyphslineL, ggLmarks = fillglyphsline(font, glyphslineL, ggLmarks, mapGlyphs, ggname, margin, 'L',ray,raypos)
			else:
				(lm, rm) = getMargins(font[gL], useRayBeam = ray, rayBeamPosition = raypos)
				margin = rm
				glyphslineL, ggLmarks = fillglyphsline(font, glyphslineL, ggLmarks, mapGlyphs, gL, margin, 'L',ray,raypos)

			ggRmarks = []
			gR = self.fontsHashKernLib[font].getGroupNameByGlyph(currglyph, 'R')
			glyphslineR = []
			Rlabel = '%s \n+composites \n+parents \n\n*Check the Left side,\nuse a Beam [B] for more accuracy' % (gR)

			if self.fontsHashKernLib[font].isKerningGroup(gR):
				# Rlabel = '%s \n+composites \n+parents \n*Check the Left side' % ( gR )
				(lm, rm) = getMargins(font[font.groups[gR][0]], useRayBeam = ray, rayBeamPosition = raypos)
				margin = lm
				for ggname in font.groups[gR]:
					if ggname in font:
						glyphslineR, ggRmarks = fillglyphsline(font, glyphslineR, ggRmarks, mapGlyphs, ggname, margin, 'R',ray,raypos)
			else:
				(lm, rm) = getMargins(font[gR], useRayBeam = ray, rayBeamPosition = raypos)
				margin = lm
				glyphslineR, ggRmarks = fillglyphsline(font, glyphslineR, ggRmarks, mapGlyphs, gR, margin, 'R',ray,raypos)

			matrix = []
			lline, lmarks, lmask = self.fontsHashKernLib[font].langSet.wrapGlyphsLine_MarksAndMasks(font, glyphslineL, ggLmarks)
			rline, rmarks, rmask = self.fontsHashKernLib[font].langSet.wrapGlyphsLine_MarksAndMasks(font, glyphslineR, ggRmarks) #, self.txtPatterns)

			matrix.append({'glyphs': lline, 'link': 'left', 'info': Llabel, 'marks': lmarks , 'data': {'mask': lmask} })
			matrix.append({'glyphs': rline, 'link': 'right', 'info': Rlabel, 'marks': rmarks , 'data': {'mask': rmask} })
			self.w.groupsView.startDrawGlyphsMatrix(matrix)
		g = []
		if sender.selectedGlyphsLine:
			g = [ convertGlyphName2unicode(font, gn) for gn in sender.selectedGlyphsLine ]
			if g:
				txt = ''.join(g)
				self.w.edit.set(txt)

	# PAIRS BUILDER
	def getPairsListFromPairsBuilderDialog(self, data):
		self.glyphsInMatrix = data['lines']
		self.PB_patternLeft = data['patternLeft']
		self.PB_patternRight = data['patternRight']
		self.PB_leftList = data['leftList']
		self.PB_rightList = data['rightList']

		matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
		if len(self.fontList)==1:
			self.linkedMode = False
			self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
		self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)

	def pairsBuilderCallback (self, sender):
		PairsBuilderDialogWindow(parentWindow = self.w,
		                         font = self.w.glyphsView.getCurrentFont(), kernhash = self.fontsHashKernLib[self.w.glyphsView.getCurrentFont()],
		                         callback = self.getPairsListFromPairsBuilderDialog,
		                         leftList = self.PB_leftList,
		                         rightList = self.PB_rightList,
		                         patternLeft = self.PB_patternLeft,
		                         patternRight = self.PB_patternRight)
	# ===========

	def fontsCallback(self, sender):
		TDFontSelectorDialogWindow( parentWindow = self.w, callback = self.fontListCallback, fontListSelected = self.fontList, scales = self.fontListScales, designSpace = self.currentDS)

	def fontListCallback(self, fontListSelected):
		# print (self.glyphsInMatrix)
		if fontListSelected:
			self.fontList = fontListSelected['selectedFonts']
			self.fontListScales = fontListSelected['scales']
			if 'ds' in fontListSelected:
				self.currentDS = fontListSelected['ds']
			self.fontsHashKernLib = makeFontsHashGroupsLib(self.fontList, self.langSet)
			self.spaceControl.setupSpaceControl(fontsHashKernLib = self.fontsHashKernLib, scalesKern = self.fontListScales)
			matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
			self.linkedMode = True
			if len(self.fontList) == 1:
				self.linkedMode = False
			self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
			self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)

	def showMarginsCallback (self, sender):
		self.showInfo = not self.showInfo
		self.w.glyphsView.switchMargins( showMargins = self.showInfo)
		self.w.groupsView.switchMargins( showMargins = self.showInfo)

	def ligthModeCallback(self, sender):
		self.lightMode = not self.lightMode
		self.w.glyphsView.switchLightMode(lightMode = self.lightMode)
		self.w.groupsView.switchLightMode(lightMode = self.lightMode)
	def swchGlyphInfoCallback(self, sender):
		self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = sender.get())
		self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = sender.get())

	def switchLinkedMode(self, sender, value):
		self.linkedMode = not self.linkedMode
		self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
	def switchLinkedModeCallback(self, sender):
		self.switchLinkedMode(sender, None)
	def switchKerningModeCallback(self, sender):
		self.spaceControl.switchKerningON()
		self.switchToolbar(self.showToolbarGroupsView)
	def switchMarginsModeCallback(self, sender):
		self.spaceControl.switchMarginsON()
		self.switchToolbar(self.showToolbarGroupsView)

	def switchBackgroundColor(self):
		if not self.warmGreyBackground:
			self.w.glyphsView.setBackgroundColor((.75, .73, .7, 1))
			self.w.groupsView.setBackgroundColor((.75, .73, .7, 1))
			self.warmGreyBackground = True
		else:
			self.w.glyphsView.setBackgroundColor((1,1,1,1))
			self.w.groupsView.setBackgroundColor((1,1,1,1))
			self.warmGreyBackground = False
	def switchBackgroundColorCallback(self, sender):
		self.switchBackgroundColor()

	def switchToolbar(self, enable = False):
		if self.spaceControl.editMode == EDITMODE_KERNING:
			self.w.groupsView.switchToolbar(enable = self.showToolbarGroupsView, imagePath = self.imageToolbar_KernMode)
		elif self.spaceControl.editMode == EDITMODE_MARGINS:
			self.w.groupsView.switchToolbar(enable = self.showToolbarGroupsView, imagePath = self.imageToolbar_MarginsMode)

	def switchToolbarCallback(self, sender):
		self.showToolbarGroupsView = not self.showToolbarGroupsView
		self.switchToolbar(self.showToolbarGroupsView)

	def langSetCallback(self, sender):
		self.checkLanguageCompatibility = not self.checkLanguageCompatibility
		self.w.glyphsView.checkLanguageCompatibility = self.checkLanguageCompatibility
		self.w.groupsView.checkLanguageCompatibility = self.checkLanguageCompatibility
		self.w.glyphsView.setStatus('check language', self.checkLanguageCompatibility)
		self.w.glyphsView.drawGlyphsMatrix(refresh = True)
		self.w.groupsView.drawGlyphsMatrix(refresh = True)

	def showNamesCallback(self, sender):
		if self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_WIDTH:
			self.titlesMode = SHOWTITLES_GLYPH_NAME
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)

		elif self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_NAME:
			self.showInfo = not self.showInfo
			self.w.glyphsView.switchMargins(showMargins = False)
			self.w.groupsView.switchMargins(showMargins = False)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)

		elif not self.showInfo:
			self.showInfo = not self.showInfo
			self.titlesMode = SHOWTITLES_GLYPH_NAME
			self.w.glyphsView.switchMargins(showMargins = True)
			self.w.groupsView.switchMargins(showMargins = True)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)


	def showWidthCallback(self, sender):
		if self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_NAME:
			self.titlesMode = SHOWTITLES_GLYPH_WIDTH
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
		elif self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_WIDTH:
			self.showInfo = not self.showInfo
			self.w.glyphsView.switchMargins(showMargins = False)
			self.w.groupsView.switchMargins(showMargins = False)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
		elif not self.showInfo:
			self.showInfo = not self.showInfo
			self.titlesMode = SHOWTITLES_GLYPH_WIDTH
			self.w.glyphsView.switchMargins(showMargins = True)
			self.w.groupsView.switchMargins(showMargins = True)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)

	def insertLineCallback(self, sender):
		self.w.glyphsView.insertGlyphsLine()

	def saveUIstate (self, state):
		if 'glyphsview.fontsize' in state:
			setExtensionDefault(PREFKEY_GlyphsViewFontSize, state['glyphsview.fontsize'])
		if 'groupsview.panelsize' in state:
			setExtensionDefault(PREFKEY_GroupsViewPanelSize, state['groupsview.panelsize'])
		if 'groupsview.fontsize' in state:
			setExtensionDefault(PREFKEY_GroupsViewFontSize, state['groupsview.fontsize'])

	def windowClose(self, sender):
		self.saveUIstate({
			'glyphsview.fontsize': scale2pt(self.w.glyphsView.scaleFactor),
			'groupsview.fontsize': scale2pt(self.w.groupsView.scaleFactor),
			'groupsview.panelsize': self.w.groupsView.height()
		})
		removeObserver(self, EVENT_REFRESH_ALL_OBSERVERS)
		removeObserver(self, EVENT_OBSERVER_SETTEXT)
		unregisterCurrentFontSubscriber(self)

def main():
	if CurrentFont():
		registerCurrentFontSubscriber(TDKernMultiTool)
	else:
		from mojo.UI import Message
		Message("No open font found..")

if __name__ == "__main__":
	main()
