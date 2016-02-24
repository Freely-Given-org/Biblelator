#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# AutocompleteFunctions.py
#
# Functions to support the autocomplete function in text editors
#
# Copyright (C) 2016 Robert Hunt
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
"""

from gettext import gettext as _

LastModifiedDate = '2016-02-24' # by RJH
ShortProgName = "AutocompleteFunctions"
ProgName = "Biblelator Autocomplete Functions"
ProgVersion = '0.35'
ProgNameVersion = '{} v{}'.format( ProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = True

import sys, logging

#from tkinter.simpledialog import askstring, askinteger
#from tkinter.filedialog import asksaveasfilename
#from tkinter.colorchooser import askcolor
#from tkinter.ttk import Style, Frame

# Biblelator imports
#from BiblelatorGlobals import DEFAULT
    ##APP_NAME, DATA_FOLDER_NAME, START, DEFAULT, EDIT_MODE_NORMAL, EDIT_MODE_USFM, BIBLE_GROUP_CODES
##from BiblelatorDialogs import showerror, showinfo, YesNoDialog, OkCancelDialog, GetBibleBookRangeDialog
#from BiblelatorHelpers import createEmptyUSFMBookText, calculateTotalVersesForBook, mapReferenceVerseKey, mapParallelVerseKey
#from TextBoxes import CustomText
##from ChildWindows import ChildWindow, HTMLWindow
#from BibleResourceWindows import BibleBox, BibleResourceWindow
##from BibleReferenceCollection import BibleReferenceCollectionWindow
#from TextEditWindow import TextEditWindow, REFRESH_TITLE_TIME, CHECK_DISK_CHANGES_TIME

# BibleOrgSys imports
sys.path.append( '../BibleOrgSys/' )
import BibleOrgSysGlobals
#from VerseReferences import SimpleVerseKey
#from BibleWriter import setDefaultControlFolder



HUNSPELL_DICTIONARY_FOLDERS = ( '/usr/share/hunspell/', )



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
        nameBit = '{}{}{}: '.format( ShortProgName, '.' if nameBit else '', nameBit )
    return '{}{}'.format( nameBit+': ' if nameBit else '', _(errorBit) )
# end of exp



def setAutocompleteWords( self, wordList, append=False ):
    """
    Given a word list, set the entries into the autocomplete words
        and then do necessary house-keeping.

    Note that the original word order is preserved (if the wordList has an order)
        so that more common/likely words can appear at the top of the list if desired.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( exp("AutocompleteFunctions.setAutocompleteWords( {} )").format( wordList, append ) )
        print( exp("AutocompleteFunctions.setAutocompleteWords( {}.., {} )").format( len(wordList), append ) )

    if not append: self.autocompleteWords = {}

    for word in wordList:
        if "'" not in word and '1' not in word:
            if len(word) >= self.autocompleteMinLength:
                firstLetter, remainder = word[0], word[1:]
                if firstLetter not in self.autocompleteWords: self.autocompleteWords[firstLetter] = []
                if remainder in self.autocompleteWords[firstLetter]:
                    if 0 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                        print( "    setAutocompleteWords discarded {!r} duplicate".format( word ) )
                else: # not already in the list
                    self.autocompleteWords[firstLetter].append( remainder )
                    for char in word:
                        if char not in self.autocompleteWordChars:
                            if BibleOrgSysGlobals.debugFlag: assert char not in ' \n\r'
                            if char not in '.':
                                self.autocompleteWordChars += char
                                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                                    print( "    setAutocompleteWords added {!r} as new wordChar".format( char ) )
            #elif BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #print( "    setAutocompleteWords discarded {!r} as too short".format( word ) )
        elif BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            if "'" not in word:
                print( "    setAutocompleteWords discarded {!r} as unwanted".format( word ) )

    if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule: # write wordlist
        print( "  setAutocompleteWords: Writing autocomplete words to file..." )
        sortedKeys = sorted( self.autocompleteWords.keys() )
        with open( 'autocompleteWordList.txt', 'wt', encoding='utf-8' ) as wordFile:
            wordCount = 0
            for firstLetter in sortedKeys:
                for remainder in sorted( self.autocompleteWords[firstLetter] ):
                    wordFile.write( firstLetter+remainder )
                    wordCount += 1
                    if wordCount == 8: wordFile.write( '\n' ); wordCount = 0
                    else: wordFile.write( ' ' )

    if BibleOrgSysGlobals.debugFlag: # print stats
        sortedKeys = sorted( self.autocompleteWords.keys() )
        if debuggingThisModule: print( "  autocomplete first letters", len(self.autocompleteWords), sortedKeys )
        grandtotal = 0
        for firstLetter in sortedKeys:
            total = len(self.autocompleteWords[firstLetter])
            if debuggingThisModule:
                print( "    {!r} {:,}{}" \
                    .format( firstLetter, total, '' if total>19 else ' '+str(self.autocompleteWords[firstLetter]) ) )
            grandtotal += total
        print( "  autocomplete total words loaded = {:,}".format( grandtotal ) )
# end of AutocompleteFunctions.setAutocompleteWords



def loadBibleAutocompleteWords( self ):
    """
    Load all the existing words in a USFM or Paratext Bible Project
        to fill the autocomplete mechanism.

    This is rather slow because of course, the entire Bible has to be read and processed first.

    self here is a USFM or ESFM edit window.

    NOTE: This list should theoretically be updated as the user enters new words!
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("AutocompleteFunctions.loadBibleAutocompleteWords()") )

    self.internalBible.loadBooks()
    self.internalBible.discover()
    #print( 'discoveryResults', self.internalBible.discoveryResults )

    # Would be nice to load current book first, but we don't know it yet
    autocompleteWords = []
    for BBB in self.internalBible.discoveryResults:
        if BBB != 'All':
            try:
                # Sort the word-list for the book to put the most common words first
                #print( 'discoveryResults', BBB, self.internalBible.discoveryResults[BBB] )
                #print( BBB, 'mTWC', self.internalBible.discoveryResults[BBB]['mainTextWordCounts'] )
                #qqq = sorted( self.internalBible.discoveryResults[BBB]['mainTextWordCounts'].items(), key=lambda c: -c[1] )
                #print( 'qqq', qqq )
                for word,count in sorted( self.internalBible.discoveryResults[BBB]['mainTextWordCounts'].items(),
                                        key=lambda duple: -duple[1] ):
                    if len(word) >= self.autocompleteMinLength \
                    and word not in autocompleteWords: # just in case we had some (common) words in there already
                        autocompleteWords.append( word )
            except KeyError: pass # Nothing for this book
    #print( 'acW', autocompleteWords )
    setAutocompleteWords( self, autocompleteWords )
    self.autocompleteType = 'Bible'
# end of AutocompleteFunctions.loadBibleAutocompleteWords



def loadBibleBookAutocompleteWords( self ):
    """
    Load all the existing words in a USFM or Paratext Bible book
        to fill the autocomplete mechanism

    self here is a USFM or ESFM edit window.

    NOTE: This list should theoretically be updated as the user enters new words!
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("AutocompleteFunctions.loadBibleBookAutocompleteWords()") )

    BBB = self.currentVerseKey.getBBB()
    print( "  got BBB", repr(BBB) )
    if BBB == 'UNK': return # UNKnown book -- no use here

    self.internalBible.loadBookIfNecessary( self.currentVerseKey.getBBB() )
    #self.internalBible.discoveryResults = OrderedDict()
    discoveryResults = self.internalBible.books[BBB]._discover()
    #print( 'discoveryResults', discoveryResults )

    # Would be nice to load current book first, but we don't know it yet
    autocompleteWords = []
    try:
        # Sort the word-list for the book to put the most common words first
        #print( 'discoveryResults', BBB, discoveryResults )
        #print( BBB, 'mTWC', discoveryResults['mainTextWordCounts'] )
        #qqq = sorted( discoveryResults['mainTextWordCounts'].items(), key=lambda c: -c[1] )
        #print( 'qqq', qqq )
        for word,count in sorted( discoveryResults['mainTextWordCounts'].items(),
                                key=lambda duple: -duple[1] ):
            if len(word) >= self.autocompleteMinLength \
            and word not in autocompleteWords: # just in case we had some (common) words in there already
                autocompleteWords.append( word )
    except KeyError:
        print( "Why did {} have no words???".format( BBB ) )
        #pass # Nothing for this book
    #print( 'acW', autocompleteWords )
    setAutocompleteWords( self, autocompleteWords )
    self.autocompleteType = 'BibleBook'
# end of AutocompleteFunctions.loadBibleBookAutocompleteWords



def loadHunspellAutocompleteWords( self, dictionaryFilepath, encoding='utf-8' ):
    """
    Load all the existing words in a Hunspell-type dictionary
        to fill the autocomplete mechanism

    self here is a text edit window or derivation.

    NOTE: This list maybe should be updated as the user enters new words
        or else have an additional user dictionary.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("AutocompleteFunctions.loadHunspellAutocompleteWords( {}, {} )").format( dictionaryFilepath, encoding ) )

    internalCount = None
    autocompleteWords = []
    lineCount = 0
    with open( dictionaryFilepath, 'rt', encoding=encoding ) as dictionaryFile:
        for line in dictionaryFile:
            lineCount += 1
            if lineCount==1 and encoding.lower()=='utf-8' and line[0]==chr(65279): #U+FEFF or \ufeff
                logging.info( "loadHunspellAutocompleteWords: Detected Unicode Byte Order Marker (BOM) in {}".format( dictionaryFilepath ) )
                line = line[1:] # Remove the Unicode Byte Order Marker (BOM)
            if line[-1]=='\n': line=line[:-1] # Remove trailing newline character
            if not line: continue # Just discard blank lines
            #print( "line", lineCount, repr(line) )

            if lineCount==1 and line.isdigit(): # first line seems to be a count
                internalCount = int( line )
                continue

            try: word, codes = line.split( '/', 1 )
            except ValueError: word, codes = line, ''
            if word in ('3GPP','AA','ACAS',): continue # Throw out rubbish
            #print( "word", repr(word), repr(codes) )
            autocompleteWords.append( word )

            wordDeleteA = word[:-1] if word[-1]=='a' else word
            wordDeleteE = word[:-1] if word[-1]=='e' else word
            wordDeleteEY = word[:-1] if word[-1] in ('e','y',) else word
            wordDeleteEChangeY = wordDeleteE[:-1]+'i' if wordDeleteE[-1]=='y' else wordDeleteE
            wordAddEAfterSY = word+'e' if word[-1]=='s' else word
            wordAddEAfterSY = wordAddEAfterSY[:-1]+'ie' if wordAddEAfterSY[-1]=='y' else wordAddEAfterSY
            wordYtoI = word[:-1]+'i' if word[-1]=='y' else word

            generatedWords = []
            """
            B -able, -ability, last syllable of stem stressed, -ate words &gt; 2 syllables
            b -ible, very basic rules, only dropped e
            D -ed, regular verb past tenses, last syllable of stem stressed
            d -ed, -ing, regular verb past tenses and adverbial form, last syllable NOT stressed
            E dis- Prefix for negation
            e out- Prefix
            h -edly, adverbial, simplified rules
            I in- im- il- ir- Prefix, opposite of.
            i -edness, degree, simplified rules
            j -fully, suffix
            K pre-, prefix
            k -ingly, adverbial form, simplified rules
            L -ment, -ments, -ment's, suffix, both generated
            l -ably, simplified rules
            N -ion, noun from verb, stress on last syllable of stem
            n -ion, -ions, noun from verb, stress NOT on last syllable of stem
            q -isation, -isations, -ization, -izations, all generated
            S -s, noun plurals, verb conjugation
            s -iser, -isers, -izer, -izers, -iser's, -izer's, all generated
            T -er, -est, adjectival comparatives, both generated
            t -isable, -isability, -izable, -izability, all generated
            u -iveness, ending for verbs
            V -ive, ending for verbs (simplified rules)
            v -ively, ending for verbs
            W -ic, adjectival ending, simplified rules
            w -ical, adjectival ending, simplified rules
            X -ions, noun plural, stress on last syllable of stem, simplified rules
            x -ional, -ionally, simplified rules, both endings formed
            Y -ly, adverb endings for adjectives
            y -ry, adjectival and noun forms, simplified rules.
            0 -al, noun from verb, simplified rules
            1 -ically, adverbial double suffix, simplified rules
            2 -iness, y+ness ending, simplified rules
            3 -ist, -ists, -ists's, professions
            5 -woman, -women, -woman's suffixes, all generated
            7 -able, last syllable NOT stressed, -ate words <= 2 syllables
            """
            for code in codes:
                #print( "  code", code, "for", repr(word) )
                if code == 'A': generatedWords.append( 're' + word )
                elif code == 'a': generatedWords.append( 'mis' + word )
                elif code == 'B': generatedWords.append( word+'able' ); generatedWords.append( word+'ability' )
                elif code == 'b': generatedWords.append( wordDeleteE + 'ible' ); generatedWords.append( wordDeleteE + 'ibility' )
                elif code == 'C': generatedWords.append( 'de' + word )
                elif code == 'c': generatedWords.append( 'over' + word )
                elif code == 'D': generatedWords.append( wordDeleteE + 'ed' ) # last syllable of stem stressed
                elif code == 'd': generatedWords.append( word+'ed' ); generatedWords.append( word+'ing' )
                elif code == 'E': generatedWords.append( 'dis' + word )
                elif code == 'e': generatedWords.append( 'out' + word )
                elif code == 'F': # e.g., ment -> prefix
                    if word[0] in ( 'm','b','p',): generatedWords.append( 'com' + word )
                    #elif word[0] == 'l': generatedWords.append( 'il' + word )
                    #elif word[0] == 'r': generatedWords.append( 'ir' + word )
                    else: generatedWords.append( 'con' + word )
                elif code == 'f': generatedWords.append( 'under' + word )
                elif code == 'G': # e.g., XXX -> ending for verbs, stress on last syllable of stem
                    generatedWords.append( wordDeleteE + 'ing' )
                elif code == 'g': # e.g., palate -> last syllable NOT stressed
                    generatedWords.append( wordDeleteE + 'ability' )
                elif code == 'H': # e.g., eighty-four -> number specific suffixes, both generated
                    generatedWords.append( word + 'th' ); generatedWords.append( word + 'fold' )
                elif code == 'h': # e.g., abash -> adverbial, simplified rules
                    generatedWords.append( wordDeleteE + 'edly' )
                elif code == 'I':
                    if word[0] in ( 'm','b','p',): generatedWords.append( 'im' + word )
                    elif word[0] == 'l': generatedWords.append( 'il' + word )
                    elif word[0] == 'r': generatedWords.append( 'ir' + word )
                    else: generatedWords.append( 'in' + word )
                elif code == 'i': generatedWords.append( wordDeleteEY + 'edness' )
                elif code == 'J': # e.g., band -> plural noun version of verb ing ending, simplified rules
                    generatedWords.append( word + 'ings' )
                elif code == 'j': # e.g., bliss, wonder -> suffix
                    generatedWords.append( word + 'fully' )
                elif code == 'K': generatedWords.append( 'pre' + word )
                elif code == 'k': generatedWords.append( wordDeleteE + 'ingly' )
                elif code == 'L': generatedWords.append( word+'ment' ); generatedWords.append( word+'ments' ); generatedWords.append( word+"ment's" )
                elif code == 'l': # e.g., avoid
                    generatedWords.append( word + 'ably' )
                elif code == 'M': # e.g., abalone -> possessive form
                    generatedWords.append( word + "'s" ) # What about other apostrophe types
                elif code == 'm': # e.g., artillery -> suffixes, all generated
                    generatedWords.append( word+'man' ); generatedWords.append( word+"man's" ); generatedWords.append( word+'men' ); generatedWords.append( word+"men's" )
                elif code == 'N': # e.g., assume
                    generatedWords.append( wordDeleteE + 'ion' )
                elif code == 'n': generatedWords.append( wordDeleteE+'ion' ); generatedWords.append( wordDeleteE+'ions' )
                elif code == 'O': # e.g., fiction -> prefix
                    generatedWords.append( 'non' + word )
                elif code == 'o': # e.g., apocrypha -> adverb from verb, simplified rules
                    generatedWords.append( wordDeleteA + 'ally' )
                elif code == 'P': # e.g., absolute -> adjective degree of comparison
                    generatedWords.append( wordYtoI+'ness' ); generatedWords.append( wordYtoI+"ness's" )
                elif code == 'p': # e.g., body -> comparative suffix
                    generatedWords.append( word+'less' )
                elif code == 'Q': # e.g., pre -> all generated
                    generatedWords.append( wordDeleteE+'ise' ); generatedWords.append( wordDeleteE+'ised' ); generatedWords.append( wordDeleteE+'ises' ); generatedWords.append( wordDeleteE+'ising' )
                    generatedWords.append( wordDeleteE+'ize' ); generatedWords.append( wordDeleteE+'ized' ); generatedWords.append( wordDeleteE+'izes' ); generatedWords.append( wordDeleteE+'izing' )
                elif code == 'R': # e.g., abjure -> doer, last syllable stressed, both forms generated
                    generatedWords.append( wordDeleteE+'er' ); generatedWords.append( wordDeleteE+'ers' ); generatedWords.append( wordDeleteE+"er's" )
                elif code == 'r': # e.g., backslid -> doer, last syllable NOT stressed, both forms generated
                    generatedWords.append( word+'er' ); generatedWords.append( word+'ers' ); generatedWords.append( word+"er's" )
                elif code == 'S': generatedWords.append( wordAddEAfterSY + 's' )
                elif code == 'T': generatedWords.append( wordDeleteEY+'er' ); generatedWords.append( wordDeleteEY+'est' )
                elif code == 'U': generatedWords.append( 'un' + word )
                elif code == 'u': generatedWords.append( wordDeleteEY + 'iveness' )
                elif code == 'V': generatedWords.append( wordDeleteEY + 'ive' )
                elif code == 'v': generatedWords.append( wordDeleteEY + 'ively' )
                elif code == 'W': generatedWords.append( wordDeleteEY + 'ic' )
                elif code == 'w': generatedWords.append( wordDeleteEY + 'ical' )
                elif code == 'X': # e.g., assume
                    generatedWords.append( wordDeleteEY + 'ions' )
                elif code == 'x': generatedWords.append( wordDeleteEY + 'ional' ); generatedWords.append( word + 'ionally' )
                elif code == 'Y': generatedWords.append( wordYtoI + 'ly' )
                elif code == 'y': generatedWords.append( word + 'ry' )
                elif code == 'Z': # e.g., academe -> diminutive and adjectival form, simplified rules
                    generatedWords.append( wordDeleteE + 'y' )
                elif code == 'z': # e.g., cage -> adverbial ending where adjective adds y
                    generatedWords.append( wordDeleteEY + 'ily' )
                elif code == '1': print( ' 1 on', repr(word), 'ignored' )
                elif code == '2': # e.g., bone -> y+ness ending, simplified rules
                    generatedWords.append( wordDeleteEY + 'iness' )
                elif code == '3': generatedWords.append( wordDeleteEY+'ist' ); generatedWords.append( wordDeleteE+'ists' ); generatedWords.append( wordDeleteE+"ist's" )
                elif code == '5': # e.g., chair
                    generatedWords.append( word+'woman' ); generatedWords.append( word+"woman's" ); generatedWords.append( word+'women' ); generatedWords.append( word+"women's" )
                elif code == '4': generatedWords.append( 'trans' + word )
                elif code == '6': # e.g., bliss, wonder -> suffix
                    generatedWords.append( word + 'ful' )
                elif code == '7': generatedWords.append( word + 'able' )
                elif BibleOrgSysGlobals.debugFlag:
                    print( lineCount, "code", code, "for", repr(word), repr(codes) )
                    halt
            print( "  generated", generatedWords, 'from', repr(word), repr(codes) )
            autocompleteWords.extend( generatedWords )

            #lastLine = line
            #if lineCount > 60: break
    #print( 'acW', len(autocompleteWords), autocompleteWords )

    if self.autocompleteMinLength < 4:
        print( "NOTE: Lengthened autocompleteMinLength from {} to {}".format( self.autocompleteMinLength, 4 ) )
        self.autocompleteMinLength = 4 # Show the window after this many characters have been typed
    setAutocompleteWords( self, autocompleteWords )
    self.autocompleteType = 'Dictionary'
# end of AutocompleteFunctions.loadHunspellAutocompleteWords



def loadILEXAutocompleteWords( self, dictionaryFilepath, lgCodes=None ):
    """
    Load all the existing words in an ILEX dictionary
        to fill the autocomplete mechanism

    self here is a text edit window or derivation.

    NOTE: This list maybe should be updated as the user enters new words
        or else have an additional user dictionary.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( exp("AutocompleteFunctions.loadILEXAutocompleteWords( {}, {} )").format( dictionaryFilepath, lgCodes ) )

    autocompleteWords = []
    lineCount = 0
    with open( dictionaryFilepath, 'rt' ) as dictionaryFile:
        for line in dictionaryFile:
            lineCount += 1
            if lineCount==1 and line[0]==chr(65279): #U+FEFF or \ufeff
                logging.info( "loadILEXAutocompleteWords: Detected Unicode Byte Order Marker (BOM) in {}".format( dictionaryFilepath ) )
                line = line[1:] # Remove the Unicode Byte Order Marker (BOM)
            if line[-1]=='\n': line=line[:-1] # Remove trailing newline character
            if not line: continue # Just discard blank lines
            #print( "line", lineCount, repr(line) )

            # wd, lg, ps, and sc are the four compulsory fields in each record
            if line.startswith( '\wd ' ):
                word = line[4:]
                if '*' in word and word[-2] == '*' and word[-1].isdigit(): # It has a subscript
                    word = word[:-2]
            elif line.startswith( '\lg ' ):
                lgCode = line[4:]
                assert len(lgCode) == 3
            elif line.startswith( '\ps ' ):
                POS = line[4:]

                if lgCodes is None or lgCode in lgCodes:
                    if POS != 'x': # abbreviations like AFAIK
                        if word not in autocompleteWords:
                            autocompleteWords.append( word )

            #lastLine = line
            #if lineCount > 600: break
    #print( 'acW', len(autocompleteWords), autocompleteWords )

    if self.autocompleteMinLength < 4:
        print( "NOTE: Lengthened autocompleteMinLength from {} to {}".format( self.autocompleteMinLength, 4 ) )
        self.autocompleteMinLength = 4 # Show the window after this many characters have been typed
    setAutocompleteWords( self, autocompleteWords )
    self.autocompleteType = 'Dictionary'
# end of AutocompleteFunctions.loadILEXAutocompleteWords



def demo():
    """
    Demo program to handle command line parameters and then run what they want.
    """
    import tkinter as tk

    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )
    #if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Available CPU count =", multiprocessing.cpu_count() )

    if BibleOrgSysGlobals.debugFlag: print( exp("Running demo...") )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( ProgNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    #uEW = AutocompleteFunctions( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of AutocompleteFunctions.demo


if __name__ == '__main__':
    from BibleOrgSysGlobals import setup, addStandardOptionsAndProcess, closedown
    import multiprocessing

    # Configure basic set-up
    parser = setup( ProgName, ProgVersion )
    addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables


    #if 1 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        ##from tkinter import TclVersion, TkVersion
        #from tkinter import tix
        #print( "TclVersion is", tk.TclVersion )
        #print( "TkVersion is", tk.TkVersion )
        #print( "tix TclVersion is", tix.TclVersion )
        #print( "tix TkVersion is", tix.TkVersion )

    demo()

    closedown( ProgName, ProgVersion )
# end of AutocompleteFunctions.py