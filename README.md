# Racket Interpreter

An interpreter written for Racket, more specifically the student languages which are (almost) a subset of the language.
These student languages are what first-semester, computer-science students at Northeastern learn to program in.
The end goal of this project is to successfully interpret the code I wrote for a homework assignment regarding graphs.

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
python -m src
```

## Licence

This project is licensed under the MIT license.

## Acknowledgments

This initially started as an adaptation of Ruslan Spivak's [tutorial](https://ruslanspivak.com/lsbasi-part1/) for writing an interpreter.
Most of the structure of this codebase come from the tutorial, but as I've begun to understand his design decisions better I've been able to change and adapt them to fit this project.
This [template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) has also been helpful in understanding how to format a README and what I should include.
