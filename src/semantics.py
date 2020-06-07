from __future__ import annotations
from typing import TYPE_CHECKING
from src.ast import ASTVisitor
from src.constants import C
from src.errors import ErrorCode, SemanticError
from src.symbol import ConstSymbol, ProcSymbol, ScopedSymbolTable
from src.token import TokenType

if TYPE_CHECKING:
    from src.ast import Const, ConstAssign, Num, ProcAssign, ProcCall, Program
    from src.token import Token


class SemanticAnalyzer(ASTVisitor):

    def __init__(self):
        self.current_scope = None

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

    def visit_ProcCall(self, node: ProcCall) -> None:
        # TODO: split this method up
        proc = node.token
        actual_param_len = len(node.actual_params)

        if proc.type is TokenType.PLUS:
            pass
        elif proc.type is TokenType.MINUS:
            if actual_param_len == 0:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=1)
        elif proc.type is TokenType.MUL:
            pass
        elif proc.type is TokenType.DIV:
            if actual_param_len == 0:
                self.arg_count_error(proc=proc, received=actual_param_len, lower=1)
        elif proc.type is TokenType.ID:
            if proc.value == 'add1':
                if actual_param_len != 1:
                    self.arg_count_error(proc=proc, received=actual_param_len, lower=1, upper=1)
            elif proc.value == 'and':
                if actual_param_len < 0:
                    self.arg_count_error(proc=proc, received=actual_param_len, lower=0)
            elif proc.value in C.BUILT_IN_PROCS:
                raise NotImplementedError(f"Semantic analyzer cannot handle builtin procedure '{proc.value}'")
            else:
                defined_proc = self.current_scope.lookup(proc.value)
                if defined_proc is None:
                    self.error(
                        error_code=ErrorCode.PROCEDURE_NOT_FOUND,
                        token=proc,
                        message=f"'{proc.value}'"
                    )

                if defined_proc.type != 'PROCEDURE':
                    self.error(
                        error_code=ErrorCode.NOT_A_PROCEDURE,
                        token=proc,
                        message=f"'{proc.value}' is not a procedure"
                    )

                formal_param_len = len(defined_proc.formal_params)
                if actual_param_len != formal_param_len:
                    self.arg_count_error(
                        proc=proc,
                        received=actual_param_len,
                        lower=formal_param_len,
                        upper=formal_param_len
                    )

                for param in node.actual_params:
                    self.visit(param)

                proc_symbol = self.current_scope.lookup(node.proc_name)
                # accessed by the interpreter when executing procedure call
                node.proc_symbol = proc_symbol
        else:
            # TODO: make more specific
            raise Exception()

        for arg in node.actual_params:
            self.visit(arg)

    def visit_Num(self, node: Num) -> None:
        pass

    def visit_Bool(self, node: Num) -> None:
        pass

    def visit_Str(self, node: Num) -> None:
        pass

    def visit_ConstAssign(self, node: ConstAssign) -> None:
        var_name = node.identifier
        var_symb = ConstSymbol(var_name)

        if self.current_scope.lookup(var_name, current_scope_only=True) is not None:
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.token,
                message=f"'{node.token.value}'"
            )

        self.current_scope.define(var_symb)

    def visit_ProcAssign(self, node: ProcAssign) -> None:
        proc_name = node.identifier
        proc_symbol = ProcSymbol(proc_name)
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
            var_symbol = ConstSymbol(param_name)
            self.current_scope.define(var_symbol)
            proc_symbol.formal_params.append(var_symbol)

        self.visit(node.expr)

        self.log_scope('')
        self.log_scope(str(proc_scope))

        self.current_scope = self.current_scope.enclosing_scope
        self.log_scope(f'LEAVE SCOPE: {proc_name}')
        self.log_scope('')

        # accessed by the interpreter when executing procedure call
        proc_symbol.expr = node.expr

    def visit_Const(self, node: Const) -> None:
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(
                error_code=ErrorCode.ID_NOT_FOUND,
                token=node.token,
                message=f"'{node.token.value}'"
            )

    def visit_Program(self, node: Program) -> None:
        self.log_scope('ENTER SCOPE: global')
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = global_scope

        for child_node in node.statements:
            self.visit(child_node)

        self.log_scope('')
        self.log_scope(str(global_scope))

        self.current_scope = self.current_scope.enclosing_scope
        self.log_scope('LEAVE SCOPE: global')
