import vanilla
import merz
from fontParts import *
import random
from AppKit import *
from mojo.pens import DecomposePointPen
from fontParts.world import *
import math


class TDGlyphsMatrix(object):

	def __init__(self, font = None, width = 3000):
		self.matrix = []
		self.font = font
		self.width = width
		self.glyphs = []
		self.insertVirtual = False

	def setFont(self, font = None):
		self.font = font

	def setWidth(self, width = 3000):
		self.width = width

	def setGlyphs(self, glyphs, insertVirtual = False):
		self.glyphs = glyphs
		self.insertVirtual = insertVirtual
		self.buildMatrix()

	def getGlyphsLine(self, idx = 0):
		return self.matrix[idx]

	def get(self):
		return self.matrix

	def buildMatrix(self):
		widthline = 0
		widthkeep = 2000
		glyphline = []
		self.matrix = []
		for idx, glyphname in enumerate(self.glyphs):
			if glyphname == '{break}':
				self.matrix.append(glyphline)
				glyphline = []
				widthline = 0
			else:
				glyph = self.font[glyphname]
				width = glyph.width
				widthline += width
				if widthline + widthkeep < self.width:
					glyphline.append(glyphname)
				else:
					self.matrix.append(glyphline)
					glyphline = []
					widthline = 0

					if self.insertVirtual:
						_glyph = self.font[self.glyphs[idx-1]]
						_width = _glyph.width
						glyphline.append(_glyph.name)
						widthline += _width

						# glyph = self.font[glyphname]
						# width = glyph.width
						# widthline += width
						# glyphline.append(glyphname)
					# else:
					glyphline.append(glyphname)
					widthline += width











