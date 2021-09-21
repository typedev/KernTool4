# -*- coding: utf-8 -*-

keysMap = {
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

	27: '-',
	24: '+',

	10: 'section',
	50: 'tilda',
	33: 'bracketleft',
	30: 'bracketright',
	41: ';',
	39: 'quotesingle',
	42: 'backslash',
	43: ',',
	47: '.',
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
	69: '+',
	78: '-',
	71: 'delete',
	81: '=',
	75: '/',
	67: '*',
	65: '.',
	121: 'pagedown',
	116: 'pageup',
	115: 'forwardup',
	119: 'backdown',
	117: 'forwarddel'
    }


def decodeModifiers (modifier):
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
	result = []
	bincode = '{:032b}'.format(modifier)
	if bincode[11] == '1': result.append('Cmd')
	if bincode[12] == '1': result.append('Alt')
	if bincode[13] == '1': result.append('Ctrl')
	if bincode[14] == '1': result.append('Shift')
	if bincode[15] == '1': result.append('Caps')
	return '+'.join(result)


def decodeCanvasKeys (keyCode, modifier):
	try:
		key = keysMap[keyCode]
	except:
		key = None

	mod = decodeModifiers(modifier)

	return {'key': key, 'mod': mod}
