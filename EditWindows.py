#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# EditWindows.py
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

LastModifiedDate = '2016-01-29' # by RJH
ShortProgName = "EditWindows"
ProgName = "Biblelator Edit Windows"
ProgVersion = '0.29'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True

import sys, os.path, logging
from collections import OrderedDict
import multiprocessing

import tkinter as tk
from tkinter.simpledialog import askstring, askinteger
from tkinter.filedialog import asksaveasfilename
from tkinter.colorchooser import askcolor
from tkinter.ttk import Style, Frame

# Biblelator imports
from BiblelatorGlobals import APP_NAME, DATA_FOLDER_NAME, START, DEFAULT, EDIT_MODE_NORMAL, EDIT_MODE_USFM, BIBLE_GROUP_CODES
from BiblelatorDialogs import showerror, showinfo, YesNoDialog, OkCancelDialog, GetBibleBookRangeDialog
from BiblelatorHelpers import createEmptyUSFMBookText, calculateTotalVersesForBook, mapReferenceVerseKey, mapParallelVerseKey
from TextBoxes import CustomText
from ChildWindows import ChildWindow, HTMLWindow
from BibleResourceWindows import BibleBox, BibleResourceWindow
from BibleReferenceCollection import BibleReferenceCollectionWindow

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
from VerseReferences import SimpleVerseKey
from BibleWriter import setDefaultControlFolder



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
        if BibleOrgSysGlobals.debugFlag: print( exp("TextEditWindow.__init__( {}, {}, {} )").format( parentApp, folderPath, filename ) )
        self.parentApp, self.folderPath, self.filename = parentApp, folderPath, filename

        # Set some dummy values required soon (esp. by refreshTitle)
        self.editMode = DEFAULT
        ChildWindow.__init__( self, self.parentApp, 'TextEditor' )
        self.moduleID = None
        self.winType = 'PlainTextEditWindow'
        self.protocol( "WM_DELETE_WINDOW", self.onCloseEditor ) # Catch when window is closed

        self.textBox['background'] = "white"
        self.textBox['selectbackground'] = "red"
        self.textBox['highlightbackground'] = "orange"
        self.textBox['inactiveselectbackground'] = "green"

        self.textBox['wrap'] = 'word'
        self.textBox.config( undo=True, autoseparators=True )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        #self.createStandardKeyboardBindings()
        self.createEditorKeyboardBindings()

        self.lastFiletime = self.lastFilesize = None
        self.clearText()

        self.autosaveTime = 3*60*1000 # msecs (zero is no autosaves)
        self.autosaveScheduled = False

        self.after( 555, self.refreshTitle )
        self.after( 2222, self.checkForDiskChanges )
    # end of TextEditWindow.__init__


    def createEditorKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.createEditorKeyboardBindings()") )
        for name,command in ( ('Paste',self.doPaste), ('Cut',self.doCut),
                             ('Undo',self.doUndo), ('Redo',self.doRedo),
                             ('Save',self.doSave), ):
            assert( (name,self.parentApp.keyBindingDict[name][0],) not in self.myKeyboardBindingsList )
            if name in self.parentApp.keyBindingDict:
                for keyCode in self.parentApp.keyBindingDict[name][1:]:
                    #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                    self.textBox.bind( keyCode, command )
                    if BibleOrgSysGlobals.debugFlag:
                        assert( keyCode not in self.myKeyboardShortcutsList )
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
        self.title( "{}[{}] {} ({}) Editable".format( '*' if self.modified() else '',
                                            _("Text"), self.filename, self.folderPath ) )
        self.after( 200, self.refreshTitle ) # Redo it so we can put up the asterisk if the text is changed
        if self.autosaveTime and self.modified() and not self.autosaveScheduled:
            self.after( self.autosaveTime, self.doAutosave ) # Redo it so we can put up the asterisk if the text is changed
            self.autosaveScheduled = True
    # end if TextEditWindow.refreshTitle


    def checkForDiskChanges( self ):
        """
        Check if the file has changed on disk.

        If it has, and the user hasn't yet made any changes, offer to reload.
        """
        #print( "checkForDiskChanges" )
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
        self.after( 2000, self.checkForDiskChanges ) # Redo it so we keep checking
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doCut()") )
        if not self.textBox.tag_ranges( tk.SEL ):
            showerror( self, APP_NAME, 'No text selected')
        else:
            self.doCopy()                       # save and delete selected text
            self.doDelete()
    # end of TextEditWindow.doCut


    def doPaste( self, event=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doPaste()") )
        try:
            text = self.selection_get( selection='CLIPBOARD')
        except tk.TclError:
            showerror( self, APP_NAME, 'Nothing to paste')
            return
        self.textBox.insert( tk.INSERT, text)          # add at current insert cursor
        self.textBox.tag_remove( tk.SEL, START, tk.END )
        self.textBox.tag_add( tk.SEL, tk.INSERT+'-%dc' % len(text), tk.INSERT )
        self.textBox.see( tk.INSERT )                   # select it, so it can be cut
    # end of TextEditWindow.doPaste


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
            assert( self.filename is None )
            assert( self.filepath is None )
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
            assert( self.folderPath )
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

        text = open( self.filepath, 'rt', encoding='utf-8' ).read()
        if text == None:
            showerror( self, APP_NAME, 'Could not decode and open file ' + self.filepath )
            return False
        else:
            self.setAllText( text )
            return True
    # end of TextEditWindow.loadText


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
                self.textBox.edit_modified( tk.FALSE ) # clear modified flag
                self.bookTextModified = False
                self.refreshTitle()
            else: self.doSaveAs()
    # end of TextEditWindow.doSave


    def doAutosave( self ):
        """
        Called if the user requests a save from the GUI.

        Sets up another call.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("TextEditWindow.doAutosave()") )
        if self.modified():
            self.doSave()
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



class USFMEditWindow( TextEditWindow, BibleResourceWindow, BibleBox ):
    """
    self.genericWindowType will be BibleEditor
    self.winType will be BiblelatorUSFMBibleEditWindow or ParatextUSFMBibleEditWindow

    Even though it contains a link to an USFMBible (InternalBible) object,
        this class always works directly with the USFM (text) files.
    """
    def __init__( self, parentApp, USFMBible, editMode=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "USFMEditWindow.__init__( {}, {} ) {}".format( parentApp, USFMBible, USFMBible.sourceFolder ) )
        self.parentApp, self.internalBible = parentApp, USFMBible
        #self.USFMFolder = self.internalBible.sourceFolder

        # Set some dummy values required soon (esp. by refreshTitle)
        self.editMode = DEFAULT
        self.bookTextModified = False
        BibleResourceWindow.__init__( self, parentApp, 'USFMBibleEditWindow', None )
        TextEditWindow.__init__( self, parentApp )
        BibleBox.__init__( self, parentApp )
        self.viewMode = 'Unformatted'

        # Make our own textBox
        self.textBox.destroy()
        self.textBox = CustomText( self, yscrollcommand=self.vScrollbar.set, wrap='word' )
        self.textBox.setTextChangeCallback( self.onTextChange )
        self.textBox['wrap'] = 'word'
        self.textBox.config( undo=True, autoseparators=True )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.config( command=self.textBox.yview ) # link the scrollbar to the text box
        #self.createStandardKeyboardBindings()
        #self.createEditorKeyboardBindings()

        # Now we need to override a few critical variables
        self.genericWindowType = 'BibleEditor'
        #self.winType = 'USFMBibleEditWindow'
        self.verseCache = OrderedDict()
        if editMode is not None: self.editMode = editMode

        if self.internalBible is None: self.editMode = None
        else:
            self.textBox['background'] = 'white'
            self.textBox['selectbackground'] = 'red'
            self.textBox['highlightbackground'] = 'orange'
            self.textBox['inactiveselectbackground'] = 'green'

        #self.textBox.bind( '<1>', self.onTextChange )
        self.folderPath = self.filename = self.filepath = None
        self.lastBBB = None
        self.bookTextBefore = self.bookText = self.bookTextAfter = None # The current text for this book
        self.exportFolderPathname = None

        #self.currentVerseKey = None
        self.loading = True
    # end of USFMEditWindow.__init__


    def refreshTitle( self ):
        referenceBit = '' if self.currentVerseKey is None else '{} {}:{} ' \
            .format( self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber() )
        self.title( '{}[{}] {} {}({}) Editable {}'.format( '*' if self.modified() else '',
                                    self.groupCode,
                                    self.internalBible.name if self.internalBible is not None else 'None',
                                    '' if self.currentVerseKey is None else referenceBit,
                                    self.editMode, self.contextViewMode ) )
    # end if USFMEditWindow.refreshTitle


    def xxdoHelp( self ):
        from Help import HelpBox
        hb = HelpBox( self.parentApp, ProgName, ProgNameVersion )
    # end of USFMEditWindow.doHelp


    def xxdoAbout( self ):
        from About import AboutBox
        ab = AboutBox( self.parentApp, ProgName, ProgNameVersion )
    # end of USFMEditWindow.doAbout


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow.createMenuBar()") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        fileMenu.add_command( label='Save', underline=0, command=self.doSave, accelerator=self.parentApp.keyBindingDict['Save'][0] )
        fileMenu.add_command( label='Save as...', underline=5, command=self.doSaveAs )
        fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu, tearoff=False )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #fileMenu.add_command( label='Export', underline=1, command=self.doMostExports )
        subfileMenuExport = tk.Menu( fileMenu, tearoff=False )
        subfileMenuExport.add_command( label='Quick exports', underline=0, command=self.doMostExports )
        subfileMenuExport.add_command( label='PhotoBible', underline=0, command=self.doPhotoBibleExport )
        subfileMenuExport.add_command( label='ODFs', underline=0, command=self.doODFsExport )
        subfileMenuExport.add_command( label='PDFs', underline=1, command=self.doPDFsExport )
        subfileMenuExport.add_command( label='All exports', underline=0, command=self.doAllExports )
        fileMenu.add_cascade( label='Export', underline=1, menu=subfileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label='Info...', underline=0, command=self.doShowInfo )
        fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.doCloseEditor )

        editMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        editMenu.add_command( label='Undo', underline=0, command=self.doUndo )
        editMenu.add_command( label='Redo', underline=0, command=self.doRedo )
        editMenu.add_separator()
        editMenu.add_command( label='Cut', underline=2, command=self.doCut )
        editMenu.add_command( label='Copy', underline=0, command=self.doCopy )
        editMenu.add_command( label='Paste', underline=0, command=self.doPaste )
        editMenu.add_separator()
        editMenu.add_command( label='Delete', underline=0, command=self.doDelete )
        editMenu.add_command( label='Select all', underline=0, command=self.doSelectAll )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label='Search', underline=0 )
        searchMenu.add_command( label='Goto line...', underline=0, command=self.doGotoLine )
        searchMenu.add_separator()
        searchMenu.add_command( label='Find...', underline=0, command=self.doFind )
        searchMenu.add_command( label='Find again', underline=5, command=self.doRefind )
        searchMenu.add_command( label='Replace...', underline=0, command=self.doFindReplace )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        gotoMenu.add_command( label='Previous book', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Next book', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Previous chapter', underline=0, command=self.doGotoPreviousChapter )
        gotoMenu.add_command( label='Next chapter', underline=0, command=self.doGotoNextChapter )
        gotoMenu.add_command( label='Previous verse', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Next verse', underline=0, command=self.notWrittenYet )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Forward', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Backward', underline=0, command=self.notWrittenYet )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Previous list item', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Next list item', underline=0, command=self.notWrittenYet )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Book', underline=0, command=self.notWrittenYet )
        gotoMenu.add_separator()
        self._groupRadioVar.set( self.groupCode )
        gotoMenu.add_radiobutton( label='Group A', underline=6, value='A', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group B', underline=6, value='B', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group C', underline=6, value='C', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group D', underline=6, value='D', variable=self._groupRadioVar, command=self.changeBibleGroupCode )

        viewMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label='View', underline=0 )
        if   self.contextViewMode == 'BeforeAndAfter': self._viewRadioVar.set( 1 )
        elif self.contextViewMode == 'BySection': self._viewRadioVar.set( 2 )
        elif self.contextViewMode == 'ByVerse': self._viewRadioVar.set( 3 )
        elif self.contextViewMode == 'ByBook': self._viewRadioVar.set( 4 )
        elif self.contextViewMode == 'ByChapter': self._viewRadioVar.set( 5 )

        viewMenu.add_radiobutton( label='Before and after...', underline=7, value=1, variable=self._viewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label='One section', underline=4, value=2, variable=self._viewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label='Single verse', underline=7, value=3, variable=self._viewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label='Whole book', underline=6, value=4, variable=self._viewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label='Whole chapter', underline=6, value=5, variable=self._viewRadioVar, command=self.changeBibleContextView )

        #viewMenu.entryconfigure( 'Before and after...', state=tk.DISABLED )
        #viewMenu.entryconfigure( 'One section', state=tk.DISABLED )
        #viewMenu.entryconfigure( 'Single verse', state=tk.DISABLED )
        #viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Check project...', underline=0, command=self.doCheckProject )
        toolsMenu.add_separator()
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        windowMenu.add_command( label='Start reference mode (A->B)', underline=6, command=self.startReferenceMode )
        windowMenu.add_command( label='Start parallel mode (A->B,C,D)', underline=6, command=self.startParallelMode )
        windowMenu.add_separator()
        windowMenu.add_command( label='Start references mode (A->)', underline=0, command=self.startReferencesMode )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label='Help', underline=0 )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout )
    # end of USFMEditWindow.createMenuBar


    def xxcreateContextMenu( self ):
        """
        """
        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label="Cut", underline=2, command=self.doCut )
        self.contextMenu.add_command( label="Copy", underline=0, command=self.doCopy )
        self.contextMenu.add_command( label="Paste", underline=0, command=self.doPaste )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Close", underline=1, command=self.doCloseEditor )

        self.bind( "<Button-3>", self.showContextMenu ) # right-click
        #self.pack()
    # end of USFMEditWindow.createContextMenu


    #def showContextMenu( self, e):
        #self.contextMenu.post( e.x_root, e.y_root )
    ## end of USFMEditWindow.showContextMenu


    #def createToolBar( self ):
        #toolbar = Frame( self, cursor='hand2', relief=tk.SUNKEN ) # bd=2
        #toolbar.pack( side=tk.BOTTOM, fill=tk.X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=tk.RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=tk.LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=tk.LEFT )
    ## end of USFMEditWindow.createToolBar


    def onTextChange( self, result, *args ):
        """
        Called whenever the text box cursor changes either with a mouse click or arrow keys.

        Checks to see if they have moved to a new chapter/verse,
            and if so, informs the parent app.
        """
        if self.loading: return # So we don't get called a million times for nothing
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.onTextChange( {}, {} )").format( repr(result), args ) )

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



        if self.textBox.edit_modified(): # check the text for USFM errors
            editedText = self.getAllText()

            # Check counts of USFM chapter and verse markers
            numChaps = editedText.count( '\\c ' )
            numVerses = editedText.count( '\\v ' )
            BBB, C, V = self.currentVerseKey.getBCV()
            #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            maxChapterMarkers = self.getNumChapters( BBB ) if self.contextViewMode=='ByBook' else 1

            if self.contextViewMode == 'BeforeAndAfter':
                maxVerseMarkers = 3
            elif self.contextViewMode == 'ByVerse':
                maxVerseMarkers = 1
            elif self.contextViewMode == 'BySection':
                maxVerseMarkers = 10
            elif self.contextViewMode == 'ByBook':
                maxVerseMarkers = self.numTotalVerses
            elif self.contextViewMode == 'ByChapter':
                maxVerseMarkers = self.getNumVerses( BBB, C )
            else: halt
            if numChaps > maxChapterMarkers:
                print( "Too many USFM chapter markers (max of {} expected)".format( maxChapterMarkers ) )
            if numVerses > maxVerseMarkers:
                print( "Too many USFM verse markers (max of {} expected)".format( maxVerseMarkers ) )

        # Try to determine the CV mark
        # It seems that we have to try various strategies because
        #       sometimes we get a 'current' mark and sometimes an 'anchor1'
        gotCV = False
        # Try to put the most useful methods first (for efficiency)
        for j, mark in enumerate( (self.textBox.mark_previous(tk.INSERT), self.textBox.mark_previous(tk.INSERT+'-1c'),
                                   self.textBox.mark_previous(tk.INSERT+' linestart+1c'), self.textBox.mark_previous(tk.INSERT+' linestart'),) ):
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #print( "  mark", j, mark )
                if mark is None: print( "    WHY is mark NONE?" )
            if mark and mark[0]=='C' and mark[1].isdigit() and 'V' in mark:
                gotCV = True; break
        if gotCV and mark != self.lastCVMark:
            self.lastCVMark = mark
            C, V = mark[1:].split( 'V', 1 )
            #self.parentApp.gotoGroupBCV( self.groupCode, self.currentVerseKey.getBBB(), C, V )
            self.after_idle( lambda: self.parentApp.gotoGroupBCV( self.groupCode, self.currentVerseKey.getBBB(), C, V ) )
    # end of USFMEditWindow.onTextChange


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doShowInfo()") )
        text  = self.getAllBookText()
        numChars = len( text )
        numLines = len( text.split( '\n' ) )
        numWords = len( text.split() )
        index = self.textBox.index( tk.INSERT )
        atLine, atColumn = index.split('.')
        BBB, C, V = self.currentVerseKey.getBCV()
        numChaps = text.count( '\\c ' )
        numVerses = text.count( '\\v ' )
        numSectionHeadings = text.count('\\s ')+text.count('\\s1 ')+text.count('\\s2 ')+text.count('\\s3 ')+text.count('\\s4 ')
        showinfo( self, '{} Window Information'.format( BBB ),
                 'Current location:\n' +
                 '  Chap:\t{}\n  Verse:\t{}\n'.format( C, V ) +
                 '  Line:\t{}\n  Column:\t{}\n'.format( atLine, atColumn ) +
                 '\nFile text statistics:\n' +
                 '  Chapts:\t{}\n  Verses:\t{}\n  Sections:\t{}\n'.format( numChaps, numVerses, numSectionHeadings ) +
                 '  Chars:\t{}\n  Lines:\t{}\n  Words:\t{}\n'.format( numChars, numLines, numWords ) +
                 '\nFile info:\n' +
                 '  Name:\t{}\n  Folder:\t{}\n  BookFN:\t{}\n  SourceFldr:\t{}\n'.format( self.filename, self.filepath, self.bookFilename, self.internalBible.sourceFolder )
                 )
    # end of USFMEditWindow.doShowInfo


    def modified( self ):
        return self.bookTextModified or self.textBox.edit_modified()
    # end of USFMEditWindow.modified


    def getBookDataFromDisk( self, BBB ):
        """
        Fetches and returns the internal Bible data for the given book
            by reading the USFM source file completely
            and returning the text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.getBookDataFromDisk( {} ) was {}").format( BBB, self.lastBBB ) )
        if BBB != self.lastBBB:
            #self.bookText = None
            #self.bookTextModified = False
            self.lastBBB = BBB
        if self.internalBible is not None:
            try: self.bookFilename = self.internalBible.possibleFilenameDict[BBB]
            except (AttributeError,KeyError) as err: # we have no books, or at least, not this book!
                #print( "  getBookDataFromDisk error: {}".format( err ) )
                #return None
                self.bookFilename = '{}-{}.USFM'.format( BibleOrgSysGlobals.BibleBooksCodes.getUSFMNumber(BBB),
                            BibleOrgSysGlobals.BibleBooksCodes.getUSFMAbbreviation(BBB) )
            self.bookFilepath = os.path.join( self.internalBible.sourceFolder, self.bookFilename )
            if self.setFilepath( self.bookFilepath ): # For title displays, etc.
                #print( exp('gVD'), BBB, repr(self.bookFilepath), repr(self.internalBible.encoding) )
                bookText = open( self.bookFilepath, 'rt', encoding=self.internalBible.encoding ).read()
                if bookText == None:
                    showerror( self, APP_NAME, 'Could not decode and open file ' + self.bookFilepath + ' with encoding ' + self.internalBible.encoding )
                return bookText
    # end of USFMEditWindow.getBookDataFromDisk


    def EditWindowsXXXdisplayAppendVerse( self, firstFlag, verseKey, verseDataString, currentVerse=False ):
        """
        Add the requested verse to the end of self.textBox.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #try: print( exp("USFMEditWindow.displayAppendVerse"), firstFlag, verseKey,
                       #'None' if verseDataString is None else verseDataString.replace('\n','NL'), currentVerse )
            #except UnicodeEncodeError: print( exp("USFMEditWindow.displayAppendVerse"), firstFlag, verseKey, currentVerse )

        BBB, C, V = verseKey.getBCV()
        markName = 'C{}V{}'.format( C, V )
        self.textBox.mark_set( markName, tk.INSERT )
        self.textBox.mark_gravity( markName, tk.LEFT )
        lastCharWasSpace = haveTextFlag = not firstFlag

        if verseDataString is None:
            if C!='0': print( "  ", exp("displayAppendVerse"), "has no data for", self.moduleID, verseKey )
            #self.textBox.insert( tk.END, '--' )
        elif self.viewMode == DEFAULT:
            for line in verseDataString.split( '\n' ):
                if line=='': continue
                line += '\n'
                if line[0]=='\\':
                    marker = ''
                    for char in line[1:]:
                        if char!='¬' and not char.isalnum(): break
                        marker += char
                    cleanText = line[len(marker)+1:].lstrip()
                else:
                    marker, cleanText = None, line
                if marker and marker[0]=='¬': pass # Ignore end markers for now
                elif marker in ('chapters',): pass # Ignore added markers for now
                else: self.textBox.insert( tk.END, line, marker )
        elif self.viewMode == 'Formatted':
            # This needs fixing -- indents, etc. should be in stylesheet not hard-coded
            for line in verseDataString.split( '\n' ):
                if line=='': continue
                line += '\n'
                if line[0]=='\\':
                    marker = ''
                    for char in line[1:]:
                        if char!='¬' and not char.isalnum(): break
                        marker += char
                    cleanText = line[len(marker)+1:].lstrip()
                else:
                    marker, cleanText = None, line
                #if isinstance( entry, tuple ):
                    #marker, cleanText = entry[0], entry[3]
                #else: marker, cleanText = entry.getMarker(), entry.getCleanText()
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
                elif marker == 'p#' and self.winType=='DBPBibleResourceWindow':
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
                    logging.critical( exp("USFMEditWindow.displayAppendVerse: Unknown marker {} {} from {}").format( marker, cleanText, verseDataString ) )
        else:
            logging.critical( exp("BibleResourceWindow.displayAppendVerse: Unknown {} view mode").format( repr(self.viewMode) ) )
    # end of USFMEditWindow.displayAppendVerse


    def xxxgetBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("USFMEditWindow.getBeforeAndAfterBibleData( {} )").format( newVerseKey ) )
            assert( isinstance( newVerseKey, SimpleVerseKey ) )

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
                        logging.critical( exp("getBeforeAndAfterBibleData failed at"), prevBBB, prevIntC )
                    failed = True
                #if not failed:
                    #if BibleOrgSysGlobals.debugFlag: print( " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            else:
                prevBBB = self.parentApp.genericBibleOrganisationalSystem.getPreviousBookCode( BBB )
                prevIntC = self.getNumChapters( prevBBB )
                prevIntV = self.getNumVerses( prevBBB, prevIntC )
                if BibleOrgSysGlobals.debugFlag: print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
            if not failed:
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getContextVerseData( previousVerseKey )
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
            nextVerseData = self.getContextVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        verseData = self.getContextVerseData( newVerseKey )

        return verseData, previousVersesData, nextVersesData
    # end of USFMEditWindow.getBeforeAndAfterBibleData


    def cacheBook( self, BBB ):
        """
        Puts the book data from self.bookText into the self.verseCache dictionary
            accessible by verse key.

        Doesn't clear the cache before starting,
            so it appends duplicate entries.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("USFMEditWindow.cacheBook( {} )").format( BBB ) )
            assert( isinstance( BBB, str ) )

        def addCacheEntry( BBB, C, V, data ):
            """
            """
            #print( "addCacheEntry", BBB, C, V, data )
            assert( BBB and C and V and data )
            verseKeyHash = SimpleVerseKey( BBB, C, V ).makeHash()
            if verseKeyHash in self.verseCache: # Oh, how come we already have this key???
                logging.critical( "cacheBook: We have a duplicate {} -- appending {} to {}".format( verseKeyHash, repr(data), repr(self.verseCache[verseKeyHash]) ) )
                data = self.verseCache[verseKeyHash] + '\n' + data
            self.verseCache[verseKeyHash] = data.replace( '\n\n', '\n' ) # Weed out blank lines
        # end of add_cascade

        C = V = '0'
        currentEntry = ''
        for line in self.bookText.split( '\n' ):
            if line.startswith( '\\c ' ) or line.startswith( '\\C ' ):
                newC = ''
                for char in line[3:]:
                    if char.isdigit(): newC += char
                    else: break
                if newC:
                    if currentEntry:
                        addCacheEntry( BBB, C, V, currentEntry )
                        currentEntry = ''
                    C, V = newC, '0'
            elif line.startswith( '\\v ' ) or line.startswith( '\\V ' ):
                newV = ''
                for char in line[3:]:
                    if char.isdigit(): newV += char
                    else: break
                if newV:
                    if currentEntry:
                        addCacheEntry( BBB, C, V, currentEntry )
                        currentEntry = ''
                    V = newV
            elif C=='0' and line.startswith( '\\' ):
                if currentEntry:
                    addCacheEntry( BBB, C, V, currentEntry )
                    currentEntry = ''
                V = str( int(V) + 1 )
            currentEntry += line + '\n'
        if currentEntry:
            addCacheEntry( BBB, C, V, currentEntry )
        #print( BBB, "verseCache:", self.verseCache )
    # end of USFMEditWindow.cacheBook


    def getCachedVerseData( self, verseKey ):
        """
        Returns the requested verse from our cache if it's there,
            otherwise returns None.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("getCachedVerseData( {} )").format( verseKey ) )
        try: return self.verseCache[verseKey.makeHash()]
        except KeyError: return None
    # end of USFMEditWindow.getCachedVerseData


    def updateShownBCV( self, newReferenceVerseKey ):
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "USFMEditWindow.updateShownBCV( {} from {} ) for".format( newReferenceVerseKey, self.currentVerseKey ), self.moduleID )
            #print( "contextViewMode", self.contextViewMode )

        oldVerseKey = self.currentVerseKey
        oldBBB = None if oldVerseKey is None else oldVerseKey.getBBB()

        if newReferenceVerseKey is None:
            newBBB = None
            self.setCurrentVerseKey( None )
        else: # it must be a real verse key
            assert( isinstance( newReferenceVerseKey, SimpleVerseKey ) )
            refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
            newBBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
            newVerseKey = SimpleVerseKey( newBBB, C, V, S )
            self.setCurrentVerseKey( newVerseKey )
            #if newBBB == 'PSA': halt
            if newBBB != oldBBB: self.numTotalVerses = calculateTotalVersesForBook( newBBB, self.getNumChapters, self.getNumVerses )

        if self.textBox.edit_modified(): # we need to extract the changes into self.bookText
            logging.critical( "We need to extract the changes into self.bookText for {}".format( oldBBB ) )
            editedText = self.getAllText()
            if self.contextViewMode == 'BeforeAndAfter':
                print( "\n\nWe need to extract the BeforeAndAfter changes into self.bookText!!!\n\n")
                halt
                #bibleData = self.getBeforeAndAfterBibleData( newVerseKey )
                #if bibleData:
                    #verseData, previousVerses, nextVerses = bibleData
                    #for verseKey,previousVerseData in previousVerses:
                        #self.displayAppendVerse( startingFlag, verseKey, previousVerseData )
                        #startingFlag = False
                    #self.displayAppendVerse( startingFlag, newVerseKey, verseData, currentVerse=True )
                    #for verseKey,nextVerseData in nextVerses:
                        #self.displayAppendVerse( False, verseKey, nextVerseData )

            elif self.contextViewMode == 'BySection':
                print( "\n\nWe need to extract the BySection changes into self.bookText!!!\n\n")
                halt
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

            elif self.contextViewMode == 'ByVerse':
                print( "\n\nWe need to extract the ByVerse changes into self.bookText!!!\n\n")
                halt
                C, V = self.currentVerseKey.getCV()
                #self.displayAppendVerse( True, newVerseKey, self.getCachedVerseData( newVerseKey ), currentVerse=True )

            elif self.contextViewMode == 'ByBook':
                print( 'USFMEditWindow.updateShownBCV', 'ByBook1' )
                self.bookText = editedText
                if newBBB == oldBBB: # We haven't changed books
                    self.verseCache = OrderedDict()
                    self.cacheBook( oldBBB )

            elif self.contextViewMode == 'ByChapter':
                print( "\n\nWe need to extract the ByChapter changes into self.bookText!!!\n\n")
                halt
                C = self.currentVerseKey.getChapterNumber()
                #BBB, C, V = newVerseKey.getBCV()
                #intV = newVerseKey.getVerseNumberInt()
                #try: numVerses = self.getNumVerses( BBB, C )
                #except KeyError: numVerses = 0
                #for thisV in range( 0, numVerses ):
                    #thisVerseKey = SimpleVerseKey( BBB, C, thisV )
                    #thisVerseData = self.getCachedVerseData( thisVerseKey )
                    #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData, currentVerse=thisV==intV )
                    #startingFlag = False

            else:
                logging.critical( exp("USFMEditWindow.updateShownBCV: Bad context view mode {}").format( self.contextViewMode ) )
                if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode
            self.bookTextModified = True

        if newReferenceVerseKey is None:
            if oldVerseKey is not None:
                if self.bookTextModified: self.doSave() # resets bookTextModified flag
                self.clearText() # Leaves the text box enabled
                self.textBox['state'] = tk.DISABLED # Don't allow editing
                self.textBox.edit_modified( False ) # clear modified flag (otherwise we could empty the book file)
                self.refreshTitle()
            return

        savedCursorPosition = self.textBox.index( tk.INSERT ) # Something like 55.6 for line 55, before column 6
        print( "savedCursorPosition", savedCursorPosition )   #   Beginning of file is 1.0

        # Safety-check since editor code not finished yet for all modes
        if self.contextViewMode in ('BeforeAndAfter','BySection','ByVerse','ByChapter',):
            print( exp("updateShownBCV: Safety-check converted {} contextViewMode for edit window").format( repr(self.contextViewMode) ) )
            self._viewRadioVar.set( 4 ) # ByBook
            self.changeBibleContextView()

        # Now check if the book they're viewing has changed since last time
        #       If so, save the old book if necessary
        #       then either load or create the new book
        #markAsUnmodified = True
        if newBBB != oldBBB: # we've switched books
            if self.bookTextModified: self.doSave() # resets bookTextModified flag
            self.bookText = self.getBookDataFromDisk( newBBB )
            if self.bookText is None:
                showerror( self, _("USFM Editor"), _("We need to create the book: {} in {}").format( newBBB, self.internalBible.sourceFolder ) )
                #ocd = OkCancelDialog( self, _("We need to create the book: {}".format( newBBB ) ), title=_('Create?') )
                #print( "ocdResult", repr(ocd.result) )
                #if ocd.result == True: # Ok was chosen
                self.setFilename( '{}-{}.USFM'.format( BibleOrgSysGlobals.BibleBooksCodes.getUSFMNumber(newBBB),
                            BibleOrgSysGlobals.BibleBooksCodes.getUSFMAbbreviation(newBBB) ), createFile=True )
                self.bookText = createEmptyUSFMBookText( newBBB, self.getNumChapters, self.getNumVerses )
                #markAsUnmodified = False
                self.bookTextModified = True
                #self.doSave() # Save the chapter/verse markers (blank book outline) ## Doesn't work -- saves a blank file
            if self.bookText is not None: self.cacheBook( newBBB )

        # Now load the desired part of the book into the edit window
        if self.bookText is not None:
            self.loading = True # Turns off USFMEditWindow onTextChange notifications for now
            self.clearText() # Leaves the text box enabled
            startingFlag = True

            if self.contextViewMode == 'BeforeAndAfter':
                halt
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
                halt
                self.displayAppendVerse( True, newVerseKey, self.getCachedVerseData( newVerseKey ), currentVerse=True )

            elif self.contextViewMode == 'BySection':
                halt
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
                print( 'USFMEditWindow.updateShownBCV', 'ByBook2' )
                BBB, C, V = newVerseKey.getBCV()
                intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
                for thisC in range( 0, self.getNumChapters( BBB )+1 ):
                    try: numVerses = self.getNumVerses( BBB, thisC )
                    except KeyError: numVerses = 0
                    for thisV in range( 0, numVerses+1 ):
                        thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                        thisVerseData = self.getCachedVerseData( thisVerseKey )
                        self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                                currentVerse=thisC==intC and thisV==intV )
                        startingFlag = False

            elif self.contextViewMode == 'ByChapter':
                halt
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
                logging.critical( exp("USFMEditWindow.updateShownBCV: Bad context view mode {}").format( self.contextViewMode ) )
                if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( tk.FALSE ) # clear modified flag
        self.loading = False # Turns onTextChange notifications back on
        self.lastCVMark = None

        # Make sure we can see what we're supposed to be looking at
        desiredMark = 'C{}V{}'.format( newVerseKey.getChapterNumber(), newVerseKey.getVerseNumber() )
        try: self.textBox.see( desiredMark )
        except tk.TclError: print( exp("USFMEditWindow.updateShownBCV couldn't find {}").format( repr( desiredMark ) ) )
        self.lastCVMark = desiredMark

        # Put the cursor back where it was (if necessary)
        if self.contextViewMode == 'ByBook':
            self.loading = True # Turns off USFMEditWindow onTextChange notifications for now
            self.textBox.mark_set( tk.INSERT, savedCursorPosition )
            self.loading = False # Turns onTextChange notifications back on

        self.refreshTitle()
    # end of USFMEditWindow.updateShownBCV


    def _prepareInternalBible( self ):
        """
        Prepare to do some of the exports or checks available in BibleOrgSys.

        Leaves the wait cursor displayed.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow._prepareInternalBible()") )
        if self.modified(): self.doSave()
        if self.internalBible is not None:
            self.parentApp.setWaitStatus( _("Preparing internal Bible...") )
            self.internalBible.load()
    # end of USFMEditWindow._prepareInternalBible

    def _prepareForExports( self ):
        """
        Prepare to do some of the exports available in BibleOrgSys.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow.prepareForExports()") )
        self._prepareInternalBible()
        if self.internalBible is not None:
            self.parentApp.setWaitStatus( _("Preparing for export...") )
            if self.exportFolderPathname is None:
                fp = self.folderPath
                if fp and fp[-1] in '/\\': fp = fp[:-1] # Removing trailing slash
                self.exportFolderPathname = fp + 'Export/'
                #print( "eFolder", repr(self.exportFolderPathname) )
                if not os.path.exists( self.exportFolderPathname ):
                    os.mkdir( self.exportFolderPathname )
            setDefaultControlFolder( '../BibleOrgSys/ControlFiles/' )
            self.parentApp.setStatus( _("Export in process...") )
    # end of USFMEditWindow._prepareForExports

    def doMostExports( self ):
        """
        Do most of the quicker exports available in BibleOrgSys.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doMostExports()") )
        self._prepareForExports()
        self.internalBible.doAllExports( self.exportFolderPathname )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doMostExports

    def doPhotoBibleExport( self ):
        """
        Do the BibleOrgSys PhotoBible export.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doPhotoBibleExport()") )
        self._prepareForExports()
        self.internalBible.toPhotoBible( os.path.join( self.exportFolderPathname, 'BOS_PhotoBible_Export/' ) )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doPhotoBibleExport

    def doODFsExport( self ):
        """
        Do the BibleOrgSys ODFsExport export.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doODFsExport()") )
        self._prepareForExports()
        self.internalBible.toODF( os.path.join( self.exportFolderPathname, 'BOS_ODF_Export/' ) )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doODFsExport

    def doPDFsExport( self ):
        """
        Do the BibleOrgSys PDFsExport export.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow.doPDFsExport()") )
        self._prepareForExports()
        self.internalBible.toTeX( os.path.join( self.exportFolderPathname, 'BOS_PDF(TeX)_Export/' ) )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doPDFsExport

    def doAllExports( self ):
        """
        Do all exports available in BibleOrgSys.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow.doAllExports()") )
        self._prepareForExports()
        self.internalBible.doAllExports( self.exportFolderPathname, wantPhotoBible=True, wantODFs=True, wantPDFs=True )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doAllExports


    def doCheckProject( self ):
        """
        Run the BibleOrgSys checks on the project.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow.doCheckProject()") )
        #self._prepareInternalBible()
        currentBBB = self.currentVerseKey.getBBB()
        gBBRD = GetBibleBookRangeDialog( self, self.internalBible, currentBBB, title=_('Books to be checked') )
        #if BibleOrgSysGlobals.debugFlag: print( "gBBRDResult", repr(gBBRD.result) )
        if gBBRD.result:
            if BibleOrgSysGlobals.debugFlag: assert( isinstance( gBBRD.result, list ) )
            if len(gBBRD.result)==1 and gBBRD.result[0]==currentBBB:
                # It's just the current book to check
                if self.modified(): self.doSave()
                self.internalBible.loadBookIfNecessary( currentBBB )
            else: # load all books
                self._prepareInternalBible()
            self.parentApp.setWaitStatus( _("Doing Bible checks...") )
            self.internalBible.check( gBBRD.result )
            displayExternally = False
            if displayExternally: # Call up a browser window
                import webbrowser
                indexFile = self.internalBible.makeErrorHTML( self.folderPath, gBBRD.result )
                webbrowser.open( indexFile )
            else: # display internally in our HTMLDialog
                indexFile = self.internalBible.makeErrorHTML( self.folderPath, gBBRD.result )
                hW = HTMLWindow( self, indexFile )
                self.parentApp.childWindows.append( hW )
                if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openCheckWindow" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doCheckProject


    def getAllBookText( self ):
        """
        Gets the displayed text and adds it to the surrounding text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.getAllBookText()") )
        boxText = self.getAllText() # from the edit window
        allBookText = self.bookTextBefore + boxText + self.bookTextAfter
        return allBookText
    # end of USFMEditWindow.getAllBookText


    def doSave( self, event=None ):
        """
        Called if the user requests a save from the GUI.

        Same as TextEditWindow.doSave except
            has a bit more housekeeping to do
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doSave()") )
        if self.modified():
            if self.folderPath and self.filename:
                filepath = os.path.join( self.folderPath, self.filename )
                allBookText = self.getAllBookText()
                with open( filepath, mode='wt' ) as theFile:
                    theFile.write( allBookText )
                self.rememberFileTimeAndSize()
                self.internalBible.bookNeedsReloading[self.currentVerseKey.getBBB()] = True
                #self.textBox.edit_modified( tk.FALSE ) # clear modified flag
                self.bookTextModified = False
                #self.internalBible.unloadBooks() # coz they're now out of date
                #self.internalBible.reloadBook( self.currentVerseKey.getBBB() ) # coz it's now out of date -- what? why?
                self.refreshTitle()
            else: self.doSaveAs()
    # end of USFMEditWindow.doSave


    def startReferenceMode( self ):
        """
        Called from the GUI to duplicate this window into Group B,
            and then link A->B to show OT references from the NT (etc.)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.startReferenceMode()") )
        if self.groupCode != BIBLE_GROUP_CODES[0]: # Not in first/default BCV group
            ynd = YesNoDialog( self, _('You are in group {}. Ok to change to group {}?').format( self.groupCode, BIBLE_GROUP_CODES[0] ), title=_('Continue?') )
            #print( "yndResult", repr(ynd.result) )
            if ynd.result != True: return
            self.groupCode = BIBLE_GROUP_CODES[0]
        assert( self.groupCode == BIBLE_GROUP_CODES[0] ) # In first/default BCV group
        uEW = USFMEditWindow( self.parentApp, self.internalBible, editMode=self.editMode )
        #if windowGeometry: uEW.geometry( windowGeometry )
        uEW.winType = self.winType # override the default
        uEW.moduleID = self.moduleID
        uEW.setFolderPath( self.folderPath )
        uEW.settings = self.settings
        #uEW.settings.loadUSFMMetadataInto( uB )
        uEW.groupCode = BIBLE_GROUP_CODES[1]
        uEW.BCVUpdateType = 'ReferenceMode'
        uEW.updateShownBCV( mapReferenceVerseKey( self.currentVerseKey ) )
        self.parentApp.childWindows.append( uEW )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openBiblelatorReferenceBibleEditWindow" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.startReferenceMode


    def startParallelMode( self ):
        """
        Called from the GUI to duplicate this window into Groups BCD,
            and then link A->BCD to show synoptic gospel parallels (etc.)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.startParallelMode()") )
        if self.groupCode != BIBLE_GROUP_CODES[0]: # Not in first/default BCV group
            ynd = YesNoDialog( self, _('You are in group {}. Ok to change to group {}?').format( self.groupCode, BIBLE_GROUP_CODES[0] ), title=_('Continue?') )
            #print( "yndResult", repr(ynd.result) )
            if ynd.result != True: return
            self.groupCode = BIBLE_GROUP_CODES[0]
        assert( self.groupCode == BIBLE_GROUP_CODES[0] ) # In first/default BCV group
        for j in range( 1, len(BIBLE_GROUP_CODES) ):
            uEW = USFMEditWindow( self.parentApp, self.internalBible, editMode=self.editMode )
            #if windowGeometry: uEW.geometry( windowGeometry )
            uEW.winType = self.winType # override the default
            uEW.moduleID = self.moduleID
            uEW.setFolderPath( self.folderPath )
            uEW.settings = self.settings
            #uEW.settings.loadUSFMMetadataInto( uB )
            uEW.groupCode = BIBLE_GROUP_CODES[j]
            uEW.BCVUpdateType = 'ParallelMode'
            uEW.updateShownBCV( mapParallelVerseKey( BIBLE_GROUP_CODES[j], self.currentVerseKey ) )
            self.parentApp.childWindows.append( uEW )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openBiblelatorParallelBibleEditWindows" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.startParallelMode


    def startReferencesMode( self ):
        """
        Called from the GUI to duplicate this window into Group B,
            and then link A->B to show OT references from the NT (etc.)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.startReferencesMode()") )
        if self.groupCode != BIBLE_GROUP_CODES[0]: # Not in first/default BCV group
            ynd = YesNoDialog( self, _('You are in group {}. Ok to change to group {}?').format( self.groupCode, BIBLE_GROUP_CODES[0] ), title=_('Continue?') )
            #print( "yndResult", repr(ynd.result) )
            if ynd.result != True: return
            self.groupCode = BIBLE_GROUP_CODES[0]
        assert( self.groupCode == BIBLE_GROUP_CODES[0] ) # In first/default BCV group
        BRCW = BibleReferenceCollectionWindow( self.parentApp, self.internalBible )
        #if windowGeometry: uEW.geometry( windowGeometry )
        BRCW.winType = self.winType # override the default
        BRCW.moduleID = self.moduleID
        BRCW.setFolderPath( self.folderPath )
        BRCW.settings = self.settings
        #BRCW.settings.loadUSFMMetadataInto( uB )
        BRCW.groupCode = BIBLE_GROUP_CODES[0] # Stays the same as the source window!
        #BRCW.BCVUpdateType = 'ReferencesMode' # Leave as default
        BRCW.updateShownBCV( self.currentVerseKey )
        self.parentApp.childWindows.append( BRCW )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openBiblelatorReferencesBibleWindow" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.startReferencesMode


    def xxcloseEditor( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow.closeEditor()") )
        if self.modified():
            pass # refuse to close yet (temp.........)
        else: self.closeChildWindow()
    # end of USFMEditWindow.closeEditor
# end of USFMEditWindow class



class ESFMEditWindow( USFMEditWindow ):
    pass
# end of ESFMEditWindow class



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
# end of EditWindows.demo


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
# end of EditWindows.py