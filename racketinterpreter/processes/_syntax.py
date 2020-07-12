from __future__ import annotations
from racketinterpreter import errors as err
from racketinterpreter.classes import tokens as t


class ParenthesesAnalyzer:

    PAREN_MAP = {
        '(': ')',
        '[': ']',
        '{': '}'
    }

    def __init__(self) -> None:
        self.paren_stack = []

    def received_paren(self, token: t.Token) -> None:
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

    def reached_eof(self, token: t.Token) -> None:
        if len(self.paren_stack) != 0:
            left_paren = self.paren_stack[-1].value
            raise err.PreLexerError(
                error_code=err.ErrorCode.RS_EXPECTED_RIGHT_PARENTHESIS,
                token=token,
                left_paren=left_paren,
                right_paren=self.PAREN_MAP[left_paren]
            )
