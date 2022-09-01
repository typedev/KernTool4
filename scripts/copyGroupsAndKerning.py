import os, sys
from fontParts.world import *
import vanilla
from mojo.UI import *
from pygments.lexer import RegexLexer, bygroups

from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles

__doc__ = """
Script to transfer all kerning groups and kerning from master font

"""


def transferGroupsAndKerning (masterfont, targetfont, transferGroups=True, transferPairs=True):
	missingGlyphs = []
	report = []

	if transferGroups:
		groups2kill = []
		for groupname, content in targetfont.groups.items():
			if groupname.startswith('public.kern'):
				groups2kill.append(groupname)
		for groupname in groups2kill:
			del targetfont.groups[groupname]

		countgroup = 0
		for groupname, content in masterfont.groups.items():

			targetfont.groups[groupname] = ()
			newcontent = []

			for glyphname in content:
				if glyphname in targetfont:
					newcontent.append(glyphname)
				else:
					missingGlyphs.append( glyphname )
			if newcontent:
				targetfont.groups[groupname] = tuple(newcontent)
				countgroup += 1
		print('source groups:', len(masterfont.groups))
		print('transfered:', len(targetfont.groups))

	if transferPairs:
		targetfont.kerning.clear()

		countpairs = 0
		for (l, r), v in masterfont.kerning.items():
			targetfont.kerning[(l, r)] = v
			countpairs += 1

		print('source pairs:', len(masterfont.kerning))
		print('transfered:', len(targetfont.kerning))

	report.append('=' * 40)
	report.append('Groups and Kerning transfer report')
	report.append('+ master: %s %s' % (masterfont.info.familyName, masterfont.info.styleName))
	report.append('+ groups: %i' % len(masterfont.groups))
	report.append('+ pairs: %i' % len(masterfont.kerning))
	report.append('- target: %s %s' % (targetfont.info.familyName, targetfont.info.styleName))
	report.append('- groups: %i' % len(targetfont.groups))
	report.append('- pairs: %i' % len(targetfont.kerning))
	if missingGlyphs:
		report.append('=' * 40)
		report.append('Glyphs missing in target font:')
		report.append('- %s' % ' '.join(missingGlyphs))

	report.append('\n')
	return report



class BaseLexerTGAKW(RegexLexer):
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


class TDTransferGroupsAndKerningWindow(object):
	def __init__ (self, parent=None):
		_version = '0.4'
		self.parent = parent
		self.fontNames = []

		self.w = vanilla.FloatingWindow((500, 600), minSize = (300, 300), title = 'Transfer Groups and Kerning v%s' % _version)
		self.w.label1 = vanilla.TextBox('auto', 'Choose Master font:')
		self.w.fontA = vanilla.PopUpButton('auto', [], sizeStyle = "regular")
		self.w.label2 = vanilla.TextBox('auto', 'Choose Target font:')
		self.w.fontB = vanilla.PopUpButton('auto', [], sizeStyle = "regular")  # , callback = self.optionsChanged
		self.w.applyGroups = vanilla.CheckBox('auto', 'Copy Groups', value = True )
		self.w.applyPairs = vanilla.CheckBox('auto', 'Copy Kerning', value = True )

		self.w.btnRun = vanilla.Button('auto', title = 'Run', callback = self.btnRunCallback)  # ,
		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False)
		self.w.textBox.setLexer(BaseLexerTGAKW())
		self.w.textBox.setHighlightStyle(get_style_by_name('material'))

		rules = [
			# Horizontal
			"H:|-border-[label1]-border-|",
			"H:|-border-[fontA]-border-|",
			"H:|-border-[label2]-border-|",
			"H:|-border-[fontB]-border-|",
			"H:|-border-[applyGroups]-space-[applyPairs(==applyGroups)]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			"V:|-border-[label1]-space-[fontA]-border-[label2]-space-[fontB]-border-[applyGroups]-border-[btnRun]-border-[textBox]-0-|",
			"V:|-border-[label1]-space-[fontA]-border-[label2]-space-[fontB]-border-[applyPairs]-border-[btnRun]-border-[textBox]-0-|",

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
		report = transferGroupsAndKerning(masterfont = fontA, targetfont = fontB,
		                                  transferGroups = self.w.applyGroups.get(), transferPairs = self.w.applyPairs.get())
		self.w.textBox.set('\n'.join(report))

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
	TDTransferGroupsAndKerningWindow(parent = parent)
