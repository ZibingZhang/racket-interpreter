from __future__ import annotations
from enum import Enum
import typing as tp


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
    # special
    LIST_ABRV = 'LIST_ABRV'

    def __str__(self) -> str:
        return self.value


class Token:
    """A token from the lexing process.

    :ivar TokenType type: The type of token.
    :ivar tp.Any value: The value of the token.
    :ivar int line_no: The line number of the tokens first character.
    :ivar: int column: The column of the tokens first character.

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
        self._children = []

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

    @property
    def children(self):
        return self._children

    def __str__(self) -> str:
        return f'<Token type:{self.type}  value:{self.value}  position:{self.line_no}:{self.column}' \
               f'{"" if len(self.children) == 0 else f"  children:{self.children}"}>'

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def create_proc(name: str, line_no: int = None, column: int = None) -> Token:
        return Token(TokenType.ID, name, line_no, column)


class Keyword(Enum):

    CONS = 'cons'
    COND = 'cond'
    DEFINE = 'define'
    DEFINE_STRUCT = 'define-struct'
    ELSE = 'else'
    CHECK_EXPECT = 'check-expect'


KEYWORDS = list(map(lambda keyword: keyword.value, Keyword))
