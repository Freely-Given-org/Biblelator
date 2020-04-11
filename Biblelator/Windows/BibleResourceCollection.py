#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BibleResourceCollection.py
#
# Bible resource collection for Biblelator Bible display/editing
#
# Copyright (C) 2014-2019 Robert Hunt
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
    (non-editable) Bible resource collection windows.

A Bible resource collection is a collection of different Bible resources
    all displaying the same reference.

    class BibleResourceBoxesList( list )
        __init__( self, resourceBoxesParent )

    class BibleResourceBox( Frame, BibleBoxAddon )
        __init__( self, parentWindow, boxType, moduleID )
        createStandardBoxKeyboardBindings( self )
        gotoBCV( self, BBB, C, V )
        getSwordVerseKey( self, verseKey )
        getCachedVerseData( self, verseKey )
        #BibleResourceBoxXXXdisplayAppendVerse( self, firstFlag, verseKey, verseContextData, currentVerseFlag=False )
        #getBeforeAndAfterBibleData( self, newVerseKey )
        setCurrentVerseKey( self, newVerseKey )
        updateShownBCV( self, newReferenceVerseKey, originator=None )
        doClose( self, event=None )
        closeResourceBox( self )

    class SwordBibleResourceBox( BibleResourceBox )
        __init__( self, parentWindow, moduleAbbreviation )
        getContextVerseData( self, verseKey )

    class DBPBibleResourceBox( BibleResourceBox )
        __init__( self, parentWindow, moduleAbbreviation )
        getContextVerseData( self, verseKey )

    class InternalBibleResourceBox( BibleResourceBox )
        __init__( self, parentWindow, modulePath )
        getContextVerseData( self, verseKey )

    class BibleResourceCollectionWindow( BibleResourceWindow )
        __init__( self, parentApp, collectionName )
        createMenuBar( self )
        refreshTitle( self )
        doRename( self )
        doOpenNewDBPBibleResourceBox( self )
        openDBPBibleResourceBox( self, moduleAbbreviation, windowGeometry=None )
        doOpenNewSwordResourceBox( self )
        openSwordBibleResourceBox( self, moduleAbbreviation, windowGeometry=None )
        doOpenNewInternalBibleResourceBox( self )
        openInternalBibleResourceBox( self, modulePath, windowGeometry=None )
        openBox( self, boxType, boxSource )
        updateShownBCV( self, newReferenceVerseKey, originator=None )
        doHelp( self, event=None )
        doAbout( self, event=None )
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2019-05-12' # by RJH
SHORT_PROGRAM_NAME = "BibleResourceCollection"
PROGRAM_NAME = "Biblelator Bible Resource Collection"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = True


import os
import logging
from collections import OrderedDict

import tkinter as tk
from tkinter.filedialog import Directory #, SaveAs
from tkinter.ttk import Frame, Button, Scrollbar

# Biblelator imports
from Biblelator.BiblelatorGlobals import APP_NAME, DEFAULT, tkBREAK, \
                BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, \
                INITIAL_RESOURCE_COLLECTION_SIZE, MINIMUM_RESOURCE_COLLECTION_SIZE, MAXIMUM_RESOURCE_COLLECTION_SIZE, \
                MAX_PSEUDOVERSES, parseWindowSize
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showInfo
from Biblelator.Dialogs.BiblelatorDialogs import SelectResourceBoxDialog, RenameResourceCollectionDialog, ChooseResourcesDialog
from Biblelator.Windows.ChildWindows import ChildWindow
from Biblelator.Windows.BibleResourceWindows import BibleResourceWindowAddon
from Biblelator.Windows.TextBoxes import BText, ChildBoxAddon, BibleBoxAddon, HebrewInterlinearBibleBoxAddon
from Biblelator.Helpers.BiblelatorHelpers import handleInternalBibles

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
from BibleOrgSys.Bible import Bible
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Online.DBPOnline import DBPBibles, DBPBible
from BibleOrgSys.Formats.SwordResources import SwordType, SwordInterface
from BibleOrgSys.UnknownBible import UnknownBible
from BibleOrgSys.Formats.PickledBible import ZIPPED_PICKLE_FILENAME_END, getZippedPickledBiblesDetails
from BibleOrgSys.Reference.BibleOrganisationalSystems import BibleOrganisationalSystem


MAX_CACHED_VERSES = 30 # Per Bible resource window



class BibleResourceBoxesList( list ):
    """
    Keeps a list of the resource (Text) boxes.

    Allows them to be moved up and down
    """
    def __init__( self, resourceBoxesParent ):
        """
        Set-up the list
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceBoxesList.__init__( {} )".format( resourceBoxesParent ) )

        self.resourceBoxesListParent = resourceBoxesParent
        list.__init__( self )
    # end of BibleResourceBoxesList.__init__


    def moveUp( self, boxObject ):
        """
        Moves the box up and redisplays.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceBoxesList.moveUp( {} )".format( boxObject ) )

        ix = self.index( boxObject )
        if ix > 0:
            self.pop( ix )
            self.insert( ix-1, boxObject ) # Insert it earlier
            self.__recreate()
    # end of BibleResourceBoxesList.moveUp


    def moveDown( self, boxObject ):
        """
        Moves the box down and redisplays.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceBoxesList.moveDown( {} )".format( boxObject ) )

        ix = self.index( boxObject )
        if ix < len(self)-1:
            self.pop( ix )
            self.insert( ix+1, boxObject ) # Insert it earlier
            self.__recreate()
    # end of BibleResourceBoxesList.moveDown


    def __recreate( self ):
        """
        Forget the packing, then redraw all of the boxes in the list
            (presumably in a new order).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceBoxesList.__recreate()" )

        for boxObject in self: # forget our current packing into the frame
            boxObject.pack_forget()
        for boxObject in self: # repack in our new order
            boxObject.pack( expand=tk.YES, fill=tk.BOTH ) # Pack me into the frame

        #else: # old code
            ## First remember the details of each box and then destroy the box
            #tempList = []
            #for boxObject in self:
                #boxType = boxObject.boxType.replace( 'BibleResourceBox', '' )
                #boxSource = boxObject.moduleID
                #tempList.append( (boxType,boxSource) )
                #boxObject.destroy()
            #self.clear()

            ## Now recreate all the boxes in order
            #for boxType,boxSource in tempList:
                #self.resourceBoxesListParent.openBox( boxType, boxSource )
    # end of BibleResourceBoxesList.__recreate
# end of BibleResourceBoxesList class



class BibleResourceBox( Frame, ChildBoxAddon, BibleBoxAddon ):
    """
    A base class to provide the boxes for a BibleResourceCollectionWindow

    The moduleID can be a name, abbreviation or folder (depending on the boxType)

    The subclass must provide a getContextVerseData function.
    """
    def __init__( self, parentWindow, boxType, moduleID ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("BibleResourceBox.__init__( {}, {}, {} )").format( parentWindow, boxType, moduleID ) )
        self.parentWindow, self.boxType, self.moduleID = parentWindow, boxType, moduleID
        self.parentApp = self.parentWindow.parentApp
        Frame.__init__( self, parentWindow )
        ChildBoxAddon.__init__( self, self.parentWindow )

        # Create a title bar frame
        titleBar = Frame( self )
        Button( titleBar, text=_('Close'), width=5, command=self.doClose ).pack( side=tk.RIGHT )
        Button( titleBar, text=_('↓'), width=2, command=self.doMeDown ).pack( side=tk.RIGHT )
        Button( titleBar, text=_('↑'), width=2, command=self.doMeUp ).pack( side=tk.RIGHT )
        # Try to get the title width somewhere near correct (if moduleID is a long path)
        adjModuleID = moduleID
        self.update() # so we can get the geometry
        width = parseWindowSize( self.parentWindow.winfo_geometry() )[0] - 60 # Allow for above button
        if len(adjModuleID)*10 > width: # Note: this doesn't adjust if the window size is changed
            #print( "BRB here1", len(adjModuleID), width, repr(adjModuleID) )
            x = len(adjModuleID)*100/width # not perfect (too small) for narrow windows
            adjModuleID = '…' + adjModuleID[int(x):]
            #print( "BRB here2", len(adjModuleID), x, repr(adjModuleID) )
        titleText = '{} ({})'.format( adjModuleID, boxType.replace( 'BibleResourceBox', '' ).replace( 'DBP', 'DBP online' ) )
        self.titleLabel = tk.Label( titleBar, text=titleText )
        self.titleLabel.pack( side=tk.TOP, fill=tk.X )
        titleBar.pack( side=tk.TOP, fill=tk.X )

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        self.textBox = BText( self, height=1, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardBoxKeyboardBindings()
        self.textBox.bind( '<Button-1>', self.setFocus ) # So disabled text box can still do select and copy functions
        self.createContextMenu() # for the box

        BibleBoxAddon.__init__( self, self.parentWindow, boxType )

        # Set-up our standard Bible styles
        for USFMKey, styleDict in self.parentApp.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        # Add our extra specialised styles
        self.textBox.tag_configure( 'contextHeader', background='pink', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'context', background='pink', font='helvetica 6' )
        self.textBox.tag_configure( 'markersHeader', background='yellow3', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'markers', background='yellow3', font='helvetica 6' )

        self.pack( expand=tk.YES, fill=tk.BOTH ) # Pack me into the frame

        # Set-up our default Bible system and our callables
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
    # end of BibleResourceBox.__init__


    def createStandardBoxKeyboardBindings( self ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceBox.createStandardBoxKeyboardBindings()") )
        for name,command in ( ('SelectAll',self.doSelectAll), ('Copy',self.doCopy),
                             ('Find',self.doBibleFind), #('Refind',self.doBoxRefind),
                             #('Info',self.doShowInfo),
                             #('ShowMain',self.parentWindow.doShowMainWindow),
                             ('Close',self.doClose),
                             ):
            self._createStandardBoxKeyboardBinding( name, command )
    # end of BibleResourceBox.createStandardBoxKeyboardBindings()


    #def gotoBCV( self, BBB, C, V ):
        #"""

        #"""
        #if BibleOrgSysGlobals.debugFlag: print( _("BibleResourceBox.gotoBCV( {} {}:{} from {} )").format( BBB, C, V, self.currentVerseKey ) )
        ## We really need to convert versification systems here
        #adjBBB, adjC, adjV, adjS = self.BibleOrganisationalSystem.convertToReferenceVersification( BBB, C, V )
        #self.parentWindow.gotoGroupBCV( self._groupCode, adjBBB, adjC, adjV ) # then the App will update me by calling updateShownBCV
    ## end of BibleResourceBox.gotoBCV


    def getSwordVerseKey( self, verseKey ):
        """
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( _("getSwordVerseKey( {} )").format( verseKey ) )
        BBB, C, V = verseKey.getBCV()
        return self.parentApp.SwordInterface.makeKey( BBB, C, V )
    # end of BibleResourceBox.getSwordVerseKey


    def getCachedVerseData( self, verseKey ):
        """
        Checks to see if the requested verse is in our cache,
            otherwise calls getContextVerseData (from the superclass) to fetch it.

        The cache keeps the newest or most recently used entries at the end.
        When it gets too large, it drops the first entry.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( _("getCachedVerseData( {} )").format( verseKey ) )
        verseKeyHash = verseKey.makeHash()
        if verseKeyHash in self.verseCache:
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  " + _("Retrieved from BibleResourceBox cache") )
            self.verseCache.move_to_end( verseKeyHash )
            return self.verseCache[verseKeyHash]
        verseContextData = self.getContextVerseData( verseKey )
        self.verseCache[verseKeyHash] = verseContextData
        if len(self.verseCache) > MAX_CACHED_VERSES:
            #print( "Removing oldest cached entry", len(self.verseCache) )
            self.verseCache.popitem( last=False )
        return verseContextData
    # end of BibleResourceBox.getCachedVerseData


    def setCurrentVerseKey( self, newVerseKey ):
        """
        Called to set the current verse key.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceBox.setCurrentVerseKey( {} )").format( newVerseKey ) )
            self.parentApp.setDebugText( "BRW setCurrentVerseKey…" )
            assert isinstance( newVerseKey, SimpleVerseKey )
        self.currentVerseKey = newVerseKey

        BBB = self.currentVerseKey.getBBB()
        try:
            self.maxChaptersThisBook = self.getNumChapters( BBB )
            self.maxVersesThisChapter = self.getNumVerses( BBB, self.currentVerseKey.getChapterNumber() )
        except KeyError: # presumably the book doesn't exist
            self.maxChaptersThisBook = self.maxVersesThisChapter = 1
    # end of BibleResourceBox.setCurrentVerseKey


    def updateShownBCV( self, newReferenceVerseKey, originator=None ):
        """
        Updates self in various ways depending on the contextViewMode held by the enclosing window.

        The new verse key is in the reference versification system.

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceBox.updateShownBCV( {}, {} ) for".format( newReferenceVerseKey, originator ), self.moduleID )
            #print( "contextViewMode", self._contextViewMode )
            assert isinstance( newReferenceVerseKey, SimpleVerseKey )

        refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
        BBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
        newVerseKey = SimpleVerseKey( BBB, C, V, S )

        self.setCurrentVerseKey( newVerseKey )
        self.clearText() # Leaves the text box enabled
        startingFlag = True

        # Safety-check in case they edited the settings file
        if 'DBP' in self.boxType and self.parentWindow._contextViewMode in ('ByBook','ByChapter',):
            print( _("updateShownBCV: Safety-check converted {} contextViewMode for DBP").format( repr(self.parentWindow._contextViewMode) ) )
            self.parentWindow._contextViewRadioVar.set( 3 ) # ByVerse
            self.parentWindow.changeBibleContextView()

        if self.parentWindow._contextViewMode == 'BeforeAndAfter':
            bibleData = self.getBeforeAndAfterBibleData( newVerseKey )
            if bibleData:
                verseData, previousVerses, nextVerses = bibleData
                for verseKey,previousVerseData in previousVerses:
                    self.displayAppendVerse( startingFlag, verseKey, previousVerseData )
                    startingFlag = False
                self.displayAppendVerse( startingFlag, newVerseKey, verseData, currentVerseFlag=True )
                for verseKey,nextVerseData in nextVerses:
                    self.displayAppendVerse( False, verseKey, nextVerseData )

        elif self.parentWindow._contextViewMode == 'ByVerse':
            cachedVerseData = self.getCachedVerseData( newVerseKey )
            #print( "cVD for", self.moduleID, newVerseKey, cachedVerseData )
            if cachedVerseData is None: # We might have a missing or bridged verse
                intV = int( V )
                while intV > 1:
                    intV -= 1 # Go back looking for bridged verses to display
                    cachedVerseData = self.getCachedVerseData( SimpleVerseKey( BBB, C, intV, S ) )
                    #print( "  cVD for", self.moduleID, intV, cachedVerseData )
                    if cachedVerseData is not None: # it seems to have worked
                        break # Might have been nice to check/confirm that it was actually a bridged verse???
            self.displayAppendVerse( True, newVerseKey, cachedVerseData, currentVerseFlag=True )

        #elif self.parentWindow._contextViewMode == 'BySection':
            #self.displayAppendVerse( True, newVerseKey, self.getCachedVerseData( newVerseKey ), currentVerseFlag=True )
            #BBB, C, V = newVerseKey.getBCV()
            #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            #print( "\nBySection is not finished yet -- just shows a single verse!\n" ) # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            ##for thisC in range( -1, self.getNumChapters( BBB ) ):
                ##try: numVerses = self.getNumVerses( BBB, thisC )
                ##except KeyError: numVerses = 0
                ##for thisV in range( numVerses ):
                    ##thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    ##thisVerseData = self.getCachedVerseData( thisVerseKey )
                    ##self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            ##currentVerseFlag=thisC==intC and thisV==intV )
                    ##startingFlag = False

        #elif self.parentWindow._contextViewMode == 'ByBook':
            #BBB, C, V = newVerseKey.getBCV()
            #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            #for thisC in range( -1, self.getNumChapters( BBB ) + 1 ):
                #try: numVerses = self.getNumVerses( BBB, thisC )
                #except KeyError: numVerses = 0
                #for thisV in range( numVerses ):
                    #thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    #thisVerseData = self.getCachedVerseData( thisVerseKey )
                    #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            #currentVerseFlag=thisC==intC and thisV==intV )
                    #startingFlag = False

        #elif self.parentWindow._contextViewMode == 'ByChapter':
            #BBB, C, V = newVerseKey.getBCV()
            #intV = newVerseKey.getVerseNumberInt()
            #try: numVerses = self.getNumVerses( BBB, C )
            #except KeyError: numVerses = 0
            #for thisV in range( numVerses + 1 ):
                #thisVerseKey = SimpleVerseKey( BBB, C, thisV )
                #thisVerseData = self.getCachedVerseData( thisVerseKey )
                #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData, currentVerseFlag=thisV==intV )
                #startingFlag = False

        else:
            logging.critical( _("BibleResourceBox.updateShownBCV: Bad context view mode {}").format( self.parentWindow._contextViewMode ) )
            if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode

        self.textBox.configure( state=tk.DISABLED ) # Don't allow editing

        # Make sure we can see what we're supposed to be looking at
        desiredMark = 'C{}V{}'.format( newVerseKey.getChapterNumber(), newVerseKey.getVerseNumber() )
        try: self.textBox.see( desiredMark )
        except tk.TclError: print( _("USFMEditWindow.updateShownBCV couldn't find {}").format( repr( desiredMark ) ) )
        self.lastCVMark = desiredMark
    # end of BibleResourceBox.updateShownBCV


    def doMeDown( self, event=None ):
        """
        Called from the GUI.
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'moveDown: {} {}'.format( self.boxType, self.moduleID ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceBox.doMeDown( {} )").format( event ) )

        self.parentWindow.resourceBoxesList.moveDown( self )
    # end of BibleResourceBox.doMeDown

    def doMeUp( self, event=None ):
        """
        Called from the GUI.
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'moveUp: {} {}'.format( self.boxType, self.moduleID ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceBox.doMeUp( {} )").format( event ) )

        self.parentWindow.resourceBoxesList.moveUp( self )
    # end of BibleResourceBox.doMeUp


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        self.closeResourceBox()
    # end of BibleResourceBox.doClose

    def closeResourceBox( self ):
        """
        Called to finally and irreversibly remove this box from our list and close it.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( _("BibleResourceBox.closeResourceBox()") )
        if self in self.parentWindow.resourceBoxesList:
            self.parentWindow.resourceBoxesList.remove( self )
            self.destroy()
        else: # we might not have finished making our box yet
            if BibleOrgSysGlobals.debugFlag:
                print( _("BibleResourceBox.closeResourceBox() for {} wasn't in list").format( self.windowType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Closed resource box" )
    # end of BibleResourceBox.closeResourceBox
# end of BibleResourceBox class



class SwordBibleResourceBox( BibleResourceBox ):
    """
    """
    def __init__( self, parentWindow, moduleAbbreviation ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: print( "SwordBibleResourceBox.__init__( {}, {} )".format( parentWindow, moduleAbbreviation ) )
        self.parentWindow, self.moduleAbbreviation = parentWindow, moduleAbbreviation
        BibleResourceBox.__init__( self, self.parentWindow, 'SwordBibleResourceBox', self.moduleAbbreviation )
        #self.boxType = 'SwordBibleResourceBox'

        #self.SwordModule = None # Loaded later in self.getBeforeAndAfterBibleData()
        self.SwordModule = self.parentApp.SwordInterface.getModule( self.moduleAbbreviation )
        if self.SwordModule is None:
            logging.error( _("SwordBibleResourceBox.__init__ Unable to open Sword module: {}").format( self.moduleAbbreviation ) )
            self.SwordModule = None
        if isinstance( self.SwordModule, Bible ):
            #print( "Handle internalBible for SwordModule" )
            handleInternalBibles( self.parentApp, self.SwordModule, self )
        else: print( "SwordModule using {} is {}".format( SwordType, self.SwordModule ) )

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("SwordBibleResourceBox.__init__ finished.") )
    # end of SwordBibleResourceBox.__init__


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("SwordBibleResourceBox.getContextVerseData( {} )").format( verseKey ) )
        if self.SwordModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                SwordKey = self.getSwordVerseKey( verseKey )
                rawContextInternalBibleData = self.parentApp.SwordInterface.getContextVerseData( self.SwordModule, SwordKey )
                rawInternalBibleData, context = rawContextInternalBibleData
                # Clean up the data -- not sure that it should be done here! … XXXXXXXXXXXXXXXXXXX
                from InternalBibleInternals import InternalBibleEntryList, InternalBibleEntry
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
    # end of SwordBibleResourceBox.getContextVerseData
# end of SwordBibleResourceBox class



class DBPBibleResourceBox( BibleResourceBox ):
    """
    This is a box displaying a versified Bible that was downloaded from the online Digital Bible Platform.

    NOTE: The DBPBible class is NOT based on the Bible class
            because it's so unlike most Bibles which are local.
    """
    def __init__( self, parentWindow, moduleAbbreviation ):
        """
        Given a Bible abbreviation, try to set up a connection to the online Digital Bible Platform.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "DBPBibleResourceBox.__init__( {}, {} )".format( parentWindow, moduleAbbreviation ) )
            assert moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6
        self.parentWindow, self.moduleAbbreviation = parentWindow, moduleAbbreviation

        self.DBPModule = None # (for refreshTitle called from the base class)
        BibleResourceBox.__init__( self, self.parentWindow, 'DBPBibleResourceBox', self.moduleAbbreviation )
        #self.boxType = 'DBPBibleResourceBox'

        try: self.DBPModule = DBPBible( self.moduleAbbreviation )
        except FileNotFoundError:
            logging.error( _("DBPBibleResourceBox.__init__ Unable to find a key to connect to Digital Bible Platform") )
            self.DBPModule = None
        except ConnectionError:
            logging.error( _("DBPBibleResourceBox.__init__ Unable to connect to Digital Bible Platform") )
            self.DBPModule = None
        #if isinstance( self.DBPModule, Bible ): # Never true
            ##print( "Handle internalBible for DBPModule" )
            #handleInternalBibles( self.parentApp, self.DBPModule, self )
        #elif
        if BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.verbosityLevel > 2:
            print( "DBPModule is", type(self.DBPModule), self.DBPModule )
    # end of DBPBibleResourceBox.__init__


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("DBPBibleResourceBox.getContextVerseData( {} )").format( verseKey ) )

        if self.DBPModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                return self.DBPModule.getContextVerseData( verseKey )
    # end of DBPBibleResourceBox.getContextVerseData
# end of DBPBibleResourceBox class



class InternalBibleResourceBox( BibleResourceBox ):
    """
    This is a box displaying a versified Bible that was loaded from the internal file system.
    """
    def __init__( self, parentWindow, modulePath ):
        """
        Given a folderpath or filepath, try to open an UnknownBible.

        If successful, set self.internalBible to point to the loaded Bible.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "InternalBibleResourceBox.__init__( {}, {!r} )".format( parentWindow, modulePath ) )

        self.parentWindow, self.modulePath = parentWindow, modulePath

        self.internalBible = None
        BibleResourceBox.__init__( self, self.parentWindow, 'InternalBibleResourceBox', self.modulePath )

        try: self.UnknownBible = UnknownBible( self.modulePath )
        except FileNotFoundError:
            logging.error( _("InternalBibleResourceBox.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
            self.UnknownBible = None
        if self.UnknownBible is not None:
            result = self.UnknownBible.search( autoLoadAlways=True )
            if isinstance( result, str ):
                print( "Unknown Bible returned: {}".format( repr(result) ) )
                self.internalBible = None
            else:
                #print( "Handle internalBible for internalBible" )
                self.internalBible = handleInternalBibles( self.parentApp, result, self )
        if self.internalBible is not None: # Define which functions we use by default
            self.getNumVerses = self.internalBible.getNumVerses
            self.getNumChapters = self.internalBible.getNumChapters
    # end of InternalBibleResourceBox.__init__


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("InternalBibleResourceBox.getContextVerseData( {} )").format( verseKey ) )

        if self.internalBible is not None:
            try: return self.internalBible.getContextVerseData( verseKey )
            except KeyError: # Could be after a verse-bridge ???
                if verseKey.getChapterNumber() != '0':
                    logging.error( _("InternalBibleResourceBox.getContextVerseData for {} {} got a KeyError") \
                                                                .format( self.boxType, verseKey ) )
    # end of InternalBibleResourceBox.getContextVerseData
# end of InternalBibleResourceBox class



#class HebrewBibleResourceBox( BibleResourceBox, HebrewInterlinearBibleBoxAddon ):
    #"""
    #This is a box displaying a versified Bible that was loaded from the internal file system.
    #"""
    #def __init__( self, parentWindow, modulePath ):
        #"""
        #Given a folderpath or filepath, try to open an UnknownBible.

        #If successful, set self.internalBible to point to the loaded Bible.
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "HebrewBibleResourceBox.__init__( {}, {!r} )".format( parentWindow, modulePath ) )

        #self.parentWindow, self.modulePath = parentWindow, modulePath

        #self.internalBible = None
        #BibleResourceBox.__init__( self, self.parentWindow, 'HebrewBibleResourceBox', self.modulePath )
        #HebrewInterlinearBibleBoxAddon.__init__( self, self.parentWindow, 4 )

        #try: self.UnknownBible = UnknownBible( self.modulePath )
        #except FileNotFoundError:
            #logging.error( _("HebrewBibleResourceBox.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
            #self.UnknownBible = None
        #if self.UnknownBible is not None:
            #result = self.UnknownBible.search( autoLoadAlways=True )
            #if isinstance( result, str ):
                #print( "Unknown Bible returned: {}".format( repr(result) ) )
                #self.internalBible = None
            #else:
                ##print( "Handle internalBible for internalBible" )
                #self.internalBible = handleInternalBibles( self.parentApp, result, self )
        #if self.internalBible is not None: # Define which functions we use by default
            #self.getNumVerses = self.internalBible.getNumVerses
            #self.getNumChapters = self.internalBible.getNumChapters
    ## end of HebrewBibleResourceBox.__init__


    #def getContextVerseData( self, verseKey ):
        #"""
        #Fetches and returns the internal Bible data for the given reference.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("HebrewBibleResourceBox.getContextVerseData( {} )").format( verseKey ) )

        #if self.internalBible is not None:
            #try: return self.internalBible.getContextVerseData( verseKey )
            #except KeyError: # Could be after a verse-bridge ???
                #if verseKey.getChapterNumber() != '0':
                    #logging.error( _("HebrewBibleResourceBox.getContextVerseData for {} {} got a KeyError") \
                                                                #.format( self.boxType, verseKey ) )
    ## end of HebrewBibleResourceBox.getContextVerseData
## end of HebrewBibleResourceBox class



class BibleResourceCollectionWindow( ChildWindow, BibleResourceWindowAddon ):
    """
    """
    def __init__( self, parentApp, collectionName, defaultContextViewMode=BIBLE_CONTEXT_VIEW_MODES[0], defaultFormatViewMode=BIBLE_FORMAT_VIEW_MODES[0] ):
        """
        Given a collection name, try to open an empty Bible resource collection window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleResourceCollectionWindow.__init__( {}, {} )".format( parentApp, collectionName ) )
        #self.parentApp = parentApp
        ChildWindow.__init__( self, parentApp, genericWindowType='BibleResource' )
        BibleResourceWindowAddon.__init__( self, 'BibleResourceCollectionWindow', collectionName, defaultContextViewMode, defaultFormatViewMode )

        self.geometry( INITIAL_RESOURCE_COLLECTION_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_RESOURCE_COLLECTION_SIZE, MAXIMUM_RESOURCE_COLLECTION_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        # Get rid of the default widgets
        self.vScrollbar.destroy()
        self.textBox.destroy()
        del self.textBox

        self.viewVersesBefore, self.viewVersesAfter = 1, 1

        self.resourceBoxesList = BibleResourceBoxesList( self )
        self.createMenuBar()

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceCollectionWindow.__init__ finished.") )
    # end of BibleResourceCollectionWindow.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( _("BibleResourceBox.createMenuBar()") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        fileMenu.add_command( label=_('Rename'), underline=0, command=self.doRename )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict[_('Info')][0] )
        fileMenu.add_separator()
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
        gotoMenu.add_command( label=_('Previous book'), underline=-1, command=self.doGotoPreviousBook )
        gotoMenu.add_command( label=_('Next book'), underline=-1, command=self.doGotoNextBook )
        gotoMenu.add_command( label=_('Previous chapter'), underline=-1, command=self.doGotoPreviousChapter )
        gotoMenu.add_command( label=_('Next chapter'), underline=-1, command=self.doGotoNextChapter )
        gotoMenu.add_command( label=_('Previous section'), underline=-1, command=self.notWrittenYet )
        gotoMenu.add_command( label=_('Next section'), underline=-1, command=self.notWrittenYet )
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

        resourcesMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=resourcesMenu, label=_('Resources'), underline=0 )
        resourcesMenu.add_command( label=_('Included…'), underline=0, command=self.doOpenNewBOSBibleResourceBox )
        resourcesMenu.add_command( label=_('Online (DBP)…'), underline=0, command=self.doOpenNewDBPBibleResourceBox )
        resourcesMenu.add_command( label=_('Sword module…'), underline=0, command=self.doOpenNewSwordResourceBox )
        resourcesMenu.add_command( label=_('Other (local)…'), underline=1, command=self.doOpenNewInternalBibleResourceBox )

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
    # end of BibleResourceCollectionWindow.createMenuBar


    def refreshTitle( self ):
        self.title( "[{}] {} Bible Resource Collection {} {}:{}".format( self._groupCode,
                        self.moduleID,
                        self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber() ) )
    # end if BibleResourceCollectionWindow.refreshTitle


    def doRename( self ):
        if BibleOrgSysGlobals.debugFlag:
            print( _("doRename()") )
            self.parentApp.setDebugText( "doRename…" )
        existingNames = []
        for cw in self.parentApp.childWindows:
            existingNames.append( cw.moduleID.upper() )
        rrc = RenameResourceCollectionDialog( self, self.moduleID, existingNames, title=_('Rename collection') )
        if BibleOrgSysGlobals.debugFlag: print( "rrcResult", repr(rrc.result) )
        if rrc.result:
            self.moduleID = rrc.result
            self.refreshTitle()
    # end if BibleResourceCollectionWindow.doRename


    def doOpenNewDBPBibleResourceBox( self ):
        """
        Open a DigitalBiblePlatform online Bible (called from a menu/GUI action).

        Requests a version name from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("doOpenNewDBPBibleResourceBox()") )
            self.parentApp.setDebugText( "doOpenNewDBPBibleResourceBox…" )

        if self.parentApp.internetAccessEnabled:
            self.parentApp.setWaitStatus( _("doOpenNewDBPBibleResourceBox…") )
            if self.parentApp.DBPInterface is None:
                try: self.parentApp.DBPInterface = DBPBibles()
                except FileNotFoundError: # probably the key file wasn't found
                    showError( self, APP_NAME, _("Sorry, the Digital Bible Platform requires a special key file") )
                    return

                availableVolumes = self.parentApp.DBPInterface.fetchAllEnglishTextVolumes()
                #print( "aV1", repr(availableVolumes) )
                if availableVolumes:
                    srb = SelectResourceBoxDialog( self, [(x,y) for x,y in availableVolumes.items()], title=_('Open DBP resource') )
                    #print( "srbResult", repr(srb.result) )
                    if srb.result:
                        for entry in srb.result:
                            self.openDBPBibleResourceBox( entry[1] )
                        #self.acceptNewBnCV()
                        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
                    elif BibleOrgSysGlobals.debugFlag: print( _("doOpenNewDBPBibleResourceBox: no resource selected!") )
                else:
                    logging.critical( _("doOpenNewDBPBibleResourceBox: no volumes available") )
                    self.parentApp.setStatus( "Digital Bible Platform unavailable (offline?)" )
        else: # no Internet allowed
            logging.critical( _("doOpenNewDBPBibleResourceBox: Internet not enabled") )
            self.parentApp.setStatus( "Digital Bible Platform unavailable (You have disabled Internet access.)" )

        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished doOpenNewDBPBibleResourceBox" )
    # end of BibleResourceCollectionWindow.doOpenNewDBPBibleResourceBox

    def openDBPBibleResourceBox( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested DBP Bible resource window.

        Returns the new DBPBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("openDBPBibleResourceBox()") )
            self.parentApp.setDebugText( "openDBPBibleResourceBox…" )
            assert moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6
        #tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        dBRB = DBPBibleResourceBox( self, moduleAbbreviation )
        if windowGeometry: halt; dBRB.geometry( windowGeometry )
        if dBRB.DBPModule is None:
            logging.critical( _("Application.openDBPBibleResourceBox: Unable to open resource {}").format( repr(moduleAbbreviation) ) )
            dBRB.destroy()
            showError( self, APP_NAME, _("Sorry, unable to open DBP resource") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openDBPBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return None
        else:
            dBRB.updateShownBCV( self.parentApp.getVerseKey( self._groupCode ) )
            self.resourceBoxesList.append( dBRB )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openDBPBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return dBRB
    # end of BibleResourceCollectionWindow.openDBPBibleResourceBox


    def doOpenNewSwordResourceBox( self ):
        """
        Open a local Sword Bible (called from a menu/GUI action).

        Requests a module abbreviation from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("openSwordResource()") )
            self.parentApp.setDebugText( "doOpenNewSwordResourceBox…" )
        self.parentApp.setWaitStatus( _("doOpenNewSwordResourceBox…") )
        if self.parentApp.SwordInterface is None and SwordType is not None:
            self.parentApp.SwordInterface = SwordInterface() # Load the Sword library
        if self.parentApp.SwordInterface is None: # still
            logging.critical( _("doOpenNewSwordResourceBox: no Sword interface available") )
            showError( self, APP_NAME, _("Sorry, no Sword interface discovered") )
            return

        givenDupleList = self.parentApp.SwordInterface.getAvailableModuleCodeDuples( ['Biblical Texts','Commentaries'] )

        #print( 'givenDupleList', givenDupleList )
        genericName = { 'Biblical Texts':'Bible', 'Commentaries':'Commentary' }
        try: ourList = ['{} ({})'.format(moduleRoughName,genericName[moduleType]) for moduleRoughName,moduleType in givenDupleList]
        except TypeError: ourList = None
        if BibleOrgSysGlobals.debugFlag: print( "{} Sword module codes available".format( len(ourList) ) )
        #print( "ourList", ourList )
        if ourList:
            srb = SelectResourceBoxDialog( self, ourList, title=_("Open Sword resource") )
            print( "srbResult", repr(srb.result) )
            if srb.result:
                for entryString in srb.result:
                    requestedModuleName, rest = entryString.split( ' (', 1 )
                    self.parentApp.setWaitStatus( _("Loading {!r} Sword module…").format( requestedModuleName ) )
                    self.openSwordBibleResourceBox( requestedModuleName )
                    self.parentApp.addRecentFile( (requestedModuleName,'','SwordBibleResourceBox') )
                #self.acceptNewBnCV()
                #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
            elif BibleOrgSysGlobals.debugFlag: print( _("doOpenNewSwordResourceBox: no resource selected!") )
        else:
            logging.critical( _("doOpenNewSwordResourceBox: no list available") )
            showError( self, APP_NAME, _("No Sword resources discovered") )
    # end of BibleResourceCollectionWindow.doOpenNewSwordResourceBox

    def openSwordBibleResourceBox( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested Sword Bible resource window.

        Returns the new SwordBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("openSwordBibleResourceBox()") )
            self.parentApp.setDebugText( "openSwordBibleResourceBox…" )
        if self.parentApp.SwordInterface is None:
            self.parentApp.SwordInterface = SwordInterface() # Load the Sword library
        #tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        swBRB = SwordBibleResourceBox( self, moduleAbbreviation )
        if windowGeometry: halt; swBRB.geometry( windowGeometry )
        swBRB.updateShownBCV( self.parentApp.getVerseKey( self._groupCode ) )
        self.resourceBoxesList.append( swBRB )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openSwordBibleResourceBox" )
        self.parentApp.setReadyStatus()
        return swBRB
    # end of BibleResourceCollectionWindow.openSwordBibleResourceBox


    def doOpenNewBOSBibleResourceBox( self ):
        """
        Open a local pickled Bible (called from a menu/GUI action).

        NOTE: This may include a Hebrew interlinear window which has to be treated different.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("doOpenNewBOSBibleResourceBox()") )
            self.parentApp.setDebugText( "doOpenNewBOSBibleResourceBox" )
        self.parentApp.setWaitStatus( _("doOpenNewBOSBibleResourceBox…") )

        # Get the info about available resources to display to the user
        infoDictList = getZippedPickledBiblesDetails( BibleOrgSysGlobals.DEFAULT_WRITEABLE_DOWNLOADED_RESOURCES_FOLDERPATH, extended=True )
        crd = ChooseResourcesDialog( self, infoDictList, title=_("Select resource(s)") )
        if not crd.result:
            self.parentApp.setReadyStatus()
            return
        assert isinstance( crd.result, list ) # Should be a list of zip files
        for zipFilename in crd.result:
            assert zipFilename.endswith( ZIPPED_PICKLE_FILENAME_END )
            zipFilepath = BibleOrgSysGlobals.DEFAULT_WRITEABLE_DOWNLOADED_RESOURCES_FOLDERPATH.joinpath( zipFilename )
            assert os.path.isfile( zipFilepath )
            #if '/WLC.' in zipFilepath: self.openHebrewBibleResourceBox( zipFilepath )
            self.openInternalBibleResourceBox( zipFilepath )
    # end of Application.doOpenNewBOSBibleResourceWindow


    def doOpenNewInternalBibleResourceBox( self ):
        """
        Open a local Bible (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("doOpenNewInternalBibleResourceBox()") )
            self.parentApp.setDebugText( "doOpenNewInternalBibleResourceBox…" )
        self.parentApp.setWaitStatus( _("doOpenNewInternalBibleResourceBox…") )

        #requestedFolder = askdirectory()
        openDialog = Directory( initialdir=self.parentApp.lastInternalBibleDir, parent=self )
        requestedFolder = openDialog.show()
        if requestedFolder:
            self.parentApp.lastInternalBibleDir = requestedFolder
            self.openInternalBibleResourceBox( requestedFolder )
            #self.acceptNewBnCV()
            #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of BibleResourceCollectionWindow.doOpenNewInternalBibleResourceBox

    def openInternalBibleResourceBox( self, modulePath, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible resource window.

        Returns the new InternalBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("openInternalBibleResourceBox()") )
            self.parentApp.setDebugText( "openInternalBibleResourceBox…" )

        #tk.Label( self, text=modulePath ).pack( side=tk.TOP, fill=tk.X )
        iBRB = InternalBibleResourceBox( self, modulePath )
        if windowGeometry: halt; iBRB.geometry( windowGeometry )
        if iBRB.internalBible is None:
            logging.critical( _("Application.openInternalBibleResourceBox: Unable to open resource {}").format( repr(modulePath) ) )
            iBRB.destroy()
            showError( self, APP_NAME, _("Sorry, unable to open internal Bible resource") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openInternalBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return None
        else:
            iBRB.updateShownBCV( self.parentApp.getVerseKey( self._groupCode ) )
            self.resourceBoxesList.append( iBRB )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openInternalBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return iBRB
    # end of BibleResourceCollectionWindow.openInternalBibleResourceBox


    #def openHebrewBibleResourceBox( self, modulePath, windowGeometry=None ):
        #"""
        #Create the actual requested local/internal Hebrew Bible resource window.

        #Returns the new HebrewBibleResourceBox object.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("openHebrewBibleResourceBox()") )
            #self.parentApp.setDebugText( "openHebrewBibleResourceBox" )

        ##tk.Label( self, text=modulePath ).pack( side=tk.TOP, fill=tk.X )
        #iBRB = HebrewBibleResourceBox( self, modulePath )
        #if windowGeometry: halt; iBRB.geometry( windowGeometry )
        #if iBRB.internalBible is None:
            #logging.critical( _("Application.openHebrewBibleResourceBox: Unable to open resource {}").format( repr(modulePath) ) )
            #iBRB.destroy()
            #showError( self, APP_NAME, _("Sorry, unable to open internal Bible resource") )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openHebrewBibleResourceBox" )
            #self.parentApp.setReadyStatus()
            #return None
        #else:
            #iBRB.updateShownBCV( self.parentApp.getVerseKey( self._groupCode ) )
            #self.resourceBoxesList.append( iBRB )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openHebrewBibleResourceBox" )
            #self.parentApp.setReadyStatus()
            #return iBRB
    ## end of BibleResourceCollectionWindow.openHebrewBibleResourceBox


    def openBox( self, boxType, boxSource ):
        """
        A general function to (re)open a text box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceCollectionWindow.openBox( {}, {} )").format( boxType, boxSource ) )

        if boxType == 'DBP': self.openDBPBibleResourceBox( boxSource )
        elif boxType == 'Sword': self.openSwordBibleResourceBox( boxSource )
        elif boxType == 'Internal': self.openInternalBibleResourceBox( boxSource )
        elif BibleOrgSysGlobals.debugFlag: halt
    # end of BibleResourceCollectionWindow.openBox


    def updateShownBCV( self, newReferenceVerseKey, originator=None ):
        """
        Updates the resource boxes in various ways depending on the contextViewMode held by the enclosing window.

        The new verse key is in the reference versification system.

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceCollectionWindow.updateShownBCV( {}, {} ) for {}").format( newReferenceVerseKey, originator, self.moduleID ) )
            #print( "contextViewMode", self._contextViewMode )
            assert isinstance( newReferenceVerseKey, SimpleVerseKey )

        #refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
        #BBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
        #newVerseKey = SimpleVerseKey( BBB, C, V, S )
        self.setCurrentVerseKey( newReferenceVerseKey )

        for resourceBox in self.resourceBoxesList:
            resourceBox.updateShownBCV( newReferenceVerseKey )

        self.refreshTitle()
    # end of BibleResourceCollectionWindow.updateShownBCV


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceCollectionWindow.doShowInfo( {} )").format( event ) )

        infoString = 'BibleResourceCollectionWindow:\n  Name:\t{}\n'.format( self.moduleID )
        for j, resourceBox in enumerate( self.resourceBoxesList ):
            infoString += '\nType{}:\t{}'.format( j+1, resourceBox.boxType ) \
                 + '\nName{}:\t{}'.format( j+1, resourceBox.moduleID )
        showInfo( self, 'Window Information', infoString )
    # end of BibleResourceCollectionWindow.doShowInfo


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceCollectionWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return tkBREAK # so we don't do the main window help also
    # end of BibleResourceCollectionWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("BibleResourceCollectionWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = programNameVersion + '\n'
        aboutInfo += '\n' + _("Information about {}").format( self.windowType ) + '\n'
        aboutInfo += '\n' + _("A Bible Resource Collection box can contain multiple different resource translations or commentaries, all showing the same Scripture reference.") + '\n'
        aboutInfo += '\n' + _("Use this window's Resources menu to add a/another resource to the window. Use the up and down arrows to order the resources within the window.")
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return tkBREAK # so we don't do the main window about also
    # end of BibleResourceCollectionWindow.doAbout
# end of BibleResourceCollectionWindow class



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
# end of BibleResourceCollection.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BibleResourceCollection.py
