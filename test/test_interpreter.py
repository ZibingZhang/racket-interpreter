from __future__ import annotations
from typing import TYPE_CHECKING, List
import unittest
from src import constants
from src.data import Boolean, InexactNumber, Integer, Procedure, Rational, String
from src.util import Util

if TYPE_CHECKING:
    from src.data import Data


class TestInterpreter(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        constants.init(should_log_scope=False, should_log_stack=False)

    def interpret_text(self, text: str, expected: List[Data]) -> None:
        result = Util.text_to_result(text)

        result_len = len(result)
        expected_len = len(expected)
        self.assertEqual(result_len, expected_len)

        for output, expected in zip(result, expected):
            self.assertEqual(type(output), type(expected))
            if issubclass(type(expected), InexactNumber):
                self.assertTrue(abs(output.value - expected.value) < 0.01)
            else:
                self.assertEqual(output, expected)

    def test_boolean(self) -> None:
        text = \
            '''
                #true
                #T
                #t
                #false
                #F
                #f
            '''
        expected = [
            Boolean(True),
            Boolean(True),
            Boolean(True),
            Boolean(False),
            Boolean(False),
            Boolean(False)
        ]
        self.interpret_text(text, expected)

    def test_number(self) -> None:
        text = \
            '''
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
            Rational(1, 2),
            Integer(-2),
            InexactNumber(0.1),
            InexactNumber(-0.05),
            InexactNumber(0.0),
            InexactNumber(0.0),
            InexactNumber(0.01)
        ]
        self.interpret_text(text, expected)

    def test_procedure(self) -> None:
        text = \
            '''
                +
                add1
                
                (define (f n) n)
                f
            '''
        expected = [
            Procedure('+'),
            Procedure('add1'),
            Procedure('f')
        ]
        self.interpret_text(text, expected)

    def test_string(self) -> None:
        text = \
            '''
                ""
                "Hello World"
                "#True"
                "3"
                "'"
            '''
        expected = [
            String(''),
            String('Hello World'),
            String('#True'),
            String('3'),
            String("'")
        ]
        self.interpret_text(text, expected)

    def test_struct(self) -> None:
        # since structs dynamically generate classes,
        # haven't thought of a good way to test some of the functionality of structs
        text = \
            '''
                (define-struct s [a b c])
                (define s0 (make-s .3 "Jeff" #T))
                
                (s? 1)
                (s? "a")
                (s? #f)
                (s? s0)
                
                (s-a s0)
                (s-b s0)
                (s-c s0)
                
                (define a-selector s-a)
                (a-selector s0)
            '''
        expected = [
            Boolean(False),
            Boolean(False),
            Boolean(False),
            Boolean(True),
            InexactNumber(0.3),
            String('Jeff'),
            Boolean(True),
            InexactNumber(0.3)
        ]
        self.interpret_text(text, expected)

    def test_scope(self) -> None:
        text = \
            '''
                (define (s t z) (- t 6))
                (define (t u s) (u s 1))
                (t s 6)
                (t * 6)
            '''
        expected = [
            Integer(0),
            Integer(6)
        ]
        self.interpret_text(text, expected)

        text = \
            '''
                (define a +)
                (define b a)
                (define c b)
                (b 1 2)
            '''
        expected = [
            Integer(3)
        ]
        self.interpret_text(text, expected)

    def test_recursion(self) -> None:
        text = \
            '''
                (define (factorial n)
                    (if (= n 0)
                        1
                        (* n (factorial (- n 1)))))
                (factorial 0)
                (factorial 10)
            '''
        expected = [
            Integer(1),
            Integer(3628800)
        ]
        self.interpret_text(text, expected)

        text = \
            '''
                (define (fibonacci-acc n i n2 n1)
                    (if (= n i) (+ n1 n2)
                        (fibonacci-acc n (add1 i) n1 (+ n1 n2))))
                (define (fibonacci n)
                    (cond [(= n 0) 0]
                          [(= n 1) 1]
                          [else (fibonacci-acc n 2 0 1)]))
                
                (fibonacci 0)
                (fibonacci 1)
                (fibonacci 2)
                (fibonacci 3)
                (fibonacci 4)
                ; (fibonacci 121)
            '''
        expected = [
            Integer(0),
            Integer(1),
            Integer(1),
            Integer(2),
            Integer(3),
            # Integer(8670007398507948658051921)
        ]
        self.interpret_text(text, expected)

    def test_builtin_if(self) -> None:
        text = \
            '''
                (if #t 1 2)
                (if #f 1 2)
            '''
        expected = [
            Integer(1),
            Integer(2)
        ]
        self.interpret_text(text, expected)

    def test_builtin_add1(self) -> None:
        text = \
            '''
                (add1 (- (/ 3 2)))
                (add1 2)
            '''
        expected = [
            Rational(-1, 2),
            Integer(3)
        ]
        self.interpret_text(text, expected)

    def test_builtin_and(self) -> None:
        text = \
            '''
                (and)
                (and #f)
                (and #t)
                (and #t #t #t)
                (and #t #f #t)
            '''
        expected = [
            Boolean(True),
            Boolean(False),
            Boolean(True),
            Boolean(True),
            Boolean(False)
        ]
        self.interpret_text(text, expected)

    def test_builtin_symbol_plus(self) -> None:
        text = \
            '''
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
            Rational(3, 2),
            Rational(3, 2),
            Rational(66, 63),
            InexactNumber(1),
            Integer(1)
        ]
        self.interpret_text(text, expected)

    def test_builtin_symbol_minus(self) -> None:
        text = \
            '''
                (- 1)
                (- 1 1/2)
                (- 1/2 1)
                (- 5/7 3/9)
                (- 3. 2)
                (- 3/2 1/2)
            '''
        expected = [
            Integer(-1),
            Rational(1, 2),
            Rational(-1, 2),
            Rational(24, 63),
            InexactNumber(1),
            Integer(1)
        ]
        self.interpret_text(text, expected)

    def test_builtin_symbol_multiply(self) -> None:
        text = \
            '''
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
            Rational(5, 6),
            Rational(27, 2),
            Integer(1),
            Integer(0),
        ]
        self.interpret_text(text, expected)

    def test_builtin_symbol_division(self) -> None:
        text = \
            '''
                (/ 1)
                (/ 2)
                (/ 1.)
                (/ 1/2 1/2)
                (/ 1/2 1/4 2)
                (/ 1/2 1/4 2.)
            '''
        expected = [
            Integer(1),
            Rational(1, 2),
            InexactNumber(1.0),
            Integer(1),
            Integer(1),
            InexactNumber(1.0)
        ]
        self.interpret_text(text, expected)


if __name__ == '__main__':
    unittest.main()
