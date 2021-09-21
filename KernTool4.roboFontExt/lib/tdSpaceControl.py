import importlib
import vanilla.dialogs
from merz import *
from fontParts import *
from mojo.tools import IntersectGlyphWithLine
# from mojo.subscriber import Subscriber, WindowController, registerCurrentGlyphSubscriber, registerRoboFontSubscriber, registerCurrentFontSubscriber
# from merz.tools.drawingTools import NSImageDrawingTools

import tdKernToolEssentials4
importlib.reload(tdKernToolEssentials4)
from tdKernToolEssentials4 import *

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
		# self.history = []
		self.makeReverseGroupsMapping()

	def clearHistory(self):
		self.history = []

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
			if self.isKerningGroup(groupname):
				if self.isLeftSideGroup(groupname):
					for glyphname in content:
						# self.leftDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.leftDic, glyphname, groupname)
				else:
					for glyphname in content:
						# self.rightDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.rightDic, glyphname, groupname)
			elif self.isMarginsGroup(groupname):
				if self.isLeftSideGroup(groupname):
					for glyphname in content:
						# self.leftMarginsDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.leftMarginsDic, glyphname, groupname)

				else:
					for glyphname in content:
						# self.rightMarginsDic[glyphname] = groupname
						self.checkMapAndAddGlyph2hashMap(self.rightMarginsDic, glyphname, groupname)


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

	def addGlyphsToGroup (self, group, glyphlist, checkKerning=True, showAlert = False):
		"""
		function for adding glyphs to a group, if the group does not exist, it will be created
		if the glyph is already in a group of the same class, the operation will be canceled
		if checkKerning = True, existing kerning with this group will be checked:
			if the glyph already has kerning identical to the group, it will be classified as an exception and removed.
			if kerning is different, such an exception will be saved
		"""
		report = []
		self.history.append(('+', group, glyphlist, checkKerning))
		def msgCanceled(self, glyphname, side, mode, showAlert):
			txt = 'Glyph %s is already in the group %s, the addition is canceled' % (glyphname, self.getGroupNameByGlyph(glyphname, side, mode))
			if showAlert:
				vanilla.dialogs.message(messageText = 'Operation canceled', informativeText = txt, alertStyle = 'critical')
			else:
				return txt


		def checkingPresenceInGroups(self, group, glyphname, side, mode, showAlert, report):

			if self.thisGlyphInGroup(glyphname, SIDE_1, mode) and side == SIDE_1:
				r = msgCanceled(self, glyphname, SIDE_1, mode, showAlert )
				report.append((r))
				return False
			elif self.thisGlyphInGroup(glyphname, SIDE_2, mode) and side == SIDE_2:
				r = msgCanceled(self, glyphname, SIDE_2, mode, showAlert)
				report.append((r))
				return False
			else:
				if glyphname not in self.font.groups[group]:
					return True
			return False

		newGroup = False
		newcontent = []
		if group not in self.font.groups:
			self.font.groups[group] = ()
			newGroup = True

		if self.isLeftSideGroup(group):
			side = SIDE_1
		else:
			side = SIDE_2

		for glyphname in glyphlist:
			if self.isKerningGroup(group):
				if checkingPresenceInGroups(self, group, glyphname, side, EDITMODE_KERNING, showAlert, report):
					newcontent.append(glyphname)
					if checkKerning:
						if side == SIDE_1:
							pairsGlyph = self.getPairsBy(glyphname, side)
							if not newGroup:
								pairsTarget = self.getPairsBy(group, side)
								for (l, r), v in pairsGlyph:
									for (_l, _r), _v in pairsTarget:
										if r == _r and v == _v:
											report.append(('added and cleared', l,r,v, '=', _l,_r,_v ))
											self.font.kerning.remove((l, r))
										elif r == _r and v != _v:
											report.append(('added and saved as exception', l,r,v, '!=', _l,_r,_v ))
							else:
								for (l, r), v in pairsGlyph:
									report.append (('copyed from', l,r,v, 'to', group,r))
									self.font.kerning[(group,r)] = self.font.kerning[(l,r)]
									report.append (('removed as exception', l,r))
									self.font.kerning.remove((l, r))
									newGroup = False

						if side == SIDE_2:
							pairsGlyph = self.getPairsBy(glyphname, side)
							if not newGroup:
								pairsTarget = self.getPairsBy(group, side)
								for (l, r), v in pairsGlyph:
									for (_l, _r), _v in pairsTarget:
										if l == _l and v == _v:
											report.append(('added and cleared', l,r,v, '=', _l,_r,_v ))
											self.font.kerning.remove((l,r))
										elif l == _l and v != _v:
											report.append(('added and saved as exception', l,r,v, '!=', _l,_r,_v ))
							else:
								for (l, r), v in pairsGlyph:
									report.append(('copyed from', l,r,v, 'to', l,group))
									self.font.kerning[(l,group)] = self.font.kerning[(l,r)]
									report.append(('removed as exception', l, r))
									self.font.kerning.remove((l, r))
									newGroup = False

			if self.isMarginsGroup(group):
				if checkingPresenceInGroups(self, group, glyphname, side, EDITMODE_MARGINS, showAlert, report):
					newcontent.append(glyphname)

		if newcontent:
			self.font.groups[group] += tuple(newcontent)
			self.makeReverseGroupsMapping()
		if report:
			for i in report:
				print (' '.join([ str(n) for n in i]))


	def delGlyphsFromGroup (self, group, glyphlist, checkKerning=True, rebuildMap = True):
		"""
		function to remove glyphs from a group
		if kerning check mode is enabled, existing kerning with this group will be checked:
			if a group has a kerning with a glyph or other group, this kerning will be copied to the glyph being removed,
			this will be classified as an exception
		"""
		report = []
		self.history.append(('-', group, glyphlist, checkKerning))
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
							self.font.kerning[(glyph, r)] = self.font.kerning[(l, r)]
							report.append (('removed from group and saved as exception', glyph,r,v, '=', l,r,v))
						if glyphpairs:
							for (l, r), v in glyphpairs:
								self.font.kerning[(glyph, r)] = self.font.kerning[(l, r)]
								report.append (('removed from group and saved as exception', glyph, r, v, '=', l, r, v))
				if side == SIDE_2:
					pairs = self.getPairsBy(group, side)
					for glyph in glyphlist:
						glyphpairs = self.getPairsBy(glyph, side)

						for (l,r),v in pairs:
							self.font.kerning[(l, glyph)] = self.font.kerning[(l, r)]
							report.append (('removed from group and saved as exception', l, glyph,v, '=', l,r,v))
						if glyphpairs:
							for (l, r), v in glyphpairs:
								self.font.kerning[(l, glyph)] = self.font.kerning[(l, r)]
								report.append (('removed from group and saved as exception', l, glyph, v, '=', l, r, v))

			self.font.groups[group] = tuple(newcontent)
			if rebuildMap:
				self.makeReverseGroupsMapping()
		if report:
			for i in report:
				print(' '.join([ str(n) for n in i]))

	def deleteGroup(self, group, checkKerning = True):
		report = []

		self.history.append(('del', group, checkKerning))
		if group in self.font.groups:
			glyphslist = self.font.groups[group]
			self.delGlyphsFromGroup(group, glyphslist, checkKerning = checkKerning, rebuildMap = False)
			report.append (('group removed', group))
			if self.isKerningGroup(group):
				report.append ( ('clearing kerning'))
				if self.isLeftSideGroup(group):
					side = SIDE_1
				else:
					side = SIDE_2
				if side == SIDE_1:
					pairs = self.getPairsBy(group, SIDE_1)
					for (l,r),v in pairs:
						report.append ( ('removed', l,r,v))
						self.font.kerning.remove((l,r))
				if side == SIDE_2:
					pairs = self.getPairsBy(group, SIDE_2)
					for (l,r),v in pairs:
						report.append (('removed', l, r, v))
						self.font.kerning.remove((l,r))

			del self.font.groups[group]
			self.makeReverseGroupsMapping()
		if report:
			for i in report:
				print(' '.join([ str(n) for n in i]))


	def checkPairLanguageCompatibility(self, pair):
		if self.langSet:
			return self.langSet.checkPairLanguageCompatibility(self.font, pair)



class TDSpaceControl(object):
	def __init__(self, fontsHashKernLib, glyphsView, groupsView = None, mode = EDITMODE_OFF, OFFispossible = False):
		self.lastValue = 0
		self.lastMultiply = []
		self.fontsHashKernLib = fontsHashKernLib
		self.glyphsView = glyphsView
		self.groupsView = groupsView
		self.editMode = mode
		self.kerningON = False
		self.marginsON = False
		self.kernControl = TDKernControl(fontsHashKernLib, glyphsView, groupsView, ON = True)
		self.marginsControl = TDMarginsControl(fontsHashKernLib, glyphsView, groupsView, ON = False)

		self.keyCommander = TDKeyCommander()
		self.keyCommander.registerKeyCommand(KEY_M, callback = self.switchModeCallback)

	def setupSpaceControl(self):
		pass

	def switchKerningON(self):
		self.kernControl.ON = True
		self.marginsControl.ON = False
		self.editMode = EDITMODE_KERNING

		self.glyphsView.selectionMode = SELECTION_MODE_PAIR
		self.glyphsView.setStatus('mode:kerning', True)
		self.glyphsView.setStatus('mode:margins', False)
		self.glyphsView.showMargins = False

		if self.groupsView:
			self.groupsView.setStatus('mode:margins', False)
			self.groupsView.setStatus('mode:kerning', True)
			self.groupsView.setStatus('mode:exceptions', True)
			self.groupsView.setStatus('show:beam', False)
			self.groupsView.selectionMode = SELECTION_MODE_PAIR
			self.groupsView.showMargins = False
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
	def __init__ (self, fontsHashKernLib, glyphsView, groupsView = None, ON = False):
		self.lastValue = 0
		self.lastMultiply = []
		self.fontsHashKernLib = fontsHashKernLib
		self.glyphsView = glyphsView
		self.groupsView = groupsView
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
		if 'mode:kerning' in sender.statuses and sender.statuses['mode:kerning'][0]:
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
	def __init__ (self, fontsHashKernLib, glyphsView, groupsView = None, ON = False):
		self.lastValue = 0
		self.lastMultiply = []
		self.lastSide = SIDE_1
		self.fontsHashKernLib = fontsHashKernLib
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
		if 'mode:margins' in sender.statuses and sender.statuses['mode:margins'][0]:
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
