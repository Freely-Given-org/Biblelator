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
    parseAndApplySettings()
    applyGivenWindowsSettings( givenWindowsSettingsName )
    getCurrentChildWindowSettings()
    saveNewWindowSetup()
    deleteExistingWindowSetup()
    viewSettings()
    writeSettingsFile()
    doSendUsageStatistics()
    fullDemo()
"""
from gettext import gettext as _
import os
from pathlib import Path
import logging

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Formats.PickledBible import ZIPPED_PICKLE_FILENAME_END

# Biblelator imports
if __name__ == '__main__':
    import sys
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator import BiblelatorGlobals
from Biblelator.BiblelatorGlobals import APP_NAME, DEFAULT, \
    DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, \
    MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE, MAX_WINDOWS, MAX_RECENT_FILES, \
    BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, \
    parseWindowSize, assembleWindowSize
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError
from Biblelator.Dialogs.BiblelatorDialogs import SaveWindowsLayoutNameDialog, DeleteWindowsLayoutNameDialog
from Biblelator.Windows.TextEditWindow import TextEditWindow


LAST_MODIFIED_DATE = '2020-05-10' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorSettingsFunctions"
PROGRAM_NAME = "Biblelator Settings Functions"
PROGRAM_VERSION = '0.46'
SettingsVersion = '0.46' # Only need to change this if the settings format has changed
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False



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



def parseAndApplySettings() -> None:
    """
    Parse the settings out of the .INI file.
    """
    logging.info( "parseAndApplySettings()" )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "parseAndApplySettings()" )
        if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "parseAndApplySettings…" )

    def retrieveWindowsSettings( windowsSettingsName:str ):
        """
        Gets a certain windows settings from the settings (INI) file information
            and puts it into a dictionary.

        Returns the dictionary.

        Called from parseAndApplySettings().
        """
        if BibleOrgSysGlobals.debugFlag:
            vPrint( 'Quiet', debuggingThisModule, "retrieveWindowsSettings( {} )".format( repr(windowsSettingsName) ) )
            if debuggingThisModule: BiblelatorGlobals.theApp.setDebugText( "retrieveWindowsSettings…" )
        windowsSettingsFields = BiblelatorGlobals.theApp.settings.data['WindowSetting'+windowsSettingsName]
        resultDict = {}
        for j in range( 1, MAX_WINDOWS+1 ):
            winNumber = 'window{}'.format( j )
            for keyName in windowsSettingsFields:
                if keyName.startswith( winNumber ):
                    if winNumber not in resultDict: resultDict[winNumber] = {}
                    resultDict[winNumber][keyName[len(winNumber):]] = windowsSettingsFields[keyName]
        #dPrint( 'Quiet', debuggingThisModule, "retrieveWindowsSettings", resultDict )
        return resultDict
    # end of retrieveWindowsSettings


    # Main code for parseAndApplySettings()
    # Parse main app stuff
    #try: BiblelatorGlobals.theApp.rootWindow.geometry( BiblelatorGlobals.theApp.settings.data[APP_NAME]['windowGeometry'] )
    #except KeyError: vPrint( 'Quiet', debuggingThisModule, "KeyError1" ) # we had no geometry set
    #except tk.TclError: logging.critical( "Application.__init__: Bad window geometry in settings file: {}".format( settings.data[APP_NAME]['windowGeometry'] ) )
    try:
        windowSize = BiblelatorGlobals.theApp.settings.data[APP_NAME]['windowSize'] if 'windowSize' in BiblelatorGlobals.theApp.settings.data[APP_NAME] else None
        windowPosition = BiblelatorGlobals.theApp.settings.data[APP_NAME]['windowPosition'] if 'windowPosition' in BiblelatorGlobals.theApp.settings.data[APP_NAME] else None
        if 0 and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "main window settings (across/down from ini file) size", repr(windowSize), "pos", repr(windowPosition) )
        if windowSize and windowPosition:
            BiblelatorGlobals.theApp.update() # Make sure that the window has finished being created
            BiblelatorGlobals.theApp.rootWindow.geometry( windowSize + '+' + windowPosition )
        else: logging.warning( "Settings.KeyError: no windowSize & windowPosition" )
    except KeyError: pass # no [APP_NAME] entries

    try: BiblelatorGlobals.theApp.minimumSize = BiblelatorGlobals.theApp.settings.data[APP_NAME]['minimumSize']
    except KeyError: BiblelatorGlobals.theApp.minimumSize = MINIMUM_MAIN_SIZE
    BiblelatorGlobals.theApp.rootWindow.minsize( *parseWindowSize( BiblelatorGlobals.theApp.minimumSize ) )
    try: BiblelatorGlobals.theApp.maximumSize = BiblelatorGlobals.theApp.settings.data[APP_NAME]['maximumSize']
    except KeyError: BiblelatorGlobals.theApp.maximumSize = MAXIMUM_MAIN_SIZE
    BiblelatorGlobals.theApp.rootWindow.maxsize( *parseWindowSize( BiblelatorGlobals.theApp.maximumSize ) )
    if 0 and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "  apply min", repr(BiblelatorGlobals.theApp.minimumSize), repr(parseWindowSize(BiblelatorGlobals.theApp.minimumSize)), "max", repr(BiblelatorGlobals.theApp.maximumSize), repr(parseWindowSize(BiblelatorGlobals.theApp.maximumSize)) )

    try: BiblelatorGlobals.theApp.doChangeTheme( BiblelatorGlobals.theApp.settings.data[APP_NAME]['themeName'] )
    except KeyError: logging.warning( "Settings.KeyError: no themeName" )

    # Parse Interface stuff
    try: BiblelatorGlobals.theApp.interfaceLanguage = BiblelatorGlobals.theApp.settings.data['Interface']['interfaceLanguage']
    except KeyError: BiblelatorGlobals.theApp.interfaceLanguage = DEFAULT
    if BibleOrgSysGlobals.debugFlag: assert BiblelatorGlobals.theApp.interfaceLanguage in ( DEFAULT, )
    try: BiblelatorGlobals.theApp.interfaceComplexity = BiblelatorGlobals.theApp.settings.data['Interface']['interfaceComplexity']
    except KeyError: BiblelatorGlobals.theApp.interfaceComplexity = DEFAULT
    if BibleOrgSysGlobals.debugFlag: assert BiblelatorGlobals.theApp.interfaceComplexity in ( DEFAULT, 'Basic', 'Advanced', )
    try: BiblelatorGlobals.theApp.touchMode = convertToPython( BiblelatorGlobals.theApp.settings.data['Interface']['touchMode'] )
    except KeyError: BiblelatorGlobals.theApp.touchMode = False
    if BibleOrgSysGlobals.debugFlag: assert BiblelatorGlobals.theApp.touchMode in ( False, True )
    try: BiblelatorGlobals.theApp.tabletMode = convertToPython( BiblelatorGlobals.theApp.settings.data['Interface']['tabletMode'] )
    except KeyError: BiblelatorGlobals.theApp.tabletMode = False
    if BibleOrgSysGlobals.debugFlag: assert BiblelatorGlobals.theApp.tabletMode in ( False, True )
    try: BiblelatorGlobals.theApp.showDebugMenu = convertToPython( BiblelatorGlobals.theApp.settings.data['Interface']['showDebugMenu'] )
    except KeyError: BiblelatorGlobals.theApp.showDebugMenu = False
    if BibleOrgSysGlobals.debugFlag: assert BiblelatorGlobals.theApp.showDebugMenu in ( False, True )

    # Parse Internet stuff
    try:
        internetAccessString = BiblelatorGlobals.theApp.settings.data['Internet']['internetAccess']
        BiblelatorGlobals.theApp.internetAccessEnabled = internetAccessString == 'Enabled'
    except KeyError: BiblelatorGlobals.theApp.internetAccessEnabled = False # default
    try:
        fastString = BiblelatorGlobals.theApp.settings.data['Internet']['internetFast']
        BiblelatorGlobals.theApp.internetFast = fastString.lower() in ('true' ,'yes',)
    except KeyError: BiblelatorGlobals.theApp.internetFast = True # default
    try:
        expensiveString = BiblelatorGlobals.theApp.settings.data['Internet']['internetExpensive']
        BiblelatorGlobals.theApp.internetExpensive = expensiveString.lower() in ('true' ,'yes',)
    except KeyError: BiblelatorGlobals.theApp.internetExpensive = True # default
    try:
        cloudBackupsString = BiblelatorGlobals.theApp.settings.data['Internet']['cloudBackups']
        BiblelatorGlobals.theApp.cloudBackupsEnabled = cloudBackupsString == 'Enabled'
    except KeyError: BiblelatorGlobals.theApp.cloudBackupsEnabled = True # default
    try:
        checkForMessagesString = BiblelatorGlobals.theApp.settings.data['Internet']['checkForDeveloperMessages']
        BiblelatorGlobals.theApp.checkForDeveloperMessagesEnabled = checkForMessagesString == 'Enabled'
    except KeyError: BiblelatorGlobals.theApp.checkForDeveloperMessagesEnabled = True # default
    try:
        lastMessageNumberString = BiblelatorGlobals.theApp.settings.data['Internet']['lastMessageNumberRead']
        BiblelatorGlobals.theApp.lastMessageNumberRead = int( lastMessageNumberString )
    except (KeyError, ValueError): BiblelatorGlobals.theApp.lastMessageNumberRead = 0
    else:
        if BiblelatorGlobals.theApp.lastMessageNumberRead < 0: BiblelatorGlobals.theApp.lastMessageNumberRead = 0 # Handle errors in ini file
    try:
        sendUsageStatisticsString = BiblelatorGlobals.theApp.settings.data['Internet']['sendUsageStatistics']
        BiblelatorGlobals.theApp.sendUsageStatisticsEnabled = sendUsageStatisticsString == 'Enabled'
    except KeyError: BiblelatorGlobals.theApp.sendUsageStatisticsEnabled = True # default
    try:
        automaticUpdatesString = BiblelatorGlobals.theApp.settings.data['Internet']['automaticUpdates']
        BiblelatorGlobals.theApp.automaticUpdatesEnabled = automaticUpdatesString == 'Enabled'
    except KeyError: BiblelatorGlobals.theApp.automaticUpdatesEnabled = True # default
    try:
        useDevelopmentVersionsString = BiblelatorGlobals.theApp.settings.data['Internet']['useDevelopmentVersions']
        BiblelatorGlobals.theApp.useDevelopmentVersionsEnabled = useDevelopmentVersionsString == 'Enabled'
    except KeyError: BiblelatorGlobals.theApp.useDevelopmentVersionsEnabled = False # default

    # Parse project info
    try: BiblelatorGlobals.theApp.currentProjectName = BiblelatorGlobals.theApp.settings.data['Project']['currentProjectName']
    except KeyError: pass # use program default

    # Parse users
    try: BiblelatorGlobals.theApp.currentUserName = BiblelatorGlobals.theApp.settings.data['Users']['currentUserName']
    except KeyError: pass # use program default
    try: BiblelatorGlobals.theApp.currentUserInitials = BiblelatorGlobals.theApp.settings.data['Users']['currentUserInitials']
    except KeyError: pass # use program default
    try: BiblelatorGlobals.theApp.currentUserEmail = BiblelatorGlobals.theApp.settings.data['Users']['currentUserEmail']
    except KeyError: pass # use program default
    try: BiblelatorGlobals.theApp.currentUserRole = BiblelatorGlobals.theApp.settings.data['Users']['currentUserRole']
    except KeyError: pass # use program default
    try: BiblelatorGlobals.theApp.currentUserAssignments = BiblelatorGlobals.theApp.settings.data['Users']['currentUserAssignments']
    except KeyError: pass # use program default

    # Parse paths
    try: BiblelatorGlobals.theApp.lastFileDir = BiblelatorGlobals.theApp.settings.data['Paths']['lastFileDir']
    except KeyError: pass # use program default
    finally:
        if str(BiblelatorGlobals.theApp.lastFileDir)[-1] not in '/\\':
            BiblelatorGlobals.theApp.lastFileDir = f'{BiblelatorGlobals.theApp.lastFileDir}/'
    try: BiblelatorGlobals.theApp.lastBiblelatorFileDir = BiblelatorGlobals.theApp.settings.data['Paths']['lastBiblelatorFileDir']
    except KeyError: pass # use program default
    finally:
        if str(BiblelatorGlobals.theApp.lastBiblelatorFileDir)[-1] not in '/\\':
            BiblelatorGlobals.theApp.lastBiblelatorFileDir = f'{BiblelatorGlobals.theApp.lastBiblelatorFileDir}/'
    try: BiblelatorGlobals.theApp.lastParatextFileDir = BiblelatorGlobals.theApp.settings.data['Paths']['lastParatextFileDir']
    except KeyError: pass # use program default
    finally:
        if str(BiblelatorGlobals.theApp.lastParatextFileDir)[-1] not in '/\\':
            BiblelatorGlobals.theApp.lastParatextFileDir = f'{BiblelatorGlobals.theApp.lastParatextFileDir}/'
    try: BiblelatorGlobals.theApp.lastInternalBibleDir = BiblelatorGlobals.theApp.settings.data['Paths']['lastInternalBibleDir']
    except KeyError: pass # use program default
    finally:
        if str(BiblelatorGlobals.theApp.lastInternalBibleDir)[-1] not in '/\\':
            BiblelatorGlobals.theApp.lastInternalBibleDir = f'{BiblelatorGlobals.theApp.lastInternalBibleDir}/'
    try: BiblelatorGlobals.theApp.lastSwordDir = BiblelatorGlobals.theApp.settings.data['Paths']['lastSwordDir']
    except KeyError: pass # use program default
    finally:
        if str(BiblelatorGlobals.theApp.lastSwordDir)[-1] not in '/\\':
            BiblelatorGlobals.theApp.lastSwordDir = f'{BiblelatorGlobals.theApp.lastSwordDir}/'

    # Parse recent files
    assert not BiblelatorGlobals.theApp.recentFiles
    try: recentFields = BiblelatorGlobals.theApp.settings.data['RecentFiles']
    except KeyError: recentFields = None
    if recentFields: # in settings file
        for j in range( 1, MAX_RECENT_FILES+1 ):
            recentName = f'recent{j}'
            for keyName in recentFields:
                if keyName.startswith( recentName ): # This index number (j) is present
                    filename = convertToPython( BiblelatorGlobals.theApp.settings.data['RecentFiles']['recent{}Filename'.format( j )] )
                    #if filename == 'None': filename = None
                    folder = convertToPython( BiblelatorGlobals.theApp.settings.data['RecentFiles']['recent{}Folder'.format( j )] )
                    #if folder == 'None': folder = None
                    if folder and str(folder)[-1] not in '/\\':
                        folder = f'{folder}/'
                    windowType = BiblelatorGlobals.theApp.settings.data['RecentFiles']['recent{}Type'.format( j )]
                    BiblelatorGlobals.theApp.recentFiles.append( (filename,folder,windowType) )
                    assert len(BiblelatorGlobals.theApp.recentFiles) == j
                    break # go to next j

    # Parse BCV groups
    try: BiblelatorGlobals.theApp.genericBibleOrganisationalSystemName = BiblelatorGlobals.theApp.settings.data['BCVGroups']['genericBibleOrganisationalSystemName']
    #except KeyError: pass # use program default
    except KeyError: BiblelatorGlobals.theApp.genericBibleOrganisationalSystemName = 'GENERIC-KJV-ENG' # Handles all bookcodes
    finally: BiblelatorGlobals.theApp.setGenericBibleOrganisationalSystem( BiblelatorGlobals.theApp.genericBibleOrganisationalSystemName )

    try: BiblelatorGlobals.theApp.currentVerseKeyGroup = BiblelatorGlobals.theApp.settings.data['BCVGroups']['currentGroup']
    except KeyError: BiblelatorGlobals.theApp.currentVerseKeyGroup = 'A'

    try: BiblelatorGlobals.theApp.GroupA_VerseKey = SimpleVerseKey(BiblelatorGlobals.theApp.settings.data['BCVGroups']['A-Book'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['A-Chapter'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['A-Verse'])
    except (KeyError,TypeError): BiblelatorGlobals.theApp.GroupA_VerseKey = SimpleVerseKey( 'GEN', '1', '1' )
    try: BiblelatorGlobals.theApp.GroupB_VerseKey = SimpleVerseKey(BiblelatorGlobals.theApp.settings.data['BCVGroups']['B-Book'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['B-Chapter'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['B-Verse'])
    except (KeyError,TypeError): BiblelatorGlobals.theApp.GroupB_VerseKey = SimpleVerseKey( 'PSA', '119', '1' )
    try: BiblelatorGlobals.theApp.GroupC_VerseKey = SimpleVerseKey(BiblelatorGlobals.theApp.settings.data['BCVGroups']['C-Book'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['C-Chapter'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['C-Verse'])
    except (KeyError,TypeError): BiblelatorGlobals.theApp.GroupC_VerseKey = SimpleVerseKey( 'MAT', '1', '1' )
    try: BiblelatorGlobals.theApp.GroupD_VerseKey = SimpleVerseKey(BiblelatorGlobals.theApp.settings.data['BCVGroups']['D-Book'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['D-Chapter'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['D-Verse'])
    except (KeyError,TypeError): BiblelatorGlobals.theApp.GroupD_VerseKey = SimpleVerseKey( 'CO1', '12', '12' )
    try: BiblelatorGlobals.theApp.GroupE_VerseKey = SimpleVerseKey(BiblelatorGlobals.theApp.settings.data['BCVGroups']['E-Book'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['E-Chapter'],BiblelatorGlobals.theApp.settings.data['BCVGroups']['E-Verse'])
    except (KeyError,TypeError): BiblelatorGlobals.theApp.GroupE_VerseKey = SimpleVerseKey( 'REV', '22', '1' )

    try: BiblelatorGlobals.theApp.lexiconWord = BiblelatorGlobals.theApp.settings.data['Lexicon']['currentWord']
    except KeyError: BiblelatorGlobals.theApp.lexiconWord = None

    # We keep our copy of all the windows settings in BiblelatorGlobals.theApp.windowsSettingsDict
    windowsSettingsNamesList = []
    for name in BiblelatorGlobals.theApp.settings.data:
        if name.startswith( 'WindowSetting' ): windowsSettingsNamesList.append( name[13:] )
        dPrint( 'Quiet', debuggingThisModule, "Available windows settings are: {}".format( windowsSettingsNamesList ) )
    if windowsSettingsNamesList: assert 'Current' in windowsSettingsNamesList
    BiblelatorGlobals.theApp.windowsSettingsDict = {}
    for windowsSettingsName in windowsSettingsNamesList:
        BiblelatorGlobals.theApp.windowsSettingsDict[windowsSettingsName] = retrieveWindowsSettings( windowsSettingsName )
    if 'Current' in windowsSettingsNamesList: applyGivenWindowsSettings( 'Current' )
    else: logging.critical( "Application.parseAndApplySettings: No current window settings available" )
# end of parseAndApplySettings



def applyGivenWindowsSettings( givenWindowsSettingsName ):
    """
    Given the name of windows settings,
        find the settings in our dictionary
        and then apply it by creating the windows.
    """
    logging.debug( "applyGivenWindowsSettings( {} )".format( repr(givenWindowsSettingsName) ) )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "applyGivenWindowsSettings( {} )".format( repr(givenWindowsSettingsName) ) )
        if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "applyGivenWindowsSettings…" )

    BiblelatorGlobals.theApp.doCloseMyChildWindows()

    windowsSettingsFields = BiblelatorGlobals.theApp.windowsSettingsDict[givenWindowsSettingsName]
    for j in range( 1, MAX_WINDOWS ):
        winNumber = 'window{}'.format( j )
        if winNumber in windowsSettingsFields:
            rw = None
            thisStuff = windowsSettingsFields[winNumber]
            windowType = thisStuff['Type']
            #windowGeometry = thisStuff['Geometry'] if 'Geometry' in thisStuff else None
            windowSize = thisStuff['Size'] if 'Size' in thisStuff else None
            windowPosition = thisStuff['Position'] if 'Position' in thisStuff else None
            windowGeometry = windowSize+'+'+windowPosition if windowSize and windowPosition else None
            #dPrint( 'Quiet', debuggingThisModule, "applyGivenWindowsSettings", windowType, windowGeometry )

            if windowType == 'SwordBibleResourceWindow':
                try:
                    rw = BiblelatorGlobals.theApp.openSwordBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'SwordBibleResourceWindow {j}' settings" )
            elif windowType == 'DBPBibleResourceWindow':
                try:
                    rw = BiblelatorGlobals.theApp.openDBPBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'DBPBibleResourceWindow {j}' settings" )
            elif windowType == 'InternalBibleResourceWindow':
                try:
                    folderpath = thisStuff['BibleFolderpath']
                    if folderpath[-1] not in '/\\' \
                    and not str(folderpath).endswith( ZIPPED_PICKLE_FILENAME_END ):
                        folderpath = f'{folderpath}/'
                    rw = BiblelatorGlobals.theApp.openInternalBibleResourceWindow( folderpath, windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'InternalBibleResourceWindow {j}' settings" )
            elif windowType == 'HebrewBibleResourceWindow':
                try:
                    folderpath = thisStuff['BibleFolderpath']
                    if folderpath[-1] not in '/\\' \
                    and not str(folderpath).endswith( ZIPPED_PICKLE_FILENAME_END ):
                        folderpath = f'{folderpath}/'
                    rw = BiblelatorGlobals.theApp.openHebrewBibleResourceWindow( folderpath, windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'HebrewBibleResourceWindow {j}' settings" )

            #elif windowType == 'HebrewLexiconResourceWindow':
                #BiblelatorGlobals.theApp.openHebrewLexiconResourceWindow( thisStuff['HebrewLexiconPath'], windowGeometry )
                ##except: logging.critical( "Unable to read all HebrewLexiconResourceWindow {} settings".format( j ) )
            #elif windowType == 'GreekLexiconResourceWindow':
                #BiblelatorGlobals.theApp.openGreekLexiconResourceWindow( thisStuff['GreekLexiconPath'], windowGeometry )
                ##except: logging.critical( "Unable to read all GreekLexiconResourceWindow {} settings".format( j ) )
            elif windowType == 'BibleLexiconResourceWindow':
                rw = BiblelatorGlobals.theApp.openBibleLexiconResourceWindow( windowGeometry )
                #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )

            elif windowType == 'BibleResourceCollectionWindow':
                collectionName = thisStuff['CollectionName']
                rw = BiblelatorGlobals.theApp.openBibleResourceCollectionWindow( collectionName, windowGeometry )
                #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )
                if 'BibleResourceCollection'+collectionName in BiblelatorGlobals.theApp.settings.data:
                    collectionSettingsFields = BiblelatorGlobals.theApp.settings.data['BibleResourceCollection'+collectionName]
                    for k in range( 1, MAX_WINDOWS ):
                        boxNumber = 'box{}'.format( k )
                        boxType = boxSource = None
                        for keyname in collectionSettingsFields:
                            if keyname.startswith( boxNumber ):
                                #dPrint( 'Quiet', debuggingThisModule, "found", keyname, "setting for", collectionName, "collection" )
                                if keyname == boxNumber+'Type': boxType = collectionSettingsFields[keyname]
                                elif keyname == boxNumber+'Source': boxSource = collectionSettingsFields[keyname]
                                else:
                                    vPrint( 'Quiet', debuggingThisModule, "Unknown {} collection key: {} = {}".format( repr(collectionName), keyname, collectionSettingsFields[keyname] ) )
                                    if BibleOrgSysGlobals.debugFlag: halt
                        if boxType and boxSource:
                            #if boxType in ( 'Internal', ):
                                #if boxSource[-1] not in '/\\': boxSource += '/' # Are they all folders -- might be wrong
                            rw.openBox( boxType, boxSource )

            elif windowType == 'TSVBibleEditWindow':
                try: folderpath = convertToPython( thisStuff['TSVFolderpath'] )
                except KeyError: folderpath = None
                rw = BiblelatorGlobals.theApp.openTSVEditWindow( folderpath, windowGeometry )
            elif windowType == 'BibleNotesWindow':
                try: folderpath = convertToPython( thisStuff['NotesFolderpath'] )
                except KeyError: folderpath = None
                rw = BiblelatorGlobals.theApp.openBibleNotesWindow( folderpath, windowGeometry )

            elif windowType == 'TranslationManualWindow':
                try:
                    try: folderpath = convertToPython( thisStuff['TMFolderpath'] )
                    except KeyError: folderpath = None
                    rw = BiblelatorGlobals.theApp.openTranslationManualWindow( folderpath, windowGeometry )
                except:
                    logging.critical( f"Unable to read all 'TranslationManualWindow {j}' settings" )

            elif windowType == 'BibleReferenceCollectionWindow':
                xyz = "JustTesting!"
                rw = BiblelatorGlobals.theApp.openBibleReferenceCollectionWindow( xyz, windowGeometry )
                #except: logging.critical( "Unable to read all BibleReferenceCollectionWindow {} settings".format( j ) )

            elif windowType == 'PlainTextEditWindow':
                try: filepath = convertToPython( thisStuff['TextFilepath'] )
                except KeyError: filepath = None
                #if filepath == 'None': filepath = None
                rw = BiblelatorGlobals.theApp.openFileTextEditWindow( filepath, windowGeometry )
                #except: logging.critical( "Unable to read all PlainTextEditWindow {} settings".format( j ) )
            elif windowType == 'BiblelatorUSFMBibleEditWindow':
                try:
                    folderpath = thisStuff['ProjectFolderpath']
                    if folderpath[-1] not in '/\\': folderpath = f'{folderpath}/'
                    rw = BiblelatorGlobals.theApp.openBiblelatorBibleEditWindow( folderpath, thisStuff['EditMode'], windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'BiblelatorUSFMBibleEditWindow {j}' settings" )
            elif windowType == 'uWUSFMBibleEditWindow':
                try:
                    folderpath = thisStuff['ProjectFolderpath']
                    if folderpath[-1] not in '/\\': folderpath = f'{folderpath}/'
                    rw = BiblelatorGlobals.theApp.openUWUSFMBibleEditWindow( folderpath, thisStuff['EditMode'], windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'uWUSFMBibleEditWindow {j}' settings" )
            elif windowType == 'Paratext8USFMBibleEditWindow':
                try:
                    rw = BiblelatorGlobals.theApp.openParatext8BibleEditWindow( thisStuff['ProjectFolder'], thisStuff['EditMode'], windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'Paratext8USFMBibleEditWindow {j}' settings" )
            elif windowType == 'Paratext7USFMBibleEditWindow':
                try:
                    rw = BiblelatorGlobals.theApp.openParatext7BibleEditWindow( thisStuff['SSFFilepath'], thisStuff['EditMode'], windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all 'Paratext7USFMBibleEditWindow {j}' settings" )
            elif windowType == 'ESFMEditWindow':
                try:
                    folderpath = thisStuff['ESFMFolder']
                    if folderpath[-1] not in '/\\': folderpath = f'{folderpath}/'
                    rw = BiblelatorGlobals.theApp.openESFMEditWindow( folderpath, thisStuff['EditMode'], windowGeometry )
                except KeyError:
                    logging.critical( f"Unable to read all ESFMEditWindow {j} settings" )

            else:
                logging.critical( "applyGivenWindowsSettings: " + _("Unknown {} window type").format( repr(windowType) ) )
                if BibleOrgSysGlobals.debugFlag: halt

            if rw is None:
                logging.critical( "applyGivenWindowsSettings: " + _("Failed to reopen '{}' window type!!! How did this happen?").format( windowType ) )
                showError( APP_NAME, _("Failed to reopen '{}'! (Program error or bad settings file.)").format( windowType ) )
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



def getCurrentChildWindowSettings():
    """
    Go through the currently open windows and get their settings data
        and save it in BiblelatorGlobals.theApp.windowsSettingsDict['Current'].
    """
    logging.debug( "getCurrentChildWindowSettings()" )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "getCurrentChildWindowSettings()" )

    if 'Current' in BiblelatorGlobals.theApp.windowsSettingsDict: del BiblelatorGlobals.theApp.windowsSettingsDict['Current']
    BiblelatorGlobals.theApp.windowsSettingsDict['Current'] = {}
    for j, appWin in enumerate( BiblelatorGlobals.theApp.childWindows ):
        if appWin.windowType in ( 'HTMLWindow', 'FindResultWindow' ):
            continue # We don't save these

        winNumber = "window{}".format( j+1 )
        BiblelatorGlobals.theApp.windowsSettingsDict['Current'][winNumber] = {}
        thisOne = BiblelatorGlobals.theApp.windowsSettingsDict['Current'][winNumber]
        thisOne['Type'] = appWin.windowType #.replace( 'Window', 'Window' )
        if 0 and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "Child", j, appWin.genericWindowType, appWin.windowType )
            vPrint( 'Quiet', debuggingThisModule, "  child geometry", appWin.geometry(), "child winfo_geometry", appWin.winfo_geometry() )
            #dPrint( 'Quiet', debuggingThisModule, "  child winfo x", appWin.winfo_x(), "child winfo rootx", appWin.winfo_rootx() )
            #dPrint( 'Quiet', debuggingThisModule, "  child winfo y", appWin.winfo_y(), "child winforooty", appWin.winfo_rooty() )
            #dPrint( 'Quiet', debuggingThisModule, "  child height", appWin.winfo_height(), "child reqheight", appWin.winfo_reqheight() )
            #dPrint( 'Quiet', debuggingThisModule, "  child width", appWin.winfo_width(), "child reqwidth", appWin.winfo_reqwidth() )
        thisOne['Size'], thisOne['Position'] = appWin.geometry().split( '+', 1 )
        if thisOne['Position'] == '0+0': # not sure why this occurs for a new window -- pops up top left
            thisOne['Position'] = appWin.winfo_geometry().split( '+', 1 )[1] # Won't be exact but close
            vPrint( 'Quiet', debuggingThisModule, "Corrected {} window position from '0+0' to {}".format( appWin.windowType, thisOne['Position'] ) )
        thisOne['MinimumSize'] = assembleWindowSize( *appWin.minsize() )
        thisOne['MaximumSize'] = assembleWindowSize( *appWin.maxsize() )
        thisOne['StatusBar'] = 'On' if appWin._showStatusBarVar.get() else 'Off'

        if appWin.windowType == 'SwordBibleResourceWindow':
            thisOne['ModuleAbbreviation'] = appWin.moduleID
        elif appWin.windowType == 'DBPBibleResourceWindow':
            thisOne['ModuleAbbreviation'] = appWin.moduleID
        elif appWin.windowType == 'InternalBibleResourceWindow':
            thisOne['BibleFolderpath'] = appWin.moduleID
        elif appWin.windowType == 'HebrewBibleResourceWindow':
            thisOne['BibleFolderpath'] = appWin.moduleID

        elif appWin.windowType == 'TSVBibleEditWindow':
            thisOne['TSVFolderpath'] = appWin.folderpath
        elif appWin.windowType == 'BibleNotesWindow':
            thisOne['NotesFolderpath'] = appWin.folderpath

        elif appWin.windowType == 'TranslationManualWindow':
            thisFolderpath = appWin.folderpath # e.g., '/mnt/SSDs/Bibles/unfoldingWordHelps/en_ta/./intro/ta-intro'
            # dPrint( 'Info', debuggingThisModule, "thisFolderpath", thisFolderpath)
            ix = str(thisFolderpath).find( './' )
            if ix > 0: thisFolderpath = str(thisFolderpath)[:ix] # Remove subpath
            thisOne['TMFolderpath'] = thisFolderpath

        elif appWin.windowType == 'BibleLexiconResourceWindow':
            pass # No details to save
        #     thisOne['BibleLexiconPath'] = appWin.moduleID

        elif appWin.windowType == 'BibleResourceCollectionWindow':
            thisOne['CollectionName'] = appWin.moduleID
        elif appWin.windowType == 'BibleReferenceCollectionWindow':
            vPrint( 'Quiet', debuggingThisModule, "WARNING: Doesn't save BibleReferenceCollectionWindow yet!" )
            #thisOne['CollectionName'] = appWin.moduleID # Just copied -- not checked

        elif appWin.windowType == 'PlainTextEditWindow':
            try: thisOne['TextFilepath'] = appWin.filepath
            except AttributeError: pass # It's possible to have a blank new text edit window open

        elif appWin.windowType == 'BiblelatorUSFMBibleEditWindow':
            thisOne['ProjectFolderpath'] = appWin.moduleID
            thisOne['EditMode'] = appWin.editMode
        elif appWin.windowType == 'uWUSFMBibleEditWindow':
            thisOne['ProjectFolderpath'] = appWin.moduleID
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
            except AttributeError:
                if 'TSV' not in appWin.windowType:
                    logging.critical( "getCurrentChildWindowSettings: " + _("Why no contextViewMode in {}").format( appWin.windowType ) )
            try: thisOne['FormatViewMode'] = appWin._formatViewMode
            except AttributeError:
                if 'TSV' not in appWin.windowType:
                    logging.critical( "getCurrentChildWindowSettings: " + _("Why no formatViewMode in {}").format( appWin.windowType ) )

        if appWin.windowType.endswith( 'EditWindow' ):
            thisOne['AutocompleteMode'] = appWin.autocompleteMode
# end of getCurrentChildWindowSettings



def saveNewWindowSetup():
    """
    Gets the name for the new window setup and saves the information.
    """
    fnPrint( debuggingThisModule, "saveNewWindowSetup()" )
    if BibleOrgSysGlobals.debugFlag:
        if debuggingThisModule: BiblelatorGlobals.theApp.setDebugText( "saveNewWindowSetup…" )

    swnd = SaveWindowsLayoutNameDialog( BiblelatorGlobals.theApp.windowsSettingsDict, title=_('Save window setup') )
    dPrint( 'Never', debuggingThisModule, "swndResult", repr(swnd.result) )
    if swnd.result:
        getCurrentChildWindowSettings()
        BiblelatorGlobals.theApp.windowsSettingsDict[swnd.result] = BiblelatorGlobals.theApp.windowsSettingsDict['Current'] # swnd.result is the new window name
        #dPrint( 'Quiet', debuggingThisModule, "swS", BiblelatorGlobals.theApp.windowsSettingsDict )
        writeSettingsFile() # Save file now in case we crash
        BiblelatorGlobals.theApp.createMenuBar() # refresh
# end of saveNewWindowSetup



def deleteExistingWindowSetup():
    """
    Gets the name of an existing window setting and deletes the setting.
    """
    fnPrint( debuggingThisModule, "deleteExistingWindowSetup()" )
    if BibleOrgSysGlobals.debugFlag:
        if debuggingThisModule: BiblelatorGlobals.theApp.setDebugText( "deleteExistingWindowSetup" )
        assert BiblelatorGlobals.theApp.windowsSettingsDict and (len(BiblelatorGlobals.theApp.windowsSettingsDict)>1 or 'Current' not in BiblelatorGlobals.theApp.windowsSettingsDict)

    dwnd = DeleteWindowsLayoutNameDialog( BiblelatorGlobals.theApp.windowsSettingsDict, title=_('Delete saved window setup') )
    dPrint( 'Never', debuggingThisModule, "dwndResult", repr(dwnd.result) )
    if dwnd.result:
        if BibleOrgSysGlobals.debugFlag:
            assert dwnd.result in BiblelatorGlobals.theApp.windowsSettingsDict
        del BiblelatorGlobals.theApp.windowsSettingsDict[dwnd.result]
        BiblelatorGlobals.theApp.settings.saveINI() # Save file now in case we crash ###-- don't worry -- it's easy to delete one
        BiblelatorGlobals.theApp.createMenuBar() # refresh
# end of deleteExistingWindowSetup



def viewSettings():
    """
    Open a pop-up text window with the current settings displayed.
    """
    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, "viewSettings()" )
        if debuggingThisModule: BiblelatorGlobals.theApp.setDebugText( "viewSettings" )

    tEW = TextEditWindow()
    #if windowGeometry: tEW.geometry( windowGeometry )
    if not tEW.setFilepath( BiblelatorGlobals.theApp.settings.settingsFilepath ) \
    or not tEW.loadText():
        tEW.doClose()
        showError( APP_NAME, _("Sorry, unable to open settings file") )
        if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Failed viewSettings" )
    else:
        BiblelatorGlobals.theApp.childWindows.append( tEW )
        if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Finished viewSettings" )
    BiblelatorGlobals.theApp.setReadyStatus()
# end of viewSettings


def writeSettingsFile():
    """
    Update our program settings and save them.
    """
    logging.info( "writeSettingsFile()" )
    fnPrint( debuggingThisModule, "writeSettingsFile()" )
    if BibleOrgSysGlobals.verbosityLevel > 0:
        vPrint( 'Quiet', debuggingThisModule, _("  Saving program settings…") )

    def convertToString( thisSetting ):
        """
        Takes special Python values and converts them to strings.
        """
        if thisSetting is None: return 'None'
        if thisSetting is True: return 'True'
        if thisSetting is False: return 'False'
        if isinstance( thisSetting, Path ):
            try:
                if thisSetting.is_dir(): return f'{thisSetting}/'
            except: pass
            return str( thisSetting )
        return thisSetting
    # end of convertToString


    # Main code for writeSettingsFile()
    if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( 'writeSettingsFile' )
    BiblelatorGlobals.theApp.settings.reset()

    BiblelatorGlobals.theApp.settings.data[APP_NAME] = {}
    mainStuff = BiblelatorGlobals.theApp.settings.data[APP_NAME]
    mainStuff['settingsVersion'] = SettingsVersion
    mainStuff['PROGRAM_VERSION'] = PROGRAM_VERSION
    mainStuff['themeName'] = BiblelatorGlobals.theApp.themeName
    if 0 and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, " root geometry", BiblelatorGlobals.theApp.rootWindow.geometry(), "root winfo_geometry", BiblelatorGlobals.theApp.rootWindow.winfo_geometry() )
        vPrint( 'Quiet', debuggingThisModule, " root winfo x", BiblelatorGlobals.theApp.rootWindow.winfo_x(), "root winfo rootx", BiblelatorGlobals.theApp.rootWindow.winfo_rootx() )
        vPrint( 'Quiet', debuggingThisModule, " root winfo y", BiblelatorGlobals.theApp.rootWindow.winfo_y(), "root winfo rooty", BiblelatorGlobals.theApp.rootWindow.winfo_rooty() )
    mainStuff['windowSize'], mainStuff['windowPosition'] = BiblelatorGlobals.theApp.rootWindow.geometry().split( '+', 1 )
    # Seems that winfo_geometry doesn't work above (causes root Window to move)
    mainStuff['minimumSize'] = BiblelatorGlobals.theApp.minimumSize
    mainStuff['maximumSize'] = BiblelatorGlobals.theApp.maximumSize
    if 0 and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, " saved size (across/down) to ini file", repr(mainStuff['windowSize']), "pos", repr(mainStuff['windowPosition']) )
        vPrint( 'Quiet', debuggingThisModule, "   min", repr(mainStuff['minimumSize']), "max", repr(mainStuff['maximumSize']) )

    # Save the user interface settings
    BiblelatorGlobals.theApp.settings.data['Interface'] = {}
    interface = BiblelatorGlobals.theApp.settings.data['Interface']
    interface['interfaceLanguage'] = BiblelatorGlobals.theApp.interfaceLanguage
    interface['interfaceComplexity'] = BiblelatorGlobals.theApp.interfaceComplexity
    interface['touchMode'] = convertToString( BiblelatorGlobals.theApp.touchMode )
    interface['tabletMode'] = convertToString( BiblelatorGlobals.theApp.tabletMode )
    interface['showDebugMenu'] = convertToString( BiblelatorGlobals.theApp.showDebugMenu )

    # Save the Internet access controls
    BiblelatorGlobals.theApp.settings.data['Internet'] = {}
    internet = BiblelatorGlobals.theApp.settings.data['Internet']
    internet['internetAccess'] = 'Enabled' if BiblelatorGlobals.theApp.internetAccessEnabled else 'Disabled'
    internet['internetFast'] = 'True' if BiblelatorGlobals.theApp.internetFast else 'False'
    internet['internetExpensive'] = 'True' if BiblelatorGlobals.theApp.internetExpensive else 'False'
    internet['cloudBackups'] = 'Enabled' if BiblelatorGlobals.theApp.cloudBackupsEnabled else 'Disabled'
    internet['checkForDeveloperMessages'] = 'Enabled' if BiblelatorGlobals.theApp.checkForDeveloperMessagesEnabled else 'Disabled'
    internet['lastMessageNumberRead'] = str( BiblelatorGlobals.theApp.lastMessageNumberRead )
    internet['sendUsageStatistics'] = 'Enabled' if BiblelatorGlobals.theApp.sendUsageStatisticsEnabled else 'Disabled'
    internet['automaticUpdates'] = 'Enabled' if BiblelatorGlobals.theApp.automaticUpdatesEnabled else 'Disabled'
    internet['useDevelopmentVersions'] = 'Enabled' if BiblelatorGlobals.theApp.useDevelopmentVersionsEnabled else 'Disabled'

    # Save the project information
    BiblelatorGlobals.theApp.settings.data['Project'] = {}
    users = BiblelatorGlobals.theApp.settings.data['Project']
    users['currentProjectName'] = BiblelatorGlobals.theApp.currentProjectName

    # Save the user information
    BiblelatorGlobals.theApp.settings.data['Users'] = {}
    users = BiblelatorGlobals.theApp.settings.data['Users']
    users['currentUserName'] = BiblelatorGlobals.theApp.currentUserName
    users['currentUserInitials'] = BiblelatorGlobals.theApp.currentUserInitials
    users['currentUserEmail'] = BiblelatorGlobals.theApp.currentUserEmail
    users['currentUserRole'] = BiblelatorGlobals.theApp.currentUserRole
    users['currentUserAssignments'] = BiblelatorGlobals.theApp.currentUserAssignments

    # Save the last paths
    BiblelatorGlobals.theApp.settings.data['Paths'] = {}
    paths = BiblelatorGlobals.theApp.settings.data['Paths']
    paths['lastFileDir'] = str(BiblelatorGlobals.theApp.lastFileDir)
    paths['lastBiblelatorFileDir'] = str(BiblelatorGlobals.theApp.lastBiblelatorFileDir)
    paths['lastParatextFileDir'] = str(BiblelatorGlobals.theApp.lastParatextFileDir)
    paths['lastInternalBibleDir'] = str(BiblelatorGlobals.theApp.lastInternalBibleDir)
    paths['lastSwordDir'] = str(BiblelatorGlobals.theApp.lastSwordDir)

    # Save the recent files
    BiblelatorGlobals.theApp.settings.data['RecentFiles'] = {}
    recent = BiblelatorGlobals.theApp.settings.data['RecentFiles']
    for j, (filename,folder,windowType) in enumerate( BiblelatorGlobals.theApp.recentFiles ):
        recentName = 'recent{}'.format( j+1 )
        recent[recentName+'Filename'] = convertToString( filename )
        recent[recentName+'Folder'] = convertToString( folder )
        recent[recentName+'Type'] = windowType

    # Save the referenceGroups A..D
    BiblelatorGlobals.theApp.settings.data['BCVGroups'] = {}
    groups = BiblelatorGlobals.theApp.settings.data['BCVGroups']
    groups['genericBibleOrganisationalSystemName'] = BiblelatorGlobals.theApp.genericBibleOrganisationalSystemName
    groups['currentGroup'] = BiblelatorGlobals.theApp.currentVerseKeyGroup
    groups['A-Book'] = BiblelatorGlobals.theApp.GroupA_VerseKey[0]
    groups['A-Chapter'] = BiblelatorGlobals.theApp.GroupA_VerseKey[1]
    groups['A-Verse'] = BiblelatorGlobals.theApp.GroupA_VerseKey[2]
    groups['B-Book'] = BiblelatorGlobals.theApp.GroupB_VerseKey[0]
    groups['B-Chapter'] = BiblelatorGlobals.theApp.GroupB_VerseKey[1]
    groups['B-Verse'] = BiblelatorGlobals.theApp.GroupB_VerseKey[2]
    groups['C-Book'] = BiblelatorGlobals.theApp.GroupC_VerseKey[0]
    groups['C-Chapter'] = BiblelatorGlobals.theApp.GroupC_VerseKey[1]
    groups['C-Verse'] = BiblelatorGlobals.theApp.GroupC_VerseKey[2]
    groups['D-Book'] = BiblelatorGlobals.theApp.GroupD_VerseKey[0]
    groups['D-Chapter'] = BiblelatorGlobals.theApp.GroupD_VerseKey[1]
    groups['D-Verse'] = BiblelatorGlobals.theApp.GroupD_VerseKey[2]
    groups['E-Book'] = BiblelatorGlobals.theApp.GroupE_VerseKey[0]
    groups['E-Chapter'] = BiblelatorGlobals.theApp.GroupE_VerseKey[1]
    groups['E-Verse'] = BiblelatorGlobals.theApp.GroupE_VerseKey[2]

    # Save the lexicon info
    BiblelatorGlobals.theApp.settings.data['Lexicon'] = {}
    lexicon = BiblelatorGlobals.theApp.settings.data['Lexicon']
    if BiblelatorGlobals.theApp.lexiconWord: lexicon['currentWord'] = BiblelatorGlobals.theApp.lexiconWord

    # Save any open Bible resource collections
    vPrint( 'Never', debuggingThisModule, "save collection data…" )
    for appWin in BiblelatorGlobals.theApp.childWindows:
        #dPrint( 'Quiet', debuggingThisModule, "  gT", appWin.genericWindowType )
        #dPrint( 'Quiet', debuggingThisModule, "  wT", appWin.windowType )
        if appWin.windowType == 'BibleResourceCollectionWindow':
            if appWin.resourceBoxesList: # so we don't create just an empty heading for an empty collection
                BiblelatorGlobals.theApp.settings.data['BibleResourceCollection'+appWin.moduleID] = {}
                thisOne = BiblelatorGlobals.theApp.settings.data['BibleResourceCollection'+appWin.moduleID]
                #dPrint( 'Quiet', debuggingThisModule, "  found", appWin.moduleID )
                for j, box in enumerate( appWin.resourceBoxesList ):
                    boxNumber = 'box{}'.format( j+1 )
                    #dPrint( 'Quiet', debuggingThisModule, "    bT", box.boxType )
                    #dPrint( 'Quiet', debuggingThisModule, "    ID", box.moduleID )
                    thisOne[boxNumber+'Type'] = box.boxType.replace( 'BibleResourceBox', '' )
                    thisOne[boxNumber+'Source'] = box.moduleID

    # Get the current child window settings
    getCurrentChildWindowSettings()
    # Save all the various window set-ups including both the named ones and the current one
    for windowsSettingName in sorted( BiblelatorGlobals.theApp.windowsSettingsDict ):
        vPrint( 'Never', debuggingThisModule, "Saving windows set-up {}".format( repr(windowsSettingName) ) )
        try: # Just in case something goes wrong with characters in a settings name
            BiblelatorGlobals.theApp.settings.data['WindowSetting'+windowsSettingName] = {}
            thisOne = BiblelatorGlobals.theApp.settings.data['WindowSetting'+windowsSettingName]
            for windowNumber,winDict in sorted( BiblelatorGlobals.theApp.windowsSettingsDict[windowsSettingName].items() ):
                vPrint( 'Never', debuggingThisModule, f"  {windowNumber} {winDict}" )
                for windowSettingName,value in sorted( winDict.items() ):
                    vPrint( 'Never', debuggingThisModule, f"  {windowSettingName} {value!r}" )
                    thisOne[windowNumber+windowSettingName] = convertToString( value )
        except UnicodeEncodeError: logging.error( "writeSettingsFile: " + _("unable to write {} windows set-up").format( repr(windowsSettingName) ) )
    BiblelatorGlobals.theApp.settings.saveINI()
# end of writeSettingsFile



MIME_BOUNDARY = 'sdafsZXXdahxcvblkDSFSDFjeflqwertlSDFSDFjkre' # Random string that won't occur in our data
def doSendUsageStatistics():
    """
    Send (POST) usage statistics over the Internet.

    Note that Biblelator is mostly closed down at this stage.
    """
    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, "doSendUsageStatistics()" )
        assert BiblelatorGlobals.theApp.internetAccessEnabled
        assert BiblelatorGlobals.theApp.sendUsageStatisticsEnabled
    elif BibleOrgSysGlobals.verbosityLevel > 0:
        vPrint( 'Quiet', debuggingThisModule, _("  Sending program usage info…") )

    adjAppName = APP_NAME.replace('/','-').replace(':','_').replace('\\','_').replace(' ','_')
    adjUserName = BiblelatorGlobals.theApp.currentUserName.replace('/','-').replace(':','_').replace('\\','_')

    # Package our stuff up into a zip file
    import tempfile
    import zipfile
    zipFilepath = os.path.join( tempfile.gettempdir(), adjAppName+'.zip' )
    #dPrint( 'Quiet', debuggingThisModule, "zipF0", repr(zipFilepath) )
    zf = zipfile.ZipFile( zipFilepath, 'w', compression=zipfile.ZIP_DEFLATED )

    # Add log file(s)
    filename = adjAppName + '_log.txt'
    #dPrint( 'Quiet', debuggingThisModule, "zipF1", repr(BiblelatorGlobals.theApp.loggingFolderpath) )
    #dPrint( 'Quiet', debuggingThisModule, "zipF2", repr(filename) )
    for extension in BibleOrgSysGlobals.STANDARD_BACKUP_EXTENSIONS:
        filepath = os.path.join( BiblelatorGlobals.theApp.loggingFolderpath, filename+extension )
        #dPrint( 'Quiet', debuggingThisModule, "  zipF3", repr(filepath) )
        if os.path.exists( filepath ):
            #dPrint( 'Quiet', debuggingThisModule, "  zipF4", repr(filepath) )
            zf.write( filepath, filename+extension )

    # Add usage file(s)
    zf.write( BiblelatorGlobals.theApp.usageLogPath, BiblelatorGlobals.theApp.usageFilename )

    # Add settings file(s)
    #dPrint( 'Quiet', debuggingThisModule, "zipF5", repr(BiblelatorGlobals.theApp.settings.settingsFilepath) )
    #dPrint( 'Quiet', debuggingThisModule, "zipF6", repr(BiblelatorGlobals.theApp.settings.settingsFilename) )
    for extension in BibleOrgSysGlobals.STANDARD_BACKUP_EXTENSIONS:
        filepath = BiblelatorGlobals.theApp.settings.settingsFilepath+extension
        #dPrint( 'Quiet', debuggingThisModule, "  zipF7", repr(filepath) )
        if os.path.exists( filepath ):
            #dPrint( 'Quiet', debuggingThisModule, "  zipF8", repr(filepath) )
            zf.write( filepath, BiblelatorGlobals.theApp.settings.settingsFilename+extension )
    zf.close()
    with open( zipFilepath, 'rb' ) as zFile:
        zData = zFile.read()
    os.remove( zipFilepath )
    zDataStr = zData.decode('latin-1') # Make extended ASCII bytes into str

    # Post the zip file to our server
    parameterList = []
    parameterList.extend( ('--' + MIME_BOUNDARY, "Content-Disposition: form-data; name=nameLine",
                           '', BiblelatorGlobals.theApp.currentUserName ) )
    parameterList.extend( ('--' + MIME_BOUNDARY, "Content-Disposition: form-data; name=emailLine",
                           '', BiblelatorGlobals.theApp.currentUserEmail ) )
    parameterList.extend( ('--' + MIME_BOUNDARY, "Content-Disposition: form-data; name=projectLine",
                           '', BiblelatorGlobals.theApp.currentProjectName ) )
    parameterList.extend( ('--' + MIME_BOUNDARY,
                    'Content-Disposition: form-data; name=uploadedZipFile; filename="{}.zip"'.format( adjUserName ),
                    'Content-Type: application/zip', '', zDataStr ) )
    parameterList.extend( ('--' + MIME_BOUNDARY + '--' , '') )
    parameterString = '\r\n'.join (parameterList)
    #dPrint( 'Quiet', debuggingThisModule, "\nparameterString", repr(parameterString) )

    headers = {"Content-type": "multipart/form-data; MIME_BOUNDARY={}".format( MIME_BOUNDARY ) }
    #dPrint( 'Quiet', debuggingThisModule, "\nheaders", headers )

    import http.client
    conn = http.client.HTTPConnection( BibleOrgSysGlobals.SUPPORT_SITE_NAME )
    conn.request( 'POST', '/Software/Biblelator/StatusInputs/SubmitAction.phtml', parameterString, headers )
    try: response = conn.getresponse()
    except http.client.RemoteDisconnected:
        vPrint( 'Quiet', debuggingThisModule, "doSendUsageStatistics remote RemoteDisconnected -- send failed" )
        conn.close()
        return
    if response.status == 200:
        vPrint( 'Quiet', debuggingThisModule, "    doSendUsageStatistics accepted by server" )
    else:
        vPrint( 'Quiet', debuggingThisModule, "doSendUsageStatistics status", repr(response.status) ) # Should be 200
        vPrint( 'Quiet', debuggingThisModule, "doSendUsageStatistics reason", repr(response.reason) ) # Should be 'OK'
        data = response.read()
        vPrint( 'Quiet', debuggingThisModule, "doSendUsageStatistics data", repr(data) ) # Web page back from the server
    conn.close()
# end of doSendUsageStatistics



def briefDemo() -> None:
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    import sys, tkinter as tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, "Platform is", sys.platform ) # e.g., "win32"
        vPrint( 'Quiet', debuggingThisModule, "OS name is", os.name ) # e.g., "nt"
        if sys.platform == "linux": vPrint( 'Quiet', debuggingThisModule, "OS uname is", os.uname() )
        vPrint( 'Quiet', debuggingThisModule, "Running main…" )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( programNameVersion )

    homeFolderpath = BibleOrgSysGlobals.findHomeFolderpath()
    loggingFolderpath = os.path.join( homeFolderpath, DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderpath, DATA_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, APP_NAME )
    settings.loadINI()

    application = Application( tkRootWindow, homeFolderpath, loggingFolderpath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    import sys, tkinter as tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, "Platform is", sys.platform ) # e.g., "win32"
        vPrint( 'Quiet', debuggingThisModule, "OS name is", os.name ) # e.g., "nt"
        if sys.platform == "linux": vPrint( 'Quiet', debuggingThisModule, "OS uname is", os.uname() )
        vPrint( 'Quiet', debuggingThisModule, "Running main…" )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( programNameVersion )

    homeFolderpath = BibleOrgSysGlobals.findHomeFolderpath()
    loggingFolderpath = os.path.join( homeFolderpath, DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderpath, DATA_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, APP_NAME )
    settings.loadINI()

    application = Application( tkRootWindow, homeFolderpath, loggingFolderpath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of BiblelatorSettingsFunctions.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BiblelatorSettingsFunctions.py
