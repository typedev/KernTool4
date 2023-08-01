from fontParts.world import *
from tdSpaceControl import *

__doc__ = """
The script collects groups with language suffixes like _cyrillic _greek and so on, will be combined with similar Latin ones.
This script is currently under development. Main problem - a lot of exceptions are thrown.
***The script works only from GroupsControl***
"""


def getExceptionsList (parent):
	self = parent.hashKernDic
	count = 0
	classexception = []
	classexception_ = []
	glyphexception = []
	glyphexception_ = []
	allexception = []
	for (l, r), v in self.font.kerning.items():
		info = getKernPairNotes(self.font, parent.hashKernDic, (l, r))
		note, lp, rp = info
		if note == PAIR_INFO_EXCEPTION or note == PAIR_INFO_ORPHAN:
			if (lp, rp) in self.font.kerning:
				classexception.append((note, l, r, lp, rp, v, self.font.kerning[(lp, rp)]))
				classexception_.append((l, r))
			else:
				glyphexception.append(('*', note, l, r, lp, rp, v, lp, rp))
				glyphexception_.append((l, r))
			allexception.append((l, r))
			count += 1
	return (classexception, classexception_, glyphexception, glyphexception_, allexception)

def combineGroupsByLanguage (parent):
	self = parent.hashKernDic
	# print ('start combining groups')
	if not self.langSet: return
	groupslist = {}
	groups2kill = []
	skipedgroups = []
	langs = ['_%s' % lang for lang in self.langSet.base.keys()]
	# print (langs)
	for group, content in self.font.groups.items():
		if self.isKerningGroup(group):
			for lang in langs:
				if lang in group:
					base = group.replace(lang, '')
					if base in self.font.groups:
						if base not in groupslist:
							groupslist[base] = [group]
						else:
							groupslist[base].append(group)
						groups2kill.append(group)
					else:
						skipedgroups.append(group)
	contentSide1 = []
	contentSide2 = []
	for basegroup, groups2combine in groupslist.items():
		# print('union is possible', basegroup, groups2combine)
		for group in groups2combine:
			content = list(self.font.groups[group])
			self.removeGlyphsFromGroup(group, content)
			self.addGlyphsToGroup(basegroup, content)
			if self.isLeftSideGroup(basegroup):
				contentSide1.extend(content)
			else:
				contentSide2.extend(content)
	# TODO нужно пройтись по глифам в базовой группе и проверить нет для них идентичных по значению пар с глифами из удаленных групп
	for group in groups2kill:
		self.deleteGroup(group)
	self.makeReverseGroupsMapping()
	# print (contentSide1)
	# print (contentSide2)
	# for basegroup in groupslist.keys():
	# 	content = list(self.font.groups[basegroup])
	return groupslist, skipedgroups

# def combineGroupsByLanguageCallback(self, parent):
	# classexceptionA, classexceptionA_, glyphexceptionA, glyphexceptionA_, allexceptionA = self.getExceptionsList()


def main (parent = None):
	if not parent: return

	self = parent.hashKernDic
	combineGroupsByLanguage(parent)
	classexception, classexception_, glyphexception, glyphexception_, allexception = getExceptionsList(parent)

	for item in classexception:
		note, l, r, lp, rp, v, v2 = item
		if v == v2:
			self.font.kerning.remove((l, r))

	parent.refreshGroupsView()


if __name__ == "__main__":
	main()
