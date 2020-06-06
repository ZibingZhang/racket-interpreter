from __future__ import annotations
import abc
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from src.token import Token


class AST(abc.ABC):
    """An abstract syntax tree."""

    pass


class ASTVisitor(abc.ABC):

    def visit(self, node: AST) -> Any:
        method_name = 'visit_' + type(node).__name__
        visit_func = getattr(self, method_name, self.error)
        return visit_func(node)

    def error(self, node) -> None:
        raise Exception(f'No visit_{type(node).__name__} method.')


class Func(AST):
    """An operator and a list of nodes."""

    def __init__(self, op: Token, nodes: Optional[List[AST]] = None) -> None:
        self.token = self.op = op
        self.nodes = [] if nodes is None else nodes

    def __str__(self) -> str:
        return f'<Func op:{self.op} nodes:{self.nodes}>'

    def __repr__(self) -> str:
        return self.__str__()

    def append(self, node: AST) -> None:
        self.nodes.append(node)


class Num(AST):
    """A number."""

    def __init__(self, number: Token) -> None:
        self.token = number
        self.value = number.value

    def __str__(self) -> str:
        return f'<Num num:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Bool(AST):
    """A boolean."""

    def __init__(self, boolean: Token) -> None:
        self.token = boolean
        self.value = boolean.value


class Str(AST):
    """A string."""

    def __init__(self, string: Token) -> None:
        self.token = string
        self.value = string.value


class Program(AST):
    """A list of statements."""

    def __init__(self, children: List[AST]) -> None:
        self.children = children


class ConstAssign(AST):
    """Defining a constant."""

    def __init__(self, identifier: str, expr: AST) -> None:
        self.identifier = identifier
        self.expr = expr


class FuncAssign(AST):
    """Defining a function."""

    def __init__(self, identifier: str, params: List[Param], expr: AST) -> None:
        self.identifier = identifier
        self.params = params
        self.expr = expr


class Const(AST):
    """A const."""

    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value


class NoOp(AST):
    """Any empty statement."""

    pass


class FuncDecl(AST):
    """Function declaration."""

    def __init__(self, identifier: str, expr):
        pass


class Param(AST):
    """A parameter."""
    def __init__(self, const_node: Token):
        self.const_node = const_node
