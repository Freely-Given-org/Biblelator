Biblelator Installation
=======================

Last updated: 2014-11-23 RJH


Please see the document Development.md for information about the design decisions behind
how and why Biblelator was developed.

This document provides basic instructions for installing and running a copy of the development
version of Biblelator onto your computer.


1. Install Python3

    Biblelator uses Python3 (it's currently being developed on Python 3.4
        but will probably run on most relatively recent versions of Python3.

    To see if Python3 is installed on your computer,
        open a terminal or command window on your system and enter:
            python3
    If Python3 is installed, it should show a version number and a >>> prompt.
        Type "quit()" (without the quotes) to exit Python.

    If it's not already installed, you should install Python3 on your system either
        through the software manager on your system, or else
        as per the instructions here at https://www.python.org/downloads.


2. Optionally install Git

    Git is a program that makes it easy to fetch the latest Biblelator files from the Internet.
    However, you don't have to install Git if you don't want to.

    You can run Git from a command window, or else from a GUI program such as TortoiseGit on Windows.

    If it's not already installed, you should install Git on your system either
        through the software manager on your system, or else
        as per the instructions here at http://git-scm.com/downloads and/or
        TortoiseGit for Windows as per the instructions at
            https://code.google.com/p/tortoisegit/wiki/Download.

    If you use Git in steps #4 and #5 below, then to upgrade later to future versions
        of BibleOrgSys and Biblelator, you just have to do a "git pull" command
        on each of those folders.


3. Create a folder for Biblelator -- we recommend the name BiblelatorFiles.
    If you want other users on your computer to be able to use Biblelator,
        either create this folder somewhere public such as in Public Documents, or else
        change the permissions of the folder to allow other users
            to be able to read from it and write to it.
    You can call the folder anything you like,
        but these instructions will assume that you called it BiblelatorFiles.


4. Install the Bible Organisational System inside the BiblelatorFiles folder.
    Open https://github.com/openscriptures/BibleOrgSys in a browser window.
    On the right-hand side of the page are links to either:
        a. Download (clone) BibleOrgSys with Git (using either HTTPS or SSH (if you have a GitHub account).
            This method allows easier updating to future development versions.
        b. Without Git, download the current version BibleOrgSys as a ZIP file and
            unzip the file in the BiblelatorFiles folder (then remove -master from the folder name).
    Either way, you should end up with a new folder called BibleOrgSys
        inside your BiblelatorFiles folder from step #3.


5. Install the Biblelator program inside the BiblelatorFiles folder.
    Open https://github.com/openscriptures/Biblelator in a browser window.
    On the right-hand side of the page are links to either:
        a. Download (clone) Biblelator with Git (using either HTTPS or SSH (if you have a GitHub account).
            This method allows easier updating to future development versions.
        b. Without Git, download the current version Biblelator as a ZIP file and
            unzip the file in the BiblelatorFiles folder (then remove -master from the folder name).
    Either way, you should end up with a new folder called Biblelator
        inside your BiblelatorFiles folder from step #3.


6. Install OpenScriptures HebrewLexicon.
    Open https://github.com/openscriptures/HebrewLexicon
    On the right-hand side of the page are links to either:
        a. Download (clone) HebrewLexicon with Git (using either HTTPS or SSH (if you have a GitHub account).
            This method allows easier updating to future corrected versions.
        b. Without Git, download the current version HebrewLexicon as a ZIP file and
            unzip the file in the first/top BiblelatorFiles folder (then remove -master from the folder name).
    Either way, you should end up with a new folder called HebrewLexicon
        inside your BiblelatorFiles folder from step #3.


7. Install morhgnt Greek Strongs info.
    Open https://github.com/morphgnt/strongs-dictionary-xml
    On the right-hand side of the page are links to either:
        a. Download (clone) strongs-dictionary-xml with Git (using either HTTPS or SSH (if you have a GitHub account).
            This method allows easier updating to future corrected versions.
        b. Without Git, download the current version strongs-dictionary-xml as a ZIP file and
            unzip the file in the first/top BiblelatorFiles folder (then remove -master from the folder name).
    Either way, you should end up with a new folder called strongs-dictionary-xml
        inside your BiblelatorFiles folder from step #3.


8. Make Biblelator.py executable -- only on Linux.
    Navigate to the 2nd Biblelator folder either in a command line window or a file manager.
        If on a command line, type "chmod +x Biblelator.py" (without the quotes), or
        if in a file manager, right-click on Biblelator.py, choose Properties,
            and Permissions (or similar) and set the Executable flag.


9. Try a test run of the Biblelator program.
    Open a command window and navigate to your second Biblelator folder using the cd command,
        e.g.,   cd /home/fred/Biblelator/Biblelator (a Linux example), or
                cd \Users\Public\Documents\Biblelator\Biblelator (a Windows example).
    On Linux, type ".\Biblelator.py --version" (without the quotes), or
    on Windows, the command is something like:
            "C:\Python34\python.exe Biblelator.py --version" (without the quotes)
        depending on your Python3 version number.
    This test run of the program should just display the Biblelator version number
        and then exit immediately.
    If you see the error "ImportError: No module named tkinter", check in case you are
	accidentally using Python 2 rather than Python 3.
    If the program does not run, please copy the contents of the command window,
        and paste them into the comment box at http://Freely-Given.org/Contact.html.


10. Try starting the Biblelator program in debug mode.
    Using a command similar to what worked in the previous step,
        replace "--version" with "--debug" to actual run the program
            but with extra debugging information displayed in the command window
            so we can more easily track issues if there's an installation program.
    This command should open the Biblelator main window
        (with an extra Debug menu and extra debug information inside the main window).
    Aside from displaying these extras, plus extra debug information displayed in the command window,
        you should be able to access all (working) Biblelator functions as usual.
    The debug mode has a HALT button, which unlike the QUIT button,
        exits immediately without saving any files or settings, so use it with caution.
    If the program does not run, please copy the contents of the command window,
        and paste them into the comment box at http://Freely-Given.org/Contact.html.
    Note that a BiblelatorData folder should be created in your home folder when you exit the program,
        and inside that, a BiblelatorSettings folder should contain your settings information
        and a BiblelatorLogs folder should contain a log file.


11. Run Biblelator in the normal mode for normal working.
    If everything seems to be working correctly,
        next time you run Biblelator you might not need to run it in debug mode,
    i.e., simply omit the "--version" and "--debug" parameters in order to run in normal mode.
    If the program does not run, please copy the contents of the command window,
        and paste them into the comment box at http://Freely-Given.org/Contact.html.
    It may also be helpful to include the contents of the Biblelator.ini file
        which should be in yourNormalHomeFolder/BiblelatorData/BiblelatorSettings/.


12. Eventually (once the program is working fully and reliably) you might like to
    make a desktop or toolbar shortcut to run Biblelator on your system so it can be started easier
    (without having to open a command window and manually navigate to files and folders).
    Meanwhile though, it's probably useful to have the command window open


13. If you wish to access online Scripture resources from the Digital Bible Platform
    (Faith Comes By Hearing FCBH), request further information from the Biblelator programmers via
    http://Freely-Given.org/Contact.html.


14. If you wish to access offline Scripture resources from the Crosswire Sword project,
    you should download and install/unzip the resources from the Crosswire or other repositories.
    You might already have these installed if you use a Sword-based Bible program such as
        Xiphos, Bibletime, BPBible, etc.
    Then you should use http://Freely-Given.org/Contact.html to contact the Biblelator programmers
        and let us know how you installed the Sword modules,
        and which folder they were installed to.
    Then hopefully we can get you started with basic access to these modules.


15. PhotoBible
    If you wish to use the PhotoBible export option for your USFM projects, you need to install
	the free ImageMagick package. For Linux, this can usually be installed from your package
	manager, and for Windows, the exe installation files can be downloaded from
	http://www.imagemagick.org/download/binaries.

16. Program updates
    If you used Git to install Biblelator and/or BibleOrgSys, you should regularly update each
        of them with "git pull" on each folder (or the equivalent command from the GUI if you
        use TortoiseGit or equivalent).
    If you installed Biblelator and/or BibleOrgSys by downloading a zip file from GitHub.com,
        you should regularly update each of them by downloading the latest zip file and
        extracting them into each folder to overwrite existing files. (This won't erase
        renamed or deleted files, but who cares.)


Please see the document GettingStarted.md for help on how the Biblelator resource and project
    windows are designed to work.
