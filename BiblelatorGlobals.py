#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorGlobals.py
#
# Global variables for Biblelator Bible display/editing
#
# Copyright (C) 2013-2017 Robert Hunt
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
Global variables and functions for program
  to allow editing of USFM Bibles using Python3 with Tkinter.

    findHomeFolderPath()
    findUsername()
    assembleWindowGeometry( width, height, xOffset, yOffset )
    assembleWindowSize( width, height )
    assembleWindowGeometryFromList( geometryValues )
    assembleWindowSizeFromList( geometryValues )
    parseWindowGeometry( geometry )
    parseWindowSize( geometry )
    centreWindow( self, width=400, height=250 )
    centreWindowOnWindow( self, parentWindow, width=400, height=250 )
    errorBeep()
"""

from gettext import gettext as _

LastModifiedDate = '2017-11-09' # by RJH
ShortProgName = "BiblelatorGlobals"
ProgName = "Biblelator Globals"
ProgVersion = '0.41'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import os, re
try: import pwd
except ImportError:
    pwd = None
    import getpass

# BibleOrgSys imports
import sys; sys.path.append( '../BibleOrgSys/' )
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
    return '{}{}'.format( nameBit, errorBit )
# end of exp



# Programmed settings
APP_NAME = 'Biblelator' # Ugly coz doesn't necessarily match the ProgName in Biblelator.py
APP_NAME_VERSION = '{} v{}'.format( APP_NAME, ProgVersion ) # Ugly coz doesn't necessarily match the ProgVersion in Biblelator.py
DATA_FOLDER_NAME = APP_NAME + 'Data/'
LOGGING_SUBFOLDER_NAME = APP_NAME + 'Logs/'
SETTINGS_SUBFOLDER_NAME = APP_NAME + 'Settings/'
PROJECTS_SUBFOLDER_NAME = APP_NAME + 'Projects/'


 # Constants for tkinter
tkSTART = '1.0'
tkBREAK = 'break'


# Our constants
DEFAULT = 'Default'
EDIT_MODE_NORMAL = 'Edit'
EDIT_MODE_USFM = 'USFM Edit'


MAX_WINDOWS = 20
MAX_RECENT_FILES = 9
MAX_PSEUDOVERSES = 999 # in a non-chapter book like a glossary or something (or before the chapter one marker )
    # NOTE: SimpleVerseKey does not currently handle larger numbers than this.


# Default window size settings (Note: X=width, Y=height)
INITIAL_MAIN_SIZE, INITIAL_MAIN_SIZE_DEBUG, MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE = '607x76', '607x360', '550x75', '700x500'
INITIAL_RESOURCE_SIZE, MINIMUM_RESOURCE_SIZE, MAXIMUM_RESOURCE_SIZE = '600x360', '350x150', '800x600'
INITIAL_RESOURCE_COLLECTION_SIZE, MINIMUM_RESOURCE_COLLECTION_SIZE, MAXIMUM_RESOURCE_COLLECTION_SIZE = '600x360', '350x150', '800x1200'
INITIAL_REFERENCE_COLLECTION_SIZE, MINIMUM_REFERENCE_COLLECTION_SIZE, MAXIMUM_REFERENCE_COLLECTION_SIZE = '600x400', '350x150', '800x1200'
INITIAL_HTML_SIZE, MINIMUM_HTML_SIZE, MAXIMUM_HTML_SIZE = '800x600', '550x200', '1200x800'
INITIAL_RESULT_WINDOW_SIZE, MINIMUM_RESULT_WINDOW_SIZE, MAXIMUM_RESULT_WINDOW_SIZE = '600x400', '550x200', '1200x800'
MINIMUM_HELP_X_SIZE, MINIMUM_HELP_Y_SIZE, MINIMUM_HELP_SIZE, MAXIMUM_HELP_SIZE = '350', '150', '350x150', '500x400'
MINIMUM_ABOUT_X_SIZE, MINIMUM_ABOUT_Y_SIZE, MINIMUM_ABOUT_SIZE, MAXIMUM_ABOUT_SIZE = '350', '150', '350x150', '500x400'

BIBLE_GROUP_CODES = 'A', 'B', 'C', 'D', 'E'
BIBLE_CONTEXT_VIEW_MODES = 'BeforeAndAfter', 'BySection', 'ByVerse', 'ByBook', 'ByChapter'
BIBLE_FORMAT_VIEW_MODES = 'Formatted', 'Unformatted',


# DEFAULT_KEY_BINDING_DICT is a dictionary where
#   the index is a menu word like 'Save'
#   and the entry is a tuple where
#       the first entry is the keyboard description of the shortcut
#       followed by all (i.e., one or more) TKinter values which should be bound to that shortcut.
#
# Not all of these are used for all windows
#
DEFAULT_KEY_BINDING_DICT = {
    _('Cut'):('Ctrl+x','<Control-x>'), #,'<Control-x>'),
    _('Copy'):('Ctrl+c','<Control-c>'), #,'<Control-c>'),
    _('Paste'):('Ctrl+v','<Control-v>'), #,'<Control-v>'),
    _('SelectAll'):('Ctrl+a','<Control-a>'), #,'<Control-a>'),
    _('Find'):('Ctrl+f','<Control-f>'), #,'<Control-f>'),
    _('Refind'):('F3/Ctrl+g','<Control-g>'), #,'<Control-g>','<F3>'),
    _('Replace'):('Ctrl+r','<Control-r>'), #,'<Control-r>'),
    _('Undo'):('Ctrl+z','<Control-z>'), #,'<Control-z>'),
    _('Redo'):('Ctrl+y','<Control-y>'), #,'<Control-y>','<Control-Shift-Z>','<Control-Shift-z>'),
    _('Line'):('Ctrl+l','<Control-l>'), #,'<Control-l>'),
    _('Save'):('Ctrl+s','<Control-s>'), #,'<Control-s>'),
    _('ShowMain'):('F2','<F2>'),
    _('Help'):('F1','<F1>'),
    _('Info'):('F11','<F11>'),
    _('About'):('F12','<F12>'),
    _('Close'):('Ctrl+F4','<Control-F4>'),
    _('Quit'):('Alt+F4','<Alt-F4>'), }
#print( DEFAULT_KEY_BINDING_DICT ); halt



def findHomeFolderPath():
    """
    Attempt to find the path to the user's home folder and return it.
    """
    possibleHomeFolders = ( os.path.expanduser('~'), os.getcwd(), os.curdir, os.pardir )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "possible home folders", possibleHomeFolders )
    for folder in possibleHomeFolders:
        if os.path.isdir( folder ) and os.access( folder, os.W_OK ):
            return folder
# end of BiblelatorGlobals.findHomeFolderPath


def findUsername():
    """
    Attempt to find the current user name and return it.
    """
    if pwd:
        return pwd.getpwuid(os.geteuid()).pw_name
    else:
        return getpass.getuser()
# end of BiblelatorGlobals.findUsername


def assembleWindowGeometry( width, height, xOffset, yOffset ):
    return "{}x{}+{}+{}".format( width, height, xOffset, yOffset )
# end of BiblelatorGlobals.assembleWindowGeometry


def assembleWindowSize( width, height ):
    return "{}x{}".format( width, height )
# end of BiblelatorGlobals.assembleWindowSize


def assembleWindowGeometryFromList( geometryValues ):
    width, height, xOffset, yOffset = geometryValues
    return "{}x{}+{}+{}".format( width, height, xOffset, yOffset )
# end of BiblelatorGlobals.assembleWindowGeometryFromList


def assembleWindowSizeFromList( geometryValues ):
    width, height = geometryValues
    return "{}x{}".format( width, height )
# end of BiblelatorGlobals.assembleWindowSizeFromList


def parseWindowGeometry( geometry ):
    """
    Given a TKinter geometry string, e,g., 493x152+820+491 or 493x123+-119+9
        being width, height, xOffset, yOffset
    return a list containing the four integer values.
    """
    m = re.match("(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geometry)
    if not m:
        raise ValueError( "parseWindowGeometry: failed to parse geometry string {!r}".format( geometry ) )
    return [int(digits) for digits in m.groups()]
# end of BiblelatorGlobals.parseWindowGeometry


def parseWindowSize( geometry ):
    """
    Given a TKinter geometry string, e,g., 493x152 (being width, height)
    return a list containing the two integer values.
    """
    m = re.match("(\d+)x(\d+)", geometry)
    if not m:
        raise ValueError( "parseWindowSize: failed to parse geometry string {!r}".format( geometry ) )
    return [int(digits) for digits in m.groups()]
# end of BiblelatorGlobals.parseWindowSize


def centreWindow( self, width=400, height=250 ):
    """
    """
    if isinstance( width, str ): width = int( width )
    if isinstance( height, str ): height = int( height )

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
    parentWidth, parentHeight, parentXOffset, parentYOffset = parseWindowGeometry( parentWindow.winfo_geometry() )
    #print( "centreWindowOnWindow parent is", "w =",parentWidth, "h =",parentHeight, "x =",parentXOffset, "y =",parentYOffset )

    x = parentXOffset + (parentWidth - width) // 2
    y = parentYOffset + (parentHeight - height) // 2
    #print( "centreWindowOnWindow", "w =",width, "h =",height, "x =",x, "y =",y )

    self.geometry('{}x{}+{}+{}'.format( width, height, x, y ) )
# end of BiblelatorGlobals.centreWindowOnWindow


def errorBeep():
    """
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("errorBeep()") )

    # Does nothing yet :-(

    #import sys
    #from subprocess import call
    #if sys.platform == 'linux': call(["xdg-open","dialog-error.ogg"])
    #elif sys.platform == 'darwin': call(["afplay","dialog-error.ogg"])
    #else: print( "errorBeep: sp", sys.platform )
# end of errorBeep


def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo…") )

    print( "assembleWindowGeometry( 123, 234, 345, 456 ) = {}".format( assembleWindowGeometry( 123, 234, 345, 456 ) ) )
    g1, g2 = "493x152+820+491", "493x123+-119+9"
    p1, p2 = parseWindowGeometry( g1 ), parseWindowGeometry( g2 )
    print( "parseWindowGeometry( {} ) = {}".format( g1, p1 ) )
    print( "assembleWindowGeometryFromList( {} ) = {}".format( p1, assembleWindowGeometryFromList( p1 ) ) )
    print( "parseWindowGeometry( {} ) = {}".format( g2, p2 ) )
    print( "assembleWindowGeometryFromList( {} ) = {}".format( p2, assembleWindowGeometryFromList( p2 ) ) )

    #tkRootWindow = Tk()
    #tkRootWindow.title( ProgNameVersion )
    #settings = ApplicationSettings( DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, ProgName )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    #tkRootWindow.mainloop()
# end of BiblelatorGlobals.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables


    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BiblelatorGlobals.py
