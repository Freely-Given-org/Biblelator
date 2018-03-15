#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorSimpleDialogs.py
#
# Various dialog windows for Biblelator Bible display/editing
#
# Copyright (C) 2013-2018 Robert Hunt
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
Various simple modal dialog windows for Biblelator Bible warnings and errors.

    def showError( parentWindow, title, errorText )
    def showWarning( parentWindow, title, warningText )
    def showInfo( parentWindow, title, infoText )
"""

from gettext import gettext as _

LastModifiedDate = '2018-03-15'
ShortProgName = "BiblelatorSimpleDialogs"
ProgName = "Biblelator simple dialogs"
ProgVersion = '0.44'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import logging

import tkinter as tk
import tkinter.messagebox as tkMsgBox

# BibleOrgSys imports
if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals



def showError( parentWindow, title, errorText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag:
        print( "showError( {}, {!r}, {!r} )".format( parentWindow, title, errorText ) )

    logging.error( '{}: {}'.format( title, errorText ) )
    parentWindow.parentApp.setStatus( _("Waiting for user input after error…") )
    tkMsgBox.showerror( title, errorText, parentWindow=parentWindow )
    parentWindow.parentApp.setReadyStatus()
# end of BiblelatorSimpleDialogs.showError


def showWarning( parentWindow, title, warningText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag:
        print( "showWarning( {}, {!r}, {!r} )".format( parentWindow, title, warningText ) )

    logging.warning( '{}: {}'.format( title, warningText ) )
    parentWindow.parentApp.setStatus( _("Waiting for user input after warning…") )
    tkMsgBox.showwarning( title, warningText, parentWindow=parentWindow )
    parentWindow.parentApp.setReadyStatus()
# end of BiblelatorSimpleDialogs.showWarning


def showInfo( parentWindow, title, infoText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "showInfo( {}, {!r}, {!r} )".format( parentWindow, title, infoText ) )
        infoText += '\n\nWindow parameters:\n'
        for configKey, configTuple  in sorted(parentWindow.configure().items()): # Append the parentWindow window config info
            if debuggingThisModule:
                print( "showInfo: {!r}={} ({})".format( configKey, configTuple, len(configTuple) ) )
            if len(configTuple)>2: # don't append alternative names like, bg for background
                # Don't display the last field if it just duplicates the previous one
                infoText += '  {}: {!r}{}\n'.format( configTuple[2], configTuple[3],
                                            '' if configTuple[4]==configTuple[3] else ', {!r}'.format( configTuple[4] ) )
            elif debuggingThisModule: # append alternative names like, bg for background
                # Don't display the last field if it just duplicates the previous one
                infoText += '  {}={!r}\n'.format( configTuple[0], configTuple[1] )

    logging.info( '{}: {}'.format( title, infoText ) )
    parentWindow.parentApp.setStatus( _("Waiting for user input after info…") )
    tkMsgBox.showinfo( title, infoText, parentWindow=parentWindow )
    parentWindow.parentApp.setReadyStatus()
# end of BiblelatorSimpleDialogs.showInfo



def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )

    # Doesn't quite work yet :-(
    tkWindow = tk.Toplevel( tkRootWindow )
    tkWindow.parentApp = tkRootWindow
    tkRootWindow.setStatus = lambda s: s
    showError( tkWindow, "Test Error", "This is just a test of an error box!" )
    showWarning( tkWindow, "Test Warning", "This is just a test of an warning box!" )
    showInfo( tkWindow, "Test Info", "This is just a test of an info box!" )
    #tkRootWindow.quit()

    # Start the program running
    #tkRootWindow.mainloop()
# end of BiblelatorSimpleDialogs.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BiblelatorSimpleDialogs.py
