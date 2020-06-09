from __future__ import annotations
import abc
import fractions as f
from typing import Any, Union


class DataType(abc.ABC):

    def __init__(self, value: Any) -> None:
        self.value = value


class Boolean(DataType):

    def __init__(self, value: bool) -> None:
        super().__init__(value)

    def __eq__(self, other):
        return issubclass(type(other), Boolean) and self.value == other.value

    def __str__(self) -> str:
        return f'#{"t" if self.value else "f"}'

    def __repr__(self) -> str:
        return self.__str__()

    def __bool__(self) -> bool:
        return self.value


class Number(DataType):

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)

    @property
    def precedence(self):
        return 6

    def __eq__(self, other):
        return issubclass(type(other), Number) and self.value == other.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            return Number(self.value + other.value)

    def __sub__(self, other) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            return Number(self.value - other.value)

    def __mul__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            return Number(self.value * other.value)

    def __truediv__(self, other) -> Number:
        if other.precedence > self.precedence:
            return 1/other.__truediv__(self)
        else:
            return Number(self.value / other.value)

    def __neg__(self) -> Number:
        return Number(-self.value)


class Procedure(DataType):

    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __eq__(self, other):
        return issubclass(type(other), Procedure) and self.value == other.value

    def __str__(self) -> str:
        return f'#<procedure:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class String(DataType):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __eq__(self, other):
        return issubclass(type(other), String) and self.value == other.value

    def __str__(self) -> str:
        return f'"{self.value}"'

    def __repr__(self) -> str:
        return self.__str__()


class RealNumber(Number):

    @property
    def precedence(self):
        return 5

    def __add__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            return RealNumber(self.value + other.value)

    def __sub__(self, other) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            return RealNumber(self.value - other.value)

    def __mul__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            return RealNumber(self.value * other.value)

    def __truediv__(self, other) -> Number:
        if other.precedence > self.precedence:
            return 1/other.__truediv__(self)
        else:
            return RealNumber(self.value / other.value)


class ExactNumber(RealNumber):

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)

    @property
    def precedence(self):
        return 3


class InexactNumber(RealNumber):

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)

    @property
    def precedence(self):
        return 4

    def __add__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            return InexactNumber(self.value + other.value)

    def __sub__(self, other) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            return InexactNumber(self.value - other.value)

    def __mul__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            return InexactNumber(self.value * other.value)

    def __truediv__(self, other) -> Number:
        if other.precedence > self.precedence:
            return 1/other.__truediv__(self)
        else:
            return InexactNumber(self.value / other.value)

    def __neg__(self) -> Number:
        return InexactNumber(-self.value)


class Integer(ExactNumber):

    def __init__(self, value: int) -> None:
        super().__init__(value)

    def __str__(self):
        return str(self.value)

    def __add__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            return Integer(self.value + other.value)

    def __sub__(self, other) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            return Integer(self.value - other.value)

    def __mul__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            return Integer(self.value * other.value)

    def __truediv__(self, other) -> Number:
        if other.precedence > self.precedence:
            return 1/other.__truediv__(self)
        else:
            fraction = f.Fraction(self.value, other.value)
            if fraction.denominator == 1:
                return Integer(fraction.numerator)
            else:
                return Rational(fraction)

    def __neg__(self) -> Number:
        return Integer(-self.value)


class Rational(ExactNumber):

    def __init__(self, fraction: f.Fraction) -> None:
        numerator = fraction.numerator
        denominator = fraction.denominator
        super().__init__(numerator / denominator)
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        return f'{self.numerator}/{self.denominator}'

    def __add__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            other_type = type(other)
            is_other_integer = issubclass(other_type, Integer)
            if is_other_integer:
                denominator = self.denominator
                numerator = self.numerator + (denominator * other.value)
                fraction = f.Fraction(numerator, denominator)
                return Rational(fraction)
            else:
                numerator = (self.numerator * other.denominator) + (self.denominator * other.numerator)
                denominator = self.denominator * other.denominator
                fraction = f.Fraction(numerator, denominator)
                if fraction.denominator == 1:
                    return Integer(fraction.numerator)
                else:
                    return Rational(fraction)

    def __sub__(self, other) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            other_type = type(other)
            is_other_integer = issubclass(other_type, Integer)
            if is_other_integer:
                denominator = self.denominator
                numerator = self.numerator - (denominator * other.value)
                fraction = f.Fraction(numerator, denominator)
                return Rational(fraction)
            else:
                numerator = (self.numerator * other.denominator) - (self.denominator * other.numerator)
                denominator = self.denominator * other.denominator
                fraction = f.Fraction(numerator, denominator)
                if fraction.denominator == 1:
                    return Integer(fraction.numerator)
                else:
                    return Rational(fraction)

    def __mul__(self, other) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            other_type = type(other)
            is_other_integer = issubclass(other_type, Integer)
            if is_other_integer:
                numerator = self.numerator * other.value
                denominator = self.denominator
            else:
                numerator = self.numerator * other.numerator
                denominator = self.denominator * other.denominator
            fraction = f.Fraction(numerator, denominator)
            if fraction.denominator == 1:
                return Integer(fraction.numerator)
            else:
                return Rational(fraction)

    def __truediv__(self, other) -> Number:
        if other.precedence > self.precedence:
            return 1/other.__truediv__(self)
        else:
            other_type = type(other)
            is_other_integer = issubclass(other_type, Integer)
            if is_other_integer:
                numerator = self.numerator
                denominator = self.denominator / other.value
            else:
                numerator = self.numerator * other.denominator
                denominator = self.denominator * other.numerator
            fraction = f.Fraction(numerator, denominator)
            if fraction.denominator == 1:
                return Integer(fraction.numerator)
            else:
                return Rational(fraction)

    def __neg__(self) -> Number:
        fraction = f.Fraction(-self.numerator, self.denominator)
        return Rational(fraction)
