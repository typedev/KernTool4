from fontParts.world import *
__doc__ = """
Script for separating groups and kerning based on language. 

Groups with base language (such as Latin, identified by the first glyph in the group) will remain with names like public.kern1.A, and for other languages will be formed classes like public.kern1.A_cyrillic or public.kern1.A_greek with the language name suffix through an underscore '_', kerning will be transferred to all related classes accordingly. As a result of the script, cross-language pairs may appear. To remove them, you can use the [removeCrossLanguagePairs.py] script.
***The script works only from GroupsControl***
"""


def splitGroupByLanguage (parent, groupname, removeCrossLanguagePairs=False):  # font, hashKernDic, langSet,
	self = parent.hashKernDic
	if groupname not in self.font.groups: return
	if not self.langSet: return
	newPairs = []
	content = self.font.groups[groupname]
	if content and self.isKerningGroup(groupname):
		keyglyph = content[0]
		basedic = {}
		for glyphname in content:
			if not self.langSet.checkPairBaseScriptCompatibility(self.font, (keyglyph, glyphname)):
				baseScripts = self.langSet.getBaseScriptByGlyphName(self.font, glyphname)
				if baseScripts:
					for baseScript in baseScripts:
						# print((keyglyph, glyphname), 'not compatible', baseScript)
						if baseScript not in basedic:
							basedic[baseScript] = [glyphname]
						else:
							basedic[baseScript].append(glyphname)
				else:
					baseScript = 'unknown'
					print((keyglyph, glyphname), 'not compatible, cant recognize base scripts. glyph will be moved to _unknown group')
					if baseScript not in basedic:
						basedic[baseScript] = [glyphname]
					else:
						basedic[baseScript].append(glyphname)
		for baseScript, glyphslist in basedic.items():
			newGroupName = '%s_%s' % (groupname, baseScript)  # glyphslist[0] groupprefix, keyglyph,
			# print('this glyphs will be groupped to %s group' % newGroupName)
			# print(glyphslist)
			(_newPairs, _dp) = self.removeGlyphsFromGroup(groupname, glyphslist)
			for pair in _newPairs:
				if pair not in newPairs:
					newPairs.append(pair)
			# newPairs.extend(_newPairs)
			(_sk, _newPairs, _dp) = self.addGlyphsToGroup(newGroupName, glyphslist)
			for pair in _newPairs:
				if pair not in newPairs:
					newPairs.append(pair)
			# newPairs.extend(_newPairs)

			# if removeCrossLanguagePairs:
			# 	pairs2remove = []
			# 	for pair in newPairs:
			# 		if pair in self.font.kerning:
			# 			if not self.checkPairLanguageCompatibilityGroupped(pair, level = 1):
			# 				pairs2remove.append(pair)
			#
			# 		for pair in pairs2remove:
			# 			self.font.kerning.remove(pair)
			# 			if pair in newPairs:
			# 				newPairs.remove(pair)
		self.makeReverseGroupsMapping()
	return newPairs

# def removeCrossLanguagePairs(parent):
# 	self = parent.hashKernDic
# 	pairs2remove = []
# 	for pair in self.font.kerning:
# 		if not self.checkPairLanguageCompatibilityGroupped(pair, level = 1):
# 			pairs2remove.append(pair)
# 	for pair in pairs2remove:
# 		self.font.kerning.remove(pair)
# 	return pairs2remove

def main (parent = None):
	if not parent: return
	print ('Start splitting groups by language')
	for groupname in parent.font.groups:
		splitGroupByLanguage(parent, groupname = groupname)
	# print('Removing Cross-language pairs')
	# removeCrossLanguagePairs(parent)
	parent.refreshGroupsView()


if __name__ == "__main__":
	main()
