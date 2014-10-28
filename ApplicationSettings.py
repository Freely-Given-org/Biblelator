#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ApplicationSettings.py
#   Last modified: 2014-10-23 (also update ProgVersion below)
#
# Main program for Biblelator Bible display/editing
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

ShortProgName = "ApplicationSettings"
ProgName = "Application Settings"
ProgVersion = "0.19"
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



class ApplicationSettings:
    def __init__( self, dataFolderName, settingsFolderName, settingsFilename ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("ApplicationSettings.__init__( {} {} {} )").format( repr(dataFolderName), repr(settingsFolderName), repr(settingsFilename) ) )
        self.dataFolderName, self.settingsFolderName, self.settingsFilename = dataFolderName, settingsFolderName, settingsFilename
        if not self.settingsFilename.endswith( '.ini' ):
            self.settingsFilename = self.settingsFilename + '.ini'
        self.dataFolder = self.settingsFolder = self.settingsFilepath = None
        possibleFolders = ( os.path.expanduser('~'), os.getcwd(), os.curdir, os.pardir )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "possibleFolders", possibleFolders )
        for folder in possibleFolders:
            if os.path.isdir( folder ) and os.access( folder, os.W_OK ):
                ourFolder1 = os.path.join( folder, dataFolderName )
                if os.path.isdir( ourFolder1 ) and os.access( ourFolder1, os.W_OK ):
                    self.dataFolder = ourFolder1
                    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                        print( t("Found dataFolder = "), self.dataFolder )
                    ourFolder2 = os.path.join( self.dataFolder, settingsFolderName )
                    if os.path.isdir( ourFolder2 ) and os.access( ourFolder2, os.W_OK ):
                        self.settingsFolder = ourFolder2
                        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                            print( t("Found settingsFolder = "), self.settingsFolder )
                        ourFilepath = os.path.join( ourFolder2, self.settingsFilename )
                        if os.path.isfile( ourFilepath ) and os.access( ourFilepath, os.W_OK ):
                            self.settingsFilepath = ourFilepath
                            if BibleOrgSysGlobals.verbosityLevel > 2 or BibleOrgSysGlobals.debugFlag:
                                print( t("Found settingsFilepath = "), self.settingsFilepath )
                    break

        # Create new data and settings folders if necessary
        if not self.dataFolder:
            logging.info( t("No data folder found") )
            for folder in possibleFolders:
                if os.path.isdir( folder ) and os.access( folder, os.W_OK ):
                    logging.info( t("Creating our data folder in '{}'").format( folder ) )
                    self.dataFolder = os.path.join( folder, dataFolderName )
                    os.mkdir( self.dataFolder )
                    break
        if not self.settingsFolder:
            logging.info( t("No settings folder found") )
            if os.path.isdir( self.dataFolder ) and os.access( self.dataFolder, os.W_OK ):
                logging.info( t("Creating our settings folder in '{}'").format( self.dataFolder ) )
                self.settingsFolder = os.path.join( self.dataFolder, settingsFolderName )
                os.mkdir( self.settingsFolder )
        if not self.settingsFilepath:
            self.settingsFilepath = os.path.join( self.settingsFolder, self.settingsFilename )
    # end of ApplicationSettings.__init__


    def __str__( self ):
        result = ""
        for item in self.data.items():
            result += str( item )
        return result
    def __repr__( self ):
        return repr( self.data.items() )


    def reset( self ):
        """
        Create a blank settings object.
        """
        self.data = configparser.ConfigParser()
        self.data.optionxform = lambda option: option # Force true case matches for options (default is all lower case)
    # end of ApplicationSettings.reset


    def load( self ):
        """
        Load the settings file (if we found it).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("ApplicationSettings.load()") )
        self.reset() # Creates self.data
        assert( self.data )
        if self.settingsFilepath and os.path.isfile( self.settingsFilepath ) and os.access( self.settingsFilepath, os.R_OK ):
            self.data.read( self.settingsFilepath )
    #end of ApplicationSettings.load


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
        # end of ApplicationSettings.save
# end of class ApplicationSettings



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

    geometryMap = parsegeometry( tkRootWindow.geometry() )
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
# end of ApplicationSettings.py