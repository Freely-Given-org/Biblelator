#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# About.py
#
# About box for Biblelator Bible display/editing
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
A simple About box window containing text and an optional logo.
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2020-01-05' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorAbout"
PROGRAM_NAME = "BiblelatorAbout Box"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button

from Biblelator.BiblelatorGlobals import MINIMUM_ABOUT_SIZE, MAXIMUM_ABOUT_SIZE, \
                                parseWindowSize, centreWindowOnWindow

from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint




class AboutBox( tk.Toplevel ):
    """
    """
    def __init__( self, parent=None, progName=None, text=None, logoPath=None ) -> None:
        """
        """
        #if BibleOrgSysGlobals.debugFlag: print( "AboutBox.__init__( {} )".format( parent ) )
        tk.Toplevel.__init__( self, parent )
        self.minimumSize = MINIMUM_ABOUT_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maximumSize = MAXIMUM_ABOUT_SIZE
        self.maxsize( *parseWindowSize( self.maximumSize ) )
        if parent: centreWindowOnWindow( self, parent )

        self.title( _("About") + ' '+progName )

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
        self.textBox.pack( side=tk.TOP, expand=tk.YES )

        self.focus_set() # take over input focus,
        self.grab_set() # disable other windows while I'm open,
        self.wait_window() # and wait here until win destroyed
    # end of AboutBox.__init__
# end of class AboutBox



#class AboutBox2():
    #"""
    #"""
    #def __init__( self, parent=None, progName=None, text=None, logoPath=None ):
        #"""
        #"""
        ##if BibleOrgSysGlobals.debugFlag: print( "AboutBox2.__init__( {} )".format( parent ) )
        #ab = tk.Toplevel( parent )
        #self.minimumXSize, self.minimumYSize = MINIMUM_ABOUT_X_SIZE, MINIMUM_ABOUT_Y_SIZE
        #ab.minsize( self.minimumXSize, self.minimumYSize )
        #if parent: centreWindowOnWindow( ab, parent )

        #if logoPath:
            #self.logo = tk.PhotoImage( file=logoPath )
            #self.label = tk.Label( ab, image=self.logo )
            #self.label.pack( side=tk.TOP )

        #self.okButton = Button( ab, text=_("Ok"), command=ab.destroy )
        #self.okButton.pack( side=tk.BOTTOM )

        #ab.title( 'About '+progName )

        #textBox = ScrolledText( ab ) #, state=tk.DISABLED )
        #textBox.configure( wrap='word' )
        #textBox.pack( expand=tk.YES )
        #textBox.insert( tk.END, text )
        #textBox.configure( state=tk.DISABLED ) # Don't allow editing

        #okButton = Button( ab, text=_("Ok"), command=ab.destroy )
        #okButton.pack()

        #ab.focus_set() # take over input focus,
        #ab.grab_set() # disable other windows while I'm open,
        #ab.wait_window() # and wait here until win destroyed
    ## end of AboutBox2.__init__
## end of class AboutBox2



def demo() -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    print( "Running demo…" )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        #print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
        for name in ('appname', 'inactive', 'scaling', 'useinputmethods', 'windowingsystem' ): # 'busy', 'caret', 'fontchooser',
            print( 'Tkinter {} is {}'.format( name, repr( tkRootWindow.tk.call('tk', name) ) ) )
    tkRootWindow.title( programNameVersion )
    ab = AboutBox( tkRootWindow, PROGRAM_NAME, programNameVersion )
    #ab = AboutBox2( tkRootWindow, PROGRAM_NAME, programNameVersion )
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
# end of About.py
