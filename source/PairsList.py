
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
from mojo.UI import SelectFont

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
		self.w = vanilla.Window((340, 800), minSize = (340, 400), title = self.idName )

		# toolbarItems = [
		# 	{
		# 		'itemIdentifier': "toolbarSelectFonts",
		# 		'label': 'Select Font',
		# 		'callback': self.selectFontCallback,
		# 		'imagePath': os.path.join(kernToolBundle.resourcesPath(), 'tb_selectfont%s.pdf' % darkm),
		# 	},
		# 	{
		# 		'itemIdentifier': AppKit.NSToolbarSpaceItemIdentifier,
		# 	},
		#
		#
		# ]
		# self.w.addToolbar("PairsListControlToolbar", toolbarItems)
		# # self.w.getNSWindow().toolbar().setSelectedItemIdentifier_('toolbarSide1')

		self.font = CurrentFont()
		self.langSet = TDLangSet()
		self.langSet.setupPatternsForFonts(AllFonts())
		self.hashKernDic = TDHashGroupsDic(self.font, self.langSet)
		self.updateKerning = True
		self.groupPrefix = ID_KERNING_GROUP
		self.groupsSide = SIDE_1

		# defaultSets = getSmartSets()
		# fontSets = getSmartSets(self.font)
		# glyphsSets = ['All Glyphs']
		# glyphsSets.extend([gset.name for gset in defaultSets])
		# glyphsSets.extend([gset.name for gset in fontSets])

		self.w.kernListView = TDMerzMatrixView('auto', delegate = self)

		rules1 = [
			"H:|-0-[kernListView]-0-|",
			"V:|-0-[kernListView]-0-|"
			# "V:||",
		]
		metrics1 = {
			"border": 1,
			"space": 1
		}
		self.w.addAutoPosSizeRules(rules1, metrics1)

		self.schemaButtons = {
			'buttonSide1': dict(xpos = 15 + 5, ypos = 'top', width = 100, value = True),
			'buttonSide2': dict(xpos = 15 + 5 + 100 + 5, ypos = 'top',width = 100, value = False),
			'buttonValue': dict(xpos = 15 + 5 + 100 + 5 + 100 + 5, ypos = 'top',width = 40, value = False),
			'buttonExcpt': dict(xpos = 15 + 5 + 100 + 5 + 100 + 5 + 40 + 5, ypos = 'top',width = 20, value = False),
			'buttonLangs': dict(xpos = 15 + 5 + 100 + 5 + 100 + 5 + 40 + 5 + 20 + 5, ypos = 'top',width = 20, value = False),
			# 'buttonDelete': dict(xpos = 15 + 5, ypos = 'bottom', width = 100, value = False),
		}

		self.kernList = self.w.kernListView.setupScene(
			layerWillDrawCallback = self.layerKernWillDrawCallback,
			selectLayerCallback = self.selectPairLayerCallback,
			# dropCallback = self.dropContentCallback,
			clearHash = False,
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

		self.scenesSelector = TDScenesSelector()
		self.scenesSelector.addScene(self.kernList, self.w.kernListView)

		self.kernListButtons = {}
		self.kernListSortOrder = 'buttonSide1'
		self.kernListSortReverse = False
		self.kernListPairs = {}
		self.kernListLastSelection = None

		# self.selectedScene = self.sceneGroups
		# self.scenesSelector.selectedScene(self.sceneGroups)

		self.w.kernListView.addControlElement(name = 'buttonSide1', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonSide2', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonValue', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonExcpt', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.kernListView.addControlElement(name = 'buttonLangs', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)

		self.pointSize = 10
		self.ScriptsBoardWindow = None

	def started (self):
		self.w.bind('close', self.windowCloseCallback)
		self.w.open()
		self.w.setTitle('%s - %s %s' % (self.idName, self.font.info.familyName, self.font.info.styleName))

		self.showKernList()
		self.scenesSelector.setSelectedScene(self.kernList)

	def selectPairLayerCallback(self, sender, info):
		self.scenesSelector.setSelectedScene(self.kernList)

		pairs = []
		for idx in self.w.kernListView.getSelectedSceneItems():
			pair = self.w.kernListView.getSceneItems()[idx]
			l,r = pair[0]
			sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs = pair[1]
			pairwrapped = list(self.langSet.wrapPairToPattern(self.font,(keyGlyphL,keyGlyphR)))
			pairs.extend(pairwrapped)


	def layerKernWillDrawCallback(self, sender, info):
		container = info['layer']
		index = info['index']
		pair = info['item']
		if not container.getSublayers():
			drawKernPairListed(container, self.font, self.schemaButtons, self.hashKernDic, pair)

	def buttonCallback(self, eventname, point, nameButton):
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
			self.w.kernListView.setSelection(itemsIndexes = selection)


	def drawSortingButton(self, container, nameButton):
		if not container: return
		drawKernListControlButton(container, nameButton, self.kernListSortOrder, self.kernListSortReverse, self.schemaButtons)

	def makeSortedList(self, pairslist = None, order = 'left', reverse = False):
		# if not pairslist:
		# 	pairslist = self.db
		# # self.indexList = {}
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


	def showKernList(self, groupname = None, glyphName = None):
		self.kernListLastSelection = (groupname, glyphName)
		pairsselected = []
		pairs = []
		for idx in self.w.kernListView.getSelectedSceneItems():
			pairsselected.append(self.w.kernListView.getSceneItems()[idx][0])

		self.w.kernListView.setSceneItems(items = [])
		# if groupname:
		# 	groupnames = [groupname]
		# 	if len(self.w.g1.groupView.getSelectedSceneItems()) > 1:
		# 		groupnames =[]
		# 		for idx in self.w.g1.groupView.getSelectedSceneItems():
		# 			gn = self.w.g1.groupView.getSceneItems()[idx]
		# 			groupnames.append(gn)
		# 	pairs = []
		# 	for groupname in groupnames:
		# 		_pairs = self.hashKernDic.getPairsBy(groupname, self.groupsSide)
		# 		pairs.extend(pair for pair, value in _pairs)
		# 		if len(self.font.groups[groupname]) != 0:
		# 			for glyphname in self.font.groups[groupname]:
		# 				_pairs = self.hashKernDic.getPairsBy(glyphname, self.groupsSide)
		# 				if _pairs:
		# 					pairs.extend(pair for pair, value in _pairs)
		#
		# if glyphName:
		# 	glyphNames = [glyphName]
		# 	if len(self.w.g1.fontView.getSelectedSceneItems()) > 1:
		# 		glyphNames = []
		# 		for idx in self.w.g1.fontView.getSelectedSceneItems():
		# 			gn = self.w.g1.fontView.getSceneItems()[idx]
		# 			glyphNames.append(gn)
		# 	pairs = []
		# 	for glyphName in glyphNames:
		# 		_pairs = self.hashKernDic.getPairsBy(glyphName, self.groupsSide)
		# 		pairs.extend(pair for pair, value in _pairs)

		self.kernListPairs = self.font.kerning.keys()
		p = self.makeSortedList(self.kernListPairs, self.kernListSortOrder, self.kernListSortReverse)
		self.w.kernListView.setSceneItems(items = p)  # , animated = 'bottom'

		selection = []
		for idx, p in enumerate(self.w.kernListView.getSceneItems()):
			if p[0] in pairsselected:
				# print ('sel', p)
				selection.append(idx)
		self.w.kernListView.setSelection(itemsIndexes = selection)

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
			self.showKernList()


	def windowCloseCallback(self, sender):
		self.w.kernListView.clearScene()
		if self.ScriptsBoardWindow:
			self.ScriptsBoardWindow.close()
		unregisterCurrentFontSubscriber(self)

	def keyDown (self, sender, event):
		sender.eventKeyDown(sender, event)

	def fontKerningDidChange(self, info):
		# TODO need rewrite.. need just update current kern list state
		# print('fontKerningDidChange IN')
		group, glyph = self.kernListLastSelection
		self.showKernList(groupname = group, glyphName = glyph)
		# if self.scenesSelector.getSelectedScene() == self.sceneGroups or self.scenesSelector.getSelectedScene() == self.sceneGroupContent or self.scenesSelector.getSelectedScene() == self.kernList:
		# 	print('fontKerningDidChange 1')
		# 	self.showKernList(groupname = self.selectedGroup)
		# elif self.scenesSelector.getSelectedScene() == self.sceneFont and self.w.g1.fontView.getSelectedSceneItems():
		# 	print('fontKerningDidChange 2')
		# 	self.showKernList(glyphName = self.w.g1.fontView.getSceneItems()[ self.w.g1.fontView.getSelectedSceneItems()[-1] ])

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
