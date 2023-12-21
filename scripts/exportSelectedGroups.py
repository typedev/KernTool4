from vanilla.dialogs import getFile, putFile


def exportSelectedGroupsGC(host):
	groups2save = []

	for groupname in host.getSelectedGroupNames():
		if groupname not in groups2save:
			groups2save.append(groupname)

	fn = putFile(messageText = 'Export Groups to file', title = 'title')
	if fn:
		groupsfile = open(fn, mode = 'w')

		txt = ''
		for groupname in sorted(groups2save):
			txt += '%s=%s\n' % (groupname, ','.join(host.font.groups[groupname]))
		groupsfile.write(txt)
		groupsfile.close()
		print('File saved.')



def main (host = None):
	if not host: return
	exportSelectedGroupsGC(host = host)