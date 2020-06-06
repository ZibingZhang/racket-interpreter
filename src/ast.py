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
        visit_func = getattr(self, method_name, self.visit_error)
        return visit_func(node)

    def visit_error(self, node) -> None:
        raise Exception(f'No visit_{type(node).__name__} method.')


class ProcCall(AST):
    """A procedure and a list of arguments."""

    def __init__(self, proc: Token, actual_params: Optional[List[AST]] = None) -> None:
        self.token = proc
        self.proc_name = proc.value
        self.actual_params = actual_params
        # a reference to procedure declaration symbol
        self.proc_symbol = None

    def __str__(self) -> str:
        return f'<ProcCall proc_name:{self.proc_name}  actual_params:{self.actual_params}>'

    def __repr__(self) -> str:
        return self.__str__()

    def append(self, arg: AST) -> None:
        self.actual_params.append(arg)


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

    def __init__(self, identifier: Token, expr: AST) -> None:
        self.token = identifier
        self.identifier = identifier.value
        self.expr = expr


class ProcAssign(AST):
    """Defining a function."""

    def __init__(self, identifier: Token, params: List[Param], expr: AST) -> None:
        self.token = identifier
        self.identifier = identifier.value
        self.params = params
        self.expr = expr


class Const(AST):
    """A constant value."""

    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value


class NoOp(AST):
    """Any empty statement."""

    pass


class Param(AST):
    """A parameter."""
    def __init__(self, const_node: Token):
        self.const_node = const_node
