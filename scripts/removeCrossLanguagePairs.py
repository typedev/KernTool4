from fontParts.world import *

__doc__ = """
The script removes cross-language pairs.

Pairs are checked for the first level of compatibility - Latin/Cyrillic, Latin/Greek, Georgian/Armenian, etc.
It is also possible to check and delete pairs according to the second level of compatibility, pairs within the same script - for example, in Latin: French / German, in Cyrillic: Abkhaz / Chuvash. But this is rarely applied in practice.
***The script works only from GroupsControl***
"""
def removeCrossLanguagePairs (parent):
	self = parent.hashKernDic
	pairs2remove = []
	for pair in self.font.kerning:
		if not self.checkPairLanguageCompatibilityGroupped(pair, level = 1):
			pairs2remove.append(pair)
	for pair in pairs2remove:
		self.font.kerning.remove(pair)
	return pairs2remove


def main (parent = None):
	if not parent: return
	print('Removing Cross-language pairs')
	removeCrossLanguagePairs(parent)


if __name__ == "__main__":
	main()
