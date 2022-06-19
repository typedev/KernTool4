# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------
# Extension build script.
# Created on the basis of a similar Tal Leming script,
# but with the addition of creating Mechanic2 registration files
# ------------------------------------------------------------------------

name = "KernTool4"
description = 'KernTool4 is an extension for working with Kerning and glyph Margins in Robofont4.'
tags = 'kerning, spacing, margins'
version = "4.1.1"
mainScriptsList = ['KernTool4', 'GroupsControl']

developer = "Alexander Lubovenko"
developerURL = "https://github.com/typedev"
roboFontVersion = "4.2"
iconFile = 'icon.png'

# ------------------------------------------------------------------------
mainScript = ''
launchAtStartUp = False

makeExtension = True
mechanic2support = True
pycOnly = False
masterBranch = 'master' # main
# ------------------------------------------------------------------------

if __name__ == "__main__":
	from AppKit import *
	import os
	import shutil
	from mojo.extensions import ExtensionBundle
	from datetime import datetime

	menuItems = [{'path': '%s.py' % ms,
	              'preferredName': ms,
	              'shortKey': ''} for ms in mainScriptsList]

	# Make the various paths.

	basePath = os.path.dirname(__file__)
	sourcePath = os.path.join(basePath, "source")
	libPath = sourcePath  # os.path.join(sourcePath, "code")
	licensePath = os.path.join(basePath, 'LICENSE')
	requirementsPath = os.path.join(basePath, "requirements.txt")
	extensionFile = "%s.roboFontExt" % name
	buildPath = basePath  # os.path.join(basePath, "build")
	extensionPath = os.path.join(buildPath, extensionFile)
	iconPath = os.path.join(basePath, iconFile)

	# Build the extension.
	if makeExtension:
		B = ExtensionBundle()
		B.name = name
		B.developer = developer
		B.developerURL = developerURL
		B.version = version
		B.launchAtStartUp = launchAtStartUp
		B.mainScript = mainScript
		docPath = os.path.join(sourcePath, "documentation")
		haveDocumentation = False
		if os.path.exists(os.path.join(docPath, "index.html")):
			haveDocumentation = True
		elif os.path.exists(os.path.join(docPath, "index.md")):
			haveDocumentation = True
		if not haveDocumentation:
			docPath = None
		B.html = haveDocumentation
		B.requiresVersionMajor = roboFontVersion.split(".")[0]
		B.requiresVersionMinor = roboFontVersion.split(".")[1]
		B.addToMenu = menuItems

		if os.path.exists(iconPath):
			B.icon = iconPath
		if os.path.exists(licensePath):
			with open(licensePath) as license:
				B.license = license.read()
		if os.path.exists(requirementsPath):
			with open(requirementsPath) as requirements:
				B.requirements = requirements.read()

		print("Building extension...", end = " ")
		v = B.save(extensionPath, libPath = libPath, pycOnly = pycOnly, htmlPath = docPath)
		print('Making zip..')
		shutil.make_archive(extensionPath, 'zip', extensionPath)
		print("done!")
		errors = B.validationErrors()
		if errors:
			print(errors)


	# Making Mechanic2 files..
	if mechanic2support:
		print ('Making Mechanic2 files..')
		repository = '%s/%s' % (developerURL, name)
		zipPath = '%s/archive/%s.zip' % (repository, masterBranch)
		iconRepo = '%s/%s/%s' % (repository.replace('https://github.com','https://raw.githubusercontent.com'),masterBranch, iconFile)
		mechanic2info = dict(
			extensionName = name,
			repository = repository,
			extensionPath = extensionFile,
			description = description,
			developer = developer,
			developerURL = developerURL,
			tags = '[ %s ]' % tags,
			icon = iconRepo,
			zipPath = zipPath,
			dateAdded = datetime.now().strftime('%Y-%m-%y %-H:%M:%S')
		)

		text = '\n'.join(['%s: %s' % (k,v) for k,v in mechanic2info.items()])
		m2exts = [ '%s.mechanic' % name, '%s.yml' % name ]
		for m2 in m2exts:
			m2filepath = os.path.join(basePath, m2)
			m2file = open(m2filepath, mode = 'w')
			m2file.write(text)
			m2file.close()
			print('File %s saved.' % m2)



