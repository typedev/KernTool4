


def main (host = None):
	if not host: return
	print ('Start...')
	font = host.font
	hashKernDic = host.hashKernDic
	for groupname, content in font.groups.items():
		if hashKernDic.isKerningGroup(groupname):
			if '_cyr' in groupname:
				newNameGroup = groupname.replace('_cyr', '')
				if newNameGroup not in font.groups:
					hashKernDic.renameGroup(groupname, newNameGroup)
				else:
					print(f'Group {newNameGroup} already exists')

	host.refreshGroupsView()


if __name__ == "__main__":
	main()