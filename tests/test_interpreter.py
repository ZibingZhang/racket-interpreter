import unittest
from racketinterpreter.classes.data import Boolean, List, InexactNum, Integer, Procedure, String, Symbol
from tests import util


class TestInterpreter(unittest.TestCase):

    def test_boolean(self):
        text = '''
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
        util.interpret_text(self, text, expected)

    def test_list(self):
        text = '''
            empty
            (cons 1 empty)
            (cons 1 (cons 2 (cons 3 empty)))
        '''
        expected = [
            List([]),
            List([Integer(1)]),
            List([Integer(1), Integer(2), Integer(3)])
        ]
        util.interpret_text(self, text, expected)

    def test_procedure(self):
        text = '''
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
        util.interpret_text(self, text, expected)

    def test_string(self):
        text = '''
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
        util.interpret_text(self, text, expected)

    def test_struct(self):
        # since structs dynamically generate classes,
        # haven't thought of a good way to test some of the functionality of structs
        text = '''
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
            InexactNum(0.3),
            String('Jeff'),
            Boolean(True),
            InexactNum(0.3)
        ]
        util.interpret_text(self, text, expected)

    def test_symbol(self):
        text = '''
            'a
            'longer-symbol
            '"this is a string"
            '#true
        '''
        expected = [
            Symbol('a'),
            Symbol('longer-symbol'),
            String('this is a string'),
            Boolean(True)
        ]
        util.interpret_text(self, text, expected)

    def test_scope(self):
        text = '''
            (define (s t z) (- t 6))
            (define (t u s) (u s 1))
            (t s 6)
            (t * 6)
        '''
        expected = [
            Integer(0),
            Integer(6)
        ]
        util.interpret_text(self, text, expected)

        text = '''
            (define a +)
            (define b a)
            (define c b)
            (b 1 2)
        '''
        expected = [
            Integer(3)
        ]
        util.interpret_text(self, text, expected)

    def test_recursion(self):
        text = '''
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
        util.interpret_text(self, text, expected)

        text = '''
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
        util.interpret_text(self, text, expected)

    def test_builtin_if(self):
        text = '''
            (if #t 1 2)
            (if #f 1 2)
        '''
        expected = [
            Integer(1),
            Integer(2)
        ]
        util.interpret_text(self, text, expected)

    def test_builtin_and(self):
        text = '''
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
        util.interpret_text(self, text, expected)
