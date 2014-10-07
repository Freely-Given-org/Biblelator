#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ResourceWindows.py
#   Last modified: 2014-10-07 (also update ProgVersion below)
#
# Base of Bible and lexicon resource windows and frames for Biblelator Bible display/editing
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
Base windows and frames to allow display and manipulation of
    Bible and lexicon resource windows.
"""

ShortProgName = "ResourceWindows"
ProgName = "Biblelator Resource Windows"
ProgVersion = "0.15"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys#, os.path, configparser, logging
from gettext import gettext as _

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
from tkinter import Toplevel, TclError, Menu, IntVar, messagebox# , Text
from tkinter import NORMAL, DISABLED, BOTTOM, LEFT, RIGHT, BOTH, YES, END, E
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Style, Frame # Sizegrip, Button, Combobox

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals

# Biblelator imports
from BiblelatorGlobals import MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE, CONTEXT_VIEW_MODES



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
            assert( genericWindowType in ('BibleResource','LexiconResource','BibleEditor') )
        self.parentApp, self.genericWindowType = parentApp, genericWindowType
        Toplevel.__init__( self, self.parentApp )
        self.protocol( "WM_DELETE_WINDOW", self.closeResourceWindow )
        self.minimumXSize, self.minimumYSize = MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE

        self.contextViewMode = 'Default'
        if 'Bible' in self.genericWindowType:
            self._viewRadio = IntVar()
            #self._viewRadio.set( 0 )
        if 'Editor' not in self.genericWindowType: # the editor creates its own
            self.createMenuBar()
            self.createContextMenu()
        #self.createToolBar()
        #self.pack( expand=1 )
        #Sizegrip( self ).pack( side=BOTTOM, anchor=E )
    # end of ResourceWindow.__init__


    def notWrittenYet( self ):
        messagebox.showerror( _("Not implemented"), _("Not yet available, sorry") )
    # end of ResourceWindow.notWrittenYet


    def changeBibleContextView( self ):
        """
        Called when  a Bible context view is changed from the menus/GUI.
        """
        currentViewNumber = self._viewRadio.get()
        if Globals.debugFlag:
            print( t("changeBibleContextView( {} ) from {}").format( repr(currentViewNumber), repr(self.contextViewMode) ) )
            assert( currentViewNumber in range( 1, 4+1 ) )
        previousContextViewMode = self.contextViewMode
        if 'Bible' in self.genericWindowType:
            if currentViewNumber == 1: self.contextViewMode = CONTEXT_VIEW_MODES[0] # 'BeforeAndAfter'
            elif currentViewNumber == 2: self.contextViewMode = CONTEXT_VIEW_MODES[1] # 'ByVerse'
            elif currentViewNumber == 3: self.contextViewMode = CONTEXT_VIEW_MODES[2] # 'ByBook'
            elif currentViewNumber == 4: self.contextViewMode = CONTEXT_VIEW_MODES[3] # 'ByChapter'
            else: halt # unknown Bible view mode
        else: halt # window type view mode not handled yet
        if self.contextViewMode != previousContextViewMode: # we need to update our view
            if   self.groupCode == 'A': windowVerseKey = self.parentApp.GroupA_VerseKey
            elif self.groupCode == 'B': windowVerseKey = self.parentApp.GroupB_VerseKey
            elif self.groupCode == 'C': windowVerseKey = self.parentApp.GroupC_VerseKey
            elif self.groupCode == 'D': windowVerseKey = self.parentApp.GroupD_VerseKey
            self.resourceFrame.updateShownBCV( windowVerseKey )
    # end of ResourceWindow.changeBibleContextView


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
        #self.win = Toplevel( self )
        self.menubar = Menu( self )
        #self['menu'] = self.menubar
        self.config( menu=self.menubar ) # alternative

        fileMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label='File', underline=0 )
        #fileMenu.add_command( label='New...', underline=0, command=self.notWrittenYet )
        #fileMenu.add_command( label='Open...', underline=0, command=self.notWrittenYet )
        #fileMenu.add_separator()
        #subfileMenuImport = Menu( fileMenu )
        #subfileMenuImport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Import', underline=0, menu=subfileMenuImport )
        #subfileMenuExport = Menu( fileMenu )
        #subfileMenuExport.add_command( label='USX', underline=0, command=self.notWrittenYet )
        #subfileMenuExport.add_command( label='HTML', underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label='Export', underline=0, menu=subfileMenuExport )
        #fileMenu.add_separator()
        fileMenu.add_command( label='Close', underline=0, command=self.closeResourceWindow ) # close this window

        editMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=editMenu, label='Edit', underline=0 )
        editMenu.add_command( label='Copy...', underline=0, command=self.notWrittenYet )
        editMenu.add_separator()
        editMenu.add_command( label='Find...', underline=0, command=self.notWrittenYet )

        gotoMenu = Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label='Goto', underline=0 )
        if 'Bible' in self.genericWindowType:
            gotoMenu.add_command( label='Previous book', underline=0, command=self.notWrittenYet )
            gotoMenu.add_command( label='Next book', underline=0, command=self.notWrittenYet )
            gotoMenu.add_command( label='Previous chapter', underline=0, command=self.notWrittenYet )
            gotoMenu.add_command( label='Next chapter', underline=0, command=self.notWrittenYet )
            gotoMenu.add_command( label='Previous verse', underline=0, command=self.notWrittenYet )
            gotoMenu.add_command( label='Next verse', underline=0, command=self.notWrittenYet )
            gotoMenu.add_separator()
            gotoMenu.add_command( label='Forward', underline=0, command=self.notWrittenYet )
            gotoMenu.add_command( label='Backward', underline=0, command=self.notWrittenYet )
            gotoMenu.add_separator()
            gotoMenu.add_command( label='Previous list item', underline=0, command=self.notWrittenYet )
            gotoMenu.add_command( label='Next list item', underline=0, command=self.notWrittenYet )
            gotoMenu.add_separator()
            gotoMenu.add_command( label='Book', underline=0, command=self.notWrittenYet )

        viewMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label='View', underline=0 )
        if 'Bible' in self.genericWindowType:
            if   self.contextViewMode == 'BeforeAndAfter': self._viewRadio.set( 1 )
            elif self.contextViewMode == 'ByVerse': self._viewRadio.set( 2 )
            elif self.contextViewMode == 'ByBook': self._viewRadio.set( 3 )
            elif self.contextViewMode == 'ByChapter': self._viewRadio.set( 4 )

            viewMenu.add_radiobutton( label='Before and after...', underline=7, value=1, variable=self._viewRadio, command=self.changeBibleContextView )
            viewMenu.add_radiobutton( label='Single verse', underline=7, value=2, variable=self._viewRadio, command=self.changeBibleContextView )
            viewMenu.add_radiobutton( label='Whole book', underline=6, value=3, variable=self._viewRadio, command=self.changeBibleContextView )
            viewMenu.add_radiobutton( label='Whole chapter', underline=6, value=4, variable=self._viewRadio, command=self.changeBibleContextView )

        toolsMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label='Tools', underline=0 )
        toolsMenu.add_command( label='Options...', underline=0, command=self.notWrittenYet )

        windowMenu = Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label='Window', underline=0 )
        windowMenu.add_command( label='Bring in', underline=0, command=self.notWrittenYet )

        helpMenu = Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, underline=0, label='Help' )
        helpMenu.add_command( label='Help...', underline=0, command=self.doHelp )
        helpMenu.add_separator()
        helpMenu.add_command( label='About...', underline=0, command=self.doAbout )

        #filename = filedialog.askopenfilename()
        #filename = filedialog.asksaveasfilename()
        #dirname = filedialog.askdirectory()
        #colorchooser.askcolor(initialcolor='#ff0000')
        #messagebox.showinfo(message='Have a good day')
        #messagebox.askyesno( message='Are you sure you want to install SuperVirus?' icon='question' title='Install' )
    # end of ResourceWindow.createMenuBar


    def createContextMenu( self ):
        """
        """
        self.contextMenu = Menu( self, tearoff=0 )
        self.contextMenu.add_command( label="Copy", underline=0, command=self.notWrittenYet )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Close", underline=0, command=self.closeResourceWindow )

        self.bind( "<Button-3>", self.showContextMenu ) # right-click
        #self.pack()
    # end of ResourceWindow.createContextMenu


    def showContextMenu(self, e):
        self.contextMenu.post( e.x_root, e.y_root )
    # end of ResourceWindow.showContextMenu


    #def createToolBar( self ):
        #if Globals.debugFlag and debuggingThisModule: print( t("ResourceWindow.createToolBar()") )
        #toolbar = Frame( self, cursor='hand2', relief=RAISED ) # bd=2
        #toolbar.pack( side=BOTTOM, fill=X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=LEFT )
    ## end of ResourceWindow.createToolBar


    def closeResourceWindow( self ):
        """
        """
        if Globals.debugFlag and debuggingThisModule: print( t("ResourceWindow.closeResourceWindow()") )
        self.parentApp.appWins.remove( self )
        self.destroy()
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
# end of ResourceWindows class



class ResourceFrames( list ):
    """
    These are the frames where most of the work is done
        in displaying resources and their controls.
    """
    def updateShownBCV( self, groupCode ):
        """
        Called when we probably need to update some resource frames with a new Bible reference.
        """
        if Globals.debugFlag: print( t("ResourceFrames.updateShownBCV( {} )").format( groupCode ) )
        for resourceFrame in self:
            if 'Bible' in resourceFrame.ResourceFrameParent.genericWindowType:
                if resourceFrame.resourceWindowParent.groupCode == groupCode:
                    resourceFrame.updateShownBCV( resourceFrame.ResourceFrameParent.parentApp.currentVerseKey )
    # end of ResourceFrames.updateShownBCV
# end of ResourceFrames class



class ResourceFrame( Frame ):
    def __init__( self, parent ):
        #if Globals.debugFlag: print( "ResourceFrame.__init__( {} )".format( parent ) )
        self.ResourceFrameParent = parent
        Frame.__init__( self, self.ResourceFrameParent )
        self.minimumXSize, self.minimumYSize = MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE
        self.ResourceFrameParent.minsize( self.minimumXSize, self.minimumYSize )
        self.pack( expand=YES, fill=BOTH )
        self.createResourceFrameWidgets()
        #self.updateText( "Hello there" )
        #Sizegrip( self ).pack( side=BOTTOM, anchor=E )
    # end of ResourceFrame.__init__

    def __str__( self ):
        """
        """
        resultString = ""
        #print( "dir", dir(self) )
        for tryThis in ('moduleAbbreviation','modulePath','editModulePath','lexiconPath',):
            if tryThis in dir(self):
                #print( "got", repr(tryThis) )
                resultString += ('\n    ' if resultString else '') + '{} = {}'.format( tryThis, repr(self.__getattribute__(tryThis)) )
        return resultString
    # end of ResourceFrame.__str__


    def createResourceFrameWidgets( self ):
        #self.label1 = Label( self, text=self.moduleAbbreviation )
        #self.label1.pack()

        #self.hi_there = Button( self )
        #self.hi_there['text'] = "Refresh"
        #self.hi_there["command"] = self.update
        #self.hi_there.pack(side="top")

        #self.bStyle = Style( self )
        #self.bStyle.configure( "Red.TButton", foreground="red", background="white" )
        #self.bStyle.map("Red.TButton",
                        #foreground=[('pressed', 'red'), ('active', 'blue')],
                        #background=[('pressed', '!disabled', 'black'), ('active', 'white')] )

        self.textBox = ScrolledText( self, state=DISABLED )
        self.textBox['wrap'] = 'word'
        #self.textBox.grid( sticky=N+E+S+W ) #.pack( expand=1 )
        self.textBox.pack( expand=YES, fill=BOTH )
        #self.textBox['state'] = DISABLED # Don't allow editing

        #self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.closeResourceFrame)
        #self.QUIT.pack( side="bottom" )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
        #Sizegrip( self ).pack( side="right" )#.grid( column=999, row=999, sticky=(S,E) )#
    # end of ResourceFrame.createApplicationWidgets


    def clearText( self ): # Leaves in normal state
        self.textBox['state'] = NORMAL
        self.textBox.delete( '1.0', END )
    # end of ResourceFrame.updateText


    def destroy( self ): # override so we can remove this frame from our list
        if Globals.debugFlag and debuggingThisModule: print( t("ResourceFrame.destroy()") )
        self.ResourceFrameParent.parentApp.projFrames.remove( self )
        Frame.destroy( self )
    # end of ResourceFrame.closeResourceFrame
# end of ResourceFrame class



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