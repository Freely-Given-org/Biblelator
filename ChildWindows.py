#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ChildWindows.py
#   Last modified: 2014-11-02 (also update ProgVersion below)
#
# Base of Bible and lexicon resource windows for Biblelator Bible display/editing
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
Base windows to allow display and manipulation of
    various Bible and lexicon, etc. child windows.
"""

ShortProgName = "ChildWindows"
ProgName = "Biblelator Child Windows"
ProgVersion = "0.21"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )

debuggingThisModule = True


import sys, logging
from gettext import gettext as _

import tkinter as tk
from tkinter.messagebox import showerror, showinfo
from tkinter.simpledialog import askstring, askinteger
from tkinter.ttk import Scrollbar

# Biblelator imports
from BiblelatorGlobals import APP_NAME, START, \
                             MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE
from BiblelatorHelpers import errorBeep

# BibleOrgSys imports
sourceFolder = "../BibleOrgSys/"
sys.path.append( sourceFolder )
import BibleOrgSysGlobals
from BibleStylesheets import DEFAULT_FONTNAME



def t( messageString ):
    """
    Prepends the module name to a error or warning message string
        if we are in debug mode.
    Returns the new string.
    """
    try: nameBit, errorBit = messageString.split( ': ', 1 )
    except ValueError: nameBit, errorBit = '', messageString
    if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit, _(errorBit) )



class HTMLText( tk.Text ):
    """
    A custom Text widget which understands and displays simple HTML.

    It currently accepts:
        heading tags:           h1,h2,h3
        paragraph tags:         p, li
        formatting tags:        span
        hard-formatting tags:   i, b, em

    For the styling, class names are appended to the tag names following a hyphen,
        e.g., <span class="Word"> would give an internal style of "spanWord".
    """
    def __init__( self, *args, **kwargs ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("HTMLText.__init__( {}, {} )").format( args, kwargs ) )
        tk.Text.__init__( self, *args, **kwargs ) # initialise the base class
        standardFont = DEFAULT_FONTNAME + ' 12'
        self.styleDict = { # earliest entries have the highest priority
            'i': { 'font':standardFont+' italic' },
            'b': { 'font':standardFont+' bold' },
            'em': { 'font':standardFont+' bold' },
            'p_i': { 'font':standardFont+' italic' },
            'p_b': { 'font':standardFont+' bold' },
            'p_em': { 'font':standardFont+' bold' },

            'span': { 'foreground':'red', 'font':standardFont },
            'li': { 'lmargin1':4, 'lmargin2':4, 'background':'pink', 'font':standardFont },

            'p': { 'background':'pink', 'font':standardFont, 'spacing1':'1' },
            'p_span': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanGreekWord': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanHebrewWord': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanKJVUsage': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanStatus': { 'foreground':'red', 'background':'pink', 'font':standardFont },

            'p_spanSource': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanSource_b': { 'foreground':'red', 'background':'pink', 'font':standardFont+' bold' },
            'p_spanSource_span': { 'foreground':'red', 'background':'pink', 'font':standardFont, 'spacing1':'1' },
            'p_spanSource_spanDef': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanSource_spanHebrew': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanSource_spanStrongs': { 'foreground':'red', 'background':'pink', 'font':standardFont },

            'p_spanMeaning': { 'foreground':'red', 'background':'pink', 'font':standardFont },
            'p_spanMeaning_b': { 'foreground':'red', 'background':'pink', 'font':standardFont+' bold' },
            'p_spanMeaning_spanDef': { 'foreground':'red', 'background':'pink', 'font':standardFont },

            'p_span_b': { 'foreground':'red', 'background':'pink', 'font':standardFont+' bold' },
            'p_spanKJVUsage_b': { 'foreground':'red', 'background':'pink', 'font':standardFont+' bold' },

            'h1': { 'justify':tk.CENTER, 'foreground':'blue', 'font':DEFAULT_FONTNAME+' 15', 'spacing1':'1', 'spacing3':'0.5' },
            'h2': { 'justify':tk.CENTER, 'foreground':'green', 'font':DEFAULT_FONTNAME+' 14', 'spacing1':'0.8', 'spacing3':'0.3' },
            'h3': { 'justify':tk.CENTER, 'foreground':'orange', 'font':DEFAULT_FONTNAME+' 13', 'spacing1':'0.5', 'spacing3':'0.2' },
            }
        for tag,styleEntry in self.styleDict.items():
            self.tag_configure( tag, **styleEntry ) # Create the style
        #background='yellow', font='helvetica 14 bold', relief=tk.RAISED
        #"background", "bgstipple", "borderwidth", "elide", "fgstipple",
        #"font", "foreground", "justify", "lmargin1", "lmargin2", "offset",
        #"overstrike", "relief", "rmargin", "spacing1", "spacing2", "spacing3",
        #"tabs", "tabstyle", "underline", and "wrap".
    # end of HTMLText.__init__


    def insert( self, point, iText ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            try: print( t("HTMLText.insert( {}, {} )").format( repr(point), repr(iText) ) )
            except UnicodeEncodeError: print( t("HTMLText.insert( {}, {} )").format( repr(point), len(iText) ) )
        if point != tk.END:
            logging.critical( t("HTMLText.insert doesn't know how to insert at {}").format( repr(point) ) )
            tk.Text.insert( self, point, iText )
            return
        remainingText = iText.replace( '\n', ' ' )
        remainingText = remainingText.replace( '<br>','\n' ).replace( '<br />','\n' ).replace( '<br/>','\n' )
        while '  ' in remainingText: remainingText = remainingText.replace( '  ', ' ' )
        currentFormatTags, currentHTMLTags = [], []
        #first = True
        while remainingText:
            #try: print( "  Remaining: {}".format( repr(remainingText) ) )
            #except UnicodeEncodeError: print( "  Remaining: {}".format( len(remainingText) ) )
            ix = remainingText.find( '<' )
            if ix == -1: # none found
                tk.Text.insert( self, point, remainingText, currentFormatTags )
                remainingText = ""
            else: # presumably we have found the start of an HTML tag
                if ix > 0: # this is where text is actually inserted into the box
                    combinedFormats = '_'.join( currentFormatTags )
                    if combinedFormats not in self.styleDict:
                        print( "  Missing format:", repr(combinedFormats), "cFT", currentFormatTags, "cHT", currentHTMLTags )
                        #try: print( "   on", repr(remainingText[:ix]) )
                        #except UnicodeEncodeError: pass
                    insertText = remainingText[:ix]
                    #print( "  Got format:", repr(combinedFormats), "cFT", currentFormatTags, "cHT", currentHTMLTags, repr(insertText) )
                    if 'Hebrew' in combinedFormats:
                        #print( "Reversing", repr(insertText ) )
                        insertText = insertText[::-1] # Reverse the string (a horrible way to approximate RTL)
                    tk.Text.insert( self, point, insertText, combinedFormats )
                    #first = False
                    remainingText = remainingText[ix:]
                #try: print( "  tag", repr(remainingText[:5]) )
                #except UnicodeEncodeError: print( "  tag" )
                ixEnd = remainingText.find( '>' )
                ixNext = remainingText.find( '<', 1 )
                #print( "ixEnd", ixEnd, "ixNext", ixNext )
                if ixEnd == -1 \
                or (ixEnd!=-1 and ixNext!=-1 and ixEnd>ixNext): # no tag close or wrong tag closed
                    logging.critical( t("HTMLText.insert: Missing close bracket") )
                    tk.Text.insert( self, point, remainingText, currentFormatTags )
                    remainingText = ""
                    break
                # There's a close marker -- check it's our one
                fullHTMLTag = remainingText[1:ixEnd] # but without the < >
                remainingText = remainingText[ixEnd+1:]
                #if remainingText:
                    #try: print( "after marker", remainingText[0] )
                    #except UnicodeEncodeError: pass
                if not fullHTMLTag:
                    logging.critical( t("HTMLText.insert: Unexpected empty HTML tags") )
                    continue
                selfClosing = fullHTMLTag[-1] == '/'
                if selfClosing:
                    fullHTMLTag = fullHTML[:-1]
                #try: print( "fullHTMLTag", repr(fullHTMLTag), "self-closing" if selfClosing else "" )
                #except UnicodeEncodeError: pass
                fullHTMLTagBits = fullHTMLTag.split()
                HTMLTag = fullHTMLTagBits[0]
                #try: print( "  bits", fullHTMLTagBits, repr(HTMLTag) )
                #except UnicodeEncodeError: pass
                if HTMLTag and HTMLTag[0] == '/': # it's a close tag
                    assert( len(fullHTMLTagBits) == 1 ) # shouldn't have any attributes on a closing tag
                    assert( not selfClosing )
                    HTMLTag = HTMLTag[1:]
                    #print( t("Got HTML {} close tag").format( repr(HTMLTag) ) )
                    #print( "cHT", currentHTMLTags )
                    if currentHTMLTags and HTMLTag == currentHTMLTags[-1]: # all good
                        currentHTMLTags.pop() # Drop it
                        currentFormatTags.pop()
                    elif currentHTMLTags:
                        logging.critical( t("HTMLText.insert: Expected to close {} but got {} instead").format( repr(currentHTMLTags[-1]), repr(HTMLTag) ) )
                    else:
                        logging.critical( t("HTMLText.insert: Unexpected HTML close {} close marker").format( repr(HTMLTag) ) )
                else: # it's not a close tag
                    if HTMLTag not in ('h1','h2','h3','p','li','span','i','b','em',):
                        logging.critical( t("HTMLText doesn't recognise or handle {} as an HTML tag").format( repr(HTMLTag) ) )
                        #currentHTMLTags.append( HTMLTag ) # remember it anyway in case it's closed later
                        continue
                    if 1 or self.edit_modified(): # This isn't the first text then
                        if HTMLTag in ('h1','h2','h3','p','li',):
                            tk.Text.insert( self, point, '\n' )
                        #elif HTMLTag in ('li',):
                            #tk.Text.insert( self, point, '\n' )
                    formatTag = HTMLTag
                    if len(fullHTMLTagBits)>1: # our HTML tag has some additional attributes
                        #print( "Looking for attributes" )
                        for bit in fullHTMLTagBits[1:]:
                            #try: print( "  bit", repr(bit) )
                            #except UnicodeEncodeError: pass
                            if bit.startswith('class="') and bit[-1]=='"':
                                formatTag += bit[7:-1] # create a tag like 'spanWord' or 'pVerse'
                            else: logging.warning( "Ignoring {} attribute on {} tag".format( bit, HTMLTag ) )
                    if not selfClosing:
                        currentHTMLTags.append( HTMLTag )
                        currentFormatTags.append( formatTag )
        if currentHTMLTags:
            logging.critical( t("HTMLText.insert: Left-over HTML tags: {}").format( currentHTMLTags ) )
        if currentFormatTags:
            logging.critical( t("HTMLText.insert: Left-over format tags: {}").format( currentFormatTags ) )
    # end of HTMLText.insert
# end of HTMLText class



class ChildWindow( tk.Toplevel ):
    """
    """
    def __init__( self, parentApp, genericWindowType ):
        """
        The genericWindowType is set here,
            but the more specific winType is set later by the subclass.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("ChildWindow.__init__( {} {} )").format( parentApp, repr(genericWindowType) ) )
            assert( parentApp )
            assert( genericWindowType in ('BibleResource','LexiconResource','TextEditor','BibleEditor') )
        self.parentApp, self.genericWindowType = parentApp, genericWindowType
        tk.Toplevel.__init__( self, self.parentApp )
        self.protocol( "WM_DELETE_WINDOW", self.closeChildWindow )
        self.minimumXSize, self.minimumYSize = MINIMUM_RESOURCE_X_SIZE, MINIMUM_RESOURCE_Y_SIZE
        self.minsize( self.minimumXSize, self.minimumYSize )

        self.createMenuBar()
        self.createToolBar()
        self.createContextMenu()

        self.myKeyboardBindings = []

        # Create a scroll bar to fill the right-hand side of the window
        self.vScrollbar = Scrollbar( self )
        self.vScrollbar.pack( side=tk.RIGHT, fill=tk.Y )

        #if 'textBox' in dir(self): # we have one already -- presumably a specialised one
            #halt # We have one already
        #else: # let's make one

        self.textBox = tk.Text( self, yscrollcommand=self.vScrollbar.set, state=tk.DISABLED )
        self.textBox['wrap'] = 'word'
        self.textBox.pack( expand=tk.YES, fill=tk.BOTH )
        self.vScrollbar.config( command=self.textBox.yview ) # link the scrollbar to the text box
        self.createStandardKeyboardBindings()
        self.textBox.bind( "<Button-1>", self.setFocus ) # So disabled text box can still do select and copy functions

        # Options for find, etc.
        self.optionsDict = {}
        self.optionsDict['caseinsens'] = True

        self.refreshTitle() # Must be in superclass
    # end of ChildWindow.__init__


    def setFocus( self, event ):
        '''Explicitly set focus, so user can select and copy text'''
        self.textBox.focus_set()


    def createMenuBar( self ):
        if BibleOrgSysGlobals.debugFlag:
            print( t("This 'createMenuBar' method MUST be overridden!") )
            halt


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        self.contextMenu = tk.Menu( self, tearoff=0 )
        self.contextMenu.add_command( label="Copy", underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict['Copy'][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Select all", underline=7, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict['SelectAll'][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Find...", underline=0, command=self.doFind, accelerator=self.parentApp.keyBindingDict['Find'][0] )
        self.contextMenu.add_separator()
        self.contextMenu.add_command( label="Close", underline=1, command=self.doClose, accelerator=self.parentApp.keyBindingDict['Close'][0] )

        self.bind( "<Button-3>", self.showContextMenu ) # right-click
        #self.pack()
    # end of ChildWindow.createContextMenu


    def showContextMenu( self, event ):
        self.contextMenu.post( event.x_root, event.y_root )
    # end of ChildWindow.showContextMenu


    def createStandardKeyboardBindings( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.createStandardKeyboardBindings()") )
        for name,command in ( ('SelectAll',self.doSelectAll), ('Copy',self.doCopy),
                             ('Find',self.doFind), ('Refind',self.doRefind),
                             ('Help',self.doHelp), ('Info',self.doShowInfo), ('About',self.doAbout),
                             ('Close',self.doClose) ):
            if name in self.parentApp.keyBindingDict:
                for keycode in self.parentApp.keyBindingDict[name][1:]:
                    #print( "Bind {} for {}".format( repr(keycode), repr(name) ) )
                    self.textBox.bind( keycode, command )
                self.myKeyboardBindings.append( (name,self.parentApp.keyBindingDict[name][0],) )
            else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
        #self.textBox.bind('<Control-a>', self.doSelectAll ); self.textBox.bind('<Control-A>', self.doSelectAll )
        #self.textBox.bind('<Control-c>', self.doCopy ); self.textBox.bind('<Control-C>', self.doCopy )
        #self.textBox.bind('<Control-f>', self.doFind ); self.textBox.bind('<Control-F>', self.doFind )
        #self.textBox.bind('<Control-g>', self.doRefind ); self.textBox.bind('<Control-G>', self.doRefind )
        #self.textBox.bind('<F1>', self.doHelp )
        #self.textBox.bind('<F3>', self.doRefind )
        #self.textBox.bind('<Control-F4>', self.doClose )
        #self.textBox.bind('<F11>', self.doShowInfo )
        #self.textBox.bind('<F12>', self.doAbout )
    # end of ChildWindow.createStandardKeyboardBindings()


    def createToolBar( self ):
        """
        Designed to be overridden.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("This 'createToolBar' method can be overridden!") )
    # end of ChildWindow.createToolBar


    def notWrittenYet( self ):
        errorBeep()
        showerror( _("Not implemented"), _("Not yet available, sorry") )
    # end of ChildWindow.notWrittenYet


    def doCopy( self, event=None ):
        """
        Copy the selected text onto the clipboard.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.doCopy()") )
        if not self.textBox.tag_ranges( tk.SEL ):       # save in cross-app clipboard
            errorBeep()
            showerror( APP_NAME, 'No text selected')
        else:
            copyText = self.textBox.get( tk.SEL_FIRST, tk.SEL_LAST)
            print( "  copied text", repr(copyText) )
            self.clipboard_clear()
            self.clipboard_append( copyText )
    # end of ChildWindow.doCopy


    def doSelectAll( self, event=None ):
        """
        Select all the text in the text box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.doSelectAll()") )
        self.textBox.tag_add( tk.SEL, START, tk.END+'-1c' )   # select entire text
        self.textBox.mark_set( tk.INSERT, START )          # move insert point to top
        self.textBox.see( tk.INSERT )                      # scroll to top
    # end of ChildWindow.doSelectAll


    def doGotoLine( self, event=None, forceline=None ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( t("TextEditWindow.doGotoLine()") )
        line = forceline or askinteger( APP_NAME, _("Enter line number") )
        self.textBox.update()
        self.textBox.focus()
        if line is not None:
            maxindex = self.textBox.index( tk.END+'-1c' )
            maxline  = int( maxindex.split('.')[0] )
            if line > 0 and line <= maxline:
                self.textBox.mark_set( tk.INSERT, '{}.0'.format(line) ) # goto line
                self.textBox.tag_remove( tk.SEL, START, tk.END )          # delete selects
                self.textBox.tag_add( tk.SEL, tk.INSERT, 'insert+1l' )  # select line
                self.textBox.see( tk.INSERT )                          # scroll to line
            else:
                errorBeep()
                showerror( APP_NAME, _("No such line number") )
    # end of ChildWindow.doGotoLine


    def doFind( self, event=None, lastkey=None ):
        key = lastkey or askstring( APP_NAME, _("Enter search string") )
        self.textBox.update()
        self.textBox.focus()
        self.lastfind = key
        if key:
            nocase = self.optionsDict['caseinsens']
            where = self.textBox.search( key, tk.INSERT, tk.END, nocase=nocase )
            if not where:                                          # don't wrap
                errorBeep()
                showerror( APP_NAME, 'String not found' )
            else:
                pastkey = where + '+%dc' % len(key)           # index past key
                self.textBox.tag_remove( tk.SEL, START, tk.END )         # remove any sel
                self.textBox.tag_add( tk.SEL, where, pastkey )        # select key
                self.textBox.mark_set( tk.INSERT, pastkey )           # for next find
                self.textBox.see( where )                          # scroll display
    # end of ChildWindow.doFind


    def doRefind( self, event=None ):
        self.doFind( self.lastfind)
    # end of ChildWindow.doRefind


    def doShowInfo( self, event=None ):
        """
        pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        text  = self.getAllText()
        bytes = len( text )             # words uses a simple guess:
        lines = len( text.split('\n') ) # any separated by whitespace
        words = len( text.split() )     # 3.x: bytes is really chars
        index = self.textBox.index( tk.INSERT ) # str is unicode code points
        where = tuple( index.split('.') )
        showinfo( APP_NAME+' Information',
                 'Current location:\n\n' +
                 'line:\t%s\ncolumn:\t%s\n\n' % where +
                 'File text statistics:\n\n' +
                 'chars:\t{}\nlines:\t{}\nwords:\t{}\n'.format( bytes, lines, words) )
    # end of ChildWindow.doShowInfo


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    def clearText( self ): # Leaves in normal state
        self.textBox['state'] = tk.NORMAL
        self.textBox.delete( START, tk.END )
    # end of ResourceFrame.updateText


    def isEmpty( self ):
        return not self.getAllText()
    # end of ChildWindow.modified


    def modified( self ):
        return self.textBox.edit_modified()
    # end of ChildWindow.modified


    def getAllText( self ):
        """ Returns all the text as a string. """
        return self.textBox.get( START, tk.END+'-1c' )
    # end of ChildWindow.modified


    def setAllText( self, newText ):
        """
        Sets the textBox (assumed to be enabled) to the given text
            then positions the insert cursor at the BEGINNING of the text.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        self.textBox['state'] = tk.NORMAL
        self.textBox.delete( START, tk.END ) # Delete everything that's existing
        self.textBox.insert( tk.END, newText )
        self.textBox.mark_set( tk.INSERT, START ) # move insert point to top
        self.textBox.see( tk.INSERT ) # scroll to top, insert is set

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( tk.FALSE ) # clear modified flag
    # end of ChildWindow.setAllText


    def doHelp( self, event=None ):
        from Help import HelpBox
        helpInfo = ProgNameVersion
        helpInfo += "\nHelp for {}".format( self.winType )
        helpInfo += "\n  Keyboard shortcuts:"
        for name,shortcut in self.myKeyboardBindings:
            helpInfo += "\n    {}\t{}".format( name, shortcut )
        hb = HelpBox( self, self.genericWindowType, helpInfo )
    # end of Application.doHelp


    def doAbout( self, event=None ):
        from About import AboutBox
        aboutInfo = ProgNameVersion
        aboutInfo += "\nInformation about {}".format( self.winType )
        ab = AboutBox( self, self.genericWindowType, aboutInfo )
    # end of Application.doAbout


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden.
        """
        self.closeChildWindow()
    # end of ChildWindow.doClose

    def closeChildWindow( self ):
        """
        Called to finally and irreversibly remove this window from our list and close it.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("ChildWindow.closeChildWindow()") )
        self.parentApp.childWindows.remove( self )
        self.destroy()
        if BibleOrgSysGlobals.debugFlag: self.parentApp.setDebugText( "Closed resource window" )
    # end of ChildWindow.closeChildWindow
# end of class ChildWindow



class ChildWindows( list ):
    """
    Just keeps a list of the resource (Toplevel) windows.
    """
    def __init__( self, ChildWindowsParent ):
        self.ChildWindowsParent = ChildWindowsParent
        list.__init__( self )


    def iconify( self ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("ChildWindows.iconify()") )
        for appWin in self:
            appWin.iconify()
    #end of ChildWindows.iconify


    def iconifyResources( self ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("ChildWindows.iconifyResources()") )
        for appWin in self:
            if 'Resource' in appWin.genericWindowType:
                appWin.iconify()
    #end of ChildWindows.iconifyResources


    def deiconify( self ):
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( t("ChildWindows.deiconify()") )
        for appWin in self:
            appWin.deiconify()
            appWin.lift( aboveThis=self.ChildWindowsParent )
    #end of ChildWindows.deiconify


    def updateThisBibleGroup( self, groupCode, newVerseKey ):
        """
        Called when we probably need to update some resource windows with a new Bible reference.
        """
        if BibleOrgSysGlobals.debugFlag: print( t("ChildWindows.updateThisBibleGroup( {}, {} )").format( groupCode, newVerseKey ) )
        for appWin in self:
            if 'Bible' in appWin.genericWindowType: # e.g., BibleResource, BibleEditor
                if appWin.groupCode == groupCode:
                    # The following line doesn't work coz it only updates ONE window
                    #self.ChildWindowsParent.after_idle( lambda: appWin.updateShownBCV( newVerseKey ) )
                    appWin.updateShownBCV( newVerseKey )
    # end of ChildWindows.updateThisBibleGroup


    def updateLexicons( self, newLexiconWord ):
        """
        Called when we probably need to update some resource windows with a new word.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( t("ChildWindows.updateLexicons( {} )").format( newLexiconWord ) )
        for appWin in self:
            if appWin.genericWindowType == 'LexiconResource':
                # The following line doesn't work coz it only updates ONE window
                #self.ChildWindowsParent.after_idle( lambda: appWin.updateLexiconWord( newLexiconWord ) )
                appWin.updateLexiconWord( newLexiconWord )
    # end of ChildWindows.updateLexicons
# end of ChildWindows class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( t("Running demo...") )
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
# end of ChildWindows.demo


if __name__ == '__main__':
    import multiprocessing

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        from tkinter import TclVersion, TkVersion
        from tkinter import tix
        print( "TclVersion is", TclVersion )
        print( "TkVersion is", TkVersion )
        print( "tix TclVersion is", tix.TclVersion )
        print( "tix TkVersion is", tix.TkVersion )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of ChildWindows.py