=======
Release
=======

These are the steps needed to release a new version of the package on PyPI.

---------------

.. contents:: **Table of Contents**

Incrementing the Version
========================

The version numbers follow the semantic versioning system, the specifications of which can be found here_.

.. _here: https://semver.org/

The `setup.py` file contains some metadata about the package including the version number which needs to be incremented.

Tag the commit which contains the final version of the code being released.

.. code:: shell

    $ git tag -a v0.1.0 -m "Release Version 0.1.0" a029ac
    $ git push origin --tags

Generating Distribution Archives
================================

Install the latest versions of `setuptools` and `wheel`.

.. code:: shell

    python -m pip install --user --upgrade setuptools wheel

Generate distribution archives.

.. code:: shell

    $ python setup.py sdist bdist_wheel

There should now be two files in the `dist` directory.

Upload the Distribution Archives
================================

Before uploading them to PyPI, first upload them to Test PyPI to ensure that everything has gone as intended.

Install Twine.

.. code:: shell

    $ python -m pip install --user --upgrade twine

Upload all of the archives under `dist` to Test PyPI.

.. code:: shell

    $ python -m twine upload --repository testpypi dist/*

Install the package to test it.

.. code:: shell

    $ python -m pip install --index-url https://test.pypi.org/simple/ --no-deps racketinterpreter
    $ python

.. code:: python

    >>> import racketinterpreter

Upload all of the archives under `dist` to PyPI.

.. code:: shell

    $ python3 -m twine upload dist/*

Sources
=======
[1_]
[2_]
[3_]

.. _1: https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
.. _2: https://packaging.python.org/tutorials/packaging-projects/
.. _3: https://www.freecodecamp.org/news/git-tag-explained-how-to-add-remove/
