#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# TextBoxes.py
#
# Base of Bible and lexicon resource windows for Biblelator Bible display/editing
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
Base widgets to allow display and manipulation of
    various Bible and lexicon, etc. child windows.

class HTMLText( tk.Text )
    __init__( self, *args, **kwargs )
    insert( self, point, iText )
    _getURL( self, event )
    openHyperlink( self, event )
    overHyperlink( self, event )
    leaveHyperlink( self, event )

class CustomText( tk.Text )
    __init__( self, *args, **kwargs )
    setTextChangeCallback( self, callableFunction )

class ChildBox
    __init__( self, parentApp )
    _createStandardKeyboardBinding( self, name, command )
    createStandardKeyboardBindings( self )
    setFocus( self, event )
    doCopy( self, event=None )
    doSelectAll( self, event=None )
    doGotoWindowLine( self, event=None, forceline=None )
    doWindowFind( self, event=None, lastkey=None )
    doWindowRefind( self, event=None )
    doShowInfo( self, event=None )
    clearText( self ) # Leaves in normal state
    isEmpty( self )
    modified( self )
    getAllText( self )
    setAllText( self, newText )
    doShowMainWindow( self, event=None )
    doClose( self, event=None )
"""

from gettext import gettext as _

LastModifiedDate = '2016-06-30' # by RJH
ShortProgName = "TextBoxes"
ProgName = "Specialised text widgets"
ProgVersion = '0.37'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True


import logging

import tkinter as tk
from tkinter.simpledialog import askstring, askinteger

# Biblelator imports
from BiblelatorGlobals import APP_NAME, START, errorBeep

# BibleOrgSys imports
if __name__ == '__main__': import sys; sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
from BibleStylesheets import DEFAULT_FONTNAME



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
    return '{}{}'.format( nameBit, errorBit )
# end of exp



KNOWN_HTML_TAGS = ('!DOCTYPE','html','head','meta','link','title','body','div',
                   'h1','h2','h3','p','li','a','span','table','tr','td','i','b','em','small')
NON_FORMATTING_TAGS = 'html','head','body','div','table','tr','td', # Not sure about div yet...........
HTML_REPLACEMENTS = ('&nbsp;',' '),('&lt;','<'),('&gt;','>'),('&amp;','&'),


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
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("HTMLText.__init__( {}, {} )").format( args, kwargs ) )
        tk.Text.__init__( self, *args, **kwargs ) # initialise the base class

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
        for tag in self.styleDict:
            if tag.endswith( '_a' ): assert tag in aTags
        for tag in aTags:
            assert tag in self.styleDict
            self.tag_bind( tag, '<Button-1>', self.openHyperlink )
            #self.tag_bind( tag, '<Enter>', self.overHyperlink )
            #self.tag_bind( tag, '<Leave>', self.leaveHyperlink )

        self._lastOverLink = None
    # end of HTMLText.__init__


    def insert( self, point, iText ):
        """
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("HTMLText.insert( {}, {} )").format( repr(point), repr(iText) ) )

        if point != tk.END:
            logging.critical( exp("HTMLText.insert doesn't know how to insert at {}").format( repr(point) ) )
            tk.Text.insert( self, point, iText )
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
                tk.Text.insert( self, point, remainingText, currentFormatTags ) # just insert all the remainingText
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
                            tk.Text.insert( self, point, insertText, (combinedFormats, hypertag,) )
                            self.tag_bind( hypertag, '<Enter>', self.overHyperlink )
                            self.tag_bind( hypertag, '<Leave>', self.leaveHyperlink )
                        else: tk.Text.insert( self, point, insertText, combinedFormats )
                        #first = False
                    remainingText = remainingText[ix:]
                #try: print( "  tag", repr(remainingText[:5]) )
                #except UnicodeEncodeError: print( "  tag" )
                ixEnd = remainingText.find( '>' )
                ixNext = remainingText.find( '<', 1 )
                #print( "ixEnd", ixEnd, "ixNext", ixNext )
                if ixEnd == -1 \
                or (ixEnd!=-1 and ixNext!=-1 and ixEnd>ixNext): # no tag close or wrong tag closed
                    logging.critical( exp("HTMLText.insert: Missing close bracket") )
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
                    logging.critical( exp("HTMLText.insert: Unexpected empty HTML tags") )
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
                    #print( exp("Got HTML {} close tag").format( repr(HTMLTag) ) )
                    #print( "cHT1", currentHTMLTags )
                    #print( "cFT1", currentFormatTags )
                    if currentHTMLTags and HTMLTag == currentHTMLTags[-1]: # all good
                        currentHTMLTags.pop() # Drop it
                        if HTMLTag not in NON_FORMATTING_TAGS:
                            currentFormatTags.pop()
                    elif currentHTMLTags:
                        logging.critical( exp("HTMLText.insert: Expected to close {} but got {} instead").format( repr(currentHTMLTags[-1]), repr(HTMLTag) ) )
                    else:
                        logging.critical( exp("HTMLText.insert: Unexpected HTML close {} close marker").format( repr(HTMLTag) ) )
                    #print( "cHT2", currentHTMLTags )
                    #print( "cFT2", currentFormatTags )
                else: # it's not a close tag so must be an open tag
                    if HTMLTag not in KNOWN_HTML_TAGS:
                        logging.critical( exp("HTMLText doesn't recognise or handle {} as an HTML tag").format( repr(HTMLTag) ) )
                        #currentHTMLTags.append( HTMLTag ) # remember it anyway in case it's closed later
                        continue
                    if HTMLTag in ('h1','h2','h3','p','li','table','tr',):
                        tk.Text.insert( self, point, '\n' )
                    #elif HTMLTag in ('li',):
                        #tk.Text.insert( self, point, '\n' )
                    elif HTMLTag in ('td',):
                        tk.Text.insert( self, point, '\t' )
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
                            else: logging.critical( "Ignoring {} attribute on {} tag".format( bit, repr(HTMLTag) ) )
                    if not selfClosing:
                        if HTMLTag != '!DOCTYPE':
                            currentHTMLTags.append( HTMLTag )
                            if HTMLTag not in NON_FORMATTING_TAGS:
                                currentFormatTags.append( formatTag )
        if currentHTMLTags:
            logging.critical( exp("HTMLText.insert: Left-over HTML tags: {}").format( currentHTMLTags ) )
        if currentFormatTags:
            logging.critical( exp("HTMLText.insert: Left-over format tags: {}").format( currentFormatTags ) )
    # end of HTMLText.insert


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
    # end of HTMLText._getURL


    def openHyperlink( self, event ):
        """
        Handle a click on a hyperlink.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("HTMLText.openHyperlink()") )
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
    # end of HTMLText.openHyperlink


    def overHyperlink( self, event ):
        """
        Handle a mouseover on a hyperlink.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("HTMLText.overHyperlink()") )
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
    # end of HTMLText.overHyperlink

    def leaveHyperlink( self, event ):
        """
        Handle a mouseover on a hyperlink.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( exp("HTMLText.leaveHyperlink()") )
        self.master.leaveLink()
    # end of HTMLText.leaveHyperlink
# end of HTMLText class



class CustomText( tk.Text ):
    """
    A custom Text widget which calls a user function whenever the text changes.

    Adapted from http://stackoverflow.com/questions/13835207/binding-to-cursor-movement-doesnt-change-insert-mark
    """
    def __init__( self, *args, **kwargs ):
        """
        """
        if BibleOrgSysGlobals.debugFlag:
            print( exp("CustomText.__init__( {}, {} )").format( args, kwargs ) )
        tk.Text.__init__( self, *args, **kwargs ) # initialise the base class

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
    # end of CustomText.__init__


    def _callback( self, result, *args ):
        """
        This little function does the actual call of the user routine
            to handle when the CustomText changes.
        """
        self.callbackFunction( result, *args )
    # end of CustomText._callback


    def setTextChangeCallback( self, callableFunction ):
        """
        Just a little function to remember the routine to call
            when the CustomText changes.
        """
        self.callbackFunction = callableFunction
    # end of CustomText.setTextChangeCallback
# end of CustomText class



class ChildBox():
    """
    A set of functions that work for any frame or window that has a member: self.textBox
    """
    def __init__( self, parentApp ):
        """
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.__init__( {} )").format( parentApp ) )
            assert parentApp
        self.parentApp = parentApp

        self.myKeyboardBindingsList = []
        if BibleOrgSysGlobals.debugFlag: self.myKeyboardShortcutsList = [] # Just for catching setting of duplicates

        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.__init__ finished.") )
    # end of ChildBox.__init__


    def _createStandardKeyboardBinding( self, name, command ):
        """
        Called from createStandardKeyboardBindings to do the actual work.
        """
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( exp("ChildBox._createStandardKeyboardBinding( {} )").format( name ) )

        try: kBD = self.parentApp.keyBindingDict
        except AttributeError: kBD = self.parentWindow.parentApp.keyBindingDict
        assert (name,kBD[name][0],) not in self.myKeyboardBindingsList
        if name in kBD:
            for keyCode in kBD[name][1:]:
                #print( "Bind {} for {}".format( repr(keyCode), repr(name) ) )
                self.textBox.bind( keyCode, command )
                if BibleOrgSysGlobals.debugFlag:
                    assert keyCode not in self.myKeyboardShortcutsList
                    self.myKeyboardShortcutsList.append( keyCode )
            self.myKeyboardBindingsList.append( (name,kBD[name][0],) )
        else: logging.critical( 'No key binding available for {}'.format( repr(name) ) )
    # end of ChildBox._createStandardKeyboardBinding()

    def createStandardKeyboardBindings( self ):
        """
        Create keyboard bindings for this widget.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.createStandardKeyboardBindings()") )

        for name,command in ( ('SelectAll',self.doSelectAll), ('Copy',self.doCopy),
                             ('Find',self.doWindowFind), ('Refind',self.doWindowRefind),
                             ('Help',self.doHelp), ('Info',self.doShowInfo), ('About',self.doAbout),
                             ('Close',self.doClose), ('ShowMain',self.doShowMainWindow), ):
            self._createStandardKeyboardBinding( name, command )
    # end of ChildBox.createStandardKeyboardBindings()


    def setFocus( self, event ):
        '''Explicitly set focus, so user can select and copy text'''
        self.textBox.focus_set()


    def doCopy( self, event=None ):
        """
        Copy the selected text onto the clipboard.
        """
        from BiblelatorDialogs import showerror
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doCopy( {} )").format( event ) )

        if not self.textBox.tag_ranges( tk.SEL ):       # save in cross-app clipboard
            errorBeep()
            showerror( self, APP_NAME, _("No text selected") )
        else:
            copyText = self.textBox.get( tk.SEL_FIRST, tk.SEL_LAST)
            print( "  copied text", repr(copyText) )
            self.clipboard_clear()
            self.clipboard_append( copyText )
    # end of ChildBox.doCopy


    def doSelectAll( self, event=None ):
        """
        Select all the text in the text box.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doSelectAll( {} )").format( event ) )

        self.textBox.tag_add( tk.SEL, START, tk.END+'-1c' )   # select entire text
        self.textBox.mark_set( tk.INSERT, START )          # move insert point to top
        self.textBox.see( tk.INSERT )                      # scroll to top
    # end of ChildBox.doSelectAll


    def doGotoWindowLine( self, event=None, forceline=None ):
        """
        """
        from BiblelatorDialogs import showerror
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'ChildBox doGotoWindowLine {}'.format( forceline ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doGotoWindowLine( {}, {} )").format( event, forceline ) )

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
                showerror( self, APP_NAME, _("No such line number") )
    # end of ChildBox.doGotoWindowLine


    def doWindowFind( self, event=None, lastkey=None ):
        """
        """
        from BiblelatorDialogs import showerror
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'ChildBox doWindowFind {!r}'.format( lastkey ) )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doWindowFind( {}, {!r} )").format( event, lastkey ) )

        key = lastkey or askstring( APP_NAME, _("Enter search string") )
        self.textBox.update()
        self.textBox.focus()
        self.lastfind = key
        if key:
            nocase = self.optionsDict['caseinsens']
            where = self.textBox.search( key, tk.INSERT, tk.END, nocase=nocase )
            if not where:                                          # don't wrap
                errorBeep()
                showerror( self, APP_NAME, _("String {!r} not found").format( key if len(key)<20 else (key[:18]+'…') ) )
            else:
                pastkey = where + '+%dc' % len(key)           # index past key
                self.textBox.tag_remove( tk.SEL, START, tk.END )         # remove any sel
                self.textBox.tag_add( tk.SEL, where, pastkey )        # select key
                self.textBox.mark_set( tk.INSERT, pastkey )           # for next find
                self.textBox.see( where )                          # scroll display
    # end of ChildBox.doWindowFind


    def doWindowRefind( self, event=None ):
        """
        """
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'ChildBox doWindowRefind' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doWindowRefind( {} ) for {!r}").format( event, self.lastfind ) )

        self.doWindowFind( lastkey=self.lastfind )
    # end of ChildBox.doWindowRefind


    def doShowInfo( self, event=None ):
        """
        Pop-up dialog giving text statistics and cursor location;
        caveat (2.1): Tk insert position column counts a tab as one
        character: translate to next multiple of 8 to match visual?
        """
        from BiblelatorDialogs import showinfo
        self.parentApp.logUsage( ProgName, debuggingThisModule, 'ChildBox doShowInfo' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doShowInfo( {} )").format( event ) )

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
        showinfo( self, 'Window Information', infoString )
    # end of ChildBox.doShowInfo


    ############################################################################
    # Utilities, useful outside this class
    ############################################################################

    def clearText( self ): # Leaves in normal state
        self.textBox.config( state=tk.NORMAL )
        self.textBox.delete( START, tk.END )
    # end of ChildBox.updateText


    def isEmpty( self ):
        return not self.getAllText()
    # end of ChildBox.isEmpty


    def modified( self ):
        return self.textBox.edit_modified()
    # end of ChildBox.modified


    def getAllText( self ):
        """
        Returns all the text as a string.
        """
        return self.textBox.get( START, tk.END+'-1c' )
    # end of ChildBox.getAllText


    def setAllText( self, newText ):
        """
        Sets the textBox (assumed to be enabled) to the given text
            then positions the insert cursor at the BEGINNING of the text.

        caller: call self.update() first if just packed, else the
        initial position may be at line 2, not line 1 (2.1; Tk bug?)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.setAllText( {!r} )").format( newText ) )

        self.textBox.config( state=tk.NORMAL ) # In case it was disabled
        self.textBox.delete( START, tk.END ) # Delete everything that's existing
        self.textBox.insert( tk.END, newText )
        self.textBox.mark_set( tk.INSERT, START ) # move insert point to top
        self.textBox.see( tk.INSERT ) # scroll to top, insert is set

        self.textBox.edit_reset() # clear undo/redo stks
        self.textBox.edit_modified( tk.FALSE ) # clear modified flag
    # end of ChildBox.setAllText


    def doShowMainWindow( self, event=None ):
        """
        Display the main window (it might be minimised or covered).
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doShowMainWindow( {} )").format( event ) )

        #self.parentApp.rootWindow.iconify() # Didn't help
        self.parentApp.rootWindow.withdraw() # For some reason, doing this first makes the window always appear above others
        self.parentApp.rootWindow.update()
        self.parentApp.rootWindow.deiconify()
        #self.parentApp.rootWindow.focus_set()
        self.parentApp.rootWindow.lift() # aboveThis=self )
    # end of ChildBox.doShowMainWindow


    def doClose( self, event=None ):
        """
        Called from the GUI.

        Can be overridden if an edit box needs to save files first.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( exp("ChildBox.doClose( {} )").format( event ) )

        self.destroy()
    # end of ChildBox.doClose
# end of ChildBox class



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo…") )

    tkRootWindow = Tk()
    tkRootWindow.title( ProgNameVersionDate if BibleOrgSysGlobals.debugFlag else ProgNameVersion )

    HTMLTextbox = HTMLText( tkRootWindow )
    HTMLTextbox.pack()

    #application = Application( parent=tkRootWindow, settings=settings )
    # Calls to the window manager class (wm in Tk)
    #application.master.title( ProgNameVersion )
    #application.master.minsize( application.minimumXSize, application.minimumYSize )

    # Start the program running
    tkRootWindow.mainloop()
# end of TextBoxes.demo


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
# end of TextBoxes.py