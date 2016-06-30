#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AutocorrectFunctions.py
#
# Functions to support the autocorrect function in text editors
#
# Copyright (C) 2016 Robert Hunt
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
"""

from gettext import gettext as _

LastModifiedDate = '2016-06-30' # by RJH
ShortProgName = "AutocorrectFunctions"
ProgName = "Biblelator Autocorrect Functions"
ProgVersion = '0.37'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


# BibleOrgSys imports
if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
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
    return '{}{}'.format( nameBit+': ' if nameBit else '', errorBit )
# end of exp



def setAutocorrectEntries( self, entryList, append=False ):
    """
    Given a word list, set the entries into the autocorrect words
        and then do necessary house-keeping.

    Note that the original word order is preserved (if the entryList has an order)
        so that more common/likely words can appear at the top of the list if desired.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( exp("AutocorrectFunctions.setAutocorrectEntries( {} )").format( entryList, append ) )
        print( exp("AutocorrectFunctions.setAutocorrectEntries( {}.., {} )").format( len(entryList), append ) )

    if append: self.autocorrectEntries.extend( entryList )
    else: self.autocorrectEntries = entryList

    # This next bit needs to be done whenever the autocorrect entries are changed
    self.maxAutocorrectLength = 0
    for inChars,outChars in self.autocorrectEntries:
        self.maxAutocorrectLength = max( len(inChars), self.maxAutocorrectLength )

    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "  autocorrect total entries loaded = {:,}".format( len(self.autocorrectEntries) ) )
# end of AutocorrectFunctions.setAutocorrectEntries


def setDefaultAutocorrectEntries( self ):
    """
    Given a word list, set the entries into the autocorrect words
        and then do necessary house-keeping.

    Note that the original word order is preserved (if the entryList has an order)
        so that more common/likely words can appear at the top of the list if desired.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("AutocorrectFunctions.setDefaultAutocorrectEntries()") )

    ourAutocorrectEntries = []

    ourAutocorrectEntries.append( ('<<','“') ) # Cycle through quotes with angle brackets
    ourAutocorrectEntries.append( ('“<','‘') )
    ourAutocorrectEntries.append( ('‘<',"'") )
    ourAutocorrectEntries.append( ("'<",'<') )
    ourAutocorrectEntries.append( ('>>','”') )
    ourAutocorrectEntries.append( ('”>','’') )
    ourAutocorrectEntries.append( ('’>',"'") )
    ourAutocorrectEntries.append( ("'>",'>') )
    ourAutocorrectEntries.append( ('--','–') ) # Cycle through en-dash/em-dash with hyphens
    ourAutocorrectEntries.append( ('–-','—') )
    ourAutocorrectEntries.append( ('—-','-') )

    ourAutocorrectEntries.append( ('f1','\\f + \\fr ') )
    ourAutocorrectEntries.append( ('f2',' \\ft ') )
    ourAutocorrectEntries.append( ('fh',' \\ft In Hibruwanon: ') )
    ourAutocorrectEntries.append( ('f3','\\f*') )

    ourAutocorrectEntries.append( ('SD',' [RJH 01Jul16] XXX') ) # Sorry -- this is a hack

    # Add trailing spaces on these ones so that autocomplete doesn't kick in as well
    #ourAutocorrectEntries.append( ('(in','(incl) ') )
    #ourAutocorrectEntries.append( ('(ex','(excl) ') )
    #ourAutocorrectEntries.append( ('tlg','the Lord God ') )

    setAutocorrectEntries( self, ourAutocorrectEntries )
# end of AutocorrectFunctions.setDefaultAutocorrectEntries



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    import tkinter as tk

    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo…") )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    #uEW = AutocorrectFunctions( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of AutocorrectFunctions.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables


    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )


    #if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        ##from tkinter import TclVersion, TkVersion
        #from tkinter import tix
        #print( "TclVersion is", tk.TclVersion )
        #print( "TkVersion is", tk.TkVersion )
        #print( "tix TclVersion is", tix.TclVersion )
        #print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of AutocorrectFunctions.py