# -*- coding: utf-8 -*-

import os
import codecs, sys, os, glob
import xml.etree.ElementTree as ET


class TDLangSet(object):
	def __init__(self, init = 'XML'):
		self.base = {}  # base script: [unicodes] # latin:[], cyrillic:[], etc.
		self.base_reversed = {} # unicode: [base script],
		self.langdic = {} # language: [unicodes]
		self.langdic_reversed = {} # unicode: [languages]
		self.langdic_structured = {} # language = dict(upper = upper, lower = lower, other = other, digits = digit, punct = punct)
		self.pattern = {} # unicode: pattern
		self.basicPatternNames = {}
		self.libPatterns = {}
		if init == 'XML':
			self._initializeFromXML()
			# print ('tdLangSet initialized from XML library')
		elif init == 'TBL':
			self._initializeFromTBL()
			# print('tdLangSet initialized from TBL library')

	def _getUnicodeFromValue(self, code):
		if code.startswith('#'):
			return int(code.replace('#',''), 16)
		else:
			return None

	def _splitUnicodesList(self, codeline, base, language, fulllist, addtofullllist = True):
		uline = []
		if codeline:
			for u in codeline.split(' '):
				_u = self._getUnicodeFromValue(u)
				if u:
					uline.append(_u)
				else:
					print ('WARNING tdLangSet: adding %s to %s %s as glyphName' % (u, base, language))
					uline.append(u)
		if uline and addtofullllist:
			fulllist.extend(uline)
		return uline, fulllist


	def _initializeFromXML(self):
		# libpath = os.path.join(sys.path[0],'resources','langset')
		libpath = os.path.dirname(__file__)
		libpath = os.path.join(libpath, 'resources','langset')
		files = glob.glob(libpath + '/**/*.xml', recursive = True)
		self.langdic = {}
		self.langdic_reversed = {}
		self.langdic_structured = {}
		self.pattern = {}
		for f in files:
			# print (f)
			tree = ET.parse(f)
			root = tree.getroot()
			base = None
			language = None
			keycode = None
			fulllist = []
			fullpatterns = []
			upper = []
			lower = []
			other = []
			digit = []
			punct = []
			pattUpper = []
			pattLower = []
			pattOther = []
			pattDigit = []
			pattPunct = []

			for elem in root:
				key = elem.attrib['name']
				value = elem.text
				# print ('key', key, value)
				if key == 'enable' and value == 'off':
					print ('ignored:',f)
					break

				if key == 'base':
					base = value
				if key == 'name':
					language = value
				if key == 'keycode':
					uni = self._getUnicodeFromValue(value)
					if uni:
						keycode = uni
					else:
						print ('ERROR in tdLangSet: keycode must be Unicode: #XXXX', base, language, value)
						keycode = None
				if key == 'upper':
					upper, fulllist = self._splitUnicodesList(value, base, language, fulllist)
				if key == 'lower':
					lower, fulllist = self._splitUnicodesList(value, base, language, fulllist)
				if key == 'other':
					other, fulllist = self._splitUnicodesList(value, base, language, fulllist)
				if key == 'digits':
					digit, fulllist = self._splitUnicodesList(value, base, language, fulllist)
				if key == 'punct':
					punct, fulllist = self._splitUnicodesList(value, base, language, fulllist)

				if key == 'patternUpper':
					pattUpper, fullpatterns = self._splitUnicodesList(value, base, language, fullpatterns)#, addtofullllist = False)
				if key == 'patternLower':
					pattLower, fullpatterns = self._splitUnicodesList(value, base, language, fullpatterns)#, addtofullllist = False)
				if key == 'patternOther':
					pattOther, fullpatterns = self._splitUnicodesList(value, base, language, fullpatterns)#, addtofullllist = False)
				if key == 'patternDigits':
					pattDigit, fullpatterns = self._splitUnicodesList(value, base, language, fullpatterns)#, addtofullllist = False)
				if key == 'patternPunct':
					pattPunct, fullpatterns = self._splitUnicodesList(value, base, language, fullpatterns)#, addtofullllist = False)

			self.langdic[language] = fulllist
			self.langdic_structured[language] = dict(upper = upper, lower = lower, other = other, digits = digit, punct = punct)
			if base not in self.base:
				self.base[base] = []

			for u in fulllist:
				if u not in self.base_reversed:
					self.base_reversed[u] = []
				if base not in self.base_reversed[u]:
					self.base_reversed[u].append(base)
				if u not in self.langdic_reversed:
					self.langdic_reversed[u] = [language]
				else:
					self.langdic_reversed[u].append(language)

				if u in upper:
					self.pattern[u] = pattUpper
				if u in lower:
					self.pattern[u] = pattLower
				if u in other:
					self.pattern[u] = pattOther
				if u in digit:
					self.pattern[u] = pattDigit
				if u in punct:
					self.pattern[u] = pattPunct

				if u not in self.base[base]:
					self.base[base].append(u)

			for u in fullpatterns:
				self.basicPatternNames[u] = None

				# if key == 'name':
				# 	self.langdic[value] = []
				# 	lang = value
				# elif key == 'upper' or key == 'lower' or key == 'other' or key == 'digits':
				# 	if value and lang:
				# 		for code in value.split(' '):
				# 			if code:
				# 				unicodeslist.append(code)
				# 				if int(code, 16) not in self.langdic_reversed:
				# 					self.langdic_reversed[int(code, 16)] = [lang]
				# 				else:
				# 					self.langdic_reversed[int(code, 16)].append(lang)
				# 		self.langdic[lang].extend(unicodeslist)


	def _initializeFromTBL(self):
		tblpath = sys.path[0] +'/langset-utf8.tbl'
		f = codecs.open(tblpath, 'r', encoding = 'utf-8')#open(tblpath, 'r')
		self.langdic = {}
		lang = ''
		for line in f:
			l = line.strip()
			if not l.startswith('@'):
				if l.startswith(';'):
					lang = l.replace(';', '')
					self.langdic[lang] = []
				else:
					if '\t' not in l and l not in self.langdic[lang]:
						self.langdic[lang].append(l)
					else:
						for tl in l.split('\t'):
							if tl not in self.langdic[lang]:
								self.langdic[lang].append(tl)
		self.langdic_reversed = {}
		for k, v in sorted(self.langdic.items()):
			for uni in v:
				if int(uni, 16) not in self.langdic_reversed:
					self.langdic_reversed[int(uni, 16)] = [k]
				else:
					self.langdic_reversed[int(uni, 16)].append(k)


	def makeConvertionPatternsFromFont(self, font):
		patterns = {}
		try:
			gspace = font.getCharacterMapping()[int('0020', 16)][0]
		except:
			gspace = 'space'
			print ('ERROR!!! glyph /space not found by unicode')
		for key, n in self.basicPatternNames.items():
			try:
				patterns[key] = font.getCharacterMapping()[key][0]
			except:
				patterns[key] = gspace
		patterns[0] = gspace
		# print (patterns)
		return patterns

	def setupPatternsForFont(self, font):
		self.libPatterns[font] = self.makeConvertionPatternsFromFont(font)
		# print ('tdLangSet created patterns for the font', font)

	def setupPatternsForFonts(self, fonts):
		self.libPatterns = {}
		for font in fonts:
			self.setupPatternsForFont(font)

	def wrapGlyphToPattern(self, font, glyphname):
		base = glyphname
		if glyphname not in font:
			side1 = font[self.libPatterns[font][0]].name
			side2 = font[self.libPatterns[font][0]].name
			return (side1, glyphname, side2)

		uni = font[glyphname].unicode
		sfx = None
		side1 = None
		side2 = None
		if '.' in glyphname and not glyphname.startswith('.'):
			base = glyphname.split('.')[0]
			sfx = '.%s' % '.'.join(glyphname.split('.')[1:])
			if base in font:
				uni = font[base].unicode
		if uni and uni in self.pattern:
			side1, side2 = self.pattern[uni]
			side1 = font[self.libPatterns[font][side1]].name
			side2 = font[self.libPatterns[font][side2]].name
			if sfx and side1 + sfx in font:
				side1 += sfx
			if sfx and side2 + sfx in font:
				side2 += sfx
		elif not uni and base in self.pattern:
			side1, side2 = self.pattern[base]
			side1 = font[self.libPatterns[font][side1]].name
			side2 = font[self.libPatterns[font][side2]].name
			if sfx and side1 + sfx in font:
				side1 += sfx
			if sfx and side2 + sfx in font:
				side2 += sfx
		else:
			side1 = font[self.libPatterns[font][0]].name
			side2 = font[self.libPatterns[font][0]].name
			# if sfx and side1 + sfx in font:
			# 	side1 += sfx
			# if sfx and side2 + sfx in font:
			# 	side2 += sfx
		return (side1, glyphname, side2)

	def wrapPairToPattern(self, font, pair):
		l, r = pair
		(side1L, g1, side2L) = self.wrapGlyphToPattern(font, l)
		(side1R, g2, side2R) = self.wrapGlyphToPattern(font, r)
		return (side1L, g1, g2, side2R)


	def wrapGlyphsLine_MarksAndMasks (self, font, glyphsline, marks):
		t = ['']
		_marks = [False]
		_mask = [False]
		for idx, name in enumerate(glyphsline):
			(side1, glyphname, side2) = self.wrapGlyphToPattern(font, name)
			# print (t[-1], pattern[0],pattern[1],pattern[2])
			if t[-1] != font[side1]:
				t.extend([font[side1], font[glyphname], font[side2]])
				_marks.extend([False, marks[idx], False])
				_mask.extend([False, True, False])
			else:
				t.extend([font[glyphname], font[side2]])
				_marks.extend([marks[idx], False])
				_mask.extend([True, False])
		return (t[1:], _marks[1:], _mask[1:])

	def _getPairUnicodes(self, font, pair):
		l, r = pair
		uniL, uniR = None, None
		if '.' in l and not l.startswith('.'):
			l = l.split('.')[0]
		if '.' in r and not r.startswith('.'):
			r = r.split('.')[0]
		if l in font and r in font:
			uniL = font[l].unicode
			uniR = font[r].unicode
		return (uniL, uniR)

	def checkPairLanguageCompatibility(self, font, pair):
		uniL, uniR = self._getPairUnicodes(font, pair)
		if uniL and uniR:
			return self.checkPairLangsByUnicodes((uniL,uniR))
		return True

	def checkPairLangsByUnicodes(self, pair):
		uniL, uniR = pair
		if uniL in self.langdic_reversed and uniR in self.langdic_reversed:
			setL = self.langdic_reversed[uniL]
			setR = self.langdic_reversed[uniR]
			if not set(setL).intersection(setR):
				return False
		return True

	def checkPairBaseScriptCompatibility(self, font, pair):
		uniL, uniR = self._getPairUnicodes(font, pair)
		if uniL and uniL in self.base_reversed and uniR and uniR in self.base_reversed:
			if not set(self.base_reversed[uniL]).intersection(self.base_reversed[uniR]):
				return False
		return True

	def getBaseScriptByGlyphName(self, font, glyphname):
		if '.' in glyphname and not glyphname.startswith('.'):
			glyphname = glyphname.split('.')[0]
		uni = None
		if glyphname in font:
			uni = font[glyphname].unicode
		if uni and uni in self.base_reversed:
			return self.base_reversed[uni]
		return None



	# def checkPairLangsByUnicodesForIn(self, pair):
	# 	uniL, uniR = pair
	# 	result = False
	# 	if uniL in self.langdic_reversed and uniR in self.langdic_reversed:
	# 		setL = self.langdic_reversed[uniL]
	# 		setR = self.langdic_reversed[uniR]
	# 		for l in setL:
	# 			if l in setR:
	# 				return True
	# 		for r in setL:
	# 			if r in setL:
	# 				return True
	#
	#
	# 		# if not set(setL).intersection(setR):
	# 		# 	return False
	# 	return True

	# def isLatin(self, uni):
	# 	return self.checkPairLangsByUnicodes((int('0041',16), uni))
	#
	# def isCyrillic(self, uni):
	# 	return self.checkPairLangsByUnicodes((int('0410',16), uni))
	#
	# def isLatinName(self, font, name):
	# 	lat_a = font.getCharacterMapping()[int('0061',16)][0]
	# 	return self.checkPairLanguageCompatibility( font, (lat_a, name))
	#
	# def isCyrillicName(self, font, name):
	# 	cyr_a = font.getCharacterMapping()[int('0430', 16)][0]
	# 	return self.checkPairLanguageCompatibility(font, (cyr_a, name))


if __name__ == "__main__":

	def generateXML():
		landster = TDLangSet(init = 'TBL')
		print (landster.langdic)
		baselang = dict(latin = '0061',
		                cyrillic = '0430',
		                greek = '0391',
		                arabic = '0627',
		                georgian = '10D0',
		                hebrew = '05D0',
		                armenian = '0531')#, digits = '0030')
		addasChar = False
		ignore = '0021 0028 0029 002B 002C 002D 002E 003A 003B 003D 003F 2013 201C 201D 2019 2014 00AB 00BB 2116 2019 00A1 00BF'.split(' ') #  0030 0031 0032 0033 0034 0035 0036 0037 0038 0039

		patterns = dict(latin = dict( upper = '0048*0048', lower = '006E*006E',
		                              other = '0048*0048', digit = '0030*0030'),
		                cyrillic =  dict( upper = '041D*041D', lower = '043D*043D',
		                                  other = '041D*041D', digit = '0030*0030'),
		                greek = dict( upper = '0397*0397', lower = '03B7*03B7',
		                              other = '0397*0397', digit = '0030*0030'),
		                arabic =  dict( upper = '0627*0627', lower = '0627*0627',
		                                other = '0627*0627', digit = '0661*0661'),
		                georgian = dict( upper = '10B6*10B6', lower = '10D8*10D8',
		                                 other = '10B6*10B6', digit = '0030*0030'),
		                hebrew = dict( upper = '05DD*05DD', lower = '05DD*05DD',
		                               other = '05DD*05DD', digit = '0030*0030'),
		                armenian = dict( upper = '0548*0548', lower = '0578*0578',
		                                 other = '0548*0548', digit = '0030*0030'),
		                # digits = dict(upper = '0030*0030', lower = '0030*0030', unk = '0030*0030'),
		                )

		libpath = os.path.join(sys.path[0],'langset')
		print (' '.join( [ chr(int(i,16)) for i in ignore] ))
		for base, key in baselang.items():
			print('*' * 40)
			directory = os.path.join(libpath,base)
			if not os.path.exists(directory):
				os.makedirs(directory)
			print (directory)
			for name, cont in landster.langdic.items():
				if key in cont:
					setl = []
					upper = []
					lower = []
					other = []
					digits = []
					punct = []
					setl.append('enable=on')
					setl.append('base=%s' % base)
					setl.append('keycode=#%s' % key)
					setl.append('name=%s' % name)
					for g in cont:
						uni = chr(int(g,16))

						if addasChar:
							g = (chr(int(g,16)))
						else:
							g = '#%s' % g
						if uni.isupper():
							upper.append(g)
						elif uni.islower():
							lower.append(g)
						elif uni.isdigit():
							digits.append(g)
						elif g not in ignore:
							other.append(g)
						else:
							punct.append(g)

					setl.append('upper=%s' % ' '.join(upper))
					setl.append('lower=%s' % ' '.join(lower))
					setl.append('other=%s' % ' '.join(other))
					setl.append('digits=%s' % ' '.join(digits))
					setl.append('punct=%s' % ' '.join(punct))
					pattern = patterns[base]
					setl.append('patternUpper=#%s' % pattern['upper'].replace('*',' #'))
					setl.append('patternLower=#%s' % pattern['lower'].replace('*',' #'))
					setl.append('patternOther=#%s' % pattern['other'].replace('*',' #'))
					setl.append('patternDigits=#%s' % pattern['digit'].replace('*',' #'))
					setl.append('patternPunct=#%s' % pattern['upper'].replace('*',' #'))

					data = ET.Element('langset')
					for item in setl:
						i = ET.SubElement(data, 'key')
						i.set('name', item.split('=')[0])
						i.text = item.split('=')[1]

					mydata = str(ET.tostring(data, encoding= 'utf-8',short_empty_elements=False),'utf-8')
					mydata = mydata.replace('><key','>\n<key')

					pathfile = os.path.join(directory, '%s.xml' % name)
					f = open(pathfile, 'w')
					f.write(mydata)
					f.close()
					# s = #014E

	# generateXML()
	def readXML():
		landster = TDLangSet()
		for k,v in landster.langdic_reversed.items():
			print (k,v)
		# print (landster.langdic_reversed)
		for k,v in landster.langdic.items():
			print (k,v)
		# print (landster.langdic)

	# generateXML()
	# readXML()
	ignore = '0021 0028 0029 002B 002C 002D 002E 003A 003B 003D 003F 2013 201C 201D 2019 2014 00AB 00BB 2116 2019 00A1 00BF 0030 0031 0032 0033 0034 0035 0036 0037 0038 0039'.split(' ')

	landster = TDLangSet()
	# for k,v in landster.base.items():
	# 	print (k)
	# 	t = ''
	# 	for i in v:
	# 		t += ' %s' % chr(i)
	# 	print (t)

	for k, v in landster.langdic.items():
		t = ''
		print(k)
		for i in v:
			t += ' %s' % chr(i)
		print(t)
	print (landster.base['cyrillic'])
	# print (landster.base_reversed)


		# for (_k,_v) in landster.base.items():
		#
		# 	if k != _k:
		# 		inter = set(v).intersection(_v)
		# 		if inter:
		# 			print (k,_k)
		# 			for l in inter:
		# 				if "%04X" % l not in ignore:
		# 					print (chr(l), l, "#%04X" % l, landster.langdic_reversed[l])

	# print (landster.basicPatternNames)
	# landster.setupPatternsForFonts(AllFonts())
	# landster.setupPatternsForFonts(AllFonts())
	# print (landster.basicPatternNames)
	# print(landster.wrapGlyphToPattern(CurrentFont(), 'Lambda'))
	# print (landster.libPatterns)
	# print (landster.pattern)
	# print (landster.checkPairLangsByUnicodes((int('0046',16),int('005A',16))))
	# print (landster.checkPairLangsByUnicodes((int('0419',16),int('0058',16))))

