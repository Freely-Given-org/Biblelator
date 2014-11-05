#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Settings.py
#   Last modified: 2014-11-06 (also update ProgVersion below)
#
# Handle settings for Biblelator Bible display/editing
#
# Copyright (C) 2013-2014 Robert Hunt
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
"""

ShortProgName = "Settings"
ProgName = "Biblelator Settings"
ProgVersion = "0.22"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, os.path, configparser, logging
from gettext import gettext as _

# Biblelator imports

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import BibleOrgSysGlobals



def t( messageString ):
    """
    Prepends the module name to a error or warning message string
        if we are in debug mode.
    Returns the new string.
    """
    try: nameBit, errorBit = messageString.split( ': ', 1 )
    except ValueError: nameBit, errorBit = '', messageString
    if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit, _(errorBit) )



class Settings:
    """
    A class containing our basic common functions for loading and saving settings, etc.
        This class is designed to be a base class only.

    Biblelator settings are designed to be human readable (and therefore easily hackable).
        For this reason, the "Windows ini" type format was chosen
            over more complex and less readable formats like XML.
    """
    def __init__( self ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        self.objectNameString = "Settings object"
        self.objectTypeString = "Settings"
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("ApplicationSettings.load()") )
        self.reset() # Creates self.data
        assert( self.data )
        if self.settingsFilepath and os.path.isfile( self.settingsFilepath ) and os.access( self.settingsFilepath, os.R_OK ):
            self.data.read( self.settingsFilepath )
    #end of Settings.load


    def save( self ):
        """
        Save all of the program settings to disk.
            They must have already been saved into self.data.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("ApplicationSettings.save()") )
        assert( self.data )
        assert( self.settingsFilepath )
        with open( self.settingsFilepath, 'wt') as settingsFile: # It may or may not have previously existed
            self.data.write( settingsFile )
    # end of Settings.save
# end of class Settings



class ApplicationSettings( Settings ):
    def __init__( self, homeFolderName, dataFolderName, settingsFolderName, settingsFilename ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("ApplicationSettings.__init__( {}, {}, {}, {} )").format( repr(homeFolderName), repr(dataFolderName), repr(settingsFolderName), repr(settingsFilename) ) )
        self.dataFolderName, self.settingsFolderName, self.settingsFilename = dataFolderName, settingsFolderName, settingsFilename
        self.objectNameString = "Application Settings object"
        self.objectTypeString = "ApplicationSettings"
        self.data = None

        if not self.settingsFilename.endswith( '.ini' ):
            self.settingsFilename = self.settingsFilename + '.ini'
        self.dataFolderPath = self.settingsFolder = self.settingsFilepath = None
        ourFolderPath1 = os.path.join( homeFolderName, dataFolderName )
        if os.path.isdir( ourFolderPath1 ) and os.access( ourFolderPath1, os.W_OK ):
            self.dataFolderPath = ourFolderPath1
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( t("Found dataFolderPath = "), self.dataFolderPath )
            ourFolderPath2 = os.path.join( self.dataFolderPath, settingsFolderName )
            if os.path.isdir( ourFolderPath2 ) and os.access( ourFolderPath2, os.W_OK ):
                self.settingsFolder = ourFolderPath2
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    print( t("Found settingsFolder = "), self.settingsFolder )
                ourFilepath = os.path.join( ourFolderPath2, self.settingsFilename )
                if os.path.isfile( ourFilepath ) and os.access( ourFilepath, os.W_OK ):
                    self.settingsFilepath = ourFilepath
                    if BibleOrgSysGlobals.verbosityLevel > 2 or BibleOrgSysGlobals.debugFlag:
                        print( t("Found settingsFilepath = "), self.settingsFilepath )

        # Create new data and settings folders if necessary
        if not self.dataFolderPath:
            logging.info( t("No data folder found") )
            if os.path.isdir( homeFolderName ) and os.access( homeFolderName, os.W_OK ):
                logging.info( t("Creating our data folder in {}").format( repr(homeFolderName) ) )
                self.dataFolderPath = os.path.join( homeFolderName, dataFolderName )
                os.mkdir( self.dataFolderPath )
        if not self.settingsFolder:
            logging.info( t("No settings folder found") )
            if os.path.isdir( self.dataFolderPath ) and os.access( self.dataFolderPath, os.W_OK ):
                logging.info( t("Creating our settings folder in {}").format( repr(self.dataFolderPath) ) )
                self.settingsFolder = os.path.join( self.dataFolderPath, settingsFolderName )
                os.mkdir( self.settingsFolder )
        if not self.settingsFilepath:
            self.settingsFilepath = os.path.join( self.settingsFolder, self.settingsFilename )
    # end of ApplicationSettings.__init__
# end of class ApplicationSettings



class ProjectSettings( Settings ):
    def __init__( self, projectFolderPath ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("ProjectSettings.__init__( {} )").format( repr(projectFolderPath) ) )
        self.projectFolderPath = projectFolderPath
        self.objectNameString = "Project Settings object"
        self.objectTypeString = "ProjectSettings"
        self.settingsFilename = "ProjectSettings.ini"
        self.data = None

        self.settingsFilepath = os.path.join( projectFolderPath, self.settingsFilename )
        if not os.path.isdir( self.projectFolderPath ):
            logging.critical( t("Project folder {} doesn't exist -- try creating it!").format( self.projectFolderPath ) )
            os.mkdir( self.projectFolderPath )
        self.containingFolderPath, self.folderName = os.path.split( self.projectFolderPath )
    # end of ProjectSettings.__init__


    def saveNameAndAbbreviation( self, projectName, projectAbbreviation ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("ProjectSettings.saveNameAndAbbreviation( {}, {} )").format( repr(projectName), repr(projectAbbreviation) ) )
            assert( self.data is None )

        self.reset() # Create new settings in self.data
        self.data['Project'] = {}
        main = self.data['Project']
        main['Name'] = projectName
        main['Abbreviation'] = projectAbbreviation
        self.save() # Write the basic data
    # end of ProjectSettings.saveNameAndAbbreviation


    def loadUSFMData( self, theUSFMBible ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("ProjectSettings.loadUSFMData( {} )").format( theUSFMBible ) )

        self.load() # Load the project settings into self.data

        main = self.data['Project']
        try: theUSFMBible.name = main['Name']
        except KeyError: logging.critical( "Missing {} field in {} project settings".format( "'Name'", repr(self.folderName) ) )
        try: theUSFMBible.abbreviation = main['Abbreviation']
        except KeyError: logging.critical( "Missing {} field in {} project settings".format( "'Abbreviation'", repr(self.folderName) ) )
    # end of ProjectSettings.loadUSFMData
# end of class ProjectSettings



def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    print( t("Running {} demo...").format( ProgName ) )

    tkRootWindow = Tk()
    # Calls to the window manager class (wm in Tk)
    tkRootWindow.geometry( "{}x{}+{}+{}".format( 320, 100, 2000, 100 ) ) # width, height, xOffset, yOffset
    tkRootWindow.title( ProgNameVersion )
    tkRootWindow.minsize( 300, 50 )
    tkRootWindow.maxsize( 400, 200 )

    geometryMap = parseWindowGeometry( tkRootWindow.geometry() )
    print( "geometry", geometryMap )
    for something in geometryMap:
        print( repr(something) )


    settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', ProgName )
    settings.load()
    print( str(settings) )
    print( repr(settings) )

    #tkRootWindow.destroy() #  Useful if we want to measure the start-up time

    # Start the program running
    tkRootWindow.mainloop()
# end of ApplicationSettings.demo


if __name__ == '__main__':
    #import multiprocessing

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    #multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables
    #printMultiprocessingInfo( 'main' )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of Settings.py