#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleResourceWindows.py
#   Last modified: 2014-10-04 (also update ProgVersion below)
#
# Bible resource windows for Biblelator Bible display/editing
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
Windows and frames to allow display and manipulation of
    (non-editable) Bible resource windows.
"""

ShortProgName = "BibleResourceWindows"
ProgName = "Biblelator Bible Resource Windows"
ProgVersion = "0.14"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, logging #, os.path, configparser, logging
from gettext import gettext as _

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
from tkinter import Toplevel, Menu, StringVar, messagebox #, Text
from tkinter import NORMAL, DISABLED, LEFT, RIGHT, BOTH, YES, END
#from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Style, Frame#, Button, Combobox
#from tkinter.tix import Spinbox

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
#from BibleOrganizationalSystems import BibleOrganizationalSystem
#import Hebrew
#from HebrewLexicon import HebrewLexicon
#from HebrewWLC import HebrewWLC
#import Greek
#from GreekNT import GreekNT
#import VerseReferences
#from USFMBible import USFMBible #, USFMStylesheets
from SwordResources import SwordType
from DigitalBiblePlatform import DBPBible
from UnknownBible import UnknownBible

# Biblelator imports
from BiblelatorGlobals import MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE
from ResourceWindows import ResourceFrame



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



class SwordBibleResourceFrame( ResourceFrame ):
    def __init__( self, parent, master, moduleAbbreviation ):
        #if Globals.debugFlag: print( "SwordBibleResourceFrame.__init__( {}, {}, {} )".format( parent, master, moduleAbbreviation ) )
        self.resourceWindowParent, self.myMaster, self.moduleAbbreviation = parent, master, moduleAbbreviation
        #print( "sP", self.SwordBibleResourceFrameParent )
        #print( "sm", self.myMaster )
        #print( "ma", self.moduleAbbreviation )
        ResourceFrame.__init__( self, self.resourceWindowParent )
        #self.grid( sticky=W+E+N+S ) #.pack()
        self.pack()
        self.resourceWindowParent.title( "{} ({})".format( self.moduleAbbreviation, 'Sw' if SwordType=="CrosswireLibrary" else 'SwM' ) )
        self.createSwordFrameWidgets()
        #print( self.ResourceFrameParent.geometry() )
        if 1:
            for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
                self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        else:
            self.textBox.tag_configure( 'verseNumberFormat', foreground='blue', font='helvetica 8', relief='raised', offset='3' )
            self.textBox.tag_configure( 'versePreSpaceFormat', background='pink', font='helvetica 8' )
            self.textBox.tag_configure( 'versePostSpaceFormat', background='pink', font='helvetica 4' )
            self.textBox.tag_configure( 'verseTextFormat', font='sil-doulos 12' )
            self.textBox.tag_configure( 'otherVerseTextFormat', font='sil-doulos 9' )
        #self.textBox.tag_configure( 'verseText', background='yellow', font='helvetica 14 bold', relief='raised' )
        #"background", "bgstipple", "borderwidth", "elide", "fgstipple", "font", "foreground", "justify", "lmargin1",
        #"lmargin2", "offset", "overstrike", "relief", "rmargin", "spacing1", "spacing2", "spacing3",
        #"tabs", "tabstyle", "underline", and "wrap".
        self.SwordModule = None # Loaded later in self.getBibleData()
    # end of SwordBibleResourceFrame.__init__

    def createSwordFrameWidgets( self ):
        pass
        #self.label1 = Label( self, text=self.moduleAbbreviation )
        #self.label1.pack()

        #self.hi_there = Button( self )
        #self.hi_there['text'] = "Refresh"
        #self.hi_there["command"] = self.update
        #self.hi_there.pack(side="top")

        #self.bStyle = Style( self )
        #self.bStyle.configure( "Red.TButton", foreground="red", background="white" )
        #self.bStyle.map("Red.TButton",
                        #foreground=[('pressed', 'red'), ('active', 'blue')],
                        #background=[('pressed', '!disabled', 'black'), ('active', 'white')] )

        #self.textBox = Text( self, width=40, height=10 )
        #self.textBox['wrap'] = 'word'
        #verseText = SwordResources.getBCV( self.parent.bcv )
        #print( "vt", verseText )
        #self.textBox.insert( '1.0', verseText )
        #self.textBox.pack()
        #self.textBox['state'] = DISABLED # Don't allow editing

        #self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        #self.QUIT.pack( side="bottom" )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    # end of SwordBibleResourceFrame.createSwordFrameWidgets

    def getBibleData( self ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if Globals.debugFlag: print( "SwordWindow.getBibleData()" )
        if self.SwordModule is None: self.SwordModule = self.myMaster.SwordInterface.getModule( self.moduleAbbreviation )
        if self.SwordModule is None:
            self.resourceWindowParent.title( "{} ({}) UNAVAILABLE".format( self.moduleAbbreviation, 'Sw' if SwordType=="CrosswireLibrary" else 'SwM' ) )
            return
        assert( self.SwordModule is not None )
        if Globals.debugFlag and debuggingThisModule: print( "sM", self.SwordModule )
        if Globals.debugFlag: print( "mN", self.SwordModule.getDescription() )

        previousVerseData = None
        if self.myMaster.previousBnameCV and self.myMaster.previousBnameCV[1]!='0' and self.myMaster.previousBnameCV[2]!='0': # Sword doesn't seem to handle introductions???
            #previousVerse = (  prevBCV, SwordResources.getBCV( prevBCV, self.moduleAbbreviation ) )
            previousVerseData = ( self.myMaster.previousBnameCV, self.myMaster.SwordInterface.getVerseData( self.SwordModule, self.myMaster.SwordPreviousKey ) )

        verseData = self.myMaster.SwordInterface.getVerseData( self.SwordModule, self.myMaster.SwordKey )

        nextVersesData = []
        for nextBnameCV,nextSwordKey in zip( self.myMaster.nextBnameCVs, self.myMaster.SwordNextKeys ):
            #nextVerseText = SwordResources.getBnameCV( nextBCV, self.moduleAbbreviation )
            nextVerseText = self.myMaster.SwordInterface.getVerseData( self.SwordModule, nextSwordKey )
            #print( "here", nextBCV, nextVerseText )
            if nextVerseText: nextVersesData.append( (nextBnameCV,nextVerseText) )

        return verseData, previousVerseData, nextVersesData
    # end of SwordBibleResourceFrame.getBibleData


    def update( self ): # Leaves in disabled state
        def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            #print( "SwordBibleResourceFrame.displayVerse", firstFlag, BnameCV, verseDataList, currentVerse )
            #haveC = None
            lastCharWasSpace = haveTextFlag = not firstFlag
            if verseDataList is None:
                print( "  ", BnameCV, "has no data" )
                self.textBox.insert( END, '--' )
            else:
                for entry in verseDataList:
                    if isinstance( entry, tuple ):
                        marker, cleanText = entry[0], entry[3]
                    else: marker, cleanText = entry.getMarker(), entry.getCleanText()
                    #print( "  ", haveTextFlag, marker, repr(cleanText) )
                    if marker == 'c': # Don't want to display this (original) c marker
                        #if not firstFlag: haveC = cleanText
                        #else: print( "   Ignore C={}".format( cleanText ) )
                        pass
                    elif marker == 'c#': # Might want to display this (added) c marker
                        if cleanText != BnameCV[0]:
                            if not lastCharWasSpace: self.textBox.insert( END, ' ', 'v-' )
                            self.textBox.insert( END, cleanText, 'c#' )
                            lastCharWasSpace = False
                    elif marker == 'p':
                        self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( END, cleanText, '*v~' if currentVerse else 'v~' )
                            lastCharWasSpace = False
                        haveTextFlag = True
                    elif marker == 'q1':
                        self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( END, cleanText, '*q1' if currentVerse else 'q1' )
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
                        logging.critical( t("SwordBibleResourceFrame.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        # end of displayVerse

        if Globals.debugFlag and debuggingThisModule: print( "SwordBibleResourceFrame.update()" )
        bibleData = self.getBibleData()
        self.clearText()
        if bibleData:
            verseData, previousVerse, nextVerses = bibleData
            #p = multiprocessing.Process( self.getBibleData )
            #p.start()

            if previousVerse:
                BnameCV, previousVerseData = previousVerse
                displayVerse( True, BnameCV, previousVerseData )
            displayVerse( not previousVerse, self.myMaster.BnameCV, verseData, currentVerse=True )
            for BnameCV,nextVerseData in nextVerses:
                displayVerse( False, BnameCV, nextVerseData )
        self.textBox['state'] = DISABLED # Don't allow editing
    # end of SwordBibleResourceFrame.update
# end of SwordBibleResourceFrame class



class DBPBibleResourceFrame( ResourceFrame ):
    def __init__( self, parent, master, moduleAbbreviation ):
        if Globals.debugFlag:
            #print( "DBPBibleResourceFrame.__init__( {}, {}, {} )".format( parent, master, moduleAbbreviation ) )
            assert( moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6 )
        self.resourceWindowParent, self.myMaster, self.moduleAbbreviation = parent, master, moduleAbbreviation
        #print( "sP", self.DBPFrameParent )
        #print( "sm", self.myMaster )
        #print( "ma", self.moduleAbbreviation )
        ResourceFrame.__init__( self, self.resourceWindowParent )
        #self.grid( sticky=W+E+N+S ) #.pack()
        self.pack()
        self.createDBPFrameWidgets()
        #print( self.ResourceFrameParent.geometry() )
        if 1:
            for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
                self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        else:
            self.textBox.tag_configure( 'verseNumberFormat', foreground='blue', font='helvetica 8', relief='raised', offset='3' )
            self.textBox.tag_configure( 'versePreSpaceFormat', background='pink', font='helvetica 8' )
            self.textBox.tag_configure( 'versePostSpaceFormat', background='pink', font='helvetica 4' )
            self.textBox.tag_configure( 'verseTextFormat', font='sil-doulos 12' )
            self.textBox.tag_configure( 'otherVerseTextFormat', font='sil-doulos 9' )
        #self.textBox.tag_configure( 'verseText', background='yellow', font='helvetica 14 bold', relief='raised' )
        #"background", "bgstipple", "borderwidth", "elide", "fgstipple", "font", "foreground", "justify", "lmargin1",
        #"lmargin2", "offset", "overstrike", "relief", "rmargin", "spacing1", "spacing2", "spacing3",
        #"tabs", "tabstyle", "underline", and "wrap".
        try: self.DBPModule = DBPBible( self.moduleAbbreviation )
        except ConnectionError:
            self.DBPModule = None
        self.resourceWindowParent.title( "{}.{}{}".format( self.moduleAbbreviation[:3], self.moduleAbbreviation[3:], ' (online)' if self.DBPModule else ' (offline)' ) )
        #if self.DBPModule:
            #if Globals.debugFlag: print( "sM", self.DBPModule )
            #if Globals.debugFlag: print( "mN", self.DBPModule.getDescription() )
    # end of DBPBibleResourceFrame.__init__

    def createDBPFrameWidgets( self ):
        pass
        #self.label1 = Label( self, text=self.moduleAbbreviation )
        #self.label1.pack()

        #self.hi_there = Button( self )
        #self.hi_there['text'] = "Refresh"
        #self.hi_there["command"] = self.update
        #self.hi_there.pack(side="top")

        #self.bStyle = Style( self )
        #self.bStyle.configure( "Red.TButton", foreground="red", background="white" )
        #self.bStyle.map("Red.TButton",
                        #foreground=[('pressed', 'red'), ('active', 'blue')],
                        #background=[('pressed', '!disabled', 'black'), ('active', 'white')] )

        #self.textBox = Text( self, width=40, height=10 )
        #self.textBox['wrap'] = 'word'
        #verseText = DBPResources.getBCV( self.parent.bcv )
        #print( "vt", verseText )
        #self.textBox.insert( '1.0', verseText )
        #self.textBox.pack()
        #self.textBox['state'] = DISABLED # Don't allow editing

        #self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        #self.QUIT.pack( side="bottom" )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    # end of DBPBibleResourceFrame.createDBPFrameWidgets


    def getBibleData( self ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if Globals.debugFlag: print( "DBPWindow.getBibleData()" )
        if not self.DBPModule:
            print( "RETURN1" )
            return

        lastParagraphNumber = None

        previousVerseData = None
        if self.myMaster.previousBnameCV and self.myMaster.previousBnameCV[1]!='0' and self.myMaster.previousBnameCV[2]!='0': # DBP doesn't seem to handle introductions???
            #previousVerse = (  prevBCV, DBPResources.getBCV( prevBCV, self.moduleAbbreviation ) )
            previousVerseData = self.DBPModule.getVerseData( self.myMaster.previousVerseKey )
            #print( "previous1", lastParagraphNumber, previousVerseData )
            if previousVerseData and previousVerseData[0][0] == 'p#':
                lastParagraphNumber = previousVerseData[0][3]
                #print( "lpN", lastParagraphNumber )
                previousVerseData.pop( 0 ) # Get rid of the p# line
                #print( "previous2", lastParagraphNumber, previousVerseData )
            previousVerseData = ( self.myMaster.previousBnameCV, previousVerseData, )

        verseData = self.DBPModule.getVerseData( self.myMaster.verseKey )
        if verseData and verseData[0][0] == 'p#':
            thisParagraphNumber = verseData[0][3]
            verseData.pop( 0 ) # Get rid of the p# line
            if lastParagraphNumber is not None and thisParagraphNumber!=lastParagraphNumber:
                #print( "insert p at this", self.myMaster.verseKey )
                verseData.insert( 0, ('p','p','','',[]) )
            lastParagraphNumber = thisParagraphNumber
            #print( "this", lastParagraphNumber, verseData )

        nextVersesData = []
        for nextVerseKey in self.myMaster.nextVerseKeys:
            BBB = nextVerseKey[0]
            nextVerseData = self.DBPModule.getVerseData( nextVerseKey )
            if nextVerseData:
                if nextVerseData and nextVerseData[0][0] == 'p#':
                    thisParagraphNumber = nextVerseData[0][3]
                    nextVerseData.pop( 0 ) # Get rid of the p# line
                    if lastParagraphNumber is not None and thisParagraphNumber!=lastParagraphNumber:
                        #print( "insert p at next", nextVerseKey )
                        nextVerseData.insert( 0, ('p','p','','',[]) )
                    lastParagraphNumber = thisParagraphNumber
                    #print( "next", lastParagraphNumber, nextVerseData )
                nextVersesData.append( (nextVerseKey,nextVerseData) )

        return verseData, previousVerseData, nextVersesData
    # end of DBPBibleResourceFrame.getBibleData


    def update( self ): # Leaves in disabled state
        def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            #print( "DBPBibleResourceFrame.displayVerse", firstFlag, BnameCV, [], currentVerse )
            #haveC = None
            lastCharWasSpace = haveTextFlag = not firstFlag
            if verseDataList is None:
                print( "  ", BnameCV, "has no data" )
                self.textBox.insert( END, '--' )
            else:
                #lastParagraphNumber = None
                for entry in verseDataList:
                    if isinstance( entry, tuple ):
                        marker, cleanText = entry[0], entry[3]
                    else: marker, cleanText = entry.getMarker(), entry.getCleanText()
                    #print( "  ", haveTextFlag, marker, repr(cleanText) )
                    if marker == 'c': # Don't want to display this (original) c marker
                        #if not firstFlag: haveC = cleanText
                        #else: print( "   Ignore C={}".format( cleanText ) )
                        pass
                    elif marker == 'c#': # Might want to display this (added) c marker
                        if cleanText != BnameCV[0]:
                            if not lastCharWasSpace: self.textBox.insert( END, ' ', 'v-' )
                            self.textBox.insert( END, cleanText, 'c#' )
                            lastCharWasSpace = False
                    #elif marker == 'p#':
                        #pass # Should be converted to p by now
                        #if lastParagraphNumber is not None and cleanText!=lastParagraphNumber:
                            #self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                            #lastCharWasSpace = True
                            #if cleanText:
                                #self.textBox.insert( END, cleanText, '*v~' if currentVerse else 'v~' )
                                #lastCharWasSpace = False
                            #haveTextFlag = True
                        #lastParagraphNumber = cleanText
                    elif marker == 'p':
                        self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( END, cleanText, '*v~' if currentVerse else 'v~' )
                            lastCharWasSpace = False
                        haveTextFlag = True
                    elif marker == 'q1':
                        self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( END, cleanText, '*q1' if currentVerse else 'q1' )
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
                        logging.critical( t("DBPBibleResourceFrame.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        # end of displayVerse

        if Globals.debugFlag: print( t("DBPBibleResourceFrame.update()") )
        if not self.DBPModule:
            print( "RETURN2" )
            return
        bibleData = self.getBibleData()
        self.clearText()
        if bibleData:
            verseData, previousVerse, nextVerses = bibleData
            if previousVerse:
                BnameCV, previousVerseData = previousVerse
                displayVerse( True, BnameCV, previousVerseData )
            displayVerse( not previousVerse, self.myMaster.BnameCV, verseData, currentVerse=True )
            for BnameCV,nextVerseData in nextVerses:
                displayVerse( False, BnameCV, nextVerseData )
        self.textBox['state'] = DISABLED # Don't allow editing
    # end of DBPBibleResourceFrame.update
# end of DBPBibleResourceFrame class



#class USFMResourceFrame( ResourceFrame ):
    #def __init__( self, parent, master, modulePath ):
        #if Globals.debugFlag: print( "USFMResourceFrame.__init__( {}, {}, {} )".format( parent, master, modulePath ) )
        #self.resourceWindowParent, self.myMaster, self.modulePath = parent, master, modulePath
        #ResourceFrame.__init__( self, self.resourceWindowParent )
        #self.pack( expand=YES, fill=BOTH )
        ##self.createUSFMResourceFrameWidgets()
        ##print( self.ResourceFrameParent.geometry() )
        #for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
            #self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        #try: self.USFMBible = USFMBible( self.modulePath )
        #except FileNotFoundError:
            #logging.error( t("USFMResourceFrame.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
            #self.USFMBible = None
        #self.resourceWindowParent.title( "{} (USFM){}".format( self.modulePath if self.USFMBible is None else self.USFMBible.name, ' NOT FOUND' if self.USFMBible is None else '' ) )
    ## end of USFMResourceFrame.__init__


    #def xxcreateUSFMResourceFrameWidgets( self ):
        #pass
        ##self.label1 = Label( self, text=self.moduleAbbreviation )
        ##self.label1.pack()

        ##self.hi_there = Button( self )
        ##self.hi_there['text'] = "Refresh"
        ##self.hi_there["command"] = self.update
        ##self.hi_there.pack(side="top")

        ##self.bStyle = Style( self )
        ##self.bStyle.configure( "Red.TButton", foreground="red", background="white" )
        ##self.bStyle.map("Red.TButton",
                        ##foreground=[('pressed', 'red'), ('active', 'blue')],
                        ##background=[('pressed', '!disabled', 'black'), ('active', 'white')] )

        ##self.textBox = Text( self, width=40, height=10 )
        ##self.textBox['wrap'] = 'word'
        ##verseText = SwordResources.getBCV( self.parent.bcv )
        ##print( "vt", verseText )
        ##self.textBox.insert( '1.0', verseText )
        ##self.textBox.pack()
        ##self.textBox['state'] = DISABLED # Don't allow editing

        ##self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        ##self.QUIT.pack( side="bottom" )

        ##Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    ## end of USFMResourceFrame.createUSFMResourceFrameWidgets

    #def getBibleData( self ):
        #"""
        #Returns the requested verse, the previous verse, and the next n verses.
        #"""
        #if Globals.debugFlag: print( t("USFMResourceFrame.getBibleData()") )
        #if self.USFMBible is None:
            #return

        #previousVerseData = None
        #if self.myMaster.previousVerseKey:
            #BBB = self.myMaster.previousVerseKey[0]
            ##if BBB not in self.USFMBible: self.USFMBible.loadBook( BBB )
            ##if self.myMaster.previousVerseKey[1]!='0' and self.myMaster.previousVerseKey[2]!='0': # Sword doesn't seem to handle introductions???
            ##previousVerse = (  prevBCV, SwordResources.getBCV( prevBCV, self.moduleAbbreviation ) )
            #previousVerseData = ( self.myMaster.previousVerseKey, self.USFMBible.getVerseData( self.myMaster.previousVerseKey ) )

        #BBB = self.myMaster.verseKey[0]
        ##print( "1", self.USFMBible )
        ##if BBB not in self.USFMBible: self.USFMBible.loadBook( BBB )
        ##print( "2", self.USFMBible )
        #verseData = self.USFMBible.getVerseData( self.myMaster.verseKey )

        #nextVersesData = []
        #for nextVerseKey in self.myMaster.nextVerseKeys:
            #BBB = nextVerseKey[0]
            ##if BBB not in self.USFMBible: self.USFMBible.loadBook( BBB )
            #nextVerseData = self.USFMBible.getVerseData( nextVerseKey )
            #if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData) )

        #return verseData, previousVerseData, nextVersesData
    ## end of USFMResourceFrame.getBibleData


    #def update( self ): # Leaves in disabled state
        #def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            ##print( "USFMResourceFrame.displayVerse", firstFlag, BnameCV, [], currentVerse )
            #haveC = None
            #lastCharWasSpace = haveTextFlag = not firstFlag
            #if verseDataList is None:
                #print( "  ", BnameCV, "has no data" )
                #self.textBox.insert( END, '--' )
            #else:
                #for entry in verseDataList:
                    #marker, cleanText = entry.getMarker(), entry.getCleanText()
                    ##print( "  ", haveTextFlag, marker, repr(cleanText) )
                    #if marker.startswith( '¬' ): pass # Ignore these closing markers
                    #elif marker == 'c': # Don't want to display this (original) c marker
                        ##if not firstFlag: haveC = cleanText
                        ##else: print( "   Ignore C={}".format( cleanText ) )
                        #pass
                    #elif marker == 'c#': # Might want to display this (added) c marker
                        #if cleanText != BnameCV[0]:
                            #if not lastCharWasSpace: self.textBox.insert( END, ' ', 'v-' )
                            #self.textBox.insert( END, cleanText, 'c#' )
                            #lastCharWasSpace = False
                    #elif marker == 's1':
                        #self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                        #haveTextFlag = True
                    #elif marker == 'r':
                        #self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                        #haveTextFlag = True
                    #elif marker == 'p':
                        #self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        #lastCharWasSpace = True
                        #if cleanText:
                            #self.textBox.insert( END, cleanText, '*v~' if currentVerse else 'v~' )
                            #lastCharWasSpace = False
                        #haveTextFlag = True
                    #elif marker == 'q1':
                        #self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        #lastCharWasSpace = True
                        #if cleanText:
                            #self.textBox.insert( END, cleanText, '*q1' if currentVerse else 'q1' )
                            #lastCharWasSpace = False
                        #haveTextFlag = True
                    #elif marker == 'm': pass
                    #elif marker == 'v':
                        #if haveTextFlag:
                            #self.textBox.insert( END, ' ', 'v-' )
                        #self.textBox.insert( END, cleanText, marker )
                        #self.textBox.insert( END, ' ', 'v+' )
                        #lastCharWasSpace = haveTextFlag = True
                    #elif marker in ('v~','p~'):
                        #self.textBox.insert( END, cleanText, '*v~' if currentVerse else marker )
                        #haveTextFlag = True
                    #else:
                        #logging.critical( t("USFMResourceFrame.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        ## end of displayVerse

        #if Globals.debugFlag: print( "USFMResourceFrame.update()" )
        #bibleData = self.getBibleData()
        #self.clearText()
        #if bibleData:
            #verseData, previousVerse, nextVerses = self.getBibleData()
            #if previousVerse:
                #BnameCV, previousVerseData = previousVerse
                #displayVerse( True, BnameCV, previousVerseData )
            #displayVerse( not previousVerse, self.myMaster.BnameCV, verseData, currentVerse=True )
            #for BnameCV,nextVerseData in nextVerses:
                #displayVerse( False, BnameCV, nextVerseData )
        #self.textBox['state'] = DISABLED # Don't allow editing
    ## end of USFMResourceFrame.update
## end of USFMResourceFrame class



class InternalBibleResourceFrame( ResourceFrame ):
    def __init__( self, parent, master, modulePath ):
        """
        Given a folder, try to open an UnknownBible.
        If successful, set self.InternalBible to point to the loaded Bible.
        """
        #if Globals.debugFlag: print( "InternalBibleResourceFrame.__init__( {}, {}, {} )".format( parent, master, modulePath ) )
        self.resourceWindowParent, self.myMaster, self.modulePath = parent, master, modulePath
        ResourceFrame.__init__( self, self.resourceWindowParent )
        self.pack( expand=YES, fill=BOTH )
        #self.createInternalBibleResourceFrameWidgets()
        #print( self.ResourceFrameParent.geometry() )
        for InternalBibleKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( InternalBibleKey, **styleDict ) # Create the style
        try: self.UnknownBible = UnknownBible( self.modulePath )
        except FileNotFoundError:
            logging.error( t("InternalBibleResourceFrame.__init__ Unable to find module path: {}").format( repr(self.modulePath) ) )
            self.UnknownBible = None
        if self.UnknownBible:
            result = self.UnknownBible.search( autoLoadAlways=True )
            if isinstance( result, str ):
                print( "Unknown Bible returned: {}".format( repr(result) ) )
                self.InternalBible = None
            else: self.InternalBible = result
        self.resourceWindowParent.title( "{} (InternalBible){}".format( self.modulePath if self.InternalBible is None else self.InternalBible.name, ' NOT FOUND' if self.InternalBible is None else '' ) )
    # end of InternalBibleResourceFrame.__init__


    def xxcreateInternalBibleResourceFrameWidgets( self ):
        pass
        #self.label1 = Label( self, text=self.moduleAbbreviation )
        #self.label1.pack()

        #self.hi_there = Button( self )
        #self.hi_there['text'] = "Refresh"
        #self.hi_there["command"] = self.update
        #self.hi_there.pack(side="top")

        #self.bStyle = Style( self )
        #self.bStyle.configure( "Red.TButton", foreground="red", background="white" )
        #self.bStyle.map("Red.TButton",
                        #foreground=[('pressed', 'red'), ('active', 'blue')],
                        #background=[('pressed', '!disabled', 'black'), ('active', 'white')] )

        #self.textBox = Text( self, width=40, height=10 )
        #self.textBox['wrap'] = 'word'
        #verseText = SwordResources.getBCV( self.parent.bcv )
        #print( "vt", verseText )
        #self.textBox.insert( '1.0', verseText )
        #self.textBox.pack()
        #self.textBox['state'] = DISABLED # Don't allow editing

        #self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        #self.QUIT.pack( side="bottom" )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    # end of InternalBibleResourceFrame.createInternalBibleResourceFrameWidgets

    def getBibleData( self ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if Globals.debugFlag: print( t("InternalBibleResourceFrame.getBibleData()") )
        if self.InternalBible is None:
            return

        previousVerseData = None
        if self.myMaster.previousVerseKey:
            BBB = self.myMaster.previousVerseKey[0]
            #if BBB not in self.InternalBible: self.InternalBible.loadBook( BBB )
            #if self.myMaster.previousVerseKey[1]!='0' and self.myMaster.previousVerseKey[2]!='0': # Sword doesn't seem to handle introductions???
            #previousVerse = (  prevBCV, SwordResources.getBCV( prevBCV, self.moduleAbbreviation ) )
            previousVerseData = ( self.myMaster.previousVerseKey, self.InternalBible.getVerseData( self.myMaster.previousVerseKey ) )

        BBB = self.myMaster.verseKey[0]
        #print( "1", self.InternalBible )
        #if BBB not in self.InternalBible: self.InternalBible.loadBook( BBB )
        #print( "2", self.InternalBible )
        verseData = self.InternalBible.getVerseData( self.myMaster.verseKey )

        nextVersesData = []
        for nextVerseKey in self.myMaster.nextVerseKeys:
            BBB = nextVerseKey[0]
            #if BBB not in self.InternalBible: self.InternalBible.loadBook( BBB )
            nextVerseData = self.InternalBible.getVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData) )

        return verseData, previousVerseData, nextVersesData
    # end of InternalBibleResourceFrame.getBibleData


    def update( self ): # Leaves in disabled state
        def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            #print( "InternalBibleResourceFrame.displayVerse", firstFlag, BnameCV, [], currentVerse )
            haveC = None
            lastCharWasSpace = haveTextFlag = not firstFlag
            if verseDataList is None:
                print( "  ", BnameCV, "has no data" )
                self.textBox.insert( END, '--' )
            else:
                for entry in verseDataList:
                    marker, cleanText = entry.getMarker(), entry.getCleanText()
                    #print( "  ", haveTextFlag, marker, repr(cleanText) )
                    if marker.startswith( '¬' ): pass # Ignore these closing markers
                    elif marker == 'c': # Don't want to display this (original) c marker
                        #if not firstFlag: haveC = cleanText
                        #else: print( "   Ignore C={}".format( cleanText ) )
                        pass
                    elif marker == 'c#': # Might want to display this (added) c marker
                        if cleanText != BnameCV[0]:
                            if not lastCharWasSpace: self.textBox.insert( END, ' ', 'v-' )
                            self.textBox.insert( END, cleanText, 'c#' )
                            lastCharWasSpace = False
                    elif marker == 's1':
                        self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                        haveTextFlag = True
                    elif marker == 'r':
                        self.textBox.insert( END, ('\n' if haveTextFlag else '')+cleanText, marker )
                        haveTextFlag = True
                    elif marker == 'p':
                        self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( END, cleanText, '*v~' if currentVerse else 'v~' )
                            lastCharWasSpace = False
                        haveTextFlag = True
                    elif marker == 'q1':
                        self.textBox.insert ( END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( END, cleanText, '*q1' if currentVerse else 'q1' )
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
                        logging.critical( t("InternalBibleResourceFrame.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        # end of displayVerse

        if Globals.debugFlag: print( "InternalBibleResourceFrame.update()" )
        bibleData = self.getBibleData()
        self.clearText()
        if bibleData:
            verseData, previousVerse, nextVerses = self.getBibleData()
            if previousVerse:
                BnameCV, previousVerseData = previousVerse
                displayVerse( True, BnameCV, previousVerseData )
            displayVerse( not previousVerse, self.myMaster.BnameCV, verseData, currentVerse=True )
            for BnameCV,nextVerseData in nextVerses:
                displayVerse( False, BnameCV, nextVerseData )
        self.textBox['state'] = DISABLED # Don't allow editing
    # end of InternalBibleResourceFrame.update
# end of InternalBibleResourceFrame class



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
# end of BibleResourceWindows.demo


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
# end of BibleResourceWindows.py
