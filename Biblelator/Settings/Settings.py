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


ProjectSettings class (Settings)
    __init__( projectFolderPath )
    saveNameAndAbbreviation( projectName, projectAbbreviation )
    saveNewBookSettings( detailsDict )
    loadUSFMMetadataInto( theUSFMBible )
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2020-01-22' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorSettings"
PROGRAM_NAME = "Biblelator Settings"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


import os.path
import logging
import configparser
from datetime import datetime

# Biblelator imports
from Biblelator.BiblelatorGlobals import APP_NAME
from Biblelator.Settings.BiblelatorSettingsFunctions import SettingsVersion

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint




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


    def load( self ):
        """
        Load the settings file (if we found it).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ApplicationSettings.load() from {!r}".format( self.settingsFilepath ) )

        self.reset() # Creates self.data
        assert self.data
        if self.settingsFilepath and os.path.isfile( self.settingsFilepath ) and os.access( self.settingsFilepath, os.R_OK ):
            self.data.read( self.settingsFilepath )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            for section in self.data:
                print( f"  Settings.load: s.d main section = {section}" )
    #end of Settings.load


    def save( self ):
        """
        Save all of the program settings to disk.
            They must have already been saved into self.data.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ApplicationSettings.save() in {!r}".format( self.settingsFilepath ) )
            assert self.data
            assert self.settingsFilepath

        BibleOrgSysGlobals.backupAnyExistingFile( self.settingsFilepath, numBackups=8 )
        with open( self.settingsFilepath, 'wt', encoding='utf-8' ) as settingsFile: # It may or may not have previously existed
            # Put a (comment) heading in the file first
            settingsFile.write( '# ' + _("{} {} settings file v{}").format( APP_NAME, PROGRAM_VERSION, SettingsVersion ) + '\n' )
            settingsFile.write( '# ' + _("Originally saved {} as {}") \
                .format( datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.settingsFilepath ) + '\n\n' )

            self.data.write( settingsFile )
    # end of Settings.save
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
            print( "ApplicationSettings.__init__( {!r}, {!r}, {!r}, {!r} )".format( homeFolderName, dataFolderName, settingsFolderName, settingsFilename ) )
        self.dataFolderName, self.settingsFolderName, self.settingsFilename = dataFolderName, settingsFolderName, settingsFilename
        # NOTE: Settings.__init__ is NOT called -- not needed
        self.objectNameString = 'Application Settings object'
        self.objectTypeString = 'ApplicationSettings'
        self.data = None

        if not self.settingsFilename.lower().endswith( '.ini' ):
            self.settingsFilename = self.settingsFilename + '.ini'
        self.dataFolderPath = self.settingsFolder = self.settingsFilepath = None
        ourFolderPath1 = os.path.join( homeFolderName, dataFolderName )
        if os.path.isdir( ourFolderPath1 ) and os.access( ourFolderPath1, os.W_OK ):
            self.dataFolderPath = ourFolderPath1
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "ApplicationSettings.__init__: Found dataFolderPath = ", self.dataFolderPath )
            ourFolderPath2 = os.path.join( self.dataFolderPath, settingsFolderName )
            if os.path.isdir( ourFolderPath2 ) and os.access( ourFolderPath2, os.W_OK ):
                self.settingsFolder = ourFolderPath2
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    print( "ApplicationSettings.__init__: Found settingsFolder = ", self.settingsFolder )
                ourFilepath = os.path.join( ourFolderPath2, self.settingsFilename )
                if os.path.isfile( ourFilepath ) and os.access( ourFilepath, os.W_OK ):
                    self.settingsFilepath = ourFilepath
                    if BibleOrgSysGlobals.verbosityLevel > 2 or BibleOrgSysGlobals.debugFlag:
                        print( "ApplicationSettings.__init__: Found settingsFilepath = ", self.settingsFilepath )

        # Create new data and settings folders if necessary
        if not self.dataFolderPath:
            logging.info( "ApplicationSettings.__init__ " + _("No data folder found") )
            if os.path.isdir( homeFolderName ) and os.access( homeFolderName, os.W_OK ):
                logging.info( "ApplicationSettings.__init__ " + _("Creating our data folder in {!r}").format( homeFolderName ) )
                self.dataFolderPath = os.path.join( homeFolderName, dataFolderName )
                os.mkdir( self.dataFolderPath )
        if not self.settingsFolder:
            logging.info( "ApplicationSettings.__init__ " + _("No settings folder found") )
            if os.path.isdir( self.dataFolderPath ) and os.access( self.dataFolderPath, os.W_OK ):
                logging.info( "ApplicationSettings.__init__ " + _("Creating our settings folder in {!r}").format( self.dataFolderPath ) )
                self.settingsFolder = os.path.join( self.dataFolderPath, settingsFolderName )
                os.mkdir( self.settingsFolder )
        if not self.settingsFilepath:
            logging.info( "ApplicationSettings.__init__ " + _("No settings file found") )
            self.settingsFilepath = os.path.join( self.settingsFolder, self.settingsFilename )
    # end of ApplicationSettings.__init__
# end of class ApplicationSettings



class ProjectSettings( Settings ):
    """
    Settings class for USFM edit windows.
    """
    def __init__( self, projectFolderPath ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ProjectSettings.__init__( {!r} )".format( projectFolderPath ) )
        self.projectFolderPath = projectFolderPath
        self.objectNameString = 'Project Settings object'
        self.objectTypeString = 'ProjectSettings'
        self.settingsFilename = 'ProjectSettings.ini'
        self.data = None

        self.settingsFilepath = os.path.join( projectFolderPath, self.settingsFilename )
        if not os.path.isdir( self.projectFolderPath ):
            logging.critical( _("Project folder {} doesn't exist -- we'll try creating it!").format( self.projectFolderPath ) )
            os.mkdir( self.projectFolderPath )
        self.containingFolderPath, self.folderName = os.path.split( self.projectFolderPath )
    # end of ProjectSettings.__init__


    def saveNameAndAbbreviation( self, projectName, projectAbbreviation ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ProjectSettings.saveNameAndAbbreviation( {!r}, {!r} )".format( projectName, projectAbbreviation ) )
            assert self.data is None

        self.reset() # Create new settings in self.data
        self.data['Project'] = {}
        main = self.data['Project']
        main['Name'] = projectName
        main['Abbreviation'] = projectAbbreviation
        self.save() # Write the basic data
    # end of ProjectSettings.saveNameAndAbbreviation


    def saveNewBookSettings( self, detailsDict ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ProjectSettings.saveNewBookSettings( {} )".format( detailsDict ) )
            assert self.data is not None

        self.data['NewBooks'] = {}
        newBooks = self.data['NewBooks']
        for someKey,someValue in detailsDict.items():
            newBooks[someKey] = someValue
        self.save() # Write the added data
    # end of ProjectSettings.saveNewBookSettings


    def loadUSFMMetadataInto( self, theUSFMBible ):
        """
        Using metadata from the project settings file,
            load the information into the given USFMBible object.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ProjectSettings.loadUSFMMetadataInto( {} )".format( theUSFMBible ) )

        self.load() # Load the project settings into self.data

        main = self.data['Project']
        try: theUSFMBible.name = main['Name']
        except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'Name'", self.folderName ) )
        try: theUSFMBible.abbreviation = main['Abbreviation']
        except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'Abbreviation'", self.folderName ) )
    # end of ProjectSettings.loadUSFMMetadataInto
# end of class ProjectSettings



def demo() -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    print( "Running {} demo…".format( PROGRAM_NAME ) )

    tkRootWindow = Tk()
    # Calls to the window manager class (wm in Tk)
    tkRootWindow.geometry( "{}x{}+{}+{}".format( 320, 100, 2000, 100 ) ) # width, height, xOffset, yOffset
    tkRootWindow.title( programNameVersion )
    tkRootWindow.minsize( 300, 50 )
    tkRootWindow.maxsize( 400, 200 )

    #geometryMap = parseWindowGeometry( tkRootWindow.winfo_geometry() )
    #print( "geometry", geometryMap )
    #for something in geometryMap:
        #print( repr(something) )


    settings = ApplicationSettings( BibleOrgSysGlobals.findHomeFolderPath(), 'BiblelatorData/', 'BiblelatorSettings/', PROGRAM_NAME )
    settings.load()
    print( str(settings) )
    print( repr(settings) )

    #tkRootWindow.destroy() #  Useful if we want to measure the start-up time

    # Start the program running
    tkRootWindow.mainloop()
# end of ApplicationSettings.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of Settings.py
