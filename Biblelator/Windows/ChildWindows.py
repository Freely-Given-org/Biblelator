#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ChildWindows.py
#
# Base of Bible and lexicon resource windows for Biblelator Bible display/editing
#
# Copyright (C) 2013-2018 Robert Hunt
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
Base windows to allow display and manipulation of
    various Bible and lexicon, etc. child windows.

    class ChildWindows( list ) -- used in Biblelator.py
        __init__( self, ChildWindowsParent )
        iconifyAll( self, childWindowType=None )
        #iconifyAllResources( self )
        deiconifyAll( self, childWindowType=None )
        saveAll( self )
        updateThisBibleGroup( self, groupCode, newVerseKey, originator=None )
        updateLexicons( self, newLexiconWord )

    class ChildWindow( tk.Toplevel, ChildBoxAddon ) -- used in BibleWindow, BibleResourceWindow, TextWindow, HTMLWindow
        __init__( self, parentApp, genericWindowType )
        geometry( self, *args, **kwargs )
        _createStandardWindowKeyboardBinding( self, name, command )
        createStandardWindowKeyboardBindings( self, reset=False )
        notWrittenYet( self )
        #createMenuBar( self )
        createContextMenu( self )
        showContextMenu( self, event )
        createToolBar( self )
        createStatusBar( self )
        doToggleStatusBar( self, setOn=None )
        setStatus( self, newStatusText='' )
        setErrorStatus( self, newStatusText )
        setWaitStatus( self, newStatusText )
        setReadyStatus( self )
        doShowMainWindow( self, event=None )
        #doHelp( self, event=None )
        #doAbout( self, event=None )
        doClose( self, event=None )

    class BibleWindowAddon( BibleBoxAddon ) -- used in BibleResourceCollectionWindow, SwordBibleResourceWindow, DBPBibleResourceWindow, InternalBibleResourceWindow
        __init__( self, parentApp, genericWindowType )
        createStandardWindowKeyboardBindings( self, reset=False )
        setContextViewMode( self, newMode )
        setFormatViewMode( self, newMode )
        setWindowGroup( self, newGroup )

    class TextWindow( ChildWindow ) -- used in HTMLWindow.doShowSource
        __init__( self, parentWindow, windowTitle=None, displayText=None, textSource=None )
        createMenuBar( self )
        createContextMenu( self )
        showContextMenu( self, event )
        createToolBar( self )
        createStatusBar( self )
        setStatus( self, newStatusText='' )
        #setWaitStatus( self, newStatusText )
        setReadyStatus( self )
        doShowInfo( self, event=None )
        doHelp( self, event=None )
        doAbout( self, event=None )
        doClose( self, event=None )

    class HTMLWindow( ChildWindow ) -- used in InternalBibleResourceWindowAddon.doCheckProject
        __init__( self, parentWindow, filepath=None )
        createMenuBar( self )
        createContextMenu( self )
        showContextMenu( self, event )
        createToolBar( self )
        createStatusBar( self )
        doToggleStatusBar( self, setOn=None )
        setStatus( self, newStatusText='' )
        #setWaitStatus( self, newStatusText )
        setReadyStatus( self )
        read( self )
        load( self, filepath )
        gotoLink( self, link )
        overLink( self, link )
        leaveLink( self )
        doGoForward( self )
        doGoBackward( self )
        doShowSource( self, event=None )
        doHelp( self, event=None )
        doAbout( self, event=None )
        doClose( self, event=None )

    class FindResultWindow( tk.Toplevel ) -- used in BibleBoxAddon.doActualBibleFind
        __init__( self, parentWindow, optionDict, resultSummaryDict, resultList, findFunction, refindFunction, replaceFunction, extendTo=None )
        notWrittenYet( self )
        createMenuBar( self )
        createContextMenu( self )
        showContextMenu( self, event )
        createToolBar( self )
        #createStatusBar( self )
        setStatus( self, newStatusText='' )
        #setWaitStatus( self, newStatusText )
        setReadyStatus( self )
        makeTreeView( self )
        itemSelected( self, event=None )
        doExtend( self, event=None )
        doActualExtend( self )
        doShowInfo( self, event=None )
        doHelp( self, event=None )
        doAbout( self, event=None )
        doClose( self, event=None )
        doRefresh( self )
        doRefind( self )
        doReplace( self )

    class CollateProjectsWindow( tk.Toplevel ) -- used in Biblelator.py
        __init__( self, parentWindow )
        #notWrittenYet( self )
        _createStandardWindowKeyboardBinding( self, name, command )
        createStandardWindowKeyboardBindings( self, reset=False )
        createMenuBar( self )
        createContextMenu( self )
        showContextMenu( self, event )
        createToolBar( self )
        createStatusBar( self )
        doToggleStatusBar( self, setOn=None )
        setStatus( self, newStatusText='' )
        #setWaitStatus( self, newStatusText )
        setReadyStatus( self )
        selectBible1( self, event=None )
        selectBible2( self, event=None )
        doNext( self, event=None )
        doPrevious( self, event=None )
        disableButtons( self )
        checkEnables( self, finalFlag=False )
        doGoCollate( self, event=None )
        doShowInfo( self, event=None )
        doHelp( self, event=None )
        doAbout( self, event=None )
        doClose( self, event=None )
        doRefresh( self )
        doRefind( self )

    demo()
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2018-03-15' # by RJH
SHORT_PROGRAM_NAME = "ChildWindows"
PROGRAM_NAME = "Biblelator Child Windows"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = True


import sys
import os.path
import logging
import re

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Style, Frame, Scrollbar, Label, Button, Treeview

# Biblelator imports
from Biblelator.BiblelatorGlobals import APP_NAME, DEFAULT, tkBREAK, \
                             BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, \
                             parseWindowGeometry, parseWindowSize, assembleWindowGeometry, errorBeep, \
                             INITIAL_RESOURCE_SIZE, MINIMUM_RESOURCE_SIZE, MAXIMUM_RESOURCE_SIZE, \
                             INITIAL_HTML_SIZE, MINIMUM_HTML_SIZE, MAXIMUM_HTML_SIZE, \
                             INITIAL_RESULT_WINDOW_SIZE, MINIMUM_RESULT_WINDOW_SIZE, MAXIMUM_RESULT_WINDOW_SIZE
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showInfo
from Biblelator.Dialogs.BiblelatorDialogs import SelectInternalBibleDialog
from Biblelator.Helpers.BiblelatorHelpers import mapReferenceVerseKey, mapParallelVerseKey #, mapReferencesVerseKey
from Biblelator.Windows.TextBoxes import BText, BCombobox, HTMLTextBox, ChildBoxAddon, BibleBoxAddon

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint




class ChildWindows( list ):
    """
    Just keeps a list of the toplevel child windows, e.g., resource windows.

    It can then apply various procedures to all the windows in the list.

    We expect to have only one instance of this class, from the main app.
    """
    def __init__( self, ChildWindowsParent ):
        self.ChildWindowsParent = ChildWindowsParent
        list.__init__( self )


    def iconifyAll( self, childWindowType=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "ChildWindows.iconifyAll( {} )".format( childWindowType ) )
        for appWin in self:
            if childWindowType is None or childWindowType in appWin.genericWindowType:
                appWin.iconify()
    #end of ChildWindows.iconifyAll


    #def iconifyAllResources( self ):
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "ChildWindows.iconifyAllResources()" )
        #for appWin in self:
            #if 'Resource' in appWin.genericWindowType:
                #appWin.iconify()
    ##end of ChildWindows.iconifyAllResources


    def deiconifyAll( self, childWindowType=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "ChildWindows.deiconifyAll( {} )".format( childWindowType ) )
        for appWin in self:
            if childWindowType is None or childWindowType in appWin.genericWindowType:
                appWin.deiconify()
                appWin.lift( aboveThis=self.ChildWindowsParent )
    #end of ChildWindows.deiconifyAll


    def saveAll( self ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "ChildWindows.saveAll()" )
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
            print( "ChildWindows.updateThisBibleGroup( {}, {}, {} )".format( groupCode, newVerseKey, originator ) )

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
            print( "ChildWindows.updateLexicons( {} )".format( newLexiconWord ) )

        for appWin in self:
            #print( "gwT", appWin.genericWindowType )
            if appWin.genericWindowType == 'LexiconResource':
                # The following line doesn't work coz it only updates ONE window
                #self.ChildWindowsParent.after_idle( lambda: appWin.updateLexiconWord( newLexiconWord ) )
                appWin.updateLexiconWord( newLexiconWord )
    # end of ChildWindows.updateLexicons
# end of ChildWindows class



class ChildWindow( tk.Toplevel, ChildBoxAddon ):
    """
    This is a base class for any toplevel window that contains a
        ChildBoxAddon, i.e., it contains a self.textBox member
        and has a menu, toolbar, and optional status bar.
    """
    def __init__( self, parentApp, genericWindowType ):
        """
        The genericWindowType is set here,
            but the more specific windowType is set later by the subclass.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildWindow.__init__( {} {!r} )").format( parentApp, genericWindowType ) )
            assert parentApp
            assert genericWindowType in ('BibleResource','LexiconResource','TextEditor','BibleEditor')
        self.parentApp, self.genericWindowType = parentApp, genericWindowType
        tk.Toplevel.__init__( self, self.parentApp )
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

        #self.createMenuBar() # requires self._groupRadioVar etc. for Bible windows
        self.createToolBar()
        #self.createContextMenu() # Don't do this by default (coz window may contain boxes which want context menus)

        #self._formatViewMode = DEFAULT
        self.settings = None

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        #if 'textBox' in self.__dict__: # we have one already -- presumably a specialised one
            #halt # We have one already
        #else: # let's make one

        self.textBox = BText( self, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        ChildBoxAddon.__init__( self, parentWindow=self )

        self.createStandardWindowKeyboardBindings()
        self.textBox.bind( '<Button-1>', self.setFocus ) # So disabled text box can still do select and copy functions

        # Options for find, etc.
        self.optionsDict = {}
        self.optionsDict['caseinsens'] = True

        self.parentApp.rootWindow.tk.call( 'wm', 'iconphoto', self._w, self.parentApp.iconImage )
        #self.refreshTitle() # Must be in superclass

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildWindow.__init__ finished.") )
    # end of ChildWindow.__init__


    def geometry( self, *args, **kwargs ):
        """
        Try to ensure that the Toplevel geometry function is easily accessed
            (and not the ChildBoxAddon function) in case this is causing us problems???

        Also found that we needed to call update first on Windows-10
            in order to set the window geometry correctly.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildWindow.geometry( {}, {} )").format( args, kwargs ) )

        if 'win' in sys.platform:  # Make sure that the window has finished being created (but unfortunately it briefly flashes up the empty window)
            self.update()
        return tk.Toplevel.geometry( self, *args, **kwargs )
    # end of ChildWindow.geometry


    def _createStandardWindowKeyboardBinding( self, name, command ):
        """
        Called from createStandardKeyboardBindings to do the actual work.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("ChildWindow._createStandardWindowKeyboardBinding( {} )").format( name ) )

        try: kBD = self.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentWindow.parentApp.keyBindingDict
        assert (name,kBD[name][0],) not in self.myKeyboardBindingsList
        if name in kBD:
            for keyCode in kBD[name][1:]:
                #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                self.bind( keyCode, command )
                if BibleOrgSysGlobals.debugFlag:
                    if keyCode in self.myKeyboardShortcutsList:
                        print( "ChildWindow._createStandardWindowKeyboardBinding wants to add duplicate {}".format( keyCode ) )
                    self.myKeyboardShortcutsList.append( keyCode )
            self.myKeyboardBindingsList.append( (name,kBD[name][0],) )
        else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of ChildWindow._createStandardWindowKeyboardBinding()

    def createStandardWindowKeyboardBindings( self, reset=False ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildWindow.createStandardWindowKeyboardBindings( {} )").format( reset ) )

        if reset:
            self.myKeyboardBindingsList = []

        for name,command in ( ('Info',self.doShowInfo),
                              ('Help',self.doHelp),
                              ('About',self.doAbout),
                              ('ShowMain',self.doShowMainWindow),
                              ('Close',self.doClose),
                              ):
            self._createStandardWindowKeyboardBinding( name, command )
    # end of ChildWindow.createStandardWindowKeyboardBindings()


    def notWrittenYet( self ):
        errorBeep()
        showError( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of ChildWindow.notWrittenYet


    #def createMenuBar( self ):
        #"""
        #Should never be called.
        #"""
        #logging.critical( _("PROGRAMMING ERROR: This 'createMenuBar' method MUST be overridden!") )
        #if BibleOrgSysGlobals.debugFlag:
            #print( _("This 'createMenuBar' method MUST be overridden!") )
            #halt
    ## end of ChildWindow.createMenuBar


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildWindow.createContextMenu()") )

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close window'), underline=1, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of ChildWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.tk_popup( event.x_root, event.y_root )
    # end of ChildWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("This 'createToolBar' method can be overridden!") )
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
            print( _("ChildWindow.createStatusBar()") )

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
            print( _("ChildWindow.doToggleStatusBar( {} ) from {}").format( setOn, self._showStatusBarVar.get() ) )

        # Make sure we don't create two status bars!!!
        currentState = self._showStatusBarVar.get()
        if setOn==True and currentState==True: return
        if setOn==False and currentState==False: return

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

        This works whether or not the status bar is displayed.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("setStatus( {!r} )").format( newStatusText ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( tkSTART, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( tkSTART, newStatusText )
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
            print( _("setErrorStatus( {!r} )").format( newStatusText ) )

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
            print( _("setWaitStatus( {!r} )").format( newStatusText ) )

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


    def doShowMainWindow( self, event=None ):
        """
        Display the main window (it might be minimised or covered).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildWindow.doShowMainWindow( {} )").format( event ) )

        #self.parentApp.rootWindow.iconify() # Didn't help
        self.parentApp.rootWindow.withdraw() # For some reason, doing this first makes the window always appear above others
        self.parentApp.rootWindow.update()
        self.parentApp.rootWindow.deiconify()
        #self.parentApp.rootWindow.focus_set()
        self.parentApp.rootWindow.lift() # aboveThis=self )
    # end of ChildWindow.doShowMainWindow


    #def doHelp( self, event=None ):
        #"""
        #Display a help box.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("SHOULD NEVER BE USED ChildWindow.doHelp( {} )").format( event ) )
        #from Help import HelpBox

        #helpInfo = programNameVersion
        #helpInfo += '\n' + _("Help for {}").format( self.windowType )
        #helpInfo += '\n  ' + _("Keyboard shortcuts:")
        #for name,shortcut in self.myKeyboardBindingsList:
            #helpInfo += "\n    {}\t{}".format( name, shortcut )
        #hb = HelpBox( self, self.genericWindowType, helpInfo )
        #return tkBREAK
    ## end of ChildWindow.doHelp


    #def doAbout( self, event=None ):
        #"""
        #Display an about box.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("SHOULD NEVER BE USED ChildWindow.doAbout( {} )").format( event ) )
        #from About import AboutBox

        #aboutInfo = programNameVersion
        #aboutInfo += "\nInformation about {}".format( self.windowType )
        #ab = AboutBox( self, self.genericWindowType, aboutInfo )
        #return tkBREAK
    ## end of ChildWindow.doAbout


    def doClose( self, event=None ):
        """
        Called to finally and irreversibly remove this window from our list and close it.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildWindow.doClose( {} ) for {}").format( event, self.genericWindowType ) )

        if self in self.parentApp.childWindows:
            self.parentApp.childWindows.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( _("ChildWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Closed child window" )
    # end of ChildWindow.doClose
# end of class ChildWindow



class BibleWindowAddon( BibleBoxAddon ):
    """
    This is a base class for any toplevel window that contains a
        BibleBoxAddon, i.e., it contains a self.textBox member that understands BCV references.
    """
    def __init__( self, genericWindowType ):
        """
        The genericWindowType is set here,
            but the more specific windowType is set later by the subclass.

        Default view modes should be set by the derived class before this is called.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleWindowAddon.__init__( {!r} )").format( genericWindowType ) )
            assert genericWindowType in ('BibleResourceWindow','LexiconResource','BibleEditor',
                                         'BibleResourceCollectionWindow','DBPBibleResourceWindow')
        self.genericWindowType = genericWindowType

        # The radio vars are used by the window menus
        self._contextViewRadioVar, self._formatViewRadioVar, self._groupRadioVar = tk.IntVar(), tk.IntVar(), tk.StringVar()
        self.setContextViewMode( DEFAULT )
        self.setFormatViewMode( DEFAULT )
        self.setWindowGroup( DEFAULT )

        BibleBoxAddon.__init__( self, parentWindow=self, BibleBoxType=genericWindowType )

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleWindowAddon.__init__ finished.") )
    # end of BibleWindowAddon.__init__


    def createStandardWindowKeyboardBindings( self, reset=False ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleWindowAddon.createStandardWindowKeyboardBindings( {} )").format( reset ) )

        if reset:
            self.myKeyboardBindingsList = []

        for name,command in ( ('Info',self.doShowInfo),
                              ('Help',self.doHelp),
                              ('About',self.doAbout),
                              ('ShowMain',self.doShowMainWindow),
                              ('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                              ('Find',self.doBibleFind), #('Refind',self.doBibleRefind),
                              ('Close',self.doClose),
                              ):
            self._createStandardWindowKeyboardBinding( name, command )
    # end of BibleWindowAddon.createStandardWindowKeyboardBindings()


    def setContextViewMode( self, newMode ):
        """
        Set the Bible context view mode for the window.

        Ideally we wouldn't need this info to be stored in both of these class variables.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleWindowAddon.setContextViewMode( {} ) for {}").format( newMode, self.genericWindowType ) )
            assert newMode==DEFAULT or newMode in BIBLE_CONTEXT_VIEW_MODES

        self._contextViewMode = self.defaultContextViewMode if newMode==DEFAULT else newMode
        self._contextViewRadioVar.set( BIBLE_CONTEXT_VIEW_MODES.index( self._contextViewMode ) + 1 )
    # end of BibleWindowAddon.setContextViewMode


    def setFormatViewMode( self, newMode ):
        """
        Set the Bible format view mode for the window.

        Ideally we wouldn't need this info to be stored in both of these class variables.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleWindowAddon.setFormatViewMode( {} ) for {}").format( newMode, self.genericWindowType ) )
            assert newMode==DEFAULT or newMode in BIBLE_FORMAT_VIEW_MODES

        self._formatViewMode = self.defaultFormatViewMode if newMode==DEFAULT else newMode
        #print( "Now set to", self._formatViewMode )
        self._formatViewRadioVar.set( BIBLE_FORMAT_VIEW_MODES.index( self._formatViewMode ) + 1 )
    # end of BibleWindowAddon.setFormatViewMode


    def setWindowGroup( self, newGroup ):
        """
        Set the Bible group for the window.

        Ideally we wouldn't need this info to be stored in both of these class variables.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleWindowAddon.setWindowGroup( {} ) for {}").format( newGroup, self.genericWindowType ) )
            assert newGroup==DEFAULT or newGroup in BIBLE_GROUP_CODES

        self._groupCode = BIBLE_GROUP_CODES[0] if newGroup==DEFAULT else newGroup
        self._groupRadioVar.set( BIBLE_GROUP_CODES.index( self._groupCode ) + 1 )
    # end of BibleWindowAddon.setWindowGroup
# end of class BibleWindowAddon



#class BibleWindow( ChildWindow, BibleBoxAddon ):
    #"""
    #This is a base class for any toplevel window that contains a
        #BibleBoxAddon, i.e., it contains a self.textBox member that understands BCV references.
    #"""
    #def __init__( self, parentApp, genericWindowType ):
        #"""
        #The genericWindowType is set here,
            #but the more specific windowType is set later by the subclass.

        #Default view modes should be set by the derived class before this is called.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("BibleWindow.__init__( {} {!r} )").format( parentApp, genericWindowType ) )
            #assert parentApp
            #assert genericWindowType in ('BibleResource','LexiconResource','BibleEditor',)
        #self.parentApp, self.genericWindowType = parentApp, genericWindowType

        ## The radio vars are used by the window menus
        #self._contextViewRadioVar, self._formatViewRadioVar, self._groupRadioVar = tk.IntVar(), tk.IntVar(), tk.StringVar()
        #self.setContextViewMode( DEFAULT )
        ##self.parentApp.viewVersesBefore, self.parentApp.viewVersesAfter = 2, 6
        #self.setFormatViewMode( DEFAULT )
        #self.setWindowGroup( DEFAULT )

        #ChildWindow.__init__( self, self.parentApp, self.genericWindowType )
        #BibleBoxAddon.__init__( self, self.parentWindow, genericWindowType )

        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("BibleWindow.__init__ finished.") )
    ## end of BibleWindow.__init__


    ##def createStandardWindowKeyboardBindings( self, reset=False ):
        ##"""
        ##Create keyboard bindings for this widget.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( _("BibleWindow.createStandardWindowKeyboardBindings( {} )").format( reset ) )

        ##if reset:
            ##self.myKeyboardBindingsList = []

        ##for name,command in ( ('Info',self.doShowInfo),
                              ##('Help',self.doHelp),
                              ##('About',self.doAbout),
                              ##('ShowMain',self.doShowMainWindow),
                              ##('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                              ##('Find',self.doBibleFind), #('Refind',self.doBibleRefind),
                              ##('Close',self.doClose),
                              ##):
            ##self._createStandardWindowKeyboardBinding( name, command )
    ### end of BibleWindow.createStandardWindowKeyboardBindings()


    ##def setContextViewMode( self, newMode ):
        ##"""
        ##Set the Bible context view mode for the window.

        ##Ideally we wouldn't need this info to be stored in both of these class variables.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( _("BibleWindow.setContextViewMode( {} ) for {}").format( newMode, self.genericWindowType ) )
            ##assert newMode==DEFAULT or newMode in BIBLE_CONTEXT_VIEW_MODES

        ##self._contextViewMode = self.defaultContextViewMode if newMode==DEFAULT else newMode
        ##self._contextViewRadioVar.set( BIBLE_CONTEXT_VIEW_MODES.index( self._contextViewMode ) + 1 )
    ### end of BibleWindow.setContextViewMode


    ##def setFormatViewMode( self, newMode ):
        ##"""
        ##Set the Bible format view mode for the window.

        ##Ideally we wouldn't need this info to be stored in both of these class variables.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( _("BibleWindow.setFormatViewMode( {} ) for {}").format( newMode, self.genericWindowType ) )
            ##assert newMode==DEFAULT or newMode in BIBLE_FORMAT_VIEW_MODES

        ##self._formatViewMode = self.defaultFormatViewMode if newMode==DEFAULT else newMode
        ###print( "Now set to", self._formatViewMode )
        ##self._formatViewRadioVar.set( BIBLE_FORMAT_VIEW_MODES.index( self._formatViewMode ) + 1 )
    ### end of BibleWindow.setFormatViewMode


    ##def setWindowGroup( self, newGroup ):
        ##"""
        ##Set the Bible group for the window.

        ##Ideally we wouldn't need this info to be stored in both of these class variables.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( _("BibleWindow.setWindowGroup( {} ) for {}").format( newGroup, self.genericWindowType ) )
            ##assert newGroup==DEFAULT or newGroup in BIBLE_GROUP_CODES

        ##self._groupCode = BIBLE_GROUP_CODES[0] if newGroup==DEFAULT else newGroup
        ##self._groupRadioVar.set( BIBLE_GROUP_CODES.index( self._groupCode ) + 1 )
    ### end of BibleWindow.setWindowGroup
## end of class BibleWindow



class TextWindow( ChildWindow ):
    """
    Displays fixed text.
    """
    def __init__( self, parentWindow, windowTitle=None, displayText=None, textSource=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.__init__( {}, {}, {} )").format( parentWindow, windowTitle, len(displayText) if displayText and len(displayText)>100 else displayText ) )
            assert parentWindow

        self.parentWindow, self.windowTitle, self.displayText, self.textSource = parentWindow, windowTitle, displayText, textSource
        self.parentApp = self.parentWindow.parentApp
        tk.Toplevel.__init__( self, self.parentWindow )
        self.protocol( 'WM_DELETE_WINDOW', self.doClose )
        self.title( self.windowTitle if self.windowTitle else 'HTMLSourceWindow' )
        self.genericWindowType = 'TextWindow'
        self.windowType = 'TextWindow'
        self.moduleID = 'Text'

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
        #self.settings = None

        buttonFrame = Frame( self ) #, cursor='hand2', relief=tk.RAISED, style='MainButtons.TFrame' )
        Button( buttonFrame, text=_("Close"), command=self.destroy ).pack( side=tk.RIGHT )
        buttonFrame.pack( side=tk.BOTTOM, fill=tk.X )

        self.textBox = ScrolledText( self, height=20, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( side=tk.TOP, fill=tk.BOTH, expand=tk.YES )
        xxxChildBoxAddon.__init__( self, parentWindow=self )

        if self.displayText:
            self.setAllText( self.displayText )
            self.textBox.configure( state=tk.DISABLED ) # Don't allow editing
    # end of TextWindow.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.createMenuBar()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_command( label=_('Save…'), underline=0, command=self.notWrittenYet )
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

        #editMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        #editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        #editMenu.add_separator()
        #editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )

        #searchMenu = tk.Menu( self.menubar )
        #self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        #searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=kBD[_('Line')][0] )
        #searchMenu.add_separator()
        #searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        #searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=kBD[_('Refind')][0] )

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
    # end of TextWindow.createMenuBar


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.createContextMenu()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=kBD[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of TextWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.tk_popup( event.x_root, event.y_root )
    # end of TextWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("This 'createToolBar' method can be overridden!") )
        pass
    # end of TextWindow.createToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.createStatusBar()") )

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
    # end of TextWindow.createStatusBar


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.setStatus( {} )").format( repr(newStatusText) ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( tkSTART, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( tkSTART, newStatusText )
            #self.statusBarTextWidget.configure( state=tk.DISABLED ) # Don't allow editing
            #self.statusText = newStatusText
            self._statusTextVar.set( newStatusText )
            if self._showStatusBarVar.get(): self.statusTextLabel.update()
    # end of TextWindow.setStatus


    #def setWaitStatus( self, newStatusText ):
        #"""
        #Set the status bar text and change the cursor to the wait/hourglass cursor.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("setWaitStatus( {} )").format( repr(newStatusText) ) )
        ##self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.setStatus( newStatusText )
        #self.update()
    ## end of TextWindow.setWaitStatus


    def setReadyStatus( self ):
        """
        Sets the status line to "Ready"
            and sets the cursor to the normal cursor.
        """
        self.setStatus( _("Ready") )
        #self.configure( cursor='' )
    # end of TextWindow.setReadyStatus


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'TextWindow doShowInfo' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("ChildBoxAddon.doShowInfo( {} )").format( event ) )

        text  = self.getAllText()
        numChars = len( text )
        numLines = len( text.split('\n') )
        numWords = len( text.split() )
        index = self.textBox.index( tk.INSERT )
        atLine, atColumn = index.split('.')
        infoString = 'Current source: {}\n\n'.format( self.textSource ) if self.textSource else ''
        infoString += 'Current location:\n' \
                 + '  Line:\t{}\n  Column:\t{}\n'.format( atLine, atColumn ) \
                 + '\nFile text statistics:\n' \
                 + '  Chars:\t{}\n  Lines:\t{}\n  Words:\t{}'.format( numChars, numLines, numWords )
        showInfo( self, 'Window Information', infoString )
    # end of TextWindow.doShowInfo


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += "\nHelp for {}".format( self.windowType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of TextWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of TextWindow.doAbout


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("TextWindow.doClose( {} )").format( event ) )

        try: cWs = self.parentWindow.parentApp.childWindows
        except AttributeError: cWs = self.parentApp.childWindows
        if self in cWs:
            cWs.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( _("TextWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentWindow.parentApp.setDebugText( "Closed HTML window" )
    # end of TextWindow.doClose
# end of class TextWindow



class HTMLWindow( ChildWindow ):
    """
    A window for displaying HTML files, e.g., USFM project checking results.
        This is effectively a primitive (very limited) browser.
    """
    def __init__( self, parentWindow, filepath=None ):
        """
        Set-up the window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.__init__( {}, {!r} )").format( parentWindow, filepath ) )
            assert parentWindow

        self.parentWindow, self.initialFilepath = parentWindow, filepath
        self.parentApp = self.parentWindow.parentApp
        tk.Toplevel.__init__( self, self.parentWindow )
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

        #if 'textBox' in self.__dict__: # we have one already -- presumably a specialised one
            #halt # We have one already
        #else: # let's make one

        self.textBox = HTMLTextBox( self, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        ChildBoxAddon.__init__( self, parentWindow=self )
        #self.createStandardWindowKeyboardBindings()
        #self.textBox.bind( '<Button-1>', self.setFocus ) # So disabled text box can still do select and copy functions

        # Options for find, etc.
        self.optionsDict = {}
        self.optionsDict['caseinsens'] = True

        if filepath:
            self.historyList = [ filepath ]
            self.historyIndex = 1 # Number from the end (starting with 1)
            self.load( filepath )
        else:
            self.historyList = []
            self.historyIndex = 0 # = None
    # end of HTMLWindow.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.createMenuBar()") )

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
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=kBD[_('Refind')][0] )

        viewMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label=_('View'), underline=0 )
        viewMenu.add_command( label=_('Source'), underline=2, command=self.doShowSource )
        viewMenu.add_separator()
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.createContextMenu()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=kBD[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of HTMLWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.tk_popup( event.x_root, event.y_root )
    # end of HTMLWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("This 'createToolBar' method can be overridden!") )
        pass
    # end of HTMLWindow.createToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.createStatusBar()") )

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
            print( _("HTMLWindow.doToggleStatusBar()") )

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
            print( _("HTMLWindow.setStatus( {} )").format( repr(newStatusText) ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( tkSTART, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( tkSTART, newStatusText )
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
            #print( _("setWaitStatus( {} )").format( repr(newStatusText) ) )
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


    def read( self ):
        """
        Reads the given HTML file and returns the contents.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.load() {} ").format( self.filepath ) )

        with open( self.filepath, 'rt', encoding='utf-8' ) as HTMLFile:
            return HTMLFile.read()
    # end of HTMLWindow.read


    def load( self, filepath ):
        """
        Loads the given HTML file into the window
            and also finds and sets the window title
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.load( {} )").format( filepath ) )

        self.filepath = filepath
        self.folderPath, self.filename = os.path.split( self.filepath )

        fileContents = self.read()
        match = re.search( '<title>(.+?)</title>', fileContents )
        if match:
            #print( '0', repr(match.group(0)) ) # This includes the entire match, i.e., with the <title> tags, etc.
            #print( '1', repr(match.group(1)) ) # This is just the title
            title = match.group(1).replace( '\n', ' ' ).replace( '\r', ' ' ).replace( '  ', ' ' )
            #print( 'title', repr(title) )
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
            print( _("HTMLWindow.gotoLink( {} )").format( link ) )

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
            print( _("HTMLWindow.overLink( {} )").format( link ) )

        self.setStatus( link ) # Display it
    # end of HTMLWindow.overLink


    def leaveLink( self ):
        """
        The user has moved the cursor away from the link.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.leaveLink()") )

        self.setStatus() # Clear it
    ## end of HTMLWindow.leaveLink


    def doGoForward( self ):
        """
        Go forward in HTML link history.
        """
        if self.historyIndex > 1:
            self.historyIndex -= 1
            self.load( self.historyList[ -self.historyIndex ] )
    # end of HTMLWindow.doGoForward


    def doGoBackward( self ):
        """
        Go backward in HTML link history.
        """
        if self.historyIndex < len( self.historyList ):
            self.historyIndex += 1
            self.load( self.historyList[ -self.historyIndex ] )
    # end of HTMLWindow.doGoBackward


    def doShowSource( self, event=None ):
        """
        Display the raw HTML source file in a separate window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.doShowSource( {} )").format( event ) )

        self.srcWindow = TextWindow( self, _("Source: {}").format( self.filename ), self.read(), self.filepath )
    # end of HTMLWindow.doShowSource


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of HTMLWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of HTMLWindow.doAbout


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("HTMLWindow.doClose( {} )").format( event ) )

        try: cWs = self.parentWindow.parentApp.childWindows
        except AttributeError: cWs = self.parentApp.childWindows
        if self in cWs:
            cWs.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( _("HTMLWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentWindow.parentApp.setDebugText( "Closed HTML window" )
    # end of HTMLWindow.doClose
# end of class HTMLWindow



class FindResultWindow( tk.Toplevel ):
    """
    Displays the find results.
    """
    def __init__( self, parentWindow, optionDict, resultSummaryDict, resultList, findFunction, refindFunction, replaceFunction, extendTo=None ):
        """
        optionDict is the dictionary of options that were given to the find function.
        resultSummaryDict is the dictionary containing summary entries (counts) for each Bible book.
            resultSummaryDict = { 'searchedBookList':[], 'foundBookList':[], }
        resultList is a list of 4-tuples or 5-tuples:
            For the normal search, the 4-tuples are:
                SimpleVerseKey, marker (none if v~), contextBefore, contextAfter
            If the search is caseless, the 5-tuples are:
                SimpleVerseKey, marker (none if v~), contextBefore, foundWordForm, contextAfter
        findFunction is the function that was called to create this window
            (which is used to refresh the window)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.__init__( {}, {}, {}, {} )").format( parentWindow, optionDict, resultSummaryDict, len(resultList) ) )
            assert parentWindow
            assert optionDict and isinstance( optionDict, dict )
            assert resultSummaryDict and isinstance( resultSummaryDict, dict )
            assert resultList and isinstance( resultList, list )

        self.parentWindow, self.optionDict, self.resultSummaryDict, self.resultList, self.findFunction, self.refindFunction, self.replaceFunction, self.extendedTo = \
            parentWindow, optionDict, resultSummaryDict, resultList, findFunction, refindFunction, replaceFunction, extendTo
        self.parentApp = self.parentWindow.parentApp
        tk.Toplevel.__init__( self, self.parentWindow )
        self.protocol( 'WM_DELETE_WINDOW', self.doClose )
        self.title( '{} Search Results'.format( self.optionDict['workName'] ) )
        self.genericWindowType = 'FindResultWindow'
        self.windowType = 'FindResultWindow'
        #self.moduleID = 'Find'

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

        # Make a frame at the top and then put our options inside it
        top = Frame( self )
        top.pack( side=tk.TOP, fill=tk.X )

        self.modeVar = tk.IntVar()
        self.modeVar.set( 0 ) # This sets the default 0:Line mode, 1:Column mode
        modeCb = tk.Checkbutton( self, text=_("Column mode"), variable=self.modeVar, command=self.makeTreeView )
        #modeCb.pack( in_=top, side=tk.LEFT )
        modeCb.grid( in_=top, row=0, column=0, padx=20, pady=5, sticky=tk.W )

        infoLabel = Label( self, text='( {:,} entries for {!r} )'.format( len(self.resultList), self.optionDict['findText'] ) )
        #infoLabel.pack( in_=top, side=tk.TOP, anchor=tk0.CENTER, padx=2, pady=2 )
        infoLabel.grid( in_=top, row=0, column=1, padx=2, pady=5 )

        if len(self.availableInternalBibles) == 1:
            extendText = _(" to {}").format( self.availableInternalBibles[0].getAName() )
        elif len(self.availableInternalBibles) > 1: extendText = '…'
        else: extendText = ''
        self.extendButton = Button( self, text=_('Extend')+"{}".format( extendText ), command=self.doExtend )
        #extendButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        self.extendButton.grid( in_=top, row=0, column=2, padx=5, pady=5, sticky=tk.W )
        if not self.availableInternalBibles: self.extendButton.configure( state=tk.DISABLED )

        refreshButton = Button( self, text=_('Refresh'), command=self.doRefresh )
        #refreshButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        refreshButton.grid( in_=top, row=1, column=0, padx=5, pady=5, sticky=tk.E )
        if self.refindFunction is None: refreshButton['state'] = tk.DISABLED

        reFindButton = Button( self, text=_('Find')+'…', command=self.doRefind )
        #reFindButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        reFindButton.grid( in_=top, row=1, column=1, padx=5, pady=5, sticky=tk.E )
        if self.findFunction is None: reFindButton['state'] = tk.DISABLED

        replaceButton = Button( self, text=_('Replace')+'…', command=self.doReplace )
        #replaceButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        replaceButton.grid( in_=top, row=1, column=2, padx=5, pady=5, sticky=tk.E )
        if self.replaceFunction is None: replaceButton['state'] = tk.DISABLED

        closeButton = Button( self, text=_('Close'), command=self.doClose )
        #closeButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        closeButton.grid( in_=top, row=1, column=3, padx=5, pady=5, sticky=tk.E )

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        if self.extendedTo: self.doActualExtend()
        else: self.makeTreeView()
    # end of FindResultWindow.__init__


    def notWrittenYet( self ):
        errorBeep()
        showError( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of FindResultWindow.notWrittenYet


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.createMenuBar()") )

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
        #searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        #searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=kBD[_('Refind')][0] )

        viewMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label=_('View'), underline=0 )
        viewMenu.add_command( label=_('Refresh'), underline=0, command=self.doRefresh ) #, accelerator=kBD[_('Refresh')][0] ) # refresh this window

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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.createContextMenu()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=kBD[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of FindResultWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.tk_popup( event.x_root, event.y_root )
    # end of FindResultWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("This 'createToolBar' method can be overridden!") )
        pass
    # end of FindResultWindow.createToolBar


    #def createStatusBar( self ):
        #"""
        #Create a status bar containing only one text label at the bottom of the main window.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("FindResultWindow.createStatusBar()") )

        #Style().configure('HTMLStatusBar.TFrame', background='yellow')
        #Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), background='white' )
        ##Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            ##background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        #self.statusBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='HTMLStatusBar.TFrame' )

        #self.statusTextLabel = Label( self.statusBar, relief=tk.SUNKEN,
                                    #textvariable=self._statusTextVar, style='{}.ChildStatusBar.TLabel'.format( self ) )
                                    ##, font=('arial',16,tk.NORMAL) )
        #self.statusTextLabel.pack( side=tk.LEFT, fill=tk.X )

        ## style='Halt.TButton',
        #self.forwardButton = Button( self.statusBar, text='Forward', command=self.doGoForward )
        #self.forwardButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        #self.backButton = Button( self.statusBar, text='Back', command=self.doGoBackward )
        #self.backButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        #self.statusBar.pack( side=tk.BOTTOM, fill=tk.X )

        ##self.setReadyStatus()
        #self.setStatus() # Clear it
    ## end of FindResultWindow.createStatusBar


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.setStatus( {} )").format( repr(newStatusText) ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( tkSTART, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( tkSTART, newStatusText )
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
            #print( _("setWaitStatus( {} )").format( repr(newStatusText) ) )
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


    def makeTreeView( self ):
        """
        Make the search result TreeView and fill it with our result list.

        First entry of self.result list is a dictionary containing the search parameters.

        Following entries are 4-tuples or 5-tuples:
            Verse reference (including an index within the verse)
            Marker
            Text before
            Actual text found (only if noCase was True)
            Text after
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( _("FindResultWindow.makeTreeView()") )
            assert self.resultList

        self.lineMode = not self.modeVar.get()

        try: self.findResultsTreeview.destroy(); del self.findResultsTreeview
        except AttributeError: pass # it may not have existed yet
        self.findResultsTreeview = Treeview( self, yscrollcommand=self.vScrollbar.set )
        self.findResultsTreeview.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.configure( command=self.findResultsTreeview.yview ) # link the scrollbar to the text box

        fText = self.optionDict['findText']
        lenFText = len( fText )
        contextLength = self.optionDict['contextLength']

        # Set-up the columns and column headings
        if self.extendedTo is None:
            self.findResultsTreeview['columns'] = ('ref','marker','fText') if self.lineMode else ('ref','marker','before','fText','after')
        else: # extended
            self.findResultsTreeview['columns'] = ('ref','marker','fText','extend') if self.lineMode else ('ref','marker','before','fText','after','extend')
        self.findResultsTreeview.column( '#0', width=50, stretch=False, anchor='w' )
        self.findResultsTreeview.heading( '#0', text=_("Bk") )
        self.findResultsTreeview.column( 'ref', width=75, stretch=False, anchor='w' )
        self.findResultsTreeview.heading( 'ref', text=_("Ref") )
        self.findResultsTreeview.column( 'marker', width=50, stretch=False, anchor='center' )
        self.findResultsTreeview.heading( 'marker', text=_("Mkr") )
        if self.lineMode:
            self.findResultsTreeview.column( 'fText', width=contextLength*8+lenFText*10+5, anchor='w' )
            self.findResultsTreeview.heading( 'fText', text=_("Found") )
        else: # column mode
            self.findResultsTreeview.column( 'before', width=contextLength*6, anchor='e' )
            self.findResultsTreeview.heading( 'before', text=_("Before") )
            self.findResultsTreeview.column( 'fText', width=lenFText*10+5, stretch=False, anchor='center' )
            cText = _("Found") if lenFText>=len( _("Found") ) else None # Leave off column heading for short fields
            self.findResultsTreeview.heading( 'fText', text=cText )
            self.findResultsTreeview.column( 'after', width=contextLength*6, anchor='w' )
            self.findResultsTreeview.heading( 'after', text=_("After") )
        if self.extendedTo is not None:
            self.findResultsTreeview.column( 'extend', width=contextLength*6, anchor='w' )
            extendName = self.extendedTo.abbreviation if self.extendedTo.abbreviation else self.extendedTo.name
            self.findResultsTreeview.heading( 'extend', text=extendName )

        lastBBB = None
        for j,resultEntry in enumerate(self.resultList):
            if len(resultEntry) == 5:
                ref,marker,before,fText,after = resultEntry
            elif len(resultEntry) == 4:
                ref,marker,before,after = resultEntry
            else: halt # programming error
            BBB,C,V = ref.getBCV()
            if BBB != lastBBB: # display a new book heading
                self.findResultsTreeview.insert( '', 'end', BBB, text=BBB, open=True)
                lastBBB = BBB
            # Now insert each reference under the BBB entry
            if self.extendedTo is None:
                if self.lineMode:
                    self.findResultsTreeview.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before+fText+after) )
                else: # column mode
                    self.findResultsTreeview.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before, fText, after) )
            else: # we have extended the results to display a second version
                try: extend = self.extendedTo.getVerseText( ref )
                except KeyError: extend = '' # couldn't find that CV reference
                if self.lineMode:
                    self.findResultsTreeview.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before+fText+after, extend) )
                else: # column mode
                    self.findResultsTreeview.insert( BBB, 'end', j, tags='BCV',
                        values=('{} {}:{}'.format(BBB,C,V), marker if marker else '', before, fText, after, extend) )

        self.findResultsTreeview.tag_bind( 'BCV', '<Double-Button-1>', self.itemSelected )
    # end of FindResultWindow.makeTreeView


    def itemSelected( self, event=None ):
        """
        They've double-clicked on a line in the search result window.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("itemSelected( {} )").format( event ) )
            #print( "ITEM SELECTED" )
            #print( dir(event) )
            #print( self.findResultsTreeview.focus() )

        j = self.findResultsTreeview.focus()
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
            print( _("doExtend( {} )").format( event ) )
            assert self.availableInternalBibles # Should be at least one

        if len(self.availableInternalBibles) == 1:
            self.extendedTo = self.availableInternalBibles[0]
        else: # Should let user choose an internal Bible
            sIBD = SelectInternalBibleDialog( self, _("Select EXTEND version"), self.availableInternalBibles )
            if sIBD.result is None: return # ESC pressed
            assert sIBD.result < len(self.availableInternalBibles)
            self.extendedTo = self.availableInternalBibles[sIBD.result]
        self.doActualExtend()
    # end of FindResultWindow.doExtend


    def doActualExtend( self ):
        """
        Extend the find box by adding another version already selected by the user.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("doActualExtend()") )

        self.parentApp.setWaitStatus( _("Extending find results…") )
        self.extendButton.configure( text=_("Extended"), state=tk.DISABLED )
        #print( "doExtend", self.geometry(), INITIAL_RESULT_WINDOW_SIZE )
        width, height, xOffset, yOffset = parseWindowGeometry( self.geometry() )
        self.geometry( assembleWindowGeometry( int(width*1.3), height, xOffset, yOffset ) ) # Make window widen
        self.makeTreeView() # Redisplay everything
        self.parentApp.setReadyStatus()
    # end of FindResultWindow.doActualExtend


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving find info
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'FindResultWindow doShowInfo' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.doShowInfo( {} )").format( event ) )

        #print( "options", self.optionDict )
        #print( "resultSummary", self.resultSummaryDict )
        #print( "resultList", self.resultList )

        # Display the options that were used for the search
        #   Doesn't yet display:
        #           'currentBCV'
        #            optionsDict['findHistoryList'] = [] # Oldest first
        #            optionsDict['contextLength'] = 30 # each side
        #            optionsDict['regexFlag'] = False
        #           'findHistoryList'

        infoString = 'Search text: {!r}\n'.format( self.optionDict['findText'] ) \
                 + 'In: {}\n'.format( self.optionDict['workName'] ) \
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
        showInfo( self, 'Window Information', infoString )
    # end of FindResultWindow.doShowInfo


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of FindResultWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of FindResultWindow.doAbout


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.doClose( {} )").format( event ) )

        try: cWs = self.parentWindow.parentApp.childWindows
        except AttributeError: cWs = self.parentApp.childWindows
        if self in cWs:
            cWs.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( _("FindResultWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentWindow.parentApp.setDebugText( "Closed HTML window" )
    # end of FindResultWindow.doClose


    def doRefresh( self ):
        """
        Refresh the find (without user input)
            by closing this window and then calling the find function again.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.doRefresh()") )

        self.doClose()
        self.refindFunction( extendTo=self.extendedTo ) # Run the find again (without user input)
    # end of FindResultWindow.doRefresh


    def doRefind( self ):
        """
        Refresh the find
            by closing this window and then calling the find function again.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.doRefind()") )

        self.doClose()
        self.findFunction() # Run the find again
    # end of FindResultWindow.doRefind


    def doReplace( self ):
        """
        Take the find into a find/replace
            by closing this window and then calling the supplied replace function.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("FindResultWindow.doReplace()") )

        self.doClose()
        self.replaceFunction() # Run the supplied find/replace function
    # end of FindResultWindow.doReplace
# end of class FindResultWindow



class CollateProjectsWindow( tk.Toplevel ):
    """
    Displays the find results.
    """
    def __init__( self, parentWindow ):
        """
        optionDict is the dictionary of options that were given to the find function.
        resultSummaryDict is the dictionary containing summary entries (counts) for each Bible book.
            resultSummaryDict = { 'searchedBookList':[], 'foundBookList':[], }
        resultList is a list of 4-tuples or 5-tuples:
            For the normal search, the 4-tuples are:
                SimpleVerseKey, marker (none if v~), contextBefore, contextAfter
            If the search is caseless, the 5-tuples are:
                SimpleVerseKey, marker (none if v~), contextBefore, foundWordForm, contextAfter
        findFunction is the function that was called to create this window
            (which is used to refresh the window)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.__init__( {}, {}, {}, {} )").format( parentWindow, optionDict, resultSummaryDict, len(resultList) ) )
            assert parentWindow
            assert optionDict and isinstance( optionDict, dict )
            assert resultSummaryDict and isinstance( resultSummaryDict, dict )
            assert resultList and isinstance( resultList, list )

        self.parentWindow = parentWindow
        self.parentApp = self.parentWindow.parentApp
        tk.Toplevel.__init__( self, self.parentWindow )
        self.protocol( 'WM_DELETE_WINDOW', self.doClose )
        self.title( _("Collate Projects") )
        self.genericWindowType = 'CollateProjectsWindow'
        self.windowType = 'CollateProjectsWindow'

        self.geometry( MAXIMUM_RESULT_WINDOW_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_RESULT_WINDOW_SIZE, MAXIMUM_RESULT_WINDOW_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        self._showStatusBarVar = tk.BooleanVar()
        self._showStatusBarVar.set( True )
        self._statusTextVar = tk.StringVar()
        self._statusTextVar.set( '' ) # first initial value

        self.myKeyboardBindingsList = []
        self.createMenuBar()
        #self.createToolBar()
        #self.createContextMenu()
        if self._showStatusBarVar.get(): self.createStatusBar()

        #self._formatViewMode = DEFAULT
        #self.settings = None

        ##print( 'All internalBibles', len(self.parentApp.internalBibles), self.parentApp.internalBibles )
        #self.availableInternalBibles = []
        #for internalBible,windowList in self.parentApp.internalBibles:
            #if internalBible is not self.parentWindow.internalBible:
                #self.availableInternalBibles.append( internalBible )
        ##print( 'Available internalBibles', len(self.availableInternalBibles), self.availableInternalBibles )

        self.BibleNameList = []
        self.BibleNameObjectDict = {}
        for iB,windowList in self.parentApp.internalBibles: # Contains 2-tuples being (internalBibleObject,list of window objects displaying that Bible)
            BibleName = iB.getAName()
            self.BibleNameList.append( BibleName )
            self.BibleNameObjectDict[BibleName] = iB
        self.internalBible1 = self.internalBible2 = None

        self.compareFunction = 'and'

        # Make a frame at the top and then put our options inside it
        top = Frame( self )
        top.pack( side=tk.TOP, fill=tk.X )

        self.thisBookOnlyVar = tk.BooleanVar()
        self.thisBookOnlyVar.set( False )
        self.BBB = self.parentApp.currentVerseKey.getBBB()
        thisBookCb = tk.Checkbutton( top, text=_("This book only ({})").format( self.BBB ),
                                    variable=self.thisBookOnlyVar )
        #thisBookCb.pack( side=tk.LEFT )
        thisBookCb.grid( row=0, column=0, padx=20, pady=5, sticky=tk.W )

        self.autoGotoVar = tk.BooleanVar()
        self.autoGotoVar.set( True )
        autoGotoCb = tk.Checkbutton( top, text=_("Auto Goto"), variable=self.autoGotoVar )
        #thisBookCb.pack( side=tk.LEFT )
        autoGotoCb.grid( row=0, column=1, padx=20, pady=5, sticky=tk.W )

        self.markersMatchVar = tk.BooleanVar()
        self.markersMatchVar.set( False )
        markersMatchCb = tk.Checkbutton( top, text=_("Format markers should match exactly (e.g., for a back-translation)"), variable=self.markersMatchVar )
        #thisBookCb.pack( side=tk.LEFT )
        markersMatchCb.grid( row=0, column=2, padx=20, pady=5, sticky=tk.W )

        #infoLabel = Label( self, text='( {:,} entries for {!r} )'.format( len(self.resultList), self.optionDict['findText'] ) )
        ##infoLabel.pack( in_=top, side=tk.TOP, anchor=tk0.CENTER, padx=2, pady=2 )
        #infoLabel.grid( in_=top, row=0, column=1, padx=2, pady=5 )

        #if len(self.availableInternalBibles) == 1:
            #extendText = _(" to {}").format( self.availableInternalBibles[0].getAName() )
        #elif len(self.availableInternalBibles) > 1: extendText = '…'
        #else: extendText = ''
        #self.extendButton = Button( self, text=_('Extend')+"{}".format( extendText ), command=self.doExtend )
        ##extendButton.pack( in_=top, side=tk.RIGHT, padx=2, pady=2 )
        #self.extendButton.grid( in_=top, row=0, column=2, padx=5, pady=5, sticky=tk.W )
        #if not self.availableInternalBibles: self.extendButton.configure( state=tk.DISABLED )


        bottom = Frame( self )
        bottom.pack( side=tk.BOTTOM, fill=tk.X )

        closeButton = Button( self, text=_('Close'), command=self.doClose )
        closeButton.pack( in_=bottom, side=tk.RIGHT, padx=2, pady=2 )
        #closeButton.grid( in_=bottom, row=1, column=3, padx=5, pady=5, sticky=tk.E )

        self.nextButton = Button( self, text=_('Next'), command=self.doNext )
        self.nextButton.pack( in_=bottom, side=tk.RIGHT, padx=2, pady=2 )
        #self.nextButton.grid( in_=bottom, row=1, column=0, padx=5, pady=5, sticky=tk.E )
        #self.nextButton.configure( state=tk.DISABLED )
        self.nextButton['state'] = tk.DISABLED

        self.previousButton = Button( self, text=_('Previous'), command=self.doPrevious )
        self.previousButton.pack( in_=bottom, side=tk.RIGHT, padx=2, pady=2 )
        #self.previousButton.grid( in_=bottom, row=1, column=1, padx=5, pady=5, sticky=tk.E )
        #self.previousButton.configure( state=tk.DISABLED )
        self.previousButton['state'] = tk.DISABLED

        self.goButton = Button( self, text=_('Go')+'…', command=self.doGoCollate )
        self.goButton.pack( in_=bottom, side=tk.RIGHT, padx=2, pady=2 )
        #self.goButton.grid( in_=bottom, row=1, column=1, padx=5, pady=5, sticky=tk.E )
        #self.goButton.configure( state=tk.DISABLED )
        self.goButton['state'] = tk.DISABLED


        left = Frame( self )
        left.pack( side=tk.LEFT, fill=tk.Y ) #, expand=tk.YES )

        self.version1Var = tk.StringVar()
        self.version1Var.set( _("(select)") )
        self.version1Box = BCombobox( left, width=40, textvariable=self.version1Var, values=self.BibleNameList )
        self.version1Box.bind('<<ComboboxSelected>>', self.selectBible1 )
        self.version1Box.bind( '<Return>', self.selectBible1 )
        #self.version1Box.bind( '<FocusIn>', self.notWrittenYet )
        self.version1Box.pack( side=tk.TOP )
        #self.version1Box.grid( row=0, column=0, columnspan=2, padx=2, pady=2, sticky=tk.W )

        self.optionsDict1 = {}
        self.optionsDict1['parentWindow'] = parentWindow
        #self.optionsDict1['parentBox'] = parentWindow.textBox
        self.optionsDict1['parentApp'] = self.parentApp
        #self.optionsDict1['givenBible'] = givenBible

        # Set-up default search options
        #self.optionsDict1['workName'] = givenBible.getAName() # Always revert to the original work
        if 'findHistoryList' not in self.optionsDict1: self.optionsDict1['findHistoryList'] = [] # Oldest first
        if 'wordMode' not in self.optionsDict1: self.optionsDict1['wordMode'] = 'Any' # or 'Whole' or 'Begins' or 'EndsWord' or 'EndsLine'
        if 'caselessFlag' not in self.optionsDict1: self.optionsDict1['caselessFlag'] = True
        if 'ignoreDiacriticsFlag' not in self.optionsDict1: self.optionsDict1['ignoreDiacriticsFlag'] = False
        if 'includeIntroFlag' not in self.optionsDict1: self.optionsDict1['includeIntroFlag'] = True
        if 'includeMainTextFlag' not in self.optionsDict1: self.optionsDict1['includeMainTextFlag'] = True
        if 'includeMarkerTextFlag' not in self.optionsDict1: self.optionsDict1['includeMarkerTextFlag'] = False
        if 'includeExtrasFlag' not in self.optionsDict1: self.optionsDict1['includeExtrasFlag'] = False
        if 'contextLength' not in self.optionsDict1: self.optionsDict1['contextLength'] = 30 # each side
        if 'bookList' not in self.optionsDict1: self.optionsDict1['bookList'] = 'ALL' # or BBB or a list
        if 'chapterList' not in self.optionsDict1: self.optionsDict1['chapterList'] = None
        if 'markerList' not in self.optionsDict1: self.optionsDict1['markerList'] = None
        self.optionsDict1['regexFlag'] = False

        self.findLabel1 = Label( left, text=_("Find:") )
        #self.findLabel1.grid( row=1, column=0, padx=2, pady=5, sticky=tk.E )
        self.findLabel1.pack( side=tk.TOP )
        self.searchString1Var = tk.StringVar()
        try: self.searchString1Var.set( self.optionsDict1['findHistoryList'][-1] )
        except IndexError: pass
        self.searchString1Box = BCombobox( left, width=35, textvariable=self.searchString1Var )
        self.searchString1Box['values'] = self.optionsDict1['findHistoryList']
        #self.searchString1Box['width'] = len( 'Deuteronomy' )
        self.searchString1Box.bind('<<ComboboxSelected>>', self.checkEnables )
        self.searchString1Box.bind( '<Return>', self.checkEnables )
        #self.searchString1Box.setTextChangeCallback( self.checkEnables )
        #self.searchString1Box.pack( side=tk.LEFT )
        #self.searchString1Box.grid( row=1, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )
        self.searchString1Box.pack( side=tk.TOP )
        self.searchString1Box.icursor( tk.END ) # Set cursor to end (makes spaces visible)

        #wordLimitsFrame = tk.LabelFrame( left, text=_('Word limits'), padx=5, pady=5 )
        #wordLimitsFrame.grid( row=2, column=0, padx=10, pady=10, sticky=tk.W )

        #self.wordModeSelectVariable = tk.IntVar()
        #if self.optionsDict['wordMode'] == 'Any': self.wordModeSelectVariable.set( 1 )
        #elif self.optionsDict['wordMode'] == 'Whole': self.wordModeSelectVariable.set( 2 )
        #elif self.optionsDict['wordMode'] == 'Begins': self.wordModeSelectVariable.set( 3 )
        #elif self.optionsDict['wordMode'] == 'EndsWord': self.wordModeSelectVariable.set( 4 )
        #elif self.optionsDict['wordMode'] == 'EndsLine': self.wordModeSelectVariable.set( 5 )
        #else: halt # programming error

        #self.rwmb1 = Radiobutton( left, text=_('No restriction'), variable=self.wordModeSelectVariable, value=1 )
        #self.rwmb1.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        ##self.rwmb1.grid( row=2, column=0, padx=2, pady=1, sticky=tk.W )
        #self.rwmb2 = Radiobutton( left, text=_('Whole words only'), variable=self.wordModeSelectVariable, value=2 )
        #self.rwmb2.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        ##self.rwmb2.grid( row=3, column=0, padx=2, pady=1, sticky=tk.W )
        #self.rwmb3 = Radiobutton( left, text=_('Beginning of word'), variable=self.wordModeSelectVariable, value=3 )
        #self.rwmb3.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        ##self.rwmb3.grid( row=4, column=0, padx=2, pady=1, sticky=tk.W )
        #self.rwmb4 = Radiobutton( left, text=_('End of word'), variable=self.wordModeSelectVariable, value=4 )
        #self.rwmb4.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        ##self.rwmb4.grid( row=5, column=0, padx=2, pady=1, sticky=tk.W )
        #self.rwmb5 = Radiobutton( left, text=_('End of line'), variable=self.wordModeSelectVariable, value=5 )
        #self.rwmb5.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )

        #self.mcaseVar = tk.IntVar()
        #if not self.optionsDict['caselessFlag']: self.mcaseVar.set( 1 )
        #mcaseCb = tk.Checkbutton( left, text=_("Match case"), variable=self.mcaseVar )
        ##mcaseCb.grid( row=6, column=0, padx=0, pady=5, sticky=tk.W )
        #mcaseCb.pack( in_=wordLimitsFrame, side=tk.TOP, anchor=tk.W, padx=0, pady=1 )
        #self.diaVar = tk.IntVar()
        #if self.optionsDict['ignoreDiacriticsFlag']: self.diaVar.set( 1 )
        #diaCb = tk.Checkbutton( left, text=_("Ignore diacritics"), variable=self.diaVar )
        ##diaCb.grid( row=6, column=2, padx=0, pady=5, sticky=tk.W )
        #diaCb.pack( in_=wordLimitsFrame, side=tk.TOP, anchor=tk.W, padx=0, pady=1 )

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar1 = Scrollbar( left )
        self.vScrollbar1.pack( side=tk.RIGHT, fill=tk.Y )

        self.textBox1 = BText( left, yscrollcommand=self.vScrollbar1.set, state=tk.DISABLED )
        self.textBox1.configure( wrap='word' )
        self.textBox1.pack( side=tk.TOP, fill=tk.BOTH ) #, expand=tk.YES )
        #self.textBox1.grid( row=2, column=0, columnspan=2, padx=2, pady=2, sticky=tk.W )
        self.vScrollbar1.configure( command=self.textBox1.yview ) # link the scrollbar to the text box

        right = Frame( self )
        right.pack( side=tk.RIGHT, fill=tk.Y ) #, expand=True )

        self.version2Var = tk.StringVar()
        self.version2Var.set( _("(select)") )
        self.version2Box = BCombobox( right, width=40, textvariable=self.version2Var, values=self.BibleNameList )
        self.version2Box.bind('<<ComboboxSelected>>', self.selectBible2 )
        self.version2Box.bind( '<Return>', self.selectBible2 )
        #self.version2Box.bind( '<FocusIn>', self.notWrittenYet )
        self.version2Box.pack( side=tk.TOP )

        self.optionsDict2 = {}
        self.optionsDict2['parentWindow'] = parentWindow
        #self.optionsDict2['parentBox'] = parentWindow.textBox
        self.optionsDict2['parentApp'] = self.parentApp
        #self.optionsDict2['givenBible'] = givenBible

        # Set-up default search options
        #self.optionsDict2['workName'] = givenBible.getAName() # Always revert to the original work
        if 'findHistoryList' not in self.optionsDict2: self.optionsDict2['findHistoryList'] = [] # Oldest first
        if 'wordMode' not in self.optionsDict2: self.optionsDict2['wordMode'] = 'Any' # or 'Whole' or 'Begins' or 'EndsWord' or 'EndsLine'
        if 'caselessFlag' not in self.optionsDict2: self.optionsDict2['caselessFlag'] = True
        if 'ignoreDiacriticsFlag' not in self.optionsDict2: self.optionsDict2['ignoreDiacriticsFlag'] = False
        if 'includeIntroFlag' not in self.optionsDict2: self.optionsDict2['includeIntroFlag'] = True
        if 'includeMainTextFlag' not in self.optionsDict2: self.optionsDict2['includeMainTextFlag'] = True
        if 'includeMarkerTextFlag' not in self.optionsDict2: self.optionsDict2['includeMarkerTextFlag'] = False
        if 'includeExtrasFlag' not in self.optionsDict2: self.optionsDict2['includeExtrasFlag'] = False
        if 'contextLength' not in self.optionsDict2: self.optionsDict2['contextLength'] = 30 # each side
        if 'bookList' not in self.optionsDict2: self.optionsDict2['bookList'] = 'ALL' # or BBB or a list
        if 'chapterList' not in self.optionsDict2: self.optionsDict2['chapterList'] = None
        if 'markerList' not in self.optionsDict2: self.optionsDict2['markerList'] = None
        self.optionsDict2['regexFlag'] = False

        self.findLabel2 = Label( right, text=_("Find:") )
        #self.findLabel2.grid( row=2, column=0, padx=2, pady=5, sticky=tk.E )
        self.findLabel2.pack( side=tk.TOP )
        self.searchString2Var = tk.StringVar()
        try: self.searchString2Var.set( self.optionsDict2['findHistoryList'][-1] )
        except IndexError: pass
        self.searchString2Box = BCombobox( right, width=35, textvariable=self.searchString2Var )
        self.searchString2Box['values'] = self.optionsDict2['findHistoryList']
        #self.searchString2Box['width'] = len( 'Deuteronomy' )
        self.searchString2Box.bind('<<ComboboxSelected>>', self.checkEnables )
        self.searchString2Box.bind( '<Return>', self.checkEnables )
        #self.searchString2Box.setTextChangeCallback( self.checkEnables )
        #self.searchString2Box.pack( side=tk.LEFT )
        #self.searchString2Box.grid( row=2, column=2, columnspan=2, padx=2, pady=2, sticky=tk.W )
        self.searchString2Box.pack( side=tk.TOP )
        self.searchString2Box.icursor( tk.END ) # Set cursor to end (makes spaces visible)

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar2 = Scrollbar( right )
        self.vScrollbar2.pack( side=tk.RIGHT, fill=tk.Y )

        self.textBox2 = BText( right, yscrollcommand=self.vScrollbar2.set, state=tk.DISABLED )
        self.textBox2.configure( wrap='word' )
        self.textBox2.pack( side=tk.TOP, fill=tk.BOTH ) #, expand=tk.YES )
        #self.textBox2.grid( row=2, column=0, columnspan=2, padx=2, pady=2, sticky=tk.W )
        self.vScrollbar2.configure( command=self.textBox2.yview ) # link the scrollbar to the text box

        self.createStandardWindowKeyboardBindings()
    # end of CollateProjectsWindow.__init__


    def _createStandardWindowKeyboardBinding( self, name, command ):
        """
        Called from createStandardKeyboardBindings to do the actual work.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("CollateProjectsWindow._createStandardWindowKeyboardBinding( {} )").format( name ) )

        try: kBD = self.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentWindow.parentApp.keyBindingDict
        assert (name,kBD[name][0],) not in self.myKeyboardBindingsList
        if name in kBD:
            for keyCode in kBD[name][1:]:
                #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                self.bind( keyCode, command )
                if BibleOrgSysGlobals.debugFlag:
                    if keyCode in self.myKeyboardShortcutsList:
                        print( "CollateProjectsWindow._createStandardWindowKeyboardBinding wants to add duplicate {}".format( keyCode ) )
                    self.myKeyboardShortcutsList.append( keyCode )
            self.myKeyboardBindingsList.append( (name,kBD[name][0],) )
        else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of CollateProjectsWindow._createStandardWindowKeyboardBinding()

    def createStandardWindowKeyboardBindings( self, reset=False ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.createStandardWindowKeyboardBindings( {} )").format( reset ) )

        if reset:
            self.myKeyboardBindingsList = []

        for name,command in ( ('Info',self.doShowInfo),
                              ('Help',self.doHelp),
                              ('About',self.doAbout),
                              #('ShowMain',self.doShowMainWindow),
                              ('Close',self.doClose),
                              ):
            self._createStandardWindowKeyboardBinding( name, command )
    # end of CollateProjectsWindow.createStandardWindowKeyboardBindings()


    #def notWrittenYet( self, event=None ):
        #errorBeep()
        #showError( self, _("Not implemented"), _("Not yet available, sorry") )
    ## end of CollateProjectsWindow.notWrittenYet


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.createMenuBar()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_command( label=_('Save…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu )
        #subfileMenuImport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Import'), underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu )
        #subfileMenuExport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label=_('HTML'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Export'), underline=0, menu=subfileMenuExport )
        #fileMenu.add_separator()
        #fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=kBD[_('Info')][0] )
        #fileMenu.add_separator()
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
        #searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        #searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=kBD[_('Refind')][0] )

        viewMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label=_('View'), underline=0 )
        viewMenu.add_command( label=_('Refresh'), underline=0, command=self.doRefresh ) #, accelerator=kBD[_('Refresh')][0] ) # refresh this window
        viewMenu.add_separator()
        viewMenu.add_checkbutton( label=_('Status bar'), underline=0, variable=self._showStatusBarVar, command=self.doToggleStatusBar )

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
    # end of CollateProjectsWindow.createMenuBar


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.createContextMenu()") )

        try: kBD = self.parentWindow.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentApp.keyBindingDict

        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=kBD[_('Copy')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=kBD[_('SelectAll')][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=kBD[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doClose, accelerator=kBD[_('Close')][0] )

        self.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()
    # end of CollateProjectsWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.tk_popup( event.x_root, event.y_root )
    # end of CollateProjectsWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("This 'createToolBar' method can be overridden!") )
        pass
    # end of CollateProjectsWindow.createToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.createStatusBar()") )

        Style().configure('HTMLStatusBar.TFrame', background='yellow')
        Style().configure( '{}.ChildStatusBar.TLabel'.format( self ), background='white' )

        self.statusBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='HTMLStatusBar.TFrame' )

        self.statusTextLabel = Label( self.statusBar, relief=tk.SUNKEN,
                                    textvariable=self._statusTextVar, style='{}.ChildStatusBar.TLabel'.format( self ) )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.LEFT, fill=tk.X )

        #self.forwardButton = Button( self.statusBar, text='Forward', command=self.doGoForward )
        #self.forwardButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        #self.backButton = Button( self.statusBar, text='Back', command=self.doGoBackward )
        #self.backButton.pack( side=tk.RIGHT, padx=2, pady=2 )
        self.statusBar.pack( side=tk.BOTTOM, fill=tk.X )

        #self.setReadyStatus()
        self.setStatus() # Clear it
    # end of CollateProjectsWindow.createStatusBar


    def doToggleStatusBar( self, setOn=None ):
        """
        Display or hide the status bar.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doToggleStatusBar()") )

        if setOn is not None:
            self._showStatusBarVar.set( setOn )

        if self._showStatusBarVar.get():
            self.createStatusBar()
        else:
            self.statusBar.destroy()
    # end of CollateProjectsWindow.doToggleStatusBar


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.setStatus( {} )").format( repr(newStatusText) ) )

        #print( "SB is", repr( self._statusTextVar.get() ) )
        if newStatusText != self._statusTextVar.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( tkSTART, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( tkSTART, newStatusText )
            #self.statusBarTextWidget.configure( state=tk.DISABLED ) # Don't allow editing
            #self.statusText = newStatusText
            self._statusTextVar.set( newStatusText )
            if self._showStatusBarVar.get(): self.statusTextLabel.update()
    # end of CollateProjectsWindow.setStatus


    #def setWaitStatus( self, newStatusText ):
        #"""
        #Set the status bar text and change the cursor to the wait/hourglass cursor.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("setWaitStatus( {} )").format( repr(newStatusText) ) )
        ##self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.setStatus( newStatusText )
        #self.update()
    ## end of CollateProjectsWindow.setWaitStatus


    def setReadyStatus( self ):
        """
        Sets the status line to "Ready"
            and sets the cursor to the normal cursor.
        """
        self.setStatus( _("Ready") )
        #self.configure( cursor='' )
    # end of CollateProjectsWindow.setReadyStatus


    def selectBible1( self, event=None ):
        """
        Select left-hand Bible.

        NOTE: We don't check here yet if the two selected Bibles are the same.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.selectBible1( {} )").format( event ) )

        BibleName1 = self.version1Var.get()
        self.internalBible1 = self.BibleNameObjectDict[BibleName1]
        self.checkEnables()
    # end of CollateProjectsWindow.selectBible1

    def selectBible2( self, event=None ):
        """
        Select right-hand Bible.

        NOTE: We don't check here yet if the two selected Bibles are the same.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.selectBible2( {} )").format( event ) )

        BibleName2 = self.version2Var.get()
        self.internalBible2 = self.BibleNameObjectDict[BibleName2]
        self.checkEnables()
    # end of CollateProjectsWindow.selectBible1


    def doNext( self, event=None ):
        """
        Process Next button.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doNext( {} )").format( event ) )

    # end of CollateProjectsWindow.doNext

    def doPrevious( self, event=None ):
        """
        Process Next button.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doPrevious( {} )").format( event ) )

    # end of CollateProjectsWindow.doPrevious


    def disableButtons( self ):
        """
        Disable all buttons.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.disableButtons()") )

        self.goButton.configure( state=tk.DISABLED )
        self.previousButton.configure( state=tk.DISABLED )
        self.nextButton.configure( state=tk.DISABLED )
    # end of CollateProjectsWindow.disableButtons

    def checkEnables( self, finalFlag=False ):
        """
        Enable or disable buttons.
        Also updates the find text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.checkEnables()") )

        self.disableButtons() # by default

        # First do a few checks
        if self.internalBible1 is None:
            if finalFlag:
                errorBeep()
                showError( self, _("Collate Projects error"), _("No Bible selected on left") )
            return
        self.optionsDict1['givenBible'] = self.internalBible1
        self.optionsDict1['workName'] = self.internalBible1.getAName()
        if self.internalBible2 is None:
            if finalFlag:
                errorBeep()
                showError( self, _("Collate Projects error"), _("No Bible selected on right") )
            return
        self.optionsDict2['givenBible'] = self.internalBible2
        self.optionsDict2['workName'] = self.internalBible2.getAName()
        if self.internalBible1 == self.internalBible2: # should this be "is"?
            if finalFlag:
                errorBeep()
                showError( self, _("Collate Projects error"), _("Left and right have identical Bibles") )
            return
        self.optionsDict1['findText'] = self.searchString1Var.get()
        if not self.optionsDict1['findText']:
            if finalFlag:
                errorBeep()
                showError( self, _("Collate Projects error"), _("No search string selected on left") )
            return
        self.optionsDict2['findText'] = self.searchString2Var.get()
        if not self.optionsDict2['findText']:
            if finalFlag:
                errorBeep()
                showError( self, _("Collate Projects error"), _("No search string selected on right") )
            return
        self.goButton.configure( state=tk.NORMAL )
    # end of CollateProjectsWindow.checkEnables


    def doGoCollate( self, event=None ):
        """
        Process Go button.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doGoCollate( {} )").format( event ) )

        # Prepare the final parameters
        self.optionsDict1['bookList'] = self.BBB if self.thisBookOnlyVar.get() else 'ALL'
        self.optionsDict2['bookList'] = self.optionsDict1['bookList']

        # Prepare the appropriate internal Bibles
        self.parentApp.setWaitStatus( _("Preparing internal Bible1…") )
        if self.optionsDict1['bookList'] == 'ALL':
            self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible1…") )
            self.internalBible1.load()
        else:
            self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible1 book…") )
            self.internalBible1.loadBook( self.optionsDict1['bookList'] )
        self.parentApp.setWaitStatus( _("Preparing internal Bible2…") )
        if self.optionsDict2['bookList'] == 'ALL':
            self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible2…") )
            self.internalBible2.load()
        else:
            self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible2 book…") )
            self.internalBible2.loadBook( self.optionsDict2['bookList'] )

        # Do the finds
        self.optionsDict1, resultSummaryDict1, findResultList1 = self.optionsDict1['givenBible'].findText( self.optionsDict1 )
        print( "Got findResultList1", findResultList1 )
        if len(findResultList1) == 0: # nothing found
            errorBeep()
            key = self.optionsDict1['findText']
            showError( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:18]+'…') ) )
            self.disableButtons()
            return
        self.optionsDict2, resultSummaryDict2, findResultList2 = self.optionsDict2['givenBible'].findText( self.optionsDict2 )
        print( "Got findResultList2", findResultList2 )
        if len(findResultList2) == 0: # nothing found
            errorBeep()
            key = self.optionsDict2['findText']
            showError( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:28]+'…') ) )
            self.disableButtons()
            return
    # end of CollateProjectsWindow.doGoCollate


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving find info
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'CollateProjectsWindow doShowInfo' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doShowInfo( {} )").format( event ) )

        #print( "options", self.optionDict )
        #print( "resultSummary", self.resultSummaryDict )
        #print( "resultList", self.resultList )

        # Display the options that were used for the search
        #   Doesn't yet display:
        #           'currentBCV'
        #            optionsDict['findHistoryList'] = [] # Oldest first
        #            optionsDict['contextLength'] = 30 # each side
        #            optionsDict['regexFlag'] = False
        #           'findHistoryList'

        infoString = 'Search text: {!r}\n'.format( self.optionDict['findText'] ) \
                 + 'In: {}\n'.format( self.optionDict['workName'] ) \
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
        showInfo( self, 'Window Information', infoString )
    # end of CollateProjectsWindow.doShowInfo


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of CollateProjectsWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of CollateProjectsWindow.doAbout


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doClose( {} )").format( event ) )

        try: cWs = self.parentWindow.parentApp.childWindows
        except AttributeError: cWs = self.parentApp.childWindows
        if self in cWs:
            cWs.remove( self )
            self.destroy()
        else: # we might not have finished making our window yet
            if BibleOrgSysGlobals.debugFlag:
                print( _("CollateProjectsWindow.doClose() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentWindow.parentApp.setDebugText( "Closed HTML window" )
    # end of CollateProjectsWindow.doClose


    def doRefresh( self ):
        """
        Refresh the find (without user input)
            by closing this window and then calling the find function again.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doRefresh()") )

        self.doClose()
        self.refindFunction( extendTo=self.extendedTo ) # Run the find again (without user input)
    # end of CollateProjectsWindow.doRefresh


    def doRefind( self ):
        """
        Refresh the find
            by closing this window and then calling the find function again.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("CollateProjectsWindow.doRefind()") )

        self.doClose()
        self.findFunction() # Run the find again
    # end of CollateProjectsWindow.doRefind
# end of class CollateProjectsWindow



def demo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: print( _("Running demo…") )

    tkRootWindow = Tk()
    tkRootWindow.title( programNameVersion )
    #settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', PROGRAM_NAME )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of ChildWindows.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of ChildWindows.py
