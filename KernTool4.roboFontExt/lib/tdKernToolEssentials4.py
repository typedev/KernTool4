# -*- coding: utf-8 -*-

# import uuid
import random
import string
from mojo.roboFont import *
from mojo.extensions import *
from mojo.pens import DecomposePointPen
from fontParts.world import *
import platform
import importlib
# import tdLangSet
# importlib.reload(tdLangSet)
# from tdLangSet import TDLangSet

MACOS_VERSION = platform.mac_ver()[0].split('.')[1]

PREFKEY_base = 'com.typedev.KernTool3'
PREFKEY_GroupName = '%s.KernGroupNameID' % PREFKEY_base
PREFKEY_LeftID = '%s.KernGroupLEFTID' % PREFKEY_base
PREFKEY_RightID = '%s.KernGroupRIGHTID' % PREFKEY_base
PREFKEY_DarkMode = '%s.KernToolUI.darkmode' % PREFKEY_base
PREFKEY_DarkModeWarmBackground = '%s.KernToolUI.darkmodeWarmBackground' % PREFKEY_base
PREFKEY_GlyphsViewFontSize = '%s.KernToolUI.GlyphsView.FontSize' % PREFKEY_base
PREFKEY_GroupsViewFontSize = '%s.KernToolUI.GroupsView.FontSize' % PREFKEY_base
PREFKEY_GroupsViewPanelSize = '%s.KernToolUI.GroupsView.PanelSize' % PREFKEY_base
PREFKEY_WindowSize = '%s.KernToolUI.Window.Size' % PREFKEY_base
PREFKEY_GlyphSequencesSArk = '%s.KernToolUI.GlyphSequences' % PREFKEY_base



ID_KERNING_GROUP = getExtensionDefault(PREFKEY_GroupName, fallback='public.kern')
ID_GROUP_LEFT = getExtensionDefault(PREFKEY_LeftID, fallback='.kern1.')
ID_GROUP_RIGHT = getExtensionDefault(PREFKEY_RightID, fallback='.kern2.')
KERNTOOL_UI_DARKMODE = getExtensionDefault(PREFKEY_DarkMode, fallback=False)
KERNTOOL_UI_DARKMODE_WARMBACKGROUND = getExtensionDefault(PREFKEY_DarkModeWarmBackground, fallback=False)

ID_GROUP_MASK_1 = ID_KERNING_GROUP.replace('.kern', ID_GROUP_LEFT) #+ ID_GROUP_LEFT
ID_GROUP_MASK_2 = ID_KERNING_GROUP.replace('.kern', ID_GROUP_RIGHT) #+ ID_GROUP_RIGHT

ID_MARGINS_GROUP = 'public.margins' # '.margins'
ID_MARGINS_GROUP_LEFT = '.margins1.'
ID_MARGINS_GROUP_RIGHT  = '.margins2.'

ID_GROUP_MARGINS_MASK_1 = ID_MARGINS_GROUP.replace('.margins', ID_MARGINS_GROUP_LEFT) #+ ID_MARGINS_GROUP_LEFT
ID_GROUP_MARGINS_MASK_2 = ID_MARGINS_GROUP.replace('.margins', ID_MARGINS_GROUP_RIGHT) #+ ID_MARGINS_GROUP_RIGHT

COMMAND_MAKE_EXCEPTION = 1
COMMAND_DELETE_PAIR = 2
# COMMAND_SET_KERNING = 3
COMMAND_NEXT_PAIR = 4
COMMAND_PREV_PAIR = 5
COMMAND_ZOOM_IN = 6
COMMAND_ZOOM_OUT = 7

COMMAND_REFRESH = 12

COMMAND_SWITCH_TOUCHE_MODE = 13
COMMAND_SWITCH_EDIT_MODE = 14
COMMAND_OPEN_PAIRS_FILE = 15
COMMAND_FLIP_PAIR = 16

COMMAND_OPEN_PAIRS_BUILDER = 17
COMMAND_PAIRVALUE_AUTOCALCULATE = 18

COMMAND_ENTER = 19
COMMAND_ESCAPE = 20
COMMAND_SELECT_FONT = 21

COMMAND_LINKED_MODE = 22

COMMAND_ALT_ENTER = 23

COMMAND_CHECK_TOUCHE = 33

COMMAND_FIX_TOUCHES = 34

COMMAND_OPEN_LINE_IN_SPACECENTER = 35
COMMAND_OPEN_GLYPH = 36

COMMAND_OFF_KERN = 37

COMMAND_COPYKERN = 38
COMMAND_PASTEKERN = 39

COMMAND_SPACEKEY = 40
COMMAND_SELECT_ALL = 41


COMMAND_MAKE_EXCEPTION_BOTH_SIDES = 42


COMMAND_SET_RIGHTKEY = 24
COMMAND_SET_SHIFT_RIGHTKEY = 25
COMMAND_SET_ALT_RIGHTKEY = 26
COMMAND_SET_ALT_LEFTKEY = 27
COMMAND_SET_SHIFT_LEFTKEY = 28
COMMAND_SET_LEFTKEY = 29
COMMAND_SET_ALT_SHIFT_RIGHTKEY = 43
COMMAND_SET_ALT_SHIFT_LEFTKEY = 44
COMMAND_SET_CMD_RIGHTKEY = 31
COMMAND_SET_CMD_LEFTKEY = 32

COMMAND_TAKE_THE_VALUE = 30

COMMAND_USE_RAY_MARGINS = 45

COMMAND_SET_ALT_DOWNKEY = 8
COMMAND_SET_ALT_UPKEY = 9
COMMAND_SET_DOWNKEY = 10
COMMAND_SET_UPKEY = 11
COMMAND_SET_SHIFT_DOWNKEY = 46
COMMAND_SET_SHIFT_UPKEY = 47
COMMAND_SET_ALT_SHIFT_DOWNKEY = 48
COMMAND_SET_ALT_SHIFT_UPKEY = 49

COMMAND_SWITCH_PAIR = 50


# COMMAND_SWITCH_VALUES_MODE = 100


EVENT_KERN_VALUE_CHANGED = 'typedev.KernTool.setNewKernValue'
EVENT_STEP_TO_LINE = 'typedev.KernTool.stepToLine'

EVENT_OBSERVERID = 'typedev.KernTool.observerID'
EVENT_OBSERVERID_CALLBACK = 'typedev.KernTool.observerIDcallback'
EVENT_KERN_VALUE_LINKED = 'typedev.KernTool.setNewKernValueLinked'
EVENT_OBSERVER_SETTEXT = 'typedev.KernTool.observerSetText'
EVENT_REFRESH_KERNTOOL = 'typedev.KernTool.refresh'
EVENT_REFRESH_ALL_OBSERVERS = 'typedev.KernTool.refreshObservers'


	# return 'uuid' + str(uuid.uuid4()).replace('-', '')[:cut]

def cutUniqName (glyphname):
	# if 'uuid' in glyphname:
	# 	a = glyphname.split('.')[:-1]
	# 	return '.'.join(a)
	# return glyphname
	if 'uuid' in glyphname:
		last_dot_index = glyphname.rfind('.')
		if last_dot_index != -1:
			return glyphname[:last_dot_index]
	return glyphname

def ran_gen(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def getUniqName(cut=32):
	return 'uuid' + ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

def uniqueName(name = None, cut = 32):
	if name:
		return '%s.uuid%s' % (name, ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
	return 'uuid%s' % ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

def getFontID (font=None):
	if font:
		fontID = {}
		fontID['fileName'] = font.fileName
		fontID['familyName'] = font.info.familyName
		fontID['styleName'] = font.info.styleName
		# print 'getfontid:', fontID
		return fontID
	return None


def isMyFontID (fontID=None):
	if fontID:
		# print 'ismyfont:', fontID
		for font in AllFonts():
			if (font.fileName == fontID['fileName']) and (font.info.familyName == fontID['familyName']) and (
						font.info.styleName == fontID['styleName']):
				return font
	return None

#
# def getPairsList (listOfGlyphs, addSpace = False):
# 	result = []
# 	for i, L in enumerate(listOfGlyphs):
# 		if i != len(listOfGlyphs) - 1:
# 			R = listOfGlyphs[i + 1]
# 			result.append([L, R])
# 			if addSpace:
# 				result.append(['space', 'space'])
# 	return result


def kern (kernValue):
	if (kernValue != None):  # and (kernValue != 0):
		return True
	return False


def addGlyphsToGroup(font, group, glyphlist, checkKerning = False):
	"""
	function for adding glyphs to a group, if the group does not exist, it will be created
	"""
	# RF3 style
	newcontent = []
	if group not in font.groups:
		font.groups[group] = ()
	for glyphname in glyphlist:
		if glyphname not in font.groups[group]:
			newcontent.append(glyphname)
	if newcontent:
		font.groups[group] += tuple(newcontent)

def delGlyphsFromGroup(font, group, glyphlist, checkKerning = False):
	"""
	function to remove glyphs from a group
	"""
	# RF3 style
	if group in font.groups:
		newcontent = []
		for glyphname in font.groups[group]:
			if glyphname not in glyphlist:
				newcontent.append(glyphname)
		font.groups[group] = tuple(newcontent)

def repositionGlyphsInGroup(font, group, idx = 0, glyphlist = None):
	# RF3 style
	if idx > len(font.groups[group]):return
	try:
		tempgroup = list(font.groups[group])
		glyphIdxName = tempgroup[idx]
		for name in glyphlist:
			tempgroup.remove(name)
		idx = 0
		for i, name in enumerate(tempgroup):
			if name == glyphIdxName:
				idx = i
		for name in glyphlist:
			tempgroup.insert(idx, name)
			idx += 1
		font.groups[group] = tuple(tempgroup)
	except:
		pass



def checkOverlapingGlyphs (font, leftglyph, rightglyph, kernvalue):
	# RF3 style
	# if not leftglyph.rightMargin or not rightglyph.leftMargin: return False
	try:
		if leftglyph.rightMargin + rightglyph.leftMargin + kernvalue > 0:
			return False
		tempLeftGlyph = leftglyph.copy()

		if leftglyph.components != None:
			dstGlyphL = RGlyph()
			dstGlyphL.width = leftglyph.width
			dstPenL = dstGlyphL.getPointPen()
			decomposePenL = DecomposePointPen(font, dstPenL)
			leftglyph.drawPoints(decomposePenL)
			tempLeftGlyph = dstGlyphL

		tempRightGlyph = rightglyph.copy()

		if rightglyph.components != None:
			dstGlyphR = RGlyph()
			dstGlyphR.width = rightglyph.width
			dstPenR = dstGlyphR.getPointPen()
			decomposePenR = DecomposePointPen(font, dstPenR)
			rightglyph.drawPoints(decomposePenR)
			tempRightGlyph = dstGlyphR

		tempRightGlyph.move((leftglyph.width + kernvalue, 0))
		tempglyph = tempLeftGlyph & tempRightGlyph
		if not tempglyph.isEmpty():
			return True
		return False
	except:
		return False


def autoCalcPairValue (font, hashKernDic, pair, mode = 'default', simplePair = False): # mode = 'fixtouches'
	# print ('Calling AutoCalc..') # for', pair
	if not simplePair:
		leftglyph = font[cutUniqName(pair['L_nameUUID'])]
		rightglyph = font[cutUniqName(pair['R_nameUUID'])]
		startKernValue = pair['kernValue']

	else:
		l, r = pair
		rawpair = researchPair(font,hashKernDic,(l,r))
		leftglyph = font[l]
		rightglyph = font[r]
		startKernValue = rawpair['kernValue']


	#researchPair(font, hashKernDic, (pair['L_nameUUID'],pair['R_nameUUID']))['kernValue']

	if not startKernValue: startKernValue = 0

	# stage 1: fix overlaping
	if checkOverlapingGlyphs(font, leftglyph, rightglyph, startKernValue):
		print ('Overlap detected..')
		stepKern = 10
		countInc = 0
		while checkOverlapingGlyphs(font, leftglyph, rightglyph, startKernValue):
			startKernValue += stepKern
			countInc += stepKern
		# print 'inc +10:', startKernValue
		startKernValue += stepKern * 3
		return countInc + (stepKern * 3)
	else:
		if mode == 'default':
			stepKern = 10
			countInc = 0
			while not checkOverlapingGlyphs(font, leftglyph, rightglyph, startKernValue):
				startKernValue -= stepKern
				countInc -= stepKern
			startKernValue += stepKern * 7
			return countInc + (stepKern * 7)
		elif mode == 'fixtouches':
			# return None
			if checkOverlapingGlyphs(font, leftglyph, rightglyph, startKernValue - 15):
				return startKernValue + 20
			else:
				return None


def getDirection (groupname):
	if ID_KERNING_GROUP and ID_GROUP_LEFT in groupname:
		return 'L'
	elif ID_KERNING_GROUP and ID_GROUP_RIGHT in groupname:
		return 'R'
	elif ID_MARGINS_GROUP and ID_MARGINS_GROUP_LEFT in groupname:
		return 'L'
	elif ID_MARGINS_GROUP and ID_MARGINS_GROUP_RIGHT in groupname:
		return 'R'
	else:
		print ('ERROR!!! Wrong Group Name')
		return None

def getDisplayNameGroup(groupname):
	# RF3 style
	if not groupname: return
	mask1 = ID_GROUP_MASK_1#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_LEFT
	mask2 = ID_GROUP_MASK_2#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_RIGHT
	mask3 = ID_GROUP_MARGINS_MASK_1
	mask4 = ID_GROUP_MARGINS_MASK_2
	if mask1 in groupname:
		return groupname.replace(mask1,'@.') # '@_'
	elif mask2 in groupname:
		return groupname.replace(mask2,'@.')
	elif mask3 in groupname:
		return groupname.replace(mask3, '#.')
	elif mask4 in groupname:
		return groupname.replace(mask4, '#.')
	else:
		return groupname

def getGroupNameFromDisplayName(groupname, direction):
	# RF3 style
	if not groupname: return
	mask1 = ID_GROUP_MASK_1#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_LEFT
	mask2 = ID_GROUP_MASK_2#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_RIGHT
	mask3 = ID_GROUP_MARGINS_MASK_1
	mask4 = ID_GROUP_MARGINS_MASK_2
	if direction == 'L' and '@.' in groupname:
		return groupname.replace('@.', mask1 )
	elif direction == 'R' and '@.' in groupname:
		return groupname.replace('@.', mask2)
	elif direction == 'L' and '#.' in groupname:
		return groupname.replace('#.', mask3 )
	elif direction == 'R' and '#.' in groupname:
		return groupname.replace('#.', mask4)


def getKeyGlyphMargin(font, keyglyph, direction):
	# if keyglyph in font:
	try:
		if direction == 'L':
			if font.info.italicAngle != 0:
				if font[keyglyph].angledRightMargin:
					return int(round(font[keyglyph].angledRightMargin, 0))
			return int(round(font[keyglyph].rightMargin, 0))
		elif direction == 'R':
			if font.info.italicAngle != 0:
				return int(round(font[keyglyph].angledLeftMargin, 0))
			return int(round(font[keyglyph].leftMargin, 0))
	except:
		return 0


def checkMarginsInGroup(font, keyglyph, groupname, direction):
	if keyglyph in font:
		keyGlyphMargin = getKeyGlyphMargin(font, keyglyph = keyglyph, direction = direction)
		for glyphname in font.groups[groupname]:
			if keyGlyphMargin != getKeyGlyphMargin(font, keyglyph = glyphname, direction = direction):
				return True
	return False

# def sortGroupsByGlyphOrder(font, direction, shortnames = False):
# 	listGroups = []
# 	listShortNames = []
# 	hashKernDic = TDHashKernDic(font)
# 	for glyphname in font.glyphOrder:
# 		if hashKernDic.thisGlyphInGroup(glyphname, direction):
# 			groupname = hashKernDic.getGroupNameByGlyph(glyphname, direction)
# 			if groupname not in listGroups:
# 				listGroups.append(groupname)
# 				listShortNames.append(getDisplayNameGroup(groupname))
# 	if shortnames:
# 		return listShortNames
# 	else:
# 		return listGroups



#
# def getListOfPairsToDisplay (font, hashKernDic, glyphsToDisplay, addSpace = False, deltaKern = None):
# 	pairsToDisplay = []
# 	for tl, tr in getPairsList(glyphsToDisplay, addSpace = addSpace):
# 		hashKernDic.insertTempGlyphInGroup((tl, tr))
# 		pair = researchPair(font, hashKernDic, (tl, tr))
# 		kernValue = pair['kernValue']
# 		if deltaKern != 0 and deltaKern and not pair['exception']:
# 			if not kernValue:
# 				kernValue = 0
# 			kernValue += deltaKern
# 		pairsToDisplay.append({'kernValue': kernValue,
# 		                       'exception': pair['exception'],
# 		                       'L_inGroup': pair['L_inGroup'],
# 		                       'R_inGroup': pair['R_inGroup'],
# 		                       'L_nameForKern': pair['L_nameForKern'],
# 		                       'R_nameForKern': pair['R_nameForKern'],
# 		                       'L_markException': pair['L_markException'],
# 		                       'R_markException': pair['R_markException']
# 		                       })
# 	return pairsToDisplay
#
# def getListOfPairsToDisplay_previewDeltaKern (font, hashKernDic, glyphsToDisplay, deltaKern = None, mixPairs = True):
# 	pairsToDisplay = []
# 	for tl, tr in getPairsList(glyphsToDisplay, addSpace = False):
# 		hashKernDic.insertTempGlyphInGroup((tl, tr))
# 		pair = researchPair(font, hashKernDic, (tl, tr))
# 		# kernValue = self._font.kerning[(pair['L_realName'], pair['R_realName'])]
# 		kernValue = pair['kernValue']
# 		if deltaKern != 0 and deltaKern and not pair['exception']:
# 			if not kernValue:
# 				kernValue = 0
# 			kernValue += deltaKern
# 		if mixPairs:
# 			pairsToDisplay.append({'kernValue': kernValue,
# 			                       'exception': pair['exception'],
# 			                       'L_inGroup': pair['L_inGroup'],
# 			                       'R_inGroup': pair['R_inGroup'],
# 			                       'L_nameForKern': pair['L_nameForKern'],
# 			                       'R_nameForKern': pair['R_nameForKern'],
# 			                       'L_markException': pair['L_markException'],
# 			                       'R_markException': pair['R_markException']
# 			                       })
# 		else:
# 			pairsToDisplay.append({'kernValue': kernValue,
# 			                       'exception': pair['exception'],
# 			                       'L_inGroup': pair['L_inGroup'],
# 			                       'R_inGroup': pair['R_inGroup'],
# 			                       'L_nameForKern': pair['L_realName'],
# 			                       'R_nameForKern': pair['R_realName'],
# 			                       'L_markException': pair['L_markException'],
# 			                       'R_markException': pair['R_markException']
# 			                       })
#
# 	return pairsToDisplay
#
#
#
# PAIR_INFO_NONE = 0
# PAIR_INFO_ORPHAN = 30
# PAIR_INFO_EXCEPTION = 20
# PAIR_INFO_EMPTY = 40  # hight rating in sort
# PAIR_INFO_ATTENTION = 10
# PAIR_INFO_EXCEPTION_DELETED = 100
# PAIR_INFO_ERROR = 90
#
#
# def getKernPairInfo_v2( font, hashKernDic, pair):
# 	tl, tr = pair
# 	# TODO need more info about empty groups?
# 	if hashKernDic.thisGroupIsMMK(tl) and len(font.groups[hashKernDic.getGroupNameByGlyph(tl, side = 'L')]) == 0:
# 		return (PAIR_INFO_EMPTY, tl, tr)
# 	if hashKernDic.thisGroupIsMMK(tr) and len(font.groups[hashKernDic.getGroupNameByGlyph(tr, side = 'R')]) == 0:
# 		return (PAIR_INFO_EMPTY, tl, tr)
#
# 	if (tl,tr) not in font.kerning:
# 		parentL = hashKernDic.getGroupNameByGlyph(tl, side = 'L')
# 		parentR = hashKernDic.getGroupNameByGlyph(tr, side = 'R')
# 		# print ('pair removed', tl,tr,parentL,parentR)
# 		return (PAIR_INFO_EXCEPTION_DELETED, parentL,parentR)#tl,tr) # ???????????
#
# 	l = hashKernDic.getKeyGlyphByGroupname(tl)
# 	r = hashKernDic.getKeyGlyphByGroupname(tr)
#
# 	if hashKernDic.thisGroupIsMMK(tl):
# 		for nl in font.groups[tl]:
# 			if (nl,tr) in font.kerning:
# 				# print('exc left', nl, tr)
# 				return (PAIR_INFO_ATTENTION, nl, tr) # return first exception from group
# 	if hashKernDic.thisGroupIsMMK(tr):
# 		for nr in font.groups[tr]:
# 			if (tl,nr) in font.kerning:
# 				# print('exc right', tl, nr)
# 				return (PAIR_INFO_ATTENTION, tl, nr)
#
# 	# if not hashKernDic.thisGroupIsMMK(tl) and not hashKernDic.thisGroupIsMMK(tr):
# 	# 	parentL = hashKernDic.getGroupNameByGlyph(tl, side = 'L')
# 	# 	parentR = hashKernDic.getGroupNameByGlyph(tr, side = 'R')
# 	# 	if parentL != tl and parentR != tr:
# 	# 		return (PAIR_INFO_ATTENTION, tl, tr)
#
#
#
# 	respair = researchPair(font, hashKernDic, (l,r))
# 	L_realName = respair['L_realName']
# 	R_realName = respair['R_realName']
# 	exception = respair['exception']
# 	# L_inGroup = respair['L_inGroup']
# 	# R_inGroup = respair['R_inGroup']
# 	L_nameForKern = respair['L_nameForKern']
# 	R_nameForKern = respair['R_nameForKern']
# 	# L_markException = respair['L_markException']
# 	# R_markException = respair['R_markException']
# 	if exception:
# 		if L_realName == L_nameForKern and R_realName == R_nameForKern:
# 			# print ('attention', l,r,L_nameForKern, R_nameForKern)
# 			return (PAIR_INFO_ATTENTION, L_nameForKern, R_nameForKern)
# 		if L_realName != L_nameForKern and R_realName !=R_nameForKern:
# 			# print('orphan', l, r, L_nameForKern, R_nameForKern)
# 			return (PAIR_INFO_ORPHAN, L_nameForKern, R_nameForKern)
# 		if L_realName != L_nameForKern or R_realName !=R_nameForKern:
# 			# print('exec', l, r, L_nameForKern, R_nameForKern)
# 			return (PAIR_INFO_EXCEPTION, L_nameForKern, R_nameForKern)
#
# 	if hashKernDic.thisGroupIsMMK(tl) and hashKernDic.thisGroupIsMMK(tr):
# 		for nl in font.groups[tl]:
# 			for nr in font.groups[tr]:
# 				if (nl,nr) in font.kerning:
# 					# print('deep investigated exc', tl, nr)
# 					return (PAIR_INFO_ATTENTION, tl, nr)
#
# 	return (PAIR_INFO_NONE, tl, tr)
#
#
#
# def getKernPairInfo( font, hashKernDic, pair):
# 	tl,tr = pair
# 	# TODO need more info about empty groups?
# 	if hashKernDic.thisGroupIsMMK(tl) and len(font.groups[hashKernDic.getGroupNameByGlyph(tl,side = 'L')]) == 0:
# 		return (PAIR_INFO_EMPTY, tl, tr)
# 	if hashKernDic.thisGroupIsMMK(tr) and len(font.groups[hashKernDic.getGroupNameByGlyph(tr, side = 'R')]) == 0:
# 		return (PAIR_INFO_EMPTY, tl, tr)
#
# 	if hashKernDic.thisGroupIsMMK(tl) and hashKernDic.thisGroupIsMMK(tr):
# 		for nl in font.groups[tl]:
# 			if (nl,tr) in font.kerning:
# 				return (PAIR_INFO_ATTENTION, nl, tr) # return first exception from group
# 		for nr in font.groups[tr]:
# 			if (tl,nr) in font.kerning:
# 				return (PAIR_INFO_ATTENTION, tl, nr)
#
# 	if not hashKernDic.thisGroupIsMMK(tl) and not hashKernDic.thisGroupIsMMK(tr):
# 		parentL = hashKernDic.getGroupNameByGlyph(tl,side = 'L')
# 		parentR = hashKernDic.getGroupNameByGlyph(tr,side = 'R')
# 		if hashKernDic.thisGroupIsMMK(parentL) and hashKernDic.thisGroupIsMMK(parentR):
# 			if (tl,tr) in font.kerning:
# 				return (PAIR_INFO_ORPHAN, parentL, parentL) # return parent names of groups
# 			else:
# 				return (PAIR_INFO_EXCEPTION_DELETED, parentL, parentL)
#
# 	if hashKernDic.thisGroupIsMMK(tl) and not hashKernDic.thisGroupIsMMK(tr):
# 		parent = hashKernDic.getGroupNameByGlyph(tr,side = 'R')
# 		if hashKernDic.thisGroupIsMMK(parent):
# 			if (tl,tr) in font.kerning:
# 				return (PAIR_INFO_EXCEPTION, tl, parent)
# 			else:
# 				return (PAIR_INFO_EXCEPTION_DELETED, tl, parent)
#
# 	if not hashKernDic.thisGroupIsMMK(tl) and hashKernDic.thisGroupIsMMK(tr):
# 		parent = hashKernDic.getGroupNameByGlyph(tl,side = 'L')
# 		if hashKernDic.thisGroupIsMMK(parent):
# 			if (tl,tr) in font.kerning:
# 				return (PAIR_INFO_EXCEPTION, parent, tr)
# 			else:
# 				return (PAIR_INFO_EXCEPTION_DELETED, parent, tr)
#
# 	if not hashKernDic.thisGroupIsMMK(tl) and not hashKernDic.thisGroupIsMMK(tr):
# 		respair = researchPair(font, hashKernDic, (tl,tr))
# 		if respair['exception']:
# 			# print ('*'*80)
# 			# print ('getiing info from researchPair', tl, tr)
# 			# for k,v in respair.items():
# 			# 	print (k,v)
# 			parentL = respair['L_nameForKern']
# 			parentR = respair['R_nameForKern']
# 			return (PAIR_INFO_EXCEPTION, parentL, parentR)
#
# 	return (PAIR_INFO_NONE,tl,tr)


# def translateKeyCodesToKernToolCommands (keycode):
# 	key = keycode['key']
# 	mod = keycode['mod']
# 	value = None
# 	command = None
# 	# print (key, mod)
# 	# exception = False
# 	# delete = False
# 	# nextPair = False
# 	# prevPair = False
# 	if key:
# 		if key == 'left':
# 			value = -10
# 			command = COMMAND_SET_LEFTKEY
# 			if mod:
# 				if mod == 'Alt':
# 					command = COMMAND_SET_ALT_LEFTKEY
# 				elif mod == 'Shift':
# 					command = COMMAND_SET_SHIFT_LEFTKEY
# 				elif mod == 'Cmd':
# 					command = COMMAND_SET_CMD_LEFTKEY
# 				elif mod == 'Alt+Shift':
# 					command = COMMAND_SET_ALT_SHIFT_LEFTKEY
#
# 		elif key == 'right':
# 			value = 10
# 			command = COMMAND_SET_RIGHTKEY
# 			if mod:
# 				if mod == 'Alt':
# 					command = COMMAND_SET_ALT_RIGHTKEY
# 				elif mod == 'Shift':
# 					command = COMMAND_SET_SHIFT_RIGHTKEY
# 				elif mod == 'Cmd':
# 					command = COMMAND_SET_CMD_RIGHTKEY
# 				elif mod == 'Alt+Shift':
# 					command = COMMAND_SET_ALT_SHIFT_RIGHTKEY
# 		elif key in '1234567890':
# 			command = COMMAND_TAKE_THE_VALUE
# 			value = int(key)
#
# 		elif key == 'up':
# 			command = COMMAND_SET_UPKEY
# 			if mod == 'Alt':
# 				command = COMMAND_SET_ALT_UPKEY
# 			elif mod == 'Shift':
# 				command = COMMAND_SET_SHIFT_UPKEY
# 			elif mod == 'Alt+Shift':
# 				command = COMMAND_SET_ALT_SHIFT_UPKEY
# 		elif key == 'down':
# 			command = COMMAND_SET_DOWNKEY
# 			if mod == 'Alt':
# 				command = COMMAND_SET_ALT_DOWNKEY
# 			elif mod == 'Shift':
# 				command = COMMAND_SET_SHIFT_DOWNKEY
# 			elif mod == 'Alt+Shift':
# 				command = COMMAND_SET_ALT_SHIFT_DOWNKEY
#
# 		elif key == 'pageup':
# 			command = COMMAND_SET_ALT_UPKEY
# 		elif key == 'pagedown':
# 			command = COMMAND_SET_ALT_DOWNKEY
#
# 		elif key == 'e':
# 			command = COMMAND_MAKE_EXCEPTION
# 			if mod == 'Alt':
# 				command = COMMAND_MAKE_EXCEPTION_BOTH_SIDES
# 		elif key == 'backspace':
# 			command = COMMAND_DELETE_PAIR
# 		elif key == 'delete':
# 			command = COMMAND_DELETE_PAIR
# 		elif key == 'forwarddel':
# 			command = COMMAND_DELETE_PAIR
#
#
# 		elif key == 'tab':
# 			if mod == 'Alt':
# 				command = COMMAND_PREV_PAIR
# 			else:
# 				command = COMMAND_NEXT_PAIR
# 		# elif
# 		elif key == '+':  # and mod == 'Cmd':
# 			command = COMMAND_ZOOM_IN
# 		elif key == '-':  # and mod == 'Cmd':
# 			command = COMMAND_ZOOM_OUT
# 		# elif key == 'r':
# 		# 	command = COMMAND_REFRESH
# 		# elif key == 'o':
# 		# 	command = COMMAND_OPEN_PAIRS_FILE
# 		elif key == 'f':
# 			command = COMMAND_FLIP_PAIR
# 		elif key == 'm':
# 			command = COMMAND_SWITCH_EDIT_MODE
# 		# elif key == 't':
# 		# 	command = COMMAND_SWITCH_TOUCHE_MODE
# 		# 	if mod == 'Cmd':
# 		# 		command = COMMAND_FIX_TOUCHES
# 		#
# 		# elif key == 'p':
# 		# 	command = COMMAND_OPEN_PAIRS_BUILDER
# 		# elif key == 'a':
# 		# 	command = COMMAND_PAIRVALUE_AUTOCALCULATE
# 		# 	if mod == 'Cmd':
# 		# 		command = COMMAND_SELECT_ALL
# 		elif key == 'enter':
# 			if mod == 'Alt':
# 				command = COMMAND_ALT_ENTER
# 			else:
# 				command = COMMAND_ENTER
# 		elif key == 'esc':
# 			command = COMMAND_ESCAPE
# 		elif key == 's':
# 			command = COMMAND_SWITCH_PAIR
# 		elif key == 'l':
# 			command = COMMAND_LINKED_MODE
# 		# elif key == 'k':
# 		# 	command = COMMAND_OFF_KERN
# 		elif key == 'b':
# 			command = COMMAND_USE_RAY_MARGINS
#
#
# 		# elif key == 'c':
# 		# 	if mod == 'Cmd':
# 		# 		command = COMMAND_COPYKERN
# 		# elif key == 'v':
# 		# 	if mod == 'Cmd':
# 		# 		command = COMMAND_PASTEKERN
# 		# elif key == 'space':
# 		# 	command = COMMAND_SPACEKEY
# 	# print ('key command', command, value)
# 	return {'value': value,
# 	        'command': command}


# from mojo.drawingTools import *

COLOR_L_PAIR_SELECTION = (0, 0, .5, .2)
COLOR_R_PAIR_SELECTION = (0, .5, 0, .2)

COLOR_L_GROUP_ICON = (0, 0, 1, 1)#(.2, 0, .6, 1)
COLOR_R_GROUP_ICON = (0, 0, 1, 1)#(0, .4, .2, 1)
COLOR_EXCEPTION_GROUP_ICON = (.8, 0, 0, 1)

COLOR_KERN_VALUE_TEXT_SELECTED = (1, 1, 1, 1)
COLOR_KERN_VALUE_TEXT = (0, 0, 0, .8)

COLOR_TITLES = (.1,.2,.25,1)#(0.2, 0.2, 0.7, 1)
COLOR_TITLES_INVERSE = (.5,.6,.65,1)
COLOR_CURSOR = (.5, 0, .5, 1)
COLOR_KERN_VALUE_POSITIVE = (0, .6, 0.2, 1)
COLOR_BACKGROUND = (1, 1, 1, 1) # (1,1,1,1)#
if KERNTOOL_UI_DARKMODE_WARMBACKGROUND:
	COLOR_KERN_VALUE_POSITIVE = (0, .5, 0.1, 1)
	COLOR_BACKGROUND = (.75, .73, .7, 1)  # (1,1,1,1)#

COLOR_KERN_VALUE_NEGATIVE = (.8, 0, 0.2, 1)
COLOR_TOUCHE = (1, 0, 0, 1)
COLOR_KERN_VALUE_ZERO = (1, .6, 0, 1)
COLOR_ALPHA_REGULAR = .2
COLOR_ALPHA_SELECTED = 1

COLOR_EXCEPTION_MARK = (1, 0, 0, 1)
COLOR_EXCEPTION_MARK_SELECTED = (1, 1, 1, .8)
COLOR_PAIR_SELECTED = (0, 0, 1, 1)

COLOR_VIRTUAL_GLYPH = (.2, 0, .5, 1)

COLOR_WHITE = (1, 1, 1, 1)
COLOR_BLACK = (0, 0, 0, 1)
COLOR_GREY_50 = (0.5, 0.5, 0.5, 1)
COLOR_GREY_30 = (.65, .65, .65, 1)
COLOR_GREY_20 = (.8, .8, .8, 1)
COLOR_GREY_10 = (.9, .9, .9, 1)
COLOR_GREY_50_A = (0.5, 0.5, 0.5, .5)
COLOR_GREY_20_A = (.8, .8, .8, .2)
COLOR_GREY_10_A = (.9, .9, .9, .1)


# def fillRGB (color=(0, 0, 0, 1), alpha = 1):
# 	r, g, b, a = color
# 	if alpha != 1:
# 		a = alpha
# 		print (alpha)
# 	fill(r, g, b, a)


# def fillRGBA (color=(0, 0, 0), alpha=1):
# 	r, g, b = color
# 	drawingTools.fill(r, g, b, alpha)