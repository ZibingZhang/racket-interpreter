from __future__ import annotations
from enum import Enum
import typing as tp
from racketinterpreter.classes import data as d
from racketinterpreter.constants import C
from racketinterpreter.errors import IllegalStateError, TailEndRecursion
from racketinterpreter.predefined import BUILT_IN_CONSTANTS, BUILT_IN_PROCS

if tp.TYPE_CHECKING:
    from racketinterpreter.classes.data import Data
    from racketinterpreter.processes import Interpreter


class ARType(Enum):
    """The type of an activation record."""

    BUILTIN = 'BUILTIN'
    PROGRAM = 'PROGRAM',
    PROCEDURE = 'PROCEDURE'


class ActivationRecord:
    """A record in the stack.

    An activation record is created for subroutines. It is especially useful whenever there is a need to assign values
    to names temporarily, e.g. assigning actual parameters to formal parameters when calling a procedure, or
    initializing builtin procedures to the global scope.

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

        if nesting_level == 0:
            self.init_builtins()

    def __setitem__(self, name: str, value: Data) -> None:
        """Define a name within this record.

        :param str name: The name to be defined.
        :param Data value: The value of the name.

        """
        self.members[name] = value

    def __getitem__(self, name: str) -> Data:
        """Retrieve the value assigned to a name within this record.

        :param str name: The name whose value to return.
        :return: The value assigned to the name.
        :rtype: Data
        :raises KeyError: If there is no value assigned to the name.
        """
        return self.members[name]

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

    def init_builtins(self) -> None:
        for const in BUILT_IN_CONSTANTS:
            self[const] = BUILT_IN_CONSTANTS[const]

        for proc in BUILT_IN_PROCS:
            self[proc] = d.Procedure(proc)

    def get(self, key) -> tp.Optional[Data]:
        return self.members.get(key)

    @staticmethod
    def log_stack(msg: str) -> None:
        """Log messages related to the stack.

        If the global constant SHOULD_LOG_STACK is set to True, this method will print out the message.

        :param str msg: The message to be displayed.
        """
        if C.SHOULD_LOG_STACK:
            print(msg)


class CallStack:
    """A call stack.

    A stack data structure that keeps track of a list of activation records. Each activation record represents a
    subroutine. The stack indicates which subroutine will get control after the current one is finished running.
    """

    def __init__(self) -> None:
        self._records = []

    def __str__(self) -> str:
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n{s}'
        return s

    def __repr__(self) -> str:
        return self.__str__()

    def get(self, name: str) -> Data:
        """Retrieves the value assigned to the name.

        The activation records are checked starting with the last one. Once an activation is found that contains a
        value assigned to the name, that value is returned.

        :param str name: The name to lookup.
        :return: The value assigned to the name.
        :rtype: Data
        :raises IllegalStateError: If there is no activation record with a value assigned to the name.
        """
        for ar in reversed(self._records):
            value = ar.get(name)
            if value is not None:
                return value
        raise IllegalStateError('Accessing undefined variables should have raised an error during semantic analysis.')

    def push(self, ar: ActivationRecord) -> None:
        """Push an activation record onto the stack.

        :param ar: An activation record.
        """
        self._records.append(ar)

    def pop(self) -> ActivationRecord:
        """Removes an activation record from the stack.

        :return: An activation record from the top of the stack.
        :rtype: ActivationRecord
        """
        return self._records.pop()

    def peek(self, levels: int = 1) -> ActivationRecord:
        """Look at an activation record at the top of the stack without removing it.

        :param int levels: The ith activation record from the top.
        :return: An activation record counting from the top of the stack.
        :rtype: ActivationRecord
        """
        return self._records[-1 * levels]
