#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# EditWindows.py
#   Last modified: 2014-10-18 (also update ProgVersion below)
#
# xxx program for Biblelator Bible display/editing
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
xxx to allow editing of USFM Bibles using Python3 and Tkinter.
"""

ShortProgName = "EditWindows"
ProgName = "Biblelator Edit Windows"
ProgVersion = "0.19"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, os.path, configparser, logging
from gettext import gettext as _
import multiprocessing

from tkinter import TclError, Toplevel, Text, Menu
from tkinter import NORMAL, DISABLED, LEFT, RIGHT, BOTH, YES, TRUE, FALSE, \
                    END, INSERT, SEL, SEL_FIRST, SEL_LAST
from tkinter.messagebox import showerror, showinfo
from tkinter.simpledialog import askstring, askinteger
from tkinter.filedialog import SaveAs
from tkinter.colorchooser import askcolor
from tkinter.ttk import Style, Frame

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
from VerseReferences import SimpleVerseKey
#import USFMBible

# Biblelator imports
from BiblelatorGlobals import APP_NAME, START, EDIT_MODE_NORMAL, EDIT_MODE_USFM
from ResourceWindows import ResourceWindow
from BibleResourceWindows import BibleResourceWindow



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



class TextEditWindow( ResourceWindow ):
    def __init__( self, parentApp, folderPath=None, filename=None ):
        if Globals.debugFlag: print( t("TextEditWindow.__init__( {}, {}, {} )").format( parentApp, folderPath, filename ) )
        self.parentApp, self.folderPath, self.filename = parentApp, folderPath, filename

        # Set some dummy values required soon (esp. by refreshTitle)
        self.editMode = 'Default'
        ResourceWindow.__init__( self, self.parentApp, 'TextEditor' )
        self.moduleID = None
        self.winType = 'PlainTextEditWindow'
        self.protocol( "WM_DELETE_WINDOW", self.closeEditor ) # Catch when window is closed

        self.textBox['background'] = "white"
        self.textBox['selectbackground'] = "red"
        self.textBox['highlightbackground'] = "orange"
        self.textBox['inactiveselectbackground'] = "green"

        self.textBox['wrap'] = 'word'
        self.textBox.config( undo=TRUE, autoseparators=TRUE )
        self.clearText()
    # end of TextEditWindow.__init__


    def refreshTitle( self ):
        self.title( "{}[{}] {} ({}) Editable".format( '*' if self.modified() else '',
                                            _("Text"), self.filename, self.folderPath ) )
    # end if TextEditWindow.refreshTitle


    def xxnotWrittenYet( self ):
        showerror( _("Not implemented"), _("Not yet available, sorry") )
    # end of TextEditWindow.notWrittenYet


    def doHelp( self ):
        from Help import HelpBox
        hb = HelpBox( self.parentApp, ProgName, ProgNameVersion )
    # end of TextEditWindow.doHelp


    def doAbout( self ):
        from About import AboutBox
        ab = AboutBox( self.parentApp, ProgName, ProgNameVersion )
    # end of TextEditWindow.doAbout


    def createMenuBar( self ):
        self.menubar = Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        fileMenu.add_command( label='Save', underline=0, command=self.notWrittenYet )
        fileMenu.add_command( label='Save as...', underline=5, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #subfileMenuImport = Menu( fileMenu )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #subfileMenuExport = Menu( fileMenu )
        #subfileMenuExport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label='HTML', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Export', underline=0, menu=subfileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label='Info...', underline=0, command=self.onInfo )
        fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.closeEditor )

        editMenu = Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        editMenu.add_command( label='Undo', underline=0, command=self.onUndo )
        editMenu.add_command( label='Redo', underline=0, command=self.onRedo )
        editMenu.add_separator()
        editMenu.add_command( label='Cut', underline=2, command=self.onCut )
        editMenu.add_command( label='Copy', underline=0, command=self.onCopy )
        editMenu.add_command( label='Paste', underline=0, command=self.onPaste )
        editMenu.add_separator()
        editMenu.add_command( label='Delete', underline=0, command=self.onDelete )
        editMenu.add_command( label='Select all', underline=0, command=self.onSelectAll )
        #editMenu.add_separator()
        #editMenu.add_command( label='Find...', underline=0, command=self.onFind )
        #editMenu.add_command( label='Replace...', underline=0, command=self.onReplace )

        searchMenu = Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label='Search', underline=0 )
        searchMenu.add_command( label='Goto line...', underline=0, command=self.onGoto )
        searchMenu.add_separator()
        searchMenu.add_command( label='Find...', underline=0, command=self.onFind )
        searchMenu.add_command( label='Find again', underline=5, command=self.onRefind )
        searchMenu.add_command( label='Replace...', underline=0, command=self.onChange )
        #searchMenu.add_separator()
        #searchMenu.add_command( label='Grep...', underline=0, command=self.onGrep )

##        gotoMenu = Menu( self.menubar )
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

##        viewMenu = Menu( self.menubar )
##        self.menubar.add_cascade( menu=viewMenu, label='View', underline=0 )
##        viewMenu.add_command( label='Whole chapter', underline=6, command=self.notWrittenYet )
##        viewMenu.add_command( label='Whole book', underline=6, command=self.notWrittenYet )
##        viewMenu.add_command( label='Single verse', underline=7, command=self.notWrittenYet )

        toolsMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )

        helpMenu = Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label='Help', underline=0 )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout )

        #filename = filedialog.askopenfilename()
        #filename = filedialog.asksaveasfilename()
        #dirname = filedialog.askdirectory()
        #colorchooser.askcolor(initialcolor='#ff0000')
        #messagebox.showinfo(message='Have a good day')
        #messagebox.askyesno( message='Are you sure you want to install SuperVirus?' icon='question' title='Install' )
    # end of TextEditWindow.createMenuBar


    def createContextMenu( self ):
        """
        """
        self.contextMenu = Menu( self, tearoff=0 )
        self.contextMenu.add_command( label="Cut", underline=2, command=self.onCut )
        self.contextMenu.add_command( label="Copy", underline=0, command=self.onCopy )
        self.contextMenu.add_command( label="Paste", underline=0, command=self.onPaste )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Select all", underline=7, command=self.onSelectAll )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Close", underline=1, command=self.onClose )

        self.bind( "<Button-3>", self.showContextMenu ) # right-click
    # end of TextEditWindow.createContextMenu


    #def showContextMenu( self, e):
        #self.contextMenu.post( e.x_root, e.y_root )
    ## end of TextEditWindow.showContextMenu


    #def createToolBar( self ):
        #toolbar = Frame( self, cursor='hand2', relief=SUNKEN ) # bd=2
        #toolbar.pack( side=BOTTOM, fill=X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=LEFT )
    ## end of TextEditWindow.createToolBar


    def onUndo( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onUndo()") )
        try: self.textBox.edit_undo()
        except TclError:
            showinfo( APP_NAME, 'Nothing to undo')
    # end of TextEditWindow.onUndo


    def onRedo( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onRedo()") )
        try: self.textBox.edit_redo()
        except TclError:
            showinfo( APP_NAME, 'Nothing to redo')
    # end of TextEditWindow.onRedo


    def xxxonCopy( self ):                           # get text selected by mouse, etc.
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onCopy()") )
        if not self.textBox.tag_ranges( SEL ):       # save in cross-app clipboard
            showerror( APP_NAME, 'No text selected')
        else:
            text = self.textBox.get( SEL_FIRST, SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
    # end of TextEditWindow.onCopy


    def onDelete( self ):                         # delete selected text, no save
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onDelete()") )
        if not self.textBox.tag_ranges( SEL ):
            showerror( APP_NAME, 'No text selected')
        else:
            self.textBox.delete( SEL_FIRST, SEL_LAST)
    # end of TextEditWindow.onDelete


    def onCut( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onCut()") )
        if not self.textBox.tag_ranges( SEL ):
            showerror( APP_NAME, 'No text selected')
        else:
            self.onCopy()                       # save and delete selected text
            self.onDelete()
    # end of TextEditWindow.onCut


    def onPaste( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onPaste()") )
        try:
            text = self.selection_get( SELection='CLIPBOARD')
        except TclError:
            showerror( APP_NAME, 'Nothing to paste')
            return
        self.textBox.insert( INSERT, text)          # add at current insert cursor
        self.textBox.tag_remove( SEL, START, END)
        self.textBox.tag_add( SEL, INSERT+'-%dc' % len(text), INSERT)
        self.textBox.see( INSERT )                   # select it, so it can be cut
    # end of TextEditWindow.onPaste


    def xxxonSelectAll( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onSelectAll()") )
        self.textBox.tag_add( SEL, START, END+'-1c' )   # select entire text
        self.textBox.mark_set( INSERT, START )          # move insert point to top
        self.textBox.see( INSERT )                      # scroll to top
    # end of TextEditWindow.onSelectAll


    ############################################################################
    # Search menu commands
    ############################################################################

    def xxxonGoto( self, forceline=None):
        line = forceline or askinteger( APP_NAME, 'Enter line number' )
        self.textBox.update()
        self.textBox.focus()
        if line is not None:
            maxindex = self.textBox.index( END+'-1c' )
            maxline  = int( maxindex.split('.')[0] )
            if line > 0 and line <= maxline:
                self.textBox.mark_set( INSERT, '{}.0'.format(line) ) # goto line
                self.textBox.tag_remove( SEL, START, END )          # delete selects
                self.textBox.tag_add( SEL, INSERT, 'insert + 1l' )  # select line
                self.textBox.see( INSERT )                          # scroll to line
            else:
                showerror( APP_NAME, 'No such line number' )
    # end of TextEditWindow.onGoto


    def xxxonFind( self, lastkey=None):
        key = lastkey or askstring( APP_NAME, 'Enter search string' )
        self.textBox.update()
        self.textBox.focus()
        self.lastfind = key
        if key:
            nocase = self.optionsDict['caseinsens']
            where = self.textBox.search( key, INSERT, END, nocase=nocase )
            if not where:                                          # don't wrap
                showerror( APP_NAME, 'String not found' )
            else:
                pastkey = where + '+%dc' % len(key)           # index past key
                self.textBox.tag_remove( SEL, START, END )         # remove any sel
                self.textBox.tag_add( SEL, where, pastkey )        # select key
                self.textBox.mark_set( INSERT, pastkey )           # for next find
                self.textBox.see( where )                          # scroll display
    # end of TextEditWindow.onFind


    def xxxonRefind( self ):
        self.onFind( self.lastfind)
    # end of TextEditWindow.onRefind


    def onChange( self ):
        """
        non-modal find/change dialog
        2.1: pass per-dialog inputs to callbacks, may be > 1 change dialog open
        """
        new = Toplevel( self )
        new.title( 'PyEdit - change')
        Label(new, text='Find text?', relief=RIDGE, width=15).grid(row=0, column=0)
        Label(new, text='Change to?', relief=RIDGE, width=15).grid(row=1, column=0)
        entry1 = Entry(new)
        entry2 = Entry(new)
        entry1.grid(row=0, column=1, sticky=EW)
        entry2.grid(row=1, column=1, sticky=EW)

        def onFind():                         # use my entry in enclosing scope
            self.onFind( entry1.get() )         # runs normal find dialog callback

        def onApply():
            self.onDoChange( entry1.get(), entry2.get() )

        Button( new, text='Find',  command=onFind ).grid(row=0, column=2, sticky=EW)
        Button( new, text='Apply', command=onApply).grid(row=1, column=2, sticky=EW)
        new.columnconfigure(1, weight=1)      # expandable entries
    # end of TextEditWindow.onChange


    def onDoChange( self, findtext, changeto):
        # on Apply in change dialog: change and refind
        if self.textBox.tag_ranges( SEL ):                      # must find first
            self.textBox.delete( SEL_FIRST, SEL_LAST)
            self.textBox.insert( INSERT, changeto)             # deletes if empty
            self.textBox.see( INSERT )
            self.onFind( findtext )                          # goto next appear
            self.textBox.update()                             # force refresh
    # end of TextEditWindow.onDoChange


    def xxxonInfo( SELf):
        """
        pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        text  = self.getAllText()
        bytes = len( text )             # words uses a simple guess:
        lines = len( text.split('\n') ) # any separated by whitespace
        words = len( text.split() )     # 3.x: bytes is really chars
        index = self.textBox.index( INSERT ) # str is unicode code points
        where = tuple( index.split('.') )
        showinfo( APP_NAME+' Information',
                 'Current location:\n\n' +
                 'line:\t%s\ncolumn:\t%s\n\n' % where +
                 'File text statistics:\n\n' +
                 'chars:\t{}\nlines:\t{}\nwords:\t{}\n'.format( bytes, lines, words) )
    # end of TextEditWindow.onInfo


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    def xxxisEmpty( self ):
        return not self.getAllText()
    # end of TextEditWindow.modified

    def xxxxmodified( self ):
        return self.textBox.edit_modified()
    # end of TextEditWindow.modified

    def xxxgetAllText( self ):
        """ Returns all the text as a string. """
        return self.textBox.get( START, END+'-1c' )
    # end of TextEditWindow.modified

    def xxxsetAllText( self, newText ):
        """
        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        self.textBox.delete( START, END )
        self.textBox.insert( END, newText )
        self.textBox.mark_set( INSERT, START ) # move insert point to top
        self.textBox.see( INSERT ) # scroll to top, insert is set

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( FALSE ) # clear modified flag
    # end of TextEditWindow.setAllText

    def setFilepath( self, newFilepath ):
        self.folderPath, self.filename = os.path.split( newFilepath )
        #self.currfile = name  # for save
        #self.filelabel.config(text=str(name))
        self.refreshTitle()
    # end of TextEditWindow.setFilepath


    def onClose( self ):
        """
        Called if the user requests a close from the GUI.
        """
        self.onClose()
    # end of TextEditWindow.closeEditor

    def closeEditor( self ):
        """
        """
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.closeEditor()") )
        if self.textBox.edit_modified():
            pass
        else: self.closeResourceWindow()
    # end of TextEditWindow.closeEditor
# end of TextEditWindow class



class USFMEditWindow( TextEditWindow, BibleResourceWindow ):
    def __init__( self, parentApp, USFMBible ):
        if Globals.debugFlag and debuggingThisModule:
            print( "USFMEditWindow.__init__( {}, {} )".format( parentApp, USFMBible ) )
        self.parentApp, self.internalBible = parentApp, USFMBible
        self.USFMFolder = self.internalBible.sourceFolder

        # Set some dummy values required soon (esp. by refreshTitle)
        self.editMode = 'Default'
        BibleResourceWindow.__init__( self, parentApp, 'BibleEditor' )
        TextEditWindow.__init__( self, parentApp )
        # Now we need to override a few critical variables
        self.genericWindowType = 'BibleEditor'
        self.winType = 'USFMBibleEditWindow'

        if self.internalBible is not None:
            self.textBox['background'] = "white"
            self.textBox['selectbackground'] = "red"
            self.textBox['highlightbackground'] = "orange"
            self.textBox['inactiveselectbackground'] = "green"
        else: self.editMode = None

        self.lastBBB = None
    # end of USFMEditWindow.__init__


    def refreshTitle( self ):
        self.title( "{}[{}] {} {} {}:{} ({}) Editable {}".format( '*' if self.modified() else '',
                                    self.groupCode,
                                    self.internalBible.name if self.internalBible is not None else 'None',
                                    self.verseKey.getBBB(), self.verseKey.getChapterNumber(), self.verseKey.getVerseNumber(),
                                    self.editMode, self.contextViewMode ) )
    # end if USFMEditWindow.refreshTitle


    def xxnotWrittenYet( self ):
        showerror( _("Not implemented"), _("Not yet available, sorry") )
    # end of USFMEditWindow.notWrittenYet


    def xxdoHelp( self ):
        from Help import HelpBox
        hb = HelpBox( self.parentApp, ProgName, ProgNameVersion )
    # end of USFMEditWindow.doHelp


    def xxdoAbout( self ):
        from About import AboutBox
        ab = AboutBox( self.parentApp, ProgName, ProgNameVersion )
    # end of USFMEditWindow.doAbout


    def createMenuBar( self ):
        self.menubar = Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        fileMenu.add_command( label='Save', underline=0, command=self.notWrittenYet )
        fileMenu.add_command( label='Save as...', underline=5, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #subfileMenuImport = Menu( fileMenu )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #subfileMenuExport = Menu( fileMenu )
        #subfileMenuExport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label='HTML', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Export', underline=0, menu=subfileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label='Info...', underline=0, command=self.onInfo )
        fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.closeEditor )

        editMenu = Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        editMenu.add_command( label='Undo', underline=0, command=self.onUndo )
        editMenu.add_command( label='Redo', underline=0, command=self.onRedo )
        editMenu.add_separator()
        editMenu.add_command( label='Cut', underline=2, command=self.onCut )
        editMenu.add_command( label='Copy', underline=0, command=self.onCopy )
        editMenu.add_command( label='Paste', underline=0, command=self.onPaste )
        editMenu.add_separator()
        editMenu.add_command( label='Delete', underline=0, command=self.onDelete )
        editMenu.add_command( label='Select all', underline=0, command=self.onSelectAll )
        #editMenu.add_separator()
        #editMenu.add_command( label='Find...', underline=0, command=self.onFind )
        #editMenu.add_command( label='Replace...', underline=0, command=self.onReplace )

        searchMenu = Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label='Search', underline=0 )
        searchMenu.add_command( label='Goto line...', underline=0, command=self.onGoto )
        searchMenu.add_separator()
        searchMenu.add_command( label='Find...', underline=0, command=self.onFind )
        searchMenu.add_command( label='Find again', underline=5, command=self.onRefind )
        searchMenu.add_command( label='Replace...', underline=0, command=self.onChange )
        #searchMenu.add_separator()
        #searchMenu.add_command( label='Grep...', underline=0, command=self.onGrep )

        gotoMenu = Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        gotoMenu.add_command( label='Previous book', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Next book', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Previous chapter', underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label='Next chapter', underline=0, command=self.notWrittenYet )
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
        self._groupRadio.set( self.groupCode )
        gotoMenu.add_radiobutton( label='Group A', underline=6, value='A', variable=self._groupRadio, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group B', underline=6, value='B', variable=self._groupRadio, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group C', underline=6, value='C', variable=self._groupRadio, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group D', underline=6, value='D', variable=self._groupRadio, command=self.changeBibleGroupCode )

        viewMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label='View', underline=0 )
        if   self.contextViewMode == 'BeforeAndAfter': self._viewRadio.set( 1 )
        elif self.contextViewMode == 'ByVerse': self._viewRadio.set( 2 )
        elif self.contextViewMode == 'ByBook': self._viewRadio.set( 3 )
        elif self.contextViewMode == 'ByChapter': self._viewRadio.set( 4 )

        viewMenu.add_radiobutton( label='Before and after...', underline=7, value=1, variable=self._viewRadio, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label='Single verse', underline=7, value=2, variable=self._viewRadio, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label='Whole book', underline=6, value=3, variable=self._viewRadio, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label='Whole chapter', underline=6, value=4, variable=self._viewRadio, command=self.changeBibleContextView )

        toolsMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )

        helpMenu = Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label='Help', underline=0 )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout )

        #filename = filedialog.askopenfilename()
        #filename = filedialog.asksaveasfilename()
        #dirname = filedialog.askdirectory()
        #colorchooser.askcolor(initialcolor='#ff0000')
        #messagebox.showinfo(message='Have a good day')
        #messagebox.askyesno( message='Are you sure you want to install SuperVirus?' icon='question' title='Install' )
    # end of USFMEditWindow.createMenuBar


    def xxcreateContextMenu( self ):
        """
        """
        self.contextMenu = Menu( self, tearoff=0 )
        self.contextMenu.add_command( label="Cut", underline=2, command=self.notWrittenYet )
        self.contextMenu.add_command( label="Copy", underline=0, command=self.notWrittenYet )
        self.contextMenu.add_command( label="Paste", underline=0, command=self.notWrittenYet )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Close", underline=1, command=self.closeEditor )

        self.bind( "<Button-3>", self.showContextMenu ) # right-click
        #self.pack()
    # end of USFMEditWindow.createContextMenu


    #def showContextMenu( self, e):
        #self.contextMenu.post( e.x_root, e.y_root )
    ## end of USFMEditWindow.showContextMenu


    #def createToolBar( self ):
        #toolbar = Frame( self, cursor='hand2', relief=SUNKEN ) # bd=2
        #toolbar.pack( side=BOTTOM, fill=X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=LEFT )
    ## end of USFMEditWindow.createToolBar


    def getBookData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if Globals.debugFlag and debuggingThisModule:
            print( t("USFMEditWindow.getBookData( {} )").format( verseKey ) )
        BBB = verseKey.getBBB()
        if BBB != self.lastBBB: self.bookText = None
        if self.internalBible is not None:
            if self.bookText is None:
                self.lastBBB = BBB
                self.bookFilename = self.internalBible.possibleFilenameDict[BBB]
                self.bookFilepath = os.path.join( self.internalBible.sourceFolder, self.bookFilename )
                self.setFilepath( self.bookFilepath ) # For title displays, etc.
                #print( t('gVD'), BBB, repr(self.bookFilepath), repr(self.internalBible.encoding) )
                self.bookText = open( self.bookFilepath, 'rt', encoding=self.internalBible.encoding ).read()
                if self.bookText == None:
                    showerror( APP_NAME, 'Could not decode and open file ' + self.bookFilepath + ' with encoding ' + self.internalBible.encoding )
            return self.bookText
    # end of USFMEditWindow.getBookData


    def xxxdisplayAppendVerse( self, firstFlag, verseKey, verseDataList, currentVerse=False ):
        """
        Add the requested verse to the end of self.textBox.
        """
        if Globals.debugFlag and debuggingThisModule:
            try: print( t("USFMEditWindow.displayAppendVerse"), firstFlag, verseKey, verseDataList, currentVerse )
            except UnicodeEncodeError: print( t("USFMEditWindow.displayAppendVerse"), firstFlag, verseKey, currentVerse )
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
                    logging.critical( t("USFMEditWindow.displayAppendVerse: Unknown marker {} {} from {}").format( marker, cleanText, verseDataList ) )
    # end of USFMEditWindow.displayAppendVerse


    def xxxgetBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if Globals.debugFlag:
            print( t("USFMEditWindow.getBeforeAndAfterBibleData( {} )").format( newVerseKey ) )
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
                        logging.critical( t("getBeforeAndAfterBibleData failed at"), prevBBB, prevIntC )
                    failed = True
                if not failed:
                    if Globals.debugFlag: print( " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            else:
                prevBBB = self.parentApp.genericBibleOrganisationalSystem.getPreviousBookCode( BBB )
                prevIntC = self.getNumChapters( prevBBB )
                prevIntV = self.getNumVerses( prevBBB, prevIntC )
                if Globals.debugFlag: print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
            if not failed:
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getVerseData( previousVerseKey )
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
            nextVerseData = self.getVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        verseData = self.getVerseData( newVerseKey )

        return verseData, previousVersesData, nextVersesData
    # end of USFMEditWindow.getBeforeAndAfterBibleData


    def updateShownBCV( self, newVerseKey ):
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        Leaves the textbox in the disabled state.
        """
        if Globals.debugFlag and debuggingThisModule:
            print( "USFMEditWindow.updateShownBCV( {}) for".format( newVerseKey ), self.moduleID )
            #print( "contextViewMode", self.contextViewMode )
            assert( isinstance( newVerseKey, SimpleVerseKey ) )

        if newVerseKey.getBBB() != self.verseKey.getBBB(): # we've switched books
            if self.modified():
                self.showerror( APP_NAME, "Should save text here!" )
            self.clearText() # Leaves the text box enabled
            self.setAllText( self.getBookData( newVerseKey ) )

        if newVerseKey != self.verseKey: # we have a change of reference
            desiredMark = 'C{}V{}'.format( newVerseKey.getChapterNumber(), newVerseKey.getVerseNumber() )
            try: self.textBox.see( desiredMark )
            except TclError: print( t("USFMEditWindow.updateShownBCV couldn't find {}").format( repr( desiredMark ) ) )
            self.verseKey = newVerseKey

        self.refreshTitle()
    # end of USFMEditWindow.updateShownBCV


    def xxcloseEditor( self ):
        """
        """
        if Globals.debugFlag and debuggingThisModule:
            print( t("USFMEditWindow.closeEditor()") )
        if self.textBox.edit_modified():
            pass
        else: self.closeResourceWindow()
    # end of USFMEditWindow.closeEditor
# end of USFMEditWindow class



class ESFMEditWindow( USFMEditWindow ):
    pass
# end of ESFMEditWindow class



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
# end of EditWindows.demo


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
# end of EditWindows.py
