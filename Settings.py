#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Settings.py
#
# Handle settings for Biblelator Bible display/editing
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

LastModifiedDate = '2016-04-23' # by RJH
ShortProgName = "Settings"
ProgName = "Biblelator Settings"
ProgVersion = '0.34'
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import os.path, configparser, logging

# Biblelator imports

# BibleOrgSys imports
if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals



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
        nameBit = '{}{}{}'.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit+': ' if nameBit else '', errorBit )
# end of exp



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
            print( exp("ApplicationSettings.load() from {!r}").format( self.settingsFilepath ) )

        self.reset() # Creates self.data
        assert self.data
        if self.settingsFilepath and os.path.isfile( self.settingsFilepath ) and os.access( self.settingsFilepath, os.R_OK ):
            self.data.read( self.settingsFilepath )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            for section in self.data:
                print( "  Settings.load: s.d main section =", section )
    #end of Settings.load


    def save( self ):
        """
        Save all of the program settings to disk.
            They must have already been saved into self.data.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ApplicationSettings.save() in {!r}").format( self.settingsFilepath ) )
            assert self.data
            assert self.settingsFilepath

        BibleOrgSysGlobals.backupAnyExistingFile( self.settingsFilepath, numBackups=4 )
        with open( self.settingsFilepath, 'wt', encoding='utf-8' ) as settingsFile: # It may or may not have previously existed
            self.data.write( settingsFile )
    # end of Settings.save
# end of class Settings



class ApplicationSettings( Settings ):
    def __init__( self, homeFolderName, dataFolderName, settingsFolderName, settingsFilename ):
        """
        This class is used before the main program starts.

        Try to find where the main settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ApplicationSettings.__init__( {!r}, {!r}, {!r}, {!r} )").format( homeFolderName, dataFolderName, settingsFolderName, settingsFilename ) )
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
                print( exp("Found dataFolderPath = "), self.dataFolderPath )
            ourFolderPath2 = os.path.join( self.dataFolderPath, settingsFolderName )
            if os.path.isdir( ourFolderPath2 ) and os.access( ourFolderPath2, os.W_OK ):
                self.settingsFolder = ourFolderPath2
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    print( exp("Found settingsFolder = "), self.settingsFolder )
                ourFilepath = os.path.join( ourFolderPath2, self.settingsFilename )
                if os.path.isfile( ourFilepath ) and os.access( ourFilepath, os.W_OK ):
                    self.settingsFilepath = ourFilepath
                    if BibleOrgSysGlobals.verbosityLevel > 2 or BibleOrgSysGlobals.debugFlag:
                        print( exp("Found settingsFilepath = "), self.settingsFilepath )

        # Create new data and settings folders if necessary
        if not self.dataFolderPath:
            logging.info( exp("No data folder found") )
            if os.path.isdir( homeFolderName ) and os.access( homeFolderName, os.W_OK ):
                logging.info( exp("Creating our data folder in {!r}").format( homeFolderName ) )
                self.dataFolderPath = os.path.join( homeFolderName, dataFolderName )
                os.mkdir( self.dataFolderPath )
        if not self.settingsFolder:
            logging.info( exp("No settings folder found") )
            if os.path.isdir( self.dataFolderPath ) and os.access( self.dataFolderPath, os.W_OK ):
                logging.info( exp("Creating our settings folder in {!r}").format( self.dataFolderPath ) )
                self.settingsFolder = os.path.join( self.dataFolderPath, settingsFolderName )
                os.mkdir( self.settingsFolder )
        if not self.settingsFilepath:
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
            print( exp("ProjectSettings.__init__( {!r} )").format( projectFolderPath ) )
        self.projectFolderPath = projectFolderPath
        self.objectNameString = 'Project Settings object'
        self.objectTypeString = 'ProjectSettings'
        self.settingsFilename = 'ProjectSettings.ini'
        self.data = None

        self.settingsFilepath = os.path.join( projectFolderPath, self.settingsFilename )
        if not os.path.isdir( self.projectFolderPath ):
            logging.critical( exp("Project folder {} doesn't exist -- try creating it!").format( self.projectFolderPath ) )
            os.mkdir( self.projectFolderPath )
        self.containingFolderPath, self.folderName = os.path.split( self.projectFolderPath )
    # end of ProjectSettings.__init__


    def saveNameAndAbbreviation( self, projectName, projectAbbreviation ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ProjectSettings.saveNameAndAbbreviation( {!r}, {!r} )").format( projectName, projectAbbreviation ) )
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
            print( exp("ProjectSettings.saveNewBookSettings( {} )").format( detailsDict ) )
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
            print( exp("ProjectSettings.loadUSFMMetadataInto( {} )").format( theUSFMBible ) )

        self.load() # Load the project settings into self.data

        main = self.data['Project']
        try: theUSFMBible.name = main['Name']
        except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'Name'", self.folderName ) )
        try: theUSFMBible.abbreviation = main['Abbreviation']
        except KeyError: logging.critical( "Missing {} field in {!r} project settings".format( "'Abbreviation'", self.folderName ) )
    # end of ProjectSettings.loadUSFMMetadataInto
# end of class ProjectSettings



def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    print( exp("Running {} demo…").format( ProgName ) )

    tkRootWindow = Tk()
    # Calls to the window manager class (wm in Tk)
    tkRootWindow.geometry( "{}x{}+{}+{}".format( 320, 100, 2000, 100 ) ) # width, height, xOffset, yOffset
    tkRootWindow.title( ProgNameVersion )
    tkRootWindow.minsize( 300, 50 )
    tkRootWindow.maxsize( 400, 200 )

    #geometryMap = parseWindowGeometry( tkRootWindow.winfo_geometry() )
    #print( "geometry", geometryMap )
    #for something in geometryMap:
        #print( repr(something) )


    settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', ProgName )
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
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )


    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of Settings.py