#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AutocorrectFunctions.py
#
# Functions to support the autocorrect function in text editors
#
# Copyright (C) 2016-2018 Robert Hunt
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
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2018-03-15' # by RJH
SHORT_PROGRAM_NAME = "AutocorrectFunctions"
PROGRAM_NAME = "Biblelator Autocorrect Functions"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint




def setAutocorrectEntries( self, autocorrectEntryList, append=False ):
    """
    Given a word list, set the entries into the autocorrect words
        and then do necessary house-keeping.

    Note that the original word order is preserved (if the autocorrectEntryList has an order)
        so that more common/likely words can appear at the top of the list if desired.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( "AutocorrectFunctions.setAutocorrectEntries( {} )".format( autocorrectEntryList, append ) )
        print( "AutocorrectFunctions.setAutocorrectEntries( {}.., {} )".format( len(autocorrectEntryList), append ) )

    if append: self.autocorrectEntries.extend( autocorrectEntryList )
    else: self.autocorrectEntries = autocorrectEntryList

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

    Note that the original word order is preserved (if the autocorrectEntryList has an order)
        so that more common/likely words can appear at the top of the list if desired.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "AutocorrectFunctions.setDefaultAutocorrectEntries()" )

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
    ourAutocorrectEntries.append( ('...','…') )

    ourAutocorrectEntries.append( ('f1','\\f + \\fr ') )
    ourAutocorrectEntries.append( ('f2',' \\ft ') )
    ourAutocorrectEntries.append( ('fh',' \\ft In Hibruwanon: ') )
    ourAutocorrectEntries.append( ('f3','\\f*') )

    from datetime import datetime # Sorry -- this is a hack for our project
    ourAutocorrectEntries.append( ('QQQ',' [{} {}] XXX' \
                .format( self.parentApp.currentUserInitials, datetime.now().strftime( '%d%b%y' ) ) ) )

    # Add trailing spaces on these ones so that autocomplete doesn't kick in as well
    #ourAutocorrectEntries.append( ('(in','(incl) ') )
    #ourAutocorrectEntries.append( ('(ex','(excl) ') )
    #ourAutocorrectEntries.append( ('tlg','the Lord God ') )

    setAutocorrectEntries( self, ourAutocorrectEntries )
# end of AutocorrectFunctions.setDefaultAutocorrectEntries



def demo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    import tkinter as tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    #uEW = AutocorrectFunctions( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of AutocorrectFunctions.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of AutocorrectFunctions.py
