from __future__ import annotations
import abc
from enum import Enum
import typing as tp
from racketinterpreter import errors as err

if tp.TYPE_CHECKING:
    import racketinterpreter.classes.data as d
    import racketinterpreter.classes.tokens as t


class AST(abc.ABC):
    """An abstract syntax tree."""

    def __init__(self, token: tp.Optional[t.Token]):
        self.token = token
        self.passed_semantic_analysis = False


class Expr(AST):
    """An expression."""

    def __init__(self, token: t.Token, value: tp.Any = None):
        super().__init__(token)
        self._value = value

    @property
    def value(self):
        if self._value is None:
            raise err.IllegalStateError('The value of the expression has not been interpreted yet.')
        return self._value


class List(AST):
    """A list."""


class StructProc(Expr):
    """A proc related to a struct."""

    def __init__(self, token: t.Token, data_type: d.DataType):
        super().__init__(token)
        self.data_type = data_type


class ASTVisitor(abc.ABC):

    def visit(self, node: AST) -> tp.Any:
        method_name = 'visit_' + type(node).__name__
        visit_func = getattr(self, method_name, self.visit_error)
        return visit_func(node)

    def visit_error(self, node) -> None:
        raise err.IllegalStateError(
            f'{self.__class__.__name__} should never have to visit a {node.__class__.__name__}.'
        )


class Bool(Expr):
    """A boolean."""

    def __init__(self, token: t.Token) -> None:
        super().__init__(token, token.value)

    def __str__(self) -> str:
        return f'<Bool value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Dec(Expr):
    """A decimal number."""

    def __init__(self, token: t.Token) -> None:
        super().__init__(token, token.value)

    def __str__(self) -> str:
        return f'<Dec value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Int(Expr):
    """A number."""

    def __init__(self, token: t.Token) -> None:
        super().__init__(token, token.value)

    def __str__(self) -> str:
        return f'<Int value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Name(Expr):
    """A name."""

    def __init__(self, token: t.Token) -> None:
        super().__init__(token, token.value)

    def __str__(self) -> str:
        return f'<Name value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Rat(Expr):
    """A rational number."""

    def __init__(self, token: t.Token) -> None:
        super().__init__(token, token.value)

    def __str__(self) -> str:
        return f'<Rat value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Str(Expr):
    """A string."""

    def __init__(self, token: t.Token) -> None:
        super().__init__(token, token.value)

    def __str__(self) -> str:
        return f'<Str value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Sym(Expr):
    """A symbol."""

    def __init__(self, token: t.Token) -> None:
        super().__init__(token, token.value)

    def __str__(self) -> str:
        return f'<Sym value:{self.value}>'

    def __repr__(self) -> str:
        return self.__str__()


class Cons(List):
    """A non-empty list."""

    def __init__(self, token: t.Token, exprs: tp.List[Expr]) -> None:
        super().__init__(token)
        self.exprs = exprs

        self.first = None
        self.rest = None

    def __str__(self) -> str:
        return f'<Cons first:{self.first}  rest:{self.rest}>'

    def __repr__(self) -> str:
        return self.__str__()


class Cond(Expr):
    """A cond statement."""

    def __init__(self, token: t.Token, exprs: tp.List[Expr]) -> None:
        super().__init__(token)
        self.exprs = exprs

        self.branches = []
        self.else_branch = None

    def __str__(self) -> str:
        return f'<Cond branches:{self.branches}  else_branch{self.else_branch}>'

    def __repr__(self) -> str:
        return self.__str__()


class CondBranch(Expr):
    """A cond branch with a condition."""

    def __init__(self, token: t.Token, exprs: tp.List[Expr]):
        super().__init__(token)
        self.exprs = exprs

        self.predicate = None
        self.expr = None

    def __str__(self) -> str:
        return f'<CondBranch predicate:{self.predicate}  expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class CondElse(Expr):
    """The else cond branch."""

    def __init__(self, token: t.Token, expr: Expr):
        super().__init__(token)
        self.expr = expr

    def __str__(self) -> str:
        return f'<CondElse expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class NameAssign(AST):
    """Assigning value to a name."""

    def __init__(self, token: t.Token, exprs: tp.List[Expr]) -> None:
        super().__init__(token)
        self.exprs = exprs
        self.identifier = None
        self.expr = None

    def __str__(self) -> str:
        return f'<NameAssign id:{self.identifier}  expr:{self.expr}>'

    def __repr__(self) -> str:
        return self.__str__()


class FormalParam(AST):
    """A formal parameter in a procedure or structure."""

    class ParamFor(Enum):

        PROC_ASSIGN = 'PROC_ASSIGN'
        STRUCT_ASSIGN = 'STRUCT_ASSIGN'

    def __init__(self, ast: AST, param_for: ParamFor) -> None:
        super().__init__(ast.token)
        self.ast = ast
        self.param_for = param_for

        self.name = None

    def __str__(self) -> str:
        return f'<FormalParam name:{self.name}  param_for:{self.param_for}>'

    def __repr__(self) -> str:
        return self.__str__()


class ProcAssign(AST):
    """Defining a procedure."""

    def __init__(self, token: t.Token, name_expr: Expr, formal_params: tp.List[FormalParam], exprs: tp.List[Expr]) -> None:
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

    def __init__(self, token: t.Token, exprs: tp.List[Expr]) -> None:
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

    def __init__(self, token: t.Token) -> None:
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


class StructHuh(StructProc):
    """A [structure-name]? procedure."""


class StructGet(StructProc):
    """A [structure-name]-[field] procedure."""


class CheckExpect(AST):
    """A test.

    The first expression is the actual value and the second expression is the expected value.
    """

    def __init__(self, token: t.Token, exprs: tp.List[Expr]):
        super().__init__(token)
        self.exprs = exprs

        self.actual = None
        self.expected = None


class Program(AST):
    """A list of statements."""

    def __init__(self, statements: tp.List[AST]) -> None:
        super().__init__(None)
        self.statements = statements

    def __str__(self) -> str:
        return f'<Program statements:{self.statements}>'

    def __repr__(self) -> str:
        return self.__str__()
