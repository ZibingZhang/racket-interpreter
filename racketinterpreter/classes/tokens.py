from __future__ import annotations
from enum import Enum
import typing as tp


class TokenType(Enum):

    # parentheses
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    # data types
    INTEGER = 'INTEGER'
    RationalNum = 'RationalNum'
    DECIMAL = 'DECIMAL'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    SYMBOL = 'SYMBOL'
    # misc
    ID = 'ID'
    EOF = 'EOF'
    # invalid
    INVALID = 'INVALID'

    def __str__(self) -> str:
        return self.value


class Token:
    """A token from the lexing process.

    :Example:
        >>> Token(TokenType.ID, 'define', 5, 37)
        <Token type:ID  value:define  position:5:37>
        >>> Token(TokenType.SYMBOL, "'sym", 3, 69)
        <Token type:SYMBOL  value:'sym  position:3:69>
    """

    def __init__(self, type: TokenType, value: tp.Any, line_no: int, column: int) -> None:
        self._type = type
        self._value = value
        self._line_no = line_no
        self._column = column

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def line_no(self):
        return self._line_no

    @property
    def column(self):
        return self._column

    def __str__(self) -> str:
        return f'<Token type:{self.type}  value:{self.value}  position:{self.line_no}:{self.column}>'

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def create_proc(name: str, line_no: int = None, column: int = None) -> Token:
        return Token(TokenType.ID, name, line_no, column)


class Keyword(Enum):

    CONS = 'cons'
    EMPTY = 'empty'
    NULL = 'null'
    COND = 'cond'
    DEFINE = 'define'
    DEFINE_STRUCT = 'define-struct'
    ELSE = 'else'
    CHECK_EXPECT = 'check-expect'


KEYWORDS = list(map(lambda keyword: keyword.value, Keyword))
