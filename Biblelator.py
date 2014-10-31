#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Biblelator.py
#   Last modified: 2014-10-29 (also update ProgVersion below)
#
# Main program for Biblelator Bible display/editing
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
Program to allow editing of USFM Bibles using Python3 and Tkinter.

Note that many times in this application, where the term 'Bible' is used
    it can refer to any versified resource, e.g., typically including commentaries.
"""

ShortProgName = "Biblelator"
ProgName = "Biblelator"
ProgVersion = "0.20"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )
SettingsVersion = "0.20" # Only need to change this if the settings format has changed

debuggingThisModule = True


import sys, os.path, logging
from gettext import gettext as _
import multiprocessing

import tkinter as tk
from tkinter.messagebox import showerror, showwarning, showinfo
from tkinter.filedialog import Open, Directory #, SaveAs
#from tkinter.filedialog import FileDialog, LoadFileDialog, SaveFileDialog
#from tkinter.filedialog import askdirectory, askopenfile, askopenfilename, askopenfiles, asksaveasfile, asksaveasfilename, test
from tkinter.ttk import Style, Frame, Button, Combobox, Label, Entry
#from tkinter.tix import Spinbox

# Biblelator imports
from BiblelatorGlobals import APP_NAME, DATA_FOLDER, LOGGING_SUBFOLDER, SETTINGS_SUBFOLDER, MAX_WINDOWS, \
        MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE, BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, \
        EDIT_MODE_NORMAL, DEFAULT_KEY_BINDING_DICT, \
        findHomeFolder, parseGeometry, assembleGeometryFromList, centreWindow
from BiblelatorHelpers import errorBeep, SaveWindowNameDialog, DeleteWindowNameDialog, SelectResourceBox
from ApplicationSettings import ApplicationSettings
from ResourceWindows import ResourceWindows, ResourceWindow
from BibleResourceWindows import SwordBibleResourceWindow, InternalBibleResourceWindow, DBPBibleResourceWindow
from LexiconResourceWindows import BibleLexiconResourceWindow
from EditWindows import TextEditWindow, USFMEditWindow, ESFMEditWindow

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import BibleOrgSysGlobals
from BibleOrganizationalSystems import BibleOrganizationalSystem
from DigitalBiblePlatform import DBPBibles
from VerseReferences import SimpleVerseKey
from BibleStylesheets import BibleStylesheet
import SwordResources
from USFMBible import USFMBible


PARATEXT_FILETYPES = [('SSF files','.ssf'),('All files','*')]



def t( messageString ):
    """
    Prepends the module name to a error or warning message string
        if we are in debug mode.
    Returns the new string.
    """
    try: nameBit, errorBit = messageString.split( ': ', 1 )
    except ValueError: nameBit, errorBit = '', messageString
    if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit, _(errorBit) )



class Application( Frame ):
    """
    This is the main application window (well, actually a frame in the root toplevel window).

    Its main job is to keep track of self.currentVerseKey (and self.currentVerseKeyGroup)
        and use that to inform child windows of BCV movements.
    """
    global settings
    def __init__( self, parent, homeFolder, loggingFolder, settings ):
        if BibleOrgSysGlobals.debugFlag: print( t("Application.__init__( {} )").format( parent ) )
        self.ApplicationParent, self.homeFolder, self.loggingFolder, self.settings = parent, homeFolder, loggingFolder, settings

        self.themeName = 'default'
        self.style = Style()

        self.lastFileDir = '.'
        self.lastFind = None
        self.openDialog = None
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
        Frame.__init__( self, self.ApplicationParent )
        self.pack()

        self.ApplicationParent.protocol( "WM_DELETE_WINDOW", self.doCloseMe ) # Catch when app is closed

        self.appWins = ResourceWindows( self )

        self.createStatusBar()
        if BibleOrgSysGlobals.debugFlag: # Create a scrolling debug box
            self.lastDebugMessage = None
            from tkinter.scrolledtext import ScrolledText
            #Style().configure('DebugText.TScrolledText', padding=2, background='orange')
            self.debugTextBox = ScrolledText( self.ApplicationParent, bg='orange' )#style='DebugText.TScrolledText' )
            self.debugTextBox.pack( side=tk.BOTTOM, fill=tk.BOTH )
            #self.debugTextBox.tag_configure( 'emp', background='yellow', font='helvetica 12 bold', relief='tk.RAISED' )
            self.debugTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
            self.setDebugText( "Starting up..." )

        self.SwordInterface = None
        self.DBPInterface = None
        #print( t("Preload the Sword library...") )
        #self.SwordInterface = SwordResources.SwordInterface() # Preload the Sword library

        # Set default folders
        self.lastParatextFileDir = './'
        self.lastInternalBibleDir = './'
        if sys.platform.startswith( 'win' ):
            self.lastParatextFileDir = 'C:\\My Paratext Projects\\'
            self.lastInternalBibleDir = 'C:\\My Paratext Projects\\'
        elif sys.platform == 'linux': # temp.........................................
            self.lastParatextFileDir = '../../../../../Data/Work/VirtualBox_Shared_Folder/My Paratext Projects/'
            self.lastInternalBibleDir = '../../../../../Data/Work/Matigsalug/'

        self.keyBindingDict = DEFAULT_KEY_BINDING_DICT
        self.myKeyboardBindings = []

        # Read and apply the saved settings
        self.parseAndApplySettings()
        if ProgName not in self.settings.data or 'windowGeometry' not in self.settings.data[ProgName]:
            centreWindow( self.ApplicationParent, 600, 360 )

##        # Open some sample windows if we don't have any already
##        if not self.appWins \
##        and BibleOrgSysGlobals.debugFlag and debuggingThisModule: # Just for testing/kickstarting
##            print( t("Application.__init__ Opening sample resources...") )
##            self.openSwordBibleResourceWindow( 'KJV' )
##            self.openSwordBibleResourceWindow( 'ASV' )
##            self.openSwordBibleResourceWindow( 'WEB' )
##            p1 = '../../../../../Data/Work/Matigsalug/Bible/MBTV/'
##            p2 = 'C:\\My Paratext Projects\\MBTV\\'
##            p = p1 if os.path.exists( p1 ) else p2
##            self.openInternalBibleResourceWindow( p )
##            self.openUSFMBibleEditWindow( p, EDIT_MODE_NORMAL )
##            #self.openHebrewLexiconResourceWindow( None )
##            #self.openGreekLexiconResourceWindow( None )
##            self.openBibleLexiconResourceWindow( None )
##            self.openDBPBibleResourceWindow( 'ENGESV' )
##            self.openDBPBibleResourceWindow( 'MBTWBT' )

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
                for appWin in self.appWins:
                    if 'Bible' in appWin.genericWindowType:
                        if appWin.groupCode == groupCode:
                            appWin.updateShownBCV( groupVerseKey )
        self.updateBCVGroup( self.currentVerseKeyGroup ) # Does a acceptNewBnCV

        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "__init__ finished." )
        self.setReadyStatus()
    # end of Application.__init__


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("createMenuBar()") )

        #self.win = Toplevel( self )
        self.menubar = tk.Menu( self.ApplicationParent )
        #self.ApplicationParent['menu'] = self.menubar
        self.ApplicationParent.config( menu=self.menubar ) # alternative

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
        #subfileMenuImport = tk.Menu( fileMenu )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu )
        #subfileMenuExport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label='HTML', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Export', underline=0, menu=subfileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label='Quit app', underline=0, command=self.doCloseMe, accelerator=self.keyBindingDict['Quit'][0] ) # quit app

        #editMenu = tk.Menu( self.menubar )
        #self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        #editMenu.add_command( label='Find...', underline=0, command=self.notWrittenYet )
        #editMenu.add_command( label='Replace...', underline=0, command=self.notWrittenYet )

        gotoMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        gotoMenu.add_command( label='Previous book', underline=0, command=self.doGotoPreviousBook )
        gotoMenu.add_command( label='Next book', underline=0, command=self.doGotoNextBook )
        gotoMenu.add_command( label='Previous chapter', underline=0, command=self.doGotoPreviousChapter )
        gotoMenu.add_command( label='Next chapter', underline=0, command=self.doGotoNextChapter )
        gotoMenu.add_command( label='Previous verse', underline=0, command=self.doGotoPreviousVerse )
        gotoMenu.add_command( label='Next verse', underline=0, command=self.doGotoNextVerse )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Forward', underline=0, command=self.doGoForward )
        gotoMenu.add_command( label='Backward', underline=0, command=self.doGoBackward )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Previous list item', underline=0, command=self.doGotoPreviousListItem )
        gotoMenu.add_command( label='Next list item', underline=0, command=self.doGotoNextListItem )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Book', underline=0, command=self.doGotoBook )

        projectMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=projectMenu, label='Project', underline=0 )
        projectMenu.add_command( label='New...', underline=0, command=self.notWrittenYet )
        #submenuNewType = tk.Menu( resourcesMenu, tearoff=False )
        #projectMenu.add_cascade( label='New...', underline=5, menu=submenuNewType )
        #submenuNewType.add_command( label='Text file...', underline=0, command=self.doOpenNewTextEditWindow )
        #projectMenu.add_command( label='Open', underline=0, command=self.notWrittenYet )
        submenuProjectOpenType = tk.Menu( projectMenu, tearoff=False )
        projectMenu.add_cascade( label='Open', underline=0, menu=submenuProjectOpenType )
        submenuProjectOpenType.add_command( label='Biblelator...', underline=0, command=self.doOpenBiblelatorProject )
        submenuProjectOpenType.add_command( label='Bibledit...', underline=0, command=self.onOpenBibleditProject )
        submenuProjectOpenType.add_command( label='Paratext...', underline=0, command=self.doOpenParatextProject )
        projectMenu.add_separator()
        projectMenu.add_command( label='Backup...', underline=0, command=self.notWrittenYet )
        projectMenu.add_command( label='Restore...', underline=0, command=self.notWrittenYet )
        projectMenu.add_separator()
        projectMenu.add_command( label='Close', underline=0, command=self.doProjectClose )

        resourcesMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=resourcesMenu, label='Resources', underline=0 )
        submenuBibleResourceType = tk.Menu( resourcesMenu, tearoff=False )
        resourcesMenu.add_cascade( label='Open Bible/commentary', underline=5, menu=submenuBibleResourceType )
        submenuBibleResourceType.add_command( label='Online (DBP)...', underline=0, command=self.doOpenDBPBibleResource )
        submenuBibleResourceType.add_command( label='Sword module...', underline=0, command=self.doOpenSwordResource )
        submenuBibleResourceType.add_command( label='Other (local)...', underline=1, command=self.doOpenInternalBibleResource )
        submenuLexiconResourceType = tk.Menu( resourcesMenu, tearoff=False )
        resourcesMenu.add_cascade( label='Open lexicon', menu=submenuLexiconResourceType )
        #submenuLexiconResourceType.add_command( label='Hebrew...', underline=5, command=self.notWrittenYet )
        #submenuLexiconResourceType.add_command( label='Greek...', underline=0, command=self.notWrittenYet )
        submenuLexiconResourceType.add_command( label='Bible', underline=0, command=self.doOpenBibleLexiconResource )
        #submenuCommentaryResourceType = tk.Menu( resourcesMenu )
        #resourcesMenu.add_cascade( label='Open commentary', underline=5, menu=submenuCommentaryResourceType )
        resourcesMenu.add_command( label='Open resource collection...', underline=5, command=self.notWrittenYet )
        resourcesMenu.add_separator()
        resourcesMenu.add_command( label='Hide all resources', underline=0, command=self.doHideResources )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Search files...', underline=0, command=self.onGrep )
        toolsMenu.add_separator()
        toolsMenu.add_command( label='Checks...', underline=0, command=self.notWrittenYet )
        toolsMenu.add_separator()
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Hide resources', underline=0, command=self.doHideResources )
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
        submenuWindowStyle = tk.Menu( windowMenu )
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
            debugMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label='Help', underline=0 )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp, accelerator=self.keyBindingDict['Help'][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout, accelerator=self.keyBindingDict['About'][0] )
    # end of Application.createMenuBar


    def createNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("createNavigationBar()") )
        Style().configure('NavigationBar.TFrame', background='yellow')
        #self.label1 = Label( self, text="My label" )
        #self.label1.pack()

        navigationBar = Frame( self, cursor='hand2', relief=tk.RAISED, style='NavigationBar.TFrame' )

        self.previousBCVButton = Button( navigationBar, width=4, text='<-', command=self.goBack, state=tk.DISABLED )
        #self.previousBCVButton['text'] = '<-'
        #self.previousBCVButton['command'] = self.goBack
        #self.previousBCVButton.grid( row=0, column=0 )
        self.previousBCVButton.pack( side=tk.LEFT )

        self.nextBCVButton = Button( navigationBar, width=4, text='->', command=self.doGoForward, state=tk.DISABLED )
        #self.nextBCVButton['text'] = '->'
        #self.nextBCVButton['command'] = self.doGoForward
        #self.nextBCVButton.grid( row=0, column=1 )
        self.nextBCVButton.pack( side=tk.LEFT )

        self.GroupAButton = Button( navigationBar, width=2, text='A', command=self.selectGroupA, state=tk.DISABLED )
        self.GroupBButton = Button( navigationBar, width=2, text='B', command=self.selectGroupB, state=tk.DISABLED )
        self.GroupCButton = Button( navigationBar, width=2, text='C', command=self.selectGroupC, state=tk.DISABLED )
        self.GroupDButton = Button( navigationBar, width=2, text='D', command=self.selectGroupD, state=tk.DISABLED )
        #self.GroupAButton.grid( row=0, column=2 )
        #self.GroupBButton.grid( row=0, column=3 )
        #self.GroupCButton.grid( row=1, column=2 )
        #self.GroupDButton.grid( row=1, column=3 )
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
        #self.bookNameBox.grid( row=0, column=4 )
        self.bookNameBox.pack( side=tk.LEFT )

        self.chapterNumberVar = tk.StringVar()
        self.chapterNumberVar.set( '1' )
        self.maxChapters = self.getNumChapters( BBB )
        #print( "maxChapters", self.maxChapters )
        self.chapterSpinbox = tk.Spinbox( navigationBar, from_=0.0, to=self.maxChapters, textvariable=self.chapterNumberVar )
        self.chapterSpinbox['width'] = 3
        self.chapterSpinbox['command'] = self.acceptNewBnCV
        self.chapterSpinbox.bind( '<Return>', self.gotoNewChapter )
        #self.chapterSpinbox.grid( row=0, column=5 )
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("createToolBar()") )

        Style().configure('ToolBar.TFrame', background='green')

        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='ToolBar.TFrame' )
        Button( toolbar, text='Hide Resources', command=self.doHideResources ).pack( side=tk.LEFT, padx=2, pady=2 )
        Button( toolbar, text='Hide All', command=self.doHideAll ).pack( side=tk.LEFT, padx=2, pady=2 )
        Button( toolbar, text='Show All', command=self.doShowAll ).pack( side=tk.LEFT, padx=2, pady=2 )
        Button( toolbar, text='Bring All', command=self.doBringAll ).pack( side=tk.LEFT, padx=2, pady=2 )
        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of Application.createToolBar


    def createDebugToolBar( self ):
        """
        Create a debug tool bar containing several additional buttons at the top of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("createDebugToolBar()") )
        Style().configure( 'DebugToolBar.TFrame', background='red' )
        Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='DebugToolBar.TFrame' )
        Button( toolbar, text='Halt', style='Halt.TButton', command=self.quit ).pack( side=tk.RIGHT, padx=2, pady=2 )
        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of Application.createDebugToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("createStatusBar()") )
        Style().configure( 'StatusBar.TLabel', background='pink' )

        self.statusTextVariable = tk.StringVar()
        self.statusTextLabel = Label( self.ApplicationParent, relief=tk.SUNKEN,
                                    textvariable=self.statusTextVariable, style='StatusBar.TLabel' )
                                    #, font=('arial',16,tk.NORMAL) )
        self.statusTextLabel.pack( side=tk.BOTTOM, fill=tk.X )
        self.statusTextVariable.set( '' ) # first initial value
        self.setStatus( "Starting up..." )
    # end of Application.createStatusBar


    def createMainKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("createMainKeyboardBindings()") )
        self.myKeyboardBindings = []
        for name,command in ( ('Help',self.doHelp), ('About',self.doAbout), ('Quit',self.doCloseMe) ):
            if name in self.keyBindingDict:
                for keycode in self.keyBindingDict[name][1:]:
                    #print( "Bind {} for {}".format( repr(keycode), repr(name) ) )
                    self.ApplicationParent.bind( keycode, command )
                self.myKeyboardBindings.append( (name,self.keyBindingDict[name][0],) )
            else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
        #self.textBox.bind('<Control-a>', self.doSelectAll ); self.textBox.bind('<Control-A>', self.doSelectAll )
        #self.textBox.bind('<Control-c>', self.doCopy ); self.textBox.bind('<Control-C>', self.doCopy )
        #self.textBox.bind('<Control-f>', self.doFind ); self.textBox.bind('<Control-F>', self.doFind )
        #self.textBox.bind('<Control-g>', self.doRefind ); self.textBox.bind('<Control-G>', self.doRefind )
        #self.textBox.bind('<F1>', self.doHelp )
        #self.textBox.bind('<F3>', self.doRefind )
        #self.textBox.bind('<Control-F4>', self.doClose )
        #self.textBox.bind('<F11>', self.doShowInfo )
        #self.textBox.bind('<F12>', self.doAbout )
    # end of ResourceWindow.createMainKeyboardBindings()


    def notWrittenYet( self ):
        errorBeep()
        showerror( _("Not implemented"), _("Not yet available, sorry") )
    # end of Application.notWrittenYet


    def getVerseKey( self, groupCode ):
        assert( groupCode in BIBLE_GROUP_CODES )
        if   groupCode == 'A': return self.GroupA_VerseKey
        elif groupCode == 'B': return self.GroupB_VerseKey
        elif groupCode == 'C': return self.GroupC_VerseKey
        elif groupCode == 'D': return self.GroupD_VerseKey
        else: halt
    # end of Application.getVerseKey


    def setStatus( self, newStatus=None ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("setStatus( {} )").format( repr(newStatus) ) )
        #print( "SB is", repr( self.statusTextVariable.get() ) )
        if newStatus != self.statusTextVariable.get(): # it's changed
            #self.statusBarTextWidget['state'] = tk.NORMAL
            #self.statusBarTextWidget.delete( '1.0', tk.END )
            #if newStatus:
                #self.statusBarTextWidget.insert( '1.0', newStatus )
            #self.statusBarTextWidget['state'] = tk.DISABLED # Don't allow editing
            #self.statusText = newStatus
            self.statusTextVariable.set( newStatus )
            self.statusTextLabel.update()
    # end of Application.setStatus

    def setReadyStatus( self ):
        self.setStatus( _("Ready") )


    def setDebugText( self, newMessage=None ):
        """
        """
        print( t("setDebugText( {} )").format( repr(newMessage) ) )
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
        self.debugTextBox.insert( tk.END, '\n\n{} child windows:'.format( len(self.appWins) ) )
        for j, appWin in enumerate( self.appWins ):
            self.debugTextBox.insert( tk.END, "\n  {} {} ({}) {} {}" \
                                    .format( j, appWin.winType.replace('ResourceWindow',''),
                                        appWin.genericWindowType.replace('Resource',''),
                                        appWin.geometry(), appWin.moduleID ) )
        #self.debugTextBox.insert( tk.END, '\n{} resource frames:'.format( len(self.appWins) ) )
        #for j, projFrame in enumerate( self.appWins ):
            #self.debugTextBox.insert( tk.END, "\n  {} {}".format( j, projFrame ) )
        self.debugTextBox['state'] = tk.DISABLED # Don't allow editing
    # end of Application.setDebugText


    def doChangeTheme( self, newThemeName ):
        """
        Set the window theme to the given scheme.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doChangeTheme( {} )").format( repr(newThemeName) ) )
            assert( newThemeName )
            self.setDebugText( 'Set theme to {}'.format( repr(newThemeName) ) )
        self.themeName = newThemeName
        try:
            self.style.theme_use( newThemeName )
        except tk.TclError as err:
            showerror( 'Error', err )
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
                print( t("retrieveWindowsSettings( {} )").format( repr(windowsSettingsName) ) )
                self.setDebugText( "retrieveWindowsSettings..." )
            windowsSettingsFields = self.settings.data['WindowSetting'+windowsSettingsName]
            resultDict = {}
            for j in range( 1, MAX_WINDOWS ):
                winNumber = "window{}".format( j )
                for keyName in windowsSettingsFields:
                    if keyName.startswith( winNumber ):
                        if winNumber not in resultDict: resultDict[winNumber] = {}
                        resultDict[winNumber][keyName[len(winNumber):]] = windowsSettingsFields[keyName]
            #print( t("retrieveWindowsSettings"), resultDict )
            return resultDict
        # end of retrieveWindowsSettings


        if BibleOrgSysGlobals.debugFlag:
            print( t("parseAndApplySettings()") )
            self.setDebugText( "parseAndApplySettings..." )
        try: self.minimumXSize, self.minimumYSize = self.settings.data[ProgName]['minimumXSize'], self.settings.data[ProgName]['minimumYSize']
        except KeyError: self.minimumXSize, self.minimumYSize = MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE
        self.ApplicationParent.minsize( self.minimumXSize, self.minimumYSize )
        try: self.ApplicationParent.geometry( self.settings.data[ProgName]['windowGeometry'] )
        except KeyError: print( "KeyError1" ) # we had no geometry set
        except tk.TclError: logging.critical( t("Application.__init__: Bad window geometry in settings file: {}").format( settings.data[ProgName]['windowGeometry'] ) )
        try: self.doChangeTheme( self.settings.data[ProgName]['themeName'] )
        except KeyError: print( "KeyError2" ) # we had no theme name set

        try: self.currentVerseKeyGroup = self.settings.data['BCVGroups']['currentGroup']
        except KeyError: self.currentVerseKeyGroup = 'A'
        try: self.GroupA_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['A-Book'],self.settings.data['BCVGroups']['A-Chapter'],self.settings.data['BCVGroups']['A-Verse'])
        except KeyError: self.GroupA_VerseKey = SimpleVerseKey( self.getFirstBookCode(), '1', '1' )
        try: self.GroupB_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['B-Book'],self.settings.data['BCVGroups']['B-Chapter'],self.settings.data['BCVGroups']['B-Verse'])
        except KeyError: self.GroupB_VerseKey = SimpleVerseKey( self.getFirstBookCode(), '1', '1' )
        try: self.GroupC_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['C-Book'],self.settings.data['BCVGroups']['C-Chapter'],self.settings.data['BCVGroups']['C-Verse'])
        except KeyError: self.GroupC_VerseKey = SimpleVerseKey( self.getFirstBookCode(), '1', '1' )
        try: self.GroupD_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['D-Book'],self.settings.data['BCVGroups']['D-Chapter'],self.settings.data['BCVGroups']['D-Verse'])
        except KeyError: self.GroupD_VerseKey = SimpleVerseKey( self.getFirstBookCode(), '1', '1' )

        try: self.lexiconWord = self.settings.data['Lexicon']['currentWord']
        except KeyError: self.lexiconWord = None

        # We keep our copy of all the windows settings in self.windowsSettingsDict
        windowsSettingsNamesList = []
        for name in self.settings.data:
            if name.startswith( 'WindowSetting' ): windowsSettingsNamesList.append( name[13:] )
        if BibleOrgSysGlobals.debugFlag: print( t("Available windows settings are: {}").format( windowsSettingsNamesList ) )
        if windowsSettingsNamesList: assert( 'Current' in windowsSettingsNamesList )
        self.windowsSettingsDict = {}
        for windowsSettingsName in windowsSettingsNamesList:
            self.windowsSettingsDict[windowsSettingsName] = retrieveWindowsSettings( self, windowsSettingsName )
        if 'Current' in windowsSettingsNamesList: self.applyGivenWindowsSettings( 'Current' )
        else: logging.critical( t("Application.parseAndApplySettings: No current window settings available") )
    # end of Application.parseAndApplySettings


    def applyGivenWindowsSettings( self, givenWindowsSettingsName ):
        """
        Given the name of windows settings,
            find the settings in our dictionary
            and then apply it by creating the windows.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("applyGivenWindowsSettings( {} )").format( repr(givenWindowsSettingsName) ) )
            self.setDebugText( "applyGivenWindowsSettings..." )
        windowsSettingsFields = self.windowsSettingsDict[givenWindowsSettingsName]
        for j in range( 1, MAX_WINDOWS ):
            winNumber = "window{}".format( j )
            if winNumber in windowsSettingsFields:
                thisStuff = windowsSettingsFields[winNumber]
                winType = thisStuff['Type']
                windowGeometry = thisStuff['Geometry'] if 'Geometry' in thisStuff else None
                #print( winType, windowGeometry )
                if winType == 'SwordBibleResourceWindow':
                    rw = self.openSwordBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                    #except: logging.error( "Unable to read SwordBibleResourceWindow {} settings".format( j ) )
                elif winType == 'DBPBibleResourceWindow':
                    rw = self.openDBPBibleResourceWindow( thisStuff['ModuleAbbreviation'], windowGeometry )
                    #except: logging.error( "Unable to read DBPBibleResourceWindow {} settings".format( j ) )
                elif winType == 'InternalBibleResourceWindow':
                    rw = self.openInternalBibleResourceWindow( thisStuff['BibleFolderPath'], windowGeometry )
                    #except: logging.error( "Unable to read InternalBibleResourceWindow {} settings".format( j ) )

                #elif winType == 'HebrewLexiconResourceWindow':
                    #self.openHebrewLexiconResourceWindow( thisStuff['HebrewLexiconPath'], windowGeometry )
                    ##except: logging.error( "Unable to read HebrewLexiconResourceWindow {} settings".format( j ) )
                #elif winType == 'GreekLexiconResourceWindow':
                    #self.openGreekLexiconResourceWindow( thisStuff['GreekLexiconPath'], windowGeometry )
                    ##except: logging.error( "Unable to read GreekLexiconResourceWindow {} settings".format( j ) )
                elif winType == 'BibleLexiconResourceWindow':
                    rw = self.openBibleLexiconResourceWindow( thisStuff['BibleLexiconPath'], windowGeometry )
                    #except: logging.error( "Unable to read BibleLexiconResourceWindow {} settings".format( j ) )

                elif winType == 'PlainTextEditWindow':
                    rw = self.doOpenNewTextEditWindow()
                    #except: logging.error( "Unable to read TextEditWindow {} settings".format( j ) )
                elif winType == 'USFMBibleEditWindow':
                    rw = self.openUSFMBibleEditWindow( thisStuff['USFMFolder'], thisStuff['EditMode'], windowGeometry )
                    #except: logging.error( "Unable to read USFMBibleEditWindow {} settings".format( j ) )
                elif winType == 'ESFMEditWindow':
                    rw = self.openESFMEditWindow( thisStuff['ESFMFolder'], thisStuff['EditMode'], windowGeometry )
                    #except: logging.error( "Unable to read ESFMEditWindow {} settings".format( j ) )

                else:
                    logging.critical( t("Application.__init__: Unknown {} window type").format( repr(winType) ) )
                    if BibleOrgSysGlobals.debugFlag: halt

                groupCode = thisStuff['GroupCode'] if 'GroupCode' in thisStuff else None
                if groupCode:
                    if BibleOrgSysGlobals.debugFlag: assert( groupCode in BIBLE_GROUP_CODES )
                    rw.groupCode = groupCode
                contextViewMode = thisStuff['ContextViewMode'] if 'ContextViewMode' in thisStuff else None
                if contextViewMode:
                    if BibleOrgSysGlobals.debugFlag: assert( contextViewMode in BIBLE_CONTEXT_VIEW_MODES )
                    rw.contextViewMode = contextViewMode
                    rw.createMenuBar()
    # end of Application.applyGivenWindowsSettings


    def getCurrentWindowSettings( self ):
        """
        Go through the currently open windows and get their settings data
            and save it in self.windowsSettingsDict['Current'].
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("getCurrentWindowSettings()") )
        if 'Current' in self.windowsSettingsDict: del self.windowsSettingsDict['Current']
        self.windowsSettingsDict['Current'] = {}
        for j, appWin in enumerate( self.appWins ):
                winNumber = "window{}".format( j+1 )
                self.windowsSettingsDict['Current'][winNumber] = {}
                thisOne = self.windowsSettingsDict['Current'][winNumber]
                thisOne['Type'] = appWin.winType #.replace( 'Window', 'Window' )
                thisOne['Geometry'] = appWin.geometry()
                if appWin.winType == 'SwordBibleResourceWindow':
                    thisOne['ModuleAbbreviation'] = appWin.moduleAbbreviation
                elif appWin.winType == 'DBPBibleResourceWindow':
                    thisOne['ModuleAbbreviation'] = appWin.moduleAbbreviation
                elif appWin.winType == 'InternalBibleResourceWindow':
                    thisOne['BibleFolderPath'] = appWin.modulePath

                #elif appWin.winType == 'HebrewLexiconResourceWindow':
                    #thisOne['HebrewLexiconPath'] = appWin.lexiconPath
                #elif appWin.winType == 'GreekLexiconResourceWindow':
                    #thisOne['HebrewLexiconPath'] = appWin.lexiconPath
                elif appWin.winType == 'BibleLexiconResourceWindow':
                    thisOne['BibleLexiconPath'] = appWin.lexiconPath

                elif appWin.winType == 'PlainTextEditWindow':
                    pass # ???
                elif appWin.winType == 'USFMBibleEditWindow':
                    thisOne['USFMFolder'] = appWin.USFMFolder
                    thisOne['EditMode'] = appWin.editMode

                else:
                    logging.critical( t("getCurrentWindowSettings: Unknown {} window type").format( repr(appWin.winType) ) )
                    if BibleOrgSysGlobals.debugFlag: halt

                if 'Bible' in appWin.genericWindowType:
                    try: thisOne['GroupCode'] = appWin.groupCode
                    except AttributeError: logging.critical( t("getCurrentWindowSettings: Why no groupCode in {}").format( appWin.winType ) )
                    try: thisOne['ContextViewMode'] = appWin.contextViewMode
                    except AttributeError: logging.critical( t("getCurrentWindowSettings: Why no contextViewMode in {}").format( appWin.winType ) )
    # end of Application.getCurrentWindowSettings


    def doSaveNewWindowSetup( self ):
        """
        Gets the name for the new window setup and saves the information.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doSaveNewWindowSetup()") )
            self.setDebugText( "doSaveNewWindowSetup..." )
        swnd = SaveWindowNameDialog( self, self.windowsSettingsDict, title=_("Save window setup") )
        print( "swndResult", repr(swnd.result) )
        if swnd.result:
            self.getCurrentWindowSettings()
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
            print( t("doDeleteExistingWindowSetup()") )
            self.setDebugText( "doDeleteExistingWindowSetup..." )
        assert( self.windowsSettingsDict and (len(self.windowsSettingsDict)>1 or 'Current' not in self.windowsSettingsDict) )
        dwnd = DeleteWindowNameDialog( self, self.windowsSettingsDict, title=_("Delete saved window setup") )
        print( "dwndResult", repr(dwnd.result) )
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
            print( t("doOpenDBPBibleResource()") )
            self.setDebugText( "doOpenDBPBibleResource..." )
        self.setStatus( "doOpenDBPBibleResource..." )
        if self.DBPInterface is None:
            self.DBPInterface = DBPBibles()
            availableVolumes = self.DBPInterface.fetchAllEnglishTextVolumes()
            #print( "aV1", repr(availableVolumes) )
            if availableVolumes:
                srb = SelectResourceBox( self, [(x,y) for x,y in availableVolumes.items()], title=_("Open DPB resource") )
                #print( "srbResult", repr(srb.result) )
                if srb.result:
                    for entry in srb.result:
                        self.openDBPBibleResourceWindow( entry[1] )
                    #self.acceptNewBnCV()
                    #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
                elif BibleOrgSysGlobals.debugFlag: print( t("doOpenDBPBibleResource: no resource selected!") )
            else:
                logging.critical( t("doOpenDBPBibleResource: no volumes available") )
                self.setStatus( "Digital Bible Platform unavailable (offline?)" )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doOpenDBPBibleResource" )
    # end of Application.doOpenDBPBibleResource

    def openDBPBibleResourceWindow( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested DBP Bible resource window.

        Returns the new DBPBibleResourceWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openDBPBibleResourceWindow()") )
            self.setDebugText( "openDBPBibleResourceWindow..." )
            assert( moduleAbbreviation and isinstance( moduleAbbreviation, str ) and len(moduleAbbreviation)==6 )
        dBRW = DBPBibleResourceWindow( self, moduleAbbreviation )
        if windowGeometry: dBRW.geometry( windowGeometry )
        self.appWins.append( dBRW )
        if dBRW.DBPModule is None:
            logging.critical( t("Application.openDBPBibleResourceWindow: Unable to open resource {}").format( repr(moduleAbbreviation) ) )
            #dBRW.destroy()
        else: dBRW.updateShownBCV( self.getVerseKey( dBRW.groupCode ) )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openDPBBibleResourceWindow" )
        self.setReadyStatus()
        return dBRW
    # end of Application.openDBPBibleResourceWindow


    def doOpenSwordResource( self ):
        """
        Open a local Sword Bible (called from a menu/GUI action).

        Requests a module abbreviation from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openSwordResource()") )
            self.setDebugText( "doOpenSwordResource..." )
        self.setStatus( "doOpenSwordResource..." )
        if self.SwordInterface is None:
            self.SwordInterface = SwordResources.SwordInterface() # Load the Sword library
        availableModules = self.SwordInterface.library
        #print( "aM1", availableModules )
        ourList = None
        if availableModules is not None:
            ourList = availableModules.getAvailableModuleCodes()
        #print( "ourList", ourList )
        if ourList:
            srb = SelectResourceBox( self, ourList, title=_("Open Sword resource") )
            #print( "srbResult", repr(srb.result) )
            if srb.result:
                for entry in srb.result:
                    self.setStatus( _("Loading {} Sword module...").format( repr(entry) ) )
                    self.openSwordBibleResourceWindow( entry )
                #self.acceptNewBnCV()
                #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
            elif BibleOrgSysGlobals.debugFlag: print( t("doOpenSwordResource: no resource selected!") )
        else:
            logging.critical( t("doOpenSwordResource: no list available") )
            showerror( APP_NAME, _("No Sword resources discovered") )
        #self.acceptNewBnCV()
        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.doOpenSwordResource

    def openSwordBibleResourceWindow( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested Sword Bible resource window.

        Returns the new SwordBibleResourceWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openSwordBibleResourceWindow()") )
            self.setDebugText( "openSwordBibleResourceWindow..." )
        if self.SwordInterface is None:
            self.SwordInterface = SwordResources.SwordInterface() # Load the Sword library
        swBRW = SwordBibleResourceWindow( self, moduleAbbreviation )
        if windowGeometry: swBRW.geometry( windowGeometry )
        self.appWins.append( swBRW )
        swBRW.updateShownBCV( self.getVerseKey( swBRW.groupCode ) )
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
            print( t("openInternalBibleResource()") )
            self.setDebugText( "doOpenInternalBibleResource..." )
        self.setStatus( "doOpenInternalBibleResource..." )
        #requestedFolder = askdirectory()
        self.openDialog = Directory( initialdir=self.lastInternalBibleDir )
        requestedFolder = self.openDialog.show()
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
            print( t("openInternalBibleResourceWindow()") )
            self.setDebugText( "openInternalBibleResourceWindow..." )
        iBRW = InternalBibleResourceWindow( self, modulePath )
        if windowGeometry: iBRW.geometry( windowGeometry )
        self.appWins.append( iBRW )
        if iBRW.internalBible is None:
            logging.critical( t("Application.openInternalBibleResourceWindow: Unable to open resource {}").format( repr(modulePath) ) )
            iBRW.destroy()
        else: iBRW.updateShownBCV( self.getVerseKey( iBRW.groupCode ) )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openInternalBibleResourceWindow" )
        self.setReadyStatus()
        return iBRW
    # end of Application.openInternalBibleResourceWindow


    def doOpenBibleLexiconResource( self ):
        """
        Open a local Bible (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doOpenBibleLexiconResource()") )
            self.setDebugText( "doOpenBibleLexiconResource..." )
        self.setStatus( "doOpenBibleLexiconResource..." )
        #requestedFolder = askdirectory()
        #if requestedFolder:
        requestedFolder = None
        self.openBibleLexiconResourceWindow( requestedFolder )
        #self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.doOpenBibleLexiconResource

    def openBibleLexiconResourceWindow( self, lexiconPath, windowGeometry=None ):
        """

        Returns the new BibleLexiconResourceWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openBibleLexiconResourceWindow()") )
            self.setDebugText( "openBibleLexiconResourceWindow..." )
        if lexiconPath is None: lexiconPath = "../"
        bLRW = BibleLexiconResourceWindow( self, lexiconPath )
        if windowGeometry: bLRW.geometry( windowGeometry )
        self.appWins.append( bLRW )
        if bLRW.BibleLexicon is None:
            logging.critical( t("Application.openBibleLexiconResourceWindow: Unable to open Bible lexicon resource {}").format( repr(lexiconPath) ) )
            #bLRW.destroy()
        elif self.lexiconWord:
            bLRW.updateLexiconWord( self.lexiconWord )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openBibleLexiconResourceWindow" )
        self.setReadyStatus()
        return bLRW
    # end of Application.openBibleLexiconResourceWindow


    def doOpenNewTextEditWindow( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doOpenNewTextEditWindow()") )
            self.setDebugText( "doOpenNewTextEditWindow..." )
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        self.appWins.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doOpenNewTextEditWindow" )
        self.setReadyStatus()
    # end of Application.doOpenNewTextEditWindow


    def doOpenFileTextEditWindow( self ):
        """
        Open a pop-up window and request the user to select a file.

        Then open the file in a plain text edit window.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doOpenFileTextEditWindow()") )
            self.setDebugText( "doOpenFileTextEditWindow..." )
        if not self.openDialog:
            fTypes = [('All files',  '*'),
                      ('Text files', '.txt')]
            self.openDialog = Open( initialdir=self.lastFileDir, filetypes=fTypes )
        fileResult = self.openDialog.show()
        if not fileResult: return
        if not os.path.isfile( fileResult ):
            showerror( APP_NAME, 'Could not open file ' + fileResult )
            return
        text = open( fileResult, 'rt', encoding='utf-8' ).read()
        if text == None:
            showerror( APP_NAME, 'Could not decode and open file ' + fileResult )
        else:
            tEW = TextEditWindow( self )
            tEW.setFilepath( fileResult )
            tEW.setAllText( text )
            #if windowGeometry: tEW.geometry( windowGeometry )
            self.appWins.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doOpenFileTextEditWindow" )
        self.setReadyStatus()
    # end of Application.doOpenFileTextEditWindow


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doViewSettings()") )
            self.setDebugText( "doViewSettings..." )
        fileResult = self.settings.settingsFilepath
        if not fileResult: return
        if not os.path.isfile( fileResult ):
            showerror( APP_NAME, 'Could not open file ' + fileResult )
            return
        text = open( fileResult, 'rt', encoding='utf-8' ).read()
        if text == None:
            showerror( APP_NAME, 'Could not decode and open file ' + fileResult )
        else:
            tEW = TextEditWindow( self )
            tEW.setFilepath( fileResult )
            tEW.setAllText( text )
            #if windowGeometry: tEW.geometry( windowGeometry )
            self.appWins.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewSettings" )
        self.setReadyStatus()
    # end of Application.doViewSettings


    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("doViewLog()") )
            self.setDebugText( "doViewLog..." )
        filename = ProgName.replace('/','-').replace(':','_').replace('\\','_') + '_log.txt'
        fileResult = os.path.join( self.loggingFolder, filename )
        if not fileResult: return
        if not os.path.isfile( fileResult ):
            showerror( APP_NAME, 'Could not open file ' + fileResult )
            return
        text = open( fileResult, 'rt', encoding='utf-8' ).read()
        if text == None:
            showerror( APP_NAME, 'Could not decode and open file ' + fileResult )
        else:
            tEW = TextEditWindow( self )
            tEW.setFilepath( fileResult )
            tEW.setAllText( text )
            #if windowGeometry: tEW.geometry( windowGeometry )
            self.appWins.append( tEW )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewLog" )
        self.setReadyStatus()
    # end of Application.doViewLog


    def openUSFMBibleEditWindow( self, USFMFolder, editMode, windowGeometry=None ):
        """

        Returns the new USFMEditWindow object.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("openUSFMBibleEditWindow()") )
            self.setDebugText( "openUSFMBibleEditWindow..." )
        uEW = USFMEditWindow( self, USFMFolder, editMode )
        if windowGeometry: uEW.geometry( windowGeometry )
        self.appWins.append( uEW )
        if uEW.InternalBible is None:
            logging.critical( t("Application.openUSFMBibleEditWindow: Unable to open USFM Bible in {}").format( repr(USFMFolder) ) )
            #uEW.destroy()
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished openUSFMBibleEditWindow" )
        self.setReadyStatus()
        return uEW
    # end of Application.openUSFMBibleEditWindow


    def goBack( self, event=None ):
        if BibleOrgSysGlobals.debugFlag:
            print( t("goBack()") )
            self.setDebugText( "goBack..." )
        #print( dir(event) )
        assert( self.BCVHistory )
        assert( self.BCVHistoryIndex )
        self.BCVHistoryIndex -= 1
        assert( self.BCVHistoryIndex >= 0)
        self.setCurrentVerseKey( self.BCVHistory[self.BCVHistoryIndex] )
        self.updatePreviousNextButtons()
        #self.acceptNewBnCV()
        self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.goBack


    def doGoForward( self, event=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("doGoForward") )
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
            print( t("updateBCVGroup( {} )").format( newGroupLetter ) )
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
        #self.acceptNewBnCV()
        self.after_idle( self.acceptNewBnCV ) # Do the acceptNewBnCV once we're idle
    # end of Application.updateBCVGroup


    def updateBCVGroupButtons( self ):
        """
        Updates the display showing the selected group and the selected BCV reference.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("updateBCVGroupButtons()") )
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
            print( t("updatePreviousNextButtons()") )
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
            print( t("doGotoPreviousBook( {} ) from {} {}:{}").format( gotoEnd, BBB, C, V ) )
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
            print( t("doGotoNextBook() from {} {}:{}").format( BBB, C, V ) )
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
            print( t("doGotoPreviousChapter() from {} {}:{}").format( BBB, C, V ) )
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
            print( t("doGotoNextChapter() from {} {}:{}").format( BBB, C, V ) )
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
            print( t("doGotoPreviousVerse() from {} {}:{}").format( BBB, C, V ) )
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
            print( t("doGotoNextVerse() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoNextVerse..." )
        intV = int( V )
        if intV < self.maxVerses: self.gotoBCV( BBB, C, intV+1 )
        else: self.doGotoNextChapter()
    # end of Application.doGotoNextVerse


    def doGoForward( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGoForward() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGoForward..." )
        self.notWrittenYet()
    # end of Application.doGoForward


    def doGoBackward( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGoBackward() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGoBackward..." )
        self.notWrittenYet()
    # end of Application.doGoBackward


    def doGotoPreviousListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoPreviousListItem() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoPreviousListItem..." )
        self.notWrittenYet()
    # end of Application.doGotoPreviousListItem


    def doGotoNextListItem( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoNextListItem() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoNextListItem..." )
        self.notWrittenYet()
    # end of Application.doGotoNextListItem


    def doGotoBook( self ):
        """
        """
        BBB, C, V = self.currentVerseKey.getBCV()
        if BibleOrgSysGlobals.debugFlag:
            print( t("doGotoBook() from {} {}:{}").format( BBB, C, V ) )
            self.setDebugText( "doGotoBook..." )
        self.notWrittenYet()
    # end of Application.doGotoBook


    def gotoNewBook( self, event=None ):
        """
        Handle a new book setting from the GUI dropbox.
        """
        if BibleOrgSysGlobals.debugFlag: print( t("gotoNewBook()") )
        #print( dir(event) )

        self.chapterNumberVar.set( '1' )
        self.verseNumberVar.set( '1' )
        self.acceptNewBnCV()
    # end of Application.gotoNewBook


    def gotoNewChapter( self, event=None ):
        """
        Handle a new chapter setting from the GUI spinbox.
        """
        if BibleOrgSysGlobals.debugFlag: print( t("gotoNewChapter()") )
        #print( dir(event) )

        #self.chapterNumberVar.set( '1' )
        self.verseNumberVar.set( '1' )
        self.acceptNewBnCV()
    # end of Application.gotoNewChapter


    def acceptNewBnCV( self, event=None ):
        """
        Handle a new book, chapter, verse setting from the GUI spinboxes.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("acceptNewBnCV()") )
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
        #if BibleOrgSysGlobals.debugFlag: print( t("haveSwordResourcesOpen()") )
        for appWin in self.appWins:
            if 'Sword' in appWin.winType:
                if self.SwordInterface is None:
                    self.SwordInterface = SwordResources.SwordInterface() # Load the Sword library
                return True
        return False
    # end of Application.haveSwordResourcesOpen


    def gotoBnCV( self, bn, C, V ):
        """
        Converts the bookname to BBB and goes to that new reference.

        Called from GUI.
        """
        if BibleOrgSysGlobals.debugFlag: print( t("gotoBnCV( {} {}:{} )").format( bn, C, V ) )
        #self.BnameCV = (bn,C,V,)
        #BBB = self.getBBB( bn )
        #print( "BBB", BBB )
        self.gotoBCV( self.getBBB( bn ), C, V )
    # end of Application.gotoBnCV


    def gotoBCV( self, BBB, C, V ):
        """

        """
        if BibleOrgSysGlobals.debugFlag: print( t("gotoBCV( {} {}:{} from {} )").format( BBB, C, V, self.currentVerseKey ) )
        self.setCurrentVerseKey( SimpleVerseKey( BBB, C, V ) )
        if BibleOrgSysGlobals.debugFlag:
            assert( self.isValidBCVRef( self.currentVerseKey, 'gotoBCV '+str(self.currentVerseKey), extended=True ) )
        if self.haveSwordResourcesOpen():
            self.SwordKey = self.SwordInterface.makeKey( BBB, C, V )
            #print( "swK", self.SwordKey.getText() )
        self.appWins.updateThisBibleGroup( self.currentVerseKeyGroup, self.currentVerseKey )
    # end of Application.gotoBCV


    def gotoGroupBCV( self, groupCode, BBB, C, V ):
        """
        Sets self.BnameCV and self.currentVerseKey (and if necessary, self.SwordKey)
            then calls update on the child windows.

        Called from child windows.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("gotoGroupBCV( {} {}:{} )").format( BBB, C, V ) )
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
            self.appWins.updateThisBibleGroup( groupCode, newVerseKey )
    # end of Application.gotoGroupBCV


    def setCurrentVerseKey( self, newVerseKey ):
        """
        Called to set the current verse key (and to set the verse key for the current group).

        Then it updates the main GUI spinboxes and our history.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("setCurrentVerseKey( {} )").format( newVerseKey ) )
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
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("acceptNewWord()") )
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
        if BibleOrgSysGlobals.debugFlag: print( t("gotoWord( {} )").format( lexiconWord ) )
        assert( lexiconWord is None or isinstance( lexiconWord, str ) )
        self.lexiconWord = lexiconWord
        self.appWins.updateLexicons( lexiconWord )
    # end of Application.gotoWord


    def doHideResources( self ):
        """
        Minimize all of our resource windows,
            i.e., leave the editor and main window
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doHideResources' )
        self.appWins.iconifyResources()
    # end of Application.doHideResources


    def doHideAll( self, includeMe=True ):
        """
        Minimize all of our windows.
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doHideAll' )
        self.appWins.iconify()
        if includeMe: self.ApplicationParent.iconify()
    # end of Application.doHideAll


    def doShowAll( self ):
        """
        Show/restore all of our windows.
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doShowAll' )
        self.appWins.deiconify()
        self.ApplicationParent.deiconify() # Do this last so it has the focus
        self.ApplicationParent.lift()
    # end of Application.doShowAll


    def doBringAll( self ):
        """
        Bring all of our windows close.
        """
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'doBringAll' )
        x, y = parseGeometry( self.ApplicationParent.geometry() )[2:4]
        if x > 30: x = x - 20
        if y > 30: y = y - 20
        for j, win in enumerate( self.appWins ):
            geometrySet = parseGeometry( win.geometry() )
            #print( geometrySet )
            newX = x + 10*j
            if newX < 10*j: newX = 10*j
            newY = y + 10*j
            if newY < 10*j: newY = 10*j
            geometrySet[2:4] = newX, newY
            win.geometry( assembleGeometryFromList( geometrySet ) )
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
                showinfo( APP_NAME, 'Grep found no matches for: %r' % grepkey)
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


    def doOpenBiblelatorProject( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( t("doOpenBiblelatorProject()") )
        self.notWrittenYet()
    # end of Application.doOpenBiblelatorProject


    def onOpenBibleditProject( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( t("onOpenBibleditProject()") )
        self.notWrittenYet()
    # end of Application.onOpenBibleditProject


    def doOpenParatextProject( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
            print( t("doOpenParatextProject()") )
            self.setDebugText( "doOpenParatextProject..." )
        #if not self.openDialog:
        self.openDialog = Open( initialdir=self.lastParatextFileDir, filetypes=PARATEXT_FILETYPES )
        fileResult = self.openDialog.show()
        if not fileResult: return
        if not os.path.isfile( fileResult ):
            showerror( APP_NAME, 'Could not open file ' + fileResult )
            return
        uB = USFMBible( None ) # Get a blank object
        uB.loadSSFData( fileResult )
##        print( "ssf" )
##        for something in uB.ssfDict:
##            try: print( "  ", something, uB.ssfDict[something] )
##            except UnicodeEncodeError: print( "   (skipped)" )
        try: uBName = uB.ssfDict['Name']
        except KeyError:
            showerror( APP_NAME, 'Could not find name in ' + fileResult )
        try: uBFullName = uB.ssfDict['FullName']
        except KeyError:
            showerror( APP_NAME, 'Could not find full name in ' + fileResult )
        if 'Editable' in uB.ssfDict and uB.ssfDict['Editable'] != 'T':
            showerror( APP_NAME, 'Project {} ({}) is not set to be editable'.format( uBName, uBFullName ) )
            return

        # Find the correct folder
        if 'Directory' not in uB.ssfDict:
            showerror( APP_NAME, 'Project {} ({}) has no directory specified'.format( uBName, uBFullName ) )
            return
        ssfDirectory = uB.ssfDict['Directory']
        if not os.path.exists( ssfDirectory ):
            showwarning( APP_NAME, 'SSF project {} ({}) directory {} not found on this system'.format( uBName, uBFullName, repr(ssfDirectory) ) )
            if not sys.platform.startswith( 'win' ): # Let's try the next folder down
                print( "Not windows" )
                print( 'ssD1', repr(ssfDirectory) )
                slash = '\\' if '\\' in ssfDirectory else '/'
                if ssfDirectory[-1] == slash: ssfDirectory = ssfDirectory[:-1] # Remove the trailing slash
                ix = ssfDirectory.rfind( slash ) # Find the last slash
                if ix!= -1:
                    ssfDirectory = os.path.join( os.path.dirname(fileResult), ssfDirectory[ix+1:] + '/' )
                    print( 'ssD2', repr(ssfDirectory) )
                    if not os.path.exists( ssfDirectory ):
                        showerror( APP_NAME, 'Unable to discover Paratext {} project folder'.format( uBName ) )
                        return
        #print( "uB1", uB )
        uB.preload( ssfDirectory )
        #print( "uB2", uB )
##        ssfText = open( fileResult, 'rt', encoding='utf-8' ).read()
##        if ssfText == None:
##            showerror( APP_NAME, 'Could not decode and open file ' + fileResult )
##        else:

        uEW = USFMEditWindow( self, uB )
        uEW.setFilepath( fileResult )
##            tEW.setAllText( ssfText )
##            #if windowGeometry: tEW.geometry( windowGeometry )
        self.appWins.append( uEW )
        uEW.updateShownBCV( self.getVerseKey( uEW.groupCode ) )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doOpenParatextProject" )
        self.setReadyStatus()
    # end of Application.doOpenParatextProject


    def doHelp( self, event=None ):
        from Help import HelpBox
        helpInfo = ProgNameVersion + "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindings:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self.ApplicationParent, ProgName, helpInfo )
    # end of Application.doHelp


    def doAbout( self, event=None ):
        from About import AboutBox
        ab = AboutBox( self.ApplicationParent, ProgName, ProgNameVersion )
    # end of Application.doAbout


    def doProjectClose( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( t("doProjectClose()") )
        self.notWrittenYet()
    # end of Application.doProjectClose


    def writeSettingsFile( self ):
        """
        Update our program settings and save them.
        """
        if BibleOrgSysGlobals.debugFlag or debuggingThisModule: print( t("writeSettingsFile()") )
        if BibleOrgSysGlobals.debugFlag: self.setDebugText( 'writeSettingsFile' )
        self.settings.reset()

        self.settings.data[ProgName] = {}
        main = self.settings.data[ProgName]
        main['settingsVersion'] = SettingsVersion
        main['progVersion'] = ProgVersion
        main['themeName'] = self.themeName
        main['windowGeometry'] = self.ApplicationParent.geometry()
        main['minimumXSize'] = str( self.minimumXSize )
        main['minimumYSize'] = str( self.minimumYSize )

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


        # Get the current window settings
        self.getCurrentWindowSettings()
        # Save all the various window set-ups
        for windowsSettingName in self.windowsSettingsDict:
            if BibleOrgSysGlobals.debugFlag: print( t("Saving windows set-up {}").format( repr(windowsSettingName) ) )
            try: # Just in case something goes wrong with characters in a settings name
                self.settings.data['WindowSetting'+windowsSettingName] = {}
                thisOne = self.settings.data['WindowSetting'+windowsSettingName]
                for windowNumber,winDict in sorted( self.windowsSettingsDict[windowsSettingName].items() ):
                    #print( "  ", repr(windowNumber), repr(winDict) )
                    for windowSettingName,value in sorted( winDict.items() ):
                        thisOne[windowNumber+windowSettingName] = value
            except: logging.error( t("writeSettingsFile: unable to write {} windows set-up").format( repr(windowsSettingName) ) )
        self.settings.save()
    # end of Application.writeSettingsFile


    def doCloseMe( self ):
        """
        Save files first, and then end the application.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("doCloseMe()") )
        haveModifications = False
        for appWin in self.appWins:
            if 'Editor' in appWin.genericWindowType and appWin.modified():
                haveModifications = True; break
        if haveModifications:
            showerror( _("Save files"), _("You need to save or close your work first.") )
        else:
            self.writeSettingsFile()
            self.ApplicationParent.destroy()
    # end of Application.doCloseMe
# end of class Application



def main( homeFolder, loggingFolder ):
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag:
        import os
        print( t("Platform is"), sys.platform ) # e.g., "win32"
        print( t("OS name is"), os.name ) # e.g., "nt"
        if sys.platform == "linux": print( t("OS uname is"), os.uname() )
        print( t("Running main...") )

    tkRootWindow = tk.Tk()
    if BibleOrgSysGlobals.debugFlag:
        print( 'Windowing system is', repr( tkRootWindow.tk.call('tk', 'windowingsystem') ) )
    tkRootWindow.title( ProgNameVersion )
    settings = ApplicationSettings( homeFolder, DATA_FOLDER, SETTINGS_SUBFOLDER, ProgName )
    settings.load()

    application = Application( tkRootWindow, homeFolder, loggingFolder, settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.main


if __name__ == '__main__':
    # Configure basic set-up
    homeFolder = findHomeFolder()
    loggingFolder = os.path.join( homeFolder, DATA_FOLDER, LOGGING_SUBFOLDER )
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion, loggingFolder=loggingFolder )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    main( homeFolder, loggingFolder )

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of Biblelator.py