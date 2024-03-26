import os
from fontParts.world import *
import mojo
import ezui
from tdLibEssentials import  uniqueName

class TDFontSelectorDialogWindow(ezui.WindowController):
	def build (self, parentWindow, callback=None,
	           fontListSelected=None, scales = None, designSpace = None, showScales = True):
		self.fontListSelected = fontListSelected
		self.scales = scales
		self.callback = callback
		self.dsList = ['']
		self.currentDS = designSpace
		self.showScales = showScales
		content = """
			= VerticalStack
			* Box @box
			> = HorizontalStack
			>> Work on:
			>> (All opened fonts...) @designSpacesButton
	        |----------------------------------------------------|
            | On/off | UFO | Family | Style | Scale kerning | ID | @complexTable
            |--------|-----|--------|-------|---------------|----|
            | []     |     |        |       | 1             |    |
            |----------------------------------------------------|
            > Sort selected fonts:
            > (Up) @upButton
	        > (Down) @downButton
	        =---=
	        (Cancel) @cancelButton
	        (Apply)  @applyButton
	        
	        """

		complexTableItems = []
		descriptionData = dict(
			complexTable = dict(
				width = 'auto',
				height = 'auto',
				items = complexTableItems,
				# allowsMultipleSelection = False,
				allowsSorting = True,
				columnDescriptions = [
					dict(
						identifier = "Select",
						title = "On / Off",
						width = 50,
						editable = True,
						cellDescription = dict(
							cellType = 'Checkbox',
						),
					),
					dict(
						identifier = "UFO",
						title = "UFO file",
						width = 200,
						minWidth = 200,
						maxWidth = 500,
						editable = False
					),
					dict(
						identifier = "Family",
						title = "Family",
						width = 120,
						minWidth = 120,
						maxWidth = 300,
						editable = False
					),
					dict(
						identifier = "Style",
						title = "Style",
						width = 120,
						minWidth = 120,
						maxWidth = 300,
						editable = False
					),

				],
			),

			cancelButton = dict(
				keyEquivalent = chr(27)
			), # call button on esc keydown
			designSpacesButton =dict(
                items=[ ],
            )
		)

		if self.showScales:
			descriptionData['complexTable']['columnDescriptions'].append(
				dict(
					identifier = "Scale",
					title = "Scale",
					width = 80,
					editable = True,
					cellDescription = dict(
						valueType = "float"
					),
				)
			)
		descriptionData['complexTable']['columnDescriptions'].append(
			dict(
				identifier = "ID",
				title = "ID",
				width = 0,
				editable = False
			),
		)

		self.w = ezui.EZSheet(
			content = content,
			size = (700,400),
			minSize = (700,400),
			descriptionData = descriptionData,
			parent = parentWindow,
			controller = self
		)

	def started (self):
		self.fontList = {}
		listitems = []
		if not self.fontListSelected:
			listitems, self.fontList = self.getAllOpenedFonts()

		else:
			idx = 0
			for font in self.fontListSelected:
				scale = 1.0
				if self.scales and font in self.scales:
					scale = self.scales[font]
				self.appendItem2ListItems(listItems = listitems, font = font, select = True, scale = scale, idx = idx)
				self.fontList[idx] = font
				idx += 1
			for font in AllFonts():
				if font not in self.fontListSelected:
					self.appendItem2ListItems(listItems = listitems, font = font, select = False, scale = 1.0, idx = idx)
					self.fontList[idx] = font
					idx += 1
		self.setFontsTable(listitems)

		dsselector = self.w.getItem('designSpacesButton')
		dslist = ['All opened fonts']
		try:
			import designspaceEditor
			for ds in AllDesignspaces():
				dslist.append(os.path.basename(ds.path))
				self.dsList.append(ds)
		except ModuleNotFoundError:
			print("module 'designspaceEditor' is not installed")

		dsselector.setItems(dslist)
		if self.currentDS:
			if os.path.basename(self.currentDS.path) in dslist:
				dsselector.setItem(os.path.basename(self.currentDS.path))

		self.w.open()

	def appendItem2ListItems(self, listItems, font, select = True, scale = None, idx = 0):
		if self.showScales:
			if 'com.typedev.KernTool.scaleKerningAndMargins' in font.lib.keys():
				scale = float(font.lib['com.typedev.KernTool.scaleKerningAndMargins'])
			listItems.append({'UFO': self.getUFOfileName(font),  # font.path.split('/')[-1],
			                  'Family': '%s' % font.info.familyName,
			                  'Style': '%s' % font.info.styleName,
			                  'Select': select,
			                  'Scale': scale,
			                  'ID': idx})
		else:
			listItems.append({'UFO': self.getUFOfileName(font),  # font.path.split('/')[-1],
			                  'Family': '%s' % font.info.familyName,
			                  'Style': '%s' % font.info.styleName,
			                  'Select': select,
			                  # 'Scale': scale,
			                  'ID': idx})

	def getUFOfileName (self, font):
		if font.path:
			return os.path.basename(font.path)
		else:
			return ('-- this is not a UFO file --')


	def resortSelectedFonts(self, order):
		table = self.w.getItem('complexTable') # .getItem("box")
		listitems = table.get()
		selectedIndexes = table.getSelectedIndexes() #[0]
		keepSelections = []
		if order == 'down':
			for selectedIndex in reversed(selectedIndexes):
				if selectedIndex < len(listitems):
					listitems.insert(selectedIndex + 1, listitems.pop(selectedIndex))
					keepSelections.append( selectedIndex + 1 )
		if order == 'up':
			for selectedIndex in selectedIndexes:
				if selectedIndex > 0:
					listitems.insert(selectedIndex - 1, listitems.pop(selectedIndex))
					keepSelections.append( selectedIndex - 1 )
		self.setFontsTable(listitems)
		if keepSelections:
			for idx in keepSelections:
				if idx < 0 or idx > len(listitems)-1:
					keepSelections.remove(idx)
			table.setSelectedIndexes(keepSelections)


	def setFontsTable(self, fontslist):
		table = self.w.getItem('complexTable') # .getItem("box")
		table.set([])
		for ufoitem in fontslist:
			if self.showScales:
				item = table.makeItem(
					Select = ufoitem['Select'],
					UFO = ufoitem['UFO'],
					Family = ufoitem['Family'],
					Style = ufoitem['Style'],
					Scale = float(ufoitem['Scale']),
					ID = ufoitem['ID']
				)
			else:
				item = table.makeItem(
					Select = ufoitem['Select'],
					UFO = ufoitem['UFO'],
					Family = ufoitem['Family'],
					Style = ufoitem['Style'],
					# Scale = float(ufoitem['Scale']),
					ID = ufoitem['ID']
				)
			table.appendItems([item])


	def getAllOpenedFonts(self):
		listitems = []
		fontlist = {}
		for idx, font in enumerate(AllFonts()):
			self.appendItem2ListItems(listItems = listitems, font = font, select = True, scale = 1.0, idx = idx)
			fontlist[idx] = font
		return listitems, fontlist


	def upButtonCallback(self, sender):
		self.resortSelectedFonts(order = 'up')

	def downButtonCallback(self, sender):
		self.resortSelectedFonts(order = 'down')

	def cancelButtonCallback (self, sender):
		self.w.close()


	def designSpacesButtonCallback(self, sender):
		selection = sender.get()
		if selection == 0:
			listitems, self.fontList = self.getAllOpenedFonts()
			self.setFontsTable(listitems)
		else:
			if not self.dsList: return
			self.currentDS = self.dsList[selection]
			idx = 0
			listitems = []
			self.fontList = {}
			for source in self.currentDS.sources:
				font = OpenFont(source.path)
				self.appendItem2ListItems(listItems = listitems, font = font, select = True, scale = 1.0, idx = idx)
				self.fontList[idx] = font
				idx +=1
			self.setFontsTable(listitems)


	def applyButtonCallback (self, sender):
		fontlist = []
		scales = {}
		table = self.w.getItem('complexTable').get() # .getItem("box")
		for item in table:
			if item['Select']:
				font = self.fontList[ item['ID'] ]
				fontlist.append( font )
				# scale = item['Scale'] # str(item['Scale']).replace(',','.')
				if self.showScales:
					scales[ font ] = float( item['Scale'] )
					font.lib['com.typedev.KernTool.scaleKerningAndMargins'] = str(item['Scale'])
		if self.callback:
			self.callback({'selectedFonts': fontlist, 'scales': scales, 'ds': self.currentDS})
		self.w.close()

