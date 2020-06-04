#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BOSManager.py
#
# BOS (Bible Organisational System) manager program
#
# Copyright (C) 2016-2020 Robert Hunt
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
import sys
import os
import logging
import subprocess
import multiprocessing

import tkinter as tk
#from tkinter.filedialog import Open, Directory, askopenfilename #, SaveAs
from tkinter.ttk import Style, Frame, Button, Scrollbar, Label, Notebook
from tkinter.scrolledtext import ScrolledText

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint
from BibleOrgSys.Reference.BibleOrganisationalSystems import BibleOrganisationalSystems, BibleOrganisationalSystem
from BibleOrgSys.Reference.BibleVersificationSystems import BibleVersificationSystems
from BibleOrgSys.Reference.BibleBookOrders import BibleBookOrderSystems
from BibleOrgSys.Reference.BibleBooksNames import BibleBooksNamesSystems
from BibleOrgSys.Reference.BiblePunctuationSystems import BiblePunctuationSystems
from BibleOrgSys.Reference.BibleStylesheets import BibleStylesheet

# Biblelator imports
if __name__ == '__main__':
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator.BiblelatorGlobals import DEFAULT, tkSTART, MAX_PSEUDOVERSES, errorBeep, \
        DATAFILES_FOLDERPATH, \
        DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, \
        DEFAULT_KEY_BINDING_DICT, \
        parseWindowGeometry, assembleWindowGeometryFromList, centreWindow, \
        parseWindowSize
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showWarning, showInfo
from Biblelator.Dialogs.BiblelatorDialogs import SelectResourceBoxDialog, GetNewProjectNameDialog, \
                                CreateNewProjectFilesDialog, GetNewCollectionNameDialog, \
                                BookNameDialog, NumberButtonDialog
from Biblelator.Helpers.BiblelatorHelpers import mapReferencesVerseKey, createEmptyUSFMBooks
from Biblelator.Settings.Settings import ApplicationSettings
from Biblelator.Settings.BiblelatorSettingsFunctions import parseAndApplySettings, writeSettingsFile, \
        saveNewWindowSetup, deleteExistingWindowSetup, applyGivenWindowsSettings, viewSettings
from Biblelator.Windows.TextBoxes import BEntry, BCombobox
from Biblelator.Windows.ChildWindows import ChildWindows
#from BibleResourceWindows import SwordBibleResourceWindow, InternalBibleResourceWindow, DBPBibleResourceWindow
#from BibleResourceCollection import BibleResourceCollectionWindow
#from BibleReferenceCollection import BibleReferenceCollectionWindow
#from LexiconResourceWindows import BibleLexiconResourceWindow
from Biblelator.Windows.TextEditWindow import TextEditWindow
#from USFMEditWindow import USFMEditWindow
#from ESFMEditWindow import ESFMEditWindow


LAST_MODIFIED_DATE = '2020-05-01' # by RJH
SHORT_PROGRAM_NAME = "BOSManager"
PROGRAM_NAME = "BOS Manager"
PROGRAM_VERSION = '0.07' # Separate versioning from Biblelator
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


MAIN_APP_NAME = 'Biblelator'
# Default window size settings (Note: X=width, Y=height)
INITIAL_MAIN_SIZE, INITIAL_MAIN_SIZE_DEBUG, MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE = '607x376', '607x460', '550x375', '700x600'



class BOSManager( Frame ):
    """
    This is the main application window (well, actually a frame in the root toplevel window).

    Its main job is to keep track of self.currentVerseKey (and self.currentVerseKeyGroup)
        and use that to inform child windows of BCV movements.
    """
    global settings
    def __init__( self, rootWindow, homeFolderpath, loggingFolderpath, iconImage, settings ):
        """
        Main app initialisation function.

        Creates the main menu and toolbar which includes the main BCV (book/chapter/verse) selector.
        """
        vPrint( 'Never', debuggingThisModule, _("BOSManager.__init__( {}, {}, {}, … )").format( rootWindow, homeFolderpath, loggingFolderpath ) )
        self.rootWindow, self.homeFolderpath, self.loggingFolderpath, self.iconImage, self.settings = rootWindow, homeFolderpath, loggingFolderpath, iconImage, settings
        self.isStarting = True

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

        dPrint( 'Quiet', debuggingThisModule, "Button default font", Style().lookup('TButton', 'font') )
        dPrint( 'Quiet', debuggingThisModule, "Label default font", Style().lookup('TLabel', 'font') )

        # We rely on the parseAndApplySettings() call below to do this
        ## Set-up our Bible system and our callables
        #self.genericBibleOrganisationalSystemName = 'GENERIC-KJV-ENG' # Handles all bookcodes
        #self.setGenericBibleOrganisationalSystem( self.genericBibleOrganisationalSystemName )

        self.stylesheet = BibleStylesheet().loadDefault()
        super().__init__( self.rootWindow )
        self.pack()

        self.rootWindow.protocol( 'WM_DELETE_WINDOW', self.doCloseMe ) # Catch when app is closed

        self.childWindows = ChildWindows( self )

        self.createStatusBar()

        ## Create our display text box
        #self.textBox = ScrolledText( self.rootWindow, bg='yellow' )#style='DebugText.TScrolledText' )
        #self.textBox.pack( side=tk.TOP, fill=tk.BOTH )
        ##self.debugTextBox.tag_configure( 'emp', background='yellow', font='helvetica 12 bold', relief='tk.RAISED' )
        #self.textBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.textBox.insert( tk.END, 'Main Text Box:' )

        if BibleOrgSysGlobals.debugFlag: # Create a scrolling debug box
            self.lastDebugMessage = None
            #Style().configure('DebugText.TScrolledText', padding=2, background='orange')
            self.debugTextBox = ScrolledText( self.rootWindow, bg='orange' )#style='DebugText.TScrolledText' )
            self.debugTextBox.pack( side=tk.BOTTOM, fill=tk.BOTH )
            #self.debugTextBox.tag_configure( 'emp', background='yellow', font='helvetica 12 bold', relief='tk.RAISED' )
            self.debugTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
            if debuggingThisModule: self.setDebugText( "Starting up…" )

        self.keyBindingDict = DEFAULT_KEY_BINDING_DICT
        self.myKeyboardBindingsList = []
        self.recentFiles = []

        # Read and apply the saved settings
        if BibleOrgSysGlobals.commandLineArguments.override is None:
            self.INIname = MAIN_APP_NAME # We use the Biblelator settings
            vPrint( 'Never', debuggingThisModule, "Using default {!r} ini file".format( self.INIname ) )
        else:
            self.INIname = BibleOrgSysGlobals.commandLineArguments.override
            vPrint( 'Normal', debuggingThisModule, _("Using settings from user-specified {!r} ini file").format( self.INIname ) )
        #self.settings = ApplicationSettings( self.homeFolderpath, DATA_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, self.INIname )
        #self.settings.load()
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
        self.createNotebook()

        # See if there's any developer messages
        if self.internetAccessEnabled and self.checkForDeveloperMessagesEnabled:
            self.doCheckForDeveloperMessages()

        self.rootWindow.title( programNameVersion )
        self.minimumSize = MINIMUM_MAIN_SIZE
        self.rootWindow.minsize( *parseWindowSize( self.minimumSize ) )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "BOSManager.__init__ finished." )
        self.isStarting = False
        self.setReadyStatus()
    # end of BOSManager.__init__


    def setGenericBibleOrganisationalSystem( self, BOSname ):
        """
        We usually use a fairly generic BibleOrganisationalSystem (BOS) to ensure
            that it contains all the books that we might ever want to navigate to.
        """
        vPrint( 'Never', debuggingThisModule, _("setGenericBibleOrganisationalSystem( {} )").format( BOSname ) )

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
        #dPrint( 'Quiet', debuggingThisModule, self.genericBookList )
        self.offsetGenesis = self.genericBookList.index( 'GEN' )
        #dPrint( 'Quiet', debuggingThisModule, 'offsetGenesis', self.offsetGenesis )
        self.bookNumberTable = {}
        for j,BBB in enumerate(self.genericBookList):
            k = j + 1 - self.offsetGenesis
            nBBB = BibleOrgSysGlobals.loadedBibleBooksCodes.getReferenceNumber( BBB )
            #dPrint( 'Quiet', debuggingThisModule, BBB, nBBB )
            self.bookNumberTable[k] = BBB
            self.bookNumberTable[BBB] = k
        #dPrint( 'Quiet', debuggingThisModule, self.bookNumberTable )
    # end of BOSManager.setGenericBibleOrganisationalSystem


    def createNormalMenuBar( self ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("createNormalMenuBar()…") )

        #self.win = Toplevel( self )
        self.menubar = tk.Menu( self.rootWindow )
        #self.rootWindow['menu'] = self.menubar
        self.rootWindow.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        ##fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        #fileNewSubmenu = tk.Menu( fileMenu, tearoff=False )
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

        if 0:
            #editMenu = tk.Menu( self.menubar, tearoff=False )
            #self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
            #editMenu.add_command( label=_('Find…'), underline=0, command=self.notWrittenYet )
            #editMenu.add_command( label=_('Replace…'), underline=0, command=self.notWrittenYet )

            booksCodesMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=booksCodesMenu, label=_('Codes'), underline=0 )
            booksCodesMenu.add_command( label=_('View…'), underline=-1, command=self.notWrittenYet )
            booksCodesMenu.add_separator()
            booksCodesMenu.add_command( label=_('Info…'), underline=0, command=self.doGotoInfo )

            ordersMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=ordersMenu, label=_('Orders'), underline=0 )
            ordersMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
            ordersMenu.add_separator()
            ordersMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

            namesMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=namesMenu, label=_('Names'), underline=0 )
            submenuBibleResourceType = tk.Menu( namesMenu, tearoff=False )
            namesMenu.add_command( label=_('View…'), underline=5, command=self.notWrittenYet )
            namesMenu.add_separator()
            namesMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

            versificationsMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=versificationsMenu, label=_('Versifications'), underline=0 )
            versificationsMenu.add_command( label=_('View…'), underline=0, command=self.notWrittenYet )
            versificationsMenu.add_separator()
            versificationsMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

            orgsMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=orgsMenu, label=_('Bibles'), underline=0 )
            orgsMenu.add_command( label=_('View…'), underline=0, command=self.notWrittenYet )
            orgsMenu.add_separator()
            orgsMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

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
    # end of BOSManager.createNormalMenuBar

    def createTouchMenuBar( self ) -> None:
        """
        """
        vPrint( 'Never', debuggingThisModule, _("createTouchMenuBar()…") )
        if debuggingThisModule or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
            assert self.touchMode

        self.createNormalMenuBar()
    # end of BOSManager.createTouchMenuBar


    def createNormalNavigationBar( self ) -> None:
        """
        """
        vPrint( 'Never', debuggingThisModule, _("createNormalNavigationBar()…") )

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
        #dPrint( 'Quiet', debuggingThisModule, "maxChapters", self.maxChaptersThisBook )
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
        #dPrint( 'Quiet', debuggingThisModule, "maxChapters", self.maxChaptersThisBook )
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
        #dPrint( 'Quiet', debuggingThisModule, "maxVerses", self.maxVersesThisChapter )
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
    # end of BOSManager.createNormalNavigationBar

    def createTouchNavigationBar( self ) -> None:
        """
        """
        vPrint( 'Never', debuggingThisModule, _("createTouchNavigationBar()…") )
        if debuggingThisModule or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
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
        #dPrint( 'Quiet', debuggingThisModule, "maxChapters", self.maxChaptersThisBook )
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
        #dPrint( 'Quiet', debuggingThisModule, "maxChapters", self.maxChaptersThisBook )
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
        #dPrint( 'Quiet', debuggingThisModule, "maxVerses", self.maxVersesThisChapter )
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
    # end of BOSManager.createTouchNavigationBar


    def createToolBar( self ):
        """
        Create a tool bar containing several helpful buttons at the top of the main window.
        """
        vPrint( 'Never', debuggingThisModule, _("createToolBar()…") )

        return

        xPad, yPad = 6, 8

        Style().configure( 'ToolBar.TFrame', background='green' )
        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='ToolBar.TFrame' )

        Style().configure( 'ShowAll.TButton', background='lightgreen' )
        Style().configure( 'HideResources.TButton', background='pink' )
        Style().configure( 'HideAll.TButton', background='orange' )

        Button( toolbar, text='Show All', style='ShowAll.TButton', command=self.doShowAll ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        Button( toolbar, text='Hide Resources', style='HideResources.TButton', command=self.doHideAllResources ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        Button( toolbar, text='Hide All', style='HideAll.TButton', command=self.doHideAll ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        #Button( toolbar, text='Bring All', command=self.doBringAll ).pack( side=tk.LEFT, padx=2, pady=2 )

        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of BOSManager.createToolBar


    def createNotebook( self ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("createToolBar()…") )

        self.notebook = Notebook( self )

        # Adding Frames as pages for the ttk.Notebook

        # Bible books codes page
        vPrint( 'Quiet', debuggingThisModule, "Create codes page" )
        self.BibleBooksCodesList = BibleOrgSysGlobals.loadedBibleBooksCodes.getAllReferenceAbbreviations()
        self.codesPage = Frame( self.notebook )
        codesLabel = Label( self.codesPage, text="Books Codes ({})".format( len(self.BibleBooksCodesList) ) )
        codesLabel.grid( row=0, column=0, columnspan=2 )
        searchBBBLabel = Label( self.codesPage, text=_("Search BBB:") )
        searchBBBLabel.grid( row=1, column=0 )
        self.codesBBBSearch = BEntry( self.codesPage, width=5 )
        self.codesBBBSearch.bind( '<Return>', self.searchBBBCode )
        self.codesBBBSearch.grid( row=1, column=1 )
        searchLabel = Label( self.codesPage, text=_("Search (all):") )
        searchLabel.grid( row=2, column=0 )
        self.codesSearch = BEntry( self.codesPage, width=8 )
        self.codesSearch.bind( '<Return>', self.searchCode )
        self.codesSearch.grid( row=2, column=1 )
        sbar = Scrollbar( self.codesPage )
        self.codesListbox = tk.Listbox( self.codesPage, width=5, relief=tk.SUNKEN )
        sbar.configure( command=self.codesListbox.yview )
        self.codesListbox.configure( yscrollcommand=sbar.set )
        self.codesListbox.bind('<<ListboxSelect>>', self.gotoNewCode )
        #self.codesListbox.bind( '<Return>', self.gotoNewCode )
        sbar.grid( row=0, column=3, rowspan=3, sticky=tk.N+tk.S )
        self.codesListbox.grid( row=0, column=2, rowspan=3, sticky=tk.N+tk.S )
        self.codeTextBox = ScrolledText( self.codesPage, bg='lightblue' )
        self.codeTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.codeTextBox.insert( tk.END, 'Codes' )
        self.codeTextBox.grid( row=0, column=4, rowspan=3, sticky=tk.N+tk.S+tk.E )
        for BBB in self.BibleBooksCodesList:
            self.codesListbox.insert( tk.END, BBB ) # fill the listbox
        self.codesSearch.insert( tk.END, 'GEN' )
        self.searchCode( None ) # Go to the above
        self.codesSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible punctuations systems page
        vPrint( 'Quiet', debuggingThisModule, "Create punct page" )
        self.BiblePunctuationSystems = BiblePunctuationSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BiblePunctuationsList = sorted( self.BiblePunctuationSystems.getAvailablePunctuationSystemNames() )
        self.punctuationPage = Frame( self.notebook )
        punctuationLabel = Label( self.punctuationPage, text="Books Punctuations ({})".format( len(self.BiblePunctuationsList) ) )
        punctuationLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.punctuationPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.punctuationsSearch = BEntry( self.punctuationPage, width=12 )
        self.punctuationsSearch.bind( '<Return>', self.searchPunctuation )
        self.punctuationsSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.punctuationPage )
        self.punctuationsListbox = tk.Listbox( self.punctuationPage, width=12, relief=tk.SUNKEN )
        sbar.configure( command=self.punctuationsListbox.yview )
        self.punctuationsListbox.configure( yscrollcommand=sbar.set )
        self.punctuationsListbox.bind('<<ListboxSelect>>', self.gotoNewPunctuation )
        #self.punctuationListbox.bind( '<Return>', self.gotoNewPunctuation )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.punctuationsListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.punctuationTextBox = ScrolledText( self.punctuationPage, bg='lightgreen' )
        self.punctuationTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.punctuationTextBox.insert( tk.END, 'Punctuations' )
        self.punctuationTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for pName in self.BiblePunctuationsList:
            self.punctuationsListbox.insert( tk.END, pName ) # fill the listbox
        self.punctuationsSearch.insert( tk.END, 'English' )
        self.searchPunctuation( None ) # Go to the above
        self.punctuationsSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible versification systems page
        vPrint( 'Quiet', debuggingThisModule, "Create vers page" )
        self.BibleVersificationsSystems = BibleVersificationSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BibleVersificationsSystemsList = sorted( self.BibleVersificationsSystems.getAvailableVersificationSystemNames() )
        self.versificationsPage = Frame( self.notebook )
        versificationsLabel = Label( self.versificationsPage, text="Bible Versification Systems ({})".format( len(self.BibleVersificationsSystemsList) ) )
        versificationsLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.versificationsPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.versificationsSearch = BEntry( self.versificationsPage, width=15 )
        self.versificationsSearch.bind( '<Return>', self.searchVersification )
        self.versificationsSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.versificationsPage )
        self.versificationsListbox = tk.Listbox( self.versificationsPage, width=15, relief=tk.SUNKEN )
        sbar.configure( command=self.versificationsListbox.yview )
        self.versificationsListbox.configure( yscrollcommand=sbar.set )
        self.versificationsListbox.bind('<<ListboxSelect>>', self.gotoNewVersification )
        #self.versificationsListbox.bind( '<Return>', self.gotoNewVersification )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.versificationsListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.versificationTextBox = ScrolledText( self.versificationsPage, bg='orange' )
        self.versificationTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.versificationTextBox.insert( tk.END, 'Versifications' )
        self.versificationTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for vName in self.BibleVersificationsSystemsList:
            self.versificationsListbox.insert( tk.END, vName ) # fill the listbox
        self.versificationsSearch.insert( tk.END, 'KJV' ) # Select KJV
        self.searchVersification( None ) # Go to KJV
        self.versificationsSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible versification mappings page
        vPrint( 'Quiet', debuggingThisModule, "Create mappings page" )
        #self.BibleMappingsSystems = BibleMappingSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BibleMappingsSystemsList = []
        self.mappingsPage = Frame( self.notebook )
        mappingsLabel = Label( self.mappingsPage, text="Mapping Mappings ({})".format( len(self.BibleMappingsSystemsList) ) )
        mappingsLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.mappingsPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.mappingsSearch = BEntry( self.mappingsPage, width=15 )
        self.mappingsSearch.bind( '<Return>', self.searchMapping )
        self.mappingsSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.mappingsPage )
        self.mappingsListbox = tk.Listbox( self.mappingsPage, width=15, relief=tk.SUNKEN )
        sbar.configure( command=self.mappingsListbox.yview )
        self.mappingsListbox.configure( yscrollcommand=sbar.set )
        self.mappingsListbox.bind('<<ListboxSelect>>', self.gotoNewMapping )
        #self.mappingsListbox.bind( '<Return>', self.gotoNewMapping )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.mappingsListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.mappingTextBox = ScrolledText( self.mappingsPage, bg='brown' )
        self.mappingTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.mappingTextBox.insert( tk.END, 'Mappings' )
        self.mappingTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for mName in self.BibleMappingsSystemsList:
            self.mappingsListbox.insert( tk.END, mName ) # fill the listbox
        self.mappingsSearch.insert( tk.END, 'KJV' ) # Select KJV
        self.searchMapping( None ) # Go to KJV
        self.mappingsSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible book order systems page
        vPrint( 'Quiet', debuggingThisModule, "Create orders page" )
        self.BibleOrdersSystems = BibleBookOrderSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BibleOrdersSystemsList = sorted( self.BibleOrdersSystems.getAvailableBookOrderSystemNames() )
        self.ordersPage = Frame( self.notebook )
        ordersLabel = Label( self.ordersPage, text="Bible Order Systems ({})".format( len(self.BibleOrdersSystemsList) ) )
        ordersLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.ordersPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.ordersSearch = BEntry( self.ordersPage, width=15 )
        self.ordersSearch.bind( '<Return>', self.searchOrder )
        self.ordersSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.ordersPage )
        self.ordersListbox = tk.Listbox( self.ordersPage, width=15, relief=tk.SUNKEN )
        sbar.configure( command=self.ordersListbox.yview )
        self.ordersListbox.configure( yscrollcommand=sbar.set )
        self.ordersListbox.bind('<<ListboxSelect>>', self.gotoNewOrder )
        #self.ordersListbox.bind( '<Return>', self.gotoNewOrder )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.ordersListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.orderTextBox = ScrolledText( self.ordersPage, bg='yellow' )
        self.orderTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.orderTextBox.insert( tk.END, 'Orders' )
        self.orderTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for oName in self.BibleOrdersSystemsList:
            self.ordersListbox.insert( tk.END, oName ) # fill the listbox
        self.ordersSearch.insert( tk.END, 'LutheranBible' )
        self.searchOrder( None ) # Go to the above
        self.ordersSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible book name systems page
        vPrint( 'Quiet', debuggingThisModule, "Create names page" )
        self.BibleNamesSystems = BibleBooksNamesSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BibleNamesSystemsList = sorted( self.BibleNamesSystems.getAvailableBooksNamesSystemNames() )
        self.namesPage = Frame( self.notebook )
        namesLabel = Label( self.namesPage, text="Bible Name Systems ({})".format( len(self.BibleNamesSystemsList) ) )
        namesLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.namesPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.namesSearch = BEntry( self.namesPage, width=15 )
        self.namesSearch.bind( '<Return>', self.searchName )
        self.namesSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.namesPage )
        self.namesListbox = tk.Listbox( self.namesPage, width=15, relief=tk.SUNKEN )
        sbar.configure( command=self.namesListbox.yview )
        self.namesListbox.configure( yscrollcommand=sbar.set )
        self.namesListbox.bind('<<ListboxSelect>>', self.gotoNewName )
        #self.namesListbox.bind( '<Return>', self.gotoNewName )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.namesListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.nameTextBox = ScrolledText( self.namesPage, bg='orange' )
        self.nameTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.nameTextBox.insert( tk.END, 'Names' )
        self.nameTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for nName in self.BibleNamesSystemsList:
            self.namesListbox.insert( tk.END, nName ) # fill the listbox
        self.namesSearch.insert( tk.END, 'eng_traditional' )
        self.searchName( None ) # Go to the above
        self.namesSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible organisational systems page
        vPrint( 'Quiet', debuggingThisModule, "Create Bibles page" )
        self.BibleOrganisationalSystems = BibleOrganisationalSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BibleOrganisationalSystemsList = sorted( self.BibleOrganisationalSystems.getAvailableOrganisationalSystemNames() )
        self.organisationsPage = Frame( self.notebook )
        organisationsLabel = Label( self.organisationsPage, text="Bible Organisation Systems ({})".format( len(self.BibleOrganisationalSystemsList) ) )
        organisationsLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.organisationsPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.organisationsSearch = BEntry( self.organisationsPage, width=18 )
        self.organisationsSearch.bind( '<Return>', self.searchOrganisation )
        self.organisationsSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.organisationsPage )
        self.organisationsListbox = tk.Listbox( self.organisationsPage, width=18, relief=tk.SUNKEN )
        sbar.configure( command=self.organisationsListbox.yview )
        self.organisationsListbox.configure( yscrollcommand=sbar.set )
        self.organisationsListbox.bind('<<ListboxSelect>>', self.gotoNewOrganisation )
        #self.organisationsListbox.bind( '<Return>', self.gotoNewOrganisation )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.organisationsListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.organisationTextBox = ScrolledText( self.organisationsPage, bg='pink' )
        self.organisationTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.organisationTextBox.insert( tk.END, 'Organisations' )
        self.organisationTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for orgName in self.BibleOrganisationalSystemsList:
            self.organisationsListbox.insert( tk.END, orgName ) # fill the listbox
        self.organisationsSearch.insert( tk.END, 'RSV71' )
        self.searchOrganisation( None ) # Go to above
        self.organisationsSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible reference systems page
        vPrint( 'Quiet', debuggingThisModule, "Create refs page" )
        #self.BibleReferenceSystems = BibleReferenceSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BibleReferenceSystemsList = []
        self.referencesPage = Frame( self.notebook )
        referencesLabel = Label( self.referencesPage, text="Bible Reference Systems ({})".format( len(self.BibleReferenceSystemsList) ) )
        referencesLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.referencesPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.referenceSearch = BEntry( self.referencesPage, width=18 )
        self.referenceSearch.bind( '<Return>', self.searchReference )
        self.referenceSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.referencesPage )
        self.referencesListbox = tk.Listbox( self.referencesPage, width=18, relief=tk.SUNKEN )
        sbar.configure( command=self.referencesListbox.yview )
        self.referencesListbox.configure( yscrollcommand=sbar.set )
        self.referencesListbox.bind('<<ListboxSelect>>', self.gotoNewReference )
        #self.referencesListbox.bind( '<Return>', self.gotoNewReference )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.referencesListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.referenceTextBox = ScrolledText( self.referencesPage, bg='orange' )
        self.referenceTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.referenceTextBox.insert( tk.END, 'References' )
        self.referenceTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for rName in self.BibleReferenceSystemsList:
            self.referencesListbox.insert( tk.END, rName ) # fill the listbox
        self.referenceSearch.insert( tk.END, 'KJV' ) # Select KJV
        self.searchReference( None ) # Go to KJV
        self.referenceSearch.delete( 0, tk.END ) # Clear the search box again

        # Bible stylesheet systems page
        vPrint( 'Quiet', debuggingThisModule, "Create stylesheets page" )
        #self.BibleStylesheetSystems = BibleStylesheetSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.BibleStylesheetSystemsList = []
        self.stylesheetsPage = Frame( self.notebook )
        stylesheetsLabel = Label( self.stylesheetsPage, text="Bible Stylesheet Systems ({})".format( len(self.BibleStylesheetSystemsList) ) )
        stylesheetsLabel.grid( row=0, column=0, columnspan=2 )
        searchLabel = Label( self.stylesheetsPage, text=_("Search:") )
        searchLabel.grid( row=1, column=0 )
        self.stylesheetSearch = BEntry( self.stylesheetsPage, width=18 )
        self.stylesheetSearch.bind( '<Return>', self.searchOrganisation )
        self.stylesheetSearch.grid( row=1, column=1 )
        sbar = Scrollbar( self.stylesheetsPage )
        self.stylesheetsListbox = tk.Listbox( self.stylesheetsPage, width=18, relief=tk.SUNKEN )
        sbar.configure( command=self.stylesheetsListbox.yview )
        self.stylesheetsListbox.configure( yscrollcommand=sbar.set )
        self.stylesheetsListbox.bind('<<ListboxSelect>>', self.gotoNewOrganisation )
        #self.stylesheetsListbox.bind( '<Return>', self.gotoNewOrganisation )
        sbar.grid( row=0, column=3, rowspan=2, sticky=tk.N+tk.S )
        self.stylesheetsListbox.grid( row=0, column=2, rowspan=2, sticky=tk.N+tk.S )
        self.stylesheetTextBox = ScrolledText( self.stylesheetsPage, bg='orange' )
        self.stylesheetTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
        #self.stylesheetTextBox.insert( tk.END, 'Organisations' )
        self.stylesheetTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
        for ssName in self.BibleStylesheetSystemsList:
            self.stylesheetsListbox.insert( tk.END, ssName ) # fill the listbox
        self.stylesheetSearch.insert( tk.END, 'KJV' ) # Select KJV
        self.searchOrganisation( None ) # Go to KJV
        self.stylesheetSearch.delete( 0, tk.END ) # Clear the search box again

        vPrint( 'Quiet', debuggingThisModule, "Add all pages" )
        self.notebook.add( self.codesPage, text=_("Codes") )
        self.notebook.add( self.punctuationPage, text=_("Punctuation") )
        self.notebook.add( self.versificationsPage, text=_("Versifications") )
        self.notebook.add( self.mappingsPage, text=_("Mappings") )
        self.notebook.add( self.ordersPage, text=_("Orders") )
        self.notebook.add( self.namesPage, text=_("Names") )
        self.notebook.add( self.organisationsPage, text=_("Bibles") )
        self.notebook.add( self.referencesPage, text=_("References") )
        self.notebook.add( self.stylesheetsPage, text=_("StyleSheets") )
        self.notebook.pack( expand=tk.YES, fill=tk.BOTH )
    # end of BOSManager.createNotebook


    def halt( self ):
        """
        Halts the program immediately without saving any files or settings.
        Only used in debug mode.
        """
        logging.critical( "User selected HALT in DEBUG MODE. Not saving any files or settings!" )
        self.quit()
    # end of BOSManager.halt


    def createDebugToolBar( self ):
        """
        Create a debug tool bar containing several additional buttons at the top of the main window.
        """
        vPrint( 'Never', debuggingThisModule, _("createDebugToolBar()…") )

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
    # end of BOSManager.createDebugToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        vPrint( 'Never', debuggingThisModule, _("createStatusBar()…") )

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
    # end of BOSManager.createStatusBar


    def createMainKeyboardBindings( self ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("createMainKeyboardBindings()…") )

        self.myKeyboardBindingsList = []
        for name,command in ( ('Help',self.doHelp), ('About',self.doAbout), ('Quit',self.doCloseMe) ):
            if name in self.keyBindingDict:
                for keyCode in self.keyBindingDict[name][1:]:
                    #dPrint( 'Quiet', debuggingThisModule, "Bind {} for {}".format( repr(keyCode), repr(name) ) )
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
    # end of BOSManager.createMainKeyboardBindings()


    #def addRecentFile( self, threeTuple ):
        #"""
        #Puts most recent first
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("addRecentFile( {} )").format( threeTuple ) )
            #assert len(threeTuple) == 3

        #try: self.recentFiles.remove( threeTuple ) # Remove a duplicate if present
        #except ValueError: pass
        #self.recentFiles.insert( 0, threeTuple ) # Put this one at the beginning of the lis
        #if len(self.recentFiles)>MAX_RECENT_FILES: self.recentFiles.pop() # Remove the last one if necessary
        #self.createNormalMenuBar()
    ## end of BOSManager.addRecentFile()


    def notWrittenYet( self ):
        errorBeep()
        showError( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of BOSManager.notWrittenYet


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        vPrint( 'Never', debuggingThisModule, _("setStatus( {!r} )").format( newStatusText ) )

        #dPrint( 'Quiet', debuggingThisModule, "SB is", repr( self.statusTextVariable.get() ) )
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
    # end of BOSManager.setStatus

    def setErrorStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        vPrint( 'Never', debuggingThisModule, _("setErrorStatus( {!r} )").format( newStatusText ) )

        #self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='StatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( 'StatusBar.TLabel', foreground='yellow', background='red' )
        self.update()
    # end of BOSManager.setErrorStatus

    def setWaitStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        vPrint( 'Never', debuggingThisModule, _("setWaitStatus( {!r} )").format( newStatusText ) )

        self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='StatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( 'StatusBar.TLabel', foreground='black', background='DarkOrange1' )
        self.update()
    # end of BOSManager.setWaitStatus

    def setReadyStatus( self ):
        """
        Sets the status line to "Ready"
            and sets the cursor to the normal cursor
        unless we're still starting
            (this covers any slow start-up functions that don't yet set helpful statuses)
        """
        if self.isStarting: self.setWaitStatus( _("Starting up…") )
        else: # we really are ready
            #self.statusTextLabel.configure( style='StatusBar.TLabelReady' )
            self.setStatus( _("Ready") )
            Style().configure( 'StatusBar.TLabel', foreground='yellow', background='forest green' )
            self.configure( cursor='' )
    # end of BOSManager.setReadyStatus


    def setDebugText( self, newMessage=None ):
        """
        """
        if debuggingThisModule:
            #dPrint( 'Quiet', debuggingThisModule, _("setDebugText( {!r} )").format( newMessage ) )
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
    # end of BOSManager.setDebugText


    def doChangeTheme( self, newThemeName ):
        """
        Set the window theme to the given scheme.
        """
        if BibleOrgSysGlobals.debugFlag:
            vPrint( 'Quiet', debuggingThisModule, _("doChangeTheme( {!r} )").format( newThemeName ) )
            assert newThemeName
            if debuggingThisModule: self.setDebugText( 'Set theme to {!r}'.format( newThemeName ) )

        self.themeName = newThemeName
        try:
            self.style.theme_use( newThemeName )
        except tk.TclError as err:
            showError( self, 'Error', err )
    # end of BOSManager.doChangeTheme


    def searchBBBCode( self, event ):
        """
        Search for the given text in the 3-character (uppercase or numeric) book codes.
        """
        enteredText = self.codesSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchBBBCode( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchBBBCode…" )

        if not enteredText: return

        eTU = enteredText.upper()
        if len(eTU)==3 and eTU!=enteredText and eTU in self.BibleBooksCodesList:
            self.setErrorStatus( "Converted entered book code to UPPER CASE" )
            enteredText = eTU

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
    # end of BOSManager.searchBBBCode


    def searchCode( self, event ):
        """
        Search for the given text through all possible book code types.
        """
        enteredText = self.codesSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchCode( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchCode…" )

        if not enteredText: return

        eTU = enteredText.upper()
        if len(eTU)==3 and eTU!=enteredText and eTU in self.BibleBooksCodesList:
            self.setErrorStatus( "Converted entered book code to UPPER CASE" )
            enteredText = eTU

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
        vPrint( 'Never', debuggingThisModule, _("gotoNewCode( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewCode…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.codesListbox.get(int(i)) for i in self.codesListbox.curselection()] )

        vPrint( 'Quiet', debuggingThisModule, "code cursel", repr(self.codesListbox.curselection()) )
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


    def searchPunctuation( self, event ):
        """
        """
        enteredText = self.punctuationsSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchPunctuation( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchPunctuation…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Books punctuation system names must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books punctuation system names must have no spaces" ); return
        elif enteredText not in self.BiblePunctuationsList:
            self.setErrorStatus( "Unknown {!r} punctuation system name".format( enteredText ) )
            return

        # Must be ok
        self.punctuationSystemName = enteredText
        index = self.BiblePunctuationsList.index( self.punctuationSystemName )

        # Select it in the listbox
        self.punctuationsListbox.select_set( index )
        self.punctuationsListbox.see( index )
        self.punctuationsListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewPunctuation below
    # end of BOSManager.searchPunctuation


    def gotoNewPunctuation( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewPunctuation( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewPunctuation…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.punctuationsListbox.get(int(i)) for i in self.punctuationsListbox.curselection()] )

        vPrint( 'Quiet', debuggingThisModule, "punct cursel", repr(self.punctuationsListbox.curselection()) )
        index = int( self.punctuationsListbox.curselection()[0] ) # Top one selected
        self.punctuationSystemName = self.punctuationsListbox.get( index )
        punctuationDict =  self.BiblePunctuationSystems.getPunctuationSystem( self.punctuationSystemName )

        # Clear the text box
        self.punctuationTextBox.configure( state=tk.NORMAL )
        self.punctuationTextBox.delete( tkSTART, tk.END )
        self.punctuationTextBox.insert( tk.END, '{}\n\n'.format( self.punctuationSystemName ) )
        #self.punctuationTextBox.insert( tk.END, '{}\n\n'.format( punctuationDict['nameEnglish'] ) )
        for field,value in sorted( punctuationDict.items() ):
            #if field not in ( 'referenceNumber', 'nameEnglish', ):
                self.punctuationTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewPunctuation


    def searchVersification( self, event ):
        """
        """
        enteredText = self.versificationsSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchVersification( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchVersification…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Books versifications must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books versifications must have no spaces" ); return
        elif enteredText not in self.BibleVersificationsSystemsList:
            self.setErrorStatus( "Unknown {!r} book versification".format( enteredText ) )
            return

        # Must be ok
        self.versificationSystemName = enteredText
        index = self.BibleVersificationsSystemsList.index( self.versificationSystemName )

        # Select it in the listbox
        self.versificationsListbox.select_set( index )
        self.versificationsListbox.see( index )
        self.versificationsListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewVersification below
    # end of BOSManager.searchVersification


    def gotoNewVersification( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewVersification( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewVersification…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.versificationsListbox.get(int(i)) for i in self.versificationsListbox.curselection()] )

        vPrint( 'Quiet', debuggingThisModule, "vers cursel", repr(self.versificationsListbox.curselection()) )
        index = int( self.versificationsListbox.curselection()[0] ) # Top one selected
        self.versificationSystemName = self.versificationsListbox.get( index )
        versificationSystem =  self.BibleVersificationsSystems.getVersificationSystem( self.versificationSystemName )

        # Clear the text box
        self.versificationTextBox.configure( state=tk.NORMAL )
        self.versificationTextBox.delete( tkSTART, tk.END )
        self.versificationTextBox.insert( tk.END, '{}\n\n'.format( self.versificationSystemName ) )
        self.versificationTextBox.insert( tk.END, '{}\n\n'.format( versificationSystem ) )
        #for field,value in sorted( versificationDict.items() ):
            #if field not in ( 'referenceNumber', 'nameEnglish', ):
                #self.versificationTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewVersification


    def searchMapping( self, event ):
        """
        """
        enteredText = self.mappingsSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchMapping( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchMapping…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Books mappings must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books mappings must have no spaces" ); return
        elif enteredText not in self.BibleMappingsSystemsList:
            self.setErrorStatus( "Unknown {!r} book mapping".format( enteredText ) )
            return

        # Must be ok
        self.mappingSystemName = enteredText
        index = self.BibleMappingsSystemsList.index( self.mappingSystemName )

        # Select it in the listbox
        self.mappingsListbox.select_set( index )
        self.mappingsListbox.see( index )
        self.mappingsListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewMapping below
    # end of BOSManager.searchMapping


    def gotoNewMapping( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewMapping( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewMapping…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.mappingsListbox.get(int(i)) for i in self.mappingsListbox.curselection()] )

        index = int( self.mappingsListbox.curselection()[0] ) # Top one selected
        self.mappingSystemName = self.mappingsListbox.get( index )
        mappingSystem =  self.BibleMappingsSystems.getMappingSystem( self.mappingSystemName )

        # Clear the text box
        self.mappingTextBox.configure( state=tk.NORMAL )
        self.mappingTextBox.delete( tkSTART, tk.END )
        self.mappingTextBox.insert( tk.END, '{}\n\n'.format( self.mappingSystemName ) )
        self.mappingTextBox.insert( tk.END, '{}\n\n'.format( mappingSystem ) )
        #for field,value in sorted( mappingDict.items() ):
            #if field not in ( 'referenceNumber', 'nameEnglish', ):
                #self.mappingTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewMapping


    def searchOrder( self, event ):
        """
        """
        enteredText = self.ordersSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchOrder( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchOrder…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Books orders must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books orders must have no spaces" ); return
        elif enteredText not in self.BibleOrdersSystemsList:
            self.setErrorStatus( "Unknown {!r} book order".format( enteredText ) )
            return

        # Must be ok
        self.orderSystemName = enteredText
        index = self.BibleOrdersSystemsList.index( self.orderSystemName )

        # Select it in the listbox
        self.ordersListbox.select_set( index )
        self.ordersListbox.see( index )
        self.ordersListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewOrder below
    # end of BOSManager.searchOrder


    def gotoNewOrder( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewOrder( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewOrder…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.ordersListbox.get(int(i)) for i in self.ordersListbox.curselection()] )

        vPrint( 'Quiet', debuggingThisModule, "order cursel", repr(self.ordersListbox.curselection()) )
        index = int( self.ordersListbox.curselection()[0] ) # Top one selected
        self.orderSystemName = self.ordersListbox.get( index )
        orderSystem =  self.BibleOrdersSystems.getBookOrderSystem( self.orderSystemName )

        # Clear the text box
        self.orderTextBox.configure( state=tk.NORMAL )
        self.orderTextBox.delete( tkSTART, tk.END )
        self.orderTextBox.insert( tk.END, '{}\n\n'.format( self.orderSystemName ) )
        self.orderTextBox.insert( tk.END, '{}\n\n'.format( orderSystem ) )
        #for field,value in sorted( orderDict.items() ):
            #if field not in ( 'referenceNumber', 'nameEnglish', ):
                #self.orderTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewOrder


    def searchName( self, event ):
        """
        """
        enteredText = self.namesSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchName( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchName…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Books names must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books names must have no spaces" ); return
        elif enteredText not in self.BibleNamesSystemsList:
            self.setErrorStatus( "Unknown {!r} book name".format( enteredText ) )
            return

        # Must be ok
        self.nameSystemName = enteredText
        index = self.BibleNamesSystemsList.index( self.nameSystemName )

        # Select it in the listbox
        self.namesListbox.select_set( index )
        self.namesListbox.see( index )
        self.namesListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewNames below
    # end of BOSManager.searchName


    def gotoNewName( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewName( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewName…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.namesListbox.get(int(i)) for i in self.namesListbox.curselection()] )

        vPrint( 'Quiet', debuggingThisModule, "name cursel", repr(self.namesListbox.curselection()) )
        index = int( self.namesListbox.curselection()[0] ) # Top one selected
        self.nameSystemName = self.namesListbox.get( index )
        nameSystem =  self.BibleNamesSystems.getBooksNamesSystem( self.nameSystemName )

        # Clear the text box
        self.nameTextBox.configure( state=tk.NORMAL )
        self.nameTextBox.delete( tkSTART, tk.END )
        self.nameTextBox.insert( tk.END, '{}\n\n'.format( self.nameSystemName ) )
        self.nameTextBox.insert( tk.END, '{}\n\n'.format( nameSystem ) )
        #for field,value in sorted( nameDict.items() ):
            #if field not in ( 'referenceNumber', 'nameEnglish', ):
                #self.nameTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewName


    def searchOrganisation( self, event ):
        """
        """
        enteredText = self.organisationsSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchOrganisation( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchOrganisation…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Bible organisational system names must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Bible organisational system names must have no spaces" ); return
        elif enteredText not in self.BibleOrganisationalSystemsList:
            self.setErrorStatus( "Unknown {!r} Bible organisational system name".format( enteredText ) )
            return

        # Must be ok
        self.organisationSystemName = enteredText
        index = self.BibleOrganisationalSystemsList.index( self.organisationSystemName )

        # Select it in the listbox
        self.organisationsListbox.select_set( index )
        self.organisationsListbox.see( index )
        self.organisationsListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewOrganisation below
    # end of BOSManager.searchOrganisation


    def gotoNewOrganisation( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewOrganisation( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewOrganisation…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.organisationsListbox.get(int(i)) for i in self.organisationsListbox.curselection()] )

        index = int( self.organisationsListbox.curselection()[0] ) # Top one selected
        self.organisationSystemName = self.organisationsListbox.get( index )
        organisationalSystemDict =  self.BibleOrganisationalSystems.getOrganisationalSystem( self.organisationSystemName )

        # Clear the text box
        self.organisationTextBox.configure( state=tk.NORMAL )
        self.organisationTextBox.delete( tkSTART, tk.END )
        self.organisationTextBox.insert( tk.END, '{} ({})\n\n'.format( self.organisationSystemName, organisationalSystemDict['type'] ) )
        self.organisationTextBox.insert( tk.END, '{}\n\n'.format( organisationalSystemDict['name'][0] ) )
        for field,value in sorted( organisationalSystemDict.items() ):
            if field not in ( 'type', ):
                self.organisationTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewOrganisation


    def searchReference( self, event ):
        """
        """
        enteredText = self.referenceSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchReference( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchReference…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Books references must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books references must have no spaces" ); return
        elif enteredText not in self.BibleReferenceSystemsList:
            self.setErrorStatus( "Unknown {!r} reference".format( enteredText ) )
            return

        # Must be ok
        self.referenceSystemName = enteredText
        index = self.BibleReferenceSystemsList.index( self.referenceSystemName )

        # Select it in the listbox
        self.referencesListbox.select_set( index )
        self.referencesListbox.see( index )
        self.referencesListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewReference below
    # end of BOSManager.searchReference


    def gotoNewReference( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewReference( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewReference…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.referencesListbox.get(int(i)) for i in self.referencesListbox.curselection()] )

        index = int( self.referencesListbox.curselection()[0] ) # Top one selected
        self.referenceSystemName = self.referencesListbox.get( index )
        referenceSystem =  self.BibleReferenceSystems.getReferenceSystem( self.referenceSystemName )

        # Clear the text box
        self.referenceTextBox.configure( state=tk.NORMAL )
        self.referenceTextBox.delete( tkSTART, tk.END )
        self.referenceTextBox.insert( tk.END, '{}\n\n'.format( self.referenceSystemName ) )
        self.referenceTextBox.insert( tk.END, '{}\n\n'.format( referenceSystem ) )
        #for field,value in sorted( referenceDict.items() ):
            #if field not in ( 'referenceNumber', 'nameEnglish', ):
                #self.referenceTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewReference


    def searchStylesheet( self, event ):
        """
        """
        enteredText = self.stylesheetsSearch.get()
        vPrint( 'Never', debuggingThisModule, _("searchStylesheet( {}, {!r} )").format( event, enteredText ) )
        if debuggingThisModule: self.setDebugText( "searchStylesheet…" )

        if not enteredText: return

        if len(enteredText)<3: self.setErrorStatus( "Books stylesheets must be at least three characters" ); return
        elif ' ' in enteredText: self.setErrorStatus( "Books stylesheets must have no spaces" ); return
        elif enteredText not in self.BibleStylesheetsSystemsList:
            self.setErrorStatus( "Unknown {!r} book stylesheet".format( enteredText ) )
            return

        # Must be ok
        self.stylesheetSystemName = enteredText
        index = self.BibleStylesheetsSystemsList.index( self.stylesheetSystemName )

        # Select it in the listbox
        self.stylesheetsListbox.select_set( index )
        self.stylesheetsListbox.see( index )
        self.stylesheetsListbox.event_generate( '<<ListboxSelect>>' ) # Will then execute gotoNewStylesheet below
    # end of BOSManager.searchStylesheet


    def gotoNewStylesheet( self, event=None ):
        """
        """
        vPrint( 'Never', debuggingThisModule, _("gotoNewStylesheet( {} )").format( event ) )
        if debuggingThisModule: self.setDebugText( "gotoNewStylesheet…" )
        #dPrint( 'Quiet', debuggingThisModule, 'You selected items: %s'%[self.stylesheetsListbox.get(int(i)) for i in self.stylesheetsListbox.curselection()] )

        index = int( self.stylesheetsListbox.curselection()[0] ) # Top one selected
        self.stylesheetSystemName = self.stylesheetsListbox.get( index )
        stylesheetSystem =  self.BibleStylesheetsSystems.getStylesheetSystem( self.stylesheetSystemName )

        # Clear the text box
        self.stylesheetTextBox.configure( state=tk.NORMAL )
        self.stylesheetTextBox.delete( tkSTART, tk.END )
        self.stylesheetTextBox.insert( tk.END, '{}\n\n'.format( self.stylesheetSystemName ) )
        self.stylesheetTextBox.insert( tk.END, '{}\n\n'.format( stylesheetSystem ) )
        #for field,value in sorted( stylesheetDict.items() ):
            #if field not in ( 'referenceNumber', 'nameEnglish', ):
                #self.stylesheetTextBox.insert( tk.END, '{}:\t{}\n'.format( field, value ) )
    # end of BOSManager.gotoNewStylesheet


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        viewSettings( self )
        #if BibleOrgSysGlobals.debugFlag:
            #dPrint( 'Never', debuggingThisModule, _("doViewSettings()…") )
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
    # end of BOSManager.doViewSettings


    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        vPrint( 'Never', debuggingThisModule, _("doViewLog()…") )
        if debuggingThisModule: self.setDebugText( "doViewLog…" )

        self.setWaitStatus( _("doViewLog…") )
        filename = PROGRAM_NAME.replace('/','-').replace(':','_').replace('\\','_') + '_log.txt'
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setPathAndFile( self.loggingFolderpath, filename ) \
        or not tEW.loadText():
            tEW.doClose()
            showError( self, SHORT_PROGRAM_NAME, _("Sorry, unable to open log file") )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed doViewLog" )
        else:
            self.childWindows.append( tEW )
            #if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewLog" ) # Don't do this -- adds to the log immediately
        self.setReadyStatus()
    # end of BOSManager.doViewLog


    def doGotoInfo( self, event=None ):
        """
        Pop-up dialog giving goto/reference info.
        """
        vPrint( 'Never', debuggingThisModule, _("BOSManager.doGotoInfo( {} )").format( event ) )

        infoString = 'Current location:\n' \
                 + '\nBible Organisational System (BOS):\n' \
                 + '  Name: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemName() ) \
                 + '  Versification: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'versificationSystem' ) ) \
                 + '  Book Order: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'bookOrderSystem' ) ) \
                 + '  Book Names: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'punctuationSystem' ) ) \
                 + '  Books: {}'.format( self.genericBibleOrganisationalSystem.getBookList() )
        showInfo( self, 'Goto Information', infoString )
    # end of BOSManager.doGotoInfo


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
        vPrint( 'Never', debuggingThisModule, _("doHelp()…") )
        from Biblelator.Dialogs.Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += "\n\nBasic instructions:"
        helpInfo += "\n  Click on a tab to view that subset of the Bible Organisational System (BOS)."
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
    # end of BOSManager.doHelp


    def doSubmitBug( self, event=None ):
        """
        Prompt the user to enter a bug report,
            collect other useful settings, etc.,
            and then send it all somewhere.
        """
        vPrint( 'Never', debuggingThisModule, _("doSubmitBug()…") )

        if not self.internetAccessEnabled: # we need to warn
            showError( self, SHORT_PROGRAM_NAME, 'You need to allow Internet access first!' )
            return

        from Biblelator.Dialogs.About import AboutBox

        submitInfo = programNameVersion
        submitInfo += "\n  This program is not yet finished but we'll add this eventually!"
        ab = AboutBox( self.rootWindow, SHORT_PROGRAM_NAME, submitInfo )
    # end of BOSManager.doSubmitBug


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        vPrint( 'Never', debuggingThisModule, _("doAbout()…") )
        from Biblelator.Dialogs.About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nA display manager for the Bible Organisational System (BOS)." \
            + "\n\nThis is still an unfinished alpha test version, but it should allow you to select and display various sets of information from the BOS." \
            + "\n\n{} is written in Python. For more information see our web pages at Freely-Given.org/Software/BibleOrgSys and Freely-Given.org/Software/Biblelator".format( SHORT_PROGRAM_NAME )
        ab = AboutBox( self.rootWindow, SHORT_PROGRAM_NAME, aboutInfo )
    # end of BOSManager.doAbout


    #def doProjectClose( self ):
        #"""
        #"""
        #dPrint( 'Never', debuggingThisModule, _("doProjectClose()…") )
        #self.notWrittenYet()
    ## end of BOSManager.doProjectClose


    #def doWriteSettingsFile( self ):
        #"""
        #Update our program settings and save them.
        #"""
        #writeSettingsFile( self )
    ### end of BOSManager.writeSettingsFile


    def doCloseMyChildWindows( self ):
        """
        Save files first, and then close child windows.
        """
        vPrint( 'Never', debuggingThisModule, _("BOSManager.doCloseMyChildWindows()…") )

        # Try to close edit windows first coz they might have work to save
        for appWin in self.childWindows.copy():
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
        for appWin in self.childWindows.copy():
            appWin.doClose()
        return True
    # end of BOSManager.doCloseMyChildWindows


    def doCloseMe( self ):
        """
        Save files first, and then end the application.
        """
        vPrint( 'Never', debuggingThisModule, _("BOSManager.doCloseMe()…") )
        vPrint( 'Never', debuggingThisModule, _("{} is closing down…").format( SHORT_PROGRAM_NAME ) )

        #writeSettingsFile( self )
        if self.doCloseMyChildWindows():
            self.rootWindow.destroy()
    # end of BOSManager.doCloseMe
# end of class BOSManager



def openBOSManager( parent ):
    """
    Open the BOS Manager as a child window.

    This is used when the BOS Manager is used inside another program.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, _("BOSManager.openBOSManager( {} )").format( parent ) )

    myWin = tk.Toplevel( parent )
    application = BOSManager( myWin, parent.homeFolderpath, parent.loggingFolderpath, parent.iconImage, parent.settings )
# end of BOSManager.openBOSManager



def briefDemo() -> None:
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( programNameVersion )

    # Set the window icon and title
    iconImage = tk.PhotoImage( file=DATAFILES_FOLDERPATH.joinpath( 'Biblelator.gif' ) )
    tkRootWindow.tk.call( 'wm', 'iconphoto', tkRootWindow._w, iconImage )
    tkRootWindow.title( programNameVersion + ' ' + _('starting') + '…' )

    homeFolderpath = BibleOrgSysGlobals.findHomeFolderpath()
    loggingFolderpath = os.path.join( homeFolderpath, DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderpath, DATA_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, PROGRAM_NAME )
    settings.load()

    application = BOSManager( tkRootWindow, homeFolderpath, loggingFolderpath, iconImage, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of BOSManager.briefDemo

def fullDemo() -> None:
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( programNameVersion )

    # Set the window icon and title
    iconImage = tk.PhotoImage( file=DATAFILES_FOLDERPATH.joinpath( 'Biblelator.gif' ) )
    tkRootWindow.tk.call( 'wm', 'iconphoto', tkRootWindow._w, iconImage )
    tkRootWindow.title( programNameVersion + ' ' + _('starting') + '…' )

    homeFolderpath = BibleOrgSysGlobals.findHomeFolderpath()
    loggingFolderpath = os.path.join( homeFolderpath, DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderpath, DATA_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, PROGRAM_NAME )
    settings.load()

    application = BOSManager( tkRootWindow, homeFolderpath, loggingFolderpath, iconImage, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of BOSManager.fullDemo


def main( homeFolderpath, loggingFolderpath ) -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    #dPrint( 'Quiet', debuggingThisModule, 'FP main', repr(homeFolderpath), repr(loggingFolderpath) )

    numInstancesFound = 0
    if sys.platform == 'linux':
        myProcess = subprocess.Popen( ['ps','xa'], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        programOutputBytes, programErrorOutputBytes = myProcess.communicate()
        #dPrint( 'Quiet', debuggingThisModule, 'pob', programOutputBytes, programErrorOutputBytes )
        #returnCode = myProcess.returncode
        programOutputString = programOutputBytes.decode( encoding='utf-8', errors='replace' ) if programOutputBytes else None
        programErrorOutputString = programErrorOutputBytes.decode( encoding='utf-8', errors='replace' ) if programErrorOutputBytes else None
        #dPrint( 'Quiet', debuggingThisModule, 'processes', repr(programOutputString) )
        for line in programOutputString.split( '\n' ):
            if 'python' in line and PROGRAM_NAME+'.py' in line:
                dPrint( 'Quiet', debuggingThisModule, 'Found in ps xa:', repr(line) )
                numInstancesFound += 1
        if programErrorOutputString: logging.critical( "ps xa got error: {}".format( programErrorOutputString ) )
    elif sys.platform in ( 'win32', 'win64', ):
        myProcess = subprocess.Popen( ['tasklist.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        programOutputBytes, programErrorOutputBytes = myProcess.communicate()
        #dPrint( 'Quiet', debuggingThisModule, 'pob', programOutputBytes, programErrorOutputBytes )
        #returnCode = myProcess.returncode
        programOutputString = programOutputBytes.decode( encoding='utf-8', errors='replace' ) if programOutputBytes else None
        programErrorOutputString = programErrorOutputBytes.decode( encoding='utf-8', errors='replace' ) if programErrorOutputBytes else None
        #dPrint( 'Quiet', debuggingThisModule, 'processes', repr(programOutputString) )
        for line in programOutputString.split( '\n' ):
            if PROGRAM_NAME+'.py' in line:
                dPrint( 'Quiet', debuggingThisModule, 'Found in tasklist:', repr(line) )
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
        vPrint( 'Quiet', debuggingThisModule, 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) ) # e.g., 'x11'

    # Set the window icon and title
    iconImage = tk.PhotoImage( file=DATAFILES_FOLDERPATH.joinpath( 'Biblelator.gif' ) )
    tkRootWindow.tk.call( 'wm', 'iconphoto', tkRootWindow._w, iconImage )
    tkRootWindow.title( programNameVersion + ' ' + _('starting') + '…' )
    application = BOSManager( tkRootWindow, homeFolderpath, loggingFolderpath, iconImage, None )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of BOSManager.main

def run() -> None:
    """
    """
    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    homeFolderpath = BibleOrgSysGlobals.findHomeFolderpath()
    # if homeFolderpath[-1] not in '/\\': homeFolderpath += '/'
    # loggingFolderpath = os.path.join( homeFolderpath, DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    loggingFolderpath = homeFolderpath.joinpath( DATA_SUBFOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, loggingFolderpath=loggingFolderpath )
    parser.add_argument( '-o', '--override', type=str, metavar='INIFilename', dest='override', help="override use of Biblelator.ini set-up" )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )
    #dPrint( 'Quiet', debuggingThisModule, BibleOrgSysGlobals.commandLineArguments ); halt

    if BibleOrgSysGlobals.debugFlag:
        vPrint( 'Quiet', debuggingThisModule, _("Platform is"), sys.platform ) # e.g., 'linux,'win32'
        vPrint( 'Quiet', debuggingThisModule, _("OS name is"), os.name ) # e.g., 'posix','nt'
        if sys.platform == "linux": vPrint( 'Quiet', debuggingThisModule, _("OS uname is"), os.uname() ) # gives about five fields
        vPrint( 'Quiet', debuggingThisModule, _("Running main…") )

    main( homeFolderpath, loggingFolderpath )

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BOSManager.run

if __name__ == '__main__':
    run()
# end of BOSManager.py
