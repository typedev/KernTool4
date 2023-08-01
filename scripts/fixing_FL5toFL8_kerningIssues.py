from fontParts.world import *





def main (parent = None):
	if not parent: return
	print ('Start...')
	font = parent.font
	hashKernDic = parent.hashKernDic
	groups2kill = []
	for groupname, content in font.groups.items():
		if groupname.startswith('_'):
			if content and content[0] == groupname.replace('_',''):

				keyGlyph = content[0]
				groupname1 = '%s.%s' % ('public.kern1', groupname)
				print('+' * 30)
				print('Making group', groupname1, content)
				report = hashKernDic.addGlyphsToGroup(groupname1, content)
				# print(report)
				groupname2 = '%s.%s' % ('public.kern2', groupname)
				print('+' * 30)
				print('Making group', groupname2, content)
				report = hashKernDic.addGlyphsToGroup(groupname2, content)
				# print(report)
				groups2kill.append(groupname)
			else:
				print('Group not defined:', groupname, '=', content)
	for groupname in groups2kill:
		del font.groups[groupname]
	parent.refreshGroupsView()


if __name__ == "__main__":
	main()
