Biblelator Notes for Programmers
================================

Last updated: 2016-06-15 RJH


I won't repeat what's in the other documentation files here. You should certainly study these
others first:
    * Installation.md
    * GettingStarted.md
    * DevelopmentPrinciples.md
    * ToDo.md


1. GitHub

    Since Biblelator (and the Bible Organisational System: BibleOrgSys) are open-source (GPL-3)
    programs, GitHub was considered a good place to host them.

    Since the OpenScriptures group was already working towards making high-quality Bible source
    texts available, this software seemed compatible with their aims and so it's been placed
    under the OpenScriptures project.

    There is currently a master branch, with various alpha releases tagged, and a development
    branch where work-in-process is being uploaded for the keenest testers to try.


2. Coding style

    You might quickly notice that we don't use that "standard" Python coding style. Hackability
    is a major aim, and I feel that my style is more readable, despite the "costs" of being
    non-standard. You're welcome to disagree, but it's my project. I won't accept patches that
    simply alter the style of the code.

    Also, generally if there's a choice of using a short variable name, e.g., wi, we prefer
    going to the extra effort to call it wordIndex. It's a strong aim to try to make the code
    as readable as reasonably possible to a novice or even non-programmer. This also means
    that readable code is preferred over very clever code, unless there's a major efficiency
    advantage.


3. Comments

    In line with #2 above, I try hard to comment blocks of code, as well as any lines that
    might not be immediately intuitive. (Admittedly, sometimes I do do the commenting when
    I go back over my code and can't figure out myself exactly what it's doing.) But again,
    to make it hackable, I try to make the code as understandable as possible.


4. Quote marks

    I tend to try to use double quotes for strings which is text, e.g., "Too many words."
    Text which should be translated is also fed through the gettext function like this:
        _("Too many words.")
    I try to use single quotes for program strings which are not presented to the user,
        e.g., lastPressed = 'EnterKey'
    I use sets of three double quotes for function and class documentation strings,
        e.g., """This function does this and that."""


5. Algorithmic efficiency

    Don't mock the inefficiency (either execution time or memory use) of any of my code. This
    is definitely prototype code -- everything so far has been written to get it working as
    quickly as possible. There's been absolutely no attempt to refactor or increase efficiency,
    and I don't plan to even consider this until AFTER the release of v1.0. That's not to say
    that patches from others to improve efficiency won't be accepted. But for me, NEW FEATURES
    are currently my priority, followed by removing bugs. Further automated testing will be
    next, following by packaging for distribution, and then restructuring and efficiency
    improvements are last.


Robert Hunt.
Biblelator developer.