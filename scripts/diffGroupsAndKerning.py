import os, sys
from fontParts.world import *
import vanilla
from mojo.UI import *
from pygments.lexer import RegexLexer, bygroups

from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles


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

def diffGroups (masterfont, targetfont):
	groupsNotInTarget = {}
	groupsNotInMaster = {}
	groupsDiff = {}
	groupsDiffOrder = {}

	report = []

	for groupname, content in masterfont.groups.items():
		if groupname not in targetfont.groups:
			groupsNotInTarget[groupname] = content
		elif not contentEqual(targetfont.groups[groupname], masterfont.groups[groupname]):
			if diffOrderOnly(targetfont.groups[groupname], masterfont.groups[groupname]):
				groupsDiffOrder[groupname] = (targetfont.groups[groupname], masterfont.groups[groupname])
			else:
				groupsDiff[groupname] = (targetfont.groups[groupname], masterfont.groups[groupname])

	for groupname, content in targetfont.groups.items():
		if groupname not in masterfont.groups:
			groupsNotInMaster[groupname] = content

	report.append('=' * 40)
	report.append('Groups differences report')
	report.append('+ master: %s %s' % (masterfont.info.familyName, masterfont.info.styleName))
	report.append('+ groups: %i' % len(masterfont.groups))
	report.append('- target: %s %s' % (targetfont.info.familyName, targetfont.info.styleName))
	report.append('- groups: %i' % len(targetfont.groups))
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
			missing = ' '.join(list(set(c1) - set(c2)))
			if missing:
				report.append('= missing: %s' % missing)
			report.append('- target (%i): %s' % (len(c1), ' '.join(c1)))
			missing = ' '.join(list(set(c2) - set(c1)))
			if missing:
				report.append('= missing: %s' % missing)
	if groupsDiffOrder:
		report.append('*' * 40)
		report.append('Groups identical but differing in glyph order:')
		report.append('= total: %i' % len(groupsDiffOrder))
		for g, (c1, c2) in groupsDiffOrder.items():
			report.append('@ %s' % g)
			report.append('+ master (%i): %s' % (len(c2), ' '.join(c2)))
			report.append('- target (%i): %s' % (len(c1), ' '.join(c1)))

	report.append('\n')
	return report


def diffKerning (masterfont, targetfont, host = None):
	pairsNotInTarget = {}
	pairsNotInMaster = {}
	pairsDiff = {}
	pairsEqual = {}
	report = []

	for (l, r), v in masterfont.kerning.items():
		if (l, r) not in targetfont.kerning:
			pairsNotInTarget[l, r] = v
		elif masterfont.kerning[l, r] != targetfont.kerning[l, r]:
			pairsDiff[l, r] = (masterfont.kerning[l, r], targetfont.kerning[l, r])
		elif masterfont.kerning[l, r] == targetfont.kerning[l, r]:
			pairsEqual[l, r] = (masterfont.kerning[l, r], targetfont.kerning[l, r])

	for (l, r), v in targetfont.kerning.items():
		if (l, r) not in masterfont.kerning:
			pairsNotInMaster[l, r] = v

	report.append('=' * 40)
	report.append('Kerning differences report:')
	report.append('+ master: %s %s' % (masterfont.info.familyName, masterfont.info.styleName))
	report.append('+ pairs: %i' % len(masterfont.kerning))
	report.append('- target: %s %s' % (targetfont.info.familyName, targetfont.info.styleName))
	report.append('- pairs: %i' % len(targetfont.kerning))
	report.append('=' * 40)
	report.append('+ Not In Master=%i \n- Not In Target=%i \n@ Diff=%i \n= Equal=%i' % (len(pairsNotInMaster),
	                                                                                    len(pairsNotInTarget),
	                                                                                    len(pairsDiff),
	                                                                                    len(pairsEqual)))
	workPath = os.path.join(masterfont.path.replace(os.path.basename(masterfont.path),''))
	if pairsNotInTarget:
		fpattern = os.path.join(workPath, 'Not In Target Patterns - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		patterns = makePatternsFromPairsList(host, masterfont, pairsNotInTarget)
		report.extend(saveKernPattern(patterns, fpattern))
	if pairsNotInMaster:
		fpattern = os.path.join(workPath, 'Not In Master Patterns - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		patterns = makePatternsFromPairsList(host, masterfont, pairsNotInMaster)
		report.extend(saveKernPattern(patterns, fpattern))
	if pairsDiff:
		fpattern = os.path.join(workPath, 'Diff Pairs Patterns - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		patterns = makePatternsFromPairsList(host, masterfont, pairsDiff)
		report.extend(saveKernPattern(patterns, fpattern))
	if pairsEqual:
		fpattern = os.path.join(workPath, 'Equal Pairs Patterns - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		patterns = makePatternsFromPairsList(host, masterfont, pairsEqual)
		report.extend(saveKernPattern(patterns, fpattern))

	report.append('\n')
	return report


class BaseLexerDGAKW(RegexLexer):
	tokens = {
		'root': [
			(r' .*\n', Name),
			# (r'(before:.*)(".*")(.*)\n', bygroups(Error, Text, Error)),
			# (r'(after:.*)(".*")(.*)\n', bygroups(String, Text, String)),
			# (r'(content:)(.*)(".*")(.*)\n', bygroups(Keyword, String, Text, String)),
			(r'not found:.*\n', Error),
			(r'(content:)(.*)\n', bygroups(Keyword, Text)),
			(r'\+.*\n', Name.Builtin),
			(r'-.*\n', Error),
			(r'@.*\n', Generic.Subheading),
			(r'\*.*\n', Comment),
			(r'=.*\n', Keyword),
			(r'\t.*', Generic.Emph),
			(r'&.*\n', Generic.Emph),
			(r'.*\n', Text),
		],
	}


class TDDiffGroupsAndKerningWindow(object):
	def __init__ (self, parent=None):
		_version = '0.4'
		self.parent = parent
		self.fontNames = []

		self.w = vanilla.FloatingWindow((500, 600), minSize = (300, 300), title = 'Differences Groups and Kerning v%s' % _version)
		self.w.label1 = vanilla.TextBox('auto', 'Choose Master font:')
		self.w.fontA = vanilla.PopUpButton('auto', [], sizeStyle = "regular")
		self.w.label2 = vanilla.TextBox('auto', 'Choose Target font:')
		self.w.fontB = vanilla.PopUpButton('auto', [], sizeStyle = "regular")  # , callback = self.optionsChanged
		self.w.btnRun = vanilla.Button('auto', title = 'Run', callback = self.btnRunCallback)  # ,
		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False)
		self.w.textBox.setLexer(BaseLexerDGAKW())
		self.w.textBox.setHighlightStyle(get_style_by_name('material'))

		rules = [
			# Horizontal
			"H:|-border-[label1]-border-|",
			"H:|-border-[fontA]-border-|",
			"H:|-border-[label2]-border-|",
			"H:|-border-[fontB]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			"V:|-border-[label1]-space-[fontA]-border-[label2]-space-[fontB]-border-[btnRun]-border-[textBox]-0-|",
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
		reportA = diffGroups(masterfont = fontA, targetfont = fontB)
		reportB = diffKerning(masterfont = fontA, targetfont = fontB, host = self.parent.hashKernDic)
		self.w.textBox.set('\n'.join(reportA) + '\n'.join(reportB))

	#
	def getFontName (self, font, fonts):
		# by Andy Clymer, June 2018
		# A helper to get the font name, starting with the preferred name and working back to the PostScript name
		# Make sure that it's not the same name as another font in the fonts list
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
			while name + " (%s)" % i in fonts:
				i += 1
			name = name + " (%s)" % i
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


def main (parent=None):
	if not parent: return
	TDDiffGroupsAndKerningWindow(parent = parent)
