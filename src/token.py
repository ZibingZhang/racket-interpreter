from __future__ import annotations
from typing import Any
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
    # reserved keywords
    # DEFINE = 'define'
    # DEFINE_STRUCT = 'define-struct'
    # COND = 'cond'
    # ELSE = 'else'
    # misc
    ID = 'ID'
    EOF = 'EOF'
    # invalid
    INVALID = 'INVALID'


class Token:

    def __init__(self, type: TokenType, value: Any,
                 line_no: int = None, column: int = None) -> None:
        self._type = type
        self._value = value
        self._line_no = line_no
        self._column = column

    @property
    def type(self) -> TokenType:
        return self._type

    @property
    def value(self) -> Any:
        return self._value

    @property
    def line_no(self) -> int:
        return self._line_no

    @property
    def column(self) -> int:
        return self._column

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


KEYWORDS = list(map(lambda keyword: keyword.value, Keyword))
