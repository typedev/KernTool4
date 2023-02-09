from fontParts.world import *


def placeCompositesIntoGroup(parent, groupname):
	font = parent.font
	hashKernDic = parent.hashKernDic
	mapComponents = font.getReverseComponentMapping()
	glyphs2add = []
	for glyphname in font.groups[groupname]:
		if glyphname in font and glyphname in mapComponents:
			components = mapComponents[glyphname]
			for component in components:
				if component not in font.groups[groupname]:
					glyphs2add.append(component)
	if glyphs2add:
		hashKernDic.addGlyphsToGroup(groupname, glyphs2add)


def main (parent = None):
	if not parent: return
	print ('Start placement of composites in groups')
	for groupname in parent.getSelectedGroupNames():
		print(groupname)
		placeCompositesIntoGroup(parent, groupname)
	parent.refreshGroupsView()


if __name__ == "__main__":
	main()
