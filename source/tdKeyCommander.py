# -*- coding: utf-8 -*-



KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_UP = 'up'
KEY_DOWN = 'down'
KEY_BACKSPACE = 'backspace'
KEY_TAB = 'tab'
KEY_SPACE = 'space'
KEY_ENTER = 'enter'
KEY_ESC = 'esc'

KEY_1 = '1'
KEY_2 = '2'
KEY_3 = '3'
KEY_4 = '4'
KEY_5 = '5'
KEY_6 = '6'
KEY_7 = '7'
KEY_8 = '8'
KEY_9 = '9'
KEY_0 = '0'

KEY_MINUS = 'minus'
KEY_PLUS = 'plus'
KEY_SECTION = 'section'
KEY_TILDA = 'tilda'
KEY_BRACKETLEFT = 'bracketleft'
KEY_BRACKETRIGHT = 'bracketright'
KEY_SEMICOLON = 'semicolon'
KEY_QUOTESINGLE = 'quotesingle'
KEY_BACKSLASH = 'backslash'
KEY_COMMA = 'comma'
KEY_PERIOD = 'period'
KEY_SLASH = 'slash'

KEY_A = 'a'
KEY_B = 'b'
KEY_C = 'c'
KEY_D = 'd'
KEY_E = 'e'
KEY_F = 'f'
KEY_G = 'g'
KEY_H = 'h'
KEY_I = 'i'
KEY_J = 'j'
KEY_K = 'k'
KEY_L = 'l'
KEY_M = 'm'
KEY_N = 'n'
KEY_O = 'o'
KEY_P = 'p'
KEY_Q = 'q'
KEY_R = 'r'
KEY_S = 's'
KEY_T = 't'
KEY_V = 'v'
KEY_U = 'u'
KEY_W = 'w'
KEY_X = 'x'
KEY_Y = 'y'
KEY_Z = 'z'

KEY_DELETE = 'delete'
KEY_EQUAL = 'equal'
KEY_ASTERISK = 'asterisk'
KEY_PAGEDOWN = 'pagedown'
KEY_PAGEUP = 'pageup'
KEY_FORWARDUP = 'forwardup'
KEY_BACKDOWN = 'backdown'
KEY_FORWARDDEL = 'forwarddel'


class TDKeyCommander(object):
	def __init__(self):
		self.keyCommands = {}
		self.keysMap = {
					123: 'left',
					124: 'right',
					126: 'up',
					125: 'down',
					51: 'backspace',
					48: 'tab',
					49: 'space',
					36: 'enter',
					53: 'esc',

					18: '1',
					19: '2',
					20: '3',
					21: '4',
					23: '5',
					22: '6',
					26: '7',
					28: '8',
					25: '9',
					29: '0',

					27: 'minus',
					24: 'plus',

					10: 'section',
					50: 'tilda',
					33: 'bracketleft',
					30: 'bracketright',
					41: 'semicolon',
					39: 'quotesingle',
					42: 'backslash',
					43: 'comma',
					47: 'period',
					44: 'slash',

					0:  'a',
					11: 'b',
					8:  'c',
					2:  'd',
					14: 'e',
					3: 'f',
					5: 'g',
					4: 'h',
					34: 'i',
					38: 'j',
					40: 'k',
					37: 'l',
					46: 'm',
					45: 'n',
					31: 'o',
					35: 'p',
					12: 'q',
					15: 'r',
					1: 's',
					17: 't',
					9:  'v',
					32: 'u',
					13: 'w',
					7:  'x',
					16: 'y',
					6:  'z',

					# NUMPAD
					82: '0',
					83: '1',
					84: '2',
					85: '3',
					86: '4',
					87: '5',
					88: '6',
					89: '7',
					91: '8',
					92: '9',
					76: 'enter',
					69: 'plus',
					78: 'minus',
					71: 'delete',
					81: 'equal',
					75: 'slash',
					67: 'asterisk',
					65: 'period',
					121: 'pagedown',
					116: 'pageup',
					115: 'forwardup',
					119: 'backdown',
					117: 'forwarddel'
				    }

	def registerKeyCommand(self, key,
	                       alt = False,
	                       shift = False,
	                       cmd = False,
	                       ctrl = False,
	                       caps = False,
	                       callback = None, callbackValue = None):
		command = (key, alt, shift, cmd, ctrl, caps) # callback, callbackValue)
		if command not in self.keyCommands:
			self.keyCommands[command] = (callback, callbackValue)

	def registerSerialKeyCommands(self, keys,
	                              alt=False,
	                              shift=False,
	                              cmd=False,
	                              ctrl=False,
	                              caps=False,
	                              callback=None	):
		for key in keys:
			self.registerKeyCommand(key, alt, shift, cmd, ctrl, caps, callback = callback, callbackValue = key)


	def checkCommand(self, sender, event):
		keypress = self.decodeCanvasKeys(event.keyCode(), event.modifierFlags())
		key = keypress['key']
		(alt, shift, cmd, ctrl, caps) = keypress['mod']

		if (key, alt, shift, cmd, ctrl, caps) in self.keyCommands:
			(callback, callbackValue) = self.keyCommands[(key, alt, shift, cmd, ctrl, caps)]
			if callback:
				callback(sender, callbackValue)

	def decodeModifiers (self, modifier):
		"""
		{:032b}
		0 0 0 0 0 0 0 0 0 0 0 1   1   1   1   1   0 0 0 0 0 0 0 1 0 0 1 0 1 0 1 1
		0                     11  12  13  14  15                                31
		cmd  00000000000100000000000100001000 b11
		alt  00000000000010000000000100100000 b12
		ctrl 00000000000001000000000100000001 b13
		shft 00000000000000100000000100000010 b14
		caps 00000000000000010000000100000000 b15
		"""
		bincode = '{:032b}'.format(modifier)

		alt = False
		shift = False
		cmd = False
		ctrl = False
		caps = False

		if bincode[11] == '1': cmd = True #result.append('Cmd')
		if bincode[12] == '1': alt = True #result.append('Alt')
		if bincode[13] == '1': ctrl = True #result.append('Ctrl')
		if bincode[14] == '1': shift = True #result.append('Shift')
		if bincode[15] == '1': caps = True #result.append('Caps')
		return (alt, shift, cmd, ctrl, caps)#'+'.join(result)

	def decodeCanvasKeys (self, keyCode, modifier):
		try:
			key = self.keysMap[keyCode]
		except:
			key = None

		mod = self.decodeModifiers(modifier)
		return {'key': key, 'mod': mod}

# for k, v in keysMap.items():
# 	# print (k,v)
# 	print ('KEY_%s = \'%s\'' % (v.upper(), v ))