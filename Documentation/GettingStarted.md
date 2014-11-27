Getting Started with Biblelator
===============================

Last updated: 2014-11-23 RJH


This document is to help the Biblelator user to get an understanding how the developer
    anticipated that the program might be used.

Installation is not described here -- you should follow the instructions in
    Installation.md before using this document.

For an overview of the program design philosophy, see Development.md.


1. Settings

    When Biblelator is run the first time, it tries to create a BiblelatorData folder in
    the user's home folder. Inside there, it creates a BiblelatorSettings folder and the
    file Biblelator.ini inside that. The idea of the settings file is that Biblelator tries
    to remember the size and position of open windows plus the current Scripture reference
    position, and to return to the last values when the program is restarted.

    The settings file can be viewed (or even changed if you are careful) with a simple text
    editor program. (If Notepad doesn't work, try Wordpad.) Just make sure that Biblelator
    is closed if you are editing settings, otherwise your changes may be overwritten when
    Biblelator exits.

    If you want to reset Biblelator to its default settings, the settings file can be
    renamed (e.g., to Biblelator.ini.bak) or deleted (if you're sure you don't want to
    reuse them) and Biblelator will now ignore those settings when starting up. (This might
    also be necessary if a bug causes Biblelator to freeze or malfunction.)


2. Logging

    A folder called BiblelatorLogs is also created inside the BiblelatorData folder. The
    last two logs (e.g., Biblelator_log.txt and Biblelator_log.txt.bak) are kept in this
    folder. These logs may be useful to the programmers after a program crash to help
    determine what caused the fault.


3. Main window

    The Biblelator main window is a small window that is used to open other windows.
    It also contains the main bar for entering book/chapter/verse values
        and for entering lexicon words.
    The main window can usually be kept fairly small and be placed in the most convenient
        part of the screen. However, if Biblelator is started in debug mode (with the
        --debug flag on the command line), the main window may need to be made larger
        in order to properly display the additional logging information.


4. Resource Windows

    Resources are texts which are opened read-only for study or reference purposes as you
        translate in a project window. This includes Bibles, commentaries, and lexicons.
    The Resource menu in the main window is used to launch new resource windows.


5. Resource Collection Windows

    Resources are texts which are opened read-only for study or reference purposes as you
        translate in a project window. This includes Bibles, commentaries, and lexicons.
    Unllike Resource Windows above, Resource Collection Windows allow the display of several
        resource boxes within the same window. This makes better use of the screen space,
        however, these resource boxes can't display large segments of the text (like chapters)
        -- only a verse or two.
    The Resource menu in the main window is used to launch new resource collection windows,
        and then individual resource boxes are opened from the Resource menu inside that
        new window.


6. Lexicon Windows

    There is a Bible lexicon window, but it's not yet automatically linked to Bible resources.
    At this stage, you can use the text book to the right of the verse number in the main
    window in order to enter Strong's codes such as H123 or G1026.
7. Project Windows

    Projects are Bibles in the process of being translated, so they have a full edit window.


8. Bible Groups

    Biblelator has four group codes (A,B,C,D) that Bible windows can be assigned to. All
    new windows are assigned to group A by default but this can be easily changed. Each
    group can be set to a different reference, e.g., if group A windows are in Matthew,
    group B windows might be displaying a reference in Isaiah that was quoted by Matthew.

    In the future, there will be automatic ways to display OT references (like the above
    example -- at the moment it must be set-up by hand) and also to display synoptic
    gospel references.