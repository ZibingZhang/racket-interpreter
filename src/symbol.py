from __future__ import annotations
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Optional
from src.ast import ASTVisitor
from src.interpreter import Interpreter

if TYPE_CHECKING:
    from src.ast import ConstAssign, Func, NoOp, Num, Program, Var


class Symbol:

    def __init__(self, name: str, sym_type: Any = None) -> None:
        self.name = name
        self.type = sym_type

    def __hash__(self):
        return hash(self.name) + hash(self.type)

    def __eq__(self, other):
        return issubclass(type(other), Symbol) and self.name == other.name and self.type == other.type


class SymbolTable:

    def __init__(self) -> None:
        self._symbols = OrderedDict()

    def __str__(self) -> str:
        sym_table_header = 'Symbol Table Contents'
        lines = [sym_table_header]
        lines.extend(
            f'{key:>10}: {value}'
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    def __repr__(self) -> str:
        return self.__str__()

    def define(self, symbol: Symbol) -> None:
        print(f'Define: {symbol}')
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        print(f'Lookup: {name}')
        symbol = self._symbols.get(name)
        return symbol


class IdentifierTypeSymbol(Symbol):

    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self):
        return f'<BuiltinTypeSymbol name:{self.name}>'

    def __repr__(self):
        return self.__str__()


class IdentifierSymbol(Symbol):

    def __init__(self, name: str, sym_type: Symbol):
        super().__init__(name, sym_type)

    def __str__(self):
        return f'<VarSymbol name:{self.name} type:{self.type}>'

    def __repr__(self):
        return self.__str__()
