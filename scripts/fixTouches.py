from mojo.events import postEvent

__doc__ = """
The script checks the list of pairs for touching glyphs and moves such pairs to a safe distance, creating exceptions if necessary.
*** Works only in KernTool, and only if one font is loaded. ***
"""


def getFontID (font=None):
	if font:
		fontID = {}
		fontID['fileName'] = font.fileName
		fontID['familyName'] = font.info.familyName
		fontID['styleName'] = font.info.styleName
		# print 'getfontid:', fontID
		return fontID
	return None

def autoFixKertTouches(host):
    fonts = host.fontList
    if len(fonts) != 1: 
        print('Please load only one font.')
        return
    font = fonts[0]
    # pairs = font.kerning.keys()
    line = ''
    ppl = 6
    pairscount = 0
    cl = None
    cr = None
    pairs = []
    for (l, r), value in font.kerning.items():

        lgroup = [l]
        rgroup = [r]
        if l.startswith('public.kern1'):
            lgroup = font.groups[l]

        if r.startswith('public.kern2'):
            rgroup = font.groups[r]

        for side1glyph in lgroup:
            for side2glyph in rgroup:
                if side1glyph in font and side2glyph in font:
                    pairs.append((side1glyph, side2glyph))

    
    report, pairs2check = host.spaceControl.kernControl.checkKernTouches(font, pairs)
    
    print('\n'.join(report))
    # print(pairs2check)
    for (l,r) in pairs2check:
        p1, lw, rw, p2 = list(host.langSet.wrapPairToPattern(font, (l, r)))
        p1 = '/%s' % p1
        p2 = '/%s' % p2
        line += '%s/%s/%s%s' % (p1, lw, rw, p2)
        pairscount += 1
        if ppl and pairscount == ppl:
            line += '\\n'
            pairscount = 0
            
    postEvent('typedev.KernTool.observerSetText',
		          glyphsLine = line,
		          glyphsready = True,
		          targetpair = (cl, cr),
		          fontID = getFontID(font),
		          # observerID = self.observerID)
		          )        
        




def main (host = None):
    if not host: return
    autoFixKertTouches(host = host) 