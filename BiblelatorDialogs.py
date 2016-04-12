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

    def errorBeep()
    def showerror( parent, title, errorText )
    def showwarning( parent, title, warningText )
    def showinfo( parent, title, infoText )
    class HTMLDialog( ModalDialog )
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
"""

from gettext import gettext as _

LastModifiedDate = '2016-04-12'
ShortProgName = "Biblelator"
ProgName = "Biblelator dialogs"
ProgVersion = '0.33'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import logging

import tkinter as tk
import tkinter.messagebox as tkmb
from tkinter.ttk import Label, Combobox, Entry, Radiobutton

# Biblelator imports
from BiblelatorGlobals import APP_NAME
from ModalDialog import ModalDialog
from TextBoxes import HTMLText

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



def errorBeep():
    """
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("errorBeep()") )

    # Does nothing yet :-(

    #import sys
    #from subprocess import call
    #if sys.platform == 'linux': call(["xdg-open","dialog-error.ogg"])
    #elif sys.platform == 'darwin': call(["afplay","dialog-error.ogg"])
    #else: print( "errorBeep: sp", sys.platform )
# end of errorBeep


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
    if BibleOrgSysGlobals.debugFlag:
        print( exp("showinfo( {}, {!r}, {!r} )").format( parent, title, infoText ) )
        infoText += '\n\nWindow parameters:\n'
        for configKey, configTuple  in sorted(parent.config().items()): # Append the parent window config info
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



class HTMLDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, text, title=None ):
        self.text = text
        ModalDialog.__init__( self, parent, title )
    # end of HTMLDialog.__init__


    def body( self, master ):
        html = HTMLText( master )
        html.grid( row=0 )
        html.insert( tk.END, self.text )
        return html
    # end of HTMLDialog.body
# end of class HTMLDialog



class YesNoDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, message, title=None ):
        self.message = message
        ModalDialog.__init__( self, parent, title, okText=_('Yes'), cancelText=_('No') )
    # end of YesNoDialog.__init__


    def body( self, master ):
        label = Label( master, text=self.message )
        label.grid( row=0 )
        return label
    # end of YesNoDialog.body
# end of class YesNoDialog



class OkCancelDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, message, title=None ):
        self.message = message
        ModalDialog.__init__( self, parent, title, okText=_('Ok'), cancelText=_('Cancel') )
    # end of OkCancelDialog.__init__


    def body( self, master ):
        label = Label( master, text=self.message )
        label.grid( row=0 )
        return label
    # end of OkCancelDialog.body
# end of class OkCancelDialog



class SaveWindowNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, existingSettings, title ):
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "SaveWindowNameDialog…" )
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parent, title )
    # end of SaveWindowNameDialog.__init__


    def body( self, master ):
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
    # end of SaveWindowNameDialog.apply


    def validate( self ):
        result = self.cb.get()
        if not result: return False
        if not isinstance( result, str ): return False
        for char in '[]':
            if char in result: return False
        return True
    # end of SaveWindowNameDialog.validate


    def apply( self ):
        self.result = self.cb.get()
        #print( exp("New window set-up name is: {!r}").format( self.result ) )
    # end of SaveWindowNameDialog.apply
# end of class SaveWindowNameDialog



class DeleteWindowNameDialog( ModalDialog ):
    """
    """
    def __init__( self, parent, existingSettings, title ):
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "DeleteWindowNameDialog…" )
        self.existingSettings = existingSettings
        self.haveExisting = len(self.existingSettings)>1 or (len(self.existingSettings) and 'Current' not in self.existingSettings)
        ModalDialog.__init__( self, parent, title, _("Delete") )
    # end of DeleteWindowNameDialog.__init__


    def body( self, master ):
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
    # end of DeleteWindowNameDialog.apply


    def validate( self ):
        result = self.cb.get()
        if not result: return False
        if not isinstance( result, str ): return False
        return True
    # end of DeleteWindowNameDialog.validate


    def apply( self ):
        self.result = self.cb.get()
        print( exp("Requested window set-up name is: {!r}").format( self.result ) )
    # end of DeleteWindowNameDialog.apply
# end of class DeleteWindowNameDialog



class SelectResourceBoxDialog( ModalDialog ):
    """
    Given a list of available resources, select one and return the list item.
    """
    def __init__( self, parent, availableSettingsList, title ):
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
    # end of SelectResourceBoxDialog.apply


    def validate( self ):
        """
        Must be at least one selected (otherwise force them to select CANCEL).
        """
        return self.lb.curselection()
    # end of SelectResourceBoxDialog.validate


    def apply( self ):
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
    # end of GetNewProjectNameDialog.apply


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.
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

        self.rb1a = Radiobutton( master, text=_("Current book ({})").format( self.currentBBB ), variable=self.selectVariable1, value=1 )
        self.rb1a.grid( row=0, column=1, sticky=tk.W )
        self.rb1b = Radiobutton( master, text=_("All books"), variable=self.selectVariable1, value=2 )
        self.rb1b.grid( row=1, column=1, sticky=tk.W )
        self.rb1c = Radiobutton( master, text=_("OT books"), variable=self.selectVariable1, value=3 )
        self.rb1c.grid( row=2, column=1, sticky=tk.W )
        self.rb1d = Radiobutton( master, text=_("NT books"), variable=self.selectVariable1, value=4 )
        self.rb1d.grid( row=3, column=1, sticky=tk.W )
        self.rb1e = Radiobutton( master, text=_("No books (not advised)"), variable=self.selectVariable1, value=5 )
        self.rb1e.grid( row=4, column=1, sticky=tk.W )

        Label( master, text=_("Files will contain:") ).grid( row=6, sticky=tk.W )
        self.selectVariable2 = tk.IntVar()

        self.rb2a = Radiobutton( master, text=_("CV markers from versification"), variable=self.selectVariable2, value=1,
                                state = tk.NORMAL if self.availableVersifications else tk.DISABLED )
        self.rb2a.grid( row=7, column=0, sticky=tk.W )
        self.rb2b = Radiobutton( master, text=_("All markers from a USFM version"), variable=self.selectVariable2, value=2 )
                                #state = tk.NORMAL if self.availableVersions else tk.DISABLED )
        self.rb2b.grid( row=8, column=0, sticky=tk.W )
        self.rb2c = Radiobutton( master, text=_("Only basic header lines (not advised)"), variable=self.selectVariable2, value=3 )
        self.rb2c.grid( row=9, column=0, sticky=tk.W )
        self.rb2d = Radiobutton( master, text=_("Nothing at all (not advised)"), variable=self.selectVariable2, value=4 )
        self.rb2d.grid( row=10, column=0, sticky=tk.W )

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
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "GetNewCollectionNameDialog…" )
        self.existingNames = existingNames
        print( "eNs", self.existingNames )
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
    # end of GetNewCollectionNameDialog.apply


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.
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
        """
        self.result = self.e1.get()
    # end of GetNewCollectionName.apply
# end of class GetNewCollectionNameDialog



class RenameResourceCollectionDialog( ModalDialog ):
    """
    Get the new name for a resource collection.
    """
    def __init__( self, parent, existingName, existingNames, title ):
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "RenameResourceCollectionDialog…" )
        self.existingName, self.existingNames = existingName, existingNames
        print( "eNs", self.existingNames )
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
        """
        self.result = self.e1.get()
    # end of RenameResourceCollectionDialog.apply
# end of class RenameResourceCollectionDialog



class GetBibleBookRangeDialog( ModalDialog ):
    """
    Get the new name for a resource collection.
    """
    def __init__( self, parent, givenBible, currentBBB, title ):
        if BibleOrgSysGlobals.debugFlag: parent.parentApp.setDebugText( "GetBibleBookRangeDialog…" )
        #assert currentBBB in givenBible -- no, it might not be loaded yet!
        self.givenBible, self.currentBBB = givenBible, currentBBB
        ModalDialog.__init__( self, parent, title )
    # end of GetBibleBookRangeDialog.__init__


    def body( self, master ):
        """
        Override the empty ModalDialog.body function
            to set up the dialog how we want it.
        """
        self.selectVariable = tk.IntVar()

        self.rb1 = Radiobutton( master, text=_("Current book")+" ({})".format( self.currentBBB ), variable=self.selectVariable, value=1 )
        self.rb1.grid( row=0, column=0, sticky=tk.W )
        allText = _("All {} books").format( len(self.givenBible) ) if len(self.givenBible)>2 else _("All books")
        self.rb2 = Radiobutton( master, text=allText, variable=self.selectVariable, value=2 )
        self.rb2.grid( row=1, column=0, sticky=tk.W )
        self.rb3 = Radiobutton( master, text=_("OT books"), variable=self.selectVariable, value=3 )
        self.rb3.grid( row=2, column=0, sticky=tk.W )
        self.rb4 = Radiobutton( master, text=_("NT books"), variable=self.selectVariable, value=4 )
        self.rb4.grid( row=3, column=0, sticky=tk.W )
        self.rb5 = Radiobutton( master, text=_("DC books"), variable=self.selectVariable, value=5 )
        self.rb5.grid( row=4, column=0, sticky=tk.W )

        return self.rb1 # initial focus
    # end of GetBibleBookRangeDialog.apply


    def validate( self ):
        """
        Override the empty ModalDialog.validate function
            to check that the results are how we need them.
        """
        resultNumber = self.selectVariable.get()
        return 1 <= resultNumber <= 5
    # end of GetBibleBookRangeDialog.validate


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.
        """
        resultNumber = self.selectVariable.get()
        if resultNumber == 1: self.result = [self.currentBBB]
        elif resultNumber == 2: self.result = [book.BBB for book in self.givenBible] # all
        elif resultNumber == 3: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.BibleBooksCodes.isOldTestament_NR(book.BBB)] # OT
        elif resultNumber == 4: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.BibleBooksCodes.isNewTestament_NR(book.BBB)] # NT
        elif resultNumber == 5: self.result = [book.BBB for book in self.givenBible if BibleOrgSysGlobals.BibleBooksCodes.isDeuterocanon_NR(book.BBB)] # DC
        else:
            halt # Unexpected result value
    # end of GetBibleBookRangeDialog.apply
# end of class GetBibleBookRangeDialog



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
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of BiblelatorDialogs.py