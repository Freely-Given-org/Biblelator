#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# LexiconResourceWindows.py
#   Last modified: 2014-10-23 (also update ProgVersion below)
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
ProgVersion = "0.19"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, os.path, logging
from gettext import gettext as _

import tkinter as tk

# Biblelator imports
from BiblelatorGlobals import MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE
from ResourceWindows import ResourceWindow, HTMLText

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
from BibleLexicon import BibleLexicon
#import Hebrew
#from HebrewLexicon import HebrewLexicon
#from GreekLexicon import GreekLexicon
#from HebrewWLC import HebrewWLC
#import Greek
#from GreekNT import GreekNT
#import VerseReferences



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


class BibleLexiconResourceWindow( ResourceWindow ):
    def __init__( self, parentApp, lexiconPath=None ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("BibleLexiconResourceWindow.__init__( {}, {} )").format( parentApp, lexiconPath ) )
        self.lexiconWord = None
        ResourceWindow.__init__( self, parentApp, 'LexiconResource' )
        self.parentApp, self.lexiconPath = parentApp, lexiconPath
        self.moduleID = self.lexiconPath
        self.winType = 'BibleLexiconResourceWindow'

        # Make our own textBox
        self.textBox.destroy()
        self.textBox = HTMLText( self, yscrollcommand=self.vScrollbar.set, wrap='word' )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.config( command=self.textBox.yview ) # link the scrollbar to the text box

        #self.createBibleLexiconResourceWindowWidgets()
        #for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
        #    self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style


        try: self.BibleLexicon = BibleLexicon( os.path.join( self.lexiconPath, 'HebrewLexicon/' ),
                                               os.path.join( self.lexiconPath, 'strongs-dictionary-xml/' ) )
        except FileNotFoundError:
            logging.critical( t("BibleLexiconResourceWindow.__init__ Unable to find Bible lexicon path: {}").format( repr(self.lexiconPath) ) )
            self.BibleLexicon = None
    # end of BibleLexiconResourceWindow.__init__


    def refreshTitle( self ):
        self.title( "[{}] {}".format( repr(self.lexiconWord), _("Bible Lexicon") ) )
    # end if BibleLexiconResourceWindow.refreshTitle


    def createMenuBar( self ):
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        #fileMenu.add_command( label='New...', underline=0, command=self.notWrittenYet )
        #fileMenu.add_command( label='Open...', underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu )
        #subfileMenuExport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label='HTML', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Export', underline=0, menu=subfileMenuExport )
        #fileMenu.add_separator()
        fileMenu.add_command( label='Info...', underline=0, command=self.onInfo )
        fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.onClose ) # close this window

        editMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        editMenu.add_command( label='Copy...', underline=0, command=self.notWrittenYet )
        editMenu.add_separator()
        editMenu.add_command( label='Find...', underline=0, command=self.notWrittenYet )

        if 0:
            gotoMenu = tk.Menu( self.menubar )
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

        if 0:
            viewMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=viewMenu, label='View', underline=0 )
            if   self.contextViewMode == 'BeforeAndAfter': self._viewRadio.set( 1 )
            elif self.contextViewMode == 'ByVerse': self._viewRadio.set( 2 )
            elif self.contextViewMode == 'ByBook': self._viewRadio.set( 3 )
            elif self.contextViewMode == 'ByChapter': self._viewRadio.set( 4 )

            viewMenu.add_radiobutton( label='Before and after...', underline=7, value=1, variable=self._viewRadio, command=self.changeBibleContextView )
            viewMenu.add_radiobutton( label='Single verse', underline=7, value=2, variable=self._viewRadio, command=self.changeBibleContextView )
            viewMenu.add_radiobutton( label='Whole book', underline=6, value=3, variable=self._viewRadio, command=self.changeBibleContextView )
            viewMenu.add_radiobutton( label='Whole chapter', underline=6, value=4, variable=self._viewRadio, command=self.changeBibleContextView )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label='Help' )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout )
    # end of BibleLexiconResourceWindow.createMenuBar


    def xxcreateBibleLexiconResourceWindowWidgets( self ):
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
        #self.textBox['state'] = tk.DISABLED # Don't allow editing

        #self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.destroy)
        #self.QUIT.pack( side="bottom" )
    # end of BibleLexiconResourceWindow.createBibleLexiconResourceWindowWidgets


    def xxxgetBibleData( self ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if Globals.debugFlag: print( t("BibleLexiconResourceWindow.getBibleData()") )
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
    # end of BibleLexiconResourceWindow.getBibleData


    def xxxupdate( self ): # Leaves in disabled state
        def displayVerse( firstFlag, BnameCV, verseDataList, currentVerse=False ):
            #print( "BibleLexiconResourceWindow.displayVerse", firstFlag, BnameCV, [], currentVerse )
            haveC = None
            lastCharWasSpace = haveTextFlag = not firstFlag
            if verseDataList is None:
                print( "  ", BnameCV, "has no data" )
                self.textBox.insert( tk.END, '--' )
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
                            if not lastCharWasSpace: self.textBox.insert( tk.END, ' ', 'v-' )
                            self.textBox.insert( tk.END, cleanText, 'c#' )
                            lastCharWasSpace = False
                    elif marker == 's1':
                        self.textBox.insert( tk.END, ('\n' if haveTextFlag else '')+cleanText, marker )
                        haveTextFlag = True
                    elif marker == 'p':
                        self.textBox.insert ( tk.END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( tk.END, cleanText, '*v~' if currentVerse else 'v~' )
                            lastCharWasSpace = False
                        haveTextFlag = True
                    elif marker == 'q1':
                        self.textBox.insert ( tk.END, '\n  ' if haveTextFlag else '  ' )
                        lastCharWasSpace = True
                        if cleanText:
                            self.textBox.insert( tk.END, cleanText, '*q1' if currentVerse else 'q1' )
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
                        logging.critical( t("BibleLexiconResourceWindow.displayVerse: Unknown marker {} {}").format( marker, cleanText ) )
        # end of displayVerse

        if Globals.debugFlag: print( "BibleLexiconResourceWindow.update()" )
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
        self.textBox['state'] = tk.DISABLED # Don't allow editing
    # end of BibleLexiconResourceWindow.update


    def updateLexiconWord( self, newLexiconWord ): # Leaves in disabled state
        if Globals.debugFlag: print( t("updateLexiconWord( {} )").format( newLexiconWord ) )
        self.lexiconWord = newLexiconWord
        self.clearText() # Leaves the text box enabled
        if self.BibleLexicon is None:
            self.textBox.insert( tk.END, "No lexicon loaded so can't display entry for {}.".format( repr(newLexiconWord) ) )
        else:
            self.textBox.insert( tk.END, "Entry for {}".format( repr(newLexiconWord) ) )
            #txt = self.BibleLexicon.getEntryData( self.lexiconWord )
            #if txt: self.textBox.insert( tk.END, '\n'+txt )
            txt = self.BibleLexicon.getEntryHTML( self.lexiconWord )
            if txt: self.textBox.insert( tk.END, '\n'+txt )
        self.textBox['state'] = tk.DISABLED # Don't allow editing
    # end of BibleLexiconResourceWindow.updateLexiconWord
# end of BibleLexiconResourceWindow class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    #from tkinter import Tk
    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if Globals.debugFlag: print( t("Running demo...") )
    #Globals.debugFlag = True

    tkRootWindow = tk.Tk()
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