from __future__ import annotations
import typing as tp
import unittest
from racketinterpreter.classes.tokens import TokenType as TT
from racketinterpreter.processes import Lexer

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import tokens as t


class TestLexer(unittest.TestCase):

    def assert_token_types(self, text: str, token_types: tp.List[t.TokenType]) -> None:
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

    def test_booleans(self):
        text = '''
            #t #T #true
            #f #F #false
        '''
        token_types = [
            TT.BOOLEAN, TT.BOOLEAN, TT.BOOLEAN,
            TT.BOOLEAN, TT.BOOLEAN, TT.BOOLEAN
        ]
        self.assert_token_types(text, token_types)

    def test_numbers(self):
        text = '''
            1 50 -12
            .1 1. -.1 -1. 1.1
            1/1 -1/1
        '''
        token_types = [
            TT.INTEGER, TT.INTEGER, TT.INTEGER,
            TT.DECIMAL, TT.DECIMAL, TT.DECIMAL, TT.DECIMAL, TT.DECIMAL,
            TT.RATIONAL, TT.RATIONAL
        ]
        self.assert_token_types(text, token_types)
