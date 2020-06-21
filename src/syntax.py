from __future__ import annotations
from typing import TYPE_CHECKING
from src.errors import ErrorCode, PreLexerError
from src.token import TokenType

if TYPE_CHECKING:
    from src.lexer import Lexer


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
        while token.type is not TokenType.EOF:
            if token.type is TokenType.LPAREN:
                self.paren_stack.append(token)

            elif token.type is TokenType.RPAREN:
                if len(self.paren_stack) == 0:
                    raise PreLexerError(
                        error_code=ErrorCode.RS_UNEXPECTED_RIGHT_PARENTHESIS,
                        token=token
                    )
                else:
                    left_paren = self.paren_stack[-1].value
                    if self.PAREN_MAP[left_paren] != token.value:
                        raise PreLexerError(
                            error_code=ErrorCode.RS_INCORRECT_RIGHT_PARENTHESIS,
                            token=token,
                            left_paren=left_paren,
                            correct_right_paren=self.PAREN_MAP[left_paren],
                            incorrect_right_paren=token.value
                        )

                self.paren_stack.pop()

            token = lexer.get_next_token()

        if len(self.paren_stack) != 0:
            left_paren = self.paren_stack[-1].value
            raise PreLexerError(
                error_code=ErrorCode.RS_EXPECTED_RIGHT_PARENTHESIS,
                token=token,
                left_paren=left_paren,
                right_paren=self.PAREN_MAP[left_paren]
            )
