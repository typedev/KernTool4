import os, sys
from fontParts.world import *
import vanilla
from mojo.UI import *
from pygments.lexer import RegexLexer, bygroups

from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles

__doc__ = """
The script removes cross-language pairs.

Pairs are checked for the first level of compatibility - Latin/Cyrillic, Latin/Greek, Georgian/Armenian, etc.
It is also possible to check and delete pairs according to the second level of compatibility, pairs within the same script - for example, in Latin: French / German, in Cyrillic: Abkhaz / Chuvash. But this is rarely applied in practice.
***The script works only from GroupsControl***
"""
def removeCrossLanguagePairs (host, level = 1, remove = True):
	# self = parent.hashKernDic
	pairs2remove = []
	for pair in host.font.kerning:
		if not host.checkPairLanguageCompatibilityGroupped(pair, level = level):
			pairs2remove.append(pair)
	if remove:
		for pair in pairs2remove:
			host.font.kerning.remove(pair)
	return pairs2remove

def checkPatternsLib(host, fonts):
	for font in fonts:
		if font not in host.langSet.libPatterns:
			host.langSet.setupPatternsForFont(font)

class BaseLexerRCP(RegexLexer):
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
class TDRemoveCrossPairsWindow(object):
	def __init__ (self, parent=None):
		_version = '0.3'
		self.parent = parent
		self.host = parent.hashKernDic
		self.fontNames = []
		langsLevels = ['1 = by Script', '2 = by Language (pairs within the same script)']
		# langs = getListLanguagesFromFont(self.parent.hashKernDic, CurrentFont())
		self.w = vanilla.FloatingWindow((500, 600), minSize = (300, 300), title = 'Remove Cross-Langauges Pairs v%s' % _version)
		# self.w.label1 = vanilla.TextBox('auto', 'Choose font:')
		# self.w.fontA = vanilla.PopUpButton('auto', [], sizeStyle = "regular")
		self.w.label2 = vanilla.TextBox('auto', 'Choose Level compatibility:')
		self.w.langLevel = vanilla.PopUpButton('auto', langsLevels, sizeStyle = "regular")
		self.w.applyRemove = vanilla.CheckBox('auto', 'do not remove, only show pairs', value = True)
		self.w.btnRun = vanilla.Button('auto', title = 'Run', callback = self.btnRunCallback)  # ,
		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False)
		self.w.textBox.setLexer(BaseLexerRCP())
		self.w.textBox.setHighlightStyle(get_style_by_name('material'))

		rules = [
			# Horizontal
			# "H:|-border-[label1]-border-|",
			# "H:|-border-[fontA]-border-|",
			"H:|-border-[label2]-border-|",
			"H:|-border-[langLevel]-border-|",
			"H:|-border-[applyRemove]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			# "V:|-border-[label1]-space-[fontA]-border-[label2]-border-[fontB]-border-[lang]-border-[btnRun]-[textBox]-0-|",
			"V:|-border-[langLevel]-border-[applyRemove]-[btnRun]-border-[textBox]-0-|"
		]
		metrics = {
			"border": 15,
			"space": 8
		}
		self.w.addAutoPosSizeRules(rules, metrics)
		# self.collectFonts()

		self.w.open()

	def btnRunCallback (self, sender):
		fontA = self.parent.font
		level = self.w.langLevel.get()
		apply = not self.w.applyRemove.get()
		checkPatternsLib(host = self.host, fonts = [fontA])
		if level == 0:
			level = 1
		elif level == 1:
			level = 2
		# print (fontA, level, apply)
		report = removeCrossLanguagePairs(self.host, level = level, remove = apply)
		self.parent.refreshGroupsView()
		patterns = []
		pattern2line = 8
		txt = ''
		p2l = 0
		for pair in report:
			l, r = pair
			lg = self.host.getKeyGlyphByGroupname(l)
			rg = self.host.getKeyGlyphByGroupname(r)
			s1, lp, rp, s2 = self.host.langSet.wrapPairToPattern(fontA, (lg, rg))
			txt += '/%s/%s/%s/%s' % (s1, lp, rp, s2)
			p2l += 1
			if p2l == pattern2line:
				patterns.append(txt)
				p2l = 0
				txt = ''
		self.w.textBox.set('\n'.join(patterns))

	# def getFontName (self, font, fonts):
	# 	# by Andy Clymer, June 2018
	# 	# A helper to get the font name, starting with the preferred name and working back to the PostScript name
	# 	# Make sure that it's not the same name as another font in the fonts list
	# 	if font.info.openTypeNamePreferredFamilyName and font.info.openTypeNamePreferredSubfamilyName:
	# 		name = "%s %s" % (font.info.openTypeNamePreferredFamilyName, font.info.openTypeNamePreferredSubfamilyName)
	# 	elif font.info.familyName and font.info.styleName:
	# 		name = "%s %s" % (font.info.familyName, font.info.styleName)
	# 	elif font.info.fullName:
	# 		name = font.info.fullName
	# 	elif font.info.fullName:
	# 		name = font.info.postscriptFontName
	# 	else: name = "Untitled"
	# 	# Add a number to the name if this name already exists
	# 	if name in fonts:
	# 		i = 2
	# 		while name + " (%s)" % i in fonts:
	# 			i += 1
	# 		name = name + " (%s)" % i
	# 	return name
	#
	# def collectFonts (self):
	# 	# by Andy Clymer, June 2018
	# 	# Hold aside the current font choices
	# 	font0idx = self.w.fontA.get()
	# 	# font1idx = self.w.fontB.get()
	# 	if not font0idx == -1:
	# 		font0name = self.fontNames[font0idx]
	# 	else: font0name = None
	# 	# if not font1idx == -1:
	# 	# 	font1name = self.fontNames[font1idx]
	# 	# else: font1name = None
	# 	# Collect info on all open fonts
	# 	self.fonts = AllFonts()
	# 	self.fontNames = []
	# 	for font in self.fonts:
	# 		self.fontNames.append(self.getFontName(font, self.fontNames))
	# 	# Update the popUpButtons
	# 	self.w.fontA.setItems(self.fontNames)
	# 	# self.w.fontB.setItems(self.fontNames)
	# 	# If there weren't any previous names, try to set the first and second items in the list
	# 	if font0name == None:
	# 		if len(self.fonts):
	# 			self.w.fontA.set(0)
	# 	# if font1name == None:
	# 	# 	if len(self.fonts) >= 1:
	# 	# 		self.w.fontB.set(1)
	# 	# Otherwise, if there had already been fonts choosen before new fonts were loaded,
	# 	# try to set the index of the fonts that were already selected
	# 	if font0name in self.fontNames:
	# 		self.w.fontA.set(self.fontNames.index(font0name))
	# 	# if font1name in self.fontNames:
	# 	# 	self.w.fontB.set(self.fontNames.index(font1name))

def main (parent = None):
	if not parent: return
	TDRemoveCrossPairsWindow(parent = parent)


