# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# The script moves unnecessary Python scripts and modules
# from the Source folder to the Skipped folder
#
# Main module names are imported from the buildExtention.py script
# -------------------------------------------------------------------------------

import os, sys, glob
import shutil
from modulefinder import ModuleFinder
# ------------------------------------------------------------------------------
import buildExtention
# ------------------------------------------------------------------------------

def moveUnnecessaryFiles(mainScriptsList = None):
    if not mainScriptsList: return
    print('Finding Dependent Modules..')
    basePath = os.path.dirname(__file__)
    sourcePath = os.path.join(basePath, 'source')
    skipedModulesPath = os.path.join(basePath,'skipped')
    print('source path:', sourcePath)
    usedModules = mainScriptsList

    for mainScript in usedModules:
        mainScriptFile = os.path.join(sourcePath, '%s.py' %  mainScript)

        path = sys.path[:]
        path[0] = os.path.dirname(mainScriptFile)
        finder = ModuleFinder(path)

        finder.load_file(mainScriptFile)
        print ('used in %s' % mainScript)
        for name, mod in finder.modules.items():
            modulePath = mod.__file__
            if modulePath and sourcePath in modulePath:
                if name not in usedModules:
                    usedModules.append(name)
                    print('\t%s' % name)

    dirpath = os.path.join(sourcePath, '*.py')
    listoffilepaths = glob.glob(dirpath)
    listoffilenames = []
    if not os.path.exists(skipedModulesPath):
        print('Making Skipped folder..')
        os.mkdir(skipedModulesPath)

    print('Moving unnecessary files..')
    for filePath in listoffilepaths:
        fileName = os.path.basename(filePath)
        moduleName = fileName.replace('.py', '')
        if moduleName not in usedModules:
            listoffilenames.append(filePath)
            print('will be moved:', fileName)
            print(filePath)
            path2move = os.path.join(skipedModulesPath,fileName)
            print('-->',path2move)
            shutil.move(filePath,path2move)
    print('done')

def main():
    moveUnnecessaryFiles(buildExtention.mainScriptsList)

if __name__ == "__main__":
    main()