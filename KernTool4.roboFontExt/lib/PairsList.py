
import merz

from merz import *
from fontParts import *
# from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber, registerRoboFontSubscriber, registerCurrentFontSubscriber
from merz.tools.drawingTools import NSImageDrawingTools
from mojo.pens import DecomposePointPen
import AppKit
import math
import vanilla
from vanilla.dragAndDrop import dropOperationMap
import mojo
import importlib
from mojo.smartSet import getSmartSets
from vanilla.dialogs import getFile, putFile
from mojo.subscriber import Subscriber, registerCurrentFontSubscriber, unregisterCurrentFontSubscriber
from mojo.UI import SelectFont, SimpleStatus, StatusBar, LightStatusBar
from mojo.events import addObserver, removeObserver, postEvent

import tdSpaceControl
importlib.reload(tdSpaceControl)
from tdSpaceControl import *

import tdMerzMatrix
importlib.reload(tdMerzMatrix)
from tdMerzMatrix import *

import tdGlyphsMerzView
importlib.reload(tdGlyphsMerzView)
from tdGlyphsMerzView import *

import tdKeyCommander
importlib.reload(tdKeyCommander)
from tdKeyCommander import *

import tdRepresentationLib
importlib.reload(tdRepresentationLib)
from tdRepresentationLib import *

import tdLangSet
importlib.reload(tdLangSet)
from tdLangSet import *

import ScriptsBoard
importlib.reload(ScriptsBoard)
# from ScriptsBoard import main
import tdGlyphparser

# DEVELOP = True
#
# if DEVELOP:
pathForBundle = os.path.dirname(__file__)
resourcePathForBundle = os.path.join(pathForBundle, "resources")
kernToolBundle = mojo.extensions.ExtensionBundle(path=pathForBundle, resourcesName=resourcePathForBundle)
#
# else:
# 	kernToolBundle = mojo.extensions.ExtensionBundle("KernTool4")

SELECTION_MODE_ALLPAIRS_PL = 0
SELECTION_MODE_SELECTEDGLYPHS_PL = 1

FILRER_SIDE_1_PL = 0
FILTER_SIDE_BOTH_PL = 1
FILRER_SIDE_2_PL = 2

PREFKEY_PL_Patterns = '%s.KernToolUI.PairsList.Patterns' % PREFKEY_base
PREFKEY_PL_Patterns_Side1 = '%s.KernToolUI.PairsList.Patterns.Side1' % PREFKEY_base
PREFKEY_PL_Patterns_Side2 = '%s.KernToolUI.PairsList.Patterns.Side2' % PREFKEY_base
PREFKEY_PL_PairsPerLine = '%s.KernToolUI.PairsList.PPL' % PREFKEY_base
PREFKEY_PL_SendingMethod = '%s.KernToolUI.SendingMethod' % PREFKEY_base


def saveKerning (font, selectedkern, filename):
	fn = filename
	groupsfile = open(fn, mode = 'w')
	txt = ''
	for (l, r) in selectedkern:
		txt += '%s %s %s\n' % (l, r, str(font.kerning[(l, r)]))
	groupsfile.write(txt)
	groupsfile.close()


def loadKernFile (font, filename, mode='replace'):  # replace / add
	fn = filename
	if os.path.exists(fn):
		f = open(fn, mode = 'r')
		pairsimported = 0
		for line in f:
			line = line.strip()
			if not line.startswith('#') and line != '':
				left = line.split(' ')[0]
				right = line.split(' ')[1]
				value = int(round((float(line.split(' ')[2])), 0))
				fl = False
				fr = False
				if left in font.groups:
					fl = True
				if left in font:
					fl = True
				if right in font.groups:
					fr = True
				if right in font:
					fr = True
				if fl and fr:
					font.kerning[(left, right)] = value
					pairsimported += 1
				# else:
				# 	print('Group or Glyph not found:', left, right, value)

		f.close()

class TDPairsListSettingsDialogWindow(object):
	def __init__ (self, parentWindow, callback=None ):
		wW = 400
		hW = 600
		self.w = vanilla.Sheet((wW, hW), parentWindow)

		self.w.sp = vanilla.Group('auto')
		metrics1 = {
			"border": 10,
			"space": 5
		}
		self.w.sp.titlebox = vanilla.TextBox('auto', 'KernTool interaction settings')
		self.w.sp.swchPatternsBox = vanilla.Box('auto', 'Pattern separator')
		self.w.sp.swchPatternsBox.radioGroup = vanilla.VerticalRadioGroup(
			"auto",
			["Automatically - depending on the language and purpose of the glyphs", "Custom"],
			callback = self.swchPatternsBoxCallback
		)
		pboxSet = getExtensionDefault(PREFKEY_PL_Patterns, fallback = 0)
		self.w.sp.swchPatternsBox.radioGroup.set(pboxSet)
		self.w.sp.swchPatternsBox.editSide1 = vanilla.EditText('auto', placeholder = 'Side1')
		self.w.sp.swchPatternsBox.editSide2 = vanilla.EditText('auto', placeholder = 'Side2')
		self.w.sp.swchPatternsBox.editSide1.enable(False)
		self.w.sp.swchPatternsBox.editSide2.enable(False)
		if pboxSet:
			self.w.sp.swchPatternsBox.editSide1.enable(True)
			self.w.sp.swchPatternsBox.editSide2.enable(True)
			self.w.sp.swchPatternsBox.editSide1.set(getExtensionDefault(PREFKEY_PL_Patterns_Side1, fallback = ''))
			self.w.sp.swchPatternsBox.editSide2.set(getExtensionDefault(PREFKEY_PL_Patterns_Side2, fallback = ''))

		rules = [
			"H:|-[radioGroup]-|",
			"H:|-[editSide1]-border-[editSide2(==editSide1)]-|",
			"V:|-[radioGroup(==%d)]-border-[editSide1]-|" % self.w.sp.swchPatternsBox.radioGroup.getFittingHeight(),
			"V:|-[radioGroup(==%d)]-border-[editSide2]-|" % self.w.sp.swchPatternsBox.radioGroup.getFittingHeight()

		]
		self.w.sp.swchPatternsBox.addAutoPosSizeRules(rules, metrics1)

		self.w.sp.swchPPLBox = vanilla.Box('auto', 'Pairs per Line')
		segmentsGrp = [{'width': 50, 'title': '∞'},
		               {'width': 50, 'title': '1'},
		               {'width': 50, 'title': '2'},
		               {'width': 50, 'title': '3'},
		               {'width': 50, 'title': '4'},
		               {'width': 50, 'title': '5'},
		               {'width': 50, 'title': '6'},
		               {'width': 50, 'title': '7'},
		               {'width': 50, 'title': '8'},
		               ]
		self.w.sp.swchPPLBox.segmentedButton = vanilla.SegmentedButton('auto',
		                                            segmentDescriptions = segmentsGrp,
		                                            selectionStyle = 'one')
		rules = [
			"H:|-[segmentedButton]-|",
			"V:|-[segmentedButton]-|", # % self.w.sp.swchPPLBox.segmentedButton.getFittingHeight()
		]
		self.w.sp.swchPPLBox.addAutoPosSizeRules(rules)
		self.w.sp.swchPPLBox.segmentedButton.set(getExtensionDefault(PREFKEY_PL_PairsPerLine,fallback = 4))


		self.w.sp.swchGroppedBox = vanilla.Box('auto', 'Sending method')
		self.w.sp.swchGroppedBox.radioGroup = vanilla.VerticalRadioGroup(
			"auto",
			["Groupped - pairs will be represented by the first characters in the group",
			 "Expanded - pairs will be represented by a list of all possible combinations"],
			# callback = self.radioGroupCallback
		)
		self.w.sp.swchGroppedBox.radioGroup.set(getExtensionDefault(PREFKEY_PL_SendingMethod,fallback = 0))
		rules = [
			"H:|-[radioGroup]-|",
			"V:|-[radioGroup(==%d)]-|" % self.w.sp.swchGroppedBox.radioGroup.getFittingHeight()
		]
		self.w.sp.swchGroppedBox.addAutoPosSizeRules(rules)

		self.w.wc = vanilla.Group('auto')
		#
		self.w.wc.btnCancel = vanilla.Button('auto', "Cancel",callback = self.btnCloseCallback)
		self.w.wc.flex1 = vanilla.Group('auto')
		self.w.wc.btnApply = vanilla.Button('auto', "Apply",callback = self.btnCloseCallback)
		rulesSP = [
			"H:|-border-[titlebox]-border-|",
			"H:|-border-[swchPatternsBox]-border-|",
			"H:|-border-[swchPPLBox]-border-|",
			"H:|-border-[swchGroppedBox]-border-|",
			"V:|-border-[titlebox]-border-[swchPatternsBox]-border-[swchPPLBox]-border-[swchGroppedBox]-border-|",
		]
		rulesWC = [
			"H:|-border-[btnCancel]-[flex1]-[btnApply]-border-|",
			"V:|-border-[btnCancel]-border-|",
			"V:|-border-[flex1]-border-|",
			"V:|-border-[btnApply]-border-|",
		]
		rules1 = [
			"H:|-border-[sp]-border-|",
			"H:|-border-[wc]-border-|",
			"V:|-border-[sp]-border-[wc]-border-|",  #-[sp]-space
		]
		self.w.sp.addAutoPosSizeRules(rulesSP, metrics1)
		self.w.wc.addAutoPosSizeRules(rulesWC, metrics1)
		self.w.addAutoPosSizeRules(rules1, metrics1)
		self.w.open()

	def btnCloseCallback(self, sender):
		if sender == self.w.wc.btnApply:
			useCustomPatterns = self.w.sp.swchPatternsBox.radioGroup.get()
			setExtensionDefault(PREFKEY_PL_Patterns, useCustomPatterns)
			if useCustomPatterns:
				setExtensionDefault(PREFKEY_PL_Patterns_Side1, self.w.sp.swchPatternsBox.editSide1.get())
				setExtensionDefault(PREFKEY_PL_Patterns_Side2, self.w.sp.swchPatternsBox.editSide2.get())
			setExtensionDefault(PREFKEY_PL_PairsPerLine, self.w.sp.swchPPLBox.segmentedButton.get())
			setExtensionDefault(PREFKEY_PL_SendingMethod, self.w.sp.swchGroppedBox.radioGroup.get())
		self.w.close()

	def swchPatternsBoxCallback(self, sender):
		if sender.get():
			self.w.sp.swchPatternsBox.editSide1.enable(True)
			self.w.sp.swchPatternsBox.editSide2.enable(True)
		else:
			self.w.sp.swchPatternsBox.editSide1.enable(False)
			self.w.sp.swchPatternsBox.editSide2.enable(False)


class TDPairsListControl4(Subscriber): #, WindowController

	debug = True
	# fontDidChangeDelay = 0

	def build (self):
		darkm = ''
		KERNTOOL_UI_DARKMODE = False
		dark = AppKit.NSAppearance.appearanceNamed_(AppKit.NSAppearanceNameDarkAqua)
		if AppKit.NSApp().appearance() == dark:
			KERNTOOL_UI_DARKMODE = True
		if KERNTOOL_UI_DARKMODE:
			darkm = '-dark'
		self.idName = 'PairsList'
		self.w = vanilla.Window((370, 700), minSize = (340, 400), title = self.idName )

		self.font = CurrentFont()
		self.langSet = TDLangSet()
		self.langSet.setupPatternsForFonts(AllFonts())
		self.hashKernDic = TDHashGroupsDic(self.font, self.langSet)
		self.updateKerning = True
		self.groupPrefix = ID_KERNING_GROUP
		self.groupsSide = SIDE_1

		self.w.toolbar = vanilla.Group('auto')
		self.w.toolbar.btnSelectFont = vanilla.Button('auto','􁉽', callback = self.selectFontCallback)
		self.w.toolbar.btnAppendPairs = vanilla.Button('auto', '􀐇', callback = self.appendPairsFromFileCallback) # 􀑎
		self.w.toolbar.btnSavePairs = vanilla.Button('auto', '􀈧', callback = self.saveSelectedPairsToFileCallback) # 􀈧 􀯵
		self.w.toolbar.flex1 = vanilla.Group('auto')
		segments1 = [{'width': 0, 'title': '􀌃'}, {'width': 0, 'title': '􀝰'}] # 􀚇 􀇵 􀂔 􀇷 􀉆 􀕹 􀊫
		self.w.toolbar.btnSwitchSelection = vanilla.SegmentedButton('auto',
		                                               segmentDescriptions = segments1,
		                                               selectionStyle = 'one',
		                                               callback = self.switchSelectionCallback,
		                                               sizeStyle = 'regular')


		self.w.toolbar.flex2 = vanilla.Group('auto')
		segments2 = [{'width': 0, 'title': '􀤶'}, {'width': 0, 'title': '􀧉'}, {'width': 0, 'title': '􀤷'}]
		self.w.toolbar.btnSwitchSide = vanilla.SegmentedButton('auto',
		                                                           segmentDescriptions = segments2,
		                                                           selectionStyle = 'one',
		                                                           callback = self.switchFilterSideCallback,
		                                                           sizeStyle = 'regular')

		self.w.toolbar.btnSwitchSelection.set(SELECTION_MODE_ALLPAIRS_PL)
		self.selectionMode = SELECTION_MODE_ALLPAIRS_PL

		self.w.toolbar.btnSwitchSide.set(FILTER_SIDE_BOTH_PL)
		self.filterMode = FILTER_SIDE_BOTH_PL
		self.w.toolbar.btnSwitchSide.enable(False)
		self.w.toolbar.flex3 = vanilla.Group('auto')

		self.w.toolbar2 = vanilla.Group('auto')
		self.w.toolbar2.btnDelete = vanilla.Button('auto', '􀈑', callback = self.deleteSelectedPairsCallback)
		self.w.toolbar2.flex1 = vanilla.Group('auto')
		self.w.toolbar2.btnSettings = vanilla.Button('auto', '􀌆', callback = self.openSettingsDialogCallback)

		self.w.toolbar2.btnSend2KernTool = vanilla.Button('auto', '􀻵', callback = self.sendSelectedPairs2KernToolCallback)


		rulesTB = [
			"H:|-border-[btnSelectFont]-border-[btnAppendPairs]-border-[btnSavePairs]-[flex1]-[btnSwitchSelection]-[flex2(==flex1)]-[btnSwitchSide]-border-|",
			"V:|-space-[btnSelectFont]-border-|",
			"V:|-space-[btnAppendPairs]-border-|",
			"V:|-space-[btnSavePairs]-border-|",
			"V:|-space-[flex1]-border-|",
			"V:|-space-[btnSwitchSelection]-border-|",
			"V:|-space-[flex2]-border-|",
			"V:|-space-[btnSwitchSide]-border-|",
			"V:|-space-[flex3]-border-|"
		]

		rulesTB2 = [
			"H:|-border-[btnDelete]-[flex1]-[btnSettings]-border-[btnSend2KernTool(==80)]-border-|",
			"V:|-border-[btnDelete]-border-|",
			"V:|-border-[flex1]-border-|",
			"V:|-border-[btnSettings]-border-|",
			"V:|-border-[btnSend2KernTool]-border-|",
		]

		self.w.kernListView = TDMerzMatrixView('auto', delegate = self)
		self.w.statusBar = SimpleStatus('auto', horizontalLine=False)# textAlign='left', , textPosLeft = 0

		rules1 = [
			"H:|-0-[toolbar]-0-|",
			"H:|-0-[kernListView]-0-|",
			"H:|-0-[toolbar2]-0-|",
			"H:|-0-[statusBar]-0-|",
			"V:|-border-[toolbar]-space-[kernListView]-space-[toolbar2]-space-[statusBar(==18)]|"
			# "V:||",
		]
		metrics1 = {
			"border": 5,
			"space": 1
		}
		self.w.toolbar.addAutoPosSizeRules(rulesTB, metrics1)
		self.w.toolbar2.addAutoPosSizeRules(rulesTB2, metrics1)
		self.w.addAutoPosSizeRules(rules1, metrics1)

		self.schemaButtons = [
			dict(name = 'buttonSide1', widthperсent = 32, value = True),
			dict(name = 'buttonSide2', widthperсent = 32, value = False),
			dict(name = 'buttonValue', widthperсent = 15, value = False),
			dict(name = 'buttonExcpt', widthperсent = 7, value = False),
			dict(name = 'buttonLangs', widthperсent = 7, value = False),
			dict(name = 'buttonError', widthperсent = 7, value = False),
		]

		self.kernList = self.w.kernListView.setupScene(
			layerWillDrawCallback = self.layerKernWillDrawCallback,
			selectLayerCallback = self.selectPairLayerCallback,
			# dropCallback = self.dropContentCallback,
			clearHash = True,
			# dropStyle = DROP_STYLE_SCENE,
			elementSize = (0, 18),
			elementMargins = (0, 0),
			backgroundColor = (1, 1, 1, 1), #(.75, .73, .7, 1), #
			selectedBorderColor = (0, 0, 0, 0),
			selectionColor = (.8, .8, .82, .8),
			controlsColor = (.2, .3, .4, 1),
			cornerRadius = 0,
			focusColor = (.7, .7, .72, .8)
		)

		self.kernListButtons = {}
		self.kernListSortOrder = 'buttonSide1'
		self.kernListSortReverse = False
		self.kernListPairs = {}
		self.kernListLastSelection = None

		self.w.kernListView.addControlElement(name = 'buttonSide1', callback = self.sortingButtonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonSide2', callback = self.sortingButtonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonValue', callback = self.sortingButtonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonExcpt', callback = self.sortingButtonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonLangs', callback = self.sortingButtonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonError', callback = self.sortingButtonCallback, drawingMethod = self.drawSortingButton)

		# self.keyCommander = TDKeyCommander()
		# self.keyCommander.registerKeyCommand(KEY_BACKSPACE, callback = self.deleteSelectedPairs)
		# self.keyCommander.registerKeyCommand(KEY_ENTER, callback = self.sendSelectedPairs2KernTool)

		self.pointSize = 10
		self.ScriptsBoardWindow = None

	def started (self):
		addObserver(self, "glyphChanged", "currentGlyphChanged")
		self.w.bind('close', self.windowCloseCallback)
		self.w.open()
		self.w.setTitle('%s - %s %s' % (self.idName, self.font.info.familyName, self.font.info.styleName))
		self.showKernList()
		# self.scenesSelector.setSelectedScene(self.kernList)

	def glyphChanged(self, info):
		if self.selectionMode == SELECTION_MODE_SELECTEDGLYPHS_PL:
			self.showKernList(glyphNames = list(self.font.selection))

	def saveSelectedPairsToFileCallback(self, sender):
		pairsfile = putFile(messageText = 'Save selected pairs to text file', title = 'Pairs List')
		if pairsfile:
			pairs = []
			if self.w.kernListView.getSelectedSceneItems():
				selection = self.w.kernListView.getSelectedSceneItems()
			else:
				selection = [idx for idx in range(0, len(self.w.kernListView.getSceneItems()))]
			for idx in selection:
				pair = self.w.kernListView.getSceneItems()[idx]
				l, r = pair[0]
				pairs.append((l, r))
			saveKerning(self.font, pairs, pairsfile)

	def appendPairsFromFileCallback(self, sender):
		pairsfile = getFile(messageText = 'Append pairs from file', title = 'Pairs List')
		if pairsfile:
			loadKernFile(self.font, pairsfile[0])
			self.showKernList()



	def sendSelectedPairs2KernTool(self):
		useCustomPatterns = getExtensionDefault(PREFKEY_PL_Patterns, fallback = 0)
		LPattern = ''
		RPattern = ''
		if useCustomPatterns:
			side1 = getExtensionDefault(PREFKEY_PL_Patterns_Side1, fallback = ' ')
			side2 = getExtensionDefault(PREFKEY_PL_Patterns_Side2, fallback = ' ')
			patternLeft = tdGlyphparser.translateText(font = self.font, text = side1)
			patternRight = tdGlyphparser.translateText(font = self.font, text = side2)
			if patternLeft:
				for l in patternLeft:
					if l != '':
						LPattern += '/%s' % l
			if patternRight:
				for r in patternRight:
					if r != '':
						RPattern += '/%s' % r
		ppl = getExtensionDefault(PREFKEY_PL_PairsPerLine, fallback = 4)
		sendingMethodExpanded = getExtensionDefault(PREFKEY_PL_SendingMethod, fallback = 0)

		line = ''
		pairscount = 0
		cl = None
		cr = None
		if sendingMethodExpanded:
			for idx in self.w.kernListView.getSelectedSceneItems():
				pair = self.w.kernListView.getSceneItems()[idx]
				l, r = pair[0]
				lgroup = [l]
				rgroup = [r]
				if l.startswith(ID_KERNING_GROUP):
					lgroup = self.font.groups[l]

				if r.startswith(ID_KERNING_GROUP):
					rgroup = self.font.groups[r]

				for side1glyph in lgroup:
					for side2glyph in rgroup:
						if side1glyph in self.font and side2glyph in self.font:
							p1, lw, rw, p2 = list(self.langSet.wrapPairToPattern(self.font, (side1glyph, side2glyph)))
							if idx == 0:
								cl = side1glyph
								cr = side2glyph
							if useCustomPatterns:
								p1 = LPattern
								p2 = RPattern
							else:
								p1 = '/%s' % p1
								p2 = '/%s' % p2
							line += '%s/%s/%s%s' % (p1, lw, rw, p2)
							pairscount += 1
							if ppl and pairscount == ppl:
								line += '\\n'
								pairscount = 0
		else:
			for idx in self.w.kernListView.getSelectedSceneItems():
				pair = self.w.kernListView.getSceneItems()[idx]
				l, r = pair[0]
				sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs, hasError = pair[1]
				if keyGlyphL in self.font and keyGlyphR in self.font:
					p1, lw, rw, p2 = list(self.langSet.wrapPairToPattern(self.font, (keyGlyphL, keyGlyphR)))
					if idx == 0:
						cl = keyGlyphL
						cr = keyGlyphR
					if useCustomPatterns:
						p1 = LPattern
						p2 = RPattern
					else:
						p1 = '/%s' % p1
						p2 = '/%s' % p2
					line += '%s/%s/%s%s' % (p1, lw, rw, p2)
					pairscount += 1
					if ppl and pairscount == ppl:
						line += '\\n'
						pairscount = 0
		postEvent('typedev.KernTool.observerSetText',
		          glyphsLine = line,
		          glyphsready = True,
		          targetpair = (cl, cr),
		          fontID = getFontID(self.font),
		          # observerID = self.observerID)
		          )

	def sendSelectedPairs2KernToolCallback(self, sender): # , value
		self.sendSelectedPairs2KernTool()

	def deleteSelectedPairs(self):
		pairs = []
		for idx in self.w.kernListView.getSelectedSceneItems():
			pair = self.w.kernListView.getSceneItems()[idx]
			l, r = pair[0]
			pairs.append((l, r))
		for pair in pairs:
			if pair in self.font.kerning:
				self.font.kerning.remove(pair)
		self.showKernList(glyphNames = self.kernListLastSelection)

	def deleteSelectedPairsCallback(self, sender): # , value
		self.deleteSelectedPairs()

	def openSettingsDialogCallback(self, sender):
		TDPairsListSettingsDialogWindow(parentWindow = self.w)


	def switchSelectionCallback(self, sender):
		if sender.get() == 0:
			self.selectionMode = SELECTION_MODE_ALLPAIRS_PL
			self.w.toolbar.btnSwitchSide.enable(False)
			self.showKernList()
		elif sender.get() == 1:
			self.selectionMode = SELECTION_MODE_SELECTEDGLYPHS_PL
			self.w.toolbar.btnSwitchSide.enable(True)
			self.showKernList(glyphNames = list(self.font.selection))

	def switchFilterSideCallback(self, sender):
		if sender.get() == 0:
			self.filterMode = FILRER_SIDE_1_PL
		elif sender.get() == 1:
			self.filterMode = FILTER_SIDE_BOTH_PL
		elif sender.get() == 2:
			self.filterMode = FILRER_SIDE_2_PL
		self.showKernList(glyphNames = self.kernListLastSelection)

	def selectPairLayerCallback(self, sender, info):
		pairs = []
		for idx in self.w.kernListView.getSelectedSceneItems():
			pair = self.w.kernListView.getSceneItems()[idx]
			l,r = pair[0]
			sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs, hasError = pair[1]
			pairwrapped = list(self.langSet.wrapPairToPattern(self.font,(keyGlyphL,keyGlyphR)))
			pairs.extend(pairwrapped)
		self.w.statusBar.set(['pairs: %i | viewed: %i | selected: %i' % (
		len(self.font.kerning), len(self.w.kernListView.getSceneItems()), len(self.w.kernListView.getSelectedSceneItems()))])


	def layerKernWillDrawCallback(self, sender, info):
		container = info['layer']
		index = info['index']
		pair = info['item']
		mode = info['drawmode']
		# if not container.getSublayers():
		drawKernPairListed(container, self.font, self.schemaButtons, self.hashKernDic, pair, mode)

	def sortingButtonCallback(self, eventname, point, nameButton):
		if eventname =='mouseUp':
			pairsselected = []
			for idx in self.w.kernListView.getSelectedSceneItems():
				pairsselected.append(self.w.kernListView.getSceneItems()[idx][0])

			if self.kernListSortOrder == nameButton:
				self.kernListSortReverse = not self.kernListSortReverse
			else:
				self.kernListSortReverse = False
			self.kernListSortOrder = nameButton

			p = self.makeSortedList(self.kernListPairs, self.kernListSortOrder, self.kernListSortReverse)
			self.w.kernListView.setSceneItems(items = p)
			selection = []
			for idx, p in enumerate(self.w.kernListView.getSceneItems()):
				if p[0] in pairsselected:
					selection.append(idx)
			if selection:
				self.w.kernListView.setSelection(itemsIndexes = selection)
			# else:
			# 	self.w.kernListView.setSelection(itemsIndexes = [0], selected = False, animate = True)
				# self.w.kernListView.setSelection(itemsIndexes = [0], selected = False)
				# self.w.kernListView.setSelection(itemsIndexes = [0])

	def drawSortingButton(self, container, nameButton):
		drawKernListSortButton(container, nameButton, self.kernListSortOrder, self.kernListSortReverse, self.schemaButtons)


	def makeSortedList(self, pairslist = None, order = 'left', reverse = False):
		_pairslist = {}
		_mask1id = 'public.kern1.'#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_DIRECTION_POSITION_LEFT
		_mask2id = 'public.kern2.'#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_DIRECTION_POSITION_RIGHT

		for (l,r) in pairslist:
			# (l, r) = pair
			# if pair not in self.font.kerning: return
			v = self.font.kerning[(l,r)]
			keyGlyphL = self.hashKernDic.getKeyGlyphByGroupname(l)  # idGlyphL
			keyGlyphR = self.hashKernDic.getKeyGlyphByGroupname(r)
			# if keyGlyphL and keyGlyphR:
			# note, _l, _r = getKernPairInfo_v2(self.font, self.hashKernDic, (l, r))
			pair = researchPair(self.font, self.hashKernDic, (keyGlyphL, keyGlyphR))
			note = 0
			if pair['exception']:
				if pair['L_realName'] != pair['L_nameForKern'] and pair['R_realName'] == pair['R_nameForKern']:
					note = 1
				elif pair['R_realName'] != pair['R_nameForKern'] and pair['L_realName'] == pair['L_nameForKern']:
					note = 2
				else:
					note = 3
			langs = 0
			if not self.hashKernDic.checkPairLanguageCompatibilityGroupped((l,r), level = 1):
				langs = 1
			elif not self.hashKernDic.checkPairLanguageCompatibilityGroupped((l,r), level = 2):
				langs = 2
			grouppedR = False
			sortR = r
			hasError = 0
			# print('ref', l,r, _l,_r, note)
			if r.startswith(ID_KERNING_GROUP):
				grouppedR = True
				sortR = r.replace(_mask2id, '')
				if r in self.hashKernDic.groupsHasErrorList:
					hasError = 20
			else:
				if r not in self.font:
					hasError = 25

			if l.startswith(ID_KERNING_GROUP):
				sortL = l.replace(_mask1id, '')
				if l in self.hashKernDic.groupsHasErrorList:
					hasError = 10
				_pairslist[(l, r)] = (sortL, sortR, True, grouppedR, v, note, keyGlyphL, keyGlyphR, langs, hasError)
			else:
				if l not in self.font:
					hasError = 15
				_pairslist[(l, r)] = (l, sortR, False, grouppedR, v, note, keyGlyphL, keyGlyphR, langs, hasError)
			# else:
			# 	print ('kerning has error', (l,r), (keyGlyphL,keyGlyphR))

		# return self.resortKernList(_pairslist, order, reverse)

	# def resortKernList(self, pairslist, order, reverse):
		if not _pairslist: return []
		if order == 'buttonSide1':
			return sorted(_pairslist.items(), key = lambda p: (p[1][0] , p[1][1]), reverse = reverse ) # , p[1][1]
		elif order == 'buttonSide2':
			return sorted(_pairslist.items(), key = lambda p: (p[1][1] , p[1][0]), reverse = reverse) # , p[1][0]
		elif order == 'buttonValue':
			return sorted(_pairslist.items(), key = lambda p: (p[1][4]), reverse = reverse) #, p[1][0] , p[1][1]
		elif order == 'buttonExcpt':
			reverse = not reverse
			return sorted(_pairslist.items(), key = lambda p: (p[1][5]), reverse = reverse) #, p[1][0], p[1][1]
		elif order == 'buttonLangs':
			reverse = not reverse
			return sorted(_pairslist.items(), key = lambda p: (p[1][8]), reverse = reverse) #, p[1][0], p[1][1]
		elif order == 'buttonError':
			reverse = not reverse
			return sorted(_pairslist.items(), key = lambda p: (p[1][9]), reverse = reverse) #, p[1][0], p[1][1]


	def showKernList(self, glyphNames = None):
		self.kernListLastSelection = glyphNames
		pairsselected = []
		pairs = []
		for idx in self.w.kernListView.getSelectedSceneItems():
			pairsselected.append(self.w.kernListView.getSceneItems()[idx][0])
		self.w.kernListView.setSceneItems(items = [])

		if glyphNames:
			pairs = []
			_pairs = None
			for name in glyphNames:
				if self.filterMode == FILRER_SIDE_1_PL:
					_pairs = self.hashKernDic.getPairsBy(name, SIDE_1)
					gname = self.hashKernDic.getGroupNameByGlyph(name, side = SIDE_1)
					if gname != name:
						_pairsG = self.hashKernDic.getPairsBy(gname, SIDE_1)
						_pairs += _pairsG

				elif self.filterMode == FILRER_SIDE_2_PL:
					_pairs = self.hashKernDic.getPairsBy(name, SIDE_2)
					gname = self.hashKernDic.getGroupNameByGlyph(name, side = SIDE_2)
					if gname != name:
						_pairsG = self.hashKernDic.getPairsBy(gname, SIDE_2)
						_pairs += _pairsG

				elif self.filterMode == FILTER_SIDE_BOTH_PL:
					_pairs1 = self.hashKernDic.getPairsBy(name, SIDE_1)
					gname = self.hashKernDic.getGroupNameByGlyph(name, side = SIDE_1)
					if gname != name:
						_pairsG = self.hashKernDic.getPairsBy(gname, SIDE_1)
						_pairs1 += _pairsG

					_pairs2 = self.hashKernDic.getPairsBy(name, SIDE_2)
					gname = self.hashKernDic.getGroupNameByGlyph(name, side = SIDE_2)
					if gname != name:
						_pairsG = self.hashKernDic.getPairsBy(gname, SIDE_2)
						_pairs2 += _pairsG

					_pairs = _pairs1 + _pairs2
				pairs.extend(pair for pair, value in _pairs)
			self.kernListPairs = pairs
		else:
			self.kernListPairs = self.font.kerning.keys()
		p = self.makeSortedList(self.kernListPairs, self.kernListSortOrder, self.kernListSortReverse)
		self.w.kernListView.setSceneItems(items = p)  # , animated = 'bottom'

		selection = []
		for idx, p in enumerate(self.w.kernListView.getSceneItems()):
			if p[0] in pairsselected:
				selection.append(idx)
		self.w.kernListView.setSelection(itemsIndexes = selection)
		self.w.statusBar.set(['pairs: %i | viewed: %i | selected: %i' % (len(self.font.kerning),len(self.w.kernListView.getSceneItems()),len(self.w.kernListView.getSelectedSceneItems()))])

	def selectFontCallback(self, sender):
		font = SelectFont(title = self.idName)
		if font:
			self.w.setTitle('%s - %s %s' % (self.idName, self.font.info.familyName, self.font.info.styleName))

			self.w.kernListView.setSceneItems(items = [])
			self.hashKernDic.clearHistory()
			self.font = font
			# self.langSet = TDLangSet()
			self.langSet.setupPatternsForFont(self.font)
			self.hashKernDic.setFont(self.font, self.langSet)

			self.w.toolbar.btnSwitchSelection.set(SELECTION_MODE_ALLPAIRS_PL)
			self.selectionMode = SELECTION_MODE_ALLPAIRS_PL

			self.w.toolbar.btnSwitchSide.set(FILTER_SIDE_BOTH_PL)
			self.filterMode = FILTER_SIDE_BOTH_PL
			self.w.toolbar.btnSwitchSide.enable(False)

			self.showKernList()


	def windowCloseCallback(self, sender):
		removeObserver(self, "currentGlyphChanged")
		merz.SymbolImageVendor.unregisterImageFactory(TDPairsListGroupSymbol)
		self.w.kernListView.clearScene()
		if self.ScriptsBoardWindow:
			self.ScriptsBoardWindow.close()
		unregisterCurrentFontSubscriber(self)

	def keyDown (self, sender, event):
		# self.keyCommander.checkCommand(sender, event)
		sender.eventKeyDown(sender, event)

	def fontKerningDidChange(self, info):
		self.showKernList(glyphNames = self.kernListLastSelection)


	def fontGroupsDidChange(self, info):
		self.hashKernDic.setFont(self.font, self.langSet)
		self.showKernList(glyphNames = self.kernListLastSelection)

	# def fontKerningDidChangePair(self, info):
	# 	print('fontKerningDidChangePair', info)


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


def main():
	registerCurrentFontSubscriber(TDPairsListControl4)
if __name__ == "__main__":
	main()
