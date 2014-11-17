#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleResourceCollection.py
#   Last modified: 2014-11-17 (also update ProgVersion below)
#
# Bible resource collection for Biblelator Bible display/editing
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
Windows and frames to allow display and manipulation of
    (non-editable) Bible resource windows.
"""

ShortProgName = "BibleResourceCollection"
ProgName = "Biblelator Bible Resource Collection"
ProgVersion = "0.25"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, logging #, os.path, configparser, logging
from gettext import gettext as _
from collections import OrderedDict

import tkinter as tk
from tkinter.filedialog import Open, Directory #, SaveAs
from tkinter.ttk import Frame, Scrollbar

# Biblelator imports
from BiblelatorGlobals import APP_NAME, START, DEFAULT, BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES
from BiblelatorDialogs import showerror, SelectResourceBox #, showwarning, showinfo, errorBeep
from ChildWindows import ChildBox
from BibleResourceWindows import BibleResourceWindow

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import BibleOrgSysGlobals
from VerseReferences import SimpleVerseKey
#from USFMFile import splitMarkerText
from DigitalBiblePlatform import DBPBibles, DBPBible
from SwordResources import SwordType, SwordInterface
from UnknownBible import UnknownBible
from BibleOrganizationalSystems import BibleOrganizationalSystem


MAX_CACHED_VERSES = 30 # Per Bible resource window



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
# end of BibleResourceCollection.t



class BibleResourceBox( Frame, ChildBox ):
    """
    The superclass must provide a getVerseData function.
    """
    def __init__( self, parentWindow, boxType, moduleID ):
        if BibleOrgSysGlobals.debugFlag: print( t("BibleResourceBox.__init__( {}, {}, {} )").format( parentWindow, boxType, moduleID ) )
        self.parentWindow, self.boxType, self.moduleID = parentWindow, boxType, moduleID
        Frame.__init__( self, parentWindow )
        ChildBox.__init__( self, self.parentWindow.parentApp )

        # Set some dummy values required soon
        self._viewRadio, self._groupRadio = tk.IntVar(), tk.StringVar()
        self.groupCode = BIBLE_GROUP_CODES[0] # Put into first/default BCV group
        self.contextViewMode = DEFAULT
        self.viewMode = DEFAULT
        self.currentVerseKey = SimpleVerseKey( 'UNK','1','1' ) # Unknown book

        if self.contextViewMode == DEFAULT:
            self.contextViewMode = 'ByVerse'
            self.parentWindow.viewVersesBefore, self.parentWindow.viewVersesAfter = 2, 6

        # Create a title bar
        titleText = '{} ({})'.format( moduleID, boxType.replace( 'BibleResourceBox', '' ) )
        self.titleLabel = tk.Label( self, text=titleText )
        self.titleLabel.pack( side=tk.TOP, fill=tk.X )

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        self.textBox = tk.Text( self, height=1, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox['wrap'] = 'word'
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.config( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardKeyboardBindings()
        self.textBox.bind( "<Button-1>", self.setFocus ) # So disabled text box can still do select and copy functions

        for USFMKey, styleDict in self.parentWindow.parentApp.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style

        self.pack( expand=tk.YES, fill=tk.BOTH ) # Pack the frame

        # Set-up our Bible system and our callables
        self.BibleOrganisationalSystem = BibleOrganizationalSystem( "GENERIC-KJV-66-ENG" ) # temp
        self.getNumChapters = self.BibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda b,c: 99 if c=='0' or c==0 else self.BibleOrganisationalSystem.getNumVerses( b, c )
        self.isValidBCVRef = self.BibleOrganisationalSystem.isValidBCVRef
        self.getFirstBookCode = self.BibleOrganisationalSystem.getFirstBookCode
        self.getPreviousBookCode = self.BibleOrganisationalSystem.getPreviousBookCode
        self.getNextBookCode = self.BibleOrganisationalSystem.getNextBookCode
        self.getBBB = self.BibleOrganisationalSystem.getBBB
        self.getBookName = self.BibleOrganisationalSystem.getBookName
        self.getBookList = self.BibleOrganisationalSystem.getBookList
        self.maxChapters, self.maxVerses = 150, 150 # temp

        self.verseCache = OrderedDict()
    # end of BibleResourceBox.__init__


    def gotoBCV( self, BBB, C, V ):
        """

        """
        if BibleOrgSysGlobals.debugFlag: print( t("BibleResourceBox.gotoBCV( {} {}:{} from {} )").format( BBB, C, V, self.currentVerseKey ) )
        # We really need to convert versification systems here
        adjBBB, adjC, adjV, adjS = self.BibleOrganisationalSystem.convertToReferenceVersification( BBB, C, V )
        self.parentWindow.gotoGroupBCV( self.groupCode, adjBBB, adjC, adjV ) # then the App will update me by calling updateShownBCV
    # end of BibleResourceBox.gotoBCV


    def getSwordVerseKey( self, verseKey ):
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("getSwordVerseKey( {} )").format( verseKey ) )
            BBB, C, V = verseKey.getBCV()
            return self.parentWindow.parentApp.SwordInterface.makeKey( BBB, C, V )
    # end of BibleResourceBox.getSwordVerseKey


    def getCachedVerseData( self, verseKey ):
        """
        Checks to see if the requested verse is in our cache,
            otherwise calls getVerseData to fetch it.

        The cache keeps the newest or most recently used entries at the end.
        When it gets too large, it drops the first entry.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("getCachedVerseData( {} )").format( verseKey ) )
        verseKeyHash = verseKey.makeHash()
        if verseKeyHash in self.verseCache:
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  " + t("Retrieved from BibleResourceBox cache") )
            self.verseCache.move_to_end( verseKeyHash )
            return self.verseCache[verseKeyHash]
        verseData = self.getVerseData( verseKey )
        self.verseCache[verseKeyHash] = verseData
        if len(self.verseCache) > MAX_CACHED_VERSES:
            #print( "Removing oldest cached entry", len(self.verseCache) )
            self.verseCache.popitem( last=False )
        return verseData
    # end of BibleResourceBox.getCachedVerseData


    def displayAppendVerse( self, firstFlag, verseKey, verseDataList, currentVerse=False ):
        """
        Add the requested verse to the end of self.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #try: print( t("BibleResourceBox.displayAppendVerse"), firstFlag, verseKey, verseDataList, currentVerse )
            #except UnicodeEncodeError: print( t("BibleResourceBox.displayAppendVerse"), firstFlag, verseKey, currentVerse )

        BBB, C, V = verseKey.getBCV()
        markName = 'C{}V{}'.format( C, V )
        self.textBox.mark_set( markName, tk.INSERT )
        self.textBox.mark_gravity( markName, tk.LEFT )
        lastCharWasSpace = haveTextFlag = not firstFlag

        if verseDataList is None:
            if C!='0': print( "  ", verseKey, "has no data for", self.moduleID )
            #self.textBox.insert( tk.END, '--' )
        elif self.viewMode == DEFAULT:
            # This needs fixing -- indents, etc. should be in stylesheet not hard-coded
            for entry in verseDataList:
                if isinstance( entry, tuple ):
                    marker, cleanText = entry[0], entry[3]
                else: marker, cleanText = entry.getMarker(), entry.getCleanText()
                #print( "  ", haveTextFlag, marker, repr(cleanText) )
                if marker and marker[0]=='¬': pass # Ignore end markers for now
                elif marker in ('chapters',): pass # Ignore added markers for now
                elif marker == 'id':
                    self.textBox.insert( tk.END, ('\n\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker in ('ide','rem',):
                    self.textBox.insert( tk.END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker == 'c': # Don't want to display this (original) c marker
                    #if not firstFlag: haveC = cleanText
                    #else: print( "   Ignore C={}".format( cleanText ) )
                    pass
                elif marker == 'c#': # Might want to display this (added) c marker
                    if cleanText != verseKey.getBBB():
                        if not lastCharWasSpace: self.textBox.insert( tk.END, ' ', 'v-' )
                        self.textBox.insert( tk.END, cleanText, 'c#' )
                        lastCharWasSpace = False
                elif marker in ('mt1','mt2','mt3','mt4', 'iot','io1','io2','io3','io4',):
                    self.textBox.insert( tk.END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker in ('s1','s2','s3','s4',):
                    self.textBox.insert( tk.END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker == 'r':
                    self.textBox.insert( tk.END, ('\n' if haveTextFlag else '')+cleanText, marker )
                    haveTextFlag = True
                elif marker in ('p','ip',):
                    self.textBox.insert ( tk.END, '\n  ' if haveTextFlag else '  ' )
                    lastCharWasSpace = True
                    if cleanText:
                        self.textBox.insert( tk.END, cleanText, '*v~' if currentVerse else 'v~' )
                        lastCharWasSpace = False
                    haveTextFlag = True
                elif marker == 'p#' and self.boxType=='DBPBibleResourceBox':
                    pass # Just ignore these for now
                elif marker in ('q1','q2','q3','q4',):
                    self.textBox.insert ( tk.END, '\n  ' if haveTextFlag else '  ' )
                    lastCharWasSpace = True
                    if cleanText:
                        self.textBox.insert( tk.END, cleanText, '*'+marker if currentVerse else marker )
                        lastCharWasSpace = False
                    haveTextFlag = True
                elif marker == 'm': pass
                elif marker == 'v':
                    if haveTextFlag:
                        self.textBox.insert( tk.END, ' ', 'v-' )
                    self.textBox.insert( tk.END, cleanText, marker )
                    self.textBox.insert( tk.END, ' ', 'v+' )
                    lastCharWasSpace = haveTextFlag = True
                elif marker in ('v~','p~'):
                    self.textBox.insert( tk.END, cleanText, '*v~' if currentVerse else marker )
                    haveTextFlag = True
                else:
                    logging.critical( t("BibleResourceBox.displayAppendVerse: Unknown marker {} {} from {}").format( marker, cleanText, verseDataList ) )
        else:
            logging.critical( t("BibleResourceBox.displayAppendVerse: Unknown {} view mode").format( repr(self.viewMode) ) )
    # end of BibleResourceBox.displayAppendVerse


    def getBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("BibleResourceBox.getBeforeAndAfterBibleData( {} )").format( newVerseKey ) )
            assert( isinstance( newVerseKey, SimpleVerseKey ) )

        BBB, C, V = newVerseKey.getBCV()
        intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        prevBBB, prevIntC, prevIntV = BBB, intC, intV
        previousVersesData = []
        for n in range( -self.parentWindow.viewVersesBefore, 0 ):
            failed = False
            #print( "  getBeforeAndAfterBibleData here with", n, prevIntC, prevIntV )
            if prevIntV > 0: prevIntV -= 1
            elif prevIntC > 0:
                prevIntC -= 1
                try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                except KeyError:
                    if prevIntC != 0: # we can expect an error for chapter zero
                        logging.critical( t("getBeforeAndAfterBibleData failed at"), prevBBB, prevIntC )
                    failed = True
                #if not failed:
                    #if BibleOrgSysGlobals.debugFlag: print( " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            else:
                prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                if prevBBB is None: failed = True
                else:
                    prevIntC = self.getNumChapters( prevBBB )
                    prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    if BibleOrgSysGlobals.debugFlag: print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
            if not failed and prevIntV is not None:
                #print( "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                assert( prevBBB and isinstance(prevBBB, str) )
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getCachedVerseData( previousVerseKey )
                if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        # Determine the next valid verse numbers
        nextBBB, nextIntC, nextIntV = BBB, intC, intV
        nextVersesData = []
        for n in range( 0, self.parentWindow.viewVersesAfter ):
            try: numVerses = self.getNumVerses( nextBBB, nextIntC )
            except KeyError: numVerses = None # for an invalid BBB
            nextIntV += 1
            if numVerses is None or nextIntV > numVerses:
                nextIntV = 1
                nextIntC += 1 # Need to check................................
            nextVerseKey = SimpleVerseKey( nextBBB, nextIntC, nextIntV )
            nextVerseData = self.getCachedVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        verseData = self.getCachedVerseData( newVerseKey )

        return verseData, previousVersesData, nextVersesData
    # end of BibleResourceBox.getBeforeAndAfterBibleData


    def setCurrentVerseKey( self, newVerseKey ):
        """
        Called to set the current verse key.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("BibleResourceBox.setCurrentVerseKey( {} )").format( newVerseKey ) )
            self.parentWindow.parentApp.setDebugText( "BRW setCurrentVerseKey..." )
            assert( isinstance( newVerseKey, SimpleVerseKey ) )
        self.currentVerseKey = newVerseKey

        BBB = self.currentVerseKey.getBBB()
        self.maxChapters = self.getNumChapters( BBB )
        self.maxVerses = self.getNumVerses( BBB, self.currentVerseKey.getChapterNumber() )
    # end of BibleResourceBox.setCurrentVerseKey


    def updateShownBCV( self, newReferenceVerseKey ):
        """
        Updates self in various ways depending on the contextViewMode held by the enclosing window.

        The new verse key is in the reference versification system.

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceBox.updateShownBCV( {}) for".format( newReferenceVerseKey ), self.moduleID )
            #print( "contextViewMode", self.contextViewMode )
            assert( isinstance( newReferenceVerseKey, SimpleVerseKey ) )

        refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
        BBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
        newVerseKey = SimpleVerseKey( BBB, C, V, S )

        self.setCurrentVerseKey( newVerseKey )
        self.clearText() # Leaves the text box enabled
        startingFlag = True

        # Safety-check in case they edited the settings file
        if 'DBP' in self.boxType and self.contextViewMode in ('ByBook','ByChapter',):
            print( t("updateShownBCV: Safety-check converted {} contextViewMode for DBP").format( repr(self.contextViewMode) ) )
            self._viewRadio.set( 3 ) # ByVerse
            self.changeBibleContextView()

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

        elif self.contextViewMode == 'BySection':
            self.displayAppendVerse( True, newVerseKey, self.getCachedVerseData( newVerseKey ), currentVerse=True )
            BBB, C, V = newVerseKey.getBCV()
            intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            print( "\nBySection is not finished yet -- just shows a single verse!\n" ) # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #for thisC in range( 0, self.getNumChapters( BBB ) ):
                #try: numVerses = self.getNumVerses( BBB, thisC )
                #except KeyError: numVerses = 0
                #for thisV in range( 0, numVerses ):
                    #thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    #thisVerseData = self.getCachedVerseData( thisVerseKey )
                    #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            #currentVerse=thisC==intC and thisV==intV )
                    #startingFlag = False

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

        else:
            logging.critical( t("BibleResourceBox.updateShownBCV: Bad context view mode {}").format( self.contextViewMode ) )
            if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode

        self.textBox['state'] = tk.DISABLED # Don't allow editing

        # Make sure we can see what we're supposed to be looking at
        desiredMark = 'C{}V{}'.format( newVerseKey.getChapterNumber(), newVerseKey.getVerseNumber() )
        try: self.textBox.see( desiredMark )
        except tk.TclError: print( t("USFMEditWindow.updateShownBCV couldn't find {}").format( repr( desiredMark ) ) )
        self.lastCVMark = desiredMark
    # end of BibleResourceBox.updateShownBCV


    def xxxsetAllText( self, newBibleText ): #, markAsUnmodified=True ):
        """
        Sets the textBox (assumed to be enabled) to the given Bible text.

        Inserts BCV marks as it does it.

        Doesn't position the cursor as it assumes a follow-up call will navigate to the current verse.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        self.delete( START, tk.END ) # clear any existing text
        self.textBox.mark_set( 'C0V0', START )
        C = V = '0'
        for line in newBibleText.split( '\n' ):
            #print( "line", repr(line) )
            if not line: self.textBox.insert( tk.END, '\n' ); continue
            marker, text = splitMarkerText( line )
            #print( "m,t", repr(marker), repr(text) )
            if marker == 'c':
                C, V = text, '0' # Doesn't handle footnotes, etc.
                markName = 'C{}V0'.format( C )
                self.textBox.mark_set( markName, tk.INSERT )
                self.textBox.mark_gravity( markName, tk.LEFT )
            elif marker == 'v':
                V = text.split()[0] # Doesn't handle footnotes, etc.
                markName = 'C{}V{}'.format( C, V )
                self.textBox.mark_set( markName, tk.INSERT )
                self.textBox.mark_gravity( markName, tk.LEFT )
            elif C == '0': # marker each line
                markName = 'C0V{}'.format( V )
                self.textBox.mark_set( markName, tk.INSERT )
                self.textBox.mark_gravity( markName, tk.LEFT )
                V = str( int(V) + 1 )
            self.textBox.insert( tk.END, line+'\n', marker ) # This will ensure a \n at the end of the file

        # Not needed here hopefully
        #self.textBox.mark_set( tk.INSERT, START ) # move insert point to top
        #self.see( tk.INSERT ) # scroll to top, insert is set

        #if markAsUnmodified:
        self.edit_reset() # clear undo/redo stks
        self.edit_modified( False ) # clear modified flag
    # end of BibleResourceBox.setAllText


    def doHelp( self, event=None ):
        from Help import HelpBox
        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.winType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of Application.doHelp


    def doAbout( self, event=None ):
        from About import AboutBox
        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.winType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of Application.doAbout
# end of BibleResourceBox class



class SwordBibleResourceBox( BibleResourceBox ):
    def __init__( self, parentWindow, moduleAbbreviation ):
        if BibleOrgSysGlobals.debugFlag: print( "SwordBibleResourceBox.__init__( {}, {} )".format( parentWindow, moduleAbbreviation ) )
        self.parentWindow, self.moduleAbbreviation = parentWindow, moduleAbbreviation
        BibleResourceBox.__init__( self, self.parentWindow, 'SwordBibleResourceBox', self.moduleAbbreviation )
        #self.boxType = 'SwordBibleResourceBox'

        #self.SwordModule = None # Loaded later in self.getBeforeAndAfterBibleData()
        self.SwordModule = self.parentWindow.parentApp.SwordInterface.getModule( self.moduleAbbreviation )
        if self.SwordModule is None:
            logging.error( t("SwordBibleResourceBox.__init__ Unable to open Sword module: {}").format( self.moduleAbbreviation ) )
            self.SwordModule = None
    # end of SwordBibleResourceBox.__init__


    def getVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( t("SwordBibleResourceBox.getVerseData( {} )").format( verseKey ) )
        if self.SwordModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                SwordKey = self.getSwordVerseKey( verseKey )
                rawInternalBibleData = self.parentWindow.parentApp.SwordInterface.getVerseData( self.SwordModule, SwordKey )
                # Clean up the data -- not sure that it should be done here! ....... XXXXXXXXXXXXXXXXXXX
                from InternalBibleInternals import InternalBibleEntryList, InternalBibleEntry
                import re
                adjustedInternalBibleData = InternalBibleEntryList()
                for existingInternalBibleEntry in rawInternalBibleData:
                    #print( 'eIBE', existingInternalBibleEntry )
                    cleanText = existingInternalBibleEntry.getCleanText()
                    cleanText = cleanText.replace( '</w>', '' )
                    cleanText = re.sub( '<w .+?>', '', cleanText )
                    newInternalBibleEntry = InternalBibleEntry( existingInternalBibleEntry[0], existingInternalBibleEntry[1], existingInternalBibleEntry[2],
                        cleanText, existingInternalBibleEntry[4], existingInternalBibleEntry[5] )
                    #print( 'nIBE', newInternalBibleEntry )
                    adjustedInternalBibleData.append( newInternalBibleEntry )
                return adjustedInternalBibleData
    # end of SwordBibleResourceBox.getVerseData
# end of SwordBibleResourceBox class



class DBPBibleResourceBox( BibleResourceBox ):
    def __init__( self, parentWindow, moduleAbbreviation ):
        if BibleOrgSysGlobals.debugFlag:
            print( "DBPBibleResourceBox.__init__( {}, {} )".format( parentWindow, moduleAbbreviation ) )
            assert( moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6 )
        self.parentWindow, self.moduleAbbreviation = parentWindow, moduleAbbreviation

        self.DBPModule = None # (for refreshTitle called from the base class)
        BibleResourceBox.__init__( self, self.parentWindow, 'DBPBibleResourceBox', self.moduleAbbreviation )
        #self.boxType = 'DBPBibleResourceBox'

        try: self.DBPModule = DBPBible( self.moduleAbbreviation )
        except FileNotFoundError:
            logging.error( t("DBPBibleResourceBox.__init__ Unable to find a key to connect to Digital Bible Platform") )
            self.DBPModule = None
        except ConnectionError:
            logging.error( t("DBPBibleResourceBox.__init__ Unable to connect to Digital Bible Platform") )
            self.DBPModule = None
    # end of DBPBibleResourceBox.__init__


    def getVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("DBPBibleResourceBox.getVerseData( {} )").format( verseKey ) )
        if self.DBPModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                return self.DBPModule.getVerseData( verseKey )
    # end of DBPBibleResourceBox.getVerseData
# end of DBPBibleResourceBox class



class InternalBibleResourceBox( BibleResourceBox ):
    def __init__( self, parentWindow, modulePath ):
        """
        Given a folder, try to open an UnknownBible.
        If successful, set self.internalBible to point to the loaded Bible.
        """
        if BibleOrgSysGlobals.debugFlag: print( "InternalBibleResourceBox.__init__( {}, {} )".format( parentWindow, modulePath ) )
        self.parentWindow, self.modulePath = parentWindow, modulePath

        self.internalBible = None
        BibleResourceBox.__init__( self, self.parentWindow, 'InternalBibleResourceBox', self.modulePath )
        #self.boxType = 'InternalBibleResourceBox'

        try: self.UnknownBible = UnknownBible( self.modulePath )
        except FileNotFoundError:
            logging.error( t("InternalBibleResourceBox.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
            self.UnknownBible = None
        if self.UnknownBible:
            result = self.UnknownBible.search( autoLoadAlways=True )
            if isinstance( result, str ):
                print( "Unknown Bible returned: {}".format( repr(result) ) )
                self.internalBible = None
            else: self.internalBible = result
        if self.internalBible is not None: # Define which functions we use by default
            self.getNumVerses = self.internalBible.getNumVerses
            self.getNumChapters = self.internalBible.getNumChapters
    # end of InternalBibleResourceBox.__init__


    def getVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("InternalBibleResourceBox.getVerseData( {} )").format( verseKey ) )
        if self.internalBible is not None:
            try: return self.internalBible.getVerseData( verseKey )
            except KeyError:
                logging.critical( t("InternalBibleResourceBox.getVerseData for {} {} got a KeyError!") \
                                                                .format( self.boxType, verseKey ) )
    # end of InternalBibleResourceBox.getVerseData
# end of InternalBibleResourceBox class



class ResourceBoxes( list ):
    """
    Just keeps a list of the resource (Text) boxes.
    """
    def __init__( self, resourceBoxesParent ):
        self.resourceBoxesParent = resourceBoxesParent
        list.__init__( self )


    def updateThisBibleGroup( self, groupCode, newVerseKey ):
        """
        Called when we probably need to update some resource windows with a new Bible reference.
        """
        if BibleOrgSysGlobals.debugFlag: print( t("ResourceBoxes.updateThisBibleGroup( {}, {} )").format( groupCode, newVerseKey ) )
        for resourceBox in self:
            if 'Bible' in resourceBox.genericWindowType: # e.g., BibleResource, BibleEditor
                if resourceBox.groupCode == groupCode:
                    # The following line doesn't work coz it only updates ONE window
                    #self.resourceBoxesParent.after_idle( lambda: resourceBox.updateShownBCV( newVerseKey ) )
                    resourceBox.updateShownBCV( newVerseKey )
    # end of ResourceBoxes.updateThisBibleGroup
# end of ResourceBoxes class



class BibleResourceCollectionWindow( BibleResourceWindow ):
#class BibleResourceCollectionWindow( ChildWindow ):
    def __init__( self, parentApp, collectionName ):
        """
        Given a collection name, try to open an empty Bible resource collection window.
        """
        if BibleOrgSysGlobals.debugFlag: print( "BibleResourceCollectionWindow.__init__( {}, {} )".format( parentApp, collectionName ) )
        self.parentApp, self.collectionName = parentApp, collectionName

        BibleResourceWindow.__init__( self, self.parentApp, 'BibleResourceCollectionWindow', self.collectionName )
        #ChildWindow.__init__( self, self.parentApp, 'BibleResource' )
        #self.winType = 'InternalBibleResourceBox'
        self.vScrollbar.destroy()
        self.textBox.destroy()

        self.resourceBoxes = ResourceBoxes( self )
    # end of BibleResourceCollectionWindow.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("BibleResourceBox.createMenuBar()") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        #fileMenu.add_command( label='Info...', underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict['Info'][0] )
        #fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.doClose, accelerator=self.parentApp.keyBindingDict['Close'][0] ) # close this window

        if 0:
            editMenu = tk.Menu( self.menubar )
            self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
            editMenu.add_command( label='Copy', underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict['Copy'][0] )
            editMenu.add_separator()
            editMenu.add_command( label='Select all', underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict['SelectAll'][0] )

            searchMenu = tk.Menu( self.menubar )
            self.menubar.add_cascade( menu=searchMenu, label='Search', underline=0 )
            searchMenu.add_command( label='Goto line...', underline=0, command=self.doGotoLine, accelerator=self.parentApp.keyBindingDict['Line'][0] )
            searchMenu.add_separator()
            searchMenu.add_command( label='Find...', underline=0, command=self.doFind, accelerator=self.parentApp.keyBindingDict['Find'][0] )
            searchMenu.add_command( label='Find again', underline=5, command=self.doRefind, accelerator=self.parentApp.keyBindingDict['Refind'][0] )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        gotoMenu.add_command( label='Previous book', underline=-1, command=self.doGotoPreviousBook )
        gotoMenu.add_command( label='Next book', underline=-1, command=self.doGotoNextBook )
        gotoMenu.add_command( label='Previous chapter', underline=-1, command=self.doGotoPreviousChapter )
        gotoMenu.add_command( label='Next chapter', underline=-1, command=self.doGotoNextChapter )
        gotoMenu.add_command( label='Previous section', underline=-1, command=self.notWrittenYet )
        gotoMenu.add_command( label='Next section', underline=-1, command=self.notWrittenYet )
        gotoMenu.add_command( label='Previous verse', underline=-1, command=self.doGotoPreviousVerse )
        gotoMenu.add_command( label='Next verse', underline=-1, command=self.doGotoNextVerse )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Forward', underline=0, command=self.doGoForward )
        gotoMenu.add_command( label='Backward', underline=0, command=self.doGoBackward )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Previous list item', underline=0, state=tk.DISABLED, command=self.doGotoPreviousListItem )
        gotoMenu.add_command( label='Next list item', underline=0, state=tk.DISABLED, command=self.doGotoNextListItem )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Book', underline=0, command=self.doGotoBook )
        gotoMenu.add_separator()
        self._groupRadio.set( self.groupCode )
        gotoMenu.add_radiobutton( label='Group A', underline=6, value='A', variable=self._groupRadio, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group B', underline=6, value='B', variable=self._groupRadio, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group C', underline=6, value='C', variable=self._groupRadio, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group D', underline=6, value='D', variable=self._groupRadio, command=self.changeBibleGroupCode )

        self.viewMenu = tk.Menu( self.menubar, tearoff=False ) # Save this reference so we can disable entries later
        self.menubar.add_cascade( menu=self.viewMenu, label='View', underline=0 )
        if   self.contextViewMode == 'BeforeAndAfter': self._viewRadio.set( 1 )
        #elif self.contextViewMode == 'BySection': self._viewRadio.set( 2 )
        elif self.contextViewMode == 'ByVerse': self._viewRadio.set( 3 )
        #elif self.contextViewMode == 'ByBook': self._viewRadio.set( 4 )
        #elif self.contextViewMode == 'ByChapter': self._viewRadio.set( 5 )
        else: print( self.contextViewMode ); halt

        self.viewMenu.add_radiobutton( label='Before and after...', underline=7, value=1, variable=self._viewRadio, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label='One section', underline=4, value=2, variable=self._viewRadio, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label='Single verse', underline=7, value=3, variable=self._viewRadio, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label='Whole book', underline=6, value=4, variable=self._viewRadio, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label='Whole chapter', underline=6, value=5, variable=self._viewRadio, command=self.changeBibleContextView )

        #if 'DBP' in self.winType: # disable excessive online use
            #self.viewMenu.entryconfigure( 'Whole book', state=tk.DISABLED )
            #self.viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        resourcesMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=resourcesMenu, label=_('Resources'), underline=0 )
        resourcesMenu.add_command( label='Online (DBP)...', underline=0, command=self.doOpenDBPBibleResource )
        resourcesMenu.add_command( label='Sword module...', underline=0, command=self.doOpenSwordResource )
        resourcesMenu.add_command( label='Other (local)...', underline=1, command=self.doOpenInternalBibleResource )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label='Help' )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp, accelerator=self.parentApp.keyBindingDict['Help'][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout, accelerator=self.parentApp.keyBindingDict['About'][0] )
    # end of BibleResourceCollectionWindow.createMenuBar


    def refreshTitle( self ):
        self.title( "[{}] {} Bible Resource Collection {} {}:{}".format( self.groupCode,
                        self.collectionName,
                        self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber() ) )
    # end if BibleResourceCollectionWindow.refreshTitle


    def changeBibleContextView( self ):
        """
        Called when  a Bible context view is changed from the menus/GUI.
        """
        currentViewNumber = self._viewRadio.get()
        if BibleOrgSysGlobals.debugFlag:
            print( t("changeBibleContextView( {} ) from {}").format( repr(currentViewNumber), repr(self.contextViewMode) ) )
            assert( currentViewNumber in range( 1, len(BIBLE_CONTEXT_VIEW_MODES)+1 ) )
        previousContextViewMode = self.contextViewMode
        if 'Bible' in self.genericWindowType:
            if currentViewNumber == 1: self.contextViewMode = BIBLE_CONTEXT_VIEW_MODES[0] # 'BeforeAndAfter'
            elif currentViewNumber == 2: self.contextViewMode = BIBLE_CONTEXT_VIEW_MODES[1] # 'BySection'
            elif currentViewNumber == 3: self.contextViewMode = BIBLE_CONTEXT_VIEW_MODES[2] # 'ByVerse'
            elif currentViewNumber == 4: self.contextViewMode = BIBLE_CONTEXT_VIEW_MODES[3] # 'ByBook'
            elif currentViewNumber == 5: self.contextViewMode = BIBLE_CONTEXT_VIEW_MODES[4] # 'ByChapter'
            else: halt # unknown Bible view mode
        else: halt # window type view mode not handled yet
        if self.contextViewMode != previousContextViewMode: # we need to update our view
            if   self.groupCode == 'A': windowVerseKey = self.parentApp.GroupA_VerseKey
            elif self.groupCode == 'B': windowVerseKey = self.parentApp.GroupB_VerseKey
            elif self.groupCode == 'C': windowVerseKey = self.parentApp.GroupC_VerseKey
            elif self.groupCode == 'D': windowVerseKey = self.parentApp.GroupD_VerseKey
            self.updateShownBCV( windowVerseKey )
    # end of BibleResourceCollectionWindow.changeBibleContextView


    def changeBibleGroupCode( self ):
        """
        Called when  a Bible group code is changed from the menus/GUI.
        """
        previousGroupCode = self.groupCode
        newGroupCode = self._groupRadio.get()
        if BibleOrgSysGlobals.debugFlag:
            print( t("changeBibleGroupCode( {} ) from {}").format( repr(newGroupCode), repr(previousGroupCode) ) )
            assert( newGroupCode in BIBLE_GROUP_CODES )
        assert( 'Bible' in self.genericWindowType )
        if 'Bible' in self.genericWindowType: # do we really need this test?
            self.groupCode = newGroupCode
        else: halt # window type view mode not handled yet
        if self.groupCode != previousGroupCode: # we need to update our view
            if   self.groupCode == 'A': windowVerseKey = self.parentApp.GroupA_VerseKey
            elif self.groupCode == 'B': windowVerseKey = self.parentApp.GroupB_VerseKey
            elif self.groupCode == 'C': windowVerseKey = self.parentApp.GroupC_VerseKey
            elif self.groupCode == 'D': windowVerseKey = self.parentApp.GroupD_VerseKey
            self.updateShownBCV( windowVerseKey )
    # end of BibleResourceCollectionWindow.changeBibleGroupCode


    def doGotoPreviousBook( self, gotoEnd=False ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoPreviousBook( {} ) from {} {}:{}").format( gotoEnd, BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousBook..." )
        newBBB = self.getPreviousBookCode( BBB )
        if newBBB is None: self.gotoBCV( BBB, '0', '0' )
        else:
            self.maxChapters = self.getNumChapters( newBBB )
            self.maxVerses = self.getNumVerses( newBBB, self.maxChapters )
            if gotoEnd: self.gotoBCV( newBBB, self.maxChapters, self.maxVerses )
            else: self.gotoBCV( newBBB, '0', '0' ) # go to the beginning
    # end of BibleResourceCollectionWindow.doGotoPreviousBook


    def doGotoNextBook( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoNextBook() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextBook..." )
        newBBB = self.getNextBookCode( BBB )
        if newBBB is None: pass # stay just where we are
        else:
            self.maxChapters = self.getNumChapters( newBBB )
            self.maxVerses = self.getNumVerses( newBBB, '0' )
            self.gotoBCV( newBBB, '0', '0' ) # go to the beginning of the book
    # end of BibleResourceCollectionWindow.doGotoNextBook


    def doGotoPreviousChapter( self, gotoEnd=False ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoPreviousChapter() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousChapter..." )
        intC, intV = int( C ), int( V )
        if intC > 0: self.gotoBCV( BBB, intC-1, self.getNumVerses( BBB, intC-1 ) if gotoEnd else '0' )
        else: self.doGotoPreviousBook( gotoEnd=True )
    # end of BibleResourceCollectionWindow.doGotoPreviousChapter


    def doGotoNextChapter( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoNextChapter() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextChapter..." )
        intC = int( C )
        if intC < self.maxChapters: self.gotoBCV( BBB, intC+1, '0' )
        else: self.doGotoNextBook()
    # end of BibleResourceCollectionWindow.doGotoNextChapter


    def doGotoPreviousVerse( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoPreviousVerse() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousVerse..." )
        intC, intV = int( C ), int( V )
        if intV > 0: self.gotoBCV( BBB, C, intV-1 )
        elif intC > 0: self.doGotoPreviousChapter( gotoEnd=True )
        else: self.doGotoPreviousBook( gotoEnd=True )
    # end of BibleResourceCollectionWindow.doGotoPreviousVerse


    def doGotoNextVerse( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoNextVerse() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextVerse..." )
        intV = int( V )
        if intV < self.maxVerses: self.gotoBCV( BBB, C, intV+1 )
        else: self.doGotoNextChapter()
    # end of BibleResourceCollectionWindow.doGotoNextVerse


    def doGoForward( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGoForward() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGoForward..." )
        self.notWrittenYet()
    # end of BibleResourceCollectionWindow.doGoForward


    def doGoBackward( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGoBackward() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGoBackward..." )
        self.notWrittenYet()
    # end of BibleResourceCollectionWindow.doGoBackward


    def doGotoPreviousListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoPreviousListItem() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousListItem..." )
        self.notWrittenYet()
    # end of BibleResourceCollectionWindow.doGotoPreviousListItem


    def doGotoNextListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoNextListItem() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextListItem..." )
        self.notWrittenYet()
    # end of BibleResourceCollectionWindow.doGotoNextListItem


    def doGotoBook( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoBook() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoBook..." )
        self.notWrittenYet()
    # end of BibleResourceCollectionWindow.doGotoBook


    def doOpenDBPBibleResource( self ):
        """
        Open an online DigitalBiblePlatform Bible (called from a menu/GUI action).

        Requests a version name from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doOpenDBPBibleResource()") )
            self.parentApp.setDebugText( "doOpenDBPBibleResource..." )
        self.parentApp.setWaitStatus( "doOpenDBPBibleResource..." )
        if self.parentApp.DBPInterface is None:
            self.parentApp.DBPInterface = DBPBibles()
            availableVolumes = self.parentApp.DBPInterface.fetchAllEnglishTextVolumes()
            #print( "aV1", repr(availableVolumes) )
            if availableVolumes:
                srb = SelectResourceBox( self, [(x,y) for x,y in availableVolumes.items()], title=_('Open DBP resource') )
                #print( "srbResult", repr(srb.result) )
                if srb.result:
                    for entry in srb.result:
                        self.openDBPBibleResourceBox( entry[1] )
                    #self.acceptNewBnCV()
                    #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
                elif BibleOrgSysGlobals.debugFlag: print( t("doOpenDBPBibleResource: no resource selected!") )
            else:
                logging.critical( t("doOpenDBPBibleResource: no volumes available") )
                self.parentApp.setStatus( "Digital Bible Platform unavailable (offline?)" )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished doOpenDBPBibleResource" )
    # end of BibleResourceCollectionWindow.doOpenDBPBibleResource

    def openDBPBibleResourceBox( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested DBP Bible resource window.

        Returns the new DBPBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openDBPBibleResourceBox()") )
            self.parentApp.setDebugText( "openDBPBibleResourceBox..." )
            assert( moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6 )
        #tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        dBRB = DBPBibleResourceBox( self, moduleAbbreviation )
        if windowGeometry: halt; dBRB.geometry( windowGeometry )
        if dBRB.DBPModule is None:
            logging.critical( t("Application.openDBPBibleResourceBox: Unable to open resource {}").format( repr(moduleAbbreviation) ) )
            dBRB.destroy()
            showerror( APP_NAME, _("Sorry, unable to open DBP resource") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openDBPBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return None
        else:
            dBRB.updateShownBCV( self.parentApp.getVerseKey( dBRB.groupCode ) )
            self.resourceBoxes.append( dBRB )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openDBPBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return dBRB
    # end of BibleResourceCollectionWindow.openDBPBibleResourceBox


    def doOpenSwordResource( self ):
        """
        Open a local Sword Bible (called from a menu/GUI action).

        Requests a module abbreviation from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openSwordResource()") )
            self.parentApp.setDebugText( "doOpenSwordResource..." )
        self.parentApp.setStatus( "doOpenSwordResource..." )
        if self.parentApp.SwordInterface is None and SwordType is not None:
            self.parentApp.SwordInterface = SwordInterface() # Load the Sword library
        if self.parentApp.SwordInterface is None: # still
            logging.critical( t("doOpenSwordResource: no Sword interface available") )
            showerror( APP_NAME, _("Sorry, no Sword interface discovered") )
            return
        availableModules = self.parentApp.SwordInterface.library
        #print( "aM1", availableModules )
        ourList = None
        if availableModules is not None:
            ourList = availableModules.getAvailableModuleCodes()
        #print( "ourList", ourList )
        if ourList:
            srb = SelectResourceBox( self, ourList, title=_("Open Sword resource") )
            #print( "srbResult", repr(srb.result) )
            if srb.result:
                for entry in srb.result:
                    self.parentApp.setWaitStatus( _("Loading {} Sword module...").format( repr(entry) ) )
                    self.openSwordBibleResourceBox( entry )
                #self.acceptNewBnCV()
                #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
            elif BibleOrgSysGlobals.debugFlag: print( t("doOpenSwordResource: no resource selected!") )
        else:
            logging.critical( t("doOpenSwordResource: no list available") )
            showerror( APP_NAME, _("No Sword resources discovered") )
        #self.acceptNewBnCV()
        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of BibleResourceCollectionWindow.doOpenSwordResource

    def openSwordBibleResourceBox( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested Sword Bible resource window.

        Returns the new SwordBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openSwordBibleResourceBox()") )
            self.parentApp.setDebugText( "openSwordBibleResourceBox..." )
        if self.parentApp.SwordInterface is None:
            self.parentApp.SwordInterface = SwordInterface() # Load the Sword library
        #tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        swBRB = SwordBibleResourceBox( self, moduleAbbreviation )
        if windowGeometry: halt; swBRB.geometry( windowGeometry )
        swBRB.updateShownBCV( self.parentApp.getVerseKey( swBRB.groupCode ) )
        self.resourceBoxes.append( swBRB )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openSwordBibleResourceBox" )
        self.parentApp.setReadyStatus()
        return swBRB
    # end of BibleResourceCollectionWindow.openSwordBibleResourceBox


    def doOpenInternalBibleResource( self ):
        """
        Open a local Bible (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openInternalBibleResource()") )
            self.parentApp.setDebugText( "doOpenInternalBibleResource..." )
        self.parentApp.setStatus( "doOpenInternalBibleResource..." )
        #requestedFolder = askdirectory()
        openDialog = Directory( initialdir=self.parentApp.lastInternalBibleDir )
        requestedFolder = openDialog.show()
        if requestedFolder:
            self.parentApp.lastInternalBibleDir = requestedFolder
            self.openInternalBibleResourceBox( requestedFolder )
            #self.acceptNewBnCV()
            #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of BibleResourceCollectionWindow.doOpenInternalBibleResource

    def openInternalBibleResourceBox( self, modulePath, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible resource window.

        Returns the new InternalBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openInternalBibleResourceBox()") )
            self.parentApp.setDebugText( "openInternalBibleResourceBox..." )
        #tk.Label( self, text=modulePath ).pack( side=tk.TOP, fill=tk.X )
        iBRB = InternalBibleResourceBox( self, modulePath )
        if windowGeometry: halt; iBRB.geometry( windowGeometry )
        if iBRB.internalBible is None:
            logging.critical( t("Application.openInternalBibleResourceBox: Unable to open resource {}").format( repr(modulePath) ) )
            iBRB.destroy()
            showerror( APP_NAME, _("Sorry, unable to open internal Bible resource") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openInternalBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return None
        else:
            iBRB.updateShownBCV( self.parentApp.getVerseKey( iBRB.groupCode ) )
            self.resourceBoxes.append( iBRB )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openInternalBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return iBRB
    # end of BibleResourceCollectionWindow.openInternalBibleResourceBox


    def openBox( self, boxType, boxSource ):
        """
        (Re)open a text box.
        """
        if boxType == 'DBP': self.openDBPBibleResourceBox( boxSource )
        elif boxType == 'Sword': self.openSwordBibleResourceBox( boxSource )
        elif boxType == 'Internal': self.openInternalBibleResourceBox( boxSource )
        elif BibleOrgSysGlobals.debugFlag: halt
    # end of BibleResourceCollectionWindow.openBox


    def updateShownBCV( self, newReferenceVerseKey ):
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        The new verse key is in the reference versification system.

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceCollectionWindow.updateShownBCV( {}) for".format( newReferenceVerseKey ), self.moduleID )
            #print( "contextViewMode", self.contextViewMode )
            assert( isinstance( newReferenceVerseKey, SimpleVerseKey ) )

        for resourceBox in self.resourceBoxes:
            resourceBox.updateShownBCV( newReferenceVerseKey )

        self.refreshTitle()
    # end of BibleResourceCollectionWindow.updateShownBCV
# end of BibleResourceCollectionWindow class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( t("Running demo...") )

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
# end of BibleResourceCollection.demo


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
# end of BibleResourceCollection.py