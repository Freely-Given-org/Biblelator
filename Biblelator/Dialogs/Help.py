#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Help.py
#
# Help box for Biblelator Bible display/editing
#
# Copyright (C) 2014-2018 Robert Hunt
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
A simple Help box window containing text and an optional logo.
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2018-03-15' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorHelp"
PROGRAM_NAME = "Biblelator Help Box"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button

from Biblelator.BiblelatorGlobals import MINIMUM_HELP_SIZE, MAXIMUM_HELP_SIZE, MINIMUM_HELP_X_SIZE, MINIMUM_HELP_Y_SIZE, \
                            parseWindowSize, centreWindowOnWindow

from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint




class HelpBox( tk.Toplevel ):
    """
    """
    def __init__( self, parent=None, progName=None, text=None, logoPath=None ):
        """
        """
        #if BibleOrgSysGlobals.debugFlag: print( "HelpBox.__init__( {} )".format( parent ) )
        tk.Toplevel.__init__( self, parent )
        self.minimumSize = MINIMUM_HELP_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maximumSize = MAXIMUM_HELP_SIZE
        self.maxsize( *parseWindowSize( self.maximumSize ) )
        if parent: centreWindowOnWindow( self, parent )

        self.title( 'Help for '+progName )

        buttonFrame = Frame( self ) #, cursor='hand2', relief=tk.RAISED, style='MainButtons.TFrame' )
        if logoPath:
            self.logo = tk.PhotoImage( file=logoPath )
            self.label = tk.Label( buttonFrame, image=self.logo )
            self.label.pack( side=tk.LEFT )
        Button( buttonFrame, text=_("Ok"), command=self.destroy ).pack( side=tk.RIGHT )
        buttonFrame.pack( side=tk.BOTTOM, fill=tk.X )

        self.textBox = ScrolledText( self, height=12 ) #, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.insert( tk.END, text )
        self.textBox.configure( state=tk.DISABLED ) # Don't allow editing
        self.textBox.pack( expand=tk.YES )

        self.focus_set() # take over input focus,
        self.grab_set() # disable other windows while I'm open,
        self.wait_window() # and wait here until win destroyed
    # end of HelpBox.__init__
# end of class HelpBox



#class HelpBox2():
    #"""
    #"""
    #def __init__( self, parent=None, progName=None, text=None, logoPath=None ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag: print( "HelpBox2.__init__( {} )".format( parent ) )
        #hb = tk.Toplevel( parent )
        #self.minimumXSize, self.minimumYSize = MINIMUM_HELP_X_SIZE, MINIMUM_HELP_Y_SIZE
        #hb.minsize( self.minimumXSize, self.minimumYSize )
        #if parent: centreWindowOnWindow( hb, parent )

        #hb.title( 'Help for '+progName )

        #textBox = ScrolledText( hb, height=12 ) #, state=tk.DISABLED )
        #textBox.configure( wrap='word' )
        #textBox.pack( expand=tk.YES )
        #textBox.insert( tk.END, text )
        #textBox.configure( state=tk.DISABLED ) # Don't allow editing

        #if logoPath:
            #self.logo = tk.PhotoImage( file=logoPath )
            #self.label = tk.Label( hb, image=self.logo )
            #self.label.pack( side=tk.LEFT )

        #self.okButton = Button( hb, text=_("Ok"), command=hb.destroy )
        #self.okButton.pack( side=tk.RIGHT )

        #hb.focus_set() # take over input focus,
        #hb.grab_set() # disable other windows while I'm open,
        #hb.wait_window() # and wait here until win destroyed
    ## end of HelpBox.__init__
## end of class HelpBox2



def demo() -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    print( "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    ab = HelpBox( tkRootWindow, PROGRAM_NAME, programNameVersion, 'BiblelatorLogoSmall.gif' )
    #ab = HelpBox2( tkRootWindow, PROGRAM_NAME, programNameVersion, 'BiblelatorLogoSmall.gif' )
    # Calls to the window manager class (wm in Tk)
    #tkRootWindow.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of main


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of Help.py
