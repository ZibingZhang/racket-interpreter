from __future__ import annotations
import abc
from typing import Any, Union


class DataType(abc.ABC):

    def __init__(self, value: Any) -> None:
        self.value = value


class Boolean(DataType):

    def __init__(self, value: bool) -> None:
        super().__init__(value)

    def __str__(self) -> str:
        return f'#{self.value}'

    def __repr__(self) -> str:
        return self.__str__()

    def __bool__(self) -> bool:
        return self.value


class Number(DataType):

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other) -> Number:
        return Number(self.value + other.value)


class Procedure(DataType):

    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __str__(self) -> str:
        return f'#<procedure:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class String(DataType):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __str__(self) -> str:
        return f'"{self.value}"'

    def __repr__(self) -> str:
        return self.__str__()
