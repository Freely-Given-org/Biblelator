#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BibleReferenceCollection.py
#
# Bible reference collection for Biblelator Bible display/editing
#
# Copyright (C) 2015-2018 Robert Hunt
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
Boxes, Frames, and Windows to allow display and manipulation of
    (non-editable) Bible reference collection windows.

A Bible reference collection is a collection of different Bible references
    all displaying from the same resource (or project).
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2018-12-12' # by RJH
SHORT_PROGRAM_NAME = "BibleReferenceCollection"
PROGRAM_NAME = "Biblelator Bible Reference Collection"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = True


import logging
from collections import OrderedDict

import tkinter as tk
from tkinter.ttk import Frame, Button, Scrollbar

# Biblelator imports
from Biblelator.BiblelatorGlobals import DEFAULT, tkBREAK, \
        BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, MAX_PSEUDOVERSES, \
        INITIAL_REFERENCE_COLLECTION_SIZE, MINIMUM_REFERENCE_COLLECTION_SIZE, MAXIMUM_REFERENCE_COLLECTION_SIZE, \
        parseWindowSize
from Biblelator.Helpers.BiblelatorHelpers import mapReferencesVerseKey, handleInternalBibles
from Biblelator.Windows.ChildWindows import ChildWindow
from Biblelator.Windows.BibleResourceWindows import BibleResourceWindowAddon
from Biblelator.Windows.TextBoxes import BibleBoxAddon

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey, SimpleVersesKey, VerseRangeKey, FlexibleVersesKey
from BibleOrgSys.Reference.BibleOrganisationalSystems import BibleOrganisationalSystem


MAX_CACHED_VERSES = 30 # Per Bible resource window



class BibleReferenceBox( Frame, BibleBoxAddon ):
    """
    """
    def __init__( self, parentWindow, parentFrame, parentApp, internalBible, referenceObject ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: print( "BibleReferenceBox.__init__( {}, {}. {}, {}, {} )".format( parentWindow, parentFrame, parentApp, internalBible.getAName(), referenceObject ) )
        self.parentWindow, self.parentFrame, self.parentApp, self.referenceObject = parentWindow, parentFrame, parentApp, referenceObject
        self.internalBible = handleInternalBibles( self.parentApp, internalBible, self )

        Frame.__init__( self, parentFrame )
        BibleBoxAddon.__init__( self, parentWindow, 'BibleReferenceBox' )

        # Set some dummy values required soon
        #self._contextViewRadioVar, self._formatViewRadioVar, self._groupRadioVar = tk.IntVar(), tk.IntVar(), tk.StringVar()
        #self._groupCode = BIBLE_GROUP_CODES[0] # Put into first/default BCV group
        #self._contextViewMode = DEFAULT
        #self._formatViewMode = DEFAULT
        self.currentVerseKey = SimpleVerseKey( 'UNK','1','1' ) # Unknown book

        #if self._contextViewMode == DEFAULT:
            #self._contextViewMode = 'ByVerse'
            #self.parentWindow.viewVersesBefore, self.parentWindow.viewVersesAfter = 2, 6
        #if self._formatViewMode == DEFAULT:
            #self._formatViewMode = 'Formatted'

        # Create a title bar
        titleBar = Frame( self )
        Button( titleBar, text=_('Close'), command=self.doClose ).pack( side=tk.RIGHT )
        ## Try to get the title width somewhere near correct (if moduleID is a long path)
        #adjModuleID = moduleID
        #self.update() # so we can get the geometry
        #width = parseWindowSize( self.parentWindow.winfo_geometry() )[0] - 60 # Allow for above button
        #if len(adjModuleID)*10 > width: # Note: this doesn't adjust if the window size is changed
            #print( "BRB here1", len(adjModuleID), width, repr(adjModuleID) )
            #x = len(adjModuleID)*100/width # not perfect (too small) for narrow windows
            #adjModuleID = '…' + adjModuleID[int(x):]
            #print( "BRB here2", len(adjModuleID), x, repr(adjModuleID) )
        #titleText = '{} ({})'.format( adjModuleID, boxType.replace( 'BibleReferenceBox', '' ) )
        titleText = self.referenceObject.getShortText()
        self.titleLabel = tk.Label( titleBar, text=titleText )
        self.titleLabel.pack( side=tk.TOP, fill=tk.X )
        titleBar.pack( side=tk.TOP, fill=tk.X )

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        self.textBox = BText( self, height=5, yscrollcommand=self.vScrollbar.set )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( expand=tk.YES, fill=tk.X ) # Full width
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardBoxKeyboardBindings()
        self.textBox.bind( '<Button-1>', self.setFocus ) # So disabled text box can still do select and copy functions

        # Set-up our standard Bible styles
        for USFMKey, styleDict in self.parentApp.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        # Add our extra specialised styles
        self.textBox.tag_configure( 'contextHeader', background='pink', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'context', background='pink', font='helvetica 6' )
        self.textBox.tag_configure( 'markersHeader', background='yellow3', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'markers', background='yellow3', font='helvetica 6' )

        self.pack( expand=tk.YES, fill=tk.BOTH ) # Pack the frame

        # Set-up our Bible system and our callables
        self.BibleOrganisationalSystem = BibleOrganisationalSystem( 'GENERIC-KJV-80-ENG' ) # temp
        self.getNumChapters = self.BibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda BBB,C: MAX_PSEUDOVERSES if C=='-1' or C==-1 \
                                        else self.BibleOrganisationalSystem.getNumVerses( BBB, C )
        self.isValidBCVRef = self.BibleOrganisationalSystem.isValidBCVRef
        self.getFirstBookCode = self.BibleOrganisationalSystem.getFirstBookCode
        self.getPreviousBookCode = self.BibleOrganisationalSystem.getPreviousBookCode
        self.getNextBookCode = self.BibleOrganisationalSystem.getNextBookCode
        self.getBBBFromText = self.BibleOrganisationalSystem.getBBBFromText
        self.getBookName = self.BibleOrganisationalSystem.getBookName
        self.getBookList = self.BibleOrganisationalSystem.getBookList
        self.maxChaptersThisBook, self.maxVersesThisChapter = 150, 150 # temp

        self.verseCache = OrderedDict()

        self.updateShownReferences( self.referenceObject )
    # end of BibleReferenceBox.__init__


    def createStandardBoxKeyboardBindings( self ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceBox.createStandardBoxKeyboardBindings()" )
        for name,command in ( ('SelectAll',self.doSelectAll), ('Copy',self.doCopy),
                             ('Find',self.doBoxFind), ('Refind',self.doBoxRefind),
                             #('Info',self.doShowInfo),
                             #('ShowMain',self.doShowMainWindow),
                             ('Close',self.doClose),
                             ):
            self._createStandardBoxKeyboardBinding( name, command )
    # end of BibleReferenceBox.createStandardBoxKeyboardBindings()


    def xxxgotoBCV( self, BBB, C, V ):
        """

        """
        if BibleOrgSysGlobals.debugFlag: print( "BibleReferenceBox.gotoBCV( {} {}:{} from {} )".format( BBB, C, V, self.currentVerseKey ) )
        # We really need to convert versification systems here
        adjBBB, adjC, adjV, adjS = self.BibleOrganisationalSystem.convertToReferenceVersification( BBB, C, V )
        self.parentWindow.gotoGroupBCV( self._groupCode, adjBBB, adjC, adjV ) # then the App will update me by calling updateShownBCV
    # end of BibleReferenceBox.gotoBCV


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceBox.getContextVerseData( {} )".format( verseKey ) )

        if self.internalBible is not None:
            try: return self.internalBible.getContextVerseData( verseKey )
            except KeyError: # Could be after a verse-bridge ???
                if verseKey.getChapterNumber() != '0':
                    logging.error( "BibleReferenceBox.getContextVerseData for {} {} got a KeyError" \
                                                                .format( self.boxType, verseKey ) )
    # end of BibleReferenceBox.getContextVerseData


    #def XXXgetSwordVerseKey( self, verseKey ):
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "getSwordVerseKey( {} )".format( verseKey ) )
        #BBB, C, V = verseKey.getBCV()
        #return self.parentApp.SwordInterface.makeKey( BBB, C, V )
    ## end of BibleReferenceBox.getSwordVerseKey


    def getCachedVerseData( self, verseKey ):
        """
        Checks to see if the requested verse is in our cache,
            otherwise calls getContextVerseData (from the superclass) to fetch it.

        The cache keeps the newest or most recently used entries at the end.
        When it gets too large, it drops the first entry.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "getCachedVerseData( {} )".format( verseKey ) )
        verseKeyHash = verseKey.makeHash()
        if verseKeyHash in self.verseCache:
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  " + "Retrieved from BibleReferenceBox cache" )
            self.verseCache.move_to_end( verseKeyHash )
            #print( "   returning", self.verseCache[verseKeyHash][0] )
            return self.verseCache[verseKeyHash]
        verseContextData = self.getContextVerseData( verseKey )
        self.verseCache[verseKeyHash] = verseContextData
        if len(self.verseCache) > MAX_CACHED_VERSES:
            #print( "Removing oldest cached entry", len(self.verseCache) )
            self.verseCache.popitem( last=False )
        return verseContextData
    # end of BibleReferenceBox.getCachedVerseData


    def updateShownReferences( self, newReferenceObject ):
        """
        Updates self in various ways depending on the contextViewMode held by the enclosing window.

        The new verse references are in the reference versification system in one of these objects:
            SimpleVerseKey (accepts 'GEN_1:1' or 'GEN','1','1')
            SimpleVersesKey (accepts 'MAT_6:1,4')
            VerseRangeKey (accepts 'JNA_2:1-7')

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceBox.updateShownReferences( {} ) for {}".format( newReferenceObject, self.internalBible.getAName() ) )
            assert isinstance( newReferenceObject, SimpleVerseKey ) or isinstance( newReferenceObject, SimpleVersesKey ) or isinstance( newReferenceObject, VerseRangeKey )

        for j, referenceVerse in enumerate( newReferenceObject ):
            #print( "  refVerse", j, referenceVerse )
            assert isinstance( referenceVerse, SimpleVerseKey )

            refBBB, refC, refV, refS = referenceVerse.getBCVS()
            BBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
            newVerseKey = SimpleVerseKey( BBB, C, V, S )
            #print( "       newVK", newVerseKey )

            # Set firstFlag as False (rather than j==0) so don't get context displayed
            self.displayAppendVerse( False, newVerseKey, self.getCachedVerseData( newVerseKey ), lastFlag=False )

        self.textBox.configure( state=tk.DISABLED ) # Don't allow editing
    # end of BibleReferenceBox.updateShownReferences


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        self.closeReferenceBox()
    # end of BibleReferenceBox.doClose

    def closeReferenceBox( self ):
        """
        Called to finally and irreversibly remove this box from our list and close it.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "BibleReferenceBox.closeReferenceBox()" )
        if self in self.parentWindow.referenceBoxes:
            self.parentWindow.referenceBoxes.remove( self )
            self.destroy()
        else: # we might not have finished making our box yet
            if BibleOrgSysGlobals.debugFlag:
                print( "BibleReferenceBox.closeReferenceBox() for {} wasn't in list".format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Closed resource box" )
    # end of BibleReferenceBox.closeReferenceBox
# end of BibleReferenceBox class



class BibleReferenceBoxes( list ):
    """
    Just keeps a list of the resource (Text) boxes.
    """
    def __init__( self, referenceBoxesParent ):
        self.referenceBoxesParent = referenceBoxesParent
        list.__init__( self )
    # end of BibleReferenceBoxes.__init__
# end of BibleReferenceBoxes class



class BibleReferenceCollectionWindow( ChildWindow, BibleResourceWindowAddon ):
    """
    """
    def __init__( self, parentApp, internalBible, defaultContextViewMode=BIBLE_CONTEXT_VIEW_MODES[0], defaultFormatViewMode=BIBLE_FORMAT_VIEW_MODES[0] ):
        """
        Given a collection name, try to open an empty Bible resource collection window.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "BibleReferenceCollectionWindow.__init__( {}, {} )".format( parentApp, internalBible.getAName() ) )
        self.internalBible = internalBible
        ChildWindow.__init__( self, parentApp, genericWindowType='BibleResource' )
        BibleResourceWindowAddon.__init__( self, 'BibleReferenceCollectionWindow', internalBible.getAName(), defaultContextViewMode, defaultFormatViewMode )

        self.geometry( INITIAL_REFERENCE_COLLECTION_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_REFERENCE_COLLECTION_SIZE, MAXIMUM_REFERENCE_COLLECTION_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        # Get rid of the default widgets
        self.vScrollbar.destroy()
        self.textBox.destroy()

        # Make a frame inside a canvas inside our window (in order to get a scrollbar)
        self.canvas = tk.Canvas( self, borderwidth=0, background='pink' ) #background="#ffffff" )
        self.vsb = Scrollbar( self, orient='vertical', command=self.canvas.yview )
        self.canvas.configure( yscrollcommand=self.vsb.set )
        self.vsb.pack( side=tk.RIGHT, fill=tk.Y )
        self.canvas.pack( side=tk.LEFT, expand=tk.YES, fill=tk.BOTH )
        self.canvasFrame = Frame( self.canvas ) #, background="#ffffff" )
        #self.canvasFrame.columnconfigure( 0, weight=1 )
        #self.canvasFrame.rowconfigure( 0, weight=1 )
        self.window = self.canvas.create_window( (0,0), window=self.canvasFrame, anchor='nw', tags='self.canvasFrame' )
        #self.columnconfigure( 0, weight=1 )
        #self.rowconfigure( 0, weight=1 )
        #self.canvasFrame.bind( '<Configure>', self.OnFrameConfigure )
        self.canvas.bind('<Configure>', self.onCanvasConfigure )

        #self.BCVUpdateType = 'ReferencesMode' # Leave as default
        self.folderPath = self.filename = self.filepath = None
        self.referenceBoxes = BibleReferenceBoxes( self )

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.__init__ finished." )
    # end of BibleReferenceCollectionWindow.__init__

    def onCanvasConfigure( self, event ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.onCanvasConfigure( {} )".format( event ) )

        canvas_width = event.width
        #print( "  Set canvas width to {}".format( canvas_width ) )

        self.canvas.itemconfigure( self.window, width=event.width)
        self.canvas.configure( scrollregion=self.canvas.bbox( 'all' ) )
        #self.canvas.itemconfigure( self.canvasFrame, width=canvas_width )
    # end of BibleReferenceCollectionWindow.onCanvasConfigure

    #def OnFrameConfigure( self, event ):
        #"""
        #Reset the scroll region to encompass the inner frame.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "BibleReferenceCollectionWindow.OnFrameConfigure( {} )".format( event ) )

        #self.canvas.configure( scrollregion=self.canvas.bbox( 'all' ) )
    ## end of BibleReferenceCollectionWindow.OnFrameConfigure


    def setFolderPath( self, newFolderPath ):
        """
        Store the folder path for where our internal Bible files will be.

        We're still waiting for the filename.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.setFolderPath( {!r} )".format( newFolderPath ) )
            assert self.filename is None
            assert self.filepath is None

        self.folderPath = newFolderPath
    # end of BibleReferenceCollectionWindow.setFolderPath


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.createMenuBar()" )

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict[_('Info')][0] )
        #fileMenu.add_separator()
        #fileMenu.add_command( label=_('Rename'), underline=0, command=self.doRename )
        #fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] ) # close this window

        # if 0:
        #     editMenu = tk.Menu( self.menubar )
        #     self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        #     editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        #     editMenu.add_separator()
        #     editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )

        #     searchMenu = tk.Menu( self.menubar )
        #     self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        #     searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=self.parentApp.keyBindingDict[_('Line')][0] )
        #     searchMenu.add_separator()
        #     searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        #     searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=self.parentApp.keyBindingDict[_('Refind')][0] )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
        #gotoMenu.add_command( label=_('Previous book'), underline=-1, command=self.doGotoPreviousBook )
        #gotoMenu.add_command( label=_('Next book'), underline=-1, command=self.doGotoNextBook )
        #gotoMenu.add_command( label=_('Previous chapter'), underline=-1, command=self.doGotoPreviousChapter )
        #gotoMenu.add_command( label=_('Next chapter'), underline=-1, command=self.doGotoNextChapter )
        #gotoMenu.add_command( label=_('Previous section'), underline=-1, command=self.notWrittenYet )
        #gotoMenu.add_command( label=_('Next section'), underline=-1, command=self.notWrittenYet )
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
        self._groupRadioVar.set( self._groupCode )
        gotoMenu.add_radiobutton( label=_('Group A'), underline=6, value='A', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group B'), underline=6, value='B', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group C'), underline=6, value='C', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group D'), underline=6, value='D', variable=self._groupRadioVar, command=self.changeBibleGroupCode )

        self.viewMenu = tk.Menu( self.menubar, tearoff=False ) # Save this reference so we can disable entries later
        self.menubar.add_cascade( menu=self.viewMenu, label=_('View'), underline=0 )
        self.viewMenu.add_radiobutton( label=_('Before and after…'), underline=7, value=1, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label=_('One section'), underline=4, value=2, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label=_('Single verse'), underline=7, value=3, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label=_('Whole book'), underline=6, value=4, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label=_('Whole chapter'), underline=6, value=5, variable=self._contextViewRadioVar, command=self.changeBibleContextView )

        self.viewMenu.add_separator()
        self.viewMenu.add_radiobutton( label=_('Formatted'), underline=0, value=1, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )
        self.viewMenu.add_radiobutton( label=_('Unformatted'), underline=0, value=2, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )

        #if 'DBP' in self.windowType: # disable excessive online use
            #self.viewMenu.entryconfigure( 'Whole book', state=tk.DISABLED )
            #self.viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        #resourcesMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=resourcesMenu, label=_('Resources'), underline=0 )
        #resourcesMenu.add_command( label=_('Online (DBP)…'), underline=0, command=self.doOpenDBPBibleResource )
        #resourcesMenu.add_command( label=_('Sword module…'), underline=0, command=self.doOpenSwordResource )
        #resourcesMenu.add_command( label=_('Other (local)…'), underline=1, command=self.doOpenInternalBibleResource )

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
    # end of BibleReferenceCollectionWindow.createMenuBar


    def refreshTitle( self ):
        self.title( "[{}] {} Bible Reference Collection".format( self._groupCode, self.internalBible.getAName() ) )
                        #self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber() ) )
    # end if BibleReferenceCollectionWindow.refreshTitle


    #def openDBPBibleReferenceBox( self, moduleAbbreviation, windowGeometry=None ):
        #"""
        #Create the actual requested DBP Bible resource window.

        #Returns the new DBPBibleReferenceBox object.
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "openDBPBibleReferenceBox()" )
            #self.parentApp.setDebugText( "openDBPBibleReferenceBox…" )
            #assert moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6
        ##tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        #dBRB = DBPBibleReferenceBox( self, moduleAbbreviation )
        #if windowGeometry: halt; dBRB.geometry( windowGeometry )
        #if dBRB.DBPModule is None:
            #logging.critical( "Application.openDBPBibleReferenceBox: Unable to open resource {}".format( repr(moduleAbbreviation) ) )
            #dBRB.destroy()
            #showError( self, APP_NAME, _("Sorry, unable to open DBP resource") )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openDBPBibleReferenceBox" )
            #self.parentApp.setReadyStatus()
            #return None
        #else:
            #dBRB.updateShownBCV( self.parentApp.getVerseKey( dBRB._groupCode ) )
            #self.referenceBoxes.append( dBRB )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openDBPBibleReferenceBox" )
            #self.parentApp.setReadyStatus()
            #return dBRB
    ## end of BibleReferenceCollectionWindow.openDBPBibleReferenceBox


    #def openInternalBibleReferenceBox( self, modulePath, windowGeometry=None ):
        #"""
        #Create the actual requested local/internal Bible resource window.

        #Returns the new InternalBibleReferenceBox object.
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "openInternalBibleReferenceBox()" )
            #self.parentApp.setDebugText( "openInternalBibleReferenceBox…" )
        ##tk.Label( self, text=modulePath ).pack( side=tk.TOP, fill=tk.X )
        #iBRB = InternalBibleReferenceBox( self, modulePath )
        #if windowGeometry: halt; iBRB.geometry( windowGeometry )
        #if iBRB.internalBible is None:
            #logging.critical( "Application.openInternalBibleReferenceBox: Unable to open resource {}".format( repr(modulePath) ) )
            #iBRB.destroy()
            #showError( self, APP_NAME, _("Sorry, unable to open internal Bible resource") )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openInternalBibleReferenceBox" )
            #self.parentApp.setReadyStatus()
            #return None
        #else:
            #iBRB.updateShownBCV( self.parentApp.getVerseKey( iBRB._groupCode ) )
            #self.referenceBoxes.append( iBRB )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openInternalBibleReferenceBox" )
            #self.parentApp.setReadyStatus()
            #return iBRB
    ## end of BibleReferenceCollectionWindow.openInternalBibleReferenceBox


    #def openBox( self, boxType, boxSource ):
        #"""
        #(Re)open a text box.
        #"""
        #if boxType == 'DBP': self.openDBPBibleReferenceBox( boxSource )
        #elif boxType == 'Sword': self.openSwordBibleReferenceBox( boxSource )
        #elif boxType == 'Internal': self.openInternalBibleReferenceBox( boxSource )
        #elif BibleOrgSysGlobals.debugFlag: halt
    ## end of BibleReferenceCollectionWindow.openBox


    def updateShownBCV( self, newReferenceVerseKey, originator=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.updateShownBCV( {}, {} ) for".format( newReferenceVerseKey, originator ), self.moduleID )
            assert isinstance( newReferenceVerseKey, SimpleVerseKey )

        refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
        BBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
        newVerseKey = SimpleVerseKey( BBB, C, V, S )

        self.updateShownReferences( mapReferencesVerseKey( newVerseKey ) )
    # end of BibleReferenceCollectionWindow.updateShownBCV


    def updateShownReferences( self, newReferencesVerseKeys ):
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        The new verse key is in the reference versification system.

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.updateShownReferences( {} ) for".format( newReferencesVerseKeys ), self.moduleID )
            #print( "contextViewMode", self._contextViewMode )
            assert isinstance( newReferencesVerseKeys, list ) or newReferencesVerseKeys is None

        # Remove any previous resource boxes
        for referenceBox in self.referenceBoxes:
            referenceBox.destroy()
        self.referenceBoxes = BibleReferenceBoxes( self )

        if newReferencesVerseKeys is not None: # open new resource boxes
            assert isinstance( newReferencesVerseKeys, list )
            for newReferencesVerseKey in newReferencesVerseKeys:
                #print( "BibleReferenceCollectionWindow.updateShownReferences.newReferencesVerseKey", newReferencesVerseKey )
                if newReferencesVerseKey is None:
                    print( "BibleReferenceCollectionWindow.updateShownReferences.newReferencesVerseKey: Why do we have NONE here?" ) #, newReferencesVerseKeys )
                else:
                    assert isinstance( newReferencesVerseKey, FlexibleVersesKey )
                    for verseKeyObject in newReferencesVerseKey:
                        #print( "  BRCWupdateShownReferences: {}".format( verseKeyObject ) )
                        referenceBox = BibleReferenceBox( self, self.canvasFrame, self.parentApp, self.internalBible, verseKeyObject )
                        self.referenceBoxes.append( referenceBox )

        self.currentVerseKeys = newReferencesVerseKeys # The FlexibleVersesKey object
        self.refreshTitle()
    # end of BibleReferenceCollectionWindow.updateShownReferences


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.doHelp()" )
        from Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of BibleReferenceCollectionWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleReferenceCollectionWindow.doAbout()" )
        from About import AboutBox

        aboutInfo = programNameVersion + '\n'
        aboutInfo += '\n' + _("Information about {}").format( self.windowType ) + '\n'
        aboutInfo += '\n' + _("A Bible Reference Collection box can contain multiple different Scripture references all shown from the same resource translation or commentary.")
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of BibleReferenceCollectionWindow.doAbout
# end of BibleReferenceCollectionWindow class



def demo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

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
# end of BibleReferenceCollection.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BibleReferenceCollection.py
