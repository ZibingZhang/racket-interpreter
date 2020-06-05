from __future__ import annotations
import abc
from functools import reduce
from typing import TYPE_CHECKING
from src.token import TokenType

if TYPE_CHECKING:
    from src.ast import AST, Func, Num
    from src.parser import Parser


class ASTVisitor(abc.ABC):

    def visit(self, node: AST):
        method_name = 'visit_' + type(node).__name__
        visit_func = getattr(self, method_name, self.error)
        return visit_func(node)

    def error(self, node):
        raise Exception(f'No visit_{type(node).__name__} method.')


class InterpreterError(Exception):

    pass


class Interpreter(ASTVisitor):

    def __init__(self, parser: Parser):
        self.parser = parser

    def visit_Func(self, node: Func):
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

    def visit_Num(self, node: Num):
        return node.value

    def interpret(self):
        ast = self.parser.parse()
        return self.visit(ast)
