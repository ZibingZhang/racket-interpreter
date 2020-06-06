from __future__ import annotations
from functools import reduce
from typing import TYPE_CHECKING, Any, List, Optional
from src.ast import ASTVisitor
from src.datatype import Boolean, Number, String
from src.token import TokenType

if TYPE_CHECKING:
    from src.ast import AST, ConstAssign, Func, FuncAssign, NoOp, Num, Program, Const
    from src.datatype import DataType


class InterpreterError(Exception):

    pass


class Interpreter(ASTVisitor):

    GLOBAL_MEMORY = dict()

    def __init__(self, tree: Optional[AST] = None) -> None:
        self.tree = tree

    def visit_Func(self, node: Func) -> DataType:
        op = node.op
        if op.type == TokenType.PLUS:
            if len(node.nodes) == 0:
                return Number(0)
            else:
                initial = 0
                iterable = node.nodes
                result = reduce(lambda acc, x: acc + self.visit(x), iterable, initial)
                return Number(result)
        elif op.type == TokenType.MINUS:
            if len(node.nodes) == 1:
                return Number(-self.visit(node.nodes[0]))
            else:
                initial = self.visit(node.nodes[0])
                iterable = node.nodes[1:]
                result = reduce(lambda acc, x: acc - self.visit(x), iterable, initial)
                return Number(result)
        elif op.type == TokenType.MUL:
            if len(node.nodes) == 0:
                return Number(1)
            else:
                initial = 1
                iterable = node.nodes
                result = reduce(lambda acc, x: acc * self.visit(x), iterable, initial)
                return Number(result)
        elif op.type == TokenType.DIV:
            if len(node.nodes) == 1:
                return Number(1/self.visit(node.nodes[0]))
            else:
                initial = self.visit(node.nodes[0])
                iterable = node.nodes[1:]
                result = reduce(lambda acc, x: acc / self.visit(x), iterable, initial)
                return Number(result)
        elif op.type == TokenType.ID:
            if op.value == 'add1':
                return self.visit(node.nodes[0]) + Number(1)
            else:
                # TODO: look up in memory, then error if not there
                raise InterpreterError(f'Error: function \'{op.value}\' not defined.')
        else:
            raise InterpreterError(f'Error: method visit_Func does not handle operator of type {op.type}.')

    def visit_Num(self, node: Num) -> Number:
        return Number(node.value)

    def visit_Bool(self, node: Num) -> Boolean:
        return Boolean(node.value)

    def visit_Str(self, node: Num) -> String:
        return String(node.value)

    def visit_ConstAssign(self, node: ConstAssign) -> None:
        var_name = node.identifier
        self.GLOBAL_MEMORY[var_name] = self.visit(node.expr)

    def visit_FuncAssign(self, node: FuncAssign) -> None:
        pass

    def visit_Const(self, node: Const) -> DataType:
        var_name = node.value
        val = self.GLOBAL_MEMORY.get(var_name)
        return val

    def visit_NoOp(self, node: NoOp) -> None:
        pass

    def visit_Program(self, node: Program) -> List[DataType]:
        result = []
        for child_node in node.children:
            value = self.visit(child_node)
            if value is not None:
                result.append(value)
        return result

    def interpret(self) -> Any:
        tree = self.tree
        return self.visit(tree)
