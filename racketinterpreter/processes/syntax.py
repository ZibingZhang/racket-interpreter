from __future__ import annotations
from typing import TYPE_CHECKING
from racketinterpreter import errors as err
from racketinterpreter.classes import tokens as t

if TYPE_CHECKING:
    from processes.lexer import Lexer


# TODO: add analyzer for double quotes
class ParenthesesAnalyzer:

    PAREN_MAP = {
        '(': ')',
        '[': ']',
        '{': '}'
    }

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.paren_stack = []

    def analyze(self):
        lexer = self.lexer
        token = lexer.get_next_token()
        while token.type is not t.TokenType.EOF:
            if token.type is t.TokenType.LPAREN:
                self.paren_stack.append(token)

            elif token.type is t.TokenType.RPAREN:
                if len(self.paren_stack) == 0:
                    raise err.PreLexerError(
                        error_code=err.ErrorCode.RS_UNEXPECTED_RIGHT_PARENTHESIS,
                        token=token
                    )
                else:
                    left_paren = self.paren_stack[-1].value
                    if self.PAREN_MAP[left_paren] != token.value:
                        raise err.PreLexerError(
                            error_code=err.ErrorCode.RS_INCORRECT_RIGHT_PARENTHESIS,
                            token=token,
                            left_paren=left_paren,
                            correct_right_paren=self.PAREN_MAP[left_paren],
                            incorrect_right_paren=token.value
                        )

                self.paren_stack.pop()

            token = lexer.get_next_token()

        if len(self.paren_stack) != 0:
            left_paren = self.paren_stack[-1].value
            raise err.PreLexerError(
                error_code=err.ErrorCode.RS_EXPECTED_RIGHT_PARENTHESIS,
                token=token,
                left_paren=left_paren,
                right_paren=self.PAREN_MAP[left_paren]
            )
