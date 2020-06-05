from typing import Any
import enum


class TokenType(enum.Enum):
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    EOF = 'EOF'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    ID = 'ID'          # start with an alphabetical char followed by any number of alphanumeric chars
    DEFINE = 'DEFINE'


class Token:

    def __init__(self, _type: TokenType, _value: Any) -> None:
        self._type = _type
        self._value = _value

    @property
    def type(self) -> TokenType:
        return self._type

    @property
    def value(self) -> Any:
        return self._value

    def __str__(self) -> str:
        return f'<Token token:{self._type} value:{self._value}>'

    def __repr__(self) -> str:
        return self.__str__()
