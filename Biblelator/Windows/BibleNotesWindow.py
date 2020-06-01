#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BibleNotesWindow.py
#
# Bible resource windows for Biblelator Bible display/editing
#
# Copyright (C) 2020 Robert Hunt
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
Windows and frames to allow display and manipulation of
    (non-editable) Bible resource windows.

    class BibleNotesWindowAddon( BibleResourceWindowAddon )
                                            --used by BibleNotesWindow, HebrewBibleResourceWindow, USFMEditWindow
        __init__( self, modulePath, defaultContextViewMode=BIBLE_CONTEXT_VIEW_MODES[0], defaultFormatViewMode=BIBLE_FORMAT_VIEW_MODES[0] )
        #createMenuBar( self )
        refreshTitle( self )
        createContextMenu( self )
        getContextVerseData( self, verseKey )
        doShowInfo( self, event=None )
        _prepareForExports( self )
        doMostExports( self )
        doPhotoBibleExport( self )
        doODFsExport( self )
        doPDFsExport( self )
        doAllExports( self )
        _doneExports( self )
        doCheckProject( self )
        #doHelp( self, event=None )
        #doAbout( self, event=None )
        #doClose( self, event=None )

    class BibleNotesWindow( ChildWindow, BibleNotesWindowAddon )
                                            -- used by the main app
        __init__( self, modulePath, defaultContextViewMode=BIBLE_CONTEXT_VIEW_MODES[0], defaultFormatViewMode=BIBLE_FORMAT_VIEW_MODES[0] )
        #createMenuBar( self )
        #refreshTitle( self )
        #createContextMenu( self )
        #getContextVerseData( self, verseKey )
        #doShowInfo( self, event=None )
        #_prepareForExports( self )
        #doMostExports( self )
        #doPhotoBibleExport( self )
        #doODFsExport( self )
        #doPDFsExport( self )
        #doAllExports( self )
        #_doneExports( self )
        #doCheckProject( self )
        #doHelp( self, event=None )
        #doAbout( self, event=None )
        #doClose( self, event=None )

    briefDemo()
    fullDemo()
"""
from gettext import gettext as _
import os
import logging
from collections import OrderedDict
import tkinter as tk

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint
from BibleOrgSys.Bible import Bible
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Formats.uWNotesBible import uWNotesBible
from BibleOrgSys.UnknownBible import UnknownBible
from BibleOrgSys.Reference.BibleOrganisationalSystems import BibleOrganisationalSystem
from BibleOrgSys.Internals.InternalBibleInternals import InternalBibleEntryList, InternalBibleEntry
from BibleOrgSys.BibleWriter import setDefaultControlFolderpath
from BibleOrgSys.Formats.PickledBible import ZIPPED_PICKLE_FILENAME_END

# Biblelator imports
if __name__ == '__main__':
    import sys
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator import BiblelatorGlobals
from Biblelator.BiblelatorGlobals import APP_NAME, \
                        DEFAULT, tkBREAK, MAX_PSEUDOVERSES, errorBeep, \
                        BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, \
                        MAXIMUM_LARGE_RESOURCE_SIZE, parseWindowSize
from Biblelator.Windows.ChildWindows import ChildWindow, BibleWindowAddon, HTMLWindow
from Biblelator.Windows.BibleResourceWindows import BibleResourceWindowAddon
from Biblelator.Windows.TextBoxes import BibleBoxAddon, HebrewInterlinearBibleBoxAddon
from Biblelator.Helpers.BiblelatorHelpers import findCurrentSection, handleInternalBibles
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showInfo, showError
from Biblelator.Dialogs.BiblelatorDialogs import GetBibleBookRangeDialog


LAST_MODIFIED_DATE = '2020-05-13' # by RJH
SHORT_PROGRAM_NAME = "BibleNotesWindow"
PROGRAM_NAME = "Biblelator Bible Notes Resource Window"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = 99


MAX_CACHED_VERSES = 300 # Per Bible resource window



class BibleNotesWindowAddon( BibleResourceWindowAddon ):
    """
    A window displaying one internal (on-disk) Bible.
    """
    def __init__( self, folderpath ):
        """
        Given a folder, try to open an UnknownBible.
        If successful, set self.internalBible to point to the loaded Bible.
        """
        vPrint( 'Never', debuggingThisModule, f"BibleNotesWindowAddon.__init__( fp={folderpath} )…" )
        self.folderpath = folderpath

        #self.internalBible = None # (for refreshTitle called from the base class)
        BibleResourceWindowAddon.__init__( self, 'BibleNotesWindow', self.folderpath, defaultContextViewMode='ByVerse' )

        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.__init__ finished.") )
    # end of BibleNotesWindowAddon.__init__


    def createMenuBar( self ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.createMenuBar()…") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

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
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] ) # close this window

        editMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Line')][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Refind')][0] )

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
        self._groupRadioVar.set( self._groupCode )
        gotoMenu.add_radiobutton( label=_('Group A'), underline=6, value='A', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group B'), underline=6, value='B', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group C'), underline=6, value='C', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group D'), underline=6, value='D', variable=self._groupRadioVar, command=self.changeBibleGroupCode )

        self.viewMenu = tk.Menu( self.menubar, tearoff=False ) # Save this reference so we can disable entries later
        self.menubar.add_cascade( menu=self.viewMenu, label=_('View'), underline=0 )
        self.viewMenu.add_radiobutton( label=_('Before and after…'), underline=7, value=1, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('One section'), underline=4, value=2, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('Single verse'), underline=7, value=3, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('Whole book'), underline=6, value=4, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('Whole chapter'), underline=6, value=5, variable=self._contextViewRadioVar, command=self.changeBibleContextView )

        self.viewMenu.add_separator()
        self.viewMenu.add_radiobutton( label=_('Formatted'), underline=0, value=1, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )
        self.viewMenu.add_radiobutton( label=_('Unformatted'), underline=0, value=2, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )

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
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('ShowMain')][0] )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label=_('Help') )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('About')][0] )
    # end of BibleNotesWindowAddon.createMenuBar


    def refreshTitle( self ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.refreshTitle()…") )

        self.title( "[{}] {} (InternalBible){} {} {}:{} [{}]".format( self._groupCode,
                        self.modulePath if self.internalBible is None else self.internalBible.getAName(),
                        ' NOT FOUND' if self.internalBible is None else '',
                        self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber(),
                        self._contextViewMode ) )
    # end if BibleNotesWindowAddon.refreshTitle


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.createContextMenu()…") )

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Bible Find…'), underline=6, command=self.doBibleFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find in window…'), underline=8, command=self.doBoxFind )#, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close window'), underline=1, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()

        self.BibleFindOptionsDict, self.BibleReplaceOptionsDict = {}, {}
    # end of BibleNotesWindowAddon.createContextMenu


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.getContextVerseData( {} )").format( verseKey ) )

        if self.internalBible is not None:
            try:
                result = self.internalBible.getContextVerseData( verseKey )
                print( "result", result )
                return result
            except KeyError: # Could be after a verse-bridge ???
                if verseKey.getChapterNumber() != '0':
                    logging.error( _("BibleNotesWindowAddon.getContextVerseData for {} {} got a KeyError") \
                                                                .format( self.windowType, verseKey ) )
    # end of BibleNotesWindowAddon.getContextVerseData


    def displayAppendVerse( self, firstFlag:bool, verseKey, verseContextData, lastFlag:bool=True, currentVerseFlag:bool=False, substituteTrailingSpaces:bool=False, substituteMultipleSpaces:bool=False ) -> None:
        """
        Add the requested note(s) to the end of self.textBox.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.

        Usually called from updateShownBCV from the subclass.
        Note that it's used in both formatted and unformatted (even edit) windows.
        """
        vPrint( 'Quiet', debuggingThisModule, "displayAppendVerse( {}, {}, {}, {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, substituteTrailingSpaces, substituteMultipleSpaces ) )
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
            assert isinstance( firstFlag, bool )
            assert isinstance( verseKey, SimpleVerseKey )
            if verseContextData:
                assert isinstance( verseContextData, tuple ) and len(verseContextData)==2 or isinstance( verseContextData, str )
            assert isinstance( lastFlag, bool )
            assert isinstance( currentVerseFlag, bool )

        def insertAtEnd( ieText:str, ieTags ) -> None:
            """
            Insert the formatted text into the end of the textbox.

            The function mostly exists so we can print the parameters if necessary for debugging.
            """
            if BibleOrgSysGlobals.debugFlag:
                if debuggingThisModule:
                    vPrint( 'Quiet', debuggingThisModule, "insertAtEnd( {!r}, {} )".format( ieText, ieTags ) )
                assert isinstance( ieText, str )
                assert isinstance( ieTags, (str,tuple) )
                # assert TRAILING_SPACE_SUBSTITUTE not in ieText
                # assert MULTIPLE_SPACE_SUBSTITUTE not in ieText

            # # Make any requested substitutions
            # if substituteMultipleSpaces:
            #     ieText = ieText.replace( '  ', DOUBLE_SPACE_SUBSTITUTE )
            #     ieText = ieText.replace( CLEANUP_LAST_MULTIPLE_SPACE, DOUBLE_SPACE_SUBSTITUTE )
            # if substituteTrailingSpaces:
            #     ieText = ieText.replace( TRAILING_SPACE_LINE, TRAILING_SPACE_LINE_SUBSTITUTE )

            self.textBox.insert( tk.END, ieText, ieTags )
        # end of BibleNotesWindowAddon.displayAppendVerse.insertAtEnd


        # Start of main code for BibleNotesWindowAddon.displayAppendVerse
        try: cVM, fVM = self._contextViewMode, self._formatViewMode
        except AttributeError: # Must be called from a box, not a window so get settings from parent
            cVM, fVM = self.parentWindow._contextViewMode, self.parentWindow._formatViewMode
        vPrint( 'Never', debuggingThisModule, "displayAppendVerse2( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )

        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, "BibleNotesWindowAddon.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
            ##try: vPrint( 'Quiet', debuggingThisModule, "BibleNotesWindowAddon.displayAppendVerse( {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, currentVerseFlag ) )
            ##except UnicodeEncodeError: vPrint( 'Quiet', debuggingThisModule, "BibleNotesWindowAddon.displayAppendVerse", firstFlag, verseKey, currentVerseFlag )

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
        #dPrint( 'Quiet', debuggingThisModule, "Marks", previousMarkName, currentMarkName, nextMarkName )

        lastCharWasSpace = haveTextFlag = not firstFlag

        if verseContextData is None:
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                vPrint( 'Quiet', debuggingThisModule, "  ", "BibleNotesWindowAddon.displayAppendVerse has no data for", verseKey )
            verseDataList = context = None
        elif isinstance( verseContextData, tuple ):
            assert len(verseContextData) == 2
            verseDataList, context = verseContextData
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #dPrint( 'Quiet', debuggingThisModule, "   VerseDataList: {}".format( verseDataList ) )
                #dPrint( 'Quiet', debuggingThisModule, "   Context: {}".format( context ) )
        elif isinstance( verseContextData, str ):
            verseDataList, context = verseContextData.split( '\n' ), None
        elif BibleOrgSysGlobals.debugFlag: halt

        # if firstFlag:
        #     pass

        #dPrint( 'Quiet', debuggingThisModule, "  Setting mark to {}".format( currentMarkName ) )
        self.textBox.mark_set( currentMarkName, tk.INSERT )
        self.textBox.mark_gravity( currentMarkName, tk.LEFT )

        if verseDataList is None:
            if C!=0 and V!=0:
                vPrint( 'Quiet', debuggingThisModule, "  ", "BibleNotesWindowAddon.displayAppendVerse has no data for", self.moduleID, verseKey )
            #self.textBox.insert( tk.END, '--' )
        else:
            #hadVerseText = False
            #try: cVM = self._contextViewMode
            #except AttributeError: cVM = self.parentWindow._contextViewMode
            lastParagraphMarker = context[-1] if context and context[-1] in BibleOrgSysGlobals.USFMParagraphMarkers \
                                        else 'v~' # If we don't know the format of a verse (or for unformatted Bibles)
            endMarkers = []

            # Pre-process the note(s) to extract them out of the pseudo-USFM
            vPrint( 'Quiet', debuggingThisModule, f"Preprocessing notes from {len(verseDataList)} entries" )
            notes = []
            thisNote = {}
            markerName = None
            for verseDataEntry in verseDataList:
                # dPrint( 'Info', debuggingThisModule, f"Have {thisNote}")
                # dPrint( 'Info', debuggingThisModule, f"Got {verseDataEntry}")
                if isinstance( verseDataEntry, InternalBibleEntry ):
                    marker, cleanText = verseDataEntry.getMarker(), verseDataEntry.getCleanText()
                    if marker[0] == '¬': continue # ignore it
                    if marker in ('c','c#'): continue # don't need these
                    if marker in ('m', 'q1'): # Might be a new note
                        if thisNote and 'OccurrenceNote' in thisNote:
                            notes.append( thisNote )
                            thisNote = {}
                    if marker == 'v': pass
                    elif marker == 'm': markerName = 'SupportReference'
                    elif marker == 'q1': markerName = 'OrigQuote'
                    elif marker == 'pi': markerName = 'Occurrence'
                    elif marker == 'q2': markerName = 'GLQuote'
                    elif marker in ('p','ip'): markerName = 'OccurrenceNote'
                    elif marker == 'p~':
                        if markerName: thisNote[markerName] = cleanText.replace( '<br>', '\n' )
                        else: halt # Shouldn't happen
                        markerName = None
                    else: halt # Unknown marker
                else: halt # Shouldn't happen
            if thisNote: notes.append( thisNote )
            # dPrint( 'Info', debuggingThisModule, f"notes ({len(notes)}) {notes}")

            vPrint( 'Quiet', debuggingThisModule, f"Displaying {len(notes)} notes from {len(verseDataList)} entries" )
            for n, note in enumerate( notes, start=1 ):
                if haveTextFlag: self.textBox.insert ( tk.END, '\n\n' )
                if len(notes) > 1:
                    insertAtEnd( str(n), 'c' )
                    haveTextFlag = True
                for field,cleanText in note.items():
                    if field == 'SupportReference':
                        self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, 'toc1' )
                        haveTextFlag = True
                    elif field == 'OrigQuote':
                        self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, 'd' )
                        haveTextFlag = True
                    elif field == 'Occurrence':
                        self.textBox.insert ( tk.END, f' ({cleanText})' )
                        haveTextFlag = True
                    elif field == 'GLQuote':
                        self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, 'sp' )
                        haveTextFlag = True
                    elif field == 'OccurrenceNote':
                        for line in cleanText.split( '\n' ):
                            self.textBox.insert ( tk.END, '\n' )
                            if line.startswith( '# '): insertAtEnd( line[2:], 's1' )
                            elif line.startswith( '## '): insertAtEnd( line[3:], 's2' )
                            elif line.startswith( '### '): insertAtEnd( line[4:], 's3' )
                            elif line.startswith( '#### '): insertAtEnd( line[5:], 's4' )
                            else: insertAtEnd( line, 'm' )
                        haveTextFlag = True

            if lastFlag and cVM=='ByVerse' and endMarkers:
                #dPrint( 'Quiet', debuggingThisModule, "endMarkers", endMarkers )
                insertAtEnd( ' '+ _("End context")+':', 'contextHeader' )
                contextString, firstMarker = "", True
                for someMarker in endMarkers:
                    #dPrint( 'Quiet', debuggingThisModule, "  someMarker", someMarker )
                    contextString += (' ' if firstMarker else ', ') + someMarker
                    firstMarker = False
                insertAtEnd( contextString+' ', 'context' )
    # end of BibleNotesWindowAddon.displayAppendVerse


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog
        """
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.doShowInfo( {} )").format( event ) )

        infoString = 'BibleNotesWindowAddon:\n' \
                 + '  Name:\t{}\n'.format( self.modulePath if self.internalBible is None else self.internalBible.getAName() ) \
                 + '  Type:\t{}\n'.format( self.modulePath if self.internalBible is None else self.internalBible.objectTypeString ) \
                 + '  Path:\t{}'.format( self.modulePath )
        showInfo( self, 'Window Information', infoString )
    # end of BibleNotesWindowAddon.doShowInfo


    def _prepareForExports( self ):
        """
        Prepare to do some of the exports available in BibleOrgSysGlobals.
        """
        logging.info( _("BibleNotesWindowAddon.prepareForExports()…") )
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.prepareForExports()…") )

        self._prepareInternalBible()
        if self.internalBible is not None:
            BiblelatorGlobals.theApp.setWaitStatus( _("Preparing for export…") )
            if self.exportFolderpath is None:
                fp = self.folderpath
                if fp and fp[-1] in '/\\': fp = fp[:-1] # Removing trailing slash
                self.exportFolderpath = fp + 'Export/'
                #dPrint( 'Quiet', debuggingThisModule, "eFolder", repr(self.exportFolderpath) )
                if not os.path.exists( self.exportFolderpath ):
                    os.mkdir( self.exportFolderpath )
            setDefaultControlFolderpath( '../BibleOrgSys/ControlFiles/' )
            BiblelatorGlobals.theApp.setWaitStatus( _("Export in process…") )
    # end of BibleNotesWindowAddon._prepareForExports

    def doMostExports( self ):
        """
        Do most of the quicker exports available in BibleOrgSysGlobals.
        """
        logging.info( _("BibleNotesWindowAddon.doMostExports()…") )
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.doMostExports()…") )

        self._prepareForExports()
        self.internalBible.doAllExports( self.exportFolderpath )
        self._doneExports()
    # end of BibleNotesWindowAddon.doMostExports

    def doPhotoBibleExport( self ):
        """
        Do the BibleOrgSys PhotoBible export.
        """
        logging.info( _("BibleNotesWindowAddon.doPhotoBibleExport()…") )
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.doPhotoBibleExport()…") )

        self._prepareForExports()
        self.internalBible.toPhotoBible( os.path.join( self.exportFolderpath, 'BOS_PhotoBible_Export/' ) )
        self._doneExports()
    # end of BibleNotesWindowAddon.doPhotoBibleExport

    def doODFsExport( self ):
        """
        Do the BibleOrgSys ODFsExport export.
        """
        logging.info( _("BibleNotesWindowAddon.doODFsExport()…") )
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.doODFsExport()…") )

        self._prepareForExports()
        self.internalBible.toODF( os.path.join( self.exportFolderpath, 'BOS_ODF_Export/' ) )
        self._doneExports()
    # end of BibleNotesWindowAddon.doODFsExport

    def doPDFsExport( self ):
        """
        Do the BibleOrgSys PDFsExport export.
        """
        logging.info( _("BibleNotesWindowAddon.doPDFsExport()…") )
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.doPDFsExport()…") )

        self._prepareForExports()
        self.internalBible.toTeX( os.path.join( self.exportFolderpath, 'BOS_PDF(TeX)_Export/' ) )
        self._doneExports()
    # end of BibleNotesWindowAddon.doPDFsExport

    def doAllExports( self ):
        """
        Do all exports available in BibleOrgSysGlobals.
        """
        logging.info( _("BibleNotesWindowAddon.doAllExports()…") )
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.doAllExports()…") )

        self._prepareForExports()
        self.internalBible.doAllExports( self.exportFolderpath, wantPhotoBible=True, wantODFs=True, wantPDFs=True )
        self._doneExports()
    # end of BibleNotesWindowAddon.doAllExports


    def _doneExports( self ):
        """
        """
        BiblelatorGlobals.theApp.setStatus( _("Waiting for user input…") )
        infoString = _("Results should be in {}").format( self.exportFolderpath )
        showInfo( self, 'Folder Information', infoString )
        BiblelatorGlobals.theApp.setReadyStatus()
    # end of BibleNotesWindowAddon.doAllExports


    def doCheckProject( self ):
        """
        Run the BibleOrgSys checks on the project.
        """
        logging.info( _("BibleNotesWindowAddon.doCheckProject()…") )
        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindowAddon.doCheckProject()…") )

        self._prepareInternalBible() # Slow but must be called before the dialog
        currentBBB = self.currentVerseKey.getBBB()
        gBBRD = GetBibleBookRangeDialog( self, self.internalBible, currentBBB, None, title=_('Books to be checked') )
        #if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', debuggingThisModule, "gBBRDResult", repr(gBBRD.result) )
        if gBBRD.result:
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBBRD.result, list )
            #if len(gBBRD.result)==1 and gBBRD.result[0]==currentBBB:
                ## It's just the current book to check
                #if self.modified(): self.doSave()
                #self.internalBible.loadBookIfNecessary( currentBBB )
            #else: # load all books
                #self._prepareInternalBible()
            BiblelatorGlobals.theApp.setWaitStatus( _("Doing Bible checks…") )
            self.internalBible.check( gBBRD.result )
            displayExternally = False
            if displayExternally: # Call up a browser window
                import webbrowser
                indexFile = self.internalBible.makeErrorHTML( self.folderpath, gBBRD.result )
                webbrowser.open( indexFile )
            else: # display internally in our HTMLWindow
                indexFile = self.internalBible.makeErrorHTML( self.folderpath, gBBRD.result )
                hW = HTMLWindow( self, indexFile )
                BiblelatorGlobals.theApp.childWindows.append( hW )
                if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Finished openCheckWindow" )
        BiblelatorGlobals.theApp.setReadyStatus()
    # end of BibleNotesWindowAddon.doCheckProject


    #def doHelp( self, event=None ):
        #"""
        #Display a help box.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindowAddon.doHelp( {} )").format( event ) )
        #from Biblelator.Dialogs.Help import HelpBox

        #helpInfo = programNameVersion
        #helpInfo += '\n' + _("Help for {}").format( self.windowType )
        #helpInfo += '\n  ' + _("Keyboard shortcuts:")
        #for name,shortcut in self.myKeyboardBindingsList:
            #helpInfo += "\n    {}\t{}".format( name, shortcut )
        #hb = HelpBox( self, self.genericWindowType, helpInfo )
        #return tkBREAK # so we don't do the main window help also
    ## end of BibleNotesWindowAddon.doHelp


    #def doAbout( self, event=None ):
        #"""
        #Display an about box.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindowAddon.doAbout( {} )").format( event ) )
        #from Biblelator.Dialogs.About import AboutBox

        #aboutInfo = programNameVersion
        #aboutInfo += "\nInformation about {}".format( self.windowType )
        #ab = AboutBox( self, self.genericWindowType, aboutInfo )
        #return tkBREAK # so we don't do the main window about also
    ## end of BibleNotesWindowAddon.doAbout


    #def doClose( self, event=None ):
        #"""
        #Called to finally and irreversibly remove this window from our list and close it.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindowAddon.doClose( {} ) for {}").format( event, self.genericWindowType ) )

        ## Remove ourself from the list of internal Bibles (and their controlling windows)
        ##dPrint( 'Quiet', debuggingThisModule, 'internalBibles initially', len(theApp.internalBibles), BiblelatorGlobals.theApp.internalBibles )
        #newBibleList = []
        #for internalBible,windowList in BiblelatorGlobals.theApp.internalBibles:
            #if internalBible is self.internalBible:
                #newWindowList = []
                #for controllingWindow in windowList:
                    #if controllingWindow is not self: # leave other windows alone
                        #newWindowList.append( controllingWindow )
                #if newWindowList: newBibleList.append( (internalBible,windowList) )
            #else: # leave this one unchanged
                #newBibleList.append( (internalBible,windowList) )
        #theApp.internalBibles = newBibleList
        ##dPrint( 'Quiet', debuggingThisModule, 'internalBibles now', len(theApp.internalBibles), BiblelatorGlobals.theApp.internalBibles )

        #BibleResourceWindow.doClose( self, event )
        #if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Closed BibleNotesWindowAddon" )
    ## end of BibleNotesWindowAddon.doClose
# end of BibleNotesWindowAddon class



class BibleNotesWindow( ChildWindow, BibleNotesWindowAddon ):
    """
    A window displaying one internal (on-disk) Bible.
    """
    def __init__( self, parentWindow, folderpath ):
        """
        Given a folder, try to open an UnknownBible.
        If successful, set self.internalBible to point to the loaded Bible.
        """
        vPrint( 'Never', debuggingThisModule, f"BibleNotesWindow.__init__( pW={parentWindow}, mP={folderpath} )…" )
        self.folderpath = folderpath
        ChildWindow.__init__( self, parentWindow, genericWindowType='BibleResource' )
        BibleNotesWindowAddon.__init__( self, folderpath )

        self.createMenuBar()
        self.createContextMenu() # Enable right-click menu

        if self.folderpath is not None:
            try: self.internalBible = uWNotesBible( self.folderpath )
            except FileNotFoundError:
                logging.critical( _("BibleNotesWindow.__init__ Unable to find module path: {!r}").format( self.folderpath ) )
                self.internalBible = None
        if self.internalBible is not None: # Define which functions we use by default
            assert isinstance( self.internalBible, Bible )
            self.internalBible.preload()
            self.getNumVerses = self.internalBible.getNumVerses
            self.getNumChapters = self.internalBible.getNumChapters
            handleInternalBibles( self.internalBible, self )

        vPrint( 'Never', debuggingThisModule, _("BibleNotesWindow.__init__ finished.") )
    # end of BibleNotesWindow.__init__


    #def createMenuBar( self ):
        #"""
        #"""
        #dPrint( 'Never', debuggingThisModule, _("BibleNotesWindow.createMenuBar()…") )
        #self.menubar = tk.Menu( self )
        ##self['menu'] = self.menubar
        #self.configure( menu=self.menubar ) # alternative

        #fileMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        ##fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        ##fileMenu.add_command( label=_('Open…'), underline=0, command=self.notWrittenYet )
        ##fileMenu.add_separator()
        ##subfileMenuImport = tk.Menu( fileMenu )
        ##subfileMenuImport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        ##fileMenu.add_cascade( label=_('Import'), underline=0, menu=subfileMenuImport )
        ##subfileMenuExport = tk.Menu( fileMenu )
        ##subfileMenuExport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        ##subfileMenuExport.add_command( label=_('HTML'), underline=0, command=self.notWrittenYet )
        ##fileMenu.add_cascade( label=_('Export'), underline=0, menu=subfileMenuExport )
        ##fileMenu.add_separator()
        #fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Info')][0] )
        #fileMenu.add_separator()
        #fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] ) # close this window

        #editMenu = tk.Menu( self.menubar )
        #self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        #editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        #editMenu.add_separator()
        #editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )

        #searchMenu = tk.Menu( self.menubar )
        #self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        #searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Line')][0] )
        #searchMenu.add_separator()
        #searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        #searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Refind')][0] )

        #gotoMenu = tk.Menu( self.menubar )
        #self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
        #gotoMenu.add_command( label=_('Previous book'), underline=-1, command=self.doGotoPreviousBook )
        #gotoMenu.add_command( label=_('Next book'), underline=-1, command=self.doGotoNextBook )
        #gotoMenu.add_command( label=_('Previous chapter'), underline=-1, command=self.doGotoPreviousChapter )
        #gotoMenu.add_command( label=_('Next chapter'), underline=-1, command=self.doGotoNextChapter )
        #gotoMenu.add_command( label=_('Previous section'), underline=-1, command=self.doGotoPreviousSection )
        #gotoMenu.add_command( label=_('Next section'), underline=-1, command=self.doGotoNextSection )
        #gotoMenu.add_command( label=_('Previous verse'), underline=-1, command=self.doGotoPreviousVerse )
        #gotoMenu.add_command( label=_('Next verse'), underline=-1, command=self.doGotoNextVerse )
        #gotoMenu.add_separator()
        #gotoMenu.add_command( label=_('Forward'), underline=0, command=self.doGoForward )
        #gotoMenu.add_command( label=_('Backward'), underline=0, command=self.doGoBackward )
        #gotoMenu.add_separator()
        #gotoMenu.add_command( label=_('Previous list item'), underline=0, state=tk.DISABLED, command=self.doGotoPreviousListItem )
        #gotoMenu.add_command( label=_('Next list item'), underline=0, state=tk.DISABLED, command=self.doGotoNextListItem )
        #gotoMenu.add_separator()
        #gotoMenu.add_command( label=_('Book'), underline=0, command=self.doGotoBook )
        #gotoMenu.add_separator()
        #self._groupRadioVar.set( self._groupCode )
        #gotoMenu.add_radiobutton( label=_('Group A'), underline=6, value='A', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        #gotoMenu.add_radiobutton( label=_('Group B'), underline=6, value='B', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        #gotoMenu.add_radiobutton( label=_('Group C'), underline=6, value='C', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        #gotoMenu.add_radiobutton( label=_('Group D'), underline=6, value='D', variable=self._groupRadioVar, command=self.changeBibleGroupCode )

        #self.viewMenu = tk.Menu( self.menubar, tearoff=False ) # Save this reference so we can disable entries later
        #self.menubar.add_cascade( menu=self.viewMenu, label=_('View'), underline=0 )
        #self.viewMenu.add_radiobutton( label=_('Before and after…'), underline=7, value=1, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label=_('One section'), underline=4, value=2, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label=_('Single verse'), underline=7, value=3, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label=_('Whole book'), underline=6, value=4, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label=_('Whole chapter'), underline=6, value=5, variable=self._contextViewRadioVar, command=self.changeBibleContextView )

        #self.viewMenu.add_separator()
        #self.viewMenu.add_radiobutton( label=_('Formatted'), underline=0, value=1, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )
        #self.viewMenu.add_radiobutton( label=_('Unformatted'), underline=0, value=2, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )

        #if 'DBP' in self.windowType: # disable excessive online use
            #self.viewMenu.entryconfigure( 'Whole book', state=tk.DISABLED )
            #self.viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        #toolsMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=toolsMenu, label=_('Tools'), underline=0 )
        #toolsMenu.add_command( label=_('Options…'), underline=0, command=self.notWrittenYet )

        #windowMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=windowMenu, label=_('Window'), underline=0 )
        #windowMenu.add_command( label=_('Bring in'), underline=0, command=self.notWrittenYet )
        #windowMenu.add_separator()
        #windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('ShowMain')][0] )

        #helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        #self.menubar.add_cascade( menu=helpMenu, underline=0, label=_('Help') )
        #helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Help')][0] )
        #helpMenu.add_separator()
        #helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('About')][0] )
    ## end of BibleNotesWindow.createMenuBar


    #def refreshTitle( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.refreshTitle()…") )

        #self.title( "[{}] {} (InternalBible){} {} {}:{} [{}]".format( self._groupCode,
                        #self.modulePath if self.internalBible is None else self.internalBible.getAName(),
                        #' NOT FOUND' if self.internalBible is None else '',
                        #self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber(),
                        #self._contextViewMode ) )
    ## end if BibleNotesWindow.refreshTitle


    #def createContextMenu( self ):
        #"""
        #Can be overriden if necessary.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.createContextMenu()…") )

        #self.contextMenu = tk.Menu( self, tearoff=0 )
        #self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Bible Find…'), underline=6, command=self.doBibleFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Find in window…'), underline=8, command=self.doBoxFind )#, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        ##self.contextMenu.add_separator()
        ##self.contextMenu.add_command( label=_('Close window'), underline=1, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] )

        #self.bind( '<Button-3>', self.showContextMenu ) # right-click
        ##self.pack()

        #self.BibleFindOptionsDict, self.BibleReplaceOptionsDict = {}, {}
    ## end of BibleNotesWindow.createContextMenu


    #def getContextVerseData( self, verseKey ):
        #"""
        #Fetches and returns the internal Bible data for the given reference.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.getContextVerseData( {} )").format( verseKey ) )

        #if self.internalBible is not None:
            #try: return self.internalBible.getContextVerseData( verseKey )
            #except KeyError: # Could be after a verse-bridge ???
                #if verseKey.getChapterNumber() != '0':
                    #logging.error( _("BibleNotesWindow.getContextVerseData for {} {} got a KeyError") \
                                                                #.format( self.windowType, verseKey ) )
    ## end of BibleNotesWindow.getContextVerseData


    #def doShowInfo( self, event=None ):
        #"""
        #Pop-up dialog
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doShowInfo( {} )").format( event ) )

        #infoString = 'BibleNotesWindow:\n' \
                 #+ '  Name:\t{}\n'.format( self.modulePath if self.internalBible is None else self.internalBible.getAName() ) \
                 #+ '  Type:\t{}\n'.format( self.modulePath if self.internalBible is None else self.internalBible.objectTypeString ) \
                 #+ '  Path:\t{}'.format( self.modulePath )
        #showInfo( self, 'Window Information', infoString )
    ## end of BibleNotesWindow.doShowInfo


    #def _prepareForExports( self ):
        #"""
        #Prepare to do some of the exports available in BibleOrgSysGlobals.
        #"""
        #logging.info( _("BibleNotesWindow.prepareForExports()…") )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.prepareForExports()…") )

        #self._prepareInternalBible()
        #if self.internalBible is not None:
            #theApp.setWaitStatus( _("Preparing for export…") )
            #if self.exportFolderpath is None:
                #fp = self.folderpath
                #if fp and fp[-1] in '/\\': fp = fp[:-1] # Removing trailing slash
                #self.exportFolderpath = fp + 'Export/'
                ##dPrint( 'Quiet', debuggingThisModule, "eFolder", repr(self.exportFolderpath) )
                #if not os.path.exists( self.exportFolderpath ):
                    #os.mkdir( self.exportFolderpath )
            #setDefaultControlFolderpath( '../BibleOrgSys/ControlFiles/' )
            #theApp.setWaitStatus( _("Export in process…") )
    ## end of BibleNotesWindow._prepareForExports

    #def doMostExports( self ):
        #"""
        #Do most of the quicker exports available in BibleOrgSysGlobals.
        #"""
        #logging.info( _("BibleNotesWindow.doMostExports()…") )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doMostExports()…") )

        #self._prepareForExports()
        #self.internalBible.doAllExports( self.exportFolderpath )
        #self._doneExports()
    ## end of BibleNotesWindow.doMostExports

    #def doPhotoBibleExport( self ):
        #"""
        #Do the BibleOrgSys PhotoBible export.
        #"""
        #logging.info( _("BibleNotesWindow.doPhotoBibleExport()…") )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doPhotoBibleExport()…") )

        #self._prepareForExports()
        #self.internalBible.toPhotoBible( os.path.join( self.exportFolderpath, 'BOS_PhotoBible_Export/' ) )
        #self._doneExports()
    ## end of BibleNotesWindow.doPhotoBibleExport

    #def doODFsExport( self ):
        #"""
        #Do the BibleOrgSys ODFsExport export.
        #"""
        #logging.info( _("BibleNotesWindow.doODFsExport()…") )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doODFsExport()…") )

        #self._prepareForExports()
        #self.internalBible.toODF( os.path.join( self.exportFolderpath, 'BOS_ODF_Export/' ) )
        #self._doneExports()
    ## end of BibleNotesWindow.doODFsExport

    #def doPDFsExport( self ):
        #"""
        #Do the BibleOrgSys PDFsExport export.
        #"""
        #logging.info( _("BibleNotesWindow.doPDFsExport()…") )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doPDFsExport()…") )

        #self._prepareForExports()
        #self.internalBible.toTeX( os.path.join( self.exportFolderpath, 'BOS_PDF(TeX)_Export/' ) )
        #self._doneExports()
    ## end of BibleNotesWindow.doPDFsExport

    #def doAllExports( self ):
        #"""
        #Do all exports available in BibleOrgSysGlobals.
        #"""
        #logging.info( _("BibleNotesWindow.doAllExports()…") )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doAllExports()…") )

        #self._prepareForExports()
        #self.internalBible.doAllExports( self.exportFolderpath, wantPhotoBible=True, wantODFs=True, wantPDFs=True )
        #self._doneExports()
    ## end of BibleNotesWindow.doAllExports


    #def _doneExports( self ):
        #"""
        #"""
        #theApp.setStatus( _("Waiting for user input…") )
        #infoString = _("Results should be in {}").format( self.exportFolderpath )
        #showInfo( self, 'Folder Information', infoString )
        #theApp.setReadyStatus()
    ## end of BibleNotesWindow.doAllExports


    #def doCheckProject( self ):
        #"""
        #Run the BibleOrgSys checks on the project.
        #"""
        #logging.info( _("BibleNotesWindow.doCheckProject()…") )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doCheckProject()…") )

        #self._prepareInternalBible() # Slow but must be called before the dialog
        #currentBBB = self.currentVerseKey.getBBB()
        #gBBRD = GetBibleBookRangeDialog( self, self.internalBible, currentBBB, None, title=_('Books to be checked') )
        ##if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', debuggingThisModule, "gBBRDResult", repr(gBBRD.result) )
        #if gBBRD.result:
            #if BibleOrgSysGlobals.debugFlag: assert isinstance( gBBRD.result, list )
            ##if len(gBBRD.result)==1 and gBBRD.result[0]==currentBBB:
                ### It's just the current book to check
                ##if self.modified(): self.doSave()
                ##self.internalBible.loadBookIfNecessary( currentBBB )
            ##else: # load all books
                ##self._prepareInternalBible()
            #theApp.setWaitStatus( _("Doing Bible checks…") )
            #self.internalBible.check( gBBRD.result )
            #displayExternally = False
            #if displayExternally: # Call up a browser window
                #import webbrowser
                #indexFile = self.internalBible.makeErrorHTML( self.folderpath, gBBRD.result )
                #webbrowser.open( indexFile )
            #else: # display internally in our HTMLWindow
                #indexFile = self.internalBible.makeErrorHTML( self.folderpath, gBBRD.result )
                #hW = HTMLWindow( self, indexFile )
                #theApp.childWindows.append( hW )
                #if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Finished openCheckWindow" )
        #theApp.setReadyStatus()
    ## end of BibleNotesWindow.doCheckProject


    #def doHelp( self, event=None ):
        #"""
        #Display a help box.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doHelp( {} )").format( event ) )
        #from Biblelator.Dialogs.Help import HelpBox

        #helpInfo = programNameVersion
        #helpInfo += '\n' + _("Help for {}").format( self.windowType )
        #helpInfo += '\n  ' + _("Keyboard shortcuts:")
        #for name,shortcut in self.myKeyboardBindingsList:
            #helpInfo += "\n    {}\t{}".format( name, shortcut )
        #hb = HelpBox( self, self.genericWindowType, helpInfo )
        #return tkBREAK # so we don't do the main window help also
    ## end of BibleNotesWindow.doHelp


    #def doAbout( self, event=None ):
        #"""
        #Display an about box.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doAbout( {} )").format( event ) )
        #from Biblelator.Dialogs.About import AboutBox

        #aboutInfo = programNameVersion
        #aboutInfo += "\nInformation about {}".format( self.windowType )
        #ab = AboutBox( self, self.genericWindowType, aboutInfo )
        #return tkBREAK # so we don't do the main window about also
    ## end of BibleNotesWindow.doAbout


    #def doClose( self, event=None ):
        #"""
        #Called to finally and irreversibly remove this window from our list and close it.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("BibleNotesWindow.doClose( {} ) for {}").format( event, self.genericWindowType ) )

        ## Remove ourself from the list of internal Bibles (and their controlling windows)
        ##dPrint( 'Quiet', debuggingThisModule, 'internalBibles initially', len(theApp.internalBibles), BiblelatorGlobals.theApp.internalBibles )
        #newBibleList = []
        #for internalBible,windowList in BiblelatorGlobals.theApp.internalBibles:
            #if internalBible is self.internalBible:
                #newWindowList = []
                #for controllingWindow in windowList:
                    #if controllingWindow is not self: # leave other windows alone
                        #newWindowList.append( controllingWindow )
                #if newWindowList: newBibleList.append( (internalBible,windowList) )
            #else: # leave this one unchanged
                #newBibleList.append( (internalBible,windowList) )
        #theApp.internalBibles = newBibleList
        ##dPrint( 'Quiet', debuggingThisModule, 'internalBibles now', len(theApp.internalBibles), BiblelatorGlobals.theApp.internalBibles )

        #BibleResourceWindow.doClose( self, event )
        #if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Closed BibleNotesWindow" )
    ## end of BibleNotesWindow.doClose
# end of BibleNotesWindow class



def briefDemo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, _("Running demo…") )

    tkRootWindow = Tk()
    tkRootWindow.title( programNameVersion )

    #settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', PROGRAM_NAME )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of BibleNotesWindow.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, _("Running demo…") )

    tkRootWindow = Tk()
    tkRootWindow.title( programNameVersion )

    #settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', PROGRAM_NAME )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of BibleNotesWindow.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BibleNotesWindow.py
