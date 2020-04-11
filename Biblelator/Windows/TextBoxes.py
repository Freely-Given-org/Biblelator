#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# TextBoxes.py
#
# Base of various textboxes for use as widgets and base classes in various windows.
#
# Copyright (C) 2013-2019 Robert Hunt
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
Base widgets to allow display and manipulation of
    various Bible and lexicon, etc. child windows.


    NOTE: These three classes are empty, but could easily be used to implement system wide
            special-character input, display fonts, etc.
    class BEntry( Entry ) -- used in many dialogs, etc. including CustomEntry
    class BCombobox( Combobox ) -- used in many places including CustomCombobox
    class BText( tk.Text ) -- use in HTMLTextBox and CustomText


    class HTMLTextBox( BText ) -- used in HTMLWindow and BibleLexiconResourceWindow
        __init__( self, *args, **kwargs )
        insert( self, point, iText )
        _getURL( self, event )
        openHyperlink( self, event )
        overHyperlink( self, event )
        leaveHyperlink( self, event )


    class CallbackAddon() -- used in CustomEntry, CustomCombobox, CustomText below
        __init__( self )
        _callback( self, result, *args )
        setTextChangeCallback( self, callableFunction )
        onTextChange( self, result, *args )

    #class CustomEntry( CallbackAddon, BEntry ) -- unused
        #__init__( self, *args, **kwargs )

    #class CustomCombobox( CallbackAddon, BCombobox ) -- unused
        #__init__( self, *args, **kwargs )

    class CustomText( CallbackAddon, BText ) -- used in TextEditWindow
        __init__( self, *args, **kwargs )
        highlightPattern( self, pattern, styleTag, startAt=tkSTART, endAt=tk.END, regexpFlag=True )
        highlightAllPatterns( self, patternCollection )


    class ChildBoxAddon()
        __init__( self, parentApp )
        _createStandardKeyboardBinding( self, name, commandFunction )
        createStandardBoxKeyboardBindings( self )
        setFocus( self, event )
        doCopy( self, event=None )
        doSelectAll( self, event=None )
        doGotoWindowLine( self, event=None, forceline=None )
        doBoxFind( self, event=None, lastkey=None )
        doBoxRefind( self, event=None )
        doShowInfo( self, event=None )
        clearText( self ) # Leaves in normal state
        isEmpty( self )
        modified( self )
        getAllText( self )
        setAllText( self, newText )
        doShowMainWindow( self, event=None )
        doClose( self, event=None )

    class BibleBoxAddon() -- used in BibleReferenceBox, BibleResourceBox, BibleWindowAddon
                                and in HebrewInterlinearBibleBoxAddon below
        __init__( self, parentApp )
        _createStandardKeyboardBinding( self, name, commandFunction )
        createContextMenu( self )
        showContextMenu( self, event )
        displayAppendVerse( self, firstFlag, verseKey, verseContextData, lastFlag=True, currentVerseFlag=False, substituteTrailingSpaces=False, substituteMultipleSpaces=False )
        getBeforeAndAfterBibleData( self, newVerseKey )
        doBibleFind( self, event=None )
        doActualBibleFind( self, extendTo=None )
        _prepareInternalBible( self, bookCode=None, givenBible=None )


    class HebrewInterlinearBibleBoxAddon( BibleBoxAddon ) -- used in HebrewBibleResourceWindow
        __init__( self, parentWindow, numInterlinearLines )
        displayAppendVerse( self, firstFlag, verseKey, verseContextData, lastFlag=True, currentVerseFlag=False, substituteTrailingSpaces=False, substituteMultipleSpaces=False )
        doClose( self, event=None )
        #getBeforeAndAfterBibleData( self, newVerseKey )
        #doBibleFind( self, event=None )
        #doActualBibleFind( self, extendTo=None )
        #_prepareInternalBible( self, bookCode=None, givenBible=None )

    demo()
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2019-05-12' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorTextBoxes"
PROGRAM_NAME = "Biblelator specialised text widgets"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = True


import logging

import tkinter as tk
import tkinter.font as tkFont
from tkinter.ttk import Entry, Combobox
from tkinter.simpledialog import askstring, askinteger

# Biblelator imports
from Biblelator.BiblelatorGlobals import APP_NAME, tkSTART, DEFAULT, errorBeep, BIBLE_FORMAT_VIEW_MODES
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showInfo


# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
from BibleOrgSys.Internals.InternalBibleInternals import InternalBibleEntry
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Reference.BibleStylesheets import DEFAULT_FONTNAME, DEFAULT_FONTSIZE
from BibleOrgSys.OriginalLanguages.HebrewWLCBible import ORIGINAL_MORPHEME_BREAK_CHAR, OUR_MORPHEME_BREAK_CHAR



KNOWN_HTML_TAGS = ('!DOCTYPE','html','head','meta','link','title','body','div',
                   'h1','h2','h3','p','li','a','span','table','tr','td','i','b','em','small')
NON_FORMATTING_TAGS = 'html','head','body','div','table','tr','td', # Not sure about div yet…
HTML_REPLACEMENTS = ('&nbsp;',' '),('&lt;','<'),('&gt;','>'),('&amp;','&'),
TRAILING_SPACE_SUBSTITUTE = '⦻' # Must not normally occur in Bible text
MULTIPLE_SPACE_SUBSTITUTE = '⧦' # Must not normally occur in Bible text
DOUBLE_SPACE_SUBSTITUTE = MULTIPLE_SPACE_SUBSTITUTE + MULTIPLE_SPACE_SUBSTITUTE
CLEANUP_LAST_MULTIPLE_SPACE = MULTIPLE_SPACE_SUBSTITUTE + ' '
TRAILING_SPACE_LINE = ' \n'
TRAILING_SPACE_LINE_SUBSTITUTE = TRAILING_SPACE_SUBSTITUTE + '\n'
ALL_POSSIBLE_SPACE_CHARS = ' ' + TRAILING_SPACE_SUBSTITUTE + MULTIPLE_SPACE_SUBSTITUTE



class BEntry( Entry ):
    """
    A custom (ttk) Entry widget which can call a user function whenever the text changes.
        This enables autocorrect.

    BEntry stands for Biblelator Entry (widget).
    """
    #def __init__( self, *args, **kwargs ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "BEntry.__init__( {}, {} )".format( args, kwargs ) )
        #Entry.__init__( self, *args, **kwargs ) # initialise the base class
        #CallbackAddon.__init__( self ) # initialise the base class
    ## end of BEntry.__init__
    pass
# end of BEntry class

class BCombobox( Combobox ):
    """
    A custom (ttk) Combobox widget which can call a user function whenever the text changes.
        This enables autocorrect.

    BCombobox stands for Biblelator Combobox (widget).
    """
    #def __init__( self, *args, **kwargs ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "BCombobox.__init__( {}, {} )".format( args, kwargs ) )
        #Combobox.__init__( self, *args, **kwargs ) # initialise the base class
        #CallbackAddon.__init__( self ) # initialise the base class
    ## end of BCombobox.__init__
    pass
# end of BCombobox class

class BText( tk.Text ):
    """
    A custom Text widget with our own keyboard bindings/short-cuts.

    BText stands for Biblelator Text (box).
    """
    #def __init__(self, master, **kw):
        #"""
        #Initialise the text widget and then set our own keyboard bindings.
        #"""
        #tk.apply( tk.Text.__init__, (self, master), kw ) # Run the init of the base class

        ## Now set-up our "default" keyboard bindings
        #self.bind( … )
    pass
# end of BText class



class HTMLTextBox( BText ):
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
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "HTMLTextBox.__init__( {}, {} )".format( args, kwargs ) )
        BText.__init__( self, *args, **kwargs ) # initialise the base class

        standardFont = DEFAULT_FONTNAME + ' 12'
        smallFont = DEFAULT_FONTNAME + ' 10'
        self.styleDict = { # earliest entries have the highest priority
            'i': { 'font':standardFont+' italic' },
            'b': { 'font':standardFont+' bold' },
            'em': { 'font':standardFont+' bold' },
            'p_i': { 'font':standardFont+' italic' },
            'p_b': { 'font':standardFont+' bold' },
            'p_em': { 'font':standardFont+' bold' },

            'span': { 'foreground':'red', 'font':standardFont },
            'li': { 'lmargin1':4, 'lmargin2':4, 'background':'pink', 'font':standardFont },
            'a': { 'foreground':'blue', 'font':standardFont, 'underline':1 },

            'small_p': { 'background':'pink', 'font':smallFont, 'spacing1':'1' },
            'small_p_pGeneratedNotice': { 'justify':tk.CENTER, 'background':'green', 'font':smallFont, 'spacing1':'1' },

            'small_p_a': { 'foreground':'blue', 'font':smallFont, 'underline':1, 'spacing1':'1' },
            'small_p_b': { 'background':'pink', 'font':smallFont+' bold', 'spacing1':'1' },

            'p': { 'background':'pink', 'font':standardFont, 'spacing1':'1' },
            'pGeneratedNotice': { 'justify':tk.CENTER, 'background':'green', 'font':smallFont, 'spacing1':'1' },

            'p_a': { 'foreground':'blue', 'font':standardFont, 'underline':1, 'spacing1':'1' },
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

            #'td_a': { 'foreground':'blue', 'font':standardFont, 'underline':1 },
            #'h1_td_a': { 'foreground':'blue', 'font':standardFont, 'underline':1 },

            'h1': { 'justify':tk.CENTER, 'foreground':'blue', 'font':DEFAULT_FONTNAME+' 15', 'spacing1':'1', 'spacing3':'0.5' },
            'h1_a': { 'justify':tk.CENTER, 'foreground':'blue', 'font':DEFAULT_FONTNAME+' 15', 'spacing1':'1', 'spacing3':'0.5',  'underline':1 },
            'h1PageHeading': { 'justify':tk.CENTER, 'foreground':'blue', 'font':DEFAULT_FONTNAME+' 15', 'spacing1':'1', 'spacing3':'0.5' },
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

        aTags = ('a','p_a','small_p_a','h1_a')
        if debuggingThisModule:
            for tag in self.styleDict:
                if tag.endswith( '_a' ): assert tag in aTags
        for tag in aTags:
            assert tag in self.styleDict
            self.tag_bind( tag, '<Button-1>', self.openHyperlink )
            #self.tag_bind( tag, '<Enter>', self.overHyperlink )
            #self.tag_bind( tag, '<Leave>', self.leaveHyperlink )

        self._lastOverLink = None
    # end of HTMLTextBox.__init__


    def insert( self, point, iText ):
        """
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "HTMLTextBox.insert( {}, {} )".format( repr(point), repr(iText) ) )

        if point != tk.END:
            logging.critical( "HTMLTextBox.insert " + _("doesn't know how to insert at {}").format( repr(point) ) )
            BText.insert( self, point, iText )
            return

        # Fix whitespace in our text to how we want it
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
                BText.insert( self, point, remainingText, currentFormatTags ) # just insert all the remainingText
                remainingText = ""
            else: # presumably we have found the start of a new HTML tag
                if ix > 0: # this is where text is actually inserted into the box
                    insertText = remainingText[:ix]
                    if HTMLTag and HTMLTag == 'title':
                        pass # This is handled elsewhere
                    elif insertText: # it's not a title and not blank so we need to display this text
                        # Combine tag formats (but ignore consecutive identical tags e.g., p with a p
                        combinedFormats, lastTag, link = '', None, None
                        #print( "cFT", currentFormatTags )
                        for tag in currentFormatTags:
                            if tag.startswith( 'a=' ):
                                tag, link = 'a', tag[2:]
                                #print( "Got <a> link {}".format( repr(link) ) )
                            if tag != lastTag:
                                if combinedFormats: combinedFormats += '_'
                                combinedFormats += tag
                                lastTag = tag
                        #print( "combinedFormats", repr(combinedFormats) )
                        if combinedFormats and combinedFormats not in self.styleDict:
                            print( "  Missing format:", repr(combinedFormats), "cFT", currentFormatTags, "cHT", currentHTMLTags )
                            #try: print( "   on", repr(remainingText[:ix]) )
                            #except UnicodeEncodeError: pass
                        insertText = remainingText[:ix]
                        #print( "  Got format:", repr(combinedFormats), "cFT", currentFormatTags, "cHT", currentHTMLTags, repr(insertText) )
                        if 'Hebrew' in combinedFormats:
                            #print( "Reversing", repr(insertText ) )
                            insertText = insertText[::-1] # Reverse the string (a horrible way to approximate RTL)
                        for htmlChars, replacementChars in HTML_REPLACEMENTS:
                            insertText = insertText.replace( htmlChars, replacementChars )
                        #if link: print( "insertMarks", repr( (combinedFormats, 'href'+link,) if link else combinedFormats ) )
                        if link:
                            hypertag = 'href' + link
                            BText.insert( self, point, insertText, (combinedFormats, hypertag,) )
                            self.tag_bind( hypertag, '<Enter>', self.overHyperlink )
                            self.tag_bind( hypertag, '<Leave>', self.leaveHyperlink )
                        else: BText.insert( self, point, insertText, combinedFormats )
                        #first = False
                    remainingText = remainingText[ix:]
                #try: print( "  tag", repr(remainingText[:5]) )
                #except UnicodeEncodeError: print( "  tag" )
                ixEnd = remainingText.find( '>' )
                ixNext = remainingText.find( '<', 1 )
                #print( "ixEnd", ixEnd, "ixNext", ixNext )
                if ixEnd == -1 \
                or (ixEnd!=-1 and ixNext!=-1 and ixEnd>ixNext): # no tag close or wrong tag closed
                    logging.critical( "HTMLTextBox.insert: " + _("Missing close bracket") )
                    BText.insert( self, point, remainingText, currentFormatTags )
                    remainingText = ""
                    break
                # There's a close marker -- check it's our one
                fullHTMLTag = remainingText[1:ixEnd] # but without the < >
                remainingText = remainingText[ixEnd+1:]
                #if remainingText:
                    #try: print( "after marker", remainingText[0] )
                    #except UnicodeEncodeError: pass
                if not fullHTMLTag:
                    logging.critical( "HTMLTextBox.insert: " + _("Unexpected empty HTML tags") )
                    continue
                selfClosing = fullHTMLTag[-1] == '/'
                if selfClosing:
                    fullHTMLTag = fullHTMLTag[:-1]
                #try: print( "fullHTMLTag", repr(fullHTMLTag), "self-closing" if selfClosing else "" )
                #except UnicodeEncodeError: pass

                # Can't do a normal split coz can have a space within a link, e.g., href="one two.htm"
                fullHTMLTagBits = []
                insideDoubleQuotes = False
                currentField = ""
                for char in fullHTMLTag:
                    if char in (' ',) and not insideDoubleQuotes:
                        fullHTMLTagBits.append( currentField )
                        currentField = ""
                    else:
                        currentField += char
                        if char == '"': insideDoubleQuotes = not insideDoubleQuotes
                if currentField: fullHTMLTagBits.append( currentField ) # Make sure we get the last bit
                #print( "{} got {}".format( repr(fullHTMLTag), fullHTMLTagBits ) )
                HTMLTag = fullHTMLTagBits[0]
                #print( "HTMLTag", repr(HTMLTag) )

                if HTMLTag and HTMLTag[0] == '/': # it's a close tag
                    assert len(fullHTMLTagBits) == 1 # shouldn't have any attributes on a closing tag
                    assert not selfClosing
                    HTMLTag = HTMLTag[1:]
                    #print( "Got HTML {} close tag".format( repr(HTMLTag) ) )
                    #print( "cHT1", currentHTMLTags )
                    #print( "cFT1", currentFormatTags )
                    if currentHTMLTags and HTMLTag == currentHTMLTags[-1]: # all good
                        currentHTMLTags.pop() # Drop it
                        if HTMLTag not in NON_FORMATTING_TAGS:
                            currentFormatTags.pop()
                    elif currentHTMLTags:
                        logging.critical( "HTMLTextBox.insert: " + _("Expected to close {} but got {} instead").format( repr(currentHTMLTags[-1]), repr(HTMLTag) ) )
                    else:
                        logging.critical( "HTMLTextBox.insert: " + _("Unexpected HTML close {} close marker").format( repr(HTMLTag) ) )
                    #print( "cHT2", currentHTMLTags )
                    #print( "cFT2", currentFormatTags )
                else: # it's not a close tag so must be an open tag
                    if HTMLTag not in KNOWN_HTML_TAGS:
                        logging.critical( _("HTMLTextBox doesn't recognise or handle {} as an HTML tag").format( repr(HTMLTag) ) )
                        #currentHTMLTags.append( HTMLTag ) # remember it anyway in case it's closed later
                        continue
                    if HTMLTag in ('h1','h2','h3','p','li','table','tr',):
                        BText.insert( self, point, '\n' )
                    #elif HTMLTag in ('li',):
                        #BText.insert( self, point, '\n' )
                    elif HTMLTag in ('td',):
                        BText.insert( self, point, '\t' )
                    formatTag = HTMLTag
                    if len(fullHTMLTagBits)>1: # our HTML tag has some additional attributes
                        #print( "Looking for attributes" )
                        for bit in fullHTMLTagBits[1:]:
                            #try: print( "  bit", repr(bit) )
                            #except UnicodeEncodeError: pass
                            if bit.startswith('class="') and bit[-1]=='"':
                                formatTag += bit[7:-1] # create a tag like 'spanWord' or 'pVerse'
                            elif formatTag=='a' and bit.startswith('href="') and bit[-1]=='"':
                                formatTag += '=' + bit[6:-1] # create a tag like 'a=http://something.com'
                            else: logging.error( "HTMLTextBox: " + _("Ignoring {} attribute on {!r} tag").format( bit, HTMLTag ) )
                    if not selfClosing:
                        if HTMLTag != '!DOCTYPE':
                            currentHTMLTags.append( HTMLTag )
                            if HTMLTag not in NON_FORMATTING_TAGS:
                                currentFormatTags.append( formatTag )
        if currentHTMLTags:
            logging.critical( "HTMLTextBox.insert: " + _("Left-over HTML tags: {}").format( currentHTMLTags ) )
        if currentFormatTags:
            logging.critical( "HTMLTextBox.insert: " + _("Left-over format tags: {}").format( currentFormatTags ) )
    # end of HTMLTextBox.insert


    def _getURL( self, event ):
        """
        Give a mouse event, get the URL underneath it.
        """
        # get the index of the mouse cursor from the event.x and y attributes
        xy = '@{0},{1}'.format( event.x, event.y )
        #print( "xy", repr(xy) ) # e.g.., '@34,77'
        #print( "ixy", repr(self.index(xy)) ) # e.g., '4.3'

        #URL = None
        tagNames = self.tag_names( xy )
        #print( "tn", tagNames )
        for tagName in tagNames:
            if tagName.startswith( 'href' ):
                URL = tagName[4:]
                #print( "URL", repr(URL) )
                return URL
    # end of HTMLTextBox._getURL


    def openHyperlink( self, event ):
        """
        Handle a click on a hyperlink.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "HTMLTextBox.openHyperlink()" )
        URL = self._getURL( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #print( "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #print( "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #print( "Clicked on {}".format( repr(clickedText) ) )

        if URL: self.master.gotoLink( URL )
    # end of HTMLTextBox.openHyperlink


    def overHyperlink( self, event ):
        """
        Handle a mouseover on a hyperlink.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "HTMLTextBox.overHyperlink()" )
        URL = self._getURL( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #print( "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #print( "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #print( "Over {}".format( repr(clickedText) ) )

        if URL: self.master.overLink( URL )
    # end of HTMLTextBox.overHyperlink

    def leaveHyperlink( self, event ):
        """
        Handle a mouseover on a hyperlink.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "HTMLTextBox.leaveHyperlink()" )
        self.master.leaveLink()
    # end of HTMLTextBox.leaveHyperlink
# end of HTMLTextBox class



class CallbackAddon():
    """
    An add-on class which can call a user function whenever the text changes.
        This enables autocorrect.

    Adapted from http://stackoverflow.com/questions/13835207/binding-to-cursor-movement-doesnt-change-insert-mark
    """
    def __init__( self ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "CallbackAddon.__init__()" )

        self.callbackFunction = None
        # All widget changes happen via an internal Tcl command with the same name as the widget:
        #       all inserts, deletes, cursor changes, etc
        #
        # The beauty of Tcl is that we can replace that command with our own command.
        # The following code does just that: replace the code with a proxy that calls the
        # original command and then calls a callback. We can then do whatever we want in the callback.
        private_callback = self.register( self._callback )
        self.tk.eval( """
            proc widget_proxy {actual_widget callback args} {

                # this prevents recursion if the widget is called
                # during the callback
                set flag ::dont_recurse(actual_widget)

                # call the real tk widget with the real args
                set result [uplevel [linsert $args 0 $actual_widget]]

                # call the callback and ignore errors, but only
                # do so on inserts, deletes, and changes in the
                # mark. Otherwise we'll call the callback way too often.
                if {! [info exists $flag]} {
                    if {([lindex $args 0] in {insert replace delete}) ||
                        ([lrange $args 0 2] == {mark set insert})} {
                        # the flag makes sure that whatever happens in the
                        # callback doesn't cause the callbacks to be called again.
                        set $flag 1
                        catch {$callback $result {*}$args } callback_result
                        unset -nocomplain $flag
                    }
                }

                # return the result from the real widget command
                return $result
            }
            """ )
        self.tk.eval( """
                rename {widget} _{widget}
                interp alias {{}} ::{widget} {{}} widget_proxy _{widget} {callback}
            """.format( widget=str(self), callback=private_callback ) )

        self.autocorrectEntries = []
        # Temporarily include some default autocorrect values
        self.autocorrectEntries.append( ('<<','“') ) # Cycle through quotes with angle brackets
        self.autocorrectEntries.append( ('“<','‘') )
        self.autocorrectEntries.append( ('‘<',"'") )
        self.autocorrectEntries.append( ("'<",'<') )
        self.autocorrectEntries.append( ('>>','”') )
        self.autocorrectEntries.append( ('”>','’') )
        self.autocorrectEntries.append( ('’>',"'") )
        self.autocorrectEntries.append( ("'>",'>') )
        self.autocorrectEntries.append( ('--','–') ) # Cycle through en-dash/em-dash with hyphens
        self.autocorrectEntries.append( ('–-','—') )
        self.autocorrectEntries.append( ('—-','-') )
        self.autocorrectEntries.append( ('...','…') )

        self.setTextChangeCallback( self.onTextChange ) # Enable it (enables autocorrect)
    # end of CallbackAddon.__init__


    def _callback( self, result, *args ):
        """
        This little function does the actual call of the user routine
            to handle when the CallbackAddon changes.
        """
        if self.callbackFunction is not None:
            self.callbackFunction( result, *args )
    # end of CallbackAddon._callback


    def setTextChangeCallback( self, callableFunction ):
        """
        Just a little function to remember the routine to call
            when the CallbackAddon changes.
        """
        self.callbackFunction = callableFunction
    # end of CallbackAddon.setTextChangeCallback


    def onTextChange( self, result, *args ):
        """
        Called (set-up as a call-back function) whenever the entry cursor changes
            either with a mouse click or arrow keys.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "CallbackAddon.onTextChange( {}, {} )".format( repr(result), args ) )

        #if 0: # Get line and column info
            #lineColumn = self.index( tk.INSERT )
            #print( "lc", repr(lineColumn) )
            #line, column = lineColumn.split( '.', 1 )
            #print( "l,c", repr(line), repr(column) )

        #if 0: # get formatting tag info
            #tagNames = self.tag_names( tk.INSERT )
            #tagNames2 = self.tag_names( lineColumn )
            #tagNames3 = self.tag_names( tk.INSERT + ' linestart' )
            #tagNames4 = self.tag_names( lineColumn + ' linestart' )
            #tagNames5 = self.tag_names( tk.INSERT + ' linestart+1c' )
            #tagNames6 = self.tag_names( lineColumn + ' linestart+1c' )
            #print( "tN", tagNames )
            #if tagNames2!=tagNames or tagNames3!=tagNames or tagNames4!=tagNames or tagNames5!=tagNames or tagNames6!=tagNames:
                #print( "tN2", tagNames2 )
                #print( "tN3", tagNames3 )
                #print( "tN4", tagNames4 )
                #print( "tN5", tagNames5 )
                #print( "tN6", tagNames6 )
                #halt

        #if 0: # show various mark strategies
            #mark1 = self.mark_previous( tk.INSERT )
            #mark2 = self.mark_previous( lineColumn )
            #mark3 = self.mark_previous( tk.INSERT + ' linestart' )
            #mark4 = self.mark_previous( lineColumn + ' linestart' )
            #mark5 = self.mark_previous( tk.INSERT + ' linestart+1c' )
            #mark6 = self.mark_previous( lineColumn + ' linestart+1c' )
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


        # Handle auto-correct
        if self.autocorrectEntries and args[0]=='insert' and args[1]=='insert':
            #print( "Handle autocorrect" )
            #previousText = getCharactersBeforeCursor( self )
            allText = self.get()
            #print( "allText", repr(allText) )
            index = self.index( tk.INSERT )
            #print( "index", repr(index) )
            previousText = allText[0:index]
            #print( "previousText", repr(previousText) )
            for inChars,outChars in self.autocorrectEntries:
                if previousText.endswith( inChars ):
                    #print( "Going to replace {!r} with {!r}".format( inChars, outChars ) )
                    # Delete the typed character(s) and replace with the new one(s)
                    self.delete( index-len(inChars), index )
                    self.insert( tk.INSERT, outChars )
                    break
        # end of auto-correct section
    # end of CallbackAddon.onTextChange
# end of CallbackAddon class




#class CustomEntry( CallbackAddon, BEntry ):
    #"""
    #A custom (ttk) Entry widget which can call a user function whenever the text changes.
        #This enables autocorrect.
    #"""
    #def __init__( self, *args, **kwargs ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "CustomEntry.__init__( {}, {} )".format( args, kwargs ) )
        #BEntry.__init__( self, *args, **kwargs ) # initialise the base class
        #CallbackAddon.__init__( self ) # initialise the base class
    ## end of CustomEntry.__init__
## end of CustomEntry class


#class CustomCombobox( CallbackAddon, BCombobox ):
    #"""
    #A custom (ttk) Combobox widget which can call a user function whenever the text changes.
        #This enables autocorrect.
    #"""
    #def __init__( self, *args, **kwargs ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "CustomCombobox.__init__( {}, {} )".format( args, kwargs ) )
        #BCombobox.__init__( self, *args, **kwargs ) # initialise the base class
        #CallbackAddon.__init__( self ) # initialise the base class
    ## end of CustomCombobox.__init__
## end of CustomCombobox class


class CustomText( CallbackAddon, BText ):
    """
    A custom Text widget which calls a user function whenever the text changes.

    Also contains a function to highlight specific patterns.
    """
    def __init__( self, *args, **kwargs ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "CustomText.__init__( {}, {} )".format( args, kwargs ) )
        BText.__init__( self, *args, **kwargs ) # initialise the base class
        CallbackAddon.__init__( self ) # initialise the base class
    # end of CustomText.__init__


    def highlightPattern( self, pattern, styleTag, startAt=tkSTART, endAt=tk.END, regexpFlag=True ):
        """
        Apply the given tag to all text that matches the given pattern.

        Useful for syntax highlighting, etc.

        # Adapted from http://stackoverflow.com/questions/4028446/python-tkinter-help-menu
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "CustomText.highlightPattern( {}, {}, start={}, end={}, regexp={} )".format( pattern, styleTag, startAt, endAt, regexpFlag ) )

        countVar = tk.IntVar()
        matchEnd = startAt
        while True:
            #print( "here0 mS={!r} mE={!r} sL={!r}".format( self.index("matchStart"), self.index("matchEnd"), self.index("searchLimit") ) )
            index = self.search( pattern, matchEnd, stopindex=endAt, count=countVar, regexp=regexpFlag )
            #print( "here1", repr(index), repr(countVar.get()) )
            if index == "": break
            #print( "here2", self.index("matchStart"), self.index("matchEnd") )
            matchEnd = "{}+{}c".format( index, countVar.get() )
            self.tag_add( styleTag, index, matchEnd )
    # end of CustomText.highlightPattern


    def highlightAllPatterns( self, patternCollection ):
        """
        Given a collection of 4-tuples, apply the styles to the patterns in the text.

        Each tuple is:
            regexpFlag: True/False
            pattern to search for
            tagName
            tagDict, e.g, {"background":"red"}
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "CustomText.highlightAllPatterns( {} )".format( patternCollection ) )

        for regexpFlag, pattern, tagName, tagDict in patternCollection:
            self.tag_configure( tagName, **tagDict )
            self.highlightPattern( pattern, tagName, regexpFlag=regexpFlag )
    # end of CustomText.highlightAllPatterns
# end of CustomText class



class ChildBoxAddon():
    """
    A set of mix-in (add-on) functions that work for any frame or window that has a member: self.textBox
    """
    def __init__( self, parentWindow ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.__init__( {} )".format( parentWindow ) )
            assert parentWindow
        self.parentWindow = parentWindow

        self.myKeyboardBindingsList = []
        if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = [] # Just for catching setting of duplicates

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.__init__ finished." )
    # end of ChildBoxAddon.__init__


    def _createStandardBoxKeyboardBinding( self, name, commandFunction ):
        """
        Called from createStandardKeyboardBindings to do the actual work.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "ChildBoxAddon._createStandardBoxKeyboardBinding( {} )".format( name ) )

        #try: kBD = self.parentApp.keyBindingDict
        #except AttributeError:
        kBD = self.parentWindow.parentApp.keyBindingDict
        assert (name,kBD[name][0],) not in self.myKeyboardBindingsList
        if name in kBD:
            for keyCode in kBD[name][1:]:
                #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                self.textBox.bind( keyCode, commandFunction )
                if BibleOrgSysGlobals.debugFlag:
                    if keyCode in self.myKeyboardShortcutsList:
                        print( "ChildBoxAddon._createStandardBoxKeyboardBinding wants to add duplicate {}".format( keyCode ) )
                    self.myKeyboardShortcutsList.append( keyCode )
            self.myKeyboardBindingsList.append( (name,kBD[name][0],) )
        else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of ChildBoxAddon._createStandardBoxKeyboardBinding()

    def createStandardBoxKeyboardBindings( self, reset=False ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.createStandardBoxKeyboardBindings( {} )".format( reset ) )

        if reset:
            self.myKeyboardBindingsList = []

        for name,commandFunction in ( ('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                             ('Find',self.doBoxFind), ('Refind',self.doBoxRefind),
                             #('Help',self.doHelp), ('Info',self.doShowInfo), ('About',self.doAbout),
                             #('ShowMain',self.parentWindow.doShowMainWindow),
                             ('Close',self.doClose),
                             ):
            self._createStandardBoxKeyboardBinding( name, commandFunction )
    # end of ChildBoxAddon.createStandardBoxKeyboardBindings()


    def setFocus( self, event ):
        """
        Explicitly set focus, so user can select and copy text
        """
        self.textBox.focus_set()
    # end of ChildBoxAddon.setFocus


    def doCopy( self, event=None ):
        """
        Copy the selected text onto the clipboard.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.doCopy( {} )".format( event ) )

        if not self.textBox.tag_ranges( tk.SEL ):       # save in cross-app clipboard
            errorBeep()
            showError( self, APP_NAME, _("No text selected") )
        else:
            copyText = self.textBox.get( tk.SEL_FIRST, tk.SEL_LAST)
            print( "  copied text", repr(copyText) )
            self.clipboard_clear()
            self.clipboard_append( copyText )
    # end of ChildBoxAddon.doCopy


    def doSelectAll( self, event=None ):
        """
        Select all the text in the text box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.doSelectAll( {} )".format( event ) )

        self.textBox.tag_add( tk.SEL, tkSTART, tk.END+'-1c' )   # select entire text
        self.textBox.mark_set( tk.INSERT, tkSTART )          # move insert point to top
        self.textBox.see( tk.INSERT )                      # scroll to top
    # end of ChildBoxAddon.doSelectAll


    def doGotoWindowLine( self, event=None, forceline=None ):
        """
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'ChildBoxAddon doGotoWindowLine {}'.format( forceline ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.doGotoWindowLine( {}, {} )".format( event, forceline ) )

        line = forceline or askinteger( APP_NAME, _("Enter line number") )
        self.textBox.update()
        self.textBox.focus()
        if line is not None:
            maxindex = self.textBox.index( tk.END+'-1c' )
            maxline  = int( maxindex.split('.')[0] )
            if line > 0 and line <= maxline:
                self.textBox.mark_set( tk.INSERT, '{}.0'.format(line) ) # goto line
                self.textBox.tag_remove( tk.SEL, tkSTART, tk.END )          # delete selects
                self.textBox.tag_add( tk.SEL, tk.INSERT, 'insert+1l' )  # select line
                self.textBox.see( tk.INSERT )                          # scroll to line
            else:
                errorBeep()
                showError( self, APP_NAME, _("No such line number") )
    # end of ChildBoxAddon.doGotoWindowLine


    def doBoxFind( self, event=None, lastkey=None ):
        """
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'ChildBoxAddon doBoxFind {!r}'.format( lastkey ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.doBoxFind( {}, {!r} )".format( event, lastkey ) )

        key = lastkey or askstring( APP_NAME, _("Enter search string"), parent=self )
        self.textBox.update()
        self.textBox.focus()
        self.lastfind = key
        if key:
            #nocase = self.optionsDict['caseinsens'] # Where should this come from?
            nocase = True
            where = self.textBox.search( key, tkSTART if lastkey is None else tk.INSERT, tk.END, nocase=nocase )
            if not where:                                          # don't wrap
                errorBeep()
                showError( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:18]+'…') ) )
            else:
                pastkey = where + '+%dc' % len(key)           # index past key
                self.textBox.tag_remove( tk.SEL, tkSTART, tk.END )         # remove any sel
                self.textBox.tag_add( tk.SEL, where, pastkey )        # select key
                self.textBox.mark_set( tk.INSERT, pastkey )           # for next find
                self.textBox.see( where )                          # scroll display
    # end of ChildBoxAddon.doBoxFind


    def doBoxRefind( self, event=None ):
        """
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'ChildBoxAddon doBoxRefind' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.doBoxRefind( {} ) for {!r}".format( event, self.lastfind ) )

        self.doBoxFind( lastkey=self.lastfind )
    # end of ChildBoxAddon.doBoxRefind


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'ChildBoxAddon doShowInfo' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.doShowInfo( {} )".format( event ) )

        text  = self.getAllText()
        numChars = len( text )
        numLines = len( text.split('\n') )
        numWords = len( text.split() )
        index = self.textBox.index( tk.INSERT )
        atLine, atColumn = index.split('.')
        infoString = 'Current location:\n' \
                 + '  Line:\t{}\n  Column:\t{}\n'.format( atLine, atColumn ) \
                 + '\nFile text statistics:\n' \
                 + '  Chars:\t{}\n  Lines:\t{}\n  Words:\t{}'.format( numChars, numLines, numWords )
        showInfo( self, 'Window Information', infoString )
    # end of ChildBoxAddon.doShowInfo


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    def clearText( self ): # Leaves in normal state
        self.textBox.configure( state=tk.NORMAL )
        self.textBox.delete( tkSTART, tk.END )
    # end of ChildBoxAddon.clearText


    def isEmpty( self ):
        return not self.getAllText()
    # end of ChildBoxAddon.isEmpty


    def modified( self ):
        """
        We want this to return True if an editable (enabled) textBox has been modified.
        """
        #print( "Configure", self.textBox.configure() ) # Prints a large dictionary of settings
        #print( "  State", self.textBox.configure()['state'] ) # Prints a 5-tuple
        if self.textBox.configure()['state'][4] == 'normal':
            return self.textBox.edit_modified()
        else: return False
    # end of ChildBoxAddon.modified


    def getAllText( self ):
        """
        Returns all the text as a string.
        """
        return self.textBox.get( tkSTART, tk.END+'-1c' )
    # end of ChildBoxAddon.getAllText


    def setAllText( self, newText ):
        """
        Sets the textBox (assumed to be enabled) to the given text
            then positions the insert cursor at the BEGINNING of the text.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.setAllText( {!r} )".format( newText ) )

        self.textBox.configure( state=tk.NORMAL ) # In case it was disabled
        self.textBox.delete( tkSTART, tk.END ) # Delete everything that's existing
        self.textBox.insert( tk.END, newText )
        self.textBox.mark_set( tk.INSERT, tkSTART ) # move insert point to top
        self.textBox.see( tk.INSERT ) # scroll to top, insert is set

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( tk.FALSE ) # clear modified flag
    # end of ChildBoxAddon.setAllText


    #def doShowMainWindow( self, event=None ):
        #"""
        #Display the main window (it might be minimised or covered).
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "ChildBoxAddon.doShowMainWindow( {} )".format( event ) )

        ##self.parentApp.rootWindow.iconify() # Didn't help
        #self.parentApp.rootWindow.withdraw() # For some reason, doing this first makes the window always appear above others
        #self.parentApp.rootWindow.update()
        #self.parentApp.rootWindow.deiconify()
        ##self.parentApp.rootWindow.focus_set()
        #self.parentApp.rootWindow.lift() # aboveThis=self )
    ## end of ChildBoxAddon.doShowMainWindow


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden if an edit box needs to save files first.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "ChildBoxAddon.doClose( {} )".format( event ) )

        self.destroy()
    # end of ChildBoxAddon.doClose
# end of ChildBoxAddon class



class BibleBoxAddon():
    """
    A set of functions that work for any Bible frame or window that has a member: self.textBox
        and also uses verseKeys
    """
    def __init__( self, parentWindow, BibleBoxType ):
        """
        This function does absolutely nothing.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleBoxAddon.__init__( {}, {} )".format( parentWindow, BibleBoxType ) )
            assert parentWindow
        self.parentWindow, self.BibleBoxType = parentWindow, BibleBoxType

        # Set-up our standard Bible styles
        for USFMKey, styleDict in self.parentWindow.parentApp.stylesheet.getTKStyles().items():
            self.textBox.tag_configure( USFMKey, **styleDict ) # Create the style
        # Add our extra specialised styles
        self.textBox.tag_configure( 'contextHeader', background='pink', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'context', background='pink', font='helvetica 6' )
        self.textBox.tag_configure( 'markersHeader', background='yellow3', font='helvetica 6 bold' )
        self.textBox.tag_configure( 'markers', background='yellow3', font='helvetica 6' )
        #else:
            #self.textBox.tag_configure( 'verseNumberFormat', foreground='blue', font='helvetica 8', relief=tk.RAISED, offset='3' )
            #self.textBox.tag_configure( 'versePreSpaceFormat', background='pink', font='helvetica 8' )
            #self.textBox.tag_configure( 'versePostSpaceFormat', background='pink', font='helvetica 4' )
            #self.textBox.tag_configure( 'verseTextFormat', font='sil-doulos 12' )
            #self.textBox.tag_configure( 'otherVerseTextFormat', font='sil-doulos 9' )
            ##self.textBox.tag_configure( 'verseText', background='yellow', font='helvetica 14 bold', relief=tk.RAISED )
            ##"background", "bgstipple", "borderwidth", "elide", "fgstipple", "font", "foreground", "justify", "lmargin1",
            ##"lmargin2", "offset", "overstrike", "relief", "rmargin", "spacing1", "spacing2", "spacing3",
            ##"tabs", "tabstyle", "underline", and "wrap".


        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleBoxAddon.__init__ finished." )
    # end of BibleBoxAddon.__init__


    def createStandardBoxKeyboardBindings( self, reset=False ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleBoxAddon.createStandardBoxKeyboardBindings( {} )".format( reset ) )

        if reset:
            self.myKeyboardBindingsList = []

        for name,commandFunction in ( ('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                             ('Find',self.doBibleFind), #('Refind',self.doBibleRefind),
                             #('Help',self.doHelp), ('Info',self.doShowInfo), ('About',self.doAbout),
                             #('ShowMain',self.doShowMainWindow),
                             ('Close',self.doClose), ):
            self._createStandardBoxKeyboardBinding( name, commandFunction )
    # end of BibleBoxAddon.createStandardBoxKeyboardBindings()


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleBoxAddon.createContextMenu()" )

        self.textBox.contextMenu = tk.Menu( self, tearoff=0 )
        self.textBox.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        self.textBox.contextMenu.add_separator()
        self.textBox.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )
        self.textBox.contextMenu.add_separator()
        self.textBox.contextMenu.add_command( label=_('Bible Find…'), underline=6, command=self.doBibleFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        self.textBox.contextMenu.add_separator()
        self.textBox.contextMenu.add_command( label=_('Find in window…'), underline=8, command=self.doBoxFind )#, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close window'), underline=1, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] )

        self.textBox.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()

        self.BibleFindOptionsDict, self.BibleReplaceOptionsDict = {}, {}
    # end of BibleBoxAddon.createContextMenu

    def showContextMenu( self, event ):
        self.textBox.contextMenu.tk_popup( event.x_root, event.y_root )
    # end of BibleBoxAddon.showContextMenu


    def displayAppendVerse( self, firstFlag, verseKey, verseContextData, lastFlag=True, currentVerseFlag=False, substituteTrailingSpaces=False, substituteMultipleSpaces=False ):
        """
        Add the requested verse to the end of self.textBox.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.

        Usually called from updateShownBCV from the subclass.
        Note that it's used in both formatted and unformatted (even edit) windows.
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule:
                print( "displayAppendVerse( {}, {}, {}, {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, substituteTrailingSpaces, substituteMultipleSpaces ) )
            assert isinstance( firstFlag, bool )
            assert isinstance( verseKey, SimpleVerseKey )
            if verseContextData:
                assert isinstance( verseContextData, tuple ) and len(verseContextData)==2 or isinstance( verseContextData, str )
            assert isinstance( lastFlag, bool )
            assert isinstance( currentVerseFlag, bool )

        def insertAtEnd( ieText, ieTags ):
            """
            Insert the formatted text into the end of the textbox.

            The function mostly exists so we can print the parameters if necessary for debugging.
            """
            if BibleOrgSysGlobals.debugFlag:
                if debuggingThisModule:
                    print( "insertAtEnd( {!r}, {} )".format( ieText, ieTags ) )
                assert isinstance( ieText, str )
                assert isinstance( ieTags, (str,tuple) )
                assert TRAILING_SPACE_SUBSTITUTE not in ieText
                assert MULTIPLE_SPACE_SUBSTITUTE not in ieText

            # Make any requested substitutions
            if substituteMultipleSpaces:
                ieText = ieText.replace( '  ', DOUBLE_SPACE_SUBSTITUTE )
                ieText = ieText.replace( CLEANUP_LAST_MULTIPLE_SPACE, DOUBLE_SPACE_SUBSTITUTE )
            if substituteTrailingSpaces:
                ieText = ieText.replace( TRAILING_SPACE_LINE, TRAILING_SPACE_LINE_SUBSTITUTE )

            self.textBox.insert( tk.END, ieText, ieTags )
        # end of BibleBoxAddon.displayAppendVerse.insertAtEnd


        # Start of main code for BibleBoxAddon.displayAppendVerse
        try: cVM, fVM = self._contextViewMode, self._formatViewMode
        except AttributeError: # Must be called from a box, not a window so get settings from parent
            cVM, fVM = self.parentWindow._contextViewMode, self.parentWindow._formatViewMode
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "displayAppendVerse2( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )

        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "BibleBoxAddon.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
            ##try: print( "BibleBoxAddon.displayAppendVerse( {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, currentVerseFlag ) )
            ##except UnicodeEncodeError: print( "BibleBoxAddon.displayAppendVerse", firstFlag, verseKey, currentVerseFlag )

        BBB, C, V = verseKey.getBCV()
        C, V = int(C), int(V)
        #C1 = C2 = int(C); V1 = V2 = int(V)
        #if V1 > 0: V1 -= 1
        #elif C1 > 0:
            #C1 -= 1
            #V1 = self.getNumVerses( BBB, C1 )
        #if V2 < self.getNumVerses( BBB, C2 ): V2 += 1
        #elif C2 < self.getNumChapters( BBB):
            #C2 += 1
            #V2 = 0
        #previousMarkName = 'C{}V{}'.format( C1, V1 )
        currentMarkName = 'C{}V{}'.format( C, V )
        #nextMarkName = 'C{}V{}'.format( C2, V2 )
        #print( "Marks", previousMarkName, currentMarkName, nextMarkName )

        lastCharWasSpace = haveTextFlag = not firstFlag

        if verseContextData is None:
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                print( "  ", "BibleBoxAddon.displayAppendVerse has no data for", verseKey )
            verseDataList = context = None
        elif isinstance( verseContextData, tuple ):
            assert len(verseContextData) == 2
            verseDataList, context = verseContextData
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #print( "   VerseDataList: {}".format( verseDataList ) )
                #print( "   Context: {}".format( context ) )
        elif isinstance( verseContextData, str ):
            verseDataList, context = verseContextData.split( '\n' ), None
        elif BibleOrgSysGlobals.debugFlag: halt

        # Display the context preceding the first verse
        if firstFlag:
            if context:
                #print( "context", context )
                #print( "  Setting context mark to {}".format( previousMarkName ) )
                #self.textBox.mark_set( previousMarkName, tk.INSERT )
                #self.textBox.mark_gravity( previousMarkName, tk.LEFT )
                insertAtEnd( ' '+_("Prior context")+':', 'contextHeader' )
                contextString, firstMarker = "", True
                for someMarker in context:
                    #print( "  someMarker", someMarker )
                    if someMarker != 'chapters':
                        contextString += (' ' if firstMarker else ', ') + someMarker
                        firstMarker = False
                insertAtEnd( contextString+' ', 'context' )
                haveTextFlag = True
            if verseDataList and fVM == 'Formatted':
                # Display the first formatting marker in this segment -- don't really need this -- see below
                #firstEntry = verseDataList[0]
                #if isinstance( firstEntry, InternalBibleEntry ): marker = firstEntry.getMarker()
                #elif isinstance( firstEntry, tuple ): marker = firstEntry[0]
                #else: marker = None
                #if marker in BibleOrgSysGlobals.USFMParagraphMarkers:
                    #insertAtEnd( ' '+_("Current context")+': ', 'contextHeader' )
                    #insertAtEnd( marker+' ', 'context' )
                # Display all line markers in this segment
                markerList = []
                for verseData in verseDataList:
                    if isinstance( verseData, InternalBibleEntry ): marker = verseData.getMarker()
                    elif isinstance( verseData, tuple ): marker = verseData[0]
                    else: marker = None
                    if marker and not marker.startswith('¬') \
                    and not marker.endswith('~') and not marker.endswith('#'):
                        markerList.append( marker )
                if markerList:
                    insertAtEnd( ' '+_("Displayed markers")+': ', 'markersHeader' )
                    insertAtEnd( str(markerList)[1:-1], 'markers' ) # Display list without square brackets

        #print( "  Setting mark to {}".format( currentMarkName ) )
        self.textBox.mark_set( currentMarkName, tk.INSERT )
        self.textBox.mark_gravity( currentMarkName, tk.LEFT )

        if verseDataList is None:
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                print( "  ", "BibleBoxAddon.displayAppendVerse has no data for", self.moduleID, verseKey )
            #self.textBox.insert( tk.END, '--' )
        else:
            #hadVerseText = False
            #try: cVM = self._contextViewMode
            #except AttributeError: cVM = self.parentWindow._contextViewMode
            lastParagraphMarker = context[-1] if context and context[-1] in BibleOrgSysGlobals.USFMParagraphMarkers \
                                        else 'v~' # If we don't know the format of a verse (or for unformatted Bibles)
            endMarkers = []

            for verseDataEntry in verseDataList:
                # This loop is used for several types of data
                if isinstance( verseDataEntry, InternalBibleEntry ):
                    marker, cleanText = verseDataEntry.getMarker(), verseDataEntry.getCleanText()
                elif isinstance( verseDataEntry, tuple ):
                    marker, cleanText = verseDataEntry[0], verseDataEntry[3]
                elif isinstance( verseDataEntry, str ): # from a Bible text editor window
                    if verseDataEntry=='': continue
                    verseDataEntry += '\n'
                    if verseDataEntry[0]=='\\':
                        marker = ''
                        for char in verseDataEntry[1:]:
                            if char!='¬' and not char.isalnum(): break
                            marker += char
                        cleanText = verseDataEntry[len(marker)+1:].lstrip()
                    else:
                        marker, cleanText = None, verseDataEntry
                elif BibleOrgSysGlobals.debugFlag: halt
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    print( "  displayAppendVerse", lastParagraphMarker, haveTextFlag, marker, repr(cleanText) )

                if fVM == 'Unformatted':
                    if marker and marker[0]=='¬': pass # Ignore end markers for now
                    elif marker in ('intro','chapters','list',): pass # Ignore added markers for now
                    else:
                        if isinstance( verseDataEntry, str ): # from a Bible text editor window
                            #print( "marker={!r}, verseDataEntry={!r}".format( marker, verseDataEntry ) )
                            insertAtEnd( verseDataEntry, marker ) # Do it just as is!
                        else: # not a str, i.e., not a text editor, but a viewable resource
                            #if hadVerseText and marker in ( 's', 's1', 's2', 's3' ):
                                #print( "  Setting s mark to {}".format( nextMarkName ) )
                                #self.textBox.mark_set( nextMarkName, tk.INSERT )
                                #self.textBox.mark_gravity( nextMarkName, tk.LEFT )
                            #print( "  Inserting ({}): {!r}".format( marker, verseDataEntry ) )
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            if marker is None:
                                insertAtEnd( cleanText, '###' )
                            else: insertAtEnd( '\\{} {}'.format( marker, cleanText ), marker+'#' )
                            haveTextFlag = True

                elif fVM == 'Formatted':
                    if marker.startswith( '¬' ):
                        if marker != '¬v': endMarkers.append( marker ) # Don't want end-verse markers
                    else: endMarkers = [] # Reset when we have normal markers

                    if marker.startswith( '¬' ):
                        pass # Ignore end markers for now
                        #assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        #if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        #insertAtEnd( cleanText, marker )
                        #haveTextFlag = True
                    elif marker == 'id':
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('ide','rem',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('h','toc1','toc2','toc3','cl¤',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('intro','chapters','list',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('mt1','mt2','mt3','mt4', 'imt1','imt2','imt3','imt4', 'iot','io1','io2','io3','io4',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('ip','ipi','im','imi','ipq','imq','ipr', 'iq1','iq2','iq3','iq4',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('s1','s2','s3','s4', 'is1','is2','is3','is4', 'ms1','ms2','ms3','ms4', 'cl',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('d','sp',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('r','mr','sr',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in BibleOrgSysGlobals.USFMParagraphMarkers:
                        assert not cleanText # No text expected with these markers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        lastParagraphMarker = marker
                        haveTextFlag = True
                    elif marker in ('b','ib'):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        assert not cleanText # No text expected with this marker
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                    #elif marker in ('m','im'):
                        #self.textBox.insert ( tk.END, '\n' if haveTextFlag else '  ', marker )
                        #if cleanText:
                            #insertAtEnd( cleanText, '*'+marker if currentVerseFlag else marker )
                            #lastCharWasSpace = False
                            #haveTextFlag = True
                    elif marker == 'p#': # Should only be from the Digital Bible Platform
                        assert self.BibleBoxType in ('DBPBibleResourceBox','DBPBibleResourceWindow')
                        #pass # Just ignore these for now
                    elif marker == 'c': # Don't want to display this (original) c marker
                        #if not firstFlag: haveC = cleanText
                        #else: print( "   Ignore C={}".format( cleanText ) )
                        pass
                    elif marker == 'c#': # Might want to display this (added) c marker
                        if cleanText != verseKey.getBBB():
                            if not lastCharWasSpace: insertAtEnd( ' ', 'v-' )
                            insertAtEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                            lastCharWasSpace = False
                    elif marker == 'v':
                        if cleanText != '1': # Don't display verse number for v1 in default view
                            if haveTextFlag:
                                insertAtEnd( ' ', (lastParagraphMarker,'v-',) if lastParagraphMarker else ('v-',) )
                            insertAtEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                            insertAtEnd( '\u2009', (lastParagraphMarker,'v+',) if lastParagraphMarker else ('v+',) ) # narrow space
                            lastCharWasSpace = haveTextFlag = True
                    elif marker in ('v~','p~'):
                        insertAtEnd( cleanText, '*'+lastParagraphMarker if currentVerseFlag else lastParagraphMarker )
                        haveTextFlag = True
                    else:
                        if BibleOrgSysGlobals.debugFlag:
                            logging.critical( _("BibleBoxAddon.displayAppendVerse (formatted): Unknown marker {!r} {!r} from {}").format( marker, cleanText, verseDataList ) )
                        else:
                            logging.critical( _("BibleBoxAddon.displayAppendVerse (formatted): Unknown marker {!r} {!r}").format( marker, cleanText ) )
                else:
                    logging.critical( _("BibleBoxAddon.displayAppendVerse: Unknown {!r} format view mode").format( fVM ) )
                    if BibleOrgSysGlobals.debugFlag: halt

            if lastFlag and cVM=='ByVerse' and endMarkers:
                #print( "endMarkers", endMarkers )
                insertAtEnd( ' '+ _("End context")+':', 'contextHeader' )
                contextString, firstMarker = "", True
                for someMarker in endMarkers:
                    #print( "  someMarker", someMarker )
                    contextString += (' ' if firstMarker else ', ') + someMarker
                    firstMarker = False
                insertAtEnd( contextString+' ', 'context' )
    # end of BibleBoxAddon.displayAppendVerse


    def getBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        if BibleOrgSysGlobals.debugFlag:
            print( "BibleBoxAddon.getBeforeAndAfterBibleData( {} )".format( newVerseKey ) )
            assert isinstance( newVerseKey, SimpleVerseKey )

        BBB, C, V = newVerseKey.getBCV()
        #print( "here1", BBB, repr(C), repr(V) )
        intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
        #print( "  here2", repr(intC), repr(intV) )

        # Determine the PREVIOUS valid verse numbers
        prevBBB, prevIntC, prevIntV = BBB, intC, intV
        previousVersesData = []
        for n in range( -self.parentApp.viewVersesBefore, 0 ):
            failed = False
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "  getBeforeAndAfterBibleData here with", repr(n), repr(prevIntC), repr(prevIntV) )
            if prevIntV is not None and prevIntV > 0: prevIntV -= 1
            elif prevIntC > 0:
                prevIntC -= 1
                try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                except KeyError:
                    if prevIntC != 0: # we can expect an error for chapter zero
                        logging.error( _("BibleBoxAddon.getBeforeAndAfterBibleData1 failed at {} {}").format( prevBBB, prevIntC ) )
                    failed = True
                #if not failed:
                    #if BibleOrgSysGlobals.debugFlag: print( " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            else:
                try: prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                except KeyError: prevBBB = None
                if prevBBB is None: failed = True
                else:
                    prevIntC = self.getNumChapters( prevBBB )
                    prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                        print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
                    if prevIntC is None or prevIntV is None:
                        logging.error( _("BibleBoxAddon.getBeforeAndAfterBibleData2 failed at {} {}:{}").format( prevBBB, prevIntC, prevIntV ) )
                        #failed = True
                        break
            if not failed and prevIntV is not None:
                #print( "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                assert prevBBB and isinstance(prevBBB, str)
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getCachedVerseData( previousVerseKey )
                if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        # Determine the NEXT valid verse numbers
        nextBBB, nextIntC, nextIntV = BBB, intC, intV
        nextVersesData = []
        for n in range( self.parentApp.viewVersesAfter ):
            try: numVerses = self.getNumVerses( nextBBB, nextIntC )
            except KeyError: numVerses = None # for an invalid BBB
            nextIntV += 1
            if numVerses is None or nextIntV > numVerses:
                nextIntV = 1
                nextIntC += 1 # Need to check…
            nextVerseKey = SimpleVerseKey( nextBBB, nextIntC, nextIntV )
            nextVerseData = self.getCachedVerseData( nextVerseKey )
            if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        # Get the CURRENT verse data
        verseData = self.getCachedVerseData( newVerseKey )

        return verseData, previousVersesData, nextVersesData
    # end of BibleBoxAddon.getBeforeAndAfterBibleData


    def doBibleFind( self, event=None ):
        """
        Get the search parameters and then execute the search.

        Note that BibleFind works on the imported files,
            so it can work from any box or window that has an internalBible.
        """
        from BiblelatorDialogs import GetBibleFindTextDialog

        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'BibleBoxAddon doBibleFind' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleBoxAddon.doBibleFind( {} )".format( event ) )

        try: haveInternalBible = self.internalBible is not None
        except AttributeError: haveInternalBible = False
        if not haveInternalBible:
            logging.critical( _("No Bible to search") )
            return
        #print( "intBib", self.internalBible )

        self.BibleFindOptionsDict['currentBCV'] = self.currentVerseKey.getBCV()
        gBSTD = GetBibleFindTextDialog( self, self.internalBible, self.BibleFindOptionsDict, title=_('Find in Bible') )
        if BibleOrgSysGlobals.debugFlag: print( "gBSTDResult", repr(gBSTD.result) )
        if gBSTD.result:
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBSTD.result, dict )
            self.BibleFindOptionsDict = gBSTD.result # Update our search options dictionary
            self.doActualBibleFind()
        self.parentApp.setReadyStatus()

        #return tkBREAK
    # end of BibleBoxAddon.doBibleFind


    def doActualBibleFind( self, extendTo=None ):
        """
        This function (called by the above doBibleFind),
            invokes the actual search (or redoes the search)
            assuming that the search parameters are already defined.
        """
        from ChildWindows import FindResultWindow

        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'BibleBoxAddon doActualBibleFind' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleBoxAddon.doActualBibleFind( {} )".format( extendTo ) )

        self.parentApp.setWaitStatus( _("Searching…") )
        #self.textBox.update()
        #self.textBox.focus()
        #self.lastfind = key
        self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, ' doActualBibleFind {}'.format( self.BibleFindOptionsDict ) )
        #print( "bookList", repr(self.BibleFindOptionsDict['bookList']) )
        bookCode = None
        if isinstance( self.BibleFindOptionsDict['bookList'], str ) \
        and self.BibleFindOptionsDict['bookList'] != 'ALL':
            bookCode = self.BibleFindOptionsDict['bookList']
        self._prepareInternalBible( bookCode, self.BibleFindOptionsDict['givenBible'] ) # Make sure that all books are loaded
        # We search the loaded Bible processed lines
        self.BibleFindOptionsDict, resultSummaryDict, findResultList = self.BibleFindOptionsDict['givenBible'].findText( self.BibleFindOptionsDict )
        #print( "Got findResultList", findResultList )
        if len(findResultList) == 0: # nothing found
            errorBeep()
            key = self.BibleFindOptionsDict['findText']
            showError( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:18]+'…') ) )
        else:
            try: replaceFunction = self.doBibleReplace
            except AttributeError: replaceFunction = None # Read-only Bible boxes don't have a replace function
            findResultWindow = FindResultWindow( self, self.BibleFindOptionsDict, resultSummaryDict, findResultList,
                                    findFunction=self.doBibleFind, refindFunction=self.doActualBibleFind,
                                    replaceFunction=replaceFunction, extendTo=extendTo )
            self.parentApp.childWindows.append( findResultWindow )
        self.parentApp.setReadyStatus()
    # end of BibleBoxAddon.doActualBibleFind


    def _prepareInternalBible( self, bookCode=None, givenBible=None ):
        """
        Prepare to do a search on the Internal Bible object
            or to do some of the exports or checks available in BibleOrgSysGlobals.

        Note that this function saves the current book if it's modified.

        If a bookcode is specified, loads only that book (so the user doesn't have to wait).

        Leaves the wait cursor displayed.
        """
        logging.debug( "BibleBoxAddon._prepareInternalBible()" )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "BibleBoxAddon._prepareInternalBible()" )
        if givenBible is None: givenBible = self.internalBible

        if self.modified(): self.doSave() # NOTE: Read-only boxes/windows don't even have a doSave() function
        if givenBible is not None:
            self.parentApp.setWaitStatus( _("Preparing internal Bible…") )
            if bookCode is None:
                self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible…") )
                givenBible.load()
            else:
                self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible book…") )
                givenBible.loadBook( bookCode )
    # end of BibleBoxAddon._prepareInternalBible
# end of class BibleBoxAddon



#class BibleBox( ChildBox ):
    #"""
    #A set of functions that work for any Bible frame or window that has a member: self.textBox
        #and also uses verseKeys
    #"""
    #def __init__( self, parentApp ):
        #"""
        #This function is not needed at all, except for debug tracing of __init__ functions (when used).
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "BibleBox.__init__( {} )".format( parentApp ) )
            #assert parentApp
        ##self.parentApp = parentApp

        #ChildBox.__init__( self, parentApp )

        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "BibleBox.__init__ finished." )
    ## end of BibleBox.__init__


    ##def createStandardBoxKeyboardBindings( self, reset=False ):
        ##"""
        ##Create keyboard bindings for this widget.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( "BibleBox.createStandardBoxKeyboardBindings( {} )".format( reset ) )

        ##if reset:
            ##self.myKeyboardBindingsList = []

        ##for name,commandFunction in ( ('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                             ##('Find',self.doBibleFind), #('Refind',self.doBibleRefind),
                             ###('Help',self.doHelp), ('Info',self.doShowInfo), ('About',self.doAbout),
                             ###('ShowMain',self.doShowMainWindow),
                             ##('Close',self.doClose), ):
            ##self._createStandardBoxKeyboardBinding( name, commandFunction )
    ### end of BibleBox.createStandardBoxKeyboardBindings()


    ##def createContextMenu( self ):
        ##"""
        ##Can be overriden if necessary.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( "BibleBox.createContextMenu()" )

        ##self.textBox.contextMenu = tk.Menu( self, tearoff=0 )
        ##self.textBox.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=self.parentApp.keyBindingDict[_('Copy')][0] )
        ##self.textBox.contextMenu.add_separator()
        ##self.textBox.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=self.parentApp.keyBindingDict[_('SelectAll')][0] )
        ##self.textBox.contextMenu.add_separator()
        ##self.textBox.contextMenu.add_command( label=_('Bible Find…'), underline=6, command=self.doBibleFind, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        ##self.textBox.contextMenu.add_separator()
        ##self.textBox.contextMenu.add_command( label=_('Find in window…'), underline=8, command=self.doBoxFind )#, accelerator=self.parentApp.keyBindingDict[_('Find')][0] )
        ###self.contextMenu.add_separator()
        ###self.contextMenu.add_command( label=_('Close window'), underline=1, command=self.doClose, accelerator=self.parentApp.keyBindingDict[_('Close')][0] )

        ##self.textBox.bind( '<Button-3>', self.showContextMenu ) # right-click
        ###self.pack()

        ##self.BibleFindOptionsDict, self.BibleReplaceOptionsDict = {}, {}
    ### end of BibleBox.createContextMenu

    ##def showContextMenu( self, event ):
        ##self.textBox.contextMenu.tk_popup( event.x_root, event.y_root )
    ### end of BibleBox.showContextMenu


    ##def displayAppendVerse( self, firstFlag, verseKey, verseContextData, lastFlag=True, currentVerseFlag=False, substituteTrailingSpaces=False, substituteMultipleSpaces=False ):
        ##"""
        ##Add the requested verse to the end of self.textBox.

        ##It connects the USFM markers as stylenames while it's doing it
            ##and adds the CV marks at the same time for navigation.

        ##Usually called from updateShownBCV from the subclass.
        ##Note that it's used in both formatted and unformatted (even edit) windows.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag:
            ##if debuggingThisModule:
                ##print( "displayAppendVerse( {}, {}, {}, {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, substituteTrailingSpaces, substituteMultipleSpaces ) )
            ##assert isinstance( firstFlag, bool )
            ##assert isinstance( verseKey, SimpleVerseKey )
            ##if verseContextData:
                ##assert isinstance( verseContextData, tuple ) and len(verseContextData)==2 or isinstance( verseContextData, str )
            ##assert isinstance( lastFlag, bool )
            ##assert isinstance( currentVerseFlag, bool )

        ##def insertAtEnd( ieText, ieTags ):
            ##"""
            ##Insert the formatted text into the end of the textbox.

            ##The function mostly exists so we can print the parameters if necessary for debugging.
            ##"""
            ##if BibleOrgSysGlobals.debugFlag:
                ##if debuggingThisModule:
                    ##print( "insertAtEnd( {!r}, {} )".format( ieText, ieTags ) )
                ##assert isinstance( ieText, str )
                ##assert isinstance( ieTags, (str,tuple) )
                ##assert TRAILING_SPACE_SUBSTITUTE not in ieText
                ##assert MULTIPLE_SPACE_SUBSTITUTE not in ieText

            ### Make any requested substitutions
            ##if substituteMultipleSpaces:
                ##ieText = ieText.replace( '  ', DOUBLE_SPACE_SUBSTITUTE )
                ##ieText = ieText.replace( CLEANUP_LAST_MULTIPLE_SPACE, DOUBLE_SPACE_SUBSTITUTE )
            ##if substituteTrailingSpaces:
                ##ieText = ieText.replace( TRAILING_SPACE_LINE, TRAILING_SPACE_LINE_SUBSTITUTE )

            ##self.textBox.insert( tk.END, ieText, ieTags )
        ### end of BibleBox.displayAppendVerse.insertAtEnd


        ### Start of main code for BibleBox.displayAppendVerse
        ##try: cVM, fVM = self._contextViewMode, self._formatViewMode
        ##except AttributeError: # Must be called from a box, not a window so get settings from parent
            ##cVM, fVM = self.parentWindow._contextViewMode, self.parentWindow._formatViewMode
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( "displayAppendVerse2( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )

        ###if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ###print( "BibleBox.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
            ####try: print( "BibleBox.displayAppendVerse( {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, currentVerseFlag ) )
            ####except UnicodeEncodeError: print( "BibleBox.displayAppendVerse", firstFlag, verseKey, currentVerseFlag )

        ##BBB, C, V = verseKey.getBCV()
        ##C, V = int(C), int(V)
        ###C1 = C2 = int(C); V1 = V2 = int(V)
        ###if V1 > 0: V1 -= 1
        ###elif C1 > 0:
            ###C1 -= 1
            ###V1 = self.getNumVerses( BBB, C1 )
        ###if V2 < self.getNumVerses( BBB, C2 ): V2 += 1
        ###elif C2 < self.getNumChapters( BBB):
            ###C2 += 1
            ###V2 = 0
        ###previousMarkName = 'C{}V{}'.format( C1, V1 )
        ##currentMarkName = 'C{}V{}'.format( C, V )
        ###nextMarkName = 'C{}V{}'.format( C2, V2 )
        ###print( "Marks", previousMarkName, currentMarkName, nextMarkName )

        ##lastCharWasSpace = haveTextFlag = not firstFlag

        ##if verseContextData is None:
            ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                ##print( "  ", "displayAppendVerse has no data for", verseKey )
            ##verseDataList = context = None
        ##elif isinstance( verseContextData, tuple ):
            ##assert len(verseContextData) == 2
            ##verseDataList, context = verseContextData
            ###if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                ###print( "   VerseDataList: {}".format( verseDataList ) )
                ###print( "   Context: {}".format( context ) )
        ##elif isinstance( verseContextData, str ):
            ##verseDataList, context = verseContextData.split( '\n' ), None
        ##elif BibleOrgSysGlobals.debugFlag: halt

        ### Display the context preceding the first verse
        ##if firstFlag:
            ##if context:
                ###print( "context", context )
                ###print( "  Setting context mark to {}".format( previousMarkName ) )
                ###self.textBox.mark_set( previousMarkName, tk.INSERT )
                ###self.textBox.mark_gravity( previousMarkName, tk.LEFT )
                ##insertAtEnd( ' '+_("Prior context")+':', 'contextHeader' )
                ##contextString, firstMarker = "", True
                ##for someMarker in context:
                    ###print( "  someMarker", someMarker )
                    ##if someMarker != 'chapters':
                        ##contextString += (' ' if firstMarker else ', ') + someMarker
                        ##firstMarker = False
                ##insertAtEnd( contextString+' ', 'context' )
                ##haveTextFlag = True
            ##if verseDataList and fVM == 'Formatted':
                ### Display the first formatting marker in this segment -- don't really need this -- see below
                ###firstEntry = verseDataList[0]
                ###if isinstance( firstEntry, InternalBibleEntry ): marker = firstEntry.getMarker()
                ###elif isinstance( firstEntry, tuple ): marker = firstEntry[0]
                ###else: marker = None
                ###if marker in BibleOrgSysGlobals.USFMParagraphMarkers:
                    ###insertAtEnd( ' '+_("Current context")+': ', 'contextHeader' )
                    ###insertAtEnd( marker+' ', 'context' )
                ### Display all line markers in this segment
                ##markerList = []
                ##for verseData in verseDataList:
                    ##if isinstance( verseData, InternalBibleEntry ): marker = verseData.getMarker()
                    ##elif isinstance( verseData, tuple ): marker = verseData[0]
                    ##else: marker = None
                    ##if marker and not marker.startswith('¬') \
                    ##and not marker.endswith('~') and not marker.endswith('#'):
                        ##markerList.append( marker )
                ##if markerList:
                    ##insertAtEnd( ' '+_("Displayed markers")+': ', 'markersHeader' )
                    ##insertAtEnd( str(markerList)[1:-1], 'markers' ) # Display list without square brackets

        ###print( "  Setting mark to {}".format( currentMarkName ) )
        ##self.textBox.mark_set( currentMarkName, tk.INSERT )
        ##self.textBox.mark_gravity( currentMarkName, tk.LEFT )

        ##if verseDataList is None:
            ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                ##print( "  ", "BibleBox.displayAppendVerse has no data for", self.moduleID, verseKey )
            ###self.textBox.insert( tk.END, '--' )
        ##else:
            ###hadVerseText = False
            ###try: cVM = self._contextViewMode
            ###except AttributeError: cVM = self.parentWindow._contextViewMode
            ##lastParagraphMarker = context[-1] if context and context[-1] in BibleOrgSysGlobals.USFMParagraphMarkers \
                                        ##else 'v~' # If we don't know the format of a verse (or for unformatted Bibles)
            ##endMarkers = []

            ##for verseDataEntry in verseDataList:
                ### This loop is used for several types of data
                ##if isinstance( verseDataEntry, InternalBibleEntry ):
                    ##marker, cleanText = verseDataEntry.getMarker(), verseDataEntry.getCleanText()
                ##elif isinstance( verseDataEntry, tuple ):
                    ##marker, cleanText = verseDataEntry[0], verseDataEntry[3]
                ##elif isinstance( verseDataEntry, str ): # from a Bible text editor window
                    ##if verseDataEntry=='': continue
                    ##verseDataEntry += '\n'
                    ##if verseDataEntry[0]=='\\':
                        ##marker = ''
                        ##for char in verseDataEntry[1:]:
                            ##if char!='¬' and not char.isalnum(): break
                            ##marker += char
                        ##cleanText = verseDataEntry[len(marker)+1:].lstrip()
                    ##else:
                        ##marker, cleanText = None, verseDataEntry
                ##elif BibleOrgSysGlobals.debugFlag: halt
                ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    ##print( "  displayAppendVerse", lastParagraphMarker, haveTextFlag, marker, repr(cleanText) )

                ##if fVM == 'Unformatted':
                    ##if marker and marker[0]=='¬': pass # Ignore end markers for now
                    ##elif marker in ('intro','chapters','list',): pass # Ignore added markers for now
                    ##else:
                        ##if isinstance( verseDataEntry, str ): # from a Bible text editor window
                            ###print( "marker={!r}, verseDataEntry={!r}".format( marker, verseDataEntry ) )
                            ##insertAtEnd( verseDataEntry, marker ) # Do it just as is!
                        ##else: # not a str, i.e., not a text editor, but a viewable resource
                            ###if hadVerseText and marker in ( 's', 's1', 's2', 's3' ):
                                ###print( "  Setting s mark to {}".format( nextMarkName ) )
                                ###self.textBox.mark_set( nextMarkName, tk.INSERT )
                                ###self.textBox.mark_gravity( nextMarkName, tk.LEFT )
                            ###print( "  Inserting ({}): {!r}".format( marker, verseDataEntry ) )
                            ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            ##if marker is None:
                                ##insertAtEnd( cleanText, '###' )
                            ##else: insertAtEnd( '\\{} {}'.format( marker, cleanText ), marker+'#' )
                            ##haveTextFlag = True

                ##elif fVM == 'Formatted':
                    ##if marker.startswith( '¬' ):
                        ##if marker != '¬v': endMarkers.append( marker ) # Don't want end-verse markers
                    ##else: endMarkers = [] # Reset when we have normal markers

                    ##if marker.startswith( '¬' ):
                        ##pass # Ignore end markers for now
                        ###assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ###if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ###insertAtEnd( cleanText, marker )
                        ###haveTextFlag = True
                    ##elif marker == 'id':
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('ide','rem',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('h','toc1','toc2','toc3','cl¤',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('intro','chapters','list',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('mt1','mt2','mt3','mt4', 'imt1','imt2','imt3','imt4', 'iot','io1','io2','io3','io4',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('ip','ipi','im','imi','ipq','imq','ipr', 'iq1','iq2','iq3','iq4',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('s1','s2','s3','s4', 'is1','is2','is3','is4', 'ms1','ms2','ms3','ms4', 'cl',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('d','sp',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in ('r','mr','sr',):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##insertAtEnd( cleanText, marker )
                        ##haveTextFlag = True
                    ##elif marker in BibleOrgSysGlobals.USFMParagraphMarkers:
                        ##assert not cleanText # No text expected with these markers
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        ##lastParagraphMarker = marker
                        ##haveTextFlag = True
                    ##elif marker in ('b','ib'):
                        ##assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        ##assert not cleanText # No text expected with this marker
                        ##if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                    ###elif marker in ('m','im'):
                        ###self.textBox.insert ( tk.END, '\n' if haveTextFlag else '  ', marker )
                        ###if cleanText:
                            ###insertAtEnd( cleanText, '*'+marker if currentVerseFlag else marker )
                            ###lastCharWasSpace = False
                            ###haveTextFlag = True
                    ##elif marker == 'p#' and self.BibleBoxType=='DBPBibleResourceBox':
                        ##pass # Just ignore these for now
                    ##elif marker == 'c': # Don't want to display this (original) c marker
                        ###if not firstFlag: haveC = cleanText
                        ###else: print( "   Ignore C={}".format( cleanText ) )
                        ##pass
                    ##elif marker == 'c#': # Might want to display this (added) c marker
                        ##if cleanText != verseKey.getBBB():
                            ##if not lastCharWasSpace: insertAtEnd( ' ', 'v-' )
                            ##insertAtEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                            ##lastCharWasSpace = False
                    ##elif marker == 'v':
                        ##if cleanText != '1': # Don't display verse number for v1 in default view
                            ##if haveTextFlag:
                                ##insertAtEnd( ' ', (lastParagraphMarker,'v-',) if lastParagraphMarker else ('v-',) )
                            ##insertAtEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                            ##insertAtEnd( '\u2009', (lastParagraphMarker,'v+',) if lastParagraphMarker else ('v+',) ) # narrow space
                            ##lastCharWasSpace = haveTextFlag = True
                    ##elif marker in ('v~','p~'):
                        ##insertAtEnd( cleanText, '*'+lastParagraphMarker if currentVerseFlag else lastParagraphMarker )
                        ##haveTextFlag = True
                    ##else:
                        ##if BibleOrgSysGlobals.debugFlag:
                            ##logging.critical( _("BibleBox.displayAppendVerse (formatted): Unknown marker {!r} {!r} from {}").format( marker, cleanText, verseDataList ) )
                        ##else:
                            ##logging.critical( _("BibleBox.displayAppendVerse (formatted): Unknown marker {!r} {!r}").format( marker, cleanText ) )
                ##else:
                    ##logging.critical( _("BibleBox.displayAppendVerse: Unknown {!r} format view mode").format( fVM ) )
                    ##if BibleOrgSysGlobals.debugFlag: halt

            ##if lastFlag and cVM=='ByVerse' and endMarkers:
                ###print( "endMarkers", endMarkers )
                ##insertAtEnd( ' '+ _("End context")+':', 'contextHeader' )
                ##contextString, firstMarker = "", True
                ##for someMarker in endMarkers:
                    ###print( "  someMarker", someMarker )
                    ##contextString += (' ' if firstMarker else ', ') + someMarker
                    ##firstMarker = False
                ##insertAtEnd( contextString+' ', 'context' )
    ### end of BibleBox.displayAppendVerse


    ##def getBeforeAndAfterBibleData( self, newVerseKey ):
        ##"""
        ##Returns the requested verse, the previous verse, and the next n verses.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag:
            ##print( "BibleBox.getBeforeAndAfterBibleData( {} )".format( newVerseKey ) )
            ##assert isinstance( newVerseKey, SimpleVerseKey )

        ##BBB, C, V = newVerseKey.getBCV()
        ##intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        ### Determine the PREVIOUS valid verse numbers
        ##prevBBB, prevIntC, prevIntV = BBB, intC, intV
        ##previousVersesData = []
        ##for n in range( -self.parentApp.viewVersesBefore, 0 ):
            ##failed = False
            ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                ##print( "  getBeforeAndAfterBibleData here with", n, prevIntC, prevIntV )
            ##if prevIntV > 0: prevIntV -= 1
            ##elif prevIntC > 0:
                ##prevIntC -= 1
                ##try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                ##except KeyError:
                    ##if prevIntC != 0: # we can expect an error for chapter zero
                        ##logging.error( _("BibleBox.getBeforeAndAfterBibleData1 failed at {} {}").format( prevBBB, prevIntC ) )
                    ##failed = True
                ###if not failed:
                    ###if BibleOrgSysGlobals.debugFlag: print( " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            ##else:
                ##try: prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                ##except KeyError: prevBBB = None
                ##if prevBBB is None: failed = True
                ##else:
                    ##prevIntC = self.getNumChapters( prevBBB )
                    ##prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                        ##print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
                    ##if prevIntC is None or prevIntV is None:
                        ##logging.error( _("BibleBox.getBeforeAndAfterBibleData2 failed at {} {}:{}").format( prevBBB, prevIntC, prevIntV ) )
                        ###failed = True
                        ##break
            ##if not failed and prevIntV is not None:
                ###print( "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                ##assert prevBBB and isinstance(prevBBB, str)
                ##previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                ##previousVerseData = self.getCachedVerseData( previousVerseKey )
                ##if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        ### Determine the NEXT valid verse numbers
        ##nextBBB, nextIntC, nextIntV = BBB, intC, intV
        ##nextVersesData = []
        ##for n in range( self.parentApp.viewVersesAfter ):
            ##try: numVerses = self.getNumVerses( nextBBB, nextIntC )
            ##except KeyError: numVerses = None # for an invalid BBB
            ##nextIntV += 1
            ##if numVerses is None or nextIntV > numVerses:
                ##nextIntV = 1
                ##nextIntC += 1 # Need to check…
            ##nextVerseKey = SimpleVerseKey( nextBBB, nextIntC, nextIntV )
            ##nextVerseData = self.getCachedVerseData( nextVerseKey )
            ##if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        ### Get the CURRENT verse data
        ##verseData = self.getCachedVerseData( newVerseKey )

        ##return verseData, previousVersesData, nextVersesData
    ### end of BibleBox.getBeforeAndAfterBibleData


    ##def doBibleFind( self, event=None ):
        ##"""
        ##Get the search parameters and then execute the search.

        ##Note that BibleFind works on the imported files,
            ##so it can work from any box or window that has an internalBible.
        ##"""
        ##from BiblelatorDialogs import GetBibleFindTextDialog

        ##self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'BibleBox doBibleFind' )
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( "BibleBox.doBibleFind( {} )".format( event ) )

        ##try: haveInternalBible = self.internalBible is not None
        ##except AttributeError: haveInternalBible = False
        ##if not haveInternalBible:
            ##logging.critical( _("No Bible to search") )
            ##return
        ###print( "intBib", self.internalBible )

        ##self.BibleFindOptionsDict['currentBCV'] = self.currentVerseKey.getBCV()
        ##gBSTD = GetBibleFindTextDialog( self, self.internalBible, self.BibleFindOptionsDict, title=_('Find in Bible') )
        ##if BibleOrgSysGlobals.debugFlag: print( "gBSTDResult", repr(gBSTD.result) )
        ##if gBSTD.result:
            ##if BibleOrgSysGlobals.debugFlag: assert isinstance( gBSTD.result, dict )
            ##self.BibleFindOptionsDict = gBSTD.result # Update our search options dictionary
            ##self.doActualBibleFind()
        ##self.parentApp.setReadyStatus()

        ###return tkBREAK
    ### end of BibleBox.doBibleFind


    ##def doActualBibleFind( self, extendTo=None ):
        ##"""
        ##This function (called by the above doBibleFind),
            ##invokes the actual search (or redoes the search)
            ##assuming that the search parameters are already defined.
        ##"""
        ##from ChildWindows import FindResultWindow

        ##self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'BibleBox doActualBibleFind' )
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( "BibleBox.doActualBibleFind( {} )".format( extendTo ) )

        ##self.parentApp.setWaitStatus( _("Searching…") )
        ###self.textBox.update()
        ###self.textBox.focus()
        ###self.lastfind = key
        ##self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, ' doActualBibleFind {}'.format( self.BibleFindOptionsDict ) )
        ###print( "bookList", repr(self.BibleFindOptionsDict['bookList']) )
        ##bookCode = None
        ##if isinstance( self.BibleFindOptionsDict['bookList'], str ) \
        ##and self.BibleFindOptionsDict['bookList'] != 'ALL':
            ##bookCode = self.BibleFindOptionsDict['bookList']
        ##self._prepareInternalBible( bookCode, self.BibleFindOptionsDict['givenBible'] ) # Make sure that all books are loaded
        ### We search the loaded Bible processed lines
        ##self.BibleFindOptionsDict, resultSummaryDict, findResultList = self.BibleFindOptionsDict['givenBible'].findText( self.BibleFindOptionsDict )
        ###print( "Got findResults", findResults )
        ##if len(findResultList) == 0: # nothing found
            ##errorBeep()
            ##key = self.BibleFindOptionsDict['findText']
            ##showError( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:18]+'…') ) )
        ##else:
            ##try: replaceFunction = self.doBibleReplace
            ##except AttributeError: replaceFunction = None # Read-only Bible boxes don't have a replace function
            ##findResultWindow = FindResultWindow( self, self.BibleFindOptionsDict, resultSummaryDict, findResultList,
                                    ##findFunction=self.doBibleFind, refindFunction=self.doActualBibleFind,
                                    ##replaceFunction=replaceFunction, extendTo=extendTo )
            ##self.parentApp.childWindows.append( findResultWindow )
        ##self.parentApp.setReadyStatus()
    ### end of BibleBox.doActualBibleFind


    ##def _prepareInternalBible( self, bookCode=None, givenBible=None ):
        ##"""
        ##Prepare to do a search on the Internal Bible object
            ##or to do some of the exports or checks available in BibleOrgSysGlobals.

        ##Note that this function saves the current book if it's modified.

        ##If a bookcode is specified, loads only that book (so the user doesn't have to wait).

        ##Leaves the wait cursor displayed.
        ##"""
        ##logging.debug( "BibleBox._prepareInternalBible()" )
        ##if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            ##print( "BibleBox._prepareInternalBible()" )
        ##if givenBible is None: givenBible = self.internalBible

        ##if self.modified(): self.doSave() # NOTE: Read-only boxes/windows don't even have a doSave() function
        ##if givenBible is not None:
            ##self.parentApp.setWaitStatus( _("Preparing internal Bible…") )
            ##if bookCode is None:
                ##self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible…") )
                ##givenBible.load()
            ##else:
                ##self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible book…") )
                ##givenBible.loadBook( bookCode )
    ### end of BibleBox._prepareInternalBible
## end of class BibleBox



class HebrewInterlinearBibleBoxAddon( BibleBoxAddon ):
    """
    A set of functions that work for a Hebrew Bible frame or window that has a member: self.textBox
        and also has a member: self.internalBible and uses verseKeys
        and displays text in multi-line (interlinear) chunks.

    "self" here is a HebrewBibleResourceWindow.
    """
    def __init__( self, parentWindow, numInterlinearLines ):
        """
        This function is not needed at all, except for debug tracing of __init__ functions (when used).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "HebrewInterlinearBibleBoxAddon.__init__( {}, nIL={} )".format( parentWindow, numInterlinearLines ) )
            assert parentWindow
            assert 0 < numInterlinearLines <= 5
        self.numInterlinearLines = numInterlinearLines

        BibleBoxAddon.__init__( self, parentWindow, 'HebrewInterlinearBibleBoxAddon' )
        self.tabStopCm = 3.0
        self.textBox.config( tabs='3.0c' ) # centimeters'
        self.pixelsPerCm =  self.parentWindow.parentApp.rootWindow.winfo_fpixels( '1c' ) # gives 37.85488958990536 for me for 2.5c
        self.tabStopPixels = self.tabStopCm * self.pixelsPerCm

        self.entryStylesNormal = ( 'HebWord', 'HebStrong', 'HebMorph', 'HebGenericGloss', 'HebSpecificGloss' )
        self.entryStylesSelected = ( 'HebWordSelected', 'HebStrongSelected', 'HebMorphSelected', 'HebGenericGlossSelected', 'HebSpecificGlossSelected' )
        self.fontsNormal, self.fontsSelected = [], []
        #tabWidthsNormal, tabWidthsSelected = [], []
        for entryStyleNormal,entryStyleSelected in zip( self.entryStylesNormal, self.entryStylesSelected ):
            fontNormal = tkFont.Font( **self.parentWindow.parentApp.stylesheet.getTKStyleDict( entryStyleNormal ) )
            fontSelected = tkFont.Font( **self.parentWindow.parentApp.stylesheet.getTKStyleDict( entryStyleSelected ) )
            self.fontsNormal.append( fontNormal )
            self.fontsSelected.append( fontSelected )
            #tabWidthNormal = fontNormal.measure( ' '*8 ) # Typically gives around 24 (pixels?)
            #tabWidthSelected = fontSelected.measure( ' '*8 ) # Typically gives around 32 (pixels?)
            ##print( "tabWidths", tabWidthNormal, tabWidthSelected )
            #tabWidthsNormal.append( tabWidthNormal )
            #tabWidthsSelected.append( tabWidthSelected )

        self.requestMissingGlosses, self.glossWindowGeometry = True, None

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "HebrewInterlinearBibleBoxAddon.__init__ finished." )
    # end of HebrewInterlinearBibleBoxAddon.__init__


    def displayAppendVerse( self, firstFlag, verseKey, verseContextData, lastFlag=True, currentVerseFlag=False, currentWordNumber=1, command=None, substituteTrailingSpaces=False, substituteMultipleSpaces=False ):
        """
        Add the requested verse to the end of self.textBox.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.

        Usually called from updateShownBCV from the subclass.
        Note that it's used in both formatted and unformatted (even edit) windows.

        command can be 'E' for edit, i.e., if a bundle has been double-clicked
        """
        if BibleOrgSysGlobals.debugFlag:
            if debuggingThisModule:
                print( "HebrewInterlinearBibleBoxAddon.displayAppendVerse( fF={}, {}, {}, lF={}, cVF={}, cWN={}, c={}, sTS={}, sMS={} )" \
                    .format( firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, currentWordNumber, command, substituteTrailingSpaces, substituteMultipleSpaces ) )
                print( "  {}".format( verseContextData[0] ) )
            assert isinstance( firstFlag, bool )
            assert isinstance( verseKey, SimpleVerseKey )
            if verseContextData:
                assert isinstance( verseContextData, tuple ) and len(verseContextData)==2 or isinstance( verseContextData, str )
            assert isinstance( lastFlag, bool )
            assert isinstance( currentVerseFlag, bool )
        self.lastDAVargs = firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, currentWordNumber, None, substituteTrailingSpaces, substituteMultipleSpaces

        self.update() # so we can get the geometry
        boxWidth = self.textBox.winfo_width()
        #print( "boxWidth", boxWidth ) # in pixels (gives 585 for me)
        self.bundlesPerLine = int( boxWidth / (self.tabStopCm * self.pixelsPerCm) ) + 1
        #print( "bundlesPerLine", self.bundlesPerLine )


        def insertAtEnd( ieText, ieTags ):
            """
            Insert the formatted text into the end of the textbox.

            The function mostly exists so we can print the parameters if necessary for debugging.
            """
            if BibleOrgSysGlobals.debugFlag:
                if debuggingThisModule:
                    print( "insertAtEnd( {!r}, {} )".format( ieText, ieTags ) )
                assert isinstance( ieText, str )
                assert ieTags is None or isinstance( ieTags, (str,tuple) )
                assert TRAILING_SPACE_SUBSTITUTE not in ieText
                assert MULTIPLE_SPACE_SUBSTITUTE not in ieText

            # Make any requested substitutions
            if substituteMultipleSpaces:
                ieText = ieText.replace( '  ', DOUBLE_SPACE_SUBSTITUTE )
                ieText = ieText.replace( CLEANUP_LAST_MULTIPLE_SPACE, DOUBLE_SPACE_SUBSTITUTE )
            if substituteTrailingSpaces:
                ieText = ieText.replace( TRAILING_SPACE_LINE, TRAILING_SPACE_LINE_SUBSTITUTE )

            self.textBox.insert( tk.END, ieText, ieTags )
        # end of HebrewInterlinearBibleBoxAddon.displayAppendVerse.insertAtEnd


        def insertAtEndLine( ieLineNumber, ieText, ieTags ):
            """
            Insert the formatted text into the end of the textbox.

            The function mostly exists so we can print the parameters if necessary for debugging.
            """
            if BibleOrgSysGlobals.debugFlag:
                if debuggingThisModule:
                    print( "insertAtEndLine( {}, {!r}, {} )".format( ieLineNumber, ieText, ieTags ) )
                assert isinstance( ieLineNumber, int )
                assert isinstance( ieText, str )
                assert ieTags is None or isinstance( ieTags, (str,tuple) )
                assert TRAILING_SPACE_SUBSTITUTE not in ieText
                assert MULTIPLE_SPACE_SUBSTITUTE not in ieText

            # Make any requested substitutions
            if substituteMultipleSpaces:
                ieText = ieText.replace( '  ', DOUBLE_SPACE_SUBSTITUTE )
                ieText = ieText.replace( CLEANUP_LAST_MULTIPLE_SPACE, DOUBLE_SPACE_SUBSTITUTE )
            if substituteTrailingSpaces:
                ieText = ieText.replace( TRAILING_SPACE_LINE, TRAILING_SPACE_LINE_SUBSTITUTE )

            self.textBox.mark_set( tk.INSERT, '{}.0 lineend'.format( ieLineNumber ) )
            self.textBox.insert( tk.INSERT, ieText, ieTags )
        # end of HebrewInterlinearBibleBoxAddon.displayAppendVerse.insertAtEndLine


        def appendVerseText( verseDataEntry, currentVerseKey, currentVerseFlag, currentWordNumber, command ):
            """
            Appends the (interlinear) verse text to the box (taking multiple lines)

            Always displays the available verse text first
                then may attempt to extract glosses.

            Returns True if the display needs updating/refreshing
            """
            from BiblelatorDialogs import GetHebrewGlossWordDialog, GetHebrewGlossWordsDialog
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "displayAppendVerse.appendVerseText( {}, {}, cVF={}, cWN={}, c={} )".format( verseDataEntry, currentVerseKey, currentVerseFlag, currentWordNumber, command ) )

            verseDictList = self.internalBible.getVerseDictList( verseDataEntry, currentVerseKey )
            #print( verseKey.getShortText(), "verseDictList", verseDictList )

            #self.textBox.insert( tk.END, '\n'*self.numInterlinearLines ) # Make sure we have enough blank lines
            insertAtEnd( '\n'*self.numInterlinearLines, None ) # Make sure we have enough blank lines
            haveTextFlag = False
            savedLineNumber = self.lineNumber

            requestMissingGlossesNow = needToRequestMissingGlosses = needToUpdate = False
            for passNumber in range( 1, 3 ):
                # We won't request missing glosses until we've displayed what we know first
                #print( "HebrewInterlinearBibleBoxAddon.appendVerseText: pass #{} {} {}".format( passNumber, requestMissingGlossesNow, needToRequestMissingGlosses ) )
                self.lineNumber = savedLineNumber
                self.acrossIndex = 0
                j = 0
                while j < len(verseDictList): # Can't use a for loop coz we mess with the index
                    j += 1 # j is now in range 1..len(verseDictList)
                    verseDict = verseDictList[j-1] # each verseDict represents one word or token
                    #print( "pn={}, j={}, c={}, verseDict={}".format( passNumber, j, command, verseDict ) )
                    #if bundlesAcross >= self.bundlesPerLine: # Start a new line
                        ##print( "Start new bundle line" )
                        ##self.textBox.insert( tk.END, '\n'*(self.numInterlinearLines+1) ) # Make sure we have enough blank lines
                        #insertAtEnd( '\n'*(self.numInterlinearLines+1) ) # Make sure we have enough blank lines
                        #self.lineNumber += self.numInterlinearLines + 1
                        #bundlesAcross = 0
                        #haveTextFlag = False
                    word = verseDict['word']
                    fullRefTuple = currentVerseKey.getBCV() + (str(j),)
                    refText = '{} {}:{}.{}'.format( *fullRefTuple )
                    #import Hebrew
                    #h = Hebrew.Hebrew( word )
                    #print( '{!r} is '.format( word ), end=None )
                    #h.printUnicodeData( word )
                    try: strongsNumber = verseDict['strong']
                    except KeyError: strongsNumber = ''
                    try: morphology = verseDict['morph']
                    except KeyError: morphology = ''
                    if self.numInterlinearLines == 3:
                        bundle = word, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                    elif self.numInterlinearLines == 4:
                        assert self.internalBible.glossingDict
                        normalizedWord =  self.internalBible.removeCantillationMarks( word, removeMetegOrSiluq=True ) \
                                            .replace( ORIGINAL_MORPHEME_BREAK_CHAR, OUR_MORPHEME_BREAK_CHAR )
                        #if normalizedWord != word:
                            #print( '   ({}) {!r} normalized to ({}) {!r}'.format( len(word), word, len(normalizedWord), normalizedWord ) )
                            ##print( '{!r} is '.format( normalizedWord ), end=None )
                            ##h.printUnicodeData( normalizedWord )
                        genericGloss,genericReferencesList,specificReferencesDict = self.internalBible.glossingDict[normalizedWord] \
                                                        if normalizedWord in self.internalBible.glossingDict else ('',[],{})
                        if passNumber>1 and ( command in ('L','R') or (command=='E' and j==currentWordNumber) ):
                            command = None
                            tempBundle = refText, normalizedWord, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                            #self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations( morphology ) )
                            ghgwd = GetHebrewGlossWordDialog( self, _("Edit generic gloss"), tempBundle, genericGloss, geometry=self.glossWindowGeometry )
                            #print( "ghgwdResultA1", ghgwd.result )
                            if ghgwd.result is None: # cancel
                                self.requestMissingGlosses = False
                            elif ghgwd.result == 'S': # skip
                                needToRequestMissingGlosses = False
                            elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                command = ghgwd.result
                            elif isinstance( ghgwd.result, dict ):
                                #print( "result1", ghgwd.result )
                                assert ghgwd.result['word']
                                genericGloss = ghgwd.result['word']
                                self.internalBible.setNewGenericGloss( normalizedWord, genericGloss, fullRefTuple )
                                self.glossWindowGeometry = ghgwd.result['geometry'] # Keeps the window size/position
                                try: command = ghgwd.result['command'] # 'L' or 'R'
                                except KeyError: command = None
                                needToRequestMissingGlosses = False
                                needToUpdate = True
                            else: halt # programming error
                        elif not genericGloss and BibleOrgSysGlobals.verbosityLevel > 0:
                            #print( "No generic gloss found for ({}) {}{}".format( len(word), word, \
                                #' to ({}) {}'.format( len(normalizedWord), normalizedWord ) if normalizedWord!=word else '' ) )
                            if self.requestMissingGlosses and requestMissingGlossesNow and not self.parentApp.starting:
                                tempBundle = refText, normalizedWord, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                                #self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations( morphology ) )
                                ghgwd = GetHebrewGlossWordDialog( self, _("Enter new generic gloss"), tempBundle, geometry=self.glossWindowGeometry )
                                #print( "ghgwdResultA2", ghgwd.result )
                                if ghgwd.result is None: # cancel
                                    self.requestMissingGlosses = False
                                elif ghgwd.result == 'S': # skip
                                    needToRequestMissingGlosses = False
                                elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                    command = ghgwd.result
                                elif isinstance( ghgwd.result, dict ):
                                    #print( "result2", ghgwd.result )
                                    assert ghgwd.result['word']
                                    genericGloss = ghgwd.result['word']
                                    self.internalBible.setNewGenericGloss( normalizedWord, genericGloss, fullRefTuple )
                                    self.glossWindowGeometry = ghgwd.result['geometry'] # Keeps the window size/position
                                    try: command = ghgwd.result['command'] # 'L','R','LL','RR'
                                    except KeyError: command = None
                                    needToRequestMissingGlosses = False
                                    needToUpdate = True
                                else: halt # programming error
                            else: needToRequestMissingGlosses = True
                        bundle = word, strongsNumber, morphology, genericGloss
                    elif self.numInterlinearLines == 5:
                        assert self.internalBible.glossingDict
                        normalizedWord =  self.internalBible.removeCantillationMarks( word, removeMetegOrSiluq=True ) \
                                            .replace( ORIGINAL_MORPHEME_BREAK_CHAR, OUR_MORPHEME_BREAK_CHAR )
                        #if normalizedWord != word:
                            #print( '   ({}) {!r} normalized to ({}) {!r}'.format( len(word), word, len(normalizedWord), normalizedWord ) )
                            ##print( '{!r} is '.format( normalizedWord ), end=None )
                            ##h.printUnicodeData( normalizedWord )
                        genericGloss,genericReferencesList,specificReferencesDict = self.internalBible.glossingDict[normalizedWord] \
                                                        if normalizedWord in self.internalBible.glossingDict else ('',[],{})
                        try: specificGloss = specificReferencesDict[fullRefTuple]
                        except KeyError: specificGloss = '' # No specific gloss for this reference
                        if passNumber>1 and ( command in ('L','R') or (command=='E' and j==currentWordNumber) ):
                            command = None
                            tempBundle = refText, normalizedWord, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                            #self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations( morphology ) )
                            ghgwd = GetHebrewGlossWordsDialog( self, _("Edit generic/specific glosses"), tempBundle, genericGloss, specificGloss, geometry=self.glossWindowGeometry )
                            #print( "ghgwdResultB1", ghgwd.result )
                            if ghgwd.result is None: # cancel
                                self.requestMissingGlosses = False
                            elif ghgwd.result == 'S': # skip
                                needToRequestMissingGlosses = False
                            elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                command = ghgwd.result
                            elif isinstance( ghgwd.result, dict ):
                                #print( "result3", ghgwd.result )
                                assert ghgwd.result['word1']
                                genericGloss = ghgwd.result['word1']
                                specificGloss = ghgwd.result['word2'] if 'word2' in ghgwd.result else None
                                self.internalBible.setNewGenericGloss( normalizedWord, genericGloss, fullRefTuple )
                                if specificGloss:
                                    self.internalBible.setNewSpecificGloss( normalizedWord, specificGloss, fullRefTuple )
                                self.glossWindowGeometry = ghgwd.result['geometry'] # Keeps the window size/position
                                try: command = ghgwd.result['command'] # 'L' or 'R'
                                except KeyError: command = None
                                needToRequestMissingGlosses = False
                                needToUpdate = True
                            else: halt # programming error
                        elif not genericGloss and BibleOrgSysGlobals.verbosityLevel > 0:
                            #print( "No generic gloss found for ({}) {}{}".format( len(word), word, \
                                #' to ({}) {}'.format( len(normalizedWord), normalizedWord ) if normalizedWord!=word else '' ) )
                            if self.requestMissingGlosses and requestMissingGlossesNow and not self.parentApp.starting:
                                tempBundle = refText, normalizedWord, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                                #self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations( morphology ) )
                                ghgwd = GetHebrewGlossWordsDialog( self, _("Enter new generic/specific glosses"), tempBundle, geometry=self.glossWindowGeometry )
                                #print( "ghgwdResultB2", ghgwd.result )
                                if ghgwd.result is None: # cancel
                                    self.requestMissingGlosses = False
                                elif ghgwd.result == 'S': # skip
                                    needToRequestMissingGlosses = False
                                elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                    command = ghgwd.result
                                elif isinstance( ghgwd.result, dict ):
                                    #print( "result4", ghgwd.result )
                                    assert ghgwd.result['word1']
                                    genericGloss = ghgwd.result['word1']
                                    specificGloss = ghgwd.result['word2'] if 'word2' in ghgwd.result else None
                                    self.internalBible.setNewGenericGloss( normalizedWord, genericGloss, fullRefTuple )
                                    if specificGloss:
                                        self.internalBible.setNewSpecificGloss( normalizedWord, specificGloss, fullRefTuple )
                                    self.glossWindowGeometry = ghgwd.result['geometry'] # Keeps the window size/position
                                    try: command = ghgwd.result['command'] # 'L' or 'R'
                                    except KeyError: command = None
                                    needToRequestMissingGlosses = False
                                    needToUpdate = True
                                else: halt # programming error
                            else: needToRequestMissingGlosses = True
                        bundle = word, strongsNumber, morphology, genericGloss, specificGloss
                    else: halt # Programming error for numInterlinearLines
                    if passNumber == 1:
                        appendBundle( bundle, j, j==currentWordNumber, haveTextFlag )
                    haveTextFlag = True
                    if command == 'L':
                        if j>1: j = j - 2 # Go left
                        else: command = None # Already at left side
                    elif command == 'R':
                        if j < len(verseDictList): pass
                        else: command = None # Already at right side
                    elif command == 'LL':
                        self.parentApp.doGotoPreviousVerse()
                        return False
                    elif command == 'RR':
                        self.parentApp.doGotoNextVerse()
                        return False
                    elif command == 'E': pass
                    else: assert command is None
                    #bundlesAcross += 1
                if self.parentApp.starting: break
                if command: continue
                if not self.requestMissingGlosses: break
                if not needToRequestMissingGlosses: break
                requestMissingGlossesNow = True
            return needToUpdate
        # end of HebrewInterlinearBibleBoxAddon.appendVerseText


        def appendBundle( textBundle, wordNumber, currentBundleFlag, haveTextFlag ):
            """
            Appends the (interlinear) word bundle to the box (taking multiple lines)
            """
            if BibleOrgSysGlobals.debugFlag:
                if debuggingThisModule:
                    print( "displayAppendVerse.appendBundle( {}, wN={}, cBF={}, hTF={} )".format( textBundle, wordNumber, currentBundleFlag, haveTextFlag ) )
                assert isinstance( textBundle, tuple )
                assert len(textBundle) == self.numInterlinearLines

            if currentBundleFlag:
                entryStyles, fonts = self.entryStylesSelected, self.fontsSelected
                self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations(textBundle[2]) )
            else:
                entryStyles, fonts = self.entryStylesNormal, self.fontsNormal

            # Find the width of each bundleEntry
            maxWidthPixels = 0
            bundleWidthsPixels = []
            tabStopsUsed = []
            for j,bundleEntry in enumerate( textBundle ):
                #print( "bundleEntry", bundleEntry )
                #(w,h) = (font.measure(text),font.metrics("linespace"))
                bundleWidthPixels = fonts[j].measure( bundleEntry ) + 6 # for safety
                bundleWidthsPixels.append( bundleWidthPixels )
                tabStopsUsed.append( int( bundleWidthPixels / self.tabStopPixels ) + 1 )
                #print( j, currentBundleFlag, bundleEntry, bundleWidthPixels )
                if bundleWidthPixels > maxWidthPixels: maxWidthPixels = bundleWidthPixels
            maxTabStopsUsed = int( maxWidthPixels / self.tabStopPixels ) + 1
            #if maxTabStopsUsed>1:
                #print( "  Need more tabs bWP={} tSU={} mWP={} tSP={} mTSU={} bpL={}" \
                        #.format( bundleWidthsPixels, tabStopsUsed, maxWidthPixels, self.tabStopPixels, maxTabStopsUsed, self.bundlesPerLine ) )

            if self.acrossIndex+maxTabStopsUsed >= self.bundlesPerLine: # Start a new line
                #print( "Start new bundle line" )
                #self.textBox.insert( tk.END, '\n'*(self.numInterlinearLines+1) ) # Make sure we have enough blank lines
                insertAtEnd( '\n'*(self.numInterlinearLines+1), None ) # Make sure we have enough blank lines
                self.lineNumber += self.numInterlinearLines + 1
                self.acrossIndex = 0
                haveTextFlag = False
            #print( "About to display bundle {} at row={} col={}".format( textBundle, self.lineNumber, self.acrossIndex ) )

            # Now display the actual bundles (with tabs appended)
            #for j,bundleEntry in enumerate( textBundle ):
            for j,(bundleEntry,bundleWidthPixels,thisTabStopsUsed) in enumerate( zip(textBundle,bundleWidthsPixels,tabStopsUsed) ):
                #print( "bundleEntry", bundleEntry, bundleWidthPixels )
                #print( "bundleEntry", bundleEntry )
                if j==0: bundleEntry = bundleEntry[::-1] # Reverse string to simulate RTL Hebrew language
                wTag = 'W{}.{}'.format( wordNumber, j )
                #if numTabsRequired:
                    #insertAtEndLine( self.lineNumber+j, '\t'*numTabsRequired, self.entryStylesNormal[j] )
                insertAtEndLine( self.lineNumber+j, bundleEntry, (entryStyles[j],wTag) )
                self.textBox.tag_bind( wTag, '<Button-1>', self.selectBundle )
                self.textBox.tag_bind( wTag, '<Double-Button-1>', self.editBundle )
                numTabsRequired = 1
                if maxTabStopsUsed > 1:
                    #tabStopsUsed = int( bundleWidthPixels / self.tabStopPixels )
                    numTabsRequired += maxTabStopsUsed - thisTabStopsUsed
                #print( "    Appending {} trailing tab{} to {!r}" \
                            #.format( numTabsRequired, '' if numTabsRequired==1 else 's', bundleEntry ) )
                insertAtEndLine( self.lineNumber+j, '\t'*numTabsRequired, None )
            self.acrossIndex += maxTabStopsUsed
            return maxTabStopsUsed
        # end of HebrewInterlinearBibleBoxAddon.appendBundle


        # Start of main code for HebrewInterlinearBibleBoxAddon.displayAppendVerse
        needsRefreshing = False
        while True:
            self.lineNumber = 0
            try: cVM, fVM = self._contextViewMode, self._formatViewMode
            except AttributeError: # Must be called from a box, not a window so get settings from parent
                cVM, fVM = self.parentWindow._contextViewMode, self.parentWindow._formatViewMode
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "displayAppendVerse2( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
            assert cVM == 'ByVerse'

            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #print( "HebrewInterlinearBibleBoxAddon.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
                ##try: print( "HebrewInterlinearBibleBoxAddon.displayAppendVerse( {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, currentVerseFlag ) )
                ##except UnicodeEncodeError: print( "HebrewInterlinearBibleBoxAddon.displayAppendVerse", firstFlag, verseKey, currentVerseFlag )

            BBB, C, V = verseKey.getBCV()
            C, V = int(C), int(V)
            #C1 = C2 = int(C); V1 = V2 = int(V)
            #if V1 > 0: V1 -= 1
            #elif C1 > 0:
                #C1 -= 1
                #V1 = self.getNumVerses( BBB, C1 )
            #if V2 < self.getNumVerses( BBB, C2 ): V2 += 1
            #elif C2 < self.getNumChapters( BBB):
                #C2 += 1
                #V2 = 0
            #previousMarkName = 'C{}V{}'.format( C1, V1 )
            currentMarkName = 'C{}V{}'.format( C, V )
            #nextMarkName = 'C{}V{}'.format( C2, V2 )
            #print( "Marks", previousMarkName, currentMarkName, nextMarkName )

            lastCharWasSpace = haveTextFlag = not firstFlag

            if verseContextData is None:
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                    print( "  ", "displayAppendVerse has no data for", verseKey )
                verseDataList = context = None
            elif isinstance( verseContextData, tuple ):
                assert len(verseContextData) == 2
                verseDataList, context = verseContextData
                #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    #print( "   VerseDataList: {}".format( verseDataList ) )
                    #print( "   Context: {}".format( context ) )
            elif isinstance( verseContextData, str ):
                verseDataList, context = verseContextData.split( '\n' ), None
            elif BibleOrgSysGlobals.debugFlag: halt

            # Display the context preceding the first verse
            if firstFlag:
                if context:
                    #print( "context", context )
                    #print( "  Setting context mark to {}".format( previousMarkName ) )
                    #self.textBox.mark_set( previousMarkName, tk.INSERT )
                    #self.textBox.mark_gravity( previousMarkName, tk.LEFT )
                    insertAtEnd( ' '+_("Prior context")+':', 'contextHeader' )
                    contextString, firstMarker = "", True
                    for someMarker in context:
                        #print( "  someMarker", someMarker )
                        if someMarker != 'chapters':
                            contextString += (' ' if firstMarker else ', ') + someMarker
                            firstMarker = False
                    insertAtEnd( contextString+' ', 'context' )
                    haveTextFlag = True
                    self.lineNumber += 1
                if verseDataList and fVM == 'Formatted':
                    # Display the first formatting marker in this segment -- don't really need this -- see below
                    #firstEntry = verseDataList[0]
                    #if isinstance( firstEntry, InternalBibleEntry ): marker = firstEntry.getMarker()
                    #elif isinstance( firstEntry, tuple ): marker = firstEntry[0]
                    #else: marker = None
                    #if marker in BibleOrgSysGlobals.USFMParagraphMarkers:
                        #insertAtEnd( ' '+_("Current context")+': ', 'contextHeader' )
                        #insertAtEnd( marker+' ', 'context' )
                    # Display all line markers in this segment
                    markerList = []
                    for verseData in verseDataList:
                        if isinstance( verseData, InternalBibleEntry ): marker = verseData.getMarker()
                        elif isinstance( verseData, tuple ): marker = verseData[0]
                        else: marker = None
                        if marker and not marker.startswith('¬') \
                        and not marker.endswith('~') and not marker.endswith('#'):
                            markerList.append( marker )
                    if markerList:
                        insertAtEnd( ' '+_("Displayed markers")+': ', 'markersHeader' )
                        insertAtEnd( str(markerList)[1:-1], 'markers' ) # Display list without square brackets
                        self.textBox.insert ( tk.END, ' ' )

            #print( "  Setting mark to {}".format( currentMarkName ) )
            self.textBox.mark_set( currentMarkName, tk.INSERT )
            self.textBox.mark_gravity( currentMarkName, tk.LEFT )

            if verseDataList is None:
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule and C!=0 and V!=0:
                    print( "  ", "HebrewInterlinearBibleBoxAddon.displayAppendVerse has no data for", self.moduleID, verseKey )
                #self.textBox.insert( tk.END, '--' )
            else:
                #hadVerseText = False
                #try: cVM = self._contextViewMode
                #except AttributeError: cVM = self.parentWindow._contextViewMode
                lastParagraphMarker = context[-1] if context and context[-1] in BibleOrgSysGlobals.USFMParagraphMarkers \
                                            else 'v~' # If we don't know the format of a verse (or for unformatted Bibles)
                endMarkers = []

                for verseDataEntry in verseDataList:
                    # This loop is used for several types of data
                    assert isinstance( verseDataEntry, InternalBibleEntry )
                    marker, cleanText, extras = verseDataEntry.getMarker(), verseDataEntry.getCleanText(), verseDataEntry.getExtras()
                    adjustedText, originalText = verseDataEntry.getAdjustedText(), verseDataEntry.getOriginalText()
                    #print( "marker={} cleanText={!r}{}".format( marker, cleanText, " extras={}".format( extras ) if extras else '' ) )
                    #print( "marker={} cleanText={!r} extras={}".format( marker, cleanText, extras ) )
                    #if adjustedText and adjustedText!=cleanText:
                        #print( ' '*(len(marker)+4), "adjustedText={!r}".format( adjustedText ) )
                    #if originalText and originalText!=cleanText:
                        #print( ' '*(len(marker)+4), "originalText={!r}".format( originalText ) )
                    #elif isinstance( verseDataEntry, tuple ):
                        #marker, cleanText = verseDataEntry[0], verseDataEntry[3]
                    #elif isinstance( verseDataEntry, str ): # from a Bible text editor window
                        #if verseDataEntry=='': continue
                        #verseDataEntry += '\n'
                        #if verseDataEntry[0]=='\\':
                            #marker = ''
                            #for char in verseDataEntry[1:]:
                                #if char!='¬' and not char.isalnum(): break
                                #marker += char
                            #cleanText = verseDataEntry[len(marker)+1:].lstrip()
                        #else:
                            #marker, cleanText = None, verseDataEntry
                    #elif BibleOrgSysGlobals.debugFlag: halt
                    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                        print( "  displayAppendVerse", lastParagraphMarker, haveTextFlag, marker, repr(cleanText) )

                    if fVM == 'Unformatted':
                        if marker and marker[0]=='¬': pass # Ignore end markers for now
                        elif marker in ('intro','chapters','list',): pass # Ignore added markers for now
                        else:
                            if isinstance( verseDataEntry, str ): # from a Bible text editor window
                                #print( "marker={!r}, verseDataEntry={!r}".format( marker, verseDataEntry ) )
                                insertAtEnd( verseDataEntry, marker ) # Do it just as is!
                            else: # not a str, i.e., not a text editor, but a viewable resource
                                #if hadVerseText and marker in ( 's', 's1', 's2', 's3' ):
                                    #print( "  Setting s mark to {}".format( nextMarkName ) )
                                    #self.textBox.mark_set( nextMarkName, tk.INSERT )
                                    #self.textBox.mark_gravity( nextMarkName, tk.LEFT )
                                #print( "  Inserting ({}): {!r}".format( marker, verseDataEntry ) )
                                if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                                if marker is None:
                                    insertAtEnd( cleanText, '###' )
                                else: insertAtEnd( '\\{} {}'.format( marker, cleanText ), marker+'#' )
                                haveTextFlag = True

                    elif fVM == 'Formatted':
                        if marker.startswith( '¬' ):
                            if marker != '¬v': endMarkers.append( marker ) # Don't want end-verse markers
                        else: endMarkers = [] # Reset when we have normal markers

                        if marker.startswith( '¬' ):
                            pass # Ignore end markers for now
                            #assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            #if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            #insertAtEnd( cleanText, marker )
                            #haveTextFlag = True
                        elif marker == 'id':
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('ide','rem',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('h','toc1','toc2','toc3','cl¤',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('intro','chapters','list',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('mt1','mt2','mt3','mt4', 'imt1','imt2','imt3','imt4', 'iot','io1','io2','io3','io4',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('ip','ipi','im','imi','ipq','imq','ipr', 'iq1','iq2','iq3','iq4',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('s1','s2','s3','s4', 'is1','is2','is3','is4', 'ms1','ms2','ms3','ms4', 'cl',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('d','sp',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in ('r','mr','sr',):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            insertAtEnd( cleanText, marker )
                            haveTextFlag = True
                        elif marker in BibleOrgSysGlobals.USFMParagraphMarkers:
                            assert not cleanText # No text expected with these markers
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                            lastParagraphMarker = marker
                            haveTextFlag = True
                        elif marker in ('b','ib'):
                            assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                            assert not cleanText # No text expected with this marker
                            if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        #elif marker in ('m','im'):
                            #self.textBox.insert ( tk.END, '\n' if haveTextFlag else '  ', marker )
                            #if cleanText:
                                #insertAtEnd( cleanText, '*'+marker if currentVerseFlag else marker )
                                #lastCharWasSpace = False
                                #haveTextFlag = True
                        #elif marker == 'p#': # and self.BibleBoxType=='DBPBibleResourceBox':
                            #pass # Just ignore these for now
                        elif marker == 'c': # Don't want to display this (original) c marker
                            #if not firstFlag: haveC = cleanText
                            #else: print( "   Ignore C={}".format( cleanText ) )
                            pass
                        elif marker == 'c#': # Might want to display this (added) c marker
                            if cleanText != verseKey.getBBB():
                                if not lastCharWasSpace: insertAtEnd( ' ', 'v-' )
                                insertAtEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                                lastCharWasSpace = False
                        elif marker == 'v':
                            if cleanText != '1': # Don't display verse number for v1 in default view
                                if haveTextFlag:
                                    insertAtEnd( ' ', (lastParagraphMarker,'v-',) if lastParagraphMarker else ('v-',) )
                                insertAtEnd( cleanText, (lastParagraphMarker,marker,) if lastParagraphMarker else (marker,) )
                                #insertAtEnd( '\u2009', (lastParagraphMarker,'v+',) if lastParagraphMarker else ('v+',) ) # narrow space
                            insertAtEnd( '\n', (lastParagraphMarker,'v+',) if lastParagraphMarker else ('v+',) ) # narrow space
                            haveTextFlag = True
                            self.lineNumber += 1
                        elif marker in ('v~','p~'):
                            needsRefreshing = appendVerseText( verseDataEntry, verseKey, currentVerseFlag, currentWordNumber=currentWordNumber, command=command )
                            command = None # So we don't repeat it
                            haveTextFlag = True
                        else:
                            if BibleOrgSysGlobals.debugFlag:
                                logging.critical( _("HebrewInterlinearBibleBoxAddon.displayAppendVerse (formatted): Unknown marker {!r} {!r} from {}").format( marker, cleanText, verseDataList ) )
                            else:
                                logging.critical( _("HebrewInterlinearBibleBoxAddon.displayAppendVerse (formatted): Unknown marker {!r} {!r}").format( marker, cleanText ) )
                    else:
                        logging.critical( _("HebrewInterlinearBibleBoxAddon.displayAppendVerse: Unknown {!r} format view mode").format( fVM ) )
                        if BibleOrgSysGlobals.debugFlag: halt

                if lastFlag and cVM=='ByVerse' and endMarkers:
                    #print( "endMarkers", endMarkers )
                    insertAtEnd( ' '+ _("End context")+':', 'contextHeader' )
                    contextString, firstMarker = "", True
                    for someMarker in endMarkers:
                        #print( "  someMarker", someMarker )
                        contextString += (' ' if firstMarker else ', ') + someMarker
                        firstMarker = False
                    insertAtEnd( contextString+' ', 'context' )
            if needsRefreshing: self.clearText() # Do another round
            else: break
    # end of HebrewInterlinearBibleBoxAddon.displayAppendVerse


    def _getBundleNumber( self, event ):
        """
        Give a mouse event, get the bundleNumber underneath it.
        """
        # get the index of the mouse cursor from the event.x and y attributes
        xy = '@{0},{1}'.format( event.x, event.y )
        #print( "xy", repr(xy) ) # e.g.., '@34,77'
        #print( "ixy", repr(self.textBox.index(xy)) ) # e.g., '4.3'

        tagNames = self.textBox.tag_names( xy )
        #print( "tn", tagNames )
        for tagName in tagNames:
            if tagName.startswith( 'W' ):
                bundleNumber = tagName[1:]
                assert '.' in bundleNumber
                #print( "bundleNumber", repr(bundleNumber) )
                return bundleNumber
    # end of HebrewInterlinearBibleBoxAddon._getBundleNumber

    def selectBundle( self, event ):
        """
        Handle a left-click on a bundle.

        Splits bundleNumber into a
            word number (e.g., first word is word 1) and
            line number (e.g., first line in bundle is line 0).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "HebrewInterlinearBibleBoxAddon.selectBundle()" )

        bundleNumber = self._getBundleNumber( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #print( "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #print( "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #print( "Clicked on {}".format( repr(clickedText) ) )

        if bundleNumber:
            wordNumberString, lineNumberString = bundleNumber.split( '.', 1 )
            #print( "select", "wn", wordNumberString, "ln", lineNumberString )
            self.clearText() # Leaves the text box enabled
            self.displayAppendVerse( self.lastDAVargs[0], self.lastDAVargs[1], self.lastDAVargs[2], self.lastDAVargs[3], self.lastDAVargs[4], int(wordNumberString), None, self.lastDAVargs[7], self.lastDAVargs[8] )
    # end of HebrewInterlinearBibleBoxAddon.selectBundle

    def editBundle( self, event ):
        """
        Handle a double-click on a bundle.

        Splits bundleNumber into a
            word number (e.g., first word is word 1) and
            line number (e.g., first line in bundle is line 0).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "HebrewInterlinearBibleBoxAddon.editBundle()" )

        bundleNumber = self._getBundleNumber( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #print( "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #print( "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #print( "Clicked on {}".format( repr(clickedText) ) )

        if bundleNumber:
            wordNumberString, lineNumberString = bundleNumber.split( '.', 1 )
            #print( "edit", "wn", wordNumberString, "ln", lineNumberString )
            self.clearText() # Leaves the text box enabled
            self.displayAppendVerse( self.lastDAVargs[0], self.lastDAVargs[1], self.lastDAVargs[2], self.lastDAVargs[3], self.lastDAVargs[4], int(wordNumberString), 'E', self.lastDAVargs[7], self.lastDAVargs[8] )
    # end of HebrewInterlinearBibleBoxAddon.editBundle


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden if an edit box needs to save files first.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "HebrewInterlinearBibleBoxAddon.doClose( {} )".format( event ) )

        try: self.internalBible.saveAnyChangedGlosses()
        except AttributeError: # if self.internalBible is None
            if debuggingThisModule: print( "Why is Hebrew internalBible None?" )

        self.destroy()
    # end of HebrewInterlinearBibleBoxAddon.doClose


    #def getBeforeAndAfterBibleData( self, newVerseKey ):
        #"""
        #Returns the requested verse, the previous verse, and the next n verses.
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #print( "HebrewInterlinearBibleBoxAddon.getBeforeAndAfterBibleData( {} )".format( newVerseKey ) )
            #assert isinstance( newVerseKey, SimpleVerseKey )

        #BBB, C, V = newVerseKey.getBCV()
        #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        ## Determine the PREVIOUS valid verse numbers
        #prevBBB, prevIntC, prevIntV = BBB, intC, intV
        #previousVersesData = []
        #for n in range( -self.parentApp.viewVersesBefore, 0 ):
            #failed = False
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #print( "  getBeforeAndAfterBibleData here with", n, prevIntC, prevIntV )
            #if prevIntV > 0: prevIntV -= 1
            #elif prevIntC > 0:
                #prevIntC -= 1
                #try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                #except KeyError:
                    #if prevIntC != 0: # we can expect an error for chapter zero
                        #logging.error( _("HebrewInterlinearBibleBoxAddon.getBeforeAndAfterBibleData1 failed at {} {}").format( prevBBB, prevIntC ) )
                    #failed = True
                ##if not failed:
                    ##if BibleOrgSysGlobals.debugFlag: print( " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            #else:
                #try: prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                #except KeyError: prevBBB = None
                #if prevBBB is None: failed = True
                #else:
                    #prevIntC = self.getNumChapters( prevBBB )
                    #prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                        #print( " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
                    #if prevIntC is None or prevIntV is None:
                        #logging.error( _("HebrewInterlinearBibleBoxAddon.getBeforeAndAfterBibleData2 failed at {} {}:{}").format( prevBBB, prevIntC, prevIntV ) )
                        ##failed = True
                        #break
            #if not failed and prevIntV is not None:
                ##print( "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                #assert prevBBB and isinstance(prevBBB, str)
                #previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                #previousVerseData = self.getCachedVerseData( previousVerseKey )
                #if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        ## Determine the NEXT valid verse numbers
        #nextBBB, nextIntC, nextIntV = BBB, intC, intV
        #nextVersesData = []
        #for n in range( self.parentApp.viewVersesAfter ):
            #try: numVerses = self.getNumVerses( nextBBB, nextIntC )
            #except KeyError: numVerses = None # for an invalid BBB
            #nextIntV += 1
            #if numVerses is None or nextIntV > numVerses:
                #nextIntV = 1
                #nextIntC += 1 # Need to check…
            #nextVerseKey = SimpleVerseKey( nextBBB, nextIntC, nextIntV )
            #nextVerseData = self.getCachedVerseData( nextVerseKey )
            #if nextVerseData: nextVersesData.append( (nextVerseKey,nextVerseData,) )

        ## Get the CURRENT verse data
        #verseData = self.getCachedVerseData( newVerseKey )

        #return verseData, previousVersesData, nextVersesData
    ## end of HebrewInterlinearBibleBoxAddon.getBeforeAndAfterBibleData


    #def doBibleFind( self, event=None ):
        #"""
        #Get the search parameters and then execute the search.

        #Note that BibleFind works on the imported files,
            #so it can work from any box or window that has an internalBible.
        #"""
        #from BiblelatorDialogs import GetBibleFindTextDialog

        #self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'HebrewInterlinearBibleBoxAddon doBibleFind' )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "HebrewInterlinearBibleBoxAddon.doBibleFind( {} )".format( event ) )

        #try: haveInternalBible = self.internalBible is not None
        #except AttributeError: haveInternalBible = False
        #if not haveInternalBible:
            #logging.critical( _("No Bible to search") )
            #return
        ##print( "intBib", self.internalBible )

        #self.BibleFindOptionsDict['currentBCV'] = self.currentVerseKey.getBCV()
        #gBSTD = GetBibleFindTextDialog( self, self.internalBible, self.BibleFindOptionsDict, title=_('Find in Bible') )
        #if BibleOrgSysGlobals.debugFlag: print( "gBSTDResult", repr(gBSTD.result) )
        #if gBSTD.result:
            #if BibleOrgSysGlobals.debugFlag: assert isinstance( gBSTD.result, dict )
            #self.BibleFindOptionsDict = gBSTD.result # Update our search options dictionary
            #self.doActualBibleFind()
        #self.parentApp.setReadyStatus()

        ##return tkBREAK
    ## end of HebrewInterlinearBibleBoxAddon.doBibleFind


    #def doActualBibleFind( self, extendTo=None ):
        #"""
        #This function (called by the above doBibleFind),
            #invokes the actual search (or redoes the search)
            #assuming that the search parameters are already defined.
        #"""
        #from ChildWindows import FindResultWindow

        #self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, 'HebrewInterlinearBibleBoxAddon doActualBibleFind' )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "HebrewInterlinearBibleBoxAddon.doActualBibleFind( {} )".format( extendTo ) )

        #self.parentApp.setWaitStatus( _("Searching…") )
        ##self.textBox.update()
        ##self.textBox.focus()
        ##self.lastfind = key
        #self.parentApp.logUsage( PROGRAM_NAME, debuggingThisModule, ' doActualBibleFind {}'.format( self.BibleFindOptionsDict ) )
        ##print( "bookList", repr(self.BibleFindOptionsDict['bookList']) )
        #bookCode = None
        #if isinstance( self.BibleFindOptionsDict['bookList'], str ) \
        #and self.BibleFindOptionsDict['bookList'] != 'ALL':
            #bookCode = self.BibleFindOptionsDict['bookList']
        #self._prepareInternalBible( bookCode, self.BibleFindOptionsDict['givenBible'] ) # Make sure that all books are loaded
        ## We search the loaded Bible processed lines
        #self.BibleFindOptionsDict, resultSummaryDict, findResultList = self.BibleFindOptionsDict['givenBible'].findText( self.BibleFindOptionsDict )
        ##print( "Got findResults", findResults )
        #if len(findResultList) == 0: # nothing found
            #errorBeep()
            #key = self.BibleFindOptionsDict['findText']
            #showError( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:18]+'…') ) )
        #else:
            #try: replaceFunction = self.doBibleReplace
            #except AttributeError: replaceFunction = None # Read-only Bible boxes don't have a replace function
            #findResultWindow = FindResultWindow( self, self.BibleFindOptionsDict, resultSummaryDict, findResultList,
                                    #findFunction=self.doBibleFind, refindFunction=self.doActualBibleFind,
                                    #replaceFunction=replaceFunction, extendTo=extendTo )
            #self.parentApp.childWindows.append( findResultWindow )
        #self.parentApp.setReadyStatus()
    ## end of HebrewInterlinearBibleBoxAddon.doActualBibleFind


    #def _prepareInternalBible( self, bookCode=None, givenBible=None ):
        #"""
        #Prepare to do a search on the Internal Bible object
            #or to do some of the exports or checks available in BibleOrgSysGlobals.

        #Note that this function saves the current book if it's modified.

        #If a bookcode is specified, loads only that book (so the user doesn't have to wait).

        #Leaves the wait cursor displayed.
        #"""
        #logging.debug( "HebrewInterlinearBibleBoxAddon._prepareInternalBible()" )
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "HebrewInterlinearBibleBoxAddon._prepareInternalBible()" )
        #if givenBible is None: givenBible = self.internalBible

        #if self.modified(): self.doSave() # NOTE: Read-only boxes/windows don't even have a doSave() function
        #if givenBible is not None:
            #self.parentApp.setWaitStatus( _("Preparing internal Bible…") )
            #if bookCode is None:
                #self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible…") )
                #givenBible.load()
            #else:
                #self.parentApp.setWaitStatus( _("Loading/Preparing internal Bible book…") )
                #givenBible.loadBook( bookCode )
    ## end of HebrewInterlinearBibleBoxAddon._prepareInternalBible
# end of class HebrewInterlinearBibleBoxAddon



def demo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

    tkRootWindow = Tk()
    tkRootWindow.title( f'{programNameVersion} {_("last modified")} {LAST_MODIFIED_DATE}' if BibleOrgSysGlobals.debugFlag else programNameVersion )

    HTMLTextBoxbox = HTMLTextBox( tkRootWindow )
    HTMLTextBoxbox.pack()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( programNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of TextBoxes.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of TextBoxes.py
