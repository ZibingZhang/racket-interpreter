from __future__ import annotations
import abc
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from racketinterpreter.data import DataType
    from racketinterpreter.tokens import Token


class AST(abc.ABC):
    """An abstract syntax tree."""
    def __init__(self, token: Token):
        self.token = token
        self.passed_semantic_analysis = False

    pass


class Expr(AST):
    """An expression."""

    pass


class StructProc(AST):
    """A proc related to a struct."""

    def __init__(self, data_class: DataType):
        self.data_class = data_class


class ASTVisitor(abc.ABC):

    def visit(self, node: AST) -> Any:
        method_name = 'visit_' + type(node).__name__
        visit_func = getattr(self, method_name, self.visit_error)
        return visit_func(node)

    def visit_error(self, node) -> None:
        raise Exception(f'No visit_{type(node).__name__} method.')


class Bool(Expr):
    """A boolean."""

    def __init__(self, token: Token) -> None:
        super().__init__(token)
        self.value = token.value

    def __str__(self) -> str:
        return f'<Bool value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Dec(Expr):
    """A decimal number."""

    def __init__(self, token: Token) -> None:
        super().__init__(token)
        self.value = token.value

    def __str__(self) -> str:
        return f'<Dec value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Id(Expr):
    """An name."""

    def __init__(self, token: Token) -> None:
        super().__init__(token)
        self.value = token.value

    def __str__(self) -> str:
        return f'<Const value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Int(Expr):
    """A number."""

    def __init__(self, token: Token) -> None:
        super().__init__(token)
        self.value = token.value

    def __str__(self) -> str:
        return f'<Int value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Rat(Expr):
    """A rational number."""

    def __init__(self, token: Token) -> None:
        super().__init__(token)
        self.value = token.value

    def __str__(self) -> str:
        return f'<Rat value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Str(Expr):
    """A string."""

    def __init__(self, token: Token) -> None:
        super().__init__(token)
        self.value = token.value

    def __str__(self) -> str:
        return f'<Str value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Cond(Expr):
    """A cond statement."""

    def __init__(self, token: Token, branches: List[AST], else_branch: Optional[CondElse] = None) -> None:
        super().__init__(token)
        self.branches = branches
        self.else_branch = else_branch

    def __str__(self) -> str:
        return f'<Cond branches:{self.branches}  else_branch{self.else_branch}>'

    def __repr__(self) -> str:
        return self.__str__()


class CondBranch(AST):
    """A cond branch with a condition."""

    def __init__(self, token: Token, exprs: List[AST]):
        super().__init__(token)
        self.exprs = exprs

        self.predicate = None
        self.expr = None

    def __str__(self) -> str:
        return f'<CondBranch predicate:{self.predicate}  expr{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class CondElse(AST):
    """The else cond branch."""

    def __init__(self, token: Token, exprs: List[AST]):
        super().__init__(token)
        self.exprs = exprs

        self.expr = None

    def __str__(self) -> str:
        return f'<CondBranch  expr{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class IdAssign(AST):
    """Defining a constant."""

    def __init__(self, token: Token, actual_params: List[AST]) -> None:
        super().__init__(token)
        self.actual_params = actual_params
        self.identifier = None
        self.expr = None

    def __str__(self) -> str:
        return f'<IdAssign id:{self.identifier}  expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class FormalParam(AST):
    """A formal parameter in a procedure or structure."""

    class ParamFor(Enum):

        PROC_ASSIGN = 'PROC ASSIGN'
        STRUCT_ASSIGN = 'STRUCT ASSIGN'

    """A parameter."""
    def __init__(self, ast: AST, param_for: ParamFor) -> None:
        super().__init__(ast.token)
        self.ast = ast
        self.param_for = param_for

        self.name = None

    def __str__(self) -> str:
        return f'<Param name:{self.name}  param_for:{self.param_for}>'

    def __repr__(self) -> str:
        return self.__str__()


class ProcAssign(AST):
    """Defining a function."""

    def __init__(self, token: Token, name_expr: AST, formal_params: List[FormalParam], exprs: List[AST]) -> None:
        super().__init__(token)

        self.name_expr = name_expr
        self.formal_params = formal_params
        self.exprs = exprs

        self.proc_name = None
        self.expr = None

    def __str__(self) -> str:
        return f'<ProcAssign name:{self.proc_name}  params:{self.formal_params}  expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class ProcCall(Expr):
    """A procedure and a list of arguments."""

    def __init__(self, token: Token, exprs: List[AST]) -> None:
        super().__init__(token)
        self.exprs = exprs

        self.original_proc_token = None
        self.proc_token = None
        self.proc_name = None

        self.actual_params = None

    def __str__(self) -> str:
        return f'<ProcCall proc_name:{self.proc_name}  actual_params:{self.actual_params}>'

    def __repr__(self) -> str:
        return self.__str__()


class StructAssign(AST):
    """Defining a new structure."""

    def __init__(self, token: Token) -> None:
        super().__init__(token)

        self.struct_name_ast = None
        self.field_asts = None
        self.extra_asts = []

        self.struct_name = None
        self.field_names = []

    def __str__(self) -> str:
        return f'<StructAssign struct_name:{self.struct_name}  field_names:{self.field_names}>'

    def __repr__(self) -> str:
        return self.__str__()


class StructMake(StructProc):
    """A make-[structure-name] procedure."""

    pass


class StructHuh(StructProc):
    """A [structure-name]? procedure."""

    pass


class StructGet(StructProc):
    """A [structure-name]-[field] procedure."""

    pass


class Program(AST):
    """A list of statements."""

    def __init__(self, statements: List[AST]) -> None:
        super().__init__(None)
        self.statements = statements

    def __str__(self) -> str:
        return f'<Program statements:{self.statements}>'

    def __repr__(self) -> str:
        return self.__str__()