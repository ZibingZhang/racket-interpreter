from __future__ import annotations
import fractions as f
from typing import TYPE_CHECKING, List
import unittest
from src import constants
from src.datatype import Boolean, InexactNumber, Integer, Procedure, Rational, String
from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser

if TYPE_CHECKING:
    from src.datatype import DataType


class TestInterpreter(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        constants.init(should_log_scope=False, should_log_stack=False)

    def interpret_text(self, text: str, expected: List[DataType]) -> None:
        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        interpreter = Interpreter(tree)
        result = interpreter.interpret()

        for output, expected in zip(result, expected):
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
            '''
        expected = [
            Integer(123),
            Integer(1),
            Integer(-987),
            Rational(f.Fraction(1, 2)),
            Integer(-2)
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

    def test_scope(self) -> None:
        text = \
            '''
                (define (s t z) (- t 6))
                (define (t u s) (u s 1))
                (t s 6)
            '''
        expected = [
            Integer(0)
        ]
        self.interpret_text(text, expected)

    def test_recursion(self) -> None:
        text = \
            '''
                (define (factorial n)
                (if (= n 0)
                    1
                    (* n (factorial (- n 1)))))
                (factorial 10)
            '''
        expected = [
            Integer(3628800)
        ]
        self.interpret_text(text, expected)

    def test_builtin_procs(self) -> None:
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

        text = \
            '''
                (add1 (- (/ 3 2)))
                (add1 2)
            '''
        expected = [
            Rational(f.Fraction(-1, 2)),
            Integer(3)
        ]
        self.interpret_text(text, expected)

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


if __name__ == '__main__':
    unittest.main()
