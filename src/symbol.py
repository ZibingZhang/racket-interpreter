from __future__ import annotations
from collections import OrderedDict
from typing import List, Optional


class Symbol:

    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return issubclass(type(other), Symbol) and self.name == other.name


class ScopedSymbolTable:

    def __init__(self, scope_name: str, scope_level: int,
                 enclosing_scope: ScopedSymbolTable = None) -> None:
        self._symbols = OrderedDict()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

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

    def define(self, symbol: Symbol) -> None:
        print(f'Define: {symbol}')
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        print(f'Lookup: {name} (Scope Name: {self.scope_name})')
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

        return symbol


class ConstSymbol(Symbol):

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __str__(self) -> str:
        return f'<ConstSymbol name:{self.name}>'

    def __repr__(self) -> str:
        return self.__str__()


class FuncSymbol(Symbol):

    def __init__(self, name: str, params: Optional[List[ConstSymbol]] = None) -> None:
        super().__init__(name)
        self.params = params if params is not None else []

    # def __init__(self, name: str):
    #     super().__init__(name)

    def __str__(self) -> str:
        return f'<ProcedureSymbol name={self.name}>'

    def __repr__(self) -> str:
        return self.__str__()

