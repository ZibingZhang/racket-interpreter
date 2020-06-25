# Racket Interpreter

An interpreter written for Racket, more specifically the student languages which are (almost) a subset of the language.
These student languages are what first-semester, computer-science students at Northeastern learn to program in.
The end goal of this project is to successfully interpret the code I wrote for a homework assignment regarding graphs.

[![PyPI version](https://badge.fury.io/py/racketinterpreter.svg)](https://badge.fury.io/py/racketinterpreter)
[![Build Status](https://travis-ci.org/ZibingZhang/racket-interpreter.svg?branch=master)](https://travis-ci.org/ZibingZhang/racket-interpreter)
<img src="https://img.shields.io/badge/license-MIT-brightgreen"></img>
<img src="https://img.shields.io/badge/python-3.7%2B-blue"></img>

## Table of Contents

  * [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installing & Running](#installing--running)
  * [Licence](#licence)
  * [Acknowledgments](#acknowledgments)
  * [Documentation](#documentation)

## Getting Started

There is no IDE nor does the interpreter read from a text file... yet.
That being said, here are the steps to set up and get the interpreter running.

### Prerequisites

The only prerequisite is to have Python 3.7+.

### Installing & Running

Clone the repository locally and execute the source module as a script.
```
git clone https://github.com/ZibingZhang/racket-interpreter.git
cd racket-interpreter
python racketinterpreter/__init__.py
```

To change the code that is being interpreted, change the value of `text` in `racketinterpreter/__init__.py`.

### Testing

```
python -m unittest
```

## Licence

This project is licensed under the MIT license.

## Acknowledgments

This initially started as an adaptation of Ruslan Spivak's [tutorial](https://ruslanspivak.com/lsbasi-part1/) for writing an interpreter.
Most of the structure of this codebase come from the tutorial, but as I've begun to understand his design decisions better I've been able to change and adapt them to fit this project.
This [template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) has also been helpful in understanding how to format a README and what I should include.

## Documentation

I've decided to keep the documentation in the same README for the time being.
