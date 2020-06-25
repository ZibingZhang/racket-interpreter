from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Optional
from racketinterpreter.errors import IllegalStateError

if TYPE_CHECKING:
    from classes.data import Data


class ARType(Enum):
    PROGRAM = 'PROGRAM',
    PROCEDURE = 'PROCEDURE'


class ActivationRecord:
    def __init__(self, name: str, type: ARType, nesting_level: int) -> None:
        self.name = name
        self.type = type
        self.nesting_level = nesting_level
        self.members = {}

    def __setitem__(self, key: str, value: Data) -> None:
        self.members[key] = value

    def __getitem__(self, key: str) -> Data:
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

    def get(self, key) -> Optional[Data]:
        return self.members.get(key)


class CallStack:
    def __init__(self) -> None:
        self._records = []

    def __str__(self) -> str:
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n{s}'
        return s

    def __repr__(self):
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

    def peek(self) -> ActivationRecord:
        return self._records[-1]