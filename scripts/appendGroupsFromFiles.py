from vanilla.dialogs import getFile, putFile


def appendGroupsFromFiles (host):
	paths = getFile(messageText = 'Import Groups from file', title = 'title', allowsMultipleSelection = True)
	if paths:
		for filepath in paths:
			# groups2kill = []
			# for groupname, content in host.font.groups.items():
			# 	if groupname.startswith(host.groupPrefix):
			# 		groups2kill.append(groupname)
			# for groupname in groups2kill:
			# 	del host.font.groups[groupname]

			f = open(filepath, mode = 'r')
			host.hashKernDic.setFont(host.font, host.langSet)
			for line in f:
				line = line.strip()
				groupname = line.split('=')[0]
				# print('Making group', groupname)
				if len(line.split('='))==2:
					glist = []
					content = line.split('=')[1].split(',')
					for gname in content:
						if gname in host.font:
							glist.append(gname)
					report = host.hashKernDic.addGlyphsToGroup(groupname,glist)
					# print (report)
			f.close()
			print('Groups imported..')
	host.hashKernDic.setFont(host.font, host.langSet)
	host.setFontView(animated = 'left')
	host.setGroupsView(animated = 'left')
		# self.w.g1.contentView.setSceneItems(  # scene = self.sceneGroupContent,
		# 	items = list(self.font.groups[self.selectedGroup]),  # len(self.kern), #
		# 	animated = 'left'
		# )

def main(host):
	if not host: return
	appendGroupsFromFiles(host)

