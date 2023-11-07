# -*- coding: utf-8 -*-

def parserTXT(text = ''):
	context = ''
	datag = []
	templine = 'code: '
	for id, litera in enumerate(text):
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
				datag.append(templine+text[-1])
				break
		if litera!='':
			if context == 'start_code':
				templine += litera
			else:
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

def parseCode(font, code):
	precode = []
	result = []
	selected = font.selectedGlyphNames
	if '?' in code:
		lp, rp = code.split('?')
		for sg in selected:
			precode.append(lp+sg+rp)
	else:
		precode.append(code)

	for c in precode:
		if ('+' in c) or ('=' in c):
			# print 'calling build glyph:', c
			print ('operation not supported:', c)
		else:
			if c in font:
				result.append(c)
	return result


def translateText(font, text):
	result = []
	data = parserTXT(text)
	for s in data:
		if s.startswith('code: '):
			s = s.replace('code: ', '')
			result.extend( parseCode(font, s) )
		else:
			if s != '\n':
				n = findGlyphNameByUnicode(font, ord(s))
			else:
				n = s
			if n != '.notdef':
				result.append(n)
	return result

if __name__ == "__main__":
	print( translateText(CurrentFont(), 'Hello world!') )





