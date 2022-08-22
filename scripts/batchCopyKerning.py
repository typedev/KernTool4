import os, sys, glob
from fontParts.world import *
import vanilla
from vanilla.dialogs import getFolder
from mojo.UI import *
from pygments.lexer import RegexLexer, bygroups

from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles

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
	report = []
	report.append('* Saving Pattern to file:')
	fn = filename
	report.append(fn)
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
	return report

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
		pattern = host.langSet.wrapPairToPattern(font, (l, r))
		patterns.append(pattern)
	return patterns

def filterKernGroups(font):
	resultGroups = {}
	for groupname, content in font.groups.items():
		if 'public.kern' in groupname:
			resultGroups[groupname] = content
	return resultGroups


def diffGlyphsTable(sourcefont, newfont):
	result = []

	for glyphname in newfont.glyphOrder:
		if glyphname not in sourcefont:
			result.append(glyphname)



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
	        (r'(content:)(.*)\n', bygroups(Keyword, Text)),
	        (r'\+.*\n', Generic.Emph),
	        (r'-.*\n', Error),
            (r'@.*\n', Generic.Subheading),
            (r'\*.*\n', Comment),
            (r'=.*\n', Keyword),
	        (r'\t.*', Generic.Emph),
            (r'.*\n', Text),
        ],
    }

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
		self.w.btnRun = vanilla.Button('auto', title = 'Run', callback = self.btnRunCallback)  # ,
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
			"V:|-border-[label1]-space-[fontA]-border-[label2]-border-[fontB]-border-[fontFolder]-border-[fontsList(==200)]-border-[bar]-border-[btnRun]-[textBox]-0-|",
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
		globalreport = []
		for targetfont in self.targetFontList:
			report = diffGroups(fontB, targetfont, ignoreOrder = True)
			globalreport.extend(report)
		globalreport.append('\n')
		self.w.textBox.set('\n'.join(globalreport))

		# checkPatternsLib(host = self.parent.hashKernDic, fonts = [fontA, fontB])
		# report = transferKern(host = self.parent.hashKernDic, masterfont = fontA, targetfont = fontB, applyTransfer = self.w.applyTransfer.get())
		# self.w.textBox.set('\n'.join(report))

	def fontFolderCallback (self, sender):
		result = getFolder('Choose Target Folder with UFO files')

		if result:
			self.w.fontsList.set([])
			items = []
			txt = ''
			paths = getFontFilesList(result[0])
			inc = int(round(100/len(paths),0))
			self.w.bar.set(0)
			for fontpath in paths:
				font = OpenFont(fontpath, showInterface = False)
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
				self.w.bar.increment(inc)
				# inc += inc

			self.w.fontsList.set(items)
			# print (getFontFilesList(result[0]))
		report = []
		for f in self.targetFontList:
			report.append('+ %s %s' % (f.info.familyName, f.info.styleName))
		report.append('\n')
		self.w.textBox.set('\n'.join(report))


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
