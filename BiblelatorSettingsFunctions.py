#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorSettingsFunctions.py
#
# for Biblelator Bible display/editing
#
# Copyright (C) 2013-2016 Robert Hunt
# Author: Robert Hunt <Freely.Given.org@gmail.com>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Program to allow editing of USFM Bibles using Python3 and Tkinter.

self refers to a Biblelator Applicaton instance.
"""

from gettext import gettext as _

LastModifiedDate = '2016-02-14' # by RJH
ShortProgName = "BiblelatorSettingsFunctions"
ProgName = "Biblelator Settings Functions"
ProgVersion = '0.30'
SettingsVersion = '0.30' # Only need to change this if the settings format has changed
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import sys, os, logging
#import multiprocessing

#import tkinter as tk
#from tkinter.filedialog import Open, Directory #, SaveAs
#from tkinter.ttk import Style, Frame, Button, Combobox, Label, Entry

# Biblelator imports
from BiblelatorGlobals import APP_NAME, MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE, MAX_WINDOWS, \
    BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, \
    parseWindowSize, assembleWindowSize
#DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, , \
        #INITIAL_MAIN_SIZE, , , \
        #,  \
        #EDIT_MODE_NORMAL, DEFAULT_KEY_BINDING_DICT, \
        #findHomeFolderPath, parseWindowGeometry, , assembleWindowGeometryFromList, , centreWindow
#from BiblelatorDialogs import errorBeep, showerror, showwarning, showinfo, \
        #SaveWindowNameDialog, DeleteWindowNameDialog, SelectResourceBoxDialog, \
        #GetNewProjectNameDialog, CreateNewProjectFilesDialog, GetNewCollectionNameDialog
#from BiblelatorHelpers import mapReferencesVerseKey, createEmptyUSFMBooks
#from Settings import ApplicationSettings, ProjectSettings
#from ChildWindows import ChildWindows
#from BibleResourceWindows import SwordBibleResourceWindow, InternalBibleResourceWindow, DBPBibleResourceWindow
#from BibleResourceCollection import BibleResourceCollectionWindow
#from BibleReferenceCollection import BibleReferenceCollectionWindow
#from LexiconResourceWindows import BibleLexiconResourceWindow
#from TextEditWindow import TextEditWindow
#from USFMEditWindow import USFMEditWindow
#from ESFMEditWindow import ESFMEditWindow

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
#from BibleOrganizationalSystems import BibleOrganizationalSystem
#from BibleVersificationSystems import BibleVersificationSystems
#from DigitalBiblePlatform import DBPBibles
from VerseReferences import SimpleVerseKey
#from BibleStylesheets import BibleStylesheet
#from SwordResources import SwordType, SwordInterface
#from USFMBible import USFMBible
#from PTXBible import PTXBible, loadPTXSSFData


TEXT_FILETYPES = [('All files',  '*'), ('Text files', '.txt')]
BIBLELATOR_PROJECT_FILETYPES = [('ProjectSettings','ProjectSettings.ini'), ('INI files','.ini'), ('All files','*')]
PARATEXT_FILETYPES = [('SSF files','.ssf'), ('All files','*')]


def exp( messageString ):
    """
    Expands the message string in debug mode.
    Prepends the module name to a error or warning message string
        if we are in debug mode.
    Returns the new string.
    """
    try: nameBit, errorBit = messageString.split( ': ', 1 )
    except ValueError: nameBit, errorBit = '', messageString
    if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit+': ' if nameBit else '', _(errorBit) )
# end of exp



def parseAndApplySettings( self ):
    """
    Parse the settings out of the .INI file.
    """
    def retrieveWindowsSettings( self, windowsSettingsName ):
        """
        Gets a certain windows settings from the settings (INI) file information
            and puts it into a dictionary.

        Returns the dictionary.

        Called from parseAndApplySettings().
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("retrieveWindowsSettings( {} )").format( repr(windowsSettingsName) ) )
            self.setDebugText( "retrieveWindowsSettings..." )
        windowsSettingsFields = self.settings.data['WindowSetting'+windowsSettingsName]
        resultDict = {}
        for j in range( 1, MAX_WINDOWS ):
            winNumber = 'window{}'.format( j )
            for keyName in windowsSettingsFields:
                if keyName.startswith( winNumber ):
                    if winNumber not in resultDict: resultDict[winNumber] = {}
                    resultDict[winNumber][keyName[len(winNumber):]] = windowsSettingsFields[keyName]
        #print( exp("retrieveWindowsSettings"), resultDict )
        return resultDict
    # end of retrieveWindowsSettings


    if BibleOrgSysGlobals.debugFlag:
        print( exp("parseAndApplySettings()") )
        self.setDebugText( "parseAndApplySettings..." )
    try: self.minimumSize = self.settings.data[APP_NAME]['minimumSize']
    except KeyError: self.minimumSize = MINIMUM_MAIN_SIZE
    self.rootWindow.minsize( *parseWindowSize( self.minimumSize ) )
    try: self.maximumSize = self.settings.data[APP_NAME]['maximumSize']
    except KeyError: self.maximumSize = MAXIMUM_MAIN_SIZE
    self.rootWindow.maxsize( *parseWindowSize( self.maximumSize ) )
    #try: self.rootWindow.geometry( self.settings.data[APP_NAME]['windowGeometry'] )
    #except KeyError: print( "KeyError1" ) # we had no geometry set
    #except tk.TclError: logging.critical( exp("Application.__init__: Bad window geometry in settings file: {}").format( settings.data[APP_NAME]['windowGeometry'] ) )
    try:
        windowSize = self.settings.data[APP_NAME]['windowSize'] if 'windowSize' in self.settings.data[APP_NAME] else None
        windowPosition = self.settings.data[APP_NAME]['windowPosition'] if 'windowPosition' in self.settings.data[APP_NAME] else None
        #print( "ws", repr(windowSize), "wp", repr(windowPosition) )
        if windowSize and windowPosition: self.rootWindow.geometry( windowSize + '+' + windowPosition )
        else: logging.warning( "Settings.KeyError: no windowSize & windowPosition" )
    except KeyError: pass # no [APP_NAME] entries

    try: self.doChangeTheme( self.settings.data[APP_NAME]['themeName'] )
    except KeyError: logging.warning( "Settings.KeyError: no themeName" )

    # Internet stuff
    try:
        internetAccessString = self.settings.data['Internet']['internetAccess']
        self.internetAccessEnabled = internetAccessString == 'Enabled'
    except KeyError: self.internetAccessEnabled = False # default
    try:
        checkForMessagesString = self.settings.data['Internet']['checkForMessages']
        self.checkForMessagesEnabled = checkForMessagesString == 'Enabled'
    except KeyError: self.checkForMessagesEnabled = True # default
    try:
        lastMessageNumberString = self.settings.data['Internet']['lastMessageNumberRead']
        self.lastMessageNumberRead = int( lastMessageNumberString )
    except (KeyError, ValueError): self.lastMessageNumberRead = -1
    try:
        sendUsageStatisticsString = self.settings.data['Internet']['sendUsageStatistics']
        self.sendUsageStatisticsEnabled = sendUsageStatisticsString == 'Enabled'
    except KeyError: self.sendUsageStatisticsEnabled = True # default
    try:
        automaticUpdatesString = self.settings.data['Internet']['automaticUpdates']
        self.automaticUpdatesEnabled = automaticUpdatesString == 'Enabled'
    except KeyError: self.automaticUpdatesEnabled = True # default
    try:
        useDevelopmentVersionsString = self.settings.data['Internet']['useDevelopmentVersions']
        self.useDevelopmentVersionsEnabled = useDevelopmentVersionsString == 'Enabled'
    except KeyError: self.useDevelopmentVersionsEnabled = False # default
    try:
        cloudBackupsString = self.settings.data['Internet']['cloudBackups']
        self.cloudBackupsEnabled = cloudBackupsString == 'Enabled'
    except KeyError: self.cloudBackupsEnabled = True # default

    # Paths
    try: self.lastFileDir = self.settings.data['Paths']['lastFileDir']
    except KeyError: pass # use program default
    try: self.lastBiblelatorFileDir = self.settings.data['Paths']['lastBiblelatorFileDir']
    except KeyError: pass # use program default
    try: self.lastParatextFileDir = self.settings.data['Paths']['lastParatextFileDir']
    except KeyError: pass # use program default
    try: self.lastInternalBibleDir = self.settings.data['Paths']['lastInternalBibleDir']
    except KeyError: pass # use program default

    # Users
    try: self.currentUser = self.settings.data['Users']['currentUser']
    except KeyError: pass # use program default

    # BCV groups
    try: self.currentVerseKeyGroup = self.settings.data['BCVGroups']['currentGroup']
    except KeyError: self.currentVerseKeyGroup = 'A'
    try: self.GroupA_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['A-Book'],self.settings.data['BCVGroups']['A-Chapter'],self.settings.data['BCVGroups']['A-Verse'])
    except KeyError: self.GroupA_VerseKey = SimpleVerseKey( self.getFirstBookCode(), '1', '1' )
    try: self.GroupB_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['B-Book'],self.settings.data['BCVGroups']['B-Chapter'],self.settings.data['BCVGroups']['B-Verse'])
    except KeyError: self.GroupB_VerseKey = SimpleVerseKey( 'PSA', '119', '1' )
    try: self.GroupC_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['C-Book'],self.settings.data['BCVGroups']['C-Chapter'],self.settings.data['BCVGroups']['C-Verse'])
    except KeyError: self.GroupC_VerseKey = SimpleVerseKey( 'MAT', '1', '1' )
    try: self.GroupD_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['D-Book'],self.settings.data['BCVGroups']['D-Chapter'],self.settings.data['BCVGroups']['D-Verse'])
    except KeyError: self.GroupD_VerseKey = SimpleVerseKey( 'REV', '22', '1' )

    try: self.lexiconWord = self.settings.data['Lexicon']['currentWord']
    except KeyError: self.lexiconWord = None

    # We keep our copy of all the windows settings in self.windowsSettingsDict
    windowsSettingsNamesList = []
    for name in self.settings.data:
        if name.startswith( 'WindowSetting' ): windowsSettingsNamesList.append( name[13:] )
    if BibleOrgSysGlobals.debugFlag: print( exp("Available windows settings are: {}").format( windowsSettingsNamesList ) )
    if windowsSettingsNamesList: assert 'Current' in windowsSettingsNamesList
    self.windowsSettingsDict = {}
    for windowsSettingsName in windowsSettingsNamesList:
        self.windowsSettingsDict[windowsSettingsName] = retrieveWindowsSettings( self, windowsSettingsName )
    if 'Current' in windowsSettingsNamesList: applyGivenWindowsSettings( self, 'Current' )
    else: logging.critical( exp("Application.parseAndApplySettings: No current window settings available") )
# end of parseAndApplySettings


def applyGivenWindowsSettings( self, givenWindowsSettingsName ):
    """
    Given the name of windows settings,
        find the settings in our dictionary
        and then apply it by creating the windows.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("applyGivenWindowsSettings( {} )").format( repr(givenWindowsSettingsName) ) )
        self.setDebugText( "applyGivenWindowsSettings..." )
    windowsSettingsFields = self.windowsSettingsDict[givenWindowsSettingsName]
    for j in range( 1, MAX_WINDOWS ):
        winNumber = 'window{}'.format( j )
        if winNumber in windowsSettingsFields:
            thisStuff = windowsSettingsFields[winNumber]
            winType = thisStuff['Type']
            #windowGeometry = thisStuff['Geometry'] if 'Geometry' in thisStuff else None
            windowSize = thisStuff['Size'] if 'Size' in thisStuff else None
            windowPosition = thisStuff['Position'] if 'Position' in thisStuff else None
            windowGeometry = windowSize+'+'+windowPosition if windowSize and windowPosition else None
            #print( winType, windowGeometry )
            if winType == 'SwordBibleResourceWindow':
                rw = self.openSwordBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                #except: logging.critical( "Unable to read all SwordBibleResourceWindow {} settings".format( j ) )
            elif winType == 'DBPBibleResourceWindow':
                rw = self.openDBPBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                #except: logging.critical( "Unable to read all DBPBibleResourceWindow {} settings".format( j ) )
            elif winType == 'InternalBibleResourceWindow':
                rw = self.openInternalBibleResourceWindow( thisStuff['BibleFolderPath'], windowGeometry )
                #except: logging.critical( "Unable to read all InternalBibleResourceWindow {} settings".format( j ) )

            #elif winType == 'HebrewLexiconResourceWindow':
                #self.openHebrewLexiconResourceWindow( thisStuff['HebrewLexiconPath'], windowGeometry )
                ##except: logging.critical( "Unable to read all HebrewLexiconResourceWindow {} settings".format( j ) )
            #elif winType == 'GreekLexiconResourceWindow':
                #self.openGreekLexiconResourceWindow( thisStuff['GreekLexiconPath'], windowGeometry )
                ##except: logging.critical( "Unable to read all GreekLexiconResourceWindow {} settings".format( j ) )
            elif winType == 'BibleLexiconResourceWindow':
                rw = self.openBibleLexiconResourceWindow( thisStuff['BibleLexiconPath'], windowGeometry )
                #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )

            elif winType == 'BibleResourceCollectionWindow':
                collectionName = thisStuff['CollectionName']
                rw = self.openBibleResourceCollectionWindow( collectionName, windowGeometry )
                #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )
                if 'BibleResourceCollection'+collectionName in self.settings.data:
                    collectionSettingsFields = self.settings.data['BibleResourceCollection'+collectionName]
                    for k in range( 1, MAX_WINDOWS ):
                        boxNumber = 'box{}'.format( k )
                        boxType = boxSource = None
                        for keyname in collectionSettingsFields:
                            if keyname.startswith( boxNumber ):
                                #print( "found", keyname, "setting for", collectionName, "collection" )
                                if keyname == boxNumber+'Type': boxType = collectionSettingsFields[keyname]
                                elif keyname == boxNumber+'Source': boxSource = collectionSettingsFields[keyname]
                                else:
                                    print( "Unknown {} collection key: {} = {}".format( repr(collectionName), keyname, collectionSettingsFields[keyname] ) )
                                    if BibleOrgSysGlobals.debugFlag: halt
                        if boxType and boxSource: rw.openBox( boxType, boxSource )

            elif winType == 'BibleReferenceCollectionWindow':
                xyz = "JustTesting!"
                rw = self.openBibleReferenceCollectionWindow( xyz, windowGeometry )
                #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )

            elif winType == 'PlainTextEditWindow':
                try: filepath = thisStuff['TextFilepath']
                except KeyError: filepath = None
                rw = self.openFileTextEditWindow( filepath, windowGeometry )
                #except: logging.critical( "Unable to read all PlainTextEditWindow {} settings".format( j ) )
            elif winType == 'BiblelatorUSFMBibleEditWindow':
                rw = self.openBiblelatorBibleEditWindow( thisStuff['ProjectFolderPath'], thisStuff['EditMode'], windowGeometry )
                #except: logging.critical( "Unable to read all BiblelatorUSFMBibleEditWindow {} settings".format( j ) )
            elif winType == 'ParatextUSFMBibleEditWindow':
                rw = self.openParatextBibleEditWindow( thisStuff['SSFFilepath'], thisStuff['EditMode'], windowGeometry )
                #except: logging.critical( "Unable to read all ParatextUSFMBibleEditWindow {} settings".format( j ) )
            elif winType == 'ESFMEditWindow':
                rw = self.openESFMEditWindow( thisStuff['ESFMFolder'], thisStuff['EditMode'], windowGeometry )
                #except: logging.critical( "Unable to read all ESFMEditWindow {} settings".format( j ) )

            else:
                logging.critical( exp("Application.__init__: Unknown {} window type").format( repr(winType) ) )
                if BibleOrgSysGlobals.debugFlag: halt

            if rw is None:
                logging.critical( exp("Application.__init__: Failed to reopen {} window type!!! How did this happen?").format( repr(winType) ) )
            else: # we've opened our child window -- now customize it a bit more
                minimumSize = thisStuff['MinimumSize'] if 'MinimumSize' in thisStuff else None
                if minimumSize:
                    if BibleOrgSysGlobals.debugFlag: assert 'x' in minimumSize
                    rw.minsize( *parseWindowSize( minimumSize ) )
                maximumSize = thisStuff['MaximumSize'] if 'MaximumSize' in thisStuff else None
                if maximumSize:
                    if BibleOrgSysGlobals.debugFlag: assert 'x' in maximumSize
                    rw.maxsize( *parseWindowSize( maximumSize ) )
                groupCode = thisStuff['GroupCode'] if 'GroupCode' in thisStuff else None
                if groupCode:
                    if BibleOrgSysGlobals.debugFlag: assert groupCode in BIBLE_GROUP_CODES
                    rw.groupCode = groupCode
                contextViewMode = thisStuff['ContextViewMode'] if 'ContextViewMode' in thisStuff else None
                if contextViewMode:
                    if BibleOrgSysGlobals.debugFlag: assert contextViewMode in BIBLE_CONTEXT_VIEW_MODES
                    rw.contextViewMode = contextViewMode
                    rw.createMenuBar() # in order to show the correct contextViewMode
# end of applyGivenWindowsSettings


def getCurrentChildWindowSettings( self ):
    """
    Go through the currently open windows and get their settings data
        and save it in self.windowsSettingsDict['Current'].
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("getCurrentChildWindowSettings()") )

    if 'Current' in self.windowsSettingsDict: del self.windowsSettingsDict['Current']
    self.windowsSettingsDict['Current'] = {}
    for j, appWin in enumerate( self.childWindows ):
            if appWin.winType == 'HTMLWindow':
                continue # We don't save these

            winNumber = "window{}".format( j+1 )
            self.windowsSettingsDict['Current'][winNumber] = {}
            thisOne = self.windowsSettingsDict['Current'][winNumber]
            thisOne['Type'] = appWin.winType #.replace( 'Window', 'Window' )
            #print( "child geometry", appWin.geometry(), "child winfo_geometry", appWin.winfo_geometry() )
            #print( "child x", appWin.winfo_x(), "child rootx", appWin.winfo_rootx() )
            #print( "child y", appWin.winfo_y(), "child rooty", appWin.winfo_rooty() )
            #print( "child height", appWin.winfo_height(), "child reqheight", appWin.winfo_reqheight() )
            #print( "child width", appWin.winfo_width(), "child reqwidth", appWin.winfo_reqwidth() )
            thisOne['Size'], thisOne['Position'] = appWin.geometry().split( '+', 1 )
            if thisOne['Position'] == '0+0': # not sure why this occurs for a new window -- pops up top left
                thisOne['Position'] = appWin.winfo_geometry().split( '+', 1 )[1] # Won't be exact but close
            thisOne['MinimumSize'] = assembleWindowSize( *appWin.minsize() )
            thisOne['MaximumSize'] = assembleWindowSize( *appWin.maxsize() )

            if appWin.winType == 'SwordBibleResourceWindow':
                thisOne['ModuleAbbreviation'] = appWin.moduleID
            elif appWin.winType == 'DBPBibleResourceWindow':
                thisOne['ModuleAbbreviation'] = appWin.moduleID
            elif appWin.winType == 'InternalBibleResourceWindow':
                thisOne['BibleFolderPath'] = appWin.moduleID

            elif appWin.winType == 'BibleLexiconResourceWindow':
                thisOne['BibleLexiconPath'] = appWin.moduleID

            elif appWin.winType == 'BibleResourceCollectionWindow':
                thisOne['CollectionName'] = appWin.moduleID

            elif appWin.winType == 'PlainTextEditWindow':
                try: thisOne['TextFilepath'] = appWin.filepath
                except AttributeError: pass # It's possible to have a blank new text edit window open

            elif appWin.winType == 'BiblelatorUSFMBibleEditWindow':
                thisOne['ProjectFolderPath'] = appWin.moduleID
                thisOne['EditMode'] = appWin.editMode
            elif appWin.winType == 'ParatextUSFMBibleEditWindow':
                thisOne['SSFFilepath'] = appWin.moduleID
                thisOne['EditMode'] = appWin.editMode

            else:
                logging.critical( exp("getCurrentChildWindowSettings: Unknown {} window type").format( repr(appWin.winType) ) )
                if BibleOrgSysGlobals.debugFlag: halt

            if 'Bible' in appWin.genericWindowType:
                try: thisOne['GroupCode'] = appWin.groupCode
                except AttributeError: logging.critical( exp("getCurrentChildWindowSettings: Why no groupCode in {}").format( appWin.winType ) )
                try: thisOne['ContextViewMode'] = appWin.contextViewMode
                except AttributeError: logging.critical( exp("getCurrentChildWindowSettings: Why no contextViewMode in {}").format( appWin.winType ) )
# end of getCurrentChildWindowSettings


def saveNewWindowSetup( self ):
    """
    Gets the name for the new window setup and saves the information.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("saveNewWindowSetup()") )
        self.setDebugText( "saveNewWindowSetup..." )
    swnd = SaveWindowNameDialog( self, self.windowsSettingsDict, title=_('Save window setup') )
    if BibleOrgSysGlobals.debugFlag: print( "swndResult", repr(swnd.result) )
    if swnd.result:
        getCurrentChildWindowSettings( self )
        self.windowsSettingsDict[swnd.result] = self.windowsSettingsDict['Current'] # swnd.result is the new window name
        print( "swS", self.windowsSettingsDict )
        self.writeSettingsFile() # Save file now in case we crash
        self.createMenuBar() # refresh
# end of saveNewWindowSetup


def doDeleteExistingWindowSetup( self ):
    """
    Gets the name of an existing window setting and deletes the setting.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("doDeleteExistingWindowSetup()") )
        self.setDebugText( "doDeleteExistingWindowSetup..." )
    assert self.windowsSettingsDict and (len(self.windowsSettingsDict)>1 or 'Current' not in self.windowsSettingsDict)
    dwnd = DeleteWindowNameDialog( self, self.windowsSettingsDict, title=_('Delete saved window setup') )
    if BibleOrgSysGlobals.debugFlag: print( "dwndResult", repr(dwnd.result) )
    if dwnd.result:
        if BibleOrgSysGlobals.debugFlag:
            assert dwnd.result in self.windowsSettingsDict
        del self.windowsSettingsDict[dwnd.result]
        #self.settings.save() # Save file now in case we crash -- don't worry -- it's easy to delete one
        self.createMenuBar() # refresh
# end of doDeleteExistingWindowSetup


def doViewSettings( self ):
    """
    Open a pop-up text window with the current settings displayed.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("doViewSettings()") )
        self.setDebugText( "doViewSettings..." )
    tEW = TextEditWindow( self )
    #if windowGeometry: tEW.geometry( windowGeometry )
    if not tEW.setFilepath( self.settings.settingsFilepath ) \
    or not tEW.loadText():
        tEW.closeChildWindow()
        showerror( self, APP_NAME, _("Sorry, unable to open settings file") )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed doViewSettings" )
    else:
        self.childWindows.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewSettings" )
    self.setReadyStatus()
# end of doViewSettings


def writeSettingsFile( self ):
    """
    Update our program settings and save them.
    """
    if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( exp("writeSettingsFile()") )
    if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'writeSettingsFile' )
    self.settings.reset()

    self.settings.data[APP_NAME] = {}
    main = self.settings.data[APP_NAME]
    main['settingsVersion'] = SettingsVersion
    main['progVersion'] = ProgVersion
    main['themeName'] = self.themeName
    #print( "root geometry", self.rootWindow.geometry(), "root winfo_geometry", self.rootWindow.winfo_geometry() )
    #print( "root x", self.rootWindow.winfo_x(), "root rootx", self.rootWindow.winfo_rootx() )
    #print( "root y", self.rootWindow.winfo_y(), "root rooty", self.rootWindow.winfo_rooty() )
    main['windowSize'], main['windowPosition'] = self.rootWindow.geometry().split( '+', 1 )
    # Seems that winfo_geometry doesn't work above (causes root Window to move)
    main['minimumSize'] = self.minimumSize
    main['maximumSize'] = self.maximumSize

    # Save the Internet access controls
    self.settings.data['Internet'] = {}
    internet = self.settings.data['Internet']
    internet['internetAccess'] = 'Enabled' if self.internetAccessEnabled else 'Disabled'
    internet['checkForMessages'] = 'Enabled' if self.checkForMessagesEnabled else 'Disabled'
    internet['lastMessageNumberRead'] = str( self.lastMessageNumberRead )
    internet['sendUsageStatistics'] = 'Enabled' if self.sendUsageStatisticsEnabled else 'Disabled'
    internet['automaticUpdates'] = 'Enabled' if self.automaticUpdatesEnabled else 'Disabled'
    internet['useDevelopmentVersions'] = 'Enabled' if self.useDevelopmentVersionsEnabled else 'Disabled'
    internet['cloudBackups'] = 'Enabled' if self.cloudBackupsEnabled else 'Disabled'

    # Save the last paths
    self.settings.data['Paths'] = {}
    paths = self.settings.data['Paths']
    paths['lastFileDir'] = self.lastFileDir
    paths['lastBiblelatorFileDir'] = self.lastBiblelatorFileDir
    paths['lastParatextFileDir'] = self.lastParatextFileDir
    paths['lastInternalBibleDir'] = self.lastInternalBibleDir

    # Save the user information
    self.settings.data['Users'] = {}
    users = self.settings.data['Users']
    users['currentUser'] = self.currentUser

    # Save the referenceGroups A..D
    self.settings.data['BCVGroups'] = {}
    groups = self.settings.data['BCVGroups']
    groups['currentGroup'] = self.currentVerseKeyGroup
    groups['A-Book'] = self.GroupA_VerseKey[0]
    groups['A-Chapter'] = self.GroupA_VerseKey[1]
    groups['A-Verse'] = self.GroupA_VerseKey[2]
    groups['B-Book'] = self.GroupB_VerseKey[0]
    groups['B-Chapter'] = self.GroupB_VerseKey[1]
    groups['B-Verse'] = self.GroupB_VerseKey[2]
    groups['C-Book'] = self.GroupC_VerseKey[0]
    groups['C-Chapter'] = self.GroupC_VerseKey[1]
    groups['C-Verse'] = self.GroupC_VerseKey[2]
    groups['D-Book'] = self.GroupD_VerseKey[0]
    groups['D-Chapter'] = self.GroupD_VerseKey[1]
    groups['D-Verse'] = self.GroupD_VerseKey[2]

    # Save the lexicon info
    self.settings.data['Lexicon'] = {}
    lexicon = self.settings.data['Lexicon']
    if self.lexiconWord: lexicon['currentWord'] = self.lexiconWord

    # Save any open Bible resource collections
    print( "save collection data..." )
    for appWin in self.childWindows:
        #print( "  gT", appWin.genericWindowType )
        #print( "  wT", appWin.winType )
        if appWin.winType == 'BibleResourceCollectionWindow':
            if appWin.resourceBoxes: # so we don't create just an empty heading for an empty collection
                self.settings.data['BibleResourceCollection'+appWin.moduleID] = {}
                thisOne = self.settings.data['BibleResourceCollection'+appWin.moduleID]
                #print( "  found", appWin.moduleID )
                for j, box in enumerate( appWin.resourceBoxes ):
                    boxNumber = 'box{}'.format( j+1 )
                    #print( "    bT", box.boxType )
                    #print( "    ID", box.moduleID )
                    thisOne[boxNumber+'Type'] = box.boxType.replace( 'BibleResourceBox', '' )
                    thisOne[boxNumber+'Source'] = box.moduleID

    # Get the current child window settings
    getCurrentChildWindowSettings( self )
    # Save all the various window set-ups including both the named ones and the current one
    for windowsSettingName in self.windowsSettingsDict:
        if BibleOrgSysGlobals.debugFlag: print( exp("Saving windows set-up {}").format( repr(windowsSettingName) ) )
        try: # Just in case something goes wrong with characters in a settings name
            self.settings.data['WindowSetting'+windowsSettingName] = {}
            thisOne = self.settings.data['WindowSetting'+windowsSettingName]
            for windowNumber,winDict in sorted( self.windowsSettingsDict[windowsSettingName].items() ):
                #print( "  ", repr(windowNumber), repr(winDict) )
                for windowSettingName,value in sorted( winDict.items() ):
                    thisOne[windowNumber+windowSettingName] = value
        except UnicodeEncodeError: logging.error( exp("writeSettingsFile: unable to write {} windows set-up").format( repr(windowsSettingName) ) )
    self.settings.save()
# end of writeSettingsFile



def demo():
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersionDate )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag:
        print( exp("Platform is"), sys.platform ) # e.g., "win32"
        print( exp("OS name is"), os.name ) # e.g., "nt"
        if sys.platform == "linux": print( exp("OS uname is"), os.uname() )
        print( exp("Running main...") )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( ProgNameVersion )

    homeFolderPath = findHomeFolderPath()
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, APP_NAME )
    settings.load()

    application = Application( tkRootWindow, homeFolderPath, loggingFolderPath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.demo


def main( homeFolderPath, loggingFolderPath ):
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersionDate )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag:
        print( exp("Platform is"), sys.platform ) # e.g., "win32"
        print( exp("OS name is"), os.name ) # e.g., "nt"
        if sys.platform == "linux": print( exp("OS uname is"), os.uname() )
        print( exp("Running main...") )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( ProgNameVersion )
    settings = ApplicationSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, APP_NAME )
    settings.load()

    application = Application( tkRootWindow, homeFolderPath, loggingFolderPath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.main


if __name__ == '__main__':
    from BibleOrgSysGlobals import setup, addStandardOptionsAndProcess, closedown

    # Configure basic set-up
    homeFolderPath = findHomeFolderPath()
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    parser = setup( ProgName, ProgVersion, loggingFolderPath=loggingFolderPath )
    addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    main( homeFolderPath, loggingFolderPath )

    closedown( ProgName, ProgVersion )
# end of BiblelatorSettingsFunctions.py