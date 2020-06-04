#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ModalDialog.py
#
# Framework for modal dialogs for the Biblelator program.
#
# Adapted from: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
#
# Copyright (C) 2014-2020 Robert Hunt
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
Framework for modal dialogs for the Biblelator program.
"""
from gettext import gettext as _
from typing import Optional

import tkinter as tk
from tkinter.ttk import Frame, Button

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint

# Biblelator imports
if __name__ == '__main__':
    import sys
    import os
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator import BiblelatorGlobals


LAST_MODIFIED_DATE = '2020-05-03' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorModalDialog"
PROGRAM_NAME = "Biblelator Modal Dialog"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False



class ModalDialog( tk.Toplevel ):
    """
    A Toplevel window that's a modal dialog
        and intended to be subclassed.
    """
    def __init__(self, parentWindow, title:Optional[str]=None, okText:Optional[str]=None, cancelText:Optional[str]=None, geometry=None) -> None:

        tk.Toplevel.__init__( self, parentWindow )
        self.transient( parentWindow )

        self.parentWindow = parentWindow
        if title: self.title( title )

        self.result = None # Used to return an optional result

        if okText is None: okText = _("Ok")
        self.okText = okText
        if cancelText is None: cancelText = _("Cancel")
        self.cancelText = cancelText
        self.makeButtonBox()

        body = Frame( self )
        self.initial_focus = self.makeBody( body ) # Create the widgets in the body
        body.pack( padx=5, pady=5, fill=tk.BOTH, expand=tk.YES )

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol( 'WM_DELETE_WINDOW', self.cancel ) # Ensure that closing the dialog does a cancel

        self.geometry( geometry if geometry else "+{}+{}".format(parentWindow.winfo_rootx()+50, parentWindow.winfo_rooty()+50) )

        BiblelatorGlobals.theApp.setStatus( _("Waiting for user input…") )
        self.initial_focus.focus_set()
        self.wait_window( self )
    # end of ModalDialog.__init__


    # construction hooks
    def makeBody( self, master ) -> None:
        """
        Create dialog body -- this method must be overridden.

        Returns the widget that should have initial focus.
        """
        vPrint( 'Normal', debuggingThisModule, "This 'body' method must be overridden!" ); halt
    # end of ModalDialog.makeBody


    def makeButtonBox( self ) -> None:
        """
        Add our standard button box

        Override if you don't want the standard buttons.
        """
        box = Frame( self )

        self.okButton = Button( box, text=self.okText, width=10, command=self.ok, default=tk.ACTIVE )
        self.okButton.pack( side=tk.LEFT, padx=5, pady=5 )
        self.cancelButton = Button( box, text=self.cancelText, width=10, command=self.cancel )
        self.cancelButton.pack( side=tk.LEFT, padx=5, pady=5 )

        self.bind( '<Return>', self.ok )
        self.bind( '<Escape>', self.cancel )

        box.pack( side=tk.BOTTOM )
    # end of ModalDialog.makeButtonBox


    #
    # standard button semantics
    def ok( self, event=None ) -> None:

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.cancel()
    # end of ModalDialog.ok


    def cancel( self, event=None ) -> None:

        # put focus back to the parent window
        BiblelatorGlobals.theApp.setReadyStatus()
        self.parentWindow.focus_set()
        self.destroy()
    # end of ModalDialog.cancel


    #
    # command hooks
    def validate( self ) -> bool:
        """
        This method is designed to be overridden
            and is called to check the entered data before the window is destroyed.
        """
        dPrint( 'Quiet', debuggingThisModule, "This 'validate' method can be overridden!" )
        return True # override
    # end of ModalDialog.validate


    def apply( self ) -> None:
        """
        This method is designed to be overridden
            and is called to obtain the entered data after the window is destroyed.

        It can optionally put the results into self.result (which otherwise defaults to None).
        """
        dPrint( 'Quiet', debuggingThisModule, "This 'apply' method should be overridden!" )
        self.result = True
    # end of ModalDialog.apply
# end of class ModalDialog



class MyTestDialog( ModalDialog ):

    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        from tkinter.ttk import Label, Entry
        from Biblelator.Windows.TextBoxes import BEntry

        Label( master, text="First:" ).grid( row=0 )
        Label( master, text="Second:" ).grid( row=1 )

        self.e1 = BEntry( master )
        self.e2 = BEntry( master )

        self.e1.grid( row=0, column=1 )
        self.e2.grid( row=1, column=1 )
        return self.e1 # initial focus
    # end of MyTestDialog.apply


    def validate( self ) -> bool:
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.
        """
        try: int( self.e1.get() ) and int( self.e2.get() )
        except ValueError:
            vPrint( 'Quiet', debuggingThisModule, "ERROR: We need two valid integers!" )
            return False
        return True
    # end of MyTestDialog.validate


    def apply( self ) -> None:
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        first = int( self.e1.get() )
        second = int( self.e2.get() )
        vPrint( 'Quiet', debuggingThisModule, first, second ) # or something
        self.result = (first, second,)
    # end of MyTestDialog.apply
# end of class MyTestDialog



def briefDemo() -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.parentApp = tkRootWindow

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    def ss( a ): pass
    tkRootWindow.setStatus = ss
    md = MyTestDialog( tkRootWindow, "Just playing" )
    vPrint( 'Quiet', debuggingThisModule, "Result is:", repr(md.result) )

    # Start the program running
    tkRootWindow.mainloop()
# end of ModalDialog.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.parentApp = tkRootWindow

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    def ss( a ): pass
    tkRootWindow.setStatus = ss
    md = MyTestDialog( tkRootWindow, "Just playing" )
    vPrint( 'Quiet', debuggingThisModule, "Result is:", repr(md.result) )

    # Start the program running
    tkRootWindow.mainloop()
# end of ModalDialog.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of ModalDialog.py
