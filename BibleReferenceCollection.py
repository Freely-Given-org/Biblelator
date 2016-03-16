#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleReferenceCollection.py
#
# Bible reference collection for Biblelator Bible display/editing
#
# Copyright (C) 2015-2016 Robert Hunt
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
    (non-editable) Bible reference collection windows.

A Bible reference collection is a collection of different Bible references
    all displaying from the same resource (or project).
"""

from gettext import gettext as _

LastModifiedDate = '2016-03-16' # by RJH
ShortProgName = "BibleReferenceCollection"
ProgName = "Biblelator Bible Reference Collection"
ProgVersion = '0.30'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import logging
from collections import OrderedDict

import tkinter as tk
#from tkinter.filedialog import Open  #, SaveAs
from tkinter.ttk import Frame, Button, Scrollbar

# Biblelator imports
from BiblelatorGlobals import DEFAULT, BIBLE_GROUP_CODES, \
                INITIAL_REFERENCE_COLLECTION_SIZE, MINIMUM_REFERENCE_COLLECTION_SIZE, MAXIMUM_REFERENCE_COLLECTION_SIZE, \
                parseWindowSize
#from BiblelatorDialogs import showerror #, showwarning, showinfo, errorBeep
from BiblelatorHelpers import mapReferencesVerseKey
from BibleResourceWindows import BibleBox, BibleResourceWindow

# BibleOrgSys imports
#sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
from VerseReferences import SimpleVerseKey, SimpleVersesKey, VerseRangeKey, FlexibleVersesKey
#from DigitalBiblePlatform import DBPBibles, DBPBible
#from SwordResources import SwordType, SwordInterface
#from UnknownBible import UnknownBible
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



class BibleReferenceBox( Frame, BibleBox ):
    """
    """
    def __init__( self, parentWindow, parentApp, internalBible, referenceObject ):
        if BibleOrgSysGlobals.debugFlag: print( exp("BibleReferenceBox.__init__( {}, {}, {}, {} )").format( parentWindow, parentApp, internalBible.name, referenceObject ) )
        self.parentWindow, self.parentApp, self.referenceObject = parentWindow, parentApp, referenceObject
        self.internalBible = self.parentApp.handleInternalBibles( internalBible )

        Frame.__init__( self, parentWindow )
        BibleBox.__init__( self, self.parentApp )

        # Set some dummy values required soon
        self._viewRadioVar, self._groupRadioVar = tk.IntVar(), tk.StringVar()
        self.groupCode = BIBLE_GROUP_CODES[0] # Put into first/default BCV group
        self.contextViewMode = DEFAULT
        self.formatViewMode = DEFAULT
        self.currentVerseKey = SimpleVerseKey( 'UNK','1','1' ) # Unknown book

        if self.contextViewMode == DEFAULT:
            self.contextViewMode = 'ByVerse'
            self.parentWindow.viewVersesBefore, self.parentWindow.viewVersesAfter = 2, 6

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

        self.textBox = tk.Text( self, height=4, yscrollcommand=self.vScrollbar.set )
        self.textBox['wrap'] = 'word'
        self.textBox.pack( expand=tk.YES, fill=tk.X ) # Full width
        self.vScrollbar.config( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardKeyboardBindings()
        self.textBox.bind( "<Button-1>", self.setFocus ) # So disabled text box can still do select and copy functions

        # Set-up our standard Bible styles
        for USFMKey, styleDict in self.parentApp.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        # Add our extra specialised styles
        self.textBox.tag_configure( 'contextHeader', background='pink', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'context', background='pink', font='helvetica 6' )

        self.pack( expand=tk.YES, fill=tk.BOTH ) # Pack the frame

        # Set-up our Bible system and our callables
        self.BibleOrganisationalSystem = BibleOrganizationalSystem( "GENERIC-KJV-66-ENG" ) # temp
        self.getNumChapters = self.BibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda b,c: 99 if c=='0' or c==0 else self.BibleOrganisationalSystem.getNumVerses( b, c )
        self.isValidBCVRef = self.BibleOrganisationalSystem.isValidBCVRef
        self.getFirstBookCode = self.BibleOrganisationalSystem.getFirstBookCode
        self.getPreviousBookCode = self.BibleOrganisationalSystem.getPreviousBookCode
        self.getNextBookCode = self.BibleOrganisationalSystem.getNextBookCode
        self.getBBB = self.BibleOrganisationalSystem.getBBB
        self.getBookName = self.BibleOrganisationalSystem.getBookName
        self.getBookList = self.BibleOrganisationalSystem.getBookList
        self.maxChapters, self.maxVerses = 150, 150 # temp

        self.verseCache = OrderedDict()

        self.updateShownReferences( self.referenceObject )
    # end of BibleReferenceBox.__init__


    def createStandardKeyboardBindings( self ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleReferenceBox.createStandardKeyboardBindings()") )
        for name,command in ( ('SelectAll',self.doSelectAll), ('Copy',self.doCopy),
                             ('Find',self.doFind), ('Refind',self.doRefind),
                             ('Info',self.doShowInfo), ('Close',self.doClose) ):
            self.createStandardKeyboardBinding( name, command )
    # end of BibleReferenceBox.createStandardKeyboardBindings()


    def xxxgotoBCV( self, BBB, C, V ):
        """

        """
        if BibleOrgSysGlobals.debugFlag: print( exp("BibleReferenceBox.gotoBCV( {} {}:{} from {} )").format( BBB, C, V, self.currentVerseKey ) )
        # We really need to convert versification systems here
        adjBBB, adjC, adjV, adjS = self.BibleOrganisationalSystem.convertToReferenceVersification( BBB, C, V )
        self.parentWindow.gotoGroupBCV( self.groupCode, adjBBB, adjC, adjV ) # then the App will update me by calling updateShownBCV
    # end of BibleReferenceBox.gotoBCV


    def getContextVerseData( self, verseKey ):
        """
        Fetches and returns the internal Bible data for the given reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleReferenceBox.getContextVerseData( {} )").format( verseKey ) )
        if self.internalBible is not None:
            try: return self.internalBible.getContextVerseData( verseKey )
            except KeyError:
                logging.critical( exp("BibleReferenceBox.getContextVerseData for {} {} got a KeyError!") \
                                                                .format( self.boxType, verseKey ) )
    # end of BibleReferenceBox.getContextVerseData


    #def XXXgetSwordVerseKey( self, verseKey ):
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("getSwordVerseKey( {} )").format( verseKey ) )
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
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("getCachedVerseData( {} )").format( verseKey ) )
        verseKeyHash = verseKey.makeHash()
        if verseKeyHash in self.verseCache:
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  " + exp("Retrieved from BibleReferenceBox cache") )
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


    def XXXXgetBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("BibleReferenceBox.getBeforeAndAfterBibleData( {} )").format( newVerseKey ) )
            assert isinstance( newVerseKey, SimpleVerseKey )

        BBB, C, V = newVerseKey.getBCV()
        intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        prevBBB, prevIntC, prevIntV = BBB, intC, intV
        previousVersesData = []
        for n in range( -self.parentWindow.viewVersesBefore, 0 ):
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
                prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                if prevBBB is None: failed = True
                else:
                    prevIntC = self.getNumChapters( prevBBB )
                    prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    if BibleOrgSysGlobals.debugFlag: print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
            if not failed and prevIntV is not None:
                #print( "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                assert prevBBB and isinstance(prevBBB, str)
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getCachedVerseData( previousVerseKey )
                if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        # Determine the next valid verse numbers
        nextBBB, nextIntC, nextIntV = BBB, intC, intV
        nextVersesData = []
        for n in range( 0, self.parentWindow.viewVersesAfter ):
            try: numVerses = self.getNumVerses( nextBBB, nextIntC )
            except KeyError: numVerses = None # for an invalid BBB
            nextIntV += 1
            if numVerses is None or nextIntV > numVerses:
                nextIntV = 1
                nextIntC += 1 # Need to check................................
            nextVerseKey = SimpleVerseKey( nextBBB, nextIntC, nextIntV )
            nextVerseData = self.getCachedVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        verseData = self.getCachedVerseData( newVerseKey )

        return verseData, previousVersesData, nextVersesData
    # end of BibleReferenceBox.getBeforeAndAfterBibleData


    def XXXsetCurrentVerseKey( self, newVerseKey ):
        """
        Called to set the current verse key.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleReferenceBox.setCurrentVerseKey( {} )").format( newVerseKey ) )
            self.parentApp.setDebugText( "BRW setCurrentVerseKey…" )
            assert isinstance( newVerseKey, SimpleVerseKey )
        self.currentVerseKey = newVerseKey

        BBB = self.currentVerseKey.getBBB()
        self.maxChapters = self.getNumChapters( BBB )
        self.maxVerses = self.getNumVerses( BBB, self.currentVerseKey.getChapterNumber() )
    # end of BibleReferenceBox.setCurrentVerseKey


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
            print( "BibleReferenceBox.updateShownReferences( {} ) for {}".format( newReferenceObject, self.internalBible.name ) )
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

        #self.setCurrentVerseKey( newVerseKey )
        #self.clearText() # Leaves the text box enabled
        #startingFlag = True

        ## Safety-check in case they edited the settings file
        #if 'DBP' in self.boxType and self.contextViewMode in ('ByBook','ByChapter',):
            #print( exp("updateShownReferences: Safety-check converted {} contextViewMode for DBP").format( repr(self.contextViewMode) ) )
            #self._viewRadioVar.set( 3 ) # ByVerse
            #self.changeBibleContextView()

        #if self.contextViewMode == 'BeforeAndAfter':
            #bibleData = self.getBeforeAndAfterBibleData( newVerseKey )
            #if bibleData:
                #verseData, previousVerses, nextVerses = bibleData
                #for verseKey,previousVerseData in previousVerses:
                    #self.displayAppendVerse( startingFlag, verseKey, previousVerseData )
                    #startingFlag = False
                #self.displayAppendVerse( startingFlag, newVerseKey, verseData, currentVerse=True )
                #for verseKey,nextVerseData in nextVerses:
                    #self.displayAppendVerse( False, verseKey, nextVerseData )

        #elif self.contextViewMode == 'ByVerse':
            #self.displayAppendVerse( True, newVerseKey, self.getCachedVerseData( newVerseKey ), currentVerse=True )

        #elif self.contextViewMode == 'BySection':
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

        #elif self.contextViewMode == 'ByBook':
            #BBB, C, V = newVerseKey.getBCV()
            #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
            #for thisC in range( 0, self.getNumChapters( BBB ) ):
                #try: numVerses = self.getNumVerses( BBB, thisC )
                #except KeyError: numVerses = 0
                #for thisV in range( 0, numVerses ):
                    #thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                    #thisVerseData = self.getCachedVerseData( thisVerseKey )
                    #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                            #currentVerse=thisC==intC and thisV==intV )
                    #startingFlag = False

        #elif self.contextViewMode == 'ByChapter':
            #BBB, C, V = newVerseKey.getBCV()
            #intV = newVerseKey.getVerseNumberInt()
            #try: numVerses = self.getNumVerses( BBB, C )
            #except KeyError: numVerses = 0
            #for thisV in range( 0, numVerses ):
                #thisVerseKey = SimpleVerseKey( BBB, C, thisV )
                #thisVerseData = self.getCachedVerseData( thisVerseKey )
                #self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData, currentVerse=thisV==intV )
                #startingFlag = False

        #else:
            #logging.critical( exp("BibleReferenceBox.updateShownBCV: Bad context view mode {}").format( self.contextViewMode ) )
            #if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode

        self.textBox['state'] = tk.DISABLED # Don't allow editing
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleReferenceBox.closeReferenceBox()") )
        if self in self.parentWindow.referenceBoxes:
            self.parentWindow.referenceBoxes.remove( self )
            self.destroy()
        else: # we might not have finished making our box yet
            if BibleOrgSysGlobals.debugFlag:
                print( exp("BibleReferenceBox.closeReferenceBox() for {} wasn't in list").format( self.winType ) )
            try: self.destroy()
            except tk.TclError: pass # never mind
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Closed resource box" )
    # end of BibleReferenceBox.closeReferenceBox
# end of BibleReferenceBox class



#class InternalBibleReferenceBox( BibleReferenceBox ):
    #def __init__( self, parentWindow, modulePath ):
        #"""
        #Given a folder, try to open an UnknownBible.
        #If successful, set self.internalBible to point to the loaded Bible.
        #"""
        #if BibleOrgSysGlobals.debugFlag: print( "InternalBibleReferenceBox.__init__( {}, {} )".format( parentWindow, modulePath ) )
        #self.parentWindow, self.modulePath = parentWindow, modulePath

        #self.internalBible = None
        #BibleReferenceBox.__init__( self, self.parentWindow, 'InternalBibleReferenceBox', self.modulePath )
        ##self.boxType = 'InternalBibleReferenceBox'

        #try: self.UnknownBible = UnknownBible( self.modulePath )
        #except FileNotFoundError:
            #logging.error( exp("InternalBibleReferenceBox.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
            #self.UnknownBible = None
        #if self.UnknownBible:
            #result = self.UnknownBible.search( autoLoadAlways=True )
            #if isinstance( result, str ):
                #print( "Unknown Bible returned: {}".format( repr(result) ) )
                #self.internalBible = None
            #else: self.internalBible = result
        #if self.internalBible is not None: # Define which functions we use by default
            #self.getNumVerses = self.internalBible.getNumVerses
            #self.getNumChapters = self.internalBible.getNumChapters
    ## end of InternalBibleReferenceBox.__init__


    #def getContextVerseData( self, verseKey ):
        #"""
        #Fetches and returns the internal Bible data for the given reference.
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("InternalBibleReferenceBox.getContextVerseData( {} )").format( verseKey ) )
        #if self.internalBible is not None:
            #try: return self.internalBible.getContextVerseData( verseKey )
            #except KeyError:
                #logging.critical( exp("InternalBibleReferenceBox.getContextVerseData for {} {} got a KeyError!") \
                                                                #.format( self.boxType, verseKey ) )
    ## end of InternalBibleReferenceBox.getContextVerseData
## end of InternalBibleReferenceBox class



class BibleReferenceBoxes( list ):
    """
    Just keeps a list of the resource (Text) boxes.
    """
    def __init__( self, referenceBoxesParent ):
        self.referenceBoxesParent = referenceBoxesParent
        list.__init__( self )
    # end of BibleReferenceBoxes.__init__
# end of BibleReferenceBoxes class



class BibleReferenceCollectionWindow( BibleResourceWindow ):
#class BibleReferenceCollectionWindow( ChildWindow ):
    def __init__( self, parentApp, internalBible ):
        """
        Given a collection name, try to open an empty Bible resource collection window.
        """
        if BibleOrgSysGlobals.debugFlag: print( "BibleReferenceCollectionWindow.__init__( {}, {} )".format( parentApp, internalBible.name ) )
        self.parentApp, self.internalBible = parentApp, internalBible
        BibleResourceWindow.__init__( self, self.parentApp, 'BibleReferenceCollectionWindow', internalBible.name )
        #ChildWindow.__init__( self, self.parentApp, 'BibleResource' )
        #self.winType = 'InternalBibleReferenceBox'

        self.geometry( INITIAL_REFERENCE_COLLECTION_SIZE )
        self.minimumSize, self.maximumSize = MINIMUM_REFERENCE_COLLECTION_SIZE, MAXIMUM_REFERENCE_COLLECTION_SIZE
        self.minsize( *parseWindowSize( self.minimumSize ) )
        self.maxsize( *parseWindowSize( self.maximumSize ) )

        # Get rid of the default widgets
        self.vScrollbar.destroy()
        self.textBox.destroy()

        # Make a frame inside a canvas inside our window (in order to get a scrollbar)
        self.canvas = tk.Canvas( self, borderwidth=0, background="#ffffff" )
        self.frame = Frame( self.canvas ) #, background="#ffffff" )
        self.vsb = Scrollbar( self, orient="vertical", command=self.canvas.yview )
        self.canvas.configure( yscrollcommand=self.vsb.set )
        self.vsb.pack( side="right", fill="y" )
        self.canvas.pack( side=tk.LEFT, fill=tk.BOTH, expand=True )
        self.canvas.create_window( (4,4), window=self.frame, anchor="nw", tags="self.frame" )
        self.frame.bind( "<Configure>", self.OnFrameConfigure )

        #self.BCVUpdateType = 'ReferencesMode' # Leave as default
        self.folderPath = self.filename = self.filepath = None
        self.referenceBoxes = BibleReferenceBoxes( self )
    # end of BibleReferenceCollectionWindow.__init__


    def OnFrameConfigure( self, event ):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure( scrollregion=self.canvas.bbox("all") )


    def setFolderPath( self, newFolderPath ):
        """
        Store the folder path for where our internal Bible files will be.

        We're still waiting for the filename.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleReferenceCollectionWindow.setFolderPath( {} )").format( repr(newFolderPath) ) )
            assert self.filename is None
            assert self.filepath is None
        self.folderPath = newFolderPath
    # end of BibleReferenceCollectionWindow.setFolderPath


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleReferenceBox.createMenuBar()") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        #fileMenu.add_command( label='Info…', underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict['Info'][0] )
        #fileMenu.add_separator()
        #fileMenu.add_command( label='Rename', underline=0, command=self.doRename )
        #fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.doClose, accelerator=self.parentApp.keyBindingDict['Close'][0] ) # close this window

        if 0:
            editMenu = tk.Menu( self.menubar )
            self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
            editMenu.add_command( label='Copy', underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict['Copy'][0] )
            editMenu.add_separator()
            editMenu.add_command( label='Select all', underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict['SelectAll'][0] )

            searchMenu = tk.Menu( self.menubar )
            self.menubar.add_cascade( menu=searchMenu, label='Search', underline=0 )
            searchMenu.add_command( label='Goto line…', underline=0, command=self.doGotoLine, accelerator=self.parentApp.keyBindingDict['Line'][0] )
            searchMenu.add_separator()
            searchMenu.add_command( label='Find…', underline=0, command=self.doFind, accelerator=self.parentApp.keyBindingDict['Find'][0] )
            searchMenu.add_command( label='Find again', underline=5, command=self.doRefind, accelerator=self.parentApp.keyBindingDict['Refind'][0] )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        #gotoMenu.add_command( label='Previous book', underline=-1, command=self.doGotoPreviousBook )
        #gotoMenu.add_command( label='Next book', underline=-1, command=self.doGotoNextBook )
        #gotoMenu.add_command( label='Previous chapter', underline=-1, command=self.doGotoPreviousChapter )
        #gotoMenu.add_command( label='Next chapter', underline=-1, command=self.doGotoNextChapter )
        #gotoMenu.add_command( label='Previous section', underline=-1, command=self.notWrittenYet )
        #gotoMenu.add_command( label='Next section', underline=-1, command=self.notWrittenYet )
        #gotoMenu.add_command( label='Previous verse', underline=-1, command=self.doGotoPreviousVerse )
        #gotoMenu.add_command( label='Next verse', underline=-1, command=self.doGotoNextVerse )
        #gotoMenu.add_separator()
        #gotoMenu.add_command( label='Forward', underline=0, command=self.doGoForward )
        #gotoMenu.add_command( label='Backward', underline=0, command=self.doGoBackward )
        #gotoMenu.add_separator()
        #gotoMenu.add_command( label='Previous list item', underline=0, state=tk.DISABLED, command=self.doGotoPreviousListItem )
        #gotoMenu.add_command( label='Next list item', underline=0, state=tk.DISABLED, command=self.doGotoNextListItem )
        #gotoMenu.add_separator()
        #gotoMenu.add_command( label='Book', underline=0, command=self.doGotoBook )
        #gotoMenu.add_separator()
        self._groupRadioVar.set( self.groupCode )
        gotoMenu.add_radiobutton( label='Group A', underline=6, value='A', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group B', underline=6, value='B', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group C', underline=6, value='C', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label='Group D', underline=6, value='D', variable=self._groupRadioVar, command=self.changeBibleGroupCode )

        self.viewMenu = tk.Menu( self.menubar, tearoff=False ) # Save this reference so we can disable entries later
        self.menubar.add_cascade( menu=self.viewMenu, label='View', underline=0 )
        if   self.contextViewMode == 'BeforeAndAfter': self._viewRadioVar.set( 1 )
        #elif self.contextViewMode == 'BySection': self._viewRadioVar.set( 2 )
        elif self.contextViewMode == 'ByVerse': self._viewRadioVar.set( 3 )
        #elif self.contextViewMode == 'ByBook': self._viewRadioVar.set( 4 )
        #elif self.contextViewMode == 'ByChapter': self._viewRadioVar.set( 5 )
        else: print( self.contextViewMode ); halt

        self.viewMenu.add_radiobutton( label='Before and after…', underline=7, value=1, variable=self._viewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label='One section', underline=4, value=2, variable=self._viewRadioVar, command=self.changeBibleContextView )
        self.viewMenu.add_radiobutton( label='Single verse', underline=7, value=3, variable=self._viewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label='Whole book', underline=6, value=4, variable=self._viewRadioVar, command=self.changeBibleContextView )
        #self.viewMenu.add_radiobutton( label='Whole chapter', underline=6, value=5, variable=self._viewRadioVar, command=self.changeBibleContextView )

        #if 'DBP' in self.winType: # disable excessive online use
            #self.viewMenu.entryconfigure( 'Whole book', state=tk.DISABLED )
            #self.viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        #resourcesMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=resourcesMenu, label=_('Resources'), underline=0 )
        #resourcesMenu.add_command( label='Online (DBP)…', underline=0, command=self.doOpenDBPBibleResource )
        #resourcesMenu.add_command( label='Sword module…', underline=0, command=self.doOpenSwordResource )
        #resourcesMenu.add_command( label='Other (local)…', underline=1, command=self.doOpenInternalBibleResource )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Options…', underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label='Help' )
        helpMenu.add_command( label='Help…', underline=0, command=self.doHelp, accelerator=self.parentApp.keyBindingDict['Help'][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label='About…', underline=0, command=self.doAbout, accelerator=self.parentApp.keyBindingDict['About'][0] )
    # end of BibleReferenceCollectionWindow.createMenuBar


    def refreshTitle( self ):
        self.title( "[{}] {} Bible Reference Collection".format( self.groupCode, self.internalBible.name ) )
                        #self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber() ) )
    # end if BibleReferenceCollectionWindow.refreshTitle


    #def openDBPBibleReferenceBox( self, moduleAbbreviation, windowGeometry=None ):
        #"""
        #Create the actual requested DBP Bible resource window.

        #Returns the new DBPBibleReferenceBox object.
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( exp("openDBPBibleReferenceBox()") )
            #self.parentApp.setDebugText( "openDBPBibleReferenceBox…" )
            #assert moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6
        ##tk.Label( self, text=moduleAbbreviation ).pack( side=tk.TOP, fill=tk.X )
        #dBRB = DBPBibleReferenceBox( self, moduleAbbreviation )
        #if windowGeometry: halt; dBRB.geometry( windowGeometry )
        #if dBRB.DBPModule is None:
            #logging.critical( exp("Application.openDBPBibleReferenceBox: Unable to open resource {}").format( repr(moduleAbbreviation) ) )
            #dBRB.destroy()
            #showerror( self, APP_NAME, _("Sorry, unable to open DBP resource") )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openDBPBibleReferenceBox" )
            #self.parentApp.setReadyStatus()
            #return None
        #else:
            #dBRB.updateShownBCV( self.parentApp.getVerseKey( dBRB.groupCode ) )
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
            #print( exp("openInternalBibleReferenceBox()") )
            #self.parentApp.setDebugText( "openInternalBibleReferenceBox…" )
        ##tk.Label( self, text=modulePath ).pack( side=tk.TOP, fill=tk.X )
        #iBRB = InternalBibleReferenceBox( self, modulePath )
        #if windowGeometry: halt; iBRB.geometry( windowGeometry )
        #if iBRB.internalBible is None:
            #logging.critical( exp("Application.openInternalBibleReferenceBox: Unable to open resource {}").format( repr(modulePath) ) )
            #iBRB.destroy()
            #showerror( self, APP_NAME, _("Sorry, unable to open internal Bible resource") )
            #if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed openInternalBibleReferenceBox" )
            #self.parentApp.setReadyStatus()
            #return None
        #else:
            #iBRB.updateShownBCV( self.parentApp.getVerseKey( iBRB.groupCode ) )
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
            #print( "contextViewMode", self.contextViewMode )
            assert isinstance( newReferencesVerseKeys, list ) or newReferencesVerseKeys is None

        # Remove any previous resource boxes
        for referenceBox in self.referenceBoxes:
            referenceBox.destroy()
        self.referenceBoxes = BibleReferenceBoxes( self )

        if newReferencesVerseKeys is not None: # open new resource boxes
            assert isinstance( newReferencesVerseKeys, list )
            for newReferencesVerseKey in newReferencesVerseKeys:
                assert isinstance( newReferencesVerseKey, FlexibleVersesKey )
                for verseKeyObject in newReferencesVerseKey:
                    #print( "  BRCWupdateShownReferences: {}".format( verseKeyObject ) )
                    referenceBox = BibleReferenceBox( self.frame, self.parentApp, self.internalBible, verseKeyObject )
                    self.referenceBoxes.append( referenceBox )

        self.currentVerseKeys = newReferencesVerseKeys # The FlexibleVersesKey object
        self.refreshTitle()
    # end of BibleReferenceCollectionWindow.updateShownReferences


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleReferenceCollectionWindow.doHelp()") )
        from Help import HelpBox

        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.winType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of BibleReferenceCollectionWindow.doHelp


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleReferenceCollectionWindow.doAbout()") )
        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.winType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of BibleReferenceCollectionWindow.doAbout
# end of BibleReferenceCollectionWindow class



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
# end of BibleReferenceCollection.demo


if __name__ == '__main__':
    from BibleOrgSysGlobals import setup, addStandardOptionsAndProcess, closedown
    import multiprocessing

    # Configure basic set-up
    parser = setup( ProgName, ProgVersion )
    addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    closedown( ProgName, ProgVersion )
# end of BibleReferenceCollection.py