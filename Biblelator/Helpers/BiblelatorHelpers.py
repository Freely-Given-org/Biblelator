#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BiblelatorHelpers.py
#
# Various non-GUI helper functions for Biblelator Bible display/editing
#
# Copyright (C) 2014-2020 Robert Hunt
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
    createEmptyUSFMBookText( BBB, getNumChapters, getNumVerses )
    createEmptyUSFMBooks( folderpath, BBB, availableVersifications, availableVersions, requestDict )
    calculateTotalVersesForBook( BBB, getNumChapters, getNumVerses )
    mapReferenceVerseKey( mainVerseKey )
    mapParallelVerseKey( forGroupCode, mainVerseKey )
    findCurrentSection( currentVerseKey, getNumChapters, getNumVerses, getVerseData )
    logChangedFile( userName, loggingFolder, projectName, savedBBB, bookText )
    parseEnteredBooknameField( bookNameEntry, CEntry, VEntry, BBBfunction )

TODO: Can some of these non-GUI functions be (made more general and) moved to the BOS?
"""
from gettext import gettext as _
import os.path
from datetime import datetime
import re

# BibleOrgSys imports
from BibleOrgSys import BibleOrgSysGlobals
from BibleOrgSys.BibleOrgSysGlobals import fnPrint, vPrint, dPrint
from BibleOrgSys.Bible import Bible
from BibleOrgSys.Reference.VerseReferences import SimpleVerseKey, BBB_RE #, FlexibleVersesKey
from BibleOrgSys.Reference.BibleReferencesLinks import BibleReferencesLinks
from BibleOrgSys.Internals.InternalBibleInternals import InternalBibleEntry

# Biblelator imports
if __name__ == '__main__':
    import sys
    aboveAboveFolderpath = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    if aboveAboveFolderpath not in sys.path:
        sys.path.insert( 0, aboveAboveFolderpath )
from Biblelator import BiblelatorGlobals


LAST_MODIFIED_DATE = '2020-05-10' # by RJH
SHORT_PROGRAM_NAME = "BiblelatorHelpers"
PROGRAM_NAME = "Biblelator helpers"
PROGRAM_VERSION = '0.46'
programNameVersion = f'{PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False



def createEmptyUSFMBookText( BBB, getNumChapters, getNumVerses ):
    """
    Give it the functions for getting the number of chapters and the number of verses
    Returns a string that is the text of a blank USFM book.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "createEmptyUSFMBookText( {} )".format( BBB ) )

    USFMAbbreviation = BibleOrgSysGlobals.loadedBibleBooksCodes.getUSFMAbbreviation( BBB )
    USFMNumber = BibleOrgSysGlobals.loadedBibleBooksCodes.getUSFMNumber( BBB )
    bookText = '\\id {} Empty book created by {}\n'.format( USFMAbbreviation.upper(), BiblelatorGlobals.APP_NAME_VERSION )
    bookText += '\\ide UTF-8\n'
    bookText += '\\h Bookname\n'
    bookText += '\\mt Book Title\n'
    try:
        for C in range( 1, getNumChapters(BBB)+1 ):
            bookText += '\\c {}\n'.format( C )
            for V in range( 1, getNumVerses(BBB,C)+1 ):
                bookText += '\\v {} \n'.format( V )
    except TypeError: # if something is None (i.e., a book without chapters or verses)
        pass
    return bookText
# end of BiblelatorHelpers.createEmptyUSFMBookText



def createEmptyUSFMBooks( folderpath, currentBBB, requestDict ):
    """
    Create empty USFM books or CV shells in the given folderpath
        as requested by the dictionary parameters:
            Books: 'OT'
            Fill: 'Versification'
            Versification: 'KJV'
            Version: 'KJV1611'
    """
    from BibleOrgSys.Reference.BibleVersificationSystems import BibleVersificationSystem
    from BibleOrgSys.Internals.InternalBible import OT39_BOOKLIST, NT27_BOOKLIST
    from BibleOrgSys.Internals.InternalBibleInternals import BOS_ALL_ADDED_MARKERS
    from BibleOrgSys.Formats.USFMBible import USFMBible

    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "createEmptyUSFMBooks( {}, {}, {} )".format( folderpath, currentBBB, requestDict ) )


    versificationObject = BibleVersificationSystem( requestDict['Versification'] ) \
                            if requestDict['Fill']=='Versification' else None
    vPrint( 'Quiet', debuggingThisModule, 'versificationObject', versificationObject )
    if versificationObject is not None:
        getNumChapters, getNumVerses = versificationObject.getNumChapters, versificationObject.getNumVerses

    if requestDict['Fill'] == 'Version':
        #ALL_CHAR_MARKERS = BibleOrgSysGlobals.loadedUSFMMarkers.getCharacterMarkersList( expandNumberableMarkers=True )
        uB = USFMBible( requestDict['Version'] ) # Get the Bible object
        vPrint( 'Quiet', debuggingThisModule, "Fill Bible1", uB )
        uB.preload()
        vPrint( 'Quiet', debuggingThisModule, "Fill Bible2", uB )
        #uB.loadBooks()
        #dPrint( 'Quiet', debuggingThisModule, "Fill Bible3", uB )

    if requestDict['Books'] == 'None': booklist = []
    elif requestDict['Books'] == 'Current': booklist = [ currentBBB ]
    elif requestDict['Books'] == 'All': booklist = OT39_BOOKLIST + NT27_BOOKLIST
    elif requestDict['Books'] == 'OT': booklist = OT39_BOOKLIST
    elif requestDict['Books'] == 'NT': booklist = NT27_BOOKLIST
    else: halt # programming error

    count = 0
    skippedBooklist = []
    for BBB in booklist:
        if requestDict['Fill'] == 'Versification' \
        and versificationObject is not None \
        and BBB not in versificationObject:
            skippedBooklist.append( BBB )
            continue
        #if requestDict['Fill'] == 'Version' \
        #and uB is not None \
        #and BBB not in uB:
            #skippedBooklist.append( BBB )
            #continue

        USFMAbbreviation = BibleOrgSysGlobals.loadedBibleBooksCodes.getUSFMAbbreviation( BBB )
        USFMNumber = BibleOrgSysGlobals.loadedBibleBooksCodes.getUSFMNumber( BBB )

        if requestDict['Fill'] == 'None': bookText = ''
        elif requestDict['Fill'] == 'Basic':
            bookText = '\\id {} Empty book created by {}\n'.format( USFMAbbreviation.upper(), BiblelatorGlobals.APP_NAME_VERSION )
            bookText += '\\ide UTF-8\n'
            bookText += '\\h Bookname\n'
            bookText += '\\mt Book Title\n'
            bookText += '\\c 1\n'
        elif requestDict['Fill'] == 'Versification':
            bookText = createEmptyUSFMBookText( BBB, getNumChapters, getNumVerses )
        elif requestDict['Fill'] == 'Version':
            try: uB.loadBook( BBB )
            except FileNotFoundError:
                skippedBooklist.append( BBB )
                continue
            uBB = uB[BBB] # Get the Bible book object
            bookText = ''
            for verseDataEntry in uBB._processedLines:
                pseudoMarker, cleanText = verseDataEntry.getMarker(), verseDataEntry.getCleanText()
                #dPrint( 'Quiet', debuggingThisModule, BBB, pseudoMarker, repr(cleanText) )
                if '¬' in pseudoMarker or pseudoMarker in BOS_ALL_ADDED_MARKERS or pseudoMarker in ('c#','vp#',):
                    continue # Just ignore added markers -- not needed here
                #if pseudoMarker in ('v','f','fr','x','xo',): # These fields should always end with a space but the processing will have removed them
                    #pseudoMarker += ' ' # Append a space since it didn't have one
                #if pseudoMarker in ALL_CHAR_MARKERS: # Character markers to be closed
                    #dPrint( 'Quiet', debuggingThisModule, "CHAR MARKER" )
                    #pass
                    ##if (USFM[-2]=='\\' or USFM[-3]=='\\') and USFM[-1]!=' ':
                    #if bookText[-1] != ' ':
                        #bookText += ' ' # Separate markers by a space e.g., \p\bk Revelation
                        #if BibleOrgSysGlobals.debugFlag: vPrint( 'Quiet', debuggingThisModule, "toUSFM: Added space to {!r} before {!r}".format( bookText[-2], pseudoMarker ) )
                    #adjValue += '\\{}*'.format( pseudoMarker ) # Do a close marker
                #elif pseudoMarker in ('f','x',): inField = pseudoMarker # Remember these so we can close them later
                #elif pseudoMarker in ('fr','fq','ft','xo',): USFM += ' ' # These go on the same line just separated by spaces and don't get closed
                if bookText: bookText += '\n' # paragraph markers go on a new line
                if not cleanText: bookText += '\\{}'.format( pseudoMarker )
                elif pseudoMarker == 'c': bookText += '\\c {}'.format( cleanText )
                elif pseudoMarker == 'v': bookText += '\\v {} '.format( cleanText )
                else: bookText += '\\{} '.format( pseudoMarker )
                #dPrint( 'Quiet', debuggingThisModule, pseudoMarker, USFM[-200:] )
        else: halt # programming error

        # Write the actual file
        filename = '{}-{}.USFM'.format( USFMNumber, USFMAbbreviation )
        with open( os.path.join( folderpath, filename ), mode='wt', encoding='utf-8' ) as theFile:
            theFile.write( bookText )
        count += 1
    vPrint( 'Quiet', debuggingThisModule, len(skippedBooklist), "books skipped:", skippedBooklist ) # Should warn the user here
    vPrint( 'Quiet', debuggingThisModule, count, "books created" )
# end of BiblelatorHelpers.createEmptyUSFMBooks



def calculateTotalVersesForBook( BBB, getNumChapters, getNumVerses ):
    """
    Give it the functions for getting the number of chapters and number of verses
    Returns the total number of verses in the book
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "calculateTotalVersesForBook( {} )".format( BBB ) )
    totalVerses = 0
    try:
        for C in range( 1, getNumChapters(BBB)+1 ):
            totalVerses += getNumVerses( BBB, C )
        return totalVerses
    except TypeError: # if something is None (i.e., a book without chapters or verses)
        return 1
# end of BiblelatorHelpers.calculateTotalVersesForBook



def mapReferenceVerseKey( mainVerseKey ):
    """
    Returns the verse key for OT references in the NT (and vv), etc.

    Returns None if we don't have a mapping.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "mapReferenceVerseKey( {} )".format( mainVerseKey.getShortText() ) )

    # A (temporary) dictionary containing NT references to OT
    REFERENCE_VERSE_KEY_DICT = {
        SimpleVerseKey('MAT','2','18'): SimpleVerseKey('JER','31','15'),
        SimpleVerseKey('MAT','3','3'): SimpleVerseKey('ISA','40','3'),
        }

    if mainVerseKey in REFERENCE_VERSE_KEY_DICT:
        vPrint( 'Never', debuggingThisModule, '  returning {}'.format( REFERENCE_VERSE_KEY_DICT[mainVerseKey].getShortText() ) )
        return REFERENCE_VERSE_KEY_DICT[mainVerseKey]
# end of BiblelatorHelpers.mapReferenceVerseKey


def mapParallelVerseKey( forGroupCode, mainVerseKey ):
    """
    Returns the verse key for synoptic references in the NT, etc.

    Returns None if we don't have a mapping.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "mapParallelVerseKey( {}, {} )".format( forGroupCode, mainVerseKey.getShortText() ) )
    groupIndex = BiblelatorGlobals.BIBLE_GROUP_CODES.index( forGroupCode ) - 1
    parallelVerseKeyDict = {
        SimpleVerseKey('MAT','3','13'): (SimpleVerseKey('MRK','1','9'), SimpleVerseKey('LUK','3','21'), SimpleVerseKey('JHN','1','31') )
        }
    if mainVerseKey in parallelVerseKeyDict:
        vPrint( 'Never', debuggingThisModule, '  returning {}'.format( parallelVerseKeyDict[mainVerseKey][groupIndex].getShortText() ) )
        return parallelVerseKeyDict[mainVerseKey][groupIndex]
# end of BiblelatorHelpers.mapParallelVerseKey



loadedReferences = None
def mapReferencesVerseKey( mainVerseKey ):
    """
    Returns the list of FlexibleVerseKeys for references related to the given verse key.

    Returns None if we don't have a mapping.
    """
    global loadedReferences
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "mapReferencesVerseKey( {} )".format( mainVerseKey.getShortText() ) )
    if loadedReferences is None:
        loadedReferences = BibleReferencesLinks()
        loadedReferences.loadData()
    result = loadedReferences.getRelatedPassagesList( mainVerseKey )
    # Returns a list containing 2-tuples:
    #    0: Link type ('QuotedOTReference','AlludedOTReference','PossibleOTReference')
    #    1: Link FlexibleVersesKey object
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "  mapReferencesVerseKey got result:", result )
    resultList = []
    if result is not None:
        for linkType, link in result:
            resultList.append( link )
    return resultList
    # old sample code
        #REFERENCE_VERSE_KEY_DICT = {
            #SimpleVerseKey('MAT','2','18'): SimpleVerseKey('JER','31','15'),
            #SimpleVerseKey('MAT','3','3'): FlexibleVersesKey( 'ISA_40:3,7,14-15' ),
            #}
        #if mainVerseKey in REFERENCE_VERSE_KEY_DICT:
            #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                #dPrint( 'Quiet', debuggingThisModule, '  returning {}'.format( REFERENCE_VERSE_KEY_DICT[mainVerseKey].getShortText() ) )
            #return REFERENCE_VERSE_KEY_DICT[mainVerseKey]
# end of BiblelatorHelpers.mapReferencesVerseKey



def findCurrentSection( currentVerseKey, getNumChapters, getNumVerses, getVerseData ):
    """
    Given the current verseKey
        and functions to find the number of chapters and verses in the book
        and a function to get verse data (probably cached),
            find the beginning and end of the current section.

    Returns the verseKey for the start of the section
        and for the end of the section -- well actually the start of the next section.

    If no sections are found, it goes a maximum of one chapter back or one chapter forward.
    """
    if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "findCurrentSection( {}, … )".format( currentVerseKey.getShortText() ) )

    def sectionFoundIn( verseData ):
        """
        Given some verse data (a string or an InternalBibleEntryList
            returns True or False whether a section heading is found in it
        """
        vPrint( 'Never', debuggingThisModule, "sectionFoundIn( {!r} )".format( verseData ) )

        if verseData is None: return False

        elif isinstance( verseData, str ):
            #dPrint( 'Quiet', debuggingThisModule, "  It's a string!" )
            if '\\s ' in thisVerseData or '\\s1' in thisVerseData \
            or '\\s2' in thisVerseData or '\\s3' in thisVerseData:
                return True

        elif isinstance( verseData, tuple ):
            #dPrint( 'Quiet', debuggingThisModule, "  It's an InternalBibleEntryList!" )
            assert len(verseData) == 2
            verseDataList, context = verseData
            #dPrint( 'Quiet', debuggingThisModule, '   dataList', repr(verseDataList) )
            #dPrint( 'Quiet', debuggingThisModule, '    context', repr(context) )
            for verseDataEntry in verseDataList:
                if isinstance( verseDataEntry, InternalBibleEntry ):
                    marker, cleanText = verseDataEntry.getMarker(), verseDataEntry.getCleanText()
                elif isinstance( verseDataEntry, tuple ):
                    marker, cleanText = verseDataEntry[0], verseDataEntry[3]
                elif isinstance( verseDataEntry, str ):
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
                if marker in ( 's','s1','s2','s3','s4' ): return True

        else:
            vPrint( 'Quiet', debuggingThisModule, 'Ooops', repr(verseData) )
            vPrint( 'Quiet', debuggingThisModule, verseData.__type__ )
            halt # Programming error

        return False
    # end of sectionFoundIn

    # Start of main section of findCurrentSection
    BBB, C, V = currentVerseKey.getBCV()
    intC, intV = currentVerseKey.getChapterNumberInt(), currentVerseKey.getVerseNumberInt()
    #dPrint( 'Quiet', debuggingThisModule, 'fCS at', BBB, C, intC, V, intV )

    # First let's find the beginning of the section
    #  which could be in the current verse/chapter,
    #   or in the previous chapter (at most we assume)
    #dPrint( 'Quiet', debuggingThisModule, 'fCS finding start…' )
    firstC = max( intC-1, 0 )
    found = False
    for thisC in reversed( range( firstC, intC+1 ) ): # Look backwards
        numVerses = getNumVerses( BBB, thisC )
        startV, endV = 0, numVerses
        if thisC == intC: endV = min( intV, numVerses )
        for thisV in reversed( range( startV, endV+1 ) ):
            thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
            thisVerseData = getVerseData( thisVerseKey )
            if debuggingThisModule: ( ' ', thisC, thisV, repr(thisVerseData) )
            if sectionFoundIn( thisVerseData ):
                found = thisC, thisV; break
        if found: break
    if not found: found = firstC, 0
    startKey = SimpleVerseKey( BBB, found[0], found[1] )

    # Now let's find the end of the section
    #  which could be in the current chapter, or in the next chapter (at most we assume)
    #dPrint( 'Quiet', debuggingThisModule, 'fCS finding end…' )
    lastC = min( intC+1, getNumChapters( BBB ) )
    found = False
    for thisC in range( intC, lastC+1 ):
        numVerses = getNumVerses( BBB, thisC )
        startV, endV = 0, numVerses
        if thisC == intC: startV = min( intV+1, numVerses )
        for thisV in range( startV, endV+1 ):
            thisVerseKey = SimpleVerseKey( BBB, thisC, thisV )
            thisVerseData = getVerseData( thisVerseKey )
            if debuggingThisModule: ( ' ', thisC, thisV, repr(thisVerseData) )
            if sectionFoundIn( thisVerseData ):
                found = thisC, thisV; break
        if found: break
    if not found: found = lastC, numVerses
    endKey = SimpleVerseKey( BBB, found[0], found[1] )
    #dPrint( 'Quiet', debuggingThisModule, "fCS returning", startKey.getShortText(), endKey.getShortText() )
    return startKey, endKey
# end of BiblelatorHelpers.findCurrentSection



def handleInternalBibles( internalBible:Bible, controllingWindow ) -> Bible:
    """
    Try to only have one copy of internal Bibles
        even if it's open in multiple windows.

    Note that Biblelator never directly changes InternalBible objects --
        they are effectively 'read-only'.

    Returns an internal Bible object.
    """
    debuggingThisFunction = False
    if debuggingThisFunction or (BibleOrgSysGlobals.debugFlag and debuggingThisModule):
        vPrint( 'Quiet', debuggingThisModule, "handleInternalBibles( {}, {} )".format( internalBible, controllingWindow ) )
        assert isinstance( internalBible, Bible )
        #BiblelatorGlobals.theApp.setDebugText( "handleInternalBibles" )
        #dPrint( 'Quiet', debuggingThisModule, "hereHIB0", repr(internalBible), len(BiblelatorGlobals.theApp.internalBibles) )

    result = internalBible # Default to returning what we were given
    if debuggingThisFunction and internalBible is None:
        vPrint( 'Quiet', debuggingThisModule, "  hIB: Got None" )
    if internalBible is not None:
        if debuggingThisFunction: vPrint( 'Quiet', debuggingThisModule, "  hIB: Not None" )
        foundControllingWindowList = None
        for iB,cWs in BiblelatorGlobals.theApp.internalBibles:
            # Some of these variables will be None but they'll still match
            #and internalBible.sourceFilepath == iB.sourceFilepath \ # PTX Bible sets sourceFilepath but others don't!
            if type(internalBible) is type(iB) \
            and internalBible.abbreviation and internalBible.abbreviation == iB.abbreviation \
            and internalBible.name and internalBible.name == iB.name \
            and internalBible.sourceFilename and internalBible.sourceFilename == iB.sourceFilename \
            and internalBible.encoding == iB.encoding: # Let's assume they're the same
                if internalBible.sourceFolder == iB.sourceFolder:
                    if debuggingThisFunction: vPrint( 'Quiet', debuggingThisModule, "  Got an IB match for {}!".format( iB.name ) )
                    result, foundControllingWindowList = iB, cWs
                    break
                else:
                    if debuggingThisFunction:
                        vPrint( 'Quiet', debuggingThisModule, "handleInternalBibles: Got an almost IB match for {}!".format( iB.name ) )
                        vPrint( 'Quiet', debuggingThisModule, "    Source folders didn't match: {!r}\n           and {!r}".format( internalBible.sourceFolder, iB.sourceFolder ) )
                    result, foundControllingWindowList = iB, cWs
                    break

        if foundControllingWindowList is None: BiblelatorGlobals.theApp.internalBibles.append( (internalBible,[controllingWindow]) )
        else: foundControllingWindowList.append( controllingWindow )

    if debuggingThisFunction or debuggingThisModule or (BibleOrgSysGlobals.debugFlag and debuggingThisModule):
        vPrint( 'Quiet', debuggingThisModule, "Internal Bibles ({}) now:".format( len(BiblelatorGlobals.theApp.internalBibles) ) )
        for something in BiblelatorGlobals.theApp.internalBibles:
            vPrint( 'Quiet', debuggingThisModule, "  ", something )
        vPrint( 'Quiet', debuggingThisModule, BiblelatorGlobals.theApp.internalBibles )
        for j,(iB,cWs) in enumerate( BiblelatorGlobals.theApp.internalBibles ):
            vPrint( 'Quiet', debuggingThisModule, "  {}/ {} in {}".format( j+1, iB.getAName(), cWs ) )
            vPrint( 'Quiet', debuggingThisModule, "      {!r} {!r} {!r} {!r}".format( iB.name, iB.givenName, iB.shortName, iB.abbreviation ) )
            vPrint( 'Quiet', debuggingThisModule, "      {!r} {!r} {!r} {!r}".format( iB.sourceFolder, iB.sourceFilename, iB.sourceFilepath, iB.fileExtension ) )
            vPrint( 'Quiet', debuggingThisModule, "      {!r} {!r} {!r} {!r}".format( iB.status, iB.revision, iB.version, iB.encoding ) )

    if debuggingThisModule or debuggingThisFunction:
        vPrint( 'Quiet', debuggingThisModule, f"  handleInternalBibles is returning: {result}")
    return result
# end of BiblelatorHelpers.handleInternalBibles


def getChangeLogFilepath( loggingFolder, projectName ):
    """
    """
    return os.path.join( loggingFolder, \
                        BibleOrgSysGlobals.makeSafeFilename( projectName.replace(' ','_') + '_ChangeLog.txt' ) )
# end of BiblelatorHelpers.getChangeLogFilepath


def logChangedFile( userName, loggingFolder, projectName, savedBBB, bookText ):
    """
    Just logs some info about the recently changed book to a log file for the project.
    """
    #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        #dPrint( 'Quiet', debuggingThisModule, "logChangedFile( {}, {!r}, {}, {} )".format( loggingFolder, projectName, savedBBB, len(bookText) ) )

    filepath = getChangeLogFilepath( loggingFolder, projectName )

    ## TODO: Why don't we just append it to the existing file???
    #try: logText = open( filepath, 'rt', encoding='utf-8' ).read()
    #except FileNotFoundError: logText = ''

    logText = '{} {} {:,} characters ({} chapters, {:,} verses) saved by {}\n' \
                .format( datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    savedBBB, len(bookText), bookText.count( '\\c ' ), bookText.count( '\\v ' ), userName )
    with open( filepath, 'at', encoding='utf-8' ) as logFile: # Append puts the file pointer at the end of the file
        logFile.write( logText )
# end of BiblelatorHelpers.logChangedFile



def parseEnteredBooknameField( bookNameEntry, currentBBB, CEntry, VEntry, BBBfunction ):
    """
    Checks if the bookName entry is just a book name, or an entire reference (e.g., "Gn 15:2")

    BBBfunction is a function to find BBB from a word/string.

    Returns the discovered BBB, C, V

    NOTE: We don't validate that they are valid C V combinations
    """
    debuggingThisFunction = False

    if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
        vPrint( 'Quiet', debuggingThisModule, "parseEnteredBooknameField( {!r}, {}, {!r}, {!r}, … )" \
                                .format( bookNameEntry, currentBBB, CEntry, VEntry ) )

    # Do a bit of preliminary cleaning-up
    bookNameEntry = bookNameEntry.strip().replace( '  ', ' ' )
    #dPrint( 'Quiet', debuggingThisModule, "parseEnteredBooknameField: pulling apart {!r}".format( bookNameEntry ) )

    # Without the bookname (i.e., stay in current book)
    # Do these first because they are more strict (only digits and use re.fullmatch not re.search or re.match)
    match = re.fullmatch( '(\d{1,3})[:\. ](\d{1,3})', bookNameEntry ) # (Current book) C:V or C.V or C V
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matched CV! {!r} {!r}".format( match.group(1), match.group(2) ) )
        return currentBBB, match.group(1), match.group(2)
    match = re.fullmatch( '(\d{1,3})', bookNameEntry ) # (Current book) C
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matched C or V! {!r} as {!r} from {!r}".format( match.group(0), match.group(1), bookNameEntry ) )
        if BibleOrgSysGlobals.loadedBibleBooksCodes.isSingleChapterBook( currentBBB ): # take it as a V (not a C)
            return currentBBB, 1, match.group(1)
        return currentBBB, match.group(1), 1
    match = re.fullmatch( '[Vv:\.](\d{1,3})', bookNameEntry ) # (Current book) V
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matchedV! {!r}".format( match.group(1) ) )
        return currentBBB, CEntry, match.group(1)

    # With a BBB first on the line
    uppercaseBookNameEntry = bookNameEntry.upper()
    match = re.fullmatch( BBB_RE + '[ ]{0,1}(\d{1,3})[:\. ](\d{1,3})', uppercaseBookNameEntry ) # bookname C:V or C.V or C V
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matchedBBBCV! {!r} {!r} {!r}".format( match.group(1), match.group(2), match.group(3) ) )
        newBBB = match.group(1)
        if BibleOrgSysGlobals.loadedBibleBooksCodes.isValidBBB( newBBB ): # confirm that it's a BBB
            return newBBB, match.group(2), match.group(3)
    match = re.fullmatch( BBB_RE + '[ ]{0,1}[Vv:\.](\d{1,3})', uppercaseBookNameEntry ) # bookname (single chapter book) V
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matchedBBBV! {!r} {!r} (for chapter {!r})".format( match.group(1), match.group(2), CEntry ) )
        newBBB = match.group(1)
        if BibleOrgSysGlobals.loadedBibleBooksCodes.isValidBBB( newBBB ): # confirm that it's a BBB
            return newBBB, CEntry, match.group(2)
    match = re.fullmatch( BBB_RE + '[ ]{0,1}(\d{1,3})', uppercaseBookNameEntry ) # bookname C (or single chapter book with V)
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matchedBBB C or V! {!r} {!r}".format( match.group(1), match.group(2) ) )
        newBBB = match.group(1)
        if BibleOrgSysGlobals.loadedBibleBooksCodes.isValidBBB( newBBB ): # confirm that it's a BBB
            if BibleOrgSysGlobals.loadedBibleBooksCodes.isSingleChapterBook( newBBB ): # take it as a V (not a C)
                return newBBB, 1, match.group(2)
            return newBBB, match.group(2), 1

    # With a bookname first on the line
    match = re.fullmatch( '([123]{0,1}?\D+?)[ ]{0,1}(\d{1,3})[:\. ](\d{1,3})', bookNameEntry ) # bookname C:V or C.V or C V
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matchedBCV! {!r} {!r} {!r}".format( match.group(1), match.group(2), match.group(3) ) )
        return BBBfunction( match.group(1) ), match.group(2), match.group(3)
    match = re.fullmatch( '([123]{0,1}?\D+?)[ ]{0,1}[Vv:\.](\d{1,3})', bookNameEntry ) # bookname (single chapter book) V
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matchedBV! {!r} {!r} (for chapter {!r})".format( match.group(1), match.group(2), CEntry ) )
        newBBB = BBBfunction( match.group(1) )
        return newBBB, CEntry, match.group(2)
    match = re.fullmatch( '([123]{0,1}?\D+?)[ ]{0,1}(\d{1,3})', bookNameEntry ) # bookname C (or single chapter book with V)
    if match:
        if debuggingThisFunction or BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            vPrint( 'Quiet', debuggingThisModule, "  matchedB C or V! {!r} {!r}".format( match.group(1), match.group(2) ) )
        newBBB = BBBfunction( match.group(1) )
        if BibleOrgSysGlobals.loadedBibleBooksCodes.isSingleChapterBook( newBBB ): # take it as a V (not a C)
            return newBBB, 1, match.group(2)
        return newBBB, match.group(2), 1

    #else: # assume it's just a book name (with no C or V specified)
    newBBB = BBBfunction( bookNameEntry )
    if newBBB == currentBBB:
        return newBBB, CEntry, VEntry
    else: return newBBB, 1, 1 # Go to the first verse
# end of BiblelatorHelpers.parseEnteredBooknameField



def briefDemo() -> None:
    """
    Main program to handle command line parameters and then run what they want.
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = Tk()
    tkRootWindow.title( programNameVersion )

    #swnd = SaveWindowsLayoutNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test SWND" )
    #dPrint( 'Quiet', debuggingThisModule, "swndResult", swnd.result )
    #dwnd = DeleteWindowsLayoutNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test DWND" )
    #dPrint( 'Quiet', debuggingThisModule, "dwndResult", dwnd.result )
    #srb = SelectResourceBox( tkRootWindow, [(x,y) for x,y, in {"ESV":"ENGESV","WEB":"ENGWEB","MS":"MBTWBT"}.items()], "Test SRB" )
    #dPrint( 'Quiet', debuggingThisModule, "srbResult", srb.result )

    # Program a shutdown
    tkRootWindow.after( 2_000, tkRootWindow.destroy ) # Destroy the widget after 2 seconds

    # Start the program running
    #tkRootWindow.mainloop()
# end of BiblelatorHelpers.briefDemo

def fullDemo() -> None:
    """
    Full demo to check class is working
    """
    from tkinter import Tk

    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )
    vPrint( 'Quiet', debuggingThisModule, "Running demo…" )

    tkRootWindow = Tk()
    tkRootWindow.title( programNameVersion )

    #swnd = SaveWindowsLayoutNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test SWND" )
    #dPrint( 'Quiet', debuggingThisModule, "swndResult", swnd.result )
    #dwnd = DeleteWindowsLayoutNameDialog( tkRootWindow, ["aaa","BBB","CcC"], "Test DWND" )
    #dPrint( 'Quiet', debuggingThisModule, "dwndResult", dwnd.result )
    #srb = SelectResourceBox( tkRootWindow, [(x,y) for x,y, in {"ESV":"ENGESV","WEB":"ENGWEB","MS":"MBTWBT"}.items()], "Test SRB" )
    #dPrint( 'Quiet', debuggingThisModule, "srbResult", srb.result )

    # Program a shutdown
    tkRootWindow.after( 30_000, tkRootWindow.destroy ) # Destroy the widget after 30 seconds

    # Start the program running
    #tkRootWindow.mainloop()
# end of BiblelatorHelpers.fullDemo

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    fullDemo()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of BiblelatorHelpers.py
