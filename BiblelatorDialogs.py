#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorDialogs.py
#
# Various dialog windows for Biblelator Bible display/editing
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
Various modal dialog windows for Biblelator Bible display/editing.

    def showerror( parent, title, errorText )
    def showwarning( parent, title, warningText )
    def showinfo( parent, title, infoText )
    #class HTMLDialog( ModalDialog )
    class YesNoDialog( ModalDialog )
    class OkCancelDialog( ModalDialog )
    class SaveWindowNameDialog( ModalDialog )
    class DeleteWindowNameDialog( ModalDialog )
    class SelectResourceBoxDialog( ModalDialog )
    class GetNewProjectNameDialog( ModalDialog )
    class CreateNewProjectFilesDialog( ModalDialog )
    class GetNewCollectionNameDialog( ModalDialog )
    class RenameResourceCollectionDialog( ModalDialog )
    class GetBibleBookRangeDialog( ModalDialog )
    class GetBibleSearchTextDialog( ModalDialog )
    class GetBibleReplaceTextDialog( ModalDialog )
    class ReplaceConfirmDialog( ModalDialog )
    class SelectInternalBibleDialog( ModalDialog )
"""

from gettext import gettext as _

LastModifiedDate = '2016-12-12'
ShortProgName = "Biblelator"
ProgName = "Biblelator dialogs"
ProgVersion = '0.39'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import logging

import tkinter as tk
import tkinter.messagebox as tkmb
from tkinter.ttk import Style, Label, Combobox, Entry, Radiobutton, Button, Frame

# Biblelator imports
from BiblelatorGlobals import APP_NAME, errorBeep
from ModalDialog import ModalDialog
#from TextBoxes import HTMLText

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



def showerror( parent, title, errorText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("showerror( {}, {!r}, {!r} )").format( parent, title, errorText ) )

    logging.error( '{}: {}'.format( title, errorText ) )
    parent.parentApp.setStatus( _("Waiting for user input after error…") )
    tkmb.showerror( title, errorText, parent=parent )
    parent.parentApp.setReadyStatus()
# end of showerror


def showwarning( parent, title, warningText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag:
        print( exp("showwarning( {}, {!r}, {!r} )").format( parent, title, warningText ) )

    logging.warning( '{}: {}'.format( title, warningText ) )
    parent.parentApp.setStatus( _("Waiting for user input after warning…") )
    tkmb.showwarning( title, warningText, parent=parent )
    parent.parentApp.setReadyStatus()
# end of showwarning


def showinfo( parent, title, infoText ):
    """
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("showinfo( {}, {!r}, {!r} )").format( parent, title, infoText ) )
        infoText += '\n\nWindow parameters:\n'
        for configKey, configTuple  in sorted(parent.configure().items()): # Append the parent window config info
            if debuggingThisModule:
                print( "showinfo: {!r}={} ({})".format( configKey, configTuple, len(configTuple) ) )
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
# end of showinfo



#class HTMLDialog( ModalDialog ):
    #"""
    #"""
    #def __init__( self, parent, text, title=None ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("HTMLDialog.__init__( {}, {!r}, {!r} )").format( parent, text, title ) )

        #self.text = text
        #ModalDialog.__init__( self, parent, title )
    ## end of HTMLDialog.__init__


    #def body( self, master ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("HTMLDialog.body( {} )").format( master ) )

        #html = HTMLText( master )
        #html.grid( row=0 )
        #html.insert( tk.END, self.text )
        #return html
    ## end of HTMLDialog.body
## end of class HTMLDialog



class YesNoDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, message, title=None ):
        """
        """
        self.message = message
        ModalDialog.__init__( self, parent, title, okText=_("Yes"), cancelText=_("No") )
    # end of YesNoDialog.__init__


    def body( self, master ):
        """
        """
        label = Label( master, text=self.message )
        label.grid( row=0 )
        return label
    # end of YesNoDialog.body
# end of class YesNoDialog



class OkCancelDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, message, title=None ):
        """
        """
        self.message = message
        ModalDialog.__init__( self, parent, title, okText=_("Ok"), cancelText=_("Cancel") )
    # end of OkCancelDialog.__init__


    def body( self, master ):
        """
        """
        label = Label( master, text=self.message )
        label.grid( row=0 )
        return label
    # end of OkCancelDialog.body
# end of class OkCancelDialog



class BookNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, bookNameList, currentIndex ): #, message, title=None ):
        """
        """
        #print( 'currentIndex', currentIndex )
        self.bookNameList, self.currentIndex = bookNameList, currentIndex
        ModalDialog.__init__( self, parent ) #, title, okText=_("Ok"), cancelText=_("Cancel") )
    # end of BookNameDialog.__init__


    def buttonBox( self ):
        """
        Do our custom buttonBox (without an ok button)
        """
        box = Frame( self )
        w = Button( box, text=self.cancelText, width=10, command=self.cancel )
        w.pack( side=tk.LEFT, padx=5, pady=5 )
        self.bind( '<Escape>', self.cancel )
        box.pack()
    # end of BookNameDialog.buttonBox


    def body( self, master ):
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
    # end of BookNameDialog.body


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
    def __init__( self, parent, startNumber, endNumber, currentNumber ): #, message, title=None ):
        """
        """
        #print( 'NumberButtonDialog', repr(startNumber), repr(endNumber), repr(currentNumber) )
        self.startNumber, self.endNumber, self.currentNumber = startNumber, endNumber, currentNumber
        ModalDialog.__init__( self, parent ) #, title, okText=_("Ok"), cancelText=_("Cancel") )
    # end of NumberButtonDialog.__init__


    def buttonBox( self ):
        """
        Do our custom buttonBox (without an ok button)
        """
        box = Frame( self )
        w = Button( box, text=self.cancelText, width=10, command=self.cancel )
        w.pack( side=tk.LEFT, padx=5, pady=5 )
        self.bind( '<Escape>', self.cancel )
        box.pack()
    # end of NumberButtonDialog.buttonBox


    def body( self, master ):
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
    # end of NumberButtonDialog.body


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



class SaveWindowNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, existingSettings, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "SaveWindowNameDialog…" )
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parent, title )
    # end of SaveWindowNameDialog.__init__


    def body( self, master ):
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
        self.cb = Combobox( master, values=cbValues )
        #self.cb.current( 0 )
        self.cb.grid( row=1 )

        return self.cb # initial focus
    # end of SaveWindowNameDialog.body


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
    # end of SaveWindowNameDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = self.cb.get()
        #print( exp("New window set-up name is: {!r}").format( self.result ) )
    # end of SaveWindowNameDialog.apply
# end of class SaveWindowNameDialog



class DeleteWindowNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, existingSettings, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "DeleteWindowNameDialog…" )
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parent, title, _("Delete") )
    # end of DeleteWindowNameDialog.__init__


    def body( self, master ):
        """
        """
        Label( master, text=_("Use to delete a saved windows set-up") ).grid( row=0 )

        #cbValues = [_("Enter (optional) new name") if self.haveExisting else _("Enter new set-up name")]
        cbValues = []
        if self.haveExisting:
            for existingName in self.existingSettings:
                if existingName != 'Current':
                    cbValues.append( existingName)
        self.cb = Combobox( master, state='readonly', values=cbValues )
        #self.cb.current( 0 )
        self.cb.grid( row=1 )

        return self.cb # initial focus
    # end of DeleteWindowNameDialog.body


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
    # end of DeleteWindowNameDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        self.result = self.cb.get()
        print( exp("Requested window set-up name is: {!r}").format( self.result ) )
    # end of DeleteWindowNameDialog.apply
# end of class DeleteWindowNameDialog



class SelectResourceBoxDialog( ModalDialog ):
    """
    Given a list of available resources, select one and return the list item.
    """
    def __init__( self, parent, availableSettingsList, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "SelectResourceBoxDialog…" )
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule:
                print( "aS", len(availableSettingsList), repr(availableSettingsList) ) # Should be a list of tuples
            assert isinstance( availableSettingsList, list )
        self.availableSettingsList = availableSettingsList
        ModalDialog.__init__( self, parent, title )
    # end of SelectResourceBoxDialog.__init__


    def body( self, master ):
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
    # end of SelectResourceBoxDialog.body


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
        print( "items", repr(items) ) # a tuple
        self.result = [self.availableSettingsList[int(item)] for item in items] # now a sublist
        print( exp("Requested resource(s) is/are: {!r}").format( self.result ) )
    # end of SelectResourceBoxDialog.apply
# end of class SelectResourceBoxDialog



class GetNewProjectNameDialog( ModalDialog ):
    """
    Get the name and an abbreviation for a new Biblelator project.
    """
    def __init__( self, parent, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "GetNewProjectNameDialog…" )
        ModalDialog.__init__( self, parent, title )
    # end of GetNewProjectNameDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
            to set up the dialog how we want it.
        """
        Label( master, text=_("Full name:") ).grid( row=0 )
        Label( master, text=_("Abbreviation:") ).grid( row=1 )

        self.e1 = Entry( master )
        self.e2 = Entry( master )

        self.e1.grid( row=0, column=1 )
        self.e2.grid( row=1, column=1 )
        return self.e1 # initial focus
    # end of GetNewProjectNameDialog.body


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
        if lenF < 3: showwarning( self.parent, APP_NAME, _("Full name is too short!") ); return False
        if lenF > 30: showwarning( self.parent, APP_NAME, _("Full name is too long!") ); return False
        if lenA < 3: showwarning( self.parent, APP_NAME, _("Abbreviation is too short!") ); return False
        if lenA > 8: showwarning( self.parent, APP_NAME, _("Abbreviation is too long!") ); return False
        if ' ' in abbreviation: showwarning( self.parent, APP_NAME, _("Abbreviation cannot contain spaces!") ); return False
        if '.' in abbreviation: showwarning( self.parent, APP_NAME, _("Abbreviation cannot contain a dot!") ); return False
        for illegalChar in ':;"@#=/\\{}':
            if illegalChar in fullname or illegalChar in abbreviation:
                showwarning( self.parent, APP_NAME, _("Not allowed {} characters").format( _('space') if illegalChar==' ' else illegalChar ) ); return False
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
    def __init__( self, parent, title, currentBBB, availableVersifications ): #, availableVersions ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "CreateNewProjectFilesDialog…" )
        #self.currentBBB, self.availableVersifications, self.availableVersions = currentBBB, availableVersifications, availableVersions
        self.currentBBB, self.availableVersifications = currentBBB, availableVersifications
        ModalDialog.__init__( self, parent, title )
    # end of CreateNewProjectFilesDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
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
        self.cb1 = Combobox( master, values=self.availableVersifications,
                                state = 'readonly' if self.availableVersifications else tk.DISABLED )
        #self.cb.current( 0 )
        self.cb1.grid( row=7, column=1 )

        ##cb2Values = ["test2a","test2b","test2c"]
        #self.cb2 = Combobox( master, values=self.availableVersions,
                                #state = 'readonly' if self.availableVersions else tk.DISABLED )
        ##self.cb.current( 0 )
        #self.cb2.grid( row=8, column=1 )

        return self.rb1a # initial focus
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
            showwarning( self.parent, APP_NAME, _("Need a versification scheme name!") ); return False
        #if result2Number==2 and not cb2result:
            #showwarning( self.parent, APP_NAME, _("Need a version name!") ); return False
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
    def __init__( self, parent, existingNames, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "GetNewCollectionNameDialog…" )
        self.existingNames = existingNames
        print( "GetNewCollectionNameDialog: eNs", self.existingNames )
        ModalDialog.__init__( self, parent, title )
    # end of GetNewCollectionNameDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
            to set up the dialog how we want it.
        """
        Label( master, text=_("Name:") ).grid( row=0 )
        self.e1 = Entry( master )
        self.e1.grid( row=0, column=1 )
        return self.e1 # initial focus
    # end of GetNewCollectionNameDialog.body


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        name = self.e1.get()
        lenN = len( name )
        if lenN < 3: showwarning( self.parent, APP_NAME, _("Name is too short!") ); return False
        if lenN > 30: showwarning( self.parent, APP_NAME, _("Name is too long!") ); return False
        for illegalChar in ' .:;"@#=/\\{}':
            if illegalChar in name:
                showwarning( self.parent, APP_NAME, _("Not allowed {} characters").format( _('space') if illegalChar==' ' else illegalChar ) ); return False
        if name.upper() in self.existingNames:
            showwarning( self.parent, APP_NAME, _("Name already in use").format( illegalChar ) ); return False
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
    def __init__( self, parent, existingName, existingNames, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "RenameResourceCollectionDialog…" )
        self.existingName, self.existingNames = existingName, existingNames
        print( "RenameResourceCollectionDialog: eNs", self.existingNames )
        ModalDialog.__init__( self, parent, title )
    # end of RenameResourceCollectionDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
            to set up the dialog how we want it.
        """
        Label( master, text=_('Enter name to replace "{}"').format( self.existingName ) ).grid( row=0, column=0, columnspan=2 )
        Label( master, text=_("New name:") ).grid( row=1, column=0 )

        self.e1 = Entry( master )
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
        if lenName < 3: showwarning( self.parent, APP_NAME, _("New name is too short!") ); return False
        if lenName > 30: showwarning( self.parent, APP_NAME, _("New name is too long!") ); return False
        for illegalChar in ' .:;"@#=/\\{}':
            if illegalChar in newName:
                showwarning( self.parent, APP_NAME, _("Not allowed {} characters").format( _('space') if illegalChar==' ' else illegalChar ) ); return False
        if newName.upper() in self.existingNames:
            showwarning( self.parent, APP_NAME, _("Name already in use").format( illegalChar ) ); return False
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
    Get the new name for a resource collection.
    """
    def __init__( self, parent, parentApp, givenBible, currentBBB, currentList, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentApp.setDebugText( "GetBibleBookRangeDialog…" )
        #assert currentBBB in givenBible -- no, it might not be loaded yet!
        self.parentApp, self.givenBible, self.currentBBB, self.currentList = parentApp, givenBible, currentBBB, currentList
        ModalDialog.__init__( self, parent, title )
    # end of GetBibleBookRangeDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
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
                text=str(self.currentList) if len(self.currentList)<10 else _('Selected books')+' ({})'.format( len(self.currentList) ),
                variable=self.booksSelectVariable, value=6 ) \
            if self.currentList and self.currentList!='ALL' else \
            Radiobutton( master, text=_('N/A'), variable=self.booksSelectVariable, value=6, state=tk.DISABLED )
        self.rb6.grid( row=5, column=0, sticky=tk.W )
        b1 = Button( master, text=_('Select')+'…', command=self.doIndividual )
        b1.grid( row=6, column=0, sticky=tk.W )

        return rb1 # initial focus
    # end of GetBibleBookRangeDialog.body


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
        """
        self.availableList = self.givenBible.getBookList()
        sIBBD = SelectIndividualBibleBooksDialog( self, self.parentApp, self.availableList, self.currentList, title=_('Books to be searched') )
        if BibleOrgSysGlobals.debugFlag: print( "individualBooks sIBBDResult", repr(sIBBD.result) )
        if sIBBD.result: # Returns a list of books
            if BibleOrgSysGlobals.debugFlag: assert isinstance( sIBBD.result, list )
            resultCount = len( sIBBD.result )
            if resultCount==1 and sIBBD.result[0]==currentBBB:
                # It's just the current book to search
                self.booksSelectVariable.set( 1 )
            elif resultCount == len( self.availableList ):
                self.booksSelectVariable.set( 2 )
            else:
                self.booksSelectVariable.set( 6 )
                self.currentList = sIBBD.result
                self.rb6['state'] = tk.NORMAL
                self.rb6['text'] = str(self.currentList) if len(self.currentList)<10 else _('Selected books')+' ({})'.format( len(self.currentList) )
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
        elif resultNumber == 3: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.BibleBooksCodes.isOldTestament_NR(book.BBB)] # OT
        elif resultNumber == 4: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.BibleBooksCodes.isNewTestament_NR(book.BBB)] # NT
        elif resultNumber == 5: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.BibleBooksCodes.isDeuterocanon_NR(book.BBB)] # DC
        elif resultNumber == 6: self.result = self.currentList
        else:
            halt # Unexpected result value
    # end of GetBibleBookRangeDialog.apply
# end of class GetBibleBookRangeDialog



class SelectIndividualBibleBooksDialog( ModalDialog ):
    """
    Get the new name for a resource collection.
    """
    def __init__( self, parent, parentApp, availableList, currentList, title ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parentApp.setDebugText( "SelectIndividualBibleBooksDialog…" )
        self.parentApp, self.availableList, self.currentList = parentApp, availableList, currentList
        ModalDialog.__init__( self, parent, title )
    # end of SelectIndividualBibleBooksDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
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
    # end of SelectIndividualBibleBooksDialog.body


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
                if BibleOrgSysGlobals.BibleBooksCodes.isOldTestament_NR( BBB ):
                    variable.set( 1 )
        elif resultNumber == 2: # 'NT'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.BibleBooksCodes.isNewTestament_NR( BBB ):
                    variable.set( 1 )
        elif resultNumber == 3: # 'DC'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.BibleBooksCodes.isDeuterocanon_NR( BBB ):
                    variable.set( 1 )
        elif resultNumber == 4: # 'Other'
            for variable, BBB in zip( self.variables, self.availableList):
                if not BibleOrgSysGlobals.BibleBooksCodes.isOldTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.BibleBooksCodes.isNewTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.BibleBooksCodes.isDeuterocanon_NR( BBB ):
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
                if BibleOrgSysGlobals.BibleBooksCodes.isOldTestament_NR( BBB ):
                    variable.set( 0 )
        elif resultNumber == 2: # 'NT'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.BibleBooksCodes.isNewTestament_NR( BBB ):
                    variable.set( 0 )
        elif resultNumber == 3: # 'DC'
            for variable, BBB in zip( self.variables, self.availableList):
                if BibleOrgSysGlobals.BibleBooksCodes.isDeuterocanon_NR( BBB ):
                    variable.set( 0 )
        elif resultNumber == 4: # 'Other'
            for variable, BBB in zip( self.variables, self.availableList):
                if not BibleOrgSysGlobals.BibleBooksCodes.isOldTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.BibleBooksCodes.isNewTestament_NR( BBB ) \
                and not BibleOrgSysGlobals.BibleBooksCodes.isDeuterocanon_NR( BBB ):
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



class GetBibleSearchTextDialog( ModalDialog ):
    """
    Get the search string (and options) for Bible search.
    """
    def __init__( self, parent, parentApp, givenBible, optionsDict, title ):
        """
        optionsDict must already contain 'currentBCV'
        """
        if BibleOrgSysGlobals.debugFlag:
            parentApp.setDebugText( "GetBibleSearchTextDialog…" )
            #assert currentBBB in givenBible -- no, it might not be loaded yet!
            assert isinstance( optionsDict, dict )
            assert 'currentBCV' in optionsDict
        self.parentApp, self.givenBible, self.optionsDict = parentApp, givenBible, optionsDict

        # Set-up default search options
        if 'work' not in self.optionsDict: self.optionsDict['work'] = givenBible.abbreviation if givenBible.abbreviation else givenBible.name
        if 'searchHistoryList' not in self.optionsDict: self.optionsDict['searchHistoryList'] = [] # Oldest first
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

        ModalDialog.__init__( self, parent, title )
    # end of GetBibleSearchTextDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
            to set up the dialog how we want it.
        """
        #print( "GetBibleSearchTextDialog.body", self.optionsDict )
        Label( master, text=_("Project:") ).grid( row=0, column=0, padx=2, pady=2, sticky=tk.E )
        self.projectNameVar = tk.StringVar()
        self.projectNameVar.set( self.optionsDict['work'] )
        self.projectNameBox = Combobox( master, width=30, textvariable=self.projectNameVar )
        #self.projectNameBox['values'] = self.bookNames
        #self.projectNameBox['width'] = len( 'Deuteronomy' )
        #self.projectNameBox.bind('<<ComboboxSelected>>', self.ok )
        #self.projectNameBox.bind( '<Return>', self.ok )
        #self.projectNameBox.pack( side=tk.LEFT )
        self.projectNameBox.grid( row=0, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )

        Label( master, text=_("Find:") ).grid( row=1, column=0, padx=2, pady=5, sticky=tk.E )
        self.searchStringVar = tk.StringVar()
        try: self.searchStringVar.set( self.optionsDict['searchHistoryList'][-1] )
        except IndexError: pass
        self.searchStringBox = Combobox( master, width=30, textvariable=self.searchStringVar )
        self.searchStringBox['values'] = self.optionsDict['searchHistoryList']
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
        #self.rbb3.grid( row=4, column=2, padx=2, pady=1, sticky=tk.W )
        if isinstance( self.optionsDict['bookList'], list ):
            if len( self.optionsDict['bookList'] ) == 1 and self.optionsDict['bookList'] != 'ALL':
                sbText = self.optionsDict['bookList'][0]
            else: sbText = len( self.optionsDict['bookList'] )
        elif isinstance( self.optionsDict['bookList'], str ) and self.optionsDict['bookList'] != 'ALL':
            sbText = 1
        else: sbText = 0
        self.rbb2 = Radiobutton( master, text=_('Current book')+' ({})'.format( self.optionsDict['currentBCV'][0] ), variable=self.booksSelectVariable, value=2 )
        self.rbb2.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rbb2.grid( row=2, column=2, padx=2, pady=1, sticky=tk.W )
        self.rbb3 = Radiobutton( master, text=_('Current chapter')+' ({} {})'.format( self.optionsDict['currentBCV'][0], self.optionsDict['currentBCV'][1] ), variable=self.booksSelectVariable, value=3 )
        self.rbb3.pack( in_=bookLimitsFrame, side=tk.TOP, fill=tk.X )
        #self.rbb3.grid( row=3, column=2, padx=2, pady=1, sticky=tk.W )
        self.rbb4 = Radiobutton( master, text=_('Selected books'+' ({})').format( sbText ), variable=self.booksSelectVariable, value=4 )
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
        theseMarkersEntry = Entry( master, textvariable=self.theseMarkersListVar, validate='all', validatecommand=(registeredFunction,'%P') )
        theseMarkersEntry.pack( in_=markerListFrame, side=tk.RIGHT, padx=2, pady=1 )

        return self.searchStringBox # initial focus
    # end of GetBibleSearchTextDialog.body


    def selectBooks( self ):
        """
        """
        self.parent._prepareInternalBible() # Slow but must be called before the dialog
        currentBBB = self.optionsDict['currentBCV'][0]
        gBBRD = GetBibleBookRangeDialog( self, self.parentApp, self.givenBible, currentBBB, self.optionsDict['bookList'], title=_('Books to be searched') )
        if BibleOrgSysGlobals.debugFlag: print( "selectBooks gBBRDResult", repr(gBBRD.result) )
        if gBBRD.result: # Returns a list of books
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBBRD.result, list )
            if len(gBBRD.result)==1 and gBBRD.result[0]==currentBBB:
                # It's just the current book to search
                self.booksSelectVariable.set( 2 )
            else:
                self.booksSelectVariable.set( 4 )
                self.optionsDict['bookList'] = gBBRD.result
                self.rbb4['text'] = _("Selected books ({})").format( len(self.optionsDict['bookList']) )
            #self.update()
        else: print( "selectBooks: No books selected!" )
    # end of GetBibleSearchTextDialog.apply


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
    # end of GetBibleSearchTextDialog.doMarkerListentry


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.

        Returns True or False.
        """
        #print( "GetBibleSearchTextDialog.validate()" )

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
                if marker in BibleOrgSysGlobals.USFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                    markerList.append( marker )
                else: # not a valid newline marker
                    showwarning( self.parent, APP_NAME, _("{!r} is not a valid newline marker!").format( marker ) ); return False
        else: # Nothing in the entry
            self.theseMarkersOnlyVar.set( 0 )

        # Now check for bad combinations
        searchText = self.searchStringVar.get()
        if not searchText: showwarning( self.parent, APP_NAME, _("Nothing to search for!") ); return False
        if searchText.lower() == 'regex:': showwarning( self.parent, APP_NAME, _("No regular expression to search for!") ); return False
        bookResultNumber = self.booksSelectVariable.get()
        if bookResultNumber==4 and ( not self.optionsDict['bookList'] or not isinstance(self.optionsDict['bookList'], list) ):
            showwarning( self.parent, APP_NAME, _("No books selected to search in!") ); return False
        if self.theseMarkersOnlyVar.get():
            if self.introVar.get() or  self.mainTextVar.get() or self.markersTextVar.get() or self.extrasVar.get():
                showwarning( self.parent, APP_NAME, _("Bad combination of fields selected!") ); return False
        return True # Must be ok
    # end of GetBibleSearchTextDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        #print( "GetBibleSearchTextDialog.apply()" )
        self.optionsDict['searchText'] = self.searchStringVar.get()

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
                    if marker in BibleOrgSysGlobals.USFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                        markerList.append( marker )
                    else: halt # not a valid newline marker
                if markerList: self.optionsDict['markerList'] = markerList

        self.result = self.optionsDict
    # end of GetBibleSearchTextDialog.apply
# end of class GetBibleSearchTextDialog



class GetBibleReplaceTextDialog( ModalDialog ):
    """
    Get the Search and Replace strings (and options) for Bible Replace.
    """
    def __init__( self, parent, parentApp, givenBible, optionsDict, title ):
        """
        optionsDict must already contain 'currentBCV'
        """
        if BibleOrgSysGlobals.debugFlag:
            parentApp.setDebugText( "GetBibleReplaceTextDialog…" )
            #assert currentBBB in givenBible -- no, it might not be loaded yet!
            assert isinstance( optionsDict, dict )
            assert 'currentBCV' in optionsDict
        self.parentApp, self.givenBible, self.optionsDict = parentApp, givenBible, optionsDict

        # Set-up default Replace options
        if 'work' not in self.optionsDict: self.optionsDict['work'] = givenBible.abbreviation if givenBible.abbreviation else givenBible.name
        if 'searchHistoryList' not in self.optionsDict: self.optionsDict['searchHistoryList'] = [] # Oldest first
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

        ModalDialog.__init__( self, parent, title )
    # end of GetBibleReplaceTextDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
            to set up the dialog how we want it.
        """
        #print( "GetBibleReplaceTextDialog.body", self.optionsDict )
        Label( master, text=_("Project:") ).grid( row=0, column=0, padx=2, pady=2, sticky=tk.E )
        self.projectNameVar = tk.StringVar()
        self.projectNameVar.set( self.optionsDict['work'] )
        self.projectNameBox = Combobox( master, width=30, textvariable=self.projectNameVar )
        #self.projectNameBox['values'] = self.bookNames
        #self.projectNameBox['width'] = len( 'Deuteronomy' )
        #self.projectNameBox.bind('<<ComboboxSelected>>', self.ok )
        #self.projectNameBox.bind( '<Return>', self.ok )
        #self.projectNameBox.pack( side=tk.LEFT )
        self.projectNameBox.grid( row=0, column=1, columnspan=2, padx=2, pady=2, sticky=tk.W )

        Label( master, text=_("Find (match case):") ).grid( row=1, column=0, padx=2, pady=5, sticky=tk.E )
        self.searchStringVar = tk.StringVar()
        try: self.searchStringVar.set( self.optionsDict['searchHistoryList'][-1] )
        except IndexError: pass
        self.searchStringBox = Combobox( master, width=30, textvariable=self.searchStringVar )
        self.searchStringBox['values'] = self.optionsDict['searchHistoryList']
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
        self.replaceStringBox = Combobox( master, width=30, textvariable=self.replaceStringVar )
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
        self.rbb4 = Radiobutton( master, text=_("Selected books ({})").format( sbText ), variable=self.booksSelectVariable, value=4 )
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
        #theseMarkersEntry = Entry( master, textvariable=self.theseMarkersListVar, validate='all', validatecommand=(registeredFunction,'%P') )
        #theseMarkersEntry.pack( in_=markerListFrame, side=tk.RIGHT, padx=2, pady=1 )

        return self.searchStringBox # initial focus
    # end of GetBibleReplaceTextDialog.body


    def selectBooks( self ):
        """
        """
        self.parent._prepareInternalBible() # Slow but must be called before the dialog
        currentBBB = self.optionsDict['currentBCV'][0]
        gBBRD = GetBibleBookRangeDialog( self, self.parentApp, self.givenBible, currentBBB, self.optionsDict['bookList'], title=_('Books to be Replaceed') )
        if BibleOrgSysGlobals.debugFlag: print( "selectBooks gBBRDResult", repr(gBBRD.result) )
        if gBBRD.result: # Returns a list of books
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBBRD.result, list )
            if len(gBBRD.result)==1 and gBBRD.result[0]==currentBBB:
                # It's just the current book to Replace
                self.booksSelectVariable.set( 2 )
            else:
                self.booksSelectVariable.set( 4 )
                self.optionsDict['bookList'] = gBBRD.result
                self.rbb4['text'] = _("Selected books ({})").format( len(self.optionsDict['bookList']) )
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
                #if marker in BibleOrgSysGlobals.USFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                    #markerList.append( marker )
                #else: # not a valid newline marker
                    #showwarning( self.parent, APP_NAME, _("{!r} is not a valid newline marker!").format( marker ) ); return False
        #else: # Nothing in the entry
            #self.theseMarkersOnlyVar.set( 0 )

        # Now check for bad combinations
        searchText = self.searchStringVar.get()
        if not searchText: showwarning( self.parent, APP_NAME, _("Nothing to search for!") ); return False
        if searchText.lower() == 'regex:': showwarning( self.parent, APP_NAME, _("No regular expression to search for!") ); return False
        replaceText = self.replaceStringVar.get()
        if replaceText.lower().startswith( 'regex:' ): showwarning( self.parent, APP_NAME, _("Don't start replace field with 'regex:'!") ); return False
        bookResultNumber = self.booksSelectVariable.get()
        if bookResultNumber==4 and ( not self.optionsDict['bookList'] or not isinstance(self.optionsDict['bookList'], list) ):
            showwarning( self.parent, APP_NAME, _("No books selected to search in!") ); return False
        #if self.theseMarkersOnlyVar.get():
            #if self.introVar.get() or  self.mainTextVar.get() or self.markersTextVar.get() or self.extrasVar.get():
                #showwarning( self.parent, APP_NAME, _("Bad combination of fields selected!") ); return False
        return True # Must be ok
    # end of GetBibleReplaceTextDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        #print( "GetBibleReplaceTextDialog.apply()" )
        self.optionsDict['searchText'] = self.searchStringVar.get()
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
                    #if marker in BibleOrgSysGlobals.USFMMarkers.getNewlineMarkersList( 'Combined' ): # we accept either q or q1, s or s1, etc.
                        #markerList.append( marker )
                    #else: halt # not a valid newline marker
                #if markerList: self.optionsDict['markerList'] = markerList

        self.result = self.optionsDict
    # end of GetBibleReplaceTextDialog.apply
# end of class GetBibleReplaceTextDialog



class ReplaceConfirmDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, parentApp, referenceString, contextBefore, searchText, contextAfter, finalText, haveUndos, title ):
        """
        optionsDict must already contain 'currentBCV'
        """
        if BibleOrgSysGlobals.debugFlag:
            parentApp.setDebugText( "ReplaceConfirmDialog…" )
            assert isinstance( contextBefore, str )
            assert isinstance( contextAfter, str )
        self.parentApp, self.referenceString, self.contextBefore, self.searchText, self.contextAfter, self.finalText, self.haveUndos = parentApp, referenceString, contextBefore, searchText, contextAfter, finalText, haveUndos
        ModalDialog.__init__( self, parent, title )
    # end of ReplaceConfirmDialog.__init__


    def body( self, master ):
        """
        """
        label1 = Label( master, text=self.referenceString )
        label1.pack( side=tk.TOP )
        label2 = Label( master, text=_('Before') )
        label2.pack( side=tk.TOP, anchor=tk.W )
        textBox1 = tk.Text( master, height=5 )
        textBox1.insert( tk.END, self.contextBefore+self.searchText+self.contextAfter )
        textBox1.configure( state=tk.DISABLED )
        textBox1.pack( side=tk.TOP, fill=tk.X )
        label3 = Label( master, text=_('After') )
        label3.pack( side=tk.TOP, anchor=tk.W )
        textBox2 = tk.Text( master, height=5 )
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
    # end of ReplaceConfirmDialog.body

    def buttonBox( self ):
        '''
        Add ourstandard button box

        Override if you don't want the standard buttons.
        '''
        box = Frame( self )

        yesButton = Button( box, text=_('Yes (Replace)'), command=self.doYes, default=tk.ACTIVE )
        yesButton.pack( side=tk.LEFT, padx=5, pady=5 )
        noButton = Button( box, text=_('No'), width=10, command=self.doNo )
        noButton.pack( side=tk.LEFT, padx=5, pady=5 )
        allButton = Button( box, text=_('All (Yes)'), width=10, command=self.doAll )
        allButton.pack( side=tk.LEFT, padx=5, pady=5 )
        cancelButton = Button( box, text=_('Stop (No more)'), command=self.doStop )
        cancelButton.pack( side=tk.LEFT, padx=5, pady=5 )
        undoButton = Button( box, text=_('Undo all'), width=10, command=self.doUndo )
        undoButton.pack( side=tk.LEFT, padx=5, pady=5 )
        if not self.haveUndos: undoButton.configure( state=tk.DISABLED )

        self.bind( '<Return>', self.doYes )
        self.bind( '<Escape>', self.doStop )

        box.pack( anchor=tk.E )
    # end of ModalDialog.buttonBox

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
    def __init__( self, parent, title, internalBibles ):
        """
        """
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "SelectInternalBibleDialog…" )
        self.internalBibles = internalBibles
        ModalDialog.__init__( self, parent, title )
    # end of SelectInternalBibleDialog.__init__


    def buttonBox( self ):
        """
        Do our custom buttonBox (without an ok button)
        """
        box = Frame( self )
        w = Button( box, text=self.cancelText, width=10, command=self.cancel )
        w.pack( side=tk.LEFT, padx=5, pady=5 )
        self.bind( '<Escape>', self.cancel )
        box.pack()
    # end of SelectInternalBibleDialog.buttonBox


    def body( self, master ):
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
    # end of SelectInternalBibleDialog.body


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
# end of BiblelatorDialogs.demo


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
# end of BiblelatorDialogs.py
