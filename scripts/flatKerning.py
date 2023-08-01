from fontParts.world import *
# from tdSpaceControl import *




def main (parent = None):
	if not parent: return
	print ('Kerning flattening started..')
	font = parent.font
	hashKernDic = parent.hashKernDic
	for groupname in font.groups:
		if hashKernDic.isKerningGroup(groupname):
			hashKernDic.deleteGroup(groupname)
	parent.refreshGroupsView()


if __name__ == "__main__":
	main()