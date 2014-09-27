#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ApplicationSettings.py
#   Last modified: 2014-09-25 (also update ProgVersion below)
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

ProgName = "ApplicationSettings"
ProgVersion = "0.11"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, os.path, configparser, logging
from gettext import gettext as _
#import multiprocessing


# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals

# Biblelator imports
#from BiblelatorGlobals import MAX_WINDOWS, MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE, GROUP_CODES, editModeNormal



class ApplicationSettings:
    def __init__( self, dataFolderName, settingsFolderName, settingsFilename ):
        """
        Try to find where the settings file might be (if anywhere).
        """
        if Globals.debugFlag and debuggingThisModule:
            print( "ApplicationSettings.__init__( {} {} {} )".format( repr(dataFolderName), repr(settingsFolderName), repr(settingsFilename) ) )
        self.dataFolderName, self.settingsFolderName, self.settingsFilename = dataFolderName, settingsFolderName, settingsFilename
        if not self.settingsFilename.endswith( '.ini' ):
            self.settingsFilename = self.settingsFilename + '.ini'
        self.dataFolder = self.settingsFolder = self.settingsFilepath = None
        possibleFolders = ( os.path.expanduser('~'), os.getcwd(), os.curdir, os.pardir )
        if Globals.debugFlag and debuggingThisModule:
            print( "possibleFolders", possibleFolders )
        for folder in possibleFolders:
            if os.path.isdir( folder ) and os.access( folder, os.W_OK ):
                ourFolder1 = os.path.join( folder, dataFolderName )
                if os.path.isdir( ourFolder1 ) and os.access( ourFolder1, os.W_OK ):
                    self.dataFolder = ourFolder1
                    if Globals.debugFlag and debuggingThisModule:
                        print( "Found dataFolder = ", self.dataFolder )
                    ourFolder2 = os.path.join( self.dataFolder, settingsFolderName )
                    if os.path.isdir( ourFolder2 ) and os.access( ourFolder2, os.W_OK ):
                        self.settingsFolder = ourFolder2
                        if Globals.debugFlag and debuggingThisModule:
                            print( "Found settingsFolder = ", self.settingsFolder )
                        ourFilepath = os.path.join( ourFolder2, self.settingsFilename )
                        if os.path.isfile( ourFilepath ) and os.access( ourFilepath, os.W_OK ):
                            self.settingsFilepath = ourFilepath
                            if Globals.verbosityLevel > 2 or Globals.debugFlag:
                                print( "Found settingsFilepath = ", self.settingsFilepath )
                    break

        # Create new data and settings folders if necessary
        if not self.dataFolder:
            logging.info( _("No data folder found") )
            for folder in possibleFolders:
                if os.path.isdir( folder ) and os.access( folder, os.W_OK ):
                    logging.info( _("Creating our data folder in '{}'").format( folder ) )
                    self.dataFolder = os.path.join( folder, dataFolderName )
                    os.mkdir( self.dataFolder )
                    break
        if not self.settingsFolder:
            logging.info( _("No settings folder found") )
            if os.path.isdir( self.dataFolder ) and os.access( self.dataFolder, os.W_OK ):
                logging.info( _("Creating our settings folder in '{}'").format( self.dataFolder ) )
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

    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    print( "Running {} demo...".format( ProgName ) )
    #Globals.debugFlag = True

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
    # Configure basic set-up
    parser = Globals.setup( ProgName, ProgVersion )
    Globals.addStandardOptionsAndProcess( parser )

    #multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables
    #printMultiprocessingInfo( 'main' )

    demo()

    Globals.closedown( ProgName, ProgVersion )
# end of ApplicationSettings.py
