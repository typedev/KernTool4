from fontParts.world import *



updateKerning = False
updateGroups = True

divider = '_'
SIDE_1 = 'L' # left side
SIDE_2 = 'R' # right side
sfxLang = ['BGR', 'SRB', 'TRK', 'NLD']

def placeLigaIntoGroups(host, glyphname, divider):
	leftBaseName = [glyphname.split(divider)[0]]
	rightBaseName = [glyphname.split(divider)[-1]]
	sfx = None
	if '.' in glyphname:
		sfx = glyphname.split('.')[-1]
	if sfx and sfx not in sfxLang:
		print('skipped: %s' % glyphname)
		return
	elif sfx:
		leftBaseName.append( f'{leftBaseName[0]}.{sfx}' )
		rightBaseName.append(rightBaseName[0].replace(f'.{sfx}', ''))
	# else:
	
	
	print(glyphname)
	print(leftBaseName)
	print(rightBaseName)
	for rbn in rightBaseName:
		targetLeftGroup = host.hashKernDic.getGroupNameByGlyph(rbn, side = SIDE_1)
		if targetLeftGroup and host.hashKernDic.isKerningGroup(targetLeftGroup):
			print('GL:', glyphname, rbn, 'founded in group:', targetLeftGroup)
			if updateGroups:
				host.hashKernDic.addGlyphsToGroup(targetLeftGroup, [glyphname])
			break
	for lbn in leftBaseName:
		targetRightGroup  = host.hashKernDic.getGroupNameByGlyph(lbn, side = SIDE_2)
		if targetRightGroup and host.hashKernDic.isKerningGroup(targetRightGroup):
			print('GL:', glyphname, lbn, 'founded in group:', targetRightGroup)
			if updateGroups:
				host.hashKernDic.addGlyphsToGroup(targetRightGroup, [glyphname])
			break
	
	
	
	
	
	# for groupname, content in font.groups.items():
	# 	if 'public.kern1' in groupname and rightBaseName in content:
	# 		# 	baseNameSfx = glyph.name.split('.')[0]
	# 		# 	if baseNameSfx in content:
	# 		if glyph.name not in content:
	# 			print ('GL:', glyph.name, rightBaseName, 'founded in group:', groupname)
	# 			font.groups[groupname].append(glyph.name)
	# 	if 'public.kern2' in groupname and leftBaseName in content:
	# 		# 	baseNameSfx = glyph.name.split('.')[0]
	# 		# 	if baseNameSfx in content:
	# 		if glyph.name not in content:
	# 			print ('GR:', glyph.name, leftBaseName, 'founded in group:', groupname)
	# 			font.groups[groupname].append(glyph.name)
				
	# if updateKerning:
	# 	for (l, r), v in host.font.kerning.items():
	# 		if l == rightBaseName:
	# 			print ('KL:', glyphname, rightBaseName, 'founded in pair:', l, r)
	# 			print ('--', l, r, v)
	# 			print ('++', glyphname, r, v)
	# 			# host.font.kerning[(glyphname, r)] = v
	# 			print ('fixed:', host.font.kerning[(glyphname, r)])
	# 		if r == leftBaseName:
	# 			print ('KR:', glyphname, leftBaseName, 'founded in pair:', l, r)
	# 			print ('--', l, r, v)
	# 			print ('++', l, glyphname, v)
	# 			# host.font.kerning[(l, glyphname)] = v
	# 			print ('fixed:', host.font.kerning[(l, glyphname)])



def main (host = None):
	if not host: return
	print ('Start of placing ligatures into groups')
	for glyph in host.font:
		if divider in glyph.name and not glyph.name.startswith(divider):
			print(glyph.name)
			placeLigaIntoGroups(host, glyph.name, divider)
	host.refreshGroupsView()


if __name__ == "__main__":
	main()
