from __future__ import annotations
import abc
import fractions as f
import functools
import typing as tp


class DataType(type):
    """The metaclass of a class representing data."""


class Data(metaclass=DataType):
    """Data from the output of the interpretation process.

    :param value: The value of the data.
    """

    @abc.abstractmethod
    def __init__(self, value: tp.Optional[tp.Any] = None) -> None:
        self.value = value


class StructDataType(type):
    """The metaclass of a class representing a struct."""


class StructData(metaclass=StructDataType):
    """Data representing a struct."""


class StructDataFactory:
    """A factory for creating struct data types."""

    @staticmethod
    def create(struct_name: str, fields: tp.List[str]) -> StructDataType:
        struct_data = StructDataType(struct_name, (StructData,), {})

        setattr(struct_data, 'field_names', fields)
        setattr(struct_data, 'fields', None)

        setattr(struct_data, 'metaclass', StructDataType)
        struct_data.metaclass = staticmethod(struct_data.metaclass)

        setattr(struct_data, '__str__', lambda self: f'(make-{struct_name} {str(" ".join(map(str, self.fields)))})')
        setattr(struct_data, '__repr__', lambda self: self.__str__())

        return struct_data


# ========== ========== ========== #
#         Base Data Classes
# ========== ========== ========== #
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

    def __eq__(self, other: tp.Any) -> bool:
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


class List(Data):
    """A list.

    :Example:
        >>> List([Integer(68), Boolean(False), Symbol("'sym")])
        '(68 #f 'sym)
        >>> List([])
        '()
    """

    def __init__(self, value: tp.List[Data]) -> None:
        super().__init__(value)

    def __eq__(self, other: tp.Any) -> bool:
        """
        :Example:
            >>> List([Integer(68), Symbol("'sym")]) == List([Integer(68), Boolean(False), Symbol("'sym")])
            False
            >>> List([Integer(68), Symbol("'sym")]) == List([Integer(68), Symbol("'sym")])
            True
            >>> List([]) == List([])
            True
        """
        return issubclass(type(other), List) and self.value == other.value

    def __hash__(self) -> int:
        """
        :Example:
            >>> type(hash(List([Integer(68), Boolean(False), Symbol("'sym")])))
            <class 'int'>
            >>> hash(List([]))
            5740354900026072187
        """
        return hash(tuple(self.value))

    def __str__(self) -> str:
        """
        :Example:
            >>> str(List([Integer(68), Boolean(False), Symbol("'sym")]))
            "'(68 #f 'sym)"
            >>> str(List([]))
            "'()"
        """
        if len(self.value) == 0:
            return "'()"
        else:
            string = ' '.join(map(str, self.value))
            return f"(list {string})"

    def __repr__(self) -> str:
        """
        :Example:
            >>> repr(List([Integer(68), Boolean(False), Symbol("'sym")]))
            "'(68 #f 'sym)"
            >>> repr(List([]))
            "'()"
        """
        return self.__str__()

    def __len__(self) -> int:
        """
        :Example:
            >>> len(List([Integer(68), Boolean(False), Symbol("'sym")]))
            3
            >>> len(List([]))
            0
        """
        return len(self.value)

    def __getitem__(self, item: tp.Union[int, slice, Integer]) -> Data:
        """
        :Example:
            >>> List([Integer(68), Boolean(False), Symbol("'sym")])[1]
            #f
            >>> List([Integer(68), Boolean(False), Symbol("'sym")])[-1]
            'sym
            >>> List([])[2]
            Traceback (most recent call last):
              ...
            IndexError: list index out of range
        """
        if type(item) is Integer:
            item = item.value

        result = self.value[item]

        if type(item) is slice:
            result = List(result)

        return result

    def __bool__(self) -> bool:
        """
        :Example:
            >>> bool(List([Integer(68), Boolean(False), Symbol("'sym")]))
            True
            >>> bool(List([]))
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

        :return: This object's precedence
        :rtype: int
        """
        return 6

    @property
    def numerator(self) -> int:
        """The numerator of the number.

        :raises AttributeError: If this number does not have a numerator an error will be raised.
        :return: The numerator
        :rtype: int
        """
        raise AttributeError

    @property
    def denominator(self) -> int:
        """The denominator of the number.

        :raises AttributeError: If this number does not have a denominator an error will be raised.
        :return: The denominator
        :rtype: int
        """
        raise AttributeError

    @property
    def real(self) -> RealNum:
        raise NotImplementedError

    @property
    def imaginary(self) -> RealNum:
        raise NotImplementedError

    def __init__(self, value: tp.Union[complex, float, int]) -> None:
        super().__init__(value)

    def __add__(self, other: Number) -> Number: ...

    def __sub__(self, other: Number) -> Number: ...

    def __mul__(self, other: Number) -> Number: ...

    def __truediv__(self, other: Number) -> Number: ...

    def __neg__(self) -> Number: ...

    def __bool__(self) -> bool:
        return not self.is_zero()

    def is_integer(self) -> bool:
        """Is this number an integer?

        :raises NotImplementedError: By default an implementation is not provided in the Number base class.
        :return: True if this number is an integer
        :rtype: bool
        """
        raise NotImplementedError

    def is_zero(self) -> bool:
        """Is this number equal to zero?

        :raises NotImplementedError: By default an implementation is not provided in the Number base class.
        :return: True if this number is equal to zero
        :rtype: bool
        """
        raise NotImplementedError


class Procedure(Data):
    """A procedure.

    :Example:
        >>> Procedure('factorial')
        #<procedure:factorial>
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __eq__(self, other: tp.Any) -> bool:
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

    def __eq__(self, other: tp.Any) -> bool:
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

    def __getitem__(self, item: tp.Union[int, slice, Integer]) -> str:
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
            result = List(result)

        return result

    def __bool__(self) -> bool:
        """
        :Example:
            >>> bool(String('Hello World!'))
            True
            >>> bool(String(''))
            False
        """
        return len(self.value) > 0

    def __iadd__(self, other: String) -> String:
        """
        :Example:
            >>> string = String('Hello')
            >>> string += String(' World!')
            >>> string
            "Hello World!"
        """
        self.value += other.value
        return self

    def __contains__(self, item: String) -> Boolean:
        """
        :Example:
            >>> String('Hello') in String('Hello World!')
            True
            >>> String('world') in String('Hello World!')
            False
        """
        return Boolean(item.value in self.value)

    def copy(self) -> String:
        """Create a copy of this string.

        :Example:
            >>> String('Hello World!').copy()
            "Hello World!"
        """
        return String(self.value)

    def lower(self) -> String:
        """Create a copy of a lowercase version of this string.

        :Example:
            >>> String('Hello World!').lower()
            "hello world!"
        """
        return String(self.value.lower())

    def upper(self) -> String:
        """Create a copy of an uppercase version of this string.

        :Example:
            >>> String('Hello World!').upper()
            "HELLO WORLD!"
        """
        return String(self.value.upper())

    def isspace(self) -> Boolean:
        return Boolean(self.value.isspace())

    def isnumeric(self) -> Boolean:
        return Boolean(self.value.isnumeric())

    def islower(self) -> Boolean:
        return Boolean(self.value.islower())

    def isupper(self) -> Boolean:
        return Boolean(self.value.isupper())


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

    def __eq__(self, other: tp.Any) -> bool:
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


# ========== ========== ========== #
#        Child Data Classes
# ========== ========== ========== #
class ConsList(List):
    """A constructed (non-empty) list."""


class ComplexNum(Number):
    """A complex number.

    A number with a real and imaginary part.
    """

    def __init__(self, real: RealNum, imaginary: RealNum) -> None:
        super().__init__(complex(real.value, imaginary.value))
        self._real = real
        self._imaginary = imaginary

    @property
    def precedence(self) -> int:
        return 7

    @property
    def real(self) -> RealNum:
        return self._real

    @property
    def imaginary(self) -> RealNum:
        return self._imaginary

    def __eq__(self, other: tp.Any) -> bool:
        """
        :Example:
            >>> ComplexNum(Integer(1), InexactNum(2.0)) == ComplexNum(Integer(1), Integer(2))
            True
            >>> RationalNum(5, 4) == ComplexNum(InexactNum(1.25), Integer(0))
            True
            >>> ComplexNum(Integer(1), Integer(-3)) == ComplexNum(Integer(5), Integer(-3))
            False
            >>> ComplexNum(Integer(1), Integer(-3)) == ComplexNum(Integer(1), Integer(3))
            False
        """
        if issubclass(type(other), RealNum):
            return self.imaginary.is_zero() and self.real == other
        elif issubclass(type(other), ComplexNum):
            return self.real == other.real and self.imaginary == other.imaginary
        else:
            return False

    def __hash__(self) -> int:
        """
        :Example:
            >>> hash(ComplexNum(InexactNum(2.3), Integer(4)))
            691752902764107782
            >>> hash(ComplexNum(Integer(0), Integer(0)))
            0
        """
        return hash(self.real) + hash(self.imaginary)

    def __str__(self) -> str:
        """
        :Example:
            >>> str(ComplexNum(Integer(3), Integer(9)))
            '3+9i'
        """
        if self.imaginary < Integer(0):
            return f'{self.real}-{-self.imaginary}i'
        else:
            return f'{self.real}+{self.imaginary}i'

    def __repr__(self) -> str:
        """
        :Example:
            >>> str(ComplexNum(Integer(3), Integer(9)))
            '3+9i'
        """
        return self.__str__()

    def __add__(self, other: Number) -> Number:
        """
        :Example:
            >>> ComplexNum(Integer(1), Integer(2)) + ComplexNum(Integer(3), Integer(4))
            4+6i
            >>> ComplexNum(Integer(3), Integer(-5)) + ComplexNum(RationalNum(7, 5), InexactNum(5))
            22/5
            >>> InexactNum(7.5) + ComplexNum(RationalNum(7, 5), InexactNum(5))
            8.9+5i
        """
        real = self.real + other.real
        imaginary = self.imaginary + other.imaginary

        return real if imaginary.is_zero() else ComplexNum(real, imaginary)

    def __sub__(self, other: Number) -> Number:
        """
        :Example:
            >>> ComplexNum(Integer(1), Integer(2)) - ComplexNum(Integer(3), Integer(4))
            -2-2i
            >>> ComplexNum(Integer(3), Integer(-5)) - ComplexNum(RationalNum(7, 5), InexactNum(-5))
            8/5
            >>> InexactNum(7.5) - ComplexNum(RationalNum(7, 5), InexactNum(5))
            6.1-5i
        """
        real = self.real - other.real
        imaginary = self.imaginary - other.imaginary

        return real if imaginary.is_zero() else ComplexNum(real, imaginary)

    def __mul__(self, other: Number) -> Number:
        """
        :Example:
            >>> ComplexNum(Integer(1), Integer(2)) * ComplexNum(Integer(3), Integer(4))
            -5+10i
            >>> ComplexNum(Integer(3), Integer(-5)) * ComplexNum(RationalNum(7, 5), InexactNum(0))
            4.2-7i
            >>> InexactNum(7.5) * ComplexNum(RationalNum(7, 5), InexactNum(5))
            10.5+37.5i
        """
        real = (self.real * other.real) - (self.imaginary * other.imaginary)
        imaginary = (self.real * other.imaginary) + (self.imaginary * other.real)

        return real if imaginary.is_zero() else ComplexNum(real, imaginary)

    def __truediv__(self, other: Number) -> Number: ...

    def __neg__(self) -> ComplexNum:
        """
        :Example:
            >>> -ComplexNum(Integer(1), Integer(2))
            -1-2i
        """
        return ComplexNum(-self.real, -self.imaginary)

    def is_integer(self) -> bool:
        """
        :Example:
            >>> ComplexNum(Integer(1), Integer(0)).is_integer()
            True
            >>> ComplexNum(RationalNum(4, 3), Integer(0)).is_integer()
            False
            >>> ComplexNum(Integer(1), Integer(2)).is_integer()
            False
        """
        return self.imaginary.is_zero() and self.real.is_integer()

    def is_zero(self) -> bool:
        """
        :Example:
            >>> ComplexNum(InexactNum(0.0), Integer(0)).is_zero()
            True
            >>> ComplexNum(RationalNum(3, 4), Integer(0)).is_zero()
            False
            >>> ComplexNum(Integer(5), Integer(2)).is_zero()
            False
        """
        return self.real.is_zero() and self.imaginary.is_zero()


@functools.total_ordering
class RealNum(Number):

    def __init__(self, value: tp.Union[float, int]) -> None:
        super().__init__(value)

    @property
    def precedence(self) -> int:
        return 5

    @property
    def real(self) -> RealNum:
        return self

    @property
    def imaginary(self) -> RealNum:
        return Integer(0)

    def __eq__(self, other: tp.Any) -> bool:
        if not issubclass(type(other), Number):
            return False
        elif other.precedence > self.precedence:
            return other.__eq__(self)
        else:
            return issubclass(type(other), RealNum) and self.value == other.value

    def __hash__(self) -> int:
        """
        :Example:
            >>> hash(RealNum(4.5))
            1152921504606846980
        """
        return hash(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return self.__str__()

    def __add__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            return RealNum(self.value + other.value)

    def __sub__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            return RealNum(self.value - other.value)

    def __mul__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            return RealNum(self.value * other.value)

    def __truediv__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return Integer(1) / other.__truediv__(self)
        else:
            return RealNum(self.value / other.value)

    def __neg__(self) -> RealNum:
        return RealNum(-self.value)

    def __lt__(self, other: Number) -> bool:
        return self.value < other.value

    def is_integer(self) -> bool:
        return type(self.value) is int or self.value.is_integer()

    def is_zero(self) -> bool:
        return self.value == 0


class InexactNum(RealNum):

    def __init__(self, value: float) -> None:
        super().__init__(value)

    @property
    def precedence(self) -> int:
        return 4

    def __add__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            return InexactNum(self.value + other.value)

    def __sub__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            return InexactNum(self.value - other.value)

    def __mul__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            return InexactNum(self.value * other.value)

    def __truediv__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return Integer(1) / other.__truediv__(self)
        else:
            return InexactNum(self.value / other.value)

    def __iadd__(self, other): ...

    def __neg__(self) -> InexactNum:
        return InexactNum(-self.value)

    def __abs__(self) -> InexactNum:
        return InexactNum(abs(self.value))


class ExactNum(RealNum):

    def __init__(self, numerator: int, denominator: int = 1) -> None:
        super().__init__(numerator if denominator == 1 else numerator / denominator)

    @property
    def precedence(self) -> int:
        return 3


class RationalNum(ExactNum):

    @property
    def precedence(self) -> int:
        return 2

    @property
    def numerator(self) -> int:
        return self._numerator

    @property
    def denominator(self) -> int:
        return self._denominator

    def __init__(self, numerator: int, denominator: int) -> None:
        super().__init__(numerator, denominator)
        self._numerator = numerator
        self._denominator = denominator

    def __str__(self) -> str:
        return f'{self.numerator}/{self.denominator}'

    def __add__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            other_type = type(other)
            is_other_integer = issubclass(other_type, Integer)
            if is_other_integer:
                denominator = self.denominator
                numerator = self.numerator + (denominator * other.value)
                fraction = f.Fraction(numerator, denominator)
                return RationalNum(fraction.numerator, fraction.denominator)
            else:
                numerator = (self.numerator * other.denominator) + (self.denominator * other.numerator)
                denominator = self.denominator * other.denominator
                fraction = f.Fraction(numerator, denominator)
                if fraction.denominator == 1:
                    return Integer(fraction.numerator)
                else:
                    return RationalNum(fraction.numerator, fraction.denominator)

    def __sub__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            other_type = type(other)
            is_other_integer = issubclass(other_type, Integer)
            if is_other_integer:
                denominator = self.denominator
                numerator = self.numerator - (denominator * other.value)
                fraction = f.Fraction(numerator, denominator)
                return RationalNum(fraction.numerator, fraction.denominator)
            else:
                numerator = (self.numerator * other.denominator) - (self.denominator * other.numerator)
                denominator = self.denominator * other.denominator
                fraction = f.Fraction(numerator, denominator)
                if fraction.denominator == 1:
                    return Integer(fraction.numerator)
                else:
                    return RationalNum(fraction.numerator, fraction.denominator)

    def __mul__(self, other: Number) -> Number:
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
                return RationalNum(fraction.numerator, fraction.denominator)

    def __truediv__(self, other: Number) -> Number:
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
                return RationalNum(fraction.numerator, fraction.denominator)

    def __iadd__(self, other): ...

    def __neg__(self) -> RationalNum:
        fraction = f.Fraction(-self.numerator, self.denominator)
        return RationalNum(fraction.numerator, fraction.denominator)

    def __abs__(self) -> RationalNum:
        numerator = abs(self.numerator)
        denominator = abs(self.denominator)
        return RationalNum(numerator, denominator)


class Integer(ExactNum):

    @property
    def precedence(self) -> int:
        return 1

    @property
    def numerator(self) -> int:
        return self.value

    @property
    def denominator(self) -> int:
        return 1

    def __init__(self, value: int) -> None:
        super().__init__(value)

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return other.__add__(self)
        else:
            return Integer(self.value + other.value)

    def __sub__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return -other.__sub__(self)
        else:
            return Integer(self.value - other.value)

    def __mul__(self, other: Number) -> Number:
        if other.precedence > self.precedence:
            return other.__mul__(self)
        else:
            return Integer(self.value * other.value)

    def __truediv__(self, other: Number) -> Number:
        other_type = type(other)
        if issubclass(other_type, RationalNum):
            numerator = self.value * other.denominator
            denominator = other.numerator
            fraction = f.Fraction(numerator, denominator)
        elif issubclass(other_type, Integer):
            numerator = self.value
            denominator = other.value
            fraction = f.Fraction(numerator, denominator)
        else:
            return InexactNum(self.value / other.value)

        if fraction.denominator == 1:
            return Integer(fraction.numerator)
        else:
            return RationalNum(fraction.numerator, fraction.denominator)

    def __iadd__(self, other): ...

    def __neg__(self) -> Integer:
        return Integer(-self.value)

    def __abs__(self) -> Integer:
        return Integer(abs(self.value))


# the natural numbers are defined starting at zero
class NaturalNum(Integer):

    # TODO: raise an error in init if not nat
    pass
