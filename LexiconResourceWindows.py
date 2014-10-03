#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# LexiconResourceWindows.py
#   Last modified: 2014-10-03 (also update ProgVersion below)
#
# Bible and lexicon resource windows for Biblelator Bible display/editing
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
    Bible and lexicon resource windows.
"""

ShortProgName = "LexiconResourceWindows"
ProgName = "Biblelator Lexicon Resource Windows"
ProgVersion = "0.13"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, os.path, logging
from gettext import gettext as _

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
#from tkinter import Toplevel, Menu, Text, StringVar, messagebox
#from tkinter import NORMAL, DISABLED, LEFT, RIGHT, BOTH, YES, END
#from tkinter.ttk import Style, Frame#, Button, Combobox
#from tkinter.tix import Spinbox

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
#from BibleOrganizationalSystems import BibleOrganizationalSystem
#import Hebrew
#from HebrewLexicon import HebrewLexicon
#from GreekLexicon import GreekLexicon
from BibleLexicon import BibleLexicon
#from HebrewWLC import HebrewWLC
#import Greek
#from GreekNT import GreekNT
#import VerseReferences
#from USFMBible import USFMBible #, USFMStylesheets
#from SwordResources import SwordType
#from DigitalBiblePlatform import DBPBible

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


#class HebrewLexiconResourceFrame( ResourceFrame ):
    #def __init__( self, parent, master, lexiconPath=None ):
        #if Globals.debugFlag: print( "HebrewLexiconResourceFrame.__init__( {}, {}, {} )".format( parent, master, lexiconPath ) )
        #self.resourceWindowParent, self.myMaster, self.lexiconPath = parent, master, lexiconPath
        #ResourceFrame.__init__( self, self.resourceWindowParent )
        #self.pack( expand=YES, fill=BOTH )
        ##self.createHebrewLexiconResourceFrameWidgets()
        ##for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
        ##    self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        #try: self.HebrewLexicon = HebrewLexicon( self.lexiconPath )
        #except FileNotFoundError:
            #logging.error( t("HebrewLexiconResourceFrame.__init__ Unable to find Hebrew lexicon path: {}").format( repr(self.lexiconPath) ) )
            #self.HebrewLexicon = None
        #self.resourceWindowParent.title( "Hebrew Lexicon" )
    ## end of HebrewLexiconResourceFrame.__init__


    #def xxcreateHebrewLexiconResourceFrameWidgets( self ):
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
        ##self.textBox['state'] = 'disabled' # Don't allow editing

        ##self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        ##self.QUIT.pack( side="bottom" )

        ##Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    ## end of HebrewLexiconResourceFrame.createHebrewLexiconResourceFrameWidgets


    #def getBibleData( self ):
        #"""
        #Returns the requested verse, the previous verse, and the next n verses.
        #"""
        #if Globals.debugFlag: print( t("HebrewLexiconResourceFrame.getBibleData()") )
        #if self.HebrewLexicon is None:
            #return
        #return

        #previousVerseData = None
        #if self.myMaster.previousVerseKey:
            #BBB = self.myMaster.previousVerseKey[0]
            ##if BBB not in self.HebrewLexicon: self.HebrewLexicon.loadBook( BBB )
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
    ## end of HebrewLexiconResourceFrame.getBibleData


    #def update( self ): # Leaves in disabled state
        #def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            ##print( "HebrewLexiconResourceFrame.displayVerse", firstFlag, BnameCV, [], currentVerse )
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
                        #logging.critical( t("HebrewLexiconResourceFrame.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        ## end of displayVerse

        #if Globals.debugFlag: print( "HebrewLexiconResourceFrame.update()" )
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
        #self.textBox['state'] = 'disabled' # Don't allow editing
    ## end of HebrewLexiconResourceFrame.update
## end of HebrewLexiconResourceFrame class



#class GreekLexiconResourceFrame( ResourceFrame ):
    #def __init__( self, parent, master, lexiconPath=None ):
        #if Globals.debugFlag: print( "GreekLexiconResourceFrame.__init__( {}, {}, {} )".format( parent, master, lexiconPath ) )
        #self.resourceWindowParent, self.myMaster, self.lexiconPath = parent, master, lexiconPath
        #ResourceFrame.__init__( self, self.resourceWindowParent )
        #self.pack( expand=YES, fill=BOTH )
        ##self.createGreekLexiconResourceFrameWidgets()
        ##for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
        ##    self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        #try: self.GreekLexicon = GreekLexicon( self.lexiconPath )
        #except FileNotFoundError:
            #logging.error( t("GreekLexiconResourceFrame.__init__ Unable to find Greek lexicon path: {}").format( repr(self.lexiconPath) ) )
            #self.GreekLexicon = None
        #self.resourceWindowParent.title( "Greek Lexicon" )
    ## end of GreekLexiconResourceFrame.__init__


    #def xxcreateGreekLexiconResourceFrameWidgets( self ):
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
        ##self.textBox['state'] = 'disabled' # Don't allow editing

        ##self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        ##self.QUIT.pack( side="bottom" )

        ##Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    ## end of GreekLexiconResourceFrame.createGreekLexiconResourceFrameWidgets


    #def getBibleData( self ):
        #"""
        #Returns the requested verse, the previous verse, and the next n verses.
        #"""
        #if Globals.debugFlag: print( t("GreekLexiconResourceFrame.getBibleData()") )
        #if self.GreekLexicon is None:
            #return
        #return

        #previousVerseData = None
        #if self.myMaster.previousVerseKey:
            #BBB = self.myMaster.previousVerseKey[0]
            ##if BBB not in self.GreekLexicon: self.GreekLexicon.loadBook( BBB )
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
    ## end of GreekLexiconResourceFrame.getBibleData


    #def update( self ): # Leaves in disabled state
        #def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            ##print( "GreekLexiconResourceFrame.displayVerse", firstFlag, BnameCV, [], currentVerse )
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
                        #logging.critical( t("GreekLexiconResourceFrame.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        ## end of displayVerse

        #if Globals.debugFlag: print( "GreekLexiconResourceFrame.update()" )
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
        #self.textBox['state'] = 'disabled' # Don't allow editing
    ## end of GreekLexiconResourceFrame.update
## end of GreekLexiconResourceFrame class



class BibleLexiconResourceFrame( ResourceFrame ):
    def __init__( self, parent, master, lexiconPath=None ):
        if Globals.debugFlag: print( "BibleLexiconResourceFrame.__init__( {}, {}, {} )".format( parent, master, lexiconPath ) )
        self.resourceWindowParent, self.myMaster, self.lexiconPath = parent, master, lexiconPath
        ResourceFrame.__init__( self, self.resourceWindowParent )
        self.pack( expand=YES, fill=BOTH )
        #self.createBibleLexiconResourceFrameWidgets()
        #for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
        #    self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        try: self.BibleLexicon = BibleLexicon( os.path.join( self.lexiconPath, 'HebrewLexicon/' ), os.path.join( self.lexiconPath, 'morphgnt/strongs-dictionary-xml/' ) )
        except FileNotFoundError:
            logging.error( t("BibleLexiconResourceFrame.__init__ Unable to find Bible lexicon path: {}").format( repr(self.lexiconPath) ) )
            self.BibleLexicon = None
        self.resourceWindowParent.title( "Bible Lexicon" )
    # end of BibleLexiconResourceFrame.__init__


    def xxcreateBibleLexiconResourceFrameWidgets( self ):
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
        #self.textBox['state'] = 'disabled' # Don't allow editing

        #self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        #self.QUIT.pack( side="bottom" )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    # end of BibleLexiconResourceFrame.createBibleLexiconResourceFrameWidgets


    def getBibleData( self ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if Globals.debugFlag: print( t("BibleLexiconResourceFrame.getBibleData()") )
        if self.BibleLexicon is None:
            return
        return

        previousVerseData = None
        if self.myMaster.previousVerseKey:
            BBB = self.myMaster.previousVerseKey[0]
            #if BBB not in self.HebrewLexicon: self.HebrewLexicon.loadBook( BBB )
            #if self.myMaster.previousVerseKey[1]!='0' and self.myMaster.previousVerseKey[2]!='0': # Sword doesn't seem to handle introductions???
            #previousVerse = (  prevBCV, SwordResources.getBCV( prevBCV, self.moduleAbbreviation ) )
            previousVerseData = ( self.myMaster.previousVerseKey, self.USFMBible.getVerseData( self.myMaster.previousVerseKey ) )

        BBB = self.myMaster.verseKey[0]
        #print( "1", self.USFMBible )
        #if BBB not in self.USFMBible: self.USFMBible.loadBook( BBB )
        #print( "2", self.USFMBible )
        verseData = self.USFMBible.getVerseData( self.myMaster.verseKey )

        nextVersesData = []
        for nextVerseKey in self.myMaster.nextVerseKeys:
            BBB = nextVerseKey[0]
            #if BBB not in self.USFMBible: self.USFMBible.loadBook( BBB )
            nextVerseData = self.USFMBible.getVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData) )

        return verseData, previousVerseData, nextVersesData
    # end of BibleLexiconResourceFrame.getBibleData


    def update( self ): # Leaves in disabled state
        def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            #print( "BibleLexiconResourceFrame.displayVerse", firstFlag, BnameCV, [], currentVerse )
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
                        logging.critical( t("BibleLexiconResourceFrame.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        # end of displayVerse

        if Globals.debugFlag: print( "BibleLexiconResourceFrame.update()" )
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
        self.textBox['state'] = 'disabled' # Don't allow editing
    # end of BibleLexiconResourceFrame.update
# end of BibleLexiconResourceFrame class



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
# end of LexiconResourceWindows.demo


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
# end of LexiconResourceWindows.py