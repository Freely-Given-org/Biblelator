#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ESFMEditWindow.py
#
# The actual edit windows for Biblelator text editing and USFM/ESFM Bible editing
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
xxx to allow editing of USFM Bibles using Python3 and Tkinter.
"""

from gettext import gettext as _

LastModifiedDate = '2018-03-15' # by RJH
ShortProgName = "ESFMEditWindow"
ProgName = "Biblelator ESFM Edit Window"
ProgVersion = '0.44'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True

#import sys #, os.path, logging #, re
#from collections import OrderedDict
#import multiprocessing

import tkinter as tk
#from tkinter.simpledialog import askstring, askinteger
#from tkinter.filedialog import asksaveasfilename
#from tkinter.colorchooser import askcolor
#from tkinter.ttk import Style, Frame

# Biblelator imports
#from BiblelatorGlobals import APP_NAME, DATA_FOLDER_NAME, tkSTART, DEFAULT, EDIT_MODE_NORMAL, EDIT_MODE_USFM, BIBLE_GROUP_CODES
#from BiblelatorDialogs import YesNoDialog, OkCancelDialog, GetBibleBookRangeDialog
#from BiblelatorHelpers import createEmptyUSFMBookText, calculateTotalVersesForBook, mapReferenceVerseKey, mapParallelVerseKey
#from TextBoxes import CustomText
#from BibleResourceWindows import BibleBox, BibleResourceWindow
#from BibleReferenceCollection import BibleReferenceCollectionWindow
from USFMEditWindow import USFMEditWindow

# BibleOrgSys imports
if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
#from VerseReferences import SimpleVerseKey
#from BibleWriter import setDefaultControlFolder



class ESFMEditWindow( USFMEditWindow ):
    pass
# end of ESFMEditWindow class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    eEW = ESFMEditWindow( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of ESFMEditWindow.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of ESFMEditWindow.py
