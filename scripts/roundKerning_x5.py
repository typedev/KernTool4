roundAndKill = True
			
def main (parent = None):
	if not parent: return
	print ('round kerning..')
	font = parent.font

	countrounded = 0
	pairs2kill = []
	print('\n++++++++++++++++++++++++++++++++++++++++')
	print(font.info.familyName, font.info.styleName)
	print('total:\t', len(font.kerning.items()))
	for (l, r), v in font.kerning.items():
		if abs(int(round(v, 0))) < 5:
			v = 0
		v = int(round(int(round(v / 5.0) * 5.0), 0))
		if v != 0:
			countrounded += 1
			if roundAndKill:
				font.kerning[(l, r)] = v
		else:
			pairs2kill.append((l, r))
	if roundAndKill:
		for pair in pairs2kill:
			font.kerning.remove(pair)

	print('checked:\t', countrounded)
	print('removed:\t', len(pairs2kill))
	print('result:\t', len(font.kerning.items()))

	parent.refreshGroupsView()
