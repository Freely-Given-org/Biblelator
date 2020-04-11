#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorSettingsFunctions.py
#
# for Biblelator Bible display/editing
#
# Copyright (C) 2013-2020 Robert Hunt
# Author: Robert Hunt <Freely.Given.org+Biblelator@gmail.com>
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

"self" refers to a Biblelator Application instance.
    parseAndApplySettings( self )
    applyGivenWindowsSettings( self, givenWindowsSettingsName )
    getCurrentChildWindowSettings( self )
    saveNewWindowSetup( self )
    deleteExistingWindowSetup( self )
    viewSettings( self )
    writeSettingsFile( self )
    doSendUsageStatistics( self )
    demo()
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2020-04-11' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorSettingsFunctions"
PROGRAM_NAME = "Biblelator Settings Functions"
PROGRAM_VERSION = '0.46'
SettingsVersion = '0.45' # Only need to change this if the settings format has changed
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


import os
import logging

# Biblelator imports
from Biblelator.BiblelatorGlobals import APP_NAME, DEFAULT, \
    DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, \
    MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE, MAX_WINDOWS, MAX_RECENT_FILES, \
    BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, \
    parseWindowSize, assembleWindowSize
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError
from Biblelator.Dialogs.BiblelatorDialogs import SaveWindowsLayoutNameDialog, DeleteWindowsLayoutNameDialog
from Biblelator.Windows.TextEditWindow import TextEditWindow

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Formats.PickledBible import ZIPPED_PICKLE_FILENAME_END



def convertToPython( text ):
    """
    Convert text to Python logic values.
    """
    if text == 'True': return True
    if text == 'False': return False
    if text == 'None': return None
    if text.lower() == 'true':
        logging.warning( f"Settings: Found {text!r} instead of 'True'" )
        return True
    elif text.lower() == 'false':
        logging.warning( f"Settings: Found {text!r} instead of 'False'" )
        return False
    if text.lower() == 'none':
        logging.warning( f"Settings: Found {text!r} instead of 'None'" )
        return None
    return text
# end of convertToPython



def parseAndApplySettings( self ):
    """
    Parse the settings out of the .INI file.

    "self" refers to a Biblelator Application instance.
    """
    logging.info( "parseAndApplySettings()" )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "parseAndApplySettings()" )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "parseAndApplySettings…" )

    def retrieveWindowsSettings( self, windowsSettingsName ):
        """
        Gets a certain windows settings from the settings (INI) file information
            and puts it into a dictionary.

        Returns the dictionary.

        Called from parseAndApplySettings().
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "retrieveWindowsSettings( {} )".format( repr(windowsSettingsName) ) )
            self.setDebugText( "retrieveWindowsSettings…" )
        windowsSettingsFields = self.settings.data['WindowSetting'+windowsSettingsName]
        resultDict = {}
        for j in range( 1, MAX_WINDOWS+1 ):
            winNumber = 'window{}'.format( j )
            for keyName in windowsSettingsFields:
                if keyName.startswith( winNumber ):
                    if winNumber not in resultDict: resultDict[winNumber] = {}
                    resultDict[winNumber][keyName[len(winNumber):]] = windowsSettingsFields[keyName]
        #print( "retrieveWindowsSettings", resultDict )
        return resultDict
    # end of retrieveWindowsSettings


    # Main code for parseAndApplySettings()
    # Parse main app stuff
    #try: self.rootWindow.geometry( self.settings.data[APP_NAME]['windowGeometry'] )
    #except KeyError: print( "KeyError1" ) # we had no geometry set
    #except tk.TclError: logging.critical( "Application.__init__: Bad window geometry in settings file: {}".format( settings.data[APP_NAME]['windowGeometry'] ) )
    try:
        windowSize = self.settings.data[APP_NAME]['windowSize'] if 'windowSize' in self.settings.data[APP_NAME] else None
        windowPosition = self.settings.data[APP_NAME]['windowPosition'] if 'windowPosition' in self.settings.data[APP_NAME] else None
        if 0 and debuggingThisModule:
            print( "main window settings (across/down from ini file) size", repr(windowSize), "pos", repr(windowPosition) )
        if windowSize and windowPosition:
            self.update() # Make sure that the window has finished being created
            self.rootWindow.geometry( windowSize + '+' + windowPosition )
        else: logging.warning( "Settings.KeyError: no windowSize & windowPosition" )
    except KeyError: pass # no [APP_NAME] entries

    try: self.minimumSize = self.settings.data[APP_NAME]['minimumSize']
    except KeyError: self.minimumSize = MINIMUM_MAIN_SIZE
    self.rootWindow.minsize( *parseWindowSize( self.minimumSize ) )
    try: self.maximumSize = self.settings.data[APP_NAME]['maximumSize']
    except KeyError: self.maximumSize = MAXIMUM_MAIN_SIZE
    self.rootWindow.maxsize( *parseWindowSize( self.maximumSize ) )
    if 0 and debuggingThisModule:
        print( "  apply min", repr(self.minimumSize), repr(parseWindowSize(self.minimumSize)), "max", repr(self.maximumSize), repr(parseWindowSize(self.maximumSize)) )

    try: self.doChangeTheme( self.settings.data[APP_NAME]['themeName'] )
    except KeyError: logging.warning( "Settings.KeyError: no themeName" )

    # Parse Interface stuff
    try: self.interfaceLanguage = self.settings.data['Interface']['interfaceLanguage']
    except KeyError: self.interfaceLanguage = DEFAULT
    if BibleOrgSysGlobals.debugFlag: assert self.interfaceLanguage in ( DEFAULT, )
    try: self.interfaceComplexity = self.settings.data['Interface']['interfaceComplexity']
    except KeyError: self.interfaceComplexity = DEFAULT
    if BibleOrgSysGlobals.debugFlag: assert self.interfaceComplexity in ( DEFAULT, 'Basic', 'Advanced', )
    try: self.touchMode = convertToPython( self.settings.data['Interface']['touchMode'] )
    except KeyError: self.touchMode = False
    if BibleOrgSysGlobals.debugFlag: assert self.touchMode in ( False, True )
    try: self.tabletMode = convertToPython( self.settings.data['Interface']['tabletMode'] )
    except KeyError: self.tabletMode = False
    if BibleOrgSysGlobals.debugFlag: assert self.tabletMode in ( False, True )
    try: self.showDebugMenu = convertToPython( self.settings.data['Interface']['showDebugMenu'] )
    except KeyError: self.showDebugMenu = False
    if BibleOrgSysGlobals.debugFlag: assert self.showDebugMenu in ( False, True )

    # Parse Internet stuff
    try:
        internetAccessString = self.settings.data['Internet']['internetAccess']
        self.internetAccessEnabled = internetAccessString == 'Enabled'
    except KeyError: self.internetAccessEnabled = False # default
    try:
        fastString = self.settings.data['Internet']['internetFast']
        self.internetFast = fastString.lower() in ('true' ,'yes',)
    except KeyError: self.internetFast = True # default
    try:
        expensiveString = self.settings.data['Internet']['internetExpensive']
        self.internetExpensive = expensiveString.lower() in ('true' ,'yes',)
    except KeyError: self.internetExpensive = True # default
    try:
        cloudBackupsString = self.settings.data['Internet']['cloudBackups']
        self.cloudBackupsEnabled = cloudBackupsString == 'Enabled'
    except KeyError: self.cloudBackupsEnabled = True # default
    try:
        checkForMessagesString = self.settings.data['Internet']['checkForDeveloperMessages']
        self.checkForDeveloperMessagesEnabled = checkForMessagesString == 'Enabled'
    except KeyError: self.checkForDeveloperMessagesEnabled = True # default
    try:
        lastMessageNumberString = self.settings.data['Internet']['lastMessageNumberRead']
        self.lastMessageNumberRead = int( lastMessageNumberString )
    except (KeyError, ValueError): self.lastMessageNumberRead = 0
    else:
        if self.lastMessageNumberRead < 0: self.lastMessageNumberRead = 0 # Handle errors in ini file
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

    # Parse project info
    try: self.currentProjectName = self.settings.data['Project']['currentProjectName']
    except KeyError: pass # use program default

    # Parse users
    try: self.currentUserName = self.settings.data['Users']['currentUserName']
    except KeyError: pass # use program default
    try: self.currentUserInitials = self.settings.data['Users']['currentUserInitials']
    except KeyError: pass # use program default
    try: self.currentUserEmail = self.settings.data['Users']['currentUserEmail']
    except KeyError: pass # use program default
    try: self.currentUserRole = self.settings.data['Users']['currentUserRole']
    except KeyError: pass # use program default
    try: self.currentUserAssignments = self.settings.data['Users']['currentUserAssignments']
    except KeyError: pass # use program default

    # Parse paths
    try: self.lastFileDir = self.settings.data['Paths']['lastFileDir']
    except KeyError: pass # use program default
    finally:
        if self.lastFileDir[-1] not in '/\\': self.lastFileDir += '/'
    try: self.lastBiblelatorFileDir = self.settings.data['Paths']['lastBiblelatorFileDir']
    except KeyError: pass # use program default
    finally:
        if self.lastBiblelatorFileDir[-1] not in '/\\': self.lastBiblelatorFileDir += '/'
    try: self.lastParatextFileDir = self.settings.data['Paths']['lastParatextFileDir']
    except KeyError: pass # use program default
    finally:
        if isinstance( self.lastParatextFileDir, str) and self.lastParatextFileDir[-1] not in '/\\':
            self.lastParatextFileDir += '/'
    try: self.lastInternalBibleDir = self.settings.data['Paths']['lastInternalBibleDir']
    except KeyError: pass # use program default
    finally:
        if isinstance( self.lastInternalBibleDir, str) and self.lastInternalBibleDir[-1] not in '/\\':
            self.lastInternalBibleDir += '/'
    try: self.lastSwordDir = self.settings.data['Paths']['lastSwordDir']
    except KeyError: pass # use program default
    finally:
        if self.lastSwordDir[-1] not in '/\\': self.lastSwordDir += '/'

    # Parse recent files
    assert not self.recentFiles
    try: recentFields = self.settings.data['RecentFiles']
    except KeyError: recentFields = None
    if recentFields: # in settings file
        for j in range( 1, MAX_RECENT_FILES+1 ):
            recentName = 'recent{}'.format( j )
            for keyName in recentFields:
                if keyName.startswith( recentName ): # This index number (j) is present
                    filename = convertToPython( self.settings.data['RecentFiles']['recent{}Filename'.format( j )] )
                    #if filename == 'None': filename = None
                    folder = convertToPython( self.settings.data['RecentFiles']['recent{}Folder'.format( j )] )
                    #if folder == 'None': folder = None
                    if folder and folder[-1] not in '/\\': folder += '/'
                    windowType = self.settings.data['RecentFiles']['recent{}Type'.format( j )]
                    self.recentFiles.append( (filename,folder,windowType) )
                    assert len(self.recentFiles) == j
                    break # go to next j

    # Parse BCV groups
    try: self.genericBibleOrganisationalSystemName = self.settings.data['BCVGroups']['genericBibleOrganisationalSystemName']
    #except KeyError: pass # use program default
    except KeyError: self.genericBibleOrganisationalSystemName = 'GENERIC-KJV-ENG' # Handles all bookcodes
    finally: self.setGenericBibleOrganisationalSystem( self.genericBibleOrganisationalSystemName )

    try: self.currentVerseKeyGroup = self.settings.data['BCVGroups']['currentGroup']
    except KeyError: self.currentVerseKeyGroup = 'A'

    try: self.GroupA_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['A-Book'],self.settings.data['BCVGroups']['A-Chapter'],self.settings.data['BCVGroups']['A-Verse'])
    except (KeyError,TypeError): self.GroupA_VerseKey = SimpleVerseKey( 'GEN', '1', '1' )
    try: self.GroupB_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['B-Book'],self.settings.data['BCVGroups']['B-Chapter'],self.settings.data['BCVGroups']['B-Verse'])
    except (KeyError,TypeError): self.GroupB_VerseKey = SimpleVerseKey( 'PSA', '119', '1' )
    try: self.GroupC_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['C-Book'],self.settings.data['BCVGroups']['C-Chapter'],self.settings.data['BCVGroups']['C-Verse'])
    except (KeyError,TypeError): self.GroupC_VerseKey = SimpleVerseKey( 'MAT', '1', '1' )
    try: self.GroupD_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['D-Book'],self.settings.data['BCVGroups']['D-Chapter'],self.settings.data['BCVGroups']['D-Verse'])
    except (KeyError,TypeError): self.GroupD_VerseKey = SimpleVerseKey( 'CO1', '12', '12' )
    try: self.GroupE_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['E-Book'],self.settings.data['BCVGroups']['E-Chapter'],self.settings.data['BCVGroups']['E-Verse'])
    except (KeyError,TypeError): self.GroupE_VerseKey = SimpleVerseKey( 'REV', '22', '1' )

    try: self.lexiconWord = self.settings.data['Lexicon']['currentWord']
    except KeyError: self.lexiconWord = None

    # We keep our copy of all the windows settings in self.windowsSettingsDict
    windowsSettingsNamesList = []
    for name in self.settings.data:
        if name.startswith( 'WindowSetting' ): windowsSettingsNamesList.append( name[13:] )
    if BibleOrgSysGlobals.debugFlag: print( "Available windows settings are: {}".format( windowsSettingsNamesList ) )
    if windowsSettingsNamesList: assert 'Current' in windowsSettingsNamesList
    self.windowsSettingsDict = {}
    for windowsSettingsName in windowsSettingsNamesList:
        self.windowsSettingsDict[windowsSettingsName] = retrieveWindowsSettings( self, windowsSettingsName )
    if 'Current' in windowsSettingsNamesList: applyGivenWindowsSettings( self, 'Current' )
    else: logging.critical( "Application.parseAndApplySettings: No current window settings available" )
# end of parseAndApplySettings



def applyGivenWindowsSettings( self, givenWindowsSettingsName ):
    """
    Given the name of windows settings,
        find the settings in our dictionary
        and then apply it by creating the windows.

    "self" refers to a Biblelator Application instance.
    """
    logging.debug( "applyGivenWindowsSettings( {} )".format( repr(givenWindowsSettingsName) ) )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "applyGivenWindowsSettings( {} )".format( repr(givenWindowsSettingsName) ) )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "applyGivenWindowsSettings…" )

    self.doCloseMyChildWindows()

    windowsSettingsFields = self.windowsSettingsDict[givenWindowsSettingsName]
    for j in range( 1, MAX_WINDOWS ):
        winNumber = 'window{}'.format( j )
        if winNumber in windowsSettingsFields:
            thisStuff = windowsSettingsFields[winNumber]
            windowType = thisStuff['Type']
            #windowGeometry = thisStuff['Geometry'] if 'Geometry' in thisStuff else None
            windowSize = thisStuff['Size'] if 'Size' in thisStuff else None
            windowPosition = thisStuff['Position'] if 'Position' in thisStuff else None
            windowGeometry = windowSize+'+'+windowPosition if windowSize and windowPosition else None
            #print( "applyGivenWindowsSettings", windowType, windowGeometry )

            if windowType == 'SwordBibleResourceWindow':
                rw = self.openSwordBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                #except: logging.critical( "Unable to read all SwordBibleResourceWindow {} settings".format( j ) )
            elif windowType == 'DBPBibleResourceWindow':
                rw = self.openDBPBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                #except: logging.critical( "Unable to read all DBPBibleResourceWindow {} settings".format( j ) )
            elif windowType == 'InternalBibleResourceWindow':
                folderPath = thisStuff['BibleFolderPath']
                if folderPath[-1] not in '/\\' \
                and not str(folderPath).endswith( ZIPPED_PICKLE_FILENAME_END ):
                    folderPath += '/'
                rw = self.openInternalBibleResourceWindow( folderPath, windowGeometry )
                #except: logging.critical( "Unable to read all InternalBibleResourceWindow {} settings".format( j ) )
            elif windowType == 'HebrewBibleResourceWindow':
                folderPath = thisStuff['BibleFolderPath']
                if folderPath[-1] not in '/\\' \
                and not str(folderPath).endswith( ZIPPED_PICKLE_FILENAME_END ):
                    folderPath += '/'
                rw = self.openHebrewBibleResourceWindow( folderPath, windowGeometry )

            #elif windowType == 'HebrewLexiconResourceWindow':
                #self.openHebrewLexiconResourceWindow( thisStuff['HebrewLexiconPath'], windowGeometry )
                ##except: logging.critical( "Unable to read all HebrewLexiconResourceWindow {} settings".format( j ) )
            #elif windowType == 'GreekLexiconResourceWindow':
                #self.openGreekLexiconResourceWindow( thisStuff['GreekLexiconPath'], windowGeometry )
                ##except: logging.critical( "Unable to read all GreekLexiconResourceWindow {} settings".format( j ) )
            elif windowType == 'BibleLexiconResourceWindow':
                rw = self.openBibleLexiconResourceWindow( thisStuff['BibleLexiconPath'], windowGeometry )
                #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )

            elif windowType == 'BibleResourceCollectionWindow':
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
                        if boxType and boxSource:
                            #if boxType in ( 'Internal', ):
                                #if boxSource[-1] not in '/\\': boxSource += '/' # Are they all folders -- might be wrong
                            rw.openBox( boxType, boxSource )

            elif windowType == 'BibleReferenceCollectionWindow':
                xyz = "JustTesting!"
                rw = self.openBibleReferenceCollectionWindow( xyz, windowGeometry )
                #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )

            elif windowType == 'PlainTextEditWindow':
                try: filepath = convertToPython( thisStuff['TextFilepath'] )
                except KeyError: filepath = None
                #if filepath == 'None': filepath = None
                rw = self.openFileTextEditWindow( filepath, windowGeometry )
                #except: logging.critical( "Unable to read all PlainTextEditWindow {} settings".format( j ) )
            elif windowType == 'BiblelatorUSFMBibleEditWindow':
                folderPath = thisStuff['ProjectFolderPath']
                if folderPath[-1] not in '/\\': folderPath += '/'
                rw = self.openBiblelatorBibleEditWindow( folderPath, thisStuff['EditMode'], windowGeometry )
                #except: logging.critical( "Unable to read all BiblelatorUSFMBibleEditWindow {} settings".format( j ) )
            elif windowType == 'Paratext8USFMBibleEditWindow':
                rw = self.openParatext8BibleEditWindow( thisStuff['ProjectFolder'], thisStuff['EditMode'], windowGeometry )
                #except: logging.critical( "Unable to read all Paratext8USFMBibleEditWindow {} settings".format( j ) )
            elif windowType == 'Paratext7USFMBibleEditWindow' \
            or windowType == 'ParatextUSFMBibleEditWindow': # This 2nd alternative can be deleted after a week or two
                rw = self.openParatext7BibleEditWindow( thisStuff['SSFFilepath'], thisStuff['EditMode'], windowGeometry )
                #except: logging.critical( "Unable to read all Paratext7USFMBibleEditWindow {} settings".format( j ) )
            elif windowType == 'ESFMEditWindow':
                folderPath = thisStuff['ESFMFolder']
                if folderPath[-1] not in '/\\': folderPath += '/'
                rw = self.openESFMEditWindow( folderPath, thisStuff['EditMode'], windowGeometry )
                #except: logging.critical( "Unable to read all ESFMEditWindow {} settings".format( j ) )

            else:
                logging.critical( "applyGivenWindowsSettings: " + _("Unknown {} window type").format( repr(windowType) ) )
                if BibleOrgSysGlobals.debugFlag: halt
                rw = None

            if rw is None:
                logging.critical( "applyGivenWindowsSettings: " + _("Failed to reopen {} window type!!! How did this happen?").format( repr(windowType) ) )
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
                    rw.setWindowGroup( groupCode )
                contextViewMode = thisStuff['ContextViewMode'] if 'ContextViewMode' in thisStuff else None
                if contextViewMode:
                    if BibleOrgSysGlobals.debugFlag: assert contextViewMode in BIBLE_CONTEXT_VIEW_MODES
                    rw.setContextViewMode( contextViewMode )
                    #rw.createMenuBar() # in order to show the correct contextViewMode
                formatViewMode = thisStuff['FormatViewMode'] if 'FormatViewMode' in thisStuff else None
                if formatViewMode:
                    if BibleOrgSysGlobals.debugFlag: assert formatViewMode in BIBLE_FORMAT_VIEW_MODES
                    rw.setFormatViewMode( formatViewMode )
                    #rw.createMenuBar() # in order to show the correct contextViewMode
                autocompleteMode = convertToPython( thisStuff['AutocompleteMode'] ) if 'AutocompleteMode' in thisStuff else None
                #if autocompleteMode == 'None': autocompleteMode = None
                if autocompleteMode:
                    if BibleOrgSysGlobals.debugFlag: assert windowType.endswith( 'EditWindow' )
                    rw.autocompleteMode = autocompleteMode
                    rw.prepareAutocomplete()
                statusBarMode = thisStuff['StatusBar'] if 'StatusBar' in thisStuff else None
                if statusBarMode:
                    statusBarOn = statusBarMode.lower() in ('on', 'true' ,'yes', 'enabled',)
                    rw.doToggleStatusBar( statusBarOn )
# end of applyGivenWindowsSettings



def getCurrentChildWindowSettings( self ):
    """
    Go through the currently open windows and get their settings data
        and save it in self.windowsSettingsDict['Current'].

    "self" refers to a Biblelator Application instance.
    """
    logging.debug( "getCurrentChildWindowSettings()" )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "getCurrentChildWindowSettings()" )

    if 'Current' in self.windowsSettingsDict: del self.windowsSettingsDict['Current']
    self.windowsSettingsDict['Current'] = {}
    for j, appWin in enumerate( self.childWindows ):
        if appWin.windowType in ( 'HTMLWindow', 'FindResultWindow' ):
            continue # We don't save these

        winNumber = "window{}".format( j+1 )
        self.windowsSettingsDict['Current'][winNumber] = {}
        thisOne = self.windowsSettingsDict['Current'][winNumber]
        thisOne['Type'] = appWin.windowType #.replace( 'Window', 'Window' )
        if 0 and debuggingThisModule:
            print( "Child", j, appWin.genericWindowType, appWin.windowType )
            print( "  child geometry", appWin.geometry(), "child winfo_geometry", appWin.winfo_geometry() )
            #print( "  child winfo x", appWin.winfo_x(), "child winfo rootx", appWin.winfo_rootx() )
            #print( "  child winfo y", appWin.winfo_y(), "child winforooty", appWin.winfo_rooty() )
            #print( "  child height", appWin.winfo_height(), "child reqheight", appWin.winfo_reqheight() )
            #print( "  child width", appWin.winfo_width(), "child reqwidth", appWin.winfo_reqwidth() )
        thisOne['Size'], thisOne['Position'] = appWin.geometry().split( '+', 1 )
        if thisOne['Position'] == '0+0': # not sure why this occurs for a new window -- pops up top left
            thisOne['Position'] = appWin.winfo_geometry().split( '+', 1 )[1] # Won't be exact but close
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "Corrected {} window position from '0+0' to {}".format( appWin.windowType, thisOne['Position'] ) )
        thisOne['MinimumSize'] = assembleWindowSize( *appWin.minsize() )
        thisOne['MaximumSize'] = assembleWindowSize( *appWin.maxsize() )
        thisOne['StatusBar'] = 'On' if appWin._showStatusBarVar.get() else 'Off'

        if appWin.windowType == 'SwordBibleResourceWindow':
            thisOne['ModuleAbbreviation'] = appWin.moduleID
        elif appWin.windowType == 'DBPBibleResourceWindow':
            thisOne['ModuleAbbreviation'] = appWin.moduleID
        elif appWin.windowType == 'InternalBibleResourceWindow':
            thisOne['BibleFolderPath'] = appWin.moduleID
        elif appWin.windowType == 'HebrewBibleResourceWindow':
            thisOne['BibleFolderPath'] = appWin.moduleID

        elif appWin.windowType == 'BibleLexiconResourceWindow':
            thisOne['BibleLexiconPath'] = appWin.moduleID

        elif appWin.windowType == 'BibleResourceCollectionWindow':
            thisOne['CollectionName'] = appWin.moduleID
        elif appWin.windowType == 'BibleReferenceCollectionWindow':
            print( "WARNING: Doesn't save BibleReferenceCollectionWindow yet!" )
            #thisOne['CollectionName'] = appWin.moduleID # Just copied -- not checked

        elif appWin.windowType == 'PlainTextEditWindow':
            try: thisOne['TextFilepath'] = appWin.filepath
            except AttributeError: pass # It's possible to have a blank new text edit window open

        elif appWin.windowType == 'BiblelatorUSFMBibleEditWindow':
            thisOne['ProjectFolderPath'] = appWin.moduleID
            thisOne['EditMode'] = appWin.editMode
        elif appWin.windowType == 'Paratext8USFMBibleEditWindow':
            thisOne['ProjectFolder'] = appWin.moduleID
            thisOne['EditMode'] = appWin.editMode
        elif appWin.windowType == 'Paratext7USFMBibleEditWindow':
            thisOne['SSFFilepath'] = appWin.moduleID
            thisOne['EditMode'] = appWin.editMode

        else:
            logging.critical( "getCurrentChildWindowSettings: " + _("Unknown {} window type").format( repr(appWin.windowType) ) )
            if BibleOrgSysGlobals.debugFlag: halt

        if 'Bible' in appWin.genericWindowType:
            try: thisOne['GroupCode'] = appWin._groupCode
            except AttributeError: logging.critical( "getCurrentChildWindowSettings: " + _("Why no groupCode in {}").format( appWin.windowType ) )
            try: thisOne['ContextViewMode'] = appWin._contextViewMode
            except AttributeError: logging.critical( "getCurrentChildWindowSettings: " + _("Why no contextViewMode in {}").format( appWin.windowType ) )
            try: thisOne['FormatViewMode'] = appWin._formatViewMode
            except AttributeError: logging.critical( "getCurrentChildWindowSettings: " + _("Why no formatViewMode in {}").format( appWin.windowType ) )

        if appWin.windowType.endswith( 'EditWindow' ):
            thisOne['AutocompleteMode'] = appWin.autocompleteMode
# end of getCurrentChildWindowSettings



def saveNewWindowSetup( self ):
    """
    Gets the name for the new window setup and saves the information.

    "self" refers to a Biblelator Application instance.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( "saveNewWindowSetup()" )
        self.setDebugText( "saveNewWindowSetup…" )

    swnd = SaveWindowsLayoutNameDialog( self, self.windowsSettingsDict, title=_('Save window setup') )
    if BibleOrgSysGlobals.debugFlag: print( "swndResult", repr(swnd.result) )
    if swnd.result:
        getCurrentChildWindowSettings( self )
        self.windowsSettingsDict[swnd.result] = self.windowsSettingsDict['Current'] # swnd.result is the new window name
        #print( "swS", self.windowsSettingsDict )
        writeSettingsFile( self ) # Save file now in case we crash
        self.createMenuBar() # refresh
# end of saveNewWindowSetup



def deleteExistingWindowSetup( self ):
    """
    Gets the name of an existing window setting and deletes the setting.

    "self" refers to a Biblelator Application instance.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( "deleteExistingWindowSetup()" )
        self.setDebugText( "deleteExistingWindowSetup" )
        assert self.windowsSettingsDict and (len(self.windowsSettingsDict)>1 or 'Current' not in self.windowsSettingsDict)

    dwnd = DeleteWindowsLayoutNameDialog( self, self.windowsSettingsDict, title=_('Delete saved window setup') )
    if BibleOrgSysGlobals.debugFlag: print( "dwndResult", repr(dwnd.result) )
    if dwnd.result:
        if BibleOrgSysGlobals.debugFlag:
            assert dwnd.result in self.windowsSettingsDict
        del self.windowsSettingsDict[dwnd.result]
        self.settings.save() # Save file now in case we crash ###-- don't worry -- it's easy to delete one
        self.createMenuBar() # refresh
# end of deleteExistingWindowSetup



def viewSettings( self ):
    """
    Open a pop-up text window with the current settings displayed.

    "self" refers to a Biblelator Application instance.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( "viewSettings()" )
        self.setDebugText( "viewSettings" )

    tEW = TextEditWindow( self )
    #if windowGeometry: tEW.geometry( windowGeometry )
    if not tEW.setFilepath( self.settings.settingsFilepath ) \
    or not tEW.loadText():
        tEW.doClose()
        showError( self, APP_NAME, _("Sorry, unable to open settings file") )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed viewSettings" )
    else:
        self.childWindows.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished viewSettings" )
    self.setReadyStatus()
# end of viewSettings


def writeSettingsFile( self ):
    """
    Update our program settings and save them.

    "self" refers to a Biblelator Application instance.
    """
    logging.info( "writeSettingsFile()" )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "writeSettingsFile()" )
    elif BibleOrgSysGlobals.verbosityLevel > 0:
        print( _("  Saving program settings…") )

    def convertToString( setting ):
        """
        Takes special Python values and converts them to strings.
        """
        if setting is None: return 'None'
        if setting == True: return 'True'
        if setting == False: return 'False'
        return setting
    # end of convertToString

    # Main code for writeSettingsFile()
    if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'writeSettingsFile' )
    self.settings.reset()

    self.settings.data[APP_NAME] = {}
    mainStuff = self.settings.data[APP_NAME]
    mainStuff['settingsVersion'] = SettingsVersion
    mainStuff['PROGRAM_VERSION'] = PROGRAM_VERSION
    mainStuff['themeName'] = self.themeName
    if 0 and debuggingThisModule:
        print( " root geometry", self.rootWindow.geometry(), "root winfo_geometry", self.rootWindow.winfo_geometry() )
        print( " root winfo x", self.rootWindow.winfo_x(), "root winfo rootx", self.rootWindow.winfo_rootx() )
        print( " root winfo y", self.rootWindow.winfo_y(), "root winfo rooty", self.rootWindow.winfo_rooty() )
    mainStuff['windowSize'], mainStuff['windowPosition'] = self.rootWindow.geometry().split( '+', 1 )
    # Seems that winfo_geometry doesn't work above (causes root Window to move)
    mainStuff['minimumSize'] = self.minimumSize
    mainStuff['maximumSize'] = self.maximumSize
    if 0 and debuggingThisModule:
        print( " saved size (across/down) to ini file", repr(mainStuff['windowSize']), "pos", repr(mainStuff['windowPosition']) )
        print( "   min", repr(mainStuff['minimumSize']), "max", repr(mainStuff['maximumSize']) )

    # Save the user interface settings
    self.settings.data['Interface'] = {}
    interface = self.settings.data['Interface']
    interface['interfaceLanguage'] = self.interfaceLanguage
    interface['interfaceComplexity'] = self.interfaceComplexity
    interface['touchMode'] = convertToString( self.touchMode )
    interface['tabletMode'] = convertToString( self.tabletMode )
    interface['showDebugMenu'] = convertToString( self.showDebugMenu )

    # Save the Internet access controls
    self.settings.data['Internet'] = {}
    internet = self.settings.data['Internet']
    internet['internetAccess'] = 'Enabled' if self.internetAccessEnabled else 'Disabled'
    internet['internetFast'] = 'True' if self.internetFast else 'False'
    internet['internetExpensive'] = 'True' if self.internetExpensive else 'False'
    internet['cloudBackups'] = 'Enabled' if self.cloudBackupsEnabled else 'Disabled'
    internet['checkForDeveloperMessages'] = 'Enabled' if self.checkForDeveloperMessagesEnabled else 'Disabled'
    internet['lastMessageNumberRead'] = str( self.lastMessageNumberRead )
    internet['sendUsageStatistics'] = 'Enabled' if self.sendUsageStatisticsEnabled else 'Disabled'
    internet['automaticUpdates'] = 'Enabled' if self.automaticUpdatesEnabled else 'Disabled'
    internet['useDevelopmentVersions'] = 'Enabled' if self.useDevelopmentVersionsEnabled else 'Disabled'

    # Save the project information
    self.settings.data['Project'] = {}
    users = self.settings.data['Project']
    users['currentProjectName'] = self.currentProjectName

    # Save the user information
    self.settings.data['Users'] = {}
    users = self.settings.data['Users']
    users['currentUserName'] = self.currentUserName
    users['currentUserInitials'] = self.currentUserInitials
    users['currentUserEmail'] = self.currentUserEmail
    users['currentUserRole'] = self.currentUserRole
    users['currentUserAssignments'] = self.currentUserAssignments

    # Save the last paths
    self.settings.data['Paths'] = {}
    paths = self.settings.data['Paths']
    paths['lastFileDir'] = str(self.lastFileDir)
    paths['lastBiblelatorFileDir'] = str(self.lastBiblelatorFileDir)
    paths['lastParatextFileDir'] = str(self.lastParatextFileDir)
    paths['lastInternalBibleDir'] = str(self.lastInternalBibleDir)
    paths['lastSwordDir'] = str(self.lastSwordDir)

    # Save the recent files
    self.settings.data['RecentFiles'] = {}
    recent = self.settings.data['RecentFiles']
    for j, (filename,folder,windowType) in enumerate( self.recentFiles ):
        recentName = 'recent{}'.format( j+1 )
        recent[recentName+'Filename'] = convertToString( filename )
        recent[recentName+'Folder'] = convertToString( folder )
        recent[recentName+'Type'] = windowType

    # Save the referenceGroups A..D
    self.settings.data['BCVGroups'] = {}
    groups = self.settings.data['BCVGroups']
    groups['genericBibleOrganisationalSystemName'] = self.genericBibleOrganisationalSystemName
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
    groups['E-Book'] = self.GroupE_VerseKey[0]
    groups['E-Chapter'] = self.GroupE_VerseKey[1]
    groups['E-Verse'] = self.GroupE_VerseKey[2]

    # Save the lexicon info
    self.settings.data['Lexicon'] = {}
    lexicon = self.settings.data['Lexicon']
    if self.lexiconWord: lexicon['currentWord'] = self.lexiconWord

    # Save any open Bible resource collections
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "save collection data…" )
    for appWin in self.childWindows:
        #print( "  gT", appWin.genericWindowType )
        #print( "  wT", appWin.windowType )
        if appWin.windowType == 'BibleResourceCollectionWindow':
            if appWin.resourceBoxesList: # so we don't create just an empty heading for an empty collection
                self.settings.data['BibleResourceCollection'+appWin.moduleID] = {}
                thisOne = self.settings.data['BibleResourceCollection'+appWin.moduleID]
                #print( "  found", appWin.moduleID )
                for j, box in enumerate( appWin.resourceBoxesList ):
                    boxNumber = 'box{}'.format( j+1 )
                    #print( "    bT", box.boxType )
                    #print( "    ID", box.moduleID )
                    thisOne[boxNumber+'Type'] = box.boxType.replace( 'BibleResourceBox', '' )
                    thisOne[boxNumber+'Source'] = box.moduleID

    # Get the current child window settings
    getCurrentChildWindowSettings( self )
    # Save all the various window set-ups including both the named ones and the current one
    for windowsSettingName in sorted( self.windowsSettingsDict ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "Saving windows set-up {}".format( repr(windowsSettingName) ) )
        try: # Just in case something goes wrong with characters in a settings name
            self.settings.data['WindowSetting'+windowsSettingName] = {}
            thisOne = self.settings.data['WindowSetting'+windowsSettingName]
            for windowNumber,winDict in sorted( self.windowsSettingsDict[windowsSettingName].items() ):
                #print( "  ", repr(windowNumber), repr(winDict) )
                for windowSettingName,value in sorted( winDict.items() ):
                    thisOne[windowNumber+windowSettingName] = convertToString( value )
        except UnicodeEncodeError: logging.error( "writeSettingsFile: " + _("unable to write {} windows set-up").format( repr(windowsSettingName) ) )
    self.settings.save()
# end of writeSettingsFile



MIME_BOUNDARY = 'sdafsZXXdahxcvblkDSFSDFjeflqwertlSDFSDFjkre' # Random string that won't occur in our data
def doSendUsageStatistics( self ):
    """
    Send (POST) usage statistics over the Internet.

    "self" refers to a Biblelator Application instance.

    Note that Biblelator is mostly closed down at this stage.
    """
    if BibleOrgSysGlobals.debugFlag:
        print( "doSendUsageStatistics()" )
        assert self.internetAccessEnabled
        assert self.sendUsageStatisticsEnabled
    elif BibleOrgSysGlobals.verbosityLevel > 0:
        print( _("  Sending program usage info…") )

    adjAppName = APP_NAME.replace('/','-').replace(':','_').replace('\\','_').replace(' ','_')
    adjUserName = self.currentUserName.replace('/','-').replace(':','_').replace('\\','_')

    # Package our stuff up into a zip file
    import tempfile, zipfile
    zipFilepath = os.path.join( tempfile.gettempdir(), adjAppName+'.zip' )
    #print( "zipF0", repr(zipFilepath) )
    zf = zipfile.ZipFile( zipFilepath, 'w', compression=zipfile.ZIP_DEFLATED )

    # Add log file(s)
    filename = adjAppName + '_log.txt'
    #print( "zipF1", repr(self.loggingFolderPath) )
    #print( "zipF2", repr(filename) )
    for extension in BibleOrgSysGlobals.STANDARD_BACKUP_EXTENSIONS:
        filepath = os.path.join( self.loggingFolderPath, filename+extension )
        #print( "  zipF3", repr(filepath) )
        if os.path.exists( filepath ):
            #print( "  zipF4", repr(filepath) )
            zf.write( filepath, filename+extension )

    # Add usage file(s)
    zf.write( self.usageLogPath, self.usageFilename )

    # Add settings file(s)
    #print( "zipF5", repr(self.settings.settingsFilepath) )
    #print( "zipF6", repr(self.settings.settingsFilename) )
    for extension in BibleOrgSysGlobals.STANDARD_BACKUP_EXTENSIONS:
        filepath = self.settings.settingsFilepath+extension
        #print( "  zipF7", repr(filepath) )
        if os.path.exists( filepath ):
            #print( "  zipF8", repr(filepath) )
            zf.write( filepath, self.settings.settingsFilename+extension )
    zf.close()
    with open( zipFilepath, 'rb' ) as zFile:
        zData = zFile.read()
    os.remove( zipFilepath )
    zDataStr = zData.decode('latin-1') # Make extended ASCII bytes into str

    # Post the zip file to our server
    parameterList = []
    parameterList.extend( ('--' + MIME_BOUNDARY, "Content-Disposition: form-data; name=nameLine",
                           '', self.currentUserName ) )
    parameterList.extend( ('--' + MIME_BOUNDARY, "Content-Disposition: form-data; name=emailLine",
                           '', self.currentUserEmail ) )
    parameterList.extend( ('--' + MIME_BOUNDARY, "Content-Disposition: form-data; name=projectLine",
                           '', self.currentProjectName ) )
    parameterList.extend( ('--' + MIME_BOUNDARY,
                    'Content-Disposition: form-data; name=uploadedZipFile; filename="{}.zip"'.format( adjUserName ),
                    'Content-Type: application/zip', '', zDataStr ) )
    parameterList.extend( ('--' + MIME_BOUNDARY + '--' , '') )
    parameterString = '\r\n'.join (parameterList)
    #print( "\nparameterString", repr(parameterString) )

    headers = {"Content-type": "multipart/form-data; MIME_BOUNDARY={}".format( MIME_BOUNDARY ) }
    #print( "\nheaders", headers )

    import http.client
    conn = http.client.HTTPConnection( 'Freely-Given.org' )
    conn.request( 'POST', '/Software/Biblelator/StatusInputs/SubmitAction.phtml', parameterString, headers )
    try: response = conn.getresponse()
    except http.client.RemoteDisconnected:
        print( "doSendUsageStatistics remote RemoteDisconnected -- send failed" )
        conn.close()
        return
    if response.status == 200:
        print( "    doSendUsageStatistics accepted by server" )
    else:
        print( "doSendUsageStatistics status", repr(response.status) ) # Should be 200
        print( "doSendUsageStatistics reason", repr(response.reason) ) # Should be 'OK'
        data = response.read()
        print( "doSendUsageStatistics data", repr(data) ) # Web page back from the server
    conn.close()
# end of doSendUsageStatistics



def demo() -> None:
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    import sys, tkinter as tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    if BibleOrgSysGlobals.debugFlag:
        print( "Platform is", sys.platform ) # e.g., "win32"
        print( "OS name is", os.name ) # e.g., "nt"
        if sys.platform == "linux": print( "OS uname is", os.uname() )
        print( "Running main…" )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( programNameVersion )

    homeFolderPath = BibleOrgSysGlobals.findHomeFolderPath()
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, APP_NAME )
    settings.load()

    application = Application( tkRootWindow, homeFolderPath, loggingFolderPath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BiblelatorSettingsFunctions.py
