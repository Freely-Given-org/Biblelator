#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BiblelatorHelpers.py
#   Last modified: 2014-11-04 (also update ProgVersion below)
#
# Various help functions for Biblelator Bible display/editing
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

ShortProgName = "Biblelator"
ProgName = "Biblelator helpers"
ProgVersion = "0.22"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys #, logging
from gettext import gettext as _

#import tkinter as tk
#import tkinter.messagebox as tkmb
#from tkinter.ttk import Label, Combobox, Entry

# Biblelator imports
from BiblelatorGlobals import APP_NAME
#from ModalDialog import ModalDialog

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



def createEmptyUSFMBook( BBB, getNumChapters, getNumVerses ):
    """
    Returns a string that is the text of a blank USFM book.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( t("createEmptyUSFMBook( {} )").format( BBB ) )
    USFMAbbreviation = BibleOrgSysGlobals.BibleBooksCodes.getUSFMAbbreviation( BBB )
    USFMNumber = BibleOrgSysGlobals.BibleBooksCodes.getUSFMNumber( BBB )
    bookText = '\\id {} Empty book created by {}\n'.format( USFMAbbreviation.upper(), APP_NAME )
    bookText += '\\ide UTF-8\n'
    bookText += '\\h Bookname\n'
    bookText += '\\mt Book Title\n'
    for C in range( 1, getNumChapters(BBB)+1 ):
        bookText += '\\c {}\n'.format( C )
        for V in range( 1, getNumVerses(BBB,C) ):
            bookText += '\\v {} \n'.format( V )
    return bookText
# end of BiblelatorHelpers.createEmptyUSFMBook


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
# end of BiblelatorHelpers.demo


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