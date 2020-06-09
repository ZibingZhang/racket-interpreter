from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List, Optional
from src.ast import ASTVisitor
from src.constants import C
from src.errors import ErrorCode, IllegalStateError, SemanticError
from src.symbol import AmbiguousSymbol, ConstSymbol, ProcSymbol, ScopedSymbolTable
from src.token import Token, TokenType

if TYPE_CHECKING:
    from src.ast import AST, Const, ConstAssign, Num, Param, ProcAssign, ProcCall, Program
    from src.symbol import Symbol


class SemanticAnalyzer(ASTVisitor):

    def __init__(self):
        self.current_scope = None
        self.interpreter = None

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

    def visit_Bool(self, node: Num) -> None:
        pass

    def visit_Num(self, node: Num) -> None:
        pass

    def visit_Str(self, node: Num) -> None:
        pass

    def visit_Const(self, node: Const) -> None:
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(
                error_code=ErrorCode.ID_NOT_FOUND,
                token=node.token,
                message=f"'{node.token.value}'"
            )

    def visit_ConstAssign(self, node: ConstAssign) -> None:
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

    def visit_Param(self, node: Param) -> None:
        raise IllegalStateError('Semantic analyzer should never have to visit a parameter.')

    def visit_ProcAssign(self, node: ProcAssign) -> None:
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

    def visit_ProcCall(self, node: ProcCall) -> None:
        if Token.is_builtin_proc(node.token):
            self._visit_builtin_ProcCall(node)
        else:
            self._visit_user_defined_ProcCall(node)

    def visit_Program(self, node: Program) -> None:
        raise NotImplementedError

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

    def enter_proc(self, node: ProcCall) -> Tuple[List[Symbol], List[AST], Optional[ProcCall]]:
        proc_name = node.proc_name
        proc = self.current_scope.lookup(proc_name)

        if proc.type == 'PROCEDURE':
            expr = proc.expr

            formal_params = proc.formal_params
            formal_params_len = len(formal_params)
            actual_params = node.actual_params
            actual_params_len = len(actual_params)

            if formal_params_len != actual_params_len:
                self.arg_count_error(
                    proc=node.token,
                    received=actual_params_len,
                    lower=formal_params_len,
                    upper=formal_params_len
                )

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

            return formal_params, actual_params, expr
        elif proc.type == 'AMBIGUOUS':
            call_stack = self.interpreter.call_stack
            scope = self.current_scope

            proc = call_stack.get(proc_name)
            proc_name = proc.value
            proc_symbol = scope.lookup(proc_name)
            while proc_symbol.type == 'AMBIGUOUS':
                scope = scope.enclosing_scope
                proc_name = proc_symbol.name
                proc_symbol = scope.lookup(proc_name)

            formal_params = proc_symbol.formal_params
            formal_params_len = len(formal_params)
            actual_params = node.actual_params
            actual_params_len = len(actual_params)

            # None if builtin proc
            expr = proc_symbol.expr

            if proc_name in C.BUILT_IN_PROCS and expr is None:
                old_token = node.token
                line_no = old_token.line_no
                column = old_token.column
                node.token = Token.create_proc(proc_name, line_no, column)
                # TODO: builtin functions can have any number of inputs potentially
                # TODO: add a better check for such a thing
                # if formal_params_len != actual_params_len:
                #     self.arg_count_error(
                #         proc=node.token,
                #         received=actual_params_len,
                #         lower=formal_params_len,
                #         upper=formal_params_len
                #     )

                return formal_params, actual_params, expr
            elif proc_name not in C.BUILT_IN_PROCS and expr is not None:
                if formal_params_len != actual_params_len:
                    self.arg_count_error(
                        proc=node.token,
                        received=actual_params_len,
                        lower=formal_params_len,
                        upper=formal_params_len
                    )

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

                return formal_params, actual_params, expr
            else:
                raise IllegalStateError('Built in procs should have no expr.')
        else:
            self.error(
                error_code=ErrorCode.NOT_A_PROCEDURE,
                token=node.token,
                message=f"'{proc_name}' is not a procedure"
            )

    def leave_proc(self, node: ProcCall) -> None:
        proc_scope = self.current_scope
        proc_name = node.proc_name
        self.log_scope('')
        self.log_scope(str(proc_scope))

        self.current_scope = proc_scope.enclosing_scope
        self.log_scope(f'LEAVE SCOPE: {proc_name}')
        self.log_scope('')

    def _visit_builtin_ProcCall(self, node: ProcCall) -> None:
        proc = node.token
        actual_param_len = len(node.actual_params)

        if proc.value == '+':
            pass
        elif proc.value == '-':
            if actual_param_len == 0:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=1)
        elif proc.value == '*':
            pass
        elif proc.value == '/':
            if actual_param_len == 0:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=1)
        elif proc.value == '=':
            if actual_param_len == 0:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=1)
        elif proc.value == 'add1':
            if actual_param_len != 1:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=1, upper=1)
        elif proc.value == 'and':
            if actual_param_len < 0:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=0)
        elif proc.value == 'if':
            if actual_param_len != 3:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=3, upper=3)
        elif proc.value in C.BUILT_IN_PROCS:
            raise NotImplementedError(f"Semantic analyzer cannot handle builtin procedure '{proc.value}'")
        else:
            # TODO: make more specific, not a user defined thing
            raise Exception()

        for param in node.actual_params:
            self.visit(param)

    def _visit_user_defined_ProcCall(self, node: ProcCall) -> None:
        proc = node.token
        actual_param_len = len(node.actual_params)

        defined_proc = self.current_scope.lookup(proc.value)
        if defined_proc is None:
            self.error(
                error_code=ErrorCode.PROCEDURE_NOT_FOUND,
                token=proc,
                message=f"'{proc.value}'"
            )

        if defined_proc.type == 'PROCEDURE':
            formal_param_len = len(defined_proc.formal_params)
            if actual_param_len != formal_param_len:
                self.arg_count_error(
                    proc=proc,
                    received=actual_param_len,
                    lower=formal_param_len,
                    upper=formal_param_len
                )
        elif defined_proc.type == 'AMBIGUOUS':
            pass
        else:
            self.error(
                error_code=ErrorCode.NOT_A_PROCEDURE,
                token=proc,
                message=f"'{proc.value}' is not a procedure"
            )

        for param in node.actual_params:
            self.visit(param)
