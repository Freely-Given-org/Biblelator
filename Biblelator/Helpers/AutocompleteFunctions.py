#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AutocompleteFunctions.py
#
# Functions to support the autocomplete function in text editors
#
# Copyright (C) 2016-2018 Robert Hunt
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
Autocomplete is the ability to pop-up a little window of suggested word completions
    as the user is typing. The user can then accept a suggestion with ENTER, or
    close the window with ESC, or just to continue typing.

This module contains most of the helper functions for loading the autocomplete
    words (which may be from a Bible or from a dictionary, etc.)
"""

from gettext import gettext as _

LAST_MODIFIED_DATE = '2018-11-25' # by RJH
SHORT_PROGRAM_NAME = "AutocompleteFunctions"
PROGRAM_NAME = "Biblelator Autocomplete Functions"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


import sys
import os
import logging
import multiprocessing
import time
from collections import defaultdict

import tkinter as tk

# Biblelator imports
from Biblelator.Windows.TextBoxes import TRAILING_SPACE_SUBSTITUTE, MULTIPLE_SPACE_SUBSTITUTE

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import vPrint
#from BibleOrgSys.Internals.InternalBibleInternals import BOS_PRINTABLE_MARKERS, BOS_EXTRA_TYPES
from BibleOrgSys.Reference.USFM3Markers import USFM_PRINTABLE_MARKERS



AVOID_BOOKS = ( 'FRT', 'BAK', 'GLS', 'XXA','XXB','XXC','XXD','XXE','XXF','XXG', 'NDX', 'UNK', )
END_CHARS_TO_REMOVE = ',—.–!?”:;' # NOTE: This intentionally doesn't include close parenthesis and similar
HUNSPELL_DICTIONARY_FOLDERS = ( '/usr/share/hunspell/', )



def setAutocompleteWords( editWindowObject, wordList, append=False ):
    """
    Given a word list, set the entries into the autocomplete words
        for an edit window and then do necessary house-keeping.

    Note that the original word order is preserved (if the supplied wordList has an order)
        so that more common/likely words can appear at the top of the list if desired.
    """
    logging.info( "AutocompleteFunctions.setAutocompleteWords( …, {}, {} )".format( len(wordList), append ) )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( "AutocompleteFunctions.setAutocompleteWords( {} )".format( wordList, append ) )
        print( "AutocompleteFunctions.setAutocompleteWords( …, {}, {} )".format( len(wordList), append ) )
        editWindowObject.parentApp.setDebugText( "setAutocompleteWords…" )

    editWindowObject.parentApp.setWaitStatus( _("Setting autocomplete words…") )
    if not append: editWindowObject.autocompleteWords = {}

    for word in wordList:
        #if "'" not in word and '1' not in word:
            #if '(' in word and ')' not in word: # perhaps something like we(excl
                #word = word + ')' # append a matching/final parenthesis
        if len(word) >= editWindowObject.autocompleteMinLength:
            firstLetter, remainder = word[0], word[1:]
            if firstLetter not in editWindowObject.autocompleteWords: editWindowObject.autocompleteWords[firstLetter] = []
            if remainder in editWindowObject.autocompleteWords[firstLetter]:
                if 0 and BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    print( "    setAutocompleteWords discarded {!r} duplicate".format( word ) )
            else: # not already in the list
                editWindowObject.autocompleteWords[firstLetter].append( remainder )
                for char in word:
                    if char not in editWindowObject.autocompleteWordChars:
                        if BibleOrgSysGlobals.debugFlag: assert char not in '\n\r'
                        if char not in ' .':
                            editWindowObject.autocompleteWordChars += char
                            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                                print( "    setAutocompleteWords added {!r} as new wordChar".format( char ) )
        #elif BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( "    setAutocompleteWords discarded {!r} as too short".format( word ) )
        #elif BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #if "'" not in word:
                #print( "    setAutocompleteWords discarded {!r} as unwanted".format( word ) )

    if BibleOrgSysGlobals.debugFlag and debuggingThisModule: # write wordlist
        print( "  setAutocompleteWords: Writing autocomplete words to file…" )
        sortedKeys = sorted( editWindowObject.autocompleteWords.keys() )
        with open( 'autocompleteWordList.txt', 'wt', encoding='utf-8' ) as wordFile:
            wordCount = 0
            for firstLetter in sortedKeys:
                for remainder in sorted( editWindowObject.autocompleteWords[firstLetter] ):
                    wordFile.write( firstLetter+remainder )
                    wordCount += 1
                    if wordCount == 8: wordFile.write( '\n' ); wordCount = 0
                    else: wordFile.write( ' ' )

    if BibleOrgSysGlobals.debugFlag: # print detailed stats
        sortedKeys = sorted( editWindowObject.autocompleteWords.keys() )
        if debuggingThisModule: print( "  autocomplete first letters", len(editWindowObject.autocompleteWords), sortedKeys )
        grandtotal = 0
        wordNumTotals = defaultdict( int )
        for firstLetter in sortedKeys:
            total = len(editWindowObject.autocompleteWords[firstLetter])
            for wordRemainder in editWindowObject.autocompleteWords[firstLetter]:
                wordNumTotals[wordRemainder.count(' ')] += 1
            if debuggingThisModule:
                print( "    {!r} {:,}{}" \
                    .format( firstLetter, total, '' if total>19 else ' '+str(editWindowObject.autocompleteWords[firstLetter]) ) )
            grandtotal += total
        #if BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.verbosityLevel > 1:
        print( "  autocomplete total words loaded = {:,}".format( grandtotal ) )
        if debuggingThisModule:
            for spaceCount in wordNumTotals:
                print( "    {} words: {}".format( spaceCount+1, wordNumTotals[spaceCount] ) )

    editWindowObject.parentApp.setReadyStatus()
# end of AutocompleteFunctions.setAutocompleteWords



internalMarkers = None
DUMMY_VALUE = 999999 # Some number bigger than the number of characters in a line

def countBookWords( BBB, internalBible, filename, isCurrentBook, internalMarkers ):
    """
    Find all the words in the Bible book and their usage counts.

    Note that this function doesn't use the internalBible books
        but rather loads the USFM (text) files directly.

    Note also that the internalMarkersList has to be passed as a paramter,
        because multi-processing on Windows can't access global variables.

    Returns a dictionary containing the results for the book.
    """
    logging.debug( "countBookWords( {}, {}, {} )".format( BBB, internalBible, filename ) )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "countBookWords( {}, {}, {} )".format( BBB, internalBible, filename ) )
    if BBB in AVOID_BOOKS:
        #print( "Didn't load autocomplete words from {} {}".format( internalBible.getAName(), BBB ) )
        return # Sometimes these books contain words from other languages, etc.

    countIncrement = 3 if isCurrentBook else 1 # Each word in current book counts higher so appears higher in the list
    # NOTE: This idea fails as soon as they change books in the edit window
    #       as the word lists are only loaded once at startup. (A reasonable compromise I think.)

    encoding = None
    if encoding is None: encoding = 'utf-8'
    lastLine, lineCount, lineDuples, lastMarker = '', 0, [], None
    wordCounts = defaultdict( int )

    def countWords( textLine ):
        """
        Note: Punctuation etc. is NOT removed.
        """
        #print( "countWords( {!r} )".format( textLine ) )
        if '\\' in textLine: # we have internal markers to remove
            #print( "  INT", marker, textLine )
            for iMarker in internalMarkers:
                #print( "   GOT", repr(iMarker) )
                textLine = textLine.replace( iMarker+' ',' ' ).replace( iMarker+'*',' ' )
                if not '\\' in textLine: break
            #print( "  NOW", marker, textLine )
        words = textLine.replace('—','— ').replace('–','– ').split() # Treat em-dash and en-dash as word break characters

        # Now look for (and count) single and some multiple word sequences
        for wx,word in enumerate( words ):
            if not word: continue
            if 'XXX' in word: continue # This is used in the Matigsalug project to mark errors
            singleWord = word
            while singleWord and singleWord[-1] in END_CHARS_TO_REMOVE:
                singleWord = singleWord[:-1] # Remove certain final punctuation
            if len(singleWord) > 2: wordCounts[singleWord] += countIncrement

            #if word[-1] not in '—.–':
            if wx < len(words)-1: # it's not the last word in the line
                doubleWord = word+' '+words[wx+1]
                #print( 'doubleWord', repr(doubleWord) )
                adjustedDoubleWord = doubleWord[:-1] if doubleWord[-1] in END_CHARS_TO_REMOVE else doubleWord
                if '. ' not in adjustedDoubleWord: # don't go across sentence boundaries
                    wordCounts[adjustedDoubleWord] += countIncrement
                if wx < len(words)-2: # there's still two words after this one
                    tripleWord = doubleWord+' '+words[wx+2]
                    #print( 'tripleWord', repr(tripleWord) )
                    adjustedTripleWord = tripleWord[:-1] if tripleWord[-1] in END_CHARS_TO_REMOVE else tripleWord
                    if '. ' not in adjustedTripleWord: # don't go across sentence boundaries
                        wordCounts[adjustedTripleWord] += countIncrement
                    if wx < len(words)-3: # there's still three words after this one
                        quadWord = tripleWord+' '+words[wx+3]
                        #print( 'quadWord', repr(quadWord) )
                        adjustedQuadWord = quadWord[:-1] if quadWord[-1] in END_CHARS_TO_REMOVE else quadWord
                        if '. ' not in adjustedQuadWord: # don't go across sentence boundaries
                            wordCounts[adjustedQuadWord] += countIncrement
                        if wx < len(words)-4: # there's still four words after this one
                            quinWord = quadWord+' '+words[wx+4]
                            #print( 'quinWord', repr(quinWord) )
                            adjustedQuinWord = quinWord[:-1] if quinWord[-1] in END_CHARS_TO_REMOVE else quinWord
                            if '. ' not in adjustedQuinWord: # don't go across sentence boundaries
                                wordCounts[adjustedQuinWord] += countIncrement
    # end of countWords

    # main code for countBookWords
    USFMFilepath = os.path.join( internalBible.sourceFolder, filename )
    with open( USFMFilepath, 'rt', encoding=internalBible.encoding ) as bookFile:
        try:
            for line in bookFile:
                lineCount += 1
                if lineCount==1 and encoding.lower()=='utf-8' and line[0]==chr(65279): #U+FEFF
                    logging.info( "countBookWords: Detected Unicode Byte Order Marker (BOM) in {}".format( USFMFilepath ) )
                    line = line[1:] # Remove the Unicode Byte Order Marker (BOM)
                if line and line[-1]=='\n': line=line[:-1] # Removing trailing newline character
                if not line: continue # Just discard blank lines
                lastLine = line
                #print ( 'USFM file line is {!r}'.format( line ) )
                #if line[0:2]=='\\_': continue # Just discard Toolbox header lines
                if line[0]=='#': continue # Just discard comment lines

                if line[0]!='\\': # Not a SFM line
                    if lastMarker is None: # We don't have any SFM data lines yet
                        logging.error( "countBookWords: Non-USFM line in {} -- line ignored at #{}".format( USFMFilepath, lineCount) )
                        #print( "SFMFile.py: XXZXResult is", lineDuples, len(line) )
                        #for x in range(0, min(6,len(line))):
                            #print( x, "'" + str(ord(line[x])) + "'" )
                        #raise IOError('Oops: Line break on last line ??? not handled here "' + line + '"')
                    else: # Append this continuation line
                        if lastMarker in USFM_PRINTABLE_MARKERS:
                            #oldmarker, oldtext = lineDuples.pop()
                            #print ("Popped",oldmarker,oldtext)
                            #print ("Adding", line, "to", oldmarker, oldtext)
                            #lineDuples.append( (oldmarker, oldtext+' '+line) )
                            countWords( line )
                        continue

                lineAfterBackslash = line[1:]
                si1 = lineAfterBackslash.find( ' ' )
                si2 = lineAfterBackslash.find( '*' )
                si3 = lineAfterBackslash.find( '\\' )
                if si1==-1: si1 = DUMMY_VALUE
                if si2==-1: si2 = DUMMY_VALUE
                if si3==-1: si3 = DUMMY_VALUE
                si = min( si1, si2, si3 )

                if si != DUMMY_VALUE:
                    if si == si3: # Marker stops before a backslash
                        marker = lineAfterBackslash[:si3]
                        text = lineAfterBackslash[si3:]
                    elif si == si2: # Marker stops at an asterisk
                        marker = lineAfterBackslash[:si2+1]
                        text = lineAfterBackslash[si2+1:]
                    elif si == si1: # Marker stops before a space
                        marker = lineAfterBackslash[:si1]
                        text = lineAfterBackslash[si1+1:] # We drop the space completely
                else: # The line is only the marker
                    marker = lineAfterBackslash
                    text = ''

                #print( " ", repr(marker), repr(text) )
                #if marker not in ignoreSFMs:
                if marker in USFM_PRINTABLE_MARKERS and text:
                    #print( "   1", marker, text )
                    if marker == 'v' and text[0].isdigit():
                        try: text = text.split( None, 1 )[1]
                        except IndexError: text = ''
                    #print( "   2", marker, text )
                    countWords( text )
                    #if not lineDuples: # Just for detection of start of real USFM
                        #lineDuples.append( (marker, text) )
                lastMarker = marker

        except UnicodeError as err:
            print( "Unicode error:", sys.exc_info()[0], err )
            logging.critical( "countBookWords: Invalid line in {} -- line ignored at #{}".format( USFMFilepath, lineCount) )
            if lineCount > 1: print( 'Previous line was: ', lastLine )
            #print( line )
            #raise

    return wordCounts
# end of AutocompleteFunctions.countBookWords


def countBookWordsHelper( parameters ):
    """
    Parameter parameters is a 4-tuple containing the BBB, folder, filename, currentBook flag, and internalMarkersList

    The internalMarkers have to be passed, because multi-processing on Windows can't access global variables.
    """
    return countBookWords( *parameters )
# end of AutocompleteFunctions.countBookWordsHelper


def loadBibleBookAutocompleteWords( editWindowObject ):
    """
    Load all the existing words in a USFM or Paratext Bible book
        to fill the autocomplete mechanism

    editWindowObject here is a USFM or ESFM edit window.

    NOTE: This list should theoretically be updated as the user enters new words!
    """
    logging.info( "loadBibleBookAutocompleteWords()" )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "loadBibleBookAutocompleteWords()" )
        editWindowObject.parentApp.setDebugText( "loadBibleBookAutocompleteWords…" )

    editWindowObject.parentApp.setWaitStatus( _("Loading {} Bible book words…").format( editWindowObject.projectName ) )
    currentBBB = editWindowObject.currentVerseKey.getBBB()
    #print( "  got BBB", repr(BBB) )
    if currentBBB == 'UNK': return # UNKnown book -- no use here

    if not editWindowObject.internalBible.preloadDone: editWindowObject.internalBible.preload()
    foundFilename = None
    for BBB2,filename in editWindowObject.internalBible.maximumPossibleFilenameTuples:
        if BBB2 == currentBBB: foundFilename = filename; break

    wordCountResults = countBookWords( currentBBB, editWindowObject.internalBible, foundFilename, False )
    #print( 'wordCountResults', len(wordCountResults) )

    # Would be nice to load current book first, but we don't know it yet
    autocompleteWords = []
    #if BibleOrgSysGlobals.debugFlag:
        #autocompleteWords = [ 'Lord God', 'Lord your(pl) God', '(is)', '(are)', '(were)', '(one who)', ]
    try:
        # Sort the word-list for the book to put the most common words first
        #print( 'wordCountResults', currentBBB, discoveryResults )
        #print( currentBBB, 'mTWC', discoveryResults['mainTextWordCounts'] )
        #qqq = sorted( discoveryResults['mainTextWordCounts'].items(), key=lambda c: -c[1] )
        #print( 'qqq', qqq )
        for word,count in sorted( wordCountResults.items(),
                                key=lambda duple: -duple[1] ):
            if len(word) >= editWindowObject.autocompleteMinLength \
            and word not in autocompleteWords: # just in case we had some (common) words in there already
                if ' ' not in word or count > 4:
                    autocompleteWords.append( word )
                #else: print( 'loadBibleBookAutocompleteWords discarding', repr(word) )
    except KeyError:
        print( "Why did {} have no words???".format( currentBBB ) )
        #pass # Nothing for this book
    #print( 'autocompleteWords', len(autocompleteWords) )
    setAutocompleteWords( editWindowObject, autocompleteWords )
    editWindowObject.addAllNewWords = True
# end of AutocompleteFunctions.loadBibleBookAutocompleteWords



def loadBibleAutocompleteWords( editWindowObject ):
    """
    Load all the existing words in a USFM or Paratext Bible Project
        to fill the autocomplete mechanism.

    This is rather slow because of course, the entire Bible has to be read and processed first.

    editWindowObject here is a USFM or ESFM edit window.

    NOTE: This list should theoretically be updated as the user enters new words!
    """
    startTime = time.time()
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "AutocompleteFunctions.loadBibleAutocompleteWords()" )
        editWindowObject.parentApp.setDebugText( "loadBibleAutocompleteWords…" )

    global internalMarkers
    if internalMarkers is None: # Get our list of markers -- note that the more common note markers are first
        internalMarkers = BibleOrgSysGlobals.loadedUSFMMarkers.getNoteMarkersList() \
            + BibleOrgSysGlobals.loadedUSFMMarkers.getCharacterMarkersList( includeBackslash=False, includeEndMarkers=False, includeNestedMarkers=True, expandNumberableMarkers=True )
        internalMarkers = ['\\'+marker for marker in internalMarkers]

    editWindowObject.parentApp.setWaitStatus( _("Loading {} Bible words…").format( editWindowObject.projectName ) )
    currentBBB = editWindowObject.currentVerseKey.getBBB()
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( "  got current BBB", repr(currentBBB) )

    if not editWindowObject.internalBible.preloadDone: editWindowObject.internalBible.preload()
    bookWordCounts = {}
    if editWindowObject.internalBible.maximumPossibleFilenameTuples:
        if BibleOrgSysGlobals.maxProcesses > 1: # Load all the books as quickly as possible
            parameters = [(BBB,editWindowObject.internalBible,filename,BBB==currentBBB,internalMarkers) for BBB,filename in editWindowObject.internalBible.maximumPossibleFilenameTuples] # Can only pass a single parameter to map
            vPrint( 'Normal', debuggingThisModule, "Autocomplete: loading up to {} USFM books using {} processes…".format( len(editWindowObject.internalBible.maximumPossibleFilenameTuples), BibleOrgSysGlobals.maxProcesses ) )
            vPrint( 'Normal', debuggingThisModule, "  NOTE: Outputs (including error & warning messages) from loading words from BibleOrgSys.Bible books may be interspersed." )
            BibleOrgSysGlobals.alreadyMultiprocessing = True
            with multiprocessing.Pool( processes=BibleOrgSysGlobals.maxProcesses ) as pool: # start worker processes
                results = pool.map( countBookWordsHelper, parameters ) # have the pool do our loads
                assert len(results) == len(editWindowObject.internalBible.maximumPossibleFilenameTuples)
                for (BBB,filename),counts in zip( editWindowObject.internalBible.maximumPossibleFilenameTuples, results ):
                    #print( "XX", BBB, filename, len(counts) if counts else counts )
                    bookWordCounts[BBB] = counts
                BibleOrgSysGlobals.alreadyMultiprocessing = False
        else: # Just single threaded
            # Load the books one by one -- assuming that they have regular Paratext style filenames
            for BBB,filename in editWindowObject.internalBible.maximumPossibleFilenameTuples:
                #if BibleOrgSysGlobals.verbosityLevel>1 or BibleOrgSysGlobals.debugFlag:
                    #print( _("  USFMBible: Loading {} from {} from {}…").format( BBB, editWindowObject.internalBible.getAName(), editWindowObject.internalBible.sourceFolder ) )
                bookWordCounts[BBB] = countBookWords( BBB, editWindowObject.internalBible, filename, BBB==currentBBB ) # also saves it
    else:
        logging.critical( "Autocomplete: " + _("No books to load in folder '{}'!").format( editWindowObject.internalBible.sourceFolder ) )

    # Now combine the books
    autocompleteCounts = {}
    for BBB,counts in bookWordCounts.items(): # combine word counts for all books
        #print( "here", BBB, len(counts) )
        if counts:
            for word, count in counts.items():
                #print( "  ", word, count )
                if len(word) >= editWindowObject.autocompleteMinLength:
                    if word in autocompleteCounts: autocompleteCounts[word] += count
                    else: autocompleteCounts[word] = count
    #print( "there", len(autocompleteCounts) )

    # Now make our list sorted with most common words first
    autocompleteWords = []
    #if BibleOrgSysGlobals.debugFlag: # add some multi-word entries just for testing
        #autocompleteWords = [ 'Lord God', 'Lord your(pl) God', '(is)', '(are)', '(were)', '(one who)', ]
    for word,count in sorted( autocompleteCounts.items(), key=lambda duple: -duple[1] ):
        if ' ' not in word or count > 9:
            autocompleteWords.append( word )
        #else:
            #print( 'loadBibleAutocompleteWords discarding', repr(word) )
            #if ' ' not in word: halt
    #if BibleOrgSysGlobals.debugFlag and debuggingThisModule: print( 'acW', autocompleteWords )

    #print( 'autocompleteWords', len(autocompleteWords) )
    setAutocompleteWords( editWindowObject, autocompleteWords )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "loadBibleAutocompleteWords took", time.time()-startTime )
    editWindowObject.addAllNewWords = True
# end of AutocompleteFunctions.loadBibleAutocompleteWords



def loadHunspellAutocompleteWords( editWindowObject, dictionaryFilepath, encoding='utf-8' ):
    """
    Load all the existing words in a Hunspell-type dictionary
        to fill the autocomplete mechanism

    editWindowObject here is a text edit window or derivation.

    NOTE: This list maybe should be updated as the user enters new words
        or else have an additional user dictionary.
    """
    logging.info( "loadHunspellAutocompleteWords( {}, {} )".format( dictionaryFilepath, encoding ) )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "loadHunspellAutocompleteWords( {}, {} )".format( dictionaryFilepath, encoding ) )
        editWindowObject.parentApp.setDebugText( "loadHunspellAutocompleteWords…" )

    editWindowObject.parentApp.setWaitStatus( _("Loading dictionary…") )
    internalCount = None
    autocompleteWords = []
    lineCount = 0
    with open( dictionaryFilepath, 'rt', encoding=encoding ) as dictionaryFile:
        for line in dictionaryFile:
            lineCount += 1
            if lineCount==1 and encoding.lower()=='utf-8' and line[0]==chr(65279): #U+FEFF or \ufeff
                logging.info( "loadHunspellAutocompleteWords: Detected Unicode Byte Order Marker (BOM) in {}".format( dictionaryFilepath ) )
                line = line[1:] # Remove the Unicode Byte Order Marker (BOM)
            if line and line[-1]=='\n': line=line[:-1] # Remove trailing newline character
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

    if editWindowObject.autocompleteMinLength < 4:
        print( "NOTE: Lengthened autocompleteMinLength from {} to {}".format( editWindowObject.autocompleteMinLength, 4 ) )
        editWindowObject.autocompleteMinLength = 4 # Show the window after this many characters have been typed
    setAutocompleteWords( editWindowObject, autocompleteWords )
    editWindowObject.addAllNewWords = False
# end of AutocompleteFunctions.loadHunspellAutocompleteWords



def loadILEXAutocompleteWords( editWindowObject, dictionaryFilepath, lgCodes=None ):
    """
    Load all the existing words in an ILEX dictionary
        to fill the autocomplete mechanism

    editWindowObject here is a text edit window or derivation.

    NOTE: This list maybe should be updated as the user enters new words
        or else have an additional user dictionary.
    """
    logging.info( "loadILEXAutocompleteWords( {}, {} )".format( dictionaryFilepath, lgCodes ) )
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "loadILEXAutocompleteWords( {}, {} )".format( dictionaryFilepath, lgCodes ) )
        editWindowObject.parentApp.setDebugText( "loadILEXAutocompleteWords…" )

    editWindowObject.parentApp.setWaitStatus( _("Loading dictionary…") )
    autocompleteWords = []
    lineCount = 0
    with open( dictionaryFilepath, 'rt', encoding='utf-8' ) as dictionaryFile:
        for line in dictionaryFile:
            lineCount += 1
            if lineCount==1:
                if line[0]==chr(65279): #U+FEFF
                    logging.info( "loadILEXAutocompleteWords1: Detected Unicode Byte Order Marker (BOM) in {}".format( dictionaryFilepath ) )
                    line = line[1:] # Remove the UTF-16 Unicode Byte Order Marker (BOM)
                elif line[:3] == 'ï»¿': # 0xEF,0xBB,0xBF
                    logging.info( "loadILEXAutocompleteWords2: Detected Unicode Byte Order Marker (BOM) in {}".format( dictionaryFilepath ) )
                    line = line[3:] # Remove the UTF-8 Unicode Byte Order Marker (BOM)
            if line and line[-1]=='\n': line=line[:-1] # Remove trailing newline character
            if not line: continue # Just discard blank lines
            #print( "line", lineCount, repr(line) )

            # wd, lg, ps, and sc are the four compulsory fields in each record
            if line.startswith( '\\wd ' ):
                word = line[4:]
                if '*' in word and word[-2] == '*' and word[-1].isdigit(): # It has a subscript
                    word = word[:-2]
            elif line.startswith( '\\lg ' ):
                lgCode = line[4:]
                assert len(lgCode) == 3
            elif line.startswith( '\\ps ' ):
                POS = line[4:]

                if lgCodes is None or lgCode in lgCodes:
                    if POS != 'x': # abbreviations like AFAIK
                        if word not in autocompleteWords:
                            autocompleteWords.append( word )

            #lastLine = line
            #if lineCount > 600: break
    #print( 'acW', len(autocompleteWords), autocompleteWords )

    if editWindowObject.autocompleteMinLength < 4:
        print( "NOTE: Lengthened autocompleteMinLength from {} to {}".format( editWindowObject.autocompleteMinLength, 4 ) )
        editWindowObject.autocompleteMinLength = 4 # Show the window after this many characters have been typed
    setAutocompleteWords( editWindowObject, autocompleteWords )
    editWindowObject.addAllNewWords = False
# end of AutocompleteFunctions.loadILEXAutocompleteWords



############################################################################
#
# The following functions are part of the autocomplete code that's
#   executed while typing.
#
# self in these functions is assumed to be an edit window
#   containing self.textBox
#
############################################################################


def getCharactersBeforeCursor( self, charCount=1 ):
    """
    Needed for auto-correct functions.
    """
    #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( "AutocompleteFunctions.getCharactersBeforeCursor( {} )".format( charCount ) )

    previousText = self.textBox.get( tk.INSERT+'-{}c'.format( charCount ), tk.INSERT )
    #print( 'getCharactersBeforeCursor: returning previousText', repr(previousText) )
    return previousText
# end of AutocompleteFunctions.getCharactersBeforeCursor


def getWordCharactersBeforeCursor( self, maxCount=4 ):
    """
    Works backwards from the cursor finding word characters
        (which we might then want to autocomplete).

    Needed for auto-complete functions.
    """
    #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( "AutocompleteFunctions.getWordCharactersBeforeCursor( {} )".format( maxCount ) )

    previousText = self.textBox.get( tk.INSERT+'-{}c'.format( maxCount ), tk.INSERT )
    #print( "previousText", repr(previousText) )
    wordText = ''
    for previousChar in reversed( previousText ):
        if previousChar in self.autocompleteWordChars:
            wordText = previousChar + wordText
        else: break
    #print( 'getWordCharactersBeforeCursor: returning wordText', repr(wordText) )
    return wordText
# end of AutocompleteFunctions.getWordCharactersBeforeCursor


def getCharactersAndWordBeforeCursor( self, maxCount=4 ):
    """
    Works backwards from the cursor finding word characters
        INCLUDING THE PREVIOUS WORD
        (which we might then want to autocomplete).

    Needed for auto-complete functions.
    """
    #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( "AutocompleteFunctions.getCharactersAndWordBeforeCursor( {} )".format( maxCount ) )

    previousText = self.textBox.get( tk.INSERT+'-{}c'.format( maxCount ), tk.INSERT )
    #print( "previousText", repr(previousText) )
    delimiterCount = 0
    wordText = ''
    for previousChar in reversed( previousText ):
        if previousChar in self.autocompleteWordChars:
            wordText = previousChar + wordText
        elif previousChar in BibleOrgSysGlobals.TRAILING_WORD_END_CHARS+MULTIPLE_SPACE_SUBSTITUTE+TRAILING_SPACE_SUBSTITUTE:
            if delimiterCount > 0: break
            #print( "Found delimiter {!r}".format( previousChar ) )
            wordText = previousChar + wordText
            delimiterCount += 1
    #print( 'getCharactersAndWordBeforeCursor: returning wordText', repr(wordText) )
    return wordText
# end of AutocompleteFunctions.getCharactersAndWordBeforeCursor


def getWordBeforeSpace( self, maxCount=20 ):
    """
    Works backwards from before the word ending character (e.g., a space) before the cursor
        trying to find the word that was last entered.

    Needed for auto-complete functions.
    """
    #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( "AutocompleteFunctions.getWordBeforeSpace( {} )".format( maxCount ) )

    previousText = self.textBox.get( tk.INSERT+'-{}c'.format( maxCount ), tk.INSERT )
    #print( "previousText1", repr(previousText) )
    assert previousText and previousText[-1] in BibleOrgSysGlobals.TRAILING_WORD_END_CHARS+MULTIPLE_SPACE_SUBSTITUTE+TRAILING_SPACE_SUBSTITUTE
    previousText = previousText[:-1] # Drop the character that ended the word
    #print( "previousText2", repr(previousText) )
    wordText = ''
    if 1 or previousText and previousText[-1].isalpha():
        for previousChar in reversed( previousText ):
            if previousChar in self.autocompleteWordChars:
                wordText = previousChar + wordText
            else: break
    #print( 'getWordBeforeSpace: returning word Text', repr(wordText) )
    return wordText
# end of AutocompleteFunctions.getWordBeforeSpace


def acceptAutocompleteSelection( self, includeTrailingSpace=False ):
    """
    Used by autocomplete routines in onTextChange.

    Gets the chosen word and inserts the end of it into the text.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #print( "AutocompleteFunctions.acceptAutocompleteSelection( {} )".format( includeTrailingSpace ) )
        assert self.autocompleteBox is not None

    currentWord = self.autocompleteBox.get( tk.ACTIVE )
    #print( '  autocompleteBox currentWord', currentWord )
    self.removeAutocompleteBox()

    if self.autocompleteOverlap:
        #print( "Have {!r} with overlap {!r}".format( currentWord, self.autocompleteOverlap ) )
        assert currentWord.startswith( self.autocompleteOverlap )
        #currentWord = currentWord[len(self.autocompleteOverlap):]

    # Autocomplete by inserting the rest of the selected word plus a space
    # NOTE: The user has to backspace over the space if they don't want it (e.g., to put a period)
    # NOTE: The box reappears with the current code if we don't append the space -- would need to add a flag
    self.textBox.insert( tk.INSERT, currentWord[len(self.autocompleteOverlap):] \
                                    + (' ' if includeTrailingSpace else '') )

    #print( "acceptAutocompleteSelection for {!r}".format( currentWord ) )
    addNewAutocompleteWord( self, currentWord )

    ## Put this word at the beginning of the list so it comes up on top next time
    #firstLetter, remainder = currentWord[0], currentWord[1:]
    #self.autocompleteWords[firstLetter].remove( remainder )
    #self.autocompleteWords[firstLetter].insert( 0, remainder )
# end of AutocompleteFunctions.acceptAutocompleteSelection


def addNewAutocompleteWord( self, possibleNewWord ):
    """
    Add the new autocomplete word if necessary,
        or at least bring it to the top of the list.

    Used by autocomplete routines in onTextChange.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        print( "AutocompleteFunctions.addNewAutocompleteWord( {!r} )".format( possibleNewWord ) )
        assert isinstance( possibleNewWord, str )
        assert possibleNewWord

    if ' ' in possibleNewWord: # bring each separate word to the top
        remainder = possibleNewWord
        while ' ' in remainder:
            individualWord, remainder = remainder.split( None, 1 )
            #print( "  word={!r}, remainder={!r}".format( individualWord, remainder ) )
            #print( "Recursive1 of {!r}".format( individualWord ) )
            addNewAutocompleteWord( self, individualWord ) # recursive call
            #print( "Recursive2 of {!r}".format( remainder ) )
            addNewAutocompleteWord( self, remainder ) # recursive call

    while possibleNewWord and possibleNewWord[-1] in END_CHARS_TO_REMOVE:
        possibleNewWord = possibleNewWord[:-1] # Remove certain final punctuation

    if len( possibleNewWord ) > self.autocompleteMinLength:
        #print( "Adding new autocomplete word: {!r}".format( possibleNewWord ) )
        # Put this word at the beginning of the list so it comes up on top next time
        firstLetter, remainder = possibleNewWord[0], possibleNewWord[1:]
        try: self.autocompleteWords[firstLetter].remove( remainder )
        except ValueError: pass # remove will fail if this really is a new word
        except KeyError: # There's no list existing for this letter
            self.autocompleteWords[firstLetter] = []
        self.autocompleteWords[firstLetter].insert( 0, remainder )
# end of AutocompleteFunctions.addNewAutocompleteWord




def demo() -> None:
    """
    Demo program to handle command line parameters and then run what they want.
    """
    import tkinter as tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    if BibleOrgSysGlobals.debugFlag: print( "Running demo…" )

    tkRootWindow = tk.Tk()
    tkRootWindow.title( programNameVersion )
    tkRootWindow.textBox = tk.Text( tkRootWindow )

    #uEW = AutocompleteFunctions( tkRootWindow, None )

    # Start the program running
    tkRootWindow.mainloop()
# end of AutocompleteFunctions.demo


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of AutocompleteFunctions.py
