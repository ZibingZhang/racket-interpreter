from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List
from src.ast import ASTVisitor
from src.builtins import BUILT_IN_PROCS
from src.constants import C
from src.errors import ErrorCode, IllegalStateError, SemanticError
from src.symbol import AmbiguousSymbol, ConstSymbol, ProcSymbol, ScopedSymbolTable
from src.token import Token

if TYPE_CHECKING:
    from src import ast


class SemanticAnalyzer(ASTVisitor):

    def __init__(self):
        self.current_scope = None
        self.interpreter = None

    def visit_Bool(self, node: ast.Bool) -> None:
        pass

    def visit_Int(self, node: ast.Int) -> None:
        pass

    def visit_Str(self, node: ast.Str) -> None:
        pass

    def visit_Rat(self, node: ast.Rat) -> None:
        pass

    def visit_Dec(self, node: ast.Dec) -> None:
        pass

    def visit_Const(self, node: ast.Const) -> None:
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)

        if var_symbol is None:
            self.error(
                error_code=ErrorCode.ID_NOT_FOUND,
                token=node.token,
                message=f"'{node.token.value}'"
            )

    def visit_ConstAssign(self, node: ast.ConstAssign) -> None:
        var_name = node.identifier
        var_symbol = ConstSymbol(var_name)

        if self.current_scope.lookup(var_name, current_scope_only=True) is not None:
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.token,
                message=f"'{node.token.value}'"
            )

        self.visit(node.expr)

        self.current_scope.define(var_symbol)

    def visit_Param(self, node: ast.Param) -> None:
        raise IllegalStateError('Semantic analyzer should never have to visit a parameter.')

    def visit_ProcAssign(self, node: ast.ProcAssign) -> None:
        proc_name = node.identifier
        proc_symbol = ProcSymbol(proc_name)

        if self.current_scope.lookup(proc_name, current_scope_only=True) is not None:
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.token,
                message=f"'{node.token.value}'"
            )

        self.current_scope.define(proc_symbol)

        self.log_scope('')
        self.log_scope(f'ENTER SCOPE: {proc_name}')
        # scope for parameters
        proc_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = proc_scope

        # insert parameters into the procedure scope
        for param_node in node.params:
            param_name = param_node.name
            var_symbol = AmbiguousSymbol(param_name)
            self.current_scope.define(var_symbol)
            proc_symbol.formal_params.append(var_symbol)

        self.visit(node.expr)

        self.log_scope('')
        self.log_scope(str(proc_scope))

        self.current_scope = self.current_scope.enclosing_scope
        self.log_scope(f'LEAVE SCOPE: {proc_name}')
        self.log_scope('')

        # accessed when interpreter is executing procedure call
        proc_symbol.expr = node.expr

    def visit_ProcCall(self, node: ast.ProcCall) -> None:
        proc_token = node.token
        proc_name = proc_token.value

        defined_proc = self.current_scope.lookup(proc_name)
        if defined_proc is None:
            self.error(
                error_code=ErrorCode.PROCEDURE_NOT_FOUND,
                token=proc_token,
                message=f"'{proc_name}'"
            )

        for param in node.actual_params:
            self.visit(param)

    def visit_Program(self, node: ast.Program) -> None:
        raise NotImplementedError

    def visit_CondElse(self, node: ast.CondElse) -> None:
        self.visit(node.expr)

    def visit_CondBranch(self, node: ast.CondBranch) -> None:
        self.visit(node.predicate)
        self.visit(node.expr)

    def visit_Cond(self, node: ast.Cond) -> None:
        for branch in node.branches:
            self.visit(branch)
        if node.else_branch is not None:
            self.visit(node.else_branch)

    def enter_program(self) -> None:
        self.log_scope('ENTER SCOPE: global')
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = global_scope

    def leave_program(self) -> None:
        global_scope = self.current_scope
        if global_scope is None or global_scope.scope_name != 'global':
            raise IllegalStateError

        self.log_scope('')
        self.log_scope(str(global_scope))

        self.current_scope = self.current_scope.enclosing_scope
        self.log_scope('LEAVE SCOPE: global')

    def get_proc_symbol_and_actual_params(self, node: ast.ProcCall) \
            -> Tuple[ProcSymbol, List[ast.Expr]]:
        proc_name = node.proc_name
        proc_symbol = self.current_scope.lookup(proc_name)

        if proc_symbol.type == 'PROCEDURE':
            pass

        elif proc_symbol.type == 'AMBIGUOUS':
            call_stack = self.interpreter.call_stack
            scope = self.current_scope

            proc = call_stack.get(proc_name)
            proc_name = proc.value
            proc_symbol = scope.lookup(proc_name)
            while proc_symbol.type == 'AMBIGUOUS':
                scope = scope.enclosing_scope
                proc_name = proc_symbol.name
                proc_symbol = scope.lookup(proc_name)

        else:
            self.error(
                error_code=ErrorCode.NOT_A_PROCEDURE,
                token=node.token,
                message=f"'{proc_name}' is not a procedure"
            )

        actual_params = node.actual_params

        return proc_symbol, actual_params

    def assert_actual_param_len(self, token: Token, proc_name: str,
                                formal_params_len: int, actual_params_len: int) -> None:
        if proc_name in BUILT_IN_PROCS.keys():
            built_in_proc = BUILT_IN_PROCS[proc_name]
            lower = built_in_proc.lower()
            upper = built_in_proc.upper()

            if upper is None:
                if not lower <= actual_params_len:
                    self.arg_count_error(
                        proc=token,
                        received=actual_params_len,
                        lower=lower,
                        upper=upper
                    )
            else:
                if not lower <= actual_params_len <= upper:
                    self.arg_count_error(
                        proc=token,
                        received=actual_params_len,
                        lower=lower,
                        upper=upper
                    )
        else:
            if formal_params_len != actual_params_len:
                self.arg_count_error(
                    proc=token,
                    received=actual_params_len,
                    lower=formal_params_len,
                    upper=formal_params_len
                )

    def enter_proc(self, proc_name, formal_params) -> None:
        self.log_scope('')
        self.log_scope(f'ENTER SCOPE: {proc_name}')
        # scope for parameters
        proc_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = proc_scope

        for param in formal_params:
            self.current_scope.define(param)

    def leave_proc(self, proc_name) -> None:
        proc_scope = self.current_scope

        self.log_scope('')
        self.log_scope(str(proc_scope))

        self.current_scope = proc_scope.enclosing_scope
        self.log_scope(f'LEAVE SCOPE: {proc_name}')
        self.log_scope('')

    def error(self, error_code: ErrorCode, token: Token, message: str):
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value}: {message}; {token}.',
        )

    def arg_count_error(self, proc: Token, received: int, lower: int = None, upper: int = None):
        if lower is None and upper is None:
            msg = ''
            self.error(ErrorCode.ARGUMENT_COUNT, proc, msg)
        elif lower is not None and upper is None:
            msg = f'expected at least {lower} arguments, received {received}'
            self.error(ErrorCode.ARGUMENT_COUNT, proc, msg)
        elif lower is None and upper is not None:
            msg = f'expected at most {upper} arguments, received {received}'
            self.error(ErrorCode.ARGUMENT_COUNT, proc, msg)
        elif lower is not None and upper is not None and lower != upper:
            msg = f'expected at between {lower} and {upper} arguments, received {received}'
            self.error(ErrorCode.ARGUMENT_COUNT, proc, msg)
        elif lower is not None and upper is not None and lower == upper:
            msg = f'expected {lower} arguments, received {received}'
            self.error(ErrorCode.ARGUMENT_COUNT, proc, msg)

    def log_scope(self, msg: str) -> None:
        if C.SHOULD_LOG_SCOPE:
            print(msg)
