from __future__ import annotations
import abc
import fractions as f
import functools
from typing import Any, List, Optional, Union


class DataType(type):
    """The metaclass of a class representing data."""


class StructDataType(DataType):
    """The metaclass of a class representing a struct."""


class Data(metaclass=DataType):
    """Data from the output of the interpretation process.

    :param value: The value of the data.
    """

    @abc.abstractmethod
    def __init__(self, value: Optional[Any] = None) -> None:
        self.value = value


class StructDataFactory:
    """A factory for creating struct data types."""

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
    """A boolean.

    :Example:
        >>> Boolean(True)
        #t
        >>> Boolean(False)
        #f
    """

    def __init__(self, value: bool) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        """
        :Example:
            >>> Boolean(False) == (Boolean(False))
            True
            >>> Boolean(True) == (Integer(5))
            False
        """
        return issubclass(type(other), Boolean) and self.value == other.value

    def __hash__(self) -> int:
        """
        :Example:
            >>> hash(Boolean(True))
            1
            >>> hash(Boolean(False))
            0
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        :Example:
            >>> str(Boolean(True))
            '#t'
            >>> str(Boolean(False))
            '#f'
        """
        return f'#{"t" if self.value else "f"}'

    def __repr__(self) -> str:
        """
        :Example:
            >>> repr(Boolean(True))
            '#t'
            >>> repr(Boolean(False))
            '#f'
        """
        return self.__str__()

    def __bool__(self) -> bool:
        """
        :Example:
            >>> bool(Boolean(True))
            True
            >>> bool(Boolean(False))
            False
        """
        return self.value

    def __int__(self):
        """
        :Example:
            >>> int(Boolean(True))
            1
            >>> int(Boolean(False))
            0
        """
        return 1 if self.value else 0


class ConsList(Data):
    """A list.

    :Example:
        >>> ConsList([Integer(68), Boolean(False), Symbol("'sym")])
        '(68 #f 'sym)
        >>> ConsList([])
        '()
    """

    def __init__(self, value: List[Data]) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        """
        :Example:
            >>> ConsList([Integer(68), Symbol("'sym")]) == ConsList([Integer(68), Boolean(False), Symbol("'sym")])
            False
            >>> ConsList([Integer(68), Symbol("'sym")]) == ConsList([Integer(68), Symbol("'sym")])
            True
            >>> ConsList([]) == ConsList([])
            True
        """
        return issubclass(type(other), ConsList) and self.value == other.value

    def __hash__(self) -> int:
        """
        :Example:
            >>> type(hash(ConsList([Integer(68), Boolean(False), Symbol("'sym")])))
            <class 'int'>
            >>> hash(ConsList([]))
            5740354900026072187
        """
        return hash(tuple(self.value))

    def __str__(self) -> str:
        """
        :Example:
            >>> str(ConsList([Integer(68), Boolean(False), Symbol("'sym")]))
            "'(68 #f 'sym)"
            >>> str(ConsList([]))
            "'()"
        """
        string = ' '.join(map(str, self.value))
        return f"'({string})"

    def __repr__(self) -> str:
        """
        :Example:
            >>> repr(ConsList([Integer(68), Boolean(False), Symbol("'sym")]))
            "'(68 #f 'sym)"
            >>> repr(ConsList([]))
            "'()"
        """
        return self.__str__()

    def __len__(self) -> int:
        """
        :Example:
            >>> len(ConsList([Integer(68), Boolean(False), Symbol("'sym")]))
            3
            >>> len(ConsList([]))
            0
        """
        return len(self.value)

    def __getitem__(self, item: Union[int, slice, Integer]) -> Data:
        """
        :Example:
            >>> ConsList([Integer(68), Boolean(False), Symbol("'sym")])[1]
            #f
            >>> ConsList([Integer(68), Boolean(False), Symbol("'sym")])[-1]
            'sym
            >>> ConsList([])[2]
            Traceback (most recent call last):
              ...
            IndexError: list index out of range
        """
        if type(item) is Integer:
            item = item.value

        result = self.value[item]

        if type(item) is slice:
            result = ConsList(result)

        return result

    def __bool__(self) -> bool:
        """
        :Example:
            >>> bool(ConsList([Integer(68), Boolean(False), Symbol("'sym")]))
            True
            >>> bool(ConsList([]))
            False
        """
        return len(self.value) > 0


class Number(Data):
    """A number."""

    @property
    def precedence(self) -> int:
        """An indicator of which object's method will be called for binary operations.

        When performing binary operations on Numbers, the implementation on the object with the higher precedence will
        be used.

        :return: This objects precedence
        :rtype: int
        """
        return 6

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__(value)


class Procedure(Data):
    """A procedure.

    :Example:
        >>> Procedure('factorial')
        #<procedure:factorial>
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __eq__(self, other) -> bool:
        """Procedures are never equal to each other.

        The only way to test if procedures are equal is to compare
        the outputs of the two procedures given the same input.
        Comparing procedures in a test should raise an error.

        :Example:
            >>> Procedure('fibonacci') == Procedure('fibonacci')
            False
            >>> Procedure('interesting?') == Procedure('weird?')
            False
        """
        return False

    def __str__(self) -> str:
        """
        :Example:
            >>> str(Procedure('fibonacci'))
            '#<procedure:fibonacci>'
        """
        return f'#<procedure:{self.value}>'

    def __repr__(self) -> str:
        """
        :Example:
            >>> repr(Procedure('fibonacci'))
            '#<procedure:fibonacci>'
        """
        return self.__str__()


class String(Data):
    """A string.

    :Example:
        >>> String('Hello World!')
        "Hello World!"
        >>> String('')
        ""
    """

    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __eq__(self, other) -> bool:
        """
        :Example:
            >>> String('abc') == String('abc')
            True
            >>> String('Case Sensitive') == String('cAsE sEnsITiVe')
            False
        """
        return issubclass(type(other), String) and self.value == other.value

    def __hash__(self) -> int:
        """
        :Example:
            >>> type(hash(String('Hello World!')))
            <class 'int'>
            >>> hash(String(''))
            0
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        :Example:
            >>> str(String('Hello World!'))
            '"Hello World!"'
            >>> str(String(''))
            '""'
        """
        return f'"{self.value}"'

    def __repr__(self) -> str:
        """
        :Example:
            >>> repr(String('Hello World!'))
            '"Hello World!"'
            >>> repr(String(''))
            '""'
        """
        return self.__str__()

    def __len__(self) -> int:
        """
        :Example:
            >>> len(String('Hello World!'))
            12
            >>> len(String(''))
            0
        """
        return len(self.value)

    def __getitem__(self, item: Union[int, slice, Integer]) -> str:
        """
        :Example:
            >>> String('Hello World!')[1]
            'e'
            >>> String('Hello World!')[-1]
            '!'
            >>> String('')[2]
            Traceback (most recent call last):
              ...
            IndexError: string index out of range
        """
        if type(item) is Integer:
            item = item.value

        result = self.value[item]

        if type(item) is slice:
            result = ConsList(result)

        return result

    def __bool__(self) -> bool:
        return len(self.value) > 0

    def __iadd__(self, other: String) -> String:
        return String(self.value + other.value)

    def __contains__(self, item: String) -> Boolean:
        return Boolean(item.value in self.value)

    def copy(self) -> String:
        return String(self.value)

    def lower(self) -> String:
        return String(self.value.lower())


class Symbol(Data):
    """A symbol.

    :Example:
        >>> Symbol("'anything")
        'anything
        >>> Symbol("'can=be_a-symbo1")
        'can=be_a-symbo1
    """

    def __init__(self, value: str) -> None:
        # the value includes the leading apostrophe
        super().__init__(value)

    def __eq__(self, other) -> bool:
        """A symbol.

        :Example:
            >>> Symbol("'abc") == Symbol("'abc")
            True
            >>> Symbol("'Case Sensitive") == Symbol("'cAsE sEnsITiVe")
            False
        """
        return issubclass(type(other), Symbol) and self.value == other.value

    def __hash__(self) -> int:
        """
        :Example:
            >>> type(hash(Symbol("'abc")))
            <class 'int'>
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        :Example:
            >>> str(Symbol("'abc"))
            "'abc"
        """
        return f"{self.value}"

    def __repr__(self) -> str:
        """
        :Example:
            >>> repr(Symbol("'abc"))
            "'abc"
        """
        return self.__str__()


@functools.total_ordering
class RealNumber(Number):

    @property
    def precedence(self) -> int:
        return 5

    def __eq__(self, other) -> bool:
        # TODO: change this when complex numbers are added
        return issubclass(type(other), RealNumber) and self.value == other.value

    def __hash__(self) -> int:
        """
        :Example:
            >>> hash(RealNumber(4.5))
            1152921504606846980
        """
        return hash(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return self.__str__()

    def __bool__(self) -> bool:
        return self.value != 0

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

    def __init__(self, numerator: int, denominator: int) -> None:
        super().__init__(numerator if denominator == 1 else numerator / denominator)

    @property
    def precedence(self) -> int:
        return 3


class Rational(ExactNumber):

    @property
    def precedence(self) -> int:
        return 2

    def __init__(self, numerator: int, denominator: int) -> None:
        super().__init__(numerator, denominator)
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
        super().__init__(value, 1)

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


# the natural numbers are defined starting at zero
class NaturalNumber(Integer):

    pass
