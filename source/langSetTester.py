from tdLangSet import *

LS = TDLangSet()
ignorechr = '! ( ) + , - . : ; = ? – “ ” ¡ ¿ — « » №'.split(' ')
# print (LS.langdic_structured)

for langname in sorted(LS.langdic_structured):
	if 65 in LS.langdic_structured[langname]['upper']:
		print('###', langname)

		for k,v in LS.langdic_structured[langname].items():
			if v and k != 'digits':

				t = ''
				for u in v:
					if chr(u) not in ignorechr:
						if ('%04X' % u)[0] == 'F':
							# print ('%04X' % u, u, chr(u))
							t += '!%04X ' % u
						else:
							t += '%s ' % (chr(u))
				if t:
					print ('%s:' % k, t)
					# print (t)
		print('\n')



# print(LS.base)