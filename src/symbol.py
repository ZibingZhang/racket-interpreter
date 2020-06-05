from __future__ import annotations
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Optional
from src.ast import ASTVisitor
from src.interpreter import Interpreter

if TYPE_CHECKING:
    from src.ast import Define, Func, NoOp, Num, Program, Var


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
        self._init_builtins()

    def _init_builtins(self) -> None:
        self.define(BuiltinTypeSymbol('NUMBER'))
        self.define(BuiltinTypeSymbol('BOOLEAN'))
        self.define(BuiltinTypeSymbol('STRING'))
        self.define(BuiltinTypeSymbol('CHARACTER'))

    def __str__(self) -> str:
        symbols = [value for value in self._symbols.values()]
        return f'<SymbolTable symbols:{symbols}>'

    def __repr__(self) -> str:
        return self.__str__()

    def define(self, symbol: Symbol) -> None:
        print(f'Define: {symbol}.')
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        print(f'Lookup: {name}')
        symbol = self._symbols.get(name)
        return symbol


class SymbolTableBuilder(ASTVisitor):
    def __init__(self):
        self.sym_table = SymbolTable()

    def visit_Func(self, node: Func) -> None:
        for arg in node.nodes:
            self.visit(arg)

    def visit_Num(self, node: Num) -> None:
        pass

    def visit_Define(self, node: Define) -> None:
        var_name = node.identifier
        var_symb = self.sym_table.lookup(var_name)
        if var_symb is not None:
            raise NameError(f'{var_name}: this name was defined previously and cannot be re-defined.')
        else:
            number_type = BuiltinTypeSymbol('NUMBER')
            self.sym_table.define(VarSymbol(var_name, number_type))
        Interpreter().visit(node.expr)

    def visit_Var(self, node: Var) -> None:
        var_name = node.value
        var_symb = self.sym_table.lookup(var_name)
        if var_symb is None:
            raise NameError(f'{var_name}: this variable is not defined.')

    def visit_NoOp(self, node: NoOp) -> None:
        pass

    def visit_Program(self, node: Program) -> None:
        for child_node in node.children:
            self.visit(child_node)


class BuiltinTypeSymbol(Symbol):

    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self):
        return f'<BuiltinTypeSymbol name:{self.name}>'

    def __repr__(self):
        return self.__str__()


class VarSymbol(Symbol):

    def __init__(self, name: str, sym_type: BuiltinTypeSymbol):
        super().__init__(name, sym_type)

    def __str__(self):
        return f'<VarSymbol name:{self.name} type:{self.type}>'

    def __repr__(self):
        return self.__str__()
