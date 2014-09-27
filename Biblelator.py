#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Biblelator.py
#   Last modified: 2014-09-25 (also update ProgVersion below)
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
"""

ProgName = "Biblelator"
ProgVersion = "0.11"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, os.path, logging
from gettext import gettext as _
import multiprocessing

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
from tkinter import Tk, Menu, StringVar, messagebox
from tkinter import NORMAL, DISABLED, BOTTOM, LEFT, RIGHT, BOTH, YES, SUNKEN, X
from tkinter.ttk import Style, Frame, Button, Combobox
from tkinter.tix import Spinbox

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals
from BibleOrganizationalSystems import BibleOrganizationalSystem
import VerseReferences
import USFMStylesheets
import SwordResources

# Biblelator imports
from BiblelatorGlobals import DATA_FOLDER, SETTINGS_FOLDER, MAX_WINDOWS, MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE, GROUP_CODES, editModeNormal, parseGeometry, assembleGeometryFromList
from ApplicationSettings import ApplicationSettings
from ResourceWindows import ResourceWindows, ResourceWindow, ResourceFrames
from BibleResourceWindows import SwordResourceFrame, USFMResourceFrame, FCBHResourceFrame
from LexiconResourceWindows import HebrewLexiconResourceFrame, GreekLexiconResourceFrame, BibleLexiconResourceFrame
from EditWindow import USFMEditWindow



def t( messageString ):
    """
    Prepends the module name to a error or warning message string
        if we are in debug mode.
    Returns the new string.
    """
    try: nameBit, errorBit = messageString.split( ': ', 1 )
    except ValueError: nameBit, errorBit = '', messageString
    if Globals.debugFlag or debuggingThisModule:
        nameBit = '{}{}{}: '.format( ProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit, _(errorBit) )



class Application( Frame ):
    global settings
    def __init__( self, parent, settings ):
        if Globals.debugFlag: print( t("Application.__init__( {} )").format( parent ) )
        self.ApplicationParent, self.settings = parent, settings
        #print( "p", parent )
        #print( "self", repr( self ) )
        self.ApplicationParent.title( ProgNameVersion )

        self.genericBOS = BibleOrganizationalSystem( "GENERIC-KJV-66-ENG" )
        self.stylesheet = USFMStylesheets.USFMStylesheet().loadDefault()
        Frame.__init__( self, self.ApplicationParent )
        self.pack()
        self.createMenuBar()
        self.createToolBar()
        self.createApplicationWidgets()

        self.SwordInterface = SwordResources.SwordInterface() # Preload the Sword library

        self.BCVHistory = []
        self.BCVHistoryIndex = None

        # Read and apply the saved settings
        #self.readSettingsFile()
        try: self.minimumXSize, self.minimumYSize = settings.data[ProgName]['minimumXSize'], settings.data[ProgName]['minimumYSize']
        except KeyError: self.minimumXSize, self.minimumYSize = MINIMUM_MAIN_X_SIZE, MINIMUM_MAIN_Y_SIZE
        #print( self.minimumXSize, self.minimumYSize )
        self.ApplicationParent.minsize( self.minimumXSize, self.minimumYSize )
        try: self.ApplicationParent.geometry( settings.data[ProgName]['windowGeometry'] )
        except KeyError: pass # we had no geometry set
        except TclError: logging.critical( t("Application.__init__: Bad window geometry in settings file: {}").format( settings.data[ProgName]['windowGeometry'] ) )
        self.appWins = ResourceWindows()
        self.projWins = ResourceFrames()
        for j in range( 1, MAX_WINDOWS ):
            tryName = "Window{}".format( j )
            if tryName in settings.data.sections():
                thisOne = settings.data[tryName]
                windowGeometry = thisOne['windowGeometry'] if 'windowGeometry' in thisOne else None
                winType = thisOne['windowType']
                if winType == 'SwordResourceWindow':
                    self.openSwordResourceFrame( thisOne['moduleAbbreviation'], windowGeometry )
                    #except: logging.error( "Unable to read SwordResourceFrame {} settings".format( j ) )
                elif winType == 'FCBHResourceWindow':
                    self.openFCBHResourceFrame( thisOne['moduleAbbreviation'], windowGeometry )
                    #except: logging.error( "Unable to read FCBHResourceFrame {} settings".format( j ) )
                elif winType == 'USFMResourceWindow':
                    self.openUSFMResourceFrame( thisOne['USFMFolder'], windowGeometry )
                    #except: logging.error( "Unable to read USFMResourceFrame {} settings".format( j ) )

                elif winType == 'HebrewLexiconResourceWindow':
                    self.openHebrewLexiconResourceFrame( thisOne['HebrewLexiconFolder'], windowGeometry )
                    #except: logging.error( "Unable to read USFMResourceFrame {} settings".format( j ) )
                elif winType == 'GreekLexiconResourceWindow':
                    self.openGreekLexiconResourceFrame( thisOne['GreekLexiconFolder'], windowGeometry )
                    #except: logging.error( "Unable to read USFMResourceFrame {} settings".format( j ) )
                elif winType == 'BibleLexiconResourceWindow':
                    self.openBibleLexiconResourceFrame( thisOne['BibleLexiconFolder'], windowGeometry )
                    #except: logging.error( "Unable to read USFMResourceFrame {} settings".format( j ) )

                elif winType == 'USFMEditWindow':
                    self.openUSFMEditWindow( thisOne['USFMFolder'], thisOne['editMode'], windowGeometry )
                    #except: logging.error( "Unable to read USFMEditWindow {} settings".format( j ) )

                else:
                    logging.critical( t("Application.__init__: Unknown {} window type").format( repr(winType) ) )
                    if Globals.debugFlag: halt
        try: self.currentBCVGroup = settings.data['BCVGroups']['currentGroup']
        except KeyError: self.currentBCVGroup = 'A'
        try: self.BCVGroupA = (settings.data['BCVGroups']['A-Book'],settings.data['BCVGroups']['A-Chapter'],settings.data['BCVGroups']['A-Verse'])
        except KeyError: self.BCVGroupA = (self.genericBOS.getFirstBookCode(), '1', '1')
        try: self.BCVGroupB = (settings.data['BCVGroups']['B-Book'],settings.data['BCVGroups']['B-Chapter'],settings.data['BCVGroups']['B-Verse'])
        except KeyError: self.BCVGroupB = (None, None, None)
        try: self.BCVGroupC = (settings.data['BCVGroups']['C-Book'],settings.data['BCVGroups']['C-Chapter'],settings.data['BCVGroups']['C-Verse'])
        except KeyError: self.BCVGroupC = (None, None, None)
        try: self.BCVGroupD = (settings.data['BCVGroups']['D-Book'],settings.data['BCVGroups']['D-Chapter'],settings.data['BCVGroups']['D-Verse'])
        except KeyError: self.BCVGroupD = (None, None, None)
        self.updateBCVGroup( self.currentBCVGroup )
        self.updateBCVButtons()

        if 0: # Play with ttk styles
            import random
            self.style = Style()
            available_themes = self.style.theme_names()
            random_theme = random.choice(available_themes)
            self.style.theme_use(random_theme)
            self.ApplicationParent.title(random_theme)

            frm = Frame( self.ApplicationParent )
            #frm.grid( sticky=W+E+N+S )
            frm.pack(expand=YES, fill=BOTH )
            # create a Combobox with themes to choose from
            self.combo = Combobox(frm, values=available_themes)
            self.combo.grid( padx=32, pady=8 )
            #else: self.combo.pack( padx=32, pady=8 )
            # make the Enter key change the style
            self.combo.bind('<Return>', self.change_style)
            # make a Button to change the style
            button = Button(frm, text='OK')
            button['command'] = self.change_style
            button.grid( pady=8 )
            #else: button.pack( pady=8 )


        # Open some sample windows if we don't have any already
        if not self.appWins and not self.projWins \
        and Globals.debugFlag and debuggingThisModule: # Just for testing/kickstarting
            print( t("Application.__init__ Opening sample resources...") )
            self.openSwordResourceFrame( 'KJV' )
            self.openSwordResourceFrame( 'ASV' )
            self.openSwordResourceFrame( 'WEB' )
            p1 = '../../../../../Data/Work/Matigsalug/Bible/MBTV/'
            p2 = 'C:\\My Paratext Projects\\MBTV\\'
            p = p1 if os.path.exists( p1 ) else p2
            self.openUSFMResourceFrame( p )
            self.openUSFMEditWindow( p, editModeNormal )
            self.openFCBHResourceFrame( 'ENGESV' )
            self.openHebrewLexiconResourceFrame( None )
            self.openGreekLexiconResourceFrame( None )
            self.openBibleLexiconResourceFrame( None )
        #self.after( 100, self.goto ) # Do a goto after the empty window has displayed
        self.goto()
    # end of Application.__init__


    if 0:
        def change_style(self, event=None):
            """set the Style to the content of the Combobox"""
            from tkinter import TclError
            content = self.combo.get()
            try:
                self.style.theme_use(content)
            except TclError as err:
                messagebox.showerror('Error', err)
            else:
                self.ApplicationParent.title(content)
        # end of Application.change_style


    def notWrittenYet( self ):
        messagebox.showerror( 'Not implemented', 'Not yet available, sorry' )


    def doAbout( self ):
        from About import AboutBox
        ab = AboutBox( self.ApplicationParent, ProgName, ProgNameVersion )


    def setStatus( self, newStatus=None ):
        """
        Set (or clear) the status bar text.
        """
        pass
    # end of Application.setStatus


    def createMenuBar( self ):
        #self.win = Toplevel( self )
        self.menubar = Menu( self.ApplicationParent )
        #self.ApplicationParent['menu'] = self.menubar
        self.ApplicationParent.config(menu=self.menubar) # alternative

        menuFile = Menu( self.menubar )
        menuFile.add_command( label='New...', command=self.notWrittenYet, underline=0 )
        menuFile.add_command( label='Open...', command=self.notWrittenYet, underline=0 )
        menuFile.add_separator()
        submenuFileImport = Menu( menuFile )
        submenuFileImport.add_command( label='USX', command=self.notWrittenYet, underline=0 )
        menuFile.add_cascade( label='Import', menu=submenuFileImport, underline=0 )
        submenuFileExport = Menu( menuFile )
        submenuFileExport.add_command( label='USX', command=self.notWrittenYet, underline=0 )
        submenuFileExport.add_command( label='HTML', command=self.notWrittenYet, underline=0 )
        menuFile.add_cascade( label='Export', menu=submenuFileExport, underline=0 )
        menuFile.add_separator()
        menuFile.add_command( label='Quit', command=self.quit, underline=0 ) # quit app
        self.menubar.add_cascade( menu=menuFile, label='File', underline=0 )

        menuEdit = Menu( self.menubar )
        menuEdit.add_command( label='Find...', command=self.notWrittenYet, underline=0 )
        menuEdit.add_command( label='Replace...', command=self.notWrittenYet, underline=0 )
        self.menubar.add_cascade( menu=menuEdit, label='Edit', underline=0 )

        menuTools = Menu( self.menubar, tearoff=False )
        menuTools.add_command( label='Options...', command=self.notWrittenYet, underline=0 )
        self.menubar.add_cascade( menu=menuTools, label='Tools', underline=0 )

        menuWindow = Menu( self.menubar, tearoff=False )
        menuWindow.add_command( label='Bring in', command=self.notWrittenYet, underline=0 )
        self.menubar.add_cascade( menu=menuWindow, label='Window', underline=0 )

        menuHelp = Menu( self.menubar, name='help', tearoff=False )
        menuHelp.add_command( label='About...', command=self.doAbout, underline=0 )
        self.menubar.add_cascade( menu=menuHelp, label='Help', underline=0 )

        #filename = filedialog.askopenfilename()
        #filename = filedialog.asksaveasfilename()
        #dirname = filedialog.askdirectory()
        #colorchooser.askcolor(initialcolor='#ff0000')
        #messagebox.showinfo(message='Have a good day')
        #messagebox.askyesno( message='Are you sure you want to install SuperVirus?' icon='question' title='Install' )
    # end of createMenuBar


    def createToolBar( self ):
        toolbar = Frame( self, cursor='hand2', relief=SUNKEN ) # bd=2
        toolbar.pack( side=BOTTOM, fill=X )
        Button( toolbar, text='Halt',  command=self.quit ).pack( side=RIGHT )
        Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=LEFT )
        Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=LEFT )
        Button( toolbar, text='Show All', command=self.showAll ).pack( side=LEFT )
        Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=LEFT )
    # end of createToolBar


    def createApplicationWidgets( self ):
        #self.label1 = Label( self, text="My label" )
        #self.label1.pack()


        self.previousBCVButton = Button( self, width=4, text='<-', command=self.goBack, state=DISABLED )
        #self.previousBCVButton['text'] = '<-'
        #self.previousBCVButton["command"] = self.goBack
        #self.previousBCVButton.grid( row=0, column=0 )
        self.previousBCVButton.pack( side=LEFT )

        self.nextBCVButton = Button( self, width=4, text='->', command=self.goForward, state=DISABLED )
        #self.nextBCVButton['text'] = '->'
        #self.nextBCVButton["command"] = self.goForward
        #self.nextBCVButton.grid( row=0, column=1 )
        self.nextBCVButton.pack( side=LEFT )

        self.GroupAButton = Button( self, width=2, text='A', command=self.selectGroupA, state=DISABLED )
        self.GroupBButton = Button( self, width=2, text='B', command=self.selectGroupB, state=DISABLED )
        self.GroupCButton = Button( self, width=2, text='C', command=self.selectGroupC, state=DISABLED )
        self.GroupDButton = Button( self, width=2, text='D', command=self.selectGroupD, state=DISABLED )
        #self.GroupAButton.grid( row=0, column=2 )
        #self.GroupBButton.grid( row=0, column=3 )
        #self.GroupCButton.grid( row=1, column=2 )
        #self.GroupDButton.grid( row=1, column=3 )
        self.GroupAButton.pack( side=LEFT )
        self.GroupBButton.pack( side=LEFT )
        self.GroupCButton.pack( side=LEFT )
        self.GroupDButton.pack( side=LEFT )

        self.bookNames = [self.genericBOS.getBookName(BBB) for BBB in self.genericBOS.getBookList()]
        bookName = self.bookNames[0]
        self.bookNameVar = StringVar()
        self.bookNameVar.set( bookName )
        self.BBB = self.genericBOS.getBBB( bookName )
        self.bookNameBox = Combobox( self, textvariable=self.bookNameVar )
        self.bookNameBox['values'] = self.bookNames
        self.bookNameBox['width'] = len( 'Deuteronomy' )
        self.bookNameBox.bind('<<ComboboxSelected>>', self.goto )
        #self.bookNameBox.grid( row=0, column=4 )
        self.bookNameBox.pack( side=LEFT )

        self.chapterNumberVar = StringVar()
        self.chapterNumberVar.set( '1' )
        self.maxChapters = self.genericBOS.getNumChapters( self.BBB )
        #print( "maxChapters", self.maxChapters )
        self.chapterSpinbox = Spinbox( self, from_=0.0, to=self.maxChapters, textvariable=self.chapterNumberVar )
        self.chapterSpinbox['width'] = 3
        self.chapterSpinbox['command'] = self.goto
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
        self.maxVerses = self.genericBOS.getNumVerses( self.BBB, self.chapterNumberVar.get() )
        #print( "maxVerses", self.maxVerses )
        #self.maxVersesVar.set( str(self.maxVerses) )
        # Add 1 to maxVerses to enable them to go to the next chapter
        self.verseSpinbox = Spinbox( self, from_=0.0, to=1.0+self.maxVerses, textvariable=self.verseNumberVar )
        self.verseSpinbox['width'] = 3
        self.verseSpinbox['command'] = self.goto
        #self.verseSpinbox.grid( row=0, column=6 )
        self.verseSpinbox.pack( side=LEFT )

        #self.verseNumberVar = StringVar()
        #self.verseNumberVar.set( '1' )
        #self.verseNumberBox = Entry( self, textvariable=self.verseNumberVar )
        #self.verseNumberBox['width'] = 3
        #self.verseNumberBox.pack()

        self.updateButton = Button( self )
        self.updateButton['text'] = 'Update'
        self.updateButton["command"] = self.goto
        #self.updateButton.grid( row=0, column=7 )
        self.updateButton.pack( side=LEFT )

        self.bStyle = Style( self )
        #self.bStyle.configure( "Red.TButton", foreground="red", background="white" )
        self.bStyle.map("Red.TButton",
                        foreground=[('pressed', 'red'), ('active', 'blue')],
                        background=[('pressed', '!disabled', 'black'), ('active', 'white')] )

        self.QUIT = Button( self, text="QUIT", style="Red.TButton", command=self.closeMe )
        #self.QUIT.grid( row=1, column=7 )
        self.QUIT.pack( side=RIGHT )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
    # end of Application.createApplicationWidgets


    def openSwordResourceFrame( self, moduleAbbreviation, windowGeometry=None ):
        rw = ResourceWindow( self.ApplicationParent, "BibleResource" )
        rw.winType = "SwordResourceFrame"
        rw.moduleAbbreviation = moduleAbbreviation
        if windowGeometry: rw.geometry( windowGeometry )
        self.appWins.append( rw )
        srw = SwordResourceFrame( rw, self, rw.moduleAbbreviation )
        srw.pack( expand=YES, fill=BOTH )
        self.projWins.append( srw )
        if not srw.SwordModule:
            logging.critical( t("Application.openSwordResourceFrame: Unable to open module {}").format( repr(moduleAbbreviation) ) )
            #rw.destroy()
    # end of Application.openSwordResourceFrame


    def openFCBHResourceFrame( self, moduleAbbreviation, windowGeometry=None ):
        rw = ResourceWindow( self.ApplicationParent, "BibleResource" )
        rw.winType = "FCBHResourceFrame"
        rw.moduleAbbreviation = moduleAbbreviation
        if windowGeometry: rw.geometry( windowGeometry )
        self.appWins.append( rw )
        frw = FCBHResourceFrame( rw, self, rw.moduleAbbreviation )
        frw.pack( expand=YES, fill=BOTH )
        self.projWins.append( frw )
        if not frw.FCBHModule:
            logging.critical( t("Application.openFCBHResourceFrame: Unable to open resource {}").format( repr(moduleAbbreviation) ) )
            #rw.destroy()
    # end of Application.openFCBHResourceFrame


    def openUSFMResourceFrame( self, USFMFolder, windowGeometry=None ):
        rw = ResourceWindow( self.ApplicationParent, "BibleResource" )
        rw.winType = "USFMResourceFrame"
        rw.USFMFolder = USFMFolder
        if windowGeometry: rw.geometry( windowGeometry )
        self.appWins.append( rw )
        urw = USFMResourceFrame( rw, self, rw.USFMFolder )
        urw.pack( expand=YES, fill=BOTH )
        self.projWins.append( urw )
        if urw.USFMBible is None:
            logging.critical( t("Application.openUSFMResourceFrame: Unable to open resource {}").format( repr(USFMFolder) ) )
            #rw.destroy()
    # end of Application.openUSFMResourceFrame


    def openHebrewLexiconResourceFrame( self, lexiconFolder, windowGeometry=None ):
        rw = ResourceWindow( self.ApplicationParent, "LexiconResource" )
        rw.winType = "HebrewLexiconResourceFrame"
        rw.lexiconFolder = lexiconFolder
        if rw.lexiconFolder is None: rw.lexiconFolder = "../HebrewLexicon/"
        if windowGeometry: rw.geometry( windowGeometry )
        self.appWins.append( rw )
        hlrw = HebrewLexiconResourceFrame( rw, self, rw.lexiconFolder )
        hlrw.pack( expand=YES, fill=BOTH )
        self.projWins.append( hlrw )
        if hlrw.HebrewLexicon is None:
            logging.critical( t("Application.openHebrewLexiconResourceFrame: Unable to open Hebrew lexicon {}").format( repr(lexiconFolder) ) )
            #rw.destroy()
    # end of Application.openHebrewLexiconResourceFrame


    def openGreekLexiconResourceFrame( self, lexiconFolder, windowGeometry=None ):
        rw = ResourceWindow( self.ApplicationParent, "LexiconResource" )
        rw.winType = "GreekLexiconResourceFrame"
        rw.lexiconFolder = lexiconFolder
        if rw.lexiconFolder is None: rw.lexiconFolder = "../morphgnt/strongs-dictionary-xml/"
        if windowGeometry: rw.geometry( windowGeometry )
        self.appWins.append( rw )
        glrw = GreekLexiconResourceFrame( rw, self, rw.lexiconFolder )
        glrw.pack( expand=YES, fill=BOTH )
        self.projWins.append( glrw )
        if glrw.GreekLexicon is None:
            logging.critical( t("Application.openGreekLexiconResourceFrame: Unable to open Greek lexicon {}").format( repr(lexiconFolder) ) )
            #rw.destroy()
    # end of Application.openGreekLexiconResourceFrame


    def openBibleLexiconResourceFrame( self, lexiconFolder, windowGeometry=None ):
        rw = ResourceWindow( self.ApplicationParent, "LexiconResource" )
        rw.winType = "BibleLexiconResourceFrame"
        rw.lexiconFolder = lexiconFolder
        if rw.lexiconFolder is None: rw.lexiconFolder = "../"
        if windowGeometry: rw.geometry( windowGeometry )
        self.appWins.append( rw )
        blrw = BibleLexiconResourceFrame( rw, self, rw.lexiconFolder )
        blrw.pack( expand=YES, fill=BOTH )
        self.projWins.append( blrw )
        if blrw.BibleLexicon is None:
            logging.critical( t("Application.openBibleLexiconResourceFrame: Unable to open Bible lexicon resource {}").format( repr(lexiconFolder) ) )
            #rw.destroy()
    # end of Application.openHebrewLexiconResourceFrame


    def openUSFMEditWindow( self, USFMFolder, editMode, windowGeometry=None ):
        rw = ResourceWindow( self.ApplicationParent, "Editor" )
        rw.winType = "USFMEditWindow"
        rw.USFMFolder, rw.editMode = USFMFolder, editMode
        if windowGeometry: rw.geometry( windowGeometry )
        self.appWins.append( rw )
        uew = USFMEditWindow( rw, self, rw.USFMFolder, rw.editMode )
        uew.pack( expand=YES, fill=BOTH )
        self.projWins.append( uew )
        if uew.USFMBible is None:
            logging.critical( t("Application.openUSFMEditWindow: Unable to open resource {}").format( repr(USFMFolder) ) )
            #rw.destroy()
    # end of Application.openUSFMEditWindow


    def goBack( self, event=None ):
        if Globals.debugFlag: print( "goBack" )
        #print( dir(event) )
        assert( self.BCVHistory )
        assert( self.BCVHistoryIndex )
        self.BCVHistoryIndex -= 1
        assert( self.BCVHistoryIndex >= 0)
        self.setCurrentBCV( self.BCVHistory[self.BCVHistoryIndex] )
        self.updatePreviousNextButtons()
        self.goto()

    def goForward( self, event=None ):
        if Globals.debugFlag: print( "goForward" )
        #print( dir(event) )
        assert( self.BCVHistory )
        assert( self.BCVHistoryIndex < len(self.BCVHistory)-1 )
        self.BCVHistoryIndex += 1
        assert( self.BCVHistoryIndex < len(self.BCVHistory) )
        self.setCurrentBCV( self.BCVHistory[self.BCVHistoryIndex] )
        self.updatePreviousNextButtons()
        self.goto()

    def setCurrentBCV( self, newBCV ):
        self.currentBCV = newBCV
        if   self.currentBCVGroup == 'A': self.BCVGroupA = self.currentBCV
        elif self.currentBCVGroup == 'B': self.BCVGroupB = self.currentBCV
        elif self.currentBCVGroup == 'C': self.BCVGroupC = self.currentBCV
        elif self.currentBCVGroup == 'D': self.BCVGroupD = self.currentBCV
        self.bookNameVar.set( self.genericBOS.getBookName(self.currentBCV[0]) )
        self.chapterNumberVar.set( self.currentBCV[1] )
        self.verseNumberVar.set( self.currentBCV[2] )
        if self.currentBCV not in self.BCVHistory:
            self.BCVHistoryIndex = len( self.BCVHistory )
            self.BCVHistory.append( self.currentBCV )
            self.updatePreviousNextButtons()

    def updateBCVGroup( self, newGroupLetter ):
        assert( newGroupLetter in GROUP_CODES )
        self.currentBCVGroup = newGroupLetter
        if   self.currentBCVGroup == 'A': self.currentBCV = self.BCVGroupA
        elif self.currentBCVGroup == 'B': self.currentBCV = self.BCVGroupB
        elif self.currentBCVGroup == 'C': self.currentBCV = self.BCVGroupC
        elif self.currentBCVGroup == 'D': self.currentBCV = self.BCVGroupD
        if self.currentBCV == (None, None, None):
            self.setCurrentBCV( (self.genericBOS.getFirstBookCode(),'1','1') )
        self.updateBCVButtons()
        self.goto()

    def updateBCVButtons( self ):
        groupButtons = [ self.GroupAButton, self.GroupBButton, self.GroupCButton, self.GroupDButton ]
        if   self.currentBCVGroup == 'A': ix = 0
        elif self.currentBCVGroup == 'B': ix = 1
        elif self.currentBCVGroup == 'C': ix = 2
        elif self.currentBCVGroup == 'D': ix = 3
        else: halt
        selectedButton = groupButtons.pop( ix )
        selectedButton.config( state=DISABLED, relief=SUNKEN )
        for otherButton in groupButtons:
            otherButton.config( state=NORMAL, relief=RAISED )
        self.bookNameVar.set( self.genericBOS.getBookName(self.currentBCV[0]) )
        self.chapterNumberVar.set( self.currentBCV[1] )
        self.verseNumberVar.set( self.currentBCV[2] )

    def updatePreviousNextButtons( self ):
        self.previousBCVButton.config( state=NORMAL if self.BCVHistory and self.BCVHistoryIndex>0 else DISABLED )
        self.nextBCVButton.config( state=NORMAL if self.BCVHistory and self.BCVHistoryIndex<len(self.BCVHistory)-1 else DISABLED )

    def selectGroupA( self ):
        self.updateBCVGroup( 'A' )
    def selectGroupB( self ):
        self.updateBCVGroup( 'B' )
    def selectGroupC( self ):
        self.updateBCVGroup( 'C' )
    def selectGroupD( self ):
        self.updateBCVGroup( 'D' )

    def updateBCVButtons( self ):
        groupButtons = [ self.GroupAButton, self.GroupBButton, self.GroupCButton, self.GroupDButton ]
        if   self.currentBCVGroup == 'A': ix = 0
        elif self.currentBCVGroup == 'B': ix = 1
        elif self.currentBCVGroup == 'C': ix = 2
        elif self.currentBCVGroup == 'D': ix = 3
        else: halt
        selectedButton = groupButtons.pop( ix )
        selectedButton.config( state=DISABLED )
        for otherButton in groupButtons:
            otherButton.config( state=NORMAL )
        self.bookNameVar.set( self.genericBOS.getBookName(self.currentBCV[0]) )
        self.chapterNumberVar.set( self.currentBCV[1] )
        self.verseNumberVar.set( self.currentBCV[2] )

    def goto( self, event=None ):
        """
        Handle a new book, chapter, verse setting.
        """
        if Globals.debugFlag: print( "goto" )
        #print( dir(event) )

        b = self.bookNameVar.get()
        c = self.chapterNumberVar.get()
        v = self.verseNumberVar.get()
        self.BnCV = (b, c, v)
        BBB = self.genericBOS.getBBB( b )
        #print( "BBB", BBB )
        self.setCurrentBCV( (BBB,c,v) )
        self.verseKey = VerseReferences.SimpleVerseKey( BBB, c, v )
        if Globals.debugFlag: print( "  BCV", self.BnCV )
        assert( self.genericBOS.isValidBCVRef( self.verseKey, repr( self.BnCV ), extended=True ) )
        self.SwordKey = self.SwordInterface.makeKey( BBB, c, v )
        #print( "swK", self.SwordKey.getText() )

        intC, intV = int( c ), int( v )
        if Globals.debugFlag and ( self.SwordKey.getChapter()!=intC or self.SwordKey.getVerse() != intV ):
            print( "Sword switched from {} {}:{} to {}:{}".format( BBB, intC,  intV, self.SwordKey.getChapter(), self.SwordKey.getVerse() ) )


        # Determine the previous verse number (if any)
        prevIntC, prevIntV = intC, intV
        self.previousBnCV = self.previousVerseKey = self.SwordPreviousKey = None
        #print( "here with", intC, intV )
        if intV > 0: prevIntV = intV - 1
        elif intC > 1:
            prevIntC = intC - 1
            prevIntV = self.genericBOS.getNumVerses( BBB, prevIntC )
            print( "Went back to previous chapter", prevIntC, prevIntV, "from", self.BnCV )
        if prevIntV!=intV or prevIntC!=intC:
            self.previousBnCV = (b, str(prevIntC), str(prevIntV))
            #print( "prev", self.previousBCV )
            assert( self.previousBnCV != self.BnCV )
            self.previousVerseKey = VerseReferences.SimpleVerseKey( BBB, prevIntC, prevIntV )
            self.SwordPreviousKey = self.SwordInterface.makeKey( BBB, str(prevIntC), str(prevIntV) )

        # Determine the next valid verse numbers
        nextIntC, nextIntV = intC, intV
        self.nextBnCVs, self.nextVerseKeys, self.SwordNextKeys = [], [], []
        for n in range( 0, 5 ):
            nextIntV += 1
            if nextIntV > self.genericBOS.getNumVerses( BBB, intC ):
                nextIntV = 1
                nextIntC += 1 # Need to check................................
            if nextIntV!=intV or nextIntC!=intC:
                nextBnCV = (b, str(nextIntC), str(nextIntV))
                assert( nextBnCV != self.BnCV )
                #print( "next", nextBCV )
                self.nextBnCVs.append( nextBnCV )
                self.nextVerseKeys.append( VerseReferences.SimpleVerseKey( BBB, nextIntC, nextIntV ) )
                self.SwordNextKeys.append( self.SwordInterface.makeKey( BBB, str(nextIntC), str(nextIntV) ) )

        self.projWins.update()
    # end of Application.goto


    def writeSettingsFile( self ):
        """
        Update our program settings and save them.
        """
        print( t("Application.writeSettingsFile()") )
        self.settings.reset()
        self.settings.data[ProgName] = {}
        main = self.settings.data[ProgName]
        main['version'] = ProgVersion
        main['windowGeometry'] = self.ApplicationParent.geometry()
        main['minimumXSize'] = str( self.minimumXSize )
        main['minimumYSize'] = str( self.minimumYSize )

        # Save the referenceGroups A..D
        self.settings.data['BCVGroups'] = {}
        groups = self.settings.data['BCVGroups']
        groups['currentGroup'] = self.currentBCVGroup
        groups['A-Book'] = self.BCVGroupA[0]
        groups['A-Chapter'] = self.BCVGroupA[1]
        groups['A-Verse'] = self.BCVGroupA[2]
        if self.BCVGroupB == (None,None,None):
            assert( self.currentBCVGroup == 'A' )
        else:
            groups['B-Book'] = self.BCVGroupB[0]
            groups['B-Chapter'] = self.BCVGroupB[1]
            groups['B-Verse'] = self.BCVGroupB[2]
            if self.BCVGroupC != (None,None,None):
                groups['C-Book'] = self.BCVGroupC[0]
                groups['C-Chapter'] = self.BCVGroupC[1]
                groups['C-Verse'] = self.BCVGroupC[2]
                if self.BCVGroupD != (None,None,None):
                    groups['D-Book'] = self.BCVGroupD[0]
                    groups['D-Chapter'] = self.BCVGroupD[1]
                    groups['D-Verse'] = self.BCVGroupD[2]

        # Save the child windows
        for j, appWin in enumerate( self.appWins ):
            winSetupName = "Window{}".format( j+1 )
            self.settings.data[winSetupName] = {}
            winSettings = self.settings.data[winSetupName]
            winSettings['windowType'] = appWin.winType.replace( 'Frame', 'Window' )
            winSettings['windowGeometry'] = appWin.geometry()
            if appWin.winType == 'SwordResourceFrame':
                winSettings['moduleAbbreviation'] = appWin.moduleAbbreviation
            elif appWin.winType == 'FCBHResourceFrame':
                winSettings['moduleAbbreviation'] = appWin.moduleAbbreviation
            elif appWin.winType == 'USFMResourceFrame':
                winSettings['USFMFolder'] = appWin.USFMFolder

            elif appWin.winType == 'HebrewLexiconResourceFrame':
                winSettings['HebrewLexiconFolder'] = appWin.lexiconFolder
            elif appWin.winType == 'GreekLexiconResourceFrame':
                winSettings['GreekLexiconFolder'] = appWin.lexiconFolder
            elif appWin.winType == 'BibleLexiconResourceFrame':
                winSettings['BibleLexiconFolder'] = appWin.lexiconFolder
                
            elif appWin.winType == 'USFMEditWindow':
                winSettings['USFMFolder'] = appWin.USFMFolder
                winSettings['editMode'] = appWin.editMode
                
            else:
                logging.critical( t("writeSettingsFile: Unknown {} window type").format( repr(appWin.winType) ) )
                if Globals.deubgFlag: halt

        self.settings.save()
    # end of writeSettingsFile


    def hideResources( self ):
        """
        Minimize all of our resource windows,
            i.e., leave the editor and main window
        """
        self.appWins.iconifyResources()
    # end of Application.hideAll


    def hideAll( self, includeMe=True ):
        """
        Minimize all of our windows.
        """
        self.appWins.iconify()
        if includeMe: self.ApplicationParent.iconify()
    # end of Application.hideAll


    def showAll( self ):
        """
        Show/restore all of our windows.
        """
        self.appWins.deiconify()
        self.ApplicationParent.deiconify() # Do this last so it has the focus
    # end of Application.hideAll


    def bringAll( self ):
        """
        Bring all of our windows close.
        """
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
        self.showAll()
    # end of Application.bringAll


    def closeMe( self ):
        """
        End the application.
        """
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
    settings = ApplicationSettings( DATA_FOLDER, SETTINGS_FOLDER, ProgName )
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


    if 1 and Globals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    main()

    Globals.closedown( ProgName, ProgVersion )
# end of Biblelator.py
