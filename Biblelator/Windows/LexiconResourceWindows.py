#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# LexiconResourceWindows.py
#
# Bible and lexicon resource windows for Biblelator Bible display/editing
#
# Copyright (C) 2013-2020 Robert Hunt
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
Windows and frames to allow display and manipulation of
    Bible and lexicon resource windows.
"""
from gettext import gettext as _
import os.path
import logging

import tkinter as tk
from tkinter.ttk import Style, Frame, Button

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint
from BibleOrgSys.OriginalLanguages.BibleLexicon import BibleLexicon

# Biblelator imports
if __name__ == '__main__':
    import sys
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator import BiblelatorGlobals
from Biblelator.Windows.TextBoxes import HTMLTextBox, ChildBoxAddon
from Biblelator.Windows.ChildWindows import ChildWindow



LAST_MODIFIED_DATE = '2020-05-03' # by RJH
SHORT_PROGRAM_NAME = "LexiconResourceWindows"
PROGRAM_NAME = "Biblelator Lexicon Resource Windows"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False



class BibleLexiconResourceWindow( ChildWindow, ChildBoxAddon ):
    """
    """
    def __init__( self, parentWindow ) -> None:
        """
        """
        fnPrint( debuggingThisModule, f"BibleLexiconResourceWindow.__init__( {parentWindow} )" )
        self.lexiconWord = None

        ChildWindow.__init__( self, parentWindow, 'LexiconResource' )
        ChildBoxAddon.__init__( self, self )
        self.moduleID = 'BibleLexicon'
        self.windowType = 'BibleLexiconResourceWindow'

        # Make our own textBox
        self.textBox.destroy()
        self.textBox = HTMLTextBox( self, yscrollcommand=self.vScrollbar.set, wrap='word' )
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.configure( command=self.textBox.yview ) # link the scrollbar to the text box
        #self.createStandardWindowKeyboardBindings( reset=True )

        self.createMenuBar()
        #self.createBibleLexiconResourceWindowWidgets()
        #for USFMKey, styleDict in self.myMaster.stylesheet.getTKStyles().items():
        #    self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style


        try: self.BibleLexicon = BibleLexicon()
        #  os.path.join( self.lexiconPath, 'HebrewLexicon/' ), # Hebrew
        #                                        os.path.join( self.lexiconPath, 'strongs-dictionary-xml/' ) ) # Greek
        except FileNotFoundError:
            logging.critical( "BibleLexiconResourceWindow.__init__ " + _("Unable to find Bible lexicon path") )
            self.BibleLexicon = None
    # end of BibleLexiconResourceWindow.__init__


    def refreshTitle( self ) -> None:
        self.title( "[{}] {}".format( repr(self.lexiconWord), _("Bible Lexicon") ) )
    # end if BibleLexiconResourceWindow.refreshTitle


    def createMenuBar( self ) -> None:
        """
        """
        fnPrint( debuggingThisModule, "BibleLexiconResourceWindow.createMenuBar()" )

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        #fileMenu.add_command( label=_('New…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_command( label=_('Open…'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu )
        #subfileMenuImport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Import'), underline=0, menu=subfileMenuImport )
        #subfileMenuExport = tk.Menu( fileMenu )
        #subfileMenuExport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label=_('HTML'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Export'), underline=0, menu=subfileMenuExport )
        #fileMenu.add_separator()
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] ) # close this window

        editMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Line')][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doBoxFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doBoxRefind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Refind')][0] )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
        gotoMenu.add_command( label=_('Previous entry'), underline=0, command=self.doGotoPreviousEntry )
        gotoMenu.add_command( label=_('Next entry'), underline=0, command=self.doGotoNextEntry )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label=_('Tools'), underline=0 )
        toolsMenu.add_command( label=_('Options…'), underline=0, command=self.notWrittenYet )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label=_('Window'), underline=0 )
        windowMenu.add_command( label=_('Bring in'), underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('ShowMain')][0] )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label=_('Help') )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('About')][0] )
    # end of BibleLexiconResourceWindow.createMenuBar


    def createToolBar( self ) -> None:
        """
        Create a tool bar containing some helpful buttons at the top of the main window.
        """
        fnPrint( debuggingThisModule, "createToolBar()" )

        xPad, yPad = (6, 8) if BiblelatorGlobals.theApp.touchMode else (4, 4)

        Style().configure( 'LexToolBar.TFrame', background='wheat1' )
        toolbar = Frame( self, cursor='hand2', relief=tk.RAISED, style='LexToolBar.TFrame' )

        Style().configure( 'LexPrevious.TButton', background='lightgreen' )
        Style().configure( 'LexNext.TButton', background='pink' )

        Button( toolbar, text=_("Previous"), style='LexPrevious.TButton', command=self.doGotoPreviousEntry ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        Button( toolbar, text=_("Next"), style='LexNext.TButton', command=self.doGotoNextEntry ) \
                    .pack( side=tk.LEFT, padx=xPad, pady=yPad )
        #Button( toolbar, text='Bring All', command=self.doBringAll ).pack( side=tk.LEFT, padx=2, pady=2 )

        toolbar.pack( side=tk.TOP, fill=tk.X )
    # end of BibleLexiconResourceWindow.createToolBar


    def doGotoPreviousEntry( self ) -> None:
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            vPrint( 'Quiet', debuggingThisModule, "doGotoPreviousEntry() from {}".format( repr(self.lexiconWord) ) )
            #self.setDebugText( "doGotoPreviousEntry…" )

        if self.lexiconWord is None:
            self.updateLexiconWord( 'G5624' )
        elif (self.lexiconWord.startswith('H') or self.lexiconWord.startswith('G')) \
        and self.lexiconWord[1:].isdigit() and int(self.lexiconWord[1:])>1:
            number = int( self.lexiconWord[1:] )
            self.updateLexiconWord( self.lexiconWord[0] + str( number-1 ) )
        else: logging.error( "can't doGotoPreviousEntry from {}".format( repr(self.lexiconWord) ) )
    # end of BibleResourceWindow.doGotoPreviousEntry


    def doGotoNextEntry( self ) -> None:
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            vPrint( 'Quiet', debuggingThisModule, "doGotoNextEntry() from {}".format( repr(self.lexiconWord) ) )
            #self.setDebugText( "doGotoNextEntry…" )

        if self.lexiconWord is None:
            self.updateLexiconWord( 'H1' )
        elif (self.lexiconWord.startswith('H') or self.lexiconWord.startswith('G')) \
        and self.lexiconWord[1:].isdigit():
            number = int( self.lexiconWord[1:] )
            self.updateLexiconWord( self.lexiconWord[0] + str( number+1 ) )
        else: logging.error( "can't doGotoNextEntry from {}".format( repr(self.lexiconWord) ) )
    # end of BibleResourceWindow.doGotoNextEntry


    def updateLexiconWord( self, newLexiconWord:str ) -> None:
        """
        Leaves text box in disabled state. (Not user editable.)
        """
        dPrint( 'Quiet', debuggingThisModule, "updateLexiconWord( {} )".format( newLexiconWord ) )

        self.lexiconWord = newLexiconWord
        self.clearText() # Leaves the text box enabled
        if self.BibleLexicon is None:
            self.textBox.insert( tk.END, "<p>No lexicon loaded so can't display entry for {}.</p>".format( repr(newLexiconWord) ) )
        else:
            self.textBox.insert( tk.END, "<h1>Entry for '{}'</h1>".format( newLexiconWord ) )
            txt = self.BibleLexicon.getEntryHTML( self.lexiconWord )
            if txt: self.textBox.insert( tk.END, f'<p>{txt}</p>' )
        self.textBox.configure( state=tk.DISABLED ) # Don't allow editing
        self.refreshTitle()
    # end of BibleLexiconResourceWindow.updateLexiconWord


    def doHelp( self, event=None ) -> None:
        """
        Display a help box.
        """
        fnPrint( debuggingThisModule, "BibleLexiconResourceWindow.doHelp( {} )".format( event ) )
        from Biblelator.Dialogs.Help import HelpBox

        helpInfo = programNameVersion
        helpInfo += '\n' + _("Help for {}").format( self.windowType )
        helpInfo += '\n  ' + _("Keyboard shortcuts:")
        for name,shortcut in self.myKeyboardBindingsList:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
        return BiblelatorGlobals.tkBREAK # so we don't do the main window help also
    # end of BibleLexiconResourceWindow.doHelp


    def doAbout( self, event=None ) -> None:
        """
        Display an about box.
        """
        fnPrint( debuggingThisModule, "BibleLexiconResourceWindow.doAbout( {} )".format( event ) )
        from Biblelator.Dialogs.About import AboutBox

        aboutInfo = programNameVersion
        aboutInfo += "\nInformation about {}".format( self.windowType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
        return BiblelatorGlobals.tkBREAK # so we don't do the main window about also
    # end of BibleLexiconResourceWindow.doAbout
# end of BibleLexiconResourceWindow class



def briefDemo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    #settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', PROGRAM_NAME )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    # tkRootWindow.mainloop()
# end of LexiconResourceWindows.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    #settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', PROGRAM_NAME )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of LexiconResourceWindows.py
