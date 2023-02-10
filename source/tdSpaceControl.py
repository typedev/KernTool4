import importlib
import vanilla.dialogs
from merz import *
from fontParts import *
from mojo.tools import IntersectGlyphWithLine
# from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber, registerRoboFontSubscriber, registerCurrentFontSubscriber
# from merz.tools.drawingTools import NSImageDrawingTools
#
# import tdKernToolEssentials4
# importlib.reload(tdKernToolEssentials4)
# from tdKernToolEssentials4 import *

import tdGlyphsMatrix
importlib.reload(tdGlyphsMatrix)

# import tdCanvasKeysDecoder
# importlib.reload(tdCanvasKeysDecoder)

# import tdPairsMaker
# importlib.reload(tdPairsMaker)
# from tdPairsMaker import PairsBuilderDialogWindow

import tdGlyphsMerzView
importlib.reload(tdGlyphsMerzView)
from tdGlyphsMerzView import *

import tdKeyCommander
importlib.reload(tdKeyCommander)
from tdKeyCommander import *

import tdLangSet
importlib.reload(tdLangSet)
from tdLangSet import *

from lib.eventTools.eventManager import postEvent, publishEvent


SELECTION_MODE_GLYPH = 1
SELECTION_MODE_PAIR = 2
SELECTION_MODE_LINE = 3

EDITMODE_KERNING = 1
EDITMODE_MARGINS = 2
EDITMODE_OFF = 0

SIDE_1 = 'L' # left side
SIDE_2 = 'R' # right side


ID_KERNING_GROUP = 'public.kern'
ID_GROUP_LEFT = '.kern1.'
ID_GROUP_RIGHT = '.kern2.'

ID_GROUP_MASK_1 = ID_KERNING_GROUP.replace('.kern', ID_GROUP_LEFT) #+ ID_GROUP_LEFT
ID_GROUP_MASK_2 = ID_KERNING_GROUP.replace('.kern', ID_GROUP_RIGHT) #+ ID_GROUP_RIGHT

ID_MARGINS_GROUP = 'public.margins' # '.margins'
ID_MARGINS_GROUP_LEFT = '.margins1.'
ID_MARGINS_GROUP_RIGHT  = '.margins2.'

ID_GROUP_MARGINS_MASK_1 = ID_MARGINS_GROUP.replace('.margins', ID_MARGINS_GROUP_LEFT) #+ ID_MARGINS_GROUP_LEFT
ID_GROUP_MARGINS_MASK_2 = ID_MARGINS_GROUP.replace('.margins', ID_MARGINS_GROUP_RIGHT) #+ ID_MARGINS_GROUP_RIGHT


PAIR_INFO_NONE = 0
PAIR_INFO_ORPHAN = 30
PAIR_INFO_EXCEPTION = 20
PAIR_INFO_EMPTY = 40  # hight rating in sort
PAIR_INFO_ATTENTION = 10
PAIR_INFO_EXCEPTION_DELETED = 100
PAIR_INFO_ERROR = 90

GROUP_NOT_FOUNDED = 10
GROUP_IS_EMPTY = 20
GROUP_MISSING_GLYPH = 30



def italicShift (angle, Ypos):
	if angle:
		return Ypos * math.tan(-angle * 0.0175) # abs(angle)
	else:
		return 0

def getDirection (groupname):
	if ID_KERNING_GROUP and ID_GROUP_LEFT in groupname:
		return SIDE_1
	elif ID_KERNING_GROUP and ID_GROUP_RIGHT in groupname:
		return SIDE_2
	elif ID_MARGINS_GROUP and ID_MARGINS_GROUP_LEFT in groupname:
		return SIDE_1
	elif ID_MARGINS_GROUP and ID_MARGINS_GROUP_RIGHT in groupname:
		return SIDE_2
	else:
		# print ('ERROR!!! Wrong Group Name')
		return None

def getDisplayNameGroup(groupname):
	# RF3 style
	if not groupname: return
	mask1 = ID_GROUP_MASK_1#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_LEFT
	mask2 = ID_GROUP_MASK_2#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_RIGHT
	mask3 = ID_GROUP_MARGINS_MASK_1
	mask4 = ID_GROUP_MARGINS_MASK_2
	if mask1 in groupname:
		return groupname.replace(mask1,'@ ') # '@_'
	elif mask2 in groupname:
		return groupname.replace(mask2,'@ ')
	elif mask3 in groupname:
		return groupname.replace(mask3, '# ')
	elif mask4 in groupname:
		return groupname.replace(mask4, '# ')
	else:
		return groupname

def getDisplayNameGroupClipped(groupname):
	# RF3 style
	if not groupname: return
	mask1 = ID_GROUP_MASK_1#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_LEFT
	mask2 = ID_GROUP_MASK_2#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_RIGHT
	mask3 = ID_GROUP_MARGINS_MASK_1
	mask4 = ID_GROUP_MARGINS_MASK_2
	if mask1 in groupname:
		return groupname.replace(mask1, '') # '@_'
	elif mask2 in groupname:
		return groupname.replace(mask2, '')
	elif mask3 in groupname:
		return groupname.replace(mask3, '')
	elif mask4 in groupname:
		return groupname.replace(mask4, '')
	else:
		return groupname

def getMargins(glyph, rounded = True, useRayBeam = False, rayBeamPosition = 0):
	italicAngle = 0
	if glyph.font:
		italicAngle = glyph.font.info.italicAngle
	if useRayBeam:
		l = glyph.getRayLeftMargin(rayBeamPosition)
		r = glyph.getRayRightMargin(rayBeamPosition)
	else:
		if italicAngle:
			l = glyph.angledLeftMargin
			r = glyph.angledRightMargin
		else:
			l = glyph.leftMargin
			r = glyph.rightMargin
	if not l:
		l = 0
	if not r:
		r = 0
	if rounded:
		l = int(round(l, 0))
		r = int(round(r, 0))
	return (l,r)


def getIntersectGlyphWithHorizontalBeam(glyph, rayBeamPosition = 0):
	try:
		xg,yg,wg,hg = glyph.bounds
	except:
		return
	intersections = sorted(IntersectGlyphWithLine(glyph, ((xg, rayBeamPosition), (wg, rayBeamPosition)), canHaveComponent=True, addSideBearings=False))
	if not (len(intersections) % 2 == 0): return
	result = []
	for i, (x, y) in enumerate(intersections[0:-1:1]):
		xn, yn = intersections[i+1]
		result.append(dict(points = (x, xn), width = round((xn - x),1)))
	return result

def getIntersectGlyphWithVerticalBeam(glyph, rayBeamPosition = 0):
	# try:
	# 	xg,yg,wg,hg = glyph.bounds
	# except:
	# 	pass
	intersections = sorted(IntersectGlyphWithLine(glyph, ((rayBeamPosition, -350), (rayBeamPosition, 1200)), canHaveComponent=True, addSideBearings=False))
	if not (len(intersections) % 2 == 0): return
	result = []
	for i, (x, y) in enumerate(intersections[0:-1:1]):
		xn, yn = intersections[i+1]
		result.append(dict(points = (y, yn), height = round((yn - y),1)))
	return result

def fillglyphsline(font, glyphsline, marks, mapGlyphs, glyphname, margin, side, useRayBeam, rayBeamPosition):
	if glyphname in mapGlyphs: # glyph is basic for some composites
		if glyphname not in glyphsline:
			glyphsline.append(glyphname)
			(lm, rm) = getMargins(font[glyphname], useRayBeam = useRayBeam, rayBeamPosition = rayBeamPosition)
			if side == SIDE_1:
				if margin != rm:
					marks.append(True)
				else:
					marks.append(False)
			elif side == SIDE_2:
				if margin != lm:
					marks.append(True)
				else:
					marks.append(False)

		for n in list(mapGlyphs[glyphname]): # get list of composites for a basic glyph
			if n not in glyphsline:
				glyphsline.append(n)
				(lm, rm) = getMargins(font[glyphname], useRayBeam = useRayBeam, rayBeamPosition = rayBeamPosition)
				if side == SIDE_1:
					if margin != rm:
						marks.append(True)
					else:
						marks.append(False)
				elif side == SIDE_2:
					if margin != lm:
						marks.append(True)
					else:
						marks.append(False)

	else: # the glyph are not basic
		if glyphname not in glyphsline:
			if font[glyphname].components: # glyph has components? lets find basic glyphs (recurse)
				_glyphname = font[glyphname].components[0].baseGlyph
				if _glyphname:
					fillglyphsline(font, glyphsline, marks, mapGlyphs, _glyphname, margin, side, useRayBeam,rayBeamPosition)
				else:
					print ('err')
			else: # no, glyph has no components
				glyphsline.append(glyphname)
				(lm, rm) = getMargins(font[glyphname], useRayBeam = useRayBeam, rayBeamPosition = rayBeamPosition)
				if side == SIDE_1:
					if margin != rm:
						marks.append(True)
					else:
						marks.append(False)
				elif side == SIDE_2:
					if margin != lm:
						marks.append(True)
					else:
						marks.append(False)
	return glyphsline, marks


def makeFontsHashGroupsLib(fonts, langSet = None):
	result = {}
	for font in fonts:
		if langSet:
			langSet.setupPatternsForFont(font)
		result[font] = TDHashGroupsDic(font, langSet)
	return result

def researchPair (font, hashDic, rawpair):
	tl, tr = rawpair
	l = cutUniqName(tl)
	r = cutUniqName(tr)
	# ldic = {}
	# rdic = {}

	pairsdic = font.kerning

	leftGlyphInGroup = False
	rightGlyphInGroup = False
	exception = False

	gL = hashDic.getGroupNameByGlyph(l, SIDE_1) # was tl!!!
	if hashDic.isKerningGroup(gL):  # != tl:
		leftGlyphInGroup = True

	gR = hashDic.getGroupNameByGlyph(r, SIDE_2) # was tr!!!
	if hashDic.isKerningGroup(gR):  # != tr:
		rightGlyphInGroup = True

	if (l, r) in pairsdic and (pairsdic[(l, r)] != None):  # and (pairsdic[(l, r)] != 0):
		_leftGlyphInGroup = leftGlyphInGroup
		_rightGlyphInGroup = rightGlyphInGroup
		if leftGlyphInGroup:
			exception = True
			_leftGlyphInGroup = not leftGlyphInGroup
		if rightGlyphInGroup:
			exception = True
			_rightGlyphInGroup = not rightGlyphInGroup
		# print 'exception v1'
		return {'L_realName': l,
		        'R_realName': r,
		        'kernValue': pairsdic[(l, r)],
		        'exception': exception,
		        'L_inGroup': _leftGlyphInGroup,
		        'R_inGroup': _rightGlyphInGroup,
		        'L_nameForKern': gL,
		        'R_nameForKern': gR,
		        'L_markException': leftGlyphInGroup,
		        'R_markException': rightGlyphInGroup
		}

	if (gL, r) in pairsdic and (pairsdic[(gL, r)] != None):  # and (pairsdic[(gL, r)] != 0):
		if rightGlyphInGroup:
			exception = True
		# print 'exception v2'
		return {'L_realName': gL,  # (gL, r, exception, leftGlyphInGroup, False, gL, gR)
		        'R_realName': r,
		        'kernValue': pairsdic[(gL, r)],
		        'exception': exception,
		        'L_inGroup': leftGlyphInGroup,
		        'R_inGroup': False,
		        'L_nameForKern': gL,
		        'R_nameForKern': gR,
		        'L_markException': leftGlyphInGroup,
		        'R_markException': rightGlyphInGroup
		}

	if (l, gR) in pairsdic and (pairsdic[(l, gR)] != None):  # and (pairsdic[(l, gR)] != 0):
		if leftGlyphInGroup:
			exception = True
		# print 'exception v3'
		return {'L_realName': l,  # (l, gR, exception, False, rightGlyphInGroup, gL, gR)
		        'R_realName': gR,
		        'kernValue': pairsdic[(l, gR)],
		        'exception': exception,
		        'L_inGroup': False,
		        'R_inGroup': rightGlyphInGroup,
		        'L_nameForKern': gL,
		        'R_nameForKern': gR,
		        'L_markException': leftGlyphInGroup,
		        'R_markException': rightGlyphInGroup
		}

	if (gL, gR) in pairsdic and (pairsdic[(gL, gR)] != None):  # and (pairsdic[(gL, gR)] != 0):
		# print 'exception v4'

		return {'L_realName': gL,  # (gL, gR, False, leftGlyphInGroup, rightGlyphInGroup, gL, gR)
		        'R_realName': gR,
		        'kernValue': pairsdic[(gL, gR)],
		        'exception': False,
		        'L_inGroup': leftGlyphInGroup,
		        'R_inGroup': rightGlyphInGroup,
		        'L_nameForKern': gL,
		        'R_nameForKern': gR,
		        'L_markException': leftGlyphInGroup,
		        'R_markException': rightGlyphInGroup
		}

	# return {'L_realName': cutUniqName(gL),
	#         'R_realName': cutUniqName(gR),
	#         'kernValue': pairsdic[(cutUniqName(gL), cutUniqName(gR))],
	#         'exception': False,
	#         'L_inGroup': leftGlyphInGroup,
	#         'R_inGroup': rightGlyphInGroup,
	#         'L_nameForKern': gL,
	#         'R_nameForKern': gR,
	#         'L_markException': leftGlyphInGroup,
	#         'R_markException': rightGlyphInGroup
	# }
	cGL = cutUniqName(gL)
	cGR = cutUniqName(gR)
	if (cGL, cGR) in pairsdic:
		return {'L_realName': cGL,
		        'R_realName': cGR,
		        'kernValue': pairsdic[(cGL, cGR)],
		        'exception': False,
		        'L_inGroup': leftGlyphInGroup,
		        'R_inGroup': rightGlyphInGroup,
		        'L_nameForKern': gL,
		        'R_nameForKern': gR,
		        'L_markException': leftGlyphInGroup,
		        'R_markException': rightGlyphInGroup
		}
	else:
		return {'L_realName': cGL,
		        'R_realName': cGR,
		        'kernValue': None,
		        'exception': False,
		        'L_inGroup': leftGlyphInGroup,
		        'R_inGroup': rightGlyphInGroup,
		        'L_nameForKern': gL,
		        'R_nameForKern': gR,
		        'L_markException': leftGlyphInGroup,
		        'R_markException': rightGlyphInGroup
		        }


# PAIR_INFO_NONE = 0
# PAIR_INFO_ORPHAN = 30
# PAIR_INFO_EXCEPTION = 20
# PAIR_INFO_EMPTY = 40  # hight rating in sort
# PAIR_INFO_ATTENTION = 10
# PAIR_INFO_EXCEPTION_DELETED = 100
# PAIR_INFO_ERROR = 90


def getKernPairNotes( font, hashKernDic, pair): # version 2
	tl, tr = pair
	if hashKernDic.isKerningGroup(tl) and len(font.groups[hashKernDic.getGroupNameByGlyph(tl, side = SIDE_1)]) == 0:
		return (PAIR_INFO_EMPTY, tl, tr)
	if hashKernDic.isKerningGroup(tr) and len(font.groups[hashKernDic.getGroupNameByGlyph(tr, side = SIDE_2)]) == 0:
		return (PAIR_INFO_EMPTY, tl, tr)

	if (tl,tr) not in font.kerning:
		parentL = hashKernDic.getGroupNameByGlyph(tl, side = SIDE_1)
		parentR = hashKernDic.getGroupNameByGlyph(tr, side = SIDE_2)
		# print ('pair removed', tl,tr,parentL,parentR)
		return (PAIR_INFO_EXCEPTION_DELETED, parentL,parentR)#tl,tr) # ???????????

	l = hashKernDic.getKeyGlyphByGroupname(tl)
	r = hashKernDic.getKeyGlyphByGroupname(tr)

	if hashKernDic.isKerningGroup(tl):
		for nl in font.groups[tl]:
			if (nl,tr) in font.kerning:
				# print('exc left', nl, tr)
				return (PAIR_INFO_ATTENTION, nl, tr) # return first exception from group
	if hashKernDic.isKerningGroup(tr):
		for nr in font.groups[tr]:
			if (tl,nr) in font.kerning:
				# print('exc right', tl, nr)
				return (PAIR_INFO_ATTENTION, tl, nr)

	# if not hashKernDic.thisGroupIsMMK(tl) and not hashKernDic.thisGroupIsMMK(tr):
	# 	parentL = hashKernDic.getGroupNameByGlyph(tl, side = 'L')
	# 	parentR = hashKernDic.getGroupNameByGlyph(tr, side = 'R')
	# 	if parentL != tl and parentR != tr:
	# 		return (PAIR_INFO_ATTENTION, tl, tr)



	respair = researchPair(font, hashKernDic, (l,r))
	L_realName = respair['L_realName']
	R_realName = respair['R_realName']
	exception = respair['exception']
	# L_inGroup = respair['L_inGroup']
	# R_inGroup = respair['R_inGroup']
	L_nameForKern = respair['L_nameForKern']
	R_nameForKern = respair['R_nameForKern']
	# L_markException = respair['L_markException']
	# R_markException = respair['R_markException']
	if exception:
		if L_realName == L_nameForKern and R_realName == R_nameForKern:
			# print ('attention', l,r,L_nameForKern, R_nameForKern)
			return (PAIR_INFO_ATTENTION, L_nameForKern, R_nameForKern)
		if L_realName != L_nameForKern and R_realName !=R_nameForKern:
			# print('orphan', l, r, L_nameForKern, R_nameForKern)
			return (PAIR_INFO_ORPHAN, L_nameForKern, R_nameForKern)
		if L_realName != L_nameForKern or R_realName !=R_nameForKern:
			# print('exec', l, r, L_nameForKern, R_nameForKern)
			return (PAIR_INFO_EXCEPTION, L_nameForKern, R_nameForKern)

	if hashKernDic.isKerningGroup(tl) and hashKernDic.isKerningGroup(tr):
		for nl in font.groups[tl]:
			for nr in font.groups[tr]:
				if (nl,nr) in font.kerning:
					# print('deep investigated exc', tl, nr)
					return (PAIR_INFO_ATTENTION, tl, nr)

	return (PAIR_INFO_NONE, tl, tr)




class TDHashGroupsDic(object):
	def __init__ (self, font, langSet = None):
		self.leftDic = {}
		self.rightDic = {}
		self.leftMarginsDic = {}
		self.rightMarginsDic = {}
		self.dicOfKeyGlyphsByGroup = {}
		self.font = font
		self.langSet = langSet
		self.history = []
		self.trackHistory = True
		self.groupsHasErrorList = []
		self.makeReverseGroupsMapping()
		# self.langSet = TDLangSet()

	def setFont(self, font, langSet = None):
		# print ('setup hashkernDic')
		self.leftDic = {}
		self.rightDic = {}
		self.leftMarginsDic = {}
		self.rightMarginsDic = {}
		self.dicOfKeyGlyphsByGroup = {}
		self.font = font
		self.langSet = langSet
		self.history = []
		self.groupsHasErrorList = []
		self.makeReverseGroupsMapping()

	def clearHistory(self):
		self.history = []

	def setHistoryPause(self):
		self.trackHistory = False
	def setHistoryResume(self):
		self.trackHistory = True


	def isLeftSideGroup (self, groupname):
		result = False
		# if groupname[ID_GROUP_DIRECTION_POSITION] == SIDE_1:
		if ID_GROUP_LEFT in groupname or ID_MARGINS_GROUP_LEFT in groupname:
			result = True
		return result

	def isKerningGroup (self, groupname):
		if groupname.startswith(ID_KERNING_GROUP):
			return True
		return False

	def isMarginsGroup(self, groupname):
		if groupname.startswith(ID_MARGINS_GROUP):
			return True
		return False

	def checkMapAndAddGlyph2hashMap(self, dic, glyphname, groupname):
		if glyphname not in dic:
			dic[glyphname] = groupname
			return True
		else:
			print ('ERROR: %s already in group %s and %s' % (glyphname, dic[glyphname], groupname))
			print ('The extension may not work correctly.\nPlease decide in which group to leave this glyph and restart the extension')
			return False

	def makeReverseGroupsMapping (self):
		self.leftDic = {}
		self.rightDic = {}
		self.leftMarginsDic = {}
		self.rightMarginsDic = {}
		self.dicOfKeyGlyphsByGroup = {}
		for groupname, content in self.font.groups.items():
			if content:
				self.dicOfKeyGlyphsByGroup[groupname] = content[0]
			else:
				self.groupsHasErrorList.append(groupname)
			if self.isKerningGroup(groupname):
				if self.isLeftSideGroup(groupname):
					for glyphname in content:
						# self.leftDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.leftDic, glyphname, groupname)
						if glyphname not in self.font:
							self.groupsHasErrorList.append(groupname)
				else:
					for glyphname in content:
						# self.rightDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.rightDic, glyphname, groupname)
						if glyphname not in self.font:
							self.groupsHasErrorList.append(groupname)
			elif self.isMarginsGroup(groupname):
				if self.isLeftSideGroup(groupname):
					for glyphname in content:
						# self.leftMarginsDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.leftMarginsDic, glyphname, groupname)
						if glyphname not in self.font:
							self.groupsHasErrorList.append(groupname)

				else:
					for glyphname in content:
						# self.rightMarginsDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.rightMarginsDic, glyphname, groupname)
						if glyphname not in self.font:
							self.groupsHasErrorList.append(groupname)


	def insertTempGlyphInGroup (self, glyphnames):  # , side):
		l, r = glyphnames
		rL = cutUniqName(l)
		rR = cutUniqName(r)

		if rL in self.leftDic:
			self.leftDic[l] = self.leftDic[rL]
			l = self.leftDic[l]

		if rR in self.rightDic:
			self.rightDic[r] = self.rightDic[rR]
			r = self.rightDic[r]
		return l, r

	def getGroupNameByGlyph (self, glyphname, side, mode = EDITMODE_KERNING):
		if mode == EDITMODE_KERNING:
			if side == SIDE_1 and glyphname in self.leftDic:
				return self.leftDic[glyphname]
			if side == SIDE_2 and glyphname in self.rightDic:
				return self.rightDic[glyphname]
		elif mode == EDITMODE_MARGINS:
			if side == SIDE_1 and glyphname in self.leftMarginsDic:
				return self.leftMarginsDic[glyphname]
			if side == SIDE_2 and glyphname in self.rightMarginsDic:
				return self.rightMarginsDic[glyphname]
		return glyphname

	def thisGlyphInGroup(self, glyphname, side, mode = EDITMODE_KERNING):
		if mode == EDITMODE_KERNING:
			if side == SIDE_1 and glyphname in self.leftDic:
				return True
			if side == SIDE_2 and glyphname in self.rightDic:
				return True
		elif mode == EDITMODE_MARGINS:
			if side == SIDE_1 and glyphname in self.leftMarginsDic:
				return True
			if side == SIDE_2 and glyphname in self.rightMarginsDic:
				return True
		return False

	def getKeyGlyphByGroupname(self, groupname):
		if groupname in self.dicOfKeyGlyphsByGroup:
			return self.dicOfKeyGlyphsByGroup[groupname]
		else:
			return groupname

	def getPairsBy(self, key, side):
		if side == SIDE_1:
			return list(filter(lambda p: p[0][0] == (key), self.font.kerning.items()))
		elif side == SIDE_2:
			return list(filter(lambda p: p[0][1] == (key), self.font.kerning.items()))

	def addGlyphsToGroup (self, group, glyphlist, checkKerning=True, checkLanguageCompatibility = False, showAlert = False):
		"""
		function for adding glyphs to a group, if the group does not exist, it will be created
		if the glyph is already in a group of the same class, the operation will be canceled
		if checkKerning = True, existing kerning with this group will be checked:
			if the glyph already has kerning identical to the group, it will be classified as an exception and removed.
			if kerning is different, such an exception will be saved
		"""
		report = []
		glyphlist2add = list(dict.fromkeys(glyphlist)) # filter possible repetitions of glyphs
		if self.trackHistory:
			self.history.append(('add', group, glyphlist2add, checkKerning, checkLanguageCompatibility))
		# def msgCanceled(self, glyphname, side, mode, showAlert):
		# 	txt = 'Glyph %s is already in the group %s, the addition is canceled' % (glyphname, self.getGroupNameByGlyph(glyphname, side, mode))
		# 	if showAlert:
		# 		vanilla.dialogs.message(messageText = 'Operation canceled', informativeText = txt, alertStyle = 'critical')
		# 	else:
		# 		return txt


		def checkingPresenceInGroups(self, group, glyphname, side, mode, showAlert, report):
			"""
			the function checks if the glyph is in a group.
			if the glyph is free returns None,
			if the glyph is already in the group returns its name
			"""
			if self.thisGlyphInGroup(glyphname, SIDE_1, mode) and side == SIDE_1:
				# r = msgCanceled(self, glyphname, SIDE_1, mode, showAlert )
				# report.append((r))
				return glyphname
			elif self.thisGlyphInGroup(glyphname, SIDE_2, mode) and side == SIDE_2:
				# r = msgCanceled(self, glyphname, SIDE_2, mode, showAlert)
				# report.append((r))
				return glyphname
			else:
				if glyphname not in self.font.groups[group]:
					return None
			return glyphname

		newGroup = False
		newcontent = []
		skiped = []
		newPairs = []
		deletedPairs = []
		if group not in self.font.groups:
			self.font.groups[group] = ()
			newGroup = True

		if self.isLeftSideGroup(group):
			side = SIDE_1
		else:
			side = SIDE_2

		for glyphname in glyphlist2add:
			if self.isKerningGroup(group):
				glyphingroup = checkingPresenceInGroups(self, group, glyphname, side, EDITMODE_KERNING, showAlert, report)
				if not glyphingroup:
					newcontent.append(glyphname)
					if checkKerning:
						if side == SIDE_1:
							pairsGlyph = self.getPairsBy(glyphname, side)
							if not newGroup:
								pairsTarget = self.getPairsBy(group, side)
								for (l, r), v in pairsGlyph:
									for (_l, _r), _v in pairsTarget:
										if r == _r and v == _v:
											report.append(('added and cleared', (l,r),v, '=', (_l,_r),_v ))
											self.font.kerning.remove((l, r))
											deletedPairs.append((l,r))
										elif r == _r and v != _v:
											report.append(('added, but saved as exception', (l,r),v, '!=', (_l,_r),_v ))
							else:
								for (l, r), v in pairsGlyph:
									if self.copyKern((l,r),(group,r),report,checkLanguageCompatibility):
										newPairs.append((group,r))
									# report.append (('copyed from', l,r,v, 'to', group,r))
									# self.font.kerning[(group,r)] = self.font.kerning[(l,r)]
									report.append (('removed as exception', (l,r)))
									self.font.kerning.remove((l, r))
									deletedPairs.append((l,r))
									newGroup = False

						if side == SIDE_2:
							pairsGlyph = self.getPairsBy(glyphname, side)
							if not newGroup:
								pairsTarget = self.getPairsBy(group, side)
								for (l, r), v in pairsGlyph:
									for (_l, _r), _v in pairsTarget:
										if l == _l and v == _v:
											report.append(('added and cleared', (l,r),v, '=', (_l,_r),_v ))
											self.font.kerning.remove((l,r))
											deletedPairs.append((l, r))
										elif l == _l and v != _v:
											report.append(('added, but saved as exception', (l,r),v, '!=', (_l,_r),_v ))
							else:
								for (l, r), v in pairsGlyph:
									if self.copyKern((l,r),(l,group),report,checkLanguageCompatibility):
										newPairs.append((l,group))
									# report.append(('copyed from', l,r,v, 'to', l,group))
									# self.font.kerning[(l,group)] = self.font.kerning[(l,r)]
									report.append(('removed as exception', (l, r)))
									self.font.kerning.remove((l, r))
									deletedPairs.append((l,r))
									newGroup = False
				else:
					skiped.append(glyphingroup)


			elif self.isMarginsGroup(group):
				glyphingroup = checkingPresenceInGroups(self, group, glyphname, side, EDITMODE_MARGINS, showAlert, report)
				if not glyphingroup:
					newcontent.append(glyphname)
				else:
					skiped.append(glyphingroup)

			else:
				newcontent.append(glyphname)

		if newcontent:
			self.font.groups[group] += tuple(newcontent)
			self.makeReverseGroupsMapping()
		# if report:
		# 	for i in report:
		# 		print (' '.join([ str(n) for n in i]))
		return (skiped, newPairs, deletedPairs)

	def repositionGlyphsInGroup (self, group, idx=0, glyphlist=None):
		# RF3 style
		if idx > len(self.font.groups[group]): return
		try:
			tempgroup = list(self.font.groups[group])
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
			self.font.groups[group] = tuple(tempgroup)
		except:
			pass

	def copyKern (self, pairSource, pairDest, report, checkLanguageCompatibility=False):
		if not checkLanguageCompatibility:
			v = self.font.kerning[pairSource]
			self.font.kerning[pairDest] = self.font.kerning[pairSource]
			report.append(('kerning was copied to', pairDest, v, 'from', pairSource, v))
			return True
		else:
			if self.checkPairLanguageCompatibilityGroupped(pairDest) and self.checkPairLanguageCompatibilityGroupped(pairSource):
				v = self.font.kerning[pairSource]
				self.font.kerning[pairDest] = self.font.kerning[pairSource]
				report.append(('kerning was copied to', pairDest, v, 'from', pairSource, v, 'compatibility verified'))
				return True
			else:
				v = self.font.kerning[pairSource]
				report.append(('pair is not compatible, ignored', pairDest, v, 'source was', pairSource, v))
				return False


	def delGlyphsFromGroup (self, group, glyphlist, checkKerning=True, rebuildMap = True, checkLanguageCompatibility = False):
		"""
		function to remove glyphs from a group
		if kerning check mode is enabled, existing kerning with this group will be checked:
			if a group has a kerning with a glyph or other group, this kerning will be copied to the glyph being removed,
			this will be classified as an exception
		"""
		report = []
		newPairs = []
		deletedPairs = []
		if self.trackHistory:
			self.history.append(('remove', group, glyphlist, checkKerning, checkLanguageCompatibility))
		if group in self.font.groups:
			newcontent = []
			for glyphname in self.font.groups[group]:
				if glyphname not in glyphlist:
					newcontent.append(glyphname)

			if checkKerning:
				if self.isLeftSideGroup(group):
					side = SIDE_1
				else:
					side = SIDE_2

				if side == SIDE_1:
					pairs = self.getPairsBy(group, side)
					for glyph in glyphlist:
						glyphpairs = self.getPairsBy(glyph, side)
						for (l,r),v in pairs:
							if (glyph, r) in self.font.kerning and self.font.kerning[(glyph, r)] != v:
								report.append(('removed from group and keep exception', (glyph, r), v, '!=', (l, r), v))
							else:
								if self.copyKern((l,r), (glyph, r), report, checkLanguageCompatibility = checkLanguageCompatibility):
									newPairs.append((glyph, r))
							# self.font.kerning[(glyph, r)] = self.font.kerning[(l, r)]
							# report.append (('removed from group and saved as exception', glyph,r,v, '=', l,r,v))
						if glyphpairs:
							for (l, r), v in glyphpairs:
								if (glyph, r) in self.font.kerning and self.font.kerning[(glyph, r)] != v:
									report.append(('removed from group and keep exception', (glyph, r), v, '!=', (l, r), v))
								else:
									if self.copyKern((l, r), (glyph, r), report, checkLanguageCompatibility = checkLanguageCompatibility):
										newPairs.append((glyph, r))
								# self.font.kerning[(glyph, r)] = self.font.kerning[(l, r)]
								# report.append (('removed from group and saved as exception', glyph, r, v, '=', l, r, v))
				if side == SIDE_2:
					pairs = self.getPairsBy(group, side)
					for glyph in glyphlist:
						glyphpairs = self.getPairsBy(glyph, side)
						for (l,r),v in pairs:
							if (l, glyph) in self.font.kerning and self.font.kerning[(l, glyph)] != v:
								report.append(('removed from group and keep exception', (glyph, r), v, '!=', (l, r), v))
							else:
								if self.copyKern((l, r), (l, glyph), report, checkLanguageCompatibility = checkLanguageCompatibility):
									newPairs.append((l, glyph))
							# self.font.kerning[(l, glyph)] = self.font.kerning[(l, r)]
							# report.append (('removed from group and saved as exception', l, glyph,v, '=', l,r,v))
						if glyphpairs:
							for (l, r), v in glyphpairs:
								if (l, glyph) in self.font.kerning and self.font.kerning[(l, glyph)] != v:
									report.append(('removed from group and keep exception', (glyph, r), v, '!=', (l, r), v))
								else:
									if self.copyKern((l, r), (l, glyph), report, checkLanguageCompatibility = checkLanguageCompatibility):
										newPairs.append((l, glyph))
								# self.font.kerning[(l, glyph)] = self.font.kerning[(l, r)]
								# report.append (('removed from group and saved as exception', l, glyph, v, '=', l, r, v))

			self.font.groups[group] = tuple(newcontent)
			if rebuildMap:
				self.makeReverseGroupsMapping()
		# if report:
		# 	for i in report:
		# 		print(' '.join([ str(n) for n in i]))
		return (newPairs, deletedPairs)

	def deleteGroup(self, group, checkKerning = True, checkLanguageCompatibility = False ):
		report = []
		newPairs = []
		deletedPairs = []
		if self.trackHistory:
			self.history.append(('delete', group, checkKerning, checkLanguageCompatibility))
		if group in self.font.groups:
			glyphslist = self.font.groups[group]
			newPairs = self.delGlyphsFromGroup(group, glyphslist, checkKerning = checkKerning,
			                        rebuildMap = False, checkLanguageCompatibility = checkLanguageCompatibility )
			report.append (('group removed', group))
			if self.isKerningGroup(group):
				report.append ( ('clearing kerning' , ''))
				if self.isLeftSideGroup(group):
					side = SIDE_1
				else:
					side = SIDE_2
				if side == SIDE_1:
					pairs = self.getPairsBy(group, SIDE_1)
					for (l,r),v in pairs:
						report.append ( ('removed', (l,r),v))
						self.font.kerning.remove((l,r))
						deletedPairs.append((l,r))
				if side == SIDE_2:
					pairs = self.getPairsBy(group, SIDE_2)
					for (l,r),v in pairs:
						report.append (('removed', (l, r), v))
						self.font.kerning.remove((l,r))
						deletedPairs.append((l,r))

			del self.font.groups[group]
			self.makeReverseGroupsMapping()
		# if report:
		# 	for i in report:
		# 		print(' '.join([ str(n) for n in i]))
		return (newPairs, deletedPairs)

	def renameGroup(self, group, newname, checkKerning = True, checkLanguageCompatibility = False ):
		report = []
		newPairs = []
		deletedPairs = []
		if self.trackHistory:
			self.history.append(('rename', group, newname, checkKerning, checkLanguageCompatibility))
		if group in self.font.groups and newname not in self.font.groups:
			content = list(self.font.groups[group])
			# self.font.groups[newname] = ()
			self.font.groups[newname] = tuple(content)
			if self.isKerningGroup(group):
				if checkKerning:
					if self.isLeftSideGroup(group):
						side = SIDE_1
					else:
						side = SIDE_2
					if side == SIDE_1:
						pairs = self.getPairsBy(group, SIDE_1)
						for (l,r),v in pairs:
							if self.copyKern((l,r),(newname, r),report,checkLanguageCompatibility = checkLanguageCompatibility):
								newPairs.append((newname, r))
							self.font.kerning.remove((l,r))
							deletedPairs.append((l,r))
					if side == SIDE_2:
						pairs = self.getPairsBy(group, SIDE_2)
						for (l,r),v in pairs:
							if self.copyKern((l,r),(l, newname),report,checkLanguageCompatibility = checkLanguageCompatibility):
								newPairs.append((l, newname))
							self.font.kerning.remove((l, r))
							deletedPairs.append((l,r))
			self.font.groups.remove(group)
			# if content:

			self.makeReverseGroupsMapping()
		# if report:
		# 	for i in report:
		# 		print(' '.join([str(n) for n in i]))
		return (newPairs, deletedPairs)



	def checkPairLanguageCompatibility(self, pair):
		if self.langSet:
			return self.langSet.checkPairLanguageCompatibility(self.font, pair)

	def checkPairLanguageCompatibilityGroupped(self, pair, level = 1): # 2 for languages, 1 for basescripts
		l, r = pair
		_l, _r = pair
		if not self.langSet: return True
		if self.isKerningGroup(l) and self.isKerningGroup(r):
			_l = self.getKeyGlyphByGroupname(l)
			_r = self.getKeyGlyphByGroupname(r)

		elif self.isKerningGroup(l) and not self.isKerningGroup(r):
			_l = self.getKeyGlyphByGroupname(l)
			_r = r
			# return self.langSet.checkPairLanguageCompatibility(self.font, (_l, r))
		elif not self.isKerningGroup(l) and self.isKerningGroup(r):
			_l = l
			_r = self.getKeyGlyphByGroupname(r)

			# return self.langSet.checkPairLanguageCompatibility(self.font, (l, _r))
		# else:
		# 	return self.langSet.checkPairLanguageCompatibility(self.font, (l,r))

		if level == 2:
			return self.langSet.checkPairLanguageCompatibility(self.font, (_l, _r))
		else:
			return self.langSet.checkPairBaseScriptCompatibility(self.font, (_l, _r))
		# if self.langSet:
		# 	return self.langSet.checkPairLanguageCompatibility(self.font, pair)

	def checkGroupHasError(self, group):
		if group in self.font.groups:
			if len(self.font.groups[group]) == 0:
				return GROUP_IS_EMPTY
			else:
				for glyph in self.font.groups[group]:
					if glyph not in self.font:
						return GROUP_MISSING_GLYPH
			return 0
		else:
			return GROUP_NOT_FOUNDED




class TDSpaceControl(object):
	def __init__(self, fontsHashKernLib, glyphsView, groupsView = None, mode = EDITMODE_OFF, OFFispossible = False, scalesKern = None, scalesMargins = None):
		self.lastValue = 0
		self.lastMultiply = []
		self.fontsHashKernLib = fontsHashKernLib
		self.scalesKern = scalesKern
		self.scalesMargins = scalesMargins
		self.glyphsView = glyphsView
		self.groupsView = groupsView
		self.editMode = mode
		self.kerningON = False
		self.marginsON = False
		self.kernControl = TDKernControl(fontsHashKernLib, glyphsView, groupsView, ON = True, scales = scalesKern)
		self.marginsControl = TDMarginsControl(fontsHashKernLib, glyphsView, groupsView, ON = False, scales = scalesMargins)

		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_M, callback = self.switchModeCallback)

	# def setupSpaceControl(self):
	# 	pass

	def setupSpaceControl(self, fontsHashKernLib, scalesKern = None, scalesMargins = None):
		self.fontsHashKernLib = fontsHashKernLib
		self.scalesKern = None
		self.scalesMargins = None
		if self.groupsView:
			self.groupsView.fontsHashKernLib = fontsHashKernLib
		if self.glyphsView:
			self.glyphsView.fontsHashKernLib = fontsHashKernLib
		self.kernControl.fontsHashKernLib = fontsHashKernLib
		self.kernControl.scales = scalesKern
		self.marginsControl.fontsHashKernLib = fontsHashKernLib
		self.marginsControl.scales = scalesMargins

	def switchKerningON(self):
		self.kernControl.ON = True
		self.marginsControl.ON = False
		self.editMode = EDITMODE_KERNING

		self.glyphsView.selectionMode = SELECTION_MODE_PAIR
		self.glyphsView.setStatus('mode:kerning', True)
		self.glyphsView.setStatus('mode:margins', False)
		# self.glyphsView.showMargins = False

		if self.groupsView:
			self.groupsView.setStatus('mode:margins', False)
			self.groupsView.setStatus('mode:kerning', True)
			self.groupsView.setStatus('mode:exceptions', True)
			self.groupsView.setStatus('show:beam', False)
			self.groupsView.selectionMode = SELECTION_MODE_PAIR
			# self.groupsView.showMargins = False
			self.groupsView.separatePairs = True
			self.groupsView.linkedMode = False
			self.groupsView.useRayBeam = False

		# self.glyphsView.selectedGlyphs = []
		self.glyphsView.refreshView()
		self.glyphsView.animateCursorStart()
		if self.groupsView:
			self.groupsView.selectedGlyphs = []
			self.groupsView.refreshView()

	def switchMarginsON(self):
		self.kernControl.ON = False
		self.marginsControl.ON = True
		self.editMode = EDITMODE_MARGINS

		self.glyphsView.selectionMode = SELECTION_MODE_GLYPH
		self.glyphsView.showMargins = True
		self.glyphsView.setStatus('mode:margins', True)
		self.glyphsView.setStatus('mode:kerning', False)
		if self.groupsView:
			self.groupsView.setStatus('mode:margins', True)
			self.groupsView.setStatus('mode:kerning', False)
			self.groupsView.setStatus('mode:exceptions', False)
			self.groupsView.selectionMode = SELECTION_MODE_GLYPH
			self.groupsView.showMargins = True
			self.groupsView.showKerning = True
			self.groupsView.separatePairs = False

		# self.glyphsView.selectedGlyphs = []
		self.glyphsView.refreshView()
		self.glyphsView.animateCursorStart()

		if self.groupsView:
			self.groupsView.selectedGlyphs = []
			self.groupsView.refreshView()

	def switchModeCallback(self, sender, value):
		if self.editMode == EDITMODE_MARGINS:
			self.switchKerningON()
		elif self.editMode == EDITMODE_KERNING:
			self.switchMarginsON()


	def checkCommand(self, sender, event):
		# if commands['command'] == COMMAND_SWITCH_EDIT_MODE:
		self.keyCommander.checkCommand(sender, event)

		if sender:
			self.kernControl.checkCommand(sender, event)
			self.marginsControl.checkCommand(sender, event)


	def refreshViews(self):
		# pass
		# print('space control refreshing')
		self.glyphsView.refreshView(justmoveglyphs = True) #justmoveglyphs = True)
		if self.groupsView:
			self.groupsView.refreshView(justmoveglyphs = True) #justmoveglyphs = True)

class TDKernControl(object):
	def __init__ (self, fontsHashKernLib, glyphsView, groupsView = None, ON = False, scales = None):
		self.lastValue = 0
		self.lastMultiply = []
		self.fontsHashKernLib = fontsHashKernLib
		self.glyphsView = glyphsView
		self.groupsView = groupsView
		self.scales = scales
		self.ON = ON
		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_BACKSPACE, callback = self.deletePairCallback)
		self.keyCommander.registerKeyCommand(KEY_LEFT, callback = self.setPairValueCallback, callbackValue = -10)
		self.keyCommander.registerKeyCommand(KEY_LEFT, alt = True, callback = self.setPairValueCallback, callbackValue = -1)
		self.keyCommander.registerKeyCommand(KEY_LEFT, shift = True, callback = self.setPairValueCallback, callbackValue = -5)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, callback = self.setPairValueCallback, callbackValue = 10)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, alt = True, callback = self.setPairValueCallback, callbackValue = 1)
		self.keyCommander.registerKeyCommand(KEY_RIGHT, shift = True, callback = self.setPairValueCallback, callbackValue = 5)
		self.keyCommander.registerKeyCommand(KEY_E, callback = self.makeExceptionCallbak, callbackValue = 'side')
		self.keyCommander.registerKeyCommand(KEY_E, alt = True, callback = self.makeExceptionCallbak, callbackValue = 'both')

		self.keyCommander.registerSerialKeyCommands([KEY_1,KEY_2,KEY_3,KEY_4,KEY_5,KEY_6,KEY_7,KEY_8,KEY_9,KEY_0],
		                                            callback = self.setMultiplyLastValueCallback)

	def getScaledValue(self, font, value):
		if not self.scales or not value or value in range(-1,2):
			return value
		elif self.scales and font in self.scales and value:
			return round(value * self.scales[font])
		else:
			return value

	def deletePairCallback(self, sender, value):
		self.setCurrentPairValue(sender, operation = 'remove')

	def setPairValueCallback(self, sender, value):
		self.setCurrentPairValue(sender, value = value)

	def makeExceptionCallbak(self, sender, value):
		self.makeException(sender, exception = value)

	def setMultiplyLastValueCallback(self, sender, value):
		self.setCurrentPairValue(sender, value = None, multiply = int(value))


	def checkCommand(self, sender, event):
		if not self.ON: return
		if sender.statuses and 'mode:kerning' in sender.statuses and sender.statuses['mode:kerning'][0]:
			self.keyCommander.checkCommand(sender, event)


	def refreshViews(self):
		# print('kern control refreshing')
		self.glyphsView.refreshView(justmoveglyphs = True)
		if self.groupsView:
			self.groupsView.refreshView(justmoveglyphs = True)

	def setValue2Pair (self, font, pair, currentPairForKern, value=None, operation='value'):
		if operation == 'value':
			if not value and not pair['exception'] and currentPairForKern in font.kerning:
				font.kerning.remove(currentPairForKern)
			else:
				font.kerning[currentPairForKern] = value
		elif operation == 'remove':
			if currentPairForKern in font.kerning:
				font.kerning.remove(currentPairForKern)
		elif operation == 'exception':
			if not value:
				value = 0
			font.kerning[currentPairForKern] = value
		postEvent(EVENT_REFRESH_ALL_OBSERVERS, #  support for KernTool1-3
		          fontID = getFontID(font),
		          observerID = None, #self.observerID,
		          pair = currentPairForKern)

	def setKernToLinkedFont(self, font, pair, currentPairForKern, value = None, multiply=None, operation = 'value'):
		currentPair = pair
		if currentPairForKern and operation == 'value':
			if value:
				self.lastValue = value
				self.lastMultiply = []
			elif multiply != None:
				if multiply == 0:
					multiply = 10
				value = (self.lastValue * multiply) - self.lastValue  # simple way, one multiply
			value = self.getScaledValue(font, value)

			if currentPairForKern in font.kerning and kern(font.kerning[currentPairForKern]):  # != None:
				self.setValue2Pair(font, pair = currentPair, currentPairForKern = currentPairForKern,
				                   value = font.kerning[currentPairForKern] + value)
			else:
				self.setValue2Pair(font, pair = currentPair, currentPairForKern = currentPairForKern, value = value)
			if currentPairForKern in font.kerning and (font.kerning[currentPairForKern]) == 0 and (not currentPair['exception']):
				self.setValue2Pair(font, pair = currentPair, currentPairForKern = currentPairForKern,
				                   operation = 'remove')
		elif currentPairForKern and operation == 'remove':
			self.setValue2Pair(font, pair = currentPair, currentPairForKern = currentPairForKern, operation = 'remove')


	def setCurrentPairValue (self, sender, value = None, multiply=None, operation = 'value'):
		if not sender.selectedGlyphs or len(sender.selectedGlyphs) != 2: return
		l = cutUniqName(sender.selectedGlyphs[0])
		r = cutUniqName(sender.selectedGlyphs[1])

		if sender.linkedMode:
			lastfont = []
			for linkedlayer in sender.linkedGlyphLinesDic[sender.selectedLink]:
				font = sender.getCurrentFont( fromLayer = linkedlayer )
				if font not in lastfont:
					lastfont.append(font)
					currentPair = researchPair(font, self.fontsHashKernLib[font], (l,r))
					currentPairForKern = (currentPair['L_realName'], currentPair['R_realName'])
					self.setKernToLinkedFont(font, pair = currentPair, currentPairForKern = currentPairForKern,
					                         value = value, multiply = multiply, operation = operation)
		else:
			font = sender.getCurrentFont()
			currentPair = researchPair(font, self.fontsHashKernLib[font], (l,r))
			currentPairForKern = (currentPair['L_realName'], currentPair['R_realName'])
			self.setKernToLinkedFont(font, pair = currentPair, currentPairForKern = currentPairForKern,
			                         value = value, multiply = multiply, operation = operation)
			# if font != CurrentFont():
		self.refreshViews()

	def makeException(self, sender, exception = 'side'):
		if sender == self.groupsView:
			font = sender.getCurrentFont()
			l = cutUniqName(sender.selectedGlyphs[0])
			r = cutUniqName(sender.selectedGlyphs[1])
			currentPair = researchPair(font, self.fontsHashKernLib[font], (l, r))
			kernValue = currentPair['kernValue']
			if not kernValue:
				kernValue = 0

			if exception == 'both':
				# print ('making exception to both sides')
				self.setValue2Pair( font, currentPair, (l,r), kernValue, operation = 'exception')

			if exception == 'side':
				# print ('making exception to', sender.selectedLink)
				if sender.selectedLink == 'left':
					self.setValue2Pair( font, currentPair, (l, currentPair['R_realName'] ), kernValue, operation = 'exception')
				elif sender.selectedLink == 'right':
					self.setValue2Pair( font, currentPair, (currentPair['L_realName'], r ), kernValue, operation = 'exception')
			self.refreshViews()


class TDMarginsControl(object):
	def __init__ (self, fontsHashKernLib, glyphsView, groupsView = None, ON = False, scales = None):
		self.lastValue = 0
		self.lastMultiply = []
		self.lastSide = SIDE_1
		self.fontsHashKernLib = fontsHashKernLib
		self.scales = scales
		self.glyphsView = glyphsView
		self.groupsView = groupsView
		self.ON = ON
		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_LEFT, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_2, value = -1))
		self.keyCommander.registerKeyCommand(KEY_LEFT, alt = True, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_1, value = -1))
		self.keyCommander.registerKeyCommand(KEY_LEFT, shift = True, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_2, value = -10))
		self.keyCommander.registerKeyCommand(KEY_LEFT, alt = True, shift = True, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_1, value= -10))

		self.keyCommander.registerKeyCommand(KEY_RIGHT, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_2, value = 1))
		self.keyCommander.registerKeyCommand(KEY_RIGHT, alt = True, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_1, value = 1))
		self.keyCommander.registerKeyCommand(KEY_RIGHT, shift = True, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_2, value = 10))
		self.keyCommander.registerKeyCommand(KEY_RIGHT, alt = True, shift = True, callback = self.setGlyphMarginsCallback,
		                                     callbackValue = dict(side = SIDE_1, value= 10))

		self.keyCommander.registerSerialKeyCommands([KEY_1,KEY_2,KEY_3,KEY_4,KEY_5,KEY_6,KEY_7,KEY_8,KEY_9,KEY_0],
		                                            callback = self.setMultiplyLastValueCallback)


	def setGlyphMarginsCallback(self, sender, value):
		self.setCurrentGlyphMargins(sender, side = value['side'], value = value['value'])
	def setMultiplyLastValueCallback(self, sender, value):
		self.setCurrentGlyphMargins(sender, side = self.lastSide, value = None, multiply = int(value))

	def checkCommand(self, sender, event):
		if not self.ON: return
		if sender.statuses and 'mode:margins' in sender.statuses and sender.statuses['mode:margins'][0]:
			self.keyCommander.checkCommand(sender, event)

	def refreshViews(self):
		# print('margins control refreshing')
		self.glyphsView.refreshView(justmoveglyphs = True)
		if self.groupsView:
			self.groupsView.refreshView(justmoveglyphs = True)

	def setCurrentGlyphMargins(self, sender, side = SIDE_1, value = None, multiply=None, operation = 'value'):
		self.lastSide = side
		if value:
			self.lastValue = value
			self.lastMultiply = []
		elif multiply != None:
			if multiply == 0:
				multiply = 10
			value = (self.lastValue * multiply) - self.lastValue

		delta = value
		if not sender.selectedGlyphs: return
		glyphname = cutUniqName(sender.selectedGlyphs[0])
		font = sender.getCurrentFont()

		if side == SIDE_1:
			if font[glyphname].leftMargin != None:
				font[glyphname].leftMargin += delta
			else: # for /space and empty glyphs etc.
				font[glyphname].width += delta
				self.refreshViews()
				return
		if side == SIDE_2:
			if font[glyphname].rightMargin != None:
				font[glyphname].rightMargin += delta
			else: # for /space and empty glyphs etc.
				font[glyphname].width += delta
				self.refreshViews()
				return
			
		# apply changes to all composites	
		mapGlyphs = sender.getCurrentFont().getReverseComponentMapping()
		if glyphname in mapGlyphs:
			for compglyphname in mapGlyphs[glyphname]:
				if side == SIDE_1:
					compglyph = font[compglyphname]
					compglyph.changed()
					if len(compglyph.components) > 1:
						for component in compglyph.components:
							component.moveBy((delta, 0))
						compglyph.components[0].moveBy((-delta, 0))
					elif len(compglyph.components) == 1:
						compglyph.components[0].moveBy((-delta, 0))

						baseglyph = compglyph.components[0]
						offset_x, offset_y = compglyph.components[0].offset
						if offset_x != 0:
							compglyph.moveBy((-offset_x, 0))
							compglyph.changed()

					compglyph.width += delta  # = font[glyphname].width
				if side == SIDE_2:
					compglyph = font[compglyphname]
					compglyph.rightMargin += delta  # =font[glyphname].rightMargin#
					
		self.refreshViews()
