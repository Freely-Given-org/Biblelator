#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Biblelator.py
#   Last modified: 2014-10-16 (also update ProgVersion below)
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
ProgVersion = "0.18"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )
SettingsVersion = "0.18" # Only need to change this if the settings format has changed

debuggingThisModule = True


import sys, os.path, logging
from gettext import gettext as _
import multiprocessing

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
from tkinter import Tk, TclError, Menu, StringVar, Spinbox, \
        TOP, BOTTOM, LEFT, RIGHT, BOTH, YES, RAISED, SUNKEN, X, \
        NORMAL, DISABLED
#from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror, showinfo
from tkinter.filedialog import Open, Directory #, SaveAs
#from tkinter.filedialog import FileDialog, LoadFileDialog, SaveFileDialog
#from tkinter.filedialog import askdirectory, askopenfile, askopenfilename, askopenfiles, asksaveasfile, asksaveasfilename, test
from tkinter.ttk import Style, Frame, Button, Combobox, Label, Entry
#from tkinter.tix import Spinbox

#fname = askopenfilename(filetypes=(("Template files", "*.tplate"),
                                           #("HTML files", "*.html;*.htm"),
                                           #("All files", "*.*") ))

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
from BibleOrganizationalSystems import BibleOrganizationalSystem
from DigitalBiblePlatform import DBPBibles
from VerseReferences import SimpleVerseKey
from BibleStylesheets import BibleStylesheet
import SwordResources
from USFMBible import USFMBible

# Biblelator imports
from BiblelatorGlobals import APP_NAME, DATA_FOLDER, SETTINGS_SUBFOLDER, MAX_WINDOWS, \
        MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE, BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, \
        EDIT_MODE_NORMAL, parseGeometry, assembleGeometryFromList, centreWindow
from BiblelatorHelpers import SaveWindowNameDialog, DeleteWindowNameDialog, SelectResourceBox
from ApplicationSettings import ApplicationSettings
from ResourceWindows import ResourceWindows, ResourceWindow
from BibleResourceWindows import SwordBibleResourceWindow, InternalBibleResourceWindow, DBPBibleResourceWindow
from LexiconResourceWindows import BibleLexiconResourceWindow
from EditWindows import TextEditWindow, USFMEditWindow, ESFMEditWindow


PARATEXT_FILETYPES = [('SSF files','.ssf'),('All files','*')]



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



class Application( Frame ):
    global settings
    def __init__( self, parent, settings ):
        if Globals.debugFlag: print( t("Application.__init__( {} )").format( parent ) )
        self.ApplicationParent, self.settings = parent, settings

        self.themeName = 'default'
        self.style = Style()

        self.lastFileDir = '.'
        self.lastFind = None
        self.openDialog = None
        self.saveDialog = None
        self.optionsDict = {}

        self.lexiconWord = None
        self.currentProject = None
        
        if Globals.debugFlag: print( "Button default font", Style().lookup("TButton", "font") )
        if Globals.debugFlag: print( "Label default font", Style().lookup("TLabel", "font") )

        self.genericBibleOrganisationalSystem = BibleOrganizationalSystem( "GENERIC-KJV-66-ENG" )
        self.stylesheet = BibleStylesheet().loadDefault()
        Frame.__init__( self, self.ApplicationParent )
        self.pack()

        self.ApplicationParent.protocol( "WM_DELETE_WINDOW", self.closeMe ) # Catch when app is closed

        self.appWins = ResourceWindows( self )

        self.createStatusBar()
        if Globals.debugFlag: # Create a scrolling debug box
            self.lastDebugMessage = None
            from tkinter.scrolledtext import ScrolledText
            #Style().configure('DebugText.TScrolledText', padding=2, background='orange')
            self.debugTextBox = ScrolledText( self.ApplicationParent, bg='orange' )#style='DebugText.TScrolledText' )
            self.debugTextBox.pack( side=BOTTOM, fill=BOTH )
            #self.debugTextBox.tag_configure( 'emp', background='yellow', font='helvetica 12 bold', relief='raised' )
            self.debugTextBox.tag_configure( 'emp', font='helvetica 10 bold' )
            self.setDebugText( "Starting up..." )

        self.SwordInterface = None
        self.DBPInterface = None
        #print( t("Preload the Sword library...") )
        #self.SwordInterface = SwordResources.SwordInterface() # Preload the Sword library

        # Set default folders
        self.lastParatextFileDir = "C:\\My Paratext Projects\\"
        self.lastInternalBibleDir = "C:\\My Paratext Projects\\"
        
        # Read and apply the saved settings
        self.parseAndApplySettings()
        if ProgName not in self.settings.data or 'windowGeometry' not in self.settings.data[ProgName]:
            centreWindow( self.ApplicationParent, 600, 360 )

##        # Open some sample windows if we don't have any already
##        if not self.appWins \
##        and Globals.debugFlag and debuggingThisModule: # Just for testing/kickstarting
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
        if Globals.debugFlag: self.createDebugToolBar()

        self.BCVHistory = []
        self.BCVHistoryIndex = None

        # Make sure all our Bible windows get updated initially
        for groupCode in BIBLE_GROUP_CODES:
            if groupCode != self.currentVerseKeyGroup: # that gets done below
                groupVerseKey = self.getVerseKey( groupCode )
                if Globals.debugFlag: assert( isinstance( groupVerseKey, SimpleVerseKey ) )
                for appWin in self.appWins:
                    if 'Bible' in appWin.genericWindowType:
                        if appWin.groupCode == groupCode:
                            appWin.updateShownBCV( groupVerseKey )
        self.updateBCVGroup( self.currentVerseKeyGroup ) # Does a acceptNewBCV

        if Globals.debugFlag: self.setDebugText( "__init__ finished." )
        self.setReadyStatus()
    # end of Application.__init__


    def getVerseKey( self, groupCode ):
        assert( groupCode in BIBLE_GROUP_CODES )
        if   groupCode == 'A': return self.GroupA_VerseKey
        elif groupCode == 'B': return self.GroupB_VerseKey
        elif groupCode == 'C': return self.GroupC_VerseKey
        elif groupCode == 'D': return self.GroupD_VerseKey
        else: halt
    # end of Application.getVerseKey
    
       
    def notWrittenYet( self ):
        showerror( _("Not implemented"), _("Not yet available, sorry") )
    # end of Application.notWrittenYet


    def doHelp( self ):
        from Help import HelpBox
        hb = HelpBox( self.ApplicationParent, ProgName, ProgNameVersion )
    # end of Application.doHelp


    def doAbout( self ):
        from About import AboutBox
        ab = AboutBox( self.ApplicationParent, ProgName, ProgNameVersion )
    # end of Application.doAbout


    def createMenuBar( self ):
        """
        """
        if Globals.debugFlag and debuggingThisModule: print( t("createMenuBar()") )

        #self.win = Toplevel( self )
        self.menubar = Menu( self.ApplicationParent )
        #self.ApplicationParent['menu'] = self.menubar
        self.ApplicationParent.config( menu=self.menubar ) # alternative

        fileMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        #fileMenu.add_command( label='New...', underline=0, command=self.notWrittenYet )
        fileNewSubmenu = Menu( fileMenu, tearoff=False )
        fileMenu.add_cascade( label='New', underline=0, menu=fileNewSubmenu )
        fileNewSubmenu.add_command( label='Text file', underline=0, command=self.onOpenNewTextEditWindow )
        fileOpenSubmenu = Menu( fileMenu, tearoff=False )
        fileMenu.add_cascade( label='Open', underline=0, menu=fileOpenSubmenu )
        fileOpenSubmenu.add_command( label='Text file...', underline=0, command=self.onOpenFileTextEditWindow )
        fileMenu.add_separator()
        fileMenu.add_command( label='Save all...', underline=0, command=self.notWrittenYet )
        #subfileMenuImport = Menu( fileMenu )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #subfileMenuExport = Menu( fileMenu )
        #subfileMenuExport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label='HTML', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Export', underline=0, menu=subfileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label='Quit app', underline=0, command=self.closeMe ) # quit app

        #editMenu = Menu( self.menubar )
        #self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        #editMenu.add_command( label='Find...', underline=0, command=self.notWrittenYet )
        #editMenu.add_command( label='Replace...', underline=0, command=self.notWrittenYet )

        gotoMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        gotoMenu.add_command( label='Previous book', underline=0, command=self.gotoPreviousBook )
        gotoMenu.add_command( label='Next book', underline=0, command=self.gotoNextBook )
        gotoMenu.add_command( label='Previous chapter', underline=0, command=self.gotoPreviousChapter )
        gotoMenu.add_command( label='Next chapter', underline=0, command=self.gotoNextChapter )
        gotoMenu.add_command( label='Previous verse', underline=0, command=self.gotoPreviousVerse )
        gotoMenu.add_command( label='Next verse', underline=0, command=self.gotoNextVerse )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Forward', underline=0, command=self.goForward )
        gotoMenu.add_command( label='Backward', underline=0, command=self.goBackward )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Previous list item', underline=0, command=self.gotoPreviousListItem )
        gotoMenu.add_command( label='Next list item', underline=0, command=self.gotoNextListItem )
        gotoMenu.add_separator()
        gotoMenu.add_command( label='Book', underline=0, command=self.gotoBook )

        projectMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=projectMenu, label='Project', underline=0 )
        projectMenu.add_command( label='New...', underline=0, command=self.notWrittenYet )
        #submenuNewType = Menu( resourcesMenu, tearoff=False )
        #projectMenu.add_cascade( label='New...', underline=5, menu=submenuNewType )
        #submenuNewType.add_command( label='Text file...', underline=0, command=self.onOpenNewTextEditWindow )
        #projectMenu.add_command( label='Open', underline=0, command=self.notWrittenYet )
        submenuProjectOpenType = Menu( projectMenu, tearoff=False )
        projectMenu.add_cascade( label='Open', underline=0, menu=submenuProjectOpenType )
        submenuProjectOpenType.add_command( label='Biblelator...', underline=0, command=self.onOpenBiblelatorProject )
        submenuProjectOpenType.add_command( label='Bibledit...', underline=0, command=self.onOpenBibleditProject )
        submenuProjectOpenType.add_command( label='Paratext...', underline=0, command=self.onOpenParatextProject )
        projectMenu.add_separator()
        projectMenu.add_command( label='Backup...', underline=0, command=self.notWrittenYet )
        projectMenu.add_command( label='Restore...', underline=0, command=self.notWrittenYet )
        projectMenu.add_separator()
        projectMenu.add_command( label='Close', underline=0, command=self.onProjectClose )

        resourcesMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=resourcesMenu, label='Resources', underline=0 )
        submenuBibleResourceType = Menu( resourcesMenu, tearoff=False )
        resourcesMenu.add_cascade( label='Open Bible/commentary', underline=5, menu=submenuBibleResourceType )
        submenuBibleResourceType.add_command( label='Online (DBP)...', underline=0, command=self.onOpenDBPBibleResource )
        submenuBibleResourceType.add_command( label='Sword module...', underline=0, command=self.onOpenSwordResource )
        submenuBibleResourceType.add_command( label='Other (local)...', underline=1, command=self.onOpenInternalBibleResource )
        submenuLexiconResourceType = Menu( resourcesMenu, tearoff=False )
        resourcesMenu.add_cascade( label='Open lexicon', menu=submenuLexiconResourceType )
        #submenuLexiconResourceType.add_command( label='Hebrew...', underline=5, command=self.notWrittenYet )
        #submenuLexiconResourceType.add_command( label='Greek...', underline=0, command=self.notWrittenYet )
        submenuLexiconResourceType.add_command( label='Bible', underline=0, command=self.onOpenBibleLexiconResource )
        #submenuCommentaryResourceType = Menu( resourcesMenu )
        #resourcesMenu.add_cascade( label='Open commentary', underline=5, menu=submenuCommentaryResourceType )
        resourcesMenu.add_command( label='Open resource collection...', underline=5, command=self.notWrittenYet )
        resourcesMenu.add_separator()
        resourcesMenu.add_command( label='Hide all resources', underline=0, command=self.onHideResources )

        toolsMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Search files...', underline=0, command=self.onGrep )
        toolsMenu.add_separator()
        toolsMenu.add_command( label='Checks...', underline=0, command=self.notWrittenYet )
        toolsMenu.add_separator()
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Hide resources', underline=0, command=self.onHideResources )
        windowMenu.add_command( label='Hide all', underline=1, command=self.onHideAll )
        windowMenu.add_command( label='Show all', underline=0, command=self.onShowAll )
        windowMenu.add_command( label='Bring all here', underline=0, command=self.onBringAll )
        windowMenu.add_separator()
        windowMenu.add_command( label='Save window setup', underline=0, command=self.saveNewWindowSetup )
        if len(self.windowsSettingsDict)>1 or (self.windowsSettingsDict and 'Current' not in self.windowsSettingsDict):
            windowMenu.add_command( label='Delete a window setting', underline=0, command=self.deleteExistingWindowSetup )
            windowMenu.add_separator()
            for savedName in self.windowsSettingsDict:
                if savedName != 'Current':
                    windowMenu.add_command( label=savedName, underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        submenuWindowStyle = Menu( windowMenu )
        windowMenu.add_cascade( label='Theme', underline=0, menu=submenuWindowStyle )
        for themeName in self.style.theme_names():
            submenuWindowStyle.add_command( label=themeName.title(), underline=0, command=lambda tN=themeName: self.changeTheme(tN) )

        if Globals.debugFlag:
            debugMenu = Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=debugMenu, label='Debug', underline=0 )
            debugMenu.add_command( label='View log...', underline=0, command=self.notWrittenYet )
            debugMenu.add_separator()
            debugMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        helpMenu = Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label='Help', underline=0 )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout )

        #filename = filedialog.askopenfilename()
        #filename = filedialog.asksaveasfilename()
        #dirname = filedialog.askdirectory()
        #colorchooser.askcolor(initialcolor='#ff0000')
        #messagebox.showinfo(message='Have a good day')
        #messagebox.askyesno( message='Are you sure you want to install SuperVirus?' icon='question' title='Install' )
    # end of Application.createMenuBar


    def createNavigationBar( self ):
        """
        """
        if Globals.debugFlag and debuggingThisModule: print( t("createNavigationBar()") )
        Style().configure('NavigationBar.TFrame', background='yellow')
        #self.label1 = Label( self, text="My label" )
        #self.label1.pack()

        navigationBar = Frame( self, cursor='hand2', relief=RAISED, style='NavigationBar.TFrame' )

        self.previousBCVButton = Button( navigationBar, width=4, text='<-', command=self.goBack, state=DISABLED )
        #self.previousBCVButton['text'] = '<-'
        #self.previousBCVButton['command'] = self.goBack
        #self.previousBCVButton.grid( row=0, column=0 )
        self.previousBCVButton.pack( side=LEFT )

        self.nextBCVButton = Button( navigationBar, width=4, text='->', command=self.goForward, state=DISABLED )
        #self.nextBCVButton['text'] = '->'
        #self.nextBCVButton['command'] = self.goForward
        #self.nextBCVButton.grid( row=0, column=1 )
        self.nextBCVButton.pack( side=LEFT )

        self.GroupAButton = Button( navigationBar, width=2, text='A', command=self.selectGroupA, state=DISABLED )
        self.GroupBButton = Button( navigationBar, width=2, text='B', command=self.selectGroupB, state=DISABLED )
        self.GroupCButton = Button( navigationBar, width=2, text='C', command=self.selectGroupC, state=DISABLED )
        self.GroupDButton = Button( navigationBar, width=2, text='D', command=self.selectGroupD, state=DISABLED )
        #self.GroupAButton.grid( row=0, column=2 )
        #self.GroupBButton.grid( row=0, column=3 )
        #self.GroupCButton.grid( row=1, column=2 )
        #self.GroupDButton.grid( row=1, column=3 )
        self.GroupAButton.pack( side=LEFT )
        self.GroupBButton.pack( side=LEFT )
        self.GroupCButton.pack( side=LEFT )
        self.GroupDButton.pack( side=LEFT )

        self.bookNames = [self.genericBibleOrganisationalSystem.getBookName(BBB) for BBB in self.genericBibleOrganisationalSystem.getBookList()]
        bookName = self.bookNames[0] # Default to Genesis usually
        self.bookNameVar = StringVar()
        self.bookNameVar.set( bookName )
        self.BBB = self.genericBibleOrganisationalSystem.getBBB( bookName )
        self.bookNameBox = Combobox( navigationBar, textvariable=self.bookNameVar )
        self.bookNameBox['values'] = self.bookNames
        self.bookNameBox['width'] = len( 'Deuteronomy' )
        self.bookNameBox.bind('<<ComboboxSelected>>', self.gotoNewBook )
        #self.bookNameBox.grid( row=0, column=4 )
        self.bookNameBox.pack( side=LEFT )

        self.chapterNumberVar = StringVar()
        self.chapterNumberVar.set( '1' )
        self.maxChapters = self.genericBibleOrganisationalSystem.getNumChapters( self.BBB )
        #print( "maxChapters", self.maxChapters )
        self.chapterSpinbox = Spinbox( navigationBar, from_=0.0, to=self.maxChapters, textvariable=self.chapterNumberVar )
        self.chapterSpinbox['width'] = 3
        self.chapterSpinbox['command'] = self.acceptNewBCV
        self.chapterSpinbox.bind( '<Return>', self.gotoNewChapter )
        #self.chapterSpinbox.grid( row=0, column=5 )
        self.chapterSpinbox.pack( side=LEFT )

        #self.chapterNumberVar = StringVar()
        #self.chapterNumberVar.set( '1' )
        #self.chapterNumberBox = Entry( self, textvariable=self.chapterNumberVar )
        #self.chapterNumberBox['width'] = 3
        #self.chapterNumberBox.pack()

        self.verseNumberVar = StringVar()
        self.verseNumberVar.set( '1' )
        #self.maxVersesVar = StringVar()
        self.maxVerses = self.genericBibleOrganisationalSystem.getNumVerses( self.BBB, self.chapterNumberVar.get() )
        #print( "maxVerses", self.maxVerses )
        #self.maxVersesVar.set( str(self.maxVerses) )
        # Add 1 to maxVerses to enable them to go to the next chapter
        self.verseSpinbox = Spinbox( navigationBar, from_=0.0, to=1.0+self.maxVerses, textvariable=self.verseNumberVar )
        self.verseSpinbox['width'] = 3
        self.verseSpinbox['command'] = self.acceptNewBCV
        self.verseSpinbox.bind( '<Return>', self.acceptNewBCV )
        self.verseSpinbox.pack( side=LEFT )

        #self.verseNumberVar = StringVar()
        #self.verseNumberVar.set( '1' )
        #self.verseNumberBox = Entry( self, textvariable=self.verseNumberVar )
        #self.verseNumberBox['width'] = 3
        #self.verseNumberBox.pack()

        self.wordVar = StringVar()
        self.wordBox = Entry( navigationBar, textvariable=self.wordVar )
        self.wordBox['width'] = 12
        self.wordBox.bind( '<Return>', self.acceptNewWord )
        self.wordBox.pack( side=LEFT )

        if 0: # I don't think we should need this button if everything else works right
            self.updateButton = Button( navigationBar )
            self.updateButton['text'] = 'Update'
            self.updateButton['command'] = self.acceptNewBCV
            #self.updateButton.grid( row=0, column=7 )
            self.updateButton.pack( side=LEFT )

        Style( self ).map("Quit.TButton", foreground=[('pressed', 'red'), ('active', 'blue')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )
        self.quitButton = Button( navigationBar, text="QUIT", style="Quit.TButton", command=self.closeMe )
        self.quitButton.pack( side=RIGHT )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
        navigationBar.pack( side=TOP, fill=X )
    # end of Application.createNavigationBar


    def createToolBar( self ):
        """
        Create a tool bar containing several buttons at the top of the main window.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("createToolBar()") )

        Style().configure('ToolBar.TFrame', background='green')

        toolbar = Frame( self, cursor='hand2', relief=RAISED, style='ToolBar.TFrame' )
        Button( toolbar, text='Hide Resources', command=self.onHideResources ).pack( side=LEFT, padx=2, pady=2 )
        Button( toolbar, text='Hide All', command=self.onHideAll ).pack( side=LEFT, padx=2, pady=2 )
        Button( toolbar, text='Show All', command=self.onShowAll ).pack( side=LEFT, padx=2, pady=2 )
        Button( toolbar, text='Bring All', command=self.onBringAll ).pack( side=LEFT, padx=2, pady=2 )
        toolbar.pack( side=TOP, fill=X )
    # end of Application.createToolBar


    def createDebugToolBar( self ):
        """
        Create a debug tool bar containing several additional buttons at the top of the main window.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("createDebugToolBar()") )
        Style().configure( 'DebugToolBar.TFrame', background='red' )
        Style().map("Halt.TButton", foreground=[('pressed', 'red'), ('active', 'yellow')],
                                            background=[('pressed', '!disabled', 'black'), ('active', 'pink')] )

        toolbar = Frame( self, cursor='hand2', relief=RAISED, style='DebugToolBar.TFrame' )
        Button( toolbar, text='Halt', style='Halt.TButton', command=self.quit ).pack( side=RIGHT, padx=2, pady=2 )
        toolbar.pack( side=TOP, fill=X )
    # end of Application.createDebugToolBar


    def createStatusBar( self ):
        """
        Create a status bar containing only one text label at the bottom of the main window.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("createStatusBar()") )
        Style().configure( 'StatusBar.TLabel', background='blue' )

        self.statusTextVariable=StringVar()
        self.statusTextLabel = Label( self.ApplicationParent, relief=SUNKEN,
                                    textvariable=self.statusTextVariable, style='StatusBar.TLabel' )
                                    #, font=('arial',16,NORMAL) )
        self.statusTextLabel.pack( side=BOTTOM, fill=X )
        self.statusTextVariable.set( '' ) # first initial value
        self.setStatus( "Starting up..." )
    # end of Application.createStatusBar


    def setStatus( self, newStatus=None ):
        """
        Set (or clear) the status bar text.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("setStatus( {} )").format( repr(newStatus) ) )
        #print( "SB is", repr( self.statusTextVariable.get() ) )
        if newStatus != self.statusTextVariable.get(): # it's changed
            #self.statusBarTextWidget['state'] = NORMAL
            #self.statusBarTextWidget.delete( '1.0', END )
            #if newStatus:
                #self.statusBarTextWidget.insert( '1.0', newStatus )
            #self.statusBarTextWidget['state'] = DISABLED # Don't allow editing
            #self.statusText = newStatus
            self.statusTextVariable.set( newStatus )
            self.statusTextLabel.update()
    # end of Application.setStatus

    def setReadyStatus( self ):
        self.setStatus( _("Ready") )

        
    def setDebugText( self, newMessage=None ):
        """
        """
        from tkinter import END
        print( t("setDebugText( {} )").format( repr(newMessage) ) )
        assert( Globals.debugFlag )
        self.debugTextBox['state'] = NORMAL # Allow editing
        self.debugTextBox.delete( '1.0', END ) # Clear everything
        self.debugTextBox.insert( END, 'DEBUGGING INFORMATION:' )
        if self.lastDebugMessage: self.debugTextBox.insert( END, '\nWas: ' + self.lastDebugMessage )
        if newMessage:
            self.debugTextBox.insert( END, '\n' )
            self.debugTextBox.insert( END, 'Msg: ' + newMessage, 'emp' )
            self.lastDebugMessage = newMessage
        self.debugTextBox.insert( END, '\n\n{} child windows:'.format( len(self.appWins) ) )
        for j, appWin in enumerate( self.appWins ):
            self.debugTextBox.insert( END, "\n  {} {} ({}) {} {}" \
                                    .format( j, appWin.winType.replace('ResourceWindow',''),
                                        appWin.genericWindowType.replace('Resource',''),
                                        appWin.geometry(), appWin.moduleID ) )
        #self.debugTextBox.insert( END, '\n{} resource frames:'.format( len(self.appWins) ) )
        #for j, projFrame in enumerate( self.appWins ):
            #self.debugTextBox.insert( END, "\n  {} {}".format( j, projFrame ) )
        self.debugTextBox['state'] = DISABLED # Don't allow editing
    # end of Application.setDebugText


    def changeTheme( self, newThemeName ):
        """
        Set the window theme to the given scheme.
        """
        if Globals.debugFlag:
            print( t("changeTheme( {} )").format( repr(newThemeName) ) )
            assert( newThemeName )
            self.setDebugText( 'Set theme to {}'.format( repr(newThemeName) ) )
        self.themeName = newThemeName
        try:
            self.style.theme_use( newThemeName )
        except TclError as err:
            showerror( 'Error', err )
    # end of Application.changeTheme


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
            if Globals.debugFlag:
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


        if Globals.debugFlag:
            print( t("parseAndApplySettings()") )
            self.setDebugText( "parseAndApplySettings..." )
        try: self.minimumXSize, self.minimumYSize = self.settings.data[ProgName]['minimumXSize'], self.settings.data[ProgName]['minimumYSize']
        except KeyError: self.minimumXSize, self.minimumYSize = MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE
        self.ApplicationParent.minsize( self.minimumXSize, self.minimumYSize )
        try: self.ApplicationParent.geometry( self.settings.data[ProgName]['windowGeometry'] )
        except KeyError: print( "KeyError1" ) # we had no geometry set
        except TclError: logging.critical( t("Application.__init__: Bad window geometry in settings file: {}").format( settings.data[ProgName]['windowGeometry'] ) )
        try: self.changeTheme( self.settings.data[ProgName]['themeName'] )
        except KeyError: print( "KeyError2" ) # we had no theme name set

        try: self.currentVerseKeyGroup = self.settings.data['BCVGroups']['currentGroup']
        except KeyError: self.currentVerseKeyGroup = 'A'
        try: self.GroupA_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['A-Book'],self.settings.data['BCVGroups']['A-Chapter'],self.settings.data['BCVGroups']['A-Verse'])
        except KeyError: self.GroupA_VerseKey = SimpleVerseKey( self.genericBibleOrganisationalSystem.getFirstBookCode(), '1', '1' )
        try: self.GroupB_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['B-Book'],self.settings.data['BCVGroups']['B-Chapter'],self.settings.data['BCVGroups']['B-Verse'])
        except KeyError: self.GroupB_VerseKey = SimpleVerseKey( self.genericBibleOrganisationalSystem.getFirstBookCode(), '1', '1' )
        try: self.GroupC_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['C-Book'],self.settings.data['BCVGroups']['C-Chapter'],self.settings.data['BCVGroups']['C-Verse'])
        except KeyError: self.GroupC_VerseKey = SimpleVerseKey( self.genericBibleOrganisationalSystem.getFirstBookCode(), '1', '1' )
        try: self.GroupD_VerseKey = SimpleVerseKey(self.settings.data['BCVGroups']['D-Book'],self.settings.data['BCVGroups']['D-Chapter'],self.settings.data['BCVGroups']['D-Verse'])
        except KeyError: self.GroupD_VerseKey = SimpleVerseKey( self.genericBibleOrganisationalSystem.getFirstBookCode(), '1', '1' )

        # We keep our copy of all the windows settings in self.windowsSettingsDict
        windowsSettingsNamesList = []
        for name in self.settings.data:
            if name.startswith( 'WindowSetting' ): windowsSettingsNamesList.append( name[13:] )
        if Globals.debugFlag: print( t("Available windows settings are: {}").format( windowsSettingsNamesList ) )
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
        if Globals.debugFlag:
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
                    rw = self.onOpenNewTextEditWindow()
                    #except: logging.error( "Unable to read TextEditWindow {} settings".format( j ) )
                elif winType == 'USFMBibleEditWindow':
                    rw = self.openUSFMBibleEditWindow( thisStuff['USFMFolder'], thisStuff['EditMode'], windowGeometry )
                    #except: logging.error( "Unable to read USFMBibleEditWindow {} settings".format( j ) )
                elif winType == 'ESFMEditWindow':
                    rw = self.openESFMEditWindow( thisStuff['ESFMFolder'], thisStuff['EditMode'], windowGeometry )
                    #except: logging.error( "Unable to read ESFMEditWindow {} settings".format( j ) )

                else:
                    logging.critical( t("Application.__init__: Unknown {} window type").format( repr(winType) ) )
                    if Globals.debugFlag: halt

                groupCode = thisStuff['GroupCode'] if 'GroupCode' in thisStuff else None
                if groupCode:
                    if Globals.debugFlag: assert( groupCode in BIBLE_GROUP_CODES )
                    rw.groupCode = groupCode
                contextViewMode = thisStuff['ContextViewMode'] if 'ContextViewMode' in thisStuff else None
                if contextViewMode:
                    if Globals.debugFlag: assert( contextViewMode in BIBLE_CONTEXT_VIEW_MODES )
                    rw.contextViewMode = contextViewMode
                    rw.createMenuBar()
    # end of Application.applyGivenWindowsSettings


    def getCurrentWindowSettings( self ):
        """
        Go through the currently open windows and get their settings data
            and save it in self.windowsSettingsDict['Current'].
        """
        if Globals.debugFlag and debuggingThisModule: print( t("getCurrentWindowSettings()") )
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
                    if Globals.debugFlag: halt
                    
                if appWin.genericWindowType == 'BibleResource':
                    try: thisOne['GroupCode'] = appWin.groupCode
                    except AttributeError: logging.critical( t("getCurrentWindowSettings: Why no groupCode in {}").format( appWin.winType ) )
                    try: thisOne['ContextViewMode'] = appWin.contextViewMode
                    except AttributeError: logging.critical( t("getCurrentWindowSettings: Why no contextViewMode in {}").format( appWin.winType ) )
    # end of Application.getCurrentWindowSettings


    def saveNewWindowSetup( self ):
        """
        Gets the name for the new window setup and saves the information.
        """
        if Globals.debugFlag:
            print( t("saveNewWindowSetup()") )
            self.setDebugText( "saveNewWindowSetup..." )
        swnd = SaveWindowNameDialog( self, self.windowsSettingsDict, title=_("Save window setup") )
        print( "swndResult", repr(swnd.result) )
        if swnd.result:
            self.getCurrentWindowSettings()
            self.windowsSettingsDict[swnd.result] = self.windowsSettingsDict['Current'] # swnd.result is the new window name
            print( "swS", self.windowsSettingsDict )
            self.writeSettingsFile() # Save file now in case we crash
            self.createMenuBar() # refresh
    # end of Application.saveNewWindowSetup


    def deleteExistingWindowSetup( self ):
        """
        Gets the name of an existing window setting and deletes the setting.
        """
        if Globals.debugFlag:
            print( t("deleteExistingWindowSetup()") )
            self.setDebugText( "deleteExistingWindowSetup..." )
        assert( self.windowsSettingsDict and (len(self.windowsSettingsDict)>1 or 'Current' not in self.windowsSettingsDict) )
        dwnd = DeleteWindowNameDialog( self, self.windowsSettingsDict, title=_("Delete saved window setup") )
        print( "dwndResult", repr(dwnd.result) )
        if dwnd.result:
            if Globals.debugFlag:
                assert( dwnd.result in self.windowsSettingsDict )
            del self.windowsSettingsDict[dwnd.result]
            #self.settings.save() # Save file now in case we crash -- don't worry -- it's easy to delete one
            self.createMenuBar() # refresh
    # end of Application.deleteExistingWindowSetup


    def onOpenDBPBibleResource( self ):
        """
        Open an online DigitalBiblePlatform Bible (called from a menu/GUI action).

        Requests a version name from the user.
        """
        if Globals.debugFlag:
            print( t("onOpenDBPBibleResource()") )
            self.setDebugText( "onOpenDBPBibleResource..." )
        self.setStatus( "onOpenDBPBibleResource..." )
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
                    #self.acceptNewBCV()
                    #self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
                elif Globals.debugFlag: print( t("onOpenDBPBibleResource: no resource selected!") )
            else:
                logging.critical( t("onOpenDBPBibleResource: no volumes available") )
                self.setStatus( "Digital Bible Platform unavailable (offline?)" )
        if Globals.debugFlag: self.setDebugText( "Finished onOpenDBPBibleResource" )
    # end of Application.onOpenDBPBibleResource

    def openDBPBibleResourceWindow( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested DBP Bible resource window.

        Returns the new DBPBibleResourceWindow object.
        """
        if Globals.debugFlag:
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
        if Globals.debugFlag: self.setDebugText( "Finished openDPBBibleResourceWindow" )
        self.setReadyStatus()
        return dBRW
    # end of Application.openDBPBibleResourceWindow


    def onOpenSwordResource( self ):
        """
        Open a local Sword Bible (called from a menu/GUI action).

        Requests a module abbreviation from the user.
        """
        if Globals.debugFlag:
            print( t("openSwordResource()") )
            self.setDebugText( "onOpenSwordResource..." )
        self.setStatus( "onOpenSwordResource..." )
        if self.SwordInterface is None:
            self.SwordInterface = SwordResources.SwordInterface() # Load the Sword library
        availableModules = self.SwordInterface.library
        #print( "aM1", availableModules )
        if availableModules is not None:
            ourList = availableModules.getAvailableModuleCodes()
            #print( "ourList", ourList )
            srb = SelectResourceBox( self, ourList, title=_("Open Sword resource") )
            #print( "srbResult", repr(srb.result) )
            if srb.result:
                for entry in srb.result:
                    self.setStatus( _("Loading {} Sword module...").format( repr(entry) ) )
                    self.openSwordBibleResourceWindow( entry )
                #self.acceptNewBCV()
                #self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
            elif Globals.debugFlag: print( t("onOpenSwordResource: no resource selected!") )
        else: logging.critical( t("onOpenSwordResource: no volumes available") )
        #self.acceptNewBCV()
        #self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
    # end of Application.onOpenSwordResource

    def openSwordBibleResourceWindow( self, moduleAbbreviation, windowGeometry=None ):
        """
        Create the actual requested Sword Bible resource window.

        Returns the new SwordBibleResourceWindow object.
        """
        if Globals.debugFlag:
            print( t("openSwordBibleResourceWindow()") )
            self.setDebugText( "openSwordBibleResourceWindow..." )
        if self.SwordInterface is None:
            self.SwordInterface = SwordResources.SwordInterface() # Load the Sword library
        swBRW = SwordBibleResourceWindow( self, moduleAbbreviation )
        if windowGeometry: swBRW.geometry( windowGeometry )
        self.appWins.append( swBRW )
        swBRW.updateShownBCV( self.getVerseKey( swBRW.groupCode ) )
        if Globals.debugFlag: self.setDebugText( "Finished openSwordBibleResourceWindow" )
        self.setReadyStatus()
        return swBRW
    # end of Application.openSwordBibleResourceWindow


    def onOpenInternalBibleResource( self ):
        """
        Open a local Bible (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if Globals.debugFlag:
            print( t("openInternalBibleResource()") )
            self.setDebugText( "onOpenInternalBibleResource..." )
        self.setStatus( "onOpenInternalBibleResource..." )
        #requestedFolder = askdirectory()
        self.openDialog = Directory( initialdir=self.lastInternalBibleDir )
        requestedFolder = self.openDialog.show()
        if requestedFolder:
            self.lastInternalBibleDir = requestedFolder
            self.openInternalBibleResourceWindow( requestedFolder )
            #self.acceptNewBCV()
            #self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
    # end of Application.onOpenInternalBibleResource

    def openInternalBibleResourceWindow( self, modulePath, windowGeometry=None ):
        """
        Create the actual requested local/internal Bible resource window.
        
        Returns the new InternalBibleResourceWindow object.
        """
        if Globals.debugFlag:
            print( t("openInternalBibleResourceWindow()") )
            self.setDebugText( "openInternalBibleResourceWindow..." )
        iBRW = InternalBibleResourceWindow( self, modulePath )
        if windowGeometry: iBRW.geometry( windowGeometry )
        self.appWins.append( iBRW )
        if iBRW.internalBible is None:
            logging.critical( t("Application.openInternalBibleResourceWindow: Unable to open resource {}").format( repr(modulePath) ) )
            iBRW.destroy()
        else: iBRW.updateShownBCV( self.getVerseKey( iBRW.groupCode ) )
        if Globals.debugFlag: self.setDebugText( "Finished openInternalBibleResourceWindow" )
        self.setReadyStatus()
        return iBRW
    # end of Application.openInternalBibleResourceWindow


    def onOpenBibleLexiconResource( self ):
        """
        Open a local Bible (called from a menu/GUI action).

        Requests a folder from the user.
        """
        if Globals.debugFlag:
            print( t("onOpenBibleLexiconResource()") )
            self.setDebugText( "onOpenBibleLexiconResource..." )
        self.setStatus( "onOpenBibleLexiconResource..." )
        #requestedFolder = askdirectory()
        #if requestedFolder:
        requestedFolder = None
        self.openBibleLexiconResourceWindow( requestedFolder )
        #self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
    # end of Application.onOpenBibleLexiconResource

    def openBibleLexiconResourceWindow( self, lexiconPath, windowGeometry=None ):
        """
        
        Returns the new BibleLexiconResourceWindow object.
        """
        if Globals.debugFlag:
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
        if Globals.debugFlag: self.setDebugText( "Finished openBibleLexiconResourceWindow" )
        self.setReadyStatus()
        return bLRW
    # end of Application.openBibleLexiconResourceWindow


    def onOpenNewTextEditWindow( self ):
        """
        """
        if Globals.debugFlag:
            print( t("onOpenNewTextEditWindow()") )
            self.setDebugText( "onOpenNewTextEditWindow..." )
        tEW = TextEditWindow( self )
        #if windowGeometry: tEW.geometry( windowGeometry )
        self.appWins.append( tEW )
        if Globals.debugFlag: self.setDebugText( "Finished onOpenNewTextEditWindow" )
        self.setReadyStatus()
    # end of Application.onOpenNewTextEditWindow


    def onOpenFileTextEditWindow( self ):
        """
        Open a pop-up window and request the user to select a file.

        Then open the file in a plain text edit window.
        """
        if Globals.debugFlag:
            print( t("onOpenFileTextEditWindow()") )
            self.setDebugText( "onOpenFileTextEditWindow..." )
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
        if Globals.debugFlag: self.setDebugText( "Finished onOpenFileTextEditWindow" )
        self.setReadyStatus()
    # end of Application.onOpenFileTextEditWindow


    def openUSFMBibleEditWindow( self, USFMFolder, editMode, windowGeometry=None ):
        """
        
        Returns the new USFMEditWindow object.
        """
        if Globals.debugFlag:
            print( t("openUSFMBibleEditWindow()") )
            self.setDebugText( "openUSFMBibleEditWindow..." )
        uEW = USFMEditWindow( self, USFMFolder, editMode )
        if windowGeometry: uEW.geometry( windowGeometry )
        self.appWins.append( uEW )
        if uEW.InternalBible is None:
            logging.critical( t("Application.openUSFMBibleEditWindow: Unable to open USFM Bible in {}").format( repr(USFMFolder) ) )
            #uEW.destroy()
        if Globals.debugFlag: self.setDebugText( "Finished openUSFMBibleEditWindow" )
        self.setReadyStatus()
        return uEW
    # end of Application.openUSFMBibleEditWindow


    def goBack( self, event=None ):
        if Globals.debugFlag:
            print( t("goBack()") )
            self.setDebugText( "goBack..." )
        #print( dir(event) )
        assert( self.BCVHistory )
        assert( self.BCVHistoryIndex )
        self.BCVHistoryIndex -= 1
        assert( self.BCVHistoryIndex >= 0)
        self.setCurrentVerseKey( self.BCVHistory[self.BCVHistoryIndex] )
        self.updatePreviousNextButtons()
        #self.acceptNewBCV()
        self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
    # end of Application.goBack


    def goForward( self, event=None ):
        if Globals.debugFlag and debuggingThisModule: print( t("goForward") )
        #print( dir(event) )
        assert( self.BCVHistory )
        assert( self.BCVHistoryIndex < len(self.BCVHistory)-1 )
        self.BCVHistoryIndex += 1
        assert( self.BCVHistoryIndex < len(self.BCVHistory) )
        self.setCurrentVerseKey( self.BCVHistory[self.BCVHistoryIndex] )
        self.updatePreviousNextButtons()
        #self.acceptNewBCV()
        self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
    # end of Application.goForward


    def setCurrentVerseKey( self, newVerseKey ):
        """
        """
        if Globals.debugFlag and debuggingThisModule:
            print( t("setCurrentVerseKey( {} )").format( newVerseKey ) )
            self.setDebugText( "setCurrentVerseKey..." )
            assert( isinstance( newVerseKey, SimpleVerseKey ) )
        self.currentVerseKey = newVerseKey
        if   self.currentVerseKeyGroup == 'A': self.GroupA_VerseKey = self.currentVerseKey
        elif self.currentVerseKeyGroup == 'B': self.GroupB_VerseKey = self.currentVerseKey
        elif self.currentVerseKeyGroup == 'C': self.GroupC_VerseKey = self.currentVerseKey
        elif self.currentVerseKeyGroup == 'D': self.GroupD_VerseKey = self.currentVerseKey
        else: halt
        self.bookNameVar.set( self.genericBibleOrganisationalSystem.getBookName(self.currentVerseKey[0]) )
        self.chapterNumberVar.set( self.currentVerseKey[1] )
        self.verseNumberVar.set( self.currentVerseKey[2] )
        if self.currentVerseKey not in self.BCVHistory:
            self.BCVHistoryIndex = len( self.BCVHistory )
            self.BCVHistory.append( self.currentVerseKey )
            self.updatePreviousNextButtons()
    # end of Application.setCurrentVerseKey


    def updateBCVGroup( self, newGroupLetter ):
        """
        Change the group to the given one (and then do a acceptNewBCV)
        """
        if Globals.debugFlag and debuggingThisModule:
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
            self.setCurrentVerseKey( SimpleVerseKey( self.genericBibleOrganisationalSystem.getFirstBookCode(), '1', '1' ) )
        self.updateBCVGroupButtons()
        #self.acceptNewBCV()
        self.after_idle( self.acceptNewBCV ) # Do the acceptNewBCV once we're idle
    # end of Application.updateBCVGroup


    def updateBCVGroupButtons( self ):
        """
        Updates the display showing the selected group and the selected BCV reference.
        """
        if Globals.debugFlag and debuggingThisModule:
            print( t("updateBCVGroupButtons()") )
            self.setDebugText( "updateBCVGroupButtons..." )
        groupButtons = [ self.GroupAButton, self.GroupBButton, self.GroupCButton, self.GroupDButton ]
        if   self.currentVerseKeyGroup == 'A': ix = 0
        elif self.currentVerseKeyGroup == 'B': ix = 1
        elif self.currentVerseKeyGroup == 'C': ix = 2
        elif self.currentVerseKeyGroup == 'D': ix = 3
        else: halt
        selectedButton = groupButtons.pop( ix )
        selectedButton.config( state=DISABLED )#, relief=SUNKEN )
        for otherButton in groupButtons:
            otherButton.config( state=NORMAL ) #, relief=RAISED )
        self.bookNameVar.set( self.genericBibleOrganisationalSystem.getBookName(self.currentVerseKey[0]) )
        self.chapterNumberVar.set( self.currentVerseKey[1] )
        self.verseNumberVar.set( self.currentVerseKey[2] )
    # end of Application.updateBCVGroupButtons


    def updatePreviousNextButtons( self ):
        """
        Updates the display showing the previous/next buttons as enabled or disabled.
        """
        if Globals.debugFlag:
            print( t("updatePreviousNextButtons()") )
            self.setDebugText( "updatePreviousNextButtons..." )
        self.previousBCVButton.config( state=NORMAL if self.BCVHistory and self.BCVHistoryIndex>0 else DISABLED )
        self.nextBCVButton.config( state=NORMAL if self.BCVHistory and self.BCVHistoryIndex<len(self.BCVHistory)-1 else DISABLED )
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


    def gotoPreviousBook( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoPreviousBook() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoPreviousBook..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoPreviousBook() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoPreviousBook..." )
    # end of Application.gotoPreviousBook


    def gotoNextBook( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoNextBook() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoNextBook..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoNextBook() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoNextBook..." )
        intC, intV = int( c ), int( v )
        intC += 1
        self.gotoBCV( b, c, v )
    # end of Application.gotoNextBook


    def gotoPreviousChapter( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoPreviousChapter() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoPreviousChapter..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoPreviousChapter() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoPreviousChapter..." )
        intC, intV = int( c ), int( v )
        if intC > 0:
            intC -= 1
            self.gotoBCV( b, intC, v )
    # end of Application.gotoPreviousChapter


    def gotoNextChapter( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoNextChapter() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoNextChapter..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoNextChapter() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoNextChapter..." )
        intC, intV = int( c ), int( v )
        intC += 1
        self.gotoBCV( b, intC, v )
    # end of Application.gotoNextChapter


    def gotoPreviousVerse( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoPreviousVerse() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoPreviousVerse..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoPreviousVerse() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoPreviousVerse..." )
        intC, intV = int( c ), int( v )
        if intV > 0:
            intV -= 1
            self.gotoBCV( b, c, intV )
    # end of Application.gotoPreviousVerse


    def gotoNextVerse( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoNextVerse() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoNextVerse..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoNextVerse() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoNextVerse..." )
        intC, intV = int( c ), int( v )
        intV += 1
        self.gotoBCV( b, c, intV )
    # end of Application.gotoNextVerse


    def goForward( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("goForward() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "goForward..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("goForward() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "goForward..." )
    # end of Application.goForward


    def goBackward( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("goBackward() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "goBackward..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("goBackward() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "goBackward..." )
    # end of Application.goBackward


    def gotoPreviousListItem( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoPreviousListItem() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoPreviousListItem..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoPreviousListItem() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoPreviousListItem..." )
    # end of Application.gotoPreviousListItem


    def gotoNextListItem( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoNextListItem() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoNextListItem..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoNextListItem() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoNextListItem..." )
    # end of Application.gotoNextListItem


    def gotoBook( self ):
        """
        """
        #if Globals.debugFlag:
            #print( t("gotoBook() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            #self.setDebugText( "gotoBook..." )
        b, c, v = self.BnameCV
        if Globals.debugFlag:
            print( t("gotoBook() from {} {}:{}").format( repr(b), repr(c), repr(v) ) )
            self.setDebugText( "gotoBook..." )
    # end of Application.gotoBook


    def gotoNewBook( self, event=None ):
        """
        Handle a new book setting from the GUI.
        """
        if Globals.debugFlag: print( t("gotoNewBook()") )
        #print( dir(event) )

        self.chapterNumberVar.set( '1' )
        self.verseNumberVar.set( '1' )
        self.acceptNewBCV( event )
    # end of Application.gotoNewBook


    def gotoNewChapter( self, event=None ):
        """
        Handle a new chapter setting from the GUI.
        """
        if Globals.debugFlag: print( t("gotoNewChapter()") )
        #print( dir(event) )

        #self.chapterNumberVar.set( '1' )
        self.verseNumberVar.set( '1' )
        self.acceptNewBCV( event )
    # end of Application.gotoNewChapter


    def acceptNewBCV( self, event=None ):
        """
        Handle a new book, chapter, verse setting from the GUI.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("acceptNewBCV()") )
        #print( dir(event) )

        bn = self.bookNameVar.get()
        C = self.chapterNumberVar.get()
        V = self.verseNumberVar.get()
        self.gotoBCV( bn, C, V )
        if Globals.debugFlag: self.setDebugText( "acceptNewBCV {} {}:{}".format( bn, C, V ) )
        self.setReadyStatus()
    # end of Application.acceptNewBCV


    def haveSwordResourcesOpen( self ):
        """
        """
        #if Globals.debugFlag: print( t("haveSwordResourcesOpen()") )
        for appWin in self.appWins:
            if 'Sword' in appWin.winType:
                if self.SwordInterface is None:
                    self.SwordInterface = SwordResources.SwordInterface() # Load the Sword library
                return True
        return False
    # end of Application.haveSwordResourcesOpen


    def gotoBCV( self, bn, C, V ):
        """
        Sets self.BnameCV and self.currentVerseKey (and if necessary, self.SwordKey)
            then calls update on the child windows.
        """
        if Globals.debugFlag: print( t("gotoBCV( {} {}:{} )").format( bn, C, V ) )
        self.BnameCV = (bn,C,V,)
        BBB = self.genericBibleOrganisationalSystem.getBBB( bn )
        #print( "BBB", BBB )
        self.setCurrentVerseKey( SimpleVerseKey( BBB, C, V ) )
        if Globals.debugFlag:
            print( "  BCV", self.BnameCV, self.currentVerseKey )
            assert( self.genericBibleOrganisationalSystem.isValidBCVRef( self.currentVerseKey, repr( self.BnameCV ), extended=True ) )
        if self.haveSwordResourcesOpen():
            self.SwordKey = self.SwordInterface.makeKey( BBB, C, V )
            #print( "swK", self.SwordKey.getText() )
        self.appWins.updateThisBibleGroup( self.currentVerseKeyGroup )
    # end of Application.gotoBCV


    def acceptNewWord( self, event=None ):
        """
        Handle a new lexicon word setting from the GUI.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("acceptNewWord()") )
        #print( dir(event) )

        newWord = self.wordVar.get()
        self.gotoWord( newWord )
        if Globals.debugFlag: self.setDebugText( "acceptNewWord {}".format( newWord ) )
        self.setReadyStatus()
    # end of Application.acceptNewWord


    def gotoWord( self, lexiconWord ):
        """
        Sets self.lexiconWord
            then calls update on the child windows.
        """
        if Globals.debugFlag: print( t("gotoWord( {} )").format( lexiconWord ) )
        assert( lexiconWord is None or isinstance( lexiconWord, str ) )
        self.lexiconWord = lexiconWord
        self.appWins.updateLexicons( lexiconWord )
    # end of Application.gotoWord


    def onHideResources( self ):
        """
        Minimize all of our resource windows,
            i.e., leave the editor and main window
        """
        if Globals.debugFlag: self.setDebugText( 'onHideResources' )
        self.appWins.iconifyResources()
    # end of Application.onHideResources


    def onHideAll( self, includeMe=True ):
        """
        Minimize all of our windows.
        """
        if Globals.debugFlag: self.setDebugText( 'onHideAll' )
        self.appWins.iconify()
        if includeMe: self.ApplicationParent.iconify()
    # end of Application.onHideAll


    def onShowAll( self ):
        """
        Show/restore all of our windows.
        """
        if Globals.debugFlag: self.setDebugText( 'onShowAll' )
        self.appWins.deiconify()
        self.ApplicationParent.deiconify() # Do this last so it has the focus
        self.ApplicationParent.lift()
    # end of Application.onShowAll


    def onBringAll( self ):
        """
        Bring all of our windows close.
        """
        if Globals.debugFlag: self.setDebugText( 'onBringAll' )
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
        self.onShowAll()
    # end of Application.onBringAll


    def onGrep( self ):
        """
        new in version 2.1: threaded external file search;
        search matched filenames in directory tree for string;
        listbox clicks open matched file at line of occurrence;

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
        from tkinter import Toplevel, StringVar, X, RIDGE, SUNKEN
        from tkinter.ttk import Label, Entry, Button
        def makeFormRow( parent, label, width=15, browse=True, extend=False ):
            var = StringVar()
            row = Frame(parent)
            lab = Label( row, text=label + '?', relief=RIDGE, width=width)
            ent = Entry( row, textvariable=var) # relief=SUNKEN
            row.pack( fill=X )                                  # uses packed row frames
            lab.pack( side=LEFT )                               # and fixed-width labels
            ent.pack( side=LEFT, expand=YES, fill=X )           # or use grid(row, col)
            if browse:
                btn = Button( row, text='browse...' )
                btn.pack( side=RIGHT )
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
        from tkinter import Tk
        from tkinter.ttk import Label
        import threading, queue

        # make non-modal un-closeable dialog
        mypopup = Tk()
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
        from tkinter import Tk, Listbox, SUNKEN, Y
        from tkinter.ttk import Scrollbar
        class ScrolledList(Frame):
            def __init__(self, options, parent=None):
                Frame.__init__(self, parent)
                self.pack(expand=YES, fill=BOTH)                   # make me expandable
                self.makeWidgets(options)

            def handleList(self, event):
                index = self.listbox.curselection()                # on list double-click
                label = self.listbox.get(index)                    # fetch selection text
                self.runCommand(label)                             # and call action here
                                                                   # or get(ACTIVE)
            def makeWidgets(self, options):
                sbar = Scrollbar(self)
                list = Listbox(self, relief=SUNKEN)
                sbar.config(command=list.yview)                    # xlink sbar and list
                list.config(yscrollcommand=sbar.set)               # move one moves other
                sbar.pack( side=RIGHT, fill=Y )                      # pack first=clip last
                list.pack( side=LEFT, expand=YES, fill=BOTH )        # list clipped first
                pos = 0
                for label in options:                              # add to listbox
                    list.insert(pos, label)                        # or insert(END,label)
                    pos += 1                                       # or enumerate(options)
               #list.config(selectmode=SINGLE, setgrid=1)          # select,resize modes
                list.bind('<Double-1>', self.handleList)           # set event handler
                self.listbox = list

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


    def onOpenBiblelatorProject( self ):
        """
        """
        if Globals.debugFlag or debuggingThisModule: print( t("onOpenBiblelatorProject()") )
        self.notWrittenYet()
    # end of Application.onOpenBiblelatorProject

        
    def onOpenBibleditProject( self ):
        """
        """
        if Globals.debugFlag or debuggingThisModule: print( t("onOpenBibleditProject()") )
        self.notWrittenYet()
    # end of Application.onOpenBibleditProject

        
    def onOpenParatextProject( self ):
        """
        """
        if Globals.debugFlag or debuggingThisModule:
            print( t("onOpenParatextProject()") )
            self.setDebugText( "onOpenParatextProject..." )
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
        if 'Directory' not in uB.ssfDict:
            showerror( APP_NAME, 'Project {} ({}) has no directory specified'.format( uBName, uBFullName ) )
            return
        #print( "uB1", uB )
        uB.preload( uB.ssfDict['Directory'] )
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
        if Globals.debugFlag: self.setDebugText( "Finished onOpenParatextProject" )
        self.setReadyStatus()
    # end of Application.onOpenParatextProject

        
    def onProjectClose( self ):
        """
        """
        if Globals.debugFlag or debuggingThisModule: print( t("onProjectClose()") )
        self.notWrittenYet()
    # end of Application.onProjectClose

        
    def writeSettingsFile( self ):
        """
        Update our program settings and save them.
        """
        if Globals.debugFlag or debuggingThisModule: print( t("writeSettingsFile()") )
        if Globals.debugFlag: self.setDebugText( 'writeSettingsFile' )
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


        # Get the current window settings
        self.getCurrentWindowSettings()
        # Save all the various window set-ups
        for windowsSettingName in self.windowsSettingsDict:
            if Globals.debugFlag: print( t("Saving windows set-up {}").format( repr(windowsSettingName) ) )
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


    def closeMe( self ):
        """
        Save files first, and then end the application.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("closeMe()") )
        haveModifications = False
        for appWin in self.appWins:
            if 'Editor' in appWin.genericWindowType and appWin.modified():
                haveModifications = True; break
        if haveModifications:
            showerror( _("Save files"), _("You need to save or close your work first.") )
        else:            
            self.writeSettingsFile()
            self.ApplicationParent.destroy()
    # end of Application.closeMe
# end of class Application



def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if Globals.debugFlag: print( t("Running main...") )
    #Globals.debugFlag = True

    tkRootWindow = Tk()
    tkRootWindow.title( ProgNameVersion )
    settings = ApplicationSettings( DATA_FOLDER, SETTINGS_SUBFOLDER, ProgName )
    settings.load()

    application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of Biblelator.main


if __name__ == '__main__':
    # Configure basic set-up
    parser = Globals.setup( ProgName, ProgVersion )
    Globals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    main()

    Globals.closedown( ProgName, ProgVersion )
# end of Biblelator.py
