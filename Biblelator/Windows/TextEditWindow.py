#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# TextEditWindow.py
#
# The edit windows for Biblelator plain text editing
#
# Copyright (C) 2013-2020 Robert Hunt
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
import os.path
import logging
import shutil
from datetime import datetime

import tkinter as tk
from tkinter import font
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import Button, Label, Entry

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint

# Biblelator imports
if __name__ == '__main__':
    import sys
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator import BiblelatorGlobals
from Biblelator.BiblelatorGlobals import APP_NAME, tkSTART, tkBREAK, DEFAULT, DATA_SUBFOLDER_NAME
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showInfo
from Biblelator.Dialogs.BiblelatorDialogs import YesNoDialog, OkCancelDialog
from Biblelator.Windows.TextBoxes import CustomText, TRAILING_SPACE_SUBSTITUTE, MULTIPLE_SPACE_SUBSTITUTE, \
                                DOUBLE_SPACE_SUBSTITUTE, ALL_POSSIBLE_SPACE_CHARS
from Biblelator.Windows.ChildWindows import ChildWindow
from Biblelator.Helpers.AutocorrectFunctions import setDefaultAutocorrectEntries # setAutocorrectEntries
from Biblelator.Helpers.AutocompleteFunctions import getCharactersBeforeCursor, \
                                getWordCharactersBeforeCursor, getCharactersAndWordBeforeCursor, \
                                getWordBeforeSpace, addNewAutocompleteWord, acceptAutocompleteSelection


LAST_MODIFIED_DATE = '2020-04-29' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorTextEditWindow"
PROGRAM_NAME = "Biblelator Text Edit Window"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = 99


REFRESH_TITLE_TIME = 500 # msecs
CHECK_DISK_CHANGES_TIME = 33333 # msecs
NO_TYPE_TIME = 6000 # msecs
NUM_AUTOCOMPLETE_POPUP_LINES = 6



class TextEditWindowAddon:
    """
    """
    def __init__( self, windowType:str, folderpath=None, filename=None ):
        """
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.__init__( {}, {}, {} )".format( windowType, folderpath, filename ) )
        self.windowType, self.folderpath, self.filename = windowType, folderpath, filename
        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'TextEditWindowAddon __init__ {} {} {}'.format( windowType, folderpath, filename ) )

        self.filepath = os.path.join( folderpath, filename ) if folderpath and filename else None
        self.moduleID = None
        self.protocol( 'WM_DELETE_WINDOW', self.doClose ) # Catch when window is closed

        self.loading = True
        self.onTextNoChangeID = None
        self.editStatus = 'Editable'

        # Make our own custom textBox which allows a callback function
        #   Delete these lines and the callback line if you don't need either autocorrect or autocomplete
        self.textBox.destroy() # from the ChildWindow default
        self.myKeyboardBindingsList = []
        if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = []

        self.customFont = tk.font.Font( family="sans-serif", size=12 )
        self.customFontBold = tk.font.Font( family="sans-serif", size=12, weight='bold' )
        self.textBox = CustomText( self, yscrollcommand=self.vScrollbar.set, wrap='word', font=self.customFont )

        self.defaultBackgroundColour = 'gold2'
        self.textBox.configure( background=self.defaultBackgroundColour )
        self.textBox.configure( selectbackground='blue' )
        self.textBox.configure( highlightbackground='orange' )
        self.textBox.configure( inactiveselectbackground='green' )
        self.textBox.configure( wrap='word', undo=True, autoseparators=True )
        self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        self.textBox.setTextChangeCallback( self.onTextChange )
        self.createEditorKeyboardBindings()
        #self.createMenuBar()
        self.createContextMenu() # Enable right-click menu

        self.lastFiletime = self.lastFilesize = None
        self.clearText()

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
        self.patternsToHighlight.append( (False,'import','red',{'background':'red'}) )
        self.patternsToHighlight.append( (False,'self','green',{'foreground':'green'}) )
        self.patternsToHighlight.append( (True,'\\d','blue',{'foreground':'blue'}) )
        self.patternsToHighlight.append( (True,'#.*?\\n','grey',{'foreground':'grey'}) )
        boldDict = {'font':self.customFontBold } #, 'background':'green'}
        for pythonKeyword in ( 'from','import', 'class','def', 'if','and','or','else','elif',
                              'for','while', 'return', 'try','accept','finally', 'assert', ):
            self.patternsToHighlight.append( (True,'\\y'+pythonKeyword+'\\y','bold',boldDict) )

        self.saveChangesAutomatically = False # different from AutoSave (which is in different files)
        self.autosaveTime = 2*60*1000 # msecs (zero is no autosaves)
        self.autosaveScheduled = False

        self.after( CHECK_DISK_CHANGES_TIME, self.checkForDiskChanges )
        #self.after( REFRESH_TITLE_TIME, self.refreshTitle )
        self.loading = self.hadTextWarning = False
        #self.lastTextChangeTime = time()

        vPrint( 'Never', debuggingThisModule, "TextEditWindowAddon.__init__ finished." )
    # end of TextEditWindowAddon.__init__


    def createEditorKeyboardBindings( self ):
        """
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.createEditorKeyboardBindings()" )

        for name,commandFunction in ( #('Paste',self.doPaste), ('Cut',self.doCut),
                             #('Undo',self.doUndo), ('Redo',self.doRedo),
                             ('Find',self.doBoxFind), ('Refind',self.doBoxRefind),
                             ('Save',self.doSave),
                             ('ShowMain',self.doShowMainWindow),
                             ):
            #dPrint( 'Quiet', debuggingThisModule, "TEW CheckLoop", (name,BiblelatorGlobals.theApp.keyBindingDict[name][0],BiblelatorGlobals.theApp.keyBindingDict[name][1],) )
            assert (name,BiblelatorGlobals.theApp.keyBindingDict[name][0],) not in self.myKeyboardBindingsList
            if name in BiblelatorGlobals.theApp.keyBindingDict:
                for keyCode in BiblelatorGlobals.theApp.keyBindingDict[name][1:]:
                    #dPrint( 'Quiet', debuggingThisModule, "  TEW Bind {} for {}".format( repr(keyCode), repr(name) ) )
                    self.textBox.bind( keyCode, commandFunction )
                    if BibleOrgSysGlobals.debugFlag:
                        assert keyCode not in self.myKeyboardShortcutsList
                        self.myKeyboardShortcutsList.append( keyCode )
                self.myKeyboardBindingsList.append( (name,BiblelatorGlobals.theApp.keyBindingDict[name][0],) )
            else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of TextEditWindowAddon.createEditorKeyboardBindings()


    def createMenuBar( self ):
        """
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.createMenuBar()" )

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        fileMenu.add_command( label=_('Save'), underline=0, command=self.doSave, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Save')][0] )
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
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] )

        editMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Undo'), underline=0, command=self.doUndo, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Undo')][0] )
        editMenu.add_command( label=_('Redo'), underline=0, command=self.doRedo, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Redo')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Cut'), underline=2, command=self.doCut, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Cut')][0] )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        editMenu.add_command( label=_('Paste'), underline=0, command=self.doPaste, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Paste')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Delete'), underline=0, command=self.doDelete )
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Line')][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Refind')][0] )
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
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('ShowMain')][0] )

        if BibleOrgSysGlobals.debugFlag:
            debugMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=debugMenu, label=_('Debug'), underline=0 )
            #debugMenu.add_command( label=_('View settings…'), underline=5, command=self.doViewSettings )
            #debugMenu.add_separator()
            debugMenu.add_command( label=_('View log…'), underline=5, command=self.doViewLog )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label=_('Help'), underline=0 )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('About')][0] )
    # end of TextEditWindowAddon.createMenuBar


    def createContextMenu( self ):
        """
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.createContextMenu()" )

        self.contextMenu = tk.Menu( self, tearoff=False )
        self.contextMenu.add_command( label=_('Cut'), underline=2, command=self.doCut, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Cut')][0] )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        self.contextMenu.add_command( label=_('Paste'), underline=0, command=self.doPaste, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Paste')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
    # end of TextEditWindowAddon.createContextMenu


    #def showContextMenu( self, e):
        #self.contextMenu.post( e.x_root, e.y_root )
    ## end of TextEditWindowAddon.showContextMenu


    #def createToolBar( self ):
        #toolbar = Frame( self, cursor='hand2', relief=tk.SUNKEN ) # bd=2
        #toolbar.pack( side=tk.BOTTOM, fill=tk.X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=tk.RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=tk.LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=tk.LEFT )
    ## end of TextEditWindowAddon.createToolBar


    def refreshTitle( self ):
        """
        Refresh the title of the text edit window,
            put an asterisk if it's modified.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.refreshTitle()" )

        self.title( "{}[{}] {} ({}) {}".format( '*' if self.modified() else '',
                                            _("Text"), self.filename, self.folderpath, self.editStatus ) )
        self.refreshTitleContinue()
    # end if TextEditWindowAddon.refreshTitle

    def refreshTitleContinue( self ):
        """
        Check if an autosave is needed,
            and schedule the next refresh.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.refreshTitleContinue()" )

        self.after( REFRESH_TITLE_TIME, self.refreshTitle ) # Redo it so we can put up the asterisk if the text is changed
        try:
            if self.autosaveTime and self.modified() and not self.autosaveScheduled:
                self.after( self.autosaveTime, self.doAutosave ) # Redo it so we can put up the asterisk if the text is changed
                self.autosaveScheduled = True
        except AttributeError:
            vPrint( 'Quiet', debuggingThisModule, "Autosave not set-up properly yet" )
    # end if TextEditWindowAddon.refreshTitleContinue


    def OnFontBigger( self ):
        """
        Make the font one point bigger
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.OnFontBigger()" )

        size = self.customFont['size']
        self.customFont.configure( size=size+1 )
    # end if TextEditWindowAddon.OnFontBigger

    def OnFontSmaller( self ):
        """
        Make the font one point smaller
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.OnFontSmaller()" )

        size = self.customFont['size']
        self.customFont.configure( size=size-1 )
    # end if TextEditWindowAddon.OnFontSmaller


    def getAllText( self ) -> str:
        """
        Returns all the text as a string.
        """
        allText = self.textBox.get( tkSTART, tk.END+'-1c' )
        #if self.markMultipleSpacesFlag:
        allText = allText.replace( MULTIPLE_SPACE_SUBSTITUTE, ' ' )
        #if self.markTrailingSpacesFlag:
        allText = allText.replace( TRAILING_SPACE_SUBSTITUTE, ' ' )
        return allText
    # end of USFMEditWindow.getAllText


    def makeAutocompleteBox( self ) -> None:
        """
        Create a pop-up listbox in order to be able to display possible autocomplete words.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.makeAutocompleteBox()" )
        if debuggingThisModule or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
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
    # end of TextEditWindowAddon.makeAutocompleteBox


    def OnAutocompleteChar( self, event ):
        """
        Used by autocomplete routines in onTextChange.

        Handles key presses entered into the pop-up word selection (list) box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.OnAutocompleteChar( {!r}, {!r} )".format( event.char, event.keysym ) )
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
    # end of TextEditWindowAddon.OnAutocompleteChar


    def doAcceptAutocompleteSelection( self, event=None ):
        """
        Used by autocomplete routines in onTextChange.

        Gets the chosen word and inserts the end of it into the text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.doAcceptAutocompleteSelection({} )".format( event ) )
            assert self.autocompleteBox is not None

        acceptAutocompleteSelection( self, includeTrailingSpace=False )
    # end of TextEditWindowAddon.doAcceptAutocompleteSelection


    def removeAutocompleteBox( self, event=None ):
        """
        Remove the pop-up Listbox (in a Frame in a Toplevel) when it's no longer required.

        Used by autocomplete routines in onTextChange.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.removeAutocompleteBox( {} )".format( event ) )
            assert self.autocompleteBox is not None

        self.textBox.focus()
        self.autocompleteBox.master.master.destroy() # master is Frame, master.master is Toplevel
        self.autocompleteBox = None
    # end of TextEditWindowAddon.removeAutocompleteBox


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
        vPrint( 'Never', debuggingThisModule, "TextEditWindowAddon.onTextChange( {}, {} )".format( repr(result), args ) )

        #if 0: # Get line and column info
            #lineColumn = self.textBox.index( tk.INSERT )
            #dPrint( 'Quiet', debuggingThisModule, "lc", repr(lineColumn) )
            #line, column = lineColumn.split( '.', 1 )
            #dPrint( 'Quiet', debuggingThisModule, "l,c", repr(line), repr(column) )

        #if 0: # get formatting tag info
            #tagNames = self.textBox.tag_names( tk.INSERT )
            #tagNames2 = self.textBox.tag_names( lineColumn )
            #tagNames3 = self.textBox.tag_names( tk.INSERT + ' linestart' )
            #tagNames4 = self.textBox.tag_names( lineColumn + ' linestart' )
            #tagNames5 = self.textBox.tag_names( tk.INSERT + ' linestart+1c' )
            #tagNames6 = self.textBox.tag_names( lineColumn + ' linestart+1c' )
            #dPrint( 'Quiet', debuggingThisModule, "tN", tagNames )
            #if tagNames2!=tagNames or tagNames3!=tagNames or tagNames4!=tagNames or tagNames5!=tagNames or tagNames6!=tagNames:
                #dPrint( 'Quiet', debuggingThisModule, "tN2", tagNames2 )
                #dPrint( 'Quiet', debuggingThisModule, "tN3", tagNames3 )
                #dPrint( 'Quiet', debuggingThisModule, "tN4", tagNames4 )
                #dPrint( 'Quiet', debuggingThisModule, "tN5", tagNames5 )
                #dPrint( 'Quiet', debuggingThisModule, "tN6", tagNames6 )
                #halt

        #if 0: # show various mark strategies
            #mark1 = self.textBox.mark_previous( tk.INSERT )
            #mark2 = self.textBox.mark_previous( lineColumn )
            #mark3 = self.textBox.mark_previous( tk.INSERT + ' linestart' )
            #mark4 = self.textBox.mark_previous( lineColumn + ' linestart' )
            #mark5 = self.textBox.mark_previous( tk.INSERT + ' linestart+1c' )
            #mark6 = self.textBox.mark_previous( lineColumn + ' linestart+1c' )
            #dPrint( 'Quiet', debuggingThisModule, "mark1", mark1 )
            #if mark2!=mark1:
                #dPrint( 'Quiet', debuggingThisModule, "mark2", mark1 )
            #if mark3!=mark1 or mark4!=mark1 or mark5!=mark1 or mark6!=mark1:
                #dPrint( 'Quiet', debuggingThisModule, "mark3", mark3 )
                #if mark4!=mark3:
                    #dPrint( 'Quiet', debuggingThisModule, "mark4", mark4 )
                #dPrint( 'Quiet', debuggingThisModule, "mark5", mark5 )
                #if mark6!=mark5:
                    #dPrint( 'Quiet', debuggingThisModule, "mark6", mark6 )


        if self.textBox.edit_modified():
            #if 1:
                #dPrint( 'Quiet', debuggingThisModule, 'args[0]', repr(args[0]) )
                #dPrint( 'Quiet', debuggingThisModule, 'args[1]', repr(args[1]) )
                #try: vPrint( 'Quiet', debuggingThisModule, 'args[2]', repr(args[2]) ) # Can be multiple characters (after autocomplete)
                #except IndexError: vPrint( 'Quiet', debuggingThisModule, "No args[2]" ) # when deleting

            # Handle substituted space characters
            saveIndex = self.textBox.index( tk.INSERT ) # Remember where the cursor was
            if args[0]=='insert' and args[1]=='insert':
                before1After1 = self.textBox.get( tk.INSERT+'-2c', tk.INSERT+'+1c' ) # Get the characters before and after
                if len(before1After1) == 3: before1, newChar, after1 = before1After1
                else: before1 = newChar = after1 = '' # this can happen sometimes
                #dPrint( 'Quiet', debuggingThisModule, '3', repr(before1), repr(newChar), repr(after1) )
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
                    #dPrint( 'Quiet', debuggingThisModule, "Deleted" )
                #elif args[1] == 'insert-1c': # we used the backspace key
                    #dPrint( 'Quiet', debuggingThisModule, "Backspaced" )
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
                #dPrint( 'Quiet', debuggingThisModule, "Handle autocorrect" )
                previousText = getCharactersBeforeCursor( self, self.maxAutocorrectLength )
                #dPrint( 'Quiet', debuggingThisModule, "previousText", repr(previousText) )
                for inChars,outChars in self.autocorrectEntries:
                    if previousText.endswith( inChars ):
                        #dPrint( 'Quiet', debuggingThisModule, "Going to replace {!r} with {!r}".format( inChars, outChars ) )
                        # Delete the typed character(s) and replace with the new one(s)
                        self.textBox.delete( tk.INSERT+'-{}c'.format( len(inChars) ), tk.INSERT )
                        self.textBox.insert( tk.INSERT, outChars )
                        break
            # end of auto-correct section


            # Handle auto-complete
            if self.autocompleteMode is not None and self.autocompleteWords and args[0] in ('insert','delete',):
                #dPrint( 'Quiet', debuggingThisModule, "Handle autocomplete1" )
                lastAutocompleteWordText = self.existingAutocompleteWordText
                self.existingAutocompleteWordText = getWordCharactersBeforeCursor( self, self.autocompleteMaxLength )
                #dPrint( 'Quiet', debuggingThisModule, "existingAutocompleteWordText: {!r}".format( self.existingAutocompleteWordText ) )
                if self.existingAutocompleteWordText != lastAutocompleteWordText:
                    # We've had an actual change in the entered text
                    possibleWords = None

                    if len(self.existingAutocompleteWordText) >= self.autocompleteMinLength:
                        # See if we have any words that start with the already typed letters
                        #dPrint( 'Quiet', debuggingThisModule, "Handle autocomplete1A with {!r}".format( self.existingAutocompleteWordText ) )
                        firstLetter, remainder = self.existingAutocompleteWordText[0], self.existingAutocompleteWordText[1:]
                        #dPrint( 'Quiet', debuggingThisModule, "firstletter={!r} remainder={!r}".format( firstLetter, remainder ) )
                        try: possibleWords = [firstLetter+thisBit for thisBit in self.autocompleteWords[firstLetter] \
                                                            if thisBit.startswith(remainder) and thisBit != remainder]
                        except KeyError: pass
                        self.autocompleteOverlap = self.existingAutocompleteWordText
                        #dPrint( 'Quiet', debuggingThisModule, 'possibleWordsA', possibleWords )

                    # Maybe we haven't typed enough yet to pop-up the standard box so we look ahead using the previous word
                    if not possibleWords:
                        previousStuff = getCharactersAndWordBeforeCursor( self, self.autocompleteMaxLength )
                        #dPrint( 'Quiet', debuggingThisModule, "Handle autocomplete1B with {!r}".format( previousStuff ) )
                        firstLetter, remainder = previousStuff[0], previousStuff[1:]
                        #dPrint( 'Quiet', debuggingThisModule, "firstletter={!r} remainder={!r}".format( firstLetter, remainder ) )
                        self.autocompleteOverlap = previousStuff
                        #try: possibleWords = [thisBit[remainderLength:] for thisBit in self.autocompleteWords[firstLetter] \
                        try: possibleWords = [firstLetter+thisBit for thisBit in self.autocompleteWords[firstLetter] \
                                                            if thisBit.startswith(remainder) and thisBit != remainder]
                        except KeyError: pass
                        self.autocompleteOverlap = previousStuff
                        #dPrint( 'Quiet', debuggingThisModule, 'possibleWordsB', possibleWords )

                    if possibleWords: # we have some word(s) to pop-up for possible selection
                        #dPrint( 'Quiet', debuggingThisModule, "Handle autocomplete2" )
                        if self.autocompleteBox is None:
                            self.makeAutocompleteBox()
                        else: # the Listbox is already made -- just empty it
                            #dPrint( 'Quiet', debuggingThisModule, 'empty listbox' )
                            self.autocompleteBox.delete( 0, tk.END ) # clear the listbox completely
                        # Now fill the Listbox
                        #dPrint( 'Quiet', debuggingThisModule, 'fill listbox' )
                        for word in possibleWords:
                            if BibleOrgSysGlobals.debugFlag: assert possibleWords.count( word ) == 1
                            self.autocompleteBox.insert( tk.END, word )
                        # Do a bit more set-up
                        #self.autocompleteBox.pack( side=tk.LEFT, fill=tk.BOTH )
                        self.autocompleteBox.select_set( '0' )
                        self.autocompleteBox.focus()
                    elif self.autocompleteBox is not None:
                        #dPrint( 'Quiet', debuggingThisModule, 'destroy1 autocomplete listbox -- no possible words' )
                        self.removeAutocompleteBox()
                    if self.addAllNewWords \
                    and args[0]=='insert' and args[1]=='insert' \
                    and args[2] in BibleOrgSysGlobals.TRAILING_WORD_END_CHARS:
                        # Just finished typing a word (by typing a space or something)
                        word = getWordBeforeSpace( self )
                        if word: # in the Bible modes, we also add new words as they're typed
                            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon: Adding/Updating autocomplete word", repr(word) )
                            addNewAutocompleteWord( self, word )
                            # NOTE: edited/deleted words aren't removed until the program restarts
            elif self.autocompleteBox is not None:
                #dPrint( 'Quiet', debuggingThisModule, 'destroy3 autocomplete listbox -- autocomplete is not enabled/appropriate' )
                self.removeAutocompleteBox()
            # end of auto-complete section

        #self.lastTextChangeTime = time()
        try: self.onTextNoChangeID = self.after( NO_TYPE_TIME, self.onTextNoChange ) # Reschedule no change function so we keep checking
        except KeyboardInterrupt:
            vPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon: Got keyboard interrupt in onTextChange (A) -- saving my file" )
            self.doSave() # Sometimes the above seems to lock up
            if self.onTextNoChangeID:
                self.after_cancel( self.onTextNoChangeID ) # Cancel any delayed no change checks which are scheduled
                self.onTextNoChangeID = None
    # end of TextEditWindowAddon.onTextChange


    def onTextNoChange( self ):
        """
        Called whenever the text box HASN'T CHANGED for NO_TYPE_TIME msecs.

        Checks for some types of formatting errors.
        """
        #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.onTextNoChange" )
        try: pass
        except KeyboardInterrupt:
            vPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon: Got keyboard interrupt in onTextNoChange (B) -- saving my file" )
            self.doSave() # Sometimes the above seems to lock up
            #self.after_cancel( self.onTextNoChangeID ) # Cancel any delayed no change checks which are scheduled
            #self.onTextNoChangeID = None
    # end of TextEditWindowAddon.onTextNoChange


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doShowInfo( {} )".format( event ) )

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
            + '  Line, column: {}, {}\n'.format( atLine, atColumn ) \
            + '\nFile text statistics:\n' \
            + '  Chars: {:,}\n  Lines: {:,}\n  Words: {:,}\n'.format( numChars, numLines, numWords ) \
            + '\nFile info:\n' \
            + '  Name: {}\n'.format( self.filename ) \
            + '  Folder: {}\n'.format( self.folderpath ) \
            + '\nSettings:\n' \
            + '  Autocorrect entries: {:,}\n  Autocomplete mode: {}\n  Autocomplete entries: {:,}\n  Autosave time: {} secs\n  Save changes automatically: {}' \
                    .format( len(self.autocorrectEntries), self.autocompleteMode, grandtotal, round(self.autosaveTime/1000), self.saveChangesAutomatically )

        showInfo( self, _("Window Information"), infoString )
    # end of TextEditWindowAddon.doShowInfo


    def doUndo( self, event=None ):
        vPrint( 'Never', debuggingThisModule, "TextEditWindowAddon.doUndo( {} )".format( event ) )

        try: self.textBox.edit_undo()
        except tk.TclError: showInfo( self, APP_NAME, _("Nothing to undo") )
        self.textBox.update() # force refresh
    # end of TextEditWindowAddon.doUndo


    def doRedo( self, event=None ):
        vPrint( 'Never', debuggingThisModule, "TextEditWindowAddon.doRedo( {} )".format( event ) )

        try: self.textBox.edit_redo()
        except tk.TclError: showInfo( self, APP_NAME, _("Nothing to redo") )
        self.textBox.update() # force refresh
    # end of TextEditWindowAddon.doRedo


    def doDelete( self, event=None ):                         # delete selected text, no save
        vPrint( 'Never', debuggingThisModule, "TextEditWindowAddon.doDelete( {} )".format( event ) )

        if not self.textBox.tag_ranges( tk.SEL ):
            showError( self, APP_NAME, _("No text selected") )
        else:
            self.textBox.delete( tk.SEL_FIRST, tk.SEL_LAST )
    # end of TextEditWindowAddon.doDelete


    def doCut( self, event=None ) -> None:
        """
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doCut( {} )".format( event ) )

        if not self.textBox.tag_ranges( tk.SEL ):
            showError( self, APP_NAME, _("No text selected") )
        else:
            self.doCopy() # In ChildBox class
            self.doDelete()
    # end of TextEditWindowAddon.doCut


    def doPaste( self, event=None ) -> None:
        """
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doPaste( {} )".format( event ) )
        dPrint( 'Never', debuggingThisModule, "  doPaste: {!r} {!r}".format( event.char, event.keysym ) )

        try:
            text = self.selection_get( selection='CLIPBOARD')
        except tk.TclError:
            showError( self, APP_NAME, _("Nothing to paste") )
            return
        self.textBox.insert( tk.INSERT, text)          # add at current insert cursor
        self.textBox.tag_remove( tk.SEL, tkSTART, tk.END )
        self.textBox.tag_add( tk.SEL, tk.INSERT+'-{}c'.format( len(text) ), tk.INSERT )
        self.textBox.see( tk.INSERT )                   # select it, so it can be cut
    # end of TextEditWindowAddon.doPaste


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
    ## end of TextEditWindowAddon.doGotoWindowLine


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
    ## end of TextEditWindowAddon.doBoxFind


    #def xxxdoBoxRefind( self ):
        #self.doBoxFind( self.lastfind)
    ## end of TextEditWindowAddon.doBoxRefind


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
    # end of TextEditWindowAddon.doBoxFindReplace


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
    # end of TextEditWindowAddon.onDoChange


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    def setFolderpath( self, newFolderpath ) -> None:
        """
        Store the folder path for where our files will be.

        We're still waiting for the filename.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.setFolderpath( {} )".format( repr(newFolderpath) ) )
        if debuggingThisModule or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
            assert self.filename is None
            assert self.filepath is None

        self.folderpath = newFolderpath
    # end of TextEditWindowAddon.setFolderpath

    def setFilename( self, filename:str, createFile:bool=False ):
        """
        Store the filepath to our file.

        A complement to the above function.

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.setFilename( {} )".format( repr(filename) ) )
        if debuggingThisModule or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
            assert self.folderpath

        self.filename = filename
        self.filepath = os.path.join( self.folderpath, self.filename )
        if createFile: # Create a blank file
            with open( self.filepath, mode='wt', encoding='utf-8' ) as theBlankFile: pass # write nothing
        return self._checkFilepath()
    # end of TextEditWindowAddon.setFilename

    def setPathAndFile( self, folderpath, filename:str ):
        """
        Store the filepath to our file.

        A more specific alternative to the above two functions. (The other alternative function is below.)

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.setPathAndFile( {}, {} )".format( repr(folderpath), repr(filename) ) )

        self.folderpath, self.filename = folderpath, filename
        self.filepath = os.path.join( self.folderpath, self.filename )
        return self._checkFilepath()
    # end of TextEditWindowAddon.setPathAndFile

    def setFilepath( self, newFilePath ):
        """
        Store the filepath to our file. (An alternative to the above function.)

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.setFilepath( {!r} )".format( newFilePath ) )

        self.filepath = newFilePath
        self.folderpath, self.filename = os.path.split( newFilePath )
        return self._checkFilepath()
    # end of TextEditWindowAddon.setFilepath

    def _checkFilepath( self ):
        """
        Checks to make sure that the file can be found and opened.

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon._checkFilepath()" )

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
    # end of TextEditWindowAddon._checkFilepath


    def rememberFileTimeAndSize( self ):
        """
        Just record the file modification time and size in bytes
            so that we can check later if it's changed on-disk.
        """
        self.lastFiletime = os.stat( self.filepath ).st_mtime
        self.lastFilesize = os.stat( self.filepath ).st_size
        vPrint( 'Never', debuggingThisModule, " rememberFileTimeAndSize: {} {}".format( self.lastFiletime, self.lastFilesize ) )
    # end of TextEditWindowAddon.rememberFileTimeAndSize


    def setAllText( self, newText ):
        """
        Sets the textBox (assumed to be enabled) to the given text
            then positions the insert cursor at the BEGINNING of the text.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.setAllText( {!r} )".format( newText ) )

        self.textBox.configure( state=tk.NORMAL ) # In case it was disabled
        self.textBox.delete( tkSTART, tk.END ) # Delete everything that's existing
        self.textBox.insert( tk.END, newText )
        self.textBox.highlightAllPatterns( self.patternsToHighlight )

        self.textBox.mark_set( tk.INSERT, tkSTART ) # move insert point to top
        self.textBox.see( tk.INSERT ) # scroll to top, insert is set

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( tk.FALSE ) # clear modified flag
    # end of TextEditWindowAddon.setAllText


    def loadText( self ):
        """
        Opens the file, reads all the data, and sets it into the text box.

        Can also be used to RELOAD the text (e.g., if it has changed on the disk).

        Returns True/False success flag.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.loadText()" )

        self.loading = True
        text = open( self.filepath, 'rt', encoding='utf-8' ).read()
        if text is None:
            showError( self, APP_NAME, 'Could not decode and open file ' + self.filepath )
            return False
        else:
            self.setAllText( text )
            self.loading = False
            return True
    # end of TextEditWindowAddon.loadText


    def getEntireText( self ):
        """
        This function can be overloaded in super classes
            (where the edit window might not display the entire text).
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.getEntireText()" )

        return self.getAllText()
    # end of TextEditWindowAddon.getEntireText


    def checkForDiskChanges( self, autoloadText=False ):
        """
        Check if the file has changed on disk.

        If it has, and the user hasn't yet made any changes, offer to reload.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.checkForDiskChanges()" )

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
                    #dPrint( 'Quiet', debuggingThisModule, "yndResult", repr(ynd.result) )
                    if ynd.result == True: yndResult = True # Yes was chosen
                if yndResult:
                    self.loadText() # reload
            self.rememberFileTimeAndSize()
        self.after( CHECK_DISK_CHANGES_TIME, self.checkForDiskChanges ) # Redo it so we keep checking
    # end if TextEditWindowAddon.checkForDiskChanges


    def doSaveAs( self, event=None ):
        """
        Called if the user requests a saveAs from the GUI.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doSaveAs( {} )".format( event ) )

        if self.modified():
            saveAsFilepath = asksaveasfilename( parent=self )
            #dPrint( 'Quiet', debuggingThisModule, "saveAsFilepath", repr(saveAsFilepath) )
            if saveAsFilepath:
                if self.setFilepath( saveAsFilepath ):
                    self.doSave()
    # end of TextEditWindowAddon.doSaveAs

    def doSave( self, event=None ):
        """
        Called if the user requests a save from the GUI.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doSave( {} )".format( event ) )

        if self.modified():
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
    # end of TextEditWindowAddon.doSave


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
            #dPrint( 'Quiet', debuggingThisModule, "TextEditWindowAddon.doAutosave()" )

        if self.modified():
            partialAutosaveFolderpath = self.folderpath if self.folderpath else BiblelatorGlobals.theApp.homeFolderpath
            # NOTE: Don't use a hidden folder coz user might not be able to find it
            autosaveFolderpath = os.path.join( partialAutosaveFolderpath, 'AutoSave/' ) \
                                    if APP_NAME in partialAutosaveFolderpath \
                                    else os.path.join( partialAutosaveFolderpath, DATA_SUBFOLDER_NAME, 'AutoSave/' )
            if not os.path.exists( autosaveFolderpath ): os.makedirs( autosaveFolderpath )
            lastDayFolderpath = os.path.join( autosaveFolderpath, 'LastDay/' )
            if not os.path.exists( lastDayFolderpath ): os.mkdir( lastDayFolderpath )

            autosaveFilename = self.filename if self.filename else 'Autosave.txt'
            #dPrint( 'Quiet', debuggingThisModule, 'autosaveFolderpath', repr(autosaveFolderpath), 'autosaveFilename', repr(autosaveFilename) )
            autosaveFilepath = os.path.join( autosaveFolderpath, autosaveFilename )
            lastDayFilepath = os.path.join( lastDayFolderpath, autosaveFilename )

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
    # end of TextEditWindowAddon.doAutosave


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            vPrint( 'Quiet', debuggingThisModule, "doViewSettings()" )
            BiblelatorGlobals.theApp.setDebugText( "doViewSettings…" )
        tEW = TextEditWindow( theApp )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setFilepath( self.settings.settingsFilepath ) \
        or not tEW.loadText():
            tEW.doClose()
            showError( self, APP_NAME, _("Sorry, unable to open settings file") )
            if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Failed doViewSettings" )
        else:
            BiblelatorGlobals.theApp.childWindows.append( tEW )
            if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Finished doViewSettings" )
        BiblelatorGlobals.theApp.setReadyStatus()
    # end of TextEditWindowAddon.doViewSettings


    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        fnPrint( debuggingThisModule, "doViewLog()" )
        if debuggingThisModule: BiblelatorGlobals.theApp.setDebugText( "doViewLog…" )

        filename = PROGRAM_NAME.replace('/','-').replace(':','_').replace('\\','_') + '_log.txt'
        tEW = TextEditWindow( theApp )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setPathAndFile( BiblelatorGlobals.theApp.loggingFolderpath, filename ) \
        or not tEW.loadText():
            tEW.doClose()
            showError( self, APP_NAME, _("Sorry, unable to open log file") )
            if BibleOrgSysGlobals.debugFlag: BiblelatorGlobals.theApp.setDebugText( "Failed doViewLog" )
        else:
            BiblelatorGlobals.theApp.childWindows.append( tEW )
            #if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewLog" ) # Don't do this -- adds to the log immediately
        BiblelatorGlobals.theApp.setReadyStatus()
    # end of TextEditWindowAddon.doViewLog


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doHelp( {} )".format( event ) )
        from Biblelator.Dialogs.Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of TextEditWindowAddon.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doAbout( {} )".format( event ) )
        from Biblelator.Dialogs.About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of TextEditWindowAddon.doAbout


    def doClose( self, event=None ):
        """
        Called if the window is about to be destroyed.

        Determines if we want/need to save any changes.
        """
        fnPrint( debuggingThisModule, "TextEditWindowAddon.doClose( {} )".format( event ) )

        if self.modified():
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
                place = ' in {}'.format( self.filename) if self.folderpath and self.filename else ''
                ocd = OkCancelDialog( self, _('Do you want to save your work{}?').format( place ), title=_('Save work?') )
                #dPrint( 'Quiet', debuggingThisModule, "ocdResult", repr(ocd.result) )
                if ocd.result == True: # Yes was chosen
                    saveWork = True
                else:
                    # place = 'to {}'.format( self.filename) if self.folderpath and self.filename else ''
                    ynd = YesNoDialog( self, _('Are you sure you want to lose your changes?'), title=_('Lose changes?') )
                    #dPrint( 'Quiet', debuggingThisModule, "yndResult", repr(ynd.result) )
                    if ynd.result == True: # Yes was chosen
                        self.textBox.edit_modified( tk.FALSE ) # clear Tkinter modified flag
                        self.bookTextModified = False
                    #else: saveWork = True
            if saveWork:
                self.doSave()
                if self.folderpath and self.filename: # assume we saved it
                    ChildWindow.doClose( self )
                    return

        if not self.modified():
            #dPrint( 'Quiet', debuggingThisModule, "HEREEEEEEEEE" )
            ChildWindow.doClose( self )
    # end of TextEditWindowAddon.doClose
# end of TextEditWindowAddon class



class TextEditWindow( TextEditWindowAddon, ChildWindow ):
    """
    """
    def __init__( self, parentWindow, folderpath=None, filename=None ):
        """
        """
        fnPrint( debuggingThisModule, f"TextEditWindow.__init__( pW={parentWindow}, fp={folderpath}, fn={filename} )" )
        self.folderpath, self.filename = folderpath, filename
        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'TextEditWindow __init__ {} {}'.format( folderpath, filename ) )

        ChildWindow.__init__( self, parentWindow, 'TextEditor' )
        TextEditWindowAddon.__init__( self, 'PlainTextEditWindow', folderpath, filename )

        #self.filepath = os.path.join( folderpath, filename ) if folderpath and filename else None
        #self.moduleID = None
        ##self.windowType = 'PlainTextEditWindow'
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

        vPrint( 'Never', debuggingThisModule, "TextEditWindow.__init__ finished." )
    # end of TextEditWindow.__init__
# end of TextEditWindow class



def briefDemo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    tEW = TextEditWindow( tkRootWindow )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of TextEditWindow.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    tEW = TextEditWindow( tkRootWindow )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of TextEditWindow.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of TextEditWindow.py
