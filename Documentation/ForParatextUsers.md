Notes for Paratext users
========================

Last updated: 2018-02-16 RJH


This document is to help the Biblelator user who has been accustomed to using UBS/SIL
    Paratext to get an understanding how the Biblelator differs from Paratext,
    including what Paratext features are missing, and what Biblelator features
    are different. You might also find HelpfulHints.md and FAQs.md helpful.

Installation is not described here -- you should follow the instructions in
    Installation.md to get the program running.

Getting started is not described here -- you should follow the instructions in
    GettingStarted.md before using this document.

For an overview of the program design philosophy, see Development.md.


Features in Biblelator that are different
=========================================

1. Window placement
    Biblelator doesn't have one large window like Paratext with "daughter" windows
    inside it. Rather the "main" window is relatively small, and "daughter" windows
    can be placed anywhere on your screen/screens, i.e., they don't all have to be
    together in one place.

2. Resources
    Paratext can display official downloaded resources (encypted zip files) that
    are kept in a special folder inside the Windows "Program Files" folder.
    Biblelator cannot access these passworded resources.

    Paratext can also display USFM resources that are inside the
    "My Paratext 8 Projects" or "My Paratext Projects" folders. Biblelator should
    be able to open and display these resources and/or to open them as projects
    for editing.

    Biblelator can display many kinds of Bible resources from any folder on your
    computer, as well as downloaded resources (from Faith Comes By Hearing).

3. Chapter/Verse Numbering
    Paratext lumps all USFM lines before chapter 1 verse 1 as chapter 1 verse 0
    (which means scrolling doesn't synchronise between different windows).

    Biblelator considers everything before the chapters/verses as "chapter -1",
    and each line is a verse number (starting with the id line as "verse 0").
    This allows the rare case of Bibles which actually have a chapter 0.

    Also, Biblelator moves things like section headings into the next verse,
    rather than displaying them as an appendage to the previous verse. The
    chapter number itself, is considered to be in "verse 0".


Features only in Biblelator
===========================

1. Autocomplete
    Biblelator can be asked to suggest words as you type. Suggested words can come
    from the current Bible, the current Bible book, or a dictionary. Just press
    ESC if you don't want any of the suggestions from the pop-up box.


Features missing from Biblelator
================================

1. Still too many to list. :(
    (See ToDo.md for a list of planned improvements and features to be added.)
