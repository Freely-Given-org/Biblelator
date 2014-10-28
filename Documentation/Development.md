Biblelator Development Principles
=================================

The following are some of the reasons behind some of the major development decisions
    concerning the development of Biblelator.


1. Python as the language

    Python is not as fast and efficient as C or C++, but it is nevertheless an elegant, well-designed
    computer language that runs quite efficiently on most modern computer hardware.

    Another reason for choosing Python is that the source code to the software is usually provided
    and that it can be easier to read by novices than some other computer languages. This is
    important to us, because Biblelator is designed to be hackable, i.e., a creator or translator
    of the Bible might have a chance of making a small change to the program in order to handle
    a specific need that he/she might have (or if not, to hire someone else to make the change).


2. Python3 versus Python2

    Python3 was already in development when the Bible Organisational System (BibleOrgSys)
    that Biblelator depends on was being prototyped. It was already obvious then that Python2
    would eventually stop being developed, and so there didn't seem to be any point in
    creating a new piece of software based on a language version already destined to be obsoleted.


3. TKinter as the widget set

    TKinter is not the most beautiful or advanced widget set, but it is an intrinsic part
    of regular Python distributions. So it was chosen for its universality rather than
    trying to choose one of quite a number of competing toolkits (e.g., QT, wxWidgets, etc.)


4. Prototype implementation

    All of the existing code is considered as "prototype/proof-of-concept", i.e., it has not
    been optimised for speed and software simplicity (refactoring), but rather to get the
    program working. After version one is released, only then will time and resources be
    spent on getting it working more efficiently.