#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BiblelatorHelpers.py
#   Last modified: 2014-09-29 (also update ProgVersion below)
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

ShortProgName = "Biblelator"
ProgName = "Biblelator helpers"
ProgVersion = "0.12"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys #, os.path, logging
from gettext import gettext as _

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
#from tkinter import Tk, TclError, Menu, Text, StringVar, messagebox
#from tkinter import NORMAL, DISABLED, TOP, BOTTOM, LEFT, RIGHT, BOTH, YES, SUNKEN, X, END
from tkinter.ttk import Combobox, Label
#from tkinter.tix import Spinbox

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
#from BibleOrganizationalSystems import BibleOrganizationalSystem
#import VerseReferences
#import USFMStylesheets
#import SwordResources

# Biblelator imports
#from BiblelatorGlobals import DATA_FOLDER, SETTINGS_FOLDER, MAX_WINDOWS, MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE, GROUP_CODES, editModeNormal, parseGeometry, assembleGeometryFromList
from ModalDialog import ModalDialog



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



class SaveWindowNameDialog( ModalDialog ):
    def __init__(self, parent, existingSettings, title=None):
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parent, title )
    # end of SaveWindowNameDialog.__init__

    def body( self, master ):
        t1 = _("Enter a new name to save windows set-up")
        if self.haveExisting: t1 += ', ' + _("or choose an existing name to overwrite")
        Label( master, text=t1 ).grid( row=0 )

        #cbValues = [_("Enter (optional) new name") if self.haveExisting else _("Enter new set-up name")]
        cbValues = []
        if self.haveExisting:
            for existingName in self.existingSettings:
                if existingName != 'Current':
                    cbValues.append( existingName)
        self.cb = Combobox( master, values=cbValues )
        #self.cb.current( 0 )
        self.cb.grid( row=1 )

        return self.cb # initial focus
    # end of SaveWindowNameDialog.apply


    def validate( self ):
        result = self.cb.get()
        if not result: return False
        if not isinstance( result, str ): return False
        for char in '[]':
            if char in result: return False
        return True
    # end of SaveWindowNameDialog.validate


    def apply( self ):
        self.result = self.cb.get()
        print( t("New window set-up name is: {}").format( repr(self.result) ) )
    # end of SaveWindowNameDialog.apply
# end of class SaveWindowNameDialog



class DeleteWindowNameDialog( ModalDialog ):
    def __init__(self, parent, existingSettings, title=None):
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parent, title, _("Delete") )
    # end of DeleteWindowNameDialog.__init__

    def body( self, master ):
        Label( master, text=_("Use to delete a saved windows set-up") ).grid( row=0 )

        #cbValues = [_("Enter (optional) new name") if self.haveExisting else _("Enter new set-up name")]
        cbValues = []
        if self.haveExisting:
            for existingName in self.existingSettings:
                if existingName != 'Current':
                    cbValues.append( existingName)
        self.cb = Combobox( master, state='readonly', values=cbValues )
        #self.cb.current( 0 )
        self.cb.grid( row=1 )

        return self.cb # initial focus
    # end of DeleteWindowNameDialog.apply


    def validate( self ):
        result = self.cb.get()
        if not result: return False
        if not isinstance( result, str ): return False
        return True
    # end of DeleteWindowNameDialog.validate


    def apply( self ):
        self.result = self.cb.get()
        print( t("Requested window set-up name is: {}").format( repr(self.result) ) )
    # end of SaveWindowNameDialog.apply
# end of class DeleteWindowNameDialog



def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if Globals.debugFlag: print( t("Running demo...") )

    tkRootWindow = Tk()

    swnd = SaveWindowNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test SWND" )
    print( "swndResult", swnd.result )
    dwnd = DeleteWindowNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test DWND" )
    print( "dwndResult", dwnd.result )
    #tkRootWindow.quit()

    # Start the program running
    #tkRootWindow.mainloop()
# end of Biblelator.demo


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
# end of BiblelatorHelpers.py