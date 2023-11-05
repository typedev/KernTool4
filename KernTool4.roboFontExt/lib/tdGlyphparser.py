# -*- coding: utf-8 -*-

def parserTXT(text = ''):
	context = ''
	datag = []
	templine = 'code: '
	for id, litera in enumerate(text):
		# print id, len(unicode(text, 'utf-8'))
		if litera == '/':
			context = 'start_code'
		if (litera == ' ') or (litera == '\n'):
			if context == 'start_code':
				context = 'end_code'
				datag.append(templine)
				templine = 'code: '
				litera = ''
			elif context == 'end_code':
				context = ''
		if id == len(text)-1:
			if context == 'start_code':
				# context = 'end_code'
				datag.append(templine+text[-1])
				# templine = 'code: '
				break
		if litera!='':
			if context == 'start_code':
				# if litera!=' ':
				templine += litera
			else:
				# if litera!='':
				datag.append(litera)
	result = []
	for a in datag:
		if a.startswith('code: '):
			a = a.replace('code: ','')
			a = a.replace('//','/slash')
			for b in a.split('/'):
				if b!='':
					result.append('code: '+b)
		else:
			result.append(a)
	return result

def findGlyphNameByUnicode (font, uni):
	try:
		return font.getCharacterMapping()[uni][0]
	except:
		# print 'WARNING! %s not found...' % uni
		return '.notdef'

def parseCode(font, tempfont, code, insertInTempFont=True):
	precode = []
	result = []
	selected = font.selection
	if '?' in code:
		lp, rp = code.split('?')
		for sg in selected:
			precode.append(lp+sg+rp)
	else:
		precode.append(code)

	for c in precode:
		if ('+' in c) or ('=' in c):
			# print 'calling code:', c
			if insertInTempFont:
				pass
				# d = buildGlyphs(font,tempfont,c)
				# print 'bulded::: ', d
				# result.append(''.join(d))
			else:
				print ('operation not supported:', c)
		else:
			# print 'simple glyph', c
			if c in font:
				# if insertInTempFont:
				# 	tempfont.insertGlyph(font[c],c)
				result.append(c)
	return result


def translateTextToGlyphs(sourcefont, tempfont, text, insertInTempFont = True):
	result = []
	data = parserTXT(text)
	for s in data:
		if s.startswith('code: '):
			s = s.replace('code: ', '')
			result.extend( parseCode(sourcefont, tempfont, s, insertInTempFont) )
		else:
			if s != '\n':
				n = findGlyphNameByUnicode(sourcefont, ord(s))
				if insertInTempFont:
					tempfont.insertGlyph(sourcefont[n], n)
			else:
				n = s
			if n != '.notdef':
				result.append(n)
	return result

def translateText(font, text):
	return translateTextToGlyphs(sourcefont=font, tempfont=None, text=text, insertInTempFont = False)






