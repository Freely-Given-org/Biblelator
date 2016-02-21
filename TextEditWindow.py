#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TextEditWindow.py
#
# The actual edit windows for Biblelator text editing and USFM/ESFM Bible editing
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
xxx to allow editing of USFM Bibles using Python3 and Tkinter.
"""

from gettext import gettext as _

LastModifiedDate = '2016-02-21' # by RJH
ShortProgName = "TextEditWindow"
ProgName = "Biblelator Text Edit Window"
ProgVersion = '0.30'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True

import sys, os.path, logging #, re
#from collections import OrderedDict
#import multiprocessing

import tkinter as tk
#from tkinter.simpledialog import askstring, askinteger
#from tkinter.filedialog import asksaveasfilename
#from tkinter.colorchooser import askcolor
#from tkinter.ttk import Style, Frame

# Biblelator imports
from BiblelatorGlobals import DEFAULT
#APP_NAME, DATA_FOLDER_NAME, START, DEFAULT, EDIT_MODE_NORMAL, EDIT_MODE_USFM, BIBLE_GROUP_CODES
#from BiblelatorDialogs import showerror, showinfo, YesNoDialog, OkCancelDialog, GetBibleBookRangeDialog
#from BiblelatorHelpers import createEmptyUSFMBookText, calculateTotalVersesForBook, mapReferenceVerseKey, mapParallelVerseKey
from TextBoxes import CustomText
from ChildWindows import ChildWindow #, HTMLWindow
#from BibleResourceWindows import BibleBox, BibleResourceWindow
#from BibleReferenceCollection import BibleReferenceCollectionWindow

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals



REFRESH_TITLE_TIME = 500 # msecs
CHECK_DISK_CHANGES_TIME = 33333 # msecs



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



class TextEditWindow( ChildWindow ):
    def __init__( self, parentApp, folderPath=None, filename=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("TextEditWindow.__init__( {}, {}, {} )").format( parentApp, folderPath, filename ) )
        self.parentApp, self.folderPath, self.filename = parentApp, folderPath, filename

        # Set some dummy values required soon (esp. by refreshTitle)
        self.editMode = DEFAULT
        ChildWindow.__init__( self, self.parentApp, 'TextEditor' ) # calls refreshTitle
        self.moduleID = None
        self.winType = 'PlainTextEditWindow'
        self.protocol( "WM_DELETE_WINDOW", self.onCloseEditor ) # Catch when window is closed

        self.loading = True

        # Make our own custom textBox which allows a callback function
        #   Delete these two lines and the callback line if you don't need either autocorrect or autocomplete
        self.textBox.destroy()
        self.textBox = CustomText( self, yscrollcommand=self.vScrollbar.set, wrap='word' )

        self.textBox['background'] = "white"
        self.textBox['selectbackground'] = "red"
        self.textBox['highlightbackground'] = "orange"
        self.textBox['inactiveselectbackground'] = "green"

        self.textBox['wrap'] = 'word'
        self.textBox.config( undo=True, autoseparators=True )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.textBox.setTextChangeCallback( self.onTextChange )
        #self.createStandardKeyboardBindings()
        self.createEditorKeyboardBindings()

        self.lastFiletime = self.lastFilesize = None
        self.clearText()

        self.autocorrectEntries = []
        # Temporarily include these default autocorrect values
        self.autocorrectEntries.append( ('<<','“') ) # Cycle through quotes with angle brackets
        self.autocorrectEntries.append( ('“<','‘') )
        self.autocorrectEntries.append( ('‘<',"'") )
        self.autocorrectEntries.append( ("'<",'<') )
        self.autocorrectEntries.append( ('>>','”') )
        self.autocorrectEntries.append( ('”>','’') )
        self.autocorrectEntries.append( ('’>',"'") )
        self.autocorrectEntries.append( ("'>",'>') )
        self.autocorrectEntries.append( ('--','–') ) # Cycle through en-dash/em-dash with hyphens
        self.autocorrectEntries.append( ('–-','—') )
        self.autocorrectEntries.append( ('—-','-') )
        self.autocorrectEntries.append( ('(in','(incl)') )
        self.autocorrectEntries.append( ('(ex','(excl)') )
        # This next bit needs to be done whenever the autocorrect entries are changed
        self.maxAutocorrectLength = 0
        for inChars,outChars in self.autocorrectEntries:
            self.maxAutocorrectLength = max( len(inChars), self.maxAutocorrectLength )

        self.autocompleteBox = self.autocompleteType = None
        self.autocompleteWords = {}
        self.autocompleteWordChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        # Note: I guess we could have used non-word chars instead (to stop the backwards word search)
        self.autocompleteMinLength = 3 # Show the window after this many characters have been typed
        self.autocompleteMaxLength = 12 # Remove window after this many characters have been typed
        self.existingAutocompleteWordText = ''

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: # temporarily put some words in
            from AutocompleteFunctions import setAutocompleteWords
            setAutocompleteWords( self, ('a','an','ate','apple','bicycle','banana','cat','caterpillar','catastrophic','catrionic','opportunity') )
            self.autocompleteType = 'GivenList'

        self.autosaveTime = 2*60*1000 # msecs (zero is no autosaves)
        self.autosaveScheduled = False

        self.after( CHECK_DISK_CHANGES_TIME, self.checkForDiskChanges )
        #self.after( REFRESH_TITLE_TIME, self.refreshTitle )
        self.loading = False

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.__init__ finished.") )
    # end of TextEditWindow.__init__


    def createEditorKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.createEditorKeyboardBindings()") )
        for name,command in ( ('Paste',self.doPaste), ('Cut',self.doCut),
                             ('Undo',self.doUndo), ('Redo',self.doRedo),
                             ('Save',self.doSave), ):
            assert (name,self.parentApp.keyBindingDict[name][0],) not in self.myKeyboardBindingsList
            if name in self.parentApp.keyBindingDict:
                for keyCode in self.parentApp.keyBindingDict[name][1:]:
                    #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                    self.textBox.bind( keyCode, command )
                    if BibleOrgSysGlobals.debugFlag:
                        assert keyCode not in self.myKeyboardShortcutsList
                        self.myKeyboardShortcutsList.append( keyCode )
                self.myKeyboardBindingsList.append( (name,self.parentApp.keyBindingDict[name][0],) )
            else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
        #self.textBox.bind('<Control-v>', self.doPaste ); self.textBox.bind('<Control-V>', self.doPaste )
        #self.textBox.bind('<Control-s>', self.doSave ); self.textBox.bind('<Control-S>', self.doSave )
        #self.textBox.bind('<Control-x>', self.doCut ); self.textBox.bind('<Control-X>', self.doCut )
        #self.textBox.bind('<Control-g>', self.doRefind ); self.textBox.bind('<Control-G>', self.doRefind )
    # end of TextEditWindow.createEditorKeyboardBindings()


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("TextEditWindow.createMenuBar()") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        fileMenu.add_command( label='Save', underline=0, command=self.doSave, accelerator=self.parentApp.keyBindingDict['Save'][0] )
        fileMenu.add_command( label='Save as...', underline=5, command=self.doSaveAs )
        #fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu, tearoff=False )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu, tearoff=False )
        #subfileMenuExport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label='HTML', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Export', underline=0, menu=subfileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label='Info...', underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict['Info'][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.doCloseEditor, accelerator=self.parentApp.keyBindingDict['Close'][0] )

        editMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        editMenu.add_command( label='Undo', underline=0, command=self.doUndo, accelerator=self.parentApp.keyBindingDict['Undo'][0] )
        editMenu.add_command( label='Redo', underline=0, command=self.doRedo, accelerator=self.parentApp.keyBindingDict['Redo'][0] )
        editMenu.add_separator()
        editMenu.add_command( label='Cut', underline=2, command=self.doCut, accelerator=self.parentApp.keyBindingDict['Cut'][0] )
        editMenu.add_command( label='Copy', underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict['Copy'][0] )
        editMenu.add_command( label='Paste', underline=0, command=self.doPaste, accelerator=self.parentApp.keyBindingDict['Paste'][0] )
        editMenu.add_separator()
        editMenu.add_command( label='Delete', underline=0, command=self.doDelete )
        editMenu.add_command( label='Select all', underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict['SelectAll'][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label='Search', underline=0 )
        searchMenu.add_command( label='Goto line...', underline=0, command=self.doGotoLine, accelerator=self.parentApp.keyBindingDict['Line'][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label='Find...', underline=0, command=self.doFind, accelerator=self.parentApp.keyBindingDict['Find'][0] )
        searchMenu.add_command( label='Find again', underline=5, command=self.doRefind, accelerator=self.parentApp.keyBindingDict['Refind'][0] )
        searchMenu.add_command( label='Replace...', underline=0, command=self.doFindReplace )
        #searchMenu.add_separator()
        #searchMenu.add_command( label='Grep...', underline=0, command=self.onGrep )

##        gotoMenu = tk.Menu( self.menubar )
##        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
##        gotoMenu.add_command( label='Previous book', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label='Next book', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label='Previous chapter', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label='Next chapter', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label='Previous verse', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label='Next verse', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_separator()
##        gotoMenu.add_command( label='Forward', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label='Backward', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_separator()
##        gotoMenu.add_command( label='Previous list item', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_command( label='Next list item', underline=0, command=self.notWrittenYet )
##        gotoMenu.add_separator()
##        gotoMenu.add_command( label='Book', underline=0, command=self.notWrittenYet )

##        viewMenu = tk.Menu( self.menubar, tearoff=False )
##        self.menubar.add_cascade( menu=viewMenu, label='View', underline=0 )
##        viewMenu.add_command( label='Whole chapter', underline=6, command=self.notWrittenYet )
##        viewMenu.add_command( label='Whole book', underline=6, command=self.notWrittenYet )
##        viewMenu.add_command( label='Single verse', underline=7, command=self.notWrittenYet )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label='Help', underline=0 )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp, accelerator=self.parentApp.keyBindingDict['Help'][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout, accelerator=self.parentApp.keyBindingDict['About'][0] )
    # end of TextEditWindow.createMenuBar


    def createContextMenu( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.createContextMenu()") )
        self.contextMenu = tk.Menu( self, tearoff=False )
        self.contextMenu.add_command( label="Cut", underline=2, command=self.doCut, accelerator=self.parentApp.keyBindingDict['Cut'][0] )
        self.contextMenu.add_command( label="Copy", underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict['Copy'][0] )
        self.contextMenu.add_command( label="Paste", underline=0, command=self.doPaste, accelerator=self.parentApp.keyBindingDict['Paste'][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Select all", underline=7, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict['SelectAll'][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Close", underline=1, command=self.doCloseEditor, accelerator=self.parentApp.keyBindingDict['Close'][0] )

        self.bind( "<Button-3>", self.showContextMenu ) # right-click
    # end of TextEditWindow.createContextMenu


    #def showContextMenu( self, e):
        #self.contextMenu.post( e.x_root, e.y_root )
    ## end of TextEditWindow.showContextMenu


    #def createToolBar( self ):
        #toolbar = Frame( self, cursor='hand2', relief=tk.SUNKEN ) # bd=2
        #toolbar.pack( side=tk.BOTTOM, fill=tk.X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=tk.RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=tk.LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=tk.LEFT )
    ## end of TextEditWindow.createToolBar


    def refreshTitle( self ):
        """
        Refresh the title of the text edit window,
            put an asterisk if it's modified.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("TextEditWindow.refreshTitle()") )

        self.title( "{}[{}] {} ({}) Editable".format( '*' if self.modified() else '',
                                            _("Text"), self.filename, self.folderPath ) )
        self.refreshTitleContinue()
    # end if TextEditWindow.refreshTitle

    def refreshTitleContinue( self ):
        """
        Check if an autosave is needed,
            and schedule the next refresh.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("TextEditWindow.refreshTitleContinue()") )

        self.after( REFRESH_TITLE_TIME, self.refreshTitle ) # Redo it so we can put up the asterisk if the text is changed
        try:
            if self.autosaveTime and self.modified() and not self.autosaveScheduled:
                self.after( self.autosaveTime, self.doAutosave ) # Redo it so we can put up the asterisk if the text is changed
                self.autosaveScheduled = True
        except AttributeError:
            print( "Autosave not set-up properly yet" )
    # end if TextEditWindow.refreshTitleContinue


    def OnAutocompleteChar( self, event ):
        """
        Used by autocomplete routines in onTextChange.

        Handles key presses entered into the pop-up word selection (list) box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.OnAutocompleteChar( {!r}, {!r} )").format( event.char, event.keysym ) )
            print( exp("TextEditWindow.OnAutocompleteChar()") )
            #print( 'char', repr(event.char), 'keysym', repr(event.keysym) )
            assert self.autocompleteBox is not None

        #if event.keysym == 'ESC':
        #if event.char==' ' or event.char in self.autocompleteWordChars:
            #self.textBox.insert( tk.INSERT, event.char ) # Causes onTextChange which reassesses
        if event.keysym == 'BackSpace':
            row, column = self.textBox.index(tk.INSERT).split('.')
            column = str( int(column) - 1 )
            self.textBox.delete( row + '.' + column, tk.INSERT )
        elif event.keysym == 'Return':
            self.acceptAutocompleteSelection()
        #elif event.keysym in ( 'Up', 'Down', 'Shift_R', 'Shift_L',
                              #'Control_L', 'Control_R', 'Alt_L',
                              #'Alt_R', 'parenleft', 'parenright'):
            #pass
        elif event.keysym == 'Escape':
            self.removeAutocompleteBox()
        elif event.char:
            self.textBox.insert( tk.INSERT, event.char ) # Causes onTextChange which reassesses
    # end of TextEditWindow.OnAutocompleteChar


    def acceptAutocompleteSelection( self, event=None ):
        """
        Used by autocomplete routines in onTextChange.

        Gets the chosen word and inserts the end of it into the text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.acceptAutocompleteSelection()") )
            assert self.autocompleteBox is not None

        result = self.autocompleteBox.get( tk.ACTIVE )
        print( 'result', result )
        self.removeAutocompleteBox()

        # Autocomplete by inserting the rest of the selected word plus a space
        # NOTE: The user has to backspace over the space if they don't want it (e.g., to put a period)
        # NOTE: The box reappears with the current code if we don't append the space -- would need to add a flag
        self.textBox.insert( tk.INSERT, result[len(self.existingAutocompleteWordText):] + ' ' )
    # end of TextEditWindow.acceptAutocompleteSelection


    def removeAutocompleteBox( self ):
        """
        Remove the pop-up Listbox (in a Frame in a Toplevel) when it's no longer required.
        Used by autocomplete routines in onTextChange.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.removeAutocompleteBox()") )
            assert self.autocompleteBox is not None

        self.textBox.focus()
        self.autocompleteBox.master.master.destroy() # master is Frame, master.master is Toplevel
        self.autocompleteBox = None
    # end of TextEditWindow.removeAutocompleteBox


    def onTextChange( self, result, *args ):
        """
        Called whenever the text box cursor changes either with a mouse click or arrow keys.

        Checks to see if they have moved to a new chapter/verse,
            and if so, informs the parent app.
        """
        if self.loading: return # So we don't get called a million times for nothing
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.onTextChange( {}, {} )").format( repr(result), args ) )

        #if 0: # Get line and column info
            #lineColumn = self.textBox.index( tk.INSERT )
            #print( "lc", repr(lineColumn) )
            #line, column = lineColumn.split( '.', 1 )
            #print( "l,c", repr(line), repr(column) )

        #if 0: # get formatting tag info
            #tagNames = self.textBox.tag_names( tk.INSERT )
            #tagNames2 = self.textBox.tag_names( lineColumn )
            #tagNames3 = self.textBox.tag_names( tk.INSERT + ' linestart' )
            #tagNames4 = self.textBox.tag_names( lineColumn + ' linestart' )
            #tagNames5 = self.textBox.tag_names( tk.INSERT + ' linestart+1c' )
            #tagNames6 = self.textBox.tag_names( lineColumn + ' linestart+1c' )
            #print( "tN", tagNames )
            #if tagNames2!=tagNames or tagNames3!=tagNames or tagNames4!=tagNames or tagNames5!=tagNames or tagNames6!=tagNames:
                #print( "tN2", tagNames2 )
                #print( "tN3", tagNames3 )
                #print( "tN4", tagNames4 )
                #print( "tN5", tagNames5 )
                #print( "tN6", tagNames6 )
                #halt

        #if 0: # show various mark strategies
            #mark1 = self.textBox.mark_previous( tk.INSERT )
            #mark2 = self.textBox.mark_previous( lineColumn )
            #mark3 = self.textBox.mark_previous( tk.INSERT + ' linestart' )
            #mark4 = self.textBox.mark_previous( lineColumn + ' linestart' )
            #mark5 = self.textBox.mark_previous( tk.INSERT + ' linestart+1c' )
            #mark6 = self.textBox.mark_previous( lineColumn + ' linestart+1c' )
            #print( "mark1", mark1 )
            #if mark2!=mark1:
                #print( "mark2", mark1 )
            #if mark3!=mark1 or mark4!=mark1 or mark5!=mark1 or mark6!=mark1:
                #print( "mark3", mark3 )
                #if mark4!=mark3:
                    #print( "mark4", mark4 )
                #print( "mark5", mark5 )
                #if mark6!=mark5:
                    #print( "mark6", mark6 )


        if self.textBox.edit_modified():
            # Handle auto-correct
            if self.autocorrectEntries and args[0]=='insert' and args[1]=='insert':
                print( "Handle autocorrect" )
                previousText = self.getCharactersBeforeCursor( self.maxAutocorrectLength )
                #print( "previousText", repr(previousText) )
                for inChars,outChars in self.autocorrectEntries:
                    if previousText.endswith( inChars ):
                        #print( "Going to replace {!r} with {!r}".format( inChars, outChars ) )
                        # Delete the typed character(s) and replace with the new one(s)
                        self.textBox.delete( tk.INSERT+'-{}c'.format( len(inChars) ), tk.INSERT )
                        self.textBox.insert( tk.INSERT, outChars )
            # end of auto-correct section


            # Handle auto-complete
            #print( 'args[0]', repr(args[0]) )
            if self.autocompleteType is not None and self.autocompleteWords and args[0] in ('insert','delete',):
                print( "Handle autocomplete1" )
                lastAutocompleteWordText = self.existingAutocompleteWordText
                self.existingAutocompleteWordText = self.getWordCharactersBeforeCursor( self.autocompleteMaxLength )
                if self.existingAutocompleteWordText != lastAutocompleteWordText:
                    # we've had an actual change in the entered text
                    if len(self.existingAutocompleteWordText) >= self.autocompleteMinLength:
                        firstLetter, remainder = self.existingAutocompleteWordText[0], self.existingAutocompleteWordText[1:]
                        try: possibleWords = [firstLetter+word for word in self.autocompleteWords[firstLetter] \
                                                                if word.startswith( self.existingAutocompleteWordText[1:] )]
                        except KeyError: possibleWords = None
                        print( 'possibleWords', possibleWords )
                        if possibleWords:
                            print( "Handle autocomplete2" )
                            if self.autocompleteBox is None:
                                print( 'create listbox' )
                                x, y, cx, cy = self.textBox.bbox( tk.INSERT )
                                topLevel = tk.Toplevel( self.textBox.master )
                                topLevel.wm_overrideredirect(1) # Don't display window decorations (close button, etc.)
                                topLevel.wm_geometry( '+{}+{}' \
                                    .format( x + self.textBox.winfo_rootx() + 2, y + cy + self.textBox.winfo_rooty() ) )
                                frame = tk.Frame( topLevel, highlightthickness=1, highlightcolor='darkgreen' )
                                frame.pack( fill=tk.BOTH, expand=tk.YES )
                                autocompleteScrollBar = tk.Scrollbar( frame, highlightthickness=0 )
                                autocompleteScrollBar.pack( side=tk.RIGHT, fill='y' )
                                self.autocompleteBox = tk.Listbox( frame, highlightthickness=0,
                                                            relief="flat",
                                                            yscrollcommand=autocompleteScrollBar.set,
                                                            height=6 )
                                autocompleteScrollBar.config( command=self.autocompleteBox.yview )
                                self.autocompleteBox.pack( side=tk.LEFT, fill=tk.BOTH )
                                #self.autocompleteBox.select_set( '0' )
                                #self.autocompleteBox.focus()
                                self.autocompleteBox.bind( '<Key>', self.OnAutocompleteChar )
                                self.autocompleteBox.bind( '<Double-1>', self.acceptAutocompleteSelection )
                                #else: # old code
                                    #self.autocompleteBox = tk.Listbox( self.textBox )
                                    #self.autocompleteBox.bind( '<Double-Button-1>', self.acceptAutocompleteSelection )
                                    #self.autocompleteBox.bind( '<Right>', self.acceptAutocompleteSelection )
                                    #self.autocompleteBox.place( x=self.winfo_x(), y=self.winfo_y()+self.winfo_height() )
                            else: # the Listbox is already made -- just empty it
                                print( 'empty listbox' )
                                self.autocompleteBox.delete( 0, tk.END ) # clear the listbox completely
                            # Now fill the Listbox
                            print( 'fill listbox' )
                            for word in possibleWords:
                                if BibleOrgSysGlobals.debugFlag: assert possibleWords.count( word ) == 1
                                self.autocompleteBox.insert( tk.END, word )
                            # Do a bit more set-up
                            #self.autocompleteBox.pack( side=tk.LEFT, fill=tk.BOTH )
                            self.autocompleteBox.select_set( '0' )
                            self.autocompleteBox.focus()
                            #self.autocompleteBox.bind( '<Key>', self.OnAutocompleteChar )
                            #self.autocompleteBox.bind( '<Double-1>', self.acceptAutocompleteSelection )

                        elif self.autocompleteBox is not None:
                            print( 'destroy1 autocomplete listbox -- no possible words' )
                            self.removeAutocompleteBox()
                    elif self.autocompleteBox is not None:
                        print( 'destroy2 autocomplete listbox -- not enough typed yet' )
                        self.removeAutocompleteBox()
            elif self.autocompleteBox is not None:
                print( 'destroy3 autocomplete listbox -- autocomplete is not enabled/appropriate' )
                self.removeAutocompleteBox()
            # end of auto-complete section
    # end of TextEditWindow.onTextChange


    def checkForDiskChanges( self ):
        """
        Check if the file has changed on disk.

        If it has, and the user hasn't yet made any changes, offer to reload.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("TextEditWindow.checkForDiskChanges()") )

        if ( self.lastFiletime and os.stat( self.filepath ).st_mtime != self.lastFiletime ) \
        or ( self.lastFilesize and os.stat( self.filepath ).st_size != self.lastFilesize ):
            if self.modified():
                showerror( self, APP_NAME, _('File {} has also changed on disk').format( repr(self.filename) ) )
            else: # We haven't modified the file since loading it
                ynd = YesNoDialog( self, _('File {} has changed on disk. Reload?').format( repr(self.filename) ), title=_('Reload?') )
                #print( "yndResult", repr(ynd.result) )
                if ynd.result == True: # Yes was chosen
                    self.loadText() # reload
            self.rememberFileTimeAndSize()
        self.after( CHECK_DISK_CHANGES_TIME, self.checkForDiskChanges ) # Redo it so we keep checking
    # end if TextEditWindow.checkForDiskChanges


    def doUndo( self, event=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doUndo()") )
        try: self.textBox.edit_undo()
        except tk.TclError: showinfo( self, APP_NAME, 'Nothing to undo' )
        self.textBox.update() # force refresh
    # end of TextEditWindow.doUndo


    def doRedo( self, event=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doRedo()") )
        try: self.textBox.edit_redo()
        except tk.TclError: showinfo( self, APP_NAME, 'Nothing to redo' )
        self.textBox.update() # force refresh
    # end of TextEditWindow.doRedo


    def doDelete( self, event=None ):                         # delete selected text, no save
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doDelete()") )
        if not self.textBox.tag_ranges( tk.SEL ):
            showerror( self, APP_NAME, 'No text selected')
        else:
            self.textBox.delete( tk.SEL_FIRST, tk.SEL_LAST )
    # end of TextEditWindow.doDelete


    def doCut( self, event=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doCut()") )

        if not self.textBox.tag_ranges( tk.SEL ):
            showerror( self, APP_NAME, 'No text selected')
        else:
            self.doCopy()                       # save and delete selected text
            self.doDelete()
    # end of TextEditWindow.doCut


    def doPaste( self, event=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doPaste()") )
        try:
            text = self.selection_get( selection='CLIPBOARD')
        except tk.TclError:
            showerror( self, APP_NAME, 'Nothing to paste')
            return
        self.textBox.insert( tk.INSERT, text)          # add at current insert cursor
        self.textBox.tag_remove( tk.SEL, START, tk.END )
        self.textBox.tag_add( tk.SEL, tk.INSERT+'-{}c'.format( len(text) ), tk.INSERT )
        self.textBox.see( tk.INSERT )                   # select it, so it can be cut
    # end of TextEditWindow.doPaste


    def getCharactersBeforeCursor( self, charCount=1 ):
        """
        Needed for auto-correct functions.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("TextEditWindow.getCharactersBeforeCursor( {} )").format( charCount ) )

        previousText = self.textBox.get( tk.INSERT+'-{}c'.format( charCount ), tk.INSERT )
        #print( 'previousText', repr(previousText) )
        return previousText
    # end of TextEditWindow.getCharactersBeforeCursor


    def getWordCharactersBeforeCursor( self, maxCount=4 ):
        """
        Needed for auto-complete functions.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.getCharactersBeforeCursor( {} )").format( maxCount ) )

        previousText = self.textBox.get( tk.INSERT+'-{}c'.format( maxCount ), tk.INSERT )
        print( "previousText", repr(previousText) )
        wordText = ''
        for previousChar in reversed( previousText ):
            if previousChar in self.autocompleteWordChars:
                wordText = previousChar + wordText
            else: break
        print( 'wordText', repr(wordText) )
        return wordText
    # end of TextEditWindow.getWordCharactersBeforeCursor


    ############################################################################
    # Search menu commands
    ############################################################################

    def xxxdoGotoLine( self, forceline=None):
        line = forceline or askinteger( APP_NAME, 'Enter line number' )
        self.textBox.update()
        self.textBox.focus()
        if line is not None:
            maxindex = self.textBox.index( tk.END+'-1c' )
            maxline  = int( maxindex.split('.')[0] )
            if line > 0 and line <= maxline:
                self.textBox.mark_set( tk.INSERT, '{}.0'.format(line) ) # goto line
                self.textBox.tag_remove( tk.SEL, START, tk.END )          # delete selects
                self.textBox.tag_add( tk.SEL, tk.INSERT, 'insert + 1l' )  # select line
                self.textBox.see( tk.INSERT )                          # scroll to line
            else:
                showerror( self, APP_NAME, 'No such line number' )
    # end of TextEditWindow.doGotoLine


    def xxxdoFind( self, lastkey=None):
        key = lastkey or askstring( APP_NAME, 'Enter search string' )
        self.textBox.update()
        self.textBox.focus()
        self.lastfind = key
        if key:
            nocase = self.optionsDict['caseinsens']
            where = self.textBox.search( key, tk.INSERT, tk.END, nocase=nocase )
            if not where:                                          # don't wrap
                showerror( self, APP_NAME, 'String not found' )
            else:
                pastkey = where + '+%dc' % len(key)           # index past key
                self.textBox.tag_remove( tk.SEL, START, tk.END )         # remove any sel
                self.textBox.tag_add( tk.SEL, where, pastkey )        # select key
                self.textBox.mark_set( tk.INSERT, pastkey )           # for next find
                self.textBox.see( where )                          # scroll display
    # end of TextEditWindow.doFind


    def xxxdoRefind( self ):
        self.doFind( self.lastfind)
    # end of TextEditWindow.doRefind


    def doFindReplace( self ):
        """
        Non-modal find/change dialog
        2.1: pass per-dialog inputs to callbacks, may be > 1 change dialog open
        """
        newPopupWindow = Toplevel( self )
        newPopupWindow.title( '{} - change'.format( APP_NAME ) )
        Label( newPopupWindow, text='Find text?', relief=RIDGE, width=15).grid( row=0, column=0 )
        Label( newPopupWindow, text='Change to?', relief=RIDGE, width=15).grid( row=1, column=0 )
        entry1 = Entry( newPopupWindow )
        entry2 = Entry( newPopupWindow )
        entry1.grid( row=0, column=1, sticky=EW )
        entry2.grid( row=1, column=1, sticky=EW )

        def doFind():                         # use my entry in enclosing scope
            self.doFind( entry1.get() )         # runs normal find dialog callback

        def onApply():
            self.onDoChange( entry1.get(), entry2.get() )

        Button( newPopupWindow, text='Find',  command=doFind ).grid(row=0, column=2, sticky=EW )
        Button( newPopupWindow, text='Apply', command=onApply).grid(row=1, column=2, sticky=EW )
        newPopupWindow.columnconfigure( 1, weight=1 )      # expandable entries
    # end of TextEditWindow.doFindReplace


    def onDoChange( self, findtext, changeto):
        # on Apply in change dialog: change and refind
        if self.textBox.tag_ranges( tk.SEL ):                      # must find first
            self.textBox.delete( tk.SEL_FIRST, tk.SEL_LAST)
            self.textBox.insert( tk.INSERT, changeto)             # deletes if empty
            self.textBox.see( tk.INSERT )
            self.doFind( findtext )                          # goto next appear
            self.textBox.update() # force refresh
    # end of TextEditWindow.onDoChange


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    def setFolderPath( self, newFolderPath ):
        """
        Store the folder path for where our files will be.

        We're still waiting for the filename.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.setFolderPath( {} )").format( repr(newFolderPath) ) )
            assert self.filename is None
            assert self.filepath is None
        self.folderPath = newFolderPath
    # end of TextEditWindow.setFolderPath

    def setFilename( self, filename, createFile=False ):
        """
        Store the filepath to our file.

        A complement to the above function.

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.setFilename( {} )").format( repr(filename) ) )
            assert self.folderPath
        self.filename = filename
        self.filepath = os.path.join( self.folderPath, self.filename )
        if createFile: # Create a blank file
            with open( self.filepath, mode='wt' ) as theBlankFile: pass # write nothing
        return self._checkFilepath()
    # end of TextEditWindow.setFilename

    def setPathAndFile( self, folderPath, filename ):
        """
        Store the filepath to our file.

        A more specific alternative to the above two functions. (The other alternative function is below.)

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.setPathAndFile( {}, {} )").format( repr(folderPath), repr(filename) ) )
        self.folderPath, self.filename = folderPath, filename
        self.filepath = os.path.join( self.folderPath, self.filename )
        return self._checkFilepath()
    # end of TextEditWindow.setPathAndFile

    def setFilepath( self, newFilePath ):
        """
        Store the filepath to our file. (An alternative to the above function.)

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.setFilepath( {} )").format( repr(newFilePath) ) )
        self.filepath = newFilePath
        self.folderPath, self.filename = os.path.split( newFilePath )
        return self._checkFilepath()
    # end of TextEditWindow.setFilepath

    def _checkFilepath( self ):
        """
        Checks to make sure that the file can be found and opened.

        Also gets the file size and last edit time so we can detect if it's changed later.

        Returns True/False success flag.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow._checkFilepath()") )

        if not os.path.isfile( self.filepath ):
            showerror( self, APP_NAME, 'No such file path: {}'.format( repr(self.filepath) ) )
            return False
        if not os.access( self.filepath, os.R_OK ):
            showerror( self, APP_NAME, 'No permission to read {} in {}'.format( repr(self.filename), repr(self.folderPath) ) )
            return False
        if not os.access( self.filepath, os.W_OK ):
            showerror( self, APP_NAME, 'No permission to write {} in {}'.format( repr(self.filename), repr(self.folderPath) ) )
            return False

        self.rememberFileTimeAndSize()

        self.refreshTitle()
        return True
    # end of TextEditWindow._checkFilepath


    def rememberFileTimeAndSize( self ):
        """
        """
        self.lastFiletime = os.stat( self.filepath ).st_mtime
        self.lastFilesize = os.stat( self.filepath ).st_size
        print( " rememberFileTimeAndSize: {} {}".format( self.lastFiletime, self.lastFilesize ) )
    # end of TextEditWindow.rememberFileTimeAndSize


    def loadText( self ):
        """
        Opens the file, reads all the data, and sets it into the text box.

        Can also be used to RELOAD the text (e.g., if it has changed on the disk).

        Returns True/False success flag.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.loadText()") )

        self.loading = True
        text = open( self.filepath, 'rt', encoding='utf-8' ).read()
        if text == None:
            showerror( self, APP_NAME, 'Could not decode and open file ' + self.filepath )
            return False
        else:
            self.setAllText( text )
            self.loading = False
            return True
    # end of TextEditWindow.loadText


    #def setAutocompleteWords( self, wordList, append=False ):
        #"""
        #Given a word list, set the entries into the autocomplete words
            #and then do necessary house-keeping.

        #Note that the original word order is preserved (if the wordList has an order)
            #so that more common/likely words can appear at the top of the list if desired.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( exp("TextEditWindow.setAutocompleteWords( {} )").format( wordList, append ) )
            #print( exp("TextEditWindow.setAutocompleteWords()") )

        #if not append: self.autocompleteWords = {}

        #for word in wordList:
            #firstLetter, remainder = word[0], word[1:]
            #if firstLetter not in self.autocompleteWords: self.autocompleteWords[firstLetter] = []
            #self.autocompleteWords[firstLetter].append( remainder )
            #for char in word:
                #if char not in self.autocompleteWordChars:
                    #self.autocompleteWordChars += char
    ## end of TextEditWindow.setAutocompleteWords


    def doSaveAs( self, event=None ):
        """
        Called if the user requests a saveAs from the GUI.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doSaveAs()") )
        if self.modified():
            saveAsFilepath = asksaveasfilename()
            #print( "saveAsFilepath", repr(saveAsFilepath) )
            if saveAsFilepath:
                if self.setFilepath( saveAsFilepath ):
                    self.doSave()
    # end of TextEditWindow.doSaveAs

    def doSave( self, event=None ):
        """
        Called if the user requests a save from the GUI.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doSave()") )

        if self.modified():
            if self.folderPath and self.filename:
                filepath = os.path.join( self.folderPath, self.filename )
                allText = self.getAllText() # from the displayed edit window
                with open( filepath, mode='wt' ) as theFile:
                    theFile.write( allText )
                self.rememberFileTimeAndSize()
                self.textBox.edit_modified( tk.FALSE ) # clear Tkinter modified flag
                #self.bookTextModified = False
                self.refreshTitle()
            else: self.doSaveAs()
    # end of TextEditWindow.doSave


    def doAutosave( self ):
        """
        Called on a timer to save a copy of the file in a separate location
            if it's been modified.

        Schedules another call.

        Doesn't use a hidden folder for the autosave files so the user can find them:
            If a save has been done, an AutoSave folder is created in the save folder,
            if not, the AutoSave folder is created in the home folder.
                (Yes, this can result in old AutoSave files in the home folder.)
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("TextEditWindow.doAutosave()") )

        if self.modified():
            partialAutosaveFolderPath = self.folderPath if self.folderPath else self.parentApp.homeFolderPath
            # NOTE: Don't use a hidden folder coz user might not be able to find it
            autosaveFolderPath = os.path.join( partialAutosaveFolderPath, 'AutoSave/' )
            if not os.path.exists( autosaveFolderPath ): os.mkdir( autosaveFolderPath )
            autosaveFilename = self.filename if self.filename else 'Autosave.txt'
            #print( 'autosaveFolderPath', repr(autosaveFolderPath), 'autosaveFilename', repr(autosaveFilename) )
            allText = self.getAllText() # from the displayed edit window
            with open( os.path.join( autosaveFolderPath, autosaveFilename ), mode='wt' ) as theFile:
                theFile.write( allText )
            self.after( self.autosaveTime, self.doAutosave )
        else:
            self.autosaveScheduled = False # Will be set again by refreshTitle
    # end of TextEditWindow.doAutosave


    def doCloseEditor( self, event=None ):
        """
        Called if the user requests a close from the GUI.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doCloseEditor()") )
        self.onCloseEditor()
    # end of TextEditWindow.closeEditor

    def onCloseEditor( self ):
        """
        Called if the window is about to be destroyed.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.onCloseEditor()") )
        if self.modified():
            if self.folderPath and self.filename:
                self.doSave()
                self.closeChildWindow()
            else: # we need to ask where to save it
                self.doSaveAs()
                if self.folderPath and self.filename: # assume we saved it
                    self.closeChildWindow()
        else: self.closeChildWindow()
    # end of TextEditWindow.onCloseEditor
# end of TextEditWindow class



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
    uEW = USFMEditWindow( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of TextEditWindow.demo


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
# end of TextEditWindow.py