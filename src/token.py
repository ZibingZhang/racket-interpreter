from __future__ import annotations
from typing import Any
from enum import Enum
from src.constants import C
from src.errors import IllegalStateError


class TokenType(Enum):
    # single-character token types
    LPAREN = '('
    RPAREN = ')'
    # data types
    NUMBER = 'NUMBER'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    # reserved keywords
    DEFINE = 'define'
    # misc
    ID = 'ID'            # start with an alphabetical char followed by any number of alphanumeric chars
    EOF = 'EOF'


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
    def is_builtin_proc(token: Token) -> bool:
        return token.value in C.BUILT_IN_PROCS

    @staticmethod
    def create_proc(name: str, line_no: int = None, column: int = None) -> Token:
        return Token(TokenType.ID, name, line_no, column)

def _build_reserved_keywords():
    """Build a dictionary of reserved keywords.

    The function relies on the fact that in the TokenType
    enumeration the beginning of the block of reserved keywords is
    marked with DEFINE and the end of the block is marked with
    the DEFINE keyword.

    Result:
        {'DEFINE': <TokenType.DEFINE: 'DEFINE'>}
    """
    # enumerations support iteration, in definition order
    tt_list = list(TokenType)
    start_idx = tt_list.index(TokenType.DEFINE)
    end_idx = tt_list.index(TokenType.DEFINE)
    reserved_keywords = {
        token_type.value: token_type
        for token_type in tt_list[start_idx:end_idx + 1]
    }
    return reserved_keywords


# TODO: move to constants file
RESERVED_KEYWORDS = _build_reserved_keywords()
