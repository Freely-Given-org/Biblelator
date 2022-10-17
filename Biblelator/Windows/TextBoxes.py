#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# TextBoxes.py
#
# Base of various textboxes for use as widgets and base classes in various windows.
#
# Copyright (C) 2013-2022 Robert Hunt
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
        __init__( self )
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
        __init__( self )
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

    fullDemo()
"""
from gettext import gettext as _
from typing import Optional
import logging

import tkinter as tk
import tkinter.font as tkFont
from tkinter.ttk import Entry, Combobox
from tkinter.simpledialog import askstring, askinteger

# PyPI imports
from markdown import markdown

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint
from BibleOrgSys.Internals.InternalBibleInternals import InternalBibleEntry
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey
from BibleOrgSys.Reference.BibleStylesheets import DEFAULT_FONTNAME, DEFAULT_FONTSIZE
from BibleOrgSys.OriginalLanguages.HebrewWLCBible import ORIGINAL_MORPHEME_BREAK_CHAR, OUR_MORPHEME_BREAK_CHAR

# Biblelator imports
if __name__ == '__main__':
    import sys
    import os
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator import BiblelatorGlobals
from Biblelator.BiblelatorGlobals import APP_NAME, tkSTART, DEFAULT, errorBeep, BIBLE_FORMAT_VIEW_MODES
from Biblelator.Dialogs.BiblelatorSimpleDialogs import showError, showInfo


LAST_MODIFIED_DATE = '2022-07-17' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorTextBoxes"
PROGRAM_NAME = "Biblelator specialised text widgets"
PROGRAM_VERSION = '0.47'
PROGRAM_NAME_VERSION = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

DEBUGGING_THIS_MODULE = False


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
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BEntry.__init__( {}, {} )".format( args, kwargs ) )
        #Entry.__init__( self, *args, **kwargs ) # initialise the base class
        #CallbackAddon.__init__( self ) # initialise the base class
    ## end of BEntry.__init__
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
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BCombobox.__init__( {}, {} )".format( args, kwargs ) )
        #Combobox.__init__( self, *args, **kwargs ) # initialise the base class
        #CallbackAddon.__init__( self ) # initialise the base class
    ## end of BCombobox.__init__
# end of BCombobox class

class BText( tk.Text ):
    """
    A custom Text widget with our own keyboard bindings/short-cuts.

    BText stands for Biblelator Text (box).
    """
    # def __init__( self, *args, **kwargs ):
    #     """
    #     Initialise the text widget and then set our own keyboard bindings.
    #     """
    #     vPrint( 'Never', DEBUGGING_THIS_MODULE, f"BText.__init__( {args}, {kwargs} )…" )

    #     # tk.apply( tk.Text.__init__, (self, master), kwargs ) # Run the init of the base class
    #     super().__init__( *args, **kwargs )

    #     self.textType = None # plain text, cf. markdown or something
    #     self.textDisplayType = DEFAULT # cf. raw or something

        # Now set-up our "default" keyboard bindings
        # self.bind( … )
# end of BText class



class HTMLTextBox( BText ):
    """
    A custom Text widget which understands and displays simple HTML.

    It currently accepts:
        heading tags:           h1,h2,h3
        paragraph tags:         p, li
        formatting tags:        span
        hard-formatting tags:   i, b, em

    For the styling, class names are appended to the tag names,
        e.g., <span class="Word"> would give an internal style of "spanWord".
    """
    def __init__( self, *args, **kwargs ):
        """
        """
        fnPrint( DEBUGGING_THIS_MODULE, f"HTMLTextBox.__init__( {args}, {kwargs} )" )
        super().__init__( *args, **kwargs ) # initialise the base class

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

            'p_spanStrongsRef': { 'foreground':'blue', 'background':'pink', 'font':standardFont },

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
        if DEBUGGING_THIS_MODULE:
            for tag in self.styleDict:
                if tag.endswith( '_a' ): assert tag in aTags
        for tag in aTags:
            assert tag in self.styleDict
            self.tag_bind( tag, '<Button-1>', self.openHyperlink )
            #self.tag_bind( tag, '<Enter>', self.overHyperlink )
            #self.tag_bind( tag, '<Leave>', self.leaveHyperlink )

        self._lastOverLink = None
    # end of HTMLTextBox.__init__


    def insert( self, point, iText ) -> None:
        """
        """
        fnPrint( DEBUGGING_THIS_MODULE, f"HTMLTextBox.insert( {point}, {len(iText)} chars )" )

        if point != tk.END:
            logging.critical( "HTMLTextBox.insert " + _("doesn't know how to insert at {}").format( repr(point) ) )
            BText.insert( self, point, iText )
            return

        # Fix whitespace in our text to how we want it
        remainingText = iText.replace( '\n', ' ' )
        remainingText = remainingText.replace( '<br>','\n' ).replace( '<br />','\n' ).replace( '<br/>','\n' )

        # Temp fix-up for UTA --------------- XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        remainingText = remainingText.replace('<ul>','\n\n').replace('</ul>','\n\n')
        remainingText = remainingText.replace('<li>',' ● ').replace('</li>','\n')

        while '  ' in remainingText: remainingText = remainingText.replace( '  ', ' ' )

        currentFormatTags, currentHTMLTags = [], []
        #first = True
        while remainingText:
            #try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Remaining: {}".format( repr(remainingText) ) )
            #except UnicodeEncodeError: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Remaining: {}".format( len(remainingText) ) )
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
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "cFT", currentFormatTags )
                        for tag in currentFormatTags:
                            if tag.startswith( 'a=' ):
                                tag, link = 'a', tag[2:]
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Got <a> link {}".format( repr(link) ) )
                            if tag != lastTag:
                                if combinedFormats: combinedFormats += '_'
                                combinedFormats += tag
                                lastTag = tag
                        # dPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"{combinedFormats=}" )
                        if combinedFormats and combinedFormats not in self.styleDict:
                            dPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"  Missing HTML format: {combinedFormats=} {currentFormatTags=} {currentHTMLTags=}" )
                            #try: dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   on", repr(remainingText[:ix]) )
                            #except UnicodeEncodeError: pass
                        insertText = remainingText[:ix]
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Got format:", repr(combinedFormats), "cFT", currentFormatTags, "cHT", currentHTMLTags, repr(insertText) )
                        if 'Hebrew' in combinedFormats:
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Reversing", repr(insertText ) )
                            insertText = insertText[::-1] # Reverse the string (a horrible way to approximate RTL)
                        for htmlChars, replacementChars in HTML_REPLACEMENTS:
                            insertText = insertText.replace( htmlChars, replacementChars )
                        #if link: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "insertMarks", repr( (combinedFormats, 'href'+link,) if link else combinedFormats ) )
                        if link:
                            hypertag = 'href' + link
                            BText.insert( self, point, insertText, (combinedFormats, hypertag,) )
                            self.tag_bind( hypertag, '<Enter>', self.overHyperlink )
                            self.tag_bind( hypertag, '<Leave>', self.leaveHyperlink )
                        else: BText.insert( self, point, insertText, combinedFormats )
                        #first = False
                    remainingText = remainingText[ix:]
                #try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  tag", repr(remainingText[:5]) )
                #except UnicodeEncodeError: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  tag" )
                ixEnd = remainingText.find( '>' )
                ixNext = remainingText.find( '<', 1 )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ixEnd", ixEnd, "ixNext", ixNext )
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
                    #try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "after marker", remainingText[0] )
                    #except UnicodeEncodeError: pass
                if not fullHTMLTag:
                    logging.critical( "HTMLTextBox.insert: " + _("Unexpected empty HTML tags") )
                    continue
                selfClosing = fullHTMLTag[-1] == '/'
                if selfClosing:
                    fullHTMLTag = fullHTMLTag[:-1]
                #try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "fullHTMLTag", repr(fullHTMLTag), "self-closing" if selfClosing else "" )
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
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "{} got {}".format( repr(fullHTMLTag), fullHTMLTagBits ) )
                HTMLTag = fullHTMLTagBits[0]
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HTMLTag", repr(HTMLTag) )

                if HTMLTag and HTMLTag[0] == '/': # it's a close tag
                    assert len(fullHTMLTagBits) == 1 # shouldn't have any attributes on a closing tag
                    assert not selfClosing
                    HTMLTag = HTMLTag[1:]
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Got HTML {} close tag".format( repr(HTMLTag) ) )
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "cHT1", currentHTMLTags )
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "cFT1", currentFormatTags )
                    if currentHTMLTags and HTMLTag == currentHTMLTags[-1]: # all good
                        currentHTMLTags.pop() # Drop it
                        if HTMLTag not in NON_FORMATTING_TAGS:
                            currentFormatTags.pop()
                    elif currentHTMLTags:
                        logging.critical( "HTMLTextBox.insert: " + _("Expected to close {} but got {} instead").format( repr(currentHTMLTags[-1]), repr(HTMLTag) ) )
                    else:
                        logging.critical( "HTMLTextBox.insert: " + _("Unexpected HTML close {} close marker").format( repr(HTMLTag) ) )
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "cHT2", currentHTMLTags )
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "cFT2", currentFormatTags )
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
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Looking for attributes" )
                        for bit in fullHTMLTagBits[1:]:
                            #try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  bit", repr(bit) )
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
        fnPrint( DEBUGGING_THIS_MODULE, f"HTMLTextBox._getURL( {event} )" )

        # get the index of the mouse cursor from the event.x and y attributes
        xy = '@{0},{1}'.format( event.x, event.y )
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "xy", repr(xy) ) # e.g.., '@34,77'
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ixy", repr(self.index(xy)) ) # e.g., '4.3'

        #URL = None
        tagNames = self.tag_names( xy )
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tn", tagNames )
        for tagName in tagNames:
            if tagName.startswith( 'href' ):
                URL = tagName[4:]
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "URL", repr(URL) )
                return URL
    # end of HTMLTextBox._getURL


    def openHyperlink( self, event ):
        """
        Handle a click on a hyperlink.
        """
        fnPrint( DEBUGGING_THIS_MODULE, f"HTMLTextBox.openHyperlink( {event} )" )
        URL = self._getURL( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Clicked on {}".format( repr(clickedText) ) )

        if URL: self.master.gotoLink( URL )
    # end of HTMLTextBox.openHyperlink


    def overHyperlink( self, event ):
        """
        Handle a mouseover on a hyperlink.
        """
        #dPrint( 'Never', DEBUGGING_THIS_MODULE, "HTMLTextBox.overHyperlink()" )
        URL = self._getURL( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Over {}".format( repr(clickedText) ) )

        if URL: self.master.overLink( URL )
    # end of HTMLTextBox.overHyperlink

    def leaveHyperlink( self, event ):
        """
        Handle a mouseover on a hyperlink.
        """
        #dPrint( 'Never', DEBUGGING_THIS_MODULE, "HTMLTextBox.leaveHyperlink()" )
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
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "CallbackAddon.__init__()" )

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
        fnPrint( DEBUGGING_THIS_MODULE, "CallbackAddon.onTextChange( {}, {} )".format( repr(result), args ) )

        #if 0: # Get line and column info
            #lineColumn = self.index( tk.INSERT )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "lc", repr(lineColumn) )
            #line, column = lineColumn.split( '.', 1 )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "l,c", repr(line), repr(column) )

        #if 0: # get formatting tag info
            #tagNames = self.tag_names( tk.INSERT )
            #tagNames2 = self.tag_names( lineColumn )
            #tagNames3 = self.tag_names( tk.INSERT + ' linestart' )
            #tagNames4 = self.tag_names( lineColumn + ' linestart' )
            #tagNames5 = self.tag_names( tk.INSERT + ' linestart+1c' )
            #tagNames6 = self.tag_names( lineColumn + ' linestart+1c' )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tN", tagNames )
            #if tagNames2!=tagNames or tagNames3!=tagNames or tagNames4!=tagNames or tagNames5!=tagNames or tagNames6!=tagNames:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tN2", tagNames2 )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tN3", tagNames3 )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tN4", tagNames4 )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tN5", tagNames5 )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tN6", tagNames6 )
                #halt

        #if 0: # show various mark strategies
            #mark1 = self.mark_previous( tk.INSERT )
            #mark2 = self.mark_previous( lineColumn )
            #mark3 = self.mark_previous( tk.INSERT + ' linestart' )
            #mark4 = self.mark_previous( lineColumn + ' linestart' )
            #mark5 = self.mark_previous( tk.INSERT + ' linestart+1c' )
            #mark6 = self.mark_previous( lineColumn + ' linestart+1c' )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "mark1", mark1 )
            #if mark2!=mark1:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "mark2", mark1 )
            #if mark3!=mark1 or mark4!=mark1 or mark5!=mark1 or mark6!=mark1:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "mark3", mark3 )
                #if mark4!=mark3:
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "mark4", mark4 )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "mark5", mark5 )
                #if mark6!=mark5:
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "mark6", mark6 )


        # Handle auto-correct
        if self.autocorrectEntries and args[0]=='insert' and args[1]=='insert':
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Handle autocorrect" )
            #previousText = getCharactersBeforeCursor( self )
            allText = self.get()
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "allText", repr(allText) )
            index = self.index( tk.INSERT )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "index", repr(index) )
            previousText = allText[0:index]
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "previousText", repr(previousText) )
            for inChars,outChars in self.autocorrectEntries:
                if previousText.endswith( inChars ):
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Going to replace {!r} with {!r}".format( inChars, outChars ) )
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
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "CustomEntry.__init__( {}, {} )".format( args, kwargs ) )
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
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "CustomCombobox.__init__( {}, {} )".format( args, kwargs ) )
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
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "CustomText.__init__( {}, {} )".format( args, kwargs ) )
        BText.__init__( self, *args, **kwargs ) # initialise the base class
        CallbackAddon.__init__( self ) # initialise the base class
    # end of CustomText.__init__


    def highlightPattern( self, pattern, styleTag, startAt=tkSTART, endAt=tk.END, regexpFlag=True ):
        """
        Apply the given tag to all text that matches the given pattern.

        Useful for syntax highlighting, etc.

        # Adapted from http://stackoverflow.com/questions/4028446/python-tkinter-help-menu
        """
        fnPrint( DEBUGGING_THIS_MODULE, "CustomText.highlightPattern( {}, {}, start={}, end={}, regexp={} )".format( pattern, styleTag, startAt, endAt, regexpFlag ) )

        countVar = tk.IntVar()
        matchEnd = startAt
        while True:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "here0 mS={!r} mE={!r} sL={!r}".format( self.index("matchStart"), self.index("matchEnd"), self.index("searchLimit") ) )
            index = self.search( pattern, matchEnd, stopindex=endAt, count=countVar, regexp=regexpFlag )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "here1", repr(index), repr(countVar.get()) )
            if index == "": break
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "here2", self.index("matchStart"), self.index("matchEnd") )
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
        fnPrint( DEBUGGING_THIS_MODULE, "CustomText.highlightAllPatterns( {} )".format( patternCollection ) )

        for regexpFlag, pattern, tagName, tagDict in patternCollection:
            self.tag_configure( tagName, **tagDict )
            self.highlightPattern( pattern, tagName, regexpFlag=regexpFlag )
    # end of CustomText.highlightAllPatterns
# end of CustomText class



class ChildBoxAddon():
    """
    A set of mix-in (add-on) functions that work for any frame or window that has a member: self.textBox
    """
    def __init__( self, parentWindow ) -> None:
        """
        """
        fnPrint( DEBUGGING_THIS_MODULE, "ChildBoxAddon.__init__( {} )".format( parentWindow ) )
        if DEBUGGING_THIS_MODULE or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
            assert parentWindow
        self.parentWindow = parentWindow

        self.myKeyboardBindingsList = []
        if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = [] # Just for catching setting of duplicates

        vPrint( 'Never', DEBUGGING_THIS_MODULE, "ChildBoxAddon.__init__ finished." )
    # end of ChildBoxAddon.__init__


    def _createStandardBoxKeyboardBinding( self, name:str, commandFunction ):
        """
        Called from createStandardKeyboardBindings to do the actual work.
        """
        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ChildBoxAddon._createStandardBoxKeyboardBinding( {} )".format( name ) )

        #try: kBD = BiblelatorGlobals.theApp.keyBindingDict
        #except AttributeError:
        kBD = BiblelatorGlobals.theApp.keyBindingDict
        assert (name,kBD[name][0],) not in self.myKeyboardBindingsList
        if name in kBD:
            for keyCode in kBD[name][1:]:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                self.textBox.bind( keyCode, commandFunction )
                if BibleOrgSysGlobals.debugFlag:
                    if keyCode in self.myKeyboardShortcutsList:
                        vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ChildBoxAddon._createStandardBoxKeyboardBinding wants to add duplicate {}".format( keyCode ) )
                    self.myKeyboardShortcutsList.append( keyCode )
            self.myKeyboardBindingsList.append( (name,kBD[name][0],) )
        else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of ChildBoxAddon._createStandardBoxKeyboardBinding()

    def createStandardBoxKeyboardBindings( self, reset=False ):
        """
        Create keyboard bindings for this widget.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "ChildBoxAddon.createStandardBoxKeyboardBindings( {} )".format( reset ) )

        if reset:
            self.myKeyboardBindingsList = []

        for name,commandFunction in ( ('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                             ('Find',self.doBoxFind), ('Refind',self.doBoxRefind),
                             #('Help',self._doHelp), ('Info',self.doShowInfo), ('About',self._doAbout),
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
        fnPrint( DEBUGGING_THIS_MODULE, "ChildBoxAddon.doCopy( {} )".format( event ) )

        if not self.textBox.tag_ranges( tk.SEL ):       # save in cross-app clipboard
            errorBeep()
            showError( self, APP_NAME, _("No text selected") )
        else:
            copyText = self.textBox.get( tk.SEL_FIRST, tk.SEL_LAST)
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  copied text", repr(copyText) )
            self.clipboard_clear()
            self.clipboard_append( copyText )
    # end of ChildBoxAddon.doCopy


    def doSelectAll( self, event=None ):
        """
        Select all the text in the text box.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "ChildBoxAddon.doSelectAll( {} )".format( event ) )

        self.textBox.tag_add( tk.SEL, tkSTART, tk.END+'-1c' )   # select entire text
        self.textBox.mark_set( tk.INSERT, tkSTART )          # move insert point to top
        self.textBox.see( tk.INSERT )                      # scroll to top
    # end of ChildBoxAddon.doSelectAll


    def doGotoWindowLine( self, event=None, forceline=None ):
        """
        """
        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'ChildBoxAddon doGotoWindowLine {}'.format( forceline ) )
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "ChildBoxAddon.doGotoWindowLine( {}, {} )".format( event, forceline ) )

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
        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'ChildBoxAddon doBoxFind {!r}'.format( lastkey ) )
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "ChildBoxAddon.doBoxFind( {}, {!r} )".format( event, lastkey ) )

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
        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'ChildBoxAddon doBoxRefind' )
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "ChildBoxAddon.doBoxRefind( {} ) for {!r}".format( event, self.lastfind ) )

        self.doBoxFind( lastkey=self.lastfind )
    # end of ChildBoxAddon.doBoxRefind


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'ChildBoxAddon doShowInfo' )
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "ChildBoxAddon.doShowInfo( {} )".format( event ) )

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
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Configure", self.textBox.configure() ) # Prints a large dictionary of settings
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  State", self.textBox.configure()['state'] ) # Prints a 5-tuple
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


    def setAllText( self, newText:str, textType:Optional[str]=None ) -> None:
        """
        Sets the textBox (assumed to be enabled) to the given text
            then positions the insert cursor at the BEGINNING of the text.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        fnPrint( DEBUGGING_THIS_MODULE, f"ChildBoxAddon.setAllText( {len(newText)} chars, {textType} )" )
        assert textType in ( None, 'Markdown', 'YAML' )
        self.textType = textType
        if textType == 'Markdown':
            newText = markdown( newText )
            # dPrint( 'Info', DEBUGGING_THIS_MODULE, f"Markdown got '{newText}'" )

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
        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ChildBoxAddon.doShowMainWindow( {} )".format( event ) )

        ##theApp.rootWindow.iconify() # Didn't help
        #theApp.rootWindow.withdraw() # For some reason, doing this first makes the window always appear above others
        #theApp.rootWindow.update()
        #theApp.rootWindow.deiconify()
        ##theApp.rootWindow.focus_set()
        #theApp.rootWindow.lift() # aboveThis=self )
    ## end of ChildBoxAddon.doShowMainWindow


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden if an edit box needs to save files first.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "ChildBoxAddon.doClose( {} )".format( event ) )

        self.destroy()
    # end of ChildBoxAddon.doClose
# end of ChildBoxAddon class



class BibleBoxAddon():
    """
    A set of functions that work for any Bible frame or window that has a member: self.textBox
        and also uses verseKeys
    """
    def __init__( self, parentWindow, BibleBoxType ) -> None:
        """
        This function does absolutely nothing.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "BibleBoxAddon.__init__( {}, {} )".format( parentWindow, BibleBoxType ) )
        self.doExtraChecking = DEBUGGING_THIS_MODULE or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag
        if self.doExtraChecking: assert parentWindow
        self.parentWindow, self.BibleBoxType = parentWindow, BibleBoxType

        # Set-up our standard Bible styles
        for USFMKey, styleDict in BiblelatorGlobals.theApp.stylesheet.getTKStyles().items():
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


        vPrint( 'Never', DEBUGGING_THIS_MODULE, "BibleBoxAddon.__init__ finished." )
    # end of BibleBoxAddon.__init__


    def createStandardBoxKeyboardBindings( self, reset=False ):
        """
        Create keyboard bindings for this widget.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "BibleBoxAddon.createStandardBoxKeyboardBindings( {} )".format( reset ) )

        if reset:
            self.myKeyboardBindingsList = []

        for name,commandFunction in ( ('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                             ('Find',self.doBibleFind), #('Refind',self.doBibleRefind),
                             #('Help',self._doHelp), ('Info',self.doShowInfo), ('About',self._doAbout),
                             #('ShowMain',self.doShowMainWindow),
                             ('Close',self.doClose), ):
            self._createStandardBoxKeyboardBinding( name, commandFunction )
    # end of BibleBoxAddon.createStandardBoxKeyboardBindings()


    def createContextMenu( self ):
        """
        Can be overriden if necessary.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "BibleBoxAddon.createContextMenu()" )

        self.textBox.contextMenu = tk.Menu( self, tearoff=0 )
        self.textBox.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        self.textBox.contextMenu.add_separator()
        self.textBox.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )
        self.textBox.contextMenu.add_separator()
        self.textBox.contextMenu.add_command( label=_('Bible Find…'), underline=6, command=self.doBibleFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        self.textBox.contextMenu.add_separator()
        self.textBox.contextMenu.add_command( label=_('Find in window…'), underline=8, command=self.doBoxFind )#, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        #self.contextMenu.add_separator()
        #self.contextMenu.add_command( label=_('Close window'), underline=1, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] )

        self.textBox.bind( '<Button-3>', self.showContextMenu ) # right-click
        #self.pack()

        self.BibleFindOptionsDict, self.BibleReplaceOptionsDict = {}, {}
    # end of BibleBoxAddon.createContextMenu

    def showContextMenu( self, event ):
        self.textBox.contextMenu.tk_popup( event.x_root, event.y_root )
    # end of BibleBoxAddon.showContextMenu


    def displayAppendVerse( self, firstFlag:bool, verseKey, verseContextData, lastFlag:bool=True, currentVerseFlag:bool=False, substituteTrailingSpaces:bool=False, substituteMultipleSpaces:bool=False ) -> None:
        """
        Add the requested verse to the end of self.textBox.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.

        Usually called from updateShownBCV from the subclass.
        Note that it's used in both formatted and unformatted (even edit) windows.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "BibleBoxAddon.displayAppendVerse( {}, {}, {}, {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, substituteTrailingSpaces, substituteMultipleSpaces ) )
        if self.doExtraChecking:
            assert isinstance( firstFlag, bool )
            assert isinstance( verseKey, SimpleVerseKey )
            if verseContextData:
                assert isinstance( verseContextData, tuple ) and len(verseContextData)==2 or isinstance( verseContextData, str )
            assert isinstance( lastFlag, bool )
            assert isinstance( currentVerseFlag, bool )

        def insertAtEnd( ieText:str, ieTags ) -> None:
            """
            Insert the formatted text into the end of the textbox.

            The function mostly exists so we can print the parameters if necessary for debugging.
            """
            fnPrint( DEBUGGING_THIS_MODULE, f"BibleBoxAddon.displayAppendVerse.insertAtEnd( {ieText=}, {ieTags=} )" )
            if self.doExtraChecking:
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
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "displayAppendVerse2( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )

        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBoxAddon.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
            ##try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBoxAddon.displayAppendVerse( {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, currentVerseFlag ) )
            ##except UnicodeEncodeError: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBoxAddon.displayAppendVerse", firstFlag, verseKey, currentVerseFlag )

        BBB, C, V = verseKey.getBCV()
        try: C = int(C)
        except ValueError:
            dPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"BibleBoxAddon.displayAppendVerse found invalid {C=}: changed to 1" )
            C = 1
        try: V = int(V)
        except ValueError:
            dPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"BibleBoxAddon.displayAppendVerse found invalid {V=}: changed to 1" )
            V = 1

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
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Marks", previousMarkName, currentMarkName, nextMarkName )

        lastCharWasSpace = haveTextFlag = not firstFlag

        if verseContextData is None:
            if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE and C!=0 and V!=0:
                vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  ", "BibleBoxAddon.displayAppendVerse has no data for", verseKey )
            verseDataList = context = None
        elif isinstance( verseContextData, tuple ):
            assert len(verseContextData) == 2
            verseDataList, context = verseContextData
            #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   VerseDataList: {}".format( verseDataList ) )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   Context: {}".format( context ) )
        elif isinstance( verseContextData, str ):
            verseDataList, context = verseContextData.split( '\n' ), None
        elif BibleOrgSysGlobals.debugFlag: halt

        # Display the context preceding the first verse
        if firstFlag:
            if context:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "context", context )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting context mark to {}".format( previousMarkName ) )
                #self.textBox.mark_set( previousMarkName, tk.INSERT )
                #self.textBox.mark_gravity( previousMarkName, tk.LEFT )
                insertAtEnd( ' '+_("Prior context")+':', 'contextHeader' )
                contextString, firstMarker = "", True
                for someMarker in context:
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  someMarker", someMarker )
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

        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting mark to {}".format( currentMarkName ) )
        self.textBox.mark_set( currentMarkName, tk.INSERT )
        self.textBox.mark_gravity( currentMarkName, tk.LEFT )

        if verseDataList is None:
            if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE and C!=0 and V!=0:
                vPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"  BibleBoxAddon.displayAppendVerse has no data for {self.moduleID} {verseKey}" )
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
                if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                    vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  displayAppendVerse", lastParagraphMarker, haveTextFlag, marker, repr(cleanText) )

                if fVM == 'Unformatted':
                    if marker and marker[0]=='¬': pass # Ignore end markers for now
                    elif marker in ('headers','intro','chapters','list',): pass # Ignore added markers for now
                    else:
                        if isinstance( verseDataEntry, str ): # from a Bible text editor window
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "marker={!r}, verseDataEntry={!r}".format( marker, verseDataEntry ) )
                            insertAtEnd( verseDataEntry, marker ) # Do it just as is!
                        else: # not a str, i.e., not a text editor, but a viewable resource
                            #if hadVerseText and marker in ( 's', 's1', 's2', 's3' ):
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting s mark to {}".format( nextMarkName ) )
                                #self.textBox.mark_set( nextMarkName, tk.INSERT )
                                #self.textBox.mark_gravity( nextMarkName, tk.LEFT )
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Inserting ({}): {!r}".format( marker, verseDataEntry ) )
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
                    elif marker in ('usfm','ide','rem',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('h','toc1','toc2','toc3','cl¤',):
                        assert marker not in BibleOrgSysGlobals.USFMParagraphMarkers
                        if haveTextFlag: self.textBox.insert ( tk.END, '\n' )
                        insertAtEnd( cleanText, marker )
                        haveTextFlag = True
                    elif marker in ('headers','intro','chapters','list',):
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
                        # dPrint( 'Info', DEBUGGING_THIS_MODULE, "self.BibleBoxType", self.BibleBoxType ) # Gives 'BibleResourceWindow'
                        # if DEBUGGING_THIS_MODULE or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
                        #     assert self.BibleBoxType in ('DBPBibleResourceBox','DBPBibleResourceWindow')
                        pass
                    elif marker == 'c': # Don't want to display this (original) c marker
                        #if not firstFlag: haveC = cleanText
                        #else: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   Ignore C={}".format( cleanText ) )
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
                        logger = logging.warning if marker in ('v=',) else logging.critical
                        if BibleOrgSysGlobals.debugFlag:
                            logger( f"BibleBoxAddon.displayAppendVerse (formatted): Unknown marker {self.moduleID} {marker}={cleanText} from {verseDataList}" )
                        else:
                            logger( f"BibleBoxAddon.displayAppendVerse (formatted): Unknown marker {self.moduleID} {marker}={cleanText}" )
                else:
                    logging.critical( _("BibleBoxAddon.displayAppendVerse: Unknown {!r} format view mode").format( fVM ) )
                    if BibleOrgSysGlobals.debugFlag: halt

            if lastFlag and cVM=='ByVerse' and endMarkers:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "endMarkers", endMarkers )
                insertAtEnd( ' '+ _("End context")+':', 'contextHeader' )
                contextString, firstMarker = "", True
                for someMarker in endMarkers:
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  someMarker", someMarker )
                    contextString += (' ' if firstMarker else ', ') + someMarker
                    firstMarker = False
                insertAtEnd( contextString+' ', 'context' )
    # end of BibleBoxAddon.displayAppendVerse


    def getBeforeAndAfterBibleData( self, newVerseKey ):
        """
        Returns the requested verse, the previous verse, and the next n verses.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "BibleBoxAddon.getBeforeAndAfterBibleData( {} )".format( newVerseKey ) )
        if BibleOrgSysGlobals.debugFlag:
            assert isinstance( newVerseKey, SimpleVerseKey )

        BBB, C, V = newVerseKey.getBCV()
        dPrint( 'Verbose', DEBUGGING_THIS_MODULE, f"BibleBoxAddon.getBeforeAndAfterBibleData1 {BBB=} {C=} {V=}" )
        intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()
        dPrint( 'Verbose', DEBUGGING_THIS_MODULE, f"  BibleBoxAddon.getBeforeAndAfterBibleData2 {BBB=} {intC=} {intV=}" )
        if intV is None:
            dPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"BibleBoxAddon.getBeforeAndAfterBibleData: fixing intV from None ({V=})" )
            V, intV = '1', 1

        # Determine the PREVIOUS valid verse numbers
        prevBBB, prevIntC, prevIntV = BBB, intC, intV
        previousVersesData = []
        for n in range( -BiblelatorGlobals.theApp.viewVersesBefore, 0 ):
            failed = False
            dPrint( 'Never', DEBUGGING_THIS_MODULE, "  BibleBoxAddon.getBeforeAndAfterBibleData here with", repr(n), repr(prevIntC), repr(prevIntV) )
            if prevIntV is not None and prevIntV > 0: prevIntV -= 1
            elif prevIntC > 0:
                prevIntC -= 1
                try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                except KeyError:
                    if prevIntC != 0: # we can expect an error for chapter zero
                        logging.error( _("BibleBoxAddon.getBeforeAndAfterBibleData1 failed at {} {}").format( prevBBB, prevIntC ) )
                    failed = True
                #if not failed:
                    #if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            else:
                try: prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                except KeyError: prevBBB = None
                if prevBBB is None: failed = True
                else:
                    prevIntC = self.getNumChapters( prevBBB )
                    prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                        vPrint( 'Quiet', DEBUGGING_THIS_MODULE, " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
                    if prevIntC is None or prevIntV is None:
                        logging.error( _("BibleBoxAddon.getBeforeAndAfterBibleData2 failed at {} {}:{}").format( prevBBB, prevIntC, prevIntV ) )
                        #failed = True
                        break
            if not failed and prevIntV is not None:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                assert prevBBB and isinstance(prevBBB, str)
                previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                previousVerseData = self.getCachedVerseData( previousVerseKey )
                if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        # Determine the NEXT valid verse numbers
        nextBBB, nextIntC, nextIntV = BBB, intC, intV
        nextVersesData = []
        for n in range( BiblelatorGlobals.theApp.viewVersesAfter ):
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

        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'BibleBoxAddon doBibleFind' )
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "BibleBoxAddon.doBibleFind( {} )".format( event ) )

        try: haveInternalBible = self.internalBible is not None
        except AttributeError: haveInternalBible = False
        if not haveInternalBible:
            logging.critical( _("No Bible to search") )
            return
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "intBib", self.internalBible )

        self.BibleFindOptionsDict['currentBCV'] = self.currentVerseKey.getBCV()
        gBSTD = GetBibleFindTextDialog( self, self.internalBible, self.BibleFindOptionsDict, title=_('Find in Bible') )
        dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "gBSTDResult", repr(gBSTD.result) )
        if gBSTD.result:
            if BibleOrgSysGlobals.debugFlag: assert isinstance( gBSTD.result, dict )
            self.BibleFindOptionsDict = gBSTD.result # Update our search options dictionary
            self.doActualBibleFind()
        BiblelatorGlobals.theApp.setReadyStatus()

        #return tkBREAK
    # end of BibleBoxAddon.doBibleFind


    def doActualBibleFind( self, extendTo=None ):
        """
        This function (called by the above doBibleFind),
            invokes the actual search (or redoes the search)
            assuming that the search parameters are already defined.
        """
        from ChildWindows import FindResultWindow

        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'BibleBoxAddon doActualBibleFind' )
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "BibleBoxAddon.doActualBibleFind( {} )".format( extendTo ) )

        BiblelatorGlobals.theApp.setWaitStatus( _("Searching…") )
        #self.textBox.update()
        #self.textBox.focus()
        #self.lastfind = key
        BiblelatorGlobals.theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, ' doActualBibleFind {}'.format( self.BibleFindOptionsDict ) )
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bookList", repr(self.BibleFindOptionsDict['bookList']) )
        bookCode = None
        if isinstance( self.BibleFindOptionsDict['bookList'], str ) \
        and self.BibleFindOptionsDict['bookList'] != 'ALL':
            bookCode = self.BibleFindOptionsDict['bookList']
        self._prepareInternalBible( bookCode, self.BibleFindOptionsDict['givenBible'] ) # Make sure that all books are loaded
        # We search the loaded Bible processed lines
        self.BibleFindOptionsDict, resultSummaryDict, findResultList = self.BibleFindOptionsDict['givenBible'].findText( self.BibleFindOptionsDict )
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Got findResultList", findResultList )
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
            BiblelatorGlobals.theApp.childWindows.append( findResultWindow )
        BiblelatorGlobals.theApp.setReadyStatus()
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
        vPrint( 'Never', DEBUGGING_THIS_MODULE, "BibleBoxAddon._prepareInternalBible()" )
        if givenBible is None: givenBible = self.internalBible

        if self.modified(): self.doSave() # NOTE: Read-only boxes/windows don't even have a doSave() function
        if givenBible is not None:
            BiblelatorGlobals.theApp.setWaitStatus( _("Preparing internal Bible…") )
            if bookCode is None:
                BiblelatorGlobals.theApp.setWaitStatus( _("Loading/Preparing internal Bible…") )
                givenBible.load()
            else:
                BiblelatorGlobals.theApp.setWaitStatus( _("Loading/Preparing internal Bible book…") )
                givenBible.loadBook( bookCode )
    # end of BibleBoxAddon._prepareInternalBible
# end of class BibleBoxAddon



#class BibleBox( ChildBox ):
    #"""
    #A set of functions that work for any Bible frame or window that has a member: self.textBox
        #and also uses verseKeys
    #"""
    #def __init__( self ):
        #"""
        #This function is not needed at all, except for debug tracing of __init__ functions (when used).
        #"""
        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.__init__( {} )".format() )

        #ChildBox.__init__( self )

        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.__init__ finished." )
    ## end of BibleBox.__init__


    ##def createStandardBoxKeyboardBindings( self, reset=False ):
        ##"""
        ##Create keyboard bindings for this widget.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.createStandardBoxKeyboardBindings( {} )".format( reset ) )

        ##if reset:
            ##self.myKeyboardBindingsList = []

        ##for name,commandFunction in ( ('SelectAll',self.doSelectAll), #('Copy',self.doCopy),
                             ##('Find',self.doBibleFind), #('Refind',self.doBibleRefind),
                             ###('Help',self._doHelp), ('Info',self.doShowInfo), ('About',self._doAbout),
                             ###('ShowMain',self.doShowMainWindow),
                             ##('Close',self.doClose), ):
            ##self._createStandardBoxKeyboardBinding( name, commandFunction )
    ### end of BibleBox.createStandardBoxKeyboardBindings()


    ##def createContextMenu( self ):
        ##"""
        ##Can be overriden if necessary.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.createContextMenu()" )

        ##self.textBox.contextMenu = tk.Menu( self, tearoff=0 )
        ##self.textBox.contextMenu.add_command( label=_('Copy'), underline=0, command=self.doCopy, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Copy')][0] )
        ##self.textBox.contextMenu.add_separator()
        ##self.textBox.contextMenu.add_command( label=_('Select all'), underline=7, command=self.doSelectAll, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('SelectAll')][0] )
        ##self.textBox.contextMenu.add_separator()
        ##self.textBox.contextMenu.add_command( label=_('Bible Find…'), underline=6, command=self.doBibleFind, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        ##self.textBox.contextMenu.add_separator()
        ##self.textBox.contextMenu.add_command( label=_('Find in window…'), underline=8, command=self.doBoxFind )#, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Find')][0] )
        ###self.contextMenu.add_separator()
        ###self.contextMenu.add_command( label=_('Close window'), underline=1, command=self.doClose, accelerator=BiblelatorGlobals.theApp.keyBindingDict[_('Close')][0] )

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
            ##if DEBUGGING_THIS_MODULE:
                ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "displayAppendVerse( {}, {}, {}, {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, substituteTrailingSpaces, substituteMultipleSpaces ) )
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
                ##if DEBUGGING_THIS_MODULE:
                    ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "insertAtEnd( {!r}, {} )".format( ieText, ieTags ) )
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
        ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "displayAppendVerse2( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )

        ###if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
            ####try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.displayAppendVerse( {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, currentVerseFlag ) )
            ####except UnicodeEncodeError: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.displayAppendVerse", firstFlag, verseKey, currentVerseFlag )

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
        ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Marks", previousMarkName, currentMarkName, nextMarkName )

        ##lastCharWasSpace = haveTextFlag = not firstFlag

        ##if verseContextData is None:
            ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE and C!=0 and V!=0:
                ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  ", "displayAppendVerse has no data for", verseKey )
            ##verseDataList = context = None
        ##elif isinstance( verseContextData, tuple ):
            ##assert len(verseContextData) == 2
            ##verseDataList, context = verseContextData
            ###if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   VerseDataList: {}".format( verseDataList ) )
                ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   Context: {}".format( context ) )
        ##elif isinstance( verseContextData, str ):
            ##verseDataList, context = verseContextData.split( '\n' ), None
        ##elif BibleOrgSysGlobals.debugFlag: halt

        ### Display the context preceding the first verse
        ##if firstFlag:
            ##if context:
                ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "context", context )
                ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting context mark to {}".format( previousMarkName ) )
                ###self.textBox.mark_set( previousMarkName, tk.INSERT )
                ###self.textBox.mark_gravity( previousMarkName, tk.LEFT )
                ##insertAtEnd( ' '+_("Prior context")+':', 'contextHeader' )
                ##contextString, firstMarker = "", True
                ##for someMarker in context:
                    ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  someMarker", someMarker )
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

        ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting mark to {}".format( currentMarkName ) )
        ##self.textBox.mark_set( currentMarkName, tk.INSERT )
        ##self.textBox.mark_gravity( currentMarkName, tk.LEFT )

        ##if verseDataList is None:
            ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE and C!=0 and V!=0:
                ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  ", "BibleBox.displayAppendVerse has no data for", self.moduleID, verseKey )
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
                ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                    ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  displayAppendVerse", lastParagraphMarker, haveTextFlag, marker, repr(cleanText) )

                ##if fVM == 'Unformatted':
                    ##if marker and marker[0]=='¬': pass # Ignore end markers for now
                    ##elif marker in ('headers','intro','chapters','list',): pass # Ignore added markers for now
                    ##else:
                        ##if isinstance( verseDataEntry, str ): # from a Bible text editor window
                            ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "marker={!r}, verseDataEntry={!r}".format( marker, verseDataEntry ) )
                            ##insertAtEnd( verseDataEntry, marker ) # Do it just as is!
                        ##else: # not a str, i.e., not a text editor, but a viewable resource
                            ###if hadVerseText and marker in ( 's', 's1', 's2', 's3' ):
                                ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting s mark to {}".format( nextMarkName ) )
                                ###self.textBox.mark_set( nextMarkName, tk.INSERT )
                                ###self.textBox.mark_gravity( nextMarkName, tk.LEFT )
                            ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Inserting ({}): {!r}".format( marker, verseDataEntry ) )
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
                    ##elif marker in ('headers','intro','chapters','list',):
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
                        ###else: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   Ignore C={}".format( cleanText ) )
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
                ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "endMarkers", endMarkers )
                ##insertAtEnd( ' '+ _("End context")+':', 'contextHeader' )
                ##contextString, firstMarker = "", True
                ##for someMarker in endMarkers:
                    ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  someMarker", someMarker )
                    ##contextString += (' ' if firstMarker else ', ') + someMarker
                    ##firstMarker = False
                ##insertAtEnd( contextString+' ', 'context' )
    ### end of BibleBox.displayAppendVerse


    ##def getBeforeAndAfterBibleData( self, newVerseKey ):
        ##"""
        ##Returns the requested verse, the previous verse, and the next n verses.
        ##"""
        ##if BibleOrgSysGlobals.debugFlag:
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.getBeforeAndAfterBibleData( {} )".format( newVerseKey ) )
            ##assert isinstance( newVerseKey, SimpleVerseKey )

        ##BBB, C, V = newVerseKey.getBCV()
        ##intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        ### Determine the PREVIOUS valid verse numbers
        ##prevBBB, prevIntC, prevIntV = BBB, intC, intV
        ##previousVersesData = []
        ##for n in range( -BiblelatorGlobals.theApp.viewVersesBefore, 0 ):
            ##failed = False
            ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  getBeforeAndAfterBibleData here with", n, prevIntC, prevIntV )
            ##if prevIntV > 0: prevIntV -= 1
            ##elif prevIntC > 0:
                ##prevIntC -= 1
                ##try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                ##except KeyError:
                    ##if prevIntC != 0: # we can expect an error for chapter zero
                        ##logging.error( _("BibleBox.getBeforeAndAfterBibleData1 failed at {} {}").format( prevBBB, prevIntC ) )
                    ##failed = True
                ###if not failed:
                    ###if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            ##else:
                ##try: prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                ##except KeyError: prevBBB = None
                ##if prevBBB is None: failed = True
                ##else:
                    ##prevIntC = self.getNumChapters( prevBBB )
                    ##prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                        ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
                    ##if prevIntC is None or prevIntV is None:
                        ##logging.error( _("BibleBox.getBeforeAndAfterBibleData2 failed at {} {}:{}").format( prevBBB, prevIntC, prevIntV ) )
                        ###failed = True
                        ##break
            ##if not failed and prevIntV is not None:
                ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                ##assert prevBBB and isinstance(prevBBB, str)
                ##previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                ##previousVerseData = self.getCachedVerseData( previousVerseKey )
                ##if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        ### Determine the NEXT valid verse numbers
        ##nextBBB, nextIntC, nextIntV = BBB, intC, intV
        ##nextVersesData = []
        ##for n in range( BiblelatorGlobals.theApp.viewVersesAfter ):
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

        ##theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'BibleBox doBibleFind' )
        ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.doBibleFind( {} )".format( event ) )

        ##try: haveInternalBible = self.internalBible is not None
        ##except AttributeError: haveInternalBible = False
        ##if not haveInternalBible:
            ##logging.critical( _("No Bible to search") )
            ##return
        ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "intBib", self.internalBible )

        ##self.BibleFindOptionsDict['currentBCV'] = self.currentVerseKey.getBCV()
        ##gBSTD = GetBibleFindTextDialog( self, self.internalBible, self.BibleFindOptionsDict, title=_('Find in Bible') )
        ##if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "gBSTDResult", repr(gBSTD.result) )
        ##if gBSTD.result:
            ##if BibleOrgSysGlobals.debugFlag: assert isinstance( gBSTD.result, dict )
            ##self.BibleFindOptionsDict = gBSTD.result # Update our search options dictionary
            ##self.doActualBibleFind()
        ##theApp.setReadyStatus()

        ###return tkBREAK
    ### end of BibleBox.doBibleFind


    ##def doActualBibleFind( self, extendTo=None ):
        ##"""
        ##This function (called by the above doBibleFind),
            ##invokes the actual search (or redoes the search)
            ##assuming that the search parameters are already defined.
        ##"""
        ##from ChildWindows import FindResultWindow

        ##theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'BibleBox doActualBibleFind' )
        ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox.doActualBibleFind( {} )".format( extendTo ) )

        ##theApp.setWaitStatus( _("Searching…") )
        ###self.textBox.update()
        ###self.textBox.focus()
        ###self.lastfind = key
        ##theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, ' doActualBibleFind {}'.format( self.BibleFindOptionsDict ) )
        ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bookList", repr(self.BibleFindOptionsDict['bookList']) )
        ##bookCode = None
        ##if isinstance( self.BibleFindOptionsDict['bookList'], str ) \
        ##and self.BibleFindOptionsDict['bookList'] != 'ALL':
            ##bookCode = self.BibleFindOptionsDict['bookList']
        ##self._prepareInternalBible( bookCode, self.BibleFindOptionsDict['givenBible'] ) # Make sure that all books are loaded
        ### We search the loaded Bible processed lines
        ##self.BibleFindOptionsDict, resultSummaryDict, findResultList = self.BibleFindOptionsDict['givenBible'].findText( self.BibleFindOptionsDict )
        ###dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Got findResults", findResults )
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
            ##theApp.childWindows.append( findResultWindow )
        ##theApp.setReadyStatus()
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
        ##if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "BibleBox._prepareInternalBible()" )
        ##if givenBible is None: givenBible = self.internalBible

        ##if self.modified(): self.doSave() # NOTE: Read-only boxes/windows don't even have a doSave() function
        ##if givenBible is not None:
            ##theApp.setWaitStatus( _("Preparing internal Bible…") )
            ##if bookCode is None:
                ##theApp.setWaitStatus( _("Loading/Preparing internal Bible…") )
                ##givenBible.load()
            ##else:
                ##theApp.setWaitStatus( _("Loading/Preparing internal Bible book…") )
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
    def __init__( self, parentWindow, numInterlinearLines:int ) -> None:
        """
        This function is not needed at all, except for debug tracing of __init__ functions (when used).
        """
        fnPrint( DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.__init__( {}, nIL={} )".format( parentWindow, numInterlinearLines ) )
        if DEBUGGING_THIS_MODULE or BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag:
            assert parentWindow
            assert 0 < numInterlinearLines <= 5
        self.numInterlinearLines = numInterlinearLines

        BibleBoxAddon.__init__( self, parentWindow, 'HebrewInterlinearBibleBoxAddon' )
        self.tabStopCm = 3.0
        self.textBox.config( tabs='3.0c' ) # centimeters'
        self.pixelsPerCm =  BiblelatorGlobals.theApp.rootWindow.winfo_fpixels( '1c' ) # gives 37.85488958990536 for me for 2.5c
        self.tabStopPixels = self.tabStopCm * self.pixelsPerCm

        self.entryStylesNormal = ( 'HebWord', 'HebStrong', 'HebMorph', 'HebGenericGloss', 'HebSpecificGloss' )
        self.entryStylesSelected = ( 'HebWordSelected', 'HebStrongSelected', 'HebMorphSelected', 'HebGenericGlossSelected', 'HebSpecificGlossSelected' )
        self.fontsNormal, self.fontsSelected = [], []
        #tabWidthsNormal, tabWidthsSelected = [], []
        for entryStyleNormal,entryStyleSelected in zip( self.entryStylesNormal, self.entryStylesSelected ):
            fontNormal = tkFont.Font( **BiblelatorGlobals.theApp.stylesheet.getTKStyleDict( entryStyleNormal ) )
            fontSelected = tkFont.Font( **BiblelatorGlobals.theApp.stylesheet.getTKStyleDict( entryStyleSelected ) )
            self.fontsNormal.append( fontNormal )
            self.fontsSelected.append( fontSelected )
            #tabWidthNormal = fontNormal.measure( ' '*8 ) # Typically gives around 24 (pixels?)
            #tabWidthSelected = fontSelected.measure( ' '*8 ) # Typically gives around 32 (pixels?)
            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tabWidths", tabWidthNormal, tabWidthSelected )
            #tabWidthsNormal.append( tabWidthNormal )
            #tabWidthsSelected.append( tabWidthSelected )

        self.glossWindowGeometry = None
        self.requestMissingGlosses = BibleOrgSysGlobals.commandLineArguments.export

        vPrint( 'Never', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.__init__ finished." )
    # end of HebrewInterlinearBibleBoxAddon.__init__


    def displayAppendVerse( self, firstFlag:bool, verseKey, verseContextData, lastFlag:bool=True, currentVerseFlag:bool=False, currentWordNumber:int=1, command=None, substituteTrailingSpaces:bool=False, substituteMultipleSpaces:bool=False ) -> None:
        """
        Add the requested verse to the end of self.textBox.

        It connects the USFM markers as stylenames while it's doing it
            and adds the CV marks at the same time for navigation.

        Usually called from updateShownBCV from the subclass.
        Note that it's used in both formatted and unformatted (even edit) windows.

        command can be 'E' for edit, i.e., if a bundle has been double-clicked
        """
        fnPrint( DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.displayAppendVerse( fF={}, {}, {}, lF={}, cVF={}, cWN={}, c={}, sTS={}, sMS={} )" \
                .format( firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, currentWordNumber, command, substituteTrailingSpaces, substituteMultipleSpaces ) )
        if self.doExtraChecking:
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  {}".format( verseContextData[0] ) )
            assert isinstance( firstFlag, bool )
            assert isinstance( verseKey, SimpleVerseKey )
            if verseContextData:
                assert isinstance( verseContextData, tuple ) and len(verseContextData)==2 or isinstance( verseContextData, str )
            assert isinstance( lastFlag, bool )
            assert isinstance( currentVerseFlag, bool )
        self.lastDAVargs = firstFlag, verseKey, verseContextData, lastFlag, currentVerseFlag, currentWordNumber, None, substituteTrailingSpaces, substituteMultipleSpaces

        self.update() # so we can get the geometry
        boxWidth = self.textBox.winfo_width()
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "boxWidth", boxWidth ) # in pixels (gives 585 for me)
        self.bundlesPerLine = int( boxWidth / (self.tabStopCm * self.pixelsPerCm) ) + 1
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bundlesPerLine", self.bundlesPerLine )


        def insertAtEnd( ieText, ieTags ):
            """
            Insert the formatted text into the end of the textbox.

            The function mostly exists so we can print the parameters if necessary for debugging.
            """
            fnPrint( DEBUGGING_THIS_MODULE, f"HebrewInterlinearBibleBoxAddon.displayAppendVerse.insertAtEnd( {ieText=}, {ieTags=} )" )
            if BibleOrgSysGlobals.debugFlag:
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
            fnPrint( DEBUGGING_THIS_MODULE, f"HebrewInterlinearBibleBoxAddon.displayAppendVerse.insertAtEndLine( {ieLineNumber}, {ieText=}, {ieTags=} )" )
            if BibleOrgSysGlobals.debugFlag:
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
            from Biblelator.Dialogs.BiblelatorDialogs import GetHebrewGlossWordDialog, GetHebrewGlossWordsDialog
            vPrint( 'Info', DEBUGGING_THIS_MODULE, "displayAppendVerse.appendVerseText( {}, {}, cVF={}, cWN={}, c={} )".format( verseDataEntry, currentVerseKey, currentVerseFlag, currentWordNumber, command ) )

            verseDictList = self.internalBible.getVerseDictList( verseDataEntry, currentVerseKey )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, verseKey.getShortText(), "verseDictList", verseDictList )

            #self.textBox.insert( tk.END, '\n'*self.numInterlinearLines ) # Make sure we have enough blank lines
            insertAtEnd( '\n'*self.numInterlinearLines, None ) # Make sure we have enough blank lines
            haveTextFlag = False
            savedLineNumber = self.lineNumber

            requestMissingGlossesNow = needToRequestMissingGlosses = needToUpdate = False
            for passNumber in range( 1, 3 ):
                # We won't request missing glosses until we've displayed what we know first
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.appendVerseText: pass #{} {} {}".format( passNumber, requestMissingGlossesNow, needToRequestMissingGlosses ) )
                self.lineNumber = savedLineNumber
                self.acrossIndex = 0
                j = 0
                while j < len(verseDictList): # Can't use a for loop coz we mess with the index
                    j += 1 # j is now in range 1..len(verseDictList)
                    verseDict = verseDictList[j-1] # each verseDict represents one word or token
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "pn={}, j={}, c={}, verseDict={}".format( passNumber, j, command, verseDict ) )
                    #if bundlesAcross >= self.bundlesPerLine: # Start a new line
                        ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Start new bundle line" )
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
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, '{!r} is '.format( word ), end=None )
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
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, '   ({}) {!r} normalized to ({}) {!r}'.format( len(word), word, len(normalizedWord), normalizedWord ) )
                            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, '{!r} is '.format( normalizedWord ), end=None )
                            ##h.printUnicodeData( normalizedWord )
                        genericGloss,genericReferencesList,specificReferencesDict = self.internalBible.glossingDict[normalizedWord] \
                                                        if normalizedWord in self.internalBible.glossingDict else ('',[],{})
                        if passNumber>1 and ( command in ('L','R') or (command=='E' and j==currentWordNumber) ):
                            command = None
                            tempBundle = refText, normalizedWord, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                            #self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations( morphology ) )
                            ghgwd = GetHebrewGlossWordDialog( self, _("Edit generic gloss"), tempBundle, genericGloss, geometry=self.glossWindowGeometry )
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ghgwdResultA1", ghgwd.result )
                            if ghgwd.result is None: # cancel
                                self.requestMissingGlosses = False
                            elif ghgwd.result == 'S': # skip
                                needToRequestMissingGlosses = False
                            elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                command = ghgwd.result
                            elif isinstance( ghgwd.result, dict ):
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "result1", ghgwd.result )
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
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "No generic gloss found for ({}) {}{}".format( len(word), word, \
                                #' to ({}) {}'.format( len(normalizedWord), normalizedWord ) if normalizedWord!=word else '' ) )
                            if self.requestMissingGlosses and requestMissingGlossesNow and not BiblelatorGlobals.theApp.isStarting:
                                tempBundle = refText, normalizedWord, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                                #self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations( morphology ) )
                                ghgwd = GetHebrewGlossWordDialog( self, _("Enter new generic gloss"), tempBundle, geometry=self.glossWindowGeometry )
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ghgwdResultA2", ghgwd.result )
                                if ghgwd.result is None: # cancel
                                    self.requestMissingGlosses = False
                                elif ghgwd.result == 'S': # skip
                                    needToRequestMissingGlosses = False
                                elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                    command = ghgwd.result
                                elif isinstance( ghgwd.result, dict ):
                                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "result2", ghgwd.result )
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
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, '   ({}) {!r} normalized to ({}) {!r}'.format( len(word), word, len(normalizedWord), normalizedWord ) )
                            ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, '{!r} is '.format( normalizedWord ), end=None )
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
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ghgwdResultB1", ghgwd.result )
                            if ghgwd.result is None: # cancel
                                self.requestMissingGlosses = False
                            elif ghgwd.result == 'S': # skip
                                needToRequestMissingGlosses = False
                            elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                command = ghgwd.result
                            elif isinstance( ghgwd.result, dict ):
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "result3", ghgwd.result )
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
                            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "No generic gloss found for ({}) {}{}".format( len(word), word, \
                                #' to ({}) {}'.format( len(normalizedWord), normalizedWord ) if normalizedWord!=word else '' ) )
                            if self.requestMissingGlosses and requestMissingGlossesNow and not BiblelatorGlobals.theApp.isStarting:
                                tempBundle = refText, normalizedWord, strongsNumber, morphology, self.internalBible.expandMorphologyAbbreviations( morphology )
                                #self.parentWindow.setStatus( self.internalBible.expandMorphologyAbbreviations( morphology ) )
                                ghgwd = GetHebrewGlossWordsDialog( self, _("Enter new generic/specific glosses"), tempBundle, geometry=self.glossWindowGeometry )
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ghgwdResultB2", ghgwd.result )
                                if ghgwd.result is None: # cancel
                                    self.requestMissingGlosses = False
                                elif ghgwd.result == 'S': # skip
                                    needToRequestMissingGlosses = False
                                elif ghgwd.result in ('L','R','LL','RR'): # go left/right
                                    command = ghgwd.result
                                elif isinstance( ghgwd.result, dict ):
                                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "result4", ghgwd.result )
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
                        BiblelatorGlobals.theApp.doGotoPreviousVerse()
                        return False
                    elif command == 'RR':
                        BiblelatorGlobals.theApp.doGotoNextVerse()
                        return False
                    elif command == 'E': pass
                    else: assert command is None
                    #bundlesAcross += 1
                if BiblelatorGlobals.theApp.isStarting: break
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
                if DEBUGGING_THIS_MODULE:
                    vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "displayAppendVerse.appendBundle( {}, wN={}, cBF={}, hTF={} )".format( textBundle, wordNumber, currentBundleFlag, haveTextFlag ) )
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
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bundleEntry", bundleEntry )
                #(w,h) = (font.measure(text),font.metrics("linespace"))
                bundleWidthPixels = fonts[j].measure( bundleEntry ) + 6 # for safety
                bundleWidthsPixels.append( bundleWidthPixels )
                tabStopsUsed.append( int( bundleWidthPixels / self.tabStopPixels ) + 1 )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, j, currentBundleFlag, bundleEntry, bundleWidthPixels )
                if bundleWidthPixels > maxWidthPixels: maxWidthPixels = bundleWidthPixels
            maxTabStopsUsed = int( maxWidthPixels / self.tabStopPixels ) + 1
            #if maxTabStopsUsed>1:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Need more tabs bWP={} tSU={} mWP={} tSP={} mTSU={} bpL={}" \
                        #.format( bundleWidthsPixels, tabStopsUsed, maxWidthPixels, self.tabStopPixels, maxTabStopsUsed, self.bundlesPerLine ) )

            if self.acrossIndex+maxTabStopsUsed >= self.bundlesPerLine: # Start a new line
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Start new bundle line" )
                #self.textBox.insert( tk.END, '\n'*(self.numInterlinearLines+1) ) # Make sure we have enough blank lines
                insertAtEnd( '\n'*(self.numInterlinearLines+1), None ) # Make sure we have enough blank lines
                self.lineNumber += self.numInterlinearLines + 1
                self.acrossIndex = 0
                haveTextFlag = False
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "About to display bundle {} at row={} col={}".format( textBundle, self.lineNumber, self.acrossIndex ) )

            # Now display the actual bundles (with tabs appended)
            #for j,bundleEntry in enumerate( textBundle ):
            for j,(bundleEntry,bundleWidthPixels,thisTabStopsUsed) in enumerate( zip(textBundle,bundleWidthsPixels,tabStopsUsed) ):
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bundleEntry", bundleEntry, bundleWidthPixels )
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bundleEntry", bundleEntry )
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
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "    Appending {} trailing tab{} to {!r}" \
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
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "displayAppendVerse2( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
            assert cVM == 'ByVerse'

            #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.displayAppendVerse( {}, {}, …, {}, {} ) for {}/{}".format( firstFlag, verseKey, lastFlag, currentVerseFlag, fVM, cVM ) )
                ##try: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.displayAppendVerse( {}, {}, {}, {} )".format( firstFlag, verseKey, verseContextData, currentVerseFlag ) )
                ##except UnicodeEncodeError: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.displayAppendVerse", firstFlag, verseKey, currentVerseFlag )

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
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Marks", previousMarkName, currentMarkName, nextMarkName )

            lastCharWasSpace = haveTextFlag = not firstFlag

            if verseContextData is None:
                if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE and C!=0 and V!=0:
                    vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  ", "displayAppendVerse has no data for", verseKey )
                verseDataList = context = None
            elif isinstance( verseContextData, tuple ):
                assert len(verseContextData) == 2
                verseDataList, context = verseContextData
                #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   VerseDataList: {}".format( verseDataList ) )
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   Context: {}".format( context ) )
            elif isinstance( verseContextData, str ):
                verseDataList, context = verseContextData.split( '\n' ), None
            elif BibleOrgSysGlobals.debugFlag: halt

            # Display the context preceding the first verse
            if firstFlag:
                if context:
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "context", context )
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting context mark to {}".format( previousMarkName ) )
                    #self.textBox.mark_set( previousMarkName, tk.INSERT )
                    #self.textBox.mark_gravity( previousMarkName, tk.LEFT )
                    insertAtEnd( ' '+_("Prior context")+':', 'contextHeader' )
                    contextString, firstMarker = "", True
                    for someMarker in context:
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  someMarker", someMarker )
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

            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting mark to {}".format( currentMarkName ) )
            self.textBox.mark_set( currentMarkName, tk.INSERT )
            self.textBox.mark_gravity( currentMarkName, tk.LEFT )

            if verseDataList is None:
                if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE and C!=0 and V!=0:
                    vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  ", "HebrewInterlinearBibleBoxAddon.displayAppendVerse has no data for", self.moduleID, verseKey )
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
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "marker={} cleanText={!r}{}".format( marker, cleanText, " extras={}".format( extras ) if extras else '' ) )
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "marker={} cleanText={!r} extras={}".format( marker, cleanText, extras ) )
                    #if adjustedText and adjustedText!=cleanText:
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, ' '*(len(marker)+4), "adjustedText={!r}".format( adjustedText ) )
                    #if originalText and originalText!=cleanText:
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, ' '*(len(marker)+4), "originalText={!r}".format( originalText ) )
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
                    if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                        vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  displayAppendVerse", lastParagraphMarker, haveTextFlag, marker, repr(cleanText) )

                    if fVM == 'Unformatted':
                        if marker and marker[0]=='¬': pass # Ignore end markers for now
                        elif marker in ('headers','intro','chapters','list',): pass # Ignore added markers for now
                        else:
                            if isinstance( verseDataEntry, str ): # from a Bible text editor window
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "marker={!r}, verseDataEntry={!r}".format( marker, verseDataEntry ) )
                                insertAtEnd( verseDataEntry, marker ) # Do it just as is!
                            else: # not a str, i.e., not a text editor, but a viewable resource
                                #if hadVerseText and marker in ( 's', 's1', 's2', 's3' ):
                                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Setting s mark to {}".format( nextMarkName ) )
                                    #self.textBox.mark_set( nextMarkName, tk.INSERT )
                                    #self.textBox.mark_gravity( nextMarkName, tk.LEFT )
                                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  Inserting ({}): {!r}".format( marker, verseDataEntry ) )
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
                        elif marker in ('headers','intro','chapters','list',):
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
                            #else: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "   Ignore C={}".format( cleanText ) )
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
                    #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "endMarkers", endMarkers )
                    insertAtEnd( ' '+ _("End context")+':', 'contextHeader' )
                    contextString, firstMarker = "", True
                    for someMarker in endMarkers:
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  someMarker", someMarker )
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
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "xy", repr(xy) ) # e.g.., '@34,77'
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "ixy", repr(self.textBox.index(xy)) ) # e.g., '4.3'

        tagNames = self.textBox.tag_names( xy )
        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tn", tagNames )
        for tagName in tagNames:
            if tagName.startswith( 'W' ):
                bundleNumber = tagName[1:]
                assert '.' in bundleNumber
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bundleNumber", repr(bundleNumber) )
                return bundleNumber
    # end of HebrewInterlinearBibleBoxAddon._getBundleNumber

    def selectBundle( self, event ):
        """
        Handle a left-click on a bundle.

        Splits bundleNumber into a
            word number (e.g., first word is word 1) and
            line number (e.g., first line in bundle is line 0).
        """
        fnPrint( DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.selectBundle()" )

        bundleNumber = self._getBundleNumber( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Clicked on {}".format( repr(clickedText) ) )

        if bundleNumber:
            wordNumberString, lineNumberString = bundleNumber.split( '.', 1 )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "select", "wn", wordNumberString, "ln", lineNumberString )
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
        fnPrint( DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.editBundle()" )

        bundleNumber = self._getBundleNumber( event )

        #if BibleOrgSysGlobals.debugFlag: # Find the range of the tag nearest the index
            #xy = '@{0},{1}'.format( event.x, event.y )
            #tagNames = self.tag_names( xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tn", tagNames )
            #for tagName in tagNames:
                #if tagName.startswith( 'href' ): break
            #tag_range = self.tag_prevrange( tagName, xy )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "tr", repr(tag_range) ) # e.g., ('6.0', '6.13')
            #clickedText = self.get( *tag_range )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Clicked on {}".format( repr(clickedText) ) )

        if bundleNumber:
            wordNumberString, lineNumberString = bundleNumber.split( '.', 1 )
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "edit", "wn", wordNumberString, "ln", lineNumberString )
            self.clearText() # Leaves the text box enabled
            self.displayAppendVerse( self.lastDAVargs[0], self.lastDAVargs[1], self.lastDAVargs[2], self.lastDAVargs[3], self.lastDAVargs[4], int(wordNumberString), 'E', self.lastDAVargs[7], self.lastDAVargs[8] )
    # end of HebrewInterlinearBibleBoxAddon.editBundle


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden if an edit box needs to save files first.
        """
        fnPrint( DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.doClose( {} )".format( event ) )

        try: self.internalBible.saveAnyChangedGlosses()
        except AttributeError: # if self.internalBible is None
            vPrint( 'Never', DEBUGGING_THIS_MODULE, "Why is Hebrew internalBible None?" )

        self.destroy()
    # end of HebrewInterlinearBibleBoxAddon.doClose


    #def getBeforeAndAfterBibleData( self, newVerseKey ):
        #"""
        #Returns the requested verse, the previous verse, and the next n verses.
        #"""
        #if BibleOrgSysGlobals.debugFlag:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.getBeforeAndAfterBibleData( {} )".format( newVerseKey ) )
            #assert isinstance( newVerseKey, SimpleVerseKey )

        #BBB, C, V = newVerseKey.getBCV()
        #intC, intV = newVerseKey.getChapterNumberInt(), newVerseKey.getVerseNumberInt()

        ## Determine the PREVIOUS valid verse numbers
        #prevBBB, prevIntC, prevIntV = BBB, intC, intV
        #previousVersesData = []
        #for n in range( -BiblelatorGlobals.theApp.viewVersesBefore, 0 ):
            #failed = False
            #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "  getBeforeAndAfterBibleData here with", n, prevIntC, prevIntV )
            #if prevIntV > 0: prevIntV -= 1
            #elif prevIntC > 0:
                #prevIntC -= 1
                #try: prevIntV = self.getNumVerses( prevBBB, prevIntC )
                #except KeyError:
                    #if prevIntC != 0: # we can expect an error for chapter zero
                        #logging.error( _("HebrewInterlinearBibleBoxAddon.getBeforeAndAfterBibleData1 failed at {} {}").format( prevBBB, prevIntC ) )
                    #failed = True
                ##if not failed:
                    ##if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, " Went back to previous chapter", prevIntC, prevIntV, "from", BBB, C, V )
            #else:
                #try: prevBBB = self.BibleOrganisationalSystem.getPreviousBookCode( BBB )
                #except KeyError: prevBBB = None
                #if prevBBB is None: failed = True
                #else:
                    #prevIntC = self.getNumChapters( prevBBB )
                    #prevIntV = self.getNumVerses( prevBBB, prevIntC )
                    #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
                        #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, " Went back to previous book", prevBBB, prevIntC, prevIntV, "from", BBB, C, V )
                    #if prevIntC is None or prevIntV is None:
                        #logging.error( _("HebrewInterlinearBibleBoxAddon.getBeforeAndAfterBibleData2 failed at {} {}:{}").format( prevBBB, prevIntC, prevIntV ) )
                        ##failed = True
                        #break
            #if not failed and prevIntV is not None:
                ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "getBeforeAndAfterBibleData XXX", repr(prevBBB), repr(prevIntC), repr(prevIntV) )
                #assert prevBBB and isinstance(prevBBB, str)
                #previousVerseKey = SimpleVerseKey( prevBBB, prevIntC, prevIntV )
                #previousVerseData = self.getCachedVerseData( previousVerseKey )
                #if previousVerseData: previousVersesData.insert( 0, (previousVerseKey,previousVerseData,) ) # Put verses in backwards

        ## Determine the NEXT valid verse numbers
        #nextBBB, nextIntC, nextIntV = BBB, intC, intV
        #nextVersesData = []
        #for n in range( BiblelatorGlobals.theApp.viewVersesAfter ):
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

        #theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'HebrewInterlinearBibleBoxAddon doBibleFind' )
        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.doBibleFind( {} )".format( event ) )

        #try: haveInternalBible = self.internalBible is not None
        #except AttributeError: haveInternalBible = False
        #if not haveInternalBible:
            #logging.critical( _("No Bible to search") )
            #return
        ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "intBib", self.internalBible )

        #self.BibleFindOptionsDict['currentBCV'] = self.currentVerseKey.getBCV()
        #gBSTD = GetBibleFindTextDialog( self, self.internalBible, self.BibleFindOptionsDict, title=_('Find in Bible') )
        #if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', DEBUGGING_THIS_MODULE, "gBSTDResult", repr(gBSTD.result) )
        #if gBSTD.result:
            #if BibleOrgSysGlobals.debugFlag: assert isinstance( gBSTD.result, dict )
            #self.BibleFindOptionsDict = gBSTD.result # Update our search options dictionary
            #self.doActualBibleFind()
        #theApp.setReadyStatus()

        ##return tkBREAK
    ## end of HebrewInterlinearBibleBoxAddon.doBibleFind


    #def doActualBibleFind( self, extendTo=None ):
        #"""
        #This function (called by the above doBibleFind),
            #invokes the actual search (or redoes the search)
            #assuming that the search parameters are already defined.
        #"""
        #from ChildWindows import FindResultWindow

        #theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, 'HebrewInterlinearBibleBoxAddon doActualBibleFind' )
        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon.doActualBibleFind( {} )".format( extendTo ) )

        #theApp.setWaitStatus( _("Searching…") )
        ##self.textBox.update()
        ##self.textBox.focus()
        ##self.lastfind = key
        #theApp.logUsage( PROGRAM_NAME, DEBUGGING_THIS_MODULE, ' doActualBibleFind {}'.format( self.BibleFindOptionsDict ) )
        ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "bookList", repr(self.BibleFindOptionsDict['bookList']) )
        #bookCode = None
        #if isinstance( self.BibleFindOptionsDict['bookList'], str ) \
        #and self.BibleFindOptionsDict['bookList'] != 'ALL':
            #bookCode = self.BibleFindOptionsDict['bookList']
        #self._prepareInternalBible( bookCode, self.BibleFindOptionsDict['givenBible'] ) # Make sure that all books are loaded
        ## We search the loaded Bible processed lines
        #self.BibleFindOptionsDict, resultSummaryDict, findResultList = self.BibleFindOptionsDict['givenBible'].findText( self.BibleFindOptionsDict )
        ##dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Got findResults", findResults )
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
            #theApp.childWindows.append( findResultWindow )
        #theApp.setReadyStatus()
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
        #if BibleOrgSysGlobals.debugFlag and DEBUGGING_THIS_MODULE:
            #dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "HebrewInterlinearBibleBoxAddon._prepareInternalBible()" )
        #if givenBible is None: givenBible = self.internalBible

        #if self.modified(): self.doSave() # NOTE: Read-only boxes/windows don't even have a doSave() function
        #if givenBible is not None:
            #theApp.setWaitStatus( _("Preparing internal Bible…") )
            #if bookCode is None:
                #theApp.setWaitStatus( _("Loading/Preparing internal Bible…") )
                #givenBible.load()
            #else:
                #theApp.setWaitStatus( _("Loading/Preparing internal Bible book…") )
                #givenBible.loadBook( bookCode )
    ## end of HebrewInterlinearBibleBoxAddon._prepareInternalBible
# end of class HebrewInterlinearBibleBoxAddon



def briefDemo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, PROGRAM_NAME_VERSION, LAST_MODIFIED_DATE )
    dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Running demo…" )

    tkRootWindow = Tk()
    tkRootWindow.title( f'{PROGRAM_NAME_VERSION} {_("last modified")} {LAST_MODIFIED_DATE}' if BibleOrgSysGlobals.debugFlag else PROGRAM_NAME_VERSION )

    HTMLTextBoxbox = HTMLTextBox( tkRootWindow )
    HTMLTextBoxbox.pack()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( PROGRAM_NAME_VERSION )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of TextBoxes.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, PROGRAM_NAME_VERSION, LAST_MODIFIED_DATE )
    dPrint( 'Quiet', DEBUGGING_THIS_MODULE, "Running demo…" )

    tkRootWindow = Tk()
    tkRootWindow.title( f'{PROGRAM_NAME_VERSION} {_("last modified")} {LAST_MODIFIED_DATE}' if BibleOrgSysGlobals.debugFlag else PROGRAM_NAME_VERSION )

    HTMLTextBoxbox = HTMLTextBox( tkRootWindow )
    HTMLTextBoxbox.pack()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( PROGRAM_NAME_VERSION )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    tkRootWindow.mainloop()
# end of TextBoxes.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of TextBoxes.py
