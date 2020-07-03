from __future__ import annotations
from typing import TYPE_CHECKING, List
import unittest
from racketinterpreter.classes.data import (
    Boolean, ConsList, InexactNumber, Integer, Procedure, Rational, String, Symbol
)
from racketinterpreter.util import Util

if TYPE_CHECKING:
    from racketinterpreter.classes.data import Data


class TestInterpreter(unittest.TestCase):

    def interpret_text(self, text: str, expected: List[Data]):
        output, _ = Util.text_to_interpreter_result(text)

        output_len = len(output)
        expected_len = len(expected)
        self.assertEqual(output_len, expected_len)

        for actual_data, expected_data in zip(output, expected):
            self.assertEqual(type(actual_data), type(expected_data))
            if issubclass(type(expected_data), InexactNumber):
                self.assertTrue(abs(actual_data.value - expected_data.value) < 0.01)
            else:
                self.assertEqual(actual_data, expected_data)

    def test_boolean(self):
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

    def test_cons_list(self):
        text = \
            '''
                empty
                (cons 1 empty)
                (cons 1 (cons 2 (cons 3 empty)))
            '''
        expected = [
            ConsList([]),
            ConsList([Integer(1)]),
            ConsList([Integer(1), Integer(2), Integer(3)])
        ]
        self.interpret_text(text, expected)

    def test_number(self):
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

    def test_number_order(self):
        text = \
            '''
                (< 2 2) (> 2 2) (<= 2 2) (>= 2 2) (= 2 2)
                (< 1 2) (> 1 2) (<= 1 2) (>= 1 2) (= 1 2)
                (= 1 1. 1/1 3/3 1.0)
                (= 0 0. 0.0 -0 -0. -.0 -0.0 .0 0/1)
            '''
        expected = [
            Boolean(False), Boolean(False), Boolean(True), Boolean(True), Boolean(True),
            Boolean(True), Boolean(False), Boolean(True), Boolean(False), Boolean(False),
            Boolean(True),
            Boolean(True)
        ]
        self.interpret_text(text, expected)

    def test_procedure(self):
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

    def test_string(self):
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

    def test_struct(self):
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

    def test_symbol(self):
        text = \
            '''
                'a
                'longer-symbol
                '"this is a string"
                '#true
            '''
        expected = [
            Symbol("'a"),
            Symbol("'longer-symbol"),
            String('this is a string'),
            Boolean(True)
        ]
        self.interpret_text(text, expected)

    def test_scope(self):
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

    def test_recursion(self):
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

    def test_builtin_if(self):
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

    def test_builtin_add1(self):
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

    def test_builtin_and(self):
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

    def test_builtin_symbol_plus(self):
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

    def test_builtin_symbol_minus(self):
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

    def test_builtin_symbol_multiply(self):
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

    def test_builtin_symbol_division(self):
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
