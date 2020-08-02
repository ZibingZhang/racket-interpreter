from __future__ import annotations
import typing as tp
import unittest
from racketinterpreter.classes.errors import ErrorCode as EC
from racketinterpreter.classes.errors import LexerError
from racketinterpreter.classes.tokens import TokenType as TT
from racketinterpreter.processes import Lexer


class TestLexer(unittest.TestCase):

    def assert_token_types(self, text: str, token_types: tp.List[TT])-> None:
        lexer = Lexer(text)
        lexer.process()
        tokens = []
        while True:
            token = lexer.get_next_token()
            if token is None:
                break
            else:
                tokens.append(token)

        self.assertEqual(len(token_types)+1, len(tokens))

        for idx in range(len(token_types)):
            self.assertEqual(token_types[idx], tokens[idx].type)

        self.assertEqual(TT.EOF, tokens[-1].type)

    def assert_lexer_error(self, text: str, error_code: EC) -> None:
        lexer = Lexer(text)
        try:
            lexer.process()
        except LexerError as e:
            self.assertEqual(error_code, e.error_code)

    def test_booleans(self):
        text = '''
            #t #T #true
            #f #F #false
        '''
        token_types = 6 * [TT.BOOLEAN]
        self.assert_token_types(text, token_types)

    def test_incorrect_booleans(self):
        self.assert_lexer_error('#a', EC.RS_BAD_SYNTAX)
        self.assert_lexer_error("'#a", EC.RS_BAD_SYNTAX)
        self.assert_lexer_error('#True', EC.RS_BAD_SYNTAX)

    def test_numbers(self):
        text = '''
            1 50 -12
            .1 1. -.1 -1. 1.1
            1/1 -1/1
        '''
        token_types = 3*[TT.INTEGER] + 5*[TT.DECIMAL] + 2*[TT.RATIONAL]
        self.assert_token_types(text, token_types)

    def test_names_that_almost_are_numbers(self):
        text = '''
            --1 -1.-1 .-1 1/-1
        '''
        token_types = 4 * [TT.NAME]
        self.assert_token_types(text, token_types)

    def test_strings(self):
        text = '''
            "Hello World!"
        '''
        token_types = 1 * [TT.STRING]
        self.assert_token_types(text, token_types)
