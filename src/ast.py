from __future__ import annotations
import abc
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from src.token import Token


class AST(abc.ABC):
    """An abstract syntax tree."""

    pass


class Func(AST):
    """An operator and a list of nodes."""

    def __init__(self, op: Token, nodes: List[AST] = None) -> None:
        self.token = self.op = op
        self.nodes = [] if nodes is None else nodes

    def __str__(self):
        return f'<Func nodes:{str(self.nodes)}>'

    def __repr__(self):
        return self.__str__()

    def append(self, node: AST) -> None:
        self.nodes.append(node)


class Num(AST):
    """A single number."""

    def __init__(self, number: Token) -> None:
        self.token = number
        self.value = number.value

    def __str__(self):
        return f'<Num num:{self.value}>'

    def __repr__(self):
        return self.__str__()


class Compound(AST):
    """A list of statements."""

    def __init__(self, children: List[AST]):
        self.children = children


class Define(AST):
    """Define statement."""

    def __init__(self, op: Token, identifier: str, value: Any):
        self.token = self.op = op
        self.identifier = identifier
        self.value = value


class Var(AST):
    """A variable."""

    def __init__(self, token: Token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    """Any empty statement."""

    pass
