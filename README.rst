==================
Racket Interpreter
==================
An interpreter written for Racket, more specifically the student languages which are (almost) a subset of the language.
These student languages are what first-semester, computer-science students at Northeastern learn to program in.
The end goal of this project is to successfully interpret the code I wrote for a homework assignment regarding graphs.

|build status| |codecov| |PyPI version| |license| |version|

.. |build status| image:: https://travis-ci.org/ZibingZhang/racket-interpreter.svg?branch=master
        :target: https://travis-ci.org/ZibingZhang/racket-interpreter
.. |codecov| image:: https://codecov.io/gh/zibingzhang/racket-interpreter/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/zibingzhang/racket-interpreter
.. |PyPI version| image:: https://badge.fury.io/py/racketinterpreter.svg
        :target: https://badge.fury.io/py/racketinterpreter
.. |license| image:: https://img.shields.io/pypi/l/racketinterpreter?color=orange
        :target: https://github.com/ZibingZhang/racket-interpreter/blob/master/LICENSE
.. |version| image:: https://img.shields.io/badge/python-3.8-blue
        :target: https://www.python.org/downloads/release/python-380/

--------------------

.. contents:: **Table of Contents**

Getting Started
===============
There is no IDE nor does the interpreter read from a text file... yet.
That being said, here are the steps to set up and get the interpreter running.

Prerequisites
~~~~~~~~~~~~~
The only prerequisite is to have Python 3.8+.
The tests are only run on Python 3.8, but there is no reason to believe that they would not pass on more recent versions.

Installing
~~~~~~~~~~
The package can be installed using pip.

.. code:: shell

    $ pip install racketinterpreter


*Try interpreting some Racket code*

.. code:: shell

    $ python

.. code:: python

    >>> import racketinterpreter
    >>> result = racketinterpreter.interpret('(define x 1) x')
    >>> print(result.output)
    ['1']

--------------------

Contributing
===============

Downloading
~~~~~~~~~~~
Clone the repository locally.

.. code:: shell

    $ git clone https://github.com/ZibingZhang/racket-interpreter.git

There is an example of the interpreter in the ``example.py`` file which can be run.

.. code:: shell

    $ python example.py

To change the code that is being interpreted, change the value of ``code``.

Generating the Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These are the steps to transpile the documentation to an easily readable HTML format.

.. code:: shell

    $ pip install -u sphinx
    $ pip install -u sphinx-rtd-theme
    $ sphinx-apidoc -eo apidoc/ racketinterpreter/ --templatedir docs/templates
    $ make html

The homepage for the documentation can be found at ``_build/html/index.html``.

If the documention needs to be regenerated for any reason, some directories need to be deleted first.

.. code:: shell

    $ rm -r _build
    $ rm -r apidoc
    $ sphinx-apidoc -eo apidoc/ racketinterpreter/ --templatedir docs/templates
    $ make html

Running the Example
~~~~~~~~~~~~~~~~~~~
There is an example of using the interpreter in ``example.py`` which can be run with the following command.

.. code:: shell

  $ python example.py

Testing
~~~~~~~
At the moment there are only unit tests.

All the tests can be run at once,

.. code:: shell

    $ python -m unittest

or file by file.

.. code:: shell

  $ python -m unittest tests/test_errors.py

--------------------

Licence
=======
This project is licensed under the MIT license.

--------------------

Acknowledgments
===============
This initially started as an adaptation of Ruslan Spivak's tutorial_ for writing an interpreter.
Most of the structure of this codebase come from the tutorial, but as I've begun to understand his design decisions better I've been able to change and adapt them to fit this project.
This template_ has also been helpful in understanding how to format a README and what I should include.

.. _tutorial: https://ruslanspivak.com/lsbasi-part1/
.. _template: https://gist.github.com/PurpleBooth/109311bb0361f32d87a2
