Getting Started with Biblelator
===============================

Last updated: 2017-09-04 RJH


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

    ADVANCED: Biblelator can also be started with the --override flag to override the
    normal Biblelator.ini settings file with your own file, e.g.,
        Biblelator.py --override Test.ini
    will use Test.ini rather than Biblelator.ini for loading/saving program settings.

    This feature can be used if you regularly switch between a number of different
    project environments, e.g., you are working on separate English and French translations
    and have different resources, etc. open in the two different projects. Run Biblelator,
    set-up your windows for the English project, then exit Biblelator. Go to the settings
    folder (see above) and rename Biblelator.ini to English.ini. Now do the same for
    the French translation windows so you get French.ini. Now you can start Biblelator
    with either of the following:
        Biblelator.py -o English
        Biblelator.py -o French

    It's recommended that you edit the .ini settings file to enable Internet access unless
        you have (security) reasons not to. You'll also see other settings that can be
        adjusted. (Eventually you'll be able to set these from inside the program, but
        the settings editor hasn't been written yet.)


2. Logging

    A folder called BiblelatorLogs is also created inside the BiblelatorData folder. The
    last two or more logs (e.g., Biblelator_log.txt and Biblelator_log.txt.bak) are kept
    in this folder. These logs may be useful to the programmers after a program crash to
    help determine what caused the fault.

    If Internet access is enabled in the settings file, and the sendUsageStatistics flag
    is enabled, then the logs will be automatically uploaded to the Freely-Given.org
    server.


3. Main window

    The Biblelator main window is a small window that is used to open other windows.
    It also contains the main bar for entering book/chapter/verse values
        and for entering lexicon words.
    The main window can usually be kept fairly small and be placed in the most convenient
        part of the screen. However, if Biblelator is started in debug mode (with the
        --debug flag on the command line), the main window may need to be made larger
        in order to properly display the additional debug logging information.
    In touch-screen mode, Biblelator will display the main window with larger buttons
    suitable for touching accurately with a fingertip.


4. Resource texts

    Resources are texts which are opened read-only for study or reference purposes as you
        translate in a project window. This includes most unencrypted Bibles, commentaries,
        and some lexicons. These might be other USFM Bibles that you have been given by
        colleagues in other nearby languages, or perhaps mainstream translations that have
        been installed on your computer by other Bible display programs or that you have
        downloaded.
    Depending on the type of resource you are opening, you might be required to select
        either a folder or a file to open the resource.


5. Resource Windows

    The Resource menu in the main window is used to launch new resource windows which can
    be moved anywhere on your screen(s).


6. Resource Collection Windows

    Resources are texts which are opened read-only for study or reference purposes as you
        translate in a project window. This includes Bibles, commentaries, and lexicons.
    Unllike Resource Windows above, Resource Collection Windows allow the display of several
        resource boxes within the same window. This makes better use of the screen space,
        however, these resource boxes can't display large segments of the text (like chapters)
        -- only a verse or two.
    The Resource menu in the main window is used to launch new resource collection windows,
        and then individual resource boxes are opened from the Resource menu inside that
        new window.


7. Reference Collection Windows

    Reference collection windows display read-only cross-references all in the same version.
    They display individual verses, groups of verses, or ranges of verses.
    The Window menu in an edit window is used to launch new reference collection windows,
        and the references will automatically show in that same version.


8. Lexicon Windows

    There is a Bible lexicon window, but it's not yet automatically linked to Bible resources.
    At this stage, you can use the text box to the right of the verse number in the main
    window in order to enter Hebrew or Greek Strong's codes such as H123 or G1026.


9. Project Windows

    Projects are Bibles in the process of being translated, so they have a full edit window.

    Note that the default settings for AutocompleteMode in the .ini settings file is None.
    Other options are Bible and BibleBook. Using Bible AutocompleteMode slows down the
    starting of Biblelator as existing Bible books are scanned to find all words used, but
    having the pop-up autocomplete box make suggestions can significantly speed up typing
    of commonly used terms, plus it can also highlight mispellings if you scan through the
    suggestions. (Use ESC or just keep typing to dismiss the pop-up window.)


9a. Biblelator Project Windows

    If Biblelator is your only Bible editor, you can use our native Bible projects. At this
    stage, you simply give a Bible name and abbreviation, e.g., "My special Bible", "MSB".
    The project files are saved as UTF-8 files in your BiblelatorSettings folder. (These
    projects are not fully developed yet.)


9b. Paratext Project Windows

    If you already have a Paratext project, Biblelator can also be used as an editor/checker
    (but of course you're likely to lose work if you edit using both programs on the same
    files at the same time so we suggest only having one of these programs open at a time).
    You point Biblelator at the .SSF file to open an existing Paratext project in Biblelator.
    (This feature is used extensively by the developer, so it's well tested, at least on
    Linux.)


10. Bible Groups

    Biblelator has five group codes (A,B,C,D,E) that Bible windows can be assigned to. All
    new windows are assigned to group A by default but this can be easily changed. Each
    group can be set to a different reference, e.g., if group A windows are in Matthew,
    group B windows might be displaying a reference in Isaiah that was quoted by Matthew.

    In the future, there will be automatic ways to display OT references (like the above
    example -- at the moment it must be set-up by hand) and also to display synoptic
    gospel references, e.g., by having separate Bible windows open in groups A,B,C,D
    automatically displaying parallels in Matthew, Mark, Luke, and John.


11. Optional Start-up Parameters

    If you start Biblelator with the --help command-line flag, the program will display
    the available parameters which can be used and then exit immediately.

    The --verbose flag can be used to get the program to display more information in
    the start-up/terminal window, although it can easily be overwhelming. However,
    it might be helpful to get more information in order to report a fault.

    The --debug flag is usually used by programmers to display debugging information
    and is more likely to cause the program to fail, so is not recommended for
    normal users.

    Note that the --strict flag is part of the Bible Organisational System
    usually used for strict checking of data files where you want to halt
    even if there's a small error. You usually don't want this behaviour
    in an editor so it's not recommended for Biblelator.

    Note that multiprocessing is currently disabled, so the --single flag
    currently does nothing.

