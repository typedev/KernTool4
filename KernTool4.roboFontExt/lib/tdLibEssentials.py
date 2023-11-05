import random
import string
# import math
# from mojo.roboFont import *
# from mojo.extensions import *
# from mojo.pens import DecomposePointPen
# from fontParts.world import *
# import platform

def cutUniqName (glyphname):
	if 'uuid' in glyphname:
		last_dot_index = glyphname.rfind('.')
		if last_dot_index != -1:
			return glyphname[:last_dot_index]
	return glyphname

def ran_gen(size, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def getUniqName(cut=32):
	return 'uuid' + ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

def uniqueName(name = None, cut = 32):
	if name:
		return '%s.uuid%s' % (name, ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
	return 'uuid%s' % ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


#
# def getDisplayNameGroup(groupname):
# 	# RF3 style
# 	if not groupname: return
# 	mask1 = ID_GROUP_MASK_1#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_LEFT
# 	mask2 = ID_GROUP_MASK_2#ID_KERNING_GROUP.replace('.kern', '') + ID_GROUP_RIGHT
# 	mask3 = ID_GROUP_MARGINS_MASK_1
# 	mask4 = ID_GROUP_MARGINS_MASK_2
# 	if mask1 in groupname:
# 		return groupname.replace(mask1,'@.') # '@_'
# 	elif mask2 in groupname:
# 		return groupname.replace(mask2,'@.')
# 	elif mask3 in groupname:
# 		return groupname.replace(mask3, '#.')
# 	elif mask4 in groupname:
# 		return groupname.replace(mask4, '#.')
# 	else:
# 		return groupname
#
# COLOR_L_PAIR_SELECTION = (0, 0, .5, .2)
# COLOR_R_PAIR_SELECTION = (0, .5, 0, .2)
#
# COLOR_L_GROUP_ICON = (0, 0, 1, 1)#(.2, 0, .6, 1)
# COLOR_R_GROUP_ICON = (0, 0, 1, 1)#(0, .4, .2, 1)
# COLOR_EXCEPTION_GROUP_ICON = (.8, 0, 0, 1)
#
# COLOR_KERN_VALUE_TEXT_SELECTED = (1, 1, 1, 1)
# COLOR_KERN_VALUE_TEXT = (0, 0, 0, .8)
#
# COLOR_TITLES = (.1,.2,.25,1)#(0.2, 0.2, 0.7, 1)
# COLOR_TITLES_INVERSE = (.5,.6,.65,1)
# COLOR_CURSOR = (.5, 0, .5, 1)
# COLOR_KERN_VALUE_POSITIVE = (0, .6, 0.2, 1)
# COLOR_BACKGROUND = (1, 1, 1, 1) # (1,1,1,1)#
# # if KERNTOOL_UI_DARKMODE_WARMBACKGROUND:
# # 	COLOR_KERN_VALUE_POSITIVE = (0, .5, 0.1, 1)
# # 	COLOR_BACKGROUND = (.75, .73, .7, 1)  # (1,1,1,1)#
#
# COLOR_KERN_VALUE_NEGATIVE = (.8, 0, 0.2, 1)
# COLOR_TOUCHE = (1, 0, 0, 1)
# COLOR_KERN_VALUE_ZERO = (1, .6, 0, 1)
# COLOR_ALPHA_REGULAR = .2
# COLOR_ALPHA_SELECTED = 1
#
# COLOR_EXCEPTION_MARK = (1, 0, 0, 1)
# COLOR_EXCEPTION_MARK_SELECTED = (1, 1, 1, .8)
# COLOR_PAIR_SELECTED = (0, 0, 1, 1)
#
# COLOR_VIRTUAL_GLYPH = (.2, 0, .5, 1)
#
# COLOR_WHITE = (1, 1, 1, 1)
# COLOR_BLACK = (0, 0, 0, 1)
# COLOR_GREY_50 = (0.5, 0.5, 0.5, 1)
# COLOR_GREY_30 = (.65, .65, .65, 1)
# COLOR_GREY_20 = (.8, .8, .8, 1)
# COLOR_GREY_10 = (.9, .9, .9, 1)
# COLOR_GREY_50_A = (0.5, 0.5, 0.5, .5)
# COLOR_GREY_20_A = (.8, .8, .8, .2)
# COLOR_GREY_10_A = (.9, .9, .9, .1)