#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Settings.py
#
# Handle settings for Biblelator Bible display/editing
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
Settings class
    __init__()
    __str__()
    __repr__()
    reset()
    load()
    save()

ApplicationSettings class (Settings)
    __init__( homeFolderName, dataFolderName, settingsFolderName, settingsFilename )


BiblelatorProjectSettings class (Settings)
    __init__( projectFolderpath )
    saveNameAndAbbreviation( projectName, projectAbbreviation )
    saveNewBookSettings( detailsDict )
    loadUSFMMetadataInto( theUSFMBible )


uWProjectSettings class (Settings)
    __init__( projectFolderpath )
    saveNameAndAbbreviation( projectName, projectAbbreviation )
    saveNewBookSettings( detailsDict )
    loadUSFMMetadataInto( theUSFMBible )
"""
from gettext import gettext as _
import os.path
import logging
import configparser
from datetime import datetime

# BibleOrgSys imports
import sys
sys.path.append( '/home/robert/Programming/WebDevelopment/OpenScriptures/BibleOrgSys/' )
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint

# Biblelator imports
if __name__ == '__main__':
    import sys
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator.BiblelatorGlobals import APP_NAME
from Biblelator.Settings.BiblelatorSettingsFunctions import SettingsVersion


LAST_MODIFIED_DATE = '2020-05-01' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorSettings"
PROGRAM_NAME = "Biblelator Settings"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False



class Settings:
    """
    A class containing our basic common functions for loading and saving settings, etc.
        This class is designed to be a base class only.

    Biblelator settings are designed to be human readable (and therefore easily hackable).
        For this reason, the "Windows ini" type format was chosen
            over more complex and less readable formats like XML.

    Super class must set self.settingsFilepath
    """
    def __init__( self ):
        """
        """
        self.objectNameString = 'Settings object'
        self.objectTypeString = 'Settings'
        self.data = None
    # end of Settings.__init__


    def __str__( self ):
        result = self.objectNameString
        if self.data:
            for item in self.data.items():
                result += str( item )
        return result
    # end of Settings.__str__

    def __repr__( self ):
        return repr( self.data.items() )
    # end of Settings.__repr__


    def reset( self ):
        """
        Create a blank settings object.
        """
        self.data = configparser.ConfigParser()
        self.data.optionxform = lambda option: option # Force true case matches for options (default is all lower case)
    # end of Settings.reset


    def loadINI( self ):
        """
        Load the settings file (if we found it).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "Settings.loadINI() from {!r}".format( self.settingsFilepath ) )

        self.reset() # Creates self.data
        assert self.data
        if self.settingsFilepath and os.path.isfile( self.settingsFilepath ) and os.access( self.settingsFilepath, os.R_OK ):
            self.data.read( self.settingsFilepath )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            for section in self.data:
                vPrint( 'Quiet', debuggingThisModule, f"  Settings.loadINI: s.d main section = {section}" )
    #end of Settings.loadINI


    def saveINI( self ):
        """
        Save all of the program settings to disk.
            They must have already been saved into self.data.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "Settings.saveINI() in {!r}".format( self.settingsFilepath ) )
            assert self.data
            assert self.settingsFilepath

        BibleOrgSysGlobals.backupAnyExistingFile( self.settingsFilepath, numBackups=8 )
        with open( self.settingsFilepath, 'wt', encoding='utf-8' ) as settingsFile: # It may or may not have previously existed
            # Put a (comment) heading in the file first
            settingsFile.write( '# ' + _("{} {} settings file v{}").format( APP_NAME, PROGRAM_VERSION, SettingsVersion ) + '\n' )
            settingsFile.write( '# ' + _("Originally saved {} as {}") \
                .format( datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.settingsFilepath ) + '\n\n' )

            self.data.write( settingsFile )
    # end of Settings.saveINI


    def loadYAML( self ):
        """
        Load the settings file (if we found it).

        Saves requiring a yaml library FWIW.

        Might still be fragile -- not fully debugged.
        """
        import re

        debuggingThisFunction = False

        vPrint( 'Quiet', debuggingThisModule, f"Settings.loadYAML() from {self.settingsFilepath}" )

        self.data = {}
        if self.settingsFilepath and os.path.isfile( self.settingsFilepath ) and os.access( self.settingsFilepath, os.R_OK ):
            with open( self.settingsFilepath, 'rt' ) as yamlFile:
                state = None
                indent = 2 # TODO: Really should deduce this number from the file
                for j, line in enumerate( yamlFile, start=1 ):
                    line = line.rstrip( '\n\r ' )
                    if not line: continue
                    if line.startswith( '#' ): continue # comment line
                    if line == '---': state = 0; continue # start of table
                    numLeadingSpaces = len(line) - len( line.lstrip( ' ' ) )
                    if debuggingThisFunction: print( f'Line {j:3} State {state} numLS={numLeadingSpaces}: "{line}"' )

                    # Check if we need to go back a level
                    if numLeadingSpaces==0:
                        if debuggingThisFunction: print( f"S-0: Returned to 0" )
                        state = 0
                    if numLeadingSpaces==indent:
                        if debuggingThisFunction: print( f"S-1: Returned to 1" )
                        state = 1

                    if state == 0:
                        match = re.match( r"([^ :]+?): ?'(.+?)'$", line )
                        if match:
                            if debuggingThisFunction: print( f"0-0: 1={match.group(1)}' 2='{match.group(2)}'" )
                            self.data[match.group(1)] = match.group(2); continue
                        match = re.match( r"([^ :]+?): ?(\d+?)$", line )
                        if match: self.data[match.group(1)] = int(match.group(2)); continue

                        match = re.match( r"([^ :]+?):$", line )
                        if match: key1 = match.group(1); state = 1; continue

                    elif state == 1:
                        if line == f"{' '*indent}-":
                            if debuggingThisFunction: print( f"1-0: '{line}' with k1='{key1}'" )
                            if key1 not in self.data: self.data[key1] = [{}]
                            else:
                                assert isinstance( self.data[key1], list )
                                assert isinstance( self.data[key1][-1], dict )
                                self.data[key1].append( {} )
                            state = 3; continue
                        match = re.match( rf"{' '*indent}([^ :]+?): ?'(.+?)'$", line )
                        if match:
                            if debuggingThisFunction: print( f"1-1: 1={match.group(1)}' 2='{match.group(2)}'" )
                            if key1 not in self.data: self.data[key1] = {}
                            else: assert isinstance( self.data[key1], dict )
                            self.data[key1][match.group(1)] = match.group(2); continue
                        match = re.match( rf"{' '*indent}([^ :]+?): ?(\d+?)$", line )
                        if match:
                            if debuggingThisFunction: print( f"1-2: 1={match.group(1)}' 2='{match.group(2)}'" )
                            if key1 not in self.data: self.data[key1] = {}
                            else: assert isinstance( self.data[key1], dict )
                            self.data[key1][match.group(1)] = int(match.group(2)); continue

                        match = re.match( rf"{' '*indent}([^ :]+?):$", line )
                        if match:
                            if debuggingThisFunction: print( f"1-3: 1={match.group(1)}'" )
                            if key1 not in self.data: self.data[key1] = {}
                            key2 = match.group(1); state = 2; continue

                    elif state == 2:
                        if line == f"{' '*2*indent}-":
                            if debuggingThisFunction: print( f"2-0: '{line}' with k1='{key1}' k2='{key2}'" )
                            if key2 not in self.data[key1]:
                                self.data[key1][key2] = [{}]
                            else:
                                assert isinstance( self.data[key1][key2], list )
                                assert isinstance( self.data[key1][key2][-1], dict )
                                self.data[key1][key2].append( {} )
                            state = 4; continue
                        match = re.match( rf"{' '*2*indent}([^ :]+?): ?'(.+?)'$", line )
                        if match:
                            if debuggingThisFunction: print( f"2-1: 1={match.group(1)}' 2='{match.group(2)}'" )
                            if key2 not in self.data[key1]: self.data[key1][key2] = {}
                            else: assert isinstance( self.data[key1][key2], dict )
                            self.data[key1][key2][match.group(1)] = match.group(2); continue
                        match = re.match( rf"{' '*2*indent}([^ :]+?): ?(\d+?)$", line )
                        if match:
                            if debuggingThisFunction: print( f"2-2: 1={match.group(1)}' 2='{match.group(2)}'" )
                            if key2 not in self.data[key1]: self.data[key1][key2] = {}
                            else: assert isinstance( self.data[key1][key2], dict )
                            self.data[key1][key2][match.group(1)] = int(match.group(2)); continue
                        match = re.match( rf"{' '*2*indent}- '(.+?)'$", line )
                        if match:
                            if debuggingThisFunction: print( f"2-3: 1={match.group(1)}'" )
                            if key2 not in self.data[key1]: self.data[key1][key2] = []
                            else: assert isinstance( self.data[key1][key2], list )
                            self.data[key1][key2].append( match.group(1) ); continue

                    elif state == 3:
                        if line == f"{' '*indent}-":
                            if debuggingThisFunction: print( f"3-0: '{line}' with k1='{key1}'" )
                            assert isinstance( self.data[key1], list )
                            assert isinstance( self.data[key1][-1], dict )
                            self.data[key1].append( {} )
                            continue
                        match = re.match( rf"{' '*2*indent}([^ :]+?): ?'(.+?)'$", line )
                        if match:
                            if debuggingThisFunction: print( f"3-1: 1={match.group(1)}' 2='{match.group(2)}'" )
                            if key1 not in self.data: self.data[key1] = [{}]
                            else: assert isinstance( self.data[key1], list )
                            self.data[key1][-1][match.group(1)] = match.group(2); continue

                    elif state == 4:
                        if line == f"{' '*2*indent}-":
                            if debuggingThisFunction: print( f"4-0: '{line}' with k1='{key1}' k2='{key2}'" )
                            assert isinstance( self.data[key1][key2], list )
                            assert isinstance( self.data[key1][key2][-1], dict )
                            self.data[key1][key2].append( {} )
                            continue
                        match = re.match( rf"{' '*3*indent}([^ :]+?): ?'(.+?)'$", line )
                        if match:
                            if debuggingThisFunction: print( f"4-1: 1={match.group(1)}' 2='{match.group(2)}'" )
                            if key2 not in self.data[key1]: self.data[key1][key2] = [{}]
                            else: assert isinstance( self.data[key1][key2], list )
                            self.data[key1][key2][-1][match.group(1)] = match.group(2); continue
        else:
            logging.critical( f"loadYAML: Unable to load and YAML from {self.filepath}" )

        # print( "\nSettings", len(self.data), self.data.keys() )
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            for section, value in self.data.items():
                vPrint( 'Quiet', debuggingThisModule, f"  loadYAML.load: {section} = {value!r}" )
    #end of Settings.loadYAML
# end of class Settings



class ApplicationSettings( Settings ):
    """
    """
    def __init__( self, homeFolderName, dataFolderName, settingsFolderName, settingsFilename ):
        """
        This class is used before the main program starts.

        Try to find where the main settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "ApplicationSettings.__init__( {!r}, {!r}, {!r}, {!r} )".format( homeFolderName, dataFolderName, settingsFolderName, settingsFilename ) )
        self.dataFolderName, self.settingsFolderName, self.settingsFilename = dataFolderName, settingsFolderName, settingsFilename
        # NOTE: Settings.__init__ is NOT called -- not needed
        self.objectNameString = 'Application Settings object'
        self.objectTypeString = 'ApplicationSettings'
        self.data = None

        if not self.settingsFilename.lower().endswith( '.ini' ):
            self.settingsFilename = self.settingsFilename + '.ini'
        self.dataFolderpath = self.settingsFolder = self.settingsFilepath = None
        ourFolderpath1 = os.path.join( homeFolderName, dataFolderName )
        if os.path.isdir( ourFolderpath1 ) and os.access( ourFolderpath1, os.W_OK ):
            self.dataFolderpath = ourFolderpath1
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                vPrint( 'Quiet', debuggingThisModule, "ApplicationSettings.__init__: Found dataFolderpath = ", self.dataFolderpath )
            ourFolderpath2 = os.path.join( self.dataFolderpath, settingsFolderName )
            if os.path.isdir( ourFolderpath2 ) and os.access( ourFolderpath2, os.W_OK ):
                self.settingsFolder = ourFolderpath2
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    vPrint( 'Quiet', debuggingThisModule, "ApplicationSettings.__init__: Found settingsFolder = ", self.settingsFolder )
                ourFilepath = os.path.join( ourFolderpath2, self.settingsFilename )
                if os.path.isfile( ourFilepath ) and os.access( ourFilepath, os.W_OK ):
                    self.settingsFilepath = ourFilepath
                    if BibleOrgSysGlobals.verbosityLevel > 2 or BibleOrgSysGlobals.debugFlag:
                        vPrint( 'Quiet', debuggingThisModule, "ApplicationSettings.__init__: Found settingsFilepath = ", self.settingsFilepath )

        # Create new data and settings folders if necessary
        if not self.dataFolderpath:
            logging.info( "ApplicationSettings.__init__ " + _("No data folder found") )
            if os.path.isdir( homeFolderName ) and os.access( homeFolderName, os.W_OK ):
                logging.info( "ApplicationSettings.__init__ " + _("Creating our data folder in {!r}").format( homeFolderName ) )
                self.dataFolderpath = os.path.join( homeFolderName, dataFolderName )
                os.mkdir( self.dataFolderpath )
        if not self.settingsFolder:
            logging.info( "ApplicationSettings.__init__ " + _("No settings folder found") )
            if os.path.isdir( self.dataFolderpath ) and os.access( self.dataFolderpath, os.W_OK ):
                logging.info( "ApplicationSettings.__init__ " + _("Creating our settings folder in {!r}").format( self.dataFolderpath ) )
                self.settingsFolder = os.path.join( self.dataFolderpath, settingsFolderName )
                os.mkdir( self.settingsFolder )
        if not self.settingsFilepath:
            logging.info( "ApplicationSettings.__init__ " + _("No settings file found") )
            self.settingsFilepath = os.path.join( self.settingsFolder, self.settingsFilename )
    # end of ApplicationSettings.__init__
# end of class ApplicationSettings



class BiblelatorProjectSettings( Settings ):
    """
    Settings class for Biblelator USFM edit windows.
    """
    def __init__( self, projectFolderpath ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "BiblelatorProjectSettings.__init__( {!r} )".format( projectFolderpath ) )
        self.projectFolderpath = projectFolderpath
        self.objectNameString = 'Biblelator Project Settings object'
        self.objectTypeString = 'BiblelatorProjectSettings'
        self.settingsFilename = 'ProjectSettings.ini'
        self.data = None

        self.settingsFilepath = os.path.join( projectFolderpath, self.settingsFilename )
        if not os.path.isdir( self.projectFolderpath ):
            logging.critical( _("Project folder {} doesn't exist -- we'll try creating it!").format( self.projectFolderpath ) )
            os.mkdir( self.projectFolderpath )
        self.containingFolderpath, self.folderName = os.path.split( self.projectFolderpath )
    # end of BiblelatorProjectSettings.__init__


    def saveNameAndAbbreviation( self, projectName:str, projectAbbreviation:str ) -> None:
        """
        Accept a project name and abbreviation.

        Used when starting a new project.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "BiblelatorProjectSettings.saveNameAndAbbreviation( {!r}, {!r} )".format( projectName, projectAbbreviation ) )
            assert self.data is None

        self.reset() # Create new settings in self.data
        self.data['Project'] = {}
        main = self.data['Project']
        main['Name'] = projectName
        main['Abbreviation'] = projectAbbreviation
        self.saveINI() # Write the basic data
    # end of BiblelatorProjectSettings.saveNameAndAbbreviation


    def saveNewBookSettings( self, detailsDict ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "BiblelatorProjectSettings.saveNewBookSettings( {} )".format( detailsDict ) )
            assert self.data is not None

        self.data['NewBooks'] = {}
        newBooks = self.data['NewBooks']
        for someKey,someValue in detailsDict.items():
            newBooks[someKey] = someValue
        self.saveINI() # Write the added data
    # end of BiblelatorProjectSettings.saveNewBookSettings


    def loadUSFMMetadataInto( self, theUSFMBible ):
        """
        Using metadata from the project settings file,
            load the information into the given USFMBible object.
        """
        vPrint( 'Info', debuggingThisModule, "BiblelatorProjectSettings.loadUSFMMetadataInto( {} )".format( theUSFMBible ) )

        self.loadINI() # Load the project settings into self.data

        main = self.data['Project']
        try: theUSFMBible.name = main['Name']
        except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'Name'", self.folderName ) )
        try: theUSFMBible.abbreviation = main['Abbreviation']
        except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'Abbreviation'", self.folderName ) )
    # end of BiblelatorProjectSettings.loadUSFMMetadataInto
# end of class BiblelatorProjectSettings



class uWProjectSettings( Settings ):
    """
    Settings class for uW USFM edit windows.
    """
    def __init__( self, projectFolderpath ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "uWProjectSettings.__init__( {!r} )".format( projectFolderpath ) )
        self.projectFolderpath = projectFolderpath
        self.objectNameString = 'uW Project Settings object'
        self.objectTypeString = 'uWProjectSettings'
        self.settingsFilename = 'manifest.yaml'
        self.data = None

        self.settingsFilepath = os.path.join( projectFolderpath, self.settingsFilename )
        if not os.path.isdir( self.projectFolderpath ):
            logging.critical( _("Project folder {} doesn't exist -- we'll try creating it!").format( self.projectFolderpath ) )
            os.mkdir( self.projectFolderpath )
        self.containingFolderpath, self.folderName = os.path.split( self.projectFolderpath )
    # end of uWProjectSettings.__init__


    # def saveNameAndAbbreviation( self, projectName, projectAbbreviation ):
    #     """
    #     """
    #     if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
    #         vPrint( 'Quiet', debuggingThisModule, "uWProjectSettings.saveNameAndAbbreviation( {!r}, {!r} )".format( projectName, projectAbbreviation ) )
    #         assert self.data is None

    #     self.reset() # Create new settings in self.data
    #     self.data['Project'] = {}
    #     main = self.data['Project']
    #     main['Name'] = projectName
    #     main['Abbreviation'] = projectAbbreviation
    #     self.saveINI() # Write the basic data
    # # end of uWProjectSettings.saveNameAndAbbreviation


    # def saveNewBookSettings( self, detailsDict ):
    #     """
    #     """
    #     if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
    #         vPrint( 'Quiet', debuggingThisModule, "uWProjectSettings.saveNewBookSettings( {} )".format( detailsDict ) )
    #         assert self.data is not None

    #     self.data['NewBooks'] = {}
    #     newBooks = self.data['NewBooks']
    #     for someKey,someValue in detailsDict.items():
    #         newBooks[someKey] = someValue
    #     self.saveYAML() # Write the added data
    # # end of uWProjectSettings.saveNewBookSettings


    def loadUWMetadataInto( self, theUSFMBible ):
        """
        Using metadata from the manifest.yaml project settings file,
            load the information into the given USFMBible object.
        """
        vPrint( 'Quiet', debuggingThisModule, f"uWProjectSettings.loadUWMetadataInto( {theUSFMBible} )" )

        self.loadYAML() # Load the project settings into self.data
        # print( "Got", self.data.keys() )

        if self.data:
            # main = self.data['dublin_core']
            # try: theUSFMBible.name = main['title']
            # except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'title'", self.folderName ) )
            # try: theUSFMBible.abbreviation = main['identifier'].upper()
            # except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'identifier'", self.folderName ) )
            if theUSFMBible.suppliedMetadata is None: theUSFMBible.suppliedMetadata = {}
            if 'uW' not in theUSFMBible.suppliedMetadata: theUSFMBible.suppliedMetadata['uW'] = {}
            assert 'Manifest' not in theUSFMBible.suppliedMetadata['uW']
            theUSFMBible.suppliedMetadata['uW']['Manifest'] = self.data
            theUSFMBible.applySuppliedMetadata( 'uW' ) # Copy some files to theUSFMBible.settingsDict
    # end of uWProjectSettings.loadUWMetadataInto
# end of class uWProjectSettings



def briefDemo() -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    s = Settings()
    print( "New s", s )

    s.settingsFilepath = '/mnt/SSDs/Bibles/English translations/unfoldingWordVersions/en_ust/manifest.yaml'
    s.loadYAML()
    print( "Filled s", s )
# end of Settings.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    s = Settings()
    print( "New s", s )

    s.settingsFilepath = '/mnt/SSDs/Bibles/English translations/unfoldingWordVersions/en_ust/manifest.yaml'
    s.loadYAML()
    print( "Filled s", s )
# end of Settings.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of Settings.py
