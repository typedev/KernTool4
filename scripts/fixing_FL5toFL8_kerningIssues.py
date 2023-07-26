from fontParts.world import *





def main (parent = None):
	if not parent: return
	print ('Start...')
	font = parent.font
	hashKernDic = parent.hashKernDic
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

			else:
				print('Group not defined:', groupname, '=', content)
	parent.refreshGroupsView()


if __name__ == "__main__":
	main()
