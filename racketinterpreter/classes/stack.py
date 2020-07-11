from __future__ import annotations
from enum import Enum
import typing as tp
from racketinterpreter.constants import C
from racketinterpreter.errors import IllegalStateError, TailEndRecursion

if tp.TYPE_CHECKING:
    from racketinterpreter.classes.data import Data
    from racketinterpreter.processes import Interpreter


class ARType(Enum):
    """The type of an activation record."""

    PROGRAM = 'PROGRAM',
    PROCEDURE = 'PROCEDURE'


class ActivationRecord:
    """A record in the stack.

    An activation record is created whenever there is need to assign values to names temporarily, e.g. assigning
    actual parameters to formal parameters when calling a procedure, or initializing builtin procedures to the global
    scope.

    :ivar str name: The name of the record, either the procedure name or 'global' for the global scope.
    :ivar ARType type: The type of activation record.
    :ivar int nesting_level: The number of activation records below this one.
    :ivar dict members: A mapping of names to values in the record.

    .. automethod:: __setitem__
    .. automethod:: __getitem__
    """

    def __init__(self, name: str, type: ARType, nesting_level: int) -> None:
        self.name = name
        self.type = type
        self.nesting_level = nesting_level
        self.members = {}

        self.interpreter = None

    def __setitem__(self, key: str, value: Data) -> None:
        """Define a name within this record.

        :param str key: The name to be defined.
        :param Data value: The value of the name.

        """
        self.members[key] = value

    def __getitem__(self, key: str) -> Data:
        """Retrieve the value assigned to a name within this record.

        :param str key: The name whose value to return.
        :return: The value assigned to the name.
        :rtype: Data
        :raises KeyError: If there is no value assigned to the name.
        """
        return self.members[key]

    def __str__(self) -> str:
        lines = [
            '{level}: {type} {name}'.format(
                level=self.nesting_level,
                type=self.type.value,
                name=self.name,
            )
        ]
        for name, val in self.members.items():
            lines.append(f'   {name:<20}: {val}')

        s = '\n'.join(lines)
        return s

    def __repr__(self) -> str:
        return self.__str__()

    def __call__(self, interpreter: Interpreter):
        self.interpreter = interpreter

        return self

    def __enter__(self):
        if self.interpreter:
            self.interpreter.call_stack.push(self)

            self.log_stack('')
            self.log_stack(f'ENTER: {self.type.value}')
            self.log_stack(str(self.interpreter.call_stack))

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None and exc_type is not TailEndRecursion:
            return

        if self.interpreter:
            self.interpreter.call_stack.pop()

            self.log_stack(f'LEAVE: {self.type.value}')
            self.log_stack(str(self.interpreter.call_stack))
            self.log_stack('')

            self.interpreter = None

    def get(self, key) -> tp.Optional[Data]:
        return self.members.get(key)

    @staticmethod
    def log_stack(msg: str) -> None:
        """Log messages related to the stack.

        If the global constant SHOULD_LOG_STACK is set to True, this method will print out the message.

        :param msg: The message to be displayed.
        """
        if C.SHOULD_LOG_STACK:
            print(msg)


class CallStack:

    def __init__(self) -> None:
        self._records = []

    def __str__(self) -> str:
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n{s}'
        return s

    def __repr__(self) -> str:
        return self.__str__()

    def get(self, key) -> Data:
        for ar in reversed(self._records):
            value = ar.get(key)
            if value is not None:
                return value
        raise IllegalStateError('Accessing undefined variables should have raised an error during semantic analysis.')

    def push(self, ar: ActivationRecord) -> None:
        self._records.append(ar)

    def pop(self) -> ActivationRecord:
        return self._records.pop()

    def peek(self, levels: int = 1) -> ActivationRecord:
        return self._records[-1 * levels]
