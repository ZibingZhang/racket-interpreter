from __future__ import annotations
from collections import OrderedDict
import typing as tp
from racketinterpreter.constants import C
from racketinterpreter.predefined import BUILT_IN_PROCS


class Symbol:

    def __init__(self, name: str, type: tp.Any = None) -> None:
        self.name = name
        self.type = type
        self.scope_level = 0

    def __hash__(self) -> int:
        return hash(self.name) + hash(self.type)

    def __eq__(self, other) -> bool:
        return issubclass(type(other), Symbol) and self.name == other.name and self.type == other.type


class ScopedSymbolTable:

    def __init__(self, scope_name: str, scope_level: int,
                 enclosing_scope: ScopedSymbolTable = None) -> None:
        self._symbols = OrderedDict()

        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

        if scope_level == 0:
            self.init_builtin_procs()

    def __str__(self) -> str:
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = [h1]

        for header_name, header_value in (
                ('Scope name', self.scope_name),
                ('Scope level', self.scope_level),
                ('Enclosing scope', self.enclosing_scope.scope_name if self.enclosing_scope else None)
        ):
            lines.append('%-15s: %s' % (header_name, header_value))

        h2 = 'Scope (Scoped Symbol Table) Contents:'
        lines.append(h2)
        lines.extend(
            f'{key:>10}: {value}'
            for key, value in self._symbols.items()
        )

        s = '\n'.join(lines)
        return s

    def __repr__(self) -> str:
        return self.__str__()

    def init_builtin_procs(self) -> None:
        for proc in BUILT_IN_PROCS.keys():
            self._symbols[proc] = ProcSymbol(proc)

    def define(self, symbol: Symbol) -> None:
        self.log_scope(f'Define: {symbol}')

        symbol.scope_level = self.scope_level

        self._symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only: bool = False) -> tp.Optional[Symbol]:
        self.log_scope(f'Lookup: {name} (Scope Name: {self.scope_name})')
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

        return symbol

    @staticmethod
    def log_scope(msg: str) -> None:
        if C.SHOULD_LOG_SCOPE:
            print(msg)


class AmbiguousSymbol(Symbol):
    """Either a procedure or data."""

    def __init__(self, name: str) -> None:
        super().__init__(name, 'AMBIGUOUS')

    def __str__(self) -> str:
        return f'<AmbiguousSymbol name:{self.name}>'

    def __repr__(self) -> str:
        return self.__str__()


class ProcSymbol(Symbol):
    """A procedure."""

    def __init__(self, name: str, formal_params: tp.Optional[tp.List[AmbiguousSymbol]] = None) -> None:
        super().__init__(name, 'PROCEDURE')
        self.formal_params = formal_params if formal_params is not None else []
        # a reference to procedure's body (AST)
        self.expr = None

    def __str__(self) -> str:
        return f'<ProcSymbol name:{self.name}  formal_params:{self.formal_params}  expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class StructTypeSymbol(Symbol):
    """A structure type."""

    def __init__(self, name: str) -> None:
        super().__init__(name, 'STRUCTURE_TYPE')

    def __str__(self) -> str:
        return f'<StructTypeSymbol name:{self.name}>'

    def __repr__(self) -> str:
        return self.__str__()
