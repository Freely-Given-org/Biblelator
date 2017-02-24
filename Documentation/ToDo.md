Biblelator ToDo List
====================

Last updated: 2017-02-22 by RJH


This is an informal list of things that need to be fixed or are planned to be done.

Eventually we will use the issue tracker at Github
    -- actually, you're welcome to list your issues there already.

Things nearer the top of the list are higher in priority
(and due to my situation often only having smallish chunks of time available,
smaller jobs often get done before larger ones unfortunately).

Biblelator bugs / unfinished
* Search/Replace globally didn't show the update in the open USFMEditWindow
* Checking window: can't click on individual errors (for goto)
* Checking window: enable/disable Back/Forward buttons (and display link when cursor over)
* Clicked on an apocryphal book (result of search) and MBT got into sort of a loop "Need to create book" / cancel
* CRITICAL: cacheBook: We have a duplicate Matigsalug Unicode Version GLS_0:419! -- already had '\n' and now appending '\\p \\k ubas\\k* [Ceb. paras, ubas; Eng. grape]\n'
* Editing bridged verse caused it to be added twice!!!
* Bible find can't find/replace space at end of line -- why not? because removed at load time!
* Find in chapter 0 gives wrong verse (only sometimes -- why??? REMs???)
* Ctrl+F doesn't work in edit window or resource for Bible Find
* F1 help and F12 about doesn't seem to work from most windows
* F2 (ShowMainWindow) still doesn't seem to work from a Lexicon window
* Windows and Bible lists need to be displayed in a window
* HTML source box isn't listed in child windows (included in show all / hide all)
* Window find doesn't seem to work on resource windows
* After moving replace box, it still keeps reappearing in the original position
* Remember find/replace lists in settings (for each window/project -- maybe not)
* Remember position of last find box
* Find box can't change projects/windows
* Get extended find box working better -- need to show whole verse somehow (why can't right click or something?)
* Sort out USFM styles for current verse / formatted / unformatted etc.
* Work more on Tools/Options for edit window to set autocomplete mode, etc.
* Make edit window status bar default (if screen is big enough)
* Clicking in edit window while still starting can cause a spinbox error
* Window settings don't work well for text collections, etc. (need to be nested???)
* Bible find needs intro set if book in FRT, GLO, etc.
* Bible find can default to any currently selected text in edit window?
* Bible find can't seem to jump to GLO lines
* Bible replace needs more work on reloading open books/Bibles
* Select entire booknumber/bookname/chapter/verse when the box in main window is clicked on
* Book number spinner needs to check if any window contains that book else skip it
* Need wait status/cursor when opening a DBP resource, doing Bible checks, etc, etc.
* Can't undo USFM Bible edit once moved cursor
* Can't double-click in USFM editor to select a word (but can in text editor)
* Ctrl+V seems to paste double in text edit windows (paste from menu or right-click only does it once)
* Text file open and Biblelator project open dialogs flash for a while and then go smaller
* Seems that Alt up and down do different things if a spinbox or the bookname box is selected
* Make opening a 2nd DBP box inside a resource collection not download everything again
* Having a DBP window open (and slow Internet) slows all verse navigation
* Going up and down repeatedly over a chapter marker (in single verse USFM edit window) is not consistent
* Do more usage logging
* Settings editor is not finished enough
* BOSManager is not finished enough
* SwordManager is not finished enough
* Make wording consistent between DIR and FOLDER
* When using custom sword module path, send it home so we can add it to the defaults???

Biblelator testing required
* Biblelator project edit windows may fail on malformed markers (e.g., space before \v)
* Need to set-up some special .ini files for testing (with every kind of window/box open)
* Systematically work through all menus


BOS bugs
* Sword conf files don't load versioned history lines correctly
* Doesn't know about Sword NRSVA versification yet
* OSIS (and other containerised) formats should insert end markers themselves when loading


BOS improvements for Biblelator
* Start Names checking tool
* Upgrade to USX 2.5
* Are we able to read Sword dictionaries?
* How to stop BibleOrganisation critical errors on Biblelator startup (need to manually cache data files???)
* Fix speech mark / quotation checking
* Fix intro/text section checking
* Fully handle nested USFM markers (USFM 2.4)
* Handle USFM 3.0 (when released)
* Update ESFM spec (when USFM 3 is released)
* Learn to read BCV files
* Expand testing functions
* Refactor code to be more modular
* Increased multiprocessing
* Investigate creating a plug-in structure
* Add check for over-long paragraphs (and sentence length?)
* Write a GUI for Bible search and search/replace ???


BOS testing required
* Can BOS import USFM with all books in one file?
* Lots of errors/warnings reading various USX Bibles
* Had 3 default mode failures: ['TestBDBSubmissions1', 'TestBDBSubmissions2', 'TestHaiola3']


BOSManager / SwordManager / Settings editor stuff
* Make Bible fields in BOSManager into clickable links (to go to other tabs)
* Work on final three tabs in BOSManager
* Get SwordManager working to list/install/update modules
* Allow settings manager to edit other settings files
* Get apply/ok/cancel working


Biblelator stuff
* Add AND and OR for Bible find
* Add a pop-up quick reference box (with all open translations???)
* Make HTML window more robust (failed if meta line was missing self-closing slash)
* Allow a long press on verse back/forward buttons (Do we need separate lists for each group code?)
* Make a way for the program or installer to automatically download reference Bibles and other resources
* USFM editor still only aware of basic/common USFM tags
* Make Biblelator use Paratext autocorrect files for Paratext projects
* Make a proper icon
* Save iconification state of windows
* Use checkboxes to allow individual exports
* Get Sword resources displaying nicer
* Check if a recreated (at startup or settings change) window in on the/a screen (and if not move it on)
* Cache DBP to disk (if have expensive Internet)???
* Need keyboard shortcuts for list up/down
* Biblelator project USFMEditWindow can't set project name correctly coz no settings loaded yet
* Paste doesn't replace the selection
* Remove double-spaces at either end of a paste
* Need to remove autocorrect settings from code and put into files (with an editor???)
* Prevent autocomplete if editing in the middle of a word -- maybe make this an option
* Display toolbox dictionary???
* Allow windows to lock together (e.g., two or more project edit windows)
* Send BCV updates from HTML window
* Allow a very simple edit mode (for users who find USFM way too complex)
* Send verse links to Paratext
* Fix flashing SSF open window for Open / Paratext project
* Don't allow two projects with the same name
* Optional hints at start-up
* Pop up a select box if previous/next buttons are held down
* Up/down verse over chapters isn't working -- also up/down chapter (to one with less verses)
* Add debug menu to edit windows to display settings/log
* Get some different views working on the edit window
* Synchronise with other Bible programs (esp. on Windows)
* Display footnotes and xrefs in resources
* Work on user stylesheets
* Make a full project properties dialog and do project setting properly
* Add "Recent" entries to the main menus
* Allow the user to set the containing folder for projects and exports
* Release version 0.40
* Include some sample folders and sample ini files
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
* Make a splash screen (turned off/on in settings file)
* Release version 0.50
* Allow users to "log-on" with usernames (passwords?)
* Allow setting of roles (administrator/project leader/superintendent/overseer, translator, consultant/reviewer/archivist/typesetter, contributor/friend/critic/observer)
* Make logging more useful
* Project sharing (Hg vs Git) -- requires server set-up
* Allow user to show history of changes per verse (and per chapter???)
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
* From a Bible edit window, have a menu item to view the current chapter/section typeset on a page (pop-up window)
* Improve the about page(s)
* Turn chapter/verse spin buttons 90 degrees (maybe)
* Learn how to install Biblelator on OS X
* Create back-translation windows with special features
* Allow more settings to be edited within the program (full settings editor)
* Allow the short-cut keys to be edited within the program
* Get full multiprocessing working
* Make autocompletion aware of previous work and so adjust for context
* Add progress bars for slow tasks
* Add tooltips
* Make proper user-adjustable (by dragging) toolbar(s)
* Create an intelligent installer (also investigate Snap packaging)
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


Jobs for others
* Work on lists (Bible people, animals, birds, vegetation, etc., etc.)
