


def main (host = None):
	if not host: return
	print ('Start...')
	font = host.font
	hashKernDic = host.hashKernDic
	for groupname, content in font.groups.items():
		if hashKernDic.isKerningGroup(groupname):
			if hashKernDic.isLeftSideGroup(groupname):
				newNameGroup = 'public.kern1.%s' % hashKernDic.getKeyGlyphByGroupname(groupname)
				hashKernDic.renameGroup(groupname, newNameGroup)
			else:
				newNameGroup = 'public.kern2.%s' % hashKernDic.getKeyGlyphByGroupname(groupname)
				hashKernDic.renameGroup(groupname, newNameGroup)
	host.refreshGroupsView()


if __name__ == "__main__":
	main()