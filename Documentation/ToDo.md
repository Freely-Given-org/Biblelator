Biblelator ToDo List
====================

Last updated: 2016-04-11 RJH


This is an informal list of things that need to be fixed or are planned to be done.

Eventually we will use the issue tracker at Github
    -- actually, you're welcome to list your issues there already.

Things nearer the top of the list are higher in priority
(and due to my situation often only having smallish chunks of time available,
smaller jobs often get done before larger ones unfortunately).

Biblelator bugs
* Need wait status/cursor when opening a DBP resource
* When stepping through verses, cursor needs to be more intelligent (seems to want to stay at current character point)
* Info box for resource windows doesn't show file name and path
* Lexicon key isn't reloaded into main window at startup
* Pressing DEL at autocomplete box inserts some weird character
* \p at end of verse really belongs with next verse
* Ask for a path for Sword modules if none found by automatic search
* Can't undo USFM Bible edit once moved cursor
* Can't double-click in USFM editor to select a word (but can in text editor)
* Ctrl+V seems to paste double in text edit windows (paste from menu only does it once)
* Text file open and Biblelator project open dialogs flash for a while and then go smaller
* Seems that Alt up and down do different things if a spinbox or the bookname box is selected
* Prevent autocomplete if editing in the middle of a word ???
* Make opening a 2nd DBP box inside a resource collection not download everything again
* Having a DBP window open (and slow Internet) slows all verse navigation
* Remove leading zeroes off Strongs numbers (e.g., G0123) if they're not found in lexicon

Bibelator testing required
* Systematically work through all menus


BOS bugs
* Why do we get some (USX) context displays like: c, s1, p, c, s1, c, s1, c, s1, c, s1, c, s1, c, s1, p
* OSIS (and other containerised) formats should insert end markers when loading

BOS improvements for Biblelator
* How to stop BibleOrganisation critical errors on Biblelator startup (need to manually cache data files???)
* Make SwordModules for Windows able to load individual books not just entire Bibles (started)
* Fix speech mark / quotation checking
* Fix intro/text section checking
* Fully handle nested USFM markers (USFM 2.4)
* Handle USFM 3.0 (when released)
* Update ESFM spec (when USFM 3 is released)
* Learn to read BCV files
* Expand testing functions
* Refactor to be more modular
* Increased multiprocessing
* Investigate plug-ins
* Add check for over-long paragraphs (and sentence length?)

BOS testing required
* Test on more MyBible modules


Biblelator stuff
* Add Internet fast/slow, expensive/cheap flags
* Make Biblelator use Paratext autocorrect files for Paratext projects
* Need a global search/replace (for chapter, book, allBooks, etc.) Alt+S ???
* Make a proper icon
* Make bridged versed show for EACH of those verse numbers
* Save iconification state of windows
* Get Sword resources displaying nicer
* Investigate tix widgets
* Cache DBP to disk (if have expensive Internet)???
* Need keyboard shortcuts for verse up/down
* Biblelator project USFMEditWindow can't set project name correctly coz no settings loaded yet
* Paste doesn't replace the selection
* Remove double-spaces at either end of a paste
* Need to remove autocorrect settings from code and put into files (with an editor???)
* Need spin buttons on bookname box
* Display toolbox dictionary???
* Allow windows to lock together (e.g., two or more project edit windows)
* Send BCV updates from HTML window
* Send verse links to Paratext
* Fix flashing SSF open window for Open / Paratext project
* Don't allow two projects with the same name
* Up/down verse over chapters isn't working -- also up/down chapter (to one with less verses)
* Add debug menu to edit windows to display settings/log
* Get some different views working on the edit window
* Synchronise with other Bible programs (esp. on Windows)
* Display footnotes and xrefs in resources
* Work on user stylesheets
* Make a full project properties dialog and do project setting properly
* Add "Recent" entries to the main menus
* Allow the user to set the containing folder for projects and exports
* Release version 0.4
* Setting max window sizes prevents maximizing -- is this what we really want?
* Consider when the same project/file is opened multiple times
* Consider/optimize toolbars in child windows (and/or hiding the menu)
* Handle multiple overlapping tags in the HTML window
* Add "Display by Section" for Bibles that have section headings
    Does that mean we have previous/next section navigation also?
* Design the default short-cut keys for verse/chapter navigation
* Work with someone as a test user
* Work out how the help system will work and start implementing some content
* Improve Sword module display (Bibles and Commentaries)
* Improve Strongs (lexicon) HTML display
* Look at doing some windows updates in idle time
* Design an icon
* Release version 0.5
* Allow users to "log-on" with usernames (passwords?)
* Allow setting of roles (administrator/project leader/superintendent/overseer, translator, consultant/reviewer/archivist/typesetter, contributor/friend/critic/observer)
* Make logging more useful (including ability to automatically email latest log???)
* Project sharing (Hg vs Git) -- requires server set-up
* Write autocompletion settings load/edit routines
* Allow autocomplete to use: Bible or Bible book, current text file, only spell-checked words, external dictionary for language, external file, etc.
* Write spell-checking routines
* Write syntax colouring routines
* Project backup to the cloud (secure Freely-Given.org server)
* Handle automatic (background) USFM syntax checking
* Allow handling of non-English DBP resources
* Think more about use of colour for distinguishing windows
* Think more about window arranging
* Make multiple Bible lexicon windows use the same (loaded) lexicon
* Handle interlinear display (for original language resources)
* Investigate integrating more online resources
* Improve the about page(s)
* Turn chapter/verse spin buttons 90 degrees
* Learn how to install Biblelator on OS X
* Create back-translation windows with special features
* Allow more settings to be edited within the program (full settings editor)
* Allow the short-cut keys to be edited within the program
* Get full multiprocessing working
* Make autocompletion aware of previous work and so adjust for context
* Add progress bars for slow tasks
* Add tooltips
* Create an intelligent installer
* Allow for secure automatic program updates (choice of stable and development branches)
* Work on automated GUI testing
* Release version 1.0 (BibleOrgSys versification systems have to be working first)
* Handle team / collaborative issues
* Think more about fonts and writing systems, special Unicode characters, etc.
* Make checklists including all original verses containing numbers/people's names/locations/flora/fauna, etc.
* Handle hyphenation
* Handle draft printing / typesetting
* Get it usable as a ESFM Bible editor
* Work on scripting/macro language
* Do NT/OT reference mode (Groups A/B work together)
* Do synoptic gospel mode (Groups A/B/C/D work together)
* Make a child window mode (all windows stay within the main window)
