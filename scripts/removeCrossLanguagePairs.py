from fontParts.world import *

__doc__ = """
The script removes cross-language pairs.

Pairs are checked for the first level of compatibility - Latin/Cyrillic, Latin/Greek, Georgian/Armenian, etc.
It is also possible to check and delete pairs according to the second level of compatibility, pairs within the same script - for example, in Latin: French / German, in Cyrillic: Abkhaz / Chuvash. But this is rarely applied in practice.
***The script works only from GroupsControl***
"""
def removeCrossLanguagePairs (parent, level = 1, remove = False):
	self = parent.hashKernDic
	pairs2remove = []
	for pair in self.font.kerning:
		if not self.checkPairLanguageCompatibilityGroupped(pair, level = level):
			pairs2remove.append(pair)
	if remove:
		for pair in pairs2remove:
			self.font.kerning.remove(pair)
	return pairs2remove


def main (parent = None):
	if not parent: return
	self = parent.hashKernDic
	print('Removing Cross-language pairs')
	pairs2remove = removeCrossLanguagePairs(parent)
	for pair in pairs2remove:
		l, r = pair
		lg = self.getKeyGlyphByGroupname(l)
		rg = self.getKeyGlyphByGroupname(r)
		s1, lp, rp, s2 = self.langSet.wrapPairToPattern(self.font, (lg, rg))
		print('/%s/%s/%s/%s' % (s1, lp, rp, s2))


if __name__ == "__main__":
	main()
