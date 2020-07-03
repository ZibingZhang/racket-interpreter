from __future__ import annotations
import fractions as f
import functools
from typing import Any, List, Optional, Union


class DataType(type):
    pass


class StructDataType(DataType):
    pass


class Data(metaclass=DataType):

    def __init__(self, value: Optional[Any] = None) -> None:
        self.value = value


class StructDataFactory:

    @staticmethod
    def create(struct_name: str, fields: List[str]) -> StructDataType:
        struct_data = StructDataType(struct_name, (Data,), {})

        setattr(struct_data, 'field_names', fields)
        setattr(struct_data, 'fields', None)

        setattr(struct_data, 'metaclass', StructDataType)
        struct_data.metaclass = staticmethod(struct_data.metaclass)

        setattr(struct_data, '__str__', lambda self: f'#<{struct_name}>')

        return struct_data


class Boolean(Data):

    def __init__(self, value: bool) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        return issubclass(type(other), Boolean) and self.value == other.value

    def __str__(self) -> str:
        return f'#{"t" if self.value else "f"}'

    def __repr__(self) -> str:
        return self.__str__()

    def __bool__(self) -> bool:
        return self.value


class ConsList(Data):

    def __init__(self, value: list) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        return issubclass(type(other), ConsList) and self.value == other.value

    def __str__(self) -> str:
        string = ' '.join(map(str, self.value))
        return f"'({string})"

    def __repr__(self) -> str:
        return self.__str__()


class Number(Data):

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)

    @property
    def precedence(self) -> int:
        return 6


class Procedure(Data):

    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        return issubclass(type(other), Procedure) and self.value == other.value

    def __str__(self) -> str:
        return f'#<procedure:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class String(Data):

    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        return issubclass(type(other), String) and self.value == other.value

    def __str__(self) -> str:
        return f'"{self.value}"'

    def __repr__(self) -> str:
        return self.__str__()


class Symbol(Data):

    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        return issubclass(type(other), Symbol) and self.value == other.value

    def __str__(self) -> str:
        # the leading apostrophe is included in self.value
        return f"{self.value}"

    def __repr__(self) -> str:
        return self.__str__()


@functools.total_ordering
class RealNumber(Number):

    @property
    def precedence(self) -> int:
        return 5

    def __eq__(self, other) -> bool:
        # TODO: change this when complex numbers are added
        return issubclass(type(other), RealNumber) and self.value == other.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return self.__str__()

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
            return Integer(1) / other.__truediv__(self)
        else:
            return RealNumber(self.value / other.value)

    def __neg__(self) -> RealNumber:
        return RealNumber(-self.value)

    def __lt__(self, other) -> bool:
        return self.value < other.value


class InexactNumber(RealNumber):

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)

    @property
    def precedence(self) -> int:
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
            return Integer(1) / other.__truediv__(self)
        else:
            return InexactNumber(self.value / other.value)

    def __neg__(self) -> InexactNumber:
        return InexactNumber(-self.value)

    def __abs__(self) -> InexactNumber:
        return InexactNumber(abs(self.value))


class ExactNumber(RealNumber):

    @property
    def precedence(self) -> int:
        return 3


class Rational(ExactNumber):

    @property
    def precedence(self) -> int:
        return 2

    def __init__(self, numerator: int, denominator: int) -> None:
        super().__init__(numerator / denominator)
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self) -> str:
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
                return Rational(fraction.numerator, fraction.denominator)
            else:
                numerator = (self.numerator * other.denominator) + (self.denominator * other.numerator)
                denominator = self.denominator * other.denominator
                fraction = f.Fraction(numerator, denominator)
                if fraction.denominator == 1:
                    return Integer(fraction.numerator)
                else:
                    return Rational(fraction.numerator, fraction.denominator)

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
                return Rational(fraction.numerator, fraction.denominator)
            else:
                numerator = (self.numerator * other.denominator) - (self.denominator * other.numerator)
                denominator = self.denominator * other.denominator
                fraction = f.Fraction(numerator, denominator)
                if fraction.denominator == 1:
                    return Integer(fraction.numerator)
                else:
                    return Rational(fraction.numerator, fraction.denominator)

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
                return Rational(fraction.numerator, fraction.denominator)

    def __truediv__(self, other) -> Number:
        if other.precedence > self.precedence:
            return Integer(1) / other.__truediv__(self)
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
                return Rational(fraction.numerator, fraction.denominator)

    def __neg__(self) -> Rational:
        fraction = f.Fraction(-self.numerator, self.denominator)
        return Rational(fraction.numerator, fraction.denominator)

    def __abs__(self) -> Rational:
        numerator = abs(self.numerator)
        denominator = abs(self.denominator)
        return Rational(numerator, denominator)


class Integer(ExactNumber):

    @property
    def precedence(self) -> int:
        return 1

    def __init__(self, value: int) -> None:
        super().__init__(value)

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value

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
        other_type = type(other)
        if issubclass(other_type, Rational):
            numerator = self.value * other.denominator
            denominator = other.numerator
            fraction = f.Fraction(numerator, denominator)
        elif issubclass(other_type, Integer):
            numerator = self.value
            denominator = other.value
            fraction = f.Fraction(numerator, denominator)
        else:
            return InexactNumber(self.value / other.value)

        if fraction.denominator == 1:
            return Integer(fraction.numerator)
        else:
            return Rational(fraction.numerator, fraction.denominator)

    def __neg__(self) -> Integer:
        return Integer(-self.value)

    def __abs__(self) -> Integer:
        return Integer(abs(self.value))
