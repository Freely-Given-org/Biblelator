#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ResourceWindows.py
#   Last modified: 2014-09-25 (also update ProgVersion below)
#
# Bible and lexicon resource windows for Biblelator Bible display/editing
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
Windows and frames to allow display and manipulation of
    Bible and lexicon resource windows.
"""

ProgName = "Biblelator Resource Windows"
ProgVersion = "0.11"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys#, os.path, configparser, logging
from gettext import gettext as _

# Importing this way means that we have to manually choose which
#       widgets that we use (if there's one in each set)
from tkinter import Toplevel, Menu, Text, StringVar, messagebox
from tkinter import NORMAL, DISABLED, LEFT, RIGHT, BOTH, YES
from tkinter.ttk import Style, Frame#, Button, Combobox
#from tkinter.tix import Spinbox

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import Globals

# Biblelator imports
from BiblelatorGlobals import MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE



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



class ResourceWindow( Toplevel ):
    def __init__( self, parent, windowType ):
        if Globals.debugFlag:
            print( "ResourceWindow.__init__( {} {} )".format( parent, repr(windowType) ) )
            assert( parent )
            assert( windowType in ('BibleResource','LexiconResource','Editor') )
        self.AppWindowParent, self.windowType = parent, windowType
        Toplevel.__init__( self, self.AppWindowParent )
        self.minimumXSize, self.minimumYSize = MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE
        #self.pack( expand=1 )
    # end of ResourceWindow.__init__
# end of class ResourceWindow



class ResourceWindows( list ):
    """
    Just keeps a list of the resource (Toplevel) windows.
    """
    def iconify( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("ResourceWindows.iconify()") )
        for appWin in self:
            appWin.iconify()
    #end of ResourceWindows.iconify

    def iconifyResources( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("ResourceWindows.iconifyResources()") )
        for appWin in self:
            if 'Resource' in appWin.windowType:
                appWin.iconify()
    #end of ResourceWindows.iconifyResources

    def deiconify( self ):
        if Globals.debugFlag and debuggingThisModule:
            print( t("ResourceWindows.deiconify()") )
        for appWin in self:
            appWin.deiconify()
    #end of ResourceWindows.deiconify
# end of ResourceWindows class



class ResourceFrames( list ):
    """
    These are the frames where most of the work is done
        in displaying resources and their controls.
    """
    def update( self ):
        if Globals.debugFlag: print( "ResourceFrames.update()" )
        for projWin in self:
            projWin.update()
    # end of ResourceFrames.update
# end of ResourceFrames class



class ResourceFrame( Frame ):
    def __init__( self, parent=None ):
        if Globals.debugFlag: print( "ResourceFrame.__init__( {} )".format( parent ) )
        self.ResourceFrameParent = parent
        Frame.__init__( self, self.ResourceFrameParent )
        #self.grid( sticky=W+E+N+S ) #.pack( expand=1 )
        self.minimumXSize, self.minimumYSize = MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE
        self.ResourceFrameParent.minsize( self.minimumXSize, self.minimumYSize )
        self.pack( expand=YES, fill=BOTH )
        self.createResourceFrameWidgets()
        #self.updateText( "Hello there" )
    # end of ResourceFrame.__init__

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

        self.textBox = Text( self, state=DISABLED )
        self.textBox['wrap'] = 'word'
        #self.textBox.grid( sticky=N+E+S+W ) #.pack( expand=1 )
        self.textBox.pack( expand=YES, fill=BOTH )
        #self.textBox['state'] = 'disabled' # Don't allow editing

        #self.QUIT = Button( self, text="Close", style="Red.TButton", command=self.closeResourceFrame)
        #self.QUIT.pack( side="bottom" )

        #Sizegrip( self ).grid( column=999, row=999, sticky=(S,E) )
        #Sizegrip( self ).pack( side="right" )#.grid( column=999, row=999, sticky=(S,E) )#
    # end of ResourceFrame.createApplicationWidgets

    def clearText( self ): # Leaves in normal state
        self.textBox['state'] = 'normal'
        self.textBox.delete( '1.0', 'end' )
    # end of ResourceFrame.updateText

    def closeResourceFrame( self ):
        #self.appWins.remove( self )
        self.destroy()
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
    settings = ApplicationSettings( 'BiblelatorData/', 'BiblelatorSettings/', ProgName )
    settings.load()

    application = Application( parent=tkRootWindow, settings=settings )
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
