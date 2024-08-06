# font = CurrentFont()
exglyphs = ['P.circled']
updateGroups = True
makeNewGlyphs = True
SIDE_1 = 'L' # left side
SIDE_2 = 'R' # right side

def getLCglyphName(glyphname):
	sfx = None
	if '.' in glyphname:
		newname = glyphname.split('.')[0].lower()
		sfx = '.'.join(glyphname.split('.')[1:])
		newname += '.%s' % sfx
	else:
		newname = glyphname.lower() #+ ''.join(glyphname.name[1:])
	return newname

def makeNewLC(font, ucglyph, lcglyph, lcunicode = None):
	if lcglyph not in font:
		if makeNewGlyphs:
			sourceGlyph = font[ucglyph]
			newGlyph = font.newGlyph(lcglyph)
			newGlyph.appendComponent(ucglyph)
			newGlyph.width = font[ucglyph].width
			# if newGlyph.unicode:
			newGlyph.unicode = lcunicode
			if lcunicode and lcunicode in sourceGlyph.unicodes:
				ucs = list(sourceGlyph.unicodes)
				ucs.remove(lcunicode)
				sourceGlyph.unicodes = tuple(ucs)
			# font.glyphOrder.append(lcglyph)
		return lcglyph
	else:
		return False
	
# def splitUnicodes
	
def addLCtoGroup(host, ucglyph, lcglyph):
	targetLeftGroup = host.hashKernDic.getGroupNameByGlyph(ucglyph, side = SIDE_1)
	if targetLeftGroup and host.hashKernDic.isKerningGroup(targetLeftGroup):
		print('\tGL:', ucglyph, lcglyph, 'founded in group:', targetLeftGroup)
		if updateGroups:
			host.hashKernDic.addGlyphsToGroup(targetLeftGroup, [lcglyph])
	targetRightGroup = host.hashKernDic.getGroupNameByGlyph(ucglyph, side = SIDE_2)
	if targetRightGroup and host.hashKernDic.isKerningGroup(targetRightGroup):
		print('\tGR:', ucglyph, lcglyph, 'founded in group:', targetRightGroup)
		if updateGroups:
			host.hashKernDic.addGlyphsToGroup(targetRightGroup, [lcglyph])
	

def makeLCfromUC(host):
	alreadyInfont =[]
	font = host.font
	for glyphname in font.glyphOrder:
		glyph = font[glyphname]
		if glyph.unicodes:
			if glyph.name not in exglyphs:
				if len(glyph.unicodes) == 2:
					newname = getLCglyphName(glyph.name) #g.name[0].lower() + ''.join(g.name[1:])
					if newname not in font:
						print(glyph.name, newname, ['%04X' % u for u in glyph.unicodes])
						if makeNewLC(font, glyph.name, newname, glyph.unicodes[1]):
							addLCtoGroup(host, glyph.name, newname)
							
					else:
						print('++++', newname, 'is taken')
						alreadyInfont.append((newname, font[newname].unicode, glyph.unicodes[1]))
				elif len(glyph.unicodes) > 2:
					print('***', glyph.name, ['%04X' % u for u in glyph.unicodes])
					newname = None
					for idx, u in enumerate(glyph.unicodes):
						if idx == 0:
							print('\t', glyph.name, '%04X' % u)
						elif idx == 1:
							newname = getLCglyphName(glyph.name)
							print('\t', newname, '%04X' % u)
							if newname not in font:
								print(glyph.name, newname, ['%04X' % u for u in glyph.unicodes])
								if makeNewLC(font, glyph.name, newname, glyph.unicodes[1]):
									addLCtoGroup(host, glyph.name, newname)
							else:
								print('++++', newname, 'is taken')
								alreadyInfont.append((newname, font[newname].unicode, glyph.unicodes[1]))
						else:
							newname = 'uni%04X' % u
							print('\t', newname, '%04X' % u)
							if newname not in font:
								print(glyph.name, newname, ['%04X' % u for u in glyph.unicodes])
								if makeNewLC(font, glyph.name, newname, u):
									addLCtoGroup(host, glyph.name, newname)
							else:
								print('++++', newname, 'is taken')
								alreadyInfont.append((newname, font[newname].unicode, glyph.unicodes[1]))
						
						
			else:
				print('###', glyph.name, ['%04X' % u for u in glyph.unicodes])
				for idx, u in enumerate(glyph.unicodes):
					if idx == 0:
						print('\t', glyph.name, '%04X' % u)
					else:
						newname = 'uni%04X' % u
						print('\t', newname, '%04X' % u)
						if newname not in font:
							print(glyph.name, newname, ['%04X' % u for u in glyph.unicodes])
							if makeNewLC(font, glyph.name, newname, u):
								addLCtoGroup(host, glyph.name, newname)
						else:
							print('++++', newname, 'is taken')
							alreadyInfont.append((newname, font[newname].unicode, glyph.unicodes[1]))
		else:
			if glyph.name not in exglyphs and glyph.name[0].isupper():
				newname = getLCglyphName(glyph.name)
				if newname not in font:
					print(glyph.name, newname)
					if makeNewLC(font, glyph.name, newname):
						addLCtoGroup(host, glyph.name, newname)
				else:
					print('++++', newname, 'is taken')
					alreadyInfont.append((newname, font[newname].unicode, glyph.unicodes[1]))
	if alreadyInfont:
		print('These glyphs is already in font')
		for item in alreadyInfont:
			print(item)
				



def main (host = None):
	if not host: return
	print ('Start making LC from UC')
	
	makeLCfromUC(host)

	host.refreshGroupsView()


if __name__ == "__main__":
	main()
