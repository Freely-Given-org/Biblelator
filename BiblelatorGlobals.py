#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BiblelatorGlobals.py
#   Last modified: 2014-10-03 (also update ProgVersion below)
#
# Global variables for Biblelator Bible display/editing
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
Global variables for program to allow editing of USFM Bibles using Python3 and Tkinter.
"""

ShortProgName = "BiblelatorGlobals"
ProgName = "Biblelator Globals"
ProgVersion = "0.13"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = False


import sys, re
#import sys, logging #, os.path, configparser, logging
from gettext import gettext as _
#import multiprocessing

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
#from tkinter import Tk, Menu, StringVar, messagebox
#from tkinter import NORMAL, DISABLED, LEFT, RIGHT, BOTH, YES
#from tkinter.ttk import Style, Frame, Button, Combobox
#from tkinter.tix import Spinbox

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals


def t( messageString ):
    """
    Prepends the module name to a error or warning message string
        if we are in debug mode.
    Returns the new string.
    """
    try: nameBit, errorBit = messageString.split( ': ', 1 )
    except ValueError: nameBit, errorBit = '', messageString
    if Globals.debugFlag or debuggingThisModule:
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit, _(errorBit) )



# Programmed settings
DATA_FOLDER = 'BiblelatorData/'
SETTINGS_SUBFOLDER = 'BiblelatorSettings/'


MAX_WINDOWS = 20


# Default settings (Note: X=width, Y=height)
MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE = 450, 100
MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE = 350, 100
GROUP_CODES = ( 'A', 'B', 'C', 'D' )


# Constants
editModeNormal = 'Edit'
editModeUSFM = 'USFM Edit'



def assembleGeometry( width, height, xOffset, yOffset ):
    return "{}x{}+{}+{}".format( width, height, xOffset, yOffset )
# end of assembleGeometry


def assembleGeometryFromList( geometryValues ):
    width, height, xOffset, yOffset = geometryValues
    return "{}x{}+{}+{}".format( width, height, xOffset, yOffset )
# end of assembleGeometry


def parseGeometry( geometry ):
    """
    Given a TKinter geometry string, e,g., 493x152+820+491 or 493x123+-119+9
        being width, height, xOffset, yOffset
    return a list containing the four integer values.
    """
    m = re.match("(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geometry)
    if not m:
        raise ValueError( "parseGeometry: failed to parse geometry string {}".format( repr(geometry) ) )
    return [int(digits) for digits in m.groups()]
# end of parseGeometry



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if Globals.debugFlag: print( t("Running demo...") )

    print( "assembleGeometry( 123, 234, 345, 456 ) = {}".format( assembleGeometry( 123, 234, 345, 456 ) ) )
    g1, g2 = "493x152+820+491", "493x123+-119+9"
    p1, p2 = parseGeometry( g1 ), parseGeometry( g2 )
    print( "parseGeometry( {} ) = {}".format( g1, p1 ) )
    print( "assembleGeometryFromList( {} ) = {}".format( p1, assembleGeometryFromList( p1 ) ) )
    print( "parseGeometry( {} ) = {}".format( g2, p2 ) )
    print( "assembleGeometryFromList( {} ) = {}".format( p2, assembleGeometryFromList( p2 ) ) )

    #tkRootWindow = Tk()
    #tkRootWindow.title( ProgNameVersion )
    #settings = ApplicationSettings( DATA_FOLDER, SETTINGS_SUBFOLDER, ProgName )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    #tkRootWindow.mainloop()
# end of BiblelatorGlobals.demo


if __name__ == '__main__':
    import multiprocessing

    # Configure basic set-up
    parser = Globals.setup( ProgName, ProgVersion )
    Globals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if 1 and Globals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    Globals.closedown( ProgName, ProgVersion )
# end of BiblelatorGlobals.py