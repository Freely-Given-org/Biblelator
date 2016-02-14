#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# AutocompleteFunctions.py
#
# Functions to support the autocomplete function in text editors
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

LastModifiedDate = '2016-02-15' # by RJH
ShortProgName = "AutocompleteFunctions"
ProgName = "Biblelator Autocomplete Functions"
ProgVersion = '0.30'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True

import sys #, os.path, logging #, re
#from collections import OrderedDict
#import multiprocessing

#import tkinter as tk
#from tkinter.simpledialog import askstring, askinteger
#from tkinter.filedialog import asksaveasfilename
#from tkinter.colorchooser import askcolor
#from tkinter.ttk import Style, Frame

# Biblelator imports
#from BiblelatorGlobals import DEFAULT
    ##APP_NAME, DATA_FOLDER_NAME, START, DEFAULT, EDIT_MODE_NORMAL, EDIT_MODE_USFM, BIBLE_GROUP_CODES
##from BiblelatorDialogs import showerror, showinfo, YesNoDialog, OkCancelDialog, GetBibleBookRangeDialog
#from BiblelatorHelpers import createEmptyUSFMBookText, calculateTotalVersesForBook, mapReferenceVerseKey, mapParallelVerseKey
#from TextBoxes import CustomText
##from ChildWindows import ChildWindow, HTMLWindow
#from BibleResourceWindows import BibleBox, BibleResourceWindow
##from BibleReferenceCollection import BibleReferenceCollectionWindow
#from TextEditWindow import TextEditWindow, REFRESH_TITLE_TIME, CHECK_DISK_CHANGES_TIME

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
#from VerseReferences import SimpleVerseKey
#from BibleWriter import setDefaultControlFolder



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
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit+': ' if nameBit else '', _(errorBit) )
# end of exp



def loadBibleAutocompleteWords( self ):
    """
    Load all the existing words in a USFM or Paratext Bible Project
        to fill the autocomplete mechanism.

    This is rather slow because of course, the entire Bible has to be read and processed first.

    self here is a USFM or ESFM edit window.

    NOTE: This list should theoretically be updated as the user enters new words!
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("AutocompleteFunctions.loadBibleAutocompleteWords()") )

    self.internalBible.loadBooks()
    self.internalBible.discover()
    #print( 'discoveryResults', self.internalBible.discoveryResults )

    # Would be nice to load current book first, but we don't know it yet
    autocompleteWords = []
    for BBB in self.internalBible.discoveryResults:
        if BBB != 'All':
            try:
                # Sort the word-list for the book to put the most common words first
                #print( 'discoveryResults', BBB, self.internalBible.discoveryResults[BBB] )
                #print( BBB, 'mTWC', self.internalBible.discoveryResults[BBB]['mainTextWordCounts'] )
                #qqq = sorted( self.internalBible.discoveryResults[BBB]['mainTextWordCounts'].items(), key=lambda c: -c[1] )
                #print( 'qqq', qqq )
                for word,count in sorted( self.internalBible.discoveryResults[BBB]['mainTextWordCounts'].items(),
                                        key=lambda duple: -duple[1] ):
                    if len(word) >= self.autocompleteMinLength \
                    and word not in autocompleteWords: # just in case we had some (common) words in there already
                        autocompleteWords.append( word )
            except KeyError: pass # Nothing for this book
    #print( 'acW', autocompleteWords )
    self.setAutocompleteWords( autocompleteWords )
    self.autocompleteType = 'Bible'
# end of AutocompleteFunctions.loadBibleAutocompleteWords



def loadBibleBookAutocompleteWords( self ):
    """
    Load all the existing words in a USFM or Paratext Bible book
        to fill the autocomplete mechanism

    self here is a USFM or ESFM edit window.

    NOTE: This list should theoretically be updated as the user enters new words!
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("AutocompleteFunctions.loadBibleBookAutocompleteWords()") )

    BBB = self.currentVerseKey.getBBB()
    self.internalBible.loadBookIfNecessary( self.currentVerseKey.getBBB() )
    self.internalBible.books[BBB]._discover( self.discoveryResults )
    #print( 'discoveryResults', self.internalBible.discoveryResults )

    # Would be nice to load current book first, but we don't know it yet
    autocompleteWords = []
    try:
        # Sort the word-list for the book to put the most common words first
        #print( 'discoveryResults', BBB, self.internalBible.discoveryResults[BBB] )
        #print( BBB, 'mTWC', self.internalBible.discoveryResults[BBB]['mainTextWordCounts'] )
        #qqq = sorted( self.internalBible.discoveryResults[BBB]['mainTextWordCounts'].items(), key=lambda c: -c[1] )
        #print( 'qqq', qqq )
        for word,count in sorted( self.internalBible.discoveryResults[BBB]['mainTextWordCounts'].items(),
                                key=lambda duple: -duple[1] ):
            if len(word) >= self.autocompleteMinLength \
            and word not in autocompleteWords: # just in case we had some (common) words in there already
                autocompleteWords.append( word )
    except KeyError:
        print( "Why did {} have no words???".format( BBB ) )
        pass # Nothing for this book
    #print( 'acW', autocompleteWords )
    self.setAutocompleteWords( autocompleteWords )
    self.autocompleteType = 'BibleBook'
# end of AutocompleteFunctions.loadBibleBookAutocompleteWords



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo...") )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    tEW = TextEditWindow( tkRootWindow )
    uEW = AutocompleteFunctions( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of AutocompleteFunctions.demo


if __name__ == '__main__':
    from BibleOrgSysGlobals import setup, addStandardOptionsAndProcess, closedown
    import multiprocessing

    # Configure basic set-up
    parser = setup( ProgName, ProgVersion )
    addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", tk.TclVersion )
        print( "TkVersion is", tk.TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    closedown( ProgName, ProgVersion )
# end of AutocompleteFunctions.py