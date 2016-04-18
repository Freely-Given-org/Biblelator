#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BOSManager.py
#
# BOS (Bible Organisational System) manager program
#
# Copyright (C) 2016 Robert Hunt
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
Program to allow viewing of various BOS (Bible Organisational System) subsystems
    such as versification systems, books names systems, etc.
"""

from gettext import gettext as _

LastModifiedDate = '2016-04-19' # by RJH
ShortProgName = "BOSManager"
ProgName = "BOS Manager"
ProgVersion = '0.34'
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import sys, os, logging, subprocess
import multiprocessing

import tkinter as tk
from tkinter.filedialog import Open, Directory, askopenfilename #, SaveAs
from tkinter.ttk import Style, Frame, Button, Combobox, Label, Entry
from tkinter.scrolledtext import ScrolledText

# Biblelator imports
from BiblelatorGlobals import DEFAULT, \
        DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, \
        INITIAL_MAIN_SIZE, INITIAL_MAIN_SIZE_DEBUG, MAX_RECENT_FILES, \
        BIBLE_GROUP_CODES, \
        DEFAULT_KEY_BINDING_DICT, \
        findHomeFolderPath, findUsername, \
        parseWindowGeometry, assembleWindowGeometryFromList, centreWindow
# BIBLE_CONTEXT_VIEW_MODES, MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE, EDIT_MODE_NORMAL, MAX_WINDOWS,
# assembleWindowSize, parseWindowSize,
from BiblelatorDialogs import errorBeep, showerror, showwarning, showinfo, \
        SelectResourceBoxDialog, \
        GetNewProjectNameDialog, CreateNewProjectFilesDialog, GetNewCollectionNameDialog, \
        BookNameDialog, NumberButtonDialog
from BiblelatorHelpers import mapReferencesVerseKey, createEmptyUSFMBooks, parseEnteredBookname
from Settings import ApplicationSettings, ProjectSettings
from BiblelatorSettingsFunctions import parseAndApplySettings, writeSettingsFile, \
        saveNewWindowSetup, deleteExistingWindowSetup, applyGivenWindowsSettings, viewSettings
from ChildWindows import ChildWindows
from BibleResourceWindows import SwordBibleResourceWindow, InternalBibleResourceWindow, DBPBibleResourceWindow
from BibleResourceCollection import BibleResourceCollectionWindow
from BibleReferenceCollection import BibleReferenceCollectionWindow
from LexiconResourceWindows import BibleLexiconResourceWindow
from TextEditWindow import TextEditWindow
from USFMEditWindow import USFMEditWindow
#from ESFMEditWindow import ESFMEditWindow

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
#if debuggingThisModule: print( 'sys.path = ', sys.path )
import BibleOrgSysGlobals
from BibleOrganizationalSystems import BibleOrganizationalSystem
from BibleVersificationSystems import BibleVersificationSystems
from DigitalBiblePlatform import DBPBibles
from VerseReferences import SimpleVerseKey
from BibleStylesheets import BibleStylesheet
from SwordResources import SwordType, SwordInterface
from USFMBible import USFMBible
from PTXBible import PTXBible, loadPTXSSFData



TEXT_FILETYPES = [('All files',  '*'), ('Text files', '.txt')]
BIBLELATOR_PROJECT_FILETYPES = [('ProjectSettings','ProjectSettings.ini'), ('INI files','.ini'), ('All files','*')]
PARATEXT_FILETYPES = [('SSF files','.ssf'), ('All files','*')]



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
    return '{}{}'.format( nameBit+': ' if nameBit else '', errorBit )
# end of exp



class BOSManager( Frame ):
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
            print( exp("BOSManager.__init__( {}, {}, {}, … )").format( rootWindow, homeFolderPath, loggingFolderPath ) )
        self.rootWindow, self.homeFolderPath, self.loggingFolderPath, self.iconImage, self.settings = rootWindow, homeFolderPath, loggingFolderPath, iconImage, settings
        self.parentApp = self # Yes, that's me, myself!
        self.starting = True

        self.themeName = 'default'
        self.style = Style()
        self.interfaceLanguage = DEFAULT
        self.interfaceComplexity = DEFAULT
        self.touchMode = False # True makes larger buttons
        self.tabletMode = False
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

        self.rootWindow.protocol( "WM_DELETE_WINDOW", self.doCloseMe ) # Catch when app is closed

        self.childWindows = ChildWindows( self )

        self.createStatusBar()

        # Create our display text book
        self.textBox = ScrolledText( self.rootWindow, bg='yellow' )#style='DebugText.TScrolledText' )
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
        self.internalBibles = []

        # Read and apply the saved settings
        #parseAndApplySettings( self )
        if ProgName not in self.settings.data or 'windowSize' not in self.settings.data[ProgName] or 'windowPosition' not in self.settings.data[ProgName]:
            initialMainSize = INITIAL_MAIN_SIZE_DEBUG if BibleOrgSysGlobals.debugFlag else INITIAL_MAIN_SIZE
            centreWindow( self.rootWindow, *initialMainSize.split( 'x', 1 ) )

        if self.touchMode:
            if BibleOrgSysGlobals.verbosityLevel > 1: print( _("Touch mode enabled!") )
            self.createTouchMenuBar()
            self.createTouchNavigationBar()
        else: # assume it's regular desktop mode
            self.createNormalMenuBar()
            self.createNormalNavigationBar()
        self.createToolBar()
        if BibleOrgSysGlobals.debugFlag: self.createDebugToolBar()
        self.createMainKeyboardBindings()

        # See if there's any developer messages
        if self.internetAccessEnabled and self.checkForMessagesEnabled:
            self.doCheckForDeveloperMessages()

        self.rootWindow.title( ProgNameVersion )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "__init__ finished." )
        self.starting = False
        self.setReadyStatus()
    # end of BOSManager.__init__


    def setGenericBibleOrganisationalSystem( self, BOSname ):
        """
        We usually use a fairly generic BibleOrganizationalSystem (BOS) to ensure
            that it contains all the books that we might ever want to navigate to.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setGenericBibleOrganisationalSystem( {} )").format( BOSname ) )

        # Set-up our Bible system and our callables
        self.genericBibleOrganisationalSystem = BibleOrganizationalSystem( self.genericBibleOrganisationalSystemName )
        self.genericBookList = self.genericBibleOrganisationalSystem.getBookList()
        #self.getNumBooks = self.genericBibleOrganisationalSystem.getNumBooks
        self.getNumChapters = self.genericBibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda b,c: 99 if c=='0' or c==0 else self.genericBibleOrganisationalSystem.getNumVerses( b, c )
        self.isValidBCVRef = self.genericBibleOrganisationalSystem.isValidBCVRef
        self.getFirstBookCode = self.genericBibleOrganisationalSystem.getFirstBookCode
        self.getPreviousBookCode = self.genericBibleOrganisationalSystem.getPreviousBookCode
        self.getNextBookCode = self.genericBibleOrganisationalSystem.getNextBookCode
        self.getBBB = self.genericBibleOrganisationalSystem.getBBB
        self.getGenericBookName = self.genericBibleOrganisationalSystem.getBookName
        #self.getBookList = self.genericBibleOrganisationalSystem.getBookList

        # Make a bookNumber table with GEN as #1
        #print( self.genericBookList )
        self.offsetGenesis = self.genericBookList.index( 'GEN' )
        #print( 'offsetGenesis', self.offsetGenesis )
        self.bookNumberTable = {}
        for j,BBB in enumerate(self.genericBookList):
            k = j + 1 - self.offsetGenesis
            nBBB = BibleOrgSysGlobals.BibleBooksCodes.getReferenceNumber( BBB )
            #print( BBB, nBBB )
            self.bookNumberTable[k] = BBB
            self.bookNumberTable[BBB] = k
        #print( self.bookNumberTable )
    # end of BOSManager.setGenericBibleOrganisationalSystem


    def createNormalMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createNormalMenuBar()") )

        #self.win = Toplevel( self )
        self.menubar = tk.Menu( self.rootWindow )
        #self.rootWindow['menu'] = self.menubar
        self.rootWindow.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        fileNewSubmenu = tk.Menu( fileMenu, tearoff=False )
        fileMenu.add_cascade( label=_('New'), underline=0, menu=fileNewSubmenu )
        fileNewSubmenu.add_command( label=_('Text file'), underline=0, command=self.notWrittenYet )
        fileOpenSubmenu = tk.Menu( fileMenu, tearoff=False )
        fileMenu.add_cascade( label=_('Open'), underline=0, menu=fileOpenSubmenu )
        fileRecentOpenSubmenu = tk.Menu( fileOpenSubmenu, tearoff=False )
        fileOpenSubmenu.add_cascade( label=_('Recent'), underline=0, menu=fileRecentOpenSubmenu )
        for j, (filename, folder, winType) in enumerate( self.recentFiles ):
            fileRecentOpenSubmenu.add_command( label=filename, underline=0, command=self.notWrittenYet )
        fileOpenSubmenu.add_separator()
        fileOpenSubmenu.add_command( label=_('Text file…'), underline=0, command=self.notWrittenYet )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Save all…'), underline=0, command=self.notWrittenYet )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Save settings'), underline=0, command=self.notWrittenYet )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Quit app'), underline=0, command=self.doCloseMe, accelerator=self.keyBindingDict[_('Quit')][0] ) # quit app

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

    def createTouchMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createTouchMenuBar()") )
            assert self.touchMode

        self.createNormalMenuBar()
    # end of BOSManager.createTouchMenuBar


    def createNormalNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createNormalNavigationBar()") )

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
        BBB = self.getBBB( bookName )
        self.bookNameBox = Combobox( navigationBar, width=len('Deuteronomy'), textvariable=self.bookNameVar )
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
        #self.chapterNumberBox = Entry( self, textvariable=self.chapterNumberVar )
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
        #self.verseNumberBox = Entry( self, textvariable=self.verseNumberVar )
        #self.verseNumberBox['width'] = 3
        #self.verseNumberBox.pack()

        self.wordVar = tk.StringVar()
        if self.lexiconWord: self.wordVar.set( self.lexiconWord )
        self.wordBox = Entry( navigationBar, width=12, textvariable=self.wordVar )
        #self.wordBox['width'] = 12
        self.wordBox.bind( '<Return>', self.acceptNewWord )
        self.wordBox.pack( side=tk.LEFT )

        if 0: # I don't think we should need this button if everything else works right
            self.updateButton = Button( navigationBar )
            self.updateButton['text'] = 'Update'
            self.updateButton['command'] = self.acceptNewBnCV
            #self.updateButton.grid( row=0, column=7 )
            self.updateButton.pack( side=tk.LEFT )

        Style( self ).map("Quit.TButton", foreground=[('pressed', 'red'), ('active', 'blue')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )
        self.quitButton = Button( navigationBar, text="QUIT", style="Quit.TButton", command=self.doCloseMe )
        self.quitButton.pack( side=tk.RIGHT )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
        navigationBar.pack( side=tk.TOP, fill=tk.X )
    # end of BOSManager.createNormalNavigationBar

    def createTouchNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createTouchNavigationBar()") )
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
        BBB = self.getBBB( bookName )
        self.bookNameBox = Combobox( navigationBar, width=len('Deuteronomy'), textvariable=self.bookNameVar )
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
        #self.chapterNumberBox = Entry( self, textvariable=self.chapterNumberVar )
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
        self.wordBox = Entry( navigationBar, width=12, textvariable=self.wordVar )
        #self.wordBox['width'] = 12
        self.wordBox.bind( '<Return>', self.acceptNewWord )
        #self.wordBox.pack( side=tk.LEFT )

        Style().configure( 'word.TButton', background='brown' )
        self.wordButton = Button( navigationBar, width=8, text=self.lexiconWord, style='word.TButton', command=self.doWordButton )
        self.wordButton.pack( side=tk.LEFT, padx=xPad, pady=yPad )

        if 0: # I don't think we should need this button if everything else works right
            self.updateButton = Button( navigationBar )
            self.updateButton['text'] = 'Update'
            self.updateButton['command'] = self.acceptNewBnCV
            #self.updateButton.grid( row=0, column=7 )
            self.updateButton.pack( side=tk.LEFT )

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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createToolBar()") )

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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createDebugToolBar()") )

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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createStatusBar()") )

        #Style().configure( 'StatusBar.TLabel', background='pink' )
        #Style().configure( 'StatusBar.TLabel', background='DarkOrange1' )
        Style().configure( 'StatusBar.TLabel', background='forest green' )

        self.statusTextVariable = tk.StringVar()
        self.statusTextLabel = Label( self.rootWindow, relief=tk.SUNKEN,
                                    textvariable=self.statusTextVariable, style='StatusBar.TLabel' )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.BOTTOM, fill=tk.X )
        self.statusTextVariable.set( '' ) # first initial value
        self.setWaitStatus( "Starting up…" )
    # end of BOSManager.createStatusBar


    def createMainKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("createMainKeyboardBindings()") )

        self.myKeyboardBindingsList = []
        for name,command in ( ('Help',self.doHelp), ('About',self.doAbout), ('Quit',self.doCloseMe) ):
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
    # end of BOSManager.createMainKeyboardBindings()


    #def addRecentFile( self, threeTuple ):
        #"""
        #Puts most recent first
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("addRecentFile( {} )").format( threeTuple ) )
            #assert len(threeTuple) == 3

        #try: self.recentFiles.remove( threeTuple ) # Remove a duplicate if present
        #except ValueError: pass
        #self.recentFiles.insert( 0, threeTuple ) # Put this one at the beginning of the lis
        #if len(self.recentFiles)>MAX_RECENT_FILES: self.recentFiles.pop() # Remove the last one if necessary
        #self.createNormalMenuBar()
    ## end of BOSManager.addRecentFile()


    def notWrittenYet( self ):
        errorBeep()
        showerror( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of BOSManager.notWrittenYet


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setStatus( {!r} )").format( newStatusText ) )

        #print( "SB is", repr( self.statusTextVariable.get() ) )
        if newStatusText != self.statusTextVariable.get(): # it's changed
            #self.statusBarTextWidget['state'] = tk.NORMAL
            #self.statusBarTextWidget.delete( '1.0', tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( '1.0', newStatusText )
            #self.statusBarTextWidget['state'] = tk.DISABLED # Don't allow editing
            #self.statusText = newStatusText
            Style().configure( 'StatusBar.TLabel', foreground='white', background='purple' )
            self.statusTextVariable.set( newStatusText )
            self.statusTextLabel.update()
    # end of BOSManager.setStatus

    def setErrorStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setErrorStatus( {!r} )").format( newStatusText ) )

        #self.rootWindow.config( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.config( style='StatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( 'StatusBar.TLabel', foreground='yellow', background='red' )
        self.update()
    # end of BOSManager.setErrorStatus

    def setWaitStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setWaitStatus( {!r} )").format( newStatusText ) )

        self.rootWindow.config( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.config( style='StatusBar.TLabelWait' )
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
        if self.starting: self.setWaitStatus( _("Starting up…") )
        else: # we really are ready
            #self.statusTextLabel.config( style='StatusBar.TLabelReady' )
            self.setStatus( _("Ready") )
            Style().configure( 'StatusBar.TLabel', foreground='yellow', background='forest green' )
            self.config( cursor='' )
    # end of BOSManager.setReadyStatus


    def setDebugText( self, newMessage=None ):
        """
        """
        if debuggingThisModule:
            #print( exp("setDebugText( {!r} )").format( newMessage ) )
            assert BibleOrgSysGlobals.debugFlag

        logging.info( 'Debug: ' + newMessage ) # Not sure why logging.debug isn't going into the file! XXXXXXXXXXXXX
        self.debugTextBox['state'] = tk.NORMAL # Allow editing
        self.debugTextBox.delete( '1.0', tk.END ) # Clear everything
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
                                        appWin.winType,
                                        #appWin.winType.replace('ChildWindow',''),
                                        appWin.genericWindowType,
                                        #appWin.genericWindowType.replace('Resource',''),
                                        appWin.winfo_geometry(), appWin.moduleID,
                                        appWin.contextViewMode if 'Bible' in appWin.genericWindowType else 'N/A',
                                        appWin.BCVUpdateType if 'Bible' in appWin.genericWindowType else 'N/A' ) )
                                        #extra ) )
        #self.debugTextBox.insert( tk.END, '\n{} resource frames:'.format( len(self.childWindows) ) )
        #for j, projFrame in enumerate( self.childWindows ):
            #self.debugTextBox.insert( tk.END, "\n  {} {}".format( j, projFrame ) )
        self.debugTextBox['state'] = tk.DISABLED # Don't allow editing
    # end of BOSManager.setDebugText


    def doChangeTheme( self, newThemeName ):
        """
        Set the window theme to the given scheme.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doChangeTheme( {!r} )").format( newThemeName ) )
            assert newThemeName
            self.setDebugText( 'Set theme to {!r}'.format( newThemeName ) )

        self.themeName = newThemeName
        try:
            self.style.theme_use( newThemeName )
        except tk.TclError as err:
            showerror( self, 'Error', err )
    # end of BOSManager.doChangeTheme


    def doCheckForDeveloperMessages( self, event=None ):
        """
        Check if there's any new messages on the website from the developer.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BOSManager.doCheckForDeveloperMessages()") )

        import requests
        # NOTE: needs to be https!!!
        try: ri = requests.get( "http://Freely-Given.org/Software/Biblelator/DevMsg/DevMsg.idx" )
        except requests.exceptions.InvalidSchema as err:
            logging.critical( exp("doCheckForDeveloperMessages: Unable to check for developer messages") )
            logging.info( exp("doCheckForDeveloperMessages: {}").format( err ) )
            showerror( self, 'Check for Developer Messages Error', err )
            return

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( 'doCheckForDeveloperMessages Status', repr(ri.status_code) )
            #print( 'Headers',  repr(ri.headers) )
            #print( 'Content', repr(ri.content) )
            #print( 'Encoding',  repr(ri.encoding) )
            #print( 'Text',  repr(ri.text) )

        if ri.status_code == 200: # successful
            fetchedText = ri.text
            while fetchedText.endswith( '\n' ): result = result[:-1] # Removing trailing line feeds
            n,ext = fetchedText.split( '.', 1 )
            ni = int( n )
            #print( ni, ext )
            if ni > self.lastMessageNumberRead:
                rq = requests.get( "http://Freely-Given.org/Software/Biblelator/DevMsg/{}.{}".format( self.lastMessageNumberRead+1, ext ) )
                if rq.status_code == 200: # successful
                    #print( r.text )

                    from About import AboutBox
                    aboutInfo = ProgNameVersion + " Developer Message #{}".format( self.lastMessageNumberRead )
                    aboutInfo += '\n  from Freely-Given.org'
                    aboutInfo += '\n\n' + rq.text
                    ab = AboutBox( self.rootWindow, ShortProgName, aboutInfo )

                    self.lastMessageNumberRead += 1
    # end of BOSManager.doCheckForDeveloperMessages


    #def doOpenRecent( self, recentIndex ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( exp("doOpenRecent( {} )").format( recentIndex ) )
            #self.setDebugText( "doOpenRecent…" )
            #assert recentIndex < len(self.recentFiles)

        #filename, folder, winType = self.recentFiles[recentIndex]
        #print( "Need to open", filename, folder, winType )
        #print( "NOT WRITTEN YET" )
    ## end of BOSManager.doOpenRecent


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        viewSettings( self )
        #if BibleOrgSysGlobals.debugFlag:
            #if debuggingThisModule: print( exp("doViewSettings()") )
            #self.setDebugText( "doViewSettings…" )
        #tEW = TextEditWindow( self )
        ##if windowGeometry: tEW.geometry( windowGeometry )
        #if not tEW.setFilepath( self.settings.settingsFilepath ) \
        #or not tEW.loadText():
            #tEW.closeChildWindow()
            #showerror( self, ShortProgName, _("Sorry, unable to open settings file") )
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
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( exp("doViewLog()") )
            self.setDebugText( "doViewLog…" )

        self.setWaitStatus( "doViewLog…" )
        filename = ProgName.replace('/','-').replace(':','_').replace('\\','_') + '_log.txt'
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setPathAndFile( self.loggingFolderPath, filename ) \
        or not tEW.loadText():
            tEW.closeChildWindow()
            showerror( self, ShortProgName, _("Sorry, unable to open log file") )
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BOSManager.doGotoInfo( {} )").format( event ) )

        infoString = 'Current location:\n' \
                 + '\nBible Organisational System (BOS):\n' \
                 + '  Name: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganizationalSystemName() ) \
                 + '  Versification: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganizationalSystemValue( 'versificationSystem' ) ) \
                 + '  Book Order: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganizationalSystemValue( 'bookOrderSystem' ) ) \
                 + '  Book Names: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganizationalSystemValue( 'punctuationSystem' ) ) \
                 + '  Books: {}'.format( self.genericBibleOrganisationalSystem.getBookList() )
        showinfo( self, 'Goto Information', infoString )
    # end of BOSManager.doGotoInfo


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BOSManager.doHelp()") )
        from Help import HelpBox

        helpInfo = ProgNameVersion
        helpInfo += "\n\nBasic instructions:"
        helpInfo += "\n  Use the Resource menu to open study/reference resources."
        helpInfo += "\n  Use the Project menu to open editable Bibles."
        helpInfo += "\n\nKeyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n  {}\t{}".format( name, shortcut )
        helpInfo += "\n\n  {}\t{}".format( 'Prev Verse', 'Alt+UpArrow' )
        helpInfo += "\n  {}\t{}".format( 'Next Verse', 'Alt+DownArrow' )
        helpInfo += "\n  {}\t{}".format( 'Prev Chapter', 'Alt+, (<)' )
        helpInfo += "\n  {}\t{}".format( 'Next Chapter', 'Alt+. (>)' )
        helpInfo += "\n  {}\t{}".format( 'Prev Book', 'Alt+[' )
        helpInfo += "\n  {}\t{}".format( 'Next Book', 'Alt+]' )
        hb = HelpBox( self.rootWindow, ShortProgName, helpInfo )
    # end of BOSManager.doHelp


    def doSubmitBug( self, event=None ):
        """
        Prompt the user to enter a bug report,
            collect other useful settings, etc.,
            and then send it all somewhere.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BOSManager.doSubmitBug()") )

        if not self.internetAccessEnabled: # we need to warn
            showerror( self, ShortProgName, 'You need to allow Internet access first!' )
            return

        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\n  This program is not yet finished but we'll add this eventually!"
        ab = AboutBox( self.rootWindow, ShortProgName, aboutInfo )
    # end of BOSManager.doSubmitBug


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BOSManager.doAbout()") )
        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\nA free USFM Bible editor." \
            + "\n\nThis is still an unfinished alpha test version, but it should edit and save your USFM Bible files reliably." \
            + "\n\nBiblelator is written in Python. For more information see our web page at Freely-Given.org/Software/Biblelator"
        ab = AboutBox( self.rootWindow, ShortProgName, aboutInfo )
    # end of BOSManager.doAbout


    #def doProjectClose( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("doProjectClose()") )
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BOSManager.doCloseMyChildWindows()") )

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
            showerror( self, _("Save files"), _("You need to save or close your work first.") )
            return False

        # Should be able to close all apps now
        for appWin in self.childWindows[:]:
            appWin.doClose()
        return True
    # end of BOSManager.doCloseMyChildWindows


    def doCloseMe( self ):
        """
        Save files first, and then end the application.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BOSManager.doCloseMe()") )
        elif BibleOrgSysGlobals.verbosityLevel > 0:
            print( _("{} is closing down…").format( ShortProgName ) )

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
        print( exp("BOSManager.openBOSManager( {} )").format( parent ) )

    myWin = tk.Toplevel( parent )
    application = BOSManager( myWin, parent.homeFolderPath, parent.loggingFolderPath, parent.iconImage, parent.settings )
# end of BOSManager.openBOSManager



def demo():
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersionDate )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( ProgNameVersion )

    homeFolderPath = findHomeFolderPath()
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = BOSManagerSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, ProgName )
    settings.load()

    application = BOSManager( tkRootWindow, homeFolderPath, loggingFolderPath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of BOSManager.demo


def main( homeFolderPath, loggingFolderPath ):
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersionDate )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    #print( 'FP main', repr(homeFolderPath), repr(loggingFolderPath) )

    numInstancesFound = 0
    if sys.platform == 'linux':
        myProcess = subprocess.Popen( ['ps','xa'], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        programOutputBytes, programErrorOutputBytes = myProcess.communicate()
        #print( 'pob', programOutputBytes, programErrorOutputBytes )
        #returnCode = myProcess.returncode
        programOutputString = programOutputBytes.decode( encoding='utf-8', errors="replace" ) if programOutputBytes else None
        programErrorOutputString = programErrorOutputBytes.decode( encoding='utf-8', errors="replace" ) if programErrorOutputBytes else None
        #print( 'processes', repr(programOutputString) )
        for line in programOutputString.split( '\n' ):
            if 'python' in line and ProgName+'.py' in line:
                if BibleOrgSysGlobals.debugFlag: print( 'Found in ps xa:', repr(line) )
                numInstancesFound += 1
        if programErrorOutputString: logging.critical( "ps xa got error: {}".format( programErrorOutputString ) )
    elif sys.platform in ( 'win32', 'win64', ):
        myProcess = subprocess.Popen( ['tasklist.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        programOutputBytes, programErrorOutputBytes = myProcess.communicate()
        #print( 'pob', programOutputBytes, programErrorOutputBytes )
        #returnCode = myProcess.returncode
        programOutputString = programOutputBytes.decode( encoding='utf-8', errors="replace" ) if programOutputBytes else None
        programErrorOutputString = programErrorOutputBytes.decode( encoding='utf-8', errors="replace" ) if programErrorOutputBytes else None
        #print( 'processes', repr(programOutputString) )
        for line in programOutputString.split( '\n' ):
            if ProgName+'.py' in line:
                if BibleOrgSysGlobals.debugFlag: print( 'Found in tasklist:', repr(line) )
                numInstancesFound += 1
        if programErrorOutputString: logging.critical( "tasklist got error: {}".format( programErrorOutputString ) )
    else: logging.critical( "Don't know how to check for already running instances in {}/{}.".format( sys.platform, os.name ) )
    if numInstancesFound > 1:
        import easygui
        logging.critical( "Found {} instances of {} running.".format( numInstancesFound, ProgName ) )
        result = easygui.ynbox('Seems {} might be already running: Continue?'.format( ProgName), ProgNameVersion, ('Yes', 'No'))
        if not result:
            logging.info( "Exiting as user requested." )
            sys.exit()

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) ) # e.g., 'x11'

    # Set the window icon and title
    iconImage = tk.PhotoImage( file='Biblelator.gif' )
    tkRootWindow.tk.call( 'wm', 'iconphoto', tkRootWindow._w, iconImage )
    tkRootWindow.title( ProgNameVersion + ' ' + _('starting') + '…' )

    if BibleOrgSysGlobals.commandLineArguments.override is None:
        INIname = ShortProgName
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "Using default {!r} ini file".format( INIname ) )
    else:
        INIname = BibleOrgSysGlobals.commandLineArguments.override
        if BibleOrgSysGlobals.verbosityLevel > 1: print( _("Using user-specified {!r} ini file").format( INIname ) )
    settings = ApplicationSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, INIname )
    settings.load()

    application = BOSManager( tkRootWindow, homeFolderPath, loggingFolderPath, iconImage, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of BOSManager.main


if __name__ == '__main__':
    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    if 'win' in sys.platform: # Convert stdout so we don't get zillions of UnicodeEncodeErrors
        from io import TextIOWrapper
        sys.stdout = TextIOWrapper( sys.stdout.detach(), sys.stdout.encoding, 'namereplace' if sys.version_info >= (3,5) else 'backslashreplace' )

    # Configure basic set-up
    homeFolderPath = findHomeFolderPath()
    if homeFolderPath[-1] not in '/\\': homeFolderPath += '/'
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion, loggingFolderPath=loggingFolderPath )
    parser.add_argument( '-o', '--override', type=str, metavar='INIFilename', dest='override', help="override use of Biblelator.ini set-up" )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )
    #print( BibleOrgSysGlobals.commandLineArguments ); halt

    if BibleOrgSysGlobals.debugFlag:
        print( exp("Platform is"), sys.platform ) # e.g., 'linux,'win32'
        print( exp("OS name is"), os.name ) # e.g., 'posix','nt'
        if sys.platform == "linux": print( exp("OS uname is"), os.uname() ) # gives about five fields
        print( exp("Running main…") )

    main( homeFolderPath, loggingFolderPath )

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BOSManager.py