#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BibleResourceWindows.py
#
# Bible resource windows for Biblelator Bible display/editing
#
# Copyright (C) 2013-2016 Robert Hunt
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

class BibleBox( ChildBox )
    displayAppendVerse( self, firstFlag, verseKey, verseContextData, lastFlag=True, currentVerse=False )
    getBeforeAndAfterBibleData( self, newVerseKey )

class BibleResourceWindow( ChildWindow, BibleBox )
    __init__( self, parentApp, windowType, moduleID )
    createMenuBar( self )
    changeBibleContextView( self )
    changeBibleGroupCode( self )
    doGotoPreviousBook( self, gotoEnd=False )
    doGotoNextBook( self )
    doGotoPreviousChapter( self, gotoEnd=False )
    doGotoNextChapter( self )
    doGotoPreviousSection( self, gotoEnd=False )
    doGotoNextSection( self )
    doGotoPreviousVerse( self )
    doGotoNextVerse( self )
    doGoForward( self )
    doGoBackward( self )
    doGotoPreviousListItem( self )
    doGotoNextListItem( self )
    doGotoBook( self )
    gotoBCV( self, BBB, C, V )
    getSwordVerseKey( self, verseKey )
    getCachedVerseData( self, verseKey )
    setCurrentVerseKey( self, newVerseKey )
    updateShownBCV( self, newReferenceVerseKey, originator=None )
    doShowInfo( self, event=None )

class SwordBibleResourceWindow( BibleResourceWindow )
    __init__( self, parentApp, moduleAbbreviation )
    refreshTitle( self )
    getContextVerseData( self, verseKey )

class DBPBibleResourceWindow( BibleResourceWindow )
    __init__( self, parentApp, moduleAbbreviation )
    refreshTitle( self )
    getContextVerseData( self, verseKey )

class InternalBibleResourceWindow( BibleResourceWindow )
    __init__( self, parentApp, modulePath )
    refreshTitle( self )
    getContextVerseData( self, verseKey )

demo()
"""

from gettext import gettext as _

LastModifiedDate = '2016-06-07' # by RJH
ShortProgName = "BibleResourceWindows"
ProgName = "Biblelator Bible Resource Windows"
ProgVersion = '0.36'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import sys, logging
from collections import OrderedDict
import tkinter as tk

# Biblelator imports
from BiblelatorGlobals import DEFAULT, BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES
from ChildWindows import ChildBox, ChildWindow
from BiblelatorHelpers import findCurrentSection, handleInternalBibles
from BiblelatorDialogs import showinfo

# BibleOrgSys imports
#if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
from VerseReferences import SimpleVerseKey
#from USFMFile import splitMarkerText
from SwordResources import SwordType
from DigitalBiblePlatform import DBPBible
from UnknownBible import UnknownBible
from BibleOrganizationalSystems import BibleOrganizationalSystem
from InternalBibleInternals import InternalBibleEntryList, InternalBibleEntry


MAX_CACHED_VERSES = 300 # Per Bible resource window



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



class BibleBox( ChildBox ):
    """
    A set of functions that work for any Bible frame or window that has a member: self.textBox
        and uses verseKeys
    """
    def displayAppendVerse( self, firstFlag, verseKey, verseContextData, lastFlag=True, currentVerse=False ):
        """
        Add the requested verse to the end of self.textBox.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.

        Usually called from updateShownBCV from the subclass.
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule:
                print( "displayAppendVerse( {}, {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, lastFlag, currentVerse ) )
            assert isinstance( firstFlag, bool )
            assert isinstance( verseKey, SimpleVerseKey )
            if verseContextData:
                assert isinstance( verseContextData, tuple ) and len(verseContextData)==2 or isinstance( verseContextData, str )
            assert isinstance( lastFlag, bool )
            assert isinstance( currentVerse, bool )

        def insertEnd( ieText, ieTags ):
            """
            Insert the formatted text into the end of the textbox.

            The function mostly exists so we can print the parameters if necessary for debugging.
            """
            if BibleOrgSysGlobals.debugFlag:
                if debuggingThisModule:
                    print( "insertEnd( {!r}, {} )".format( ieText, ieTags ) )
                assert isinstance( ieText, str )
                assert isinstance( ieTags, (str,tuple) )
            self.textBox.insert( tk.END, ieText, ieTags )
        # end of insertEnd

        # Start of main code for displayAppendVerse
        try: cVM = self.contextViewMode
        except AttributeError: cVM = self.parentWindow.contextViewMode
        #fVM = self.formatViewMode

        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("BibleBox.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}").format( firstFlag, verseKey, lastFlag, currentVerse, fVM, cVM ) )
            ##try: print( exp("BibleBox.displayAppendVerse( {}, {}, {}, {} )").format( firstFlag, verseKey, verseContextData, currentVerse ) )
            ##except UnicodeEncodeError: print( exp("BibleBox.displayAppendVerse"), firstFlag, verseKey, currentVerse )

        BBB, C, V = verseKey.getBCV()
        C, V = int(C), int(V)
        #C1 = C2 = int(C); V1 = V2 = int(V)
        #if V1 > 0: V1 -= 1
        #elif C1 > 0:
            #C1 -= 1
            #V1 = self.getNumVerses( BBB, C1 )
        #if V2 < self.getNumVerses( BBB, C2 ): V2 += 1
        #elif C2 < self.getNumChapters( BBB):
            #C2 += 1
            #V2 = 0
        #previousMarkName = 'C{}V{}'.format( C1, V1 )
        currentMarkName = 'C{}V{}'.format( C, V )
        #nextMarkName = 'C{}V{}'.format( C2, V2 )
        #print( "Marks", previousMarkName, currentMarkName, nextMarkName )

        lastCharWasSpace = haveTextFlag = not firstFlag

        if verseContextData is None:
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                print( "  ", exp("displayAppendVerse"), "has no data for", verseKey )
            verseDataList = context = None
        elif isinstance( verseContextData, tuple ):
            assert len(verseContextData) == 2
            verseDataList, context = verseContextData
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #print( "   VerseDataList: {}".format( verseDataList ) )
                #print( "   Context: {}".format( context ) )
        elif isinstance( verseContextData, str ):
            verseDataList, context = verseContextData.split( '\n' ), None
        elif BibleOrgSysGlobals.debugFlag: halt

        # Display the context preceding the first verse
        if firstFlag and context:
            #print( "context", context )
            #print( "  Setting context mark to {}".format( previousMarkName ) )
            #self.textBox.mark_set( previousMarkName, tk.INSERT )
            #self.textBox.mark_gravity( previousMarkName, tk.LEFT )
            insertEnd( "Context:", 'contextHeader' )
            contextString, firstMarker = "", True
            for someMarker in context:
                #print( "  someMarker", someMarker )
                if someMarker != 'chapters':
                    contextString += (' ' if firstMarker else ', ') + someMarker
                    firstMarker = False
            insertEnd( contextString, 'context' )
            haveTextFlag = True

        #print( "  Setting mark to {}".format( currentMarkName ) )
        self.textBox.mark_set( currentMarkName, tk.INSERT )
        self.textBox.mark_gravity( currentMarkName, tk.LEFT )

        if verseDataList is None:
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                print( "  ", exp("BibleBox.displayAppendVerse"), "has no data for", self.moduleID, verseKey )
            #self.textBox.insert( tk.END, '--' )
        else:
            #hadVerseText = False
            endMarkers = []
            lastParagraphMarker = context[-1] if context and context[-1] in BibleOrgSysGlobals.USFMParagraphMarkers \
                                        else 'v~' # If we don't know the format of a verse (or for unformatted Bibles)
            for entry in verseDataList:
                if isinstance( entry, InternalBibleEntry ):
                    marker, cleanText = entry.getMarker(), entry.getCleanText()
                elif isinstance( entry, tuple ):
                    marker, cleanText = entry[0], entry[3]
                elif isinstance( entry, str ):
                    if entry=='': continue
                    entry += '\n'
                    if entry[0]=='\\':
                        marker = ''
                        for char in entry[1:]:
                            if char!='¬' and not char.isalnum(): break
                            marker += char
                        cleanText = entry[len(marker)+1:].lstrip()
                    else:
                        marker, cleanText = None, entry
                elif BibleOrgSysGlobals.debugFlag: halt
                if debuggingThisModule:
                    print( "  displayAppendVerse", lastParagraphMarker, haveTextFlag, marker, repr(cleanText) )

                if self.formatViewMode == 'Unformatted':
                    if marker and marker[0]=='¬': pass # Ignore end markers for now
                    elif marker in ('chapters',): pass # Ignore added markers for now
                    else:
                        #if hadVerseText and marker in ( 's', 's1', 's2', 's3' ):
                            #print( "  Setting s mark to {}".format( nextMarkName ) )
                            #self.textBox.mark_set( nextMarkName, tk.INSERT )
                            #self.textBox.mark_gravity( nextMarkName, tk.LEFT )
                        #print( "  Inserting ({}): {!r}".format( marker, entry ) )
                        self.textBox.insert( tk.END, entry, marker )
                        #hadVerseText = True

                elif self.formatViewMode == DEFAULT:
                    if marker.startswith( '¬' ):
                        if marker != '¬v': endMarkers.append( marker ) # Don't want end-verse markers
                    else: endMarkers = [] # Reset when we have normal markers

                    if marker.startswith( '¬' ): pass # Ignore end markers for now
                    elif marker in ('intro','chapters',): pass # Ignore added markers for now
                    elif marker in ('h','toc1','toc2','toc3','cl¤',): pass # Ignore administrative markers for now
                    elif marker == 'id':
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n\n' )
                        insertEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('ide','rem',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('mt1','mt2','mt3','mt4', 'imt1','imt2','imt3','imt4', 'iot','io1','io2','io3','io4',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('ip','ipi','im','imi','ipq','imq','ipr', 'iq1','iq2','iq3','iq4',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('s1','s2','s3','s4', 'is1','is2','is3','is4', 'ms1','ms2','ms3','ms4', 'cl',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('d','sp',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('r','mr','sr',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in BibleOrgSysGlobals.USFMParagraphMarkers:
                        assert not cleanText # No text expected with these markers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        lastParagraphMarker = marker
                        haveTextFlag = True
                    elif marker in ('b','ib'):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        assert not cleanText # No text expected with this marker
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                    #elif marker in ('m','im'):
                        #self.textBox.insert ( tk.END, '\n' if haveTextFlag else '  ', marker )
                        #if cleanText:
                            #insertEnd( cleanText, '*'+marker if currentVerse else marker )
                            #lastCharWasSpace = False
                            #haveTextFlag = True
                    elif marker == 'p#' and self.boxType=='DBPBibleResourceBox':
                        pass # Just ignore these for now
                    elif marker == 'c': # Don't want to display this (original) c marker
                        #if not firstFlag: haveC = cleanText
                        #else: print( "   Ignore C={}".format( cleanText ) )
                        pass
                    elif marker == 'c#': # Might want to display this (added) c marker
                        if cleanText != verseKey.getBBB():
                            if not lastCharWasSpace: insertEnd( ' ', 'v-' )
                            insertEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                            lastCharWasSpace = False
                    elif marker == 'v':
                        if haveTextFlag:
                            insertEnd( ' ', (lastParagraphMarker,'v-',) if lastParagraphMarker else ('v-',) )
                        insertEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                        insertEnd( '\u2009', (lastParagraphMarker,'v+',) if lastParagraphMarker else ('v+',) ) # narrow space
                        lastCharWasSpace = haveTextFlag = True
                    elif marker in ('v~','p~'):
                        insertEnd( cleanText, '*'+lastParagraphMarker if currentVerse else lastParagraphMarker )
                        haveTextFlag = True
                    else:
                        if BibleOrgSysGlobals.debugFlag:
                            logging.critical( exp("BibleBox.displayAppendVerse: Unknown marker {!r} {!r} from {}").format( marker, cleanText, verseDataList ) )
                        else:
                            logging.critical( exp("BibleBox.displayAppendVerse: Unknown marker {!r} {!r}").format( marker, cleanText ) )
                else:
                    logging.critical( exp("BibleBox.displayAppendVerse: Unknown {!r} format view mode").format( self.formatViewMode ) )
                    if BibleOrgSysGlobals.debugFlag: halt

            try: cVM = self.contextViewMode
            except AttributeError: cVM = self.parentWindow.contextViewMode
            if lastFlag and cVM=='ByVerse' and endMarkers:
                #print( "endMarkers", endMarkers )
                insertEnd( " End context:", 'contextHeader' )
                contextString, firstMarker = "", True
                for someMarker in endMarkers:
                    #print( "  someMarker", someMarker )
                    contextString += (' ' if firstMarker else ', ') + someMarker
                    firstMarker = False
                insertEnd( contextString, 'context' )
    # end of BibleBox.displayAppendVerse


    def getBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("BibleBox.getBeforeAndAfterBibleData( {} )").format( newVerseKey ) )
            assert isinstance( newVerseKey, SimpleVerseKey )

        BBB, C, V = newVerseKey.getBCV()
        intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        prevBBB, prevIntC, prevIntV = BBB, intC, intV
        previousVersesData = []
        for n in range( -self.parentApp.viewVersesBefore, 0 ):
            failed = False
            #print( "  getBeforeAndAfterBibleData here with", n, prevIntC, prevIntV )
            if prevIntV > 0: prevIntV -= 1
            elif prevIntC > 0:
                prevIntC -= 1
                try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                except KeyError:
                    if prevIntC != 0: # we can expect an error for chapter zero
                        logging.critical( exp("BibleBox.getBeforeAndAfterBibleData failed at"), prevBBB, prevIntC )
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
                assert prevBBB and isinstance(prevBBB, str)
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getCachedVerseData( previousVerseKey )
                if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        # Determine the next valid verse numbers
        nextBBB, nextIntC, nextIntV = BBB, intC, intV
        nextVersesData = []
        for n in range( 0, self.parentApp.viewVersesAfter ):
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
    # end of BibleBox.getBeforeAndAfterBibleData
# end of class BibleBox



class BibleResourceWindow( ChildWindow, BibleBox ):
    """
    The superclass must provide a getContextVerseData function.
    """
    def __init__( self, parentApp, windowType, moduleID ):
        if BibleOrgSysGlobals.debugFlag: print( exp("BibleResourceWindow.__init__( {}, {}, {} )").format( parentApp, windowType, moduleID ) )
        self.parentApp, self.windowType, self.moduleID = parentApp, windowType, moduleID

        # Set some dummy values required soon (esp. by refreshTitle)
        self._viewRadioVar, self._groupRadioVar = tk.IntVar(), tk.StringVar()
        self.groupCode = BIBLE_GROUP_CODES[0] # Put into first/default BCV group
        self.contextViewMode = DEFAULT
        self.BCVUpdateType = DEFAULT
        self.currentVerseKey = SimpleVerseKey( 'UNK','1','1' ) # Unknown book

        if self.contextViewMode == DEFAULT:
            self.contextViewMode = 'BeforeAndAfter'
            self.parentApp.viewVersesBefore, self.parentApp.viewVersesAfter = 2, 6
        ChildWindow.__init__( self, self.parentApp, 'BibleResource' )
        BibleBox.__init__( self, self.parentApp )

        # Set-up our standard Bible styles
        for USFMKey, styleDict in self.parentApp.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        # Add our extra specialised styles
        self.textBox.tag_configure( 'contextHeader', background='pink', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'context', background='pink', font='helvetica 6' )
        #else:
            #self.textBox.tag_configure( 'verseNumberFormat', foreground='blue', font='helvetica 8', relief=tk.RAISED, offset='3' )
            #self.textBox.tag_configure( 'versePreSpaceFormat', background='pink', font='helvetica 8' )
            #self.textBox.tag_configure( 'versePostSpaceFormat', background='pink', font='helvetica 4' )
            #self.textBox.tag_configure( 'verseTextFormat', font='sil-doulos 12' )
            #self.textBox.tag_configure( 'otherVerseTextFormat', font='sil-doulos 9' )
            ##self.textBox.tag_configure( 'verseText', background='yellow', font='helvetica 14 bold', relief=tk.RAISED )
            ##"background", "bgstipple", "borderwidth", "elide", "fgstipple", "font", "foreground", "justify", "lmargin1",
            ##"lmargin2", "offset", "overstrike", "relief", "rmargin", "spacing1", "spacing2", "spacing3",
            ##"tabs", "tabstyle", "underline", and "wrap".

        # Set-up our Bible system and our callables
        self.BibleOrganisationalSystem = BibleOrganizationalSystem( 'GENERIC-KJV-81-ENG' ) # temp
        self.getNumChapters = self.BibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda b,c: 99 if b=='UNK' or c=='0' or c==0 else self.BibleOrganisationalSystem.getNumVerses( b, c )
        self.isValidBCVRef = self.BibleOrganisationalSystem.isValidBCVRef
        self.getFirstBookCode = self.BibleOrganisationalSystem.getFirstBookCode
        self.getPreviousBookCode = self.BibleOrganisationalSystem.getPreviousBookCode
        self.getNextBookCode = self.BibleOrganisationalSystem.getNextBookCode
        self.getBBBFromText = self.BibleOrganisationalSystem.getBBBFromText
        self.getBookName = self.BibleOrganisationalSystem.getBookName
        self.getBookList = self.BibleOrganisationalSystem.getBookList
        self.maxChaptersThisBook, self.maxVersesThisChapter = 150, 150 # temp

        self.BibleFindOptionsDict = {}
        self.verseCache = OrderedDict()

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceWindow.__init__ finished.") )
    # end of BibleResourceWindow.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleResourceWindow.createMenuBar()") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_command( label=_('Open…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu )
        #subfileMenuImport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Import'), underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu )
        #subfileMenuExport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label=_('HTML'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Export'), underline=0, menu=subfileMenuExport )
        #fileMenu.add_separator()
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] ) # close this window

        editMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=self.parentApp.keyBindingDict[_('Line')][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doWindowRefind, accelerator=self.parentApp.keyBindingDict[_('Refind')][0] )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
        gotoMenu.add_command( label=_('Previous book'), underline=-1, command=self.doGotoPreviousBook )
        gotoMenu.add_command( label=_('Next book'), underline=-1, command=self.doGotoNextBook )
        gotoMenu.add_command( label=_('Previous chapter'), underline=-1, command=self.doGotoPreviousChapter )
        gotoMenu.add_command( label=_('Next chapter'), underline=-1, command=self.doGotoNextChapter )
        gotoMenu.add_command( label=_('Previous section'), underline=-1, command=self.doGotoPreviousSection )
        gotoMenu.add_command( label=_('Next section'), underline=-1, command=self.doGotoNextSection )
        gotoMenu.add_command( label=_('Previous verse'), underline=-1, command=self.doGotoPreviousVerse )
        gotoMenu.add_command( label=_('Next verse'), underline=-1, command=self.doGotoNextVerse )
        gotoMenu.add_separator()
        gotoMenu.add_command( label=_('Forward'), underline=0, command=self.doGoForward )
        gotoMenu.add_command( label=_('Backward'), underline=0, command=self.doGoBackward )
        gotoMenu.add_separator()
        gotoMenu.add_command( label=_('Previous list item'), underline=0, state=tk.DISABLED, command=self.doGotoPreviousListItem )
        gotoMenu.add_command( label=_('Next list item'), underline=0, state=tk.DISABLED, command=self.doGotoNextListItem )
        gotoMenu.add_separator()
        gotoMenu.add_command( label=_('Book'), underline=0, command=self.doGotoBook )
        gotoMenu.add_separator()
        self._groupRadioVar.set( self.groupCode )
        gotoMenu.add_radiobutton( label=_('Group A'), underline=6, value='A', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group B'), underline=6, value='B', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group C'), underline=6, value='C', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group D'), underline=6, value='D', variable=self._groupRadioVar, command=self.changeBibleGroupCode )

        self.viewMenu = tk.Menu( self.menubar, tearoff=False ) # Save this reference so we can disable entries later
        self.menubar.add_cascade( menu=self.viewMenu, label=_('View'), underline=0 )
        if   self.contextViewMode == 'BeforeAndAfter': self._viewRadioVar.set( 1 )
        elif self.contextViewMode == 'BySection': self._viewRadioVar.set( 2 )
        elif self.contextViewMode == 'ByVerse': self._viewRadioVar.set( 3 )
        elif self.contextViewMode == 'ByBook': self._viewRadioVar.set( 4 )
        elif self.contextViewMode == 'ByChapter': self._viewRadioVar.set( 5 )
        else: print( self.contextViewMode ); halt

        self.viewMenu.add_radiobutton( label=_('Before and after…'), underline=7, value=1, variable=self._viewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('One section'), underline=4, value=2, variable=self._viewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('Single verse'), underline=7, value=3, variable=self._viewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('Whole book'), underline=6, value=4, variable=self._viewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('Whole chapter'), underline=6, value=5, variable=self._viewRadioVar, command=self.changeBibleContextView )

        if 'DBP' in self.windowType: # disable excessive online use
            self.viewMenu.entryconfigure( 'Whole book', state=tk.DISABLED )
            self.viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label=_('Tools'), underline=0 )
        toolsMenu.add_command( label=_('Options…'), underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label=_('Window'), underline=0 )
        windowMenu.add_command( label=_('Bring in'), underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=self.parentApp.keyBindingDict[_('ShowMain')][0] )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label=_('Help') )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=self.parentApp.keyBindingDict[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=self.parentApp.keyBindingDict[_('About')][0] )
    # end of BibleResourceWindow.createMenuBar


    def changeBibleContextView( self ):
        """
        Called when  a Bible context view is changed from the menus/GUI.
        """
        currentViewNumber = self._viewRadioVar.get()

        if BibleOrgSysGlobals.debugFlag:
            print( exp("BibleResourceWindow.changeBibleContextView( {!r} ) from {!r}").format( currentViewNumber, self.contextViewMode ) )
            assert currentViewNumber in range( 1, len(BIBLE_CONTEXT_VIEW_MODES)+1 )

        if 'Editor' in self.genericWindowType and self.saveChangesAutomatically and self.modified():
            self.doSave( 'Auto from change contextView' )

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
            #if   self.groupCode == 'A': windowVerseKey = self.parentApp.GroupA_VerseKey
            #elif self.groupCode == 'B': windowVerseKey = self.parentApp.GroupB_VerseKey
            #elif self.groupCode == 'C': windowVerseKey = self.parentApp.GroupC_VerseKey
            #elif self.groupCode == 'D': windowVerseKey = self.parentApp.GroupD_VerseKey
            #self.updateShownBCV( windowVerseKey )
            self.updateShownBCV( self.currentVerseKey )
    # end of BibleResourceWindow.changeBibleContextView


    def changeBibleGroupCode( self ):
        """
        Called when  a Bible group code is changed from the menus/GUI.
        """
        previousGroupCode = self.groupCode
        newGroupCode = self._groupRadioVar.get()

        if BibleOrgSysGlobals.debugFlag:
            print( exp("changeBibleGroupCode( {!r} ) from {!r}").format( newGroupCode, previousGroupCode ) )
            assert newGroupCode in BIBLE_GROUP_CODES
            assert 'Bible' in self.genericWindowType

        if 'Bible' in self.genericWindowType: # do we really need this test?
            self.groupCode = newGroupCode
        else: halt # window type view mode not handled yet
        if self.groupCode != previousGroupCode: # we need to update our view
            if   self.groupCode == 'A': windowVerseKey = self.parentApp.GroupA_VerseKey
            elif self.groupCode == 'B': windowVerseKey = self.parentApp.GroupB_VerseKey
            elif self.groupCode == 'C': windowVerseKey = self.parentApp.GroupC_VerseKey
            elif self.groupCode == 'D': windowVerseKey = self.parentApp.GroupD_VerseKey
            self.updateShownBCV( windowVerseKey )
    # end of BibleResourceWindow.changeBibleGroupCode


    def doGotoPreviousBook( self, gotoEnd=False ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceWindow.doGotoPreviousBook()").format( gotoEnd ) )

        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousBook( {} ) from {} {}:{}").format( gotoEnd, BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousBook…" )
        newBBB = self.getPreviousBookCode( BBB )
        if newBBB is None: self.gotoBCV( BBB, '0', '0' )
        else:
            self.maxChaptersThisBook = self.getNumChapters( newBBB )
            self.maxVersesThisChapter = self.getNumVerses( newBBB, self.maxChaptersThisBook )
            if gotoEnd: self.gotoBCV( newBBB, self.maxChaptersThisBook, self.maxVersesThisChapter )
            else: self.gotoBCV( newBBB, '0', '0' ) # go to the beginning
    # end of BibleResourceWindow.doGotoPreviousBook


    def doGotoNextBook( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceWindow.doGotoNextBook()") )

        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextBook() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextBook…" )
        newBBB = self.getNextBookCode( BBB )
        if newBBB is None: pass # stay just where we are
        else:
            self.maxChaptersThisBook = self.getNumChapters( newBBB )
            self.maxVersesThisChapter = self.getNumVerses( newBBB, '0' )
            self.gotoBCV( newBBB, '0', '0' ) # go to the beginning of the book
    # end of BibleResourceWindow.doGotoNextBook


    def doGotoPreviousChapter( self, gotoEnd=False ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceWindow.doGotoPreviousChapter()") )

        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousChapter() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousChapter…" )
        intC, intV = int( C ), int( V )
        if intC > 0: self.gotoBCV( BBB, intC-1, self.getNumVerses( BBB, intC-1 ) if gotoEnd else '0' )
        else: self.doGotoPreviousBook( gotoEnd=True )
    # end of BibleResourceWindow.doGotoPreviousChapter


    def doGotoNextChapter( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceWindow.doGotoNextChapter()") )

        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextChapter() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextChapter…" )
        intC = int( C )
        if intC < self.maxChaptersThisBook: self.gotoBCV( BBB, intC+1, '0' )
        else: self.doGotoNextBook()
    # end of BibleResourceWindow.doGotoNextChapter


    def doGotoPreviousSection( self, gotoEnd=False ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceWindow.doGotoPreviousSection()") )

        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousSection() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousSection…" )
        # First the start of the current section
        sectionStart1, sectionEnd1 = findCurrentSection( self.currentVerseKey, self.getNumChapters, self.getNumVerses, self.getCachedVerseData )
        print( "section1 Start/End", sectionStart1, sectionEnd1 )
        intC1, intV1 = sectionStart1.getChapterNumberInt(), sectionStart1.getVerseNumberInt()
        # Go back one verse from the start of the current section
        if intV1 == 0:
            if intC1 == 0:
                self.doGotoPreviousBook( gotoEnd=True )
                return
            else:
                intC1 -= 1
                intV1 = self.getNumVerses( BBB, C1)
        else: intV1 -= 1
        # Now find the start of this previous section
        sectionStart2, sectionEnd2 = findCurrentSection( SimpleVerseKey( BBB, intC1, intV1), self.getNumChapters, self.getNumVerses, self.getCachedVerseData )
        print( "section2 Start/End", sectionStart2, sectionEnd2 )
        BBB2, C2, V2 = sectionStart2.getBCV()
        self.gotoBCV( BBB2, C2, V2 )
    # end of BibleResourceWindow.doGotoPreviousSection


    def doGotoNextSection( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceWindow.doGotoNextSection()") )

        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextSection() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextSection…" )
        # Find the end of the current section (which is the first verse of the next section)
        sectionStart, sectionEnd = findCurrentSection( self.currentVerseKey, self.getNumChapters, self.getNumVerses, self.getCachedVerseData )
        print( "section Start/End", sectionStart, sectionEnd )
        intC2, intV2 = sectionEnd.getChapterNumberInt(), sectionEnd.getVerseNumberInt()
        if intC2 < self.maxChaptersThisBook \
        or (intC2==self.maxChaptersThisBook and intV2< self.getNumVerses( BBB, intC2) ):
            self.gotoBCV( BBB, intC2, intV2 )
        else: self.doGotoNextBook()
    # end of BibleResourceWindow.doGotoNextSection


    def doGotoPreviousVerse( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousVerse() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousVerse…" )
        intC, intV = int( C ), int( V )
        if intV > 0: self.gotoBCV( BBB, C, intV-1 )
        elif intC > 0: self.doGotoPreviousChapter( gotoEnd=True )
        else: self.doGotoPreviousBook( gotoEnd=True )
    # end of BibleResourceWindow.doGotoPreviousVerse


    def doGotoNextVerse( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextVerse() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextVerse…" )
        intV = int( V )
        if intV < self.maxVersesThisChapter: self.gotoBCV( BBB, C, intV+1 )
        else: self.doGotoNextChapter()
    # end of BibleResourceWindow.doGotoNextVerse


    def doGoForward( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGoForward() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGoForward…" )
        self.notWrittenYet()
    # end of BibleResourceWindow.doGoForward


    def doGoBackward( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGoBackward() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGoBackward…" )
        self.notWrittenYet()
    # end of BibleResourceWindow.doGoBackward


    def doGotoPreviousListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousListItem() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoPreviousListItem…" )
        self.notWrittenYet()
    # end of BibleResourceWindow.doGotoPreviousListItem


    def doGotoNextListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextListItem() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoNextListItem…" )
        self.notWrittenYet()
    # end of BibleResourceWindow.doGotoNextListItem


    def doGotoBook( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoBook() from {} {}:{}").format( BBB, C, V ) )
            self.parentApp.setDebugText( "BRW doGotoBook…" )
        self.notWrittenYet()
    # end of BibleResourceWindow.doGotoBook


    def gotoBCV( self, BBB, C, V ):
        """

        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("gotoBCV( {} {}:{} from {} )").format( BBB, C, V, self.currentVerseKey ) )
        # We really need to convert versification systems here
        adjBBB, adjC, adjV, adjS = self.BibleOrganisationalSystem.convertToReferenceVersification( BBB, C, V )
        self.parentApp.gotoGroupBCV( self.groupCode, adjBBB, adjC, adjV ) # then the App will update me by calling updateShownBCV
    # end of BibleResourceWindow.gotoBCV


    def getSwordVerseKey( self, verseKey ):
        """
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("getSwordVerseKey( {} )").format( verseKey ) )

        BBB, C, V = verseKey.getBCV()
        return self.parentApp.SwordInterface.makeKey( BBB, C, V )
    # end of BibleResourceWindow.getSwordVerseKey


    def getCachedVerseData( self, verseKey ):
        """
        Checks to see if the requested verse is in our cache,
            otherwise calls getContextVerseData (from the superclass) to fetch it.

        The cache keeps the newest or most recently used entries at the end.
        When it gets too large, it drops the first entry.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("getCachedVerseData( {} )").format( verseKey ) )

        verseKeyHash = verseKey.makeHash()
        if verseKeyHash in self.verseCache:
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  " + exp("Retrieved from BibleResourceWindow cache") )
            self.verseCache.move_to_end( verseKeyHash )
            return self.verseCache[verseKeyHash]
        verseData = self.getContextVerseData( verseKey )
        self.verseCache[verseKeyHash] = verseData
        if len(self.verseCache) > MAX_CACHED_VERSES:
            #print( "Removing oldest cached entry", len(self.verseCache) )
            self.verseCache.popitem( last=False )
        return verseData
    # end of BibleResourceWindow.getCachedVerseData


    def setCurrentVerseKey( self, newVerseKey ):
        """
        Called to set the current verse key.

        Note that newVerseKey can be None.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setCurrentVerseKey( {} )").format( newVerseKey ) )
            self.parentApp.setDebugText( "BRW setCurrentVerseKey…" )

        if newVerseKey is None:
            self.currentVerseKey = None
            self.maxChaptersThisBook = self.maxVersesThisChapter = 0
            return

        # If we get this far, it must be a real verse key
        assert isinstance( newVerseKey, SimpleVerseKey )
        self.currentVerseKey = newVerseKey

        BBB = self.currentVerseKey.getBBB()
        self.maxChaptersThisBook = self.getNumChapters( BBB )
        self.maxVersesThisChapter = self.getNumVerses( BBB, self.currentVerseKey.getChapterNumber() )
    # end of BibleResourceWindow.setCurrentVerseKey


    def updateShownBCV( self, newReferenceVerseKey, originator=None ):
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        The new verse key is in the reference versification system.

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceWindow.updateShownBCV( {}, {} ) for".format( newReferenceVerseKey, originator ), self.moduleID )
            #print( "contextViewMode", self.contextViewMode )
            assert isinstance( newReferenceVerseKey, SimpleVerseKey )

        refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
        BBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
        newVerseKey = SimpleVerseKey( BBB, C, V, S )

        self.setCurrentVerseKey( newVerseKey )
        self.clearText() # Leaves the text box enabled
        startingFlag = True

        # Safety-check in case they edited the settings file
        if 'DBP' in self.windowType and self.contextViewMode in ('ByBook','ByChapter',):
            print( exp("updateShownBCV: Safety-check converted {!r} contextViewMode for DBP").format( self.contextViewMode ) )
            self._viewRadioVar.set( 3 ) # ByVerse
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
            BBB, intC, intV = newVerseKey.getBBB(), newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            sectionStart, sectionEnd = findCurrentSection( newVerseKey, self.getNumChapters, self.getNumVerses, self.getCachedVerseData )
            intC1, intV1 = sectionStart.getChapterNumberInt(), sectionStart.getVerseNumberInt()
            intC2, intV2 = sectionEnd.getChapterNumberInt(), sectionEnd.getVerseNumberInt()
            for thisC in range( intC1, intC2+1 ):
                try: numVerses = self.getNumVerses( BBB, thisC )
                except KeyError: numVerses = 0
                startV, endV = 0, numVerses
                if thisC == intC1: startV = intV1
                if thisC == intC2: endV = intV2
                for thisV in range( startV, endV+1 ):
                    thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    thisVerseData = self.getCachedVerseData( thisVerseKey )
                    self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            currentVerse=thisC==intC and thisV==intV )
                    startingFlag = False

        elif self.contextViewMode == 'ByBook':
            BBB, C, V = newVerseKey.getBCV()
            intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            for thisC in range( 0, self.getNumChapters( BBB ) + 1 ):
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
            for thisV in range( 0, numVerses + 1 ):
                thisVerseKey = SimpleVerseKey( BBB, C, thisV )
                thisVerseData = self.getCachedVerseData( thisVerseKey )
                self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData, currentVerse=thisV==intV )
                startingFlag = False

        else:
            logging.critical( exp("BibleResourceWindow.updateShownBCV: Bad context view mode {}").format( self.contextViewMode ) )
            if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode

        self.textBox['state'] = tk.DISABLED # Don't allow editing

        # Make sure we can see what we're supposed to be looking at
        desiredMark = 'C{}V{}'.format( newVerseKey.getChapterNumber(), newVerseKey.getVerseNumber() )
        try: self.textBox.see( desiredMark )
        except tk.TclError: print( exp("BibleResourceWindow.updateShownBCV couldn't find {!r}").format( desiredMark ) )
        self.lastCVMark = desiredMark

        self.refreshTitle()
    # end of BibleResourceWindow.updateShownBCV
# end of BibleResourceWindow class



class SwordBibleResourceWindow( BibleResourceWindow ):
    """
    """
    def __init__( self, parentApp, moduleAbbreviation ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: print( "SwordBibleResourceWindow.__init__( {}, {} )".format( parentApp, moduleAbbreviation ) )
        self.parentApp, self.moduleAbbreviation = parentApp, moduleAbbreviation
        BibleResourceWindow.__init__( self, self.parentApp, 'SwordBibleResourceWindow', self.moduleAbbreviation )
        #self.windowType = 'SwordBibleResourceWindow'

        #self.SwordModule = None # Loaded later in self.getBeforeAndAfterBibleData()
        self.SwordModule = self.parentApp.SwordInterface.getModule( self.moduleAbbreviation )
        if self.SwordModule is None:
            logging.error( exp("SwordBibleResourceWindow.__init__ Unable to open Sword module: {}").format( self.moduleAbbreviation ) )
            self.SwordModule = None
    # end of SwordBibleResourceWindow.__init__


    def refreshTitle( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("SwordBibleResourceWindow.refreshTitle()") )

        self.title( "[{}] {} ({}) {} {}:{} [{}]".format( self.groupCode,
                                    self.moduleAbbreviation, 'Sw' if SwordType=="CrosswireLibrary" else 'SwM',
                                    self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber(),
                                    self.contextViewMode ) )
    # end if SwordBibleResourceWindow.refreshTitle


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("SwordBibleResourceWindow.getContextVerseData( {} )").format( verseKey ) )
        if self.SwordModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                SwordKey = self.getSwordVerseKey( verseKey )
                rawInternalBibleContextData = self.parentApp.SwordInterface.getContextVerseData( self.SwordModule, SwordKey )
                if rawInternalBibleContextData is None: return '', ''
                rawInternalBibleData, context = rawInternalBibleContextData
                # Clean up the data -- not sure that it should be done here! ....... XXXXXXXXXXXXXXXXXXX
                #from InternalBibleInternals import InternalBibleEntryList, InternalBibleEntry
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
                return adjustedInternalBibleData, context
    # end of SwordBibleResourceWindow.getContextVerseData


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("SwordBibleResourceWindow.doShowInfo( {} )").format( event ) )

        infoString = 'SwordBibleResourceWindow:\n' \
                 + '  Module:\t\t{}\n'.format( self.moduleAbbreviation ) \
                 + '  Type:\t\t{}\n'.format( '' if self.SwordModule is None else self.SwordModule.getType() ) \
                 + '  Format:\t\t{}\n'.format( '' if self.SwordModule is None else self.SwordModule.getMarkup() ) \
                 + '  Encoding:\t{}'.format( '' if self.SwordModule is None else self.SwordModule.getEncoding() )
        showinfo( self, 'Window Information', infoString )
    # end of SwordBibleResourceWindow.doShowInfo
# end of SwordBibleResourceWindow class



class DBPBibleResourceWindow( BibleResourceWindow ):
    """
    """
    def __init__( self, parentApp, moduleAbbreviation ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "DBPBibleResourceWindow.__init__( {}, {} )".format( parentApp, moduleAbbreviation ) )
            assert moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6
        self.parentApp, self.moduleAbbreviation = parentApp, moduleAbbreviation

        self.DBPModule = None # (for refreshTitle called from the base class)
        BibleResourceWindow.__init__( self, self.parentApp, 'DBPBibleResourceWindow', self.moduleAbbreviation )
        #self.windowType = 'DBPBibleResourceWindow'

        # Disable excessive online use
        self.viewMenu.entryconfigure( 'Whole book', state=tk.DISABLED )
        self.viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        try: self.DBPModule = DBPBible( self.moduleAbbreviation )
        except FileNotFoundError:
            logging.error( exp("DBPBibleResourceWindow.__init__ Unable to find a key to connect to Digital Bible Platform") )
            self.DBPModule = None
        except ConnectionError:
            logging.error( exp("DBPBibleResourceWindow.__init__ Unable to connect to Digital Bible Platform") )
            self.DBPModule = None
    # end of DBPBibleResourceWindow.__init__


    def refreshTitle( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("DBPBibleResourceWindow.refreshTitle()") )

        self.title( "[{}] {}.{}{} {} {}:{} [{}]".format( self.groupCode,
                                        self.moduleAbbreviation[:3], self.moduleAbbreviation[3:],
                                        ' (online)' if self.DBPModule else ' (offline)',
                                        self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber(),
                                        self.contextViewMode ) )
    # end if DBPBibleResourceWindow.refreshTitle


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("DBPBibleResourceWindow.getContextVerseData( {} )").format( verseKey ) )

        if self.DBPModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                return self.DBPModule.getContextVerseData( verseKey )
    # end of DBPBibleResourceWindow.getContextVerseData


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("DBPBibleResourceWindow.doShowInfo( {} )").format( event ) )

        infoString = 'DBPBibleResourceWindow:\n' \
                 + '  Name:\t{}'.format( self.moduleAbbreviation )
        showinfo( self, 'Window Information', infoString )
    # end of DBPBibleResourceWindow.doShowInfo
# end of DBPBibleResourceWindow class



class InternalBibleResourceWindow( BibleResourceWindow ):
    """
    """
    def __init__( self, parentApp, modulePath ):
        """
        Given a folder, try to open an UnknownBible.
        If successful, set self.internalBible to point to the loaded Bible.
        """
        if BibleOrgSysGlobals.debugFlag: print( "InternalBibleResourceWindow.__init__( {}, {} )".format( parentApp, modulePath ) )
        self.parentApp, self.modulePath = parentApp, modulePath

        self.internalBible = None # (for refreshTitle called from the base class)
        BibleResourceWindow.__init__( self, self.parentApp, 'InternalBibleResourceWindow', self.modulePath )
        #self.windowType = 'InternalBibleResourceWindow'

        try: self.UnknownBible = UnknownBible( self.modulePath )
        except FileNotFoundError:
            logging.error( exp("InternalBibleResourceWindow.__init__ Unable to find module path: {!r}").format( self.modulePath ) )
            self.UnknownBible = None
        if self.UnknownBible:
            result = self.UnknownBible.search( autoLoadAlways=True )
            if isinstance( result, str ):
                print( "Unknown Bible returned: {!r}".format( result ) )
                self.internalBible = None
            else:
                self.internalBible = handleInternalBibles( self.parentApp, result, self )
        if self.internalBible is not None: # Define which functions we use by default
            self.getNumVerses = self.internalBible.getNumVerses
            self.getNumChapters = self.internalBible.getNumChapters
    # end of InternalBibleResourceWindow.__init__


    def refreshTitle( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("InternalBibleResourceWindow.refreshTitle()") )

        self.title( "[{}] {} (InternalBible){} {} {}:{} [{}]".format( self.groupCode,
                        self.modulePath if self.internalBible is None else self.internalBible.name,
                        ' NOT FOUND' if self.internalBible is None else '',
                        self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber(),
                        self.contextViewMode ) )
    # end if InternalBibleResourceWindow.refreshTitle


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("InternalBibleResourceWindow.getContextVerseData( {} )").format( verseKey ) )
        if self.internalBible is not None:
            try: return self.internalBible.getContextVerseData( verseKey )
            except KeyError:
                if verseKey.getChapterNumber() != '0':
                    logging.critical( exp("InternalBibleResourceWindow.getContextVerseData for {} {} got a KeyError!") \
                                                                .format( self.windowType, verseKey ) )
    # end of InternalBibleResourceWindow.getContextVerseData


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("InternalBibleResourceWindow.doShowInfo( {} )").format( event ) )

        infoString = 'InternalBibleResourceWindow:\n' \
                 + '  Name:\t{}\n'.format( self.modulePath if self.internalBible is None else self.internalBible.name ) \
                 + '  Type:\t{}\n'.format( self.modulePath if self.internalBible is None else self.internalBible.objectTypeString ) \
                 + '  Path:\t{}'.format( self.modulePath )
        showinfo( self, 'Window Information', infoString )
    # end of InternalBibleResourceWindow.doShowInfo
# end of InternalBibleResourceWindow class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo…") )

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
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    if 'win' in sys.platform: # Convert stdout so we don't get zillions of UnicodeEncodeErrors
        from io import TextIOWrapper
        sys.stdout = TextIOWrapper( sys.stdout.detach(), sys.stdout.encoding, 'namereplace' if sys.version_info >= (3,5) else 'backslashreplace' )

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BibleResourceWindows.py