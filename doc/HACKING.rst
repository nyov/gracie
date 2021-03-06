=================
Developer's guide
=================

:Author: Ben Finney <ben+python@benfinney.id.au>
:Updated: 2009-12-27

Project layout
==============

::

    ./                  Top level of source tree
        doc/            Project documentation
        bin/            Executable programs
            gracied     Main program daemon
        gracie/         Gracie library code
        test/           Unit tests

Code style
==========

Python
------

All Python code should conform to the guidelines in PEP8_. In
particular:

* Indent each level using 4 spaces (``U+0020 SPACE``), and no TABs
  (``U+0008 CHARACTER TABULATION``).

* Name modules in lower case, ``multiplewordslikethis``.

* Name classes in title case, ``MultipleWordsLikeThis``.

* Name functions, instances and other variables in lower case,
  ``multiple_words_like_this``.

* Every module, class, and function has a Python doc string.

* Doc strings are written as triple-quoted strings.

  * The first line is a one-line summary of the object. This summary
    line appears on the same line as the opening triple-quote,
    separated by a single space.
  
  * Further lines, if needed, are separated from the first by one
    blank line.

  * The closing triple-quote appears on a separate line.

  Example::

    def frobnicate(spam):
        """ Perform frobnication on ``spam``.

            The frobnication is done by the Dietzel-Venkman algorithm,
            and optimises for the case where ``spam`` is freebled and
            agglutinative.

            """
        spagnify(spam)
        # …

* All ``import`` statements appear at the top of the module.

* Each ``import`` statement imports a single module, or multiple names
  from a single module.

  Example::

    import sys
    import os
    from spam import foo, bar, baz

..  _PEP8: http://www.python.org/dev/peps/pep-0008/

Additional style guidelines:

* A page break (``U+000C FORM FEED``) whitespace character is used
  within a module to break up semantically separate areas of the
  module.

Unit tests
==========

All code should aim for 100% coverage by unit tests. New code, or
changes to existing code, will only be considered for inclusion in the
development tree when accompanied by corresponding additions or
changes to the unit tests.

Test-driven development
-----------------------

Where possible, practice test-driven development to implement program
code.

* During a development session, maintain a separate window or terminal
  with the unit test suite for the project running continuously, or
  automatically every few seconds.

* Any time a test is failing, the only valid change is to make all
  tests pass.

* Develop new interface features (changes to the program unit's
  behaviour) only when all current tests pass.

* Refactor as needed, but only when all tests pass.

  * Refactoring is any change to the code which does not alter its
    interface or expected behaviour, such as performance
    optimisations, readability improvements, modularisation
    improvements etc.

* Develop new or changed program behaviour by:

  * *First* write a single, specific test case for that new behaviour,
    then watch the test fail in the absence of the desired behaviour.

  * Implement the minimum necessary change to satisfy the failing
    test. Continue until all tests pass again, then stop making
    functional changes.

  * Once all tests (including the new test) pass, consider refactoring
    the code and the tests immediately, then ensure all the tests pass
    again after any changes.

  * Iterate for each incremental change in interface or behaviour.

Test-driven development is not absolutely necessary, but is the
simplest, most direct way to generate the kind of program changes
accompanied by unit tests that are necessary for inclusion in the
project.


..
    Local variables:
    coding: utf-8
    mode: rst
    time-stamp-format: "%:y-%02m-%02d"
    time-stamp-start: "^:Updated:[ 	]+"
    time-stamp-end: "$"
    time-stamp-line-limit: 20
    End:
    vim: fileencoding=utf-8 filetype=rst :
