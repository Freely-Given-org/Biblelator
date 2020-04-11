#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ESFMEditWindow.py
#
# The actual edit windows for Biblelator text editing and USFM/ESFM Bible editing
#
# Copyright (C) 2013-2018 Robert Hunt
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
xxx to allow editing of USFM Bibles using Python3 and Tkinter.
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2018-03-15' # by RJH
SHORT_PROGRAM_NAME = "ESFMEditWindow"
PROGRAM_NAME = "Biblelator ESFM Edit Window"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

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
from Biblelator.Windows.USFMEditWindow import USFMEditWindow

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint

#from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
#from BibleOrgSys.BibleWriter import setDefaultControlFolderpath



class ESFMEditWindow( USFMEditWindow ):
    pass
# end of ESFMEditWindow class



def demo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    eEW = ESFMEditWindow( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of ESFMEditWindow.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of ESFMEditWindow.py
