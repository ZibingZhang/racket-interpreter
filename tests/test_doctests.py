import doctest
import unittest
from racketinterpreter.classes import data
from racketinterpreter.classes import tokens

suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite(data))
suite.addTest(doctest.DocTestSuite(tokens))
runner = unittest.TextTestRunner()
result = runner.run(suite)
