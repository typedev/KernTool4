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
	report.append('+ master: %s %s' % (masterfont.info.familyName, masterfont.info.styleName) )
	report.append('+ groups: %i' % len(masterfont.groups))
	report.append('- target: %s %s' % (targetfont.info.familyName, targetfont.info.styleName) )
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
			report.append('- target (%i): %s' % (len(c1), ' '.join(c1)))
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


#
# def diffKerning(oldTable, newTable, labelFrom = 'old', labelTo = 'new'):
#     newPairs = {}
#     delPairs = {}
#     chgPairs = {}
#     nulPairs = {}
#     report = tdReport.Report(process='diffKern')
#     report.stroke('=')
#     report.add('Kerning report:')
#     for (l, r), v in newTable.items():
#         if v == 0:
#             nulPairs[l, r] = v
#         elif not oldTable.has_key((l, r)):
#             newPairs[l, r] = v
#             report.add('New Pair: %s %s %i' % (l, r, v))
#         elif oldTable[l, r] != newTable[l, r]:
#             chgPairs[l, r] = [oldTable[l, r], newTable[l, r]]
#             report.add('Changed Pair: %s %s' % (l, r))
#             report.add('%s: %i\t%s: %i' % (labelFrom,
#              oldTable[l, r],
#              labelTo,
#              newTable[l, r]), level=1)
#
#     for (l, r), v in oldTable.items():
#         if not newTable.has_key((l, r)):
#             delPairs[l, r] = v
#             report.add('Pair Deleted: %s %s %i' % (l, r, v))
#
#     report.add('Pairs TOTAL: Added=%i Deleted=%i Changed=%i Null pairs (ignored)=%i' % (len(newPairs),
#      len(delPairs),
#      len(chgPairs),
#      len(nulPairs)))
#     return report.gettext()


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
		report = diffGroups(masterfont = fontA, targetfont = fontB)
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
	TDDiffGroupsAndKerningWindow(parent = parent)
