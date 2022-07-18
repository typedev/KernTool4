import os, sys
from fontParts.world import *


def saveKerning (selectedkern, filename):
	print('Saving Kerning Pairs to file:')
	fn = filename
	print(fn)
	groupsfile = open(fn, mode = 'w')
	txt = ''
	for (l, r), v in sorted(selectedkern.items()):
		txt += '%s %s %s\n' % (l, r, v)
	groupsfile.write(txt)
	groupsfile.close()
	print(len(selectedkern), 'pairs saved..')
	print('Done.')

def saveKernPattern(patternlist, filename, pattern2line = 8):
	print('Saving Kerning Pattern to file:')
	fn = filename
	print(fn)
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
	print('Done.')

def getListLanguagesFromFont(self, font):
	listlanguages = []
	for glyph in font:
		langset = self.langSet.getBaseScriptByGlyphName(font, glyph.name)
		if langset:
			for lang in langset:
				if lang not in listlanguages:
					listlanguages.append(lang)
	return listlanguages

def transferKern(self, masterfont, targetfonts, language = 'cyrillic', applyTransfer = False):
	# pathname = os.path.dirname(sys.argv[0])
	workPath = os.path.join(masterfont.path.replace(os.path.basename(masterfont.path),''))

	listlanguages = getListLanguagesFromFont(self, masterfont)
	# print (listlanguages)
	listlanguages.remove(language)
	# print (listlanguages)
	for targetfont in targetfonts:
		print ('Start transfer %s pairs' % language)
		print ('\tfrom:\t', masterfont.info.familyName, masterfont.info.styleName)
		print ('\tto:\t', targetfont.info.familyName, targetfont.info.styleName)
		pairs2transfer = []
		skipedpairs = []
		questionablePairs = []
		for (l,r), v in masterfont.kerning.items():
			if (l, r) in targetfont.kerning:
				# skip pair if they already in target font and show diff value
				lg = self.getKeyGlyphByGroupname(l)
				rg = self.getKeyGlyphByGroupname(r)
				pattern = self.langSet.wrapPairToPattern(masterfont, (lg, rg))
				skipedpairs.append((l, r, lg, rg, v, targetfont.kerning[(l, r)], pattern))
			else:
				lg = self.getKeyGlyphByGroupname(l)
				rg = self.getKeyGlyphByGroupname(r)
				llang = self.langSet.getBaseScriptByGlyphName(masterfont, lg)
				rlang = self.langSet.getBaseScriptByGlyphName(masterfont, rg)
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
							pattern = self.langSet.wrapPairToPattern(masterfont, (lg, rg))
							questionablePairs.append((l,r,lg,rg,llang,rlang,v, pattern))
						else:
							pattern = self.langSet.wrapPairToPattern(masterfont, (lg, rg))
							pairs2transfer.append((l,r,lg,rg,llang,rlang,v, pattern))
							if applyTransfer:
								targetfont.kerning[(l,r)] = masterfont.kerning[(l,r)]

		if pairs2transfer:
			pattern2transfer = []
			pattern2transferSpace = []
			pairs2filetransfer = {}
			print ('+'*40)
			print ('PairsList contains %s language' % language)
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
			saveKernPattern(pattern2transfer, fpattern)
			saveKernPattern(pattern2transferSpace, fpatternS)

		if questionablePairs:
			pattern2questionable = []
			pairs2filequestionable = {}
			pattern2transferSpace = []
			print ('%'*40)
			print ('Pairs contains %s language but transfer is questionable' % language)
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

			saveKerning(pairs2filequestionable, fpairspath)
			saveKernPattern(pattern2questionable, fpattern)
			saveKernPattern(pattern2transferSpace, fpatternS)

		if skipedpairs:
			patternSkipped = []
			pairs2fileskipped = {}
			pairs2filemaster = {}
			pattern2transferSpace = []
			print('=' * 40)
			print('Pairs already in target font, skipped..')
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
			saveKerning(pairs2fileskipped, fpairspath)
			saveKerning(pairs2filemaster, fpairsmasterpath)
			saveKernPattern(patternSkipped, fpattern)
			saveKernPattern(pattern2transferSpace, fpatternS)


		print ('Total pairs:', len(masterfont.kerning.items()),
		       'Pairs to transfer:', len(pairs2transfer),
		       'Questionable:', len(questionablePairs),
		       'Skiped pairs:', len(skipedpairs))


def main(parent = None):
	if not parent: return
	self = parent.hashKernDic
	targetfonts = []
	masterfont = self.font
	for font in AllFonts():
		if font != masterfont:
			targetfonts.append(font)
	transferKern(self, masterfont = masterfont, targetfonts = targetfonts)
	self.makeReverseGroupsMapping()
	parent.refreshGroupsView()

if __name__ == "__main__":
	main()