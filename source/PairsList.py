
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
		self.w = vanilla.Window((340, 700), minSize = (340, 400), title = self.idName )

		self.font = CurrentFont()
		self.langSet = TDLangSet()
		self.langSet.setupPatternsForFonts(AllFonts())
		self.hashKernDic = TDHashGroupsDic(self.font, self.langSet)
		self.updateKerning = True
		self.groupPrefix = ID_KERNING_GROUP
		self.groupsSide = SIDE_1

		self.w.toolbar = vanilla.Group('auto')
		self.w.toolbar.btnSelectFont = vanilla.Button('auto','􁉽', callback = self.selectFontCallback)
		self.w.toolbar.btnAppendPairs = vanilla.Button('auto', '􀐇', callback = self.selectFontCallback) # 􀑎
		self.w.toolbar.btnSavePairs = vanilla.Button('auto', '􀈧', callback = self.selectFontCallback) # 􀈧 􀯵
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

		self.w.kernListView = TDMerzMatrixView('auto', delegate = self)
		self.w.statusBar = SimpleStatus('auto', horizontalLine=False)# textAlign='left', , textPosLeft = 0

		rules1 = [
			"H:|-0-[toolbar]-0-|",
			"H:|-0-[kernListView]-0-|",
			"H:|-0-[statusBar]-0-|",
			"V:|-border-[toolbar]-space-[kernListView]-space-[statusBar(==18)]|"
			# "V:||",
		]
		metrics1 = {
			"border": 5,
			"space": 1
		}
		self.w.toolbar.addAutoPosSizeRules(rulesTB, metrics1)
		self.w.addAutoPosSizeRules(rules1, metrics1)

		self.schemaButtons = [
			dict(name = 'buttonSide1', widthperсent = 36, value = True),
			dict(name = 'buttonSide2', widthperсent = 36, value = False),
			dict(name = 'buttonValue', widthperсent = 14, value = False),
			dict(name = 'buttonExcpt', widthperсent = 7, value = False),
			dict(name = 'buttonLangs', widthperсent = 7, value = False),
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

		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_BACKSPACE, callback = self.deleteSelectedPairs)
		self.keyCommander.registerKeyCommand(KEY_ENTER, callback = self.sendSelectedPairs2KernTool)

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

	def sendSelectedPairs2KernTool(self,sender, value):
		pairs = []
		for idx in self.w.kernListView.getSelectedSceneItems():
			pair = self.w.kernListView.getSceneItems()[idx]
			l, r = pair[0]
			sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs = pair[1]
			p1, lw, rw, p2 = list(self.langSet.wrapPairToPattern(self.font, (keyGlyphL, keyGlyphR)))
			pairs.append('/%s/%s/%s/%s' % (p1, lw, rw, p2))
		line = ''.join(pairs)
		postEvent('typedev.KernTool.observerSetText',
		          glyphsLine = line,
		          glyphsready = True,
		          targetpair = None,
		          fontID = getFontID(self.font),
		          # observerID = self.observerID)
		          )

	def deleteSelectedPairs(self, sender, value):
		pairs = []
		for idx in self.w.kernListView.getSelectedSceneItems():
			pair = self.w.kernListView.getSceneItems()[idx]
			l, r = pair[0]
			pairs.append((l,r))
		for pair in pairs:
			if pair in self.font.kerning:
				self.font.kerning.remove(pair)
		self.showKernList(glyphNames = self.kernListLastSelection)


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
			sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs = pair[1]
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
			# print('ref', l,r, _l,_r, note)
			if r.startswith(ID_KERNING_GROUP):
				grouppedR = True
				sortR = r.replace(_mask2id, '')

			if l.startswith(ID_KERNING_GROUP):
				sortL = l.replace(_mask1id, '')
				_pairslist[(l, r)] = (sortL, sortR, True, grouppedR, v, note, keyGlyphL, keyGlyphR, langs)
			else:
				_pairslist[(l, r)] = (l, sortR, False, grouppedR, v, note, keyGlyphL, keyGlyphR, langs)
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
		self.keyCommander.checkCommand(sender, event)
		sender.eventKeyDown(sender, event)

	def fontKerningDidChange(self, info):
		self.showKernList(glyphNames = self.kernListLastSelection)


	def fontGroupsDidChange(self, info):
		pass

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
