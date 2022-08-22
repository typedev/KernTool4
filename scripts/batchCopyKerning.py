import os, sys, glob
from fontParts.world import *
import vanilla
from vanilla.dialogs import getFolder
from mojo.UI import *
from pygments.lexer import RegexLexer, bygroups

from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles



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

def getFontFilesList (fontsFolder):
	filepath = os.path.join(fontsFolder, '*.ufo')

	listoffilepaths = glob.glob(filepath)
	listoffilenames = []
	for filename in listoffilepaths:
		# listoffilenames.append(os.path.basename(filename))
		# print filename
		listoffilenames.append(filename) # .split('/')[-1]
	return listoffilenames


def contentEqual (g1, g2):
	a = ''.join(g1)
	b = ''.join(g2)
	if a != b:
		return False
	else:
		return True


def diffOrderOnly (g1, g2):
	a = ''.join(sorted(g1))
	b = ''.join(sorted(g2))
	if a != b:
		return False
	else:
		return True


def saveKernPattern(patternlist, filename, pattern2line = 8):
	# report = []
	# report.append('* Saving Pattern to file:')
	fn = filename
	# report.append(fn)
	groupsfile = open(fn, mode = 'w')
	txt = ''
	p2l = 0
	for pattern in patternlist:
		s1, lp, rp, s2 = pattern
		txt += '/%s/%s/%s/%s' % (s1, lp, rp, s2)
		p2l += 1
		if p2l == pattern2line:
			txt += '\n'
			p2l = 0
	groupsfile.write(txt)
	groupsfile.close()
	# report.append('= Done.')
	# return report

def makePatternsFromPairsList(host, font, pairslist):
	patterns = []
	pairs = []
	for pair in pairslist.keys():
		l, r = pair
		lg = host.getKeyGlyphByGroupname(l)
		rg = host.getKeyGlyphByGroupname(r)
		pairs.append((lg,rg))
	for pair in sorted(pairs):
		l, r = pair
		pattern = ('space', l, r, 'space')
		patterns.append(pattern)
	return patterns

def filterKernGroups(font):
	resultGroups = {}
	for groupname, content in font.groups.items():
		if 'public.kern' in groupname:
			resultGroups[groupname] = content
	return resultGroups


def diffGlyphsTable(sourcefont, newfont):
	glyphslist = []

	for glyphname in newfont.glyphOrder:
		if glyphname not in sourcefont:
			glyphslist.append(glyphname)
	return glyphslist


def diffGroups (masterfont, targetfont, ignoreOrder = True):
	groupsNotInTarget = {}
	groupsNotInMaster = {}
	groupsDiff = {}
	groupsDiffOrder = {}

	report = []
	masterGroups = filterKernGroups(masterfont)
	targetGroups = filterKernGroups(targetfont)

	for groupname, content in masterGroups.items():
		if groupname not in targetGroups:
			groupsNotInTarget[groupname] = content
		elif not contentEqual(targetGroups[groupname], masterGroups[groupname]):
			if diffOrderOnly(targetGroups[groupname], masterGroups[groupname]):
				groupsDiffOrder[groupname] = (targetGroups[groupname], masterGroups[groupname])
			else:
				groupsDiff[groupname] = (targetGroups[groupname], masterGroups[groupname])

	for groupname, content in targetGroups.items():
		if groupname not in masterGroups:
			groupsNotInMaster[groupname] = content

	report.append('=' * 40)
	report.append('Groups differences report')
	report.append('+ master: %s %s' % (masterfont.info.familyName, masterfont.info.styleName))
	report.append('+ groups: %i' % len(masterGroups))
	report.append('- target: %s %s' % (targetfont.info.familyName, targetfont.info.styleName))
	report.append('- groups: %i' % len(targetGroups))
	if groupsNotInTarget:
		report.append('*' * 40)
		report.append('Groups not founded in Target font:')
		report.append('= total: %i' % len(groupsNotInTarget))
		for g, c in groupsNotInTarget.items():
			report.append('@ %s' % g)
	if groupsNotInMaster:
		report.append('*' * 40)
		report.append('Groups not founded in Master font:')
		report.append('= total: %i' % len(groupsNotInMaster))
		for g, c in groupsNotInMaster.items():
			report.append('@ %s' % g)
	if groupsDiff:
		report.append('*' * 40)
		report.append('Groups with differences in composition:')
		report.append('= total: %i' % len(groupsDiff))
		for g, (c1, c2) in groupsDiff.items():
			report.append('@ %s' % g)
			report.append('+ master (%i): %s' % (len(c2), ' '.join(c2)))
			report.append('- target (%i): %s' % (len(c1), ' '.join(c1)))
	if groupsDiffOrder and not ignoreOrder:
		report.append('*' * 40)
		report.append('Groups identical but differing in glyph order:')
		report.append('= total: %i' % len(groupsDiffOrder))
		for g, (c1, c2) in groupsDiffOrder.items():
			report.append('@ %s' % g)
			report.append('+ master (%i): %s' % (len(c2), ' '.join(c2)))
			report.append('- target (%i): %s' % (len(c1), ' '.join(c1)))

	report.append('\n')
	return report

class BaseLexerCKBL(RegexLexer):
	tokens = {
        'root': [
            (r' .*\n', Name),
            # (r'(before:.*)(".*")(.*)\n', bygroups(Error, Text, Error)),
	        # (r'(after:.*)(".*")(.*)\n', bygroups(String, Text, String)),
	        # (r'(content:)(.*)(".*")(.*)\n', bygroups(Keyword, String, Text, String)),
	        (r'not found:.*\n', Error),
	        (r'(new glyphs:)(.*)\n', bygroups(Keyword, Text)),
	        (r'\+.*\n', Generic.Emph),
	        (r'-.*\n', Error),
            (r'@.*\n', Generic.Subheading),
            (r'\*.*\n', Comment),
            (r'=.*\n', Keyword),
	        (r'\t.*', Generic.Emph),
            (r'.*\n', Text),
        ],
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
		self.trackHistory = True
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


class TDCopyKernWindow(object):
	def __init__ (self, ):
		_version = '0.2'
		self.fontNames = []
		self.targetFontList = []
		self.w = vanilla.FloatingWindow((500, 800), minSize = (300, 300), title = 'Copy Kerning by NEW Glyphs v%s' % _version)
		self.w.label1 = vanilla.TextBox('auto', 'Choose Latin Source font:')
		self.w.fontA = vanilla.PopUpButton('auto', [], sizeStyle = "regular")
		self.w.label2 = vanilla.TextBox('auto', 'Choose Cyrillic Source font:')
		self.w.fontB = vanilla.PopUpButton('auto', [], sizeStyle = "regular") # , callback = self.optionsChanged
		self.w.fontFolder = vanilla.Button('auto', 'Choose Target Folder with UFO files', sizeStyle = "regular", callback = self.fontFolderCallback)  # , callback = self.optionsChanged
		self.w.fontsList = vanilla.List('auto', [],
		                                allowsMultipleSelection = False,
		                                columnDescriptions=[{"title": "UFO", },
		                                                    {"title": "Family", 'width': 150},
		                                                    {'title': 'Style', 'width': 150},
		                                                    ],
		                                )
		self.w.bar = vanilla.ProgressBar('auto')
		self.w.btnRun = vanilla.Button('auto', title = 'Start Copy kerning', callback = self.btnRunCallback)  # ,
		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False)
		self.w.textBox.setLexer(BaseLexerCKBL())
		self.w.textBox.setHighlightStyle(get_style_by_name('material'))

		rules = [
			# Horizontal
			"H:|-border-[label1]-border-|",
			"H:|-border-[fontA]-border-|",
			"H:|-border-[label2]-border-|",
			"H:|-border-[fontB]-border-|",
			"H:|-border-[fontFolder]-border-|",
			"H:|-border-[fontsList]-border-|",
			"H:|-border-[bar]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			"V:|-border-[label1]-space-[fontA]-border-[label2]-space-[fontB]-border-[fontFolder]-space-[fontsList(==150)]-space-[bar]-space-[btnRun]-[textBox]-0-|",
		]
		metrics = {
			"border": 15,
			"space": 8
		}
		self.w.addAutoPosSizeRules(rules, metrics)
		self.collectFonts()
		self.w.open()

	def btnRunCallback (self, sender):
		fontA = self.fonts[self.w.fontA.get()]
		fontB = self.fonts[self.w.fontB.get()]
		hashKernDic = TDHashGroupsDic(fontB)
		globalreport = []
		glyphslist = diffGlyphsTable(fontA, fontB)
		# # for glyphname in glyphslist:
		globalreport.append('new glyphs: %s' % ' '.join(glyphslist))
		self.w.bar.set(0)
		inc = int(round(100 / len(self.targetFontList), 0))
		for targetfont in self.targetFontList:

			report = diffGroups(fontB, targetfont, ignoreOrder = True)
			globalreport.extend(report)
			pairs2copy = {}
			for glyphname in glyphslist:
				lpairs = hashKernDic.getPairsBy(glyphname, SIDE_1)
				rpairs = hashKernDic.getPairsBy(glyphname, SIDE_2)
				lg = hashKernDic.getGroupNameByGlyph(glyphname, SIDE_1)
				rg = hashKernDic.getGroupNameByGlyph(glyphname, SIDE_2)
				if lg != glyphname:
					lpairs.extend(hashKernDic.getPairsBy(lg,SIDE_1))
				if rg != glyphname:
					rpairs.extend(hashKernDic.getPairsBy(rg,SIDE_2))
				# globalreport.append('%s' % glyphname)
				# globalreport.append('\tside1:')
				for (l, r), v in lpairs:
					if (l,r) not in targetfont.kerning and (l,r) not in fontA.kerning:
						pairs2copy[(l,r)] = v
						targetfont.kerning[(l,r)] = v
				for (l, r), v in rpairs:
					if (l, r) not in targetfont.kerning and (l, r) not in fontA.kerning:
						pairs2copy[(l, r)] = v
						targetfont.kerning[(l, r)] = v


			globalreport.append('= total copied pairs: %i' % len(pairs2copy))
			workPath = os.path.join(targetfont.path.replace(os.path.basename(targetfont.path), ''))

			fpattern = os.path.join(workPath, 'Patterns to check - %s.txt' % (os.path.basename(targetfont.path.replace('.ufo',''))))
			globalreport.append('* Patterns saved to file: \n%s' % fpattern)
			patterns = makePatternsFromPairsList(hashKernDic, targetfont, pairs2copy)
			saveKernPattern(patterns, fpattern)
			targetfont.save()
			self.w.bar.set(inc)
			inc += inc
		globalreport.append('\n')

		self.w.textBox.set('\n'.join(globalreport))
		for targetfont in self.targetFontList:
			targetfont.close()



	def fontFolderCallback (self, sender):
		result = getFolder('Choose Target Folder with UFO files')

		if result:
			self.w.fontsList.set([])
			fontA = self.fonts[self.w.fontA.get()]
			fontB = self.fonts[self.w.fontB.get()]
			items = []
			txt = ''
			paths = getFontFilesList(result[0])
			inc = int(round(100/len(paths),0))
			self.w.bar.set(0)
			for fontpath in paths:
				font = OpenFont(fontpath, showInterface = False)
				if font != fontA and font != fontB:
					self.targetFontList.append(font)
					ufo = os.path.basename(fontpath)
					family = font.info.familyName
					style = font.info.styleName
					item = dict(
						UFO = ufo,
						Family = family,
						Style = style
					)
					items.append(item)
				self.w.bar.set(inc)
				inc += inc
			self.w.bar.set(100)
			self.w.fontsList.set(items)
			# print (getFontFilesList(result[0]))
		# report = []
		# for f in self.targetFontList:
		# 	report.append('+ %s %s' % (f.info.familyName, f.info.styleName))
		# report.append('\n')
		# self.w.textBox.set('\n'.join(report))


#
	def getFontName (self, font, fonts):
		# by Andy Clymer, June 2018
		# A helper to get the font name, starting with the preferred name and working back to the PostScript name
		# Make sure that it's not the same name as another font in the fonts list
		ufofile = os.path.basename(font.path)
		if font.info.openTypeNamePreferredFamilyName and font.info.openTypeNamePreferredSubfamilyName:
			name = "%s %s" % (font.info.openTypeNamePreferredFamilyName, font.info.openTypeNamePreferredSubfamilyName)
		elif font.info.familyName and font.info.styleName:
			name = "%s %s" % (font.info.familyName, font.info.styleName)
		elif font.info.fullName:
			name = font.info.fullName
		elif font.info.fullName:
			name = font.info.postscriptFontName
		else: name = "Untitled"
		# Add a number to the name if this name already exists
		if name in fonts:
			i = 2
			while name + " (%s)-(%s)" % (ufofile, i) in fonts:
				i += 1
			name = name + " (%s)-(%s)" % (ufofile, i)
		return name

	def collectFonts (self):
		# by Andy Clymer, June 2018
		# Hold aside the current font choices
		font0idx = self.w.fontA.get()
		font1idx = self.w.fontB.get()
		if not font0idx == -1:
			font0name = self.fontNames[font0idx]
		else: font0name = None
		if not font1idx == -1:
			font1name = self.fontNames[font1idx]
		else: font1name = None
		# Collect info on all open fonts
		self.fonts = AllFonts()
		self.fontNames = []
		for font in self.fonts:
			self.fontNames.append(self.getFontName(font, self.fontNames))
		# Update the popUpButtons
		self.w.fontA.setItems(self.fontNames)
		self.w.fontB.setItems(self.fontNames)
		# If there weren't any previous names, try to set the first and second items in the list
		if font0name == None:
			if len(self.fonts):
				self.w.fontA.set(0)
		if font1name == None:
			if len(self.fonts) >= 1:
				self.w.fontB.set(1)
		# Otherwise, if there had already been fonts choosen before new fonts were loaded,
		# try to set the index of the fonts that were already selected
		if font0name in self.fontNames:
			self.w.fontA.set(self.fontNames.index(font0name))
		if font1name in self.fontNames:
			self.w.fontB.set(self.fontNames.index(font1name))


def main ():
	TDCopyKernWindow()


if __name__ == "__main__":
	main()
