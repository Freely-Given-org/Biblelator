#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Biblelator.py
#
# Main program for Biblelator Bible display/editing
#
# Copyright (C) 2013-2016 Robert Hunt
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
Program to allow editing of USFM Bibles using Python3 and Tkinter.

Note that many times in this application, where the term 'Bible' is used
    it can refer to any versified resource, e.g., typically including commentaries.
"""

from gettext import gettext as _

LastModifiedDate = '2016-01-31' # by RJH
ShortProgName = "Biblelator"
ProgName = "Biblelator"
ProgVersion = '0.29'
SettingsVersion = '0.29' # Only need to change this if the settings format has changed
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import sys, os, logging
import multiprocessing

import tkinter as tk
from tkinter.filedialog import Open, Directory #, SaveAs
from tkinter.ttk import Style, Frame, Button, Combobox, Label, Entry

# Biblelator imports
from BiblelatorGlobals import APP_NAME, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, MAX_WINDOWS, \
        INITIAL_MAIN_SIZE, MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE, \
        BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, \
        EDIT_MODE_NORMAL, DEFAULT_KEY_BINDING_DICT, \
        findHomeFolderPath, parseWindowGeometry, parseWindowSize, assembleWindowGeometryFromList, assembleWindowSize, centreWindow
from BiblelatorDialogs import errorBeep, showerror, showwarning, showinfo, \
        SaveWindowNameDialog, DeleteWindowNameDialog, SelectResourceBoxDialog, \
        GetNewProjectNameDialog, CreateNewProjectFilesDialog, GetNewCollectionNameDialog
from BiblelatorHelpers import mapReferencesVerseKey, createEmptyUSFMBooks
from Settings import ApplicationSettings, ProjectSettings
from ChildWindows import ChildWindows
from BibleResourceWindows import SwordBibleResourceWindow, InternalBibleResourceWindow, DBPBibleResourceWindow
from BibleResourceCollection import BibleResourceCollectionWindow
from BibleReferenceCollection import BibleReferenceCollectionWindow
from LexiconResourceWindows import BibleLexiconResourceWindow
from EditWindows import TextEditWindow, USFMEditWindow, ESFMEditWindow

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
print( 'sys.path = ', sys.path )
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
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit+': ' if nameBit else '', _(errorBit) )
# end of exp



class Application( Frame ):
    """
    This is the main application window (well, actually a frame in the root toplevel window).

    Its main job is to keep track of self.currentVerseKey (and self.currentVerseKeyGroup)
        and use that to inform child windows of BCV movements.
    """
    global settings
    def __init__( self, rootWindow, homeFolderPath, loggingFolderPath, settings ):
        if BibleOrgSysGlobals.debugFlag: print( exp("Application.__init__( {}, ... )").format( rootWindow ) )
        self.rootWindow, self.homeFolderPath, self.loggingFolderPath, self.settings = rootWindow, homeFolderPath, loggingFolderPath, settings
        self.parentApp = self # Yes, that's me, myself!

        self.themeName = 'default'
        self.style = Style()

        self.lastFind = None
        #self.openDialog = None
        self.saveDialog = None
        self.optionsDict = {}

        self.lexiconWord = None
        self.currentProject = None

        if BibleOrgSysGlobals.debugFlag: print( "Button default font", Style().lookup("TButton", "font") )
        if BibleOrgSysGlobals.debugFlag: print( "Label default font", Style().lookup("TLabel", "font") )

        # Set-up our Bible system and our callables
        self.genericBibleOrganisationalSystem = BibleOrganizationalSystem( "GENERIC-KJV-66-ENG" )
        self.getNumChapters = self.genericBibleOrganisationalSystem.getNumChapters
        self.getNumVerses = lambda b,c: 99 if c=='0' or c==0 else self.genericBibleOrganisationalSystem.getNumVerses( b, c )
        self.isValidBCVRef = self.genericBibleOrganisationalSystem.isValidBCVRef
        self.getFirstBookCode = self.genericBibleOrganisationalSystem.getFirstBookCode
        self.getPreviousBookCode = self.genericBibleOrganisationalSystem.getPreviousBookCode
        self.getNextBookCode = self.genericBibleOrganisationalSystem.getNextBookCode
        self.getBBB = self.genericBibleOrganisationalSystem.getBBB
        self.getBookName = self.genericBibleOrganisationalSystem.getBookName
        self.getBookList = self.genericBibleOrganisationalSystem.getBookList

        self.stylesheet = BibleStylesheet().loadDefault()
        Frame.__init__( self, self.rootWindow )
        self.pack()

        self.rootWindow.protocol( "WM_DELETE_WINDOW", self.doCloseMe ) # Catch when app is closed

        self.childWindows = ChildWindows( self )

        self.createStatusBar()
        if BibleOrgSysGlobals.debugFlag: # Create a scrolling debug box
            self.lastDebugMessage = None
            from tkinter.scrolledtext import ScrolledText
            #Style().configure('DebugText.TScrolledText', padding=2, background='orange')
            self.debugTextBox = ScrolledText( self.rootWindow, bg='orange' )#style='DebugText.TScrolledText' )
            self.debugTextBox.pack( side=tk.BOTTOM, fill=tk.BOTH )
            #self.debugTextBox.tag_configure( 'emp', background='yellow', font='helvetica 12 bold', relief='tk.RAISED' )
            self.debugTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
            self.setDebugText( "Starting up..." )

        self.SwordInterface = None
        self.DBPInterface = None
        #print( exp("Preload the Sword library...") )
        #self.SwordInterface = SwordResources.SwordInterface() # Preload the Sword library

        # Set default folders
        self.lastFileDir = '.'
        self.lastBiblelatorFileDir = os.path.join( self.homeFolderPath, DATA_FOLDER_NAME )
        self.lastParatextFileDir = './'
        self.lastInternalBibleDir = './'
        if sys.platform.startswith( 'win' ):
            self.lastParatextFileDir = 'C:\\My Paratext Projects\\'
            self.lastInternalBibleDir = 'C:\\My Paratext Projects\\'
        elif sys.platform == 'linux': # temp.........................................
            #self.lastParatextFileDir = '../../../../../Data/Work/VirtualBox_Shared_Folder/'
            self.lastParatextFileDir = '../../../../../Data/Work/Matigsalug/Bible/'
            self.lastInternalBibleDir = '../../../../../Data/Work/Matigsalug/Bible/'

        self.keyBindingDict = DEFAULT_KEY_BINDING_DICT
        self.myKeyboardBindingsList = []

        # Read and apply the saved settings
        self.parseAndApplySettings()
        if ProgName not in self.settings.data or 'windowSize' not in self.settings.data[ProgName] or 'windowPosition' not in self.settings.data[ProgName]:
            centreWindow( self.rootWindow, *INITIAL_MAIN_SIZE.split( 'x', 1 ) )

        self.createMenuBar()
        self.createNavigationBar()
        self.createToolBar()
        if BibleOrgSysGlobals.debugFlag: self.createDebugToolBar()
        self.createMainKeyboardBindings()

        self.BCVHistory = []
        self.BCVHistoryIndex = None

        # Make sure all our Bible windows get updated initially
        for groupCode in BIBLE_GROUP_CODES:
            if groupCode != self.currentVerseKeyGroup: # that gets done below
                groupVerseKey = self.getVerseKey( groupCode )
                if BibleOrgSysGlobals.debugFlag: assert( isinstance( groupVerseKey, SimpleVerseKey ) )
                for appWin in self.childWindows:
                    if 'Bible' in appWin.genericWindowType:
                        if appWin.groupCode == groupCode:
                            appWin.updateShownBCV( groupVerseKey )
        self.updateBCVGroup( self.currentVerseKeyGroup ) # Does an acceptNewBnCV

        # See if there's any developer messages
        if self.internetAccessEnabled and self.checkForMessagesEnabled:
            self.doCheckForDeveloperMessages()

        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "__init__ finished." )
        self.setReadyStatus()
    # end of Application.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("createMenuBar()") )

        #self.win = Toplevel( self )
        self.menubar = tk.Menu( self.rootWindow )
        #self.rootWindow['menu'] = self.menubar
        self.rootWindow.config( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        #fileMenu.add_command( label='New...', underline=0, command=self.notWrittenYet )
        fileNewSubmenu = tk.Menu( fileMenu, tearoff=False )
        fileMenu.add_cascade( label='New', underline=0, menu=fileNewSubmenu )
        fileNewSubmenu.add_command( label='Text file', underline=0, command=self.doOpenNewTextEditWindow )
        fileOpenSubmenu = tk.Menu( fileMenu, tearoff=False )
        fileMenu.add_cascade( label='Open', underline=0, menu=fileOpenSubmenu )
        fileOpenSubmenu.add_command( label='Text file...', underline=0, command=self.doOpenFileTextEditWindow )
        fileMenu.add_separator()
        fileMenu.add_command( label='Save all...', underline=0, command=self.notWrittenYet )
        fileMenu.add_separator()
        fileMenu.add_command( label='Save settings', underline=0, command=self.writeSettingsFile )
        fileMenu.add_separator()
        fileMenu.add_command( label='Quit app', underline=0, command=self.doCloseMe, accelerator=self.keyBindingDict['Quit'][0] ) # quit app

        #editMenu = tk.Menu( self.menubar, tearoff=False )
        #self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        #editMenu.add_command( label='Find...', underline=0, command=self.notWrittenYet )
        #editMenu.add_command( label='Replace...', underline=0, command=self.notWrittenYet )

        gotoMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        gotoMenu.add_command( label='Previous book', underline=-1, command=self.doGotoPreviousBook )
        gotoMenu.add_command( label='Next book', underline=-1, command=self.doGotoNextBook )
        gotoMenu.add_command( label='Previous chapter', underline=-1, command=self.doGotoPreviousChapter )
        gotoMenu.add_command( label='Next chapter', underline=-1, command=self.doGotoNextChapter )
        gotoMenu.add_command( label='Previous section', underline=-1, command=self.notWrittenYet )
        gotoMenu.add_command( label='Next section', underline=-1, command=self.notWrittenYet )
        gotoMenu.add_command( label='Previous verse', underline=-1, command=self.doGotoPreviousVerse )
        gotoMenu.add_command( label='Next verse', underline=-1, command=self.doGotoNextVerse )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Forward', underline=0, command=self.doGoForward )
        gotoMenu.add_command( label='Backward', underline=0, command=self.doGoBackward )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Previous list item', underline=0, state=tk.DISABLED, command=self.doGotoPreviousListItem )
        gotoMenu.add_command( label='Next list item', underline=0, state=tk.DISABLED, command=self.doGotoNextListItem )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Book', underline=0, command=self.doGotoBook )

        projectMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=projectMenu, label='Project', underline=0 )
        projectMenu.add_command( label='New...', underline=0, command=self.doStartNewProject )
        #submenuNewType = tk.Menu( resourcesMenu, tearoff=False )
        #projectMenu.add_cascade( label='New...', underline=5, menu=submenuNewType )
        #submenuNewType.add_command( label='Text file...', underline=0, command=self.doOpenNewTextEditWindow )
        #projectMenu.add_command( label='Open', underline=0, command=self.notWrittenYet )
        submenuProjectOpenType = tk.Menu( projectMenu, tearoff=False )
        projectMenu.add_cascade( label='Open', underline=0, menu=submenuProjectOpenType )
        submenuProjectOpenType.add_command( label='Biblelator...', underline=0, command=self.doOpenBiblelatorProject )
        #submenuProjectOpenType.add_command( label='Bibledit...', underline=0, command=self.doOpenBibleditProject )
        submenuProjectOpenType.add_command( label='Paratext...', underline=0, command=self.doOpenParatextProject )
        projectMenu.add_separator()
        projectMenu.add_command( label='Backup...', underline=0, command=self.notWrittenYet )
        projectMenu.add_command( label='Restore...', underline=0, command=self.notWrittenYet )
        #projectMenu.add_separator()
        #projectMenu.add_command( label='Export', underline=1, command=self.doProjectExports )

        resourcesMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=resourcesMenu, label='Resources', underline=0 )
        submenuBibleResourceType = tk.Menu( resourcesMenu, tearoff=False )
        resourcesMenu.add_cascade( label='Open Bible/commentary', underline=5, menu=submenuBibleResourceType )
        submenuBibleResourceType.add_command( label='Online (DBP)...', underline=0, state=tk.NORMAL if self.internetAccessEnabled else tk.DISABLED, command=self.doOpenDBPBibleResource )
        submenuBibleResourceType.add_command( label='Sword module...', underline=0, command=self.doOpenSwordResource )
        submenuBibleResourceType.add_command( label='Other (local)...', underline=1, command=self.doOpenInternalBibleResource )
        submenuLexiconResourceType = tk.Menu( resourcesMenu, tearoff=False )
        resourcesMenu.add_cascade( label='Open lexicon', menu=submenuLexiconResourceType )
        #submenuLexiconResourceType.add_command( label='Hebrew...', underline=5, command=self.notWrittenYet )
        #submenuLexiconResourceType.add_command( label='Greek...', underline=0, command=self.notWrittenYet )
        submenuLexiconResourceType.add_command( label='Bible', underline=0, command=self.doOpenBibleLexiconResource )
        #submenuCommentaryResourceType = tk.Menu( resourcesMenu, tearoff=False )
        #resourcesMenu.add_cascade( label='Open commentary', underline=5, menu=submenuCommentaryResourceType )
        resourcesMenu.add_command( label='Open resource collection', underline=5, command=self.doOpenBibleResourceCollection )
        resourcesMenu.add_separator()
        resourcesMenu.add_command( label='Hide all resources', underline=0, command=self.doHideAllResources )
        resourcesMenu.add_command( label='Show all resources', underline=0, command=self.doShowAllResources )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Search files...', underline=0, command=self.onGrep )
        toolsMenu.add_separator()
        toolsMenu.add_command( label='Checks...', underline=0, command=self.notWrittenYet )
        toolsMenu.add_separator()
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Hide resources', underline=0, command=self.doHideAllResources )
        windowMenu.add_command( label='Hide all', underline=1, command=self.doHideAll )
        windowMenu.add_command( label='Show all', underline=0, command=self.doShowAll )
        windowMenu.add_command( label='Bring all here', underline=0, command=self.doBringAll )
        windowMenu.add_separator()
        windowMenu.add_command( label='Save window setup', underline=0, command=self.doSaveNewWindowSetup )
        if len(self.windowsSettingsDict)>1 or (self.windowsSettingsDict and 'Current' not in self.windowsSettingsDict):
            windowMenu.add_command( label='Delete a window setting', underline=0, command=self.doDeleteExistingWindowSetup )
            windowMenu.add_separator()
            for savedName in self.windowsSettingsDict:
                if savedName != 'Current':
                    windowMenu.add_command( label=savedName, underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        submenuWindowStyle = tk.Menu( windowMenu, tearoff=False )
        windowMenu.add_cascade( label='Theme', underline=0, menu=submenuWindowStyle )
        for themeName in self.style.theme_names():
            submenuWindowStyle.add_command( label=themeName.title(), underline=0, command=lambda tN=themeName: self.doChangeTheme(tN) )

        if BibleOrgSysGlobals.debugFlag:
            debugMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=debugMenu, label='Debug', underline=0 )
            debugMenu.add_command( label='View settings...', underline=0, command=self.doViewSettings )
            debugMenu.add_separator()
            debugMenu.add_command( label='View log...', underline=0, command=self.doViewLog )
            debugMenu.add_separator()
            debugMenu.add_command( label='Submit bug...', underline=0, command=self.doSubmitBug )
            debugMenu.add_separator()
            debugMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label='Help', underline=0 )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp, accelerator=self.keyBindingDict['Help'][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label='Submit bug...', underline=0, state=tk.NORMAL if self.internetAccessEnabled else tk.DISABLED, command=self.doSubmitBug )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout, accelerator=self.keyBindingDict['About'][0] )
    # end of Application.createMenuBar


    def createNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("createNavigationBar()") )
        Style().configure('NavigationBar.TFrame', background='yellow')

        navigationBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='NavigationBar.TFrame' )

        self.previousBCVButton = Button( navigationBar, width=4, text='<-', command=self.doGoBackward, state=tk.DISABLED )
        self.previousBCVButton.pack( side=tk.LEFT )
        self.nextBCVButton = Button( navigationBar, width=4, text='->', command=self.doGoForward, state=tk.DISABLED )
        self.nextBCVButton.pack( side=tk.LEFT )

        self.GroupAButton = Button( navigationBar, width=2, text='A', command=self.selectGroupA, state=tk.DISABLED )
        self.GroupBButton = Button( navigationBar, width=2, text='B', command=self.selectGroupB, state=tk.DISABLED )
        self.GroupCButton = Button( navigationBar, width=2, text='C', command=self.selectGroupC, state=tk.DISABLED )
        self.GroupDButton = Button( navigationBar, width=2, text='D', command=self.selectGroupD, state=tk.DISABLED )
        self.GroupAButton.pack( side=tk.LEFT )
        self.GroupBButton.pack( side=tk.LEFT )
        self.GroupCButton.pack( side=tk.LEFT )
        self.GroupDButton.pack( side=tk.LEFT )

        self.bookNames = [self.getBookName(BBB) for BBB in self.getBookList()]
        bookName = self.bookNames[0] # Default to Genesis usually
        self.bookNameVar = tk.StringVar()
        self.bookNameVar.set( bookName )
        BBB = self.getBBB( bookName )
        self.bookNameBox = Combobox( navigationBar, textvariable=self.bookNameVar )
        self.bookNameBox['values'] = self.bookNames
        self.bookNameBox['width'] = len( 'Deuteronomy' )
        self.bookNameBox.bind('<<ComboboxSelected>>', self.gotoNewBook )
        self.bookNameBox.pack( side=tk.LEFT )

        self.chapterNumberVar = tk.StringVar()
        self.chapterNumberVar.set( '1' )
        self.maxChapters = self.getNumChapters( BBB )
        #print( "maxChapters", self.maxChapters )
        self.chapterSpinbox = tk.Spinbox( navigationBar, from_=0.0, to=self.maxChapters, textvariable=self.chapterNumberVar )
        self.chapterSpinbox['width'] = 3
        self.chapterSpinbox['command'] = self.acceptNewBnCV
        self.chapterSpinbox.bind( '<Return>', self.gotoNewChapter )
        self.chapterSpinbox.pack( side=tk.LEFT )

        #self.chapterNumberVar = tk.StringVar()
        #self.chapterNumberVar.set( '1' )
        #self.chapterNumberBox = Entry( self, textvariable=self.chapterNumberVar )
        #self.chapterNumberBox['width'] = 3
        #self.chapterNumberBox.pack()

        self.verseNumberVar = tk.StringVar()
        self.verseNumberVar.set( '1' )
        #self.maxVersesVar = tk.StringVar()
        self.maxVerses = self.getNumVerses( BBB, self.chapterNumberVar.get() )
        #print( "maxVerses", self.maxVerses )
        #self.maxVersesVar.set( str(self.maxVerses) )
        # Add 1 to maxVerses to enable them to go to the next chapter
        self.verseSpinbox = tk.Spinbox( navigationBar, from_=0.0, to=1.0+self.maxVerses, textvariable=self.verseNumberVar )
        self.verseSpinbox['width'] = 3
        self.verseSpinbox['command'] = self.acceptNewBnCV
        self.verseSpinbox.bind( '<Return>', self.acceptNewBnCV )
        self.verseSpinbox.pack( side=tk.LEFT )

        #self.verseNumberVar = tk.StringVar()
        #self.verseNumberVar.set( '1' )
        #self.verseNumberBox = Entry( self, textvariable=self.verseNumberVar )
        #self.verseNumberBox['width'] = 3
        #self.verseNumberBox.pack()

        self.wordVar = tk.StringVar()
        self.wordBox = Entry( navigationBar, textvariable=self.wordVar )
        self.wordBox['width'] = 12
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
    # end of Application.createNavigationBar


    def createToolBar( self ):
        """
        Create a tool bar containing several buttons at the top of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("createToolBar()") )

        Style().configure('ToolBar.TFrame', background='green')

        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='ToolBar.TFrame' )
        Button( toolbar, text='Hide Resources', command=self.doHideAllResources ).pack( side=tk.LEFT, padx=2, pady=2 )
        Button( toolbar, text='Hide All', command=self.doHideAll ).pack( side=tk.LEFT, padx=2, pady=2 )
        Button( toolbar, text='Show All', command=self.doShowAll ).pack( side=tk.LEFT, padx=2, pady=2 )
        Button( toolbar, text='Bring All', command=self.doBringAll ).pack( side=tk.LEFT, padx=2, pady=2 )
        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of Application.createToolBar


    def halt( self ):
        """
        Halts the program immediately without saving any files or settings.
        Only used in debug mode.
        """
        logging.critical( "User selected HALT in DEBUG MODE. Not saving any files or settings!" )
        self.quit()
    # end of Application.halt


    def createDebugToolBar( self ):
        """
        Create a debug tool bar containing several additional buttons at the top of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("createDebugToolBar()") )
        Style().configure( 'DebugToolBar.TFrame', background='red' )
        Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='DebugToolBar.TFrame' )
        Button( toolbar, text='Halt', style='Halt.TButton', command=self.halt ).pack( side=tk.RIGHT, padx=2, pady=2 )
        Button( toolbar, text='Save settings', command=self.writeSettingsFile ).pack( side=tk.RIGHT, padx=2, pady=2 )
        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of Application.createDebugToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("createStatusBar()") )
        Style().configure( 'StatusBar.TLabel', background='pink' )

        self.statusTextVariable = tk.StringVar()
        self.statusTextLabel = Label( self.rootWindow, relief=tk.SUNKEN,
                                    textvariable=self.statusTextVariable, style='StatusBar.TLabel' )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.BOTTOM, fill=tk.X )
        self.statusTextVariable.set( '' ) # first initial value
        self.setWaitStatus( "Starting up..." )
    # end of Application.createStatusBar


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
            else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of Application.createMainKeyboardBindings()


    def notWrittenYet( self ):
        errorBeep()
        showerror( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of Application.notWrittenYet


    def getVerseKey( self, groupCode ):
        assert( groupCode in BIBLE_GROUP_CODES )
        if   groupCode == 'A': return self.GroupA_VerseKey
        elif groupCode == 'B': return self.GroupB_VerseKey
        elif groupCode == 'C': return self.GroupC_VerseKey
        elif groupCode == 'D': return self.GroupD_VerseKey
        else: halt
    # end of Application.getVerseKey


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("setStatus( {} )").format( repr(newStatusText) ) )
        #print( "SB is", repr( self.statusTextVariable.get() ) )
        if newStatusText != self.statusTextVariable.get(): # it's changed
            #self.statusBarTextWidget['state'] = tk.NORMAL
            #self.statusBarTextWidget.delete( '1.0', tk.END )
            #if newStatusText:
                #self.statusBarTextWidget.insert( '1.0', newStatusText )
            #self.statusBarTextWidget['state'] = tk.DISABLED # Don't allow editing
            #self.statusText = newStatusText
            self.statusTextVariable.set( newStatusText )
            self.statusTextLabel.update()
    # end of Application.setStatus

    def setWaitStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setWaitStatus( {} )").format( repr(newStatusText) ) )
        self.rootWindow.config( cursor='watch' ) # 'wait' can only be used on Windows
        self.setStatus( newStatusText )
        self.update()
    # end of Application.setWaitStatus

    def setReadyStatus( self ):
        """
        Sets the status line to "Ready"
            and sets the cursor to the normal cursor.
        """
        self.setStatus( _("Ready") )
        self.config( cursor='' )
    # end of Application.setReadyStatus


    def setDebugText( self, newMessage=None ):
        """
        """
        print( exp("setDebugText( {} )").format( repr(newMessage) ) )
        logging.info( 'Debug: ' + newMessage ) # Not sure why logging.debug isn't going into the file! XXXXXXXXXXXXX
        assert( BibleOrgSysGlobals.debugFlag )
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
                                    .format( j,
                                        appWin.winType,
                                        #appWin.winType.replace('ChildWindow',''),
                                        appWin.genericWindowType,
                                        #appWin.genericWindowType.replace('Resource',''),
                                        appWin.geometry(), appWin.moduleID,
                                        appWin.contextViewMode if 'Bible' in appWin.genericWindowType else 'N/A',
                                        appWin.BCVUpdateType if 'Bible' in appWin.genericWindowType else 'N/A' ) )
                                        #extra ) )
        #self.debugTextBox.insert( tk.END, '\n{} resource frames:'.format( len(self.childWindows) ) )
        #for j, projFrame in enumerate( self.childWindows ):
            #self.debugTextBox.insert( tk.END, "\n  {} {}".format( j, projFrame ) )
        self.debugTextBox['state'] = tk.DISABLED # Don't allow editing
    # end of Application.setDebugText


    def doChangeTheme( self, newThemeName ):
        """
        Set the window theme to the given scheme.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doChangeTheme( {} )").format( repr(newThemeName) ) )
            assert( newThemeName )
            self.setDebugText( 'Set theme to {}'.format( repr(newThemeName) ) )
        self.themeName = newThemeName
        try:
            self.style.theme_use( newThemeName )
        except tk.TclError as err:
            showerror( self, 'Error', err )
    # end of Application.doChangeTheme


    def parseAndApplySettings( self ):
        """
        Parse the settings out of the .INI file.
        """
        def retrieveWindowsSettings( self, windowsSettingsName ):
            """
            Gets a certain windows settings from the settings (INI) file information
                and puts it into a dictionary.

            Returns the dictionary.

            Called from parseAndApplySettings().
            """
            if BibleOrgSysGlobals.debugFlag:
                print( exp("retrieveWindowsSettings( {} )").format( repr(windowsSettingsName) ) )
                self.setDebugText( "retrieveWindowsSettings..." )
            windowsSettingsFields = self.settings.data['WindowSetting'+windowsSettingsName]
            resultDict = {}
            for j in range( 1, MAX_WINDOWS ):
                winNumber = 'window{}'.format( j )
                for keyName in windowsSettingsFields:
                    if keyName.startswith( winNumber ):
                        if winNumber not in resultDict: resultDict[winNumber] = {}
                        resultDict[winNumber][keyName[len(winNumber):]] = windowsSettingsFields[keyName]
            #print( exp("retrieveWindowsSettings"), resultDict )
            return resultDict
        # end of retrieveWindowsSettings


        if BibleOrgSysGlobals.debugFlag:
            print( exp("parseAndApplySettings()") )
            self.setDebugText( "parseAndApplySettings..." )
        try: self.minimumSize = self.settings.data[ProgName]['minimumSize']
        except KeyError: self.minimumSize = MINIMUM_MAIN_SIZE
        self.rootWindow.minsize( *parseWindowSize( self.minimumSize ) )
        try: self.maximumSize = self.settings.data[ProgName]['maximumSize']
        except KeyError: self.maximumSize = MAXIMUM_MAIN_SIZE
        self.rootWindow.maxsize( *parseWindowSize( self.maximumSize ) )
        #try: self.rootWindow.geometry( self.settings.data[ProgName]['windowGeometry'] )
        #except KeyError: print( "KeyError1" ) # we had no geometry set
        #except tk.TclError: logging.critical( exp("Application.__init__: Bad window geometry in settings file: {}").format( settings.data[ProgName]['windowGeometry'] ) )
        try:
            windowSize = self.settings.data[ProgName]['windowSize'] if 'windowSize' in self.settings.data[ProgName] else None
            windowPosition = self.settings.data[ProgName]['windowPosition'] if 'windowPosition' in self.settings.data[ProgName] else None
            #print( "ws", repr(windowSize), "wp", repr(windowPosition) )
            if windowSize and windowPosition: self.rootWindow.geometry( windowSize + '+' + windowPosition )
            else: logging.warning( "Settings.KeyError: no windowSize & windowPosition" )
        except KeyError: pass # no [ProgName] entries

        try: self.doChangeTheme( self.settings.data[ProgName]['themeName'] )
        except KeyError: logging.warning( "Settings.KeyError: no themeName" )

        # Internet stuff
        try:
            internetAccessString = self.settings.data['Internet']['internetAccess']
            self.internetAccessEnabled = internetAccessString == 'Enabled'
        except KeyError: self.internetAccessEnabled = False # default
        try:
            checkForMessagesString = self.settings.data['Internet']['checkForMessages']
            self.checkForMessagesEnabled = checkForMessagesString == 'Enabled'
        except KeyError: self.checkForMessagesEnabled = True # default
        try:
            lastMessageNumberString = self.settings.data['Internet']['lastMessageNumberRead']
            self.lastMessageNumberRead = int( lastMessageNumberString )
        except (KeyError, ValueError): self.lastMessageNumberRead = -1
        try:
            sendUsageStatisticsString = self.settings.data['Internet']['sendUsageStatistics']
            self.sendUsageStatisticsEnabled = sendUsageStatisticsString == 'Enabled'
        except KeyError: self.sendUsageStatisticsEnabled = True # default
        try:
            automaticUpdatesString = self.settings.data['Internet']['automaticUpdates']
            self.automaticUpdatesEnabled = automaticUpdatesString == 'Enabled'
        except KeyError: self.automaticUpdatesEnabled = True # default
        try:
            useDevelopmentVersionsString = self.settings.data['Internet']['useDevelopmentVersions']
            self.useDevelopmentVersionsEnabled = useDevelopmentVersionsString == 'Enabled'
        except KeyError: self.useDevelopmentVersionsEnabled = False # default
        try:
            cloudBackupsString = self.settings.data['Internet']['cloudBackups']
            self.cloudBackupsEnabled = cloudBackupsString == 'Enabled'
        except KeyError: self.cloudBackupsEnabled = True # default

        try: self.currentVerseKeyGroup = self.settings.data['BCVGroups']['currentGroup']
        except KeyError: self.currentVerseKeyGroup = 'A'
        try: self.GroupA_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['A-Book'],self.settings.data['BCVGroups']['A-Chapter'],self.settings.data['BCVGroups']['A-Verse'])
        except KeyError: self.GroupA_VerseKey = SimpleVerseKey( self.getFirstBookCode(), '1', '1' )
        try: self.GroupB_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['B-Book'],self.settings.data['BCVGroups']['B-Chapter'],self.settings.data['BCVGroups']['B-Verse'])
        except KeyError: self.GroupB_VerseKey = SimpleVerseKey( 'PSA', '119', '1' )
        try: self.GroupC_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['C-Book'],self.settings.data['BCVGroups']['C-Chapter'],self.settings.data['BCVGroups']['C-Verse'])
        except KeyError: self.GroupC_VerseKey = SimpleVerseKey( 'MAT', '1', '1' )
        try: self.GroupD_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['D-Book'],self.settings.data['BCVGroups']['D-Chapter'],self.settings.data['BCVGroups']['D-Verse'])
        except KeyError: self.GroupD_VerseKey = SimpleVerseKey( 'REV', '22', '1' )

        try: self.lexiconWord = self.settings.data['Lexicon']['currentWord']
        except KeyError: self.lexiconWord = None

        # We keep our copy of all the windows settings in self.windowsSettingsDict
        windowsSettingsNamesList = []
        for name in self.settings.data:
            if name.startswith( 'WindowSetting' ): windowsSettingsNamesList.append( name[13:] )
        if BibleOrgSysGlobals.debugFlag: print( exp("Available windows settings are: {}").format( windowsSettingsNamesList ) )
        if windowsSettingsNamesList: assert( 'Current' in windowsSettingsNamesList )
        self.windowsSettingsDict = {}
        for windowsSettingsName in windowsSettingsNamesList:
            self.windowsSettingsDict[windowsSettingsName] = retrieveWindowsSettings( self, windowsSettingsName )
        if 'Current' in windowsSettingsNamesList: self.applyGivenWindowsSettings( 'Current' )
        else: logging.critical( exp("Application.parseAndApplySettings: No current window settings available") )
    # end of Application.parseAndApplySettings


    def applyGivenWindowsSettings( self, givenWindowsSettingsName ):
        """
        Given the name of windows settings,
            find the settings in our dictionary
            and then apply it by creating the windows.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("applyGivenWindowsSettings( {} )").format( repr(givenWindowsSettingsName) ) )
            self.setDebugText( "applyGivenWindowsSettings..." )
        windowsSettingsFields = self.windowsSettingsDict[givenWindowsSettingsName]
        for j in range( 1, MAX_WINDOWS ):
            winNumber = 'window{}'.format( j )
            if winNumber in windowsSettingsFields:
                thisStuff = windowsSettingsFields[winNumber]
                winType = thisStuff['Type']
                #windowGeometry = thisStuff['Geometry'] if 'Geometry' in thisStuff else None
                windowSize = thisStuff['Size'] if 'Size' in thisStuff else None
                windowPosition = thisStuff['Position'] if 'Position' in thisStuff else None
                windowGeometry = windowSize+'+'+windowPosition if windowSize and windowPosition else None
                #print( winType, windowGeometry )
                if winType == 'SwordBibleResourceWindow':
                    rw = self.openSwordBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                    #except: logging.critical( "Unable to read all SwordBibleResourceWindow {} settings".format( j ) )
                elif winType == 'DBPBibleResourceWindow':
                    rw = self.openDBPBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                    #except: logging.critical( "Unable to read all DBPBibleResourceWindow {} settings".format( j ) )
                elif winType == 'InternalBibleResourceWindow':
                    rw = self.openInternalBibleResourceWindow( thisStuff['BibleFolderPath'], windowGeometry )
                    #except: logging.critical( "Unable to read all InternalBibleResourceWindow {} settings".format( j ) )

                #elif winType == 'HebrewLexiconResourceWindow':
                    #self.openHebrewLexiconResourceWindow( thisStuff['HebrewLexiconPath'], windowGeometry )
                    ##except: logging.critical( "Unable to read all HebrewLexiconResourceWindow {} settings".format( j ) )
                #elif winType == 'GreekLexiconResourceWindow':
                    #self.openGreekLexiconResourceWindow( thisStuff['GreekLexiconPath'], windowGeometry )
                    ##except: logging.critical( "Unable to read all GreekLexiconResourceWindow {} settings".format( j ) )
                elif winType == 'BibleLexiconResourceWindow':
                    rw = self.openBibleLexiconResourceWindow( thisStuff['BibleLexiconPath'], windowGeometry )
                    #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )

                elif winType == 'BibleResourceCollectionWindow':
                    collectionName = thisStuff['CollectionName']
                    rw = self.openBibleResourceCollectionWindow( collectionName, windowGeometry )
                    #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )
                    if 'BibleResourceCollection'+collectionName in self.settings.data:
                        collectionSettingsFields = self.settings.data['BibleResourceCollection'+collectionName]
                        for k in range( 1, MAX_WINDOWS ):
                            boxNumber = 'box{}'.format( k )
                            boxType = boxSource = None
                            for keyname in collectionSettingsFields:
                                if keyname.startswith( boxNumber ):
                                    #print( "found", keyname, "setting for", collectionName, "collection" )
                                    if keyname == boxNumber+'Type': boxType = collectionSettingsFields[keyname]
                                    elif keyname == boxNumber+'Source': boxSource = collectionSettingsFields[keyname]
                                    else:
                                        print( "Unknown {} collection key: {} = {}".format( repr(collectionName), keyname, collectionSettingsFields[keyname] ) )
                                        if BibleOrgSysGlobals.debugFlag: halt
                            if boxType and boxSource: rw.openBox( boxType, boxSource )

                elif winType == 'BibleReferenceCollectionWindow':
                    xyz = "JustTesting!"
                    rw = self.openBibleReferenceCollectionWindow( xyz, windowGeometry )
                    #except: logging.critical( "Unable to read all BibleLexiconResourceWindow {} settings".format( j ) )

                elif winType == 'PlainTextEditWindow':
                    rw = self.doOpenNewTextEditWindow()
                    #except: logging.critical( "Unable to read all PlainTextEditWindow {} settings".format( j ) )
                elif winType == 'BiblelatorUSFMBibleEditWindow':
                    rw = self.openBiblelatorBibleEditWindow( thisStuff['ProjectFolderPath'], thisStuff['EditMode'], windowGeometry )
                    #except: logging.critical( "Unable to read all BiblelatorUSFMBibleEditWindow {} settings".format( j ) )
                elif winType == 'ParatextUSFMBibleEditWindow':
                    rw = self.openParatextBibleEditWindow( thisStuff['SSFFilepath'], thisStuff['EditMode'], windowGeometry )
                    #except: logging.critical( "Unable to read all ParatextUSFMBibleEditWindow {} settings".format( j ) )
                elif winType == 'ESFMEditWindow':
                    rw = self.openESFMEditWindow( thisStuff['ESFMFolder'], thisStuff['EditMode'], windowGeometry )
                    #except: logging.critical( "Unable to read all ESFMEditWindow {} settings".format( j ) )

                else:
                    logging.critical( exp("Application.__init__: Unknown {} window type").format( repr(winType) ) )
                    if BibleOrgSysGlobals.debugFlag: halt

                if rw is None:
                    logging.critical( exp("Application.__init__: Failed to reopen {} window type!!! How did this happen?").format( repr(winType) ) )
                else: # we've opened our child window -- now customize it a bit more
                    minimumSize = thisStuff['MinimumSize'] if 'MinimumSize' in thisStuff else None
                    if minimumSize:
                        if BibleOrgSysGlobals.debugFlag: assert( 'x' in minimumSize )
                        rw.minsize( *parseWindowSize( minimumSize ) )
                    maximumSize = thisStuff['MaximumSize'] if 'MaximumSize' in thisStuff else None
                    if maximumSize:
                        if BibleOrgSysGlobals.debugFlag: assert( 'x' in maximumSize )
                        rw.maxsize( *parseWindowSize( maximumSize ) )
                    groupCode = thisStuff['GroupCode'] if 'GroupCode' in thisStuff else None
                    if groupCode:
                        if BibleOrgSysGlobals.debugFlag: assert( groupCode in BIBLE_GROUP_CODES )
                        rw.groupCode = groupCode
                    contextViewMode = thisStuff['ContextViewMode'] if 'ContextViewMode' in thisStuff else None
                    if contextViewMode:
                        if BibleOrgSysGlobals.debugFlag: assert( contextViewMode in BIBLE_CONTEXT_VIEW_MODES )
                        rw.contextViewMode = contextViewMode
                        rw.createMenuBar() # in order to show the correct contextViewMode
    # end of Application.applyGivenWindowsSettings


    def doCheckForDeveloperMessages( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("Application.doCheckForDeveloperMessages()") )

        import requests
        try: ri = requests.get( "http://Freely-Given.org/Software/Biblelator/DevMsg/DevMsg.idx" )
        except Exception as err:
            logging.critical( exp("doCheckForDeveloperMessages: Unable to check for developer messages") )
            logging.info( exp("doCheckForDeveloperMessages: {}").format( err ) )
            showerror( self, 'Check for Developer Messages Error', err )
            return
        #print( 'Status', repr(ri.status_code) )
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
                ab = AboutBox( self.rootWindow, APP_NAME, aboutInfo )

                self.lastMessageNumberRead += 1
    # end of Application.doCheckForDeveloperMessages


    def getCurrentChildWindowSettings( self ):
        """
        Go through the currently open windows and get their settings data
            and save it in self.windowsSettingsDict['Current'].
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("getCurrentChildWindowSettings()") )
        if 'Current' in self.windowsSettingsDict: del self.windowsSettingsDict['Current']
        self.windowsSettingsDict['Current'] = {}
        for j, appWin in enumerate( self.childWindows ):
                if appWin.winType == 'HTMLWindow':
                    continue # We don't save these

                winNumber = "window{}".format( j+1 )
                self.windowsSettingsDict['Current'][winNumber] = {}
                thisOne = self.windowsSettingsDict['Current'][winNumber]
                thisOne['Type'] = appWin.winType #.replace( 'Window', 'Window' )
                thisOne['Size'], thisOne['Position'] = appWin.geometry().split( '+', 1 )
                thisOne['MinimumSize'] = assembleWindowSize( *appWin.minsize() )
                thisOne['MaximumSize'] = assembleWindowSize( *appWin.maxsize() )
                if appWin.winType == 'SwordBibleResourceWindow':
                    thisOne['ModuleAbbreviation'] = appWin.moduleID
                elif appWin.winType == 'DBPBibleResourceWindow':
                    thisOne['ModuleAbbreviation'] = appWin.moduleID
                elif appWin.winType == 'InternalBibleResourceWindow':
                    thisOne['BibleFolderPath'] = appWin.moduleID

                #elif appWin.winType == 'HebrewLexiconResourceWindow':
                    #thisOne['HebrewLexiconPath'] = appWin.lexiconPath
                #elif appWin.winType == 'GreekLexiconResourceWindow':
                    #thisOne['HebrewLexiconPath'] = appWin.lexiconPath
                elif appWin.winType == 'BibleLexiconResourceWindow':
                    thisOne['BibleLexiconPath'] = appWin.moduleID

                elif appWin.winType == 'BibleResourceCollectionWindow':
                    thisOne['CollectionName'] = appWin.moduleID

                elif appWin.winType == 'PlainTextEditWindow':
                    pass # ???

                elif appWin.winType == 'BiblelatorUSFMBibleEditWindow':
                    thisOne['ProjectFolderPath'] = appWin.moduleID
                    thisOne['EditMode'] = appWin.editMode
                elif appWin.winType == 'ParatextUSFMBibleEditWindow':
                    thisOne['SSFFilepath'] = appWin.moduleID
                    thisOne['EditMode'] = appWin.editMode

                elif appWin.winType == 'HTMLWindow':
                    pass # We don't save these

                else:
                    logging.critical( exp("getCurrentChildWindowSettings: Unknown {} window type").format( repr(appWin.winType) ) )
                    if BibleOrgSysGlobals.debugFlag: halt

                if 'Bible' in appWin.genericWindowType:
                    try: thisOne['GroupCode'] = appWin.groupCode
                    except AttributeError: logging.critical( exp("getCurrentChildWindowSettings: Why no groupCode in {}").format( appWin.winType ) )
                    try: thisOne['ContextViewMode'] = appWin.contextViewMode
                    except AttributeError: logging.critical( exp("getCurrentChildWindowSettings: Why no contextViewMode in {}").format( appWin.winType ) )
    # end of Application.getCurrentChildWindowSettings


    def doSaveNewWindowSetup( self ):
        """
        Gets the name for the new window setup and saves the information.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doSaveNewWindowSetup()") )
            self.setDebugText( "doSaveNewWindowSetup..." )
        swnd = SaveWindowNameDialog( self, self.windowsSettingsDict, title=_('Save window setup') )
        if BibleOrgSysGlobals.debugFlag: print( "swndResult", repr(swnd.result) )
        if swnd.result:
            self.getCurrentChildWindowSettings()
            self.windowsSettingsDict[swnd.result] = self.windowsSettingsDict['Current'] # swnd.result is the new window name
            print( "swS", self.windowsSettingsDict )
            self.writeSettingsFile() # Save file now in case we crash
            self.createMenuBar() # refresh
    # end of Application.doSaveNewWindowSetup


    def doDeleteExistingWindowSetup( self ):
        """
        Gets the name of an existing window setting and deletes the setting.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doDeleteExistingWindowSetup()") )
            self.setDebugText( "doDeleteExistingWindowSetup..." )
        assert( self.windowsSettingsDict and (len(self.windowsSettingsDict)>1 or 'Current' not in self.windowsSettingsDict) )
        dwnd = DeleteWindowNameDialog( self, self.windowsSettingsDict, title=_('Delete saved window setup') )
        if BibleOrgSysGlobals.debugFlag: print( "dwndResult", repr(dwnd.result) )
        if dwnd.result:
            if BibleOrgSysGlobals.debugFlag:
                assert( dwnd.result in self.windowsSettingsDict )
            del self.windowsSettingsDict[dwnd.result]
            #self.settings.save() # Save file now in case we crash -- don't worry -- it's easy to delete one
            self.createMenuBar() # refresh
    # end of Application.doDeleteExistingWindowSetup


    def doOpenDBPBibleResource( self ):
        """
        Open an online DigitalBiblePlatform Bible (called from a menu/GUI action).

        Requests a version name from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doOpenDBPBibleResource()") )
            self.setDebugText( "doOpenDBPBibleResource..." )

        if self.internetAccessEnabled:
            self.setWaitStatus( "doOpenDBPBibleResource..." )
            if self.DBPInterface is None:
                self.DBPInterface = DBPBibles()
                availableVolumes = self.DBPInterface.fetchAllEnglishTextVolumes()
                #print( "aV1", repr(availableVolumes) )
                if availableVolumes:
                    srb = SelectResourceBoxDialog( self, [(x,y) for x,y in availableVolumes.items()], title=_('Open DBP resource') )
                    #print( "srbResult", repr(srb.result) )
                    if srb.result:
                        for entry in srb.result:
                            self.openDBPBibleResourceWindow( entry[1] )
                        #self.acceptNewBnCV()
                        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
                    elif BibleOrgSysGlobals.debugFlag: print( exp("doOpenDBPBibleResource: no resource selected!") )
                else:
                    logging.critical( exp("doOpenDBPBibleResource: no volumes available") )
                    self.setStatus( "Digital Bible Platform unavailable (offline?)" )
        else: # no Internet allowed
            logging.critical( exp("doOpenDBPBibleResource: Internet not enabled") )
            self.setStatus( "Digital Bible Platform unavailable (You have disabled Internet access.)" )

        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doOpenDBPBibleResource" )
    # end of Application.doOpenDBPBibleResource

    def openDBPBibleResourceWindow( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested DBP Bible resource window.

        Returns the new DBPBibleResourceWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openDBPBibleResourceWindow()") )
            self.setDebugText( "openDBPBibleResourceWindow..." )
            assert( moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6 )
        dBRW = DBPBibleResourceWindow( self, moduleAbbreviation )
        if windowGeometry: dBRW.geometry( windowGeometry )
        if dBRW.DBPModule is None:
            logging.critical( exp("Application.openDBPBibleResourceWindow: Unable to open resource {}").format( repr(moduleAbbreviation) ) )
            dBRW.closeChildWindow()
            showerror( self, APP_NAME, _("Sorry, unable to open DBP resource") )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed openDBPBibleResourceWindow" )
            self.setReadyStatus()
            return None
        else:
            dBRW.updateShownBCV( self.getVerseKey( dBRW.groupCode ) )
            self.childWindows.append( dBRW )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openDBPBibleResourceWindow" )
            self.setReadyStatus()
            return dBRW
    # end of Application.openDBPBibleResourceWindow


    def doOpenSwordResource( self ):
        """
        Open a local Sword Bible (called from a menu/GUI action).

        Requests a module abbreviation from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openSwordResource()") )
            self.setDebugText( "doOpenSwordResource..." )
        self.setStatus( "doOpenSwordResource..." )
        if self.SwordInterface is None and SwordType is not None:
            self.SwordInterface = SwordInterface() # Load the Sword library
        if self.SwordInterface is None: # still
            logging.critical( exp("doOpenSwordResource: no Sword interface available") )
            showerror( self, APP_NAME, _("Sorry, no Sword interface discovered") )
            return
        #availableSwordModules = self.SwordInterface.library
        #print( "aM1", availableSwordModules )
        #ourList = None
        #if availableSwordModules is not None:
        givenList = self.SwordInterface.getAvailableModuleCodeTuples( ['Biblical Texts','Commentaries'] )
        genericName = { 'RawText':'Bible', 'zText':'Bible', 'RawCom':'Commentary', 'RawCom4':'Commentary', 'zCom':'Commentary' }
        genericName = { 'Biblical Texts':'Bible', 'Commentaries':'Commentary' }
        ourList = ['{} ({})'.format(moduleRoughName,genericName[moduleType]) for moduleRoughName,moduleType in givenList]
        if BibleOrgSysGlobals.debugFlag: print( "{} Sword module codes available".format( len(ourList) ) )
        #print( "ourList", ourList )
        if ourList:
            srb = SelectResourceBoxDialog( self, ourList, title=_("Open Sword resource") )
            print( "srbResult", repr(srb.result) )
            if srb.result:
                for entryString in srb.result:
                    requestedModuleName, rest = entryString.split( ' (', 1 )
                    self.setWaitStatus( _("Loading {} Sword module...").format( repr(requestedModuleName) ) )
                    self.openSwordBibleResourceWindow( requestedModuleName )
                #self.acceptNewBnCV()
                #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
            elif BibleOrgSysGlobals.debugFlag: print( exp("doOpenSwordResource: no resource selected!") )
        else:
            logging.critical( exp("doOpenSwordResource: no list available") )
            showerror( self, APP_NAME, _("No Sword resources discovered") )
        #self.acceptNewBnCV()
        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.doOpenSwordResource

    def openSwordBibleResourceWindow( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested Sword Bible resource window.

        Returns the new SwordBibleResourceWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openSwordBibleResourceWindow()") )
            self.setDebugText( "openSwordBibleResourceWindow..." )
        if self.SwordInterface is None:
            self.SwordInterface = SwordInterface() # Load the Sword library
        swBRW = SwordBibleResourceWindow( self, moduleAbbreviation )
        if windowGeometry: swBRW.geometry( windowGeometry )
        swBRW.updateShownBCV( self.getVerseKey( swBRW.groupCode ) )
        self.childWindows.append( swBRW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openSwordBibleResourceWindow" )
        self.setReadyStatus()
        return swBRW
    # end of Application.openSwordBibleResourceWindow


    def doOpenInternalBibleResource( self ):
        """
        Open a local Bible (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openInternalBibleResource()") )
            self.setDebugText( "doOpenInternalBibleResource..." )
        self.setStatus( "doOpenInternalBibleResource..." )
        #requestedFolder = askdirectory()
        openDialog = Directory( title=_("Select Bible folder"), initialdir=self.lastInternalBibleDir )
        requestedFolder = openDialog.show()
        if requestedFolder:
            self.lastInternalBibleDir = requestedFolder
            self.openInternalBibleResourceWindow( requestedFolder )
            #self.acceptNewBnCV()
            #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.doOpenInternalBibleResource

    def openInternalBibleResourceWindow( self, modulePath, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible resource window.

        Returns the new InternalBibleResourceWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openInternalBibleResourceWindow()") )
            self.setDebugText( "openInternalBibleResourceWindow..." )
        iBRW = InternalBibleResourceWindow( self, modulePath )
        if windowGeometry: iBRW.geometry( windowGeometry )
        if iBRW.internalBible is None:
            logging.critical( exp("Application.openInternalBibleResourceWindow: Unable to open resource {}").format( repr(modulePath) ) )
            iBRW.closeChildWindow()
            showerror( self, APP_NAME, _("Sorry, unable to open internal Bible resource") )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed openInternalBibleResourceWindow" )
            self.setReadyStatus()
            return None
        else:
            iBRW.updateShownBCV( self.getVerseKey( iBRW.groupCode ) )
            self.childWindows.append( iBRW )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openInternalBibleResourceWindow" )
            self.setReadyStatus()
            return iBRW
    # end of Application.openInternalBibleResourceWindow


    def doOpenBibleLexiconResource( self ):
        """
        Open the Bible lexicon (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doOpenBibleLexiconResource()") )
            self.setDebugText( "doOpenBibleLexiconResource..." )
        self.setWaitStatus( "doOpenBibleLexiconResource..." )
        #requestedFolder = askdirectory()
        #if requestedFolder:
        requestedFolder = None
        self.openBibleLexiconResourceWindow( requestedFolder )
        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.doOpenBibleLexiconResource

    def openBibleLexiconResourceWindow( self, lexiconPath, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible lexicon resource window.

        Returns the new BibleLexiconResourceWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openBibleLexiconResourceWindow()") )
            self.setDebugText( "openBibleLexiconResourceWindow..." )
        if lexiconPath is None: lexiconPath = "../"
        bLRW = BibleLexiconResourceWindow( self, lexiconPath )
        if windowGeometry: bLRW.geometry( windowGeometry )
        if bLRW.BibleLexicon is None:
            logging.critical( exp("Application.openBibleLexiconResourceWindow: Unable to open Bible lexicon resource {}").format( repr(lexiconPath) ) )
            bLRW.closeChildWindow()
            showerror( self, APP_NAME, _("Sorry, unable to open Bible lexicon resource") )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed openBibleLexiconResourceWindow" )
            self.setReadyStatus()
            return None
        else:
            if self.lexiconWord: bLRW.updateLexiconWord( self.lexiconWord )
            self.childWindows.append( bLRW )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openBibleLexiconResourceWindow" )
            self.setReadyStatus()
            return bLRW
    # end of Application.openBibleLexiconResourceWindow


    def doOpenBibleResourceCollection( self ):
        """
        Open a collection of Bible resources (called from a menu/GUI action).
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doOpenBibleResourceCollection()") )
            self.setDebugText( "doOpenBibleResourceCollection..." )
        self.setStatus( "doOpenBibleResourceCollection..." )
        existingNames = []
        for cw in self.childWindows:
            existingNames.append( cw.moduleID.upper() )
        gncn = GetNewCollectionNameDialog( self, existingNames, title=_("New Collection Name") )
        if gncn.result: self.openBibleResourceCollectionWindow( gncn.result )
    # end of Application.doOpenBibleResourceCollection

    def openBibleResourceCollectionWindow( self, collectionName, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible resource collection window.

        Returns the new BibleCollectionWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openBibleResourceCollectionWindow( {} )").format( repr(collectionName) ) )
            self.setDebugText( "openBibleResourceCollectionWindow..." )
        BRC = BibleResourceCollectionWindow( self, collectionName )
        if windowGeometry: BRC.geometry( windowGeometry )
        #if BRC.internalBible is None:
        #    logging.critical( exp("Application.openBibleResourceCollection: Unable to open resource {}").format( repr(modulePath) ) )
        #    BRC.closeChildWindow()
        #    showerror( self, APP_NAME, _("Sorry, unable to open internal Bible resource") )
        #    if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed openInternalBibleResourceWindow" )
        #    self.setReadyStatus()
        #    return None
        #else:
        BRC.updateShownBCV( self.getVerseKey( BRC.groupCode ) )
        self.childWindows.append( BRC )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openBibleResourceCollection" )
        self.setReadyStatus()
        return BRC
    # end of Application.openBibleResourceCollectionWindow


    def doOpenBibleReferenceCollection( self ):
        """
        Open a collection of Bible References (called from a menu/GUI action).
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doOpenBibleReferenceCollection()") )
            self.setDebugText( "doOpenBibleReferenceCollection..." )
        self.setStatus( "doOpenBibleReferenceCollection..." )
        existingNames = []
        for cw in self.childWindows:
            existingNames.append( cw.moduleID.upper() )
        gncn = GetNewCollectionNameDialog( self, existingNames, title=_("New Collection Name") )
        if gncn.result: self.openBibleReferenceCollectionWindow( gncn.result )
    # end of Application.doOpenBibleReferenceCollection

    def openBibleReferenceCollectionWindow( self, collectionName, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible Reference collection window.

        Returns the new BibleCollectionWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openBibleReferenceCollectionWindow( {} )").format( repr(collectionName) ) )
            self.setDebugText( "openBibleReferenceCollectionWindow..." )
        BRC = BibleReferenceCollectionWindow( self, collectionName )
        if windowGeometry: BRC.geometry( windowGeometry )
        #if BRC.internalBible is None:
        #    logging.critical( exp("Application.openBibleReferenceCollection: Unable to open Reference {}").format( repr(modulePath) ) )
        #    BRC.closeChildWindow()
        #    showerror( self, APP_NAME, _("Sorry, unable to open internal Bible Reference") )
        #    if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed openInternalBibleReferenceWindow" )
        #    self.setReadyStatus()
        #    return None
        #else:
        BRC.updateShownReferences( mapReferencesVerseKey( self.getVerseKey( BIBLE_GROUP_CODES[0] ) ) )
        self.childWindows.append( BRC )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openBibleReferenceCollection" )
        self.setReadyStatus()
        return BRC
    # end of Application.openBibleReferenceCollectionWindow


    def doOpenNewTextEditWindow( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doOpenNewTextEditWindow()") )
            self.setDebugText( "doOpenNewTextEditWindow..." )
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        self.childWindows.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doOpenNewTextEditWindow" )
        self.setReadyStatus()
    # end of Application.doOpenNewTextEditWindow


    def doOpenFileTextEditWindow( self ):
        """
        Open a pop-up window and request the user to select a file.

        Then open the file in a plain text edit window.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doOpenFileTextEditWindow()") )
            self.setDebugText( "doOpenFileTextEditWindow..." )
        openDialog = Open( initialdir=self.lastFileDir, filetypes=TEXT_FILETYPES )
        fileResult = openDialog.show()
        if not fileResult: return
        if not os.path.isfile( fileResult ):
            showerror( self, APP_NAME, 'Could not open file ' + fileResult )
            return
        text = open( fileResult, 'rt', encoding='utf-8' ).read()
        if text == None:
            showerror( self, APP_NAME, 'Could not decode and open file ' + fileResult )
        else:
            tEW = TextEditWindow( self )
            tEW.setFilepath( fileResult )
            tEW.setAllText( text )
            #if windowGeometry: tEW.geometry( windowGeometry )
            self.childWindows.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doOpenFileTextEditWindow" )
        self.setReadyStatus()
    # end of Application.doOpenFileTextEditWindow


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doViewSettings()") )
            self.setDebugText( "doViewSettings..." )
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setFilepath( self.settings.settingsFilepath ) \
        or not tEW.loadText():
            tEW.closeChildWindow()
            showerror( self, APP_NAME, _("Sorry, unable to open settings file") )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed doViewSettings" )
        else:
            self.childWindows.append( tEW )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewSettings" )
        self.setReadyStatus()
    # end of Application.doViewSettings


    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doViewLog()") )
            self.setDebugText( "doViewLog..." )
        filename = ProgName.replace('/','-').replace(':','_').replace('\\','_') + '_log.txt'
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setPathAndFile( self.loggingFolderPath, filename ) \
        or not tEW.loadText():
            tEW.closeChildWindow()
            showerror( self, APP_NAME, _("Sorry, unable to open log file") )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Failed doViewLog" )
        else:
            self.childWindows.append( tEW )
            #if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewLog" ) # Don't do this -- adds to the log immediately
        self.setReadyStatus()
    # end of Application.doViewLog


    def doStartNewProject( self ):
        """
        Asks the user for a project name and abbreviation,
            creates the new folder,
            offers to create blank books,
        and then opens an editor window.
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( exp("doStartNewProject()") )
        gnpn = GetNewProjectNameDialog( self, title=_("New Project Name") )
        if not gnpn.result: return
        if gnpn.result: # This is a dictionary
            projName, projAbbrev = gnpn.result['Name'], gnpn.result['Abbreviation']
            newFolderPath = os.path.join( self.homeFolderPath, DATA_FOLDER_NAME, projAbbrev )
            if os.path.isdir( newFolderPath ):
                showerror( self, _("New Project"), _("Sorry, we already have a {!r} project folder in {}") \
                                            .format( projAbbrev, os.path.join( self.homeFolderPath, DATA_FOLDER_NAME ) ) )
                return None
            os.mkdir( newFolderPath )

            #availableVersifications = ['KJV',]
            bvss = BibleVersificationSystems().loadData() # Doesn't reload the XML unnecessarily :)
            availableVersifications = bvss.getAvailableVersificationSystemNames()
            thisBBB = self.getVerseKey( BIBLE_GROUP_CODES[0] ).getBBB() # New windows start in group 0
            cnpf = CreateNewProjectFilesDialog( self, _("Create blank {} files").format( projAbbrev ),
                                thisBBB, availableVersifications )
            #if not cnpf.result: return
            if cnpf.result: # This is a dictionary
                print( "Dialog results:", cnpf.result )
                if cnpf.result['Fill'] == 'Version': # Need to find a USFM project to copy
                    openDialog = Directory( title=_("Select USFM folder"), initialdir=self.lastInternalBibleDir )
                    requestedFolder = openDialog.show()
                    if requestedFolder:
                        self.lastInternalBibleDir = requestedFolder
                        cnpf.result['Version'] = requestedFolder
                    #else: return
                createEmptyUSFMBooks( newFolderPath, thisBBB, cnpf.result )

            uB = USFMBible( newFolderPath ) # Get a blank object
            uB.name, uB.abbreviation = projName, projAbbrev
            uEW = USFMEditWindow( self, uB )
            uEW.winType = 'BiblelatorUSFMBibleEditWindow' # override the default
            uEW.moduleID = newFolderPath
            uEW.setFolderPath( newFolderPath )
            uEW.settings = ProjectSettings( newFolderPath )
            uEW.settings.saveNameAndAbbreviation( projName, projAbbrev )
            if cnpf.result: uEW.settings.saveNewBookSettings( cnpf.result )
            uEW.updateShownBCV( self.getVerseKey( uEW.groupCode ) )
            self.childWindows.append( uEW )
            if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doStartNewProject" )
            self.setReadyStatus()
            return uEW
    # end of Application.doStartNewProject


    def doOpenBiblelatorProject( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( exp("doOpenBiblelatorProject()") )
        openDialog = Open( initialdir=self.lastBiblelatorFileDir, filetypes=BIBLELATOR_PROJECT_FILETYPES )
        projectSettingsFilepath = openDialog.show()
        if not projectSettingsFilepath: return
        if not os.path.isfile( projectSettingsFilepath ):
            showerror( self, APP_NAME, 'Could not open file ' + projectSettingsFilepath )
            return
        containingFolderPath, settingsFilename = os.path.split( projectSettingsFilepath )
        if BibleOrgSysGlobals.debugFlag: assert( settingsFilename == 'ProjectSettings.ini' )
        self.openBiblelatorBibleEditWindow( containingFolderPath )
    # end of Application.doOpenBiblelatorProject

    def openBiblelatorBibleEditWindow( self, projectFolderPath, editMode=None, windowGeometry=None ):
        """
        Create the actual requested local Biblelator Bible project window.

        Returns the new USFMEditWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openBiblelatorBibleEditWindow( {!r} )").format( projectFolderPath ) )
            self.setDebugText( "openBiblelatorBibleEditWindow..." )
            assert( os.path.isdir( projectFolderPath ) )

        uB = USFMBible( projectFolderPath )
        uEW = USFMEditWindow( self, uB, editMode=editMode )
        if windowGeometry: uEW.geometry( windowGeometry )
        uEW.winType = 'BiblelatorUSFMBibleEditWindow' # override the default
        uEW.moduleID = projectFolderPath
        uEW.setFolderPath( projectFolderPath )
        uEW.settings = ProjectSettings( projectFolderPath )
        uEW.settings.loadUSFMMetadataInto( uB )
        uEW.updateShownBCV( self.getVerseKey( uEW.groupCode ) )
        self.childWindows.append( uEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openBiblelatorBibleEditWindow" )
        self.setReadyStatus()
        return uEW
    # end of Application.openBiblelatorBibleEditWindow



    #def doOpenBibleditProject( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( exp("doOpenBibleditProject()") )
        #self.notWrittenYet()
    ## end of Application.doOpenBibleditProject


    def doOpenParatextProject( self ):
        """
        Open the Paratext Bible project (called from a menu/GUI action).

        Requests a SSF file from the user.
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
            print( exp("doOpenParatextProject()") )
            self.setDebugText( "doOpenParatextProject..." )
        #if not self.openDialog:
        openDialog = Open( initialdir=self.lastParatextFileDir, filetypes=PARATEXT_FILETYPES )
        SSFFilepath = openDialog.show()
        if not SSFFilepath: return
        if not os.path.isfile( SSFFilepath ):
            showerror( self, APP_NAME, 'Could not open file ' + SSFFilepath )
            return
        ptxBible = PTXBible( None ) # Create a blank Paratext Bible object
        #ptxBible.loadSSFData( SSFFilepath )
        SSFDict = loadPTXSSFData( ptxBible, SSFFilepath )
        if SSFDict:
            if ptxBible.suppliedMetadata is None: ptxBible.suppliedMetadata = {}
            if 'PTX' not in ptxBible.suppliedMetadata: ptxBible.suppliedMetadata['PTX'] = {}
            ptxBible.suppliedMetadata['PTX']['SSF'] = SSFDict
            ptxBible.applySuppliedMetadata( 'SSF' ) # Copy some to ptxBible.settingsDict
        #print( "ptx/ssf" )
        #for something in ptxBible.suppliedMetadata['PTX']['SSF']:
            #print( "  ", something, repr(ptxBible.suppliedMetadata['PTX']['SSF'][something]) )
        try: ptxBibleName = ptxBible.suppliedMetadata['PTX']['SSF']['Name']
        except KeyError:
            showerror( self, APP_NAME, "Could not find 'Name' in " + SSFFilepath )
        try: ptxBibleFullName = ptxBible.suppliedMetadata['PTX']['SSF']['FullName']
        except KeyError:
            showerror( self, APP_NAME, "Could not find 'FullName' in " + SSFFilepath )
        if 'Editable' in ptxBible.suppliedMetadata and ptxBible.suppliedMetadata['Editable'] != 'T':
            showerror( self, APP_NAME, 'Project {} ({}) is not set to be editable'.format( ptxBibleName, ptxBibleFullName ) )
            return

        # Find the correct folder that contains the actual USFM files
        if 'Directory' in ptxBible.suppliedMetadata['PTX']['SSF']:
            ssfDirectory = ptxBible.suppliedMetadata['PTX']['SSF']['Directory']
        else:
            showerror( self, APP_NAME, 'Project {} ({}) has no folder specified (bad SSF file?) -- trying folder below SSF'.format( ptxBibleName, ptxBibleFullName ) )
            ssfDirectory = None
        if ssfDirectory is None or not os.path.exists( ssfDirectory ):
            if ssfDirectory is not None:
                showwarning( self, APP_NAME, 'SSF project {} ({}) folder {} not found on this system -- trying folder below SSF instead'.format( ptxBibleName, ptxBibleFullName, repr(ssfDirectory) ) )
            if not sys.platform.startswith( 'win' ): # Let's try the next folder down
                print( "doOpenParatextProject: Not windows" )
                print( 'doOpenParatextProject: ssD1', repr(ssfDirectory) )
                slash = '\\' if '\\' in ssfDirectory else '/'
                if ssfDirectory[-1] == slash: ssfDirectory = ssfDirectory[:-1] # Remove the trailing slash
                ix = ssfDirectory.rfind( slash ) # Find the last slash
                if ix!= -1:
                    ssfDirectory = os.path.join( os.path.dirname(SSFFilepath), ssfDirectory[ix+1:] + '/' )
                    print( 'doOpenParatextProject: ssD2', repr(ssfDirectory) )
                    if not os.path.exists( ssfDirectory ):
                        showerror( self, APP_NAME, 'Unable to discover Paratext {} project folder'.format( ptxBibleName ) )
                        return
        self.openParatextBibleEditWindow( SSFFilepath ) # Has to repeat some of the above unfortunately
    # end of Application.doOpenParatextProject

    def openParatextBibleEditWindow( self, SSFFilepath, editMode=None, windowGeometry=None ):
        """
        Create the actual requested local Paratext Bible project window.

        Returns the new USFMEditWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("openParatextBibleEditWindow( {} )").format( repr(SSFFilepath) ) )
            self.setDebugText( "openParatextBibleEditWindow..." )
            assert( os.path.isfile( SSFFilepath ) )

        ptxBible = PTXBible( None ) # Create a blank Paratext Bible object
        SSFDict = loadPTXSSFData( ptxBible, SSFFilepath )
        if SSFDict:
            if ptxBible.suppliedMetadata is None: ptxBible.suppliedMetadata = {}
            if 'PTX' not in ptxBible.suppliedMetadata: ptxBible.suppliedMetadata['PTX'] = {}
            ptxBible.suppliedMetadata['PTX']['SSF'] = SSFDict
            ptxBible.applySuppliedMetadata( 'SSF' ) # Copy some to BibleObject.settingsDict

        if 'Directory' in ptxBible.suppliedMetadata['PTX']['SSF']:
            ssfDirectory = ptxBible.suppliedMetadata['PTX']['SSF']['Directory']
        else:
            ssfDirectory = None
        if ssfDirectory is None or not os.path.exists( ssfDirectory ):
            if not sys.platform.startswith( 'win' ): # Let's try the next folder down
                print( "openParatextBibleEditWindow: Not windows" )
                print( 'openParatextBibleEditWindow: ssD1', repr(ssfDirectory) )
                slash = '\\' if '\\' in ssfDirectory else '/'
                if ssfDirectory[-1] == slash: ssfDirectory = ssfDirectory[:-1] # Remove the trailing slash
                ix = ssfDirectory.rfind( slash ) # Find the last slash
                if ix!= -1:
                    ssfDirectory = os.path.join( os.path.dirname(SSFFilepath), ssfDirectory[ix+1:] + '/' )
                    print( 'ssD2', repr(ssfDirectory) )
                    if not os.path.exists( ssfDirectory ):
                        showerror( self, APP_NAME, 'Unable to discover Paratext {} project folder'.format( ptxBibleName ) )
                        return
        ptxBible.sourceFolder = ptxBible.sourceFilepath = ssfDirectory
        ptxBible.preload()

        uEW = USFMEditWindow( self, ptxBible, editMode=editMode )
        if windowGeometry: uEW.geometry( windowGeometry )
        uEW.winType = 'ParatextUSFMBibleEditWindow' # override the default
        uEW.moduleID = SSFFilepath
        uEW.setFilepath( SSFFilepath )
        uEW.updateShownBCV( self.getVerseKey( uEW.groupCode ) )
        self.childWindows.append( uEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openParatextBibleEditWindow" )
        self.setReadyStatus()
        return uEW
    # end of Application.openParatextBibleEditWindow


    #def doProjectExports( self ):
    #    """
    #    Taking the
    #    """
    ## end of Application.openParatextBibleEditWindow


    def doGoBackward( self, event=None ):
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGoBackward()") )
            self.setDebugText( "doGoBackward..." )
        #print( dir(event) )
        assert( self.BCVHistory )
        assert( self.BCVHistoryIndex )
        self.BCVHistoryIndex -= 1
        assert( self.BCVHistoryIndex >= 0)
        self.setCurrentVerseKey( self.BCVHistory[self.BCVHistoryIndex] )
        self.updatePreviousNextButtons()
        #self.acceptNewBnCV()
        self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.doGoBackward


    def doGoForward( self, event=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("doGoForward") )
        #print( dir(event) )
        assert( self.BCVHistory )
        assert( self.BCVHistoryIndex < len(self.BCVHistory)-1 )
        self.BCVHistoryIndex += 1
        assert( self.BCVHistoryIndex < len(self.BCVHistory) )
        self.setCurrentVerseKey( self.BCVHistory[self.BCVHistoryIndex] )
        self.updatePreviousNextButtons()
        #self.acceptNewBnCV()
        self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.doGoForward


    def updateBCVGroup( self, newGroupLetter ):
        """
        Change the group to the given one (and then do a acceptNewBnCV)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("updateBCVGroup( {} )").format( newGroupLetter ) )
            self.setDebugText( "updateBCVGroup..." )
            assert( newGroupLetter in BIBLE_GROUP_CODES )
        self.currentVerseKeyGroup = newGroupLetter
        if   self.currentVerseKeyGroup == 'A': self.currentVerseKey = self.GroupA_VerseKey
        elif self.currentVerseKeyGroup == 'B': self.currentVerseKey = self.GroupB_VerseKey
        elif self.currentVerseKeyGroup == 'C': self.currentVerseKey = self.GroupC_VerseKey
        elif self.currentVerseKeyGroup == 'D': self.currentVerseKey = self.GroupD_VerseKey
        else: halt
        if self.currentVerseKey == ('', '1', '1'):
            self.setCurrentVerseKey( SimpleVerseKey( self.getFirstBookCode(), '1', '1' ) )
        self.updateBCVGroupButtons()
        self.acceptNewBnCV()
        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.updateBCVGroup


    def updateBCVGroupButtons( self ):
        """
        Updates the display showing the selected group and the selected BCV reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("updateBCVGroupButtons()") )
            self.setDebugText( "updateBCVGroupButtons..." )
        groupButtons = [ self.GroupAButton, self.GroupBButton, self.GroupCButton, self.GroupDButton ]
        if   self.currentVerseKeyGroup == 'A': ix = 0
        elif self.currentVerseKeyGroup == 'B': ix = 1
        elif self.currentVerseKeyGroup == 'C': ix = 2
        elif self.currentVerseKeyGroup == 'D': ix = 3
        else: halt
        selectedButton = groupButtons.pop( ix )
        selectedButton.config( state=tk.DISABLED )#, relief=tk.SUNKEN )
        for otherButton in groupButtons:
            otherButton.config( state=tk.NORMAL ) #, relief=tk.RAISED )
        self.bookNameVar.set( self.getBookName(self.currentVerseKey[0]) )
        self.chapterNumberVar.set( self.currentVerseKey[1] )
        self.verseNumberVar.set( self.currentVerseKey[2] )
    # end of Application.updateBCVGroupButtons


    def updatePreviousNextButtons( self ):
        """
        Updates the display showing the previous/next buttons as enabled or disabled.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("updatePreviousNextButtons()") )
            self.setDebugText( "updatePreviousNextButtons..." )
        self.previousBCVButton.config( state=tk.NORMAL if self.BCVHistory and self.BCVHistoryIndex>0 else tk.DISABLED )
        self.nextBCVButton.config( state=tk.NORMAL if self.BCVHistory and self.BCVHistoryIndex<len(self.BCVHistory)-1 else tk.DISABLED )
    # end of Application.updatePreviousNextButtons


    def selectGroupA( self ):
        self.updateBCVGroup( 'A' )
    # end of Application.selectGroupA
    def selectGroupB( self ):
        self.updateBCVGroup( 'B' )
    # end of Application.selectGroupB
    def selectGroupC( self ):
        self.updateBCVGroup( 'C' )
    # end of Application.selectGroupC
    def selectGroupD( self ):
        self.updateBCVGroup( 'D' )
    # end of Application.selectGroupD


    def doGotoPreviousBook( self, gotoEnd=False ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousBook( {} ) from {} {}:{}").format( gotoEnd, BBB, C, V ) )
            self.setDebugText( "doGotoPreviousBook..." )
        newBBB = self.getPreviousBookCode( BBB )
        if newBBB is None: self.gotoBCV( BBB, '0', '0' )
        else:
            self.maxChapters = self.getNumChapters( newBBB )
            self.maxVerses = self.getNumVerses( newBBB, self.maxChapters )
            if gotoEnd: self.gotoBCV( newBBB, self.maxChapters, self.maxVerses )
            else: self.gotoBCV( newBBB, '0', '0' ) # go to the beginning
    # end of Application.doGotoPreviousBook


    def doGotoNextBook( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextBook() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoNextBook..." )
        newBBB = self.getNextBookCode( BBB )
        if newBBB is None: pass # stay just where we are
        else:
            self.maxChapters = self.getNumChapters( newBBB )
            self.maxVerses = self.getNumVerses( newBBB, '0' )
            self.gotoBCV( newBBB, '0', '0' ) # go to the beginning of the book
    # end of Application.doGotoNextBook


    def doGotoPreviousChapter( self, gotoEnd=False ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousChapter() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoPreviousChapter..." )
        intC, intV = int( C ), int( V )
        if intC > 0: self.gotoBCV( BBB, intC-1, self.getNumVerses( BBB, intC-1 ) if gotoEnd else '0' )
        else: self.doGotoPreviousBook( gotoEnd=True )
    # end of Application.doGotoPreviousChapter


    def doGotoNextChapter( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextChapter() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoNextChapter..." )
        intC = int( C )
        if intC < self.maxChapters: self.gotoBCV( BBB, intC+1, '0' )
        else: self.doGotoNextBook()
    # end of Application.doGotoNextChapter


    def doGotoPreviousVerse( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousVerse() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoPreviousVerse..." )
        intC, intV = int( C ), int( V )
        if intV > 0: self.gotoBCV( BBB, C, intV-1 )
        elif intC > 0: self.doGotoPreviousChapter( gotoEnd=True )
        else: self.doGotoPreviousBook( gotoEnd=True )
    # end of Application.doGotoPreviousVerse


    def doGotoNextVerse( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextVerse() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoNextVerse..." )
        intV = int( V )
        if intV < self.maxVerses: self.gotoBCV( BBB, C, intV+1 )
        else: self.doGotoNextChapter()
    # end of Application.doGotoNextVerse


    #def doGoForward( self ):
        #"""
        #"""
        #BBB, C, V = self.currentVerseKey.getBCV()
        #if BibleOrgSysGlobals.debugFlag:
            #print( exp("doGoForward() from {} {}:{}").format( BBB, C, V ) )
            #self.setDebugText( "doGoForward..." )
        #self.notWrittenYet()
    ## end of Application.doGoForward


    #def doGoBackward( self ):
        #"""
        #"""
        #BBB, C, V = self.currentVerseKey.getBCV()
        #if BibleOrgSysGlobals.debugFlag:
            #print( exp("doGoBackward() from {} {}:{}").format( BBB, C, V ) )
            #self.setDebugText( "doGoBackward..." )
        #self.notWrittenYet()
    ## end of Application.doGoBackward


    def doGotoPreviousListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousListItem() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoPreviousListItem..." )
        self.notWrittenYet()
    # end of Application.doGotoPreviousListItem


    def doGotoNextListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextListItem() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoNextListItem..." )
        self.notWrittenYet()
    # end of Application.doGotoNextListItem


    def doGotoBook( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoBook() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoBook..." )
        self.notWrittenYet()
    # end of Application.doGotoBook


    def gotoNewBook( self, event=None ):
        """
        Handle a new book setting from the GUI dropbox.
        """
        if BibleOrgSysGlobals.debugFlag: print( exp("gotoNewBook()") )
        #print( dir(event) )

        self.chapterNumberVar.set( '1' )
        self.verseNumberVar.set( '1' )
        self.acceptNewBnCV()
    # end of Application.gotoNewBook


    def gotoNewChapter( self, event=None ):
        """
        Handle a new chapter setting from the GUI spinbox.
        """
        if BibleOrgSysGlobals.debugFlag: print( exp("gotoNewChapter()") )
        #print( dir(event) )

        #self.chapterNumberVar.set( '1' )
        self.verseNumberVar.set( '1' )
        self.acceptNewBnCV()
    # end of Application.gotoNewChapter


    def acceptNewBnCV( self, event=None ):
        """
        Handle a new book, chapter, verse setting from the GUI spinboxes.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("acceptNewBnCV()") )
        #print( dir(event) )

        bn = self.bookNameVar.get()
        C = self.chapterNumberVar.get()
        V = self.verseNumberVar.get()
        self.gotoBnCV( bn, C, V )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "acceptNewBnCV {} {}:{}".format( bn, C, V ) )
        self.setReadyStatus()
    # end of Application.acceptNewBnCV


    def haveSwordResourcesOpen( self ):
        """
        """
        #if BibleOrgSysGlobals.debugFlag: print( exp("haveSwordResourcesOpen()") )
        for appWin in self.childWindows:
            if 'Sword' in appWin.winType:
                if self.SwordInterface is None:
                    self.SwordInterface = SwordInterface() # Load the Sword library
                return True
        return False
    # end of Application.haveSwordResourcesOpen


    def gotoBnCV( self, bn, C, V ):
        """
        Converts the bookname to BBB and goes to that new reference.

        Called from GUI.
        """
        if BibleOrgSysGlobals.debugFlag: print( exp("gotoBnCV( {} {}:{} )").format( bn, C, V ) )
        #self.BnameCV = (bn,C,V,)
        #BBB = self.getBBB( bn )
        #print( "BBB", BBB )
        self.gotoBCV( self.getBBB( bn ), C, V )
    # end of Application.gotoBnCV


    def gotoBCV( self, BBB, C, V ):
        """

        """
        if BibleOrgSysGlobals.debugFlag: print( exp("gotoBCV( {} {}:{} from {} )").format( BBB, C, V, self.currentVerseKey ) )
        self.setCurrentVerseKey( SimpleVerseKey( BBB, C, V ) )
        if BibleOrgSysGlobals.debugFlag:
            assert( self.isValidBCVRef( self.currentVerseKey, 'gotoBCV '+str(self.currentVerseKey), extended=True ) )
        if self.haveSwordResourcesOpen():
            self.SwordKey = self.SwordInterface.makeKey( BBB, C, V )
            #print( "swK", self.SwordKey.getText() )
        self.childWindows.updateThisBibleGroup( self.currentVerseKeyGroup, self.currentVerseKey )
    # end of Application.gotoBCV


    def gotoGroupBCV( self, groupCode, BBB, C, V ):
        """
        Sets self.BnameCV and self.currentVerseKey (and if necessary, self.SwordKey)
            then calls update on the child windows.

        Called from child windows.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("gotoGroupBCV( {} {}:{} )").format( BBB, C, V ) )
            assert( groupCode in BIBLE_GROUP_CODES )
        newVerseKey = SimpleVerseKey( BBB, C, V )
        if groupCode == self.currentVerseKeyGroup:
            if BibleOrgSysGlobals.debugFlag: assert( newVerseKey != self.currentVerseKey )
            self.gotoBCV( BBB, C, V )
        else: # it's not the currently selected group
            if   groupCode == 'A': oldVerseKey, self.GroupA_VerseKey = self.GroupA_VerseKey, newVerseKey
            elif groupCode == 'B': oldVerseKey, self.GroupA_VerseKey = self.GroupA_VerseKey, newVerseKey
            elif groupCode == 'C': oldVerseKey, self.GroupA_VerseKey = self.GroupA_VerseKey, newVerseKey
            elif groupCode == 'D': oldVerseKey, self.GroupA_VerseKey = self.GroupA_VerseKey, newVerseKey
            else: halt
            if BibleOrgSysGlobals.debugFlag: assert( newVerseKey != oldVerseKey ) # we shouldn't have even been called
            self.childWindows.updateThisBibleGroup( groupCode, newVerseKey )
    # end of Application.gotoGroupBCV


    def setCurrentVerseKey( self, newVerseKey ):
        """
        Called to set the current verse key (and to set the verse key for the current group).

        Then it updates the main GUI spinboxes and our history.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("setCurrentVerseKey( {} )").format( newVerseKey ) )
            self.setDebugText( "setCurrentVerseKey..." )
            assert( isinstance( newVerseKey, SimpleVerseKey ) )
        self.currentVerseKey = newVerseKey
        if   self.currentVerseKeyGroup == 'A': self.GroupA_VerseKey = self.currentVerseKey
        elif self.currentVerseKeyGroup == 'B': self.GroupB_VerseKey = self.currentVerseKey
        elif self.currentVerseKeyGroup == 'C': self.GroupC_VerseKey = self.currentVerseKey
        elif self.currentVerseKeyGroup == 'D': self.GroupD_VerseKey = self.currentVerseKey
        else: halt

        BBB = self.currentVerseKey.getBBB()
        self.maxChapters = self.getNumChapters( BBB )
        self.chapterSpinbox['to'] = self.maxChapters
        self.maxVerses = self.getNumVerses( BBB, self.chapterNumberVar.get() )
        self.verseSpinbox['to'] = self.maxVerses # + 1???

        self.bookNameVar.set( self.getBookName( BBB ) )
        self.chapterNumberVar.set( self.currentVerseKey.getChapterNumber() )
        self.verseNumberVar.set( self.currentVerseKey.getVerseNumber() )

        if self.currentVerseKey not in self.BCVHistory:
            self.BCVHistoryIndex = len( self.BCVHistory )
            self.BCVHistory.append( self.currentVerseKey )
            self.updatePreviousNextButtons()
    # end of Application.setCurrentVerseKey


    def acceptNewWord( self, event=None ):
        """
        Handle a new lexicon word setting from the GUI.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("acceptNewWord()") )
        #print( dir(event) )

        newWord = self.wordVar.get()
        self.gotoWord( newWord )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "acceptNewWord {}".format( newWord ) )
        self.setReadyStatus()
    # end of Application.acceptNewWord


    def gotoWord( self, lexiconWord ):
        """
        Sets self.lexiconWord
            then calls update on the child windows.
        """
        if BibleOrgSysGlobals.debugFlag: print( exp("gotoWord( {} )").format( lexiconWord ) )
        assert( lexiconWord is None or isinstance( lexiconWord, str ) )
        self.lexiconWord = lexiconWord
        self.childWindows.updateLexicons( lexiconWord )
    # end of Application.gotoWord


    def doHideAllResources( self ):
        """
        Minimize all of our resource windows,
            i.e., leave the editor and main window
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doHideAllResources' )
        self.childWindows.iconifyAll( 'Resource' )
    # end of Application.doHideAllResources


    def doShowAllResources( self ):
        """
        Minimize all of our resource windows,
            i.e., leave the editor and main window
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doShowAllResources' )
        self.childWindows.deiconifyAll( 'Resource' )
    # end of Application.doShowAllResources


    def doHideAll( self, includeMe=True ):
        """
        Minimize all of our windows.
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doHideAll' )
        self.childWindows.iconifyAll()
        if includeMe: self.rootWindow.iconify()
    # end of Application.doHideAll


    def doShowAll( self ):
        """
        Show/restore all of our windows.
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doShowAll' )
        self.childWindows.deiconifyAll()
        self.rootWindow.deiconify() # Do this last so it has the focus
        self.rootWindow.lift()
    # end of Application.doShowAll


    def doBringAll( self ):
        """
        Bring all of our windows close.
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doBringAll' )
        x, y = parseWindowGeometry( self.rootWindow.geometry() )[2:4]
        if x > 30: x = x - 20
        if y > 30: y = y - 20
        for j, win in enumerate( self.childWindows ):
            geometrySet = parseWindowGeometry( win.geometry() )
            #print( geometrySet )
            newX = x + 10*j
            if newX < 10*j: newX = 10*j
            newY = y + 10*j
            if newY < 10*j: newY = 10*j
            geometrySet[2:4] = newX, newY
            win.geometry( assembleWindowGeometryFromList( geometrySet ) )
        self.doShowAll()
    # end of Application.doBringAll


    def onGrep( self ):
        """
        new in version 2.1: threaded external file search;
        search matched filenames in directory tree for string;
        tk.Listbox clicks open matched file at line of occurrence;

        search is threaded so the GUI remains active and is not
        blocked, and to allow multiple greps to overlap in time;
        could use threadtools, but avoid loop in no active grep;

        grep Unicode policy: text files content in the searched tree
        might be in any Unicode encoding: we don't ask about each (as
        we do for opens), but allow the encoding used for the entire
        tree to be input, preset it to the platform filesystem or
        text default, and skip files that fail to decode; in worst
        cases, users may need to run grep N times if N encodings might
        exist;  else opens may raise exceptions, and opening in binary
        mode might fail to match encoded text against search string;

        TBD: better to issue an error if any file fails to decode?
        but utf-16 2-bytes/char format created in Notepad may decode
        without error per utf-8, and search strings won't be found;
        TBD: could allow input of multiple encoding names, split on
        comma, try each one for every file, without open loadEncode?
        """
        #from tkinter import Toplevel, StringVar, X, RIDGE, tk.SUNKEN
        from tkinter.ttk import Label, Entry, Button
        def makeFormRow( parent, label, width=15, browse=True, extend=False ):
            var = tk.StringVar()
            row = Frame(parent)
            lab = Label( row, text=label + '?', relief=RIDGE, width=width)
            ent = Entry( row, textvariable=var) # relief=tk.SUNKEN
            row.pack( fill=tk.X )                                  # uses packed row frames
            lab.pack( side=tk.LEFT )                               # and fixed-width labels
            ent.pack( side=tk.LEFT, expand=tk.YES, fill=tk.X )           # or use grid(row, col)
            if browse:
                btn = Button( row, text='browse...' )
                btn.pack( side=tk.RIGHT )
                if not extend:
                    btn.config( command=lambda:
                                var.set(askopenfilename() or var.get()) )
                else:
                    btn.config( command=lambda:
                                var.set( var.get() + ' ' + askopenfilename()) )
            return var
        # end of makeFormRow

        # nonmodal dialog: get dirnname, filenamepatt, grepkey
        popup = Toplevel()
        popup.title( 'PyEdit - grep')
        var1 = makeFormRow( popup, label='Directory root',   width=18, browse=False)
        var2 = makeFormRow( popup, label='Filename pattern', width=18, browse=False)
        var3 = makeFormRow( popup, label='Search string',    width=18, browse=False)
        var4 = makeFormRow( popup, label='Content encoding', width=18, browse=False)
        var1.set( '.')      # current dir
        var2.set( '*.py')   # initial values
        var4.set( sys.getdefaultencoding() )    # for file content, not filenames
        cb = lambda: self.onDoGrep(var1.get(), var2.get(), var3.get(), var4.get())
        Button( popup, text='Go',command=cb).pack()
    # end of Application.onGrep


    def onDoGrep( self, dirname, filenamepatt, grepkey, encoding):
        """
        on Go in grep dialog: populate scrolled list with matches
        tbd: should producer thread be daemon so it dies with app?
        """
        #from tkinter import Tk
        from tkinter.ttk import Label
        import threading, queue

        # make non-modal un-closeable dialog
        mypopup = tk.Tk()
        mypopup.title( 'PyEdit - grepping')
        status = Label( mypopup, text='Grep thread searching for: %r...' % grepkey )
        status.pack(padx=20, pady=20)
        mypopup.protocol( 'WM_DELETE_WINDOW', lambda: None)  # ignore X close

        # start producer thread, consumer loop
        myqueue = queue.Queue()
        threadargs = (filenamepatt, dirname, grepkey, encoding, myqueue)
        threading.Thread(target=self.grepThreadProducer, args=threadargs).start()
        self.grepThreadConsumer(grepkey, encoding, myqueue, mypopup)
    # end of Application.onDoGrep


    def grepThreadProducer( self, filenamepatt, dirname, grepkey, encoding, myqueue):
        """
        in a non-GUI parallel thread: queue find.find results list;
        could also queue matches as found, but need to keep window;
        file content and file names may both fail to decode here;

        TBD: could pass encoded bytes to find() to avoid filename
        decoding excs in os.walk/listdir, but which encoding to use:
        sys.getfilesystemencoding() if not None?  see also Chapter6
        footnote issue: 3.1 fnmatch always converts bytes per Latin-1;
        """
        import fnmatch, os

        def find(pattern, startdir=os.curdir):
            for (thisDir, subsHere, filesHere) in os.walk(startdir):
                for name in subsHere + filesHere:
                    if fnmatch.fnmatch(name, pattern):
                        fullpath = os.path.join(thisDir, name)
                        yield fullpath
        # end of find

        matches = []
        try:
            for filepath in find(pattern=filenamepatt, startdir=dirname):
                try:
                    textfile = open(filepath, encoding=encoding)
                    for (linenum, linestr) in enumerate(textfile):
                        if grepkey in linestr:
                            msg = '%s@%d  [%s]' % (filepath, linenum + 1, linestr)
                            matches.append(msg)
                except UnicodeError as X:
                    print( 'Unicode error in:', filepath, X)       # eg: decode, bom
                except IOError as X:
                    print( 'IO error in:', filepath, X)            # eg: permission
        finally:
            myqueue.put(matches)      # stop consumer loop on find excs: filenames?
    # end of Application.grepThreadProducer


    def grepThreadConsumer( self, grepkey, encoding, myqueue, mypopup):
        """
        in the main GUI thread: watch queue for results or [];
        there may be multiple active grep threads/loops/queues;
        there may be other types of threads/checkers in process,
        especially when PyEdit is attached component (PyMailGUI);
        """
        import queue
        try:
            matches = myqueue.get(block=False)
        except queue.Empty:
            myargs  = (grepkey, encoding, myqueue, mypopup)
            self.after(250, self.grepThreadConsumer, *myargs)
        else:
            mypopup.destroy()     # close status
            self.update()         # erase it now
            if not matches:
                showinfo( self, APP_NAME, 'Grep found no matches for: %r' % grepkey)
            else:
                self.grepMatchesList(matches, grepkey, encoding)
    # end of Application.grepThreadConsumer


    def grepMatchesList( self, matches, grepkey, encoding):
        """
        populate list after successful matches;
        we already know Unicode encoding from the search: use
        it here when filename clicked, so open doesn't ask user;
        """
        #from tkinter import Tk, tk.Listbox, tk.SUNKEN, Y
        from tkinter.ttk import Scrollbar
        class ScrolledList( Frame ):
            def __init__(self, options, parent=None):
                Frame.__init__(self, parent)
                self.pack(expand=tk.YES, fill=tk.BOTH)                   # make me expandable
                self.makeWidgets(options)

            def handleList(self, event):
                index = self.tk.Listbox.curselection()                # on list double-click
                label = self.tk.Listbox.get(index)                    # fetch selection text
                self.runCommand(label)                             # and call action here
                                                                   # or get(tk.ACTIVE)
            def makeWidgets(self, options):
                sbar = Scrollbar(self)
                list = tk.Listbox(self, relief=tk.SUNKEN)
                sbar.config(command=list.yview)                    # xlink sbar and list
                list.config(yscrollcommand=sbar.set)               # move one moves other
                sbar.pack( side=tk.RIGHT, fill=tk.Y )                      # pack first=clip last
                list.pack( side=tk.LEFT, expand=tk.YES, fill=tk.BOTH )        # list clipped first
                pos = 0
                for label in options:                              # add to tk.Listbox
                    list.insert(pos, label)                        # or insert(tk.END,label)
                    pos += 1                                       # or enumerate(options)
               #list.config(selectmode=SINGLE, setgrid=1)          # select,resize modes
                list.bind('<Double-1>', self.handleList)           # set event handler
                self.tk.Listbox = list

            def runCommand(self, selection):                       # redefine me lower
                print('You selected:', selection)
        # end of class ScrolledList

        print( 'Matches for %s: %s' % (grepkey, len(matches)))

        # catch list double-click
        class ScrolledFilenames(ScrolledList):
            def runCommand( self, selection):
                file, line = selection.split( '  [', 1)[0].split( '@')
                editor = TextEditorMainPopup(
                    loadFirst=file, winTitle=' grep match', loadEncode=encoding)
                editor.onGoto(int(line))
                editor.text.focus_force()   # no, really

        # new non-modal widnow
        popup = Tk()
        popup.title( 'PyEdit - grep matches: %r (%s)' % (grepkey, encoding))
        ScrolledFilenames(parent=popup, options=matches)
    # end of Application.grepMatchesList


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("Application.doHelp()") )
        from Help import HelpBox

        helpInfo = ProgNameVersion
        helpInfo += "\n\nBasic instructions:"
        helpInfo += "\n  Use the Resource menu to open study/reference resources."
        helpInfo += "\n  Use the Project menu to open editable Bibles."
        helpInfo += "\n\nKeyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n  {}\t{}".format( name, shortcut )
        hb = HelpBox( self.rootWindow, APP_NAME, helpInfo )
    # end of Application.doHelp


    def doSubmitBug( self, event=None ):
        """
        Prompt the user to enter a bug report,
            collect other useful settings, etc.,
            and then send it all somewhere.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("Application.doSubmitBug()") )

        if not self.internetAccessEnabled: # we need to warn
            showerror( self, APP_NAME, 'You need to allow Internet access first!' )
            return

        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\n  This program is not yet finished but we'll add this eventually!"
        ab = AboutBox( self.rootWindow, APP_NAME, aboutInfo )
    # end of Application.doSubmitBug


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("Application.doAbout()") )
        from About import AboutBox

        aboutInfo = ProgNameVersion
        aboutInfo += "\n  This program is not yet finished but the Resource menu should mostly work."
        ab = AboutBox( self.rootWindow, APP_NAME, aboutInfo )
    # end of Application.doAbout


    #def doProjectClose( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( exp("doProjectClose()") )
        #self.notWrittenYet()
    ## end of Application.doProjectClose


    def writeSettingsFile( self ):
        """
        Update our program settings and save them.
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( exp("writeSettingsFile()") )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'writeSettingsFile' )
        self.settings.reset()

        self.settings.data[ProgName] = {}
        main = self.settings.data[ProgName]
        main['settingsVersion'] = SettingsVersion
        main['progVersion'] = ProgVersion
        main['themeName'] = self.themeName
        main['windowSize'], main['windowPosition'] = self.rootWindow.geometry().split( '+', 1 )
        main['minimumSize'] = self.minimumSize
        main['maximumSize'] = self.maximumSize

        # Save the Internet access controls
        self.settings.data['Internet'] = {}
        internet = self.settings.data['Internet']
        internet['internetAccess'] = 'Enabled' if self.internetAccessEnabled else 'Disabled'
        internet['checkForMessages'] = 'Enabled' if self.checkForMessagesEnabled else 'Disabled'
        internet['lastMessageNumberRead'] = str( self.lastMessageNumberRead )
        internet['sendUsageStatistics'] = 'Enabled' if self.sendUsageStatisticsEnabled else 'Disabled'
        internet['automaticUpdates'] = 'Enabled' if self.automaticUpdatesEnabled else 'Disabled'
        internet['useDevelopmentVersions'] = 'Enabled' if self.useDevelopmentVersionsEnabled else 'Disabled'
        internet['cloudBackups'] = 'Enabled' if self.cloudBackupsEnabled else 'Disabled'

        # Save the referenceGroups A..D
        self.settings.data['BCVGroups'] = {}
        groups = self.settings.data['BCVGroups']
        groups['currentGroup'] = self.currentVerseKeyGroup
        groups['A-Book'] = self.GroupA_VerseKey[0]
        groups['A-Chapter'] = self.GroupA_VerseKey[1]
        groups['A-Verse'] = self.GroupA_VerseKey[2]
        groups['B-Book'] = self.GroupB_VerseKey[0]
        groups['B-Chapter'] = self.GroupB_VerseKey[1]
        groups['B-Verse'] = self.GroupB_VerseKey[2]
        groups['C-Book'] = self.GroupC_VerseKey[0]
        groups['C-Chapter'] = self.GroupC_VerseKey[1]
        groups['C-Verse'] = self.GroupC_VerseKey[2]
        groups['D-Book'] = self.GroupD_VerseKey[0]
        groups['D-Chapter'] = self.GroupD_VerseKey[1]
        groups['D-Verse'] = self.GroupD_VerseKey[2]

        # Save the lexicon info
        self.settings.data['Lexicon'] = {}
        lexicon = self.settings.data['Lexicon']
        if self.lexiconWord: lexicon['currentWord'] = self.lexiconWord

        # Save any open Bible resource collections
        print( "save collection data..." )
        for appWin in self.childWindows:
            #print( "  gT", appWin.genericWindowType )
            #print( "  wT", appWin.winType )
            if appWin.winType == 'BibleResourceCollectionWindow':
                if appWin.resourceBoxes: # so we don't create just an empty heading for an empty collection
                    self.settings.data['BibleResourceCollection'+appWin.moduleID] = {}
                    thisOne = self.settings.data['BibleResourceCollection'+appWin.moduleID]
                    #print( "  found", appWin.moduleID )
                    for j, box in enumerate( appWin.resourceBoxes ):
                        boxNumber = 'box{}'.format( j+1 )
                        #print( "    bT", box.boxType )
                        #print( "    ID", box.moduleID )
                        thisOne[boxNumber+'Type'] = box.boxType.replace( 'BibleResourceBox', '' )
                        thisOne[boxNumber+'Source'] = box.moduleID

        # Get the current child window settings
        self.getCurrentChildWindowSettings()
        # Save all the various window set-ups including both the named ones and the current one
        for windowsSettingName in self.windowsSettingsDict:
            if BibleOrgSysGlobals.debugFlag: print( exp("Saving windows set-up {}").format( repr(windowsSettingName) ) )
            try: # Just in case something goes wrong with characters in a settings name
                self.settings.data['WindowSetting'+windowsSettingName] = {}
                thisOne = self.settings.data['WindowSetting'+windowsSettingName]
                for windowNumber,winDict in sorted( self.windowsSettingsDict[windowsSettingName].items() ):
                    #print( "  ", repr(windowNumber), repr(winDict) )
                    for windowSettingName,value in sorted( winDict.items() ):
                        thisOne[windowNumber+windowSettingName] = value
            except UnicodeEncodeError: logging.error( exp("writeSettingsFile: unable to write {} windows set-up").format( repr(windowsSettingName) ) )
        self.settings.save()
    # end of Application.writeSettingsFile


    def doCloseMe( self ):
        """
        Save files first, and then end the application.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("doCloseMe()") )
        haveModifications = False
        for appWin in self.childWindows:
            if 'Editor' in appWin.genericWindowType and appWin.modified():
                haveModifications = True; break
        if haveModifications:
            showerror( self, _("Save files"), _("You need to save or close your work first.") )
        else:
            self.writeSettingsFile()
            self.rootWindow.destroy()
    # end of Application.doCloseMe
# end of class Application



def demo():
    """
    Unattended demo program to handle command line parameters and then run what they want.

    Which windows open depends on the saved settings from the last use.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersionDate )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag:
        print( exp("Platform is"), sys.platform ) # e.g., "win32"
        print( exp("OS name is"), os.name ) # e.g., "nt"
        if sys.platform == "linux": print( exp("OS uname is"), os.uname() )
        print( exp("Running main...") )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( ProgNameVersion )

    homeFolderPath = findHomeFolderPath()
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    settings = ApplicationSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, ProgName )
    settings.load()

    application = Application( tkRootWindow, homeFolderPath, loggingFolderPath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.demo


def main( homeFolderPath, loggingFolderPath ):
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersionDate )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag:
        print( exp("Platform is"), sys.platform ) # e.g., "win32"
        print( exp("OS name is"), os.name ) # e.g., "nt"
        if sys.platform == "linux": print( exp("OS uname is"), os.uname() )
        print( exp("Running main...") )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( ProgNameVersion )
    settings = ApplicationSettings( homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, ProgName )
    settings.load()

    application = Application( tkRootWindow, homeFolderPath, loggingFolderPath, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.main


if __name__ == '__main__':
    from BibleOrgSysGlobals import setup, addStandardOptionsAndProcess, closedown

    # Configure basic set-up
    homeFolderPath = findHomeFolderPath()
    loggingFolderPath = os.path.join( homeFolderPath, DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME )
    parser = setup( ProgName, ProgVersion, loggingFolderPath=loggingFolderPath )
    addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    main( homeFolderPath, loggingFolderPath )

    closedown( ProgName, ProgVersion )
# end of Biblelator.py