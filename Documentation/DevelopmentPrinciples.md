Biblelator Development Principles
=================================

Last updated: 2018-02-16 RJH


The following are some of the reasons behind some of the major development decisions
    concerning the development of Biblelator.


1. Python as the language

    Python is not as fast and efficient as C or C++, but it is nevertheless an elegant, well-designed
    computer language that runs quite satisfactorily on most modern computer hardware.

    Another reason for choosing Python is that the source code to the software is usually provided
    and that it can be easier to read by novices/non-programmers than some other computer languages.
    This is important to us, because Biblelator is designed to be hackable, i.e., a creator or
    translator of the Bible might have a chance of making a small change to the program in order
    to handle a specific need that he/she might have (or if not, to hire someone else to make the
    change).

    According to Wikipedia: "Python is a widely used high-level, general-purpose, interpreted,
    dynamic programming language. Its design philosophy emphasizes code readability, and its syntax
    allows programmers to express concepts in fewer lines of code than would be possible in languages
    such as C++ or Java. The language provides constructs intended to enable clear programs on both
    a small and large scale." These are exactly some of the reasons that Python was chosen.
    (From https://en.wikipedia.org/wiki/Python_(programming_language) )


2. Python3 versus Python2

    Python3 was already in development when the Bible Organisational System (BibleOrgSys --
    started 2010) that Biblelator (started 2014) depends on was being prototyped. It was already
    obvious then that Python2 would eventually stop being developed, and so there didn't seem to
    be any point in creating a new piece of software based on a language version already
    destined to be obsoleted (even though many libraries hadn't yet been updated at the time).

    Also Python3 was Unicode compatible from the beginning and this is important for a Bible
    editor that's expected to be used to handle many non-Roman based character sets.


3. Tkinter as the widget set

    Tkinter is not the most beautiful or advanced widget set, but it is an intrinsic part
    of regular Python distributions. So it was chosen for its universality rather than
    trying to choose one of quite a number of competing toolkits (e.g., QT, wxWidgets, etc.)
    which require extra installation complexities and which may not work well (or at all)
    on some platforms. Time will tell whether or not this was a wise decision -- unfortunately
    some cross-platform behaviours have been found to be inconsistent.


4. Internationalisation

    Like the Bible Organisational System (BibleOrgSys) that Biblelator is based on top of, this
    Bible editor is designed to (eventually) be flexible enough to handle different versification
    systems, different combinations and orders for Bible books, etc.

    Some preparation work has already been done in the program to allow translations of menus,
    etc., to match your Operating System locale/language, but no translations have been
    started yet.

    Although all string handling in the BibleOrgSys and Biblelator is Unicode, no attempts
    have been made yet to test or handle complex fonts or right-to-left languages.


5. More control of child window placement

    Biblelator tries to allow the user to place the main window and child windows anywhere on
    a multi-screen system, but with tools to easily find child windows if they get covered.

    Possibly a future option will allow windows to be constrained within the main window.


6. Use of colour

    Biblelator tries to use colour effectively to help distinguish the various different types
    of controls and windows, as well as to distinguish various kinds of fields within documents.
    We have more concern about functionality (using colours to assist the user in finding things
    quickly), than in attractive appearance. Much more use of colour and stylesheets is expected
    in future versions.


7. Use of autocompletion and autocorrection

    Biblelator tries to use autocompletion of words and other modern helps to assist the
    translators to work more efficiently.


8. Use of keyboard shortcuts

    Biblelator aims to (eventually) make it very efficient for users to edit Bibles if they
    are prepared to invest a little time and energy into learning keyboard shortcuts for
    navigating around Bibles and around the most commonly used menu entries. (It's planned
    that keyboard shortcuts will eventually be customisable by the user.)


9. Downplaying chapters and verses

    I don't like the over-emphasis of chapters and verses in Bibles. I'm much more interested
    in semantic structure such as phrases, clauses, sentences, paragraphs, and sections. So
    Biblelator is designed to downplay chapter and verse boundaries as much as possible (yet
    keep them available for those who do value them).


10. Including book introductions

    Biblelator considers a book introduction as chapter "-1", and considers anything before
    verse one in a chapter (e.g., a chapter heading), as verse "zero". It should be as easy and
    convenient to edit introductions as actual Bible text, and we can also handle the (rare)
    Bibles that have an actual chapter 0 with "verses".


11. Including other front and back matter

    Biblelator is aware of front and back matter (e.g., Bible introduction, glossary, etc.)
    and knows to treat them differently than books containing chapters and verses.


12. Saving your work

    We currently use AutoSave to save regular copies of your Bible editing and plan to use
    (optional of course) remote storage in the cloud in the future to provide assurance
    that program bugs or power or computer failures won't lose lots of work.

    WARNING: Of course, being an early tester increases the risk that you'll be the one to
    discover a new bug, but the developer is currently using Biblelator for his own Bible
    translation work.


13. No hidden folders

    Settings files, log files, autosave files, etc. are all saved in non-hidden folders.
    While this might irritate some tidyness freaks, it's in line with our "hackable"
    goals to make everything about Biblelator obvious and accessible.


14. Protecting your work

    We do plan to implement a system where an administrator can set permissions for who in a
    team has easy edit access to particular projects and books (or even chapters) within
    projects. However, please note that since this requirement is in opposition to the
    "hackability" requirement, it will only be nominal protection that works with users who
    conform to the system, i.e., computer savy users will certainly be able to find ways to
    circumvent such "protections".


15. Translation resources

    We do hope to be able to automatically access more open-source Bible translation resources,
    create more of our own resources (especially key terms and other lists), and maybe get
    permission to redistribute other Bible and related modules in an easier-to-user format.


16. Prototype implementation

    All of the existing code is considered as "prototype/proof-of-concept", i.e., it has not
    been optimised for speed and software simplicity (refactoring), but rather to get the
    program working. (There is also an element of balancing expensive programmer time
    [expensive as "in short supply"] vs. cheap computer CPU time which we expect to continue
    to get "cheaper" as even mobile devices get faster/multicored CPUs and GPUs plus more
    onboard RAM and non-volatile [e.g., FLASH] memory.)

    Future optimisations will include optimising screen space, both for modern desktop
    environments and for small screen mobile devices. Bible translators usually like lots
    of resources open and they all compete for screen space. A first step might be getting
    rid of some of the menus and/or moving some commonly used buttons onto the blank space
    in the menu bars.

    After version one is released, only then will time and resources be spent on getting
    the program working more efficiently. Also, after version one, new versions will provide
    a path to automatically upgrade settings and other files if the formats change -- this
    is not guaranteed for preliminary versions (where you might have to set-up your
    preferences again).

    Note that not all settings can be adjusted from the menus in the prototypes -- some must
    be still be adjusted by editing settings files or changing program code.


17. User-requested priorities

    As far as fixing deficiencies and adding new features, we will try to prioritise what actual
    users find important for their workflow, including the developer of course.


18. ESFM (Enhanced Standard Format Markers) aware

    Biblelator is intended to become an ESFM Bible editor. This allows more links and other
    information to be included in source Bibles (especially those intended for online display.)

    NOTE: ESFM development is currently on hold, awaiting the release of the USFM v3
    specifications. See http://Freely-Given.org/Software/BibleDropBox/ESFMBibles.html
    for more info.
