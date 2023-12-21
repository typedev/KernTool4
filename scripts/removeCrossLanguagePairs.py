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
		patterns.append('\n')
		self.w.textBox.set('\n'.join(patterns))



def main (parent = None):
	if not parent: return
	TDRemoveCrossPairsWindow(parent = parent)


