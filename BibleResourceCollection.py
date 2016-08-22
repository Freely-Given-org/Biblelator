#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BibleResourceCollection.py
#
# Bible resource collection for Biblelator Bible display/editing
#
# Copyright (C) 2014-2016 Robert Hunt
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
Boxes, Frames, and Windows to allow display and manipulation of
    (non-editable) Bible resource collection windows.

A Bible resource collection is a collection of different Bible resources
    all displaying the same reference.

class BibleResourceBox( Frame, BibleBox )
    __init__( self, parentWindow, boxType, moduleID )
    createStandardKeyboardBindings( self )
    gotoBCV( self, BBB, C, V )
    getSwordVerseKey( self, verseKey )
    getCachedVerseData( self, verseKey )
    #BibleResourceBoxXXXdisplayAppendVerse( self, firstFlag, verseKey, verseContextData, currentVerse=False )
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
class BibleResourceBoxes( list )
    __init__( self, resourceBoxesParent )
class BibleResourceCollectionWindow( BibleResourceWindow )
    __init__( self, parentApp, collectionName )
    createMenuBar( self )
    refreshTitle( self )
    doRename( self )
    doOpenDBPBibleResourceBox( self )
    openDBPBibleResourceBox( self, moduleAbbreviation, windowGeometry=None )
    doOpenSwordResourceBox( self )
    openSwordBibleResourceBox( self, moduleAbbreviation, windowGeometry=None )
    doOpenInternalBibleResourceBox( self )
    openInternalBibleResourceBox( self, modulePath, windowGeometry=None )
    openBox( self, boxType, boxSource )
    updateShownBCV( self, newReferenceVerseKey, originator=None )
    doHelp( self, event=None )
    doAbout( self, event=None )
"""

from gettext import gettext as _

LastModifiedDate = '2016-08-21' # by RJH
ShortProgName = "BibleResourceCollection"
ProgName = "Biblelator Bible Resource Collection"
ProgVersion = '0.38'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import logging
from collections import OrderedDict

import tkinter as tk
from tkinter.filedialog import Directory #, SaveAs
from tkinter.ttk import Frame, Button, Scrollbar

# Biblelator imports
from BiblelatorGlobals import APP_NAME, DEFAULT, BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, BIBLE_FORMAT_VIEW_MODES, \
                INITIAL_RESOURCE_COLLECTION_SIZE, MINIMUM_RESOURCE_COLLECTION_SIZE, MAXIMUM_RESOURCE_COLLECTION_SIZE, \
                MAX_PSEUDOVERSES, parseWindowSize
from BiblelatorDialogs import showerror, showinfo, SelectResourceBoxDialog, RenameResourceCollectionDialog
from BibleResourceWindows import BibleResourceWindow
from TextBoxes import BibleBox
from BiblelatorHelpers import handleInternalBibles

# BibleOrgSys imports
#if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
from Bible import Bible
from VerseReferences import SimpleVerseKey
from DigitalBiblePlatform import DBPBibles, DBPBible
from SwordResources import SwordType, SwordInterface
from UnknownBible import UnknownBible
from BibleOrganizationalSystems import BibleOrganizationalSystem


MAX_CACHED_VERSES = 30 # Per Bible resource window



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



class BibleResourceBox( Frame, BibleBox ):
    """
    A base class to provide the boxes for a BibleResourceCollectionWindow

    The moduleID can be a name, abbreviation or folder (depending on the boxType)

    The subclass must provide a getContextVerseData function.
    """
    def __init__( self, parentWindow, boxType, moduleID ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: print( exp("BibleResourceBox.__init__( {}, {}, {} )").format( parentWindow, boxType, moduleID ) )
        self.parentWindow, self.boxType, self.moduleID = parentWindow, boxType, moduleID
        self.parentApp = self.parentWindow.parentApp
        Frame.__init__( self, parentWindow )
        BibleBox.__init__( self, self.parentApp )

        # Create a title bar frame
        titleBar = Frame( self )
        Button( titleBar, text=_('Close'), width=5, command=self.doClose ).pack( side=tk.RIGHT )
        # Try to get the title width somewhere near correct (if moduleID is a long path)
        adjModuleID = moduleID
        self.update() # so we can get the geometry
        width = parseWindowSize( self.parentWindow.winfo_geometry() )[0] - 60 # Allow for above button
        if len(adjModuleID)*10 > width: # Note: this doesn't adjust if the window size is changed
            #print( "BRB here1", len(adjModuleID), width, repr(adjModuleID) )
            x = len(adjModuleID)*100/width # not perfect (too small) for narrow windows
            adjModuleID = '…' + adjModuleID[int(x):]
            #print( "BRB here2", len(adjModuleID), x, repr(adjModuleID) )
        titleText = '{} ({})'.format( adjModuleID, boxType.replace( 'BibleResourceBox', '' ) )
        self.titleLabel = tk.Label( titleBar, text=titleText )
        self.titleLabel.pack( side=tk.TOP, fill=tk.X )
        titleBar.pack( side=tk.TOP, fill=tk.X )

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        self.textBox = tk.Text( self, height=1, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox.configure( wrap='word' )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardKeyboardBindings()
        self.textBox.bind( '<Button-1>', self.setFocus ) # So disabled text box can still do select and copy functions

        # Set-up our standard Bible styles
        for USFMKey, styleDict in self.parentApp.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        # Add our extra specialised styles
        self.textBox.tag_configure( 'contextHeader', background='pink', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'context', background='pink', font='helvetica 6' )

        self.pack( expand=tk.YES, fill=tk.BOTH ) # Pack the frame

        # Set-up our default Bible system and our callables
        self.BibleOrganisationalSystem = BibleOrganizationalSystem( 'GENERIC-KJV-81-ENG' ) # temp
        self.getNumChapters = self.BibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda b,c: MAX_PSEUDOVERSES if c=='0' or c==0 \
                                        else self.BibleOrganisationalSystem.getNumVerses( b, c )
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


    def createStandardKeyboardBindings( self ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceBox.createStandardKeyboardBindings()") )
        for name,command in ( ('SelectAll',self.doSelectAll), ('Copy',self.doCopy),
                             ('Find',self.doWindowFind), ('Refind',self.doWindowRefind),
                             ('Info',self.doShowInfo), ('Close',self.doClose), ):
            self._createStandardKeyboardBinding( name, command )
    # end of BibleResourceBox.createStandardKeyboardBindings()


    #def gotoBCV( self, BBB, C, V ):
        #"""

        #"""
        #if BibleOrgSysGlobals.debugFlag: print( exp("BibleResourceBox.gotoBCV( {} {}:{} from {} )").format( BBB, C, V, self.currentVerseKey ) )
        ## We really need to convert versification systems here
        #adjBBB, adjC, adjV, adjS = self.BibleOrganisationalSystem.convertToReferenceVersification( BBB, C, V )
        #self.parentWindow.gotoGroupBCV( self._groupCode, adjBBB, adjC, adjV ) # then the App will update me by calling updateShownBCV
    ## end of BibleResourceBox.gotoBCV


    def getSwordVerseKey( self, verseKey ):
        """
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("getSwordVerseKey( {} )").format( verseKey ) )
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
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("getCachedVerseData( {} )").format( verseKey ) )
        verseKeyHash = verseKey.makeHash()
        if verseKeyHash in self.verseCache:
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  " + exp("Retrieved from BibleResourceBox cache") )
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
            print( exp("BibleResourceBox.setCurrentVerseKey( {} )").format( newVerseKey ) )
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
            print( exp("updateShownBCV: Safety-check converted {} contextViewMode for DBP").format( repr(self.parentWindow._contextViewMode) ) )
            self.parentWindow._contextViewRadioVar.set( 3 ) # ByVerse
            self.parentWindow.changeBibleContextView()

        if self.parentWindow._contextViewMode == 'BeforeAndAfter':
            bibleData = self.getBeforeAndAfterBibleData( newVerseKey )
            if bibleData:
                verseData, previousVerses, nextVerses = bibleData
                for verseKey,previousVerseData in previousVerses:
                    self.displayAppendVerse( startingFlag, verseKey, previousVerseData )
                    startingFlag = False
                self.displayAppendVerse( startingFlag, newVerseKey, verseData, currentVerse=True )
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
            self.displayAppendVerse( True, newVerseKey, cachedVerseData, currentVerse=True )

        #elif self.parentWindow._contextViewMode == 'BySection':
            #self.displayAppendVerse( True, newVerseKey, self.getCachedVerseData( newVerseKey ), currentVerse=True )
            #BBB, C, V = newVerseKey.getBCV()
            #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            #print( "\nBySection is not finished yet -- just shows a single verse!\n" ) # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            ##for thisC in range( 0, self.getNumChapters( BBB ) ):
                ##try: numVerses = self.getNumVerses( BBB, thisC )
                ##except KeyError: numVerses = 0
                ##for thisV in range( 0, numVerses ):
                    ##thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    ##thisVerseData = self.getCachedVerseData( thisVerseKey )
                    ##self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            ##currentVerse=thisC==intC and thisV==intV )
                    ##startingFlag = False

        #elif self.parentWindow._contextViewMode == 'ByBook':
            #BBB, C, V = newVerseKey.getBCV()
            #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            #for thisC in range( 0, self.getNumChapters( BBB ) + 1 ):
                #try: numVerses = self.getNumVerses( BBB, thisC )
                #except KeyError: numVerses = 0
                #for thisV in range( 0, numVerses ):
                    #thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    #thisVerseData = self.getCachedVerseData( thisVerseKey )
                    #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            #currentVerse=thisC==intC and thisV==intV )
                    #startingFlag = False

        #elif self.parentWindow._contextViewMode == 'ByChapter':
            #BBB, C, V = newVerseKey.getBCV()
            #intV = newVerseKey.getVerseNumberInt()
            #try: numVerses = self.getNumVerses( BBB, C )
            #except KeyError: numVerses = 0
            #for thisV in range( 0, numVerses + 1 ):
                #thisVerseKey = SimpleVerseKey( BBB, C, thisV )
                #thisVerseData = self.getCachedVerseData( thisVerseKey )
                #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData, currentVerse=thisV==intV )
                #startingFlag = False

        else:
            logging.critical( exp("BibleResourceBox.updateShownBCV: Bad context view mode {}").format( self.parentWindow._contextViewMode ) )
            if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode

        self.textBox.configure( state=tk.DISABLED ) # Don't allow editing

        # Make sure we can see what we're supposed to be looking at
        desiredMark = 'C{}V{}'.format( newVerseKey.getChapterNumber(), newVerseKey.getVerseNumber() )
        try: self.textBox.see( desiredMark )
        except tk.TclError: print( exp("USFMEditWindow.updateShownBCV couldn't find {}").format( repr( desiredMark ) ) )
        self.lastCVMark = desiredMark
    # end of BibleResourceBox.updateShownBCV


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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleResourceBox.closeResourceBox()") )
        if self in self.parentWindow.resourceBoxes:
            self.parentWindow.resourceBoxes.remove( self )
            self.destroy()
        else: # we might not have finished making our box yet
            if BibleOrgSysGlobals.debugFlag:
                print( exp("BibleResourceBox.closeResourceBox() for {} wasn't in list").format( self.windowType ) )
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
            logging.error( exp("SwordBibleResourceBox.__init__ Unable to open Sword module: {}").format( self.moduleAbbreviation ) )
            self.SwordModule = None
        if isinstance( self.SwordModule, Bible ):
            #print( "Handle internalBible for SwordModule" )
            handleInternalBibles( self.parentApp, self.SwordModule, self )
        else: print( "SwordModule is", self.SwordModule )
    # end of SwordBibleResourceBox.__init__


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("SwordBibleResourceBox.getContextVerseData( {} )").format( verseKey ) )
        if self.SwordModule is not None:
            if verseKey.getChapterNumber()!='0' and verseKey.getVerseNumber()!='0': # not sure how to get introductions, etc.
                SwordKey = self.getSwordVerseKey( verseKey )
                rawContextInternalBibleData = self.parentApp.SwordInterface.getContextVerseData( self.SwordModule, SwordKey )
                rawInternalBibleData, context = rawContextInternalBibleData
                # Clean up the data -- not sure that it should be done here! ....... XXXXXXXXXXXXXXXXXXX
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
            logging.error( exp("DBPBibleResourceBox.__init__ Unable to find a key to connect to Digital Bible Platform") )
            self.DBPModule = None
        except ConnectionError:
            logging.error( exp("DBPBibleResourceBox.__init__ Unable to connect to Digital Bible Platform") )
            self.DBPModule = None
        if isinstance( self.DBPModule, Bible ):
            #print( "Handle internalBible for DBPModule" )
            handleInternalBibles( self.parentApp, self.DBPModule, self )
        else: print( "DBPModule is", self.DBPModule )
    # end of DBPBibleResourceBox.__init__


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("DBPBibleResourceBox.getContextVerseData( {} )").format( verseKey ) )

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
            logging.error( exp("InternalBibleResourceBox.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
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
            print( exp("InternalBibleResourceBox.getContextVerseData( {} )").format( verseKey ) )

        if self.internalBible is not None:
            try: return self.internalBible.getContextVerseData( verseKey )
            except KeyError: # Could be after a verse-bridge ???
                if verseKey.getChapterNumber() != '0':
                    logging.error( exp("InternalBibleResourceBox.getContextVerseData for {} {} got a KeyError") \
                                                                .format( self.boxType, verseKey ) )
    # end of InternalBibleResourceBox.getContextVerseData
# end of InternalBibleResourceBox class



class BibleResourceBoxes( list ):
    """
    Just keeps a list of the resource (Text) boxes.
    """
    def __init__( self, resourceBoxesParent ):
        self.resourceBoxesParent = resourceBoxesParent
        list.__init__( self )
    # end of BibleResourceBoxes.__init__
# end of BibleResourceBoxes class



class BibleResourceCollectionWindow( BibleResourceWindow ):
    """
    """
    def __init__( self, parentApp, collectionName, defaultContextViewMode=BIBLE_CONTEXT_VIEW_MODES[0], defaultFormatViewMode=BIBLE_FORMAT_VIEW_MODES[0] ):
        """
        Given a collection name, try to open an empty Bible resource collection window.
        """
        if BibleOrgSysGlobals.debugFlag: print( "BibleResourceCollectionWindow.__init__( {}, {} )".format( parentApp, collectionName ) )
        self.parentApp = parentApp
        BibleResourceWindow.__init__( self, parentApp, 'BibleResourceCollectionWindow', collectionName, defaultContextViewMode, defaultFormatViewMode )
        #ChildWindow.__init__( self, self.parentApp, 'BibleResource' )
        #self.windowType = 'InternalBibleResourceBox'

        self.geometry( INITIAL_RESOURCE_COLLECTION_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_RESOURCE_COLLECTION_SIZE, MAXIMUM_RESOURCE_COLLECTION_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        # Get rid of the default widgets
        self.vScrollbar.destroy()
        self.textBox.destroy()

        self.viewVersesBefore, self.viewVersesAfter = 1, 1

        self.resourceBoxes = BibleResourceBoxes( self )
    # end of BibleResourceCollectionWindow.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleResourceBox.createMenuBar()") )
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

        if 0:
            editMenu = tk.Menu( self.menubar )
            self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
            editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
            editMenu.add_separator()
            editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )

            searchMenu = tk.Menu( self.menubar )
            self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
            searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=self.parentApp.keyBindingDict[_('Line')][0] )
            searchMenu.add_separator()
            searchMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
            searchMenu.add_command( label=_('Find again'), underline=5, command=self.doWindowRefind, accelerator=self.parentApp.keyBindingDict[_('Refind')][0] )

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
        resourcesMenu.add_command( label=_('Online (DBP)…'), underline=0, command=self.doOpenDBPBibleResourceBox )
        resourcesMenu.add_command( label=_('Sword module…'), underline=0, command=self.doOpenSwordResourceBox )
        resourcesMenu.add_command( label=_('Other (local)…'), underline=1, command=self.doOpenInternalBibleResourceBox )

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
            print( exp("doRename()") )
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


    def doOpenDBPBibleResourceBox( self ):
        """
        Open an online DigitalBiblePlatform Bible (called from a menu/GUI action).

        Requests a version name from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doOpenDBPBibleResourceBox()") )
            self.parentApp.setDebugText( "doOpenDBPBibleResourceBox…" )

        if self.parentApp.internetAccessEnabled:
            self.parentApp.setWaitStatus( "doOpenDBPBibleResourceBox…" )
            if self.parentApp.DBPInterface is None:
                try: self.parentApp.DBPInterface = DBPBibles()
                except FileNotFoundError: # probably the key file wasn't found
                    showerror( self, APP_NAME, _("Sorry, the Digital Bible Platform requires a special key file") )
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
                    elif BibleOrgSysGlobals.debugFlag: print( exp("doOpenDBPBibleResourceBox: no resource selected!") )
                else:
                    logging.critical( exp("doOpenDBPBibleResourceBox: no volumes available") )
                    self.parentApp.setStatus( "Digital Bible Platform unavailable (offline?)" )
        else: # no Internet allowed
            logging.critical( exp("doOpenDBPBibleResourceBox: Internet not enabled") )
            self.parentApp.setStatus( "Digital Bible Platform unavailable (You have disabled Internet access.)" )

        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished doOpenDBPBibleResourceBox" )
    # end of BibleResourceCollectionWindow.doOpenDBPBibleResourceBox

    def openDBPBibleResourceBox( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested DBP Bible resource window.

        Returns the new DBPBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openDBPBibleResourceBox()") )
            self.parentApp.setDebugText( "openDBPBibleResourceBox…" )
            assert moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6
        #tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        dBRB = DBPBibleResourceBox( self, moduleAbbreviation )
        if windowGeometry: halt; dBRB.geometry( windowGeometry )
        if dBRB.DBPModule is None:
            logging.critical( exp("Application.openDBPBibleResourceBox: Unable to open resource {}").format( repr(moduleAbbreviation) ) )
            dBRB.destroy()
            showerror( self, APP_NAME, _("Sorry, unable to open DBP resource") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openDBPBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return None
        else:
            dBRB.updateShownBCV( self.parentApp.getVerseKey( self._groupCode ) )
            self.resourceBoxes.append( dBRB )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openDBPBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return dBRB
    # end of BibleResourceCollectionWindow.openDBPBibleResourceBox


    def doOpenSwordResourceBox( self ):
        """
        Open a local Sword Bible (called from a menu/GUI action).

        Requests a module abbreviation from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openSwordResource()") )
            self.parentApp.setDebugText( "doOpenSwordResourceBox…" )
        self.parentApp.setWaitStatus( "doOpenSwordResourceBox…" )
        if self.parentApp.SwordInterface is None and SwordType is not None:
            self.parentApp.SwordInterface = SwordInterface() # Load the Sword library
        if self.parentApp.SwordInterface is None: # still
            logging.critical( exp("doOpenSwordResourceBox: no Sword interface available") )
            showerror( self, APP_NAME, _("Sorry, no Sword interface discovered") )
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
            elif BibleOrgSysGlobals.debugFlag: print( exp("doOpenSwordResourceBox: no resource selected!") )
        else:
            logging.critical( exp("doOpenSwordResourceBox: no list available") )
            showerror( self, APP_NAME, _("No Sword resources discovered") )

        ## Old code
        #availableModules = self.parentApp.SwordInterface.library
        ##print( "aM1", availableModules )
        #ourList = None
        #if availableModules is not None:
            #ourList = availableModules.getAvailableModuleCodes()
        ##print( "ourList", ourList )
        #if ourList:
            #srb = SelectResourceBoxDialog( self, ourList, title=_("Open Sword resource") )
            ##print( "srbResult", repr(srb.result) )
            #if srb.result:
                #for entry in srb.result:
                    #self.parentApp.setWaitStatus( _("Loading {} Sword module…").format( repr(entry) ) )
                    #self.openSwordBibleResourceBox( entry )
                ##self.acceptNewBnCV()
                ##self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
            #elif BibleOrgSysGlobals.debugFlag: print( exp("doOpenSwordResourceBox: no resource selected!") )
        #else:
            #logging.critical( exp("doOpenSwordResourceBox: no list available") )
            #showerror( self, APP_NAME, _("No Sword resources discovered") )
        ##self.acceptNewBnCV()
        ##self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of BibleResourceCollectionWindow.doOpenSwordResourceBox

    def openSwordBibleResourceBox( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested Sword Bible resource window.

        Returns the new SwordBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openSwordBibleResourceBox()") )
            self.parentApp.setDebugText( "openSwordBibleResourceBox…" )
        if self.parentApp.SwordInterface is None:
            self.parentApp.SwordInterface = SwordInterface() # Load the Sword library
        #tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        swBRB = SwordBibleResourceBox( self, moduleAbbreviation )
        if windowGeometry: halt; swBRB.geometry( windowGeometry )
        swBRB.updateShownBCV( self.parentApp.getVerseKey( self._groupCode ) )
        self.resourceBoxes.append( swBRB )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openSwordBibleResourceBox" )
        self.parentApp.setReadyStatus()
        return swBRB
    # end of BibleResourceCollectionWindow.openSwordBibleResourceBox


    def doOpenInternalBibleResourceBox( self ):
        """
        Open a local Bible (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openInternalBibleResource()") )
            self.parentApp.setDebugText( "doOpenInternalBibleResourceBox…" )
        self.parentApp.setWaitStatus( "doOpenInternalBibleResourceBox…" )

        #requestedFolder = askdirectory()
        openDialog = Directory( initialdir=self.parentApp.lastInternalBibleDir, parent=self )
        requestedFolder = openDialog.show()
        if requestedFolder:
            self.parentApp.lastInternalBibleDir = requestedFolder
            self.openInternalBibleResourceBox( requestedFolder )
            #self.acceptNewBnCV()
            #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of BibleResourceCollectionWindow.doOpenInternalBibleResourceBox

    def openInternalBibleResourceBox( self, modulePath, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible resource window.

        Returns the new InternalBibleResourceBox object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openInternalBibleResourceBox()") )
            self.parentApp.setDebugText( "openInternalBibleResourceBox…" )

        #tk.Label( self, text=modulePath ).pack( side=tk.TOP, fill=tk.X )
        iBRB = InternalBibleResourceBox( self, modulePath )
        if windowGeometry: halt; iBRB.geometry( windowGeometry )
        if iBRB.internalBible is None:
            logging.critical( exp("Application.openInternalBibleResourceBox: Unable to open resource {}").format( repr(modulePath) ) )
            iBRB.destroy()
            showerror( self, APP_NAME, _("Sorry, unable to open internal Bible resource") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openInternalBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return None
        else:
            iBRB.updateShownBCV( self.parentApp.getVerseKey( self._groupCode ) )
            self.resourceBoxes.append( iBRB )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openInternalBibleResourceBox" )
            self.parentApp.setReadyStatus()
            return iBRB
    # end of BibleResourceCollectionWindow.openInternalBibleResourceBox


    def openBox( self, boxType, boxSource ):
        """
        (Re)open a text box.
        """
        if boxType == 'DBP': self.openDBPBibleResourceBox( boxSource )
        elif boxType == 'Sword': self.openSwordBibleResourceBox( boxSource )
        elif boxType == 'Internal': self.openInternalBibleResourceBox( boxSource )
        elif BibleOrgSysGlobals.debugFlag: halt
    # end of BibleResourceCollectionWindow.openBox


    def updateShownBCV( self, newReferenceVerseKey, originator=None ):
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        The new verse key is in the reference versification system.

        Leaves the textbox in the disabled state.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceCollectionWindow.updateShownBCV( {}, {} ) for {}").format( newReferenceVerseKey, originator, self.moduleID ) )
            #print( "contextViewMode", self._contextViewMode )
            assert isinstance( newReferenceVerseKey, SimpleVerseKey )

        #refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
        #BBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
        #newVerseKey = SimpleVerseKey( BBB, C, V, S )
        self.setCurrentVerseKey( newReferenceVerseKey )

        for resourceBox in self.resourceBoxes:
            resourceBox.updateShownBCV( newReferenceVerseKey )

        self.refreshTitle()
    # end of BibleResourceCollectionWindow.updateShownBCV


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceCollectionWindow.doShowInfo( {} )").format( event ) )

        infoString = 'BibleResourceCollectionWindow:\n  Name:\t{}\n'.format( self.moduleID )
        for j, resourceBox in enumerate( self.resourceBoxes ):
            infoString += '\nType{}:\t{}'.format( j+1, resourceBox.boxType ) \
                 + '\nName{}:\t{}'.format( j+1, resourceBox.moduleID )
        showinfo( self, 'Window Information', infoString )
    # end of BibleResourceCollectionWindow.doShowInfo


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceCollectionWindow.doHelp( {} )").format( event ) )
        from Help import HelpBox

        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.windowType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of BibleResourceCollectionWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleResourceCollectionWindow.doAbout( {} )").format( event ) )
        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of BibleResourceCollectionWindow.doAbout
# end of BibleResourceCollectionWindow class



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
# end of BibleResourceCollection.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    import sys
    if 'win' in sys.platform: # Convert stdout so we don't get zillions of UnicodeEncodeErrors
        from io import TextIOWrapper
        sys.stdout = TextIOWrapper( sys.stdout.detach(), sys.stdout.encoding, 'namereplace' if sys.version_info >= (3,5) else 'backslashreplace' )

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BibleResourceCollection.py