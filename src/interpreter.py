from __future__ import annotations
from functools import reduce
from typing import TYPE_CHECKING, Any, List, Optional
from src.ast import ASTVisitor
from src.token import TokenType

if TYPE_CHECKING:
    from src.ast import AST, Define, Func, NoOp, Num, Program, Var
    from src.parser import Parser


class InterpreterError(Exception):

    pass


class Interpreter(ASTVisitor):

    GLOBAL_MEMORY = dict()

    def __init__(self, tree: Optional[AST] = None) -> None:
        self.tree = tree

    def visit_Func(self, node: Func) -> float:
        op = node.op
        if op.type == TokenType.PLUS:
            if len(node.nodes) == 0:
                return 0
            else:
                initial = 0
                iterable = node.nodes
                result = reduce(lambda acc, x: acc + self.visit(x), iterable, initial)
                return result
        elif op.type == TokenType.MINUS:
            if len(node.nodes) == 1:
                return -self.visit(node.nodes[0])
            else:
                initial = self.visit(node.nodes[0])
                iterable = node.nodes[1:]
                result = reduce(lambda acc, x: acc - self.visit(x), iterable, initial)
                return result
        elif op.type == TokenType.MUL:
            if len(node.nodes) == 0:
                return 1
            else:
                initial = 1
                iterable = node.nodes
                result = reduce(lambda acc, x: acc * self.visit(x), iterable, initial)
                return result
        elif op.type == TokenType.DIV:
            if len(node.nodes) == 1:
                return 1/self.visit(node.nodes[0])
            else:
                initial = self.visit(node.nodes[0])
                iterable = node.nodes[1:]
                result = reduce(lambda acc, x: acc / self.visit(x), iterable, initial)
                return result
        else:
            raise InterpreterError(f'Method visit_Func does not handle operator of type {op.type}.')

    def visit_Num(self, node: Num) -> float:
        return node.value

    def visit_Define(self, node: Define) -> None:
        var_name = node.identifier
        current_val = self.GLOBAL_MEMORY.get(var_name)
        if current_val is not None:
            raise InterpreterError(f'{var_name}: this name was defined previously and cannot be re-defined.')
        else:
            self.GLOBAL_MEMORY[var_name] = self.visit(node.expr)

    def visit_Var(self, node: Var) -> float:
        var_name = node.value
        val = self.GLOBAL_MEMORY.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_NoOp(self, node: NoOp) -> None:
        pass

    def visit_Program(self, node: Program) -> List[str]:
        result = []
        for child_node in node.children:
            value = self.visit(child_node)
            if value is not None:
                result.append(value)
        return result

    def interpret(self) -> Any:
        tree = self.tree
        return self.visit(tree)
