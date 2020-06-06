from enum import Enum


class ARType(Enum):
    PROGRAM = 'PROGRAM',
    PROCEDURE = 'PROCEDURE'


class ActivationRecord:
    def __init__(self, name: str, type: ARType, nesting_level: int):
        self.name = name
        self.type = type
        self.nesting_level = nesting_level
        self.members = {}

    def __setitem__(self, key, value):
        self.members[key] = value

    def __getitem__(self, key):
        return self.members[key]

    def get(self, key):
        return self.members.get(key)

    def __str__(self):
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

    def __repr__(self):
        return self.__str__()


class CallStack:
    def __init__(self):
        self._records = []

    def __str__(self):
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n{s}'
        return s

    def __repr__(self):
        return self.__str__()

    def push(self, ar: ActivationRecord):
        self._records.append(ar)

    def pop(self) -> ActivationRecord:
        return self._records.pop()

    def peek(self) -> ActivationRecord:
        return self._records[-1]

    def get(self, key):
        for ar in reversed(self._records):
            value = ar.get(key)
            if value is not None:
                return value
