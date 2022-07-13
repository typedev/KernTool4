
from AppKit import *
from mojo.UI import *
from vanilla import *
from fontParts.world import *
from mojo.UI import CodeEditor

__doc__ = """
Script to check kerning and groups.

Finds and removes lost glyphs in groups, empty groups, lost pairs, pairs with None and Zero value. For pairs with a Zero value, a list will be collected for checking.

***The script works only from GroupsControl***
"""

def clearKernAndGroups(parent,
                       deleteHolesInGroup = True,
                       deleteEmptyGroup = True,
                       deleteLostPairs = True,
                       deleteNoneKern = True,
                       deleteZeroKern = False):
	"""
		deleteHolesInGroup = True  # remove glyphs from groups if they are missing in the font
		deleteEmptyGroup = True  # remove empty groups
		deleteLostPairs = True  # remove pairs if missing glyphs are involved
		deleteNoneKern = True  # remove pairs if their value is undefined
		deleteZeroKern = False  # remove pairs if their value is 0
	"""
	font = parent.font
	report = []
	report.append('=' * 40)
	report.append('%s %s' % (font.info.familyName, font.info.styleName))
	report.append('=' * 40)
	report.append('Investigating for missing glyphs in Groups..')
	totalKernGroup = 0
	emptyKernGroup = 0

	def delGlyphsFromGroup(font, group, glyphlist, checkKerning = False):
		"""
		function to remove glyphs from a group
		"""
		# RF3 style
		if group in font.groups:
			newcontent = []
			for glyphname in font.groups[group]:
				if glyphname not in glyphlist:
					newcontent.append(glyphname)
			font.groups[group] = tuple(newcontent)

	for groupname, content in font.groups.items():
		if 'public.kern' in groupname:
			totalKernGroup += 1
			totalGlyphs = len(content)
			lostGlyphs = 0

			glyphs2kill = []
			for gname in content:
				if gname not in font:
					glyphs2kill.append(gname)

			if glyphs2kill:
				lostGlyphs = len(glyphs2kill)
				report.append('Group %s has %i glyphs' % (groupname, len(content)))
				for gname in glyphs2kill:
					report.append('\t%s not founded in font' % gname)
				if lostGlyphs == totalGlyphs:
					report.append('\t*** The group will be empty')

			if deleteHolesInGroup and glyphs2kill:
				delGlyphsFromGroup(font, groupname, glyphs2kill)
				report.append('\tremoved: %s' % ' '.join(glyphs2kill))

	report.append('*'*40)
	report.append('Investigating for Empty Kern groups..')
	totalKernGroup = 0
	groups2kill = []
	for groupname, content in font.groups.items():
		if 'public.kern' in groupname:
			totalKernGroup += 1
			if len(content) == 0:
				# print ('Empty group founded', groupname)
				groups2kill.append(groupname)
				# if deleteEmptyGroup:
				# 	del font.groups[groupname]
				# 	print ('and killed...')
	if groups2kill:
		report.append('Empty groups found:')
		t = ''
		for g in groups2kill:
			if deleteEmptyGroup:
				del font.groups[g]
				t = 'removed..'
			report.append('\t%s %s' % (g, t))

	report.append ('Total Kern Group: %i' % totalKernGroup)
	report.append ('Empty Kern Group: %i' % len(groups2kill))

	report.append ('*' * 40)
	report.append ('Investigating for Lost Pairs..')
	lostPairs = []
	for (l, r), v in font.kerning.items():
		fl = False
		fr = False
		if l in font.groups:
			fl = True
		elif l in font:
			fl = True
		if r in font.groups:
			fr = True
		elif r in font:
			fr = True
		if fl and fr:
			pass
		else:
			# print ('Not found pair', l, r, v)
			lostPairs.append((l,r))
			# if deleteHolesKern:
			# 	del font.kerning[(l, r)]
	if lostPairs:
		report.append ('Lost Pairs founded:')
		for pair in lostPairs:
			t = ''
			if deleteLostPairs:
				del font.kerning[pair]
				t = 'removed..'
			report.append ('\t%s %s %s' % (pair[0], pair[1], t))

	report.append ('*' * 40)
	report.append ('Investigating for None kerning values..')
	nullPairs = []
	for (l, r), v in font.kerning.items():
		if l and r and v or v == 0: pass
		else:
			nullPairs.append((l,r))
			# print ('Founded None kerning:')
			# print ('\t', l, r, v)
			# if deleteNoneKern:
			# 	del font.kerning[(l, r)]
			# 	print ('\tfixed')
	if nullPairs:
		report.append ('Pairs with None Kerning founded:')
		for pair in nullPairs:
			t = ''
			if deleteNoneKern:
				del font.kerning[pair]
				t = 'removed..'
			report.append ('\t%s %s %s' % (pair[0], pair[1], t))
		report.append ('Total None pairs: %i' % len(nullPairs))

	report.append ('*' * 40)
	report.append ('Investigating for Zero kern values..')
	zeroPairs = []
	zeroPatterns = []
	for (l, r), v in font.kerning.items():
		if l and r and v == 0:
			zeroPairs.append((l,r))
			lg = parent.getKeyGlyphByGroupname(l)
			rg = parent.getKeyGlyphByGroupname(r)
			pattern = parent.langSet.wrapPairToPattern(font, (lg, rg))
			zeroPatterns.append(pattern)
			# print ('Founded Zero kerning:')
			# print ('\t',l, r, v)
			# if deleteZeroKern:
			# 	del font.kerning[(l, r)]
			# 	print ('\tfixed')

	if zeroPairs:

		report.append  ('Pairs with Zero value founded:')
		for pair in zeroPairs:
			t = ''
			if deleteZeroKern:
				del font.kerning[pair]
				t = 'removed..'
			report.append ('\t%s %s %s' % (pair[0], pair[1], t))
		if not deleteZeroKern and zeroPatterns:
			report.append('Patterns to check:')
			pattern2line = 8
			txt = ''
			p2l = 0
			for pattern in zeroPatterns:
				s1, lp, rp, s2 = pattern
				txt += '/%s/%s/%s/%s' % (s1, lp, rp, s2)
				p2l += 1
				if p2l == pattern2line:
					report.append(txt)
					p2l = 0
					txt = ''
			if txt:
				report.append(txt)
		report.append ('Total Zero value pairs: %i' % len(zeroPairs))
	return report



class TDKernAndGroupsCleaner:
	def __init__(self, parent = None):
		_version = '0.2'
		self.parent = parent

		self.w = FloatingWindow((400, 500),minSize = (300, 300), title = 'Groups and Kerning Cleaner v%s' % _version)

		self.w.label1 = TextBox('auto', '􀀺 Find missing glyphs in Groups')
		self.w.label2 = TextBox('auto', '􀀼 Find Empty Groups')
		self.w.label3 = TextBox('auto', '􀀾 Find Lost Pairs')
		self.w.label4 = TextBox('auto', '􀁀 Find Pairs with None value')
		self.w.label5 = TextBox('auto', '􀁂 Find Pairs with Zero value')
		self.w.chkboxDeleteHolesInGroup = CheckBox('auto','and Delete', value=True)
		self.w.chkboxDeleteEmptyGroup = CheckBox('auto','and Delete', value=True)
		self.w.chkboxDeleteLostPairs = CheckBox('auto','and Delete', value=True)
		self.w.chkboxDeleteNoneKern = CheckBox('auto','and Delete', value=True)
		self.w.chkboxDeleteZeroKern = CheckBox('auto','and Delete', value=False)
		self.w.btnRun = Button('auto', title = 'Run', callback = self.btnRunCallback) #,

		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False, lexer = 'text')

		rules = [
			# Horizontal
			"H:|-border-[label1]-border-|",
			"H:|-border-[chkboxDeleteHolesInGroup]-border-|",
			"H:|-border-[label2]-border-|",
			"H:|-border-[chkboxDeleteEmptyGroup]-border-|",
			"H:|-border-[label3]-border-|",
			"H:|-border-[chkboxDeleteLostPairs]-border-|",
			"H:|-border-[label4]-border-|",
			"H:|-border-[chkboxDeleteNoneKern]-border-|",
			"H:|-border-[label5]-border-|",
			"H:|-border-[chkboxDeleteZeroKern]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			"V:|-border-[label1]-space-[chkboxDeleteHolesInGroup]-space-[label2]-space-[chkboxDeleteEmptyGroup]-space-[label3]-space-[chkboxDeleteLostPairs]-space-[label4]-space-[chkboxDeleteNoneKern]-space-[label5]-space-[chkboxDeleteZeroKern]-space-[btnRun]-border-[textBox]-0-|"
		]
		metrics = {
			"border": 15,
			"space": 8
		}
		self.w.addAutoPosSizeRules(rules, metrics)


		# self.w.bind("close", self.windowClose)
		self.w.open()

	def btnRunCallback(self, sender):
		deleteHolesInGroup = self.w.chkboxDeleteHolesInGroup.get()
		deleteEmptyGroup = self.w.chkboxDeleteEmptyGroup.get()
		deleteLostPairs = self.w.chkboxDeleteLostPairs.get()
		deleteNoneKern = self.w.chkboxDeleteNoneKern.get()
		deleteZeroKern = self.w.chkboxDeleteZeroKern.get()
		report = clearKernAndGroups(parent = self.parent.hashKernDic,
		                   deleteHolesInGroup = deleteHolesInGroup,
		                   deleteEmptyGroup = deleteEmptyGroup,
		                   deleteLostPairs = deleteLostPairs,
		                   deleteNoneKern = deleteNoneKern,
		                   deleteZeroKern = deleteZeroKern)
		self.w.textBox.set('\n'.join(report))
		self.parent.hashKernDic.makeReverseGroupsMapping()
		self.parent.refreshGroupsView()


def main(parent = None):
	if not parent: return
	TDKernAndGroupsCleaner(parent = parent)


if __name__ == "__main__":
	main()