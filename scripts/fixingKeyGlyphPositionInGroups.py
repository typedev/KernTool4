
from AppKit import *
from mojo.UI import *
from vanilla import *
from fontParts.world import *
from mojo.UI import CodeEditor

from fontParts.world import *

__doc__ = """
The script finds and corrects the position of the KeyGlyph in the group.

It is believed that in UFO the order of glyphs in a group does not matter, however, to simplify some functions in GroupsControl, it was decided to consider the first glyph in the group as the key one and determine the difference in margins for the remaining glyphs, as well as the language compatibility of glyphs in the group.
Most often, the group name matches the key glyph. If this is not the case, confusion is possible. The script determines the key glyph from the group name and puts it in the first position.
Valid group names:
public.kern1.glyphname
public.kern1.glyphname.suffix1.suffix2...
public.kern1.glyphname_suffix1_suffix2...

***The script works only from GroupsControl***
"""



def fixbaseGlyphInGroup(font, group, baseglyph):
	if baseglyph not in font:
		return False
	newcontent = [baseglyph]

	for gname in font.groups[group]:
		if gname not in newcontent:
			newcontent.append(gname)
	font.groups[group] = tuple(newcontent)
	return True

	
def fixKeyGlyphPosition(parent, fixing = True, truchangeperiod = True):
	font = parent.font
	report = []
	report.append('=' * 40)
	report.append('%s %s' % (font.info.familyName, font.info.styleName))
	report.append('=' * 40)
	errorslist = []
	fixedlist = []
	lostkeyglyphs = []
	for group, content in font.groups.items():
		if 'public.kern' in group:
			tg = '.'.join(group.split('.')[2:])
			target = tg
			if '_' in tg and truchangeperiod:
				target = tg.replace('_','.')
			if content[0] != target:
				if target in content:
					fixedlist.append((group, content))
					if fixing:
						if fixbaseGlyphInGroup(font, group, target):
							pass
						else:
							lostkeyglyphs.append ((target,group))

				else:
					if tg == target: target = ''
					errorslist.append((group, tg, target, content))
	if fixedlist:
		report.append ('*' * 40)
		report.append ('Founded groups:')
		for (g,c) in fixedlist:
			report.append (g)
			report.append ('\tbefore:\t%s' % ' '.join(c))
			report.append ('\tafter:\t%s' % ' '.join(font.groups[g]))
	if errorslist:
		report.append('*' * 40)
		report.append ('Questionable groups (not fixed):')
		for item in errorslist:
			group, tg, target, content = item
			report.append (group)
			report.append ('\tnot found:\t%s %s' % (tg, target))
			report.append ('\tcontent:\t%s' % ' '.join(content))
	if lostkeyglyphs:
		report.append('*' * 40)
		report.append('Lost key glyphs:')
		for item in lostkeyglyphs:
			glyph, group = item
			report.append('\t%s %s' % (glyph, group))
	return report

class TDfixKeyGlyphPosition:
	def __init__(self, parent = None):
		_version = '0.2'
		self.parent = parent

		self.w = FloatingWindow((400, 500),minSize = (300, 300), title = 'fixing KeyGlyph position v%s' % _version)
		self.w.label1 = TextBox('auto', 'Find groups to fix KeyGlyph position')
		self.w.chkbox = CheckBox('auto','and fix them..', value=True)
		self.w.btnRun = Button('auto', title = 'Run', callback = self.btnRunCallback) #,

		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False, lexer = 'text')

		rules = [
			# Horizontal
			"H:|-border-[label1]-border-|",
			"H:|-border-[chkbox]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			"V:|-border-[label1]-space-[chkbox]-space-[btnRun]-border-[textBox]-0-|"
		]
		metrics = {
			"border": 15,
			"space": 8
		}
		self.w.addAutoPosSizeRules(rules, metrics)
		self.w.open()

	def btnRunCallback(self, sender):
		report = fixKeyGlyphPosition(parent = self.parent.hashKernDic)
		self.w.textBox.set('\n'.join(report))
		self.parent.hashKernDic.makeReverseGroupsMapping()
		self.parent.refreshGroupsView()

				
def main(parent = None):
	if not parent: return
	TDfixKeyGlyphPosition(parent = parent)



if __name__ == "__main__":
	main()
	