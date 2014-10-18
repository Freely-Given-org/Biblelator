#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ResourceWindows.py
#   Last modified: 2014-10-18 (also update ProgVersion below)
#
# Base of Bible and lexicon resource windows for Biblelator Bible display/editing
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
Base windows to allow display and manipulation of
    Bible and lexicon resource windows.
"""

ShortProgName = "ResourceWindows"
ProgName = "Biblelator Resource Windows"
ProgVersion = "0.19"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys
from gettext import gettext as _

from tkinter import Toplevel, TclError, Menu, messagebox
from tkinter import NORMAL, DISABLED, BOTTOM, LEFT, RIGHT, BOTH, YES, E, FALSE, \
                    END, INSERT, SEL, SEL_FIRST, SEL_LAST
from tkinter.messagebox import showerror, showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askstring, askinteger

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals

# Biblelator imports
from BiblelatorGlobals import APP_NAME, START, \
                             MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE



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



class ResourceWindow( Toplevel ):
    """
    """
    def __init__( self, parentApp, genericWindowType ):
        """
        The genericWindowType is set here,
            but the more accurate winType is set later by the subclass.
        """
        if Globals.debugFlag:
            #print( t("ResourceWindow.__init__( {} {} )").format( parentApp, repr(genericWindowType) ) )
            assert( parentApp )
            assert( genericWindowType in ('BibleResource','LexiconResource','TextEditor','BibleEditor') )
        self.parentApp, self.genericWindowType = parentApp, genericWindowType
        Toplevel.__init__( self, self.parentApp )
        self.protocol( "WM_DELETE_WINDOW", self.closeResourceWindow )
        self.minimumXSize, self.minimumYSize = MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE

        self.createMenuBar()
        self.createToolBar()
        self.createContextMenu()

        self.textBox = ScrolledText( self, state=DISABLED )
        self.textBox['wrap'] = 'word'
        self.textBox.pack( expand=YES, fill=BOTH )

        # Options for find, etc.
        self.optionsDict = {}
        self.optionsDict['caseinsens'] = True

        self.refreshTitle() # Must be in superclass
    # end of ResourceWindow.__init__


    def notWrittenYet( self ):
        messagebox.showerror( _("Not implemented"), _("Not yet available, sorry") )
    # end of ResourceWindow.notWrittenYet


    def clearText( self ): # Leaves in normal state
        self.textBox['state'] = NORMAL
        self.textBox.delete( '1.0', END )
    # end of ResourceFrame.updateText


    def doHelp( self ):
        from Help import HelpBox
        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.winType )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of Application.doHelp


    def doAbout( self ):
        from About import AboutBox
        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.winType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of Application.doAbout


    def createMenuBar( self ):
        if Globals.debugFlag:
            print( t("This 'createMenuBar' method MUST be overridden!") )
            halt


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        self.contextMenu = Menu( self, tearoff=0 )
        self.contextMenu.add_command( label="Copy", underline=0, command=self.onCopy )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Select all", underline=7, command=self.onSelectAll )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Find...", underline=0, command=self.onFind )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Close", underline=1, command=self.onClose )

        self.bind( "<Button-3>", self.showContextMenu ) # right-click
        #self.pack()
    # end of ResourceWindow.createContextMenu


    def showContextMenu(self, e):
        self.contextMenu.post( e.x_root, e.y_root )
    # end of ResourceWindow.showContextMenu


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        if Globals.debugFlag:
            print( t("This 'createToolBar' method can be overridden!") )
    # end of ResourceWindow.createToolBar


    def onCopy( self ):                           # get text selected by mouse, etc.
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onCopy()") )
        if not self.textBox.tag_ranges( SEL ):       # save in cross-app clipboard
            showerror( APP_NAME, 'No text selected')
        else:
            text = self.textBox.get( SEL_FIRST, SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
    # end of ResourceWindow.onCopy


    def onSelectAll( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.onSelectAll()") )
        self.textBox.tag_add( SEL, START, END+'-1c' )   # select entire text
        self.textBox.mark_set( INSERT, START )          # move insert point to top
        self.textBox.see( INSERT )                      # scroll to top
    # end of ResourceWindow.onSelectAll


    def onGoto( self, forceline=None):
        line = forceline or askinteger( APP_NAME, _("Enter line number") )
        self.textBox.update()
        self.textBox.focus()
        if line is not None:
            maxindex = self.textBox.index( END+'-1c' )
            maxline  = int( maxindex.split('.')[0] )
            if line > 0 and line <= maxline:
                self.textBox.mark_set( INSERT, '{}.0'.format(line) ) # goto line
                self.textBox.tag_remove( SEL, START, END )          # delete selects
                self.textBox.tag_add( SEL, INSERT, 'insert + 1l' )  # select line
                self.textBox.see( INSERT )                          # scroll to line
            else:
                showerror( APP_NAME, _("No such line number") )
    # end of ResourceWindow.onGoto


    def onFind( self, lastkey=None):
        key = lastkey or askstring( APP_NAME, _("Enter search string") )
        self.textBox.update()
        self.textBox.focus()
        self.lastfind = key
        if key:
            nocase = self.optionsDict['caseinsens']
            where = self.textBox.search( key, INSERT, END, nocase=nocase )
            if not where:                                          # don't wrap
                showerror( APP_NAME, 'String not found' )
            else:
                pastkey = where + '+%dc' % len(key)           # index past key
                self.textBox.tag_remove( SEL, START, END )         # remove any sel
                self.textBox.tag_add( SEL, where, pastkey )        # select key
                self.textBox.mark_set( INSERT, pastkey )           # for next find
                self.textBox.see( where )                          # scroll display
    # end of ResourceWindow.onFind


    def onRefind( self ):
        self.onFind( self.lastfind)
    # end of ResourceWindow.onRefind


    def onInfo( self ):
        """
        pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        text  = self.getAllText()
        bytes = len( text )             # words uses a simple guess:
        lines = len( text.split('\n') ) # any separated by whitespace
        words = len( text.split() )     # 3.x: bytes is really chars
        index = self.textBox.index( INSERT ) # str is unicode code points
        where = tuple( index.split('.') )
        showinfo( APP_NAME+' Information',
                 'Current location:\n\n' +
                 'line:\t%s\ncolumn:\t%s\n\n' % where +
                 'File text statistics:\n\n' +
                 'chars:\t{}\nlines:\t{}\nwords:\t{}\n'.format( bytes, lines, words) )
    # end of ResourceWindow.onInfo


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    def isEmpty( self ):
        return not self.getAllText()
    # end of ResourceWindow.modified

    def modified( self ):
        return self.textBox.edit_modified()
    # end of ResourceWindow.modified

    def getAllText( self ):
        """ Returns all the text as a string. """
        return self.textBox.get( START, END+'-1c' )
    # end of ResourceWindow.modified

    def setAllText( self, newText ):
        """
        Sets the textBox (assumed to be enabled) to the given text
            then positions the insert cursor at the BEGINNING of the text.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        self.textBox.delete( START, END )
        self.textBox.insert( END, newText )
        self.textBox.mark_set( INSERT, START ) # move insert point to top
        self.textBox.see( INSERT ) # scroll to top, insert is set

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( FALSE ) # clear modified flag
    # end of ResourceWindow.setAllText


    def onClose( self ):
        """
        Called from the GUI.

        Can be overridden.
        """
        self.closeResourceWindow()
    # end of ResourceWindow.onClose

    def closeResourceWindow( self ):
        """
        Called to finally and irreversibly remove this window from our list and close it.
        """
        if Globals.debugFlag and debuggingThisModule: print( t("ResourceWindow.closeResourceWindow()") )
        self.parentApp.appWins.remove( self )
        self.destroy()
        if Globals.debugFlag: self.parentApp.setDebugText( "Closed resource window" )
    # end of ResourceWindow.closeResourceWindow
# end of class ResourceWindow



class ResourceWindows( list ):
    """
    Just keeps a list of the resource (Toplevel) windows.
    """
    def __init__( self, ResourceWindowsParent ):
        self.ResourceWindowsParent = ResourceWindowsParent
        list.__init__( self )


    def iconify( self ):
        if Globals.debugFlag and debuggingThisModule: print( t("ResourceWindows.iconify()") )
        for appWin in self:
            appWin.iconify()
    #end of ResourceWindows.iconify


    def iconifyResources( self ):
        if Globals.debugFlag and debuggingThisModule: print( t("ResourceWindows.iconifyResources()") )
        for appWin in self:
            if 'Resource' in appWin.genericWindowType:
                appWin.iconify()
    #end of ResourceWindows.iconifyResources


    def deiconify( self ):
        if Globals.debugFlag and debuggingThisModule: print( t("ResourceWindows.deiconify()") )
        for appWin in self:
            appWin.deiconify()
            appWin.lift( aboveThis=self.ResourceWindowsParent )
    #end of ResourceWindows.deiconify


    def updateThisBibleGroup( self, groupCode ):
        """
        Called when we probably need to update some resource windows with a new Bible reference.
        """
        if Globals.debugFlag: print( t("ResourceWindows.updateThisBibleGroup( {} )").format( groupCode ) )
        for appWin in self:
            if 'Bible' in appWin.genericWindowType: # e.g., BibleResource, BibleEditor
                if appWin.groupCode == groupCode:
                    appWin.updateShownBCV( appWin.parentApp.currentVerseKey )
    # end of ResourceWindows.updateThisBibleGroup


    def updateLexicons( self, newLexiconWord ):
        """
        Called when we probably need to update some resource windows with a new word.
        """
        if Globals.debugFlag:
            print( t("ResourceWindows.updateLexicons( {} )").format( newLexiconWord ) )
        for appWin in self:
            if appWin.genericWindowType == 'LexiconResource':
                appWin.updateLexiconWord( newLexiconWord )
    # end of ResourceWindows.updateLexicons
# end of ResourceWindows class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    if Globals.verbosityLevel > 0: print( ProgNameVersion )
    #if Globals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if Globals.debugFlag: print( t("Running demo...") )
    #Globals.debugFlag = True

    tkRootWindow = Tk()
    tkRootWindow.title( ProgNameVersion )
    #settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', ProgName )
    #settings.load()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of ResourceWindows.demo


if __name__ == '__main__':
    import multiprocessing

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

    demo()

    Globals.closedown( ProgName, ProgVersion )
# end of ResourceWindows.py
