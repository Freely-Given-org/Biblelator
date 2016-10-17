#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# USFMEditWindow.py
#
# The actual edit windows for Biblelator text editing and USFM/ESFM Bible editing
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
xxx to allow editing of USFM Bibles using Python3 and Tkinter.
"""

from gettext import gettext as _

LastModifiedDate = '2016-10-17' # by RJH
ShortProgName = "USFMEditWindow"
ProgName = "Biblelator USFM Edit Window"
ProgVersion = '0.39'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True

import os.path, logging
from collections import OrderedDict

import tkinter as tk
from tkinter.ttk import Style, Notebook, Frame, Label, Radiobutton

# Biblelator imports
from BiblelatorGlobals import APP_NAME, START, DEFAULT, BIBLE_GROUP_CODES, BIBLE_CONTEXT_VIEW_MODES, \
                                errorBeep
from BiblelatorDialogs import showerror, showinfo, OkCancelDialog, \
                                YesNoDialog, GetBibleReplaceTextDialog, ReplaceConfirmDialog
from BiblelatorHelpers import createEmptyUSFMBookText, calculateTotalVersesForBook, \
                                mapReferenceVerseKey, mapParallelVerseKey, findCurrentSection, \
                                handleInternalBibles, getChangeLogFilepath, logChangedFile
from ModalDialog import ModalDialog
from ChildWindows import HTMLWindow
from BibleResourceWindows import InternalBibleResourceWindow
from BibleReferenceCollection import BibleReferenceCollectionWindow
from TextEditWindow import TextEditWindow #, NO_TYPE_TIME
from AutocompleteFunctions import loadBibleAutocompleteWords, loadBibleBookAutocompleteWords, \
                                    loadHunspellAutocompleteWords, loadILEXAutocompleteWords

# BibleOrgSys imports
import BibleOrgSysGlobals
from VerseReferences import SimpleVerseKey
from USFMBible import searchReplaceText



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



class ToolsOptionsDialog( ModalDialog ):
    """
    """
    #def __init__( self, parent ): #, message, title=None ):
        #print( 'ToolsOptionsDialog' )
        #self.startNumber, self.endNumber, self.currentNumber = startNumber, endNumber, currentNumber
        #ModalDialog.__init__( self, parent ) #, title, okText=_("Ok"), cancelText=_("Cancel") )
    ## end of ToolsOptionsDialog.__init__


    #def buttonBox( self ):
        #"""
        #Do our custom buttonBox (without an ok button)
        #"""
        #box = Frame( self )
        #w = Button( box, text=self.cancelText, width=10, command=self.cancel )
        #w.pack( side=tk.LEFT, padx=5, pady=5 )
        #self.bind( '<Escape>', self.cancel )
        #box.pack()
    ## end of ToolsOptionsDialog.buttonBox


    acValues = None, 'Bible', 'BibleBook', 'Dictionary1', 'Dictionary2'

    def body( self, master ):
        """
        Adapted from http://stackoverflow.com/questions/7591294/how-to-create-a-self-resizing-grid-of-buttons-in-tkinter
        """
        self.notebook = Notebook( master )

        # Adding Frames as pages for the ttk.Notebook

        # General page
        print( "Create general page" )
        self.generalPage = Frame( self.notebook )
        mcaseCb = tk.Checkbutton( self.generalPage, text=_("Show status bar"), variable=self.parent._showStatusBarVar )
        mcaseCb.grid( row=0, column=0 )

        # Autocomplete page
        print( "Create autocomplete page" )
        self.autocompletePage = Frame( self.notebook )

        Label( self.autocompletePage, text=_("Autocomplete mode: Use words from") ).grid( row=0 )
        self.selectVariable1 = tk.IntVar()
        acValue = ToolsOptionsDialog.acValues.index( self.parent.autocompleteMode )
        self.selectVariable1.set( acValue + 1 )
        self.rb1a = Radiobutton( self.autocompletePage, text=_("None/Off"), variable=self.selectVariable1, value=1 )
        self.rb1a.grid( row=0, column=1, sticky=tk.W )
        self.rb1a = Radiobutton( self.autocompletePage, text=_("Current Bible ({})").format( self.parent.projectName ), variable=self.selectVariable1, value=2 )
        self.rb1a.grid( row=1, column=1, sticky=tk.W )
        self.rb1a = Radiobutton( self.autocompletePage, text=_("Current Bible book ({})").format( self.parent.currentVerseKey.getBBB() ), variable=self.selectVariable1, value=3 )
        self.rb1a.grid( row=2, column=1, sticky=tk.W )
        self.rb1b = Radiobutton( self.autocompletePage, text=_("Dictionary1"), variable=self.selectVariable1, value=4 )
        self.rb1b.grid( row=3, column=1, sticky=tk.W )
        self.rb1c = Radiobutton( self.autocompletePage, text=_("Dictionary2"), variable=self.selectVariable1, value=5 )
        self.rb1c.grid( row=4, column=1, sticky=tk.W )

        print( "Add all pages" )
        self.notebook.add( self.generalPage, text=_("General") )
        self.notebook.add( self.autocompletePage, text=_("AutoComplete") )
        self.notebook.pack( expand=tk.YES, fill=tk.BOTH )
    # end of ToolsOptionsDialog.body


    def apply( self ):
        """
        Override the empty ModalDialog.apply function
            to process the results how we need them.

        Results are left in self.result
        """
        existingAutocompleteMode = self.parent.autocompleteMode
        self.parent.autocompleteMode = ToolsOptionsDialog.acValues[self.selectVariable1.get()-1]
        if self.parent.autocompleteMode != existingAutocompleteMode:
            print( "Switching to {!r} autocomplete mode (from {!r})".format( self.parent.autocompleteMode, existingAutocompleteMode ) )

        self.result = True
    # end of ToolsOptionsDialog.apply
# end of class ToolsOptionsDialog



class USFMEditWindow( TextEditWindow, InternalBibleResourceWindow ):
    """
    self.genericWindowType will be BibleEditor
    self.windowType will be BiblelatorUSFMBibleEditWindow or ParatextUSFMBibleEditWindow

    Even though it contains a link to an USFMBible (InternalBible) object,
        this class always works directly with the USFM (text) files for editing
            and also for search/replace (but does use the InternalBible object for search).
    """
    def __init__( self, parentApp, USFMBible, editMode=None ):
        """
        """
        logging.debug( "USFMEditWindow.__init__( {}, {} ) {}".format( parentApp, USFMBible, USFMBible.sourceFolder ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "USFMEditWindow.__init__( {}, {} ) {}".format( parentApp, USFMBible, USFMBible.sourceFolder ) )
        self.parentApp = parentApp
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'USFMEditWindow __init__ {}'.format( USFMBible.sourceFolder ) )

        # Set some dummy values required soon (esp. by refreshTitle)
        #self.defaultContextViewMode = BIBLE_CONTEXT_VIEW_MODES[0] # BeforeAndAfter
        #self.defaultFormatViewMode = 'Unformatted' # Only option done so far
        self.editMode = DEFAULT
        self.editStatus = 'Editable'
        self.bookTextModified = False
        self.projectName = 'NoProjectName'
        InternalBibleResourceWindow.__init__( self, parentApp, None, BIBLE_CONTEXT_VIEW_MODES[0], 'Unformatted' )
        TextEditWindow.__init__( self, parentApp ) # calls refreshTitle
        #self.overrideredirect( 1 ) # Remove the title bar

        # Now we need to override a few critical variables
        self.genericWindowType = 'BibleEditor' # from 'TextEditor'
        self.windowType = 'USFMBibleEditWindow' # from 'PlainTextEditWindow'
        if editMode is not None: self.editMode = editMode
        self.verseCache = OrderedDict()

        #self.doToggleStatusBar( True ) # defaults to off in ChildWindow

        self.internalBible = handleInternalBibles( self.parentApp, USFMBible, self )
        if self.internalBible is not None:
            self.projectName = self.internalBible.shortName if self.internalBible.shortName else self.internalBible.givenName
            if not self.projectName:
                self.projectName = self.internalBible.name if self.internalBible.name else self.internalBible.abbreviation
        #try: print( "\n\n\n\nUEW settings for {}:".format( self.projectName ), self.settings )
        #except: print( "\n\n\n\nUEW has no settings!" )
        #if not self.projectName: self.projectName = 'NoProjectName'

        self.myKeyboardBindingsList = []
        if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = []

        Style().configure( self.projectName+'USFM.Vertical.TScrollbar', background='green' )
        self.vScrollbar.configure( command=self.textBox.yview, style=self.projectName+'USFM.Vertical.TScrollbar' ) # link the scrollbar to the text box
        #self.createStandardKeyboardBindings()
        self.createEditorKeyboardBindings()

        self.defaultBackgroundColour = 'plum1'
        if self.internalBible is None: self.editMode = None
        else:
            self.textBox.configure( background=self.defaultBackgroundColour )
            self.textBox.configure( selectbackground='blue' )
            self.textBox.configure( highlightbackground='orange' )
            self.textBox.configure( inactiveselectbackground='green' )

        # Temporarily include some default invalid values
        self.invalidCombinations = ['__',',,',' ,','..',' .',';;',' ;','!!',' !',
                                    '"',
                                    '\\f*,','\\f*.','\\f*:','\\f*;','\\f*?','\\f*!',
                                    '\\x*,','\\x*.','\\x* ',
                                    ] # characters or character combinations that shouldn't occur

        self.checkForPairs = [] # tuples with pairs of characters that should normally be together in the same verse
                                # NOTE: don't include pairs (like quotes) that frequently occur across multiple verses
                                #   i.e., are often NOT closed within the same line or verse.
        # Temporarily include some pairs
        self.checkForPairs.extend( ( ('(',')'), ('[',']'), ('_ ',' _'),) )
        self.checkForPairs.extend( ( ('\\f ','\\f*'), ('\\x ','\\x*'), ('\\fe ','\\fe*'),) )
        self.checkForPairs.extend( ( # Special text
                                     ('\\add ','\\add*'), ('\\bk ','\\bk*'), ('\\dc ','\\dc*'),
                                     ('\\k ','\\k*'), ('\\nd ','\\nd*'), ('\\ord ','\\ord*'),
                                     ('\\pn ','\\pn*'), ('\\qt ','\\qt*'), ('\\sig ','\\sig*'),
                                     ('\\sls ','\\sls*'), ('\\tl ','\\tl*'), ('\\wj ','\\wj*'),

                                     # Character formatting
                                     ('\\em ','\\em*'), ('\\bd ','\\bd*'), ('\\it ','\\it*'),
                                     ('\\bdit ','\\bdit*'), ('\\no ','\\no*'), ('\\sc ','\\sc*'),

                                     # Special features
                                     ('\\fig ','\\fig*'), ('\\ndx ','\\ndx*'), ('\\pro ','\\pro*'),
                                     ('\\w ','\\w*'), ('\\wg ','\\wg*'), ('\\wh ','\\wh*'),
                                    ) )

        self.patternsToHighlight = []
        # Temporarily include some default values
        self.patternsToHighlight.append( (True,'\\\\.*?[ *\n]','green',{'foreground':'green'}) ) # green USFM markers
        self.patternsToHighlight.append( (True,'\\d','blue',{'foreground':'blue'}) ) # blue digits
        self.patternsToHighlight.append( (True,'\\\\s .*?\n','redBold',{'font':self.customFontBold, 'foreground':'red'}) ) # red section headings
        self.patternsToHighlight.append( (True,'\\\\r .*?\n','greenBold',{'font':self.customFontBold, 'foreground':'green'}) ) # green section references
        self.patternsToHighlight.append( (False,'XXX','redBack',{'background':'red'}) )
        #boldDict = {'font':self.customFontBold } #, 'background':'green'}
        #for pythonKeyword in ( 'from','import', 'class','def', 'if','and','or','else','elif',
                              #'for','while', 'return', 'try','accept','finally', 'assert', ):
            #self.patternsToHighlight.append( (True,'\\y'+pythonKeyword+'\\y','bold',boldDict) )

        self.folderPath = self.filename = self.filepath = None
        self.lastBBB = None
        self.bookTextBefore = self.bookText = self.bookTextAfter = None # The current text for this book
        self.exportFolderPathname = None

        self.saveChangesAutomatically = True # different from AutoSave (which is in different files in different folders)

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.__init__ finished.") )
    # end of USFMEditWindow.__init__


    #def __str__(self): return "USFMEditWindow"
    #def __repr__(self): return "USFMEditWindow"


    def refreshTitle( self ):
        """
        Refresh the title of the USFM edit window,
            put an asterisk if it's modified
            and update the BCV reference.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("USFMEditWindow.refreshTitle()") )

        referenceBit = '' if self.currentVerseKey is None else '{} {}:{} ' \
            .format( self.currentVerseKey.getBBB(), self.currentVerseKey.getChapterNumber(), self.currentVerseKey.getVerseNumber() )
        self.title( '{}[{}] {} {}({}) {} {}'.format( '*' if self.modified() else '',
                                    self._groupCode, self.projectName,
                                    '' if self.currentVerseKey is None else referenceBit,
                                    self.editMode, self.editStatus, self._contextViewMode ) )
        Style().configure( self.projectName+'USFM.Vertical.TScrollbar', background='yellow' if self.modified() else 'SeaGreen1' )
        self.refreshTitleContinue() # handle Autosave
    # end if USFMEditWindow.refreshTitle


    #def xxdoHelp( self ):
        #from Help import HelpBox
        #hb = HelpBox( self.parentApp, ProgName, ProgNameVersion )
    ## end of USFMEditWindow.doHelp


    #def xxdoAbout( self ):
        #from About import AboutBox
        #ab = AboutBox( self.parentApp, ProgName, ProgNameVersion )
    ## end of USFMEditWindow.doAbout


    def createEditorKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.createEditorKeyboardBindings()") )

        for name,command in ( #('Paste',self.doPaste), ('Cut',self.doCut),
                             #('Undo',self.doUndo), ('Redo',self.doRedo),
                             ('Save',self.doSave),
                             ('Find',self.doBibleFind), ('Replace',self.doBibleReplace),
                             ('ShowMain',self.doShowMainWindow), ):
            assert (name,self.parentApp.keyBindingDict[name][0],) not in self.myKeyboardBindingsList
            if name in self.parentApp.keyBindingDict:
                for keyCode in self.parentApp.keyBindingDict[name][1:]:
                    #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                    self.textBox.bind( keyCode, command )
                    if BibleOrgSysGlobals.debugFlag:
                        assert keyCode not in self.myKeyboardShortcutsList
                        self.myKeyboardShortcutsList.append( keyCode )
                self.myKeyboardBindingsList.append( (name,self.parentApp.keyBindingDict[name][0],) )
            else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of USFMEditWindow.createEditorKeyboardBindings()


    def createMenuBar( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.createMenuBar()") )

        self.menubar = tk.Menu( self )
        #self['menu'] = self.menubar
        self.configure( menu=self.menubar ) # alternative

        fileMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=fileMenu, label=_('File'), underline=0 )
        fileMenu.add_command( label=_('Save'), underline=0, command=self.doSave, accelerator=self.parentApp.keyBindingDict[_('Save')][0] )
        fileMenu.add_command( label=_('Save as…'), underline=5, command=self.doSaveAs )
        fileMenu.add_separator()
        #subfileMenuImport = tk.Menu( fileMenu, tearoff=False )
        #subfileMenuImport.add_command( label=_('USX'), underline=0, command=self.notWrittenYet )
        #fileMenu.add_cascade( label=_('Import'), underline=0, menu=subfileMenuImport )
        #fileMenu.add_command( label=_('Export'), underline=1, command=self.doMostExports )
        subFileMenuExport = tk.Menu( fileMenu, tearoff=False )
        subFileMenuExport.add_command( label=_('Quick exports'), underline=0, command=self.doMostExports )
        subFileMenuExport.add_command( label=_('PhotoBible'), underline=0, command=self.doPhotoBibleExport )
        subFileMenuExport.add_command( label=_('ODFs'), underline=0, command=self.doODFsExport )
        subFileMenuExport.add_command( label=_('PDFs'), underline=1, command=self.doPDFsExport )
        subFileMenuExport.add_command( label=_('All exports'), underline=0, command=self.doAllExports )
        fileMenu.add_cascade( label=_('Export'), underline=1, menu=subFileMenuExport )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Info…'), underline=0, command=self.doShowInfo )
        fileMenu.add_separator()
        fileMenu.add_command( label=_('Close'), underline=0, command=self.doClose )

        editMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=editMenu, label=_('Edit'), underline=0 )
        editMenu.add_command( label=_('Undo'), underline=0, command=self.doUndo )
        editMenu.add_command( label=_('Redo'), underline=0, command=self.doRedo )
        editMenu.add_separator()
        editMenu.add_command( label=_('Cut'), underline=2, command=self.doCut )
        editMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy )
        editMenu.add_command( label=_('Paste'), underline=0, command=self.doPaste )
        editMenu.add_separator()
        editMenu.add_command( label=_('Delete'), underline=0, command=self.doDelete )
        editMenu.add_command( label=_('Select all'), underline=0, command=self.doSelectAll )

        searchMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=searchMenu, label=_('Search'), underline=0 )
        #subsearchMenuBible = tk.Menu( searchMenu, tearoff=False )
        searchMenu.add_command( label=_('Bible Find…'), underline=0, command=self.doBibleFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        #subsearchMenuBible.add_command( label=_('Find again'), underline=5, command=self.notWrittenYet )
        searchMenu.add_command( label=_('Replace…'), underline=0, command=self.doBibleReplace, accelerator=self.parentApp.keyBindingDict[_('Replace')][0] )
        #searchMenu.add_cascade( label=_('Bible'), underline=0, menu=subsearchMenuBible )
        searchMenu.add_separator()
        subSearchMenuWindow = tk.Menu( searchMenu, tearoff=False )
        subSearchMenuWindow.add_command( label=_('Goto line…'), underline=0, command=self.doGotoWindowLine )
        subSearchMenuWindow.add_separator()
        subSearchMenuWindow.add_command( label=_('Find…'), underline=0, command=self.doWindowFind )
        subSearchMenuWindow.add_command( label=_('Find again'), underline=5, command=self.doWindowRefind )
        subSearchMenuWindow.add_command( label=_('Replace…'), underline=0, command=self.doWindowFindReplace )
        searchMenu.add_cascade( label=_('Window'), underline=0, menu=subSearchMenuWindow )

        gotoMenu = tk.Menu( self.menubar )
        self.menubar.add_cascade( menu=gotoMenu, label=_('Goto'), underline=0 )
        gotoMenu.add_command( label=_('Previous book'), underline=0, command=self.doGotoPreviousBook )
        gotoMenu.add_command( label=_('Next book'), underline=0, command=self.doGotoNextBook )
        gotoMenu.add_command( label=_('Previous chapter'), underline=0, command=self.doGotoPreviousChapter )
        gotoMenu.add_command( label=_('Next chapter'), underline=0, command=self.doGotoNextChapter )
        gotoMenu.add_command( label=_('Previous section'), underline=0, command=self.doGotoPreviousSection )
        gotoMenu.add_command( label=_('Next section'), underline=0, command=self.doGotoNextSection )
        gotoMenu.add_command( label=_('Previous verse'), underline=0, command=self.doGotoPreviousVerse )
        gotoMenu.add_command( label=_('Next verse'), underline=0, command=self.doGotoNextVerse )
        gotoMenu.add_separator()
        gotoMenu.add_command( label=_('Forward'), underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label=_('Backward'), underline=0, command=self.notWrittenYet )
        gotoMenu.add_separator()
        gotoMenu.add_command( label=_('Previous list item'), underline=0, command=self.notWrittenYet )
        gotoMenu.add_command( label=_('Next list item'), underline=0, command=self.notWrittenYet )
        gotoMenu.add_separator()
        gotoMenu.add_command( label=_('Book'), underline=0, command=self.notWrittenYet )
        gotoMenu.add_separator()
        self._groupRadioVar.set( self._groupCode )
        gotoMenu.add_radiobutton( label=_('Group A'), underline=6, value='A', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group B'), underline=6, value='B', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group C'), underline=6, value='C', variable=self._groupRadioVar, command=self.changeBibleGroupCode )
        gotoMenu.add_radiobutton( label=_('Group D'), underline=6, value='D', variable=self._groupRadioVar, command=self.changeBibleGroupCode )

        #if   self._contextViewMode == 'BeforeAndAfter': self._contextViewRadioVar.set( 1 )
        #elif self._contextViewMode == 'BySection': self._contextViewRadioVar.set( 2 )
        #elif self._contextViewMode == 'ByVerse': self._contextViewRadioVar.set( 3 )
        #elif self._contextViewMode == 'ByBook': self._contextViewRadioVar.set( 4 )
        #elif self._contextViewMode == 'ByChapter': self._contextViewRadioVar.set( 5 )

        viewMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=viewMenu, label=_('View'), underline=0 )
        viewMenu.add_radiobutton( label=_('Before and after…'), underline=7, value=1, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label=_('One section'), underline=4, value=2, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label=_('Single verse'), underline=7, value=3, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label=_('Whole book'), underline=6, value=4, variable=self._contextViewRadioVar, command=self.changeBibleContextView )
        viewMenu.add_radiobutton( label=_('Whole chapter'), underline=6, value=5, variable=self._contextViewRadioVar, command=self.changeBibleContextView )

        #if   self._formatViewMode == 'Formatted': self._formatViewRadioVar.set( 1 )
        #elif self._formatViewMode == 'Unformatted': self._formatViewRadioVar.set( 2 )
        #else: print( self._formatViewMode ); halt

        #viewMenu.add_separator()
        #viewMenu.add_radiobutton( label=_('Formatted'), underline=0, value=1, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )
        #viewMenu.add_radiobutton( label=_('Unformatted'), underline=0, value=2, variable=self._formatViewRadioVar, command=self.changeBibleFormatView )

        viewMenu.add_separator()
        viewMenu.add_command( label=_('Larger text'), underline=0, command=self.OnFontBigger )
        viewMenu.add_command( label=_('Smaller text'), underline=1, command=self.OnFontSmaller )
        viewMenu.add_separator()
        viewMenu.add_checkbutton( label=_('Status bar'), underline=0, variable=self._showStatusBarVar, command=self.doToggleStatusBar )

        #viewMenu.entryconfigure( 'Before and after…', state=tk.DISABLED )
        #viewMenu.entryconfigure( 'One section', state=tk.DISABLED )
        #viewMenu.entryconfigure( 'Single verse', state=tk.DISABLED )
        #viewMenu.entryconfigure( 'Whole chapter', state=tk.DISABLED )

        toolsMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=toolsMenu, label=_('Tools'), underline=0 )
        toolsMenu.add_command( label=_('Check project…'), underline=0, command=self.doCheckProject )
        toolsMenu.add_separator()
        toolsMenu.add_command( label=_('Options…'), underline=0, command=self.doAdjustOptions )

        windowMenu = tk.Menu( self.menubar, tearoff=False )
        self.menubar.add_cascade( menu=windowMenu, label=_('Window'), underline=0 )
        windowMenu.add_command( label=_('Bring in'), underline=0, command=self.notWrittenYet )
        windowMenu.add_separator()
        windowMenu.add_command( label=_('Start reference mode (A->B)'), underline=6, command=self.startReferenceMode )
        windowMenu.add_command( label=_('Start parallel mode (A->B,C,D)'), underline=6, command=self.startParallelMode )
        windowMenu.add_separator()
        windowMenu.add_command( label=_('Start references mode (A->)'), underline=0, command=self.startReferencesMode )
        windowMenu.add_separator()
        windowMenu.add_command( label=_('Show main window'), underline=0, command=self.doShowMainWindow, accelerator=self.parentApp.keyBindingDict[_('ShowMain')][0] )

        if BibleOrgSysGlobals.debugFlag:
            debugMenu = tk.Menu( self.menubar, tearoff=False )
            self.menubar.add_cascade( menu=debugMenu, label=_('Debug'), underline=0 )
            #debugMenu.add_command( label=_('View settings…'), underline=5, command=self.doViewSettings )
            #debugMenu.add_separator()
            debugMenu.add_command( label=_('View log…'), underline=5, command=self.doViewLog )

        helpMenu = tk.Menu( self.menubar, name='help', tearoff=False )
        self.menubar.add_cascade( menu=helpMenu, label=_('Help'), underline=0 )
        helpMenu.add_command( label=_('Help…'), underline=0, command=self.doHelp )
        helpMenu.add_separator()
        helpMenu.add_command( label=_('About…'), underline=0, command=self.doAbout )
    # end of USFMEditWindow.createMenuBar


    #def xxcreateContextMenu( self ):
        #"""
        #"""
        #self.contextMenu = tk.Menu( self, tearoff=0 )
        #self.contextMenu.add_command( label=_('Cut'), underline=2, command=self.doCut )
        #self.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy )
        #self.contextMenu.add_command( label=_('Paste'), underline=0, command=self.doPaste )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close'), underline=1, command=self.doCloseEditor )

        #self.bind( '<Button-3>', self.showContextMenu ) # right-click
        ##self.pack()
    ## end of USFMEditWindow.createContextMenu


    #def showContextMenu( self, e):
        #self.contextMenu.post( e.x_root, e.y_root )
    ## end of USFMEditWindow.showContextMenu


    #def createToolBar( self ):
        #toolbar = Frame( self, cursor='hand2', relief=tk.SUNKEN ) # bd=2
        #toolbar.pack( side=tk.BOTTOM, fill=tk.X )
        #Button( toolbar, text='Halt',  command=self.quit ).pack( side=tk.RIGHT )
        #Button( toolbar, text='Hide Resources', command=self.hideResources ).pack(side=tk.LEFT )
        #Button( toolbar, text='Hide All', command=self.hideAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Show All', command=self.showAll ).pack( side=tk.LEFT )
        #Button( toolbar, text='Bring All', command=self.bringAll ).pack( side=tk.LEFT )
    ## end of USFMEditWindow.createToolBar


    def doAdjustOptions( self ):
        """
        """
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'doAdjustOptions' )
        logging.debug( exp("doAdjustOptions()") )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("doAdjustOptions()") )
            self.parentApp.setDebugText( "doAdjustOptions…" )
        #self.parentApp.setWaitStatus( _("Preparing autocomplete words…") )

        tOD = ToolsOptionsDialog( self ) # This is a modal dialog
    # end of USFMEditWindow.doAdjustOptions



    def prepareAutocomplete( self ):
        """
        """
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'prepareAutocomplete' )
        logging.debug( exp("prepareAutocomplete()") )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("prepareAutocomplete()") )
            self.parentApp.setDebugText( "prepareAutocomplete…" )
        self.parentApp.setWaitStatus( _("Preparing autocomplete words…") )

        # Choose ONE of the following options
        if self.autocompleteMode == 'Bible':
            loadBibleAutocompleteWords( self ) # Find words used in the Bible to fill the autocomplete mechanism
        elif self.autocompleteMode == 'BibleBook':
            loadBibleBookAutocompleteWords( self ) # Find words used in this Bible book to fill the autocomplete mechanism
        elif self.autocompleteMode == 'Dictionary1':
            loadHunspellAutocompleteWords( self, '/usr/share/hunspell/en_AU.dic', 'iso8859-15' )
        elif self.autocompleteMode == 'Dictionary2':
            loadILEXAutocompleteWords( self, '../../../MyPrograms/TED_Dictionary/EnglishDict.db', ('ENG','BRI',) )
        elif BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( repr(self.autocompleteMode) ); halt # Programming error
    # end of USFMEditWindow.prepareAutocomplete



    def onTextChange( self, result, *args ):
        """
        Called whenever the text box cursor changes either with a mouse click or arrow keys.

        Checks to see if they have moved to a new chapter/verse,
            and if so, informs the parent app.
        """
        if self.loading: return # So we don't get called a million times for nothing
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.onTextChange( {}, {} )").format( repr(result), args ) )

        #if 0: # Get line and column info
            #lineColumn = self.textBox.index( tk.INSERT )
            #print( "lc", repr(lineColumn) )
            #line, column = lineColumn.split( '.', 1 )
            #print( "l,c", repr(line), repr(column) )

        #if 0: # get formatting tag info
            #tagNames = self.textBox.tag_names( tk.INSERT )
            #tagNames2 = self.textBox.tag_names( lineColumn )
            #tagNames3 = self.textBox.tag_names( tk.INSERT + ' linestart' )
            #tagNames4 = self.textBox.tag_names( lineColumn + ' linestart' )
            #tagNames5 = self.textBox.tag_names( tk.INSERT + ' linestart+1c' )
            #tagNames6 = self.textBox.tag_names( lineColumn + ' linestart+1c' )
            #print( "tN", tagNames )
            #if tagNames2!=tagNames or tagNames3!=tagNames or tagNames4!=tagNames or tagNames5!=tagNames or tagNames6!=tagNames:
                #print( "tN2", tagNames2 )
                #print( "tN3", tagNames3 )
                #print( "tN4", tagNames4 )
                #print( "tN5", tagNames5 )
                #print( "tN6", tagNames6 )
                #halt

        #if 0: # show various mark strategies
            #mark1 = self.textBox.mark_previous( tk.INSERT )
            #mark2 = self.textBox.mark_previous( lineColumn )
            #mark3 = self.textBox.mark_previous( tk.INSERT + ' linestart' )
            #mark4 = self.textBox.mark_previous( lineColumn + ' linestart' )
            #mark5 = self.textBox.mark_previous( tk.INSERT + ' linestart+1c' )
            #mark6 = self.textBox.mark_previous( lineColumn + ' linestart+1c' )
            #print( "mark1", mark1 )
            #if mark2!=mark1:
                #print( "mark2", mark1 )
            #if mark3!=mark1 or mark4!=mark1 or mark5!=mark1 or mark6!=mark1:
                #print( "mark3", mark3 )
                #if mark4!=mark3:
                    #print( "mark4", mark4 )
                #print( "mark5", mark5 )
                #if mark6!=mark5:
                    #print( "mark6", mark6 )

        try: TextEditWindow.onTextChange( self, result, *args ) # Handles autocorrect and autocomplete
        except KeyboardInterrupt:
            print( "USFMEditWindow: Got keyboard interrupt (1) -- saving my file…" )
            self.doSave() # Sometimes the above seems to lock up
            #print( 'gfs', self.onTextNoChangeID )
            if self.onTextNoChangeID:
                self.after_cancel( self.onTextNoChangeID ) # Cancel any delayed no change checks which are scheduled
                self.onTextNoChangeID = None
            return

        if self.textBox.edit_modified():
            self.bookTextModified = True

            # Check the text for USFM errors
            try: self.checkUSFMTextForProblems()
            except KeyboardInterrupt:
                print( "USFMEditWindow: Got keyboard interrupt (2) -- saving my file…" )
                self.doSave() # Sometimes the above seems to lock up
                #print( 'DSDS', self.onTextNoChangeID )
                if self.onTextNoChangeID:
                    self.after_cancel( self.onTextNoChangeID ) # Cancel any delayed no change checks which are scheduled
                    self.onTextNoChangeID = None
                return

        # Try to determine the CV mark
        # It seems that we have to try various strategies because
        #       sometimes we get a 'current' mark and sometimes an 'anchor1'
        gotCV = False
        # Try to put the most useful methods first (for efficiency)
        for mark in (self.textBox.mark_previous(tk.INSERT), self.textBox.mark_previous(tk.INSERT+'-1c'),
                    self.textBox.mark_previous(tk.INSERT+' linestart+1c'), self.textBox.mark_previous(tk.INSERT+' linestart'),):
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #print( "  mark", j, mark )
                if mark is None: print( "    WHY is mark NONE?" )
            if mark and mark[0]=='C' and mark[1].isdigit() and 'V' in mark:
                gotCV = True; break
        if gotCV and mark != self.lastCVMark:
            self.lastCVMark = mark
            C, V = mark[1:].split( 'V', 1 )
            #self.parentApp.gotoGroupBCV( self._groupCode, self.currentVerseKey.getBBB(), C, V )
            self.after_idle( lambda: self.parentApp.gotoGroupBCV( self._groupCode, self.currentVerseKey.getBBB(), C, V, originator=self ) )
    # end of USFMEditWindow.onTextChange


    def onTextNoChange( self ):
        """
        Called whenever the text box HASN'T CHANGED for NO_TYPE_TIME msecs.

        Checks for some types of formatting errors.
        """
        #print( "USFMEditWindow.onTextNoChange" )

        # Check the text for formatting errors
        try: self.checkUSFMTextForProblems( includeFormatting=True )
        except KeyboardInterrupt:
            print( "USFMEditWindow: Got keyboard interrupt (3) -- saving my file" )
            self.doSave() # Sometimes the above seems to lock up
    # end of USFMEditWindow.onTextNoChange


    def checkUSFMTextForProblems( self, includeFormatting=False ):
        """
        Called whenever the text box HASN'T CHANGED for NO_TYPE_TIME msecs.

        Checks for some types of formatting errors.
        """
        #print( "USFMEditWindow.checkUSFMTextForProblems", includeFormatting )

        editedText = self.getAllText()

        # Check counts of USFM chapter and verse markers
        numChaps = editedText.count( '\\c ' )
        numVerses = editedText.count( '\\v ' )
        BBB, C, V = self.currentVerseKey.getBCV()
        #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        if self._contextViewMode == 'BeforeAndAfter':
            minChapterMarkers, maxChapterMarkers = 0, 1
            if C == '0': minVerseMarkers = maxVerseMarkers = 0
            elif C=='1' and V=='1': minVerseMarkers = maxVerseMarkers = 2
            else: minVerseMarkers = maxVerseMarkers = 3
        elif self._contextViewMode == 'ByVerse':
            minChapterMarkers = maxChapterMarkers = 1 if V=='0' and C!='0' else 0
            if C == '0': minVerseMarkers = maxVerseMarkers = 0
            elif V == '0': minVerseMarkers = maxVerseMarkers = 0
            else: minVerseMarkers = maxVerseMarkers = 1
        elif self._contextViewMode == 'BySection':
            minChapterMarkers, maxChapterMarkers = 0, 1
            minVerseMarkers, maxVerseMarkers = (0,0) if C=='0' else (1,10)
        elif self._contextViewMode == 'ByBook':
            minChapterMarkers = maxChapterMarkers = self.getNumChapters( BBB )
            minVerseMarkers = maxVerseMarkers = self.numTotalVerses
        elif self._contextViewMode == 'ByChapter':
            minChapterMarkers = maxChapterMarkers = 0 if C=='0' else 1
            minVerseMarkers = maxVerseMarkers = 0 if C=='0' else self.getNumVerses( BBB, C )
        else: halt

        errorMessage = warningMessage = suggestionMessage = None
        if numChaps > maxChapterMarkers:
            errorMessage = _("Too many USFM chapter markers (max of {} expected)").format( maxChapterMarkers )
            #print( errorMessage )
        elif numChaps < minChapterMarkers:
            warningMessage = _("May have missing USFM chapter markers (expected {}, found {})").format( maxChapterMarkers, numChaps )
            #print( warningMessage )
        if numVerses > maxVerseMarkers:
            errorMessage = _("Too many USFM verse markers (max of {} expected)").format( maxVerseMarkers )
            #print( errorMessage )
        elif numVerses < minVerseMarkers:
            warningMessage = _("May have missing USFM verse markers (expected {}, found {})").format( maxVerseMarkers, numVerses )
            #print( warningMessage )
        if '  ' in editedText:
            warningMessage = _("No good reason to have multiple spaces in a USFM book")
            #print( warningMessage )
        elif includeFormatting and ' \n' in editedText:
            suggestionMessage = _("No good reason to have a line ending with a space in a USFM book")

        if not errorMessage and not warningMessage: # and not suggestionMessage:
            adjText = editedText
            if adjText and adjText[-1] in ('\n','\r',): adjText = adjText[:-1] # Remove the final newline character
            for line in adjText.split( '\n' ):
                #print( "checkUSFMTextForProblems got line: {!r}".format( line ) )
                if not line:
                    warningMessage = _("No good reason to have a blank line in a USFM book")
                if line:
                    if line[0] == '\\':
                        marker = line.split( None, 1)[0][1:] # First token, but without the first (backslash) character
                        #print( "  Found marker: {!r}".format( marker ) )
                        if marker not in BibleOrgSysGlobals.USFMMarkers:
                            errorMessage = _("Not a recognized USFM marker {!r}").format( marker )
                            break
                    else:
                        errorMessage = _("Line should start with backslash, not '{}{}'").format( line[:8], '…' if len(line)>8 else '' )
                        break

        if not errorMessage and not warningMessage: # and not suggestionMessage:
            for segment in self.invalidCombinations:
                if segment in editedText:
                    warningMessage = _("Found {!r} invalid character(s) in USFM text").format( segment ); break

        if not errorMessage and not warningMessage and not suggestionMessage:
            for pairStart,pairEnd in self.checkForPairs:
                if editedText.count( pairStart ) != editedText.count( pairEnd ):
                    warningMessage = _("Counts of {!r} and {!r} differ in USFM text").format( pairStart, pairEnd ); break
                # NOTE: Code below doesn't give error with ( ( ) -- that's why we have the counts above
                ixl = -1
                while True:
                    ixl = editedText.find( pairStart, ixl+1 )
                    if ixl == -1: break # none / no more found
                    ixr = editedText.find( pairEnd, ixl+len(pairStart) )
                    if ixr == -1: # no matching pair
                        warningMessage = _("Found {!r} without matching {!r} in USFM text").format( pairStart, pairEnd ); break
                if warningMessage: break # from outer loop
                ixr = 99999 # Now work backwards
                while True:
                    ixr = editedText.rfind( pairEnd, 0, ixr )
                    if ixr == -1: break
                    ixl = editedText.rfind( pairStart, 0, ixr )
                    if ixl == -1:
                        warningMessage = _("Found {!r} without previous {!r} in USFM text").format( pairEnd, pairStart ); break
                if warningMessage: break # from outer loop

        haveOwnStatusBar = self._showStatusBarVar.get()
        if errorMessage:
            if haveOwnStatusBar: self.setErrorStatus( errorMessage )
            else: self.parentApp.setErrorStatus( errorMessage )
            self.textBox.configure( background='firebrick1' )
            self.hadTextWarning = True
        elif warningMessage:
            if haveOwnStatusBar: self.setErrorStatus( warningMessage )
            else: self.parentApp.setErrorStatus( warningMessage )
            self.textBox.configure( background='chocolate1' )
            self.hadTextWarning = True
        elif suggestionMessage:
            if haveOwnStatusBar: self.setErrorStatus( suggestionMessage )
            else: self.parentApp.setErrorStatus( suggestionMessage )
            self.textBox.configure( background='orchid1' ) # Make this one not too dissimilar from the default
            self.hadTextWarning = True
        elif self.hadTextWarning: # last time but not now
            self.textBox.configure( background=self.defaultBackgroundColour )
            if haveOwnStatusBar: self.setReadyStatus()
            else: self.parentApp.setReadyStatus()
    # end of USFMEditWindow.checkUSFMTextForProblems


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'doShowInfo' )
        logging.debug( exp("USFMEditWindow.doShowInfo( {} )").format( event ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doShowInfo( {} )").format( event ) )

        text  = self.getEntireText()
        numChars = len( text )
        numLines = len( text.split( '\n' ) )
        numWords = len( text.split() )
        index = self.textBox.index( tk.INSERT )
        atLine, atColumn = index.split('.')

        BBB, C, V = self.currentVerseKey.getBCV()
        numChaps = text.count( '\\c ' )
        numVerses = text.count( '\\v ' )
        numSectionHeadings = text.count('\\s ')+text.count('\\s1 ')+text.count('\\s2 ')+text.count('\\s3 ')+text.count('\\s4 ')

        grandtotal = 0
        for firstLetter in self.autocompleteWords:
            grandtotal += len( self.autocompleteWords[firstLetter] )

        infoString = 'Current location:\n' \
            + '  BCV: {} {}:{}\n'.format( BBB, C, V ) \
            + '  Line, column: {}, {}\n'.format( atLine, atColumn ) \
            + '\nFile text statistics:\n' \
            + '  Chapts: {:,}\n  Verses: {:,}\n  Sections: {:,}\n'.format( numChaps, numVerses, numSectionHeadings ) \
            + '  Chars: {:,}\n  Lines: {:,}\n  Words: {:,}\n'.format( numChars, numLines, numWords ) \
            + '\nFile info:\n' \
            + '  Name: {}\n  Folder: {}\n  BookFN: {}\n  SourceFldr: {}\n' \
                    .format( self.filename, self.filepath, self.bookFilename, self.internalBible.sourceFolder ) \
            + '\nSettings:\n' \
            + '  Autocorrect entries: {:,}\n  Autocomplete mode: {}\n  Autocomplete entries: {:,}\n  Autosave time: {} secs\n  Save changes automatically: {}' \
                .format( len(self.autocorrectEntries), self.autocompleteMode, grandtotal, round(self.autosaveTime/1000), self.saveChangesAutomatically )
        showinfo( self, '{} Window Information'.format( BBB ), infoString )
    # end of USFMEditWindow.doShowInfo


    def modified( self ):
        return self.bookTextModified or self.textBox.edit_modified()
    # end of USFMEditWindow.modified


    def getBookDataFromDisk( self, BBB ):
        """
        Fetches and returns the internal Bible data for the given book
            by reading the USFM source file completely
            and returning the text.
        """
        logging.debug( exp("USFMEditWindow.getBookDataFromDisk( {} ) was {} for {}").format( BBB, self.lastBBB, self.projectName ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.getBookDataFromDisk( {} ) was {} for {}").format( BBB, self.lastBBB, self.projectName ) )

        if BBB != self.lastBBB:
            #self.bookText = None
            #self.bookTextModified = False
            self.lastBBB = BBB
        if self.internalBible is not None:
            try: self.bookFilename = self.internalBible.possibleFilenameDict[BBB]
            except (AttributeError,KeyError) as err: # we have no books, or at least, not this book!
                #print( "  getBookDataFromDisk error: {}".format( err ) )
                #return None
                uNumber, uAbbrev = BibleOrgSysGlobals.BibleBooksCodes.getUSFMNumber(BBB), BibleOrgSysGlobals.BibleBooksCodes.getUSFMAbbreviation(BBB)
                if uNumber is None or uAbbrev is None: self.bookFilename = None
                else: self.bookFilename = '{}-{}.USFM'.format( uNumber, uAbbrev )
            if self.bookFilename:
                self.bookFilepath = os.path.join( self.internalBible.sourceFolder, self.bookFilename )
                if self.setFilepath( self.bookFilepath ): # For title displays, etc.
                    #print( exp('gVD'), BBB, repr(self.bookFilepath), repr(self.internalBible.encoding) )
                    bookText = open( self.bookFilepath, 'rt', encoding=self.internalBible.encoding ).read()
                    if bookText == None:
                        showerror( self, APP_NAME, _("Couldn't decode and open file {} with encoding {}").format( self.bookFilepath, self.internalBible.encoding ) )
                    return bookText
            else:
                showerror( self, APP_NAME, _("Couldn't determine USFM filename for {!r} book").format( BBB ) )
                return None
    # end of USFMEditWindow.getBookDataFromDisk


    def cacheBook( self, BBB, clearFirst=True ):
        """
        Puts the book data from self.bookText into the self.verseCache dictionary
            accessible by verse key.

        Automatically attaches section headings to the following verse
            (rather than having them appear at the end of the current verse).

        Normally clears the cache before starting,
            to prevent duplicate entries.
        """
        logging.debug( exp("USFMEditWindow.cacheBook( {}, {} ) for {}").format( BBB, clearFirst, self.projectName ) )
        if BibleOrgSysGlobals.debugFlag:
            print( exp("USFMEditWindow.cacheBook( {}, {} ) for {}").format( BBB, clearFirst, self.projectName ) )
            assert isinstance( BBB, str )

        if clearFirst:
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  Clearing cache first!" )
            self.verseCache = OrderedDict()

        def addCacheEntry( BBB, C, V, data ):
            """
            Check for duplicates before
                adding a new BCV entry to the book cache.
            """
            #print( "addCacheEntry", BBB, C, V, data )
            assert BBB and C and V and data
            verseKeyHash = SimpleVerseKey( BBB, C, V ).makeHash()
            if verseKeyHash in self.verseCache: # Oh, how come we already have this key???
                if data == self.verseCache[verseKeyHash]:
                    logging.critical( "cacheBook: We have an identical duplicate {}: {!r}".format( verseKeyHash, data ) )
                else:
                    logging.critical( "cacheBook: We have a duplicate {} -- already had {!r} and now appending {!r}" \
                                    .format( verseKeyHash, self.verseCache[verseKeyHash], data ) )
                    data = self.verseCache[verseKeyHash] + '\n' + data
            self.verseCache[verseKeyHash] = data.replace( '\n\n', '\n' ) # Weed out blank lines
        # end of USFMEditWindow.cacheBook.addCacheEntry

        def getMarkerText( blIndex ):
            """
            Given an index to (nonlocal) bookLines,
                get that line and break into 2-tuple (marker,text).
            """
            gmtLine = bookLines[blIndex]
            #marker = text = None
            if gmtLine and gmtLine[0] == '\\':
                try: marker, text = gmtLine[1:].split( None, 1 )
                except ValueError: marker, text = gmtLine[1:].split( None, 1 )[0], ''
            else: marker, text = None, gmtLine
            return marker, text
        # end of USFMEditWindow.cacheBook.getMarkerText

        # Main code for cacheBook
        sectionHeadings = ( 's', 's1', 's2', 's3', 's4', )
        C = V = '0'
        startedVerseEarly = False
        currentEntry = ''
        bookLines = self.bookText.split( '\n' )
        numLines = len( bookLines )
        for j in range( 0, numLines): # Do it this way to make it easy to look-ahead
            line = bookLines[j]
            marker, text = getMarkerText( j )
            #print( "cacheBook line", repr(marker), repr(text) )

            if marker in ( 'c', 'C' ):
                newC = ''
                for char in line[3:]: # Get chapter number digits
                    if char.isdigit(): newC += char
                    else: break
                if newC:
                    if currentEntry:
                        addCacheEntry( BBB, C, V, currentEntry )
                        currentEntry = ''
                    C, V = newC, '0'
            elif marker in sectionHeadings:
                if j<numLines-2:
                    marker1, text1 = getMarkerText( j+1 )
                    if marker1 in ('r','sr','mr',):
                        marker2, text2 = getMarkerText( j+2 )
                        if marker2 in BibleOrgSysGlobals.USFMParagraphMarkers and not text2:
                            marker3, text3 = getMarkerText( j+3 )
                            if marker3 in ( 'v', 'V' ):
                                # Start a new verse entry here if we have a section heading, cross-reference, empty paragraph marker, then the next verse
                                if currentEntry: # Save the previous CV entry
                                    addCacheEntry( BBB, C, V, currentEntry )
                                    currentEntry = ''
                                    startedVerseEarly = True
                    elif marker1 in ( 'v', 'V' ): # There's actually a missing paragraph marker but nevermind
                        # Start a new verse entry here if we have a section heading, missing paragraph marker, then the next verse
                        if currentEntry: # Save the previous CV entry
                            addCacheEntry( BBB, C, V, currentEntry )
                            currentEntry = ''
                            startedVerseEarly = True
                    elif marker1 in BibleOrgSysGlobals.USFMParagraphMarkers and not text1:
                        marker2, text2 = getMarkerText( j+2 )
                        if marker2 in ( 'v', 'V' ):
                            # Start a new verse entry here if we have a section heading, empty paragraph marker, then the next verse
                            if currentEntry: # Save the previous CV entry
                                addCacheEntry( BBB, C, V, currentEntry )
                                currentEntry = ''
                                startedVerseEarly = True
            elif marker in ( 'v', 'V' ):
                newV = ''
                for char in line[3:]:
                    if char.isdigit(): newV += char
                    else: break
                if newV:
                    if currentEntry and not startedVerseEarly:
                        addCacheEntry( BBB, C, V, currentEntry )
                        currentEntry = ''
                    V = newV
                    startedVerseEarly = False
            elif marker in BibleOrgSysGlobals.USFMParagraphMarkers and not text and not startedVerseEarly: # already
                if j<numLines-1:
                    marker1, text1 = getMarkerText( j+1 )
                    if marker1 in ( 'v', 'V' ):
                        # We want to move this empty paragraph marker into the next verse
                        if currentEntry:
                            addCacheEntry( BBB, C, V, currentEntry )
                            currentEntry = ''
                            startedVerseEarly = True
            elif C=='0' and line.startswith( '\\' ):
                if currentEntry: # Should only happen if the file has blank lines before any chapter markers
                    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                        print( "cE", currentEntry )
                        # NOTE: This can fail if there's a line in the file NOT beginning with a USFM
                        #   i.e., a continuation line
                        assert currentEntry == '\n' # Warn programmer if it's anything different
                    addCacheEntry( BBB, C, V, currentEntry ) # Will give a duplicate entry error adding to newline
                    currentEntry = ''
                addCacheEntry( BBB, C, V, line + '\n' )
                V = str( int(V) + 1 )
                continue # Don't save current entry in next line
            currentEntry += line + '\n'
        if currentEntry: # cache the final verse
            addCacheEntry( BBB, C, V, currentEntry )
        #from itertools import islice
        #print( "USFMEditWindow.cacheBook", BBB, "verseCache:", list( islice( self.verseCache, 0, 20 ) ) )
    # end of USFMEditWindow.cacheBook


    def getCachedVerseData( self, verseKey ):
        """
        Returns the requested verse from our cache if it's there,
            otherwise returns None.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("getCachedVerseData( {} )").format( verseKey ) )
        try: return self.verseCache[verseKey.makeHash()]
        except KeyError: return None
    # end of USFMEditWindow.getCachedVerseData


    def updateShownBCV( self, newReferenceVerseKey, originator=None ):
        """
        Updates self.textBox in various ways depending on the contextViewMode held by the enclosing window.

        If newReferenceVerseKey is None: clears the window

        Otherwise, basically does the following steps (depending on the contextViewMode):
            1/ Saves any changes in the editor to self.bookText
            2/ If we've changed book:
                if changes to self.bookText, save them to disk
                load the new book text
            3/ Load the appropriate verses into the editor according to the contextViewMode.
        """
        logging.debug( "USFMEditWindow.updateShownBCV( {}, {} ) from {} for".format( newReferenceVerseKey, originator, self.currentVerseKey ), self.moduleID )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "USFMEditWindow.updateShownBCV( {}, {} ) from {} for".format( newReferenceVerseKey, originator, self.currentVerseKey ), self.moduleID )
            #print( "contextViewMode", self._contextViewMode )
            #assert self._formatViewMode == 'Unformatted' # Only option done so far

        if self.autocompleteBox is not None: self.removeAutocompleteBox()
        self.textBox.configure( background=self.defaultBackgroundColour ) # Go back to default background
        if self._formatViewMode != 'Unformatted': # Only option done so far
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "Ignoring {!r} mode for USFMEditWindow".format( self._formatViewMode ) )
            return

        oldVerseKey = self.currentVerseKey
        oldBBB, oldC, oldV = (None,None,None) if oldVerseKey is None else oldVerseKey.getBCV()

        if newReferenceVerseKey is None:
            newBBB = None
            self.setCurrentVerseKey( None )
        else: # it must be a real verse key
            assert isinstance( newReferenceVerseKey, SimpleVerseKey )
            refBBB, refC, refV, refS = newReferenceVerseKey.getBCVS()
            newBBB, C, V, S = self.BibleOrganisationalSystem.convertFromReferenceVersification( refBBB, refC, refV, refS )
            newVerseKey = SimpleVerseKey( newBBB, C, V, S )
            self.setCurrentVerseKey( newVerseKey )
            #if newBBB == 'PSA': halt
            if newBBB != oldBBB: self.numTotalVerses = calculateTotalVersesForBook( newBBB, self.getNumChapters, self.getNumVerses )
            if C != oldC and self.saveChangesAutomatically and self.modified(): self.doSave( 'Auto from chapter change' )

        if originator is self: # We initiated this by clicking in our own edit window
            # Don't do everything below because that makes the window contents move around annoyingly when clicked
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "Seems to be called from self--not much to do here" )
            self.refreshTitle()
            return

        if self.textBox.edit_modified(): # we need to extract the changes into self.bookText
            assert self.bookTextModified
            self.bookText = self.getEntireText()
            if newBBB == oldBBB: # We haven't changed books -- update our book cache
                self.cacheBook( newBBB )

        if newReferenceVerseKey is None:
            if oldVerseKey is not None:
                if self.bookTextModified: self.doSave() # resets bookTextModified flag
                self.clearText() # Leaves the text box enabled
                self.textBox.configure( state=tk.DISABLED ) # Don't allow editing
                self.textBox.edit_modified( False ) # clear modified flag (otherwise we could empty the book file)
                self.refreshTitle()
            return

        savedCursorPosition = self.textBox.index( tk.INSERT ) # Something like 55.6 for line 55, before column 6
        #print( "savedCursorPosition", savedCursorPosition )   #   Beginning of file is 1.0

        # Now check if the book they're viewing has changed since last time
        #       If so, save the old book if necessary
        #       then either load or create the new book
        #markAsUnmodified = True
        if newBBB != oldBBB: # we've switched books
            if self.bookTextModified: self.doSave() # resets bookTextModified flag
            self.editStatus = 'Editable'
            self.bookText = self.getBookDataFromDisk( newBBB )
            if self.bookText is None:
                uNumber, uAbbrev = BibleOrgSysGlobals.BibleBooksCodes.getUSFMNumber(newBBB), BibleOrgSysGlobals.BibleBooksCodes.getUSFMAbbreviation(newBBB)
                if uNumber is None or uAbbrev is None: # no use asking about creating the book
                    # NOTE: I think we've already shown this error in getBookDataFromDisk()
                    #showerror( self, APP_NAME, _("Couldn't determine USFM filename for {!r} book").format( newBBB ) )
                    self.clearText() # Leaves the text box enabled
                    self.textBox.edit_modified( tk.FALSE ) # clear Tkinter modified flag
                    self.bookTextModified = False
                    self.textBox.configure( state=tk.DISABLED ) # Don't allow editing
                    self.editStatus = 'DISABLED'
                else:
                    #showerror( self, _("USFM Editor"), _("We need to create the book: {} in {}").format( newBBB, self.internalBible.sourceFolder ) )
                    ocd = OkCancelDialog( self, _("We need to create the book: {} in {}".format( newBBB, self.internalBible.sourceFolder ) ), title=_('Create?') )
                    print( "ocdResult", repr(ocd.result) )
                    if ocd.result == True: # Ok was chosen
                        self.setFilename( '{}-{}.USFM'.format( uNumber, uAbbrev ), createFile=True )
                        self.bookText = createEmptyUSFMBookText( newBBB, self.getNumChapters, self.getNumVerses )
                        #markAsUnmodified = False
                        self.bookTextModified = True
                        #self.doSave() # Save the chapter/verse markers (blank book outline) ## Doesn't work -- saves a blank file
            else: self.cacheBook( newBBB )

        # Now load the desired part of the book into the edit window
        #   while at the same time, setting self.bookTextBefore and self.bookTextAfter
        #   (so that combining these three components, would reconstitute the entire file).
        if self.bookText is not None:
            self.loading = True # Turns off USFMEditWindow onTextChange notifications for now
            self.clearText() # Leaves the text box enabled
            startingFlag = True

            if self._contextViewMode == 'BeforeAndAfter':
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( 'USFMEditWindow.updateShownBCV', 'BeforeAndAfter2' )
                BBB, intC, intV = newVerseKey.getBBB(), newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
                self.bookTextBefore = self.bookTextAfter = ''
                numChaps = self.getNumChapters( BBB )
                if numChaps is None: numChaps = 0
                for thisC in range( 0, numChaps+1 ):
                    try: numVerses = self.getNumVerses( BBB, thisC )
                    except KeyError: numVerses = 0
                    for thisV in range( 0, numVerses+1 ):
                        thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                        thisVerseData = self.getCachedVerseData( thisVerseKey )
                        if thisC < intC: self.bookTextBefore += thisVerseData if thisVerseData else ''
                        elif thisC > intC: self.bookTextAfter += thisVerseData if thisVerseData else ''
                        elif thisV < intV-1: self.bookTextBefore += thisVerseData if thisVerseData else ''
                        elif thisV > intV+1: self.bookTextAfter += thisVerseData if thisVerseData else ''
                        else: # these are the displayed verses
                            RC = self.textBox.index( tk.INSERT ) # Something like 55.6 for line 55, before column 6
                            self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                                currentVerse=thisC==intC and thisV==intV,
                                                substituteTrailingSpaces=self.markTrailingSpacesFlag,
                                                substituteMultipleSpaces=self.markMultipleSpacesFlag )
                            if thisC==intC and thisV==intV and thisVerseData: # this is the current verse
                                row, col = RC.split( '.', 1 ) # Get our starting row/column
                                #print( 'R.C', repr(RC), repr(row), repr(col), 'tVD', repr(thisVerseData) )
                                lines = thisVerseData.split( '\n' )
                                offset = 0
                                if lines[0] and lines[0][0]=='\\' and lines[0][1:] in BibleOrgSysGlobals.USFMParagraphMarkers:
                                    # Assume the first line is just a USFM paragraph marker (with no other info)
                                    #print( "Move to 2.end after", repr(lines[0]), "for", self.moduleID )
                                    offset = 1
                                savedCursorPosition = '{}.end'.format( int(row) + offset ) # Move the cursor to the end of the SECOND line in the verse
                                #print( "Move to {!r} after {!r} for {}".format( savedCursorPosition, lines[0], self.moduleID ) )
                            startingFlag = False

            elif self._contextViewMode == 'ByVerse':
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( 'USFMEditWindow.updateShownBCV', 'ByVerse2' )
                savedCursorPosition = '1.end' # Default the cursor to the end of the first line
                BBB, intC, intV = newVerseKey.getBBB(), newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
                self.bookTextBefore = self.bookTextAfter = ''
                numChaps = self.getNumChapters( BBB )
                if numChaps is None: numChaps = 0
                for thisC in range( 0, numChaps+1 ):
                    try: numVerses = self.getNumVerses( BBB, thisC )
                    except KeyError: numVerses = 0
                    for thisV in range( 0, numVerses+1 ):
                        thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                        thisVerseData = self.getCachedVerseData( thisVerseKey )
                        if thisC < intC: self.bookTextBefore += thisVerseData if thisVerseData else ''
                        elif thisC > intC: self.bookTextAfter += thisVerseData if thisVerseData else ''
                        elif thisV < intV: self.bookTextBefore += thisVerseData if thisVerseData else ''
                        elif thisV > intV: self.bookTextAfter += thisVerseData if thisVerseData else ''
                        else: # this is the current verse
                            #print( "tVD for", self.moduleID, thisVerseKey, thisVerseData )
                            if thisVerseData is None: # We might have a missing or bridged verse
                                intV = int( thisV )
                                while intV > 1:
                                    intV -= 1 # Go back looking for bridged verses to display
                                    thisVerseData = self.getCachedVerseData( SimpleVerseKey( BBB, thisC, intV ) )
                                    #print( "  tVD for", self.moduleID, intV, thisVerseData )
                                    if thisVerseData is not None: # it seems to have worked
                                        break # Might have been nice to check/confirm that it was actually a bridged verse???
                            self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                                currentVerse=thisC==intC and thisV==intV,
                                                substituteTrailingSpaces=self.markTrailingSpacesFlag,
                                                substituteMultipleSpaces=self.markMultipleSpacesFlag )
                            #print( 'tVD', repr(thisVerseData) )
                            if thisVerseData:
                                lines = thisVerseData.split( '\n' )
                                if lines[0] and lines[0][0]=='\\' and lines[0][1:] in BibleOrgSysGlobals.USFMParagraphMarkers:
                                    # Assume the first line is just a USFM paragraph marker (with no other info)
                                    #print( "Move to 2.end after", repr(lines[0]), "for", self.moduleID )
                                    savedCursorPosition = '2.end' # Move the cursor to the end of the SECOND line

            elif self._contextViewMode == 'BySection':
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( 'USFMEditWindow.updateShownBCV', 'BySection2' )
                BBB, intC, intV = newVerseKey.getBBB(), newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
                sectionStart, sectionEnd = findCurrentSection( newVerseKey, self.getNumChapters, self.getNumVerses, self.getCachedVerseData )
                intC1, intV1 = sectionStart.getChapterNumberInt(), sectionStart.getVerseNumberInt()
                intC2, intV2 = sectionEnd.getChapterNumberInt(), sectionEnd.getVerseNumberInt()
                self.bookTextBefore = self.bookTextAfter = ''
                for thisC in range( 0, self.getNumChapters( BBB )+1 ):
                    try: numVerses = self.getNumVerses( BBB, thisC )
                    except KeyError: numVerses = 0
                    for thisV in range( 0, numVerses+1 ):
                        thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                        thisVerseData = self.getCachedVerseData( thisVerseKey )
                        if thisC < intC1 or (thisC==intC1 and thisV<intV1):
                            self.bookTextBefore += thisVerseData if thisVerseData else ''
                        elif thisC > intC2 or (thisC==intC2 and thisV>intV2):
                            self.bookTextAfter += thisVerseData if thisVerseData else ''
                        else: # we're in the section that we're interested in
                            self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                                    currentVerse=thisC==intC and thisV==intV )
                            startingFlag = False

            elif self._contextViewMode == 'ByBook':
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( 'USFMEditWindow.updateShownBCV', 'ByBook2' )
                self.bookTextBefore = self.bookTextAfter = ''
                BBB, intC, intV = newVerseKey.getBBB(), newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
                for thisC in range( 0, self.getNumChapters( BBB ) + 1 ):
                    try: numVerses = self.getNumVerses( BBB, thisC )
                    except KeyError: numVerses = 0
                    for thisV in range( 0, numVerses+1 ):
                        thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                        thisVerseData = self.getCachedVerseData( thisVerseKey )
                        #print( 'tVD', repr(thisVerseData) )
                        self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                                currentVerse=thisC==intC and thisV==intV )
                        startingFlag = False

            elif self._contextViewMode == 'ByChapter':
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( 'USFMEditWindow.updateShownBCV', 'ByChapter2' )
                BBB, intC, intV = newVerseKey.getBBB(), newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
                self.bookTextBefore = self.bookTextAfter = ''
                for thisC in range( 0, self.getNumChapters( BBB ) + 1 ):
                    try: numVerses = self.getNumVerses( BBB, thisC )
                    except KeyError: numVerses = 0
                    for thisV in range( 0, numVerses + 1 ):
                        thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
                        thisVerseData = self.getCachedVerseData( thisVerseKey )
                        if thisC < intC: self.bookTextBefore += thisVerseData if thisVerseData else ''
                        elif thisC > intC: self.bookTextAfter += thisVerseData if thisVerseData else ''
                        else:
                            self.displayAppendVerse( startingFlag, thisVerseKey, thisVerseData,
                                                currentVerse=thisC==intC and thisV==intV )
                            startingFlag = False

            else:
                logging.critical( exp("USFMEditWindow.updateShownBCV: Bad context view mode {}").format( self._contextViewMode ) )
                if BibleOrgSysGlobals.debugFlag: halt # Unknown context view mode

        self.textBox.highlightAllPatterns( self.patternsToHighlight )

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( tk.FALSE ) # clear modified flag
        self.loading = False # Turns onTextChange notifications back on
        self.lastCVMark = None

        # Make sure we can see what we're supposed to be looking at
        desiredMark = 'C{}V{}'.format( newVerseKey.getChapterNumber(), newVerseKey.getVerseNumber() )
        try: self.textBox.see( desiredMark )
        except tk.TclError: print( exp("USFMEditWindow.updateShownBCV couldn't find {} mark {!r}").format( newVerseKey.getBBB(), desiredMark ) )
        self.lastCVMark = desiredMark

        # Put the cursor back where it was (if necessary)
        self.loading = True # Turns off USFMEditWindow onTextChange notifications for now
        self.textBox.mark_set( tk.INSERT, savedCursorPosition )
        self.loading = False # Turns onTextChange notifications back on

        self.refreshTitle()
        if self._showStatusBarVar.get(): self.setReadyStatus()
    # end of USFMEditWindow.updateShownBCV


    def getEntireText( self ):
        """
        Gets the displayed text and adds it to the surrounding text.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("USFMEditWindow.getEntireText()") )

        # Get the text from the edit box and clean it up
        editBoxText = self.getAllText()

        # Add the stuff that wasn't displayed before and after the currently displayed verses
        entireText = self.bookTextBefore + editBoxText + self.bookTextAfter
        return entireText
    # end of USFMEditWindow.getEntireText


    def doBibleReplace( self, event=None ):
        """
        """
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'USFMEditWindow doBibleReplace' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doBibleReplace( {} )").format( event ) )

        if self.internalBible is None:
            logging.critical( _("No Bible to search") )
            return
        #print( "intBib", self.internalBible )

        self.BibleReplaceOptionsDict['currentBCV'] = self.currentVerseKey.getBCV()
        gBRTD = GetBibleReplaceTextDialog( self, self.parentApp, self.internalBible, self.BibleReplaceOptionsDict, title=_('Replace in Bible') )
        if BibleOrgSysGlobals.debugFlag: print( "gBRTDResult", repr(gBRTD.result) )
        if gBRTD.result:
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBRTD.result, dict )
            self.BibleReplaceOptionsDict = gBRTD.result # Update our search options dictionary
            self.parentApp.setWaitStatus( _("Searching/Replacing…") )
            #self.textBox.update()
            #self.textBox.focus()
            #self.lastReplace = key
            self.parentApp.logUsage( ProgName, debuggingThisModule, ' doBibleReplace {}'.format( self.BibleReplaceOptionsDict ) )
            #self._prepareInternalBible() # Make sure that all books are loaded
            self.doSave() # Make sure that any saves are made to disk
            # We load and search/replace the actual text files
            self.BibleReplaceOptionsDict, resultSummaryDict = searchReplaceText( self.internalBible, self.BibleReplaceOptionsDict, self.searchReplaceCallback )
            #print( "Got searchReplaceResults", resultSummaryDict )
            if 'hadRegexError' in resultSummaryDict and resultSummaryDict['hadRegexError']:
                errorBeep()
                showerror( self, APP_NAME, _("Regex error with {!r} or {!r}") \
                    .format( self.BibleReplaceOptionsDict['searchText'], self.BibleReplaceOptionsDict['replaceText'] ) )
            elif resultSummaryDict['numFinds'] == 0:
                errorBeep()
                key = self.BibleReplaceOptionsDict['searchText']
                showerror( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:18]+'…') ) )
            else:
                self.checkForDiskChanges( autoloadText=True )
                if len(resultSummaryDict['replacedBookList']) == 1:
                    showinfo( self, APP_NAME, _("Made {} replacements in {}").format( resultSummaryDict['numReplaces'], resultSummaryDict['replacedBookList'][0] ) )
                elif resultSummaryDict['numReplaces'] == 0:
                    showinfo( self, APP_NAME, _("No replacements made") )
                else: # more than one book
                    showinfo( self, APP_NAME, _("Made {} replacements in {} books").format( resultSummaryDict['numReplaces'], len(resultSummaryDict['replacedBookList']) ) )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doBibleReplace


    def searchReplaceCallback( self, ref, contextBefore, ourSearchText, contextAfter, willBeText, haveUndosFlag ):
        """
        Asks the user if they want to do the replace.

        Returns a single UPPERCASE character
            'N' (no), 'Y' (yes), 'A' (all), or 'S' (stop).
        """
        rcd = ReplaceConfirmDialog( self, self.parentApp, ref, contextBefore, ourSearchText, contextAfter, willBeText, haveUndosFlag, _("Replace {!r}?").format( ourSearchText ) )
        if rcd.result is None: rcd.result = 'N' # ESC pressed
        assert rcd.result in 'YNASU'
        return rcd.result
    # end of searchReplaceCallback


    def doSave( self, event=None ):
        """
        Called if the user requests a save from the GUI.

        Same as TextEditWindow.doSave except
            has a bit more housekeeping to do
        plus we always save with Windows newline endings.
        """

        logging.debug( exp("USFMEditWindow.doSave( {} )").format( event ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.doSave( {} )").format( event ) )

        if self.modified():
            if self.folderPath and self.filename:
                filepath = os.path.join( self.folderPath, self.filename )
                self.bookText = self.getEntireText()
                print( "Saving {} with {} encoding".format( filepath, self.internalBible.encoding ) )
                logging.debug( "Saving {} with {} encoding".format( filepath, self.internalBible.encoding ) )
                with open( filepath, mode='wt', encoding=self.internalBible.encoding, newline='\r\n' ) as theFile:
                    theFile.write( self.bookText )
                self.rememberFileTimeAndSize()
                BBB = self.currentVerseKey.getBBB()
                self.internalBible.bookNeedsReloading[BBB] = True
                self.textBox.edit_modified( tk.FALSE ) # clear Tkinter modified flag
                self.bookTextModified = False
                #self.internalBible.unloadBooks() # coz they're now out of date
                #self.internalBible.reloadBook( self.currentVerseKey.getBBB() ) # coz it's now out of date -- what? why?
                self.cacheBook( BBB ) # Wasted if we're closing the window/program, but important if we're continuing to edit
                self.refreshTitle()
                logChangedFile( self.parentApp.currentUserName, self.parentApp.loggingFolderPath, self.projectName, BBB, self.bookText )
            else: self.doSaveAs()
    # end of USFMEditWindow.doSave


    def startReferenceMode( self ):
        """
        Called from the GUI to duplicate this window into Group B,
            and then link A->B to show OT references from the NT (etc.)
        """
        logging.info( exp("USFMEditWindow.startReferenceMode()") )
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'USFMEditWindow.startReferenceMode' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.startReferenceMode()") )

        if self._groupCode != BIBLE_GROUP_CODES[0]: # Not in first/default BCV group
            ynd = YesNoDialog( self, _('You are in group {}. Ok to change to group {}?').format( self._groupCode, BIBLE_GROUP_CODES[0] ), title=_('Continue?') )
            #print( "yndResult", repr(ynd.result) )
            if ynd.result != True: return
            self.setWindowGroup( BIBLE_GROUP_CODES[0] )
        assert self._groupCode == BIBLE_GROUP_CODES[0] # In first/default BCV group
        uEW = USFMEditWindow( self.parentApp, self.internalBible, editMode=self.editMode )
        #if windowGeometry: uEW.geometry( windowGeometry )
        uEW.windowType = self.windowType # override the default
        uEW.moduleID = self.moduleID
        uEW.setFolderPath( self.folderPath )
        uEW.settings = self.settings
        #uEW.settings.loadUSFMMetadataInto( uB )
        uEW.setWindowGroup( BIBLE_GROUP_CODES[1] )
        uEW.BCVUpdateType = 'ReferenceMode'
        uEW.updateShownBCV( mapReferenceVerseKey( self.currentVerseKey ) )
        self.parentApp.childWindows.append( uEW )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openBiblelatorReferenceBibleEditWindow" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.startReferenceMode


    def startParallelMode( self ):
        """
        Called from the GUI to duplicate this window into Groups BCD,
            and then link A->BCD to show synoptic gospel parallels (etc.)
        """
        logging.info( exp("USFMEditWindow.startParallelMode()") )
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'USFMEditWindow.startParallelMode' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.startParallelMode()") )

        if self._groupCode != BIBLE_GROUP_CODES[0]: # Not in first/default BCV group
            ynd = YesNoDialog( self, _('You are in group {}. Ok to change to group {}?').format( self._groupCode, BIBLE_GROUP_CODES[0] ), title=_('Continue?') )
            #print( "yndResult", repr(ynd.result) )
            if ynd.result != True: return
            self.setWindowGroup( BIBLE_GROUP_CODES[0] )
        assert self._groupCode == BIBLE_GROUP_CODES[0] # In first/default BCV group
        for j in range( 1, len(BIBLE_GROUP_CODES) ):
            uEW = USFMEditWindow( self.parentApp, self.internalBible, editMode=self.editMode )
            #if windowGeometry: uEW.geometry( windowGeometry )
            uEW.windowType = self.windowType # override the default
            uEW.moduleID = self.moduleID
            uEW.setFolderPath( self.folderPath )
            uEW.settings = self.settings
            #uEW.settings.loadUSFMMetadataInto( uB )
            uEW.setWindowGroup( BIBLE_GROUP_CODES[j] )
            uEW.BCVUpdateType = 'ParallelMode'
            uEW.updateShownBCV( mapParallelVerseKey( BIBLE_GROUP_CODES[j], self.currentVerseKey ) )
            self.parentApp.childWindows.append( uEW )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openBiblelatorParallelBibleUSFMEditWindow" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.startParallelMode


    def startReferencesMode( self ):
        """
        Called from the GUI to duplicate this window into Group B,
            and then link A->B to show OT references from the NT (etc.)
        """
        logging.info( exp("USFMEditWindow.startReferencesMode()") )
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'USFMEditWindow.startReferencesMode' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("USFMEditWindow.startReferencesMode()") )

        if self._groupCode != BIBLE_GROUP_CODES[0]: # Not in first/default BCV group
            ynd = YesNoDialog( self, _('You are in group {}. Ok to change to group {}?').format( self._groupCode, BIBLE_GROUP_CODES[0] ), title=_('Continue?') )
            #print( "yndResult", repr(ynd.result) )
            if ynd.result != True: return
            self.setWindowGroup( BIBLE_GROUP_CODES[0] )
        assert self._groupCode == BIBLE_GROUP_CODES[0] # In first/default BCV group
        BRCW = BibleReferenceCollectionWindow( self.parentApp, self.internalBible )
        #if windowGeometry: uEW.geometry( windowGeometry )
        #BRCW.windowType = self.windowType # override the default
        BRCW.moduleID = self.moduleID
        BRCW.setFolderPath( self.folderPath )
        BRCW.settings = self.settings
        #BRCW.settings.loadUSFMMetadataInto( uB )
        BRCW.setWindowGroup( BIBLE_GROUP_CODES[0] ) # Stays the same as the source window!
        #BRCW.BCVUpdateType = 'ReferencesMode' # Leave as default
        BRCW.updateShownBCV( self.currentVerseKey )
        self.parentApp.childWindows.append( BRCW )
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished openBiblelatorReferencesBibleWindow" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.startReferencesMode


    # WHY IS THIS IN HERE ???
    def doViewSettings( self ):
        """
        Open a pop-up text window with the current settings displayed.
        """
        logging.debug( exp("doViewSettings()") )
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'USFMEditWindow.doViewSettings' )
        if BibleOrgSysGlobals.debugFlag:
            print( exp("doViewSettings()") )
            self.parentApp.setDebugText( "doViewSettings…" )

        tEW = TextEditWindow( self.parentApp )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setFilepath( self.settings.settingsFilepath ) \
        or not tEW.loadText():
            tEW.closeChildWindow()
            showerror( self, APP_NAME, _("Sorry, unable to open settings file") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed doViewSettings" )
        else:
            self.parentApp.childWindows.append( tEW )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Finished doViewSettings" )
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doViewSettings


    # WHY IS THIS IN HERE ???
    def doViewLog( self ):
        """
        Open a pop-up text window with the current log displayed.
        """
        logging.debug( exp("doViewLog()") )
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule: print( exp("doViewLog()") )
            self.parentApp.setDebugText( "doViewLog…" )

        tEW = TextEditWindow( self.parentApp )
        #if windowGeometry: tEW.geometry( windowGeometry )
        if not tEW.setFilepath( getChangeLogFilepath( self.parentApp.loggingFolderPath, self.projectName ) ) \
        or not tEW.loadText():
            tEW.closeChildWindow()
            showerror( self, APP_NAME, _("Sorry, unable to open log file") )
            if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Failed doViewLog" )
        else:
            self.parentApp.childWindows.append( tEW )
            #if BibleOrgSysGlobals.debugFlag: self.setDebugText( "Finished doViewLog" ) # Don't do this -- adds to the log immediately
        self.parentApp.setReadyStatus()
    # end of USFMEditWindow.doViewLog


    #def xxcloseEditor( self ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("USFMEditWindow.closeEditor()") )
        #if self.modified():
            #pass # refuse to close yet (temp.........)
        #else: self.closeChildWindow()
    ## end of USFMEditWindow.closeEditor
# end of USFMEditWindow class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo…") )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    uEW = USFMEditWindow( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of USFMEditWindow.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    import sys
    if 'win' in sys.platform: # Convert stdout so we don't get zillions of UnicodeEncodeErrors
        from io import TextIOWrapper
        sys.stdout = TextIOWrapper( sys.stdout.detach(), sys.stdout.encoding, 'namereplace' if sys.version_info >= (3,5) else 'backslashreplace' )

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", tk.TclVersion )
        print( "TkVersion is", tk.TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of USFMEditWindow.py
