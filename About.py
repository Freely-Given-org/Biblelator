#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# About.py
#   Last modified: 2014-09-18 (also update ProgVersion below)
#
# Main program for Biblelator Bible display/editing
#
# Copyright (C) 2014 Robert Hunt
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

ProgName = "About"
ProgVersion = "0.10"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, os.path, configparser, logging
from gettext import gettext as _
import multiprocessing

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import tix
#from tkinter.ttk import * # Overrides any of the above widgets

sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
from BibleOrganizationalSystems import BibleOrganizationalSystem
import Hebrew
from HebrewLexicon import HebrewLexicon
from HebrewWLC import HebrewWLC
import Greek
from GreekNT import GreekNT
import VerseReferences
import USFMBible, USFMStylesheets
import SwordResources, DigitalBiblePlatform

from ApplicationSettings import ApplicationSettings


class AboutBox( tk.Toplevel ):
    def __init__( self, parent=None, progName=None, text=None ):
        if Globals.debugFlag: print( "ApplicationWindow.__init__( {} )".format( parent ) )
        tk.Toplevel.__init__( self, parent )
        #self.minimumXSize, self.minimumYSize = MINIMUM_X_SIZE, MINIMUM_Y_SIZE
        self.title( 'About '+progName )
        self.textBox = tk.Text( self ) #, state=tk.DISABLED )
        self.textBox['wrap'] = 'word'
        self.textBox.pack( expand=tk.YES )
        self.textBox.insert( 'end', text )

        self.okButton = tk.Button( self, text='Ok', command=self.destroy )
        self.okButton.pack()

        self.focus_set() # take over input focus,
        self.grab_set() # disable other windows while I'm open,
        self.wait_window() # and wait here until win destroyed
    # end of AboutBox.__init__
# end of class AboutBox


class AboutBox2():
    def __init__( self, parent=None, progName=None, text=None ):
        if Globals.debugFlag: print( "ApplicationWindow.__init__( {} )".format( parent ) )
        ab = tk.Toplevel( parent )
        #self.minimumXSize, self.minimumYSize = MINIMUM_X_SIZE, MINIMUM_Y_SIZE
        ab.title( 'About '+progName )
        textBox = tk.Text( ab ) #, state=tk.DISABLED )
        textBox['wrap'] = 'word'
        textBox.pack( expand=tk.YES )
        textBox.insert( 'end', text )

        okButton = tk.Button( ab, text='Ok', command=ab.destroy )
        okButton.pack()

        ab.focus_set() # take over input focus,
        ab.grab_set() # disable other windows while I'm open,
        ab.wait_window() # and wait here until win destroyed
    # end of AboutBox.__init__
# end of class AboutBox


def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    print( "Running demo..." )
    #Globals.debugFlag = True

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )
    ab = AboutBox( tkRootWindow, ProgName, ProgNameVersion )
    ab = AboutBox2( tkRootWindow, ProgName, ProgNameVersion )
    # Calls to the window manager class (wm in Tk)
    #tkRootWindow.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of main


if __name__ == '__main__':
    # Configure basic set-up
    parser = Globals.setup( ProgName, ProgVersion )
    Globals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if Globals.debugFlag:
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        #print( "tix TclVersion is", tix.TclVersion )
        #print( "tix TkVersion is", tix.TkVersion )

    demo()

    Globals.closedown( ProgName, ProgVersion )
# end of About.py