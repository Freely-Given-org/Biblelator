#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BiblelatorGlobals.py
#   Last modified: 2014-11-02 (also update ProgVersion below)
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
ProgVersion = "0.21"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = False


import sys, os, re
from gettext import gettext as _
#import multiprocessing

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



# Programmed settings
APP_NAME = 'Biblelator'
DATA_FOLDER = APP_NAME + 'Data/'
LOGGING_SUBFOLDER = APP_NAME + 'Logs/'
SETTINGS_SUBFOLDER = APP_NAME + 'Settings/'


START = '1.0' # constant for tkinter


MAX_WINDOWS = 20


# Default settings (Note: X=width, Y=height)
MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE = 550, 150
MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE = 350, 150
MINIMUM_HELP_X_SIZE, MINIMUM_HELP_Y_SIZE = 350, 150
MINIMUM_ABOUT_X_SIZE, MINIMUM_ABOUT_Y_SIZE = 350, 150

BIBLE_GROUP_CODES = ( 'A', 'B', 'C', 'D' )
BIBLE_CONTEXT_VIEW_MODES = ( 'BeforeAndAfter', 'BySection', 'ByVerse', 'ByBook', 'ByChapter' )


# Constants
EDIT_MODE_NORMAL = 'Edit'
EDIT_MODE_USFM = 'USFM Edit'


DEFAULT_KEY_BINDING_DICT = { 'Cut':('Ctrl+x','<Control-X>','<Control-x>'), 'Copy':('Ctrl+c','<Control-C>','<Control-c>'),
        'Paste':('Ctrl+v','<Control-V>','<Control-v>'), 'SelectAll':('Ctrl+a','<Control-A>','<Control-a>'),
        'Find':('Ctrl+f','<Control-F>','<Control-f>'), 'Refind':('F3/Ctrl+g','<Control-G>','<Control-g>','<F3>'),
        'Undo':('Ctrl+z','<Control-Z>','<Control-z>'), 'Redo':('Ctrl+y','<Control-Y>','<Control-y>','<Control-Shift-Z>','<Control-Shift-z>'),
        'Line':('Ctrl+l','<Control-L>','<Control-l>'), 'Save':('Ctrl+c','<Control-S>','<Control-s>'),
        'Help':('F1','<F1>'), 'Info':('F11','<F11>'), 'About':('F12','<F12>'),
        'Close':('Ctrl+F4','<Control-F4>'), 'Quit':('Alt+F4','<Alt-F4>'), }



def findHomeFolder():
    """
    Attempt to find the user's home folder and return it.
    """
    possibleHomeFolders = ( os.path.expanduser('~'), os.getcwd(), os.curdir, os.pardir )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "possible home folders", possibleHomeFolders )
    for folder in possibleHomeFolders:
        if os.path.isdir( folder ) and os.access( folder, os.W_OK ):
            return folder
# end of BiblelatorGlobals.findHomeFolder


def assembleGeometry( width, height, xOffset, yOffset ):
    return "{}x{}+{}+{}".format( width, height, xOffset, yOffset )
# end of BiblelatorGlobals.assembleGeometry


def assembleGeometryFromList( geometryValues ):
    width, height, xOffset, yOffset = geometryValues
    return "{}x{}+{}+{}".format( width, height, xOffset, yOffset )
# end of BiblelatorGlobals.assembleGeometryFromList


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
# end of BiblelatorGlobals.parseGeometry


def centreWindow( self, width=400, height=250 ):
    """
    """
    screenWidth = self.winfo_screenwidth()
    screenHeight = self.winfo_screenheight()

    x = (screenWidth - width) // 2
    y = (screenHeight - height) // 2
    #print( "centreWindow", width, height, screenWidth, screenHeight, x, y )

    self.geometry('{}x{}+{}+{}'.format( width, height, x, y ) )
# end of BiblelatorGlobals.centreWindow


def centreWindowOnWindow( self, parentWindow, width=400, height=250 ):
    """
    """
    parentWidth, parentHeight, parentXOffset, parentYOffset = parseGeometry( parentWindow.geometry() )
    #print( "centreWindowOnWindow parent is", "w =",parentWidth, "h =",parentHeight, "x =",parentXOffset, "y =",parentYOffset )

    x = parentXOffset + (parentWidth - width) // 2
    y = parentYOffset + (parentHeight - height) // 2
    #print( "centreWindowOnWindow", "w =",width, "h =",height, "x =",x, "y =",y )

    self.geometry('{}x{}+{}+{}'.format( width, height, x, y ) )
# end of BiblelatorGlobals.centreWindowOnWindow


def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( t("Running demo...") )

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
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BiblelatorGlobals.py