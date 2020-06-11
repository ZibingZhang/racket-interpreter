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


class Bool(AST):
    """A boolean."""

    def __init__(self, boolean: Token) -> None:
        self.token = boolean
        self.value = boolean.value

    def __str__(self) -> str:
        return f'<Bool value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Int(AST):
    """A number."""

    def __init__(self, number: Token) -> None:
        self.token = number
        self.value = number.value

    def __str__(self) -> str:
        return f'<Int value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Str(AST):
    """A string."""

    def __init__(self, string: Token) -> None:
        self.token = string
        self.value = string.value

    def __str__(self) -> str:
        return f'<Str value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Rat(AST):
    """A rational number."""

    def __init__(self, number: Token) -> None:
        self.token = number
        self.value = number.value

    def __str__(self) -> str:
        return f'<Rat value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Dec(AST):
    """A decimal number."""

    def __init__(self, number: Token) -> None:
        self.token = number
        self.value = number.value

    def __str__(self) -> str:
        return f'<Dec value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Const(AST):
    """A constant value."""

    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value

    def __str__(self) -> str:
        return f'<Const value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class ConstAssign(AST):
    """Defining a constant."""

    def __init__(self, identifier: Token, expr: AST) -> None:
        self.token = identifier
        self.identifier = identifier.value
        self.expr = expr

    def __str__(self) -> str:
        return f'<ConstAssign id:{self.identifier}  expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class Param(AST):
    """A parameter."""
    def __init__(self, param: Token) -> None:
        self.token = param
        self.name = param.value

    def __str__(self) -> str:
        return f'<Param name:{self.name}>'

    def __repr__(self) -> str:
        return self.__str__()


class ProcAssign(AST):
    """Defining a function."""

    def __init__(self, identifier: Token, params: List[Param], expr: AST) -> None:
        self.token = identifier
        self.identifier = identifier.value
        self.params = params
        self.expr = expr

    def __str__(self) -> str:
        return f'<ProcAssign id:{self.identifier}  params:{self.params}  expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class ProcCall(AST):
    """A procedure and a list of arguments."""

    def __init__(self, proc: Token, actual_params: Optional[List[AST]] = None) -> None:
        self.token = self.original_token = proc
        self.proc_name = proc.value
        self.actual_params = actual_params

    def __str__(self) -> str:
        return f'<ProcCall proc_name:{self.proc_name}  actual_params:{self.actual_params}>'

    def __repr__(self) -> str:
        return self.__str__()

    def append(self, arg: AST) -> None:
        self.actual_params.append(arg)


class Program(AST):
    """A list of statements."""

    def __init__(self, statements: List[AST]) -> None:
        self.statements = statements

    def __str__(self) -> str:
        return f'<Program statements:{self.statements}>'

    def __repr__(self) -> str:
        return self.__str__()


class CondElse(AST):
    """The else cond branch."""

    def __init__(self, token: Token, expr: AST):
        self.token = token
        self.expr = expr

    def __str__(self) -> str:
        return f'<CondBranch  expr{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class CondBranch(AST):
    """A cond branch with a condition."""

    def __init__(self, token: Token, predicate: AST, expr: AST):
        self.token = token
        self.predicate = predicate
        self.expr = expr

    def __str__(self) -> str:
        return f'<CondBranch predicate:{self.predicate}  expr{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class Cond(AST):
    """A cond statement."""

    def __init__(self, token: Token, branches: List[CondBranch], else_branch: Optional[CondElse] = None) -> None:
        self.token = token
        self.branches = branches
        self.else_branch = else_branch

    def __str__(self) -> str:
        return f'<Cond branches:{self.branches}  else_branch{self.else_branch}>'

    def __repr__(self) -> str:
        return self.__str__()
