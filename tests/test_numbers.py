import unittest
from racketinterpreter.classes.data import InexactNum, Integer, RationalNum
from tests import util


class TestNumbers(unittest.TestCase):

    def test_number(self):
        text = '''
            123
            01
            -987
            1/2
            -2/1
            000.100
            -.05
            -.0
            .0
            .01
        '''
        expected = [
            Integer(123),
            Integer(1),
            Integer(-987),
            RationalNum(1, 2),
            Integer(-2),
            InexactNum(0.1),
            InexactNum(-0.05),
            InexactNum(0.0),
            InexactNum(0.0),
            InexactNum(0.01)
        ]
        util.interpret_text(self, text, expected)

    def test_builtin_add1(self):
        text = '''
            (add1 (- (/ 3 2)))
            (add1 2)
        '''
        expected = [
            RationalNum(-1, 2),
            Integer(3)
        ]
        util.interpret_text(self, text, expected)

    def test_builtin_sym_multiply(self):
        text = '''
            (*)
            (* 2)
            (* 1/2 5/3)
            (* 1/2 9 3)
            (* 3/2 2/3)
            (* 1. 0)
        '''
        expected = [
            Integer(1),
            Integer(2),
            RationalNum(5, 6),
            RationalNum(27, 2),
            Integer(1),
            Integer(0),
        ]
        util.interpret_text(self, text, expected)

    def test_builtin_sym_plus(self):
        text = '''
            (+)
            (+ 1)
            (+ 1 1/2)
            (+ 1/2 1)
            (+ 5/7 3/9)
            (+ 5/7 3/9 -1/22 0.)
            (+ 1/2 1/2)
        '''
        expected = [
            Integer(0),
            Integer(1),
            RationalNum(3, 2),
            RationalNum(3, 2),
            RationalNum(66, 63),
            InexactNum(1),
            Integer(1)
        ]
        util.interpret_text(self, text, expected)

    def test_builtin_sym_minus(self):
        text = '''
            (- 1)
            (- 1 1/2)
            (- 1/2 1)
            (- 5/7 3/9)
            (- 3. 2)
            (- 3/2 1/2)
        '''
        expected = [
            Integer(-1),
            RationalNum(1, 2),
            RationalNum(-1, 2),
            RationalNum(24, 63),
            InexactNum(1),
            Integer(1)
        ]
        util.interpret_text(self, text, expected)

    def test_builtin_sym_divide(self):
        text = '''
            (/ 1)
            (/ 2)
            (/ 1.)
            (/ 1/2 1/2)
            (/ 1/2 1/4 2)
            (/ 1/2 1/4 2.)
        '''
        expected = [
            Integer(1),
            RationalNum(1, 2),
            InexactNum(1.0),
            Integer(1),
            Integer(1),
            InexactNum(1.0)
        ]
        util.interpret_text(self, text, expected)
