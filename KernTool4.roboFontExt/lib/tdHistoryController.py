import os, sys
from fontParts.world import *
import vanilla
import mojo
from mojo.UI import *
from pygments.lexer import RegexLexer, bygroups
from mojo.subscriber import Subscriber, registerCurrentFontSubscriber, unregisterCurrentFontSubscriber, listRegisteredSubscribers
from vanilla.dialogs import getFile, putFile

from pygments.token import *
from pygments.styles import get_style_by_name, get_all_styles
from tdKernToolEssentials4 import getUniqName, getFontID, isMyFontID




class TDCustomLexer(RegexLexer):
	name = 'GCHistoryLexer'
	aliases = ['GCHistory']
	filenames = ['*.GCHistory']

	tokens = {
		'root': [
            (r'\badd\b', String),
            (r'\bremove\b', Error),
            (r'\bdelete\b', Keyword),
            (r'[KL][+-]\s*', Name.Variable),
            (r'public\S*\s', Name.Builtin),
            (r'\b\w+\b', Name),
            (r'\s+', Text),
        ],
	}


class TDHistoryControllerWindow(Subscriber):
	debug = True

	# fontDidChangeDelay = 0

	def build (self):
		_version = '0.1'
		self.host = None
		self.fontID = None
		self.fontNames = []

		self.w = vanilla.FloatingWindow((500, 600), minSize = (300, 300), title = 'History v%s' % _version)

		self.w.btnStart = vanilla.Button('auto', title = 'On', callback = self.btnStartStopCallback)
		self.w.btnStop = vanilla.Button('auto', title = 'Off', callback = self.btnStartStopCallback)
		self.w.flex1 = vanilla.Group('auto')
		self.w.btnRollBack = vanilla.Button('auto', title = 'Step back', callback = self.btnStartStopCallback)
		self.w.flex2 = vanilla.Group('auto')
		self.w.btnLoad = vanilla.Button('auto', title = 'Apply from file', callback = self.importHistoryCallback)
		self.w.btnSave = vanilla.Button('auto', title = 'Save', callback = self.exportHistoryCallback)
		self.w.flex3 = vanilla.Group('auto')
		self.w.btnReset = vanilla.Button('auto', title = 'Reset', callback = self.btnStartStopCallback)

		self.w.textBox = CodeEditor('auto', text = '', readOnly = True, showLineNumbers = False, checksSpelling = False)
		self.w.textBox.setLexer(TDCustomLexer())
		self.w.textBox.setHighlightStyle(get_style_by_name('material'))

		rules = [
			# Horizontal
			"H:|-border-[btnStart]-space-[btnStop]-[flex1]-[btnRollBack]-[flex2(==flex1)]-[btnLoad]-space-[btnSave]-[flex3(==flex1)]-[btnReset]-border-|",
			"H:|-0-[textBox]-0-|",
			# Vertical
			"V:|-border-[btnStart]-border-[textBox]-0-|",
			"V:|-border-[btnStop]-border-[textBox]-0-|",
			"V:|-border-[flex1]-border-[textBox]-0-|",
			"V:|-border-[btnRollBack]-border-[textBox]-0-|",
			"V:|-border-[flex2]-border-[textBox]-0-|",
			"V:|-border-[btnLoad]-border-[textBox]-0-|",
			"V:|-border-[btnSave]-border-[textBox]-0-|",
			"V:|-border-[flex3]-border-[textBox]-0-|",
			"V:|-border-[btnReset]-border-[textBox]-0-|",
		]
		metrics = {
			"border": 15,
			"space": 3
		}
		self.w.addAutoPosSizeRules(rules, metrics)
		# self.collectFonts()
		# self.w.open()

	def started (self):
		self.w.bind('close', self.windowClose)
		self.w.open()
		# self.showHistory()

	def btnStartStopCallback(self,sender):
		if self.host:
			if sender == self.w.btnStart:
				self.host.hashKernDic.setHistoryResume()
				self.host.w.g2.btnHistory.setTitle('History On')
			elif sender == self.w.btnStop:
				self.host.hashKernDic.setHistoryPause()
				self.host.w.g2.btnHistory.setTitle('History Off')
			elif sender == self.w.btnReset:
				self.host.hashKernDic.clearHistory()
				self.showHistory()
			elif sender == self.w.btnRollBack:
				self.rollBack()
				self.showHistory()
				self.host.refreshGroupsView()

	def getHistoryAsText(self):
		if self.host:
			# print(self.host.hashKernDic.history)
			commands = []
			for item in self.host.hashKernDic.history:
				c, g, n = '', '', ''
				o, l = False, False
				if item[0] == 'delete':
					c = 'delete'
					g = item[1]
					n = ''
					o = item[3]
					l = item[4]
				elif item[0] == 'add':
					c = 'add'
					g = item[1]
					n = ' '.join(item[2])
					o = item[3]
					l = item[4]
				elif item[0] == 'remove':
					c = 'remove'
					g = item[1]
					n = ' '.join(item[2])
					o = item[3]
					l = item[4]
				if o:
					o = '+'  # check kerning
				else:
					o = '-'  # skip kerning
				if l:
					l = '+'  # check language
				else:
					l = '-'  # skip language
				commands.append('%s K%s L%s %s %s' % (c, o, l, g, n))
			return commands

	def exportHistoryCallback (self, sender):
		fn = putFile(messageText = 'Export History to file', title = 'title')
		if fn:
			commands = self.getHistoryAsText()
			f = open(fn, mode = 'w')
			f.write('\n'.join(commands))
			f.close()

	def importHistoryCallback (self, sender):
		fn = getFile(messageText = 'Import History from file', title = 'title')
		if fn and fn[0]:
			f = open(fn[0], mode = 'r')
			for line in f:
				line = line.strip()
				if line and not line.startswith('#'):
					# command = []
					command = line.split(' ')
					# print (command)
					if command[0] == 'add':
						checkKerning = False
						checkLanguage = False
						if command[1] == '+':
							checkKerning = True
						if command[2] == '+':
							checkLanguage = True
						groupname = command[3]
						glyphslist = command[4:]
						self.host.hashKernDic.addGlyphsToGroup(groupname, glyphslist, checkKerning = checkKerning,
						                                  checkLanguageCompatibility = checkLanguage)
					elif command[0] == 'remove':
						checkKerning = False
						checkLanguage = False
						if command[1] == '+':
							checkKerning = True
						if command[2] == '+':
							checkLanguage = True
						groupname = command[3]
						glyphslist = command[4:]
						self.host.hashKernDic.removeGlyphsFromGroup(groupname, glyphslist, checkKerning = checkKerning,
						                                            checkLanguageCompatibility = checkLanguage)
					elif command[0] == 'delete':
						checkKerning = False
						checkLanguage = False
						if command[1] == '+':
							checkKerning = True
						if command[2] == '+':
							checkLanguage = True
						groupname = command[3]
						self.host.hashKernDic.deleteGroup(groupname, checkKerning = checkKerning, checkLanguageCompatibility = checkLanguage)
			f.close()
			self.host.hashKernDic.clearHistory()
			self.host.setFontView(animated = 'left')
			self.host.setGroupsView(animated = 'left')
			self.host.refreshGroupsView()
			# self.w.g1.contentView.setSceneItems(  items = list(self.font.groups[self.selectedGroup]),  animated = 'left')

	def rollBack(self, doubleStep = False):
		if self.host.hashKernDic.history:
			lastCommand = self.host.hashKernDic.history[-1]
			groupname = lastCommand[1]
			glyphslist = lastCommand[2]
			checkKerning = False
			checkLanguage = False
			if lastCommand[3]:
				checkKerning = True
			if lastCommand[4]:
				checkLanguage = True

			if lastCommand[0] == 'add' and not doubleStep:
				self.host.hashKernDic.removeGlyphsFromGroup(groupname, glyphslist, checkKerning = False, checkLanguageCompatibility = False)
				self.host.hashKernDic.history = self.host.hashKernDic.history[:-2]
			elif lastCommand[0] == 'remove':
				self.host.hashKernDic.addGlyphsToGroup(groupname, glyphslist, checkKerning = checkKerning, checkLanguageCompatibility = checkLanguage)
				self.host.hashKernDic.history = self.host.hashKernDic.history[:-2]
			elif lastCommand[0] == 'delete':
				self.host.hashKernDic.history = self.host.hashKernDic.history[:-1]
				self.rollBack(doubleStep = True)


	def showHistory(self):
		commands = self.getHistoryAsText()
		commands.append('\n\n')
		self.w.textBox.set('\n'.join(commands))

	def fontGroupsDidChange(self, info):
		self.showHistory()

	def windowClose (self, sender):
		unregisterCurrentFontSubscriber(self)

def main (host = None):
	if not host: return

	registerCurrentFontSubscriber(TDHistoryControllerWindow)
	for subscontrol in listRegisteredSubscribers():
		if type(subscontrol) == TDHistoryControllerWindow:
			if not subscontrol.host:
				subscontrol.host = host
				subscontrol.showHistory()
				# subscontrol.fontID = getFontID()

# if __name__ == "__main__":
# 	main('Not none')