#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorDialogs.py
#
# Various dialog windows for Biblelator Bible display/editing
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
Various modal dialog windows for Biblelator Bible display/editing.

    #class HTMLDialog( ModalDialog )
        #__init__( self, parentWindow, text, title=None )
    class YesNoDialog( ModalDialog )
        __init__( self, parentWindow, message, title=None )
    class OkCancelDialog( ModalDialog )
        __init__( self, parentWindow, message, title=None )

    class BookNameDialog( ModalDialog )
        __init__( self, parentWindow, bookNameList, currentIndex )
    class NumberButtonDialog( ModalDialog ):
        A dialog box which allows the user to select a number from a given range.
        This is used in touch mode to select chapter and/or verse numbers.
        __init__( self, parentWindow, startNumber, endNumber, currentNumber )

    class SaveWindowsLayoutNameDialog( ModalDialog )
        __init__( self, parentWindow, existingSettings, title )
    class DeleteWindowsLayoutNameDialog( ModalDialog )
        __init__( self, parentWindow, existingSettings, title )

    class SelectResourceBoxDialog( ModalDialog )
        Given a list of available resources, select one and return the list item.
        __init__( self, parentWindow, availableSettingsList, title )
    class GetNewProjectNameDialog( ModalDialog )
        Get the name and an abbreviation for a new Biblelator project.
        __init__( self, parentWindow, title )
    class CreateNewProjectFilesDialog( ModalDialog )
        Find if they want blank files created for a new Biblelator project.
        __init__( self, parentWindow, title, currentBBB, availableVersifications )
    class GetNewCollectionNameDialog( ModalDialog )
        __init__( self, parentWindow, existingNames, title )
    class RenameResourceCollectionDialog( ModalDialog )
        Get the new name for a resource collection.
        __init__( self, parentWindow, existingName, existingNames, title )
    class GetBibleBookRangeDialog( ModalDialog )
        __init__( self, parentWindow, givenBible, currentBBB, currentList, title )
    class SelectIndividualBibleBooksDialog( ModalDialog )
        __init__( self, parentWindow, availableList, currentList, title )

    class GetBibleFindTextDialog( ModalDialog )
        Get the search string (and options) for Bible search.
        __init__( self, parentWindow, givenBible, optionsDict, title )
    class GetBibleReplaceTextDialog( ModalDialog )
        Get the Find and Replace strings (and options) for Bible Replace.
        __init__( self, parentWindow, givenBible, optionsDict, title )
    class ReplaceConfirmDialog( ModalDialog )
        __init__( self, parentWindow, referenceString, contextBefore, findText, contextAfter, finalText, haveUndos, title )

    class SelectInternalBibleDialog( ModalDialog )
        Select one internal Bible from a given list.
        __init__( self, parentWindow, title, internalBibles )
    #class GetSwordPathDialog( ModalDialog )

    class GetHebrewGlossWordDialog( ModalDialog )
        Get a new (gloss) word from the user.
        Accepts a bundle (e.g., list, tuple) of short strings to display to the user first.
        Unlike our other dialogues, this one can remember its size and position.
        Returns:
            S for skip,
            or None for cancel,
            or else a dictionary possibly containing 'word','command','geometry'
        __init__( self, parentWindow, title, contextLines, word='', geometry=None )
    class GetHebrewGlossWordsDialog( GetHebrewGlossWordDialog )
        Get up to two new (gloss) words from the user.
            The first one (usually generic gloss) is compulsory.
            The second one (usually specific gloss) is optional.
        Accepts a bundle (e.g., list, tuple) of short strings to display to the user first.
        Unlike our other dialogues, this one can remember its size and position.
        Returns:
            S for skip,
            or None for cancel,
            or else a dictionary possibly containing 'word1','word2','command','geometry'
        __init__( self, parentWindow, title, contextLines, word1='', word2='', geometry=None )

    class ChooseResourcesDialog( ModalDialog )
        Given a list of available resources, select one and return the list item.
        __init__( self, parentWindow, availableResourceDictsList, title )
    class DownloadResourcesDialog( ModalDialog )
        Given a list of available downloadable resources (new or updates),
            select one or more and download it/them.
        Return result = number of successful downloads
        __init__( self, parentWindow, title )

TODO: Put title parameter consistently after parentWindow parameter.

TODO: Work out how to automatically test keypresses in dialogs.
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2019-09-19'
SHORT_PROGRAM_NAME = "BiblelatorDialogs"
PROGRAM_NAME = "Biblelator dialogs"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


import os
import logging
import urllib.request

import tkinter as tk
import tkinter.font as tkFont
from tkinter.ttk import Style, Label, Radiobutton, Button, Frame

# Biblelator imports
from Biblelator.BiblelatorGlobals import APP_NAME, errorBeep
from Biblelator.Dialogs.ModalDialog import ModalDialog
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showWarning
from Biblelator.Windows.TextBoxes import BEntry, BCombobox, BText

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
from BibleOrgSys.Formats.PickledBible import ZIPPED_PICKLE_FILENAME_END



#class HTMLDialog( ModalDialog ):
    #"""
    #"""
    #def __init__( self, parentWindow, text, title=None ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "HTMLDialog.__init__( {}, {!r}, {!r} )".format( parentWindow, text, title ) )

        #self.text = text
        #ModalDialog.__init__( self, parentWindow, title )
    ## end of HTMLDialog.__init__


    #def makeBody( self, master ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "HTMLDialog.makeBody( {} )".format( master ) )

        #html = HTMLTextBox( master )
        #html.grid( row=0 )
        #html.insert( tk.END, self.text )
        #return html
    ## end of HTMLDialog.makeBody
## end of class HTMLDialog



class YesNoDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, message, title=None ):
        """
        """
        self.message = message
        ModalDialog.__init__( self, parentWindow, title, okText=_("Yes"), cancelText=_("No") )
    # end of YesNoDialog.__init__


    def makeBody( self, master ):
        """
        """
        label = Label( master, text=self.message )
        label.grid( row=0 )
        return label
    # end of YesNoDialog.makeBody
# end of class YesNoDialog



class OkCancelDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, message, title=None ):
        """
        """
        self.message = message
        ModalDialog.__init__( self, parentWindow, title, okText=_("Ok"), cancelText=_("Cancel") )
    # end of OkCancelDialog.__init__


    def makeBody( self, master ):
        """
        """
        label = Label( master, text=self.message )
        label.grid( row=0 )
        return label
    # end of OkCancelDialog.makeBody
# end of class OkCancelDialog



class BookNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, bookNameList, currentIndex ): #, message, title=None ):
        """
        """
        #print( 'currentIndex', currentIndex )
        self.bookNameList, self.currentIndex = bookNameList, currentIndex
        ModalDialog.__init__( self, parentWindow ) #, title, okText=_("Ok"), cancelText=_("Cancel") )
    # end of BookNameDialog.__init__


    def makeButtonBox( self ):
        """
        Do our custom buttonBox (without an ok button)
        """
        box = Frame( self )
        w = Button( box, text=self.cancelText, width=10, command=self.cancel )
        w.pack( side=tk.LEFT, padx=5, pady=5 )
        self.bind( '<Escape>', self.cancel )
        box.pack( side=tk.BOTTOM )
    # end of BookNameDialog.makeButtonBox


    def makeBody( self, master ):
        """
        Adapted from http://stackoverflow.com/questions/7591294/how-to-create-a-self-resizing-grid-of-buttons-in-tkinter
        """
        buttonsAcross = 5
        numBooks = len( self.bookNameList )
        if numBooks > 100: buttonsAcross = 12
        elif numBooks > 80: buttonsAcross = 10
        elif numBooks > 60: buttonsAcross = 8
        elif numBooks > 30: buttonsAcross = 6
        xPad, yPad = 6, 8

        grid=Frame( master )
        grid.grid( column=0, row=7, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W )
        tk.Grid.rowconfigure( master, 7, weight=1 )
        tk.Grid.columnconfigure( master, 0, weight=1 )

        Style().configure( 'bN.TButton', background='lightgreen' )
        Style().configure( 'selectedBN.TButton', background='orange' )
        for j,bookName in enumerate(self.bookNameList):
            row, col = j // buttonsAcross, j % buttonsAcross
            #print( j, row, col )
            Button( master, width=6, text=bookName,
                                style='selectedBN.TButton' if j==self.currentIndex else 'bN.TButton', \
                                command=lambda which=j: self.apply(which) ) \
                        .grid( column=col, row=row, padx=xPad, pady=yPad, sticky=tk.N+tk.S+tk.E+tk.W )
        #col += 1
        #if col >= buttonsAcross: row +=1; col=0
        #Button( master, text=_("Cancel"), command=lambda which='CANCEL': self.apply(which) ) \
                    #.grid( column=col, row=row, padx=xPad, pady=yPad, sticky=tk.N+tk.S+tk.E+tk.W )

        for x in range(10):
            tk.Grid.columnconfigure( master, x, weight=1 )
        for y in range(5):
            tk.Grid.rowconfigure( master, y, weight=1 )
        #for j,bookName in enumerate(self.bookNameList):
            #Button( master, width=6, text=bookName, style='bN.TButton', command=lambda which=j: self.apply(which) ) \
                        #.grid()
        #return 0
    # end of BookNameDialog.makeBody


    def apply( self, buttonNumber ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        #if buttonNumber!='CANCEL': self.result = buttonNumber
        self.result = buttonNumber
        self.cancel() # We want to exit the dialog immediately
    # end of BookNameDialog.apply
# end of class BookNameDialog



class NumberButtonDialog( ModalDialog ):
    """
    A dialog box which allows the user to select a number from a given range.

    This is used in touch mode to select chapter and/or verse numbers.
    """
    def __init__( self, parentWindow, startNumber, endNumber, currentNumber ): #, message, title=None ):
        """
        """
        #print( 'NumberButtonDialog', repr(startNumber), repr(endNumber), repr(currentNumber) )
        self.startNumber, self.endNumber, self.currentNumber = startNumber, endNumber, currentNumber
        ModalDialog.__init__( self, parentWindow ) #, title, okText=_("Ok"), cancelText=_("Cancel") )
    # end of NumberButtonDialog.__init__


    def makeButtonBox( self ):
        """
        Do our custom buttonBox (without an ok button)
        """
        box = Frame( self )
        w = Button( box, text=self.cancelText, width=10, command=self.cancel )
        w.pack( side=tk.LEFT, padx=5, pady=5 )
        self.bind( '<Escape>', self.cancel )
        box.pack( side=tk.BOTTOM )
    # end of NumberButtonDialog.makeButtonBox


    def makeBody( self, master ):
        """
        Adapted from http://stackoverflow.com/questions/7591294/how-to-create-a-self-resizing-grid-of-buttons-in-tkinter
        """
        buttonsAcross = 5
        if self.endNumber > 90: buttonsAcross = 8
        elif self.endNumber > 30: buttonsAcross = 6
        xPad, yPad = 6, 8

        grid=Frame( master )
        grid.grid( column=0, row=7, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W )
        tk.Grid.rowconfigure( master, 7, weight=1 )
        tk.Grid.columnconfigure( master, 0, weight=1 )

        Style().configure( 'n.TButton', background='lightgreen' )
        Style().configure( 'selectedN.TButton', background='orange' )
        for j in range( self.startNumber, self.endNumber+1 ):
            row, col = j // buttonsAcross, j % buttonsAcross
            #print( j, row, col )
            Button( master, width=3, text=j,
                                style='selectedN.TButton' if j==self.currentNumber else 'n.TButton', \
                                command=lambda which=j: self.apply(which) ) \
                        .grid( column=col, row=row, padx=xPad, pady=yPad, sticky=tk.N+tk.S+tk.E+tk.W )
        #col += 1
        #if col >= buttonsAcross: row +=1; col=0
        #Button( master, text=_("Cancel"), command=lambda which='CANCEL': self.apply(which) ) \
                    #.grid( column=col, row=row, padx=xPad, pady=yPad, sticky=tk.N+tk.S+tk.E+tk.W )

        for x in range(10):
            tk.Grid.columnconfigure( master, x, weight=1 )
        for y in range(5):
            tk.Grid.rowconfigure( master, y, weight=1 )
        #for j,bookName in enumerate(self.bookNameList):
            #Button( master, width=6, text=bookName, style='bN.TButton', command=lambda which=j: self.apply(which) ) \
                        #.grid()
        #return 0
    # end of NumberButtonDialog.makeBody


    def apply( self, buttonNumber ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        #if buttonNumber!='CANCEL': self.result = buttonNumber
        self.result = buttonNumber
        self.cancel() # We want to exit the dialog immediately
    # end of NumberButtonDialog.apply
# end of class NumberButtonDialog



class SaveWindowsLayoutNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, existingSettings, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "SaveWindowsLayoutNameDialog…" )
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parentWindow, title )
    # end of SaveWindowsLayoutNameDialog.__init__


    def makeBody( self, master ):
        """
        """
        t1 = _("Enter a new name to save windows set-up")
        if self.haveExisting: t1 += ', ' + _("or choose an existing name to overwrite")
        Label( master, text=t1 ).grid( row=0 )

        #cbValues = [_("Enter (optional) new name") if self.haveExisting else _("Enter new set-up name")]
        cbValues = []
        if self.haveExisting:
            for existingName in self.existingSettings:
                if existingName != 'Current':
                    cbValues.append( existingName)
        self.cb = BCombobox( master, values=cbValues )
        #self.cb.current( 0 )
        self.cb.grid( row=1 )

        return self.cb # initial focus
    # end of SaveWindowsLayoutNameDialog.makeBody


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        result = self.cb.get()
        if not result: return False
        if not isinstance( result, str ): return False
        for char in '[]':
            if char in result: return False
        return True
    # end of SaveWindowsLayoutNameDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = self.cb.get()
        #print( "New window set-up name is: {!r}".format( self.result ) )
    # end of SaveWindowsLayoutNameDialog.apply
# end of class SaveWindowsLayoutNameDialog



class DeleteWindowsLayoutNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, existingSettings, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "DeleteWindowsLayoutNameDialog…" )
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parentWindow, title, _("Delete") )
    # end of DeleteWindowsLayoutNameDialog.__init__


    def makeBody( self, master ):
        """
        """
        Label( master, text=_("Use to delete a saved windows set-up") ).grid( row=0 )

        #cbValues = [_("Enter (optional) new name") if self.haveExisting else _("Enter new set-up name")]
        cbValues = []
        if self.haveExisting:
            for existingName in self.existingSettings:
                if existingName != 'Current':
                    cbValues.append( existingName)
        self.cb = BCombobox( master, state='readonly', values=cbValues )
        #self.cb.current( 0 )
        self.cb.grid( row=1 )

        return self.cb # initial focus
    # end of DeleteWindowsLayoutNameDialog.makeBody


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        result = self.cb.get()
        if not result: return False
        if not isinstance( result, str ): return False
        return True
    # end of DeleteWindowsLayoutNameDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = self.cb.get()
        print( "Requested window set-up name is: {!r}".format( self.result ) )
    # end of DeleteWindowsLayoutNameDialog.apply
# end of class DeleteWindowsLayoutNameDialog



class SelectResourceBoxDialog( ModalDialog ):
    """
    Given a list of available resources, select one and return the list item.
    """
    def __init__( self, parentWindow, availableSettingsList, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "SelectResourceBoxDialog…" )
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule:
                print( "aS", len(availableSettingsList), repr(availableSettingsList) ) # Should be a list of tuples
            assert isinstance( availableSettingsList, list )
        self.availableSettingsList = availableSettingsList
        ModalDialog.__init__( self, parentWindow, title )
    # end of SelectResourceBoxDialog.__init__


    def makeBody( self, master ):
        Label( master, text=_("Select a resource to open") ).grid( row=0 )

        self.lb = tk.Listbox( master, selectmode=tk.EXTENDED )
        """ Note: selectmode can be
            SINGLE (just a single choice),
            BROWSE (same, but the selection can be moved using the mouse),
            MULTIPLE (multiple item can be choosen, by clicking at them one at a time), or
            tk.EXTENDED (multiple ranges of items can be chosen using the Shift and Control keyboard modifiers).
            The default is BROWSE.
            Use MULTIPLE to get “checklist” behavior,
            and tk.EXTENDED when the user would usually pick only one item,
                but sometimes would like to select one or more ranges of items. """
        for item in self.availableSettingsList:
            #print( "it", repr(item) )
            if isinstance( item, tuple ): item = item[0]
            self.lb.insert( tk.END, item )
        self.lb.grid( row=1 )

        return self.lb # initial focus
    # end of SelectResourceBoxDialog.makeBody


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Must be at least one selected (otherwise force them to select CANCEL).

        Returns True or False.
        """
        return self.lb.curselection()
    # end of SelectResourceBoxDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        items = self.lb.curselection()
        print( "items", repr(items) ) # a tuple of index integers
        self.result = [self.availableSettingsList[int(item)] for item in items] # now a sublist
        print( "Requested resource(s) is/are: {!r}".format( self.result ) )
    # end of SelectResourceBoxDialog.apply
# end of class SelectResourceBoxDialog



class GetNewProjectNameDialog( ModalDialog ):
    """
    Get the name and an abbreviation for a new Biblelator project.
    """
    def __init__( self, parentWindow, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "GetNewProjectNameDialog…" )
        ModalDialog.__init__( self, parentWindow, title )
    # end of GetNewProjectNameDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        Label( master, text=_("Full name:") ).grid( row=0 )
        Label( master, text=_("Abbreviation:") ).grid( row=1 )

        self.e1 = BEntry( master )
        self.e2 = BEntry( master )

        self.e1.grid( row=0, column=1 )
        self.e2.grid( row=1, column=1 )
        return self.e1 # initial focus
    # end of GetNewProjectNameDialog.makeBody


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        fullname = self.e1.get()
        lenF = len( fullname )
        abbreviation = self.e2.get()
        lenA = len( abbreviation )
        if lenF < 3: showWarning( self.parentWindow, APP_NAME, _("Full name is too short!") ); return False
        if lenF > 30: showWarning( self.parentWindow, APP_NAME, _("Full name is too long!") ); return False
        if lenA < 3: showWarning( self.parentWindow, APP_NAME, _("Abbreviation is too short!") ); return False
        if lenA > 8: showWarning( self.parentWindow, APP_NAME, _("Abbreviation is too long!") ); return False
        if ' ' in abbreviation: showWarning( self.parentWindow, APP_NAME, _("Abbreviation cannot contain spaces!") ); return False
        if '.' in abbreviation: showWarning( self.parentWindow, APP_NAME, _("Abbreviation cannot contain a dot!") ); return False
        for illegalChar in ':;"@#=/\\{}':
            if illegalChar in fullname or illegalChar in abbreviation:
                showWarning( self.parentWindow, APP_NAME, _("Not allowed {} characters").format( _('space') if illegalChar==' ' else illegalChar ) ); return False
        return True
    # end of GetNewProjectNameDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        fullname = self.e1.get()
        abbreviation = self.e2.get()
        self.result = { 'Name':fullname, 'Abbreviation':abbreviation }
    # end of GetNewProjectNameDialog.apply
# end of class GetNewProjectNameDialog



class CreateNewProjectFilesDialog( ModalDialog ):
    """
    Find if they want blank files created for a new Biblelator project.
    """
    def __init__( self, parentWindow, title, currentBBB, availableVersifications ): #, availableVersions ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "CreateNewProjectFilesDialog…" )
        #self.currentBBB, self.availableVersifications, self.availableVersions = currentBBB, availableVersifications, availableVersions
        self.currentBBB, self.availableVersifications = currentBBB, availableVersifications
        ModalDialog.__init__( self, parentWindow, title )
    # end of CreateNewProjectFilesDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        Label( master, text=_("Create book files:") ).grid( row=0 )
        self.selectVariable1 = tk.IntVar()
        rb1a = Radiobutton( master, text=_('Current book ({})').format( self.currentBBB ), variable=self.selectVariable1, value=1 )
        rb1a.grid( row=0, column=1, sticky=tk.W )
        rb1b = Radiobutton( master, text=_('All books'), variable=self.selectVariable1, value=2 )
        rb1b.grid( row=1, column=1, sticky=tk.W )
        rb1c = Radiobutton( master, text=_('OT books'), variable=self.selectVariable1, value=3 )
        rb1c.grid( row=2, column=1, sticky=tk.W )
        rb1d = Radiobutton( master, text=_('NT books'), variable=self.selectVariable1, value=4 )
        rb1d.grid( row=3, column=1, sticky=tk.W )
        rb1e = Radiobutton( master, text=_('No books (not advised)'), variable=self.selectVariable1, value=5 )
        rb1e.grid( row=4, column=1, sticky=tk.W )

        Label( master, text=_("Files will contain:") ).grid( row=6, sticky=tk.W )
        self.selectVariable2 = tk.IntVar()
        rb2a = Radiobutton( master, text=_("CV markers from versification"), variable=self.selectVariable2, value=1,
                                state = tk.NORMAL if self.availableVersifications else tk.DISABLED )
        rb2a.grid( row=7, column=0, sticky=tk.W )
        rb2b = Radiobutton( master, text=_("All markers from a USFM version"), variable=self.selectVariable2, value=2 )
                                #state = tk.NORMAL if self.availableVersions else tk.DISABLED )
        rb2b.grid( row=8, column=0, sticky=tk.W )
        rb2c = Radiobutton( master, text=_("Only basic header lines (not advised)"), variable=self.selectVariable2, value=3 )
        rb2c.grid( row=9, column=0, sticky=tk.W )
        rb2d = Radiobutton( master, text=_("Nothing at all (not advised)"), variable=self.selectVariable2, value=4 )
        rb2d.grid( row=10, column=0, sticky=tk.W )

        #cb1Values = ["test1a","test1b","test1c"]
        self.cb1 = BCombobox( master, values=self.availableVersifications,
                                state = 'readonly' if self.availableVersifications else tk.DISABLED )
        #self.cb.current( 0 )
        self.cb1.grid( row=7, column=1 )

        ##cb2Values = ["test2a","test2b","test2c"]
        #self.cb2 = BCombobox( master, values=self.availableVersions,
                                #state = 'readonly' if self.availableVersions else tk.DISABLED )
        ##self.cb.current( 0 )
        #self.cb2.grid( row=8, column=1 )

        return rb1a # initial focus
    # end of CreateNewProjectFilesDialog.apply


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        result1Number, result2Number = self.selectVariable1.get(), self.selectVariable2.get() # ints
        #cb1result, cb2result = self.cb1.get(), self.cb2.get() # strings
        cb1result = self.cb1.get() # string

        if result1Number<1 or result1Number>5 or result2Number<1 or result2Number>5: return False

        if result2Number==1 and not cb1result:
            showWarning( self.parentWindow, APP_NAME, _("Need a versification scheme name!") ); return False
        #if result2Number==2 and not cb2result:
            #showWarning( self.parentWindow, APP_NAME, _("Need a version name!") ); return False
        return True
    # end of CreateNewProjectFilesDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        result1Number, result2Number = self.selectVariable1.get(), self.selectVariable2.get() # ints
        #cb1result, cb2result = self.cb1.get(), self.cb2.get() # strings
        cb1result = self.cb1.get() # string
        bookResult = [None,'Current','All','OT','NT','None']
        fillResult = [None,'Versification','Version','Basic','None']
        self.result = { 'Books':bookResult[result1Number], 'Fill':fillResult[result2Number],
                       #'Versification':cb1result, 'Version':cb2result }
                       'Versification':cb1result }
    # end of CreateNewProjectFilesDialog.apply
# end of class CreateNewProjectFilesDialog



class GetNewCollectionNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, existingNames, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "GetNewCollectionNameDialog…" )
        self.existingNames = existingNames
        #print( "GetNewCollectionNameDialog: eNs", self.existingNames )
        ModalDialog.__init__( self, parentWindow, title )
    # end of GetNewCollectionNameDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        Label( master, text=_("Name:") ).grid( row=0 )
        self.e1 = BEntry( master )
        self.e1.grid( row=0, column=1 )
        return self.e1 # initial focus
    # end of GetNewCollectionNameDialog.makeBody


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        name = self.e1.get()
        lenN = len( name )
        if lenN < 3: showWarning( self.parentWindow, APP_NAME, _("Name is too short!") ); return False
        if lenN > 30: showWarning( self.parentWindow, APP_NAME, _("Name is too long!") ); return False
        for illegalChar in ' .:;"@#=/\\{}':
            if illegalChar in name:
                showWarning( self.parentWindow, APP_NAME, _("Not allowed {} characters").format( _('space') if illegalChar==' ' else illegalChar ) ); return False
        if name.upper() in self.existingNames:
            showWarning( self.parentWindow, APP_NAME, _("Name already in use").format( illegalChar ) ); return False
        return True
    # end of GetNewCollectionNameDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = self.e1.get()
    # end of GetNewCollectionName.apply
# end of class GetNewCollectionNameDialog



class RenameResourceCollectionDialog( ModalDialog ):
    """
    Get the new name for a resource collection.
    """
    def __init__( self, parentWindow, existingName, existingNames, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "RenameResourceCollectionDialog…" )
        self.existingName, self.existingNames = existingName, existingNames
        print( "RenameResourceCollectionDialog: eNs", self.existingNames )
        ModalDialog.__init__( self, parentWindow, title )
    # end of RenameResourceCollectionDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        Label( master, text=_('Enter name to replace "{}"').format( self.existingName ) ).grid( row=0, column=0, columnspan=2 )
        Label( master, text=_("New name:") ).grid( row=1, column=0 )

        self.e1 = BEntry( master )
        self.e1.grid( row=1, column=1 )
        return self.e1 # initial focus
    # end of RenameResourceCollectionDialog.apply


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        newName = self.e1.get()
        lenName = len( newName )
        if lenName < 3: showWarning( self.parentWindow, APP_NAME, _("New name is too short!") ); return False
        if lenName > 30: showWarning( self.parentWindow, APP_NAME, _("New name is too long!") ); return False
        for illegalChar in ' .:;"@#=/\\{}':
            if illegalChar in newName:
                showWarning( self.parentWindow, APP_NAME, _("Not allowed {} characters").format( _('space') if illegalChar==' ' else illegalChar ) ); return False
        if newName.upper() in self.existingNames:
            showWarning( self.parentWindow, APP_NAME, _("Name already in use").format( illegalChar ) ); return False
        return True
    # end of RenameResourceCollectionDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = self.e1.get()
    # end of RenameResourceCollectionDialog.apply
# end of class RenameResourceCollectionDialog



class GetBibleBookRangeDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, givenBible, currentBBB, currentList, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "GetBibleBookRangeDialog…" )
        #assert currentBBB in givenBible -- no, it might not be loaded yet!
        self.givenBible, self.currentBBB, self.currentList = givenBible, currentBBB, currentList
        ModalDialog.__init__( self, parentWindow, title )
    # end of GetBibleBookRangeDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        self.booksSelectVariable = tk.IntVar()

        rb1 = Radiobutton( master, text=_('Current book')+" ({})".format( self.currentBBB ), variable=self.booksSelectVariable, value=1 )
        rb1.grid( row=0, column=0, sticky=tk.W )
        allText = _("All {} books").format( len(self.givenBible) ) if len(self.givenBible)>2 else _('All books')
        rb2 = Radiobutton( master, text=allText, variable=self.booksSelectVariable, value=2 )
        rb2.grid( row=1, column=0, sticky=tk.W )
        rb3 = Radiobutton( master, text=_('OT books'), variable=self.booksSelectVariable, value=3 )
        rb3.grid( row=2, column=0, sticky=tk.W )
        rb4 = Radiobutton( master, text=_('NT books'), variable=self.booksSelectVariable, value=4 )
        rb4.grid( row=3, column=0, sticky=tk.W )
        rb5 = Radiobutton( master, text=_('DC books'), variable=self.booksSelectVariable, value=5 )
        rb5.grid( row=4, column=0, sticky=tk.W )
        self.rb6 = Radiobutton( master,
                text=', '.join(self.currentList) if len(self.currentList)<10 else _('Selected books ({})').format( len(self.currentList) ),
                variable=self.booksSelectVariable, value=6 ) \
            if self.currentList and self.currentList!='ALL' else \
            Radiobutton( master, text=_('(N/A)'), variable=self.booksSelectVariable, value=6, state=tk.DISABLED )
        self.rb6.grid( row=5, column=0, sticky=tk.W )
        b1 = Button( master, text=_('Select')+'…', command=self.doIndividual )
        b1.grid( row=6, column=0, sticky=tk.W )

        return rb1 # initial focus
    # end of GetBibleBookRangeDialog.makeBody


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        resultNumber = self.booksSelectVariable.get()
        return 1 <= resultNumber <= 6
    # end of GetBibleBookRangeDialog.validate


    def doIndividual( self ):
        """
        Allow the user to select individual books(s).
        """
        self.parentApp = self.parentWindow.parentApp # Need to set this up before calling dialog from a dialog
        self.availableList = self.givenBible.getBookList()
        sIBBD = SelectIndividualBibleBooksDialog( self, self.availableList, self.currentList, title=_('Books to be searched') )
        if BibleOrgSysGlobals.debugFlag: print( "individualBooks sIBBDResult", repr(sIBBD.result) )
        if sIBBD.result: # Returns a list of books
            if BibleOrgSysGlobals.debugFlag: assert isinstance( sIBBD.result, list )
            resultCount = len( sIBBD.result )
            if resultCount==1 and sIBBD.result[0]==self.currentBBB:
                # It's just the current book to search
                self.booksSelectVariable.set( 1 )
            elif resultCount == len( self.availableList ):
                self.booksSelectVariable.set( 2 )
            else:
                self.booksSelectVariable.set( 6 )
                self.currentList = sIBBD.result
                self.rb6['state'] = tk.NORMAL
                self.rb6['text'] = ', '.join(self.currentList) if len(self.currentList)<10 else _('Selected books ({})').format( len(self.currentList) )
            #self.update()
        else: print( "selectIndividual: Nothing selected!" )
    # end of GetBibleBookRangeDialog.doIndividual


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        resultNumber = self.booksSelectVariable.get()
        if resultNumber == 1: self.result = [self.currentBBB]
        elif resultNumber == 2: self.result = [book.BBB for book in self.givenBible] # all
        elif resultNumber == 3: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.loadedBibleBooksCodes.isOldTestament_NR(book.BBB)] # OT
        elif resultNumber == 4: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.loadedBibleBooksCodes.isNewTestament_NR(book.BBB)] # NT
        elif resultNumber == 5: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.loadedBibleBooksCodes.isDeuterocanon_NR(book.BBB)] # DC
        elif resultNumber == 6: self.result = self.currentList
        else:
            halt # Unexpected result value
    # end of GetBibleBookRangeDialog.apply
# end of class GetBibleBookRangeDialog



class SelectIndividualBibleBooksDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, availableList, currentList, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "SelectIndividualBibleBooksDialog…" )
        self.availableList, self.currentList = availableList, currentList
        ModalDialog.__init__( self, parentWindow, title )
    # end of SelectIndividualBibleBooksDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        self.groupSelectVariable = tk.IntVar()
        rb1b = Radiobutton( master, text=_('OT books'), variable=self.groupSelectVariable, value=1 )
        rb1b.grid( row=0, column=0, sticky=tk.W )
        rb1c = Radiobutton( master, text=_('NT books'), variable=self.groupSelectVariable, value=2 )
        rb1c.grid( row=1, column=0, sticky=tk.W )
        rb1d = Radiobutton( master, text=_('DC books'), variable=self.groupSelectVariable, value=3 )
        rb1d.grid( row=2, column=0, sticky=tk.W )
        rb1e = Radiobutton( master, text=_('Other books'), variable=self.groupSelectVariable, value=4 )
        rb1e.grid( row=3, column=0, sticky=tk.W )
        rb1f = Radiobutton( master, text=_('All books'), variable=self.groupSelectVariable, value=5 )
        rb1f.grid( row=4, column=0, sticky=tk.W )

        b1 = Button( master, text=_('Select'), command=self.doSelect )
        b1.grid( row=5, column=0, sticky=tk.W )
        b2 = Button( master, text=_('Deselect'), command=self.doDeselect )
        b2.grid( row=6, column=0, sticky=tk.W )


        # Adapted from http://stackoverflow.com/questions/7591294/how-to-create-a-self-resizing-grid-of-buttons-in-tkinter
        numBooks = len( self.availableList )
        if numBooks > 100: buttonsAcross = 12
        elif numBooks > 80: buttonsAcross = 10
        elif numBooks > 60: buttonsAcross = 8
        elif numBooks > 30: buttonsAcross = 6
        else: buttonsAcross = 5
        xPad, yPad = 6, 8

        grid=Frame( master )
        grid.grid( column=0, row=7, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W )
        tk.Grid.rowconfigure( master, 7, weight=1 )
        tk.Grid.columnconfigure( master, 0, weight=1 )

        self.variables = []
        for j,BBB in enumerate(self.availableList):
            col, row = j // buttonsAcross + 1, j % buttonsAcross
            #print( j, row, col )
            thisVar =  tk.IntVar()
            if BBB in self.currentList: thisVar.set( 1 ) # Preset any formerly selected books
            self.variables.append( thisVar )
            tk.Checkbutton( master, text=BBB, variable=thisVar ) \
                    .grid( column=col, row=row, padx=xPad, pady=yPad, sticky=tk.N+tk.S+tk.E+tk.W )

        for x in range(10):
            tk.Grid.columnconfigure( master, x, weight=1 )
        for y in range(5):
            tk.Grid.rowconfigure( master, y, weight=1 )

        #return 0
    # end of SelectIndividualBibleBooksDialog.makeBody


    #def validate( self ):
        #"""
        #Override the empty ModalDialog.validate function
            #to check that the results are how we need them.

        #Returns True or False.
        #"""
        #resultNumber = self.booksSelectVariable.get()
        #return 1 <= resultNumber <= 5
    ## end of SelectIndividualBibleBooksDialog.validate


    def doSelect( self ):
        """
        Button does nothing at all if no radio buttons selected.
        """
        resultNumber = self.groupSelectVariable.get()
        if resultNumber == 1: # 'OT'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.loadedBibleBooksCodes.isOldTestament_NR( BBB ):
                    variable.set( 1 )
        elif resultNumber == 2: # 'NT'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.loadedBibleBooksCodes.isNewTestament_NR( BBB ):
                    variable.set( 1 )
        elif resultNumber == 3: # 'DC'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.loadedBibleBooksCodes.isDeuterocanon_NR( BBB ):
                    variable.set( 1 )
        elif resultNumber == 4: # 'Other'
            for variable, BBB in zip( self.variables, self.availableList):
                if not BibleOrgSysGlobals.loadedBibleBooksCodes.isOldTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.loadedBibleBooksCodes.isNewTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.loadedBibleBooksCodes.isDeuterocanon_NR( BBB ):
                    variable.set( 1 )
        elif resultNumber == 5: # 'ALL'
            for variable in self.variables: variable.set( 1 )
        self.groupSelectVariable.set( 0 ) # Turn off all radiobuttons
    # end of SelectIndividualBibleBooksDialog.doSelect


    def doDeselect( self ):
        """
        Button does nothing at all if no radio buttons selected.
        """
        resultNumber = self.groupSelectVariable.get()
        if resultNumber == 1: # 'OT'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.loadedBibleBooksCodes.isOldTestament_NR( BBB ):
                    variable.set( 0 )
        elif resultNumber == 2: # 'NT'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.loadedBibleBooksCodes.isNewTestament_NR( BBB ):
                    variable.set( 0 )
        elif resultNumber == 3: # 'DC'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.loadedBibleBooksCodes.isDeuterocanon_NR( BBB ):
                    variable.set( 0 )
        elif resultNumber == 4: # 'Other'
            for variable, BBB in zip( self.variables, self.availableList):
                if not BibleOrgSysGlobals.loadedBibleBooksCodes.isOldTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.loadedBibleBooksCodes.isNewTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.loadedBibleBooksCodes.isDeuterocanon_NR( BBB ):
                    variable.set( 0 )
        elif resultNumber == 5: # 'ALL'
            for variable in self.variables: variable.set( 0 )
        self.groupSelectVariable.set( 0 ) # Turn off all radiobuttons
    # end of SelectIndividualBibleBooksDialog.doDeselect


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = []
        for variable, bookName in zip( self.variables, self.availableList ):
            if variable.get(): self.result.append( bookName )
    # end of SelectIndividualBibleBooksDialog.apply
# end of class SelectIndividualBibleBooksDialog



class GetBibleFindTextDialog( ModalDialog ):
    """
    Get the search string (and options) for Bible search.
    """
    def __init__( self, parentWindow, givenBible, optionsDict, title ):
        """
        optionsDict must already contain 'currentBCV'
        """
        if BibleOrgSysGlobals.debugFlag:
            parentWindow.parentApp.setDebugText( "GetBibleFindTextDialog…" )
            #assert currentBBB in givenBible -- no, it might not be loaded yet!
            assert isinstance( optionsDict, dict )
            assert 'currentBCV' in optionsDict
        self.givenBible, self.optionsDict = givenBible, optionsDict
        self.optionsDict['parentWindow'] = parentWindow
        self.optionsDict['parentBox'] = parentWindow.textBox
        self.optionsDict['parentApp'] = parentWindow.parentApp
        self.optionsDict['givenBible'] = givenBible

        # Set-up default search options
        self.optionsDict['workName'] = givenBible.getAName() # Always revert to the original work
        if 'findHistoryList' not in self.optionsDict: self.optionsDict['findHistoryList'] = [] # Oldest first
        if 'wordMode' not in self.optionsDict: self.optionsDict['wordMode'] = 'Any' # or 'Whole' or 'Begins' or 'EndsWord' or 'EndsLine'
        if 'caselessFlag' not in self.optionsDict: self.optionsDict['caselessFlag'] = True
        if 'ignoreDiacriticsFlag' not in self.optionsDict: self.optionsDict['ignoreDiacriticsFlag'] = False
        if 'includeIntroFlag' not in self.optionsDict: self.optionsDict['includeIntroFlag'] = True
        if 'includeMainTextFlag' not in self.optionsDict: self.optionsDict['includeMainTextFlag'] = True
        if 'includeMarkerTextFlag' not in self.optionsDict: self.optionsDict['includeMarkerTextFlag'] = False
        if 'includeExtrasFlag' not in self.optionsDict: self.optionsDict['includeExtrasFlag'] = False
        if 'contextLength' not in self.optionsDict: self.optionsDict['contextLength'] = 30 # each side
        if 'bookList' not in self.optionsDict: self.optionsDict['bookList'] = 'ALL' # or BBB or a list
        if 'chapterList' not in self.optionsDict: self.optionsDict['chapterList'] = None
        if 'markerList' not in self.optionsDict: self.optionsDict['markerList'] = None
        self.optionsDict['regexFlag'] = False

        ModalDialog.__init__( self, parentWindow, title )
    # end of GetBibleFindTextDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        #print( "GetBibleFindTextDialog.makeBody", self.optionsDict )

        Label( master, text=_("Project:") ).grid( row=0, column=0, padx=2, pady=2, sticky=tk.E )
        self.projectNameVar = tk.StringVar()
        self.projectNameVar.set( self.optionsDict['workName'] )
        self.projectNameBox = BCombobox( master, width=30, textvariable=self.projectNameVar )
        # Find other Bible boxes which might be added as possible projects
        #print( "  parentWindow window {}".format( self.optionsDict['parentWindow'] ) )
        #from TextBoxes import BibleBox
        possibilityList = []
        self.projectDict = {}
        for appWin in self.parentWindow.parentApp.childWindows:
            #print( "Saw {}/{}/{}".format( appWin.genericWindowType, appWin.windowType, type(appWin) ) )
            if 'Bible' in appWin.genericWindowType:
                #print( "  Found {}/{}/{}".format( appWin.genericWindowType, appWin.windowType, type(appWin) ) )
                # Some windows have a single text box, others have a collection of boxes
                try: # See if we have a text box
                    #print( "    TextBox {}/{}".format( appWin.textBox, type(appWin.textBox) ) )
                    if appWin.textBox is not None:
                        iB = appWin.internalBible
                        bibleWork = iB.getAName()
                        #print( "    BibleWork={!r}".format( bibleWork ) )
                        if bibleWork not in possibilityList: # Don't want duplicates
                            possibilityList.append( bibleWork )
                            self.projectDict[bibleWork] = ('Window',appWin,appWin.textBox,iB)
                except: pass
                try: # See if we have a list of boxes
                    for resourceBox in appWin.resourceBoxesList:
                        #print( "      ResourceBox {}/{}".format( resourceBox.textBox, type(resourceBox.textBox) ) )
                        if resourceBox.textBox is not None:
                            iB = resourceBox.internalBible
                            bibleWork = iB.getAName()
                            #print( "    BibleWork={!r}".format( bibleWork ) )
                            if bibleWork not in possibilityList: # Don't want duplicates
                                possibilityList.append( bibleWork )
                                self.projectDict[bibleWork] = ('Box',appWin,resourceBox,iB)
                except: pass
        self.projectNameBox['values'] = possibilityList
        self.projectNameBox.grid( row=0, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )

        Label( master, text=_("Find:") ).grid( row=1, column=0, padx=2, pady=5, sticky=tk.E )
        self.searchStringVar = tk.StringVar()
        try: self.searchStringVar.set( self.optionsDict['findHistoryList'][-1] )
        except IndexError: pass
        self.searchStringBox = BCombobox( master, width=30, textvariable=self.searchStringVar )
        self.searchStringBox['values'] = self.optionsDict['findHistoryList']
        #self.searchStringBox['width'] = len( 'Deuteronomy' )
        self.searchStringBox.bind('<<ComboboxSelected>>', self.ok )
        self.searchStringBox.bind( '<Return>', self.ok )
        #self.searchStringBox.pack( side=tk.LEFT )
        self.searchStringBox.grid( row=1, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )
        self.searchStringBox.icursor( tk.END ) # Set cursor to end (makes spaces visible)

        wordLimitsFrame = tk.LabelFrame( master, text=_('Word limits'), padx=5, pady=5 )
        wordLimitsFrame.grid( row=2, column=0, padx=10, pady=10, sticky=tk.W )

        self.wordModeSelectVariable = tk.IntVar()
        if self.optionsDict['wordMode'] == 'Any': self.wordModeSelectVariable.set( 1 )
        elif self.optionsDict['wordMode'] == 'Whole': self.wordModeSelectVariable.set( 2 )
        elif self.optionsDict['wordMode'] == 'Begins': self.wordModeSelectVariable.set( 3 )
        elif self.optionsDict['wordMode'] == 'EndsWord': self.wordModeSelectVariable.set( 4 )
        elif self.optionsDict['wordMode'] == 'EndsLine': self.wordModeSelectVariable.set( 5 )
        else: halt # programming error

        self.rwmb1 = Radiobutton( master, text=_('No restriction'), variable=self.wordModeSelectVariable, value=1 )
        self.rwmb1.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb1.grid( row=2, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb2 = Radiobutton( master, text=_('Whole words only'), variable=self.wordModeSelectVariable, value=2 )
        self.rwmb2.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb2.grid( row=3, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb3 = Radiobutton( master, text=_('Beginning of word'), variable=self.wordModeSelectVariable, value=3 )
        self.rwmb3.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb3.grid( row=4, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb4 = Radiobutton( master, text=_('End of word'), variable=self.wordModeSelectVariable, value=4 )
        self.rwmb4.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb4.grid( row=5, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb5 = Radiobutton( master, text=_('End of line'), variable=self.wordModeSelectVariable, value=5 )
        self.rwmb5.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )

        self.mcaseVar = tk.IntVar()
        if not self.optionsDict['caselessFlag']: self.mcaseVar.set( 1 )
        mcaseCb = tk.Checkbutton( master, text=_("Match case"), variable=self.mcaseVar )
        #mcaseCb.grid( row=6, column=0, padx=0, pady=5, sticky=tk.W )
        mcaseCb.pack( in_=wordLimitsFrame, side=tk.TOP, anchor=tk.W, padx=0, pady=1 )
        self.diaVar = tk.IntVar()
        if self.optionsDict['ignoreDiacriticsFlag']: self.diaVar.set( 1 )
        diaCb = tk.Checkbutton( master, text=_("Ignore diacritics"), variable=self.diaVar )
        #diaCb.grid( row=6, column=2, padx=0, pady=5, sticky=tk.W )
        diaCb.pack( in_=wordLimitsFrame, side=tk.TOP, anchor=tk.W, padx=0, pady=1 )

        bookLimitsFrame = tk.LabelFrame( master, text=_("Book limits"), padx=5, pady=5 )
        bookLimitsFrame.grid( row=2, column=2, padx=10, pady=10, sticky=tk.W )

        self.booksSelectVariable = tk.IntVar()
        if self.optionsDict['bookList'] == 'ALL': self.booksSelectVariable.set( 1 )
        elif self.optionsDict['bookList'] == self.optionsDict['currentBCV'][0]:
            if self.optionsDict['chapterList'] == None: self.booksSelectVariable.set( 2 )
            else: self.booksSelectVariable.set( 3 )
        elif isinstance( self.optionsDict['bookList'], str ): # Some other bookcode (but not the current one)
            self.booksSelectVariable.set( 4 )
        elif isinstance( self.optionsDict['bookList'], list ): self.booksSelectVariable.set( 4 )
        else:
            print( "booklist options", self.optionsDict['bookList'] )
            print( "whole options dict", self.optionsDict )
            halt # programming error

        allText = _("All {} books").format( len(self.givenBible) ) if len(self.givenBible)>2 else _("All books")
        self.rbb1 = Radiobutton( master, text=allText, variable=self.booksSelectVariable, value=1 )
        self.rbb1.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        self.rbb2 = Radiobutton( master, text=_('Current book')+' ({})'.format( self.optionsDict['currentBCV'][0] ), variable=self.booksSelectVariable, value=2 )
        self.rbb2.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rbb2.grid( row=2, column=2, padx=2, pady=1, sticky=tk.W )
        self.rbb3 = Radiobutton( master, text=_('Current chapter')+' ({} {})'.format( self.optionsDict['currentBCV'][0], self.optionsDict['currentBCV'][1] ), variable=self.booksSelectVariable, value=3 )
        self.rbb3.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rbb3.grid( row=3, column=2, padx=2, pady=1, sticky=tk.W )
        sbText = '(N/A)' if self.optionsDict['bookList']=='ALL' \
            else ', '.join(self.optionsDict['bookList']) if len(self.optionsDict['bookList'])<10 \
            else '({})'.format( len(self.optionsDict['bookList']) )
        self.rbb4 = Radiobutton( master, text=_('Selected books {}').format( sbText ), variable=self.booksSelectVariable, value=4 )
        #self.rbb4.grid( row=5, column=2, padx=2, pady=1, sticky=tk.W )
        self.rbb4.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        bb = Button( master, text=_('Select books')+'…', command=self.selectBooks )
        bb.pack( in_=bookLimitsFrame, side=tk.TOP, anchor=tk.E )

        fieldLimitsFrame = tk.LabelFrame( master, text=_("Field limits"), padx=5, pady=5 )
        fieldLimitsFrame.grid( row=3, column=2, padx=10, pady=10, sticky=tk.W )

        self.introVar = tk.IntVar()
        if self.optionsDict['includeIntroFlag']: self.introVar.set( 1 )
        introCb = tk.Checkbutton( master, text=_("Include introductions"), variable=self.introVar )
        #introCb.grid( row=6, column=0, padx=0, pady=5, sticky=tk.W )
        introCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )
        self.mainTextVar = tk.IntVar()
        if self.optionsDict['includeMainTextFlag']: self.mainTextVar.set( 1 )
        mainTextCb = tk.Checkbutton( master, text=_("Include main text"), variable=self.mainTextVar )
        #mainTextCb.grid( row=6, column=0, padx=0, pady=5, sticky=tk.W )
        mainTextCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )
        self.markersTextVar = tk.IntVar()
        if self.optionsDict['includeMarkerTextFlag']: self.markersTextVar.set( 1 )
        markersCb = tk.Checkbutton( master, text=_("Include text of markers"), variable=self.markersTextVar )
        #markersCb.grid( row=6, column=0, padx=0, pady=5, sticky=tk.W )
        markersCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )
        self.extrasVar = tk.IntVar()
        if self.optionsDict['includeExtrasFlag']: self.extrasVar.set( 1 )
        extrasCb = tk.Checkbutton( master, text=_("Include footnotes & cross-references"), variable=self.extrasVar )
        #extrasCb.grid( row=6, column=0, padx=0, pady=5, sticky=tk.W )
        extrasCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )

        markerListFrame = tk.Frame( master, padx=5, pady=5 )
        markerListFrame.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, fill=tk.X, padx=2, pady=1 )
        self.theseMarkersOnlyVar = tk.IntVar()
        if self.optionsDict['markerList']:
            self.theseMarkersOnlyVar.set( 1 )
            self.introVar.set( 0 ); self.mainTextVar.set( 0 ); self.markersTextVar.set( 0 ); self.extrasVar.set( 0 )
        theseMarkersCb = tk.Checkbutton( master, text=_("Only this marker(s):"), variable=self.theseMarkersOnlyVar )
        theseMarkersCb.pack( in_=markerListFrame, side=tk.LEFT, padx=2, pady=1 )
        self.theseMarkersListVar = tk.StringVar()
        self.theseMarkersListVar.set( ','.join(mkr for mkr in self.optionsDict['markerList']) if self.optionsDict['markerList'] else '' )
        registeredFunction = self.register( self.doMarkerListentry )
        theseMarkersEntry = BEntry( master, textvariable=self.theseMarkersListVar,
                                    validate='all', validatecommand=(registeredFunction,'%P') )
        theseMarkersEntry.pack( in_=markerListFrame, side=tk.RIGHT, padx=2, pady=1 )

        return self.searchStringBox # initial focus
    # end of GetBibleFindTextDialog.makeBody


    def selectBooks( self ):
        """
        """
        self.parentWindow._prepareInternalBible() # Slow but must be called before the dialog
        currentBBB = self.optionsDict['currentBCV'][0]
        gBBRD = GetBibleBookRangeDialog( self, self.parentWindow.parentApp, self.givenBible, currentBBB, self.optionsDict['bookList'], title=_('Books to be searched') )
        if BibleOrgSysGlobals.debugFlag: print( "selectBooks gBBRDResult", repr(gBBRD.result) )
        if gBBRD.result: # Returns a list of books
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBBRD.result, list )
            if len(gBBRD.result)==1 and gBBRD.result[0]==currentBBB:
                # It's just the current book to search
                self.booksSelectVariable.set( 2 )
            else:
                self.booksSelectVariable.set( 4 )
                self.optionsDict['bookList'] = gBBRD.result
                sbText = '(N/A)' if self.optionsDict['bookList']=='ALL' \
                    else ', '.join(self.optionsDict['bookList']) if len(self.optionsDict['bookList'])<10 \
                    else '({})'.format( len(self.optionsDict['bookList']) )
                self.rbb4['text'] = _('Selected books {}').format( sbText )
            #self.update()
        else: print( "selectBooks: No books selected!" )
    # end of GetBibleFindTextDialog.apply


    def doMarkerListentry( self, willBe ):
        """
        """
        #print( "doMarkerListentry( {!r} )".format( willBe ) )
        #thisText = self.theseMarkersListVar.get()
        if willBe: # There's something in the entry
            self.theseMarkersOnlyVar.set( 1 )
            self.introVar.set( 0 ); self.mainTextVar.set( 0 ); self.markersTextVar.set( 0 ); self.extrasVar.set( 0 )
        else: self.theseMarkersOnlyVar.set( 0 )
        for char in willBe:
            if char not in ' abcdefghijklmnopqrstuvwxyz1234,': return False
        return True # accept it
    # end of GetBibleFindTextDialog.doMarkerListentry


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        #print( "GetBibleFindTextDialog.validate()" )

        # Do some normalization first
        theseMarkersOnlyText = self.theseMarkersListVar.get()
        if theseMarkersOnlyText: # check that they're valid newline markers
            # First normalize the entries
            theseMarkersOnlyText = theseMarkersOnlyText.strip().replace('  ',' ').replace(' ',',').replace(',,,',',').replace(',,',',').replace(',',', ')
            self.theseMarkersListVar.set( theseMarkersOnlyText )
            self.theseMarkersOnlyVar.set( 1 )
        if theseMarkersOnlyText: # check that they're valid newline markers
            markerList = []
            for marker in theseMarkersOnlyText.split( ',' ):
                #print( "marker", marker )
                marker = marker.strip()
                if marker in BibleOrgSysGlobals.loadedUSFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                    markerList.append( marker )
                else: # not a valid newline marker
                    showWarning( self.parentWindow, APP_NAME, _("{!r} is not a valid newline marker!").format( marker ) ); return False
        else: # Nothing in the entry
            self.theseMarkersOnlyVar.set( 0 )

        # Now check for bad combinations
        findText = self.searchStringVar.get()
        if not findText: showWarning( self.parentWindow, APP_NAME, _("Nothing to search for!") ); return False
        if findText.lower() == 'regex:': showWarning( self.parentWindow, APP_NAME, _("No regular expression to search for!") ); return False
        bookResultNumber = self.booksSelectVariable.get()
        if bookResultNumber==4 and not self.optionsDict['bookList']:
            showWarning( self.parentWindow, APP_NAME, _("No books selected to search in!") ); return False
        if self.theseMarkersOnlyVar.get():
            if self.introVar.get() or  self.mainTextVar.get() or self.markersTextVar.get() or self.extrasVar.get():
                showWarning( self.parentWindow, APP_NAME, _("Bad combination of fields selected!") ); return False
        return True # Must be ok
    # end of GetBibleFindTextDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        #print( "GetBibleFindTextDialog.apply()" )

        workName = self.projectNameVar.get()
        if workName != self.optionsDict['workName']: # then they've changed it
            self.optionsDict['workName'] = workName
            descr,window,box,iB = self.projectDict[workName]
            assert descr in ( 'Window', 'Box' )
            self.optionsDict['parentWindow'] = window
            self.optionsDict['parentBox'] = box
            self.optionsDict['parentApp'] = window.parentApp
            self.optionsDict['givenBible'] = iB

        self.optionsDict['findText'] = self.searchStringVar.get()

        wordModeResultNumber = self.wordModeSelectVariable.get()
        if wordModeResultNumber == 1: self.optionsDict['wordMode'] = 'Any'
        elif wordModeResultNumber == 2: self.optionsDict['wordMode'] = 'Whole'
        elif wordModeResultNumber == 3: self.optionsDict['wordMode'] = 'Begins'
        elif wordModeResultNumber == 4: self.optionsDict['wordMode'] = 'EndsWord'
        elif wordModeResultNumber == 5: self.optionsDict['wordMode'] = 'EndsLine'
        else:
            halt # Unexpected result value

        bookResultNumber = self.booksSelectVariable.get()
        self.optionsDict['chapterList'] = None
        if bookResultNumber == 1: self.optionsDict['bookList'] = 'ALL'
        elif bookResultNumber == 2: self.optionsDict['bookList'] = self.optionsDict['currentBCV'][0]
        elif bookResultNumber == 3:
            self.optionsDict['bookList'] = self.optionsDict['currentBCV'][0]
            self.optionsDict['chapterList'] = [self.optionsDict['currentBCV'][1]]
        elif bookResultNumber == 4: #self.optionsDict['bookList'] should already be set
            pass
        else:
            halt # Unexpected result value

        # Checkboxes
        self.optionsDict['caselessFlag'] = not self.mcaseVar.get()
        self.optionsDict['ignoreDiacriticsFlag'] = bool( self.diaVar.get() )
        self.optionsDict['includeIntroFlag'] = bool( self.introVar.get() )
        self.optionsDict['includeMainTextFlag'] = bool( self.mainTextVar.get() )
        self.optionsDict['includeExtrasFlag'] = bool( self.extrasVar.get() )
        self.optionsDict['includeMarkerTextFlag'] = bool( self.markersTextVar.get() )
        if self.optionsDict['includeIntroFlag'] or self.optionsDict['includeMainTextFlag'] \
        or self.optionsDict['includeExtrasFlag'] or self.optionsDict['includeMarkerTextFlag']:
            self.optionsDict['markerList'] = None
        else:
            theseMarkersOnlyText = self.theseMarkersListVar.get()
            if theseMarkersOnlyText: # check that they're valid newline markers
                # First normalize the entries
                theseMarkersOnlyText = theseMarkersOnlyText.strip().replace('  ',' ').replace(' ',',').replace(',,,',',').replace(',,',',').replace(',',', ')
            if theseMarkersOnlyText: # check that they're valid newline markers
                markerList = []
                for marker in theseMarkersOnlyText.split( ',' ):
                    #print( "marker", marker )
                    marker = marker.strip()
                    if marker in BibleOrgSysGlobals.loadedUSFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                        markerList.append( marker )
                    else: halt # not a valid newline marker
                if markerList: self.optionsDict['markerList'] = markerList

        self.result = self.optionsDict
    # end of GetBibleFindTextDialog.apply
# end of class GetBibleFindTextDialog



class GetBibleReplaceTextDialog( ModalDialog ):
    """
    Get the Find and Replace strings (and options) for Bible Replace.
    """
    def __init__( self, parentWindow, givenBible, optionsDict, title ):
        """
        optionsDict must already contain 'currentBCV'
        """
        if BibleOrgSysGlobals.debugFlag:
            parentWindow.parentApp.setDebugText( "GetBibleReplaceTextDialog…" )
            #assert currentBBB in givenBible -- no, it might not be loaded yet!
            assert isinstance( optionsDict, dict )
            assert 'currentBCV' in optionsDict
        self.givenBible, self.optionsDict = givenBible, optionsDict
        self.optionsDict['parentWindow'] = parentWindow
        self.optionsDict['parentBox'] = parentWindow.textBox
        self.optionsDict['parentApp'] = parentWindow.parentApp
        self.optionsDict['givenBible'] = givenBible

        # Set-up default Replace options
        self.optionsDict['workName'] = givenBible.getAName() # Always revert to the original work
        if 'findHistoryList' not in self.optionsDict: self.optionsDict['findHistoryList'] = [] # Oldest first
        if 'replaceHistoryList' not in self.optionsDict: self.optionsDict['replaceHistoryList'] = [] # Oldest first
        if 'wordMode' not in self.optionsDict: self.optionsDict['wordMode'] = 'Any' # or 'Whole' or 'Begins' or 'EndsWord' or 'EndsLine'
        #if 'caselessFlag' not in self.optionsDict: self.optionsDict['caselessFlag'] = True
        #if 'ignoreDiacriticsFlag' not in self.optionsDict: self.optionsDict['ignoreDiacriticsFlag'] = False
        #if 'includeIntroFlag' not in self.optionsDict: self.optionsDict['includeIntroFlag'] = True
        #if 'includeMainTextFlag' not in self.optionsDict: self.optionsDict['includeMainTextFlag'] = True
        #if 'includeMarkerTextFlag' not in self.optionsDict: self.optionsDict['includeMarkerTextFlag'] = False
        #if 'includeExtrasFlag' not in self.optionsDict: self.optionsDict['includeExtrasFlag'] = False
        if 'contextLength' not in self.optionsDict: self.optionsDict['contextLength'] = 60 # each side
        if 'bookList' not in self.optionsDict: self.optionsDict['bookList'] = 'ALL' # or BBB or a list
        #if 'chapterList' not in self.optionsDict: self.optionsDict['chapterList'] = None
        #if 'markerList' not in self.optionsDict: self.optionsDict['markerList'] = None
        if 'doBackups' not in optionsDict: optionsDict['doBackups'] = True # No ability to change this from the dialog
        self.optionsDict['regexFlag'] = False

        ModalDialog.__init__( self, parentWindow, title )
    # end of GetBibleReplaceTextDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        #print( "GetBibleReplaceTextDialog.makeBody", self.optionsDict )
        Label( master, text=_("Project:") ).grid( row=0, column=0, padx=2, pady=2, sticky=tk.E )
        self.projectNameVar = tk.StringVar()
        self.projectNameVar.set( self.optionsDict['workName'] )
        self.projectNameBox = BCombobox( master, width=30, textvariable=self.projectNameVar )
        # Find other Bible boxes which might be added as possible projects
        #print( "  parentWindow window {}".format( self.optionsDict['parentWindow'] ) )
        #from TextBoxes import BibleBox
        possibilityList = []
        self.projectDict = {}
        for appWin in self.parentWindow.parentApp.childWindows:
            #print( "Saw {}/{}/{}".format( appWin.genericWindowType, appWin.windowType, type(appWin) ) )
            if 'Bible' in appWin.genericWindowType and 'Edit' in appWin.windowType:
                #print( "  Found {}/{}/{}".format( appWin.genericWindowType, appWin.windowType, type(appWin) ) )
                # Some windows have a single text box, others have a collection of boxes
                try: # See if we have a text box
                    #print( "    TextBox {}/{}".format( appWin.textBox, type(appWin.textBox) ) )
                    if appWin.textBox is not None:
                        iB = appWin.internalBible
                        bibleWork = getAName()
                        if bibleWork not in possibilityList: # Don't want duplicates
                            possibilityList.append( bibleWork )
                            self.projectDict[bibleWork] = ('Window',appWin,appWin.textBox,iB)
                except: pass
                try: # See if we have a list of boxes
                    for resourceBox in appWin.resourceBoxesList:
                        #print( "      ResourceBox {}/{}".format( resourceBox.textBox, type(resourceBox.textBox) ) )
                        if resourceBox.textBox is not None:
                            iB = resourceBox.internalBible
                            bibleWork = getAName()
                            if bibleWork not in possibilityList: # Don't want duplicates
                                possibilityList.append( bibleWork )
                                self.projectDict[bibleWork] = ('Box',appWin,resourceBox,IB)
                except: pass
        self.projectNameBox['values'] = possibilityList
        self.projectNameBox.grid( row=0, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )

        Label( master, text=_("Find (match case):") ).grid( row=1, column=0, padx=2, pady=5, sticky=tk.E )
        self.searchStringVar = tk.StringVar()
        try: self.searchStringVar.set( self.optionsDict['findHistoryList'][-1] )
        except IndexError: pass
        self.searchStringBox = BCombobox( master, width=30, textvariable=self.searchStringVar )
        self.searchStringBox['values'] = self.optionsDict['findHistoryList']
        #self.searchStringBox['width'] = len( 'Deuteronomy' )
        self.searchStringBox.bind('<<ComboboxSelected>>', self.ok )
        self.searchStringBox.bind( '<Return>', self.ok )
        #self.searchStringBox.pack( side=tk.LEFT )
        self.searchStringBox.grid( row=1, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )
        self.searchStringBox.icursor( tk.END ) # Set cursor to end (makes spaces visible)

        Label( master, text=_("Replace:") ).grid( row=2, column=0, padx=2, pady=5, sticky=tk.E )
        self.replaceStringVar = tk.StringVar()
        try: self.replaceStringVar.set( self.optionsDict['replaceHistoryList'][-1] )
        except IndexError: pass
        self.replaceStringBox = BCombobox( master, width=30, textvariable=self.replaceStringVar )
        self.replaceStringBox['values'] = self.optionsDict['replaceHistoryList']
        #self.replaceStringBox['width'] = len( 'Deuteronomy' )
        self.replaceStringBox.bind('<<ComboboxSelected>>', self.ok )
        self.replaceStringBox.bind( '<Return>', self.ok )
        #self.replaceStringBox.pack( side=tk.LEFT )
        self.replaceStringBox.grid( row=2, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )
        self.replaceStringBox.icursor( tk.END ) # Set cursor to end (makes spaces visible)

        wordLimitsFrame = tk.LabelFrame( master, text=_("Word limits"), padx=5, pady=5 )
        wordLimitsFrame.grid( row=3, column=0, padx=10, pady=10, sticky=tk.W )

        self.wordModeSelectVariable = tk.IntVar()
        if self.optionsDict['wordMode'] == 'Any': self.wordModeSelectVariable.set( 1 )
        elif self.optionsDict['wordMode'] == 'Whole': self.wordModeSelectVariable.set( 2 )
        elif self.optionsDict['wordMode'] == 'Begins': self.wordModeSelectVariable.set( 3 )
        elif self.optionsDict['wordMode'] == 'EndsWord': self.wordModeSelectVariable.set( 4 )
        elif self.optionsDict['wordMode'] == 'EndsLine': self.wordModeSelectVariable.set( 5 )
        else: halt # programming error

        self.rwmb1 = Radiobutton( master, text=_("No restriction" ), variable=self.wordModeSelectVariable, value=1 )
        self.rwmb1.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb1.grid( row=3, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb2 = Radiobutton( master, text=_("Whole words only" ), variable=self.wordModeSelectVariable, value=2 )
        self.rwmb2.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb2.grid( row=4, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb3 = Radiobutton( master, text=_("Beginning of word" ), variable=self.wordModeSelectVariable, value=3 )
        self.rwmb3.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb3.grid( row=5, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb4 = Radiobutton( master, text=_("End of word" ), variable=self.wordModeSelectVariable, value=4 )
        self.rwmb4.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rwmb4.grid( row=6, column=0, padx=2, pady=1, sticky=tk.W )
        self.rwmb5 = Radiobutton( master, text=_("End of line" ), variable=self.wordModeSelectVariable, value=5 )
        self.rwmb5.pack( in_=wordLimitsFrame, side=tk.TOP, fill=tk.X )

        #self.mcaseVar = tk.IntVar()
        #if not self.optionsDict['caselessFlag']: self.mcaseVar.set( 1 )
        #mcaseCb = tk.Checkbutton( master, text=_("Match case"), variable=self.mcaseVar )
        ##mcaseCb.grid( row=7, column=0, padx=0, pady=5, sticky=tk.W )
        #mcaseCb.pack( in_=wordLimitsFrame, side=tk.TOP, anchor=tk.W, padx=0, pady=1 )
        #self.diaVar = tk.IntVar()
        #if self.optionsDict['ignoreDiacriticsFlag']: self.diaVar.set( 1 )
        #diaCb = tk.Checkbutton( master, text=_("Ignore diacritics"), variable=self.diaVar )
        ##diaCb.grid( row=7, column=2, padx=0, pady=5, sticky=tk.W )
        #diaCb.pack( in_=wordLimitsFrame, side=tk.TOP, anchor=tk.W, padx=0, pady=1 )

        bookLimitsFrame = tk.LabelFrame( master, text=_("Book limits"), padx=5, pady=5 )
        bookLimitsFrame.grid( row=3, column=2, padx=10, pady=10, sticky=tk.W )

        self.booksSelectVariable = tk.IntVar()
        if self.optionsDict['bookList'] == 'ALL': self.booksSelectVariable.set( 1 )
        elif self.optionsDict['bookList'] == self.optionsDict['currentBCV'][0]:
            #if self.optionsDict['chapterList'] == None: self.booksSelectVariable.set( 2 )
            #else:
            self.booksSelectVariable.set( 3 )
        elif isinstance( self.optionsDict['bookList'], list ): self.booksSelectVariable.set( 4 )
        else: halt # programming error

        allText = _("All {} books").format( len(self.givenBible) ) if len(self.givenBible)>2 else _("All books")
        self.rbb1 = Radiobutton( master, text=allText, variable=self.booksSelectVariable, value=1 )
        self.rbb1.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rbb3.grid( row=5, column=2, padx=2, pady=1, sticky=tk.W )
        if isinstance( self.optionsDict['bookList'], list ):
            if len( self.optionsDict['bookList'] ) == 1: sbText = self.optionsDict['bookList'][0]
            else: sbText = len( self.optionsDict['bookList'] )
        else: sbText = 0
        self.rbb2 = Radiobutton( master, text=_("Current book")+" ({})".format( self.optionsDict['currentBCV'][0] ), variable=self.booksSelectVariable, value=2 )
        self.rbb2.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rbb3 = Radiobutton( master, text=_("Current chapter")+" ({} {})".format( self.optionsDict['currentBCV'][0], self.optionsDict['currentBCV'][1] ), variable=self.booksSelectVariable, value=3 )
        #self.rbb3.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        sbText = '(N/A)' if self.optionsDict['bookList']=='ALL' \
            else ', '.join(self.optionsDict['bookList']) if len(self.optionsDict['bookList'])<10 \
            else '({})'.format( len(self.optionsDict['bookList']) )
        self.rbb4 = Radiobutton( master, text=_('Selected books {}').format( sbText ), variable=self.booksSelectVariable, value=4 )
        self.rbb4.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        bb = Button( master, text=_("Select books…"), command=self.selectBooks )
        bb.pack( in_=bookLimitsFrame, side=tk.TOP, anchor=tk.E )

        #fieldLimitsFrame = tk.LabelFrame( master, text=_("Field limits"), padx=5, pady=5 )
        #fieldLimitsFrame.grid( row=4, column=2, padx=10, pady=10, sticky=tk.W )

        #self.introVar = tk.IntVar()
        #if self.optionsDict['includeIntroFlag']: self.introVar.set( 1 )
        #introCb = tk.Checkbutton( master, text=_("Include introductions"), variable=self.introVar )
        ##introCb.grid( row=7, column=0, padx=0, pady=5, sticky=tk.W )
        #introCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )
        #self.mainTextVar = tk.IntVar()
        #if self.optionsDict['includeMainTextFlag']: self.mainTextVar.set( 1 )
        #mainTextCb = tk.Checkbutton( master, text=_("Include main text"), variable=self.mainTextVar )
        ##mainTextCb.grid( row=7, column=0, padx=0, pady=5, sticky=tk.W )
        #mainTextCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )
        #self.markersTextVar = tk.IntVar()
        #if self.optionsDict['includeMarkerTextFlag']: self.markersTextVar.set( 1 )
        #markersCb = tk.Checkbutton( master, text=_("Include text of markers"), variable=self.markersTextVar )
        ##markersCb.grid( row=7, column=0, padx=0, pady=5, sticky=tk.W )
        #markersCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )
        #self.extrasVar = tk.IntVar()
        #if self.optionsDict['includeExtrasFlag']: self.extrasVar.set( 1 )
        #extrasCb = tk.Checkbutton( master, text=_("Include footnotes & cross-references"), variable=self.extrasVar )
        ##extrasCb.grid( row=7, column=0, padx=0, pady=5, sticky=tk.W )
        #extrasCb.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, padx=2, pady=1 )

        #markerListFrame = tk.Frame( master, padx=5, pady=5 )
        #markerListFrame.pack( in_=fieldLimitsFrame, side=tk.TOP, anchor=tk.W, fill=tk.X, padx=2, pady=1 )
        #self.theseMarkersOnlyVar = tk.IntVar()
        #if self.optionsDict['markerList']:
            #self.theseMarkersOnlyVar.set( 1 )
            #self.introVar.set( 0 ); self.mainTextVar.set( 0 ); self.markersTextVar.set( 0 ); self.extrasVar.set( 0 )
        #theseMarkersCb = tk.Checkbutton( master, text=_("Only this marker(s):"), variable=self.theseMarkersOnlyVar )
        #theseMarkersCb.pack( in_=markerListFrame, side=tk.LEFT, padx=2, pady=1 )
        #self.theseMarkersListVar = tk.StringVar()
        #self.theseMarkersListVar.set( ','.join(mkr for mkr in self.optionsDict['markerList']) if self.optionsDict['markerList'] else '' )
        #registeredFunction = self.register( self.doMarkerListentry )
        #theseMarkersEntry = BEntry( master, textvariable=self.theseMarkersListVar, validate='all', validatecommand=(registeredFunction,'%P') )
        #theseMarkersEntry.pack( in_=markerListFrame, side=tk.RIGHT, padx=2, pady=1 )

        return self.searchStringBox # initial focus
    # end of GetBibleReplaceTextDialog.makeBody


    def selectBooks( self ):
        """
        """
        self.parentWindow._prepareInternalBible() # Slow but must be called before the dialog
        currentBBB = self.optionsDict['currentBCV'][0]
        gBBRD = GetBibleBookRangeDialog( self, self.givenBible, currentBBB, self.optionsDict['bookList'], title=_('Books to be Replaceed') )
        if BibleOrgSysGlobals.debugFlag: print( "selectBooks gBBRDResult", repr(gBBRD.result) )
        if gBBRD.result: # Returns a list of books
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBBRD.result, list )
            if len(gBBRD.result)==1 and gBBRD.result[0]==currentBBB:
                # It's just the current book to Replace
                self.booksSelectVariable.set( 2 )
            else:
                self.booksSelectVariable.set( 4 )
                self.optionsDict['bookList'] = gBBRD.result
                sbText = '(N/A)' if self.optionsDict['bookList']=='ALL' \
                    else ', '.join(self.optionsDict['bookList']) if len(self.optionsDict['bookList'])<10 \
                    else '({})'.format( len(self.optionsDict['bookList']) )
                self.rbb4['text'] = text=_('Selected books {}').format( sbText )
            #self.update()
        else: print( "selectBooks: No books selected!" )
    # end of GetBibleReplaceTextDialog.apply


    #def doMarkerListentry( self, willBe ):
        #"""
        #"""
        ##print( "doMarkerListentry( {!r} )".format( willBe ) )
        ##thisText = self.theseMarkersListVar.get()
        #if willBe: # There's something in the entry
            #self.theseMarkersOnlyVar.set( 1 )
            #self.introVar.set( 0 ); self.mainTextVar.set( 0 ); self.markersTextVar.set( 0 ); self.extrasVar.set( 0 )
        #else: self.theseMarkersOnlyVar.set( 0 )
        #for char in willBe:
            #if char not in ' abcdefghijklmnopqrstuvwxyz1234,': return False
        #return True # accept it
    ## end of GetBibleReplaceTextDialog.doMarkerListentry


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        #print( "GetBibleReplaceTextDialog.validate()" )

        ## Do some normalization first
        #theseMarkersOnlyText = self.theseMarkersListVar.get()
        #if theseMarkersOnlyText: # check that they're valid newline markers
            ## First normalize the entries
            #theseMarkersOnlyText = theseMarkersOnlyText.strip().replace('  ',' ').replace(' ',',').replace(',,,',',').replace(',,',',').replace(',',', ')
            #self.theseMarkersListVar.set( theseMarkersOnlyText )
            #self.theseMarkersOnlyVar.set( 1 )
        #if theseMarkersOnlyText: # check that they're valid newline markers
            #markerList = []
            #for marker in theseMarkersOnlyText.split( ',' ):
                ##print( "marker", marker )
                #marker = marker.strip()
                #if marker in BibleOrgSysGlobals.loadedUSFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                    #markerList.append( marker )
                #else: # not a valid newline marker
                    #showWarning( self.parentWindow, APP_NAME, _("{!r} is not a valid newline marker!").format( marker ) ); return False
        #else: # Nothing in the entry
            #self.theseMarkersOnlyVar.set( 0 )

        # Now check for bad combinations
        findText = self.searchStringVar.get()
        if not findText: showWarning( self.parentWindow, APP_NAME, _("Nothing to search for!") ); return False
        if findText.lower() == 'regex:': showWarning( self.parentWindow, APP_NAME, _("No regular expression to search for!") ); return False
        replaceText = self.replaceStringVar.get()
        if replaceText.lower().startswith( 'regex:' ): showWarning( self.parentWindow, APP_NAME, _("Don't start replace field with 'regex:'!") ); return False
        bookResultNumber = self.booksSelectVariable.get()
        if bookResultNumber==4 and ( not self.optionsDict['bookList'] or not isinstance(self.optionsDict['bookList'], list) ):
            showWarning( self.parentWindow, APP_NAME, _("No books selected to search in!") ); return False
        #if self.theseMarkersOnlyVar.get():
            #if self.introVar.get() or  self.mainTextVar.get() or self.markersTextVar.get() or self.extrasVar.get():
                #showWarning( self.parentWindow, APP_NAME, _("Bad combination of fields selected!") ); return False
        return True # Must be ok
    # end of GetBibleReplaceTextDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        #print( "GetBibleReplaceTextDialog.apply()" )

        workName = self.projectNameVar.get()
        if workName != self.optionsDict['workName']: # then they've changed it
            self.optionsDict['workName'] = workName
            descr,window,box,iB = self.projectDict[workName]
            assert descr in ( 'Window', 'Box' )
            self.optionsDict['parentWindow'] = window
            self.optionsDict['parentBox'] = box
            self.optionsDict['parentApp'] = window.parentApp
            self.optionsDict['givenBible'] = iB

        self.optionsDict['findText'] = self.searchStringVar.get()
        self.optionsDict['replaceText'] = self.replaceStringVar.get()

        wordModeResultNumber = self.wordModeSelectVariable.get()
        if wordModeResultNumber == 1: self.optionsDict['wordMode'] = 'Any'
        elif wordModeResultNumber == 2: self.optionsDict['wordMode'] = 'Whole'
        elif wordModeResultNumber == 3: self.optionsDict['wordMode'] = 'Begins'
        elif wordModeResultNumber == 4: self.optionsDict['wordMode'] = 'EndsWord'
        elif wordModeResultNumber == 5: self.optionsDict['wordMode'] = 'EndsLine'
        else:
            halt # Unexpected result value

        bookResultNumber = self.booksSelectVariable.get()
        #self.optionsDict['chapterList'] = None
        if bookResultNumber == 1: self.optionsDict['bookList'] = 'ALL'
        elif bookResultNumber == 2: self.optionsDict['bookList'] = self.optionsDict['currentBCV'][0]
        #elif bookResultNumber == 3:
            #self.optionsDict['bookList'] = self.optionsDict['currentBCV'][0]
            #self.optionsDict['chapterList'] = [self.optionsDict['currentBCV'][1]]
        elif bookResultNumber == 4: #self.optionsDict['bookList'] should already be set
            pass
        else:
            if BibleOrgSysGlobals.debugFlag: halt # Unexpected result value

        # Checkboxes
        #self.optionsDict['caselessFlag'] = not self.mcaseVar.get()
        #self.optionsDict['ignoreDiacriticsFlag'] = bool( self.diaVar.get() )
        #self.optionsDict['includeIntroFlag'] = bool( self.introVar.get() )
        #self.optionsDict['includeMainTextFlag'] = bool( self.mainTextVar.get() )
        #self.optionsDict['includeExtrasFlag'] = bool( self.extrasVar.get() )
        #self.optionsDict['includeMarkerTextFlag'] = bool( self.markersTextVar.get() )
        #if self.optionsDict['includeIntroFlag'] or self.optionsDict['includeMainTextFlag'] \
        #or self.optionsDict['includeExtrasFlag'] or self.optionsDict['includeMarkerTextFlag']:
            #self.optionsDict['markerList'] = None
        #else:
            #theseMarkersOnlyText = self.theseMarkersListVar.get()
            #if theseMarkersOnlyText: # check that they're valid newline markers
                ## First normalize the entries
                #theseMarkersOnlyText = theseMarkersOnlyText.strip().replace('  ',' ').replace(' ',',').replace(',,,',',').replace(',,',',').replace(',',', ')
            #if theseMarkersOnlyText: # check that they're valid newline markers
                #markerList = []
                #for marker in theseMarkersOnlyText.split( ',' ):
                    ##print( "marker", marker )
                    #marker = marker.strip()
                    #if marker in BibleOrgSysGlobals.loadedUSFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                        #markerList.append( marker )
                    #else: halt # not a valid newline marker
                #if markerList: self.optionsDict['markerList'] = markerList

        self.result = self.optionsDict
    # end of GetBibleReplaceTextDialog.apply
# end of class GetBibleReplaceTextDialog



class ReplaceConfirmDialog( ModalDialog ):
    """
    """
    def __init__( self, parentWindow, referenceString, contextBefore, findText, contextAfter, finalText, haveUndos, title ):
        """
        optionsDict must already contain 'currentBCV'
        """
        if BibleOrgSysGlobals.debugFlag:
            parentWindow.parentApp.setDebugText( "ReplaceConfirmDialog…" )
            assert isinstance( contextBefore, str )
            assert isinstance( contextAfter, str )
        self.referenceString, self.contextBefore, self.findText, self.contextAfter, self.finalText, self.haveUndos = referenceString, contextBefore, findText, contextAfter, finalText, haveUndos
        ModalDialog.__init__( self, parentWindow, title )
    # end of ReplaceConfirmDialog.__init__


    def makeBody( self, master ):
        """
        """
        #from TextBoxes import BText
        label1 = Label( master, text=self.referenceString )
        label1.pack( side=tk.TOP )
        label2 = Label( master, text=_('Before') )
        label2.pack( side=tk.TOP, anchor=tk.W )
        textBox1 = BText( master, height=5 )
        textBox1.insert( tk.END, self.contextBefore+self.findText+self.contextAfter )
        textBox1.configure( state=tk.DISABLED )
        textBox1.pack( side=tk.TOP, fill=tk.X )
        label3 = Label( master, text=_('After') )
        label3.pack( side=tk.TOP, anchor=tk.W )
        textBox2 = BText( master, height=5 )
        textBox2.insert( tk.END, self.finalText )
        textBox2.configure( state=tk.DISABLED )
        textBox2.pack( side=tk.TOP, fill=tk.X )

        #buttonFrame = tk.Frame( master, padx=5, pady=5 )
        #buttonFrame.pack( side=tk.BOTTOM, anchor=tk.E, fill=tk.X, padx=2, pady=1 )
        #yesButton = Button( master, text=_('Yes'), command=self.doYes )
        #yesButton.pack( in_=buttonFrame, side=tk.LEFT, padx=2, pady=2 )
        #noButton = Button( master, text=_('No'), command=self.doNo )
        #noButton.pack( in_=buttonFrame, side=tk.LEFT, padx=2, pady=2 )
        #allButton = Button( master, text=_('All'), command=self.doAll )
        #allButton.pack( in_=buttonFrame, side=tk.LEFT, padx=2, pady=2 )
        #cancelButton = Button( master, text=_('Stop'), command=self.doStop )
        #cancelButton.pack( in_=buttonFrame, side=tk.LEFT, padx=2, pady=2 )

        #return yesButton
        return 0
    # end of ReplaceConfirmDialog.makeBody

    def makeButtonBox( self ):
        """
        Add our custom button box
        """
        box = Frame( self )

        yesButton = Button( box, text=_('Yes (Replace)'), command=self.doYes, default=tk.ACTIVE )
        yesButton.pack( side=tk.LEFT, padx=5, pady=5 )
        noButton = Button( box, text=_('No'), width=10, command=self.doNo )
        noButton.pack( side=tk.LEFT, padx=5, pady=5 )
        allButton = Button( box, text=_('All (Yes)'), width=10, command=self.doAll )
        allButton.pack( side=tk.LEFT, padx=5, pady=5 )
        cancelButton = Button( box, text=_('Stop (No more)') if self.haveUndos else _('Stop (None)'), command=self.doStop )
        cancelButton.pack( side=tk.LEFT, padx=5, pady=5 )
        undoButton = Button( box, text=_('Undo all'), width=10, command=self.doUndo )
        undoButton.pack( side=tk.LEFT, padx=5, pady=5 )
        if not self.haveUndos: undoButton.configure( state=tk.DISABLED )

        self.bind( '<Return>', self.doYes )
        self.bind( '<Escape>', self.doStop )

        box.pack( side=tk.BOTTOM, anchor=tk.E )
    # end of ModalDialog.makeButtonBox

    def doYes( self, event=None ):
        self.result = 'Y'
        self.cancel()
    # end of ReplaceConfirmDialog.doYes

    def doNo( self, event=None ):
        self.result = 'N'
        self.cancel()
    # end of ReplaceConfirmDialog.doNo

    def doAll( self, event=None ):
        self.result = 'A'
        self.cancel()
    # end of ReplaceConfirmDialog.doAll

    def doStop( self, event=None ):
        self.result = 'S'
        self.cancel()
    # end of ReplaceConfirmDialog.doStop

    def doUndo( self, event=None ):
        self.result = 'U'
        self.cancel()
    # end of ReplaceConfirmDialog.doStop
# end of class ReplaceConfirmDialog



class SelectInternalBibleDialog( ModalDialog ):
    """
    Select one internal Bible from a given list.
    """
    def __init__( self, parentWindow, title, internalBibles ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "SelectInternalBibleDialog…" )
        self.internalBibles = internalBibles
        ModalDialog.__init__( self, parentWindow, title )
    # end of SelectInternalBibleDialog.__init__


    def makeButtonBox( self ):
        """
        Do our custom buttonBox (without an ok button)
        """
        box = Frame( self )
        w = Button( box, text=self.cancelText, width=10, command=self.cancel )
        w.pack( side=tk.LEFT, padx=5, pady=5 )
        self.bind( '<Escape>', self.cancel )
        box.pack( side=tk.BOTTOM )
    # end of SelectInternalBibleDialog.makeButtonBox


    def makeBody( self, master ):
        """
        Adapted from http://stackoverflow.com/questions/7591294/how-to-create-a-self-resizing-grid-of-buttons-in-tkinter
        """
        buttonsAcross = 2
        #if numBooks > 100: buttonsAcross = 12
        #elif numBooks > 80: buttonsAcross = 10
        #elif numBooks > 60: buttonsAcross = 8
        #elif numBooks > 30: buttonsAcross = 6
        xPad, yPad = 6, 8

        grid=Frame( master )
        grid.grid( column=0, row=7, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W )
        tk.Grid.rowconfigure( master, 7, weight=1 )
        tk.Grid.columnconfigure( master, 0, weight=1 )

        Style().configure( 'iB.TButton', background='lightgreen' )
        #Style().configure( 'selectedBN.TButton', background='orange' )
        for j,iB in enumerate(self.internalBibles):
            row, col = j // buttonsAcross, j % buttonsAcross
            BibleName = iB.getAName()
            #print( j, row, col )
            Button( master, width=30, text=iB.getAName(), style='iB.TButton', \
                                command=lambda which=j: self.apply(which) ) \
                        .grid( column=col, row=row, padx=xPad, pady=yPad, sticky=tk.N+tk.S+tk.E+tk.W )
        #col += 1
        #if col >= buttonsAcross: row +=1; col=0
        #Button( master, text=_("Cancel"), command=lambda which='CANCEL': self.apply(which) ) \
                    #.grid( column=col, row=row, padx=xPad, pady=yPad, sticky=tk.N+tk.S+tk.E+tk.W )

        for x in range(10):
            tk.Grid.columnconfigure( master, x, weight=1 )
        for y in range(5):
            tk.Grid.rowconfigure( master, y, weight=1 )
        #for j,bookName in enumerate(self.bookNameList):
            #Button( master, width=6, text=bookName, style='bN.TButton', command=lambda which=j: self.apply(which) ) \
                        #.grid()
        #return 0
    # end of SelectInternalBibleDialog.makeBody


    def apply( self, buttonNumber ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        #if buttonNumber!='CANCEL': self.result = buttonNumber
        self.result = buttonNumber
        self.cancel() # We want to exit the dialog immediately
    # end of SelectInternalBibleDialog.apply
# end of class SelectInternalBibleDialog



#class GetSwordPathDialog( ModalDialog ):
    #"""
    #Get the folder path to search for Sword modules (none found in "normal" places).
    #"""
    #def __init__( self, parentWindow, title ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "GetSwordPathDialog…" )
        #self.alreadyTriedList = []
        #ModalDialog.__init__( self, parentWindow, title )
    ## end of GetSwordPathDialog.__init__


    #def setAlreadyTriedList( self, alreadyTriedList ):
        #self.alreadyTriedList = alreadyTriedList
    ## end of GetSwordPathDialog.setAlreadyTriedList


    #def makeBody( self, master ):
        #"""
        #Override the empty ModalDialog.makeBody function
            #to set up the dialog how we want it.
        #"""
        #Label( master, text=_("Already tried:") ).grid( row=0 )
        #Label( master, text=_("New path to Sword modules:") ).grid( row=1 )

        #l1 = Label( master, text=self.alreadyTriedList if self.alreadyTriedList else _("Unknown") )
        #self.e1 = BEntry( master )

        #l1.grid( row=0, column=1 )
        #self.e1.grid( row=1, column=1 )
        #return self.e1 # initial focus
    ## end of GetSwordPathDialog.makeBody


    #def validate( self ):
        #"""
        #Override the empty ModalDialog.validate function
            #to check that the results are how we need them.

        #Returns True or False.
        #"""
        #enteredPath = self.e1.get()
        #if not os.path.isdir( enteredPath):
            #showWarning( self.parentWindow, APP_NAME, _("Pathname seems invalid") ); return False
        #epAdjusted = enteredPath.lower().replace( '\\', '/' )
        #if epAdjusted[-1] != '/': epAdjusted += '/'
        #if epAdjusted.endswith( 'mods.d/'):
            #showWarning( self.parentWindow, APP_NAME, _("Pathname shouldn't include mods.d") ); return False
        #if not os.path.isdir( os.path.join( enteredPath, 'mods.d/' ) ):
            #showWarning( self.parentWindow, APP_NAME, _("Pathname seems to have no 'mods.d' subfolder") ); return False
        #return True
    ## end of GetSwordPathDialog.validate


    #def apply( self ):
        #"""
        #Override the empty ModalDialog.apply function
            #to process the results how we need them.

        #Results are left in self.result
        #"""
        #enteredPath = self.e1.get()
        #self.result = enteredPath
    ## end of GetSwordPathDialog.apply
## end of class GetSwordPathDialog



class GetHebrewGlossWordDialog( ModalDialog ):
    """
    Get a new (gloss) word from the user.

    Accepts a bundle (e.g., list, tuple) of short strings to display to the user first.

    Unlike our other dialogues, this one can remember its size and position.

    Returns:
        S for skip,
        L, R for left/right, or LL, RR
        or None for cancel,
        or else a dictionary possibly containing 'word','command','geometry'
    """
    def __init__( self, parentWindow, title, contextLines, word='', geometry=None ):
        """
        """
        #print( "GetHebrewGlossWordDialog( …, …, {}, {!r}, {} )".format( contextLines, word, geometry ) )
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "GetHebrewGlossWordDialog…" )
        self.parentWindow, self.contextLines, self.word = parentWindow, contextLines, word

        self.customHebrewFont = tkFont.Font( family='Ezra', size=20 )
        self.customFont = tkFont.Font( family='Helvetica', size=12 )

        self.transliterationScheme = 'Names'

        self.returnCommand = None
        ModalDialog.__init__( self, parentWindow, title, geometry=geometry )
    # end of GetHebrewGlossWordDialog.__init__


    def handleStrongs( self, textString ):
        """
        Given a string, see if a Strong's number can be found
            and if so, direct the lexicon to this entry.

        Typical strings might be '8034', 'd/776', '3651 c', '8423+'

        NOTE: doesn't change/update the lexicon word in the main app window.
        """
        #print( "handleStrongs( {!r} )".format( textString ) )
        if debuggingThisModule or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
            assert textString

        if textString[-1] == '+': textString = textString[:-1] # Is this general enough -- maybe we just to remove all + signs???

        strongsNumber = None
        if textString.isdigit(): strongsNumber = textString
        else:
            for smallerString in textString.split( '/' ):
                if smallerString.isdigit(): strongsNumber = smallerString; break
                else:
                    for smallestString in smallerString.split( ' ' ):
                        if smallestString.isdigit(): strongsNumber = smallestString; break
                if strongsNumber: break
        if strongsNumber:
            self.parentWindow.parentApp.childWindows.updateLexicons( 'H' + strongsNumber )
    # end of GetHebrewGlossWordDialog.handleStrongs


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        row = 0
        Style().configure( 'LR.TButton', background='orange', font=('Helvetica', 24) )
        Button( master, text='<<', width=3, style='LR.TButton', command=self.doGoLeft2 ).grid( row=row, column=0 )
        Button( master, text='<', width=3, style='LR.TButton', command=self.doGoLeft1 ).grid( row=row, column=1 )
        Button( master, text='>', width=3, style='LR.TButton', command=self.doGoRight1 ).grid( row=row, column=3 )
        Button( master, text='>>', width=3, style='LR.TButton', command=self.doGoRight2 ).grid( row=row, column=4 )
        for j,line in enumerate( self.contextLines ):
            if not line: continue # skip missing lines
            thisFont = self.customFont
            if j == 1:
                if not self.word \
                and ( line.startswith( 'ו' 'ַ' '=' ) or line.startswith( 'ו' 'ָ' '=' ) \
                  or line.startswith( 'ו' 'ְ' '=' ) ):
                    self.word = 'and='
                line = line[::-1] # Reverse line to simulate RTL Hebrew language
                thisFont = self.customHebrewFont
            elif j == 2: self.handleStrongs( line )
            if len(line) > 20:
                Label( master, text=line, font=thisFont ).grid( row=row, column=0, columnspan=5 )
            else: Label( master, text=line, font=thisFont ).grid( row=row, column=1, columnspan=3 )
            row += 1

        self.entry = BEntry( master )
        self.entry.grid( row=row, column=2 )
        if self.word: self.entry.insert( 0, self.word )
        return self.entry # initial focus
    # end of GetHebrewGlossWordDialog.makeBody


    def makeButtonBox( self ):
        """
        Add our custom button box
        """
        box = Frame( self )

        cancelButton = Button( box, text=self.cancelText, width=10, command=self.cancel )
        cancelButton.pack( side=tk.RIGHT, padx=5, pady=5 )
        okButton = Button( box, text=self.okText, width=10, command=self.ok, default=tk.ACTIVE )
        okButton.pack( side=tk.RIGHT, padx=5, pady=5 )
        skipOoneButton = Button( box, text=_('Skip this one'), command=self.doSkipOne )
        skipOoneButton.pack( side=tk.RIGHT, padx=5, pady=5 )
        translitButton = Button( box, text=_('Transliterate'), command=self.doTransliterate )
        translitButton.pack( side=tk.LEFT, padx=5, pady=5 )

        self.bind( '<Return>', self.ok )
        self.bind( '<Escape>', self.cancel )

        box.pack( side=tk.BOTTOM, fill=tk.X )
    # end of GetHebrewGlossWordDialog.makeButtonBox


    def doTransliterate( self ):
        """
        Copy a transliterated version of the Hebrew text into the entry.
        """
        from Hebrew import Hebrew

        #if not self.entry.get():
        self.entry.delete( 0, tk.END )

        h = Hebrew( self.contextLines[1] )
        transliterated = h.transliterate( scheme=self.transliterationScheme )

        # Rotate through possible schemes
        if self.transliterationScheme=='Names':
            self.transliterationScheme = 'Default'
            transliterated = transliterated.title()
        elif self.transliterationScheme=='Default': self.transliterationScheme = 'Standard'
        elif self.transliterationScheme=='Standard': self.transliterationScheme = 'Names'

        self.entry.insert( 0, transliterated )
    # end of GetHebrewGlossWordDialog.doTransliterate


    def doGoLeft1( self, event=None ):
        self.result = self.returnCommand = 'L'
        self.ok() if self.entry.get() else self.cancel() # So don't have to have text
    # end of GetHebrewGlossWordDialog.doGoLeft

    def doGoRight1( self, event=None ):
        self.result = self.returnCommand = 'R'
        self.ok() if self.entry.get() else self.cancel() # So don't have to have text
    # end of GetHebrewGlossWordDialog.doGoRight

    def doGoLeft2( self, event=None ):
        self.result = self.returnCommand = 'LL'
        self.ok() if self.entry.get() else self.cancel() # So don't have to have text
    # end of GetHebrewGlossWordDialog.doGoLeft

    def doGoRight2( self, event=None ):
        self.result = self.returnCommand = 'RR'
        self.ok() if self.entry.get() else self.cancel() # So don't have to have text
    # end of GetHebrewGlossWordDialog.doGoRight


    def doSkipOne( self, event=None ):
        self.result = 'S'
        self.cancel() # So don't have to have text
    # end of GetHebrewGlossWordDialog.doSkipOne


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        resultWord = self.entry.get()
        for illegalChar in ' :;"@#\\{}':
            if illegalChar in resultWord:
                showWarning( self.parentWindow, APP_NAME, _("Not allowed {} characters") \
                                    .format( _('space') if illegalChar==' ' else illegalChar ) )
                return False
        if resultWord.count('=') != self.contextLines[1].count('='):
            showWarning( self.parentWindow, APP_NAME, _("Number of morpheme breaks (=) must match") )
            return False
        return True
    # end of GetHebrewGlossWordDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = { 'geometry':self.geometry() }
        word = self.entry.get()
        if word: self.result['word'] = word
        if self.returnCommand: self.result['command'] = self.returnCommand
    # end of GetHebrewGlossWordDialog.apply
# end of class GetHebrewGlossWordDialog



class GetHebrewGlossWordsDialog( GetHebrewGlossWordDialog ):
    """
    Get up to two new (gloss) words from the user.
        The first one (usually generic gloss) is compulsory.
        The second one (usually specific gloss) is optional.

    Accepts a bundle (e.g., list, tuple) of short strings to display to the user first.

    Unlike our other dialogues, this one can remember its size and position.

    Returns:
        S for skip,
        L, R for left/right, or LL, RR
        or None for cancel,
        or else a dictionary possibly containing 'word1','word2','command','geometry'
    """
    def __init__( self, parentWindow, title, contextLines, word1='', word2='', geometry=None ):
        """
        """
        #print( "GetHebrewGlossWordsDialog( …, …, {}, {!r}, {!r}, {} )".format( contextLines, word1, word2, geometry ) )
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "GetHebrewGlossWordsDialog…" )
        self.parentWindow, self.contextLines, self.word, self.word2 = parentWindow, contextLines, word1, word2

        self.customHebrewFont = tkFont.Font( family='Ezra', size=20 )
        self.customFont = tkFont.Font( family='Helvetica', size=12 )

        self.transliterationScheme = 'Names'

        self.returnCommand = None
        ModalDialog.__init__( self, parentWindow, title, geometry=geometry )
    # end of GetHebrewGlossWordsDialog.__init__


    def makeBody( self, master ):
        """
        Override the empty ModalDialog.makeBody function
            to set up the dialog how we want it.
        """
        row = 0
        Style().configure( 'LR.TButton', background='orange', font=('Helvetica', 24) )
        Button( master, text='<<', width=3, style='LR.TButton', command=self.doGoLeft2 ).grid( row=row, column=0 )
        Button( master, text='<', width=3, style='LR.TButton', command=self.doGoLeft1 ).grid( row=row, column=1 )
        Button( master, text='>', width=3, style='LR.TButton', command=self.doGoRight1 ).grid( row=row, column=3 )
        Button( master, text='>>', width=3, style='LR.TButton', command=self.doGoRight2 ).grid( row=row, column=4 )
        for j,line in enumerate( self.contextLines ):
            if not line: continue # skip missing lines
            thisFont = self.customFont
            if j == 1:
                if not self.word \
                and ( line.startswith( 'ו' 'ַ' '=' ) or line.startswith( 'ו' 'ָ' '=' ) \
                  or line.startswith( 'ו' 'ְ' '=' ) ):
                    self.word = 'and='
                line = line[::-1] # Reverse line to simulate RTL Hebrew language
                thisFont = self.customHebrewFont
            elif j == 2: self.handleStrongs( line )
            if len(line) > 20:
                Label( master, text=line, font=thisFont ).grid( row=row, column=0, columnspan=5 )
            else: Label( master, text=line, font=thisFont ).grid( row=row, column=1, columnspan=3 )
            row += 1

        self.entry = BEntry( master )
        self.entry.grid( row=row, column=2 )
        self.entry2 = BEntry( master )
        self.entry2.grid( row=row+1, column=2 )
        if self.word: self.entry.insert( 0, self.word )
        if self.word2: self.entry2.insert( 0, self.word2 )
        return self.entry # initial focus
    # end of GetHebrewGlossWordsDialog.makeBody


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        resultWord1, resultWord2 = self.entry.get(), self.entry2.get()
        if not resultWord1: return False # It's compulsory
        for resultWord in ( resultWord1, resultWord2 ):
            for illegalChar in ' :;"@#\\{}':
                if illegalChar in resultWord:
                    showWarning( self.parentWindow, APP_NAME, _("Not allowed {} characters") \
                                        .format( _('space') if illegalChar==' ' else illegalChar ) )
                    return False
            if resultWord and resultWord.count('=') != self.contextLines[1].count('='):
                showWarning( self.parentWindow, APP_NAME, _("Number of morpheme breaks (=) must match") )
                return False
        return True
    # end of GetHebrewGlossWordsDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = { 'geometry':self.geometry() }
        word1, word2 = self.entry.get(), self.entry2.get()
        if word1: self.result['word1'] = word1
        if word2: self.result['word2'] = word2
        if self.returnCommand: self.result['command'] = self.returnCommand
    # end of GetHebrewGlossWordsDialog.apply
# end of class GetHebrewGlossWordsDialog



class ChooseResourcesDialog( ModalDialog ):
    """
    Given a list of available resources, select one and return the list item.
    """
    def __init__( self, parentWindow, availableResourceDictsList, title ):
        """
        NOTE: from the dictionaries in the list, we just use 'abbreviation' and 'givenName'
                to build up the list of available resources.
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "ChooseResourcesDialog…" )
        if BibleOrgSysGlobals.debugFlag:
            #if debuggingThisModule:
                #print( "aRDL", len(availableResourceDictsList), repr(availableResourceDictsList) ) # Should be a list of dicts
            assert isinstance( availableResourceDictsList, list )
        self.availableResourceDictsList = sorted( availableResourceDictsList, key=lambda aRD: aRD['abbreviation'] )
        ModalDialog.__init__( self, parentWindow, title )
    # end of ChooseResourcesDialog.__init__


    def makeBody( self, master ):
        """
        """
        Label( master, text=_("Select one or more resources to open") ).pack( side=tk.TOP, fill=tk.X )

        self.lb = tk.Listbox( master, selectmode=tk.EXTENDED )
        """ Note: selectmode can be
            SINGLE (just a single choice),
            BROWSE (same, but the selection can be moved using the mouse),
            MULTIPLE (multiple item can be choosen, by clicking at them one at a time), or
            tk.EXTENDED (multiple ranges of items can be chosen using the Shift and Control keyboard modifiers).
            The default is BROWSE.
            Use MULTIPLE to get “checklist” behavior,
            and tk.EXTENDED when the user would usually pick only one item,
                but sometimes would like to select one or more ranges of items. """
        maxAbbrevWidth = max([len(aRD['abbreviation']) for aRD in self.availableResourceDictsList])
        for availableResourceDict in self.availableResourceDictsList:
            #print( "aRD", repr(availableResourceDict) )
            abbrev = availableResourceDict['abbreviation']
            item = '{}{}{}'.format( abbrev, ' '*(1+maxAbbrevWidth-len(abbrev)), availableResourceDict['givenName'] )
            self.lb.insert( tk.END, item )
        self.lb.pack( fill=tk.BOTH, expand=tk.YES )

        return self.lb # initial focus
    # end of ChooseResourcesDialog.makeBody


    def makeButtonBox( self ):
        """
        Add our custom button box
        """
        box = Frame( self )

        downloadButton = Button( box, text=_('Download more…'), command=self.doDownloadMore, state=tk.NORMAL if self.parentWindow.parentApp.internetAccessEnabled else tk.DISABLED )
        downloadButton.pack( side=tk.LEFT, padx=5, pady=5 )
        okButton = Button( box, text=self.okText, width=10, command=self.ok, default=tk.ACTIVE )
        okButton.pack( side=tk.LEFT, padx=5, pady=5 )
        cancelButton = Button( box, text=self.cancelText, width=10, command=self.cancel )
        cancelButton.pack( side=tk.LEFT, padx=5, pady=5 )

        self.bind( '<Return>', self.ok )
        self.bind( '<Escape>', self.cancel )

        box.pack( side=tk.BOTTOM, anchor=tk.E )
    # end of ChooseResourcesDialog.makeButtonBox


    def doDownloadMore( self ):
        """
        Allow the user to select resources to download from Freely-Given.org.
        """
        self.parentApp = self.parentWindow.parentApp # Need to set this up before calling dialog from a dialog
        dRD = DownloadResourcesDialog( self, title=_('Resources to download') )
        if BibleOrgSysGlobals.debugFlag: print( "doDownloadMore dRD result", repr(dRD.result) )
        if dRD.result:
            #if BibleOrgSysGlobals.debugFlag: assert isinstance( dRD.result, list )
            self.result = 'rerunDialog'
            self.cancel() # Hand control back (then hopefully rerun with new data
        else: print( "doDownloadMore: " + _("Nothing was selected!") )
    # end of ChooseResourcesDialog.doDownloadMore


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Must be at least one selected (otherwise force them to select CANCEL).

        Returns True or False.
        """
        return self.lb.curselection()
    # end of ChooseResourcesDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result,
            in this case, a list of zippedPickle filenames.
        """
        #selectedItemIndexes = self.lb.curselection()
        #print( "selectedItemIndexes", repr(selectedItemIndexes) ) # a tuple of index integers
        self.result = [self.availableResourceDictsList[int(itemIndex)]['zipFilename'] for itemIndex in self.lb.curselection()] # now a sublist
        #print( "SelectResourceBoxDialog: Requested resource(s) is/are: {!r}".format( self.result ) )
    # end of SelectResourceBoxDialog.apply
# end of class ChooseResourcesDialog



class DownloadResourcesDialog( ModalDialog ):
    """
    Given a list of available downloadable resources (new or updates),
        select one or more and download it/them.

    Return result = number of successful downloads
    """
    def __init__( self, parentWindow, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentWindow.parentApp.setDebugText( "DownloadResourcesDialog…" )
        if BibleOrgSysGlobals.debugFlag:
            #if debuggingThisModule:
                #print( "aRDL", len(availableResourceDictsList), repr(availableResourceDictsList) ) # Should be a list of dicts
            assert isinstance( title, str )
        self.downloadCount = 0
        ModalDialog.__init__( self, parentWindow, title )
    # end of DownloadResourcesDialog.__init__


    def makeBody( self, master ):
        """
        NOTE: This needs to be https eventually

        NOTE: This code depends on the exact page sent by the server (not generalised enough)

        NOTE: We really need more information here than just the abbreviation and file creation date/time.
        """
        import re
        from datetime import datetime

        try: responseObject = urllib.request.urlopen( BibleOrgSysGlobals.DISTRIBUTABLE_RESOURCES_URL )
        except urllib.error.URLError:
            if BibleOrgSysGlobals.debugFlag:
                logging.critical( "DownloadResourcesDialog.makeBody: error fetching {}".format( BibleOrgSysGlobals.DISTRIBUTABLE_RESOURCES_URL ) )
            Label( master, text=_("Unable to connect to server") ).pack( side=tk.TOP, fill=tk.X )
            self.okButton.config( state=tk.DISABLED )
            return None
        responsePageSTR = responseObject.read().decode('utf-8')
        #print( "responsePageSTR", responsePageSTR )
        availableResourceList = []
        searchString = ZIPPED_PICKLE_FILENAME_END + '</a>'
        searchRegex1 = '<a href="(\\w{{2,10}}){}">'.format( ZIPPED_PICKLE_FILENAME_END.replace( '.', '\\.' ) )
        searchRegex2 = '>(20\\d\\d-\\d\\d-\\d\\d \\d\\d:\\d\\d) '
        for line in responsePageSTR.split( '\n' ):
            #print( "line", line )
            if searchString in line:
                #print( "usefulLine", line )
                match = re.search( searchRegex1, line )
                if match:
                    #print( "Matched", match.start(), match.end() )
                    #print( repr(match.group(0)), repr(match.group(1)) )
                    fileAbbreviation = match.group(1)
                    #print( "fileAbbreviation", fileAbbreviation )
                    match = re.search( searchRegex2, line )
                    if match:
                        #print( "Matched", match.start(), match.end() )
                        #print( repr(match.group(0)), repr(match.group(1)) )
                        dateTimeString = match.group(1)
                        #print( "dateString", repr(dateString), "timeString", repr(timeString) )
                        availableResourceList.append( (fileAbbreviation,dateTimeString) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "availableResourceList", len(availableResourceList), availableResourceList )

        if availableResourceList:
            maxAbbrevWidth = max([len(aR[0]) for aR in availableResourceList])
            self.downloadableList = []
            for abbrev,dateTimeString in availableResourceList:
                #print( "aRD", repr(availableResourceDict) )
                filename = abbrev + ZIPPED_PICKLE_FILENAME_END
                resourceFilepath = BibleOrgSysGlobals.DEFAULT_WRITEABLE_DOWNLOADED_RESOURCES_FOLDERPATH.joinpath( filename )
                itemString = None
                if os.path.exists( resourceFilepath ):
                    if debuggingThisModule: print( "You already have", resourceFilepath )
                    #print( os.stat(resourceFilepath) )
                    #print( os.stat(resourceFilepath).st_mtime, datetime.fromtimestamp(os.stat(resourceFilepath).st_mtime) )
                    #print( os.stat(resourceFilepath).st_ctime, datetime.fromtimestamp(os.stat(resourceFilepath).st_ctime) )
                    fileDateTime1 = datetime.fromtimestamp( os.stat(resourceFilepath).st_mtime )
                    fileDateTime2 = datetime.fromtimestamp( os.stat(resourceFilepath).st_ctime )
                    #print( "  fileDateTime1", fileDateTime1 )
                    serverDateTime = datetime.strptime( dateTimeString, '%Y-%m-%d %H:%M' )
                    #print( "  serverDateTime", serverDateTime )
                    if (serverDateTime - fileDateTime1 ).total_seconds() > 3600: # one hour later
                        if debuggingThisModule: print( "Updateable resource:", abbrev )
                        itemString = '{} {}{}{}'.format( _("Update"), abbrev, ' '*(1+maxAbbrevWidth-len(abbrev)), dateTimeString )
                    elif debuggingThisModule: print( "  Seems up-to-date:", abbrev )
                else: # Seems we don't have this one
                        if debuggingThisModule: print( "New resource:", abbrev )
                        itemString = '{}    {}{}{}'.format( _("New"), abbrev, ' '*(1+maxAbbrevWidth-len(abbrev)), dateTimeString )
                if itemString: self.downloadableList.append( (abbrev,itemString) )
            if self.downloadableList:
                Label( master, text=_("Select one or more resources to download") ).pack( side=tk.TOP, fill=tk.X )
                self.lb = tk.Listbox( master, selectmode=tk.EXTENDED )
                """ Note: selectmode can be
                    SINGLE (just a single choice),
                    BROWSE (same, but the selection can be moved using the mouse),
                    MULTIPLE (multiple items can be choosen, by clicking at them one at a time), or
                    tk.EXTENDED (multiple ranges of items can be chosen using the Shift and Control keyboard modifiers).
                    The default is BROWSE.
                    Use MULTIPLE to get “checklist” behavior,
                    and tk.EXTENDED when the user would usually pick only one item,
                        but sometimes would like to select one or more ranges of items. """
                for abbrev,itemString in self.downloadableList: self.lb.insert( tk.END, itemString )
                self.lb.pack( fill=tk.BOTH, expand=tk.YES )
                return self.lb # initial focus
            else:
                Label( master, text=_("No out-of-date resources discovered") ).pack( side=tk.TOP, fill=tk.X )
        else:
            Label( master, text=_("No downloadable resources discovered") ).pack( side=tk.TOP, fill=tk.X )
        self.okButton.config( state=tk.DISABLED )
    # end of DownloadResourcesDialog.makeBody


    def doDownloadFile( self, abbrev ):
        """
        """
        if self.parentWindow.parentApp.doDownloadResource( abbrev ):
            self.downloadCount += 1
    # end of DownloadResourcesDialog.doDownloadFile


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result,
            in this case, a list of zippedPickle filenames.
        """
        selectedItemIndexes = self.lb.curselection()
        #print( "selectedItemIndexes", repr(selectedItemIndexes) ) # a tuple of index integers
        for selectedItemIndex in selectedItemIndexes:
            self.doDownloadFile( self.downloadableList[selectedItemIndex][0] )
        self.result = self.downloadCount
    # end of SelectResourceBoxDialog.apply
# end of class DownloadResourcesDialog



def demo() -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )

    # We need to set a parentApp variable and setStatus/setReadyStatus functions
    class tempApp():
        def __init__( self ):
            self.childWindows=[]
            self.internetAccessEnabled = True
        def setStatus( self, newStatusText='' ): pass
        def setReadyStatus( self ): pass
    tkRootWindow.parentApp = tempApp()

    ynD = YesNoDialog( tkRootWindow, message="Choose yes or no", title="Testing YesNoDialog" )
    print( "YesNoResult", ynD.result )
    ocD = OkCancelDialog( tkRootWindow, message="Choose ok or cancel", title="Testing OkCancelDialog" )
    print( "OkCancelResult", ocD.result )
    bnD = BookNameDialog( tkRootWindow, bookNameList=["aaa","BBB","CcC"], currentIndex=1 )
    print( "BookNameResult", bnD.result )
    nbD = NumberButtonDialog( tkRootWindow, startNumber=1, endNumber=11, currentNumber=6 )
    print( "NumberButtonResult", nbD.result )
    swnd = SaveWindowsLayoutNameDialog( tkRootWindow, existingSettings=["aaa","BBB","CcC"], title="Test SWND" )
    print( "SaveWindowNameResult", swnd.result )
    dwnd = DeleteWindowsLayoutNameDialog( tkRootWindow, existingSettings=["aaa","BBB","CcC"], title="Test DWND" )
    print( "DeleteWindowNameResult", dwnd.result )
    srb = SelectResourceBoxDialog( tkRootWindow, availableSettingsList=[(x,y) for x,y, in {"ESV":"ENGESV","WEB":"ENGWEB","MS":"MBTWBT"}.items()], title="Test SRB" )
    print( "SelectResourceBoxResult", srb.result )
    gnpnD = GetNewProjectNameDialog( tkRootWindow, title="Testing GetNewProjectNameDialog" )
    print( "GetNewProjectNameResult", gnpnD.result )

    from BibleVersificationSystems import BibleVersificationSystems
    bvss = BibleVersificationSystems().loadData() # Doesn't reload the XML unnecessarily :)
    availableVersifications = bvss.getAvailableVersificationSystemNames()
    cnpfD = CreateNewProjectFilesDialog( tkRootWindow, title="Testing CreateNewProjectFilesDialog", currentBBB='PSA', availableVersifications=availableVersifications )
    print( "CreateNewProjectFilesResult", cnpfD.result )

    gncnD = GetNewCollectionNameDialog( tkRootWindow, existingNames=["aaa","BBB","CcC"], title="Testing GetNewCollectionNameDialog" )
    print( "GetNewCollectionNameResult", gncnD.result )
    rrcD = RenameResourceCollectionDialog( tkRootWindow, existingName="xyz", existingNames=["aaa","BBB","CcC"], title="Testing RenameResourceCollectionDialog" )
    print( "RenameResourceCollectionResult", rrcD.result )

    class internalBible():
        def __init__( self ): self.BBB='GEN'
        def __len__( self ): return 3
        def getBookList( self ): return ['EXO','MAT','REV']
        def getAName( self ): return 'Fred'
    testBible = internalBible()

    gbbrD = GetBibleBookRangeDialog( tkRootWindow, givenBible=testBible, currentBBB='SA1', currentList=["aaa","BBB","CcC"], title="Testing GetBibleBookRangeDialog" )
    print( "GetBibleBookRangeResult", gbbrD.result )

    sibbD = SelectIndividualBibleBooksDialog( tkRootWindow, availableList=["aaa","BBB"], currentList=["aaa","BBB","CcC"], title="Testing SelectIndividualBibleBooksDialog" )
    print( "SelectIndividualBibleBooksResult", sibbD.result )

    tkRootWindow.textBox = tk.Text( tkRootWindow, width=40, height=10 )
    testOptionsDict = {'currentBCV':('ACT','1','1')}
    gbftD = GetBibleFindTextDialog( tkRootWindow, givenBible=testBible, optionsDict=testOptionsDict, title="Testing GetBibleFindTextDialog" )
    print( "GetBibleFindTextResult", gbftD.result )
    gbrtD = GetBibleReplaceTextDialog( tkRootWindow, givenBible=testBible, optionsDict=testOptionsDict, title="Testing GetBibleReplaceTextDialog" )
    print( "GetBibleReplaceTextResult", gbrtD.result )
    rcD = ReplaceConfirmDialog( tkRootWindow, referenceString="def", contextBefore="abc", findText="def", contextAfter="ghi", finalText="xyz", haveUndos=True, title="Testing ReplaceConfirmDialog" )
    print( "ReplaceConfirmResult", rcD.result )

    sibD = SelectInternalBibleDialog( tkRootWindow, title="Testing SelectInternalBibleDialog", internalBibles=[testBible] )
    print( "SelectInternalBibleResult", sibD.result )

    ghgwD = GetHebrewGlossWordDialog( tkRootWindow, title="Testing GetHebrewGlossWordDialog", contextLines=['abc','def','ghi'], word="word" )
    print( "GetHebrewGlossWordResult", ghgwD.result )
    ghgwsD = GetHebrewGlossWordsDialog( tkRootWindow, title="Testing GetHebrewGlossWordsDialog", contextLines=['abc','def','ghi'], word1="generic", word2="specific" )
    print( "GetHebrewGlossWordsResult", ghgwsD.result )

    availableResourceDictsList = [{'abbreviation':"aaa",'givenName':"AAA",'zipFilename':'a.zip'},{'abbreviation':"ddd",'givenName':"BBB",'zipFilename':'b.zip'},{'abbreviation':"ccc",'givenName':"CCC",'zipFilename':'c.zip'}]
    crD = ChooseResourcesDialog( tkRootWindow, availableResourceDictsList=availableResourceDictsList, title="Testing ChooseResourcesDialog" )
    print( "ChooseResourcesResult", crD.result )
    drD = DownloadResourcesDialog( tkRootWindow, title="Testing DownloadResourcesDialog" )
    print( "DownloadResourcesResult", drD.result )

    #tkRootWindow.quit()

    # Start the program running
    #tkRootWindow.mainloop()
# end of BiblelatorDialogs.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BiblelatorDialogs.py
