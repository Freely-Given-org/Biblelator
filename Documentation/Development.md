Biblelator Development Principles
=================================

Last updated: 2016-02-12 RJH


The following are some of the reasons behind some of the major development decisions
    concerning the development of Biblelator.


1. Python as the language

    Python is not as fast and efficient as C or C++, but it is nevertheless an elegant, well-designed
    computer language that runs quite satisfactorily on most modern computer hardware. Also, it can
    be relatively readable by a non Python programmer.

    Another reason for choosing Python is that the source code to the software is usually provided
    and that it can be easier to read by novices than some other computer languages. This is
    important to us, because Biblelator is designed to be hackable, i.e., a creator or translator
    of the Bible might have a chance of making a small change to the program in order to handle
    a specific need that he/she might have (or if not, to hire someone else to make the change).


2. Python3 versus Python2

    Python3 was already in development when the Bible Organisational System (BibleOrgSys --
    started 2010) that Biblelator (started 2014) depends on was being prototyped. It was already
    obvious then that Python2 would eventually stop being developed, and so there didn't seem to
    be any point in creating a new piece of software based on a language version already
    destined to be obsoleted (even though many libraries hadn't yet been updated at the time).


3. TKinter as the widget set

    TKinter is not the most beautiful or advanced widget set, but it is an intrinsic part
    of regular Python distributions. So it was chosen for its universality rather than
    trying to choose one of quite a number of competing toolkits (e.g., QT, wxWidgets, etc.)
    which require extra installation complexities and which may not work well (or at all)
    on some platforms. Time will tell whether or not this was a wise decision -- unfortunately
    some cross-platform behaviours have been found to be inconsistent.


4. Internationalised

    Like the Bible Organisational System (BibleOrgSys) that Biblelator is based on top of, this
    Bible editor is designed to (eventually) be flexible enough to handle different versification
    systems, different combinations and orders for Bible books, etc.


5. Downplaying chapters and verses

    I don't like the over-emphasis of chapters and verses. I'm much more interested in semantic
    structure such as phrases, clauses, sentences, and paragraphs. So Biblelator is designed
    to downplay chapter and verse boundaries as much as possible (yet keep them available for
    those who do value them).


6. Use of colour

    Biblelator tries to use colour effectively to help distinguish the various different types
    of windows, as well as to distinguish various kinds of fields within documents.


7. Use of autocompletion and autocorrection

    Biblelator tries to use autocompletion of words and other modern helps to assist the
    translation to work more efficiently.


8. Including book introductions

    Biblelator considers a book introduction as chapter "zero", and considers anything before
    verse one in a chapter (e.g., a section heading), as verse "zero". It should be as easy and
    convenient to edit introductions as actual Bible text.


9. Including other front and back matter

    Biblelator is aware of front and back matter (e.g., Bible introduction, glossary, etc.)
    and knows to treat them differently than books containing chapters and verses.


10. More control of child window placement

    Biblelator tries to allow the user to place the main window and child windows anywhere on
    a multi-screen system, but with tools to easily find child windows if they get covered.


11. Prototype implementation

    All of the existing code is considered as "prototype/proof-of-concept", i.e., it has not
    been optimised for speed and software simplicity (refactoring), but rather to get the
    program working. Note that not all settings can be adjusted from the menus in the
    prototypes -- some must be adjusted by editing settings files or changing program code.

    After version one is released, only then will time and resources be spent on getting it
    working more efficiently. Also, after version one, new versions will provide a path to
    automatically upgrade settings and other files if the formats change -- this is not
    guaranteed for preliminary versions (where you might have to set-up your preferences
    again).


12. User-requested priorities

    As far as fixing deficiencies and adding new features, we will try to prioritise what actual
    users find important for their workflow, including the developer of course.


13. ESFM (Enhanced Standard Format Markers) aware

    Biblelator is intended to become an ESFM Bible editor. This allows more links and other
    information to be included in source Bibles (especially those intended for online display.)