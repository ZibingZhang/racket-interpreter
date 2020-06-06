from __future__ import annotations
import abc
from typing import Union


class DataType(abc.ABC):
    pass


class Number(DataType):

    def __init__(self, value: Union[float, int]) -> None:
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()

    def __add__(self, other) -> Number:
        return Number(self.value + other.value)


class Boolean(DataType):

    def __init__(self, value: bool) -> None:
        self.value = value

    def __str__(self):
        return f'#{self.value}'

    def __repr__(self):
        return self.__str__()


class String(DataType):
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self):
        return f'"{self.value}"'

    def __repr__(self):
        return self.__str__()
