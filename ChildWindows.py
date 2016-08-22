#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ChildWindows.py
#
# Base of Bible and lexicon resource windows for Biblelator Bible display/editing
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
Base windows to allow display and manipulation of
    various Bible and lexicon, etc. child windows.

    class ChildWindow
    class ChildWindows
    class HTMLWindow
    class FindResultWindow
"""

from gettext import gettext as _

LastModifiedDate = '2016-08-21' # by RJH
ShortProgName = "ChildWindows"
ProgName = "Biblelator Child Windows"
ProgVersion = '0.38'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import sys, os.path, logging, re

import tkinter as tk
from tkinter.simpledialog import askstring, askinteger
from tkinter.ttk import Style, Frame, Scrollbar, Label, Button, Treeview

# Biblelator imports
from BiblelatorGlobals import APP_NAME, DEFAULT, BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, \
                             parseWindowGeometry, parseWindowSize, assembleWindowGeometry, errorBeep, \
                             INITIAL_RESOURCE_SIZE, MINIMUM_RESOURCE_SIZE, MAXIMUM_RESOURCE_SIZE, \
                             INITIAL_HTML_SIZE, MINIMUM_HTML_SIZE, MAXIMUM_HTML_SIZE, \
                             INITIAL_RESULT_WINDOW_SIZE, MINIMUM_RESULT_WINDOW_SIZE, MAXIMUM_RESULT_WINDOW_SIZE
from BiblelatorDialogs import showerror, showinfo, SelectInternalBibleDialog
from BiblelatorHelpers import mapReferenceVerseKey, mapParallelVerseKey #, mapReferencesVerseKey
from TextBoxes import ChildBox, BibleBox, HTMLText

# BibleOrgSys imports
#if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals



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
    return '{}{}'.format( nameBit, errorBit )
# end of exp



class ChildWindow( tk.Toplevel, ChildBox ):
    """
    This is a base class for any toplevel window that contains a
        ChildBox, i.e., it contains a self.textBox memember.
    """
    def __init__( self, parentApp, genericWindowType ):
        """
        The genericWindowType is set here,
            but the more specific windowType is set later by the subclass.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.__init__( {} {} )").format( parentApp, repr(genericWindowType) ) )
            assert parentApp
            assert genericWindowType in ('BibleResource','LexiconResource','TextEditor','BibleEditor',)
        self.parentApp, self.genericWindowType = parentApp, genericWindowType
        tk.Toplevel.__init__( self, self.parentApp )
        ChildBox.__init__( self, self.parentApp )
        self.protocol( 'WM_DELETE_WINDOW', self.doClose )

        self.geometry( INITIAL_RESOURCE_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_RESOURCE_SIZE, MAXIMUM_RESOURCE_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        # Allow child windows to have an optional status bar
        self._showStatusBarVar = tk.BooleanVar()
        self._showStatusBarVar.set( False ) # defaults to off
        self._statusTextVar = tk.StringVar()
        self._statusTextVar.set( '' ) # first initial value
        # You have to create self.statusTextLabel in order to display the status somewhere

        self.createMenuBar()
        self.createToolBar()
        self.createContextMenu()

        #self._formatViewMode = DEFAULT
        self.settings = None

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        #if 'textBox' in dir(self): # we have one already -- presumably a specialised one
            #halt # We have one already
        #else: # let's make one

        self.textBox = tk.Text( self, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardKeyboardBindings()
        self.textBox.bind( '<Button-1>', self.setFocus ) # So disabled text box can still do select and copy functions

        # Options for find, etc.
        self.optionsDict = {}
        self.optionsDict['caseinsens'] = True

        self.parentApp.rootWindow.tk.call( 'wm', 'iconphoto', self._w, self.parentApp.iconImage )
        self.refreshTitle() # Must be in superclass

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.__init__ finished.") )
    # end of ChildWindow.__init__


    def geometry( self, *args, **kwargs ):
        """
        Try to ensure that the Toplevel geometry function is easily accessed
            (and not the ChildBox function) in case this is causing us problems???

        Also found that we needed to call update first on Windows-10
            in order to set the window geometry correctly.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.geometry( {}, {} )").format( args, kwargs ) )

        if 'win' in sys.platform:  # Make sure that the window has finished being created (but unfortunately it briefly flashes up the empty window)
            self.update()
        return tk.Toplevel.geometry( self, *args, **kwargs )
    # end of ChildWindow.geometry


    def notWrittenYet( self ):
        errorBeep()
        showerror( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of ChildWindow.notWrittenYet


    #def createMenuBar( self ):
        #"""
        #Should never be called.
        #"""
        #logging.critical( exp("PROGRAMMING ERROR: This 'createMenuBar' method MUST be overridden!") )
        #if BibleOrgSysGlobals.debugFlag:
            #print( exp("This 'createMenuBar' method MUST be overridden!") )
            #halt
    ## end of ChildWindow.createMenuBar


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of ChildWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.post( event.x_root, event.y_root )
    # end of ChildWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("This 'createToolBar' method can be overridden!") )
        pass
    # end of ChildWindow.createToolBar


    # NOTE: The child window may not even have a status bar, but we allow for it
    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.

        We use the window label to name the status bar style,
            so that each status bar style is unique for each different window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.createStatusBar()") )

        #Style().configure('ChildWindowStatusBar.TFrame', background='yellow')
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), background='purple' )
        #Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            #background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        #self.statusBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='ChildWindowStatusBar.TFrame' )

        self.textBox.pack_forget() # Make sure the status bar gets the priority at the bottom of the window
        self.vScrollbar.pack_forget()
        self.statusTextLabel = Label( self, relief=tk.SUNKEN,
                                    textvariable=self._statusTextVar, style='{}.ChildStatusBar.TLabel'.format( self ) )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.BOTTOM, fill=tk.X )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )
        self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )

        self.setStatus() # Clear it
        self.parentApp.setReadyStatus() # So it doesn't get left with an error message on it
    # end of ChildWindow.createStatusBar


    def doToggleStatusBar( self, setOn=None ):
        """
        Display or hide the status bar for the child window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.doToggleStatusBar()") )

        if setOn is not None:
            self._showStatusBarVar.set( setOn )

        if self._showStatusBarVar.get():
            self.createStatusBar()
        else:
            try: self.statusTextLabel.destroy()
            except AttributeError: pass # no such thing
    # end of ChildWindow.doToggleStatusBar


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setStatus( {!r} )").format( newStatusText ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( START, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( START, newStatusText )
            #self.statusBarTextWidget.configure( state=tk.DISABLED ) # Don't allow editing
            #self.statusText = newStatusText
            Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), foreground='white', background='purple' )
            self._statusTextVar.set( newStatusText )
            try: self.statusTextLabel.update()
            except AttributeError: pass # if there's no such thing as self.statusTextLabel (i.e., no status bar for this window)
    # end of ChildWindow.setStatus

    def setErrorStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setErrorStatus( {!r} )").format( newStatusText ) )

        #self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='ChildStatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), foreground='yellow', background='red' )
        self.update()
    # end of ChildWindow.setErrorStatus

    def setWaitStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setWaitStatus( {!r} )").format( newStatusText ) )

        self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='ChildStatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), foreground='black', background='DarkOrange1' )
        self.update()
    # end of ChildWindow.setWaitStatus

    def setReadyStatus( self ):
        """
        Sets the status line to blank
            and sets the cursor to the normal cursor
        unless we're still starting
            (this covers any slow start-up functions that don't yet set helpful statuses)
        """
        #self.statusTextLabel.configure( style='ChildStatusBar.TLabelReady' )
        self.setStatus( '' )
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), foreground='yellow', background='forest green' )
        self.configure( cursor='' )
    # end of ChildWindow.setReadyStatus


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.windowType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of ChildWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of ChildWindow.doAbout


    def doClose( self, event=None ):
        """
        Called to finally and irreversibly remove this window from our list and close it.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildWindow.doClose( {} ) for {}").format( event, self.genericWindowType ) )

        if self in self.parentApp.childWindows:
            self.parentApp.childWindows.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( exp("ChildWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Closed child window" )
    # end of ChildWindow.doClose
# end of class ChildWindow



class BibleWindow( ChildWindow, BibleBox ):
    """
    This is a base class for any toplevel window that contains a
        BibleBox, i.e., it contains a self.textBox member that understands BCV references.
    """
    def __init__( self, parentApp, genericWindowType ):
        """
        The genericWindowType is set here,
            but the more specific windowType is set later by the subclass.

        Default view modes should be set by the derived class before this is called.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleWindow.__init__( {} {!r} )").format( parentApp, genericWindowType ) )
            assert parentApp
            assert genericWindowType in ('BibleResource','LexiconResource','BibleEditor',)
        self.parentApp, self.genericWindowType = parentApp, genericWindowType

        # The radio vars are used by the window menus
        self._contextViewRadioVar, self._formatViewRadioVar, self._groupRadioVar = tk.IntVar(), tk.IntVar(), tk.StringVar()
        self.setContextViewMode( DEFAULT )
        #self.parentApp.viewVersesBefore, self.parentApp.viewVersesAfter = 2, 6
        self.setFormatViewMode( DEFAULT )
        self.setWindowGroup( DEFAULT )

        ChildWindow.__init__( self, self.parentApp, self.genericWindowType )
        BibleBox.__init__( self, self.parentApp )

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleWindow.__init__ finished.") )
    # end of BibleWindow.__init__


    def setContextViewMode( self, newMode ):
        """
        Set the Bible context view mode for the window.

        Ideally we wouldn't need this info to be stored in both of these class variables.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleWindow.setContextViewMode( {} ) for {}").format( newMode, self.genericWindowType ) )
            assert newMode==DEFAULT or newMode in BIBLE_CONTEXT_VIEW_MODES

        self._contextViewMode = self.defaultContextViewMode if newMode==DEFAULT else newMode
        self._contextViewRadioVar.set( BIBLE_CONTEXT_VIEW_MODES.index( self._contextViewMode ) + 1 )
    # end of BibleWindow.setContextViewMode


    def setFormatViewMode( self, newMode ):
        """
        Set the Bible format view mode for the window.

        Ideally we wouldn't need this info to be stored in both of these class variables.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleWindow.setFormatViewMode( {} ) for {}").format( newMode, self.genericWindowType ) )
            assert newMode==DEFAULT or newMode in BIBLE_FORMAT_VIEW_MODES

        self._formatViewMode = self.defaultFormatViewMode if newMode==DEFAULT else newMode
        #print( "Now set to", self._formatViewMode )
        self._formatViewRadioVar.set( BIBLE_FORMAT_VIEW_MODES.index( self._formatViewMode ) + 1 )
    # end of BibleWindow.setFormatViewMode


    def setWindowGroup( self, newGroup ):
        """
        Set the Bible group for the window.

        Ideally we wouldn't need this info to be stored in both of these class variables.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleWindow.setWindowGroup( {} ) for {}").format( newGroup, self.genericWindowType ) )
            assert newGroup==DEFAULT or newGroup in BIBLE_GROUP_CODES

        self._groupCode = BIBLE_GROUP_CODES[0] if newGroup==DEFAULT else newGroup
        self._groupRadioVar.set( BIBLE_GROUP_CODES.index( self._groupCode ) + 1 )
    # end of BibleWindow.setWindowGroup
# end of class BibleWindow



class ChildWindows( list ):
    """
    Just keeps a list of the toplevel child windows, e.g., Resource windows.
    """
    def __init__( self, ChildWindowsParent ):
        self.ChildWindowsParent = ChildWindowsParent
        list.__init__( self )


    def iconifyAll( self, childWindowType=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("ChildWindows.iconifyAll( {} )").format( childWindowType ) )
        for appWin in self:
            if childWindowType is None or childWindowType in appWin.genericWindowType:
                appWin.iconify()
    #end of ChildWindows.iconifyAll


    #def iconifyAllResources( self ):
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("ChildWindows.iconifyAllResources()") )
        #for appWin in self:
            #if 'Resource' in appWin.genericWindowType:
                #appWin.iconify()
    ##end of ChildWindows.iconifyAllResources


    def deiconifyAll( self, childWindowType=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("ChildWindows.deiconifyAll( {} )").format( childWindowType ) )
        for appWin in self:
            if childWindowType is None or childWindowType in appWin.genericWindowType:
                appWin.deiconify()
                appWin.lift( aboveThis=self.ChildWindowsParent )
    #end of ChildWindows.deiconifyAll


    def saveAll( self ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("ChildWindows.saveAll()") )
        for appWin in self:
            if 'Edit' in appWin.genericWindowType:
                appWin.doSave()
    #end of ChildWindows.saveAll


    def updateThisBibleGroup( self, groupCode, newVerseKey, originator=None ):
        """
        Called when we probably need to update some resource windows with a new Bible reference.

        Note that this new verse key is in the reference versification system.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("ChildWindows.updateThisBibleGroup( {}, {}, {} )").format( groupCode, newVerseKey, originator ) )

        for appWin in self:
            if 'Bible' in appWin.genericWindowType: # e.g., BibleResource, BibleEditor
                if appWin.BCVUpdateType==DEFAULT and appWin._groupCode==groupCode:
                    # The following line doesn't work coz it only updates ONE window
                    #self.ChildWindowsParent.after_idle( lambda: appWin.updateShownBCV( newVerseKey ) )
                    appWin.updateShownBCV( newVerseKey, originator=originator )
                    #print( '  Normal', appWin._groupCode, newVerseKey, appWin.moduleID )
                elif groupCode == BIBLE_GROUP_CODES[0]:
                    if appWin.BCVUpdateType=='ReferenceMode' and appWin._groupCode==BIBLE_GROUP_CODES[1]:
                        appWin.updateShownBCV( mapReferenceVerseKey( newVerseKey ), originator=originator )
                        #print( '  Reference', appWin._groupCode, mapReferenceVerseKey( newVerseKey ), appWin.moduleID )
                    elif appWin.BCVUpdateType=='ParallelMode' and appWin._groupCode!=BIBLE_GROUP_CODES[0]:
                        appWin.updateShownBCV( mapParallelVerseKey( appWin._groupCode, newVerseKey ), originator=originator )
                        #print( '  Parallel', appWin._groupCode, mapParallelVerseKey( appWin._groupCode, newVerseKey ), appWin.moduleID )
                    #elif appWin.BCVUpdateType=='ReferencesMode':
                        #appWin.updateShownReferences( mapReferencesVerseKey( newVerseKey ) )
                        ##print( '  Parallel', appWin._groupCode, mapParallelVerseKey( appWin._groupCode, newVerseKey ), appWin.moduleID )
    # end of ChildWindows.updateThisBibleGroup


    def updateLexicons( self, newLexiconWord ):
        """
        Called when we probably need to update some resource windows with a new word.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("ChildWindows.updateLexicons( {} )").format( newLexiconWord ) )
        for appWin in self:
            #print( "gwT", appWin.genericWindowType )
            if appWin.genericWindowType == 'LexiconResource':
                # The following line doesn't work coz it only updates ONE window
                #self.ChildWindowsParent.after_idle( lambda: appWin.updateLexiconWord( newLexiconWord ) )
                appWin.updateLexiconWord( newLexiconWord )
    # end of ChildWindows.updateLexicons
# end of ChildWindows class



class HTMLWindow( tk.Toplevel, ChildBox ):
    """
    """
    def __init__( self, parentWindow, filename=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.__init__( {}, {} )").format( parentWindow, repr(filename) ) )
            assert parentWindow

        self.parentWindow, self.initialFilename = parentWindow, filename
        tk.Toplevel.__init__( self, self.parentWindow )
        ChildBox.__init__( self, self.parentWindow )
        self.protocol( 'WM_DELETE_WINDOW', self.doClose )
        self.title( 'HTMLWindow' )
        self.genericWindowType = 'HTMLWindow'
        self.windowType = 'HTMLWindow'
        self.moduleID = 'HTML'

        self.geometry( INITIAL_HTML_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_HTML_SIZE, MAXIMUM_HTML_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        self._showStatusBarVar = tk.BooleanVar()
        self._showStatusBarVar.set( True )
        self._statusTextVar = tk.StringVar()
        self._statusTextVar.set( '' ) # first initial value

        self.createMenuBar()
        self.createToolBar()
        self.createContextMenu()
        if self._showStatusBarVar.get(): self.createStatusBar()

        #self._formatViewMode = DEFAULT
        self.settings = None

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        #if 'textBox' in dir(self): # we have one already -- presumably a specialised one
            #halt # We have one already
        #else: # let's make one

        self.textBox = HTMLText( self, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardKeyboardBindings()
        #self.textBox.bind( '<Button-1>', self.setFocus ) # So disabled text box can still do select and copy functions

        # Options for find, etc.
        self.optionsDict = {}
        self.optionsDict['caseinsens'] = True

        if filename:
            self.historyList = [ filename ]
            self.historyIndex = 1 # Number from the end (starting with 1)
            self.load( filename )
        else:
            self.historyList = []
            self.historyIndex = 0 # = None
    # end of HTMLWindow.__init__


    def notWrittenYet( self ):
        errorBeep()
        showerror( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of HTMLWindow.notWrittenYet


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.createMenuBar()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

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
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=kBD[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=kBD[_('Close')][0] ) # close this window

        editMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=kBD[_('Line')][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=kBD[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doWindowRefind, accelerator=kBD[_('Refind')][0] )

        viewMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label=_('View'), underline=0 )
        viewMenu.add_checkbutton( label=_('Status bar'), underline=0, variable=self._showStatusBarVar, command=self.doToggleStatusBar )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
        gotoMenu.add_command( label=_('Back'), underline=0, command=self.doGoBackward )
        gotoMenu.add_command( label=_('Forward'), underline=0, command=self.doGoForward )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label=_('Tools'), underline=0 )
        toolsMenu.add_command( label=_('Options…'), underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label=_('Window'), underline=0 )
        windowMenu.add_command( label=_('Bring in'), underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=kBD[_('ShowMain')][0] )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label=_('Help') )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=kBD[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=kBD[_('About')][0] )
    # end of HTMLWindow.createMenuBar


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=kBD[_('Find')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=kBD[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of HTMLWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.post( event.x_root, event.y_root )
    # end of HTMLWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("This 'createToolBar' method can be overridden!") )
        pass
    # end of HTMLWindow.createToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.createStatusBar()") )

        Style().configure('HTMLStatusBar.TFrame', background='yellow')
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), background='white' )
        #Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            #background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        self.statusBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='HTMLStatusBar.TFrame' )

        self.statusTextLabel = Label( self.statusBar, relief=tk.SUNKEN,
                                    textvariable=self._statusTextVar, style='{}.ChildStatusBar.TLabel'.format( self ) )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.LEFT, fill=tk.X )

        # style='Halt.TButton',
        self.forwardButton = Button( self.statusBar, text='Forward', command=self.doGoForward )
        self.forwardButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        self.backButton = Button( self.statusBar, text='Back', command=self.doGoBackward )
        self.backButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        self.statusBar.pack( side=tk.BOTTOM, fill=tk.X )

        #self.setReadyStatus()
        self.setStatus() # Clear it
    # end of HTMLWindow.createStatusBar


    def doToggleStatusBar( self, setOn=None ):
        """
        Display or hide the status bar.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.doToggleStatusBar()") )

        if setOn is not None:
            self._showStatusBarVar.set( setOn )

        if self._showStatusBarVar.get():
            self.createStatusBar()
        else:
            self.statusBar.destroy()
    # end of HTMLWindow.doToggleStatusBar


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.setStatus( {} )").format( repr(newStatusText) ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( START, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( START, newStatusText )
            #self.statusBarTextWidget.configure( state=tk.DISABLED ) # Don't allow editing
            #self.statusText = newStatusText
            self._statusTextVar.set( newStatusText )
            if self._showStatusBarVar.get(): self.statusTextLabel.update()
    # end of HTMLWindow.setStatus


    #def setWaitStatus( self, newStatusText ):
        #"""
        #Set the status bar text and change the cursor to the wait/hourglass cursor.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("setWaitStatus( {} )").format( repr(newStatusText) ) )
        ##self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.setStatus( newStatusText )
        #self.update()
    ## end of HTMLWindow.setWaitStatus


    def setReadyStatus( self ):
        """
        Sets the status line to "Ready"
            and sets the cursor to the normal cursor.
        """
        self.setStatus( _("Ready") )
        #self.configure( cursor='' )
    # end of HTMLWindow.setReadyStatus


    def load( self, filepath ):
        """
        Loads the given HTML file into the window
            and also finds and sets the window title
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.load( {} )").format( filepath ) )

        self.folderPath, self.filename = os.path.split( filepath )
        with open( filepath, 'rt', encoding='utf-8' ) as HTMLFile:
            fileContents = HTMLFile.read()
        match = re.search( '<title>(.+?)</title>', fileContents )
        if match:
            #print( '0', repr(match.group(0)) ) # This includes the entire match, i.e., with the <title> tags, etc.
            #print( '1', repr(match.group(1)) ) # This is just the title
            title = match.group(1).replace( '\n', ' ' ).replace( '\r', ' ' ).replace( '  ', ' ' )
            #print( "title", repr(title) )
            self.title( title )
        else: self.title( 'HTMLWindow' )
        self.setAllText( fileContents )
    # end of HTMLWindow.load


    def gotoLink( self, link ):
        """
        Loads the given HTML file into the window
            and also finds and sets the window title
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.gotoLink( {} )").format( link ) )

        if not os.path.isabs( link ): # relative filepath
            link = os.path.join( self.folderPath, link )
        self.load( link )
        self.historyList.append( link )
        self.historyIndex = 1
    # end of HTMLWindow.gotoLink


    def overLink( self, link ):
        """
        The cursor is hovering over a link.

        Display the link address in the status bar.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.overLink( {} )").format( link ) )

        self.setStatus( link ) # Display it
    # end of HTMLWindow.overLink


    def leaveLink( self ):
        """
        The user has moved the cursor away from the link.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.leaveLink()") )

        self.setStatus() # Clear it
    # end of HTMLWindow.leaveLink


    def doGoForward( self ):
        """
        Go forward in HTML link history.
        """
        if self.historyIndex > 1:
            self.historyIndex -= 1
            self.load( self.historyList[ -self.historyIndex ] )
    # end of BibleResourceWindow.doGoForward


    def doGoBackward( self ):
        """
        Go backward in HTML link history.
        """
        if self.historyIndex < len( self.historyList ):
            self.historyIndex += 1
            self.load( self.historyList[ -self.historyIndex ] )
    # end of BibleResourceWindow.doGoBackward


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.windowType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of HTMLWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of HTMLWindow.doAbout


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLWindow.doClose( {} )").format( event ) )

        try: cWs = self.parentWindow.parentApp.childWindows
        except AttributeError: cWs = self.parentApp.childWindows
        if self in cWs:
            cWs.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( exp("HTMLWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentWindow.parentApp.setDebugText( "Closed HTML window" )
    # end of HTMLWindow.doClose
# end of class HTMLWindow



class FindResultWindow( tk.Toplevel, ChildBox ):
    """
    Displays the find results.
    """
    def __init__( self, parentWindow, optionDict, resultSummaryDict, resultList ):
        """
        optionDict is the dictionary of options that were given to the find function.
        resultSummaryDict is the dictionary containing summary entries (counts) for each Bible book.
            resultSummaryDict = { 'searchedBookList':[], 'foundBookList':[], }
        resultList is a list of 4-tuples or 5-tuples:
            For the normal search, the 4-tuples are:
                SimpleVerseKey, marker (none if v~), contextBefore, contextAfter
            If the search is caseless, the 5-tuples are:
                SimpleVerseKey, marker (none if v~), contextBefore, foundWordForm, contextAfter
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.__init__( {}, {}, {}, {} )").format( parentWindow, optionDict, resultSummaryDict, len(resultList) ) )
            assert parentWindow
            assert optionDict and isinstance( optionDict, dict )
            assert resultSummaryDict and isinstance( resultSummaryDict, dict )
            assert resultList and isinstance( resultList, list )

        self.parentWindow, self.optionDict, self.resultSummaryDict, self.resultList = parentWindow, optionDict, resultSummaryDict, resultList
        tk.Toplevel.__init__( self, self.parentWindow )
        ChildBox.__init__( self, self.parentWindow )
        self.protocol( 'WM_DELETE_WINDOW', self.doClose )
        self.parentApp = self.parentWindow.parentApp
        self.title( '{} Search Results'.format( self.optionDict['work'] ) )
        self.genericWindowType = 'FindResultWindow'
        self.windowType = 'FindResultWindow'
        self.moduleID = 'HTML'

        self.geometry( INITIAL_RESULT_WINDOW_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_RESULT_WINDOW_SIZE, MAXIMUM_RESULT_WINDOW_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        self._showStatusBarVar = tk.BooleanVar()
        self._showStatusBarVar.set( True )
        self._statusTextVar = tk.StringVar()
        self._statusTextVar.set( '' ) # first initial value

        self.createMenuBar()
        #self.createToolBar()
        #self.createContextMenu()
        #if self._showStatusBarVar.get(): self.createStatusBar()

        #self._formatViewMode = DEFAULT
        self.settings = None

        #print( 'All internalBibles', len(self.parentApp.internalBibles), self.parentApp.internalBibles )
        self.availableInternalBibles = []
        for internalBible,windowList in self.parentApp.internalBibles:
            if internalBible is not self.parentWindow.internalBible:
                self.availableInternalBibles.append( internalBible )
        #print( 'Available internalBibles', len(self.availableInternalBibles), self.availableInternalBibles )
        self.extendedTo = None

        # Make a frame at the top and then put our options inside it
        top = Frame( self )
        top.pack( side=tk.TOP, fill=tk.X )

        self.modeVar = tk.IntVar()
        self.modeVar.set( 0 ) # This sets the default 0:Line mode, 1:Column mode
        modeCb = tk.Checkbutton( self, text=_("Column mode"), variable=self.modeVar, command=self.makeTree )
        #modeCb.pack( in_=top, side=tk.LEFT )
        modeCb.grid( in_=top, row=0, column=0, padx=20, pady=5, sticky=tk.W )

        infoLabel = Label( self, text='( {:,} entries for {!r} )'.format( len(self.resultList), self.optionDict['searchText'] ) )
        #infoLabel.pack( in_=top, side=tk.TOP, anchor=tk0.CENTER, padx=2, pady=2 )
        infoLabel.grid( in_=top, row=0, column=1, padx=2, pady=5 )

        if len(self.availableInternalBibles) == 1:
            extendText = _(" to {}").format( self.availableInternalBibles[0].getAName() )
        elif len(self.availableInternalBibles) > 1: extendText = '…'
        else: extendText = ''
        self.extendButton = Button( self, text=_("Extend{}").format( extendText ), command=self.doExtend )
        #extendButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        self.extendButton.grid( in_=top, row=0, column=2, padx=5, pady=5, sticky=tk.W )
        if not self.availableInternalBibles: self.extendButton.configure( state=tk.DISABLED )

        closeButton = Button( self, text=_("Close"), command=self.doClose )
        #closeButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        closeButton.grid( in_=top, row=0, column=3, padx=5, pady=5, sticky=tk.E )

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        self.makeTree()
    # end of FindResultWindow.__init__


    def notWrittenYet( self ):
        errorBeep()
        showerror( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of FindResultWindow.notWrittenYet


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.createMenuBar()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        fileMenu.add_command( label=_('Save…'), underline=0, command=self.notWrittenYet )
        fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu )
        #subfileMenuImport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Import'), underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu )
        #subfileMenuExport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label=_('HTML'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Export'), underline=0, menu=subfileMenuExport )
        #fileMenu.add_separator()
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=kBD[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=kBD[_('Close')][0] ) # close this window

        #editMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        #editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        #editMenu.add_separator()
        #editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )

        #searchMenu = tk.Menu( self.menubar )
        #self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        #searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=kBD[_('Line')][0] )
        #searchMenu.add_separator()
        #searchMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=kBD[_('Find')][0] )
        #searchMenu.add_command( label=_('Find again'), underline=5, command=self.doWindowRefind, accelerator=kBD[_('Refind')][0] )

        #viewMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=viewMenu, label=_('View'), underline=0 )
        #viewMenu.add_checkbutton( label=_('Status bar'), underline=0, variable=self._showStatusBarVar, command=self.doToggleStatusBar )

        #gotoMenu = tk.Menu( self.menubar )
        #self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
        #gotoMenu.add_command( label=_('Back'), underline=0, command=self.doGoBackward )
        #gotoMenu.add_command( label=_('Forward'), underline=0, command=self.doGoForward )

        #toolsMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=toolsMenu, label=_('Tools'), underline=0 )
        #toolsMenu.add_command( label=_('Options…'), underline=0, command=self.notWrittenYet )

        #windowMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=windowMenu, label=_('Window'), underline=0 )
        #windowMenu.add_command( label=_('Bring in'), underline=0, command=self.notWrittenYet )
        #windowMenu.add_separator()
        #windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=kBD[_('ShowMain')][0] )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label=_('Help') )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=kBD[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=kBD[_('About')][0] )
    # end of FindResultWindow.createMenuBar


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=kBD[_('Find')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=kBD[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of FindResultWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.post( event.x_root, event.y_root )
    # end of FindResultWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("This 'createToolBar' method can be overridden!") )
        pass
    # end of FindResultWindow.createToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.createStatusBar()") )

        Style().configure('HTMLStatusBar.TFrame', background='yellow')
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), background='white' )
        #Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            #background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        self.statusBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='HTMLStatusBar.TFrame' )

        self.statusTextLabel = Label( self.statusBar, relief=tk.SUNKEN,
                                    textvariable=self._statusTextVar, style='{}.ChildStatusBar.TLabel'.format( self ) )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.LEFT, fill=tk.X )

        # style='Halt.TButton',
        self.forwardButton = Button( self.statusBar, text='Forward', command=self.doGoForward )
        self.forwardButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        self.backButton = Button( self.statusBar, text='Back', command=self.doGoBackward )
        self.backButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        self.statusBar.pack( side=tk.BOTTOM, fill=tk.X )

        #self.setReadyStatus()
        self.setStatus() # Clear it
    # end of FindResultWindow.createStatusBar


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.setStatus( {} )").format( repr(newStatusText) ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( START, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( START, newStatusText )
            #self.statusBarTextWidget.configure( state=tk.DISABLED ) # Don't allow editing
            #self.statusText = newStatusText
            self._statusTextVar.set( newStatusText )
            if self._showStatusBarVar.get(): self.statusTextLabel.update()
    # end of FindResultWindow.setStatus


    #def setWaitStatus( self, newStatusText ):
        #"""
        #Set the status bar text and change the cursor to the wait/hourglass cursor.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("setWaitStatus( {} )").format( repr(newStatusText) ) )
        ##self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.setStatus( newStatusText )
        #self.update()
    ## end of FindResultWindow.setWaitStatus


    def setReadyStatus( self ):
        """
        Sets the status line to "Ready"
            and sets the cursor to the normal cursor.
        """
        self.setStatus( _("Ready") )
        #self.configure( cursor='' )
    # end of FindResultWindow.setReadyStatus


    def makeTree( self ):
        """
        Make the tree and fill it with our result list.

        First entry of self.result list is a dictionary containing the search parameters.

        Following entries are 4-tuples or 5-tuples:
            Verse reference (including an index within the verse)
            Marker
            Text before
            Actual text found (only if noCase was True)
            Text after
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( exp("FindResultWindow.makeTree()") )
            assert self.resultList

        self.lineMode = not self.modeVar.get()

        try: self.tree.destroy(); del self.tree
        except AttributeError: pass # it may not have existed yet
        self.tree = Treeview( self, yscrollcommand=self.vScrollbar.set )
        self.tree.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.configure( command=self.tree.yview ) # link the scrollbar to the text box

        fText = self.optionDict['searchText']
        lenFText = len( fText )
        contextLength = self.optionDict['contextLength']

        if self.extendedTo is None:
            self.tree['columns'] = ('ref','marker','fText') if self.lineMode else ('ref','marker','before','fText','after')
        else: # extended
            self.tree['columns'] = ('ref','marker','fText','extend') if self.lineMode else ('ref','marker','before','fText','after','extend')
        self.tree.column( '#0', width=50, stretch=False, anchor='w' )
        self.tree.heading( '#0', text=_("Bk") )
        self.tree.column( 'ref', width=75, stretch=False, anchor='w' )
        self.tree.heading( 'ref', text=_("Ref") )
        self.tree.column( 'marker', width=50, stretch=False, anchor='center' )
        self.tree.heading( 'marker', text=_("Mkr") )
        if self.lineMode:
            self.tree.column( 'fText', width=contextLength*8+lenFText*10+5, anchor='w' )
            self.tree.heading( 'fText', text=_("Found") )
        else: # column mode
            self.tree.column( 'before', width=contextLength*6, anchor='e' )
            self.tree.heading( 'before', text=_("Before") )
            self.tree.column( 'fText', width=lenFText*10+5, stretch=False, anchor='center' )
            cText = _("Found") if lenFText>=len( _("Found") ) else None # Leave off column heading for short fields
            self.tree.heading( 'fText', text=cText )
            self.tree.column( 'after', width=contextLength*6, anchor='w' )
            self.tree.heading( 'after', text=_("After") )
        if self.extendedTo is not None:
            self.tree.column( 'extend', width=contextLength*6, anchor='w' )
            extendName = self.extendedTo.abbreviation if self.extendedTo.abbreviation else self.extendedTo.name
            self.tree.heading( 'extend', text=extendName )

        lastBBB = None
        for j,resultEntry in enumerate(self.resultList):
            if len(resultEntry) == 5:
                ref,marker,before,fText,after = resultEntry
            elif len(resultEntry) == 4:
                ref,marker,before,after = resultEntry
            else: halt # programming error
            BBB,C,V = ref.getBCV()
            if BBB != lastBBB:
                self.tree.insert( '', 'end', BBB, text=BBB, open=True)
                lastBBB = BBB
            if self.extendedTo is None:
                if self.lineMode:
                    self.tree.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before+fText+after) )
                else: # column mode
                    self.tree.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before, fText, after) )
            else: # we have extended the results to display a second version
                try: extend = self.extendedTo.getVerseText( ref )
                except KeyError: extend = '' # couldn't find that CV reference
                if self.lineMode:
                    self.tree.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before+fText+after, extend) )
                else: # column mode
                    self.tree.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before, fText, after, extend) )

        self.tree.tag_bind( 'BCV', '<Double-Button-1>', self.itemSelected )
    # end of FindResultWindow.makeTree


    def itemSelected( self, event=None ):
        """
        They've double-clicked on a line in the search result window.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("itemSelected( {} )").format( event ) )
            #print( "ITEM SELECTED" )
            #print( dir(event) )
            #print( self.tree.focus() )

        j = self.tree.focus()
        #print( "j", repr(j) )
        if j == 'I001': j=0 # Not sure why this is happening for the first entry???
        ref = self.resultList[int(j)][0] # Add one to skip past the optionDict which is the first results item
        BBB,C,V = ref.getBCV()
        #print( 'itemSelected', j, ref, BBB, C, V )
        self.parentApp.gotoBCV( BBB, C, V )
        # NOTE: Ideally we should select the actual text here also
    # end of FindResultWindow.itemSelected


    def doExtend( self, event=None ):
        """
        Extend the find box by adding another version
            (which the user might select if there's more than one available)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("doExtend( {} )").format( event ) )
            assert self.availableInternalBibles # Should be at least one

        if len(self.availableInternalBibles) == 1:
            self.extendedTo = self.availableInternalBibles[0]
        else: # Should let user choose an internal Bible
            sIBD = SelectInternalBibleDialog( self, _("Select EXTEND version"), self.availableInternalBibles )
            if sIBD.result is None: return # ESC pressed
            assert sIBD.result < len(self.availableInternalBibles)
            self.extendedTo = self.availableInternalBibles[sIBD.result]
        self.parentApp.setWaitStatus()
        self.extendButton.configure( text=_("Extended"), state=tk.DISABLED )
        #print( "doExtend", self.geometry(), INITIAL_RESULT_WINDOW_SIZE )
        width, height, xOffset, yOffset = parseWindowGeometry( self.geometry() )
        self.geometry( assembleWindowGeometry( int(width*1.3), height, xOffset, yOffset ) ) # Make window widen
        self.makeTree() # Redisplay everything
        self.parentApp.setReadyStatus()
    # end of FindResultWindow.doExtend


    #def load( self, filepath ):
        #"""
        #Loads the given HTML file into the window
            #and also finds and sets the window title
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("FindResultWindow.load( {} )").format( filepath ) )

        #self.folderPath, self.filename = os.path.split( filepath )
        #with open( filepath, 'rt', encoding='utf-8' ) as HTMLFile:
            #fileContents = HTMLFile.read()
        #match = re.search( '<title>(.+?)</title>', fileContents )
        #if match:
            ##print( '0', repr(match.group(0)) ) # This includes the entire match, i.e., with the <title> tags, etc.
            ##print( '1', repr(match.group(1)) ) # This is just the title
            #title = match.group(1).replace( '\n', ' ' ).replace( '\r', ' ' ).replace( '  ', ' ' )
            ##print( "title", repr(title) )
            #self.title( title )
        #else: self.title( 'FindResultWindow' )
        #self.setAllText( fileContents )
    ## end of FindResultWindow.load


    #def gotoLink( self, link ):
        #"""
        #Loads the given HTML file into the window
            #and also finds and sets the window title
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("FindResultWindow.gotoLink( {} )").format( link ) )

        #if not os.path.isabs( link ): # relative filepath
            #link = os.path.join( self.folderPath, link )
        #self.load( link )
        #self.historyList.append( link )
        #self.historyIndex = 1
    ## end of FindResultWindow.gotoLink


    #def overLink( self, link ):
        #"""
        #Loads the given HTML file into the window
            #and also finds and sets the window title
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("FindResultWindow.overLink( {} )").format( link ) )

        #self.setStatus( link ) # Display it
    ## end of FindResultWindow.overLink


    #def leaveLink( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("FindResultWindow.leaveLink()") )

        #self.setStatus() # Clear it
    ## end of FindResultWindow.leaveLink


    #def doGoForward( self ):
        #"""
        #"""
        #if self.historyIndex > 1:
            #self.historyIndex -= 1
            #self.load( self.historyList[ -self.historyIndex ] )
    ## end of BibleResourceWindow.doGoForward


    #def doGoBackward( self ):
        #"""
        #"""
        #if self.historyIndex < len( self.historyList ):
            #self.historyIndex += 1
            #self.load( self.historyList[ -self.historyIndex ] )
    ## end of BibleResourceWindow.doGoBackward


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving find info
        """
        from BiblelatorDialogs import showinfo
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'FindResultWindow doShowInfo' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.doShowInfo( {} )").format( event ) )

        #print( "options", self.optionDict )
        #print( "resultSummary", self.resultSummaryDict )
        #print( "resultList", self.resultList )

        # Display the options that were used for the search
        #   Doesn't yet display:
        #           'currentBCV'
        #            optionsDict['searchHistoryList'] = [] # Oldest first
        #            optionsDict['contextLength'] = 30 # each side
        #            optionsDict['regexFlag'] = False
        #           'searchHistoryList'

        infoString = 'Search text: {!r}\n'.format( self.optionDict['searchText'] ) \
                 + 'In: {}\n'.format( self.optionDict['work'] ) \
                 + 'Books: {}\n'.format( self.optionDict['bookList'] )
        if self.optionDict['chapterList']: infoString += 'chapters: {}\n'.format( self.optionDict['chapterList'] )
        if self.optionDict['markerList']: infoString += 'markers: {}\n'.format( self.optionDict['markerList'] )
        infoString += '\nOptions:\n' \
                 + '  Words: {}\n'.format( self.optionDict['wordMode'] ) \
                 + '  Caseless: {}\n'.format( self.optionDict['caselessFlag'] )
        if self.optionDict['markerList']: infoString += '  Ignore diacritics: {}\n'.format( self.optionDict['ignoreDiacriticsFlag'] )
        infoString += '\nInclude:\n' \
                 + '  Intro: {}\n'.format( self.optionDict['includeIntroFlag'] ) \
                 + '  Main text: {}\n'.format( self.optionDict['includeMainTextFlag'] ) \
                 + '  Marker text: {}\n'.format( self.optionDict['includeMarkerTextFlag'] ) \
                 + '  Notes: {}\n'.format( self.optionDict['includeExtrasFlag'] )

        if infoString[-1] == '\n': infoString = infoString[:-1] # Remove surplus newline marker
        showinfo( self, 'Window Information', infoString )
    # end of FindResultWindow.doShowInfo


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.windowType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of FindResultWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of FindResultWindow.doAbout


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("FindResultWindow.doClose( {} )").format( event ) )

        try: cWs = self.parentWindow.parentApp.childWindows
        except AttributeError: cWs = self.parentApp.childWindows
        if self in cWs:
            cWs.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( exp("FindResultWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentWindow.parentApp.setDebugText( "Closed HTML window" )
    # end of FindResultWindow.doClose
# end of class FindResultWindow



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
# end of ChildWindows.demo


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
# end of ChildWindows.py