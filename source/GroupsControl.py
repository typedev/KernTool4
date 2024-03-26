
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
from mojo.UI import SelectFont, AskString
from mojo.events import postEvent
from vanilla.vanillaBase import osVersionCurrent, osVersion10_14

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

import tdHistoryController
importlib.reload(tdHistoryController)

# from ScriptsBoard import main


DEVELOP = False

if DEVELOP:
	pathForBundle = os.path.dirname(__file__)
	RESOURCES_FOLDER = os.path.join(pathForBundle, "resources")
	print(DEVELOP, RESOURCES_FOLDER)
else:
	kernToolBundle = mojo.extensions.ExtensionBundle("KernTool4")
	RESOURCES_FOLDER = str(kernToolBundle.resourcesFolder).replace('resources', 'lib/resources')

class TDGroupsControl4(Subscriber): #, WindowController

	debug = True
	# fontDidChangeDelay = 0

	def build (self):
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
		self.idName = 'GroupsControl4'
		self.w = vanilla.Window((1250, 800), minSize = (400, 600), title = self.idName )

		toolbarItems = [
			{
				'itemIdentifier': "toolbarSelectFonts",
				'label': 'Select Font',
				'callback': self.selectFontCallback,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_selectfont%s.pdf' % darkm),
			},
			{
				'itemIdentifier': AppKit.NSToolbarSpaceItemIdentifier,
			},
			# {
			# 	'itemIdentifier': "toolbarMarginsGroup",
			# 	'label': 'Margins Groups',
			# 	'callback': self.allCallbacks,
			# 	'selectable': True,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_margins_groups%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': "toolbarKerningGroup",
			# 	'label': 'Kerning Groups',
			# 	'callback': self.allCallbacks,
			# 	'selectable': True,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_kerning_groups%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			# },
			{
				'itemIdentifier': "toolbarImportGroup",
				'label': 'Import Groups',
				'callback': self.importGroupsCallback,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_import_groups%s.pdf' % darkm),
			},
			{
				'itemIdentifier': "toolbarExportGroup",
				'label': 'Export Groups',
				'callback': self.exportGroupsCallback,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_export_groups%s.pdf' % darkm),
			},
			{
				'itemIdentifier': AppKit.NSToolbarSpaceItemIdentifier,
			},
			# {
			# 	'itemIdentifier': "toolbarImportHistory",
			# 	'label': 'Load History',
			# 	'callback': self.importHistory,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_import_history%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': "toolbarExportHistory",
			# 	'label': 'Save History',
			# 	'callback': self.exportHistory,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_export_history%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': "toolbarHistoryController",
			# 	'label': 'History',
			# 	'callback': self.callHistoryController,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_history%s.pdf' % darkm),
			# },
			# # {
			# # 	'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			# # },
			# {
			# 	'itemIdentifier': AppKit.NSToolbarSpaceItemIdentifier,
			# },
			{
				'itemIdentifier': "toolbarAddGroup",
				'label': 'Add Group',
				'callback': self.addGroupCallbacks,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_add_group%s.pdf' % darkm),
				'toolTip': 'Create a group from the selected glyphs'
			},
			{
				'itemIdentifier': "toolbarAddMultiGroup",
				'label': 'Сreate groups',
				'callback': self.addGroupByListCallbacks,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_add_multigroups%s.pdf' % darkm),
				'toolTip': 'Create a group for each of the selected glyphs'
			},
			{
				'itemIdentifier': AppKit.NSToolbarSpaceItemIdentifier,
			},
			{
				'itemIdentifier': "toolbarDeleteGroup",
				'label': 'Delete Group',
				'callback': self.deleteSelectedGroupCallback,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_delete_group%s.pdf' % darkm),
				'toolTip': 'Delete selected groups'
			},
			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},
			# {
			# 	'itemIdentifier': "toolbarSplitGroup",
			# 	'label': 'Split by Script',
			# 	'callback': self.splitGroupCallback,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_split_groups%s.pdf' % darkm),
			# 	'toolTip': 'Split selected groups by language'
			# },
			# {
			# 	'itemIdentifier': "toolbarCombineGroup",
			# 	'label': 'Combine by Script',
			# 	'callback': self.combineGroupsByLanguageCallback,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_combine_groups%s.pdf' % darkm),
			# 	'toolTip': 'Combine all groups by language'
			# },
			# {
			# 	'itemIdentifier': "toolbarRemoveCrossPairs",
			# 	'label': 'Remove Cross-Pairs',
			# 	'callback': self.removeCrossScriptsCallback,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_remove_crosspairs%s.pdf' % darkm),
			# 	'toolTip': 'Remove Cross-Language kerning pairs from font'
			# },
			# {
			# 	'itemIdentifier': AppKit.NSToolbarSpaceItemIdentifier,
			# },
			{
				'itemIdentifier': "toolbarRenameGroup",
				'label': 'Rename Group',
				'callback': self.renameGroupCallback,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_rename_group%s.pdf' % darkm),
			},
			# {
			# 	'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			# },
			# {
			# 	'itemIdentifier': "toolbarSide1",
			# 	'label': 'Side 1',
			# 	'callback': self.allCallbacks,
			# 	'selectable': True,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_side1%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': "toolbarSide2",
			# 	'label': 'Side 2',
			# 	'callback': self.allCallbacks,
			# 	'selectable': True,
			# 	'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_side2%s.pdf' % darkm),
			# },
			# {
			# 	'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			# },
			{
				'itemIdentifier': AppKit.NSToolbarFlexibleSpaceItemIdentifier,
			},
			{
				'itemIdentifier': "toolbarScripts",
				'label': 'Scripts',
				'callback': self.runScriptsBoardCallback,
				# 'selectable': True,
				'imagePath': os.path.join(RESOURCES_FOLDER, 'tb_scripts%s.pdf' % darkm),
			},

		]
		self.w.addToolbar("GroupsControlToolbar", toolbarItems)
		# self.w.getNSWindow().toolbar().setSelectedItemIdentifier_('toolbarSide1')

		self.font = CurrentFont()
		self.langSet = TDLangSet()
		self.langSet.setupPatternsForFonts(AllFonts())
		self.hashKernDic = TDHashGroupsDic(self.font, self.langSet)
		self.selectedGroup = None #sorted(self.font.groups.keys())[0]
		self.hideGrouped = True
		self.updateKerning = True
		self.groupPrefix = ID_KERNING_GROUP
		self.groupsSide = SIDE_1

		defaultSets = getSmartSets()
		fontSets = getSmartSets(self.font)
		glyphsSets = ['All Glyphs']
		glyphsSets.extend([gset.name for gset in defaultSets])
		glyphsSets.extend([gset.name for gset in fontSets])

		self.w.g2 = vanilla.Group('auto')
		self.w.g2.selectGlyphSet = vanilla.PopUpButton('auto', glyphsSets)
		self.w.g2.checkHideGrouped = vanilla.CheckBox('auto', title = 'Hide groupped', value = True)
		self.w.g2.checkKeepKerning = vanilla.CheckBox('auto', title = 'Keep kerning when moving glyphs', value = True, callback = self.checkKeepKerningCallback)

		#TODO
		self.w.g2.selectGlyphSet.enable(False)
		self.w.g2.checkHideGrouped.enable(False)

		self.w.g2.flex1 = vanilla.Group('auto')
		self.w.g2.flex2 = vanilla.Group('auto')

		segments = [{'width': 100,'title': 'Side 1'}, {'width': 100,'title': 'Side 2'}]
		self.w.g2.switchSide = vanilla.SegmentedButton('auto',
		                                               segmentDescriptions = segments,
		                                               selectionStyle = 'one',
		                                               callback = self.switchSideCallback,
		                                               sizeStyle = 'regular')
		self.w.g2.switchSide.set(0)
		self.w.g2.selectGroup = vanilla.PopUpButton('auto', sorted(self.font.groups.keys()), callback = self.selectorGroupsCallback)
		self.w.g2.btnHistory = vanilla.Button('auto', 'History On', callback = self.callHistoryController)

		self.w.g1 = vanilla.Group('auto')
		self.w.g1.fontView = TDMerzMatrixView('auto', delegate = self )
		self.w.g1.groupView = TDMerzMatrixView('auto', delegate = self )
		self.w.g1.contentView = TDMerzMatrixView('auto', delegate = self )

		self.w.g1.kernListView = TDMerzMatrixView('auto', delegate = self)

		self.w.g1.linesPreview = TDGlyphsMerzView(
			delegate = self,
			posSize = 'auto',
			backgroundColor = COLOR_BACKGROUND,  # (1, 1, 1, 1),#(.75, .73, .7, .8),
			# selectionCallback = self.glyphsViewSelectionCallback,
			fontsHashKernLib = {self.font: self.hashKernDic},
			glyphsLineWillDrawCallback = self.glyphsLineWillDrawCallback

		)
		self.w.g1.linesPreview.scaleFactor = pt2Scale(72)
		self.w.g1.linesPreview.setStatus('showing dependencies', True)
		
		scale = 1
		if 'com.typedev.KernTool.scaleKerningAndMargins' in self.font.lib.keys():
			scale = float(self.font.lib['com.typedev.KernTool.scaleKerningAndMargins'])

		self.spaceControl = TDSpaceControl({self.font: self.hashKernDic}, self.w.g1.linesPreview, mode = EDITMODE_MARGINS, scalesKern = {self.font: scale}, scalesMargins = {self.font: scale})
		self.previewMode = 'margins'
		self.spaceControl.switchMarginsON()


		rules1 = [
			"H:|[fontView]-space-[groupView(>=fontView)]-space-[kernListView(>=340)]|",
			"H:|[fontView]-space-[contentView(>=fontView)]-space-[kernListView(>=340)]|",
			"H:|[linesPreview]|",
			"V:|[fontView]-space-[linesPreview(==175)]|",
			"V:|[groupView]-space-[contentView(==245)]-space-[linesPreview(==175)]|",
			"V:|[kernListView]-space-[linesPreview(==175)]|"
			# "V:||",
		]
		metrics1 = {
			"border": 1,
			"space": 1
		}
		metrics2 = {
			"sborder": 20,
			"border": 7,
			"space": 0
		}
		rules2 = [
			"H:|-sborder-[selectGlyphSet]-sborder-[checkHideGrouped]-[flex1]-[checkKeepKerning]-sborder-[switchSide]-sborder-[selectGroup(==switchSide)]-[flex2(==flex1)]-[btnHistory]-sborder-|", #
			"V:|-border-[selectGlyphSet]-space-|",
			"V:|-border-[checkHideGrouped]-space-|",
			"V:|-border-[checkKeepKerning]-space-|",
			"V:|-border-[flex1]-space-|",
			"V:|-border-[switchSide]-space-|",
			"V:|-border-[selectGroup]-space-|",
			"V:|-border-[flex2]-space-|",
			"V:|-border-[btnHistory]-space-|",
		]
		rules3 = [
			"H:|[g2]|",
			"H:|[g1]|",
			"V:|[g2]-[g1]|",
		]

		self.w.g1.addAutoPosSizeRules(rules1, metrics1)
		self.w.g2.addAutoPosSizeRules(rules2, metrics2)
		self.w.addAutoPosSizeRules(rules3, metrics1)

		self.sceneGroups = self.w.g1.groupView.setupScene(
			layerWillDrawCallback = self.layerGroupWillDrawCallback,
			selectLayerCallback = self.selectGroupLayerCallback,
			dropCallback = self.dropContentCallback,
			clearHash = True,
			dropStyle = DROP_STYLE_DROPIN,
			elementSize = (80, 80),
			elementMargins = (2,2),
			backgroundColor = (.5, .6, .7, 1),
			selectionColor = (0, 0, 1, .5),
			controlsColor = (.2, .3, .4, 1),
			cornerRadius = 5,
			focusColor = (1,1,1,.5)
		)
		self.sceneGroupContent = self.w.g1.contentView.setupScene(
			layerWillDrawCallback = self.layerContentWillDrawCallback,
			selectLayerCallback = self.selectContentLayerCallback,
			dropCallback = self.dropContentCallback,
			clearHash = False,
			dropStyle = DROP_STYLE_INSERT,
			elementSize = (65, 65),
			elementMargins = (2,2),
			backgroundColor = (.5, .6, .7, 1),
			selectionColor = (0, 0, 1, .5),
			controlsColor = (.2, .3, .4, 1),
			cornerRadius = 5,
			focusColor = (1, 1, 1, .5)
		)
		self.sceneFont = self.w.g1.fontView.setupScene(
			layerWillDrawCallback = self.layerFontWillDrawCallback,
			selectLayerCallback = self.fontViewSelectionCallback,
			dropCallback = self.dropContentCallback,
			clearHash = True,
			dropStyle = DROP_STYLE_SCENE,
			elementSize = (65, 65),
			elementMargins = (2, 2),
			backgroundColor = (.5, .6, .7, 1),
			selectionColor = (0, 0, 1, .5),
			controlsColor = (.2, .3, .4, 1),
			cornerRadius = 5,
			focusColor = (1, 1, 1, .5)
		)
		self.schemaButtons = [
			dict(name = 'buttonSide1', widthperсent = 36, value = True),
			dict(name = 'buttonSide2', widthperсent = 36, value = False),
			dict(name = 'buttonValue', widthperсent = 14, value = False),
			dict(name = 'buttonExcpt', widthperсent = 7, value = False),
			dict(name = 'buttonLangs', widthperсent = 7, value = False),
		]
		self.schemaButtonsBottom = {
			'buttonDelete': dict(xpos = 15 + 5, ypos = 'bottom', width = 148, value = 'Delete selected'),
			'buttonSend': dict(xpos = 15 + 5 + 148 + 5, ypos = 'bottom', width = 148, value = 'Send selected to KernTool'),
		}

		self.kernList = self.w.g1.kernListView.setupScene(
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

		self.scenesSelector = TDScenesSelector()
		self.scenesSelector.addScene(self.sceneGroups, self.w.g1.groupView)
		self.scenesSelector.addScene(self.sceneGroupContent, self.w.g1.contentView)
		self.scenesSelector.addScene(self.sceneFont, self.w.g1.fontView)
		self.scenesSelector.addScene(self.kernList, self.w.g1.kernListView)

		self.kernListButtons = {}
		self.kernListSortOrder = 'buttonSide1'
		self.kernListSortReverse = False
		self.kernListPairs = {}
		self.kernListLastSelection = None

		# self.selectedScene = self.sceneGroups
		# self.scenesSelector.selectedScene(self.sceneGroups)

		self.w.g1.kernListView.addControlElement(name = 'buttonSide1', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.g1.kernListView.addControlElement(name = 'buttonSide2', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.g1.kernListView.addControlElement(name = 'buttonValue', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.g1.kernListView.addControlElement(name = 'buttonExcpt', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)
		self.w.g1.kernListView.addControlElement(name = 'buttonLangs', callback = self.buttonCallback, drawingMethod = self.drawSortingButton)

		self.w.g1.kernListView.addControlElement(name = 'buttonDelete', callback = self.buttonBottomCallback, drawingMethod = self.drawBottomButton)
		self.w.g1.kernListView.addControlElement(name = 'buttonSend', callback = self.buttonBottomCallback, drawingMethod = self.drawBottomButton)

		# self.keyCommander = TDKeyCommander()
		# self.keyCommander.registerKeyCommand(KEY_BACKSPACE, callback = self.deleteSelectedPairs)
		# self.keyCommander.registerKeyCommand(KEY_ENTER, callback = self.sendSelectedPairs2KernTool)

		self.pointSize = 10
		self.ScriptsBoardWindow = None

	def started (self):
		self.w.bind('close', self.windowCloseCallback)
		self.w.open()

		self.refreshGroupsView()
		# self.selectedScene = self.sceneGroups
		# if self.sceneGroups:
		self.scenesSelector.setSelectedScene(self.sceneGroups)

	# =========================================================================================
	def selectPairLayerCallback(self, sender, info):
		self.scenesSelector.setSelectedScene(self.kernList)
		if self.previewMode == 'margins':
			self.previewMode = 'kerning'
			self.spaceControl.switchKerningON()
			self.w.g1.linesPreview.switchMargins(True)
			self.w.g1.linesPreview.setStatus('showing dependencies', False)

		pairs = []
		for idx in self.w.g1.kernListView.getSelectedSceneItems():
			pair = self.w.g1.kernListView.getSceneItems()[idx]
			l,r = pair[0]
			sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs, hasError = pair[1]
			pairwrapped = list(self.langSet.wrapPairToPattern(self.font,(keyGlyphL,keyGlyphR)))
			pairs.extend(pairwrapped)
		matrix = prepareGlyphsMatrix([pairs], [self.font]) #, lineinfo = '%s // %s' % (l, r)
		self.w.g1.linesPreview.startDrawGlyphsMatrix(matrix, animatedStart = False)


	def layerKernWillDrawCallback(self, sender, info):
		container = info['layer']
		index = info['index']
		pair = info['item']
		# if not container.getSublayers():
		drawKernPairListed(container, self.font, self.schemaButtons, self.hashKernDic, pair)


	def layerGroupWillDrawCallback (self, sender, info):
		layer = info['layer']
		index = info['index']
		groupName = info['item']
		if not layer.getSublayers():
			drawGroupStack(layer, self.font, groupName, langSet = self.langSet)


	def layerContentWillDrawCallback(self, sender, info):
		layer = info['layer']
		index = info['index']
		glyphname = info['item']
		if not layer.getSublayers():
			drawGroupedGlyph(layer, self.font, self.selectedGroup, glyphname, langSet = self.langSet)


	def layerFontWillDrawCallback(self, sender, info):
		layer = info['layer']
		index = info['index']
		glyphname = info['item']
		if not layer.getSublayers():
			drawFontGlyph(layer, self.font, glyphname)

	def buttonCallback(self, eventname, point, nameButton):
		if eventname =='mouseUp':
			pairsselected = []
			for idx in self.w.g1.kernListView.getSelectedSceneItems():
				pairsselected.append(self.w.g1.kernListView.getSceneItems()[idx][0])

			if self.kernListSortOrder == nameButton:
				self.kernListSortReverse = not self.kernListSortReverse
			else:
				self.kernListSortReverse = False
			self.kernListSortOrder = nameButton

			p = self.makeSortedList(self.kernListPairs, self.kernListSortOrder, self.kernListSortReverse)
			self.w.g1.kernListView.setSceneItems(items = p)
			selection = []
			for idx, p in enumerate(self.w.g1.kernListView.getSceneItems()):
				if p[0] in pairsselected:
					selection.append(idx)
			self.w.g1.kernListView.setSelection(itemsIndexes = selection)

	def drawSortingButton(self, container, nameButton):
		if not container: return
		drawKernListSortButton(container, nameButton, self.kernListSortOrder, self.kernListSortReverse, self.schemaButtons)

	def sendSelectedPairs2KernTool(self,sender, value):
		pairs = []
		for idx in self.w.g1.kernListView.getSelectedSceneItems():
			pair = self.w.g1.kernListView.getSceneItems()[idx]
			l, r = pair[0]
			sortL, sortR, grouppedL, grouppedR, value, note, keyGlyphL, keyGlyphR, langs, hasError = pair[1]
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
		for idx in self.w.g1.kernListView.getSelectedSceneItems():
			pair = self.w.g1.kernListView.getSceneItems()[idx]
			l, r = pair[0]
			pairs.append((l,r))
		for pair in pairs:
			if pair in self.font.kerning:
				self.font.kerning.remove(pair)
		# print(pairs)
		self.w.g1.linesPreview.refreshView()

	def buttonBottomCallback(self, eventname, point, nameButton):
		if eventname =='mouseUp':
			if nameButton == 'buttonSend':
				self.sendSelectedPairs2KernTool(None,None)
			elif nameButton == 'buttonDelete':
				self.deleteSelectedPairs(None,None)

	def drawBottomButton(self, container, nameButton):
		if not container: return
		drawKernListBottomControlButton(container, nameButton, self.schemaButtonsBottom)

	def glyphsLineWillDrawCallback (self, sender, container):
		if not sender.selectedGlyphs: return
		if self.previewMode != 'margins': return
		glyphs = container.getInfoValue('glyphs')
		side = container.getInfoValue('link')
		marks = container.getInfoValue('marks')  # [False for i in glyphs]#
		data = container.getInfoValue('data')

		ray = sender.useRayBeam
		raypos = sender.rayBeamPosition

		if 'mask' in data and data['mask']:
			masks = data['mask']
			startIdx = 1
		else:
			masks = [False, True] * (int(len(glyphs) / 2))

		if side == 'left':
			(lm, rm) = getMargins(glyphs[1], useRayBeam = ray, rayBeamPosition = raypos)
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


	def isGlyphNotInGroups(self, glyphname):
		if self.groupPrefix == ID_KERNING_GROUP:
			mode = EDITMODE_KERNING
		elif self.groupPrefix == ID_MARGINS_GROUP:
			mode = EDITMODE_MARGINS
		else:
			print ('wrong direction TDFontView')
			return
		return not self.hashKernDic.thisGlyphInGroup(glyphname, side = self.groupsSide, mode = mode)

	def getFilteredFontListOfGlyphs(self):
		#TODO need use Smartset
		glyphs = []
		for glyphname in self.font.glyphOrder:
			if self.hideGrouped:
				if self.isGlyphNotInGroups(glyphname):
					glyphs.append(glyphname)
			else:
				glyphs.append(glyphname)
		return glyphs


	def setFontView(self, animated = None):
		self.w.setTitle('%s - %s %s' % (self.idName, self.font.info.familyName, self.font.info.styleName))
		self.w.g1.fontView.setSceneItems(items = self.getFilteredFontListOfGlyphs(), animated = animated)

	def setGroupsView(self, selected = None, animated = None):
		if self.groupPrefix == ID_KERNING_GROUP:
			id_left = ID_GROUP_LEFT
			id_right = ID_GROUP_RIGHT
		elif self.groupPrefix == ID_MARGINS_GROUP:
			id_left = ID_MARGINS_GROUP_LEFT
			id_right = ID_MARGINS_GROUP_RIGHT
		else:
			print ('wrong direction TDGroupsCollectionView')
			return

		groupsList = []
		self.selectedGroup = None
		for idx, groupname in enumerate(sorted(self.font.groups.keys())):
			if groupname.startswith(self.groupPrefix):
				if (self.groupsSide == SIDE_1 and id_left in groupname) or (self.groupsSide == SIDE_2 and id_right in groupname):
					groupsList.append(groupname)
		self.w.g1.groupView.setSceneItems(  # scene = self.sceneGroups,
			items = groupsList,  # len(self.kern), #
			animated = animated
		)
		self.w.g1.contentView.setSceneItems(  # scene = self.sceneGroupContent,
			items = [],  # len(self.kern), #
		)
		self.w.g1.linesPreview.startDrawGlyphsMatrix([], animatedStart = False)
		self.w.g2.selectGroup.setItems(groupsList)

		if not selected and groupsList:
			self.selectedGroup = groupsList[0]
		elif selected and groupsList:
			self.selectedGroup = selected
			self.w.g1.groupView.setSelection(itemsIndexes = [self.w.g1.groupView.getSceneItems().index(self.selectedGroup)])
		if self.selectedGroup:
			self.w.g1.contentView.setSceneItems(  # scene = self.sceneGroupContent,
				items = list(self.font.groups[self.selectedGroup]),  # len(self.kern), #
				animated = 'shake'
			)
			self.showDependencies(groupname = self.selectedGroup)


	def switchSideCallback(self, sender):
		side = sender.get()
		# print (side)
		if side == 0:
			self.groupsSide = SIDE_1
		elif side == 1:
			self.groupsSide = SIDE_2
		self.refreshGroupsView()


	def refreshGroupsView(self):
		side = None
		if self.groupsSide == SIDE_1:
			side = 'left'
		elif self.groupsSide == SIDE_2:
			side = 'right'

		self.setFontView(animated = side)
		self.setGroupsView(animated = side)
		if self.selectedGroup:
			self.w.g1.contentView.setSceneItems(  # scene = self.sceneGroupContent,
				items = list(self.font.groups[self.selectedGroup]),  # len(self.kern), #
				animated = side
			)
			self.showKernList(groupname = self.selectedGroup)

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
			hasError = 0
			# print('ref', l,r, _l,_r, note)
			if r.startswith(ID_KERNING_GROUP):
				grouppedR = True
				sortR = r.replace(_mask2id, '')

			if l.startswith(ID_KERNING_GROUP):
				sortL = l.replace(_mask1id, '')
				_pairslist[(l, r)] = (sortL, sortR, True, grouppedR, v, note, keyGlyphL, keyGlyphR, langs, hasError)
			else:
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
			# reverse = not reverse
			return sorted(_pairslist.items(), key = lambda p: (p[1][8]), reverse = reverse) #, p[1][0], p[1][1]


	def showKernList(self, groupname = None, glyphName = None):
		self.kernListLastSelection = (groupname, glyphName)
		pairsselected = []
		pairs = []
		for idx in self.w.g1.kernListView.getSelectedSceneItems():
			pairsselected.append(self.w.g1.kernListView.getSceneItems()[idx][0])

		self.w.g1.kernListView.setSceneItems(items = [])
		if groupname:
			# groupnames = [groupname]
			# if len(self.w.g1.groupView.getSelectedSceneItems()) > 1:
			# 	groupnames =[]
			# 	for idx in self.w.g1.groupView.getSelectedSceneItems():
			# 		gn = self.w.g1.groupView.getSceneItems()[idx]
			# 		groupnames.append(gn)
			groupnames = self.getSelectedGroupNames()
			pairs = []
			for groupname in groupnames:
				_pairs = self.hashKernDic.getPairsBy(groupname, self.groupsSide)
				pairs.extend(pair for pair, value in _pairs)
				if len(self.font.groups[groupname]) != 0:
					for glyphname in self.font.groups[groupname]:
						_pairs = self.hashKernDic.getPairsBy(glyphname, self.groupsSide)
						if _pairs:
							pairs.extend(pair for pair, value in _pairs)

		if glyphName:
			glyphNames = [glyphName]
			if len(self.w.g1.fontView.getSelectedSceneItems()) > 1:
				glyphNames = []
				for idx in self.w.g1.fontView.getSelectedSceneItems():
					gn = self.w.g1.fontView.getSceneItems()[idx]
					glyphNames.append(gn)
			pairs = []
			for glyphName in glyphNames:
				_pairs = self.hashKernDic.getPairsBy(glyphName, self.groupsSide)
				pairs.extend(pair for pair, value in _pairs)

		self.kernListPairs = pairs
		p = self.makeSortedList(pairs, self.kernListSortOrder, self.kernListSortReverse)
		self.w.g1.kernListView.setSceneItems(items = p)  # , animated = 'bottom'

		selection = []
		for idx, p in enumerate(self.w.g1.kernListView.getSceneItems()):
			if p[0] in pairsselected:
				# print ('sel', p)
				selection.append(idx)
		self.w.g1.kernListView.setSelection(itemsIndexes = selection)


	def showDependencies(self, groupname = None, glyphName = None):
		if groupname:
			if len(self.font.groups[groupname]) == 0:
				self.w.g1.linesPreview.startDrawGlyphsMatrix([], animatedStart = False)
				self.showKernList(groupname = groupname)
				return
			try:
				keyGlyph = self.font[self.hashKernDic.getKeyGlyphByGroupname(groupname)]
			except:
				self.w.g1.linesPreview.startDrawGlyphsMatrix([], animatedStart = False)
				self.showKernList(groupname = groupname)
				return
			displayTitle = groupname
			self.showKernList(groupname = groupname)
		if glyphName:
			try:
				keyGlyph = self.font[glyphName]
			except:
				self.w.g1.linesPreview.startDrawGlyphsMatrix([], animatedStart = False)
				self.showKernList(glyphName = glyphName)
				return
			displayTitle = glyphName
			self.showKernList(glyphName = glyphName)

		mapGlyphs = self.font.getReverseComponentMapping()
		ray = self.w.g1.linesPreview.useRayBeam
		raypos = self.w.g1.linesPreview.rayBeamPosition
		ggLmarks = []
		glyphslineL = []
		margin = 0
		side = ''
		txtside = ''
		(lm, rm) = getMargins(keyGlyph, useRayBeam = ray, rayBeamPosition = raypos)
		if self.groupsSide == SIDE_1:
			side = 'left'
			txtside = 'Right'
			margin = rm
		elif self.groupsSide == SIDE_2:
			side = 'right'
			txtside = 'Left'
			margin = lm

		if groupname:
			for ggname in self.font.groups[groupname]:
				if ggname in self.font:
					glyphslineL, ggLmarks = fillglyphsline(self.font, glyphslineL, ggLmarks, mapGlyphs, ggname, margin, self.groupsSide, ray, raypos)
		if glyphName:
			glyphslineL, ggLmarks = fillglyphsline(self.font, glyphslineL, ggLmarks, mapGlyphs, glyphName, margin, self.groupsSide, ray, raypos) # 'L'

		lline, lmarks, lmask = self.hashKernDic.langSet.wrapGlyphsLine_MarksAndMasks(self.font, glyphslineL, ggLmarks)  # , self.txtPatterns)
		matrix = dict(glyphs = lline,  # glyphslineL,# self.font.groups[info]
		              marks = lmarks,
		              link = side,
		              data = {'mask': lmask},
		              info = '%s  \n+composites\n+parents\n\n*Check the %s side,\nuse a Beam [B] for more accuracy' % (displayTitle, txtside))
		self.w.g1.linesPreview.startDrawGlyphsMatrix([matrix], animatedStart = False)

	def getSelectedGroupNames(self):
		groupnames = []
		if self.selectedGroup:
			groupnames = [self.selectedGroup]
			if len(self.w.g1.groupView.getSelectedSceneItems()) > 1:
				groupnames = []
				for idx in self.w.g1.groupView.getSelectedSceneItems():
					gn = self.w.g1.groupView.getSceneItems()[idx]
					groupnames.append(gn)
		return groupnames


	def selectGroupLayerCallback (self, sender, info):
		layer = info['layer']
		index = info['index']
		# if self.previewMode != 'margins':
		# 	self.spaceControl.switchMarginsON()
		# self.selectedScene = self.sceneGroups
		self.scenesSelector.setSelectedScene(self.sceneGroups)
		if self.previewMode != 'margins':
			self.previewMode = 'margins'
			self.spaceControl.switchMarginsON()
			self.w.g1.linesPreview.switchMargins(showMargins = True)
			self.w.g1.linesPreview.setStatus('showing dependencies', True)

		self.selectedGroup = info['item']#self.groupsIdx[index]
		self.w.g1.contentView.setSceneItems(items = list(self.font.groups[self.selectedGroup]), animated = 'shake')
		self.showDependencies(groupname = self.selectedGroup)


	def fontViewSelectionCallback (self, sender, info):
		layer = info['layer']
		index = info['index']
		glyphName = info['item'] #listofglyphs[index] #info['item']
		if not glyphName: return
		# self.selectedScene = self.sceneFont
		self.scenesSelector.setSelectedScene(self.sceneFont)
		if self.previewMode != 'margins':
			self.previewMode = 'margins'
			self.spaceControl.switchMarginsON()
			self.w.g1.linesPreview.switchMargins(showMargins = True)
			self.w.g1.linesPreview.setStatus('showing dependencies', True)
		self.showDependencies( glyphName = glyphName)


	def selectContentLayerCallback (self, sender, info):
		layer = info['layer']
		index = info['index']
		glyphName = info['item']
		if not glyphName: return
		# self.selectedScene = self.sceneGroupContent
		self.scenesSelector.setSelectedScene(self.sceneGroupContent)
		if self.previewMode != 'margins':
			self.previewMode = 'margins'
			self.spaceControl.switchMarginsON()
			self.w.g1.linesPreview.switchMargins(showMargins = True)
			self.w.g1.linesPreview.setStatus('showing dependencies', True)
		self.showDependencies(glyphName = glyphName)


	def updateFontAndGroupViews(self, listofglyphs, itemsIndexes, skipedNames):
		self.w.g1.contentView.setSceneItems(items = list(self.font.groups[self.selectedGroup]), animated = 'shake')  # scene = destinationScene,
		for sn in skipedNames:
			itemsIndexes.remove(listofglyphs.index(sn))
		self.w.g1.fontView.setSceneItems(items = self.getFilteredFontListOfGlyphs())
		self.w.g1.groupView.updateSceneItems(  # scene = self.sceneGroups,
			itemsIndexes = [self.w.g1.groupView.getSceneItems().index(self.selectedGroup)])  # self.sceneGroups
		self.showDependencies(groupname = self.selectedGroup)


	def dropContentCallback(self, sender, dropInfo):
		destinationScene = dropInfo['destinationScene']
		sourceScene = dropInfo['sourceScene']
		layerOver = dropInfo['layerOver']
		itemsIndexes = dropInfo['itemsIndexes']

		if destinationScene == self.sceneGroupContent and sourceScene == self.sceneFont:
			# print ('add glyphs to group')
			listofglyphs = self.w.g1.fontView.getSceneItems() # self.sceneFont
			if layerOver == 'scene':
				skipedNames,np,dp = self.hashKernDic.addGlyphsToGroup(self.selectedGroup, [listofglyphs[idx] for idx in itemsIndexes], checkKerning = self.updateKerning)
				self.updateFontAndGroupViews(listofglyphs,itemsIndexes,skipedNames)
			else:
				skipedNames,np,dp = self.hashKernDic.addGlyphsToGroup(self.selectedGroup, [listofglyphs[idx] for idx in itemsIndexes], checkKerning = self.updateKerning)
				self.hashKernDic.repositionGlyphsInGroup(self.selectedGroup, layerOver, [listofglyphs[idx] for idx in itemsIndexes] )
				self.updateFontAndGroupViews(listofglyphs,itemsIndexes,skipedNames)

		if destinationScene == self.sceneFont and sourceScene == self.sceneGroupContent:
			# print ('remove glyph from group')
			listofglyphs = self.w.g1.contentView.getSceneItems() # self.sceneGroupContent
			self.hashKernDic.removeGlyphsFromGroup(self.selectedGroup, [listofglyphs[idx] for idx in itemsIndexes], checkKerning = self.updateKerning)
			self.w.g1.contentView.setSceneItems(items = list(self.font.groups[self.selectedGroup]), animated = 'shake') # scene = sourceScene,

			self.w.g1.fontView.setSceneItems(items = self.getFilteredFontListOfGlyphs())
			self.w.g1.groupView.updateSceneItems( # scene = self.sceneGroups,
			                                  itemsIndexes = [self.w.g1.groupView.getSceneItems().index(self.selectedGroup)]) # self.sceneGroups
			self.showDependencies(groupname = self.selectedGroup)

		if destinationScene == self.sceneGroups and sourceScene == self.sceneFont:
			# print('add glyphs to group over groups view')
			listofglyphs = self.w.g1.fontView.getSceneItems() # self.sceneFont

			self.selectedGroup = self.w.g1.groupView.getSceneItems()[layerOver] # self.sceneGroups
			self.w.g1.groupView.setSelection(itemsIndexes = [layerOver]) # scene = self.sceneGroups,
			skipedNames,np,dp = self.hashKernDic.addGlyphsToGroup(self.selectedGroup, [listofglyphs[idx] for idx in itemsIndexes], checkKerning = self.updateKerning)
			self.updateFontAndGroupViews(listofglyphs, itemsIndexes, skipedNames)

		if destinationScene == self.sceneGroupContent and sourceScene == self.sceneGroupContent:
			if layerOver == 'scene': return
			# print('resort glyphs in group')
			listofglyphs = self.w.g1.contentView.getSceneItems()
			self.hashKernDic.repositionGlyphsInGroup(self.selectedGroup, layerOver, [listofglyphs[idx] for idx in itemsIndexes])
			self.w.g1.contentView.setSceneItems(items = list(self.font.groups[self.selectedGroup]), animated = 'shake')
			self.w.g1.groupView.updateSceneItems(  # scene = self.sceneGroups,
				itemsIndexes = [self.w.g1.groupView.getSceneItems().index(self.selectedGroup)])


	def createGroup(self, font, glist):
		if len(glist) != 0:
			keyGlyph = glist[0]

			if self.groupPrefix == ID_KERNING_GROUP:
				id_left_mask = ID_GROUP_MASK_1
				id_right_mask = ID_GROUP_MASK_2
			elif self.groupPrefix == ID_MARGINS_GROUP:
				id_left_mask = ID_GROUP_MARGINS_MASK_1
				id_right_mask = ID_GROUP_MARGINS_MASK_2
			else:
				# print('wrong direction TDFontView')
				return

			mask1 = id_left_mask#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_LEFT
			mask2 = id_right_mask#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_RIGHT
			if self.groupsSide == SIDE_1:
				groupname = '%s%s' % (mask1, keyGlyph)
			elif self.groupsSide == SIDE_2:
				groupname = '%s%s' % (mask2, keyGlyph)
			else: return

			self.hashKernDic.addGlyphsToGroup(groupname, glist, checkKerning = self.updateKerning)
			if self.groupPrefix == ID_MARGINS_GROUP:
				mapGlyphs = font.getReverseComponentMapping()
				for g in glist:
					if g in mapGlyphs:
						self.hashKernDic.addGlyphsToGroup(groupname,sorted(mapGlyphs[g]), checkKerning = self.updateKerning)
			self.selectedGroup = groupname

	def createGroupsByList(self, font, glist):
		for glyphname in glist:
			self.createGroup(font, [glyphname])


	def addGroupCallbacks(self, sender):
		listofglyphs = self.w.g1.fontView.getSceneItems()
		itemsIndexes = self.w.g1.fontView.getSelectedSceneItems()
		glist = [listofglyphs[idx] for idx in itemsIndexes]
		self.createGroup(self.font, glist)
		self.w.g1.fontView.setSceneItems(items = self.getFilteredFontListOfGlyphs())
		self.setGroupsView(selected = self.selectedGroup)


	def addGroupByListCallbacks(self, sender):
		listofglyphs = self.w.g1.fontView.getSceneItems()
		itemsIndexes = self.w.g1.fontView.getSelectedSceneItems()
		glist = [listofglyphs[idx] for idx in itemsIndexes]
		self.createGroupsByList(self.font, glist)
		self.w.g1.fontView.setSceneItems(items = self.getFilteredFontListOfGlyphs())
		self.setGroupsView(selected = self.selectedGroup)


	def deleteSelectedGroupCallback(self, sender):
		# print('deleteSelectedGroupCallback IN')
		if self.selectedGroup:
			if self.scenesSelector.getSelectedScene() == self.sceneGroups or self.scenesSelector.getSelectedScene() == self.sceneGroupContent:
				# print('deleteSelectedGroupCallback OUT')
				listofgroups = self.w.g1.groupView.getSceneItems()
				itemsIndexes = self.w.g1.groupView.getSelectedSceneItems()
				glist = [listofgroups[idx] for idx in itemsIndexes]
				for groupname in glist:
					self.hashKernDic.deleteGroup(groupname, self.updateKerning)
				self.w.g1.fontView.setSceneItems(items = self.getFilteredFontListOfGlyphs())
				self.setGroupsView()
				if self.selectedGroup:
					self.w.g1.contentView.setSceneItems(  # scene = self.sceneGroupContent,
						items = list(self.font.groups[self.selectedGroup]),  # len(self.kern), #
						animated = 'shake'
					)

	def renameGroupCallback(self, sender):
		oldname = self.selectedGroup
		newname = AskString('Enter new name', value = oldname, title = 'Rename Group')
		if newname and newname != oldname and ID_KERNING_GROUP in newname:
			self.hashKernDic.renameGroup(oldname, newname)
			self.selectedGroup = newname
			self.refreshGroupsView()
			self.setSelectedGroup(groupname = newname)

	def setSelectedGroup(self, groupname = None, index = None):
		if groupname:
			if self.selectedGroup != groupname:
				index = self.w.g1.groupView.getSceneItems().index(groupname)
				self.selectedGroup = groupname
		elif index:
			self.selectedGroup = self.w.g1.groupView.getSceneItems()[index]

		if index:
			self.w.g1.groupView.setSelection(itemsIndexes = [index], selected = True, animate = True)
			self.w.g1.contentView.setSceneItems(  # scene = self.sceneGroupContent,
				items = list(self.font.groups[self.selectedGroup]),  # len(self.kern), #
				animated = 'shake'
			)
			self.showDependencies(groupname = self.selectedGroup)


	def selectorGroupsCallback(self, sender):
		index = sender.get()
		self.setSelectedGroup(index = index)


	def checkKeepKerningCallback(self, sender):
		self.updateKerning = sender.get()

	def allCallbacks(self, sender):
		pass

	def selectFontCallback(self, sender):

		font = SelectFont(title = self.idName)
		if font:
			self.w.g1.fontView.setSceneItems(items = [])
			self.w.g1.groupView.setSceneItems(items = [])
			self.w.g1.contentView.setSceneItems(items = [])
			self.w.g1.kernListView.setSceneItems(items = [])
			self.hashKernDic.clearHistory()
			self.font = font
			# self.langSet = TDLangSet()
			self.langSet.setupPatternsForFont(self.font)
			self.hashKernDic.setFont(self.font, self.langSet)

			self.w.g1.linesPreview.fontsHashKernLib = {self.font: self.hashKernDic}

			self.spaceControl.fontsHashKernLib = {self.font: self.hashKernDic}
			self.spaceControl.kernControl.fontsHashKernLib = {self.font: self.hashKernDic}
			self.spaceControl.marginsControl.fontsHashKernLib = {self.font: self.hashKernDic}
			if 'com.typedev.KernTool.scaleKerningAndMargins' in self.font.lib.keys():
				scale = float(self.font.lib['com.typedev.KernTool.scaleKerningAndMargins'])
				self.spaceControl.scalesKern = {self.font: scale}
				self.spaceControl.scalesMargins = {self.font: scale}

			self.refreshGroupsView()


	def importGroupsCallback (self, sender):
		fn = getFile(messageText = 'Import Groups from file', title = 'title')

		if fn and fn[0]:
			groups2kill = []
			for groupname, content in self.font.groups.items():
				if groupname.startswith(self.groupPrefix):
					groups2kill.append(groupname)
			for groupname in groups2kill:
				del self.font.groups[groupname]

			f = open(fn[0], mode = 'r')
			# self.font.groups.clear()
			self.hashKernDic.setFont(self.font, self.langSet)
			for line in f:
				line = line.strip()
				groupname = line.split('=')[0]
				print('Making group', groupname)
				# self.font.groups[groupname] = ()
				if len(line.split('='))==2:
					glist = []
					content = line.split('=')[1].split(',')
					for gname in content:
						if gname in self.font:
							glist.append(gname)
					# self.font.groups[groupname] = tuple(glist)
					report = self.hashKernDic.addGlyphsToGroup(groupname,glist)
					# print (report)
			f.close()
			print('Groups imported..')
			self.hashKernDic.setFont(self.font, self.langSet)
			self.setFontView(animated = 'left')
			self.setGroupsView(animated = 'left')
			# self.w.g1.contentView.setSceneItems(  # scene = self.sceneGroupContent,
			# 	items = list(self.font.groups[self.selectedGroup]),  # len(self.kern), #
			# 	animated = 'left'
			# )


	def exportGroupsCallback (self, sender):
		groups2save = {}
		for groupname, content in self.font.groups.items():
			if groupname.startswith(self.groupPrefix):
				if groupname not in groups2save:
					groups2save[groupname] = self.font.groups[groupname]

		fn = putFile(messageText = 'Export Groups to file', title = 'title')
		if fn:
			groupsfile = open(fn, mode = 'w')

			txt = ''
			for groupname in sorted(groups2save):
				txt += '%s=%s\n' % (groupname, ','.join(groups2save[groupname]))
			groupsfile.write(txt)
			groupsfile.close()
			print('File saved.')

	def windowCloseCallback(self, sender):
		self.w.g1.fontView.clearScene()
		self.w.g1.groupView.clearScene()
		self.w.g1.contentView.clearScene()
		self.w.g1.kernListView.clearScene()
		if self.ScriptsBoardWindow:
			try:
				self.ScriptsBoardWindow.close()
			except: pass
		unregisterCurrentFontSubscriber(self)

	def keyDown (self, sender, event):
		self.spaceControl.checkCommand(sender, event)
		# self.keyCommander.checkCommand(sender, event)
		self.w.g1.contentView.setSceneItems(items = list(self.font.groups[self.selectedGroup]), animated = 'shake')  # scene = destinationScene,
		self.w.g1.groupView.updateSceneItems(  # scene = self.sceneGroups,
			itemsIndexes = [self.w.g1.groupView.getSceneItems().index(self.selectedGroup)])  # self.sceneGroups
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

	def runScriptsBoardCallback(self, sender):
		self.ScriptsBoardWindow = ScriptsBoard.main(parent = self)

	def callHistoryController(self, sender):
		tdHistoryController.main(host = self)


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
	if CurrentFont():
		registerCurrentFontSubscriber(TDGroupsControl4)
	else:
		from mojo.UI import Message
		Message("No open font found..")

if __name__ == "__main__":
	main()