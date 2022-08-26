import os, sys
from fontParts.world import *
import vanilla
from mojo.UI import *
from pygments.lexer import RegexLexer, bygroups

from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles

def saveKerning (selectedkern, filename, pref = '+'):
	report =[]
	report.append('* Saving PairsList to file:')
	fn = filename
	report.append(fn)
	groupsfile = open(fn, mode = 'w')
	txt = ''
	for (l, r), v in sorted(selectedkern.items()):
		txt += '%s %s %s\n' % (l, r, v)
	groupsfile.write(txt)
	groupsfile.close()
	report.append('%s %i pairs saved..' % (pref, len(selectedkern)))
	# report.append('* Done.')
	return report

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

def getListLanguagesFromFont(host, font):
	listlanguages = []
	for glyph in font:
		langset = host.langSet.getBaseScriptByGlyphName(font, glyph.name)
		if langset:
			for lang in langset:
				if lang not in listlanguages:
					listlanguages.append(lang)
	return listlanguages

def transferKern(host, masterfont, targetfont, language = 'cyrillic', applyTransfer = True):
	# pathname = os.path.dirname(sys.argv[0])
	workPath = os.path.join(masterfont.path.replace(os.path.basename(masterfont.path),''))

	listlanguages = getListLanguagesFromFont(host, masterfont)
	# print (listlanguages)
	listlanguages.remove(language)
	report = []
	report.append('='*40)
	report.append ('Start transfer %s pairs' % language)
	report.append ('from: %s %s' % (masterfont.info.familyName, masterfont.info.styleName))
	report.append ('to:   %s %s' % (targetfont.info.familyName, targetfont.info.styleName))
	pairs2transfer = []
	skipedpairs = []
	questionablePairs = []
	for (l,r), v in masterfont.kerning.items():
		if (l, r) in targetfont.kerning:
			# skip pair if they already in target font and show diff value
			lg = host.getKeyGlyphByGroupname(l)
			rg = host.getKeyGlyphByGroupname(r)
			pattern = host.langSet.wrapPairToPattern(masterfont, (lg, rg))
			skipedpairs.append((l, r, lg, rg, v, targetfont.kerning[(l, r)], pattern))
		else:
			lg = host.getKeyGlyphByGroupname(l)
			rg = host.getKeyGlyphByGroupname(r)
			llang = host.langSet.getBaseScriptByGlyphName(masterfont, lg)
			rlang = host.langSet.getBaseScriptByGlyphName(masterfont, rg)
			if llang and rlang:
				if language in llang or language in rlang:
					lmulty = False
					rmulty = False
					for lang in listlanguages:
						if lang in llang:
							lmulty = True
						if lang in rlang:
							rmulty = True
					if lmulty and rmulty:
						pattern = host.langSet.wrapPairToPattern(masterfont, (lg, rg))
						questionablePairs.append((l,r,lg,rg,llang,rlang,v, pattern))
					else:
						pattern = host.langSet.wrapPairToPattern(masterfont, (lg, rg))
						pairs2transfer.append((l,r,lg,rg,llang,rlang,v, pattern))
						if applyTransfer:
							targetfont.kerning[(l,r)] = masterfont.kerning[(l,r)]

	if pairs2transfer:
		pattern2transfer = []
		pattern2transferSpace = []
		pairs2filetransfer = {}
		report.append ('*'*40)
		report.append ('PairsList contains %s language' % language)
		for item in pairs2transfer:
			l, r, lg, rg, llang, rlang, v, pattern = item
			pairs2filetransfer[(l,r)] = v

			pattern2transfer.append(pattern)
			s1, lp, rp, s2 = pattern
			pattern = ('space', lp, rp, 'space')
			pattern2transferSpace.append(pattern)

		fpairspath = os.path.join(workPath, 'PairsList for transfer - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		fpattern = os.path.join(workPath, 'Patterns to check - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		fpatternS = os.path.join(workPath, 'Patterns wSpace to check - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		if not applyTransfer:
			saveKerning(pairs2filetransfer, fpairspath)
		report.extend(saveKernPattern(pattern2transfer, fpattern))
		report.extend(saveKernPattern(pattern2transferSpace, fpatternS))

	if questionablePairs:
		pattern2questionable = []
		pairs2filequestionable = {}
		pattern2transferSpace = []
		report.append ('*'*40)
		report.append ('- Pairs contains %s language but transfer is questionable' % language)
		for item in questionablePairs:
			l, r, lg, rg, llang, rlang, v, pattern = item
			pairs2filequestionable[(l,r)] = v

			pattern2questionable.append( pattern )
			s1, lp, rp, s2 = pattern
			pattern = ('space', lp, rp, 'space')
			pattern2transferSpace.append(pattern)
		fpairspath = os.path.join(workPath, 'Questionable PairsList - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		fpattern = os.path.join(workPath, 'Questionable Patterns - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		fpatternS = os.path.join(workPath, 'Questionable Patterns wSpace to check - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))

		report.extend(saveKerning(pairs2filequestionable, fpairspath, pref = '-'))
		report.extend(saveKernPattern(pattern2questionable, fpattern))
		report.extend(saveKernPattern(pattern2transferSpace, fpatternS))

	if skipedpairs:
		patternSkipped = []
		pairs2fileskipped = {}
		pairs2filemaster = {}
		pattern2transferSpace = []
		report.append('*' * 40)
		report.append('= Pairs already in target font, skipped..')
		for item in skipedpairs:
			l, r, lg, rg, v, v2, pattern = item
			pairs2fileskipped[(l,r)] = v2
			pairs2filemaster[(l,r)] = v

			patternSkipped.append( pattern )
			s1, lp, rp, s2 = pattern
			pattern = ('space', lp, rp, 'space')
			pattern2transferSpace.append(pattern)
		fpairspath = os.path.join(workPath, 'Skipped PairsList - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		fpairsmasterpath = os.path.join(workPath, 'Skipped Master PairsList - %s %s.txt' % (masterfont.info.familyName, masterfont.info.styleName))
		fpattern = os.path.join(workPath, 'Skipped Patterns - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		fpatternS = os.path.join(workPath, 'Skipped Patterns wSpace to check - %s %s.txt' % (targetfont.info.familyName, targetfont.info.styleName))
		report.extend(saveKerning(pairs2fileskipped, fpairspath))
		report.extend(saveKerning(pairs2filemaster, fpairsmasterpath))
		report.extend(saveKernPattern(patternSkipped, fpattern))
		report.extend(saveKernPattern(pattern2transferSpace, fpatternS))

	report.append ('= Total pairs: %i' % len(masterfont.kerning.items()))
	report.append ('+ Pairs to transfer: %i' % len(pairs2transfer))
	report.append ('- Questionable: %i' % len(questionablePairs))
	report.append ('* Skiped pairs: %i' % len(skipedpairs))
	report.append('\n')
	return report

class BaseLexerTKBL(RegexLexer):
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

def checkPatternsLib(host, fonts):
	for font in fonts:
		if font not in host.langSet.libPatterns:
			host.langSet.setupPatternsForFont(font)

class TDTransferKernWindow(object):
	def __init__ (self, parent=None):
		_version = '0.3'
		self.parent = parent
		self.fontNames = []
		langs = ['cyrillic']
		# langs = getListLanguagesFromFont(self.parent.hashKernDic, CurrentFont())
		self.w = vanilla.FloatingWindow((500, 600), minSize = (300, 300), title = 'Transfer Kerning by Language v%s' % _version)
		self.w.label1 = vanilla.TextBox('auto', 'Choose Master font:')
		self.w.fontA = vanilla.PopUpButton('auto', [], sizeStyle = "regular")
		self.w.label2 = vanilla.TextBox('auto', 'Choose Target font:')
		self.w.fontB = vanilla.PopUpButton('auto', [], sizeStyle = "regular") # , callback = self.optionsChanged
		self.w.lang = vanilla.PopUpButton('auto', langs, sizeStyle = "regular")
		self.w.applyTransfer = vanilla.CheckBox('auto', 'Apply Transfer', value = True)
		self.w.btnRun = vanilla.Button('auto', title = 'Run', callback = self.btnRunCallback)  # ,
		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False)
		self.w.textBox.setLexer(BaseLexerTKBL())
		self.w.textBox.setHighlightStyle(get_style_by_name('material'))

		rules = [
			# Horizontal
			"H:|-border-[label1]-border-|",
			"H:|-border-[fontA]-border-|",
			"H:|-border-[label2]-border-|",
			"H:|-border-[fontB]-border-|",
			"H:|-border-[lang]-border-[applyTransfer(120)]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			"V:|-border-[label1]-space-[fontA]-border-[label2]-border-[fontB]-border-[lang]-border-[btnRun]-[textBox]-0-|",
			"V:|-border-[label1]-space-[fontA]-border-[label2]-border-[fontB]-border-[applyTransfer]-[btnRun]-border-[textBox]-0-|"
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
		checkPatternsLib(host = self.parent.hashKernDic, fonts = [fontA, fontB])
		report = transferKern(host = self.parent.hashKernDic, masterfont = fontA, targetfont = fontB, applyTransfer = self.w.applyTransfer.get())
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


def main(parent = None):
	if not parent: return
	TDTransferKernWindow(parent = parent)




if __name__ == "__main__":
	main()