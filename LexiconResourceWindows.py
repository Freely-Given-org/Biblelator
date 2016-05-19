#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# LexiconResourceWindows.py
#
# Bible and lexicon resource windows for Biblelator Bible display/editing
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
Windows and frames to allow display and manipulation of
    Bible and lexicon resource windows.
"""

from gettext import gettext as _

LastModifiedDate = '2016-04-26' # by RJH
ShortProgName = "LexiconResourceWindows"
ProgName = "Biblelator Lexicon Resource Windows"
ProgVersion = '0.35'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import os.path, logging

import tkinter as tk

# Biblelator imports
from TextBoxes import HTMLText
from ChildWindows import ChildWindow

# BibleOrgSys imports
#sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
from BibleLexicon import BibleLexicon
#import Hebrew
#from HebrewLexicon import HebrewLexicon
#from GreekLexicon import GreekLexicon
#from HebrewWLC import HebrewWLC
#import Greek
#from GreekNT import GreekNT



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
    return '{}{}'.format( nameBit, errorBit )
# end of exp



class BibleLexiconResourceWindow( ChildWindow ):
    def __init__( self, parentApp, lexiconPath=None ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("BibleLexiconResourceWindow.__init__( {}, {} )").format( parentApp, lexiconPath ) )
        self.lexiconWord = None
        ChildWindow.__init__( self, parentApp, 'LexiconResource' )
        self.parentApp, self.lexiconPath = parentApp, lexiconPath
        self.moduleID = self.lexiconPath
        self.windowType = 'BibleLexiconResourceWindow'

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
            logging.critical( exp("BibleLexiconResourceWindow.__init__ Unable to find Bible lexicon path: {}").format( repr(self.lexiconPath) ) )
            self.BibleLexicon = None
    # end of BibleLexiconResourceWindow.__init__


    def refreshTitle( self ):
        self.title( "[{}] {}".format( repr(self.lexiconWord), _("Bible Lexicon") ) )
    # end if BibleLexiconResourceWindow.refreshTitle


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("BibleLexiconResourceWindow.createMenuBar()") )
        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

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
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo, accelerator=self.parentApp.keyBindingDict[_('Info')][0] )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] ) # close this window

        editMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        editMenu.add_separator()
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        searchMenu.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine, accelerator=self.parentApp.keyBindingDict[_('Line')][0] )
        searchMenu.add_separator()
        searchMenu.add_command( label=_('Find…'), underline=0, command=self.doWindowFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        searchMenu.add_command( label=_('Find again'), underline=5, command=self.doWindowRefind, accelerator=self.parentApp.keyBindingDict[_('Refind')][0] )

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
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=self.parentApp.keyBindingDict[_('ShowMain')][0] )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label=_('Help') )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp, accelerator=self.parentApp.keyBindingDict[_('Help')][0] )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout, accelerator=self.parentApp.keyBindingDict[_('About')][0] )
    # end of BibleLexiconResourceWindow.createMenuBar


    def doGotoPreviousEntry( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoPreviousEntry() from {}").format( repr(self.lexiconWord) ) )
            #self.setDebugText( "doGotoPreviousEntry…" )
        if (self.lexiconWord.startswith('H') or self.lexiconWord.startswith('G')) and self.lexiconWord[1:].isdigit():
            number = int( self.lexiconWord[1:] )
            self.updateLexiconWord( self.lexiconWord[0] + str( number-1 ) )
        else: logging.error( "can't doGotoPreviousEntry from {}".format( repr(self.lexiconWord) ) )
    # end of BibleResourceWindow.doGotoPreviousEntry


    def doGotoNextEntry( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doGotoNextEntry() from {}").format( repr(self.lexiconWord) ) )
            #self.setDebugText( "doGotoNextEntry…" )
        if (self.lexiconWord.startswith('H') or self.lexiconWord.startswith('G')) and self.lexiconWord[1:].isdigit():
            number = int( self.lexiconWord[1:] )
            self.updateLexiconWord( self.lexiconWord[0] + str( number+1 ) )
        else: logging.error( "can't doGotoNextEntry from {}".format( repr(self.lexiconWord) ) )
    # end of BibleResourceWindow.doGotoNextEntry


    def updateLexiconWord( self, newLexiconWord ): # Leaves in disabled state
        if BibleOrgSysGlobals.debugFlag: print( exp("updateLexiconWord( {} )").format( newLexiconWord ) )
        self.lexiconWord = newLexiconWord
        self.clearText() # Leaves the text box enabled
        if self.BibleLexicon is None:
            self.textBox.insert( tk.END, "<p>No lexicon loaded so can't display entry for {}.</p>".format( repr(newLexiconWord) ) )
        else:
            self.textBox.insert( tk.END, "<h1>Entry for {}</h1>".format( repr(newLexiconWord) ) )
            #txt = self.BibleLexicon.getEntryData( self.lexiconWord )
            #if txt: self.textBox.insert( tk.END, '\n'+txt )
            txt = self.BibleLexicon.getEntryHTML( self.lexiconWord )
            if txt: self.textBox.insert( tk.END, '<p>'+txt+'</p>' )
        self.textBox['state'] = tk.DISABLED # Don't allow editing
        self.refreshTitle()
    # end of BibleLexiconResourceWindow.updateLexiconWord
# end of BibleLexiconResourceWindow class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    #from tkinter import Tk
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo…") )

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
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables


    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of LexiconResourceWindows.py