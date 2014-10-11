#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleResourceWindows.py
#   Last modified: 2014-10-11 (also update ProgVersion below)
#
# Bible resource frames for Biblelator Bible display/editing
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
Windows and frames to allow display and manipulation of
    (non-editable) Bible resource windows.
"""

ShortProgName = "BibleResourceWindows"
ProgName = "Biblelator Bible Resource Windows"
ProgVersion = "0.16"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, logging #, os.path, configparser, logging
from gettext import gettext as _
from collections import OrderedDict

from tkinter import DISABLED, BOTH, YES, END

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
from VerseReferences import SimpleVerseKey
#from BibleOrganizationalSystems import BibleOrganizationalSystem
from SwordResources import SwordType
from DigitalBiblePlatform import DBPBible
from UnknownBible import UnknownBible

# Biblelator imports
from BiblelatorGlobals import GROUP_CODES
from ResourceWindows import ResourceWindow


MAX_CACHED_VERSES = 300 # Per Bible resource window



def t( messageString ):
    """
    Prepends the module name to a error or warning message string
        if we are in debug mode.
    Returns the new string.
    """
    try: nameBit, errorBit = messageString.split( ': ', 1 )
    except ValueError: nameBit, errorBit = '', messageString
    if Globals.debugFlag or debuggingThisModule:
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit, _(errorBit) )
# end of BibleResourceWindows.t



class BibleResourceWindow( ResourceWindow ):
    def __init__( self, parentApp, moduleID ):
        if Globals.debugFlag: print( t("BibleResourceWindow.__init__( {}, {} )").format( parentApp, moduleID ) )
        self.parentApp, self.moduleID = parentApp, moduleID
        ResourceWindow.__init__( self, self.parentApp, 'BibleResource' )
        #self.pack()

        if self.contextViewMode=='Default':
            self.contextViewMode = 'BeforeAndAfter'
            self.parentApp.viewVersesBefore, self.parentApp.viewVersesAfter = 2, 6
        self.groupCode = GROUP_CODES[0] # Put into first/default BCV group

        if 1:
            for USFMKey, styleDict in self.parentApp.stylesheet.getTKStyles().items():
                self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        else:
            self.textBox.tag_configure( 'verseNumberFormat', foreground='blue', font='helvetica 8', relief='raised', offset='3' )
            self.textBox.tag_configure( 'versePreSpaceFormat', background='pink', font='helvetica 8' )
            self.textBox.tag_configure( 'versePostSpaceFormat', background='pink', font='helvetica 4' )
            self.textBox.tag_configure( 'verseTextFormat', font='sil-doulos 12' )
            self.textBox.tag_configure( 'otherVerseTextFormat', font='sil-doulos 9' )
        #self.textBox.tag_configure( 'verseText', background='yellow', font='helvetica 14 bold', relief='raised' )
        #"background", "bgstipple", "borderwidth", "elide", "fgstipple", "font", "foreground", "justify", "lmargin1",
        #"lmargin2", "offset", "overstrike", "relief", "rmargin", "spacing1", "spacing2", "spacing3",
        #"tabs", "tabstyle", "underline", and "wrap".

        # Define which functions we use by default
        self.getNumVerses = self.parentApp.genericBibleOrganisationalSystem.getNumVerses
        self.getNumChapters = self.parentApp.genericBibleOrganisationalSystem.getNumChapters

        self.cache = OrderedDict()
    # end of BibleResourceWindow.__init__


    def getSwordVerseKey( self, verseKey ):
            if Globals.debugFlag and debuggingThisModule: print( t("getSwordVerseKey( {} )").format( verseKey ) )
            BBB, C, V = verseKey.getBCV()
            return self.parentApp.SwordInterface.makeKey( BBB, C, V )
    # end of BibleResourceWindow.getSwordVerseKey


    def getVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.

        MUST BE OVERRIDDEN.
        """
        if Globals.debugFlag: print( t("This 'body' method must be overridden!") ); halt
    # end of BibleResourceWindow.getVerseData


    def getCachedVerseData( self, verseKey ):
        """
        Checks to see if the requested verse is in our cache,
            otherwise calls getVerseData to fetch it.

        The cache keeps the newest or most recently used entries at the end.
        When it gets too large, it drops the first entry.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("getCachedVerseData( {} )").format( verseKey ) )
        if str(verseKey) in self.cache:
            #if Globals.debugFlag and debuggingThisModule: print( "  " + t("Retrieved from BibleResourceWindow cache") )
            self.cache.move_to_end( str(verseKey) )
            return self.cache[str(verseKey)]
        verseData = self.getVerseData( verseKey )
        self.cache[str(verseKey)] = verseData
        if len(self.cache) > MAX_CACHED_VERSES:
            #print( "Removing oldest cached entry", len(self.cache) )
            self.cache.popitem( last=False )
        return verseData
    # end of BibleResourceWindow.getCachedVerseData


    def displayAppendVerse( self, firstFlag, verseKey, verseDataList, currentVerse=False ):
        """
        Add the requested verse to the end of self.textBox.
        """
        if Globals.debugFlag and debuggingThisModule:
            print( t("BibleResourceWindow.displayAppendVerse"), firstFlag, verseKey, verseDataList, currentVerse )
        lastCharWasSpace = haveTextFlag = not firstFlag
        if verseDataList is None:
            print( "  ", verseKey, "has no data for", self.moduleID )
            #self.textBox.insert( END, '--' )
        else:
            for entry in verseDataList:
                if isinstance( entry, tuple ):
                    marker, cleanText = entry[0], entry[3]
                else: marker, cleanText = entry.getMarker(), entry.getCleanText()
                #print( "  ", haveTextFlag, marker, repr(cleanText) )
                if marker and marker[0]=='¬': pass # Ignore end markers for now
                elif marker in ('chapters',): pass # Ignore added markers for now
                elif marker == 'id':
                    self.textBox.insert( END, ('\n\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker in ('ide','rem',):
                    self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker == 'c': # Don't want to display this (original) c marker
                    #if not firstFlag: haveC = cleanText
                    #else: print( "   Ignore C={}".format( cleanText ) )
                    pass
                elif marker == 'c#': # Might want to display this (added) c marker
                    if cleanText != verseKey.getBBB():
                        if not lastCharWasSpace: self.textBox.insert( END, ' ', 'v-' )
                        self.textBox.insert( END, cleanText, 'c#' )
                        lastCharWasSpace = False
                elif marker in ('mt1','mt2','mt3','mt4', 'iot','io1','io2','io3','io4',):
                    self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker in ('s1','s2','s3','s4',):
                    self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker == 'r':
                    self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker in ('p','ip',):
                    self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                    lastCharWasSpace = True
                    if cleanText:
                        self.textBox.insert( END, cleanText, '*v~' if currentVerse else 'v~' )
                        lastCharWasSpace = False
                    haveTextFlag = True
                elif marker == 'p#' and self.winType=='DBPBibleResourceWindow':
                    pass # Just ignore these for now
                elif marker in ('q1','q2','q3','q4',):
                    self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                    lastCharWasSpace = True
                    if cleanText:
                        self.textBox.insert( END, cleanText, '*'+marker if currentVerse else marker )
                        lastCharWasSpace = False
                    haveTextFlag = True
                elif marker == 'm': pass
                elif marker == 'v':
                    if haveTextFlag:
                        self.textBox.insert( END, ' ', 'v-' )
                    self.textBox.insert( END, cleanText, marker )
                    self.textBox.insert( END, ' ', 'v+' )
                    lastCharWasSpace = haveTextFlag = True
                elif marker in ('v~','p~'):
                    self.textBox.insert( END, cleanText, '*v~' if currentVerse else marker )
                    haveTextFlag = True
                else:
                    logging.critical( t("BibleResourceWindow.displayAppendVerse: Unknown marker {} {} from {}").format( marker, cleanText, verseDataList ) )
    # end of BibleResourceWindow.displayAppendVerse


    def getBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if Globals.debugFlag: print( t("BibleResourceWindow.getBeforeAndAfterBibleData( {} )").format( newVerseKey ) )

        BBB, C, V = newVerseKey.getBCV()
        intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        prevBBB, prevIntC, prevIntV = BBB, intC, intV
        previousVersesData = []
        for n in range( -self.parentApp.viewVersesBefore, 0 ):
            failed = False
            print( "  getBeforeAndAfterBibleData here with", n, prevIntC, prevIntV )
            if prevIntV > 0: prevIntV -= 1
            elif prevIntC > 0:
                prevIntC -= 1
                try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                except KeyError:
                    if prevIntC != 0: # we can expect an error for chapter zero
                        logging.critical( t("getBeforeAndAfterBibleData failed at"), prevBBB, prevIntC )
                    failed = True
                if not failed:
                    print( " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            else:
                prevBBB = self.parentApp.genericBibleOrganisationalSystem.getPreviousBookCode( BBB )
                prevIntC = self.getNumChapters( prevBBB )
                prevIntV = self.getNumVerses( prevBBB, prevIntC )
                print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
            if not failed:
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getCachedVerseData( previousVerseKey )
                if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        # Determine the next valid verse numbers
        nextBBB, nextIntC, nextIntV = BBB, intC, intV
        nextVersesData = []
        for n in range( 0, self.parentApp.viewVersesAfter ):
            try: numVerses = self.getNumVerses( nextBBB, nextIntC )
            except KeyError: numVerses = 0
            nextIntV += 1
            if nextIntV > numVerses:
                nextIntV = 1
                nextIntC += 1 # Need to check................................
            nextVerseKey = SimpleVerseKey( nextBBB, nextIntC, nextIntV )
            nextVerseData = self.getCachedVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        verseData = self.getCachedVerseData( newVerseKey )

        return verseData, previousVersesData, nextVersesData
    # end of BibleResourceWindow.getBeforeAndAfterBibleData


    def updateShownBCV( self, newVerseKey ):
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        Leaves the textbox in the disabled state.
        """
        if Globals.debugFlag and debuggingThisModule:
            print( "BibleResourceWindow.updateShownBCV( {}) for".format( newVerseKey ), self.moduleID )
            print( "contextViewMode", self.contextViewMode )
        self.clearText() # Leaves the text box enabled
        startingFlag = True

        if self.contextViewMode == 'BeforeAndAfter':
            bibleData = self.getBeforeAndAfterBibleData( newVerseKey )
            if bibleData:
                verseData, previousVerses, nextVerses = bibleData
                for verseKey,previousVerseData in previousVerses:
                    self.displayAppendVerse( startingFlag, verseKey, previousVerseData )
                    startingFlag = False
                self.displayAppendVerse( startingFlag, newVerseKey, verseData, currentVerse=True )
                for verseKey,nextVerseData in nextVerses:
                    self.displayAppendVerse( False, verseKey, nextVerseData )

        elif self.contextViewMode == 'ByVerse':
            self.displayAppendVerse( True, newVerseKey, self.getCachedVerseData( newVerseKey ), currentVerse=True )

        elif self.contextViewMode == 'ByBook':
            BBB, C, V = newVerseKey.getBCV()
            intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            for thisC in range( 0, self.getNumChapters( BBB ) ):
                try: numVerses = self.getNumVerses( BBB, thisC )
                except KeyError: numVerses = 0
                for thisV in range( 0, numVerses ):
                    thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    thisVerseData = self.getCachedVerseData( thisVerseKey )
                    self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            currentVerse=thisC==intC and thisV==intV )
                    startingFlag = False

        elif self.contextViewMode == 'ByChapter':
            BBB, C, V = newVerseKey.getBCV()
            intV = newVerseKey.getVerseNumberInt()
            try: numVerses = self.getNumVerses( BBB, C )
            except KeyError: numVerses = 0
            for thisV in range( 0, numVerses ):
                thisVerseKey = SimpleVerseKey( BBB, C, thisV )
                thisVerseData = self.getCachedVerseData( thisVerseKey )
                self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData, currentVerse=thisV==intV )
                startingFlag = False

        else: halt # Unknown context view mode

        self.textBox['state'] = DISABLED # Don't allow editing
        self.refreshTitle()
    # end of BibleResourceWindow.updateShownBCV
# end of BibleResourceWindow class



class SwordBibleResourceWindow( BibleResourceWindow ):
    def __init__( self, parentApp, moduleAbbreviation ):
        if Globals.debugFlag: print( "SwordBibleResourceWindow.__init__( {}, {} )".format( parentApp, moduleAbbreviation ) )
        BibleResourceWindow.__init__( self, parentApp, moduleAbbreviation )
        self.parentApp, self.moduleAbbreviation = parentApp, moduleAbbreviation
        self.winType = 'SwordBibleResourceWindow'

        #self.SwordModule = None # Loaded later in self.getBeforeAndAfterBibleData()
        self.SwordModule = self.parentApp.SwordInterface.getModule( self.moduleAbbreviation )
        if self.SwordModule is None:
            logging.error( t("SwordBibleResourceWindow.__init__ Unable to open Sword module: {}").format( self.moduleAbbreviation ) )
            self.SwordModule = None
    # end of SwordBibleResourceWindow.__init__


    def refreshTitle( self ):
        self.title( "[{}] {} ({}) {}".format( self.groupCode,
                                    self.moduleAbbreviation, 'Sw' if SwordType=="CrosswireLibrary" else 'SwM',
                                    self.contextViewMode ) )
    # end if SwordBibleResourceWindow.refreshTitle


    def getVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if Globals.debugFlag: print( t("SwordBibleResourceWindow.getVerseData( {} )").format( verseKey ) )
        if self.SwordModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                SwordKey = self.getSwordVerseKey( verseKey )
                return self.parentApp.SwordInterface.getVerseData( self.SwordModule, SwordKey )
    # end of SwordBibleResourceWindow.getVerseData
# end of SwordBibleResourceWindow class



class DBPBibleResourceWindow( BibleResourceWindow ):
    def __init__( self, parentApp, moduleAbbreviation ):
        if Globals.debugFlag:
            print( "DBPBibleResourceWindow.__init__( {}, {} )".format( parentApp, moduleAbbreviation ) )
            assert( moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6 )
        BibleResourceWindow.__init__( self, parentApp, moduleAbbreviation )
        self.parentApp, self.moduleAbbreviation = parentApp, moduleAbbreviation
        self.winType = 'DBPBibleResourceWindow'

        try: self.DBPModule = DBPBible( self.moduleAbbreviation )
        except FileNotFoundError:
            logging.error( t("DBPBibleResourceWindow.__init__ Unable to find a key to connect to Digital Bible Platform") )
            self.DBPModule = None
        except ConnectionError:
            logging.error( t("DBPBibleResourceWindow.__init__ Unable to connect to Digital Bible Platform") )
            self.DBPModule = None
    # end of DBPBibleResourceWindow.__init__


    def refreshTitle( self ):
        self.title( "[{}] {}.{}{} {}".format( self.groupCode,
                                                self.moduleAbbreviation[:3], self.moduleAbbreviation[3:],
                                                ' (online)' if self.DBPModule else ' (offline)',
                                                self.contextViewMode ) )
    # end if DBPBibleResourceWindow.refreshTitle


    def getVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("DBPBibleResourceWindow.getVerseData( {} )").format( verseKey ) )
        if self.DBPModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                return self.DBPModule.getVerseData( verseKey )
    # end of DBPBibleResourceWindow.getVerseData
# end of DBPBibleResourceWindow class



class InternalBibleResourceWindow( BibleResourceWindow ):
    def __init__( self, parentApp, modulePath ):
        """
        Given a folder, try to open an UnknownBible.
        If successful, set self.InternalBible to point to the loaded Bible.
        """
        if Globals.debugFlag: print( "InternalBibleResourceWindow.__init__( {}, {} )".format( parentApp, modulePath ) )
        BibleResourceWindow.__init__( self, parentApp, modulePath )
        self.parentApp, self.modulePath = parentApp, modulePath
        self.winType = 'InternalBibleResourceWindow'

        try: self.UnknownBible = UnknownBible( self.modulePath )
        except FileNotFoundError:
            logging.error( t("InternalBibleResourceWindow.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
            self.UnknownBible = None
        if self.UnknownBible:
            result = self.UnknownBible.search( autoLoadAlways=True )
            if isinstance( result, str ):
                print( "Unknown Bible returned: {}".format( repr(result) ) )
                self.InternalBible = None
            else: self.InternalBible = result
        if self.InternalBible is not None: # Define which functions we use by default
            self.getNumVerses = self.InternalBible.getNumVerses
            self.getNumChapters = self.InternalBible.getNumChapters
    # end of InternalBibleResourceWindow.__init__


    def refreshTitle( self ):
        self.title( "[{}] {} (InternalBible){} {}".format( self.groupCode,
                        self.modulePath if self.InternalBible is None else self.InternalBible.name,
                        ' NOT FOUND' if self.InternalBible is None else '', self.contextViewMode ) )
    # end if InternalBibleResourceWindow.refreshTitle


    def getVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if Globals.debugFlag: print( t("InternalBibleResourceWindow.getVerseData( {} )").format( verseKey ) )
        if self.InternalBible is not None:
            try: return self.InternalBible.getVerseData( verseKey )
            except KeyError:
                logging.critical( t("InternalBibleResourceWindow.getVerseData for {} {} got a KeyError!") \
                                                                .format( self.winType, verseKey ) )
    # end of InternalBibleResourceWindow.getVerseData
# end of InternalBibleResourceWindow class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if Globals.debugFlag: print( t("Running demo...") )
    #Globals.debugFlag = True

    tkRootWindow = Tk()
    tkRootWindow.title( ProgNameVersion )

    #settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', ProgName )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of BibleResourceWindows.demo


if __name__ == '__main__':
    import multiprocessing

    # Configure basic set-up
    parser = Globals.setup( ProgName, ProgVersion )
    Globals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if 1 and Globals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    Globals.closedown( ProgName, ProgVersion )
# end of BibleResourceWindows.py
