#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorSettingsEditor.py
#
# BOS (Bible Organisational System) manager program
#
# Copyright (C) 2016-2019 Robert Hunt
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
Program to allow viewing of various BOS (Bible Organisational System) subsystems
    such as versification systems, books names systems, etc.
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2010-05-12' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorSettingsEditor"
PROGRAM_NAME = "Biblelator Settings Editor"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = True


import sys
import os
import logging, subprocess
import multiprocessing

import tkinter as tk
from tkinter.ttk import Style, Frame, Button, Scrollbar, Label, Notebook
from tkinter.scrolledtext import ScrolledText

# Biblelator imports
from Biblelator.BiblelatorGlobals import DEFAULT, tkSTART, MAX_RECENT_FILES, errorBeep, \
        DATA_FOLDER_NAME, LOGGING_SUBFOLDER_NAME, SETTINGS_SUBFOLDER_NAME, \
        DEFAULT_KEY_BINDING_DICT, MAX_PSEUDOVERSES, \
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
from BibleOrgSys.Reference.BibleStylesheets import BibleStylesheet



MAIN_APP_NAME = 'Biblelator'
# Default window size settings (Note: X=width, Y=height)
INITIAL_MAIN_SIZE, INITIAL_MAIN_SIZE_DEBUG, MINIMUM_MAIN_SIZE, MAXIMUM_MAIN_SIZE = '607x376', '607x460', '550x375', '700x600'



class BiblelatorSettingsEditor( Frame ):
    """
    This is the main application window (well, actually a frame in the root toplevel window).

    Its main job is to keep track of self.currentVerseKey (and self.currentVerseKeyGroup)
        and use that to inform child windows of BCV movements.
    """
    global settings
    def __init__( self, rootWindow, homeFolderPath, loggingFolderPath, iconImage ):
        """
        Main app initialisation function.

        Creates the main menu and toolbar which includes the main BCV (book/chapter/verse) selector.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BiblelatorSettingsEditor.__init__( {}, {}, {}, … )".format( rootWindow, homeFolderPath, loggingFolderPath ) )
        self.rootWindow, self.homeFolderPath, self.loggingFolderPath, self.iconImage = rootWindow, homeFolderPath, loggingFolderPath, iconImage
        self.parentApp = self # Yes, that's me, myself!
        self.starting = True

        self.themeName = 'default'
        self.style = Style()
        self.interfaceLanguage = DEFAULT
        self.interfaceComplexity = DEFAULT
        self.touchMode = False # True makes larger buttons
        self.tabletMode = False
        self.showDebugMenu = False
        self.internetAccessEnabled = False

        self.lastFind = None
        #self.openDialog = None
        self.saveDialog = None
        self.optionsDict = {}

        self.fixedSettingsFlag = False # Can the user change the settings file that we're looking at?

        if BibleOrgSysGlobals.debugFlag: print( "Button default font", Style().lookup('TButton', 'font') )
        if BibleOrgSysGlobals.debugFlag: print( "Label default font", Style().lookup('TLabel', 'font') )

        self.stylesheet = BibleStylesheet().loadDefault()
        Frame.__init__( self, self.rootWindow )
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
            self.setDebugText( "Starting up…" )

        self.keyBindingDict = DEFAULT_KEY_BINDING_DICT
        self.myKeyboardBindingsList = []
        self.recentFiles = []

        # Read and apply the saved settings
        if BibleOrgSysGlobals.commandLineArguments.override is None:
            self.INIname = MAIN_APP_NAME # We use the Biblelator settings
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "Using default {!r} ini file".format( self.INIname ) )
        else:
            self.INIname = BibleOrgSysGlobals.commandLineArguments.override
            vPrint( 'Normal', debuggingThisModule, _("Using settings from user-specified {!r} ini file").format( self.INIname ) )
        #self.settings = ApplicationSettings( self.homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, self.INIname )
        #self.settings.load()
        #if PROGRAM_NAME not in self.settings.data or 'windowSize' not in self.settings.data[PROGRAM_NAME] or 'windowPosition' not in self.settings.data[PROGRAM_NAME]:
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
        self.createMainButtons()
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
    # end of BiblelatorSettingsEditor.__init__


    def setGenericBibleOrganisationalSystem( self, BOSname ):
        """
        We usually use a fairly generic BibleOrganisationalSystem (BOS) to ensure
            that it contains all the books that we might ever want to navigate to.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "setGenericBibleOrganisationalSystem( {} )".format( BOSname ) )

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
    # end of BiblelatorSettingsEditor.setGenericBibleOrganisationalSystem


    def createNormalMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createNormalMenuBar()" )

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

        # if 0:
        #     #editMenu = tk.Menu( self.menubar, tearoff=False )
        #     #self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        #     #editMenu.add_command( label=_('Find…'), underline=0, command=self.notWrittenYet )
        #     #editMenu.add_command( label=_('Replace…'), underline=0, command=self.notWrittenYet )

        #     booksCodesMenu = tk.Menu( self.menubar, tearoff=False )
        #     self.menubar.add_cascade( menu=booksCodesMenu, label=_('Codes'), underline=0 )
        #     booksCodesMenu.add_command( label=_('View…'), underline=-1, command=self.notWrittenYet )
        #     booksCodesMenu.add_separator()
        #     booksCodesMenu.add_command( label=_('Info…'), underline=0, command=self.doGotoInfo )

        #     ordersMenu = tk.Menu( self.menubar, tearoff=False )
        #     self.menubar.add_cascade( menu=ordersMenu, label=_('Orders'), underline=0 )
        #     ordersMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        #     ordersMenu.add_separator()
        #     ordersMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

        #     namesMenu = tk.Menu( self.menubar, tearoff=False )
        #     self.menubar.add_cascade( menu=namesMenu, label=_('Names'), underline=0 )
        #     submenuBibleResourceType = tk.Menu( namesMenu, tearoff=False )
        #     namesMenu.add_command( label=_('View…'), underline=5, command=self.notWrittenYet )
        #     namesMenu.add_separator()
        #     namesMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

        #     versificationsMenu = tk.Menu( self.menubar, tearoff=False )
        #     self.menubar.add_cascade( menu=versificationsMenu, label=_('Versifications'), underline=0 )
        #     versificationsMenu.add_command( label=_('View…'), underline=0, command=self.notWrittenYet )
        #     versificationsMenu.add_separator()
        #     versificationsMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

        #     orgsMenu = tk.Menu( self.menubar, tearoff=False )
        #     self.menubar.add_cascade( menu=orgsMenu, label=_('Bibles'), underline=0 )
        #     orgsMenu.add_command( label=_('View…'), underline=0, command=self.notWrittenYet )
        #     orgsMenu.add_separator()
        #     orgsMenu.add_command( label=_('Info…'), underline=0, command=self.notWrittenYet )

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
    # end of BiblelatorSettingsEditor.createNormalMenuBar

    def createTouchMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createTouchMenuBar()" )
            assert self.touchMode

        self.createNormalMenuBar()
    # end of BiblelatorSettingsEditor.createTouchMenuBar


    def createNormalNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createNormalNavigationBar()" )

    # end of BiblelatorSettingsEditor.createNormalNavigationBar

    def createTouchNavigationBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createTouchNavigationBar()" )
            assert self.touchMode

    # end of BiblelatorSettingsEditor.createTouchNavigationBar


    def createToolBar( self ):
        """
        Create a tool bar containing several helpful buttons at the top of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createToolBar()" )

    # end of BiblelatorSettingsEditor.createToolBar


    def createMainButtons( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createMainButtons()" )

        xPad, yPad = (6, 8) if self.touchMode else (2, 2)

        Style().configure( 'MainButtons.TFrame', background='red' )
        Style().map("Ok.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        buttonFrame = Frame( self, cursor='hand2', relief=tk.RAISED, style='MainButtons.TFrame' )

        Button( buttonFrame, text=_("Ok"), style='Ok.TButton', command=self.doOk ) \
                        .pack( side=tk.RIGHT, padx=xPad, pady=yPad )
        Button( buttonFrame, text=_("Apply"), style='Ok.TButton', command=self.doApply ) \
                        .pack( side=tk.RIGHT, padx=xPad, pady=yPad )
        Button( buttonFrame, text=_("Cancel"), style='Ok.TButton', command=self.doCancel ) \
                        .pack( side=tk.RIGHT, padx=xPad, pady=yPad )

        buttonFrame.pack( side=tk.BOTTOM, fill=tk.X )
    # end of BiblelatorSettingsEditor.createMainButtons


    def createNotebook( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createToolBar()" )

        self.notebook = Notebook( self )

        # Adding Frames as pages for the ttk.Notebook

        # Main settings files page
        print( "Create main settings files page" )
        self.settingsFilesPage = Frame( self.notebook )
        self.fdrVar = tk.StringVar()
        fdrLabel = Label( self.settingsFilesPage, text=_("Standard folder:") )
        fdrLabel.grid( row=0, column=0, padx=0, pady=2, sticky=tk.E )
        self.fdrEntry = BEntry( self.settingsFilesPage, width=50, textvariable=self.fdrVar, state=tk.DISABLED )
        self.fdrEntry.grid( row=0, column=1, padx=2, pady=2, sticky=tk.W )

        fnLabel = Label( self.settingsFilesPage, text=_("Settings name:") )
        fnLabel.grid( row=1, column=0, padx=0, pady=2, sticky=tk.E )
        self.fnVar = tk.StringVar()
        if self.fixedSettingsFlag:
            self.fnEntry = BEntry( self.settingsFilesPage, width=15, textvariable=self.fnVar, state=tk.DISABLED )
        else: # not fixed settings
            self.fnEntry = BCombobox( self.settingsFilesPage, width=15, textvariable=self.fnVar )
            #self.fnEntry['values'] = self.bookNames
            self.fnEntry.bind('<<ComboboxSelected>>', self.selectedNewSettingsFile )
            self.fnEntry.bind( '<Return>', self.selectedNewSettingsFile )
        self.fnEntry.grid( row=1, column=1, padx=2, pady=2, sticky=tk.W )


        # Main settings page
        print( "Create main settings page" )
        self.mainPage = Frame( self.notebook )
        self.svVar = tk.StringVar()
        svLabel = Label( self.mainPage, text=_("Settings version:") )
        svLabel.grid( row=0, column=0, padx=0, pady=2, sticky=tk.E )
        self.svEntry = BEntry( self.mainPage, width=8, textvariable=self.svVar, state=tk.DISABLED )
        #self.fnEntry.bind( '<Return>', self.searchBBBCode )
        self.svEntry.grid( row=0, column=1, padx=2, pady=2, sticky=tk.W )
        self.pvVar = tk.StringVar()
        pvLabel = Label( self.mainPage, text=_("Program version:") )
        pvLabel.grid( row=1, column=0, padx=0, pady=2, sticky=tk.E )
        self.pvEntry = BEntry( self.mainPage, width=8, textvariable=self.pvVar, state=tk.DISABLED )
        #self.fnEntry.bind( '<Return>', self.searchBBBCode )
        self.pvEntry.grid( row=1, column=1, padx=2, pady=2, sticky=tk.W )
        self.thnVar = tk.StringVar()
        thnLabel = Label( self.mainPage, text=_("Theme name:") )
        thnLabel.grid( row=2, column=0, padx=0, pady=2, sticky=tk.E )
        self.thnEntry = BEntry( self.mainPage, width=20, textvariable=self.thnVar, state=tk.DISABLED )
        #self.fnEntry.bind( '<Return>', self.searchBBBCode )
        self.thnEntry.grid( row=2, column=1, padx=2, pady=2, sticky=tk.W )
        self.wszVar = tk.StringVar()
        wszLabel = Label( self.mainPage, text=_("Window size:") )
        wszLabel.grid( row=3, column=0, padx=0, pady=2, sticky=tk.E )
        self.wszEntry = BEntry( self.mainPage, width=12, textvariable=self.wszVar, state=tk.DISABLED )
        #self.fnEntry.bind( '<Return>', self.searchBBBCode )
        self.wszEntry.grid( row=3, column=1, padx=2, pady=2, sticky=tk.W )
        self.wposVar = tk.StringVar()
        wposLabel = Label( self.mainPage, text=_("Window position:") )
        wposLabel.grid( row=4, column=0, padx=0, pady=2, sticky=tk.E )
        self.wposEntry = BEntry( self.mainPage, width=12, textvariable=self.wposVar, state=tk.DISABLED )
        #self.fnEntry.bind( '<Return>', self.searchBBBCode )
        self.wposEntry.grid( row=4, column=1, padx=2, pady=2, sticky=tk.W )
        self.minszVar = tk.StringVar()
        minszLabel = Label( self.mainPage, text=_("Minimum size:") )
        minszLabel.grid( row=5, column=0, padx=0, pady=2, sticky=tk.E )
        self.minszEntry = BEntry( self.mainPage, width=12, textvariable=self.minszVar, state=tk.DISABLED )
        #self.fnEntry.bind( '<Return>', self.searchBBBCode )
        self.minszEntry.grid( row=5, column=1, padx=2, pady=2, sticky=tk.W )
        self.maxszVar = tk.StringVar()
        maxszLabel = Label( self.mainPage, text=_("Maximum size:") )
        maxszLabel.grid( row=6, column=0, padx=0, pady=2, sticky=tk.E )
        self.maxszEntry = BEntry( self.mainPage, width=12, textvariable=self.maxszVar, state=tk.DISABLED )
        #self.fnEntry.bind( '<Return>', self.searchBBBCode )
        self.maxszEntry.grid( row=6, column=1, padx=2, pady=2, sticky=tk.W )

        # Interface page
        print( "Create interface page" )
        self.interfacePage = Frame( self.notebook )
        self.ilVar = tk.StringVar()
        ilLabel = Label( self.interfacePage, text=_("Language:") )
        ilLabel.grid( row=0, column=0, padx=0, pady=2, sticky=tk.E )
        self.ilEntry = BEntry( self.interfacePage, width=25, textvariable=self.ilVar, state=tk.DISABLED )
        #self.ilEntry.bind( '<Return>', self.searchBBBCode )
        self.ilEntry.grid( row=0, column=1, padx=2, pady=2, sticky=tk.W )
        self.icVar = tk.StringVar()
        icLabel = Label( self.interfacePage, text=_("Complexity:") )
        icLabel.grid( row=1, column=0, padx=0, pady=2, sticky=tk.E )
        self.icEntry = BEntry( self.interfacePage, width=25, textvariable=self.icVar, state=tk.DISABLED )
        #self.icEntry.bind( '<Return>', self.searchBBBCode )
        self.icEntry.grid( row=1, column=1, padx=2, pady=2, sticky=tk.W )
        self.tchVar = tk.IntVar()
        tchCb = tk.Checkbutton( self.interfacePage, text=_("Touch mode:"), variable=self.tchVar, command=self.flagChange )
        tchCb.grid( row=2, column=1, padx=0, pady=2, sticky=tk.W )
        self.tabVar = tk.IntVar()
        tabCb = tk.Checkbutton( self.interfacePage, text=_("Tablet mode:"), variable=self.tabVar, command=self.flagChange )
        tabCb.grid( row=3, column=1, padx=0, pady=2, sticky=tk.W )
        self.sdmVar = tk.IntVar()
        tabCb = tk.Checkbutton( self.interfacePage, text=_("Show debug mode:"), variable=self.sdmVar, command=self.flagChange )
        tabCb.grid( row=3, column=1, padx=0, pady=2, sticky=tk.W )

        # Internet communications page
        print( "Create Internet page" )
        self.internetPage = Frame( self.notebook )
        self.iaVar = tk.IntVar()
        iaCb = tk.Checkbutton( self.internetPage, text=_("Internet access enabled"), variable=self.iaVar, command=self.flagChange )
        iaCb.grid( row=0, column=0, padx=0, pady=2, sticky=tk.W )
        self.ifVar = tk.IntVar()
        ifCb = tk.Checkbutton( self.internetPage, text=_("Internet is fast"), variable=self.ifVar, command=self.flagChange )
        ifCb.grid( row=1, column=0, padx=20, pady=2, sticky=tk.W )
        self.ieVar = tk.IntVar()
        ieCb = tk.Checkbutton( self.internetPage, text=_("Internet is expensive"), variable=self.ieVar, command=self.flagChange )
        ieCb.grid( row=2, column=0, padx=20, pady=2, sticky=tk.W )
        self.cbVar = tk.IntVar()
        cbCb = tk.Checkbutton( self.internetPage, text=_("Cloud backup enabled"), variable=self.cbVar, command=self.flagChange )
        cbCb.grid( row=3, column=0, padx=20, pady=2, sticky=tk.W )
        self.cdVar = tk.IntVar()
        cdCb = tk.Checkbutton( self.internetPage, text=_("Check for developer messages"), variable=self.cdVar, command=self.flagChange )
        cdCb.grid( row=4, column=0, padx=20, pady=2, sticky=tk.W )
        self.lmVar = tk.StringVar()
        lmLabel = Label( self.internetPage, text=_("Last message number read:") )
        lmLabel.grid( row=5, column=0, sticky=tk.E )
        self.lmEntry = BEntry( self.internetPage, width=5, textvariable=self.lmVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.lmEntry.grid( row=5, column=1 )
        self.usVar = tk.IntVar()
        usCb = tk.Checkbutton( self.internetPage, text=_("Send usage statistics"), variable=self.usVar, command=self.flagChange )
        usCb.grid( row=6, column=0, padx=20, pady=2, sticky=tk.W )
        self.auVar = tk.IntVar()
        auCb = tk.Checkbutton( self.internetPage, text=_("Automatic updates"), variable=self.auVar, command=self.flagChange )
        auCb.grid( row=7, column=0, padx=20, pady=2, sticky=tk.W )
        self.dvVar = tk.IntVar()
        dvCb = tk.Checkbutton( self.internetPage, text=_("Use development versions"), variable=self.dvVar, command=self.flagChange )
        dvCb.grid( row=8, column=0, padx=40, pady=2, sticky=tk.W )

        # Projects page
        print( "Create projects page" )
        self.projectsPage = Frame( self.notebook )
        self.cpVar = tk.StringVar()
        cpLabel = Label( self.projectsPage, text=_("Current project name:") )
        cpLabel.grid( row=0, column=0, padx=0, pady=2, sticky=tk.E )
        self.cpEntry = BEntry( self.projectsPage, width=25, textvariable=self.cpVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.cpEntry.grid( row=0, column=1, padx=2, pady=2, sticky=tk.W )

        # Users page
        print( "Create users page" )
        self.usersPage = Frame( self.notebook )
        self.unVar = tk.StringVar()
        unLabel = Label( self.usersPage, text=_("Current user name:") )
        unLabel.grid( row=0, column=0, padx=0, pady=2, sticky=tk.E )
        self.unEntry = BEntry( self.usersPage, width=25, textvariable=self.unVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.unEntry.grid( row=0, column=1, padx=2, pady=2, sticky=tk.W )
        self.uiVar = tk.StringVar()
        uiLabel = Label( self.usersPage, text=_("Current user initials:") )
        uiLabel.grid( row=1, column=0, padx=0, pady=2, sticky=tk.E )
        self.uiEntry = BEntry( self.usersPage, width=5, textvariable=self.uiVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.uiEntry.grid( row=1, column=1, padx=2, pady=2, sticky=tk.W )
        self.uemVar = tk.StringVar()
        uemLabel = Label( self.usersPage, text=_("User email:") )
        uemLabel.grid( row=2, column=0, padx=0, pady=2, sticky=tk.E )
        self.uemEntry = BEntry( self.usersPage, width=25, textvariable=self.uemVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.uemEntry.grid( row=2, column=1, padx=2, pady=2, sticky=tk.W )
        self.urVar = tk.StringVar()
        urLabel = Label( self.usersPage, text=_("User role:") )
        urLabel.grid( row=3, column=0, padx=0, pady=2, sticky=tk.E )
        self.urEntry = BEntry( self.usersPage, width=20, textvariable=self.urVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.urEntry.grid( row=3, column=1, padx=2, pady=2, sticky=tk.W )
        self.uasVar = tk.StringVar()
        uasLabel = Label( self.usersPage, text=_("User assignments:") )
        uasLabel.grid( row=4, column=0, padx=0, pady=2, sticky=tk.E )
        self.uasEntry = BEntry( self.usersPage, width=20, textvariable=self.uasVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.uasEntry.grid( row=4, column=1, padx=2, pady=2, sticky=tk.W )

        # Paths page
        print( "Create paths page" )
        self.pathsPage = Frame( self.notebook )
        self.ltfVar = tk.StringVar()
        ltfLabel = Label( self.pathsPage, text=_("Last text folder:") )
        ltfLabel.grid( row=0, column=0, padx=0, pady=2, sticky=tk.E )
        self.ltfEntry = BEntry( self.pathsPage, width=35, textvariable=self.ltfVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.ltfEntry.grid( row=0, column=1, padx=2, pady=2, sticky=tk.W )
        self.lbfVar = tk.StringVar()
        lbfLabel = Label( self.pathsPage, text=_("Last Biblelator folder:") )
        lbfLabel.grid( row=1, column=0, padx=0, pady=2, sticky=tk.E )
        self.lbfEntry = BEntry( self.pathsPage, width=35, textvariable=self.lbfVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.lbfEntry.grid( row=2, column=1, padx=2, pady=2, sticky=tk.W )
        self.lpfVar = tk.StringVar()
        lpfLabel = Label( self.pathsPage, text=_("Last Paratext folder:") )
        lpfLabel.grid( row=2, column=0, padx=0, pady=2, sticky=tk.E )
        self.lpfEntry = BEntry( self.pathsPage, width=35, textvariable=self.lpfVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.lpfEntry.grid( row=2, column=1, padx=2, pady=2, sticky=tk.W )
        self.libfVar = tk.StringVar()
        libfLabel = Label( self.pathsPage, text=_("Last internal Bible folder:") )
        libfLabel.grid( row=3, column=0, padx=0, pady=2, sticky=tk.E )
        self.libfEntry = BEntry( self.pathsPage, width=35, textvariable=self.libfVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.libfEntry.grid( row=3, column=1, padx=2, pady=2, sticky=tk.W )

        # Recent files page
        print( "Create recent files page" )
        self.recentFilesPage = Frame( self.notebook )
        self.rffnVars, self.rffldVars, self.rftypVars = [], [], []
        for rr in range( MAX_RECENT_FILES ):
            self.rffnVars.append( tk.StringVar() ); self.rffldVars.append( tk.StringVar() ); self.rftypVars.append( tk.StringVar() );
            Label( self.recentFilesPage, text='{}:'.format(rr+1) ).grid( row=2*rr, column=0, padx=0, pady=3, sticky=tk.E )
            BEntry( self.recentFilesPage, width=30, textvariable=self.rffnVars[rr] ).grid( row=2*rr, column=1, padx=2, pady=3, sticky=tk.W )
            BEntry( self.recentFilesPage, width=30, textvariable=self.rftypVars[rr] ).grid( row=2*rr, column=2, padx=2, pady=3, sticky=tk.W )
            BEntry( self.recentFilesPage, width=60, textvariable=self.rffldVars[rr] ).grid( row=2*rr+1, column=1, columnspan=2, padx=2, pady=1, sticky=tk.W )

        # Bible BCV (book/chapter/verse) page
        print( "Create BCV page" )
        self.BCVGroupsPage = Frame( self.notebook )
        self.gBOSVar = tk.StringVar()
        gBOSLabel = Label( self.BCVGroupsPage, text=_("Generic BOS name:") )
        gBOSLabel.grid( row=0, column=0, padx=0, pady=2, sticky=tk.E )
        self.gBOSEntry = BEntry( self.BCVGroupsPage, width=35, textvariable=self.gBOSVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.gBOSEntry.grid( row=0, column=1, padx=2, pady=2, sticky=tk.W )
        self.cgVar = tk.StringVar()
        cgLabel = Label( self.BCVGroupsPage, text=_("Current group:") )
        cgLabel.grid( row=1, column=0, padx=0, pady=2, sticky=tk.E )
        self.cgEntry = BEntry( self.BCVGroupsPage, width=3, textvariable=self.cgVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.cgEntry.grid( row=1, column=1, padx=2, pady=2, sticky=tk.W )
        self.gaVar = tk.StringVar()
        gaLabel = Label( self.BCVGroupsPage, text=_("Group A:") )
        gaLabel.grid( row=2, column=0, padx=0, pady=2, sticky=tk.E )
        self.gaEntry = BEntry( self.BCVGroupsPage, width=12, textvariable=self.gaVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.gaEntry.grid( row=2, column=1, padx=2, pady=2, sticky=tk.W )
        self.gbVar = tk.StringVar()
        gbLabel = Label( self.BCVGroupsPage, text=_("Group B:") )
        gbLabel.grid( row=3, column=0, padx=0, pady=2, sticky=tk.E )
        self.gbEntry = BEntry( self.BCVGroupsPage, width=12, textvariable=self.gbVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.gbEntry.grid( row=3, column=1, padx=2, pady=2, sticky=tk.W )
        self.gcVar = tk.StringVar()
        gcLabel = Label( self.BCVGroupsPage, text=_("Group C:") )
        gcLabel.grid( row=4, column=0, padx=0, pady=2, sticky=tk.E )
        self.gcEntry = BEntry( self.BCVGroupsPage, width=12, textvariable=self.gcVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.gcEntry.grid( row=4, column=1, padx=2, pady=2, sticky=tk.W )
        self.gdVar = tk.StringVar()
        gdLabel = Label( self.BCVGroupsPage, text=_("Group D:") )
        gdLabel.grid( row=5, column=0, padx=0, pady=2, sticky=tk.E )
        self.gdEntry = BEntry( self.BCVGroupsPage, width=12, textvariable=self.gdVar )
        #self.lmEntry.bind( '<Return>', self.searchBBBCode )
        self.gdEntry.grid( row=5, column=1, padx=2, pady=2, sticky=tk.W )

        # Current windows page
        print( "Create current windows page" )
        self.currentWindowsPage = Frame( self.notebook )
        if __name__ == '__main__':
            pass
        else:
            self.currentWindowsTextBox = ScrolledText( self.currentWindowsPage, bg='orange' )
            self.currentWindowsTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
            #self.currentWindowsTextBox.insert( tk.END, 'Organisations' )
            self.currentWindowsTextBox.grid( row=0, column=4, rowspan=2, sticky=tk.N+tk.S+tk.E )
            self.currentWindowsTextBox.insert( tk.END, "We cannot adjust the current windows from inside Biblelator.\n\nIf you wish to adjust current windows, please close Biblelator and run BiblelatorSettingsEditor.py in stand-alone mode." )

        print( "Add all pages" )
        self.notebook.add( self.settingsFilesPage, text=_("Settings files") )
        self.notebook.add( self.mainPage, text=_("Main") )
        self.notebook.add( self.interfacePage, text=_("Interface") )
        self.notebook.add( self.internetPage, text=_("Internet") )
        self.notebook.add( self.projectsPage, text=_("Projects") )
        self.notebook.add( self.usersPage, text=_("Users") )
        self.notebook.add( self.pathsPage, text=_("Paths") )
        self.notebook.add( self.recentFilesPage, text=_("Recent files") )
        self.notebook.add( self.BCVGroupsPage, text=_("BCV groups") )
        self.notebook.add( self.currentWindowsPage, text=_("Current windows") )
        self.notebook.pack( expand=tk.YES, fill=tk.BOTH )

        self.loadSettingsIntoTabs()
        self.somethingChanged = False
    # end of BiblelatorSettingsEditor.createNotebook


    def flagChange( self ): self.somethingChanged = True


    def loadSettingsIntoTabs( self ):
        """
        Load the current settings for self.INIname into self.settings.data
            and then load them into the variables for our editor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "loadSettingsIntoTabs() for {!r}".format( self.INIname ) )

        self.settings = ApplicationSettings( self.homeFolderPath, DATA_FOLDER_NAME, SETTINGS_SUBFOLDER_NAME, self.INIname )
        self.settings.load()
        self.settingsChangedFlag = False

        self.fdrVar.set( self.settings.settingsFolder )
        self.fnVar.set( self.INIname )
        if not self.fixedSettingsFlag:
            self.iniList = []
            for something in os.listdir( self.settings.settingsFolder ):
                somepath = os.path.join( self.settings.settingsFolder, something )
                if os.path.isfile( somepath ):
                    if somepath.upper().endswith( '.INI' ):
                        self.iniList.append( something[:-4] )
            self.fnEntry['values'] = self.iniList

        try: self.svVar.set( self.settings.data[MAIN_APP_NAME]['settingsVersion'] )
        except KeyError: self.svVar.set( '' )
        try: self.pvVar.set( self.settings.data[MAIN_APP_NAME]['PROGRAM_VERSION'] )
        except KeyError: self.pvVar.set( '' )
        try: self.thnVar.set( self.settings.data['Interface']['themeName'] )
        except KeyError: self.thnVar.set( 'default' )
        try: self.wszVar.set( self.settings.data[MAIN_APP_NAME]['windowSize'] )
        except KeyError: self.wszVar.set( '' )
        try: self.wposVar.set( self.settings.data[MAIN_APP_NAME]['windowPosition'] )
        except KeyError: self.wposVar.set( '' )
        try: self.minszVar.set( self.settings.data[MAIN_APP_NAME]['minimumSize'] )
        except KeyError: self.minszVar.set( '' )
        try: self.maxszVar.set( self.settings.data[MAIN_APP_NAME]['maximumSize'] )
        except KeyError: self.maxszVar.set( '' )

        try: self.ilVar.set( self.settings.data['Interface']['interfaceLanguage'] )
        except KeyError: self.ilVar.set( 'Default' )
        try: self.icVar.set( self.settings.data['Interface']['interfaceComplexity'] )
        except KeyError: self.icVar.set( 'Default' )
        try: self.tchVar.set( self.settings.data['Interface']['touchMode'] == 'True' )
        except KeyError: self.tchVar.set( False )
        try: self.tabVar.set( self.settings.data['Interface']['tabletMode'] == 'True' )
        except KeyError: self.tabVar.set( False )
        try: self.sdmVar.set( self.settings.data['Interface']['showDebugMenu'] == 'True' )
        except KeyError: self.sdmVar.set( False )

        try: self.iaVar.set( self.settings.data['Internet']['internetAccess'] == 'Enabled' )
        except KeyError: self.iaVar.set( True )
        try: self.ifVar.set( self.settings.data['Internet']['internetFast'].lower() in ('true' ,'yes',) )
        except KeyError: self.ifVar.set( True )
        try: self.ieVar.set( self.settings.data['Internet']['internetExpensive'].lower() in ('true' ,'yes',) )
        except KeyError: self.ieVar.set( True )
        try: self.cbVar.set( self.settings.data['Internet']['cloudBackups'] == 'Enabled' )
        except KeyError: self.cbVar.set( True )
        try: self.cdVar.set( self.settings.data['Internet']['checkForDeveloperMessages'] == 'Enabled' )
        except KeyError: self.cdVar.set( True )
        try: self.lmVar.set( self.settings.data['Internet']['lastMessageNumberRead'] )
        except KeyError: self.lmVar.set( 0 )
        try: self.usVar.set( self.settings.data['Internet']['sendUsageStatistics'] == 'Enabled' )
        except KeyError: self.suVar.set( True )
        try: self.auVar.set( self.settings.data['Internet']['automaticUpdates'] == 'Enabled' )
        except KeyError: self.auVar.set( True )
        try: self.dvVar.set( self.settings.data['Internet']['useDevelopmentVersions'] == 'Enabled' )
        except KeyError: self.dvVar.set( False )

        try: self.cpVar.set( self.settings.data['Project']['currentProjectName'] )
        except KeyError: self.cpVar.set( '' )

        try: self.unVar.set( self.settings.data['Users']['currentUserName'] )
        except KeyError: self.unVar.set( '' )
        try: self.uiVar.set( self.settings.data['Users']['currentUserInitials'] )
        except KeyError: self.uiVar.set( '' )
        try: self.uemVar.set( self.settings.data['Users']['currentUserEmail'] )
        except KeyError: self.uemVar.set( '' )
        try: self.urVar.set( self.settings.data['Users']['currentUserRole'] )
        except KeyError: self.urVar.set( 'Translator' )
        try: self.uasVar.set( self.settings.data['Users']['currentUserAssignments'] )
        except KeyError: self.uasVar.set( 'ALL' )

        try: self.ltfVar.set( self.settings.data['Paths']['lastFileDir'] )
        except KeyError: self.ltfVar.set( '' )
        try: self.lbfVar.set( self.settings.data['Paths']['lastBiblelatorFileDir'] )
        except KeyError: self.lbfVar.set( '' )
        try: self.lpfVar.set( self.settings.data['Paths']['lastParatextFileDir'] )
        except KeyError: self.lpfVar.set( '' )
        try: self.libfVar.set( self.settings.data['Paths']['lastInternalBibleDir'] )
        except KeyError: self.libfVar.set( '' )

        for rr in range( MAX_RECENT_FILES ):
            try:
                self.rffnVars[rr].set( self.settings.data['RecentFiles']['recent{}Filename'.format(rr+1)] )
                self.rffldVars[rr].set( self.settings.data['RecentFiles']['recent{}Folder'.format(rr+1)] )
                self.rftypVars[rr].set( self.settings.data['RecentFiles']['recent{}Type'.format(rr+1)] )
            except KeyError: self.rffnVars[rr].set( '' ); self.rffldVars[rr].set( '' ); self.rftypVars[rr].set( '' )

        try: self.gBOSVar.set( self.settings.data['BCVGroups']['genericBibleOrganisationalSystemName'] )
        except KeyError: self.gBOSVar.set( '' )
        try: self.cgVar.set( self.settings.data['BCVGroups']['currentGroup'] )
        except KeyError: self.cgVar.set( 'A' )
        try: self.gaVar.set( '{} {}:{}'.format( self.settings.data['BCVGroups']['A-Book'], self.settings.data['BCVGroups']['A-Chapter'], self.settings.data['BCVGroups']['A-Verse'] ) )
        except KeyError: self.gaVar.set( 'GEN 1:1' )
        try: self.gbVar.set( '{} {}:{}'.format( self.settings.data['BCVGroups']['B-Book'], self.settings.data['BCVGroups']['B-Chapter'], self.settings.data['BCVGroups']['B-Verse'] ) )
        except KeyError: self.gbVar.set( 'GEN 1:1' )
        try: self.gcVar.set( '{} {}:{}'.format( self.settings.data['BCVGroups']['C-Book'], self.settings.data['BCVGroups']['C-Chapter'], self.settings.data['BCVGroups']['C-Verse'] ) )
        except KeyError: self.gcVar.set( 'GEN 1:1' )
        try: self.gdVar.set( '{} {}:{}'.format( self.settings.data['BCVGroups']['D-Book'], self.settings.data['BCVGroups']['D-Chapter'], self.settings.data['BCVGroups']['D-Verse'] ) )
        except KeyError: self.gdVar.set( 'GEN 1:1' )
    # end of BiblelatorSettingsEditor.loadSettingsIntoTabs


    def updateSettingsFromTabs( self ):
        """
        Update the settings from the editor, and return True/False if they have changed.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "updateSettingsFromTabs()" )

        changed = False

        last = self.settings.data['Internet']['internetAccess']
        now = 'Enabled' if self.iaVar.get() else 'Disabled'
        self.settings.data['Internet']['internetAccess'] = now
        if now!=last: changed = True

        if changed: assert self.somethingChanged
        return changed
    # end of BiblelatorSettingsEditor.updateSettingsFromTabs


    def halt( self ):
        """
        Halts the program immediately without saving any files or settings.
        Only used in debug mode.
        """
        logging.critical( "User selected HALT in DEBUG MODE. Not saving any files or settings!" )
        self.quit()
    # end of BiblelatorSettingsEditor.halt


    def createDebugToolBar( self ):
        """
        Create a debug tool bar containing several additional buttons at the top of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createDebugToolBar()" )

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
    # end of BiblelatorSettingsEditor.createDebugToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createStatusBar()" )

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
    # end of BiblelatorSettingsEditor.createStatusBar


    def createMainKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "createMainKeyboardBindings()" )

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
    # end of BiblelatorSettingsEditor.createMainKeyboardBindings()


    #def addRecentFile( self, threeTuple ):
        #"""
        #Puts most recent first
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "addRecentFile( {} )".format( threeTuple ) )
            #assert len(threeTuple) == 3

        #try: self.recentFiles.remove( threeTuple ) # Remove a duplicate if present
        #except ValueError: pass
        #self.recentFiles.insert( 0, threeTuple ) # Put this one at the beginning of the lis
        #if len(self.recentFiles)>MAX_RECENT_FILES: self.recentFiles.pop() # Remove the last one if necessary
        #self.createNormalMenuBar()
    ## end of BiblelatorSettingsEditor.addRecentFile()


    def notWrittenYet( self ):
        errorBeep()
        showError( self, _("Not implemented"), _("Not yet available, sorry") )
    # end of BiblelatorSettingsEditor.notWrittenYet


    def setStatus( self, newStatusText='' ):
        """
        Set (or clear) the status bar text.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "setStatus( {!r} )".format( newStatusText ) )

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
    # end of BiblelatorSettingsEditor.setStatus

    def setErrorStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "setErrorStatus( {!r} )".format( newStatusText ) )

        #self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='StatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( 'StatusBar.TLabel', foreground='yellow', background='red' )
        self.update()
    # end of BiblelatorSettingsEditor.setErrorStatus

    def setWaitStatus( self, newStatusText ):
        """
        Set the status bar text and change the cursor to the wait/hourglass cursor.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "setWaitStatus( {!r} )".format( newStatusText ) )

        self.rootWindow.configure( cursor='watch' ) # 'wait' can only be used on Windows
        #self.statusTextLabel.configure( style='StatusBar.TLabelWait' )
        self.setStatus( newStatusText )
        Style().configure( 'StatusBar.TLabel', foreground='black', background='DarkOrange1' )
        self.update()
    # end of BiblelatorSettingsEditor.setWaitStatus

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
    # end of BiblelatorSettingsEditor.setReadyStatus


    def setDebugText( self, newMessage=None ):
        """
        """
        if debuggingThisModule:
            #print( "setDebugText( {!r} )".format( newMessage ) )
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
            self.debugTextBox.insert( tk.END, "\n  {} wT={} gWT={} {} modID={} cVM={} fVM={} BCV={}" \
                                    .format( j+1,
                                        appWin.windowType,
                                        #appWin.windowType.replace('ChildWindow',''),
                                        appWin.genericWindowType,
                                        #appWin.genericWindowType.replace('Resource',''),
                                        appWin.winfo_geometry(), appWin.moduleID,
                                        appWin._contextViewMode if 'Bible' in appWin.genericWindowType else 'N/A',
                                        appWin._formatViewMode if 'Bible' in appWin.genericWindowType else 'N/A',
                                        appWin.BCVUpdateType if 'Bible' in appWin.genericWindowType else 'N/A' ) )
                                        #extra ) )
        #self.debugTextBox.insert( tk.END, '\n{} resource frames:'.format( len(self.childWindows) ) )
        #for j, projFrame in enumerate( self.childWindows ):
            #self.debugTextBox.insert( tk.END, "\n  {} {}".format( j, projFrame ) )
        self.debugTextBox.configure( state=tk.DISABLED ) # Don't allow editing
    # end of BiblelatorSettingsEditor.setDebugText


    def doChangeTheme( self, newThemeName ):
        """
        Set the window theme to the given scheme.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "doChangeTheme( {!r} )".format( newThemeName ) )
            assert newThemeName
            self.setDebugText( 'Set theme to {!r}'.format( newThemeName ) )

        self.themeName = newThemeName
        try:
            self.style.theme_use( newThemeName )
        except tk.TclError as err:
            showError( self, 'Error', err )
    # end of BiblelatorSettingsEditor.doChangeTheme


    def selectedNewSettingsFile( self, event=None ):
        """
        Handle a new settings files selected from the GUI dropbox.
        """
        enteredFilename = self.fnVar.get()
        self.logUsage( PROGRAM_NAME, debuggingThisModule, 'selectedNewSettingsFile' )
        if 1 or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "selectedNewSettingsFile( {} ) for {!r}".format( event, enteredFilename ) )
            #print( dir(event) )

        self.doApply() # Save any changes to current settings file
        self.INIname = enteredFilename
        self.loadSettingsIntoTabs()
    # end of BiblelatorSettingsEditor.selectedNewSettingsFile


    def doOk( self, event=None ):
        """
        Pop-up dialog
        """
        if 1 or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BiblelatorSettingsEditor.doOk( {} )".format( event ) )

        if self.settingsChangedFlag: halt
        self.doCloseMe()
    # end of BiblelatorSettingsEditor.doOk

    def doApply( self, event=None ):
        """
        Pop-up dialog
        """
        if 1 or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BiblelatorSettingsEditor.doApply( {} )".format( event ) )

        if self.settingsChangedFlag: halt
    # end of BiblelatorSettingsEditor.doApply

    def doCancel( self, event=None ):
        """
        Pop-up dialog
        """
        if 1 or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BiblelatorSettingsEditor.doCancel( {} )".format( event ) )

        if self.settingsChangedFlag: halt
        self.doCloseMe()
    # end of BiblelatorSettingsEditor.doCancel


    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        viewSettings( self )
        #if BibleOrgSysGlobals.debugFlag:
            #if debuggingThisModule: print( "doViewSettings()" )
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
    # end of BiblelatorSettingsEditor.doViewSettings


    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( "doViewLog()" )
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
    # end of BiblelatorSettingsEditor.doViewLog


    def doGotoInfo( self, event=None ):
        """
        Pop-up dialog giving goto/reference info.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BiblelatorSettingsEditor.doGotoInfo( {} )".format( event ) )

        infoString = 'Current location:\n' \
                 + '\nBible Organisational System (BOS):\n' \
                 + '  Name: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemName() ) \
                 + '  Versification: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'versificationSystem' ) ) \
                 + '  Book Order: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'bookOrderSystem' ) ) \
                 + '  Book Names: {}\n'.format( self.genericBibleOrganisationalSystem.getOrganisationalSystemValue( 'punctuationSystem' ) ) \
                 + '  Books: {}'.format( self.genericBibleOrganisationalSystem.getBookList() )
        showInfo( self, 'Goto Information', infoString )
    # end of BiblelatorSettingsEditor.doGotoInfo


    def logUsage( self, p1, p2, p3 ):
        """
        Not required in this app.
        """
        pass
    # end of BiblelatorSettingsEditor.logUsage


    def doHelp( self, event=None ):
        """
        Display a help box.
        """
        from Help import HelpBox
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "doHelp()" )

        helpInfo = programNameVersion
        helpInfo += "\n\nBasic instructions:"
        helpInfo += "\n  Click on a tab to view that subset of the Biblelator settings."
        helpInfo += "\n\nNOTE: It is also possible to edit the settings file(s) directly, but the editor should give you more context help with the various options."
        helpInfo += "\n\nKeyboard shortcuts:"
        #for name,shortcut in self.myKeyboardBindingsList:
            #helpInfo += "\n  {}\t{}".format( name, shortcut )
        #helpInfo += "\n\n  {}\t{}".format( 'Prev Verse', 'Alt+UpArrow' )
        #helpInfo += "\n  {}\t{}".format( 'Next Verse', 'Alt+DownArrow' )
        #helpInfo += "\n  {}\t{}".format( 'Prev Chapter', 'Alt+, (<)' )
        #helpInfo += "\n  {}\t{}".format( 'Next Chapter', 'Alt+. (>)' )
        #helpInfo += "\n  {}\t{}".format( 'Prev Book', 'Alt+[' )
        #helpInfo += "\n  {}\t{}".format( 'Next Book', 'Alt+]' )
        helpImage = 'BiblelatorLogoSmall.gif'
        hb = HelpBox( self.rootWindow, SHORT_PROGRAM_NAME, helpInfo, helpImage )
    # end of BiblelatorSettingsEditor.doHelp


    def doSubmitBug( self, event=None ):
        """
        Prompt the user to enter a bug report,
            collect other useful settings, etc.,
            and then send it all somewhere.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "doSubmitBug()" )

        if not self.internetAccessEnabled: # we need to warn
            showError( self, SHORT_PROGRAM_NAME, 'You need to allow Internet access first!' )
            return

        from About import AboutBox

        submitInfo = programNameVersion
        submitInfo += "\n  This program is not yet finished but we'll add this eventually!"
        ab = AboutBox( self.rootWindow, SHORT_PROGRAM_NAME, submitInfo )
    # end of BiblelatorSettingsEditor.doSubmitBug


    def doAbout( self, event=None ):
        """
        Display an about box.
        """
        from About import AboutBox
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "doAbout()" )

        aboutInfo = programNameVersion
        aboutInfo += "\nAn editor for the Biblelator (Bible translation editor) settings." \
            + "\n\nThis is still an unfinished alpha test version, but it should allow you to view (not yet alter/save) various settings in Biblelator." \
            + "\n\n{} is written in Python. For more information see our web page at Freely-Given.org/Software/Biblelator".format( SHORT_PROGRAM_NAME )
        aboutImage = 'BiblelatorLogoSmall.gif'
        ab = AboutBox( self.rootWindow, SHORT_PROGRAM_NAME, aboutInfo, aboutImage )
    # end of BiblelatorSettingsEditor.doAbout


    #def doProjectClose( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "doProjectClose()" )
        #self.notWrittenYet()
    ## end of BiblelatorSettingsEditor.doProjectClose


    #def doWriteSettingsFile( self ):
        #"""
        #Update our program settings and save them.
        #"""
        #writeSettingsFile( self )
    ### end of BiblelatorSettingsEditor.writeSettingsFile


    def doCloseMyChildWindows( self ):
        """
        Save files first, and then close child windows.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BiblelatorSettingsEditor.doCloseMyChildWindows()" )

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
    # end of BiblelatorSettingsEditor.doCloseMyChildWindows


    def doCloseMe( self ):
        """
        Save files first, and then end the application.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BiblelatorSettingsEditor.doCloseMe()" )
        elif BibleOrgSysGlobals.verbosityLevel > 0:
            print( _("{} is closing down…").format( SHORT_PROGRAM_NAME ) )

        #writeSettingsFile( self )
        if self.doCloseMyChildWindows():
            self.rootWindow.destroy()
    # end of BiblelatorSettingsEditor.doCloseMe
# end of class BiblelatorSettingsEditor



def openBiblelatorSettingsEditor( parent ):
    """
    Open the BOS Manager as a child window.

    This is used when the BOS Manager is used inside another program.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "BiblelatorSettingsEditor.openBiblelatorSettingsEditor( {} )".format( parent ) )

    myWin = tk.Toplevel( parent )
    application = BiblelatorSettingsEditor( myWin, parent.homeFolderPath, parent.loggingFolderPath, parent.iconImage )
# end of BiblelatorSettingsEditor.openBiblelatorSettingsEditor



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

    application = BiblelatorSettingsEditor( tkRootWindow, homeFolderPath, loggingFolderPath, iconImage )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of BiblelatorSettingsEditor.demo


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
    application = BiblelatorSettingsEditor( tkRootWindow, homeFolderPath, loggingFolderPath, iconImage )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of BiblelatorSettingsEditor.main


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
        print( "Platform is", sys.platform ) # e.g., 'linux,'win32'
        print( "OS name is", os.name ) # e.g., 'posix','nt'
        if sys.platform == "linux": print( "OS uname is", os.uname() ) # gives about five fields
        print( "Running main…" )

    main( homeFolderPath, loggingFolderPath )

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BiblelatorSettingsEditor.py
