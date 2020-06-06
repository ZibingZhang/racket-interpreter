from __future__ import annotations
from typing import TYPE_CHECKING
from src.ast import ASTVisitor
from src.symbol import SymbolTable, IdentifierSymbol, IdentifierTypeSymbol

if TYPE_CHECKING:
    from src.ast import Func, Num, ConstAssign, Var, NoOp, Program


class SemanticAnalyzer(ASTVisitor):

    def __init__(self):
        self.sym_table = SymbolTable()

    def visit_Func(self, node: Func) -> None:
        for arg in node.nodes:
            self.visit(arg)

    def visit_Num(self, node: Num) -> None:
        pass

    def visit_Bool(self, node: Num) -> None:
        pass

    def visit_Str(self, node: Num) -> None:
        pass

    def visit_ConstAssign(self, node: ConstAssign) -> None:
        type_symbol = IdentifierTypeSymbol('CONSTANT')
        self.sym_table.define(type_symbol)

        var_name = node.identifier
        var_symb = IdentifierSymbol(var_name, type_symbol)

        if self.sym_table.lookup(var_name) is not None:
            raise NameError(f'Error: \'{var_name}\' was defined previously and cannot be re-defined.')

        self.sym_table.define(var_symb)

    def visit_FuncAssign(self, node: ConstAssign) -> None:
        type_symbol = IdentifierTypeSymbol('FUNCTION')
        self.sym_table.define(type_symbol)

        var_name = node.identifier
        var_symb = IdentifierSymbol(var_name, type_symbol)

        if self.sym_table.lookup(var_name) is not None:
            raise NameError(f'Error: \'{var_name}\' was defined previously and cannot be re-defined.')

        self.sym_table.define(var_symb)

    def visit_Var(self, node: Var) -> None:
        var_name = node.value
        var_symbol = self.sym_table.lookup(var_name)
        if var_symbol is None:
            raise NameError(f'Error: Symbol(variable) not found \'{var_name}\'')

    def visit_NoOp(self, node: NoOp) -> None:
        pass

    def visit_Program(self, node: Program) -> None:
        for child_node in node.children:
            self.visit(child_node)
