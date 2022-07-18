
# from AppKit import *
from vanilla import *
from mojo.UI import CodeEditor
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles
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

def markKeyGlyph(content, keyglyph):
	result = []
	for g in content:
		if g == keyglyph:
			result.append('"%s"' % g)
		else:
			result.append(g)
	return result
	
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
					if fixing:
						if fixbaseGlyphInGroup(font, group, target):
							fixedlist.append((group, content, font.groups[group], target))
						else:
							lostkeyglyphs.append ((target,group))
					else:
						fixedlist.append((group, content, font.groups[group], target))

				else:
					if tg == target: target = ''
					errorslist.append((group, tg, target, content))

	if errorslist:
		report.append('*' * 40)
		report.append ('Questionable groups (cannot be fixed due to name mismatch):')
		for item in errorslist:
			group, tg, target, content = item
			report.append ('@ %s' %group)
			report.append ('- %s %s' % (tg, target))
			report.append ('content:\t%s' % ' '.join(content))

	if lostkeyglyphs:
		report.append('*' * 40)
		report.append('Lost key glyphs:')
		for item in lostkeyglyphs:
			glyph, group = item
			report.append('- %s %s' % (glyph, group))

	if fixedlist:
		report.append ('*' * 40)
		report.append ('Founded groups:')
		for (g, c, newc, t) in fixedlist:
			report.append ('@ %s' % g)
			if fixing:
				report.append ('before:\t%s' % ' '.join(markKeyGlyph(c,t)))
				report.append ('after:\t%s' % ' '.join(markKeyGlyph(newc,t)))
			else:
				report.append ('content:\t%s' % ' '.join(markKeyGlyph(newc,t)))

	report.append('\n')
	return report


class BaseLexerFKGPIG(RegexLexer):
	tokens = {
        'root': [
            (r' .*\n', Name),
            (r'(before:.*)(".*")(.*)\n', bygroups(Error, Text, Error)),
	        (r'(after:.*)(".*")(.*)\n', bygroups(String, Text, String)),
	        (r'(content:)(.*)(".*")(.*)\n', bygroups(Keyword, String, Text, String)),
	        (r'(content:)(.*)\n', bygroups(Keyword, Text)),
	        (r'-.*\n', Error),
            (r'@.*\n', Generic.Subheading),
            (r'\*.*\n', Comment),
            (r'=.*\n', Keyword),
	        (r'\t.*', Generic.Emph),
            (r'.*\n', Text),
        ],
    }

class TDfixKeyGlyphPosition:
	def __init__(self, parent = None):
		_version = '0.3'
		self.parent = parent
		# self.styles = [ dict( title = style, callback = self.changeStyleCallback ) for style in list(get_all_styles())]
		self.w = FloatingWindow((600, 400),minSize = (300, 300), title = 'fixing KeyGlyph position v%s' % _version)
		self.w.label1 = TextBox('auto', 'Find groups to fix KeyGlyph position')
		self.w.chkbox = CheckBox('auto','and fix them..', value=False)
		self.w.btnRun = Button('auto', title = 'Run', callback = self.btnRunCallback) #,
		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False)
		# self.w.btnStyle = ActionButton('auto', items = self.styles, sizeStyle = 'mini') #items = self.styles
		self.w.flex1 = Group('auto')
		self.w.textBox.setLexer(BaseLexerFKGPIG())
		self.w.textBox.setHighlightStyle(get_style_by_name('material'))  # solarized-light

		rules = [
			# Horizontal
			"H:|-border-[label1]-border-|",
			"H:|-border-[chkbox]-border-|",
			"H:|-border-[btnRun]-border-|",
			"H:|-0-[textBox]-0-|",
			# "H:|-border-[flex1]-[btnStyle(30)]-border-|",
			# Vertical
			"V:|-border-[label1]-space-[chkbox]-space-[btnRun]-space-[textBox]-0-|",
			# "V:|-border-[label1]-space-[chkbox]-space-[btnRun]-space-[textBox]-3-[flex1]-5-|",
			# "V:|-border-[label1]-space-[chkbox]-space-[btnRun]-space-[textBox]-3-[btnStyle]-5-|",
		]
		metrics = {
			"border": 15,
			"space": 8
		}
		self.w.addAutoPosSizeRules(rules, metrics)
		self.w.open()

	def btnRunCallback(self, sender):
		report = fixKeyGlyphPosition(parent = self.parent.hashKernDic, fixing = self.w.chkbox.get())
		self.w.textBox.set('\n'.join(report))
		self.parent.hashKernDic.makeReverseGroupsMapping()
		self.parent.refreshGroupsView()

	# def changeStyleCallback(self, sender):
	# 	print (sender.title())
	# 	self.w.textBox.setHighlightStyle(get_style_by_name(sender.title()))

				
def main(parent = None):
	if not parent: return
	TDfixKeyGlyphPosition(parent = parent)



if __name__ == "__main__":
	main()
	