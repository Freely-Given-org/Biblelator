#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BiblelatorHelpers.py
#
# Various non-GUI helper functions for Biblelator Bible display/editing
#
# Copyright (C) 2014-2015 Robert Hunt
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

from gettext import gettext as _

LastModifiedDate = '2015-01-10' # by RJH
ShortProgName = "Biblelator"
ProgName = "Biblelator helpers"
ProgVersion = '0.28'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import sys

# Biblelator imports
from BiblelatorGlobals import APP_NAME, BIBLE_GROUP_CODES

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import BibleOrgSysGlobals
from VerseReferences import SimpleVerseKey



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



def mapReferenceVerseKey( mainVerseKey ):
    """
    Returns the verse key for OT references in the NT (and vv), etc.

    Returns None if we don't have a mapping.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( t("mapReferenceVerseKey( {} )").format( mainVerseKey.getShortText() ) )
    referenceVerseKeyDict = {
        SimpleVerseKey('MAT','2','18'): SimpleVerseKey('JER','31','15'),
        SimpleVerseKey('MAT','3','3'): SimpleVerseKey('ISA','40','3'),
        }
    if mainVerseKey in referenceVerseKeyDict:
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( '  returning {}'.format( referenceVerseKeyDict[mainVerseKey].getShortText() ) )
        return referenceVerseKeyDict[mainVerseKey]
# end of BiblelatorHelpers.mapReferenceVerseKey


def mapParallelVerseKey( forGroupCode, mainVerseKey ):
    """
    Returns the verse key for synoptic references in the NT, etc.

    Returns None if we don't have a mapping.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( t("mapParallelVerseKey( {}, {} )").format( forGroupCode, mainVerseKey.getShortText() ) )
    groupIndex = BIBLE_GROUP_CODES.index( forGroupCode ) - 1
    parallelVerseKeyDict = {
        SimpleVerseKey('MAT','3','13'): (SimpleVerseKey('MRK','1','9'), SimpleVerseKey('LUK','3','21'), SimpleVerseKey('JHN','1','31') )
        }
    if mainVerseKey in parallelVerseKeyDict:
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( '  returning {}'.format( parallelVerseKeyDict[mainVerseKey][groupIndex].getShortText() ) )
        return parallelVerseKeyDict[mainVerseKey][groupIndex]
# end of BiblelatorHelpers.mapParallelVerseKey



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
    #srb = SelectResourceBox( tkRootWindow, [(x,y) for x,y, in {"ESV":"ENGESV","WEB":"ENGWEB","MS":"MBTWBT"}.items()], "Test SRB" )
    #print( "srbResult", srb.result )

    #tkRootWindow.quit()

    # Start the program running
    #tkRootWindow.mainloop()
# end of BiblelatorHelpers.demo


if __name__ == '__main__':
    from BibleOrgSysGlobals import setup, addStandardOptionsAndProcess, closedown
    import multiprocessing

    # Configure basic set-up
    parser = setup( ProgName, ProgVersion )
    addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    closedown( ProgName, ProgVersion )
# end of BiblelatorHelpers.py