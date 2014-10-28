#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BiblelatorHelpers.py
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

ShortProgName = "Biblelator"
ProgName = "Biblelator helpers"
ProgVersion = "0.19"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys #, os.path, logging
from gettext import gettext as _

import tkinter as tk
from tkinter.ttk import Label, Combobox

# Biblelator imports
from ModalDialog import ModalDialog

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



def errorBeep():
    """
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("errorBeep()") )
    #import sys
    #from subprocess import call
    #if sys.platform == 'linux': call(["xdg-open","dialog-error.ogg"])
    #elif sys.platform == 'darwin': call(["afplay","dialog-error.ogg"])
    #else: print( "errorBeep: sp", sys.platform )
# end of errorBeep



class SaveWindowNameDialog( ModalDialog ):
    """
    """
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
    """
    """
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
    # end of DeleteWindowNameDialog.apply
# end of class DeleteWindowNameDialog



class SelectResourceBox( ModalDialog ):
    """
    Given a list of available resources, select one and return the list item.
    """
    def __init__(self, parent, availableSettingsList, title=None):
        print( "aS", repr(availableSettingsList) ) # Should be a list of tuples
        if BibleOrgSysGlobals.debugFlag: assert( isinstance( availableSettingsList, list ) )
        self.availableSettingsList = availableSettingsList
        ModalDialog.__init__( self, parent, title )
    # end of SelectResourceBox.__init__

    def body( self, master ):
        Label( master, text=_("Select a resource to open") ).grid( row=0 )

        self.lb = tk.Listbox( master, selectmode=tk.EXTENDED )
        """ Note: selectmode can be
            SINGLE (just a single choice),
            BROWSE (same, but the selection can be moved using the mouse),
            MULTIPLE (multiple item can be choosen, by clicking at them one at a time), or
            tk.EXTENDED (multiple ranges of items can be chosen using the Shift and Control keyboard modifiers).
            The default is BROWSE.
            Use MULTIPLE to get “checklist” behavior,
            and tk.EXTENDED when the user would usually pick only one item,
                but sometimes would like to select one or more ranges of items. """
        for item in self.availableSettingsList:
            #print( "it", repr(item) )
            if isinstance( item, tuple ): item = item[0]
            self.lb.insert( tk.END, item )
        self.lb.grid( row=1 )

        return self.lb # initial focus
    # end of SelectResourceBox.apply


    def validate( self ):
        """
        Must be at least one selected (otherwise force them to select CANCEL).
        """
        return self.lb.curselection()
    # end of SelectResourceBox.validate


    def apply( self ):
        items = self.lb.curselection()
        print( "items", repr(items) ) # a tuple
        self.result = [self.availableSettingsList[int(item)] for item in items] # now a sublist
        print( t("Requested resource(s) is/are: {}").format( repr(self.result) ) )
    # end of SelectResourceBox.apply
# end of class SelectResourceBox



def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( t("Running demo...") )

    tkRootWindow = Tk()
    tkRootWindow.title( ProgNameVersion )

    #swnd = SaveWindowNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test SWND" )
    #print( "swndResult", swnd.result )
    #dwnd = DeleteWindowNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test DWND" )
    #print( "dwndResult", dwnd.result )
    srb = SelectResourceBox( tkRootWindow, [(x,y) for x,y, in {"ESV":"ENGESV","WEB":"ENGWEB","MS":"MBTWBT"}.items()], "Test SRB" )
    print( "srbResult", srb.result )

    #tkRootWindow.quit()

    # Start the program running
    #tkRootWindow.mainloop()
# end of Biblelator.demo


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
# end of BiblelatorHelpers.py