
import vanilla
from vanilla.dialogs import getFile, putFile, ask
import os
from merz import *
from fontParts import *
import AppKit
import mojo
import ezui
from mojo.subscriber import Subscriber, registerCurrentGlyphSubscriber, unregisterCurrentGlyphSubscriber
from mojo.events import addObserver, removeObserver
from vanilla.vanillaBase import osVersionCurrent, osVersion10_14
import re, codecs
import importlib
from mojo.UI import OpenGlyphWindow

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

# import tdLangSet
# importlib.reload(tdLangSet)
# from tdLangSet import *

CONTEXTGLYPHSLINESLIST = """
0 1 2 3 4 5 6 7 8 9
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
А Б В Г Д Е Ё Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я
а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я
! , . : ; ? ‐ ‑ ‘ ’ ‚ “ ” „ ‹ › « »
""".split('\n')[1:-1]



# =================================

DEVELOP = True

if DEVELOP:
	pathForBundle = os.path.dirname(__file__)
	# print('SpaceArk dir', pathForBundle)
	resourcePathForBundle = os.path.join(pathForBundle, "resources")
	kernToolBundle = mojo.extensions.ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)

else:
	kernToolBundle = mojo.extensions.ExtensionBundle("SpaceArk")

# print (pathForBundle, resourcePathForBundle, kernToolBundle.resourcesPath())

class TDGlyphSequencesEditWindow(ezui.WindowController):
	def build (self, callback = None):
		content = """
		= HorizontalStack
		|----------| 
		| sequence | @sequencesTable
		|----------|
		> (+-) @addRemoveButton
		> Glyphs must be unique in all sequences
		=---=
	    (Cancel) @cancelButton
	    (Apply)  @applyButton
		"""
		sequencesTableData = [
        ]
		descriptionData = dict(
            sequencesTable=dict(
                # width=100,
                items=sequencesTableData,
	            columnDescriptions = [
		            dict(
			            identifier = "sequence",
			            # title = "Sequence",
			            # width = 50,
			            editable = True,
		            ),
	            ],

            ),
			cancelButton = dict(
				keyEquivalent = chr(27)
			),  # call button on esc keydown
		)
		self.w = ezui.EZWindow(
			title = "Glyph Sequence Editor",
			size = (700, 400),
			minSize = (700, 400),
			content = content,
			descriptionData = descriptionData,
			controller = self
		)

	def started (self):
		table = self.w.getItem('sequencesTable')
		lines = getExtensionDefault(PREFKEY_GlyphSequencesSArk, fallback = CONTEXTGLYPHSLINESLIST)
		for line in lines:
			item = table.makeItem(
				sequence = line
			)
			table.appendItems([item])
		self.w.open()

	def addRemoveButtonAddCallback (self, sender):
		table = self.w.getItem("sequencesTable")
		item = table.makeItem(
			sequence = ''
		)
		table.appendItems([item])
		table.setSelectedIndexes([len(table.get())-1])

	def addRemoveButtonRemoveCallback (self, sender):
		table = self.w.getItem("sequencesTable")
		table.removeSelectedItems()

	def cancelButtonCallback (self, sender):
		self.w.close()

	def applyButtonCallback(self, sender):
		lines = []
		table = self.w.getItem('sequencesTable')
		glyphs = []
		for item in table.get():
			line = item['sequence']
			for glyph in line.split(' '):
				if glyph:
					if glyph in glyphs:
						from mojo.UI import Message
						Message("Found duplicate glyphs in sequences..", informativeText = glyph)
						return
					else:
						glyphs.append(glyph)
			lines.append(item['sequence'])
		setExtensionDefault(PREFKEY_GlyphSequencesSArk, value = lines)

		self.w.close()








class TDSpaceArkTool(Subscriber): #, WindowController

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

		self.w = vanilla.Window((1000,800), minSize = (200, 100), title = 'SpaceArk', autosaveName = PREFKEY_WindowSize)

		toolbarItems = [
			{
				'itemIdentifier': "toolbarSelectFonts",
				'label': 'Select Fonts',
				'callback': self.fontsCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_selectfonts%s.pdf' % darkm),
			},
			# {
			# 	'itemIdentifier': "toolbarMakePairs",
			# 	'label': 'Make Pairs',
			# 	'callback': self.pairsBuilderCallback,
			# 	'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_makepairs%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': "toolbarLoadFile",
			# 	'label': 'Load Text',
			# 	'callback': self.loadTextCallback,
			# 	'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_loadfile%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': "toolbarSaveFile",
			# 	'label': 'Save Text',
			# 	'callback': self.saveTextCallbak,
			# 	'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_savefile%s.pdf' % darkm),
			# },
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
				'itemIdentifier': "toolbarShowMetrics",
				'label': 'Show Metrics',
				'callback': self.showMetricsCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_showmetrics%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Show Font Dimensions'
			},
			{
				'itemIdentifier': "toolbarShowSkeleton",
				'label': 'Show Skeleton',
				'callback': self.showSkeletonCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_showskeleton%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Show Glyph Skeleton'
			},
			{
				'itemIdentifier': "toolbarShowBlues",
				'label': 'Show Blues',
				'callback': self.showBluesZonesCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_showblues%s.pdf' % darkm),
				# 'selectable': True,
				'toolTip': 'Show Blue zones'
			},
			# {
			# 	'itemIdentifier': "toolbarShowFamilys",
			# 	'label': 'Show Familys',
			# 	'callback': self.showFamilyZonesCallback,
			# 	'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_showfamily%s.pdf' % darkm),
			# 	# 'selectable': True,
			# 	'toolTip': 'Show Family zones'
			# },

			{
				'itemIdentifier': "toolbarLightMode",
				'label': 'Light Mode',
				'callback': self.ligthModeCallback,
				'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_lightmode%s.pdf' % darkm),
				'toolTip': 'Hide all and show only glyphs as plain text'
			},

			# {
			# 	'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			# },

			# {
			# 	'itemIdentifier': "toolbarLangSet",
			# 	'label': 'Check Language',
			# 	'callback': self.langSetCallback,
			# 	'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_langset%s.pdf' % darkm),
			# 	'toolTip': 'Check language compatibility'
			# },

			# {
			# 	'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			# },
			# {
			# 	'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			# },
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
		self.w.addToolbar("SpaceArkToolbar", toolbarItems)
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
			posSize = (0, 30, -0, -0), #(5, 35, -5, -290)
			backgroundColor=COLOR_BACKGROUND,#(1, 1, 1, 1),#(.75, .73, .7, .8),
			selectionCallback = self.glyphsViewSelectionCallback,
			doubleClickCallback = self.glyphsViewDoubleClickCallback,
			glyphsLineWillDrawCallback = self.glyphsLineWillDrawCallback,
			fontsHashKernLib = self.fontsHashKernLib
		)
		# self.w.glyphsView.lineGap = 50
		# self.w.glyphsView.selectionMode = SELECTION_MODE_LINE
		self.w.glyphsView.setStatus('mode:margins', True)
		self.w.glyphsView.setStatus('linked', True)
		# self.w.glyphsView.setStatus('check language', True)

		self.w.glyphsView.id = 'glyphs view'
		self.w.glyphsView.scaleFactor = pt2Scale(KERNTOOL_UI_GLYPHS_VIEW_FONTSIZE)
		self.w.glyphsView.canUseVerticalRayBeam = True

		self.showInfo = True
		self.titlesMode = SHOWTITLES_GLYPH_NAME
		self.showMetrics = False
		self.showSkeleton = False
		# self.showBlueZones = False
		# self.showFamilyZones = False
		self.switchZones = 0
		# self.checkLanguageCompatibility = True
		# self.showWidth = False
		self.linkedMode = True
		self.lightMode = False
		self.warmGreyBackground = False
		self.switchers = []

		self.w.glyphsView.selectionMode = SELECTION_MODE_GLYPH
		self.w.glyphsView.showKerning = True
		self.w.glyphsView.switchMargins(True)

		self.showToolbarGroupsView = False
		self.imageToolbar_KernMode = os.path.join(kernToolBundle.resourcesPath(), 'toolbar_kern_cut.pdf' )
		self.imageToolbar_MarginsMode = os.path.join(kernToolBundle.resourcesPath(), 'toolbar_margins.pdf' )

		self.spaceControl = TDSpaceControl(self.fontsHashKernLib, self.w.glyphsView, mode = EDITMODE_MARGINS)
		self.spaceControl.switchMarginsON()


		# self.w.editLeft = vanilla.EditText((5, 5, 120, 21), callback = self.editCallback) #-120
		# self.w.edit = vanilla.EditText((130, 5, -245, 21), callback = self.editCallback) #-120
		# self.w.editRight = vanilla.EditText((-240, 5, 120, 21), callback = self.editCallback) #-120
		#
		# self.w.btnInsertLine = vanilla.Button((-110, 4, 100, 21), 'get selection',  callback = self.insertLineCallback)
		self.w.eb = vanilla.Group((0,0,-0,29))
		self.w.eb.btnLL = vanilla.Button('auto','􀆉',callback = self.btnSwithGlyphCallback)
		self.w.eb.editLeft = vanilla.EditText('auto', callback = self.editCallback) #-120
		self.w.eb.btnLR = vanilla.Button('auto','􀆊',callback = self.btnSwithGlyphCallback)

		self.w.eb.edit = vanilla.EditText('auto', callback = self.editCallback) #-120
		self.w.eb.btnInsertLine = vanilla.Button('auto', 'get selection',  callback = self.insertLineCallback)
		self.w.eb.btnWrapLine = vanilla.Button('auto', 'wrap',  callback = self.btnWrapCallback)


		self.w.eb.btnRL = vanilla.Button('auto','􀆉',callback = self.btnSwithGlyphCallback)
		self.w.eb.editRight = vanilla.EditText('auto', callback = self.editCallback) #-120
		self.w.eb.btnRR = vanilla.Button('auto','􀆊',callback = self.btnSwithGlyphCallback)

		self.w.eb.btnEBsettings = vanilla.Button('auto','􀥏',callback = self.btnSequencesEditorCallback)



		rulesEditBar = [
		    # Horizontal
		    "H:|-border-[btnLL]-space-[editLeft(==120)]-space-[btnLR]-border-[edit]-space-[btnInsertLine(==120)]-space-[btnWrapLine(==80)]-border-[btnRL]-space-[editRight(==120)]-space-[btnRR]-border-[btnEBsettings]-border-|",
		    # Vertical
			"V:|-space-[btnLL]-space-|",
		    "V:|-space-[editLeft]-space-|",
			"V:|-space-[btnLR]-space-|",
		    "V:|-space-[edit]-space-|",
			"V:|-space-[btnInsertLine]-space-|",
			"V:|-space-[btnWrapLine]-space-|",
			"V:|-space-[btnRL]-space-|",
			"V:|-space-[editRight]-space-|",
			"V:|-space-[btnRR]-space-|",
			"V:|-space-[btnEBsettings]-space-|",

		]
		metricsEditBar = {
			"border": 10,
			"space": 3
		}
		self.w.eb.addAutoPosSizeRules(rulesEditBar, metricsEditBar)

		self.blockEventFontChange = False

		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_F, callback = self.flipPair)
		# self.keyCommander.registerKeyCommand(KEY_S, callback = self.switchPair)
		self.keyCommander.registerKeyCommand(KEY_L, callback = self.switchLinkedMode)

		self._saveInProcess = False
		# self.keyCommander.registerKeyCommand(KEY_S, alt = True, ctrl = True, callback = self.getStateCallbak)



	def started (self):
		# addObserver(self, 'refreshKernViewFromOtherObserver', EVENT_REFRESH_ALL_OBSERVERS)
		# addObserver(self, 'setTextFromOutside', EVENT_OBSERVER_SETTEXT)
		selected = list(CurrentFont().selection)
		if not selected:

			selected = 'H H O H H O O H'.split(' ')
			self.w.eb.edit.set('HHOHHOOH')
		else:
			self.w.eb.edit.set('/'+'/'.join(selected))

		self.glyphsInMatrix = [selected]

		matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
		if len(self.fontList)==1:
			self.linkedMode = False
			self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)

		self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)
		self.makeLinesOfSwitchers()
		self.w.bind('close', self.windowClose)
		self.w.open()



	# def refreshKernViewFromOtherObserver(self,info):
	# 	# print ('OBSERVER', info)
	# 	if 'target' in info:
	# 		if info['target'] == 'font':
	# 			# print ('target FONT')
	# 			self.w.glyphsView.refreshView(justmoveglyphs = True)  # , justmoveglyphs = True)
	# 			# self.w.groupsView.refreshView(justmoveglyphs = True)
	# 			return
	# 		if info['target'] == 'glyph.refresh':
	# 			print('target GLYPH')
	# 			self.w.glyphsView.refreshView()  # , justmoveglyphs = True)
	# 			# self.w.groupsView.refreshView()
	# 			return
	def makeLinesOfSwitchers(self):
		self.switchers = []
		lines = getExtensionDefault(PREFKEY_GlyphSequencesSArk, fallback = CONTEXTGLYPHSLINESLIST)
		for line in lines:
			lineofglyphs = tdGlyphparser.translateText(CurrentFont(), line.replace(' ',''))
			self.switchers.append(lineofglyphs)


	def refreshViews(self):
		self.spaceControl.refreshViews()

	def fontDidChange(self, info):
		# print('font did Change')
		if not self.blockEventFontChange: # receive fontDidChange for external tools only
			self.refreshViews()
		self.blockEventFontChange = False

	def glyphDidChange(self, info):
		# self.w.glyphsView.setGlyphNamesListToCurrentLine(self.glyphsInMatrix)
		# print ('glyph did Change')
		# txt = self.w.edit.get()
		# # if '/?' in txt:
		# if CurrentGlyph():
		# 	txt = txt.replace('/?', '/%s' % CurrentGlyph().name)
		# self.w.glyphsView.setTextToCurrentLine(text = txt) #, font = CurrentGlyph().font
		self.setEditText2View()

		# self.w.glyphsView.refreshView()

	def roboFontDidSwitchCurrentGlyph (self, info):
		# print ('glyph did Switch')
		# print(self.glyphsInMatrix)
		self.setEditText2View()

		# txt = self.w.edit.get()
		# # if '/?' in txt:
		# if CurrentGlyph():
		# 	txt = txt.replace('/?', '/%s' % CurrentGlyph().name)
		# self.w.glyphsView.setTextToCurrentLine(text = txt) #, font = CurrentGlyph().font
		# self.w.glyphsView.refreshView()

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
		if sender == self.w.glyphsView and self.w.glyphsView.selectionMode == SELECTION_MODE_PAIR:
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



	def setTextFromOutside(self, notification):
		# if notification['fontID'] != self.fontID: return
		# self.setFont(self._font, hashKernDic = self.hashKernDic)
		need_covertion = True
		if 'glyphsready' in notification and notification['glyphsready']:
			need_covertion = False


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
			tm = TDGlyphsMatrix(self.w.glyphsView.getCurrentFont(), width = 15000)
			tm.setGlyphs(tline, insertVirtual = True)
			tm.buildMatrix()

			self.glyphsInMatrix = tm.get()
			matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
			if len(self.fontList) == 1:
				self.linkedMode = False
				self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
			self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)


	def setEditText2View(self):
		txtL = self.w.eb.editLeft.get()
		txt = self.w.eb.edit.get()
		txtR = self.w.eb.editRight.get()
		gL = []
		gC = []
		gR = []
		if txtL:
			gL = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = txtL)
		if txt:
			gC = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = txt)
		if txtR:
			gR = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = txtR)
		glyphsline = []
		for g in gC:
			if gL:
				glyphsline += gL
			glyphsline.append(g)
			if gR:
				glyphsline += gR
		if glyphsline:
			self.w.glyphsView.setGlyphNamesListToCurrentLine(glyphsline)
		self.glyphsInMatrix = glyphsline

	# if '/?' in txt:
	# if CurrentGlyph():
	# 	txt = txt.replace('/?', '/%s' % CurrentGlyph().name)
	# self.glyphsInMatrix = [self.w.glyphsView.setTextToCurrentLine(text = txt)] #, font = CurrentGlyph().font()


	def editCallback (self, info):
		self.setEditText2View()
		# print (self.glyphsInMatrix)

	def btnSwithGlyphCallback(self, sender):
		self.makeLinesOfSwitchers()
		def findLineOfSwitchers(switchers, glyphname):
			if not glyphname: return
			for line in switchers:
				if glyphname in line:
					return line, line.index(glyphname)
			return None, None

		currentGlyph = None
		currentLine = None
		stepIdx = 0
		sideSwitch = None
		if sender == self.w.eb.btnLL:
			currentLine = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = self.w.eb.editLeft.get())
			# if len(c)>1:return
			if not currentLine: return
			currentGlyph = currentLine[-1]
			stepIdx = -1
			sideSwitch = SIDE_1

		if sender == self.w.eb.btnLR:
			currentLine = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = self.w.eb.editLeft.get())
			# if len(c)>1:return
			if not currentLine: return

			currentGlyph = currentLine[-1]
			stepIdx = 1
			sideSwitch = SIDE_1

		if sender == self.w.eb.btnRL:
			currentLine = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = self.w.eb.editRight.get())
			# if len(c)>1:return
			if not currentLine: return

			currentGlyph = currentLine[0]
			stepIdx = -1
			sideSwitch = SIDE_2

		if sender == self.w.eb.btnRR:
			currentLine = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = self.w.eb.editRight.get())
			# if len(c)>1:return
			if not currentLine: return

			currentGlyph = currentLine[0]
			stepIdx = 1
			sideSwitch = SIDE_2

		# print(currentGlyph, self.switchers)

		lineOfSwitchers, idx = findLineOfSwitchers(self.switchers, currentGlyph)
		cidx = idx
		if lineOfSwitchers:
			# print(lineOfSwitchers, idx)
			if idx + stepIdx > len(lineOfSwitchers)-1:
				idx = 0
			elif idx + stepIdx < 0:
				idx = len(lineOfSwitchers)-1
			else:
				idx = idx + stepIdx
		# print(cidx, idx, lineOfSwitchers[cidx], lineOfSwitchers[idx])
		if sideSwitch == SIDE_1:
			currentLine[-1] = lineOfSwitchers[idx]
			self.w.eb.editLeft.set('/' + '/'.join(currentLine))
		elif sideSwitch == SIDE_2:
			currentLine[0] = lineOfSwitchers[idx]
			self.w.eb.editRight.set('/' + '/'.join(currentLine))
		self.setEditText2View()



	def btnWrapCallback(self, sender):
		txt = self.w.eb.edit.get()
		glyphslinetxt = []
		glyphsline = []
		if txt:
			glyphslinetxt = tdGlyphparser.translateText(font = self.w.glyphsView.getCurrentFont(), text = txt)
			gline, _, _ = self.langSet.wrapGlyphsLine_MarksAndMasks(font = self.w.glyphsView.getCurrentFont(),
			                                          glyphsline = glyphslinetxt,
			                                          marks = [True]*len(glyphslinetxt))
			glyphsline = [glyph.name for glyph in gline]
			print(glyphsline)

		if glyphsline:
			self.w.glyphsView.setGlyphNamesListToCurrentLine(glyphsline)
		self.glyphsInMatrix = glyphsline



	def glyphsLineWillDrawCallback(self, sender, container):
		if sender != self.w.glyphsView: return
		glyphs = container.getInfoValue('glyphs')
		font = container.getInfoValue('font')

		lineinfo = container.getInfoValue('lineinfo')
		widthLine = 0
		if not lineinfo: lineinfo = ''
		if self.titlesMode == SHOWTITLES_GLYPH_WIDTH:

			for idx, glyph in enumerate(glyphs):
				kernvalue = 0
				if idx+1<len(glyphs):
					pair = researchPair(font, self.fontsHashKernLib[font], (glyph.name, glyphs[idx+1].name))
					kernvalue = pair['kernValue']
					if not kernvalue: kernvalue = 0
				widthLine += glyph.width + kernvalue

		lineinfo = re.sub(r'\w*:\d\w*', '', lineinfo).strip()
		if self.titlesMode == SHOWTITLES_GLYPH_WIDTH:
			lineinfo += '\n\nwidth:%i' % widthLine

		container.setInfoValue('lineinfo', lineinfo)




	def glyphsViewSelectionCallback(self, sender):
		if sender == self.w.glyphsView:
		# 	l = cutUniqName(sender.selectedGlyphs[0])
		# 	r = cutUniqName(sender.selectedGlyphs[1])
			font = sender.getCurrentFont()
			hashKernDic = self.fontsHashKernLib[font]



	def fontsCallback(self, sender):
		TDFontSelectorDialogWindow( parentWindow = self.w, callback = self.fontListCallback, fontListSelected = self.fontList, scales = self.fontListScales, designSpace = self.currentDS)

	def fontListCallback(self, fontListSelected):
		# print (self.glyphsInMatrix)
		if fontListSelected:
			self.fontList = fontListSelected['selectedFonts']
			self.fontListScales = fontListSelected['scales']
			if 'ds' in fontListSelected:
				self.currentDS = fontListSelected['ds']
			# print (self.fontListScales)
			self.fontsHashKernLib = makeFontsHashGroupsLib(self.fontList, self.langSet)
			self.spaceControl.setupSpaceControl(fontsHashKernLib = self.fontsHashKernLib, scalesKern = self.fontListScales)

			matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
			self.linkedMode = True
			if len(self.fontList) == 1:
				self.linkedMode = False
			self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
			self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = True)
		# elif not fontListSelected and self.fontList:
		# 	print('rebuild matrix 2')
		# 	self.fontsHashKernLib = makeFontsHashGroupsLib(self.fontList, self.langSet)
		# 	self.spaceControl.setFontsHashKernLib(self.fontsHashKernLib)
		#
		# 	matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
		# 	if len(self.fontList) == 1:
		# 		self.linkedMode = False
		# 		self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
		# 	self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = False)



	def showMarginsCallback (self, sender):
		self.showInfo = not self.showInfo
		self.w.glyphsView.switchMargins( showMargins = self.showInfo)
		# self.w.groupsView.switchMargins( showMargins = self.showInfo)

	def ligthModeCallback(self, sender):
		self.lightMode = not self.lightMode
		self.w.glyphsView.switchLightMode(lightMode = self.lightMode)
		# self.w.groupsView.switchLightMode(lightMode = self.lightMode)
	def swchGlyphInfoCallback(self, sender):
		self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = sender.get())
		# self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = sender.get())

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

	def showMetricsCallback (self, sender):
		self.showMetrics = not self.showMetrics
		self.w.glyphsView.switchMetrics( showMetrics = self.showMetrics)

	def showBluesZonesCallback (self, sender):
		self.switchZones +=1
		if self.switchZones == 3: self.switchZones = 0
		if self.switchZones == 0:
			self.w.glyphsView.setStatus('zones:blue values', False)
			self.w.glyphsView.setStatus('zones:family blues', False)
			self.w.glyphsView.switchBluesZones( showBluesZones = False)
			self.w.glyphsView.switchFamilyZones(showFamilyZones = False)
		elif self.switchZones == 1:
			self.w.glyphsView.setStatus('zones:blue values', True)
			self.w.glyphsView.setStatus('zones:family blues', False)
			self.w.glyphsView.switchFamilyZones(showFamilyZones = False)
			self.w.glyphsView.switchBluesZones(showBluesZones = True)
		elif self.switchZones == 2:
			self.w.glyphsView.setStatus('zones:blue values', False)
			self.w.glyphsView.setStatus('zones:family blues', True)
			self.w.glyphsView.switchBluesZones(showBluesZones = False)
			self.w.glyphsView.switchFamilyZones(showFamilyZones = True)


	def showSkeletonCallback(self, sender):
		self.showSkeleton = not self.showSkeleton
		self.w.glyphsView.switchSkeletonMode( showSkeleton = self.showSkeleton)


	def switchBackgroundColor(self):
		if not self.warmGreyBackground:
			self.w.glyphsView.setBackgroundColor((.75, .73, .7, 1))
			# self.w.groupsView.setBackgroundColor((.75, .73, .7, 1))
			self.warmGreyBackground = True
		else:
			self.w.glyphsView.setBackgroundColor((1,1,1,1))
			# self.w.groupsView.setBackgroundColor((1,1,1,1))
			self.warmGreyBackground = False
	def switchBackgroundColorCallback(self, sender):
		self.switchBackgroundColor()

	def switchToolbar(self, enable = False):
		# pass
		if self.spaceControl.editMode == EDITMODE_KERNING:
			self.w.glyphsView.switchToolbar(enable = self.showToolbarGroupsView, imagePath = self.imageToolbar_KernMode)
		elif self.spaceControl.editMode == EDITMODE_MARGINS:
			self.w.glyphsView.switchToolbar(enable = self.showToolbarGroupsView, imagePath = self.imageToolbar_MarginsMode)

	def switchToolbarCallback(self, sender):
		self.showToolbarGroupsView = not self.showToolbarGroupsView
		self.switchToolbar(self.showToolbarGroupsView)


	def showNamesCallback(self, sender):
		if self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_WIDTH:
			self.titlesMode = SHOWTITLES_GLYPH_NAME
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			# self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)

		elif self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_NAME:
			self.showInfo = not self.showInfo
			self.w.glyphsView.switchMargins(showMargins = False)
			# self.w.groupsView.switchMargins(showMargins = False)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			# self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)

		elif not self.showInfo:
			self.showInfo = not self.showInfo
			self.titlesMode = SHOWTITLES_GLYPH_NAME
			self.w.glyphsView.switchMargins(showMargins = True)
			# self.w.groupsView.switchMargins(showMargins = True)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			# self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)


	def showWidthCallback(self, sender):
		if self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_NAME:
			self.titlesMode = SHOWTITLES_GLYPH_WIDTH
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			# self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
		elif self.showInfo and self.titlesMode == SHOWTITLES_GLYPH_WIDTH:
			self.showInfo = not self.showInfo
			self.w.glyphsView.switchMargins(showMargins = False)
			self.titlesMode = SHOWTITLES_GLYPH_NAME
			# self.w.groupsView.switchMargins(showMargins = False)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			# self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
		elif not self.showInfo:
			self.showInfo = not self.showInfo
			self.titlesMode = SHOWTITLES_GLYPH_WIDTH
			self.w.glyphsView.switchMargins(showMargins = True)
			# self.w.groupsView.switchMargins(showMargins = True)
			self.w.glyphsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)
			# self.w.groupsView.switchGlyphsInfoMode(glyphsInfo = self.titlesMode)

	def insertLineCallback(self, sender):
		# self.w.glyphsView.insertGlyphsLine()
		selected = list(self.w.glyphsView.getCurrentFont().selection)
		if not selected:
			selected = 'H H O H H O O H'.split(' ')
			self.w.eb.edit.set('HHOHHOOH')
		else:
			self.w.eb.edit.set('/' + '/'.join(selected))

		# self.glyphsInMatrix = [selected]
		self.setEditText2View()

		#
		# matrix = prepareGlyphsMatrix(self.glyphsInMatrix, self.fontList)
		# if len(self.fontList) == 1:
		# 	self.linkedMode = False
		# 	self.w.glyphsView.switchLinkedMode(linked = self.linkedMode)
		#
		# self.w.glyphsView.startDrawGlyphsMatrix(matrix, animatedStart = False)
	def btnSequencesEditorCallback(self, sender):
		se = TDGlyphSequencesEditWindow()


	def glyphsViewDoubleClickCallback(self, sender):
		font = sender.selectedFont
		glyphs = sender.selectedGlyphs
		OpenGlyphWindow(font[cutUniqName(glyphs[0])])

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
			# 'groupsview.fontsize': scale2pt(self.w.groupsView.scaleFactor),
			# 'groupsview.panelsize': self.w.groupsView.height()
		})
		# removeObserver(self, EVENT_REFRESH_ALL_OBSERVERS)
		# removeObserver(self, EVENT_OBSERVER_SETTEXT)
		unregisterCurrentGlyphSubscriber(self)

def main():
	if CurrentFont():
		registerCurrentGlyphSubscriber(TDSpaceArkTool)
	else:
		from mojo.UI import Message
		Message("No open font found..")

if __name__ == "__main__":
	main()
