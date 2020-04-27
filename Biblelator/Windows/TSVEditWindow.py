#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# TSVEditWindow.py
#
# The edit windows for Biblelator TSV table editing
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
A general window with one text box that has full editing functions,
    i.e., load, save, save-as, font resizing, etc.

The add-on can be used to build other editing windows.
"""
from gettext import gettext as _
from typing import List, Tuple, Optional
import os.path
import logging
import shutil
from datetime import datetime
import random

import tkinter as tk
from tkinter import font
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import Frame, Scrollbar, Button, Label, Entry, Style

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Reference.BibleOrganisationalSystems import BibleOrganisationalSystem

# Biblelator imports
if __name__ == '__main__':
    import sys
    aboveAboveFolderPath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderPath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderPath )
from Biblelator.BiblelatorGlobals import APP_NAME, tkSTART, tkBREAK, DEFAULT, \
                                DATA_FOLDER_NAME, BIBLE_GROUP_CODES
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showInfo
from Biblelator.Dialogs.BiblelatorDialogs import YesNoDialog, OkCancelDialog
from Biblelator.Windows.TextBoxes import CustomText, TRAILING_SPACE_SUBSTITUTE, MULTIPLE_SPACE_SUBSTITUTE, \
                                DOUBLE_SPACE_SUBSTITUTE, ALL_POSSIBLE_SPACE_CHARS
from Biblelator.Windows.ChildWindows import ChildWindow, BibleWindowAddon
from Biblelator.Helpers.AutocorrectFunctions import setDefaultAutocorrectEntries # setAutocorrectEntries
from Biblelator.Helpers.AutocompleteFunctions import getCharactersBeforeCursor, \
                                getWordCharactersBeforeCursor, getCharactersAndWordBeforeCursor, \
                                getWordBeforeSpace, addNewAutocompleteWord, acceptAutocompleteSelection


LAST_MODIFIED_DATE = '2020-04-27' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorTSVEditWindow"
PROGRAM_NAME = "Biblelator TSV Edit Window"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = 7


REFRESH_TITLE_TIME = 500 # msecs
CHECK_DISK_CHANGES_TIME = 33333 # msecs
NO_TYPE_TIME = 6000 # msecs
NUM_AUTOCOMPLETE_POPUP_LINES = 6
MAX_PSEUDOVERSES = 200 # What should this really be?


class TSVEditWindowAddon:
    """
    """
    def __init__( self, windowType:str, folderpath:str, filename:str ):
        """
        """
        if 1 or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, f"TSVEditWindowAddon.__init__( {windowType}, {folderpath}, {filename} )…" )
        self.windowType, self.folderpath, self.filename = windowType, folderpath, filename
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, f"TSVEditWindowAddon __init__ {windowType} {folderpath} {filename}" )

        self.loading = True

        # Read the entire file contents at the beginning (assumes lots of RAM)
        self.filepath = os.path.join( folderpath, filename )
        try:
            with open( self.filepath, 'rt', encoding='utf-8' ) as input_file:
                self.originalText = input_file.read()
        except FileNotFoundError:
            showError( self, APP_NAME, f"Could not open and read '{self.filepath}'" )
            return
        if not self.originalText:
            showError( self, APP_NAME, f"Could not open and read {self.filepath}" )
            return
        fileLines = self.originalText.split( '\n' )
        if fileLines and fileLines[-1] == '':
            print( "Deleting final blank line" )
            fileLines = fileLines[:-1]
            self.hadTrailingNL = True
        else:
            self.hadTrailingNL = False
        self.numOriginalLines = len( fileLines )
        print( f"{len(self.originalText):,} bytes ({self.numOriginalLines:,} lines) read from {self.filepath}" )
        if self.numOriginalLines < 2:
            showError( self, APP_NAME, f'Not enough ({self.numOriginalLines}) preexisting lines in file ' + filepath )
        # We keep self.originalText and self.numOriginalLines to determine later if we have any changes

        print( "Checking loaded TSV table…" )
        self.num_columns = None
        self.tsvTable:List[List] = []
        for j, line in enumerate( fileLines, start=1 ):
            if line and line[-1]=='\n': line = line[:-1] # Remove trailing nl
            columns = line.split( '\t' )
            if self.num_columns is None:
                self.num_columns = len( columns )
                # print( f"  Have {self.num_columns} columns")
            elif len(columns) != self.num_columns:
                logging.critical( f"Expected {self.num_columns} columns but found {len(columns)} in row {j} of {filepath}" )
            self.tsvTable.append( columns )
        self.tsvHeaders = self.tsvTable[0]
        vPrint( 'Quiet', debuggingThisModule, f"  Have table headers ({self.num_columns}): {self.tsvHeaders}" )
        self.numDataRows = len(self.tsvTable) - 1
        vPrint( 'Quiet', debuggingThisModule, f"  Have {self.numDataRows:,} rows" )

        # self.protocol( 'WM_DELETE_WINDOW', self.doClose ) # Catch when window is closed

        # Set-up our Bible system and our callables
        self.BibleOrganisationalSystem = BibleOrganisationalSystem( 'GENERIC-KJV-80-ENG' ) # temp
        self.getNumChapters = self.BibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda BBB,C: MAX_PSEUDOVERSES if BBB=='UNK' or C=='-1' or C==-1 \
                                        else self.BibleOrganisationalSystem.getNumVerses( BBB, C )

        self.current_row = None
        self.onTextNoChangeID = None
        self.editStatus = 'Editable'

        self._groupCode = 'A' # Fixed

        # # Make our own custom textBox which allows a callback function
        # #   Delete these lines and the callback line if you don't need either autocorrect or autocomplete
        # self.textBox.destroy() # from the ChildWindow default
        # self.myKeyboardBindingsList = []
        # if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = []

        # self.customFont = tk.font.Font( family="sans-serif", size=12 )
        # self.customFontBold = tk.font.Font( family="sans-serif", size=12, weight='bold' )
        # self.textBox = CustomText( self, yscrollcommand=self.vScrollbar.set, wrap='word', font=self.customFont )

        # self.defaultBackgroundColour = 'gold2'
        # self.textBox.configure( background=self.defaultBackgroundColour )
        # self.textBox.configure( selectbackground='blue' )
        # self.textBox.configure( highlightbackground='orange' )
        # self.textBox.configure( inactiveselectbackground='green' )
        # self.textBox.configure( wrap='word', undo=True, autoseparators=True )
        # # self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
        # self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        # self.textBox.setTextChangeCallback( self.onTextChange )
        # self.createEditorKeyboardBindings()
        # #self.createMenuBar()
        # self.createContextMenu() # Enable right-click menu

        self.lastFiletime = self.lastFilesize = None
        # self.clearText()

        self.markMultipleSpacesFlag = True
        self.markTrailingSpacesFlag = True

        self.autocorrectEntries = []
        # Temporarily include some default autocorrect values
        setDefaultAutocorrectEntries( self )
        #setAutocorrectEntries( self, ourAutocorrectEntries )

        self.autocompleteBox, self.autocompleteWords, self.existingAutocompleteWordText = None, {}, ''
        self.autocompleteWordChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        # Note: I guess we could have used non-word chars instead (to stop the backwards word search)
        self.autocompleteMinLength = 3 # Show the normal window after this many characters have been typed
        self.autocompleteMaxLength = 15 # Remove window after this many characters have been typed
        self.autocompleteMode = None # None or Dictionary1 or Dictionary2 (or Bible or BibleBook)
        self.addAllNewWords = False

        self.invalidCombinations = [] # characters or character combinations that shouldn't occur
        # Temporarily include some default invalid values
        self.invalidCombinations = [',,',' ,',] # characters or character combinations that shouldn't occur

        self.patternsToHighlight = []
        # Temporarily include some default values -- simplistic demonstration examples
        self.patternsToHighlight.append( (True, r'rc://en/ta/[^ \]\)]+','blue',{'foreground':'blue'}) )
        self.patternsToHighlight.append( (True, r'rc://en/tw/[^ \]\)]+','orange',{'foreground':'orange', 'background':'grey'}) )
        self.patternsToHighlight.append( (True, r'rc://[^ \]\)]+','blue',{'foreground':'blue'}) )
        self.patternsToHighlight.append( (True,'#.*?\\n','grey',{'foreground':'grey'}) )
        self.patternsToHighlight.append( (False,'...','error',{'background':'red'}) )
        self.patternsToHighlight.append( (False,'Introduction','intro',{'foreground':'green'}) )
        self.patternsToHighlight.append( (False,'Who ','who',{'foreground':'green'}) )
        self.patternsToHighlight.append( (False,'What ','what',{'foreground':'green'}) )
        self.patternsToHighlight.append( (False,'How ','how',{'foreground':'green'}) )
        self.patternsToHighlight.append( (True, r'\d','digits',{'foreground':'blue'}) )
        # boldDict = {'font':self.customFontBold } #, 'background':'green'}
        # for pythonKeyword in ( 'from','import', 'class','def', 'if','and','or','else','elif',
        #                       'for','while', 'return', 'try','accept','finally', 'assert', ):
        #     self.patternsToHighlight.append( (True,'\\y'+pythonKeyword+'\\y','bold',boldDict) )

        self.saveChangesAutomatically = False # different from AutoSave (which is in different files)
        self.autosaveTime = 2*60*1000 # msecs (zero is no autosaves)
        self.autosaveScheduled = False

        self.thisBookUSFMCode = None
        self.buildWidgets()
        self.gotoRow()
        self.validateTSVTable() # gotoRow() sets self.thisBookUSFMCode needed by validateTSVTable()

        self.after( CHECK_DISK_CHANGES_TIME, self.checkForDiskChanges )
        #self.after( REFRESH_TITLE_TIME, self.refreshTitle )
        self.loading = self.hadTextWarning = False
        #self.lastTextChangeTime = time()

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.__init__ finished." )
    # end of TSVEditWindowAddon.__init__


    def buildWidgets( self ):
        """
        """
        vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.buildWidgets()…" )

        # Temp XXX ....................
        Label( self, text='WARNING: Proof of concept only—file saves are disabled so any changes will not be permanent!').pack()
        Label( self, text='Note also that it currently only loads one TSV file, so it can’t yet switch between books.').pack()

        Style().configure( 'good.TLabel', background='white' )
        Style().configure( 'bad.TLabel', background='red' )

        # self.createStatusBar()
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), background='purple' )
        #Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            #background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        #self.statusBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='ChildWindowStatusBar.TFrame' )

        # self.textBox.pack_forget() # Make sure the status bar gets the priority at the bottom of the window
        # self.vScrollbar.pack_forget()
        self.statusTextLabel = Label( self, relief=tk.SUNKEN,
                                    textvariable=self._statusTextVar, style='{}.ChildStatusBar.TLabel'.format( self ) )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.BOTTOM, fill=tk.X )
        # self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )
        # self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )

        ButtonFrame = Frame( self )
        ButtonFrame.pack( side=tk.TOP, fill=tk.X, expand=True )

        self.moveUpButton = Button( ButtonFrame, text=_('Move row up'), command=self.doMoveUp )
        self.moveUpButton.pack( side=tk.LEFT, padx=4, pady=2 )
        self.moveDownButton = Button( ButtonFrame, text=_('Move row down'), command=self.doMoveDown )
        self.moveDownButton.pack( side=tk.LEFT, padx=4, pady=2 )
        self.addBeforeButton = Button( ButtonFrame, text=_('Add row before'), command=self.doAddBefore )
        self.addBeforeButton.pack( side=tk.LEFT, padx=4, pady=2 )
        self.addAfterButton = Button( ButtonFrame, text=_('Add row after'), command=self.doAddAfter )
        self.addAfterButton.pack( side=tk.LEFT, padx=4, pady=2 )
        self.deleteRowButton = Button( ButtonFrame, text=_('Delete row'), command=self.doDeleteRow )
        self.deleteRowButton.pack( side=tk.LEFT, padx=12, pady=2 )

        idFrame = Frame( self ) # Row number, Book, C, V, ID
        idFrame.pack( side=tk.TOP, fill=tk.X )
        secondFrame = Frame( self )
        secondFrame.pack( side=tk.TOP, fill=tk.X, expand=True )
        thirdFrame = Frame( self )
        thirdFrame.pack( side=tk.TOP, fill=tk.X, expand=True )

        Label( idFrame, text=_('Row') ).pack( side=tk.LEFT, padx=(4,1), pady=2 )
        self.topButton = Button( idFrame, text='◄', width=1, command=self.gotoTop )
        self.topButton.pack( side=tk.LEFT, padx=(2,0), pady=2 )
        self.rowNumberVar = tk.IntVar()
        self.rowNumberVar.set( 1 )
        self.rowSpinbox = tk.Spinbox( idFrame, from_=1.0, to=self.numDataRows, textvariable=self.rowNumberVar, width=3, command=self.gotoRow )
        self.rowSpinbox.bind( '<Return>', self.gotoRow )
        self.rowSpinbox.pack( side=tk.LEFT, padx=0, pady=2 )
        self.bottomButton = Button( idFrame, text='►', width=1, command=self.gotoBottom )
        self.bottomButton.pack( side=tk.LEFT, padx=(0,4), pady=2 )

        self.widgets = []
        for j, headerText in enumerate( self.tsvHeaders, start=1 ):
            # print( f"{j}/ {headerText}")
            if headerText == 'Book':
                self.bookColumn = j-1
                widgetFrame = Frame( idFrame )
                headerWidget = Label( widgetFrame, text=headerText )
                dataWidget = Label( widgetFrame )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, padx=6, pady=2 )
                var = None
            elif headerText == 'Chapter':
                self.chapterColumn = j-1
                widgetFrame = Frame( idFrame )
                headerWidget = Label( widgetFrame, width=8, text=headerText )
                var = tk.StringVar()
                dataWidget = Entry( widgetFrame, width=8, textvariable=var )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, padx=(4,1), pady=2 )
            elif headerText == 'Verse':
                self.verseColumn = j-1
                widgetFrame = Frame( idFrame )
                headerWidget = Label( widgetFrame, width=6, text=headerText )
                var = tk.StringVar()
                dataWidget = Entry( widgetFrame, width=6, textvariable=var )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, padx=(1,4), pady=2 )
            elif headerText == 'ID':
                self.idColumn = j-1
                widgetFrame = Frame( idFrame )
                headerWidget = Label( widgetFrame, text=headerText )
                dataWidget = Label( widgetFrame )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, padx=6, pady=2 )
                var = None
            elif headerText == 'SupportReference':
                self.supportReferenceColumn = j-1
                widgetFrame = Frame( secondFrame )
                headerWidget = Label( widgetFrame, width=30, text=headerText )
                var = tk.StringVar()
                dataWidget = Entry( widgetFrame, width=30, textvariable=var )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, padx=4, pady=2 )
            elif headerText == 'OrigQuote':
                self.origQuoteColumn = j-1
                widgetFrame = Frame( secondFrame )
                headerWidget = Label( widgetFrame, width=50, text=headerText )
                var = tk.StringVar()
                dataWidget = Entry( widgetFrame, width=50, textvariable=var )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, expand=tk.YES, padx=4, pady=2 )
            elif headerText == 'Occurrence':
                self.occurenceColumn = j-1
                widgetFrame = Frame( secondFrame )
                headerWidget = Label( widgetFrame, width=2, text='#' )
                var = tk.StringVar()
                dataWidget = Entry( widgetFrame, width=2, textvariable=var )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, padx=4, pady=2 )
            elif headerText == 'GLQuote':
                self.GLQuoteColumn = j-1
                widgetFrame = Frame( thirdFrame )
                headerWidget = Label( widgetFrame, width=60, text=headerText )
                var = tk.StringVar()
                dataWidget = Entry( widgetFrame, width=60, textvariable=var )
                headerWidget.pack()
                dataWidget.pack()
                widgetFrame.pack( side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=4, pady=2 )
            elif headerText == 'OccurrenceNote':
                self.occurrenceNoteColumn = j-1
                widgetFrame = Frame( self )
                headerWidget = Label( widgetFrame, text=headerText )

                # Make our own custom textBox which allows a callback function
                #   Delete these lines and the callback line if you don't need either autocorrect or autocomplete
                self.vScrollbar.destroy() # from the ChildWindow default
                self.textBox.destroy() # from the ChildWindow default
                self.myKeyboardBindingsList = []
                if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = []

                self.vScrollbar = Scrollbar( widgetFrame )
                self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

                self.customFont = tk.font.Font( family="sans-serif", size=12 )
                self.customFontBold = tk.font.Font( family="sans-serif", size=12, weight='bold' )
                self.textBox = CustomText( widgetFrame, yscrollcommand=self.vScrollbar.set, wrap='word', font=self.customFont )

                self.defaultBackgroundColour = 'gold2'
                self.textBox.configure( background=self.defaultBackgroundColour )
                self.textBox.configure( selectbackground='blue' )
                self.textBox.configure( highlightbackground='orange' )
                self.textBox.configure( inactiveselectbackground='green' )
                self.textBox.configure( wrap='word', undo=True, autoseparators=True )
                # self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
                self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
                self.textBox.setTextChangeCallback( self.onTextChange )
                self.createEditorKeyboardBindings()
                #self.createMenuBar()
                self.createContextMenu() # Enable right-click menu
                dataWidget = self.textBox

                headerWidget.pack()
                dataWidget.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
                widgetFrame.pack( side=tk.TOP, padx=4, pady=2 )
                var = 'TB'
            else: # it's not one we recognise / usually expect
                widgetFrame = Frame( self )
                headerWidget = Label( widgetFrame, text=headerText )
                dataWidget = Label( widgetFrame )
                headerWidget.pack()
                dataWidget.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
                widgetFrame.pack( side=tk.LEFT, padx=4, pady=2 )
                var = None
            # Doesn't work to bind KeyPress coz the text hasn't changed yet!
            dataWidget.bind( '<KeyRelease>', self.checkCurrentDisplayedRowData )
            dataWidget.bind( '<FocusIn>', self.checkCurrentDisplayedRowData )
            dataWidget.bind( '<FocusOut>', self.checkCurrentDisplayedRowData )
            self.widgets.append( (var,dataWidget) )

        self.numLabel = Label( idFrame )
        self.numLabel.pack( side=tk.RIGHT, padx=8, pady=2 )

        self.setStatus() # Clear it
        self.parentApp.setReadyStatus() # So it doesn't get left with an error message on it
    # end of TSVEditWindowAddon.buildWidgets function


    def gotoRow( self, event=None, force:bool=False, notifyMain:bool=True ) -> None:
        """
        Handle a new row number.
        """
        vPrint( 'Quiet', debuggingThisModule, f"gotoRow( {event}, f={force}, nM={notifyMain} ) from {self.current_row}…" )
        #vPrint( 'Never', debuggingThisModule, dir(event) )

        row = self.rowNumberVar.get()
        # Check for bad numbers (they must have manually entered them as spinner doesn't allow this)
        if row < 1:
            self.rowNumberVar.set( 1 ); return
        if row > self.numDataRows:
            self.rowNumberVar.set( self.numDataRows ); return
        assert 1 <= row <= self.numDataRows
        if row==self.current_row and not force: return # Nothing to do here

        if self.current_row: # The last row might have changed
            self.retrieveCurrentRowData( updateTable=True ) # in case current row was edited
        currentRowData = self.tsvTable[row]
        self.numLabel.configure( text=f'Have {self.numDataRows} rows (plus header)' )

        if self.thisBookUSFMCode is None:
            self.thisBookUSFMCode = currentRowData[self.bookColumn]
            self.BBB = BibleOrgSysGlobals.loadedBibleBooksCodes.getBBBFromUSFMAbbreviation( self.thisBookUSFMCode )
        elif currentRowData[self.bookColumn] != self.thisBookUSFMCode:
            logging.critical( f"Row {row} seems to have a different book code '{currentRowData[self.bookColumn]}' from expected '{self.thisBookUSFMCode}'" )
        C, V, = currentRowData[self.chapterColumn], currentRowData[self.verseColumn]
        if C == 'front': C = '-1'
        if V == 'intro': V = '0'
        self.currentVerseKey = SimpleVerseKey( self.BBB,C,V )
        if notifyMain and not self.loading:
            self.parentApp.gotoBCV( self.BBB, C, V ) # Update main window (and from there, other child windows)

        assert len(currentRowData) == self.num_columns
        for j, (var,dataWidget) in enumerate( self.widgets ):
            # print( f"{j}/ {dir(dataWidget) if j==0 else dataWidget.winfo_name}")
            if var=='TB': self.setAllText( currentRowData[j].replace( '<br>', '\n' ) ) # For TextBox
            elif var: var.set( currentRowData[j] ) # For Entries
            else: dataWidget.configure( text=currentRowData[j] ) # For Labels

        self.current_row = row

        # Update button states
        self.setStatus() # Clear it
        self.topButton.configure( state=tk.NORMAL if row>1 else tk.DISABLED )
        self.bottomButton.configure( state=tk.NORMAL if row<self.numDataRows else tk.DISABLED )
        self.moveUpButton.configure( state=tk.NORMAL if row>1 else tk.DISABLED )
        self.moveDownButton.configure( state=tk.NORMAL if row<self.numDataRows else tk.DISABLED )
        self.deleteRowButton.configure( state=tk.NORMAL if self.numDataRows else tk.DISABLED )
        self.checkCurrentDisplayedRowData() # Update field states
    # end of TSVEditWindowAddon.gotoRow function


    def updateShownBCV( self, newReferenceVerseKey, originator=None ) -> None:
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        If newReferenceVerseKey is None: clears the window

        Otherwise, basically does the following steps (depending on the contextViewMode):
            1/ Saves any changes in the editor to self.bookText
            2/ If we've changed book:
                if changes to self.bookText, save them to disk
                load the new book text
            3/ Load the appropriate verses into the editor according to the contextViewMode.
        """
        vPrint( 'Never', debuggingThisModule, f"TSVEditWindowAddon.updateShownBCV( {newReferenceVerseKey}, {originator} ) from {self.currentVerseKey} for {self.moduleID}" )
        # vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.updateShownBCV( {}, {} ) from {} for".format( newReferenceVerseKey, originator, self.currentVerseKey ), self.moduleID )
            #vPrint( 'Quiet', debuggingThisModule, "contextViewMode", self._contextViewMode )
            #assert self._formatViewMode == 'Unformatted' # Only option done so far

        # Check the book
        if not newReferenceVerseKey: return
        BBB, C, V = newReferenceVerseKey.getBCV()
        # print( f"Was given {BBB} {C}:{V}" )
        if BBB != self.BBB: # Just ignore other book references for now XXX
            print( f"  Ref {newReferenceVerseKey} is not in our {self.BBB} book" )
            return
        # Nothing to do if we're already at that BCV ref
        if newReferenceVerseKey == self.currentVerseKey:
            # print( f"  We are already at that ref—don't mess with our rows" )
            return

        # Go through all our rows to find if this verse occurs in the table
        # NOTE: The present code doesn't change the row if there's no entry for that BCV ref
        #       What would the user want here?
        for j, row in enumerate( self.tsvTable ):
            if str(row[self.chapterColumn]) == newReferenceVerseKey.C \
            and str(row[self.verseColumn]) == newReferenceVerseKey.V:
                self.rowNumberVar.set( j )
                self.gotoRow( notifyMain=False ) # Don't notify up or it gets recursive
                break
    # end of TSVEditWindowAddon.updateShownBCV function


    def setCurrentVerseKey( self, newVerseKey ) -> None:
        """
        Called to set the current verse key.

        Note that newVerseKey can be None.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, _("setCurrentVerseKey( {} )").format( newVerseKey ) )
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
    # end of BibleResourceWindowAddon.setCurrentVerseKey


    def gotoTop( self, event=None ) -> None:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, f"gotoTop( {event} )…" )
        assert self.current_row > 1
        self.rowNumberVar.set( 1 )
        self.gotoRow() # Refresh
    # end of TSVEditWindowAddon.gotoTop function

    def gotoBottom( self, event=None ) -> None:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, f"gotoBottom( {event} )…" )
        assert self.current_row < self.numDataRows
        self.rowNumberVar.set( self.numDataRows )
        self.gotoRow() # Refresh
    # end of TSVEditWindowAddon.gotoBottom function


    def doMoveUp( self, event=None ) -> None:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, f"doMoveUp( {event} )…" )
        assert self.current_row > 1
        currentRowData = self.retrieveCurrentRowData( updateTable=False ) # in case current row was edited
        self.tsvTable[self.current_row-1], self.tsvTable[self.current_row] = currentRowData, self.tsvTable[self.current_row-1]
        self.rowNumberVar.set( self.current_row - 1 ) # Stay on the same (moved-up) row
        self.gotoRow() # Refresh
    # end of TSVEditWindowAddon.doMoveUp function

    def doMoveDown( self, event=None ) -> None:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, f"doMoveDown( {event} )…" )
        assert self.current_row < self.numDataRows
        currentRowData = self.retrieveCurrentRowData( updateTable=False ) # in case current row was edited
        self.tsvTable[self.current_row], self.tsvTable[self.current_row+1] = self.tsvTable[self.current_row+1], currentRowData
        self.rowNumberVar.set( self.current_row + 1 ) # Stay on the same (moved-up) row
        self.gotoRow() # Refresh
    # end of TSVEditWindowAddon.doMoveDown function

    def doAddBefore( self, event=None ) -> None:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, f"doAddBefore( {event} )…" )
        currentRowData = self.retrieveCurrentRowData( updateTable=True ) # in case current row was edited
        newRowData = currentRowData.copy()
        newRowData[self.idColumn] = self.generateID()
        newRowData[self.occurenceColumn] = '1'
        newRowData[self.supportReferenceColumn] = newRowData[self.origQuoteColumn] = ''
        newRowData[self.GLQuoteColumn] = newRowData[self.occurrenceNoteColumn] = ''
        self.tsvTable.insert( self.current_row, newRowData )
        self.numDataRows += 1
        self.gotoRow( force=True ) # Stay on the same row number (which is the new row), but cause refresh
    # end of TSVEditWindowAddon.doAddBefore function

    def doAddAfter( self, event=None ) -> None:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, f"doAddAfter( {event} )…" )
        currentRowData = self.retrieveCurrentRowData( updateTable=True ) # in case current row was edited
        newRowData = currentRowData.copy()
        newRowData[self.idColumn] = self.generateID()
        newRowData[self.occurenceColumn] = '1'
        newRowData[self.supportReferenceColumn] = newRowData[self.origQuoteColumn] = ''
        newRowData[self.GLQuoteColumn] = newRowData[self.occurrenceNoteColumn] = ''
        self.tsvTable.insert( self.current_row+1, newRowData )
        self.numDataRows += 1
        self.rowNumberVar.set( self.current_row + 1 ) # Go to the new (=next) row
        self.gotoRow() # Refresh
    # end of TSVEditWindowAddon.doAddAfter function

    def doDeleteRow( self, event=None ) -> None:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, f"doDeleteRow( {event} )…" )
        assert self.numDataRows
        self.deletedRow = self.tsvTable.pop( self.current_row )
        self.numDataRows -= 1
        self.gotoRow( force=True ) # Stay on the same row, but cause refresh
    # end of TSVEditWindowAddon.doDeleteRow function


    def retrieveCurrentRowData( self, updateTable:bool ) -> List[str]:
        """
        Get the data out of the displayed boxes and return it.

        If updateTable is True, also put any changed data back into the table.
        """
        vPrint( 'Never', debuggingThisModule, f"retrieveCurrentRowData( uT={updateTable}) for {self.current_row}…" )

        if not self.current_row: return # Still setting up -- nothing to do here yet

        # Extract the data out of the various Label, Entry, and TextBox widgets
        retrievedRowData = [''] * self.num_columns # Create blank row first
        for j, (var,dataWidget) in enumerate( self.widgets ):
            # print( f"{j}/ {dir(dataWidget) if j==0 else dataWidget.winfo_name}")
            if var=='TB': retrievedRowData[j] = self.getAllText().replace( '\n', '<br>' ) # For TextBox
            elif var: retrievedRowData[j] = var.get() # For Entries
            else: retrievedRowData[j] = dataWidget['text'] # For Labels
        assert len(retrievedRowData) == self.num_columns
        # vPrint( 'Quiet', debuggingThisModule, f" got retrieveCurrentRowData: {retrievedRowData}" )

        # Now we can replace that row in the table (if requested)
        vPrint( 'Never', debuggingThisModule, f"  Row {self.current_row} has changed: {retrievedRowData != self.tsvTable[self.current_row]}" )
        if updateTable and retrievedRowData != self.tsvTable[self.current_row]:
            vPrint( 'Quiet', debuggingThisModule, f"\nRow {self.current_row}: replace {self.tsvTable[self.current_row]}\n   with {retrievedRowData}" )
            self.tsvTable[self.current_row] = retrievedRowData

        return retrievedRowData
    # end of TSVEditWindowAddon.retrieveCurrentRowData


    def generateID( self ) -> str:
        """
        Generate 4-character random ID (starting with a lowercase letter)
        Theoretically they only have to be unique within a verse,
            but we make them unique within the whole table/file.
        """
        vPrint( 'Quiet', debuggingThisModule, "generateID()…" )
        while True:
            newID = random.choice( 'abcdefghijklmnopqrstuvwxyz') \
                    + random.choice( 'abcdefghijklmnopqrstuvwxyz0123456789' ) \
                    + random.choice( 'abcdefghijklmnopqrstuvwxyz0123456789' ) \
                    + random.choice( 'abcdefghijklmnopqrstuvwxyz0123456789' )
            if newID not in self.allIDs:
                self.allIDs.add( newID )
                return newID
    # end of TSVEditWindowAddon.generateID function


    def checkCurrentDisplayedRowData( self, event=None ) -> bool:
        """
        Called when focus changes

        Updates widget colours.
        """
        vPrint( 'Quiet', debuggingThisModule, "checkCurrentDisplayedRowData()…" )
        # if self.loading: return

        currentRowData = self.retrieveCurrentRowData( updateTable=False )

        self.maxChaptersThisBook = self.getNumChapters( self.BBB )
        currentC = self.currentVerseKey.getChapterNumber()
        self.maxVersesThisChapter = self.getNumVerses( self.BBB, currentC )

        errorList = []
        for j, (fieldData,(var,widget)) in enumerate( zip( currentRowData, self.widgets ) ):
            haveError = False
            if j == self.bookColumn: # Label
                if not fieldData:
                    errorList.append( f"Missing book (name) field: '{fieldData}'" ); haveError = True
                elif fieldData != self.thisBookUSFMCode:
                    errorList.append( f"Wrong '{fieldData}' book (name) field -- expected '{self.thisBookUSFMCode}'" ); haveError = True
            elif j == self.chapterColumn: # Entry
                if not fieldData:
                    errorList.append( f"Missing chapter (number) field" ); haveError = True
                elif fieldData not in ('front',) and not fieldData.isdigit():
                    errorList.append( f"Invalid chapter (number) field: '{fieldData}'" ); haveError = True
                elif fieldData.isdigit(): # We expect chapter numbers to increment by 1
                    intC = int( fieldData )
                    print( "self.maxChaptersThisBook", repr(self.maxChaptersThisBook) )
                    if intC < -1:
                        errorList.append( f"Invalid chapter (number) field: '{fieldData}'" ); haveError = True
                    elif intC > self.maxChaptersThisBook:
                        errorList.append( f"Invalid chapter (number) field: '{fieldData}' in {self.BBB} with {self.maxChaptersThisBook} (max) chapters" ); haveError = True
                    else:
                        lastC = nextC = None
                        if self.current_row > 1: lastC = self.tsvTable[self.current_row-1][self.chapterColumn]
                        if self.current_row < self.numDataRows: nextC = self.tsvTable[self.current_row+1][self.chapterColumn]
                        if lastC and lastC.isdigit() and intC not in (int(lastC), int(lastC)+1):
                            errorList.append( f"Unexpected chapter (number) field: '{fieldData}' after {lastC}" ); haveError = True
                        elif nextC and nextC.isdigit() and intC not in (int(nextC), int(nextC)-1):
                            errorList.append( f"Unexpected chapter (number) field: '{fieldData}' before {nextC}" ); haveError = True
            elif j == self.verseColumn: # Entry
                if not fieldData:
                    errorList.append( f"Missing verse (number) field" ); haveError = True
                elif fieldData not in ('intro',) and not fieldData.isdigit():
                    errorList.append( f"Invalid verse (number) field: '{fieldData}'" ); haveError = True
                if fieldData == 'intro' and currentRowData[self.chapterColumn] != 'front':
                    errorList.append( f"Unexpected verse (number) field: '{fieldData}' when Chapter is '{currentRowData[self.chapterColumn]}'" ); haveError = True
                elif fieldData.isdigit(): # We expect verse numbers to increment
                    intV = int( fieldData )
                    print( "self.maxVersesThisChapter", repr(self.maxVersesThisChapter) )
                    if intV < 0:
                        errorList.append( f"Invalid verse (number) field: '{fieldData}'" ); haveError = True
                    elif intV > self.maxVersesThisChapter:
                        errorList.append( f"Invalid verse (number) field: '{fieldData}' in {self.BBB} {currentC} with {self.maxVersesThisChapter} (max) verses" ); haveError = True
                    else:
                        lastV = nextV = None
                        if self.current_row > 1: lastV = self.tsvTable[self.current_row-1][self.verseColumn]
                        if self.current_row < self.numDataRows: nextV = self.tsvTable[self.current_row+1][self.verseColumn]
                        if lastV and lastV.isdigit() and intV < int(lastV):
                            errorList.append( f"Unexpected verse (number) field: '{fieldData}' after {lastV}" ); haveError = True
                        elif nextV and nextV.isdigit() and intV > int(nextV):
                            errorList.append( f"Unexpected verse (number) field: '{fieldData}' before {nextV}" ); haveError = True
            elif j == self.idColumn:
                if len(fieldData) < 4:
                    errorList.append( f"ID field '{fieldData}' is too short" )
                    anyErrors = True
            elif j == self.supportReferenceColumn: # Label
                for badText in ('...','  ',' … '):
                    if badText in fieldData:
                        errorList.append( f"Unexpected '{badText}' in '{fieldData}'" ); haveError = True
                if fieldData:
                    if fieldData[0] == ' ':
                        errorList.append( f"Unexpected leading space(s) in '{fieldData}'" ); haveError = True
                    if fieldData[-1] == ' ':
                        errorList.append( f"Unexpected trailing space(s) in '{fieldData}'" ); haveError = True
            elif j == self.origQuoteColumn: # Entry
                for badText in ('...','  ',' … '):
                    if badText in fieldData:
                        errorList.append( f"Unexpected '{badText}' in '{fieldData}'" ); haveError = True
                if fieldData:
                    if fieldData[0] == ' ':
                        errorList.append( f"Unexpected leading space(s) in '{fieldData}'" ); haveError = True
                    if fieldData[-1] == ' ':
                        errorList.append( f"Unexpected trailing space(s) in '{fieldData}'" ); haveError = True
            elif j == self.occurenceColumn: # Entry
                if not fieldData:
                    errorList.append( f"Missing occurrence (number) field" ); haveError = True
                elif currentRowData[self.origQuoteColumn] and fieldData not in '123456789':
                    errorList.append( f"Unexpected occurrence (number) field: '{fieldData}'" ); haveError = True
                elif not currentRowData[self.origQuoteColumn] and fieldData != '0':
                    errorList.append( f"Unexpected occurrence (number) field: '{fieldData}'" ); haveError = True
            elif j == self.GLQuoteColumn: # Entry
                for badText in ('...','  ',' … '):
                    if badText in fieldData:
                        errorList.append( f"Unexpected '{badText}' in '{fieldData}'" ); haveError = True
                if fieldData:
                    if fieldData[0] == ' ':
                        errorList.append( f"Unexpected leading space(s) in '{fieldData}'" ); haveError = True
                    if fieldData[-1] == ' ':
                        errorList.append( f"Unexpected trailing space(s) in '{fieldData}'" ); haveError = True
            elif j == self.occurrenceNoteColumn: # TextBox
                for badText in ('...','  ',' … '):
                    if badText in fieldData:
                        errorList.append( f"Unexpected '{badText}' in '{fieldData}'" ); haveError = True
                for lChar,rChar in (('(',')'),('[',']'),('{','}')):
                    lCount, rCount = fieldData.count(lChar), fieldData.count(rChar)
                    if lCount != rCount:
                        errorList.append( f"Unmatched {lCount} '{lChar}' chars vs {rCount} '{rChar}' chars in '{fieldData}'" ); haveError = True
                if fieldData:
                    if fieldData[0] == ' ':
                        errorList.append( f"Unexpected leading space(s) in '{fieldData}'" ); haveError = True
                    if fieldData[-1] == ' ':
                        errorList.append( f"Unexpected trailing space(s) in '{fieldData}'" ); haveError = True
            if haveError:
                if var == 'TB':
                    widget.configure( bg='orange' )
                else: # ttk Label or Entry
                    widget.configure( style='bad.TLabel' )
                anyErrors = True
            else: # no error
                if var == 'TB':
                    widget.configure( bg='gold2' )
                else: # ttk Label or Entry
                    widget.configure( style='good.TLabel' )
        currentRowData = self.retrieveCurrentRowData( updateTable=False )

        if errorList:
            self.setErrorStatus( errorList[0] )
            return True
        self.setStatus() # Clear it
        return False
    # end of TSVEditWindowAddon.checkCurrentDisplayedRowData function


    def validateTSVTable( self ) -> int:
        """
        """
        vPrint( 'Quiet', debuggingThisModule, "validateTSVTable()…" )
        num_errors = 0
        self.allIDs = set()
        for j, row in enumerate( self.tsvTable[1:], start=2 ):
            bkCode, C, V, thisID = row[self.bookColumn], row[self.chapterColumn], row[self.verseColumn], row[self.idColumn]
            if not bkCode:
                print( f"  Missing USFM book id (expected '{self.thisBookUSFMCode}') in row {j}: {row}" )
                num_errors += 1
            elif bkCode != self.thisBookUSFMCode:
                print( f"  Bad USFM book id '{bkCode}' (expected '{self.thisBookUSFMCode}') in row {j}: {row}" )
                num_errors += 1
            if not C:
                print( f"  Missing chapter field in row {j}: {row}" )
                num_errors += 1
            if not V:
                print( f"  Missing verse field in row {j}: {row}" )
                num_errors += 1
            if thisID in self.allIDs:
                print( f"  Already had ID='{thisID}'" )
                num_errors += 1
            else:
                self.allIDs.add( thisID )
        return num_errors
    # end of TSVEditWindowAddon.validateTSVTable()





    def createEditorKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.createEditorKeyboardBindings()" )

        for name,commandFunction in ( #('Paste',self.doPaste), ('Cut',self.doCut),
                             #('Undo',self.doUndo), ('Redo',self.doRedo),
                             ('Find',self.doBoxFind), ('Refind',self.doBoxRefind),
                             ('Save',self.doSave),
                             ('ShowMain',self.doShowMainWindow),
                             ):
            #vPrint( 'Quiet', debuggingThisModule, "TEW CheckLoop", (name,self.parentApp.keyBindingDict[name][0],self.parentApp.keyBindingDict[name][1],) )
            assert (name,self.parentApp.keyBindingDict[name][0],) not in self.myKeyboardBindingsList
            if name in self.parentApp.keyBindingDict:
                for keyCode in self.parentApp.keyBindingDict[name][1:]:
                    #vPrint( 'Quiet', debuggingThisModule, "  TEW Bind {} for {}".format( repr(keyCode), repr(name) ) )
                    self.textBox.bind( keyCode, commandFunction )
                    if BibleOrgSysGlobals.debugFlag:
                        assert keyCode not in self.myKeyboardShortcutsList
                        self.myKeyboardShortcutsList.append( keyCode )
                self.myKeyboardBindingsList.append( (name,self.parentApp.keyBindingDict[name][0],) )
            else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of TSVEditWindowAddon.createEditorKeyboardBindings()


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.createMenuBar()" )

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        fileMenu.add_command( label=_('Save'), underline=0, command=self.doSave, accelerator=self.parentApp.keyBindingDict[_('Save')][0] )
        fileMenu.add_command( label=_('Save as…'), underline=5, command=self.doSaveAs )
        #fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu, tearoff=False )
        #subfileMenuImport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Import'), underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu, tearoff=False )
        #subfileMenuExport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label=_('HTML'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Export'), underline=0, menu=subfileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] )

        editMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Undo'), underline=0, command=self.doUndo, accelerator=self.parentApp.keyBindingDict[_('Undo')][0] )
        editMenu.add_command( label=_('Redo'), underline=0, command=self.doRedo, accelerator=self.parentApp.keyBindingDict[_('Redo')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Cut'), underline=2, command=self.doCut, accelerator=self.parentApp.keyBindingDict[_('Cut')][0] )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        editMenu.add_command( label=_('Paste'), underline=0, command=self.doPaste, accelerator=self.parentApp.keyBindingDict[_('Paste')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Delete'), underline=0, command=self.doDelete )
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=self.parentApp.keyBindingDict[_('Line')][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=self.parentApp.keyBindingDict[_('Refind')][0] )
        searchMenu.add_command( label=_('Replace…'), underline=0, command=self.doBoxFindReplace )
        #searchMenu.add_separator()
        #searchMenu.add_command( label=_('Grep…'), underline=0, command=self.onGrep )

##        gotoMenu = tk.Menu( self.menubar )
##        self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
##        gotoMenu.add_command( label=_('Previous book'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label=_('Next book'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label=_('Previous chapter'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label=_('Next chapter'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label=_('Previous verse'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label=_('Next verse'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_separator()
##        gotoMenu.add_command( label=_('Forward'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label=_('Backward'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_separator()
##        gotoMenu.add_command( label=_('Previous list item'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label=_('Next list item'), underline=0, command=self.notWrittenYet )
##        gotoMenu.add_separator()
##        gotoMenu.add_command( label=_('Book'), underline=0, command=self.notWrittenYet )

        viewMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label=_('View'), underline=0 )
        viewMenu.add_command( label=_('Larger text'), underline=0, command=self.OnFontBigger )
        viewMenu.add_command( label=_('Smaller text'), underline=1, command=self.OnFontSmaller )
        viewMenu.add_separator()
        viewMenu.add_checkbutton( label=_('Status bar'), underline=9, variable=self._showStatusBarVar, command=self.doToggleStatusBar )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label=_('Tools'), underline=0 )
        toolsMenu.add_command( label=_('Options…'), underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label=_('Window'), underline=0 )
        windowMenu.add_command( label=_('Bring in'), underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=self.parentApp.keyBindingDict[_('ShowMain')][0] )

        if BibleOrgSysGlobals.debugFlag:
            debugMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=debugMenu, label=_('Debug'), underline=0 )
            #debugMenu.add_command( label=_('View settings…'), underline=5, command=self.doViewSettings )
            #debugMenu.add_separator()
            debugMenu.add_command( label=_('View log…'), underline=5, command=self.doViewLog )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label=_('Help'), underline=0 )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=self.parentApp.keyBindingDict[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=self.parentApp.keyBindingDict[_('About')][0] )
    # end of TSVEditWindowAddon.createMenuBar


    def setWindowGroup( self, newGroup ):
        """
        Set the Bible group for the window.

        Ideally we wouldn't need this info to be stored in both of these class variables.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, _("BibleWindowAddon.setWindowGroup( {} ) for {}").format( newGroup, self.genericWindowType ) )
            assert newGroup==DEFAULT or newGroup in BIBLE_GROUP_CODES

        self._groupCode = BIBLE_GROUP_CODES[0] if newGroup==DEFAULT else newGroup
        # self._groupRadioVar.set( BIBLE_GROUP_CODES.index( self._groupCode ) + 1 )
    # end of BibleWindowAddon.setWindowGroup


    def createContextMenu( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.createContextMenu()" )

        self.contextMenu = tk.Menu( self, tearoff=False )
        self.contextMenu.add_command( label=_('Cut'), underline=2, command=self.doCut, accelerator=self.parentApp.keyBindingDict[_('Cut')][0] )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        self.contextMenu.add_command( label=_('Paste'), underline=0, command=self.doPaste, accelerator=self.parentApp.keyBindingDict[_('Paste')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
    # end of TSVEditWindowAddon.createContextMenu


    #def showContextMenu( self, e):
        #self.contextMenu.post( e.x_root, e.y_root )
    ## end of TSVEditWindowAddon.showContextMenu


    #def createToolBar( self ):
        #toolbar = Frame( self, cursor='hand2', relief=tk.SUNKEN ) # bd=2
        #toolbar.pack( side=tk.BOTTOM, fill=tk.X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=tk.RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=tk.LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=tk.LEFT )
    ## end of TSVEditWindowAddon.createToolBar


    def refreshTitle( self ):
        """
        Refresh the title of the text edit window,
            put an asterisk if it's modified.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.refreshTitle()" )

        self.title( "{}[{}] {} ({}) {}".format( '*' if self.modified() else '',
                                            _("Text"), self.filename, self.folderpath, self.editStatus ) )
        self.refreshTitleContinue()
    # end if TSVEditWindowAddon.refreshTitle

    def refreshTitleContinue( self ):
        """
        Check if an autosave is needed,
            and schedule the next refresh.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.refreshTitleContinue()" )

        self.after( REFRESH_TITLE_TIME, self.refreshTitle ) # Redo it so we can put up the asterisk if the text is changed
        try:
            if self.autosaveTime and self.modified() and not self.autosaveScheduled:
                self.after( self.autosaveTime, self.doAutosave ) # Redo it so we can put up the asterisk if the text is changed
                self.autosaveScheduled = True
        except AttributeError:
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                vPrint( 'Quiet', debuggingThisModule, "Autosave not set-up properly yet" )
    # end if TSVEditWindowAddon.refreshTitleContinue


    def OnFontBigger( self ):
        """
        Make the font one point bigger
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.OnFontBigger()" )

        size = self.customFont['size']
        self.customFont.configure( size=size+1 )
    # end if TSVEditWindowAddon.OnFontBigger

    def OnFontSmaller( self ):
        """
        Make the font one point smaller
        """
        vPrint( 'Verbose', debuggingThisModule, "TSVEditWindowAddon.OnFontSmaller()…" )

        size = self.customFont['size']
        self.customFont.configure( size=size-1 )
    # end if TSVEditWindowAddon.OnFontSmaller


    def getAllText( self ):
        """
        Returns all the text as a string.
        """
        vPrint( 'Never', debuggingThisModule, "TSVEditWindowAddon.getAllText()…" )

        allText = self.textBox.get( tkSTART, tk.END+'-1c' )
        #if self.markMultipleSpacesFlag:
        allText = allText.replace( MULTIPLE_SPACE_SUBSTITUTE, ' ' )
        #if self.markTrailingSpacesFlag:
        allText = allText.replace( TRAILING_SPACE_SUBSTITUTE, ' ' )

        vPrint( 'Never', debuggingThisModule, f"  getAllText returning ({len(allText)}) {allText!r}" )
        return allText
    # end of TSVEditWindowAddon.getAllText


    def makeAutocompleteBox( self ):
        """
        Create a pop-up listbox in order to be able to display possible autocomplete words.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.makeAutocompleteBox()" )
            assert self.autocompleteBox is None

        # Create the pop-up listbox
        x, y, cx, cy = self.textBox.bbox( tk.INSERT ) # Get canvas coordinates
        topLevel = tk.Toplevel( self.textBox.master )
        topLevel.wm_overrideredirect(1) # Don't display window decorations (close button, etc.)
        topLevel.wm_geometry( '+{}+{}' \
            .format( x + self.textBox.winfo_rootx() + 2, y + cy + self.textBox.winfo_rooty() ) )
        frame = tk.Frame( topLevel, highlightthickness=1, highlightcolor='darkgreen' )
        frame.pack( fill=tk.BOTH, expand=tk.YES )
        autocompleteScrollbar = tk.Scrollbar( frame, highlightthickness=0 )
        autocompleteScrollbar.pack( side=tk.RIGHT, fill=tk.Y )
        self.autocompleteBox = tk.Listbox( frame, highlightthickness=0,
                                    relief='flat',
                                    yscrollcommand=autocompleteScrollbar.set,
                                    width=20, height=NUM_AUTOCOMPLETE_POPUP_LINES )
        autocompleteScrollbar.configure( command=self.autocompleteBox.yview )
        self.autocompleteBox.pack( side=tk.LEFT, fill=tk.BOTH )
        #self.autocompleteBox.select_set( '0' )
        #self.autocompleteBox.focus()
        self.autocompleteBox.bind( '<KeyPress>', self.OnAutocompleteChar )
        self.autocompleteBox.bind( '<Double-Button-1>', self.doAcceptAutocompleteSelection )
        self.autocompleteBox.bind( '<FocusOut>', self.removeAutocompleteBox )
    # end of TSVEditWindowAddon.makeAutocompleteBox


    def OnAutocompleteChar( self, event ):
        """
        Used by autocomplete routines in onTextChange.

        Handles key presses entered into the pop-up word selection (list) box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.OnAutocompleteChar( {!r}, {!r} )".format( event.char, event.keysym ) )
            assert self.autocompleteBox is not None

        #if event.keysym == 'ESC':
        #if event.char==' ' or event.char in self.autocompleteWordChars:
            #self.textBox.insert( tk.INSERT, event.char ) # Causes onTextChange which reassesses
        if event.keysym == 'BackSpace':
            row, column = self.textBox.index(tk.INSERT).split('.')
            column = str( int(column) - 1 )
            self.textBox.delete( row + '.' + column, tk.INSERT ) # parameters are fromPoint, toPoint
        elif event.keysym == 'Delete':
            row, column = self.textBox.index(tk.INSERT).split('.')
            column = str( int(column) + 1 ) # Only works as far as the end of the line (won't delete a \n)
            # Change the call below to a single parameter if you want it to work across lines
            self.textBox.delete( tk.INSERT, row + '.' + column ) # parameters are fromPoint, toPoint
        elif event.keysym == 'Return':
            acceptAutocompleteSelection( self, includeTrailingSpace=False )
        #elif event.keysym in ( 'Up', 'Down', 'Shift_R', 'Shift_L',
                              #'Control_L', 'Control_R', 'Alt_L',
                              #'Alt_R', 'parenleft', 'parenright'):
            #pass
        elif event.keysym == 'Escape':
            self.removeAutocompleteBox()
        #elif event.keysym in ( 'Delete', ): pass # Just ignore these keypresses
        elif event.char:
            #if event.char in '.,': acceptAutocompleteSelection( self, includeTrailingSpace=False )
            self.textBox.insert( tk.INSERT, event.char ) # Causes onTextChange which reassesses
                                    #+ (' ' if event.char in ',' else '') )
    # end of TSVEditWindowAddon.OnAutocompleteChar


    def doAcceptAutocompleteSelection( self, event=None ):
        """
        Used by autocomplete routines in onTextChange.

        Gets the chosen word and inserts the end of it into the text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doAcceptAutocompleteSelection({} )".format( event ) )
            assert self.autocompleteBox is not None

        acceptAutocompleteSelection( self, includeTrailingSpace=False )
    # end of TSVEditWindowAddon.doAcceptAutocompleteSelection


    def removeAutocompleteBox( self, event=None ):
        """
        Remove the pop-up Listbox (in a Frame in a Toplevel) when it's no longer required.

        Used by autocomplete routines in onTextChange.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.removeAutocompleteBox( {} )".format( event ) )
            assert self.autocompleteBox is not None

        self.textBox.focus()
        self.autocompleteBox.master.master.destroy() # master is Frame, master.master is Toplevel
        self.autocompleteBox = None
    # end of TSVEditWindowAddon.removeAutocompleteBox


    def onTextChange( self, result, *args ):
        """
        Called (set-up as a call-back function) whenever the text box cursor changes
            either with a mouse click or arrow keys.

        Checks to see if they have moved to a new chapter/verse,
            and if so, informs the parent app.
        """
        if self.onTextNoChangeID:
            self.after_cancel( self.onTextNoChangeID ) # Cancel any delayed checks which are scheduled
            self.onTextNoChangeID = None
        if self.loading: return # So we don't get called a million times for nothing
        return # temp XXXX ...........................
                # PRevents extra double spaces being inserted!!! WHY WHY
        vPrint( 'Quiet', debuggingThisModule, f"TSVEditWindowAddon.onTextChange( {result!r}, {args} )…" )

        #if 0: # Get line and column info
            #lineColumn = self.textBox.index( tk.INSERT )
            #vPrint( 'Quiet', debuggingThisModule, "lc", repr(lineColumn) )
            #line, column = lineColumn.split( '.', 1 )
            #vPrint( 'Quiet', debuggingThisModule, "l,c", repr(line), repr(column) )

        #if 0: # get formatting tag info
            #tagNames = self.textBox.tag_names( tk.INSERT )
            #tagNames2 = self.textBox.tag_names( lineColumn )
            #tagNames3 = self.textBox.tag_names( tk.INSERT + ' linestart' )
            #tagNames4 = self.textBox.tag_names( lineColumn + ' linestart' )
            #tagNames5 = self.textBox.tag_names( tk.INSERT + ' linestart+1c' )
            #tagNames6 = self.textBox.tag_names( lineColumn + ' linestart+1c' )
            #vPrint( 'Quiet', debuggingThisModule, "tN", tagNames )
            #if tagNames2!=tagNames or tagNames3!=tagNames or tagNames4!=tagNames or tagNames5!=tagNames or tagNames6!=tagNames:
                #vPrint( 'Quiet', debuggingThisModule, "tN2", tagNames2 )
                #vPrint( 'Quiet', debuggingThisModule, "tN3", tagNames3 )
                #vPrint( 'Quiet', debuggingThisModule, "tN4", tagNames4 )
                #vPrint( 'Quiet', debuggingThisModule, "tN5", tagNames5 )
                #vPrint( 'Quiet', debuggingThisModule, "tN6", tagNames6 )
                #halt

        #if 0: # show various mark strategies
            #mark1 = self.textBox.mark_previous( tk.INSERT )
            #mark2 = self.textBox.mark_previous( lineColumn )
            #mark3 = self.textBox.mark_previous( tk.INSERT + ' linestart' )
            #mark4 = self.textBox.mark_previous( lineColumn + ' linestart' )
            #mark5 = self.textBox.mark_previous( tk.INSERT + ' linestart+1c' )
            #mark6 = self.textBox.mark_previous( lineColumn + ' linestart+1c' )
            #vPrint( 'Quiet', debuggingThisModule, "mark1", mark1 )
            #if mark2!=mark1:
                #vPrint( 'Quiet', debuggingThisModule, "mark2", mark1 )
            #if mark3!=mark1 or mark4!=mark1 or mark5!=mark1 or mark6!=mark1:
                #vPrint( 'Quiet', debuggingThisModule, "mark3", mark3 )
                #if mark4!=mark3:
                    #vPrint( 'Quiet', debuggingThisModule, "mark4", mark4 )
                #vPrint( 'Quiet', debuggingThisModule, "mark5", mark5 )
                #if mark6!=mark5:
                    #vPrint( 'Quiet', debuggingThisModule, "mark6", mark6 )


        if self.textBox.edit_modified():
            #if 1:
                #vPrint( 'Quiet', debuggingThisModule, 'args[0]', repr(args[0]) )
                #vPrint( 'Quiet', debuggingThisModule, 'args[1]', repr(args[1]) )
                #try: vPrint( 'Quiet', debuggingThisModule, 'args[2]', repr(args[2]) ) # Can be multiple characters (after autocomplete)
                #except IndexError: vPrint( 'Quiet', debuggingThisModule, "No args[2]" ) # when deleting

            # Handle substituted space characters
            saveIndex = self.textBox.index( tk.INSERT ) # Remember where the cursor was
            if args[0]=='insert' and args[1]=='insert':
                before1After1 = self.textBox.get( tk.INSERT+'-2c', tk.INSERT+'+1c' ) # Get the characters before and after
                if len(before1After1) == 3: before1, newChar, after1 = before1After1
                else: before1 = newChar = after1 = '' # this can happen sometimes
                #vPrint( 'Quiet', debuggingThisModule, '3', repr(before1), repr(newChar), repr(after1) )
                # FALSE AFTER AUTOCOMPLETE assert newChar == args[2] # Char before cursor should be char just typed
                if self.markMultipleSpacesFlag and newChar == ' ': # Check if we've typed multiple spaces
                    # NOTE: We DON'T make this into a TRAILING_SPACE_SUBSTITUTE -- too disruptive during regular typing
                    #elf.textBox.get( tk.INSERT+'-{}c'.format( maxCount ), tk.INSERT )
                    if before1 in ALL_POSSIBLE_SPACE_CHARS:
                        self.textBox.delete( tk.INSERT+'-2c', tk.INSERT ) # Delete previous space/substitute plus new space
                        self.textBox.insert( tk.INSERT, DOUBLE_SPACE_SUBSTITUTE ) # Replace with substitute
                    else: # check after the cursor also
                        nextChar = self.textBox.get( tk.INSERT, tk.INSERT+'+1c' ) # Get the following character
                        if nextChar in ALL_POSSIBLE_SPACE_CHARS:
                            self.textBox.delete( tk.INSERT+'-1c', tk.INSERT+'+1c' ) # Delete chars around cursor
                            self.textBox.insert( tk.INSERT, DOUBLE_SPACE_SUBSTITUTE ) # Replace with substitute
                            self.textBox.mark_set( tk.INSERT, saveIndex ) # Put the cursor back
                elif newChar not in ' \n\r': # Check if we followed a trailing space substitute
                    if before1 == TRAILING_SPACE_SUBSTITUTE:
                        self.textBox.delete( tk.INSERT+'-2c', tk.INSERT ) # Delete trailing space substitute plus new char
                        self.textBox.insert( tk.INSERT, ' '+newChar ) # Replace with proper space and new char
                    before3After2 = self.textBox.get( tk.INSERT+'-3c', tk.INSERT+'+2c' ) # Get the pairs of characters before and after
                    if before1 == MULTIPLE_SPACE_SUBSTITUTE and before3After2[0] not in ALL_POSSIBLE_SPACE_CHARS:
                        self.textBox.delete( tk.INSERT+'-2c', tk.INSERT ) # Delete previous space substitute plus new char
                        self.textBox.insert( tk.INSERT, ' '+newChar ) # Replace with normal space plus new char
                    try:
                        if before3After2[3] == MULTIPLE_SPACE_SUBSTITUTE and before3After2[4] not in ALL_POSSIBLE_SPACE_CHARS:
                            self.textBox.delete( tk.INSERT, tk.INSERT+'+1c' ) # Delete following space substitute
                            self.textBox.insert( tk.INSERT, ' ' ) # Replace with normal space
                            self.textBox.mark_set( tk.INSERT, saveIndex ) # Put the cursor back
                    except IndexError: pass # Could be working at end of file
                #previousText = self.getSubstitutedChararactersBeforeCursor()
            elif args[0] == 'delete':
                #if args[1] == 'insert': # we used the delete key
                    #vPrint( 'Quiet', debuggingThisModule, "Deleted" )
                #elif args[1] == 'insert-1c': # we used the backspace key
                    #vPrint( 'Quiet', debuggingThisModule, "Backspaced" )
                #else: vPrint( 'Quiet', debuggingThisModule, "What's this!", repr(args[1]) )
                chars4 = self.textBox.get( tk.INSERT+'-2c', tk.INSERT+'+2c' ) # Get the characters (now forced together) around the cursor
                if len(chars4) == 4: before2, before1, after1, after2 = chars4
                else: before2 = before1 = after1 = after2 = '' # not sure about this
                if before1 == ' ' and after1 == '\n': # Put trailing substitute
                    if self.markTrailingSpacesFlag:
                        self.textBox.delete( tk.INSERT+'-1c', tk.INSERT ) # Delete the space
                        self.textBox.insert( tk.INSERT, TRAILING_SPACE_SUBSTITUTE ) # Replace with trailing substitute
                elif before1 in ALL_POSSIBLE_SPACE_CHARS and after1 in ALL_POSSIBLE_SPACE_CHARS: # Put multiple substitute
                    if self.markMultipleSpacesFlag:
                        self.textBox.delete( tk.INSERT+'-1c', tk.INSERT+'+1c' ) # Delete chars around cursor
                        self.textBox.insert( tk.INSERT, DOUBLE_SPACE_SUBSTITUTE ) # Replace with substitute
                        self.textBox.mark_set( tk.INSERT, saveIndex ) # Put the cursor back
                if before1 == MULTIPLE_SPACE_SUBSTITUTE and after1 not in ALL_POSSIBLE_SPACE_CHARS and before2 not in ALL_POSSIBLE_SPACE_CHARS:
                    self.textBox.delete( tk.INSERT+'-1c', tk.INSERT ) # Delete the space substitute
                    self.textBox.insert( tk.INSERT, ' ' ) # Replace with normal space
                if after1 == MULTIPLE_SPACE_SUBSTITUTE and before1 not in ALL_POSSIBLE_SPACE_CHARS and after2 not in ALL_POSSIBLE_SPACE_CHARS:
                    self.textBox.delete( tk.INSERT, tk.INSERT+'+1c' ) # Delete the space substitute
                    self.textBox.insert( tk.INSERT, ' ' ) # Replace with normal space
                    self.textBox.mark_set( tk.INSERT, saveIndex ) # Put the cursor back

            # Handle auto-correct
            if self.autocorrectEntries and args[0]=='insert' and args[1]=='insert':
                #vPrint( 'Quiet', debuggingThisModule, "Handle autocorrect" )
                previousText = getCharactersBeforeCursor( self, self.maxAutocorrectLength )
                #vPrint( 'Quiet', debuggingThisModule, "previousText", repr(previousText) )
                for inChars,outChars in self.autocorrectEntries:
                    if previousText.endswith( inChars ):
                        #vPrint( 'Quiet', debuggingThisModule, "Going to replace {!r} with {!r}".format( inChars, outChars ) )
                        # Delete the typed character(s) and replace with the new one(s)
                        self.textBox.delete( tk.INSERT+'-{}c'.format( len(inChars) ), tk.INSERT )
                        self.textBox.insert( tk.INSERT, outChars )
                        break
            # end of auto-correct section


            # Handle auto-complete
            if self.autocompleteMode is not None and self.autocompleteWords and args[0] in ('insert','delete',):
                #vPrint( 'Quiet', debuggingThisModule, "Handle autocomplete1" )
                lastAutocompleteWordText = self.existingAutocompleteWordText
                self.existingAutocompleteWordText = getWordCharactersBeforeCursor( self, self.autocompleteMaxLength )
                #vPrint( 'Quiet', debuggingThisModule, "existingAutocompleteWordText: {!r}".format( self.existingAutocompleteWordText ) )
                if self.existingAutocompleteWordText != lastAutocompleteWordText:
                    # We've had an actual change in the entered text
                    possibleWords = None

                    if len(self.existingAutocompleteWordText) >= self.autocompleteMinLength:
                        # See if we have any words that start with the already typed letters
                        #vPrint( 'Quiet', debuggingThisModule, "Handle autocomplete1A with {!r}".format( self.existingAutocompleteWordText ) )
                        firstLetter, remainder = self.existingAutocompleteWordText[0], self.existingAutocompleteWordText[1:]
                        #vPrint( 'Quiet', debuggingThisModule, "firstletter={!r} remainder={!r}".format( firstLetter, remainder ) )
                        try: possibleWords = [firstLetter+thisBit for thisBit in self.autocompleteWords[firstLetter] \
                                                            if thisBit.startswith(remainder) and thisBit != remainder]
                        except KeyError: pass
                        self.autocompleteOverlap = self.existingAutocompleteWordText
                        #vPrint( 'Quiet', debuggingThisModule, 'possibleWordsA', possibleWords )

                    # Maybe we haven't typed enough yet to pop-up the standard box so we look ahead using the previous word
                    if not possibleWords:
                        previousStuff = getCharactersAndWordBeforeCursor( self, self.autocompleteMaxLength )
                        #vPrint( 'Quiet', debuggingThisModule, "Handle autocomplete1B with {!r}".format( previousStuff ) )
                        firstLetter, remainder = previousStuff[0], previousStuff[1:]
                        #vPrint( 'Quiet', debuggingThisModule, "firstletter={!r} remainder={!r}".format( firstLetter, remainder ) )
                        self.autocompleteOverlap = previousStuff
                        #try: possibleWords = [thisBit[remainderLength:] for thisBit in self.autocompleteWords[firstLetter] \
                        try: possibleWords = [firstLetter+thisBit for thisBit in self.autocompleteWords[firstLetter] \
                                                            if thisBit.startswith(remainder) and thisBit != remainder]
                        except KeyError: pass
                        self.autocompleteOverlap = previousStuff
                        #vPrint( 'Quiet', debuggingThisModule, 'possibleWordsB', possibleWords )

                    if possibleWords: # we have some word(s) to pop-up for possible selection
                        #vPrint( 'Quiet', debuggingThisModule, "Handle autocomplete2" )
                        if self.autocompleteBox is None:
                            self.makeAutocompleteBox()
                        else: # the Listbox is already made -- just empty it
                            #vPrint( 'Quiet', debuggingThisModule, 'empty listbox' )
                            self.autocompleteBox.delete( 0, tk.END ) # clear the listbox completely
                        # Now fill the Listbox
                        #vPrint( 'Quiet', debuggingThisModule, 'fill listbox' )
                        for word in possibleWords:
                            if BibleOrgSysGlobals.debugFlag: assert possibleWords.count( word ) == 1
                            self.autocompleteBox.insert( tk.END, word )
                        # Do a bit more set-up
                        #self.autocompleteBox.pack( side=tk.LEFT, fill=tk.BOTH )
                        self.autocompleteBox.select_set( '0' )
                        self.autocompleteBox.focus()
                    elif self.autocompleteBox is not None:
                        #vPrint( 'Quiet', debuggingThisModule, 'destroy1 autocomplete listbox -- no possible words' )
                        self.removeAutocompleteBox()
                    if self.addAllNewWords \
                    and args[0]=='insert' and args[1]=='insert' \
                    and args[2] in BibleOrgSysGlobals.TRAILING_WORD_END_CHARS:
                        # Just finished typing a word (by typing a space or something)
                        word = getWordBeforeSpace( self )
                        if word: # in the Bible modes, we also add new words as they're typed
                            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon: Adding/Updating autocomplete word", repr(word) )
                            addNewAutocompleteWord( self, word )
                            # NOTE: edited/deleted words aren't removed until the program restarts
            elif self.autocompleteBox is not None:
                #vPrint( 'Quiet', debuggingThisModule, 'destroy3 autocomplete listbox -- autocomplete is not enabled/appropriate' )
                self.removeAutocompleteBox()
            # end of auto-complete section

        #self.lastTextChangeTime = time()
        try: self.onTextNoChangeID = self.after( NO_TYPE_TIME, self.onTextNoChange ) # Reschedule no change function so we keep checking
        except KeyboardInterrupt:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon: Got keyboard interrupt in onTextChange (A) -- saving my file" )
            self.doSave() # Sometimes the above seems to lock up
            if self.onTextNoChangeID:
                self.after_cancel( self.onTextNoChangeID ) # Cancel any delayed no change checks which are scheduled
                self.onTextNoChangeID = None
    # end of TSVEditWindowAddon.onTextChange


    def onTextNoChange( self ):
        """
        Called whenever the text box HASN'T CHANGED for NO_TYPE_TIME msecs.

        Checks for some types of formatting errors.
        """
        #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.onTextNoChange" )
        try: pass
        except KeyboardInterrupt:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon: Got keyboard interrupt in onTextNoChange (B) -- saving my file" )
            self.doSave() # Sometimes the above seems to lock up
            #self.after_cancel( self.onTextNoChangeID ) # Cancel any delayed no change checks which are scheduled
            #self.onTextNoChangeID = None
    # end of TSVEditWindowAddon.onTextNoChange


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doShowInfo( {} )".format( event ) )

        text  = self.getEntireText()
        numChars = len( text )
        numLines = len( text.split( '\n' ) )
        numWords = len( text.split() )
        index = self.textBox.index( tk.INSERT )
        atLine, atColumn = index.split('.')

        grandtotal = 0
        for firstLetter in self.autocompleteWords:
            vPrint( 'Quiet', debuggingThisModule, "fL", firstLetter )
            grandtotal += len( self.autocompleteWords[firstLetter] )

        infoString = 'Current location:\n' \
            + '  Row: {}\n'.format( self.current_row ) \
            + '\nFile text statistics:\n' \
            + '  Rows: {:,}\n  Columns: {:,}\n  Headers: {}\n'.format( self.numDataRows, self.num_columns, self.tsvHeaders ) \
            + '\nFile info:\n' \
            + '  Name: {}\n'.format( self.filename ) \
            + '  Folder: {}\n'.format( self.folderpath ) \
            + '\nChecking status:\n' \
            + '  References & IDs: {}\n'.format( 'unknown' ) \
            + '  Order: {}\n'.format( 'unknown' ) \
            + '  Quotes: {}\n'.format( 'unknown' ) \
            + '  Links: {}\n'.format( 'unknown' ) \
            + '  Markdown: {}\n'.format( 'unknown' ) \
            + '\nSettings:\n' \
            + '  Autocorrect entries: {:,}\n  Autocomplete mode: {}\n  Autocomplete entries: {:,}\n  Autosave time: {} secs\n  Save changes automatically: {}' \
                    .format( len(self.autocorrectEntries), self.autocompleteMode, grandtotal, round(self.autosaveTime/1000), self.saveChangesAutomatically )

        showInfo( self, _("Window Information"), infoString )
    # end of TSVEditWindowAddon.doShowInfo


    def doUndo( self, event=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doUndo( {} )".format( event ) )

        try: self.textBox.edit_undo()
        except tk.TclError: showInfo( self, APP_NAME, _("Nothing to undo") )
        self.textBox.update() # force refresh
    # end of TSVEditWindowAddon.doUndo


    def doRedo( self, event=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doRedo( {} )".format( event ) )

        try: self.textBox.edit_redo()
        except tk.TclError: showInfo( self, APP_NAME, _("Nothing to redo") )
        self.textBox.update() # force refresh
    # end of TSVEditWindowAddon.doRedo


    def doDelete( self, event=None ):                         # delete selected text, no save
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doDelete( {} )".format( event ) )

        if not self.textBox.tag_ranges( tk.SEL ):
            showError( self, APP_NAME, _("No text selected") )
        else:
            self.textBox.delete( tk.SEL_FIRST, tk.SEL_LAST )
    # end of TSVEditWindowAddon.doDelete


    def doCut( self, event=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doCut( {} )".format( event ) )

        if not self.textBox.tag_ranges( tk.SEL ):
            showError( self, APP_NAME, _("No text selected") )
        else:
            self.doCopy() # In ChildBox class
            self.doDelete()
    # end of TSVEditWindowAddon.doCut


    def doPaste( self, event=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doPaste( {} )".format( event ) )
            vPrint( 'Quiet', debuggingThisModule, "  doPaste: {!r} {!r}".format( event.char, event.keysym ) )

        try:
            text = self.selection_get( selection='CLIPBOARD')
        except tk.TclError:
            showError( self, APP_NAME, _("Nothing to paste") )
            return
        self.textBox.insert( tk.INSERT, text)          # add at current insert cursor
        self.textBox.tag_remove( tk.SEL, tkSTART, tk.END )
        self.textBox.tag_add( tk.SEL, tk.INSERT+'-{}c'.format( len(text) ), tk.INSERT )
        self.textBox.see( tk.INSERT )                   # select it, so it can be cut
    # end of TSVEditWindowAddon.doPaste


    ############################################################################
    # Search menu commands
    ############################################################################

    #def xxxdoGotoWindowLine( self, forceline=None):
        #line = forceline or askinteger( APP_NAME, _("Enter line number") )
        #self.textBox.update()
        #self.textBox.focus()
        #if line is not None:
            #maxindex = self.textBox.index( tk.END+'-1c' )
            #maxline  = int( maxindex.split('.')[0] )
            #if line > 0 and line <= maxline:
                #self.textBox.mark_set( tk.INSERT, '{}.0'.format(line) ) # goto line
                #self.textBox.tag_remove( tk.SEL, tkSTART, tk.END )          # delete selects
                #self.textBox.tag_add( tk.SEL, tk.INSERT, 'insert + 1l' )  # select line
                #self.textBox.see( tk.INSERT )                          # scroll to line
            #else:
                #showError( self, APP_NAME, _("No such line number") )
    ## end of TSVEditWindowAddon.doGotoWindowLine


    #def xxxdoBoxFind( self, lastkey=None):
        #key = lastkey or askstring( APP_NAME, _("Enter search string") )
        #self.textBox.update()
        #self.textBox.focus()
        #self.lastfind = key
        #if key:
            #nocase = self.optionsDict['caseinsens']
            #where = self.textBox.search( key, tk.INSERT, tk.END, nocase=nocase )
            #if not where:                                          # don't wrap
                #showError( self, APP_NAME, _("String not found") )
            #else:
                #pastkey = where + '+%dc' % len(key)           # index past key
                #self.textBox.tag_remove( tk.SEL, tkSTART, tk.END )         # remove any sel
                #self.textBox.tag_add( tk.SEL, where, pastkey )        # select key
                #self.textBox.mark_set( tk.INSERT, pastkey )           # for next find
                #self.textBox.see( where )                          # scroll display
    ## end of TSVEditWindowAddon.doBoxFind


    #def xxxdoBoxRefind( self ):
        #self.doBoxFind( self.lastfind)
    ## end of TSVEditWindowAddon.doBoxRefind


    def doBoxFindReplace( self ):
        """
        Non-modal find/change dialog
        2.1: pass per-dialog inputs to callbacks, may be > 1 change dialog open
        """
        newPopupWindow = tk.Toplevel( self )
        newPopupWindow.title( '{} - change'.format( APP_NAME ) )
        Label( newPopupWindow, text='Find text?', relief=tk.RIDGE, width=15).grid( row=0, column=0 )
        Label( newPopupWindow, text='Change to?', relief=tk.RIDGE, width=15).grid( row=1, column=0 )
        entry1 = BEntry( newPopupWindow )
        entry2 = BEntry( newPopupWindow )
        entry1.grid( row=0, column=1, sticky=tk.EW )
        entry2.grid( row=1, column=1, sticky=tk.EW )

        def doBoxFind():                         # use my entry in enclosing scope
            self.doBoxFind( entry1.get() )         # runs normal find dialog callback

        def onApply():
            self.onDoChange( entry1.get(), entry2.get() )

        Button( newPopupWindow, text='Find',  command=doBoxFind ).grid(row=0, column=2, sticky=tk.EW )
        Button( newPopupWindow, text='Apply', command=onApply).grid(row=1, column=2, sticky=tk.EW )
        newPopupWindow.columnconfigure( 1, weight=1 )      # expandable entries
    # end of TSVEditWindowAddon.doBoxFindReplace


    def onDoChange( self, findtext, changeto):
        """
        on Apply in change dialog: change and refind
        """
        if self.textBox.tag_ranges( tk.SEL ):                      # must find first
            self.textBox.delete( tk.SEL_FIRST, tk.SEL_LAST)
            self.textBox.insert( tk.INSERT, changeto)             # deletes if empty
            self.textBox.see( tk.INSERT )
            self.doBoxFind( findtext )                          # goto next appear
            self.textBox.update() # force refresh
    # end of TSVEditWindowAddon.onDoChange


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    # def setFolderPath( self, newFolderPath ):
    #     """
    #     Store the folder path for where our files will be.

    #     We're still waiting for the filename.
    #     """
    #     if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
    #         vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.setFolderPath( {} )".format( repr(newFolderPath) ) )
    #         assert self.filename is None
    #         assert self.filepath is None

    #     self.folderpath = newFolderPath
    # # end of TSVEditWindowAddon.setFolderPath

    # def setFilename( self, filename, createFile=False ):
    #     """
    #     Store the filepath to our file.

    #     A complement to the above function.

    #     Also gets the file size and last edit time so we can detect if it's changed later.

    #     Returns True/False success flag.
    #     """
    #     if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
    #         vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.setFilename( {} )".format( repr(filename) ) )
    #         assert self.folderpath

    #     self.filename = filename
    #     self.filepath = os.path.join( self.folderpath, self.filename )
    #     if createFile: # Create a blank file
    #         with open( self.filepath, mode='wt', encoding='utf-8' ) as theBlankFile: pass # write nothing
    #     return self._checkFilepath()
    # # end of TSVEditWindowAddon.setFilename

    # def setPathAndFile( self, folderpath, filename ):
    #     """
    #     Store the filepath to our file.

    #     A more specific alternative to the above two functions. (The other alternative function is below.)

    #     Also gets the file size and last edit time so we can detect if it's changed later.

    #     Returns True/False success flag.
    #     """
    #     if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
    #         vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.setPathAndFile( {}, {} )".format( repr(folderpath), repr(filename) ) )

    #     self.folderpath, self.filename = folderpath, filename
    #     self.filepath = os.path.join( self.folderpath, self.filename )
    #     return self._checkFilepath()
    # # end of TSVEditWindowAddon.setPathAndFile

    # def setFilepath( self, newFilePath ):
    #     """
    #     Store the filepath to our file. (An alternative to the above function.)

    #     Also gets the file size and last edit time so we can detect if it's changed later.

    #     Returns True/False success flag.
    #     """
    #     if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
    #         vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.setFilepath( {!r} )".format( newFilePath ) )

    #     self.filepath = newFilePath
    #     self.folderpath, self.filename = os.path.split( newFilePath )
    #     return self._checkFilepath()
    # # end of TSVEditWindowAddon.setFilepath

    def _checkFilepath( self ):
        """
        Checks to make sure that the file can be found and opened.

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon._checkFilepath()" )

        if not os.path.isfile( self.filepath ):
            showError( self, APP_NAME, _("No such filepath: {!r}").format( self.filepath ) )
            return False
        if not os.access( self.filepath, os.R_OK ):
            showError( self, APP_NAME, _("No permission to read {!r} in {!r}").format( self.filename, self.folderpath ) )
            return False
        if not os.access( self.filepath, os.W_OK ):
            showError( self, APP_NAME, _("No permission to write {!r} in {!r}").format( self.filename, self.folderpath ) )
            return False

        self.rememberFileTimeAndSize()

        self.refreshTitle()
        return True
    # end of TSVEditWindowAddon._checkFilepath


    def rememberFileTimeAndSize( self ) -> None:
        """
        Just record the file modification time and size in bytes
            so that we can check later if it's changed on-disk.
        """
        self.lastFiletime = os.stat( self.filepath ).st_mtime
        self.lastFilesize = os.stat( self.filepath ).st_size
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, " rememberFileTimeAndSize: {} {}".format( self.lastFiletime, self.lastFilesize ) )
    # end of TSVEditWindowAddon.rememberFileTimeAndSize


    def setAllText( self, newText ):
        """
        Sets the textBox (assumed to be enabled) to the given text
            then positions the insert cursor at the BEGINNING of the text.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        vPrint( 'Never', debuggingThisModule, f"TextEditWindowAddon.setAllText( ({len(newText)}) {newText!r} )…" )

        self.textBox.configure( state=tk.NORMAL ) # In case it was disabled
        self.textBox.delete( tkSTART, tk.END ) # Delete everything that's existing
        XXX = self.getAllText() # temp
        if XXX: print( "WHY WHY", repr(XXX) )
        self.textBox.insert( tk.END, newText )
        self.textBox.highlightAllPatterns( self.patternsToHighlight )

        self.textBox.mark_set( tk.INSERT, tkSTART ) # move insert point to top
        self.textBox.see( tk.INSERT ) # scroll to top, insert is set

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( tk.FALSE ) # clear modified flag
    # end of TextEditWindowAddon.setAllText


    # def loadText( self ):
    #     """
    #     Opens the file, reads all the data, and sets it into the text box.

    #     Can also be used to RELOAD the text (e.g., if it has changed on the disk).

    #     Returns True/False success flag.
    #     """
    #     if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
    #         vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.loadText()" )

    #     self.loading = True
    #     text = open( self.filepath, 'rt', encoding='utf-8' ).read()
    #     if text == None:
    #         showError( self, APP_NAME, 'Could not decode and open file ' + self.filepath )
    #         return False
    #     else:
    #         self.setAllText( text )
    #         self.loading = False
    #         return True
    # # end of TSVEditWindowAddon.loadText


    def getEntireText( self ):
        """
        This function can be overloaded in super classes
            (where the edit window might not display the entire text).
        """
        vPrint( 'Never', debuggingThisModule, "TSVEditWindowAddon.getEntireText()…" )

        return self.getAllText()
    # end of TSVEditWindowAddon.getEntireText


    def checkForDiskChanges( self, autoloadText=False ):
        """
        Check if the file has changed on disk.

        If it has, and the user hasn't yet made any changes, offer to reload.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.checkForDiskChanges()" )

        if self.filepath and os.path.isfile( self.filepath ) \
        and ( ( self.lastFiletime and os.stat( self.filepath ).st_mtime != self.lastFiletime ) \
          or ( self.lastFilesize and os.stat( self.filepath ).st_size != self.lastFilesize ) ):
            if self.modified():
                showError( self, APP_NAME, _("File {} has also changed on disk").format( repr(self.filename) ) )
            else: # We haven't modified the file since loading it
                yndResult = False
                if autoloadText: yndResult = True
                else: # ask the user
                    ynd = YesNoDialog( self, _("File {} has changed on disk. Reload?").format( repr(self.filename) ), title=_('Reload?') )
                    #vPrint( 'Quiet', debuggingThisModule, "yndResult", repr(ynd.result) )
                    if ynd.result == True: yndResult = True # Yes was chosen
                if yndResult:
                    self.loadText() # reload
            self.rememberFileTimeAndSize()
        self.after( CHECK_DISK_CHANGES_TIME, self.checkForDiskChanges ) # Redo it so we keep checking
    # end if TSVEditWindowAddon.checkForDiskChanges


    def doReassembleFile( self ) -> None:
        """
        Undoes this:
            fileLines = self.originalText.split( '\n' )
            if fileLines and fileLines[-1] == '':
                print( "Deleting final blank line" )
                fileLines = fileLines[:-1]
                self.hadTrailingNL = True
        """
        vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doReassembleFile()…" )
        self.retrieveCurrentRowData( updateTable=True ) # in case current row was edited

        fileLines = ['\t'.join( rowData ) for rowData in self.tsvTable]
        vPrint( 'Quiet', debuggingThisModule, f"  Reassembled {len(fileLines)} table lines (incl. header) cf. {self.numOriginalLines} lines read" )
        self.newText = '\n'.join( fileLines )
        if self.hadTrailingNL: self.newText = f'{self.newText}\n'
        vPrint( 'Quiet', debuggingThisModule, f"  New text is {len(self.newText):,} bytes cf. {len(self.originalText):,} bytes read" )
    # end of TSVEditWindowAddon.doReassembleFile


    def modified( self ) -> bool:
        """
        Overrides the ChildWindows one, which only works from the one TextBox
        """
        self.doReassembleFile()
        return self.newText != self.originalText
    # end of TSVEditWindowAddon.modified


    def doSaveAs( self, event=None ):
        """
        Called if the user requests a saveAs from the GUI.
        """
        vPrint( 'Quiet', debuggingThisModule, f"TSVEditWindowAddon.doSaveAs( {event} ) with {self.modified()}…" )

        if self.modified() and 0 and XXX:
            saveAsFilepath = asksaveasfilename( parent=self )
            #vPrint( 'Quiet', debuggingThisModule, "saveAsFilepath", repr(saveAsFilepath) )
            if saveAsFilepath:
                if self.setFilepath( saveAsFilepath ):
                    self.doSave()
    # end of TSVEditWindowAddon.doSaveAs

    def doSave( self, event=None ):
        """
        Called if the user requests a save from the GUI.
        """
        vPrint( 'Quiet', debuggingThisModule, f"TSVEditWindowAddon.doSave( {event} ) with {self.modified()}…" )

        self.doReassembleFile()

        if self.modified() and 0 and XXX:
            if self.folderpath and self.filename:
                filepath = os.path.join( self.folderpath, self.filename )
                allText = self.getEntireText() # from the displayed edit window
                with open( filepath, mode='wt', encoding='utf-8' ) as theFile:
                    theFile.write( allText )
                self.rememberFileTimeAndSize()
                self.textBox.edit_modified( tk.FALSE ) # clear Tkinter modified flag
                #self.bookTextModified = False
                self.refreshTitle()
            else: self.doSaveAs()
    # end of TSVEditWindowAddon.doSave


    def doAutosave( self ):
        """
        Called on a timer to save a copy of the file in a separate location
            if it's been modified.

        Also saves a daily copy of the file into a sub-folder.

        Schedules another call.

        Doesn't use a hidden folder for the autosave files so the user can find them:
            If a save has been done, an AutoSave folder is created in the save folder,
            if not, the AutoSave folder is created in the home folder.
                (Yes, this can result in old AutoSave files in the home folder.)
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doAutosave()" )

        if 0 and self.modified():
            partialAutosaveFolderPath = self.folderpath if self.folderpath else self.parentApp.homeFolderPath
            # NOTE: Don't use a hidden folder coz user might not be able to find it
            autosaveFolderPath = os.path.join( partialAutosaveFolderPath, 'AutoSave/' ) \
                                    if APP_NAME in partialAutosaveFolderPath \
                                    else os.path.join( partialAutosaveFolderPath, DATA_FOLDER_NAME, 'AutoSave/' )
            if not os.path.exists( autosaveFolderPath ): os.makedirs( autosaveFolderPath )
            lastDayFolderPath = os.path.join( autosaveFolderPath, 'LastDay/' )
            if not os.path.exists( lastDayFolderPath ): os.mkdir( lastDayFolderPath )

            autosaveFilename = self.filename if self.filename else 'Autosave.txt'
            #vPrint( 'Quiet', debuggingThisModule, 'autosaveFolderPath', repr(autosaveFolderPath), 'autosaveFilename', repr(autosaveFilename) )
            autosaveFilepath = os.path.join( autosaveFolderPath, autosaveFilename )
            lastDayFilepath = os.path.join( lastDayFolderPath, autosaveFilename )

            # Check if we need a daily save
            if os.path.isfile( autosaveFilepath ) \
            and ( not os.path.isfile( lastDayFilepath ) \
            or datetime.fromtimestamp( os.stat( lastDayFilepath ).st_mtime ).date() != datetime.today().date() ):
            #or not self.filepath \
                vPrint( 'Quiet', debuggingThisModule, "doAutosave: saving daily file", lastDayFilepath )
                shutil.copyfile( autosaveFilepath, lastDayFilepath ) # We save a copy of the PREVIOUS autosaved file

            # Now save this updated file
            allText = self.getEntireText() # from the displayed edit window and/or elsewhere
            with open( autosaveFilepath, mode='wt', encoding='utf-8' ) as theFile:
                theFile.write( allText )
            self.after( self.autosaveTime, self.doAutosave )
        else:
            self.autosaveScheduled = False # Will be set again by refreshTitle
    # end of TSVEditWindowAddon.doAutosave


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            vPrint( 'Quiet', debuggingThisModule, "doViewSettings()" )
            self.parentApp.setDebugText( "doViewSettings…" )
        tEW = TSVEditWindow( self.parentApp )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setFilepath( self.settings.settingsFilepath ) \
        or not tEW.loadText():
            tEW.doClose()
            showError( self, APP_NAME, _("Sorry, unable to open settings file") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed doViewSettings" )
        else:
            self.parentApp.childWindows.append( tEW )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished doViewSettings" )
        self.parentApp.setReadyStatus()
    # end of TSVEditWindowAddon.doViewSettings


    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        vPrint( 'Never', debuggingThisModule, "doViewLog()" )
        if debuggingThisModule: self.parentApp.setDebugText( "doViewLog…" )

        filename = PROGRAM_NAME.replace('/','-').replace(':','_').replace('\\','_') + '_log.txt'
        tEW = TSVEditWindow( self.parentApp )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setPathAndFile( self.parentApp.loggingFolderPath, filename ) \
        or not tEW.loadText():
            tEW.doClose()
            showError( self, APP_NAME, _("Sorry, unable to open log file") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed doViewLog" )
        else:
            self.parentApp.childWindows.append( tEW )
            #if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewLog" ) # Don't do this -- adds to the log immediately
        self.parentApp.setReadyStatus()
    # end of TSVEditWindowAddon.doViewLog


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doHelp( {} )".format( event ) )
        from Biblelator.Dialogs.Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of TSVEditWindowAddon.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doAbout( {} )".format( event ) )
        from Biblelator.Dialogs.About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of TSVEditWindowAddon.doAbout


    def doClose( self, event=None ):
        """
        Called if the window is about to be destroyed.

        Determines if we want/need to save any changes.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindowAddon.doClose( {} )".format( event ) )

        if 0 and self.modified():
            saveWork = False
            if self.saveChangesAutomatically and self.folderpath and self.filename:
                #self.doSave( 'Auto from win close' )
                #self.doClose()
                saveWork = True
            else:
                #if self.folderpath and self.filename:
                    #self.doSave()
                    #self.doClose()
                #else: # we need to ask where to save it
                place = 'in {}'.format( self.filename) if self.folderpath and self.filename else ''
                ocd = OkCancelDialog( self, _('Do you want to save your work{}?').format( place ), title=_('Save work?') )
                #vPrint( 'Quiet', debuggingThisModule, "ocdResult", repr(ocd.result) )
                if ocd.result == True: # Yes was chosen
                    saveWork = True
                else:
                    place = 'to {}'.format( self.filename) if self.folderpath and self.filename else ''
                    ynd = YesNoDialog( self, _('Are you sure you want to lose your changes?').format( place ), title=_('Lose changes?') )
                    #vPrint( 'Quiet', debuggingThisModule, "yndResult", repr(ynd.result) )
                    if ynd.result == True: # Yes was chosen
                        self.textBox.edit_modified( tk.FALSE ) # clear Tkinter modified flag
                        self.bookTextModified = False
                    #else: saveWork = True
            if saveWork:
                self.doSave()
                if self.folderpath and self.filename: # assume we saved it
                    ChildWindow.doClose( self )
                    return

        if 1 or not self.modified():
            #vPrint( 'Quiet', debuggingThisModule, "HEREEEEEEEEE" )
            ChildWindow.doClose( self )
    # end of TSVEditWindowAddon.doClose
# end of TSVEditWindowAddon class



class TSVEditWindow( TSVEditWindowAddon, ChildWindow ):
    """
    """
    def __init__( self, parentApp, fileLines:List, filepath:str ):
        """
        """
        if 1 or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, f"TSVEditWindow.__init__( {parentApp}, {len(fileLines)}, {filepath} )" )
        self.fileLines, self.filepath = fileLines, filepath
        parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, f"TSVEditWindow __init__ {len(fileLines)} {filepath}" )

        # NOTE: Bible is added so we get BCV alerts
        windowType, genericWindowType = 'TSVBibleEditWindow', 'TSVBibleEditor'
        self.moduleID = 'TSV'
        self.BCVUpdateType = DEFAULT # For BCV updates
        self.BBB = 'UNK' # Unknown book
        self.currentVerseKey = SimpleVerseKey( self.BBB,'1','1' )
        ChildWindow.__init__( self, parentApp, genericWindowType )
        # BibleWindowAddon.__init__( self, genericWindowType )
        TSVEditWindowAddon.__init__( self, windowType, fileLines, filepath )

        #self.filepath = os.path.join( folderpath, filename ) if folderpath and filename else None
        #self.moduleID = None
        ##self.windowType = 'TSVBibleEditWindow'
        #self.protocol( 'WM_DELETE_WINDOW', self.doClose ) # Catch when window is closed

        #self.loading = True
        #self.onTextNoChangeID = None
        #self.editStatus = 'Editable'

        ## Make our own custom textBox which allows a callback function
        ##   Delete these lines and the callback line if you don't need either autocorrect or autocomplete
        #self.textBox.destroy() # from the ChildWindow default
        #self.myKeyboardBindingsList = []
        #if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = []

        #self.customFont = tk.font.Font( family="sans-serif", size=12 )
        #self.customFontBold = tk.font.Font( family="sans-serif", size=12, weight='bold' )
        #self.textBox = CustomText( self, yscrollcommand=self.vScrollbar.set, wrap='word', font=self.customFont )

        #self.defaultBackgroundColour = 'gold2'
        #self.textBox.configure( background=self.defaultBackgroundColour )
        #self.textBox.configure( selectbackground='blue' )
        #self.textBox.configure( highlightbackground='orange' )
        #self.textBox.configure( inactiveselectbackground='green' )
        #self.textBox.configure( wrap='word', undo=True, autoseparators=True )
        #self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
        #self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        #self.textBox.setTextChangeCallback( self.onTextChange )
        #self.createEditorKeyboardBindings()
        self.createMenuBar()
        #self.createContextMenu() # Enable right-click menu

        #self.lastFiletime = self.lastFilesize = None
        #self.clearText()

        #self.markMultipleSpacesFlag = True
        #self.markTrailingSpacesFlag = True

        #self.autocorrectEntries = []
        ## Temporarily include some default autocorrect values
        #setDefaultAutocorrectEntries( self )
        ##setAutocorrectEntries( self, ourAutocorrectEntries )

        #self.autocompleteBox, self.autocompleteWords, self.existingAutocompleteWordText = None, {}, ''
        #self.autocompleteWordChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        ## Note: I guess we could have used non-word chars instead (to stop the backwards word search)
        #self.autocompleteMinLength = 3 # Show the normal window after this many characters have been typed
        #self.autocompleteMaxLength = 15 # Remove window after this many characters have been typed
        #self.autocompleteMode = None # None or Dictionary1 or Dictionary2 (or Bible or BibleBook)
        #self.addAllNewWords = False

        #self.invalidCombinations = [] # characters or character combinations that shouldn't occur
        ## Temporarily include some default invalid values
        #self.invalidCombinations = [',,',' ,',] # characters or character combinations that shouldn't occur

        #self.patternsToHighlight = []
        ## Temporarily include some default values -- simplistic demonstration examples
        #self.patternsToHighlight.append( (False,'import','red',{'background':'red'}) )
        #self.patternsToHighlight.append( (False,'self','green',{'foreground':'green'}) )
        #self.patternsToHighlight.append( (True,'\\d','blue',{'foreground':'blue'}) )
        #self.patternsToHighlight.append( (True,'#.*?\\n','grey',{'foreground':'grey'}) )
        #boldDict = {'font':self.customFontBold } #, 'background':'green'}
        #for pythonKeyword in ( 'from','import', 'class','def', 'if','and','or','else','elif',
                              #'for','while', 'return', 'try','accept','finally', 'assert', ):
            #self.patternsToHighlight.append( (True,'\\y'+pythonKeyword+'\\y','bold',boldDict) )

        #self.saveChangesAutomatically = False # different from AutoSave (which is in different files)
        #self.autosaveTime = 2*60*1000 # msecs (zero is no autosaves)
        #self.autosaveScheduled = False

        #self.after( CHECK_DISK_CHANGES_TIME, self.checkForDiskChanges )
        ##self.after( REFRESH_TITLE_TIME, self.refreshTitle )
        #self.loading = self.hadTextWarning = False
        ##self.lastTextChangeTime = time()

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "TSVEditWindow.__init__ finished." )
    # end of TSVEditWindow.__init__
# end of TSVEditWindow class



def briefDemo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    tEW = TSVEditWindow( tkRootWindow )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of TSVEditWindow.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    tEW = TSVEditWindow( tkRootWindow )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of TSVEditWindow.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of TSVEditWindow.py
