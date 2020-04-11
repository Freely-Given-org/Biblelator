#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SwordManager.py
#
# Sword module download manager program
#
# Copyright (C) 2016-2018 Robert Hunt
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
Tabbed dialog box to allow viewing of various BOS (Bible Organisational System) subsystems
    such as versification systems, books names systems, etc.

This is opened as a TopLevel window in Biblelator
    but can also be run as a stand-alone program.
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2018-12-12' # by RJH
SHORT_PROGRAM_NAME = "SwordManager"
PROGRAM_NAME = "Sword Manager"
PROGRAM_VERSION = '0.05' # Separate versioning from Biblelator
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = True


import sys
import os
import logging, subprocess
import multiprocessing
#from collections import OrderedDict


import tkinter as tk
from tkinter.ttk import Style, Frame, Button, Scrollbar, Label, Notebook
from tkinter.scrolledtext import ScrolledText

# Biblelator imports
from Biblelator.BiblelatorGlobals import DEFAULT, tkSTART, MAX_PSEUDOVERSES, errorBeep, \
        DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, \
        DEFAULT_KEY_BINDING_DICT, \
        parseWindowGeometry, assembleWindowGeometryFromList, centreWindow, \
        parseWindowSize
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showWarning, showInfo
from Biblelator.Dialogs.BiblelatorDialogs import SelectResourceBoxDialog, GetNewProjectNameDialog, \
                                CreateNewProjectFilesDialog, GetNewCollectionNameDialog, \
                                BookNameDialog, NumberButtonDialog
from Biblelator.Helpers.BiblelatorHelpers import mapReferencesVerseKey, createEmptyUSFMBooks
from Biblelator.Settings.Settings import ApplicationSettings, ProjectSettings
from Biblelator.Settings.BiblelatorSettingsFunctions import parseAndApplySettings, writeSettingsFile, \
        saveNewWindowSetup, deleteExistingWindowSetup, applyGivenWindowsSettings, viewSettings
from Biblelator.Windows.TextBoxes import BEntry, BCombobox
from Biblelator.Windows.ChildWindows import ChildWindows
from Biblelator.Windows.TextEditWindow import TextEditWindow

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
from BibleOrgSys.Reference.BibleOrganisationalSystems import BibleOrganisationalSystem
#from BibleOrgSys.Reference.BibleVersificationSystems import BibleVersificationSystems
#from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Reference.BibleStylesheets import BibleStylesheet
from BibleOrgSys.Formats.SwordResources import SwordType, SwordInterface
from BibleOrgSys.Online.SwordInstallManager import SwordInstallManager



MAIN_APP_NAME = 'Biblelator'
# Default window size settings (Note: X=width, Y=height)
INITIAL_MAIN_SIZE, INITIAL_MAIN_SIZE_DEBUG, MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE = '607x376', '607x460', '550x375', '700x600'



class SwordManager( Frame ):
    """
    This is the main application window (well, actually a frame in the root toplevel window).

    Its main job is to keep track of self.currentVerseKey (and self.currentVerseKeyGroup)
        and use that to inform child windows of BCV movements.
    """
    global settings
    def __init__( self, rootWindow, homeFolderPath, loggingFolderPath, iconImage, settings ):
        """
        Main app initialisation function.

        Creates the main menu and toolbar which includes the main BCV (book/chapter/verse) selector.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("SwordManager.__init__( {}, {}, {}, … )").format( rootWindow, homeFolderPath, loggingFolderPath ) )
        self.rootWindow, self.homeFolderPath, self.loggingFolderPath, self.iconImage, self.settings = rootWindow, homeFolderPath, loggingFolderPath, iconImage, settings
        self.parentApp = self # Yes, that's me, myself!
        self.starting = True

        self.themeName = 'default'
        self.style = Style()
        self.interfaceLanguage = DEFAULT
        self.interfaceComplexity = DEFAULT
        self.touchMode = False # True makes larger buttons
        self.tabletMode = False
        self.showDebugMenu = True
        self.internetAccessEnabled = False

        self.lastFind = None
        #self.openDialog = None
        self.saveDialog = None
        self.optionsDict = {}

        self.lexiconWord = None
        self.currentProject = None

        if BibleOrgSysGlobals.debugFlag: print( "Button default font", Style().lookup('TButton', 'font') )
        if BibleOrgSysGlobals.debugFlag: print( "Label default font", Style().lookup('TLabel', 'font') )

        # We rely on the parseAndApplySettings() call below to do this
        ## Set-up our Bible system and our callables
        #self.genericBibleOrganisationalSystemName = 'GENERIC-KJV-ENG' # Handles all bookcodes
        #self.setGenericBibleOrganisationalSystem( self.genericBibleOrganisationalSystemName )

        self.stylesheet = BibleStylesheet().loadDefault()
        Frame.__init__( self, self.rootWindow )
        self.pack()

        self.rootWindow.protocol( 'WM_DELETE_WINDOW', self.doCloseMe ) # Catch when app is closed

        self.childWindows = ChildWindows( self )

        self.createStatusBar()

        self.SwIM = SwordInstallManager()

        # Create our display text book
        self.textBox = ScrolledText( self.rootWindow, bg='lightskyblue' )#style='DebugText.TScrolledText' )
        self.textBox.pack( side=tk.TOP, fill=tk.BOTH )
        #self.debugTextBox.tag_configure( 'emp', background='yellow', font='helvetica 12 bold', relief='tk.RAISED' )
        self.textBox.tag_configure( 'emp', font='helvetica 10 bold' )
        self.textBox.insert( tk.END, 'Main Text Box:' )

        if BibleOrgSysGlobals.debugFlag: # Create a scrolling debug box
            self.lastDebugMessage = None
            #Style().configure('DebugText.TScrolledText', padding=2, background='orange')
            self.debugTextBox = ScrolledText( self.rootWindow, bg='orange' )#style='DebugText.TScrolledText' )
            self.debugTextBox.pack( side=tk.BOTTOM, fill=tk.BOTH )
            #self.debugTextBox.tag_configure( 'emp', background='yellow', font='helvetica 12 bold', relief='tk.RAISED' )
            self.debugTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
            self.setDebugText( "Starting up…" )

        self.keyBindingDict = DEFAULT_KEY_BINDING_DICT
        self.myKeyboardBindingsList = []
        self.recentFiles = []

        # Read and apply the saved settings
        #parseAndApplySettings( self )
        if not self.settings or PROGRAM_NAME not in self.settings.data or 'windowSize' not in self.settings.data[PROGRAM_NAME] or 'windowPosition' not in self.settings.data[PROGRAM_NAME]:
            initialMainSize = INITIAL_MAIN_SIZE_DEBUG if BibleOrgSysGlobals.debugFlag else INITIAL_MAIN_SIZE
            centreWindow( self.rootWindow, *initialMainSize.split( 'x', 1 ) )

        if self.touchMode:
            vPrint( 'Normal', debuggingThisModule, _("Touch mode enabled!") )
            self.createTouchMenuBar()
            self.createTouchNavigationBar()
        else: # assume it's regular desktop mode
            self.createNormalMenuBar()
            self.createNormalNavigationBar()
        self.createToolBar()
        if BibleOrgSysGlobals.debugFlag: self.createDebugToolBar()
        self.createMainKeyboardBindings()

        self.repoDict = None
        self.createNotebook()

        # See if there's any developer messages
        if self.internetAccessEnabled and self.checkForDeveloperMessagesEnabled:
            self.doCheckForDeveloperMessages()

        self.rootWindow.title( programNameVersion )
        self.minimumSize = MINIMUM_MAIN_SIZE
        self.rootWindow.minsize( *parseWindowSize( self.minimumSize ) )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "__init__ finished." )
        self.starting = False
        self.setReadyStatus()
    # end of SwordManager.__init__


    def setGenericBibleOrganisationalSystem( self, BOSname ):
        """
        We usually use a fairly generic BibleOrganisationalSystem (BOS) to ensure
            that it contains all the books that we might ever want to navigate to.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("setGenericBibleOrganisationalSystem( {} )").format( BOSname ) )

        # Set-up our Bible system and our callables
        self.genericBibleOrganisationalSystem = BibleOrganisationalSystem( self.genericBibleOrganisationalSystemName )
        self.genericBookList = self.genericBibleOrganisationalSystem.getBookList()
        #self.getNumBooks = self.genericBibleOrganisationalSystem.getNumBooks
        self.getNumChapters = self.genericBibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda BBB,C: MAX_PSEUDOVERSES if C=='-1' or C==-1 \
                                        else self.genericBibleOrganisationalSystem.getNumVerses( BBB, C )
        self.isValidBCVRef = self.genericBibleOrganisationalSystem.isValidBCVRef
        self.getFirstBookCode = self.genericBibleOrganisationalSystem.getFirstBookCode
        self.getPreviousBookCode = self.genericBibleOrganisationalSystem.getPreviousBookCode
        self.getNextBookCode = self.genericBibleOrganisationalSystem.getNextBookCode
        self.getBBBFromText = self.genericBibleOrganisationalSystem.getBBBFromText
        self.getGenericBookName = self.genericBibleOrganisationalSystem.getBookName
        #self.getBookList = self.genericBibleOrganisationalSystem.getBookList

        # Make a bookNumber table with GEN as #1
        #print( self.genericBookList )
        self.offsetGenesis = self.genericBookList.index( 'GEN' )
        #print( 'offsetGenesis', self.offsetGenesis )
        self.bookNumberTable = {}
        for j,BBB in enumerate(self.genericBookList):
            k = j + 1 - self.offsetGenesis
            nBBB = BibleOrgSysGlobals.loadedBibleBooksCodes.getReferenceNumber( BBB )
            #print( BBB, nBBB )
            self.bookNumberTable[k] = BBB
            self.bookNumberTable[BBB] = k
        #print( self.bookNumberTable )
    # end of SwordManager.setGenericBibleOrganisationalSystem


    def createNormalMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createNormalMenuBar()") )

        #self.win = Toplevel( self )
        self.menubar = tk.Menu( self.rootWindow )
        #self.rootWindow['menu'] = self.menubar
        self.rootWindow.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        fileNewSubmenu = tk.Menu( fileMenu, tearoff=False )
        #fileMenu.add_cascade( label=_('New'), underline=0, menu=fileNewSubmenu )
        #fileNewSubmenu.add_command( label=_('Text file'), underline=0, command=self.notWrittenYet )
        #fileOpenSubmenu = tk.Menu( fileMenu, tearoff=False )
        #fileMenu.add_cascade( label=_('Open'), underline=0, menu=fileOpenSubmenu )
        #fileRecentOpenSubmenu = tk.Menu( fileOpenSubmenu, tearoff=False )
        #fileOpenSubmenu.add_cascade( label=_('Recent'), underline=0, menu=fileRecentOpenSubmenu )
        #for j, (filename, folder, windowType) in enumerate( self.recentFiles ):
            #fileRecentOpenSubmenu.add_command( label=filename, underline=0, command=self.notWrittenYet )
        #fileOpenSubmenu.add_separator()
        #fileOpenSubmenu.add_command( label=_('Text file…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #fileMenu.add_command( label=_('Save all…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #fileMenu.add_command( label=_('Save settings'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        fileMenu.add_command( label=_('Quit app'), underline=0, command=self.doCloseMe, accelerator=self.keyBindingDict[_('Quit')][0] ) # quit app

        if BibleOrgSysGlobals.debugFlag:
            debugMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=debugMenu, label=_('Debug'), underline=0 )
            debugMenu.add_command( label=_('View settings…'), underline=0, command=self.doViewSettings )
            debugMenu.add_separator()
            debugMenu.add_command( label=_('View log…'), underline=5, command=self.doViewLog )
            debugMenu.add_separator()
            debugMenu.add_command( label=_('Submit bug…'), underline=0, command=self.doSubmitBug )
            debugMenu.add_separator()
            debugMenu.add_command( label=_('Options…'), underline=0, command=self.notWrittenYet )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label=_('Help'), underline=0 )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=self.keyBindingDict[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('Submit bug…'), underline=0, state=tk.NORMAL if self.internetAccessEnabled else tk.DISABLED, command=self.doSubmitBug )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=self.keyBindingDict[_('About')][0] )
    # end of SwordManager.createNormalMenuBar

    def createTouchMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createTouchMenuBar()") )
            assert self.touchMode

        self.createNormalMenuBar()
    # end of SwordManager.createTouchMenuBar


    def createNormalNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createNormalNavigationBar()") )

        return

        Style().configure('NavigationBar.TFrame', background='yellow')

        navigationBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='NavigationBar.TFrame' )

        self.previousBCVButton = Button( navigationBar, width=4, text='<-', command=self.doGoBackward, state=tk.DISABLED )
        self.previousBCVButton.pack( side=tk.LEFT )
        self.nextBCVButton = Button( navigationBar, width=4, text='->', command=self.doGoForward, state=tk.DISABLED )
        self.nextBCVButton.pack( side=tk.LEFT )

        Style().configure( 'A.TButton', background='lightgreen' )
        Style().configure( 'B.TButton', background='pink' )
        Style().configure( 'C.TButton', background='orange' )
        Style().configure( 'D.TButton', background='brown' )
        self.GroupAButton = Button( navigationBar, width=2, text='A', style='A.TButton', command=self.selectGroupA, state=tk.DISABLED )
        self.GroupBButton = Button( navigationBar, width=2, text='B', style='B.TButton', command=self.selectGroupB, state=tk.DISABLED )
        self.GroupCButton = Button( navigationBar, width=2, text='C', style='C.TButton', command=self.selectGroupC, state=tk.DISABLED )
        self.GroupDButton = Button( navigationBar, width=2, text='D', style='D.TButton', command=self.selectGroupD, state=tk.DISABLED )
        self.GroupAButton.pack( side=tk.LEFT )
        self.GroupBButton.pack( side=tk.LEFT )
        self.GroupCButton.pack( side=tk.LEFT )
        self.GroupDButton.pack( side=tk.LEFT )

        self.bookNumberVar = tk.StringVar()
        self.bookNumberVar.set( '1' )
        self.maxBooks = len( self.genericBookList )
        #print( "maxChapters", self.maxChaptersThisBook )
        self.bookNumberSpinbox = tk.Spinbox( navigationBar, width=3, from_=1-self.offsetGenesis, to=self.maxBooks, textvariable=self.bookNumberVar )
        #self.bookNumberSpinbox['width'] = 3
        self.bookNumberSpinbox['command'] = self.spinToNewBookNumber
        self.bookNumberSpinbox.bind( '<Return>', self.spinToNewBookNumber )
        self.bookNumberSpinbox.pack( side=tk.LEFT )

        self.bookNames = [self.getGenericBookName(BBB) for BBB in self.genericBookList] # self.getBookList()]
        bookName = self.bookNames[1] # Default to Genesis usually
        self.bookNameVar = tk.StringVar()
        self.bookNameVar.set( bookName )
        BBB = self.getBBBFromText( bookName )
        self.bookNameBox = BCombobox( navigationBar, width=len('Deuteronomy'), textvariable=self.bookNameVar )
        self.bookNameBox['values'] = self.bookNames
        #self.bookNameBox['width'] = len( 'Deuteronomy' )
        self.bookNameBox.bind('<<ComboboxSelected>>', self.spinToNewBook )
        self.bookNameBox.bind( '<Return>', self.spinToNewBook )
        self.bookNameBox.pack( side=tk.LEFT )

        self.chapterNumberVar = tk.StringVar()
        self.chapterNumberVar.set( '1' )
        self.maxChaptersThisBook = self.getNumChapters( BBB )
        #print( "maxChapters", self.maxChaptersThisBook )
        self.chapterSpinbox = tk.Spinbox( navigationBar, width=3, from_=0.0, to=self.maxChaptersThisBook, textvariable=self.chapterNumberVar )
        #self.chapterSpinbox['width'] = 3
        self.chapterSpinbox['command'] = self.spinToNewChapter
        self.chapterSpinbox.bind( '<Return>', self.spinToNewChapter )
        self.chapterSpinbox.pack( side=tk.LEFT )

        #self.chapterNumberVar = tk.StringVar()
        #self.chapterNumberVar.set( '1' )
        #self.chapterNumberBox = BEntry( self, textvariable=self.chapterNumberVar )
        #self.chapterNumberBox['width'] = 3
        #self.chapterNumberBox.pack()

        self.verseNumberVar = tk.StringVar()
        self.verseNumberVar.set( '1' )
        #self.maxVersesThisChapterVar = tk.StringVar()
        self.maxVersesThisChapter = self.getNumVerses( BBB, self.chapterNumberVar.get() )
        #print( "maxVerses", self.maxVersesThisChapter )
        #self.maxVersesThisChapterVar.set( str(self.maxVersesThisChapter) )
        # Add 1 to maxVerses to enable them to go to the next chapter
        self.verseSpinbox = tk.Spinbox( navigationBar, width=3, from_=0.0, to=1.0+self.maxVersesThisChapter, textvariable=self.verseNumberVar )
        #self.verseSpinbox['width'] = 3
        self.verseSpinbox['command'] = self.acceptNewBnCV
        self.verseSpinbox.bind( '<Return>', self.acceptNewBnCV )
        self.verseSpinbox.pack( side=tk.LEFT )

        #self.verseNumberVar = tk.StringVar()
        #self.verseNumberVar.set( '1' )
        #self.verseNumberBox = BEntry( self, textvariable=self.verseNumberVar )
        #self.verseNumberBox['width'] = 3
        #self.verseNumberBox.pack()

        self.wordVar = tk.StringVar()
        if self.lexiconWord: self.wordVar.set( self.lexiconWord )
        self.wordBox = BEntry( navigationBar, width=12, textvariable=self.wordVar )
        #self.wordBox['width'] = 12
        self.wordBox.bind( '<Return>', self.acceptNewWord )
        self.wordBox.pack( side=tk.LEFT )

        # if 0: # I don't think we should need this button if everything else works right
        #     self.updateButton = Button( navigationBar )
        #     self.updateButton['text'] = 'Update'
        #     self.updateButton['command'] = self.acceptNewBnCV
        #     #self.updateButton.grid( row=0, column=7 )
        #     self.updateButton.pack( side=tk.LEFT )

        Style( self ).map("Quit.TButton", foreground=[('pressed', 'red'), ('active', 'blue')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )
        self.quitButton = Button( navigationBar, text="QUIT", style="Quit.TButton", command=self.doCloseMe )
        self.quitButton.pack( side=tk.RIGHT )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
        navigationBar.pack( side=tk.TOP, fill=tk.X )
    # end of SwordManager.createNormalNavigationBar

    def createTouchNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createTouchNavigationBar()") )
            assert self.touchMode

        return

        xPad, yPad = 6, 8
        minButtonCharWidth = 4

        Style().configure('NavigationBar.TFrame', background='yellow')
        navigationBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='NavigationBar.TFrame' )

        self.previousBCVButton = Button( navigationBar, width=minButtonCharWidth, text='<-', command=self.doGoBackward, state=tk.DISABLED )
        self.previousBCVButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )
        self.nextBCVButton = Button( navigationBar, width=minButtonCharWidth, text='->', command=self.doGoForward, state=tk.DISABLED )
        self.nextBCVButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )

        Style().configure( 'A.TButton', background='lightgreen' )
        Style().configure( 'B.TButton', background='pink' )
        Style().configure( 'C.TButton', background='orange' )
        Style().configure( 'D.TButton', background='brown' )
        self.GroupAButton = Button( navigationBar, width=minButtonCharWidth,
                                   text='A', style='A.TButton', command=self.selectGroupA, state=tk.DISABLED )
        self.GroupBButton = Button( navigationBar, width=minButtonCharWidth,
                                   text='B', style='B.TButton', command=self.selectGroupB, state=tk.DISABLED )
        self.GroupCButton = Button( navigationBar, width=minButtonCharWidth,
                                   text='C', style='C.TButton', command=self.selectGroupC, state=tk.DISABLED )
        self.GroupDButton = Button( navigationBar, width=minButtonCharWidth,
                                   text='D', style='D.TButton', command=self.selectGroupD, state=tk.DISABLED )
        self.GroupAButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )
        self.GroupBButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )
        self.GroupCButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )
        self.GroupDButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )

        self.bookNumberVar = tk.StringVar()
        self.bookNumberVar.set( '1' )
        self.maxBooks = len( self.genericBookList )
        #print( "maxChapters", self.maxChaptersThisBook )
        self.bookNumberSpinbox = tk.Spinbox( navigationBar, width=3, from_=1-self.offsetGenesis, to=self.maxBooks, textvariable=self.bookNumberVar )
        #self.bookNumberSpinbox['width'] = 3
        self.bookNumberSpinbox['command'] = self.spinToNewBookNumber
        self.bookNumberSpinbox.bind( '<Return>', self.spinToNewBookNumber )
        #self.bookNumberSpinbox.pack( side=tk.LEFT )

        self.bookNames = [self.getGenericBookName(BBB) for BBB in self.genericBookList] # self.getBookList()]
        bookName = self.bookNames[1] # Default to Genesis usually
        self.bookNameVar = tk.StringVar()
        self.bookNameVar.set( bookName )
        BBB = self.getBBBFromText( bookName )
        self.bookNameBox = BCombobox( navigationBar, width=len('Deuteronomy'), textvariable=self.bookNameVar )
        self.bookNameBox['values'] = self.bookNames
        #self.bookNameBox['width'] = len( 'Deuteronomy' )
        self.bookNameBox.bind('<<ComboboxSelected>>', self.spinToNewBook )
        self.bookNameBox.bind( '<Return>', self.spinToNewBook )
        #self.bookNameBox.pack( side=tk.LEFT )

        Style().configure( 'bookName.TButton', background='brown' )
        self.bookNameButton = Button( navigationBar, width=8, text=bookName, style='bookName.TButton', command=self.doBookNameButton )
        self.bookNameButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )

        self.chapterNumberVar = tk.StringVar()
        self.chapterNumberVar.set( '1' )
        self.maxChaptersThisBook = self.getNumChapters( BBB )
        #print( "maxChapters", self.maxChaptersThisBook )
        self.chapterSpinbox = tk.Spinbox( navigationBar, width=3, from_=0.0, to=self.maxChaptersThisBook, textvariable=self.chapterNumberVar )
        #self.chapterSpinbox['width'] = 3
        self.chapterSpinbox['command'] = self.spinToNewChapter
        self.chapterSpinbox.bind( '<Return>', self.spinToNewChapter )
        #self.chapterSpinbox.pack( side=tk.LEFT )

        Style().configure( 'chapterNumber.TButton', background='brown' )
        self.chapterNumberButton = Button( navigationBar, width=minButtonCharWidth, text='1', style='chapterNumber.TButton', command=self.doChapterNumberButton )
        self.chapterNumberButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )

        #self.chapterNumberVar = tk.StringVar()
        #self.chapterNumberVar.set( '1' )
        #self.chapterNumberBox = BEntry( self, textvariable=self.chapterNumberVar )
        #self.chapterNumberBox['width'] = 3
        #self.chapterNumberBox.pack()

        self.verseNumberVar = tk.StringVar()
        self.verseNumberVar.set( '1' )
        #self.maxVersesThisChapterVar = tk.StringVar()
        self.maxVersesThisChapter = self.getNumVerses( BBB, self.chapterNumberVar.get() )
        #print( "maxVerses", self.maxVersesThisChapter )
        #self.maxVersesThisChapterVar.set( str(self.maxVersesThisChapter) )
        # Add 1 to maxVerses to enable them to go to the next chapter
        self.verseSpinbox = tk.Spinbox( navigationBar, width=3, from_=0.0, to=1.0+self.maxVersesThisChapter, textvariable=self.verseNumberVar )
        #self.verseSpinbox['width'] = 3
        self.verseSpinbox['command'] = self.acceptNewBnCV
        self.verseSpinbox.bind( '<Return>', self.acceptNewBnCV )
        #self.verseSpinbox.pack( side=tk.LEFT )

        Style().configure( 'verseNumber.TButton', background='brown' )
        self.verseNumberButton = Button( navigationBar, width=minButtonCharWidth, text='1', style='verseNumber.TButton', command=self.doVerseNumberButton )
        self.verseNumberButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )

        self.wordVar = tk.StringVar()
        if self.lexiconWord: self.wordVar.set( self.lexiconWord )
        self.wordBox = BEntry( navigationBar, width=12, textvariable=self.wordVar )
        #self.wordBox['width'] = 12
        self.wordBox.bind( '<Return>', self.acceptNewWord )
        #self.wordBox.pack( side=tk.LEFT )

        Style().configure( 'word.TButton', background='brown' )
        self.wordButton = Button( navigationBar, width=8, text=self.lexiconWord, style='word.TButton', command=self.doWordButton )
        self.wordButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )

        # if 0: # I don't think we should need this button if everything else works right
        #     self.updateButton = Button( navigationBar )
        #     self.updateButton['text'] = 'Update'
        #     self.updateButton['command'] = self.acceptNewBnCV
        #     #self.updateButton.grid( row=0, column=7 )
        #     self.updateButton.pack( side=tk.LEFT )

        Style( self ).map("Quit.TButton", foreground=[('pressed', 'red'), ('active', 'blue')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )
        self.quitButton = Button( navigationBar, text=_("QUIT"), style="Quit.TButton", command=self.doCloseMe )
        self.quitButton.pack( side=tk.RIGHT, padx=xPad, pady=yPad )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
        navigationBar.pack( side=tk.TOP, fill=tk.X )
    # end of SwordManager.createTouchNavigationBar


    def createToolBar( self ):
        """
        Create a tool bar containing several helpful buttons at the top of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createToolBar()") )

        return

        xPad, yPad = 6, 8

        Style().configure( 'ToolBar.TFrame', background='green' )
        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='ToolBar.TFrame' )

        Style().configure( 'ShowAll.TButton', background='lightgreen' )
        Style().configure( 'HideResources.TButton', background='pink' )
        Style().configure( 'HideAll.TButton', background='orange' )

        Button( toolbar, text=_("Show All"), style='ShowAll.TButton', command=self.doShowAll ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        Button( toolbar, text=_("Hide Resources"), style='HideResources.TButton', command=self.doHideAllResources ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        Button( toolbar, text=_("Hide All"), style='HideAll.TButton', command=self.doHideAll ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        #Button( toolbar, text='Bring All', command=self.doBringAll ).pack( side=tk.LEFT, padx=2, pady=2 )

        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of SwordManager.createToolBar


    def createNotebook( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createToolBar()") )

        self.notebook = Notebook( self )

        # Adding Frames as pages for the ttk.Notebook

        # Sources page
        print( "Create sources page" )
        if self.repoDict is None:
            self.repoDict = {}
            for repoName,repoData in self.SwIM.downloadSources.items():
                var = tk.BooleanVar()
                self.repoDict[repoName] = (var,repoData)
        else: # check if it's been expanded
            for repoName,repoData in self.SwIM.downloadSources.items():
                if repoName not in self.repoDict:
                    var = tk.BooleanVar()
                    self.repoDict[repoName] = (var,repoData)
        self.sourcesPage = Frame( self.notebook )

        self.sourceModeVar = tk.IntVar()
        self.sourceModeVar.set( 1 )
        Label( self.sourcesPage, text="Source repositories", justify = tk.LEFT ).grid( row=0, column=0, sticky=tk.W )
        tk.Radiobutton( self.sourcesPage, text="Single source only", padx = 20, variable=self.sourceModeVar, value=1 ).grid( row=1, column=0, sticky=tk.W )
        tk.Radiobutton( self.sourcesPage, text="Allow multiple sources", padx = 20, variable=self.sourceModeVar, value=2 ).grid( row=2, column=0, sticky=tk.W )
        Label( self.sourcesPage, text=_("SOURCE") ).grid( row=0, column=4 )
        Label( self.sourcesPage, text=_("MODE") ).grid( row=0, column=5 )
        Label( self.sourcesPage, text=_("SITE") ).grid( row=0, column=6 )
        Label( self.sourcesPage, text=_("FOLDER") ).grid( row=0, column=7 )
        for j, repoName in enumerate( self.repoDict ):
            var, repoData = self.repoDict[repoName]
            cb = tk.Checkbutton( self.sourcesPage, text=repoName, variable=var, command=self.searchCode )
            cb.grid( row=j+1, column=4, sticky=tk.W )
            e0 = BEntry( self.sourcesPage, width=5 )
            e0.insert( tk.END, repoData[0] )
            e0.configure( state=tk.DISABLED )
            e0.grid( row=j+1, column=5, sticky=tk.W )
            e1 = BEntry( self.sourcesPage, width=15 )
            e1.insert( tk.END, repoData[1] )
            e1.configure( state=tk.DISABLED )
            e1.grid( row=j+1, column=6, sticky=tk.W )
            e2 = BEntry( self.sourcesPage, width=20 )
            e2.insert( tk.END, repoData[2] )
            e2.configure( state=tk.DISABLED )
            e2.grid( row=j+1, column=7, sticky=tk.W )

        # Folders page
        print( "Create folders page" )
        self.foldersPage = Frame( self.notebook )
        foldersLabel = Label( self.foldersPage, text="Install folder(s)" )
        foldersLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.foldersPage, text=_("Install folder:") )
        searchLabel.grid( row=1, column=0 )
        self.foldersSearch = BEntry( self.foldersPage, width=25 )
        self.foldersSearch.bind( '<Return>', self.searchCode )
        self.foldersSearch.grid( row=1, column=1 )
        searchLabel2 = Label( self.foldersPage, text=_("Temp folder:") )
        searchLabel2.grid( row=2, column=0 )
        self.foldersSearch2 = BEntry( self.foldersPage, width=25 )
        self.foldersSearch2.bind( '<Return>', self.searchCode )
        self.foldersSearch2.grid( row=2, column=1 )
        sbar = Scrollbar( self.foldersPage )
        self.foldersListbox = tk.Listbox( self.foldersPage, width=5, relief=tk.SUNKEN )
        sbar.configure( command=self.foldersListbox.yview )
        self.foldersListbox.configure( yscrollcommand=sbar.set )
        self.foldersListbox.bind('<<ListboxSelect>>', self.gotoNewCode )
        #self.foldersListbox.bind( '<Return>', self.gotoNewCode )
        sbar.grid( row=0, column=3, rowspan=3, sticky=tk.N+tk.S )
        self.foldersListbox.grid( row=0, column=2, rowspan=3, sticky=tk.N+tk.S )
        self.folderTextBox = ScrolledText( self.foldersPage, bg='lightblue' )
        self.folderTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.folderTextBox.insert( tk.END, 'Codes' )
        self.folderTextBox.grid( row=0, column=4, rowspan=3, sticky=tk.N+tk.S+tk.E )
        #for BBB in self.BibleBooksCodesList:
            #self.foldersListbox.insert( tk.END, BBB ) # fill the listbox
        self.foldersSearch.insert( tk.END, str(self.SwIM.currentInstallFolder) )
        self.foldersSearch2.insert( tk.END, str(self.SwIM.currentTempFolder) )
        #self.searchCode( None ) # Go to the above
        #self.foldersSearch.delete( 0, tk.END ) # Clear the search box again


        # Folders page
        print( "Create install page" )
        self.installPage = Frame( self.notebook )
        foldersLabel = Label( self.installPage, text="Install new module(s)" )
        foldersLabel.grid( row=0, column=0, columnspan=2 )

        # Folders page
        print( "Create update page" )
        self.updatePage = Frame( self.notebook )
        foldersLabel = Label( self.updatePage, text="Update module(s)" )
        foldersLabel.grid( row=0, column=0, columnspan=2 )

        # Folders page
        print( "Create modules page" )
        self.modulesPage = Frame( self.notebook )
        foldersLabel = Label( self.modulesPage, text="View modules" )
        foldersLabel.grid( row=0, column=0, columnspan=2 )

        print( "Add all pages" )
        self.notebook.add( self.sourcesPage, text=_("Sources") )
        self.notebook.add( self.foldersPage, text=_("Folders") )
        self.notebook.add( self.installPage, text=_("Install new") )
        self.notebook.add( self.updatePage, text=_("Update") )
        self.notebook.add( self.modulesPage, text=_("View modules") )
        self.notebook.pack( expand=tk.YES, fill=tk.BOTH )
    # end of SwordManager.createNotebook


    def halt( self ):
        """
        Halts the program immediately without saving any files or settings.
        Only used in debug mode.
        """
        logging.critical( "User selected HALT in DEBUG MODE. Not saving any files or settings!" )
        self.quit()
    # end of SwordManager.halt


    def createDebugToolBar( self ):
        """
        Create a debug tool bar containing several additional buttons at the top of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createDebugToolBar()") )

        xPad, yPad = (6, 8) if self.touchMode else (2, 2)

        Style().configure( 'DebugToolBar.TFrame', background='red' )
        Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='DebugToolBar.TFrame' )
        Button( toolbar, text='Halt', style='Halt.TButton', command=self.halt ) \
                        .pack( side=tk.RIGHT, padx=xPad, pady=yPad )
        Button( toolbar, text='Save settings', command=lambda: writeSettingsFile(self) ) \
                        .pack( side=tk.RIGHT, padx=xPad, pady=yPad )
        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of SwordManager.createDebugToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createStatusBar()") )

        #Style().configure( 'StatusBar.TLabel', background='pink' )
        #Style().configure( 'StatusBar.TLabel', background='DarkOrange1' )
        Style().configure( 'StatusBar.TLabel', background='forest green' )

        self.statusTextVariable = tk.StringVar()
        self.statusTextLabel = Label( self.rootWindow, relief=tk.SUNKEN,
                                    textvariable=self.statusTextVariable, style='StatusBar.TLabel' )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.BOTTOM, fill=tk.X )
        self.statusTextVariable.set( '' ) # first initial value
        self.setWaitStatus( _("Starting up…") )
    # end of SwordManager.createStatusBar


    def createMainKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("createMainKeyboardBindings()") )

        self.myKeyboardBindingsList = []
        for name,command in ( ('Help',self.doHelp),
                              ('About',self.doAbout),
                              ('Quit',self.doCloseMe)
                              ):
            if name in self.keyBindingDict:
                for keyCode in self.keyBindingDict[name][1:]:
                    #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                    self.rootWindow.bind( keyCode, command )
                self.myKeyboardBindingsList.append( (name,self.keyBindingDict[name][0],) )
            else: logging.critical( 'No key binding available for {!r}'.format( name ) )

        # These bindings apply to/from all windows
        #self.bind_all( '<Alt-Up>', self.doGotoPreviousVerse )
        #self.bind_all( '<Alt-Down>', self.doGotoNextVerse )
        #self.bind_all( '<Alt-comma>', self.doGotoPreviousChapter )
        #self.bind_all( '<Alt-period>', self.doGotoNextChapter )
        #self.bind_all( '<Alt-bracketleft>', self.doGotoPreviousBook )
        #self.bind_all( '<Alt-bracketright>', self.doGotoNextBook )
    # end of SwordManager.createMainKeyboardBindings()


    #def addRecentFile( self, threeTuple ):
        #"""
        #Puts most recent first
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("addRecentFile( {} )").format( threeTuple ) )
            #assert len(threeTuple) == 3

        #try: self.recentFiles.remove( threeTuple ) # Remove a duplicate if present
        #except ValueError: pass
        #self.recentFiles.insert( 0, threeTuple ) # Put this one at the beginning of the lis
        #if len(self.recentFiles)>MAX_RECENT_FILES: self.recentFiles.pop() # Remove the last one if necessary
        #self.createNormalMenuBar()
    ## end of SwordManager.addRecentFile()


    def notWrittenYet( self ):
        errorBeep()
        showError( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of SwordManager.notWrittenYet


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("setStatus( {!r} )").format( newStatusText ) )

        #print( "SB is", repr( self.statusTextVariable.get() ) )
        if newStatusText != self.statusTextVariable.get(): # it's changed
            #self.statusBarTextWidget.configure( state=tk.NORMAL )
            #self.statusBarTextWidget.delete( tkSTART, tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( tkSTART, newStatusText )
            #self.statusBarTextWidget.configure( state=tk.DISABLED ) # Don't allow editing
            #self.statusText = newStatusText
            Style().configure( 'StatusBar.TLabel', foreground='white', background='purple' )
            self.statusTextVariable.set( newStatusText )
            self.statusTextLabel.update()
    # end of SwordManager.setStatus

    def setErrorStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("setErrorStatus( {!r} )").format( newStatusText ) )

        #self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='StatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( 'StatusBar.TLabel', foreground='yellow', background='red' )
        self.update()
    # end of SwordManager.setErrorStatus

    def setWaitStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("setWaitStatus( {!r} )").format( newStatusText ) )

        self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='StatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( 'StatusBar.TLabel', foreground='black', background='DarkOrange1' )
        self.update()
    # end of SwordManager.setWaitStatus

    def setReadyStatus( self ):
        """
        Sets the status line to "Ready"
            and sets the cursor to the normal cursor
        unless we're still starting
            (this covers any slow start-up functions that don't yet set helpful statuses)
        """
        if self.starting: self.setWaitStatus( _("Starting up…") )
        else: # we really are ready
            #self.statusTextLabel.configure( style='StatusBar.TLabelReady' )
            self.setStatus( _("Ready") )
            Style().configure( 'StatusBar.TLabel', foreground='yellow', background='forest green' )
            self.configure( cursor='' )
    # end of SwordManager.setReadyStatus


    def setDebugText( self, newMessage=None ):
        """
        """
        if debuggingThisModule:
            #print( _("setDebugText( {!r} )").format( newMessage ) )
            assert BibleOrgSysGlobals.debugFlag

        logging.info( 'Debug: ' + newMessage ) # Not sure why logging.debug isn't going into the file! XXXXXXXXXXXXX
        self.debugTextBox.configure( state=tk.NORMAL ) # Allow editing
        self.debugTextBox.delete( tkSTART, tk.END ) # Clear everything
        self.debugTextBox.insert( tk.END, 'DEBUGGING INFORMATION:' )
        if self.lastDebugMessage: self.debugTextBox.insert( tk.END, '\nWas: ' + self.lastDebugMessage )
        if newMessage:
            self.debugTextBox.insert( tk.END, '\n' )
            self.debugTextBox.insert( tk.END, 'Msg: ' + newMessage, 'emp' )
            self.lastDebugMessage = newMessage
        self.debugTextBox.insert( tk.END, '\n\n{} child windows:'.format( len(self.childWindows) ) )
        for j, appWin in enumerate( self.childWindows ):
            #try: extra = ' ({})'.format( appWin.BCVUpdateType )
            #except AttributeError: extra = ''
            self.debugTextBox.insert( tk.END, "\n  {} wT={} gWT={} {} modID={} cVM={} BCV={}" \
                                    .format( j+1,
                                        appWin.windowType,
                                        #appWin.windowType.replace('ChildWindow',''),
                                        appWin.genericWindowType,
                                        #appWin.genericWindowType.replace('Resource',''),
                                        appWin.winfo_geometry(), appWin.moduleID,
                                        appWin._contextViewMode if 'Bible' in appWin.genericWindowType else 'N/A',
                                        appWin.BCVUpdateType if 'Bible' in appWin.genericWindowType else 'N/A' ) )
                                        #extra ) )
        #self.debugTextBox.insert( tk.END, '\n{} resource frames:'.format( len(self.childWindows) ) )
        #for j, projFrame in enumerate( self.childWindows ):
            #self.debugTextBox.insert( tk.END, "\n  {} {}".format( j, projFrame ) )
        self.debugTextBox.configure( state=tk.DISABLED ) # Don't allow editing
    # end of SwordManager.setDebugText


    def doChangeTheme( self, newThemeName ):
        """
        Set the window theme to the given scheme.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( _("doChangeTheme( {!r} )").format( newThemeName ) )
            assert newThemeName
            self.setDebugText( 'Set theme to {!r}'.format( newThemeName ) )

        self.themeName = newThemeName
        try:
            self.style.theme_use( newThemeName )
        except tk.TclError as err:
            showError( self, 'Error', err )
    # end of SwordManager.doChangeTheme


    def searchCode( self, event ):
        """
        """
        enteredText = self.foldersSearch.get()
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( _("searchFolder( {}, {!r} )").format( event, enteredText ) )
            self.setDebugText( "searchFolder…" )

        if not enteredText: return

        return

        if len(enteredText)!=3: self.setErrorStatus( "Books codes must be three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books codes must have no spaces" ); return
        elif enteredText not in self.BibleBooksCodesList:
            self.setErrorStatus( "Unknown {!r} book code".format( enteredText ) )
            return

        # Must be ok
        self.BBB = enteredText
        index = self.BibleBooksCodesList.index( self.BBB )

        # Select it in the listbox
        self.codesListbox.select_set( index )
        self.codesListbox.see( index )
        self.codesListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewCode below
    # end of BOSManager.searchCode


    def gotoNewCode( self, event=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( _("gotoNewCode( {} )").format( event ) )
            self.setDebugText( "gotoNewCode…" )
            #print( 'You selected items: %s'%[self.codesListbox.get(int(i)) for i in self.codesListbox.curselection()] )

        print( "code cursel", repr(self.codesListbox.curselection()) )
        index = int( self.codesListbox.curselection()[0] ) # Top one selected
        self.BBB = self.codesListbox.get( index )
        codeDict =  BibleOrgSysGlobals.loadedBibleBooksCodes._getFullEntry( self.BBB )

        # Clear the text box
        self.codeTextBox.configure( state=tk.NORMAL )
        self.codeTextBox.delete( tkSTART, tk.END )
        self.codeTextBox.insert( tk.END, '{} (#{})\n\n'.format( self.BBB, codeDict['referenceNumber'] ) )
        self.codeTextBox.insert( tk.END, '{}\n\n'.format( codeDict['nameEnglish'] ) )
        for field,value in sorted( codeDict.items() ):
            if field not in ( 'referenceNumber', 'nameEnglish', ):
                self.codeTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewCode


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        viewSettings( self )
        #if BibleOrgSysGlobals.debugFlag:
            #if debuggingThisModule: print( _("doViewSettings()") )
            #self.setDebugText( "doViewSettings…" )
        #tEW = TextEditWindow( self )
        ##if windowGeometry: tEW.geometry( windowGeometry )
        #if not tEW.setFilepath( self.settings.settingsFilepath ) \
        #or not tEW.loadText():
            #tEW.doClose()
            #showError( self, SHORT_PROGRAM_NAME, _("Sorry, unable to open settings file") )
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: self.setDebugText( "Failed doViewSettings" )
        #else:
            #self.childWindows.append( tEW )
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: self.setDebugText( "Finished doViewSettings" )
        #self.setReadyStatus()
    # end of SwordManager.doViewSettings


    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( _("doViewLog()") )
            self.setDebugText( "doViewLog…" )

        self.setWaitStatus( _("doViewLog…") )
        filename = PROGRAM_NAME.replace('/','-').replace(':','_').replace('\\','_') + '_log.txt'
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setPathAndFile( self.loggingFolderPath, filename ) \
        or not tEW.loadText():
            tEW.doClose()
            showError( self, SHORT_PROGRAM_NAME, _("Sorry, unable to open log file") )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed doViewLog" )
        else:
            self.childWindows.append( tEW )
            #if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewLog" ) # Don't do this -- adds to the log immediately
        self.setReadyStatus()
    # end of SwordManager.doViewLog


    def doGotoInfo( self, event=None ):
        """
        Pop-up dialog giving goto/reference info.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("SwordManager.doGotoInfo( {} )").format( event ) )

        infoString = 'Current location:\n' \
                 + '\nBible Organisational System (BOS):\n' \
                 + '  Name: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemName() ) \
                 + '  Versification: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'versificationSystem' ) ) \
                 + '  Book Order: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'bookOrderSystem' ) ) \
                 + '  Book Names: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'punctuationSystem' ) ) \
                 + '  Books: {}'.format( self.genericBibleOrganisationalSystem.getBookList() )
        showInfo( self, 'Goto Information', infoString )
    # end of SwordManager.doGotoInfo


    def logUsage( self, p1, p2, p3 ):
        """
        Not required in this app.
        """
        pass
    # end of BOSManager.logUsage


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( _("doHelp()") )
        from Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += "\n\nBasic instructions:"
        helpInfo += "\n  Click on a tab to view that area of the Sword Manager."
        helpInfo += "\n\nKeyboard shortcuts:"
        #for name,shortcut in self.myKeyboardBindingsList:
            #helpInfo += "\n  {}\t{}".format( name, shortcut )
        #helpInfo += "\n\n  {}\t{}".format( 'Prev Verse', 'Alt+UpArrow' )
        #helpInfo += "\n  {}\t{}".format( 'Next Verse', 'Alt+DownArrow' )
        #helpInfo += "\n  {}\t{}".format( 'Prev Chapter', 'Alt+, (<)' )
        #helpInfo += "\n  {}\t{}".format( 'Next Chapter', 'Alt+. (>)' )
        #helpInfo += "\n  {}\t{}".format( 'Prev Book', 'Alt+[' )
        #helpInfo += "\n  {}\t{}".format( 'Next Book', 'Alt+]' )
        hb = HelpBox( self.rootWindow, SHORT_PROGRAM_NAME, helpInfo )
    # end of SwordManager.doHelp


    def doSubmitBug( self, event=None ):
        """
        Prompt the user to enter a bug report,
            collect other useful settings, etc.,
            and then send it all somewhere.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( _("doSubmitBug()") )

        if not self.internetAccessEnabled: # we need to warn
            showError( self, SHORT_PROGRAM_NAME, 'You need to allow Internet access first!' )
            return

        from About import AboutBox

        submitInfo = programNameVersion
        submitInfo += "\n  This program is not yet finished but we'll add this eventually!"
        ab = AboutBox( self.rootWindow, SHORT_PROGRAM_NAME, submitInfo )
    # end of SwordManager.doSubmitBug


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("doAbout()") )
        from About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nA display manager for Sword (from CrossWire) Bible modules." \
            + "\n\nThis is still an unfinished alpha test version, but it should allow you to display and set various parameters" \
            + " and then download and view Bible and commentary modules from the Internet." \
            + "\n\n{} is written in Python.".format( SHORT_PROGRAM_NAME ) \
            + " For more information see our web pages at Freely-Given.org/Software/BibleOrgSys and Freely-Given.org/Software/Biblelator and Freely-Given.org/Software/BibleDropBox/SwordModules.html"
        ab = AboutBox( self.rootWindow, SHORT_PROGRAM_NAME, aboutInfo )
    # end of SwordManager.doAbout


    #def doProjectClose( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( _("doProjectClose()") )
        #self.notWrittenYet()
    ## end of SwordManager.doProjectClose


    #def doWriteSettingsFile( self ):
        #"""
        #Update our program settings and save them.
        #"""
        #writeSettingsFile( self )
    ### end of SwordManager.writeSettingsFile


    def doCloseMyChildWindows( self ):
        """
        Save files first, and then close child windows.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("SwordManager.doCloseMyChildWindows()") )

        # Try to close edit windows first coz they might have work to save
        for appWin in self.childWindows[:]:
            if 'Editor' in appWin.genericWindowType and appWin.modified():
                appWin.doClose()
                #appWin.onCloseEditor( terminate=False )
                ##if appWin.saveChangesAutomatically: appWin.doSave( 'Auto from app close' )
                ##else: appWin.onCloseEditor()

        # See if they saved/closed them all
        haveModifications = False
        for appWin in self.childWindows:
            if 'Editor' in appWin.genericWindowType and appWin.modified():
                if appWin.modified(): # still???
                    haveModifications = True; break
        if haveModifications:
            showError( self, _("Save files"), _("You need to save or close your work first.") )
            return False

        # Should be able to close all apps now
        for appWin in self.childWindows[:]:
            appWin.doClose()
        return True
    # end of SwordManager.doCloseMyChildWindows


    def doCloseMe( self ):
        """
        Save files first, and then end the application.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("SwordManager.doCloseMe()") )
        elif BibleOrgSysGlobals.verbosityLevel > 0:
            print( _("{} is closing down…").format( SHORT_PROGRAM_NAME ) )

        #writeSettingsFile( self )
        if self.doCloseMyChildWindows():
            self.rootWindow.destroy()
    # end of SwordManager.doCloseMe
# end of class SwordManager



def openSwordManager( parent ):
    """
    Open the Sword Manager as a child window.

    This is used when the Sword Manager is used inside another program.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( _("SwordManager.openSwordManager( {} )").format( parent ) )

    myWin = tk.Toplevel( parent )
    application = SwordManager( myWin, parent.homeFolderPath, parent.loggingFolderPath, parent.iconImage, parent.settings )
# end of SwordManager.openSwordManager



def demo() -> None:
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( programNameVersion )

    # Set the window icon and title
    iconImage = tk.PhotoImage( file='Biblelator.gif' )
    tkRootWindow.tk.call( 'wm', 'iconphoto', tkRootWindow._w, iconImage )
    tkRootWindow.title( programNameVersion + ' ' + _('starting') + '…' )

    homeFolderPath = BibleOrgSysGlobals.findHomeFolderPath()
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, PROGRAM_NAME )
    settings.load()

    application = SwordManager( tkRootWindow, homeFolderPath, loggingFolderPath, iconImage, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of SwordManager.demo


def main( homeFolderPath, loggingFolderPath ):
    """
    Main program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    #print( 'FP main', repr(homeFolderPath), repr(loggingFolderPath) )

    numInstancesFound = 0
    if sys.platform == 'linux':
        myProcess = subprocess.Popen( ['ps','xa'], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        programOutputBytes, programErrorOutputBytes = myProcess.communicate()
        #print( 'pob', programOutputBytes, programErrorOutputBytes )
        #returnCode = myProcess.returncode
        programOutputString = programOutputBytes.decode( encoding='utf-8', errors='replace' ) if programOutputBytes else None
        programErrorOutputString = programErrorOutputBytes.decode( encoding='utf-8', errors='replace' ) if programErrorOutputBytes else None
        #print( 'processes', repr(programOutputString) )
        for line in programOutputString.split( '\n' ):
            if 'python' in line and PROGRAM_NAME+'.py' in line:
                if BibleOrgSysGlobals.debugFlag: print( 'Found in ps xa:', repr(line) )
                numInstancesFound += 1
        if programErrorOutputString: logging.critical( "ps xa got error: {}".format( programErrorOutputString ) )
    elif sys.platform in ( 'win32', 'win64', ):
        myProcess = subprocess.Popen( ['tasklist.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        programOutputBytes, programErrorOutputBytes = myProcess.communicate()
        #print( 'pob', programOutputBytes, programErrorOutputBytes )
        #returnCode = myProcess.returncode
        programOutputString = programOutputBytes.decode( encoding='utf-8', errors='replace' ) if programOutputBytes else None
        programErrorOutputString = programErrorOutputBytes.decode( encoding='utf-8', errors='replace' ) if programErrorOutputBytes else None
        #print( 'processes', repr(programOutputString) )
        for line in programOutputString.split( '\n' ):
            if PROGRAM_NAME+'.py' in line:
                if BibleOrgSysGlobals.debugFlag: print( 'Found in tasklist:', repr(line) )
                numInstancesFound += 1
        if programErrorOutputString: logging.critical( "tasklist got error: {}".format( programErrorOutputString ) )
    else: logging.critical( "Don't know how to check for already running instances in {}/{}.".format( sys.platform, os.name ) )
    if numInstancesFound > 1:
        import easygui
        logging.critical( "Found {} instances of {} running.".format( numInstancesFound, PROGRAM_NAME ) )
        result = easygui.ynbox('Seems {} might be already running: Continue?'.format( PROGRAM_NAME), programNameVersion, ('Yes', 'No'))
        if not result:
            logging.info( "Exiting as user requested." )
            sys.exit()

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) ) # e.g., 'x11'

    # Set the window icon and title
    iconImage = tk.PhotoImage( file='Biblelator.gif' )
    tkRootWindow.tk.call( 'wm', 'iconphoto', tkRootWindow._w, iconImage )
    tkRootWindow.title( programNameVersion + ' ' + _('starting') + '…' )
    application = SwordManager( tkRootWindow, homeFolderPath, loggingFolderPath, iconImage, None )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of SwordManager.main


if __name__ == '__main__':
    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    homeFolderPath = BibleOrgSysGlobals.findHomeFolderPath()
    if homeFolderPath[-1] not in '/\\': homeFolderPath += '/'
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, loggingFolderPath=loggingFolderPath )
    parser.add_argument( '-o', '--override', type=str, metavar='INIFilename', dest='override', help="override use of Biblelator.ini set-up" )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )
    #print( BibleOrgSysGlobals.commandLineArguments ); halt

    if BibleOrgSysGlobals.debugFlag:
        print( _("Platform is"), sys.platform ) # e.g., 'linux,'win32'
        print( _("OS name is"), os.name ) # e.g., 'posix','nt'
        if sys.platform == "linux": print( _("OS uname is"), os.uname() ) # gives about five fields
        print( _("Running main…") )

    main( homeFolderPath, loggingFolderPath )

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of SwordManager.py
