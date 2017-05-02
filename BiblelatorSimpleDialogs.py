#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorSimpleDialogs.py
#
# Various dialog windows for Biblelator Bible display/editing
#
# Copyright (C) 2013-2017 Robert Hunt
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

    def showError( parent, title, errorText )
    def showWarning( parent, title, warningText )
    def showInfo( parent, title, infoText )
"""

from gettext import gettext as _

LastModifiedDate = '2017-04-11'
ShortProgName = "BiblelatorSimpleDialogs"
ProgName = "Biblelator simple dialogs"
ProgVersion = '0.40'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import logging

import tkinter as tk
import tkinter.messagebox as tkmb

# BibleOrgSys imports
import BibleOrgSysGlobals



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
    return '{}{}'.format( nameBit+': ' if nameBit else '', errorBit )
# end of exp



def showError( parent, title, errorText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("showError( {}, {!r}, {!r} )").format( parent, title, errorText ) )

    logging.error( '{}: {}'.format( title, errorText ) )
    parent.parentApp.setStatus( _("Waiting for user input after error…") )
    tkmb.showerror( title, errorText, parent=parent )
    parent.parentApp.setReadyStatus()
# end of showError


def showWarning( parent, title, warningText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("showWarning( {}, {!r}, {!r} )").format( parent, title, warningText ) )

    logging.warning( '{}: {}'.format( title, warningText ) )
    parent.parentApp.setStatus( _("Waiting for user input after warning…") )
    tkmb.showwarning( title, warningText, parent=parent )
    parent.parentApp.setReadyStatus()
# end of showWarning


def showInfo( parent, title, infoText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("showInfo( {}, {!r}, {!r} )").format( parent, title, infoText ) )
        infoText += '\n\nWindow parameters:\n'
        for configKey, configTuple  in sorted(parent.configure().items()): # Append the parent window config info
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
    parent.parentApp.setStatus( _("Waiting for user input after info…") )
    tkmb.showinfo( title, infoText, parent=parent )
    parent.parentApp.setReadyStatus()
# end of showInfo



def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo…") )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )

    #swnd = SaveWindowNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test SWND" )
    #print( "swndResult", swnd.result )
    #dwnd = DeleteWindowNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test DWND" )
    #print( "dwndResult", dwnd.result )
    srb = SelectResourceBoxDialog( tkRootWindow, [(x,y) for x,y, in {"ESV":"ENGESV","WEB":"ENGWEB","MS":"MBTWBT"}.items()], "Test SRB" )
    print( "srbResult", srb.result )

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


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BiblelatorSimpleDialogs.py
