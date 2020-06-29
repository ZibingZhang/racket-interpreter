from __future__ import annotations
from typing import Any, Final
from enum import Enum


class TokenType(Enum):
    # parentheses
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    # data types
    INTEGER = 'INTEGER'
    RATIONAL = 'RATIONAL'
    DECIMAL = 'DECIMAL'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    SYMBOL = 'SYMBOL'
    # misc
    ID = 'ID'
    EOF = 'EOF'
    # invalid
    INVALID = 'INVALID'


class Token:

    def __init__(self, type: TokenType, value: Any, line_no: int, column: int) -> None:
        self.type: Final = type
        self.value: Final = value
        self.line_no: Final = line_no
        self.column: Final = column

    def __str__(self) -> str:
        return f'<Token token:{self.type}  value:{self.value}  position:{self.line_no}:{self.column}>'

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def create_proc(name: str, line_no: int = None, column: int = None) -> Token:
        return Token(TokenType.ID, name, line_no, column)


class Keyword(Enum):
    COND = 'cond'
    DEFINE = 'define'
    DEFINE_STRUCT = 'define-struct'
    ELSE = 'else'
    CHECK_EXPECT = 'check-expect'


KEYWORDS = list(map(lambda keyword: keyword.value, Keyword))
