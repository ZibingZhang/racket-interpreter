from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List, Any
from src import ast
from src.ast import ASTVisitor, AST
from src.builtins import BUILT_IN_PROCS
from src.constants import C
from src.data import Procedure, StructDataFactory
from src.errors import ErrorCode, IllegalStateError, SemanticError
from src.symbol import AmbiguousSymbol, ProcSymbol, ScopedSymbolTable
from src.token import KEYWORDS, Keyword, Token, TokenType

if TYPE_CHECKING:
    from src.data import DataType


class SemanticAnalyzer(ASTVisitor):

    def __init__(self):
        self.current_scope = None
        self.interpreter = None

    def visit(self, node: AST) -> Any:
        if node.passed_semantic_analysis:
            return
        else:
            result = super().visit(node)
            node.passed_semantic_analysis = True
            return result

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

    def visit_Id(self, node: ast.Id) -> None:
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)

        if var_symbol is None:
            raise SemanticError(
                error_code=ErrorCode.USED_BEFORE_DEFINITION,
                token=node.token,
                name=var_name
            )

    def visit_IdAssign(self, node: ast.IdAssign) -> None:
        token = node.token
        actual_params = node.actual_params
        actual_params_len = len(actual_params)

        if actual_params_len == 0 or type(actual_params[0]) is not ast.Id \
                or actual_params[0].value in KEYWORDS:
            next_token = actual_params[0].token if actual_params_len > 0 else None
            raise SemanticError(
                error_code=ErrorCode.D_EXPECTED_A_NAME,
                token=token,
                next_token=next_token
            )

        const_token = actual_params[0].token
        const_name = const_token.value
        if actual_params_len == 1:
            raise SemanticError(
                error_code=ErrorCode.D_V_MISSING_AN_EXPRESSION,
                token=token,
                name=const_name
            )
        elif actual_params_len > 2:
            extra_count = actual_params_len - 2
            raise SemanticError(
                error_code=ErrorCode.D_V_EXPECTED_ONE_EXPRESSION,
                token=token,
                extra_count=extra_count,
                name=const_name
            )
        elif type(actual_params[1]) is ast.Id and actual_params[1].value in KEYWORDS:
            keyword = actual_params[1].value
            token = actual_params[1].token
            if keyword == Keyword.COND.value:
                raise SemanticError(
                    error_code=ErrorCode.C_EXPECTED_OPEN_PARENTHESIS,
                    token=token
                )
            elif keyword == Keyword.DEFINE.value:
                raise SemanticError(
                    error_code=ErrorCode.D_V_EXPECTED_OPEN_PARENTHESIS,
                    token=token
                )
            elif keyword == Keyword.DEFINE_STRUCT.value:
                raise SemanticError(
                    error_code=ErrorCode.DS_EXPECTED_OPEN_PARENTHESIS,
                    token=token
                )
            elif keyword == Keyword.ELSE.value:
                raise SemanticError(
                    error_code=ErrorCode.E_NOT_ALLOWED,
                    token=token
                )
            else:
                raise IllegalStateError

        node.identifier = node.actual_params[0].value
        node.expr = node.actual_params[1]

        var_name = node.identifier
        var_symbol = AmbiguousSymbol(var_name)

        if self.current_scope.lookup(var_name, current_scope_only=True) is not None:
            if var_name in BUILT_IN_PROCS:
                error_code = ErrorCode.BUILTIN_OR_IMPORTED_NAME
            else:
                error_code = ErrorCode.PREVIOUSLY_DEFINED_NAME

            raise SemanticError(
                error_code=error_code,
                token=const_token
            )

        self.visit(node.expr)

        self.current_scope.define(var_symbol)

    def visit_FormalParam(self, node: ast.FormalParam) -> None:
        token = node.token

        if token.type is not TokenType.ID or token.value in KEYWORDS:
            if node.param_for is ast.FormalParam.ParamFor.PROC_ASSIGN:
                error_code = ErrorCode.D_P_EXPECTED_A_VARIABLE
            elif node.param_for is ast.FormalParam.ParamFor.STRUCT_ASSIGN:
                error_code = ErrorCode.DS_EXPECTED_A_FIELD
            else:
                raise IllegalStateError

            raise SemanticError(
                error_code=error_code,
                token=token
            )

        node.name = node.ast.value

    def visit_ProcAssign(self, node: ast.ProcAssign) -> None:
        proc_name_expr = node.name_expr
        proc_name_token = proc_name_expr.token if proc_name_expr else None
        if proc_name_token is None or proc_name_token.type is not TokenType.ID \
                or proc_name_token.value in KEYWORDS:
            raise SemanticError(
                error_code=ErrorCode.D_P_EXPECTED_FUNCTION_NAME,
                token=node.token,
                name_token=proc_name_token
            )

        exprs = node.exprs
        exprs_len = len(exprs)
        if exprs_len == 0:
            raise SemanticError(
                error_code=ErrorCode.D_P_MISSING_AN_EXPRESSION,
                token=node.token
            )
        elif exprs_len > 1:
            raise SemanticError(
                error_code=ErrorCode.D_P_EXPECTED_ONE_EXPRESSION,
                token=node.token,
                part_count=exprs_len-1
            )

        proc_name = proc_name_token.value
        node.proc_name = proc_name
        node.expr = exprs[0]

        for param in node.formal_params:
            self.visit(param)

        proc_symbol = ProcSymbol(proc_name)

        if self.current_scope.lookup(proc_name, current_scope_only=True) is not None:
            if proc_name in BUILT_IN_PROCS:
                error_code = ErrorCode.BUILTIN_OR_IMPORTED_NAME
            else:
                error_code = ErrorCode.PREVIOUSLY_DEFINED_NAME

            raise SemanticError(
                error_code=error_code,
                token=proc_name_token
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

        # TODO: put this in the visit loop, make visit return the symbol?
        # insert parameters into the procedure scope
        param_names = set()
        for param_node in node.formal_params:
            param_name = param_node.name

            if param_name in param_names:
                raise SemanticError(
                    error_code=ErrorCode.D_DUPLICATE_VARIABLE,
                    token=node.token,
                    name=param_name
                )

            var_symbol = AmbiguousSymbol(param_name)
            self.current_scope.define(var_symbol)
            proc_symbol.formal_params.append(var_symbol)
            param_names.add(param_name)

        self.visit(node.expr)

        self.log_scope('')
        self.log_scope(str(proc_scope))

        self.current_scope = self.current_scope.enclosing_scope
        self.log_scope(f'LEAVE SCOPE: {proc_name}')
        self.log_scope('')

        # accessed when interpreter is executing procedure call
        proc_symbol.expr = node.expr

    def visit_ProcCall(self, node: ast.ProcCall) -> None:
        exprs = node.exprs
        if len(exprs) == 0:
            proc_token = None
        else:
            op = exprs[0]
            proc_token = op.token

        if proc_token is None or proc_token.type != TokenType.ID:
            raise SemanticError(
                error_code=ErrorCode.FC_EXPECTED_A_FUNCTION,
                token=node.token,
                proc_token=proc_token
            )

        node.original_proc_token = proc_token
        node.proc_token = proc_token
        node.proc_name = proc_token.value

        node.actual_params = node.exprs[1:]

        proc_token = node.proc_token
        proc_name = proc_token.value

        if proc_name in KEYWORDS:
            if proc_name == Keyword.DEFINE.value:
                raise SemanticError(
                    error_code=ErrorCode.D_NOT_TOP_LEVEL,
                    token=proc_token
                )
            elif proc_name == Keyword.DEFINE_STRUCT.value:
                raise SemanticError(
                    error_code=ErrorCode.DS_NOT_TOP_LEVEL,
                    token=proc_token
                )
            elif proc_name == Keyword.ELSE.value:
                raise SemanticError(
                    error_code=ErrorCode.E_NOT_ALLOWED,
                    token=proc_token
                )

        defined_proc = self.current_scope.lookup(proc_name)
        if defined_proc is None:
            raise SemanticError(
                error_code=ErrorCode.USED_BEFORE_DEFINITION,
                token=node.token,
                name=proc_name
            )

        for param in node.actual_params:
            self.visit(param)

    def visit_Program(self, node: ast.Program) -> None:
        raise IllegalStateError('Semantic analyzer should never have to visit a program.')

    def visit_CondElse(self, node: ast.CondElse) -> None:
        exprs = node.exprs
        exprs_len = len(exprs)
        if exprs_len != 1:
            raise SemanticError(
                error_code=ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE,
                token=node.token,
                part_count=exprs_len + 1
            )

        node.expr = node.exprs[0]

        self.visit(node.expr)

    def visit_CondBranch(self, node: ast.CondBranch) -> None:
        exprs = node.exprs
        exprs_len = len(exprs)
        if exprs_len != 2:
            raise SemanticError(
                error_code=ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE,
                token=node.token,
                part_count=exprs_len
            )

        node.predicate = exprs[0]
        node.expr = exprs[1]

        predicate_token = node.predicate.token
        if predicate_token.type is TokenType.ID and predicate_token.value == Keyword.ELSE.value:
            raise SemanticError(
                error_code=ErrorCode.C_ELSE_NOT_LAST_CLAUSE,
                token=node.token
            )

        self.visit(node.predicate)
        self.visit(node.expr)

    def visit_Cond(self, node: ast.Cond) -> None:
        branches_len = len(node.branches)
        else_branch = node.else_branch

        if branches_len == 0 and else_branch is None:
            raise SemanticError(
                error_code=ErrorCode.C_EXPECTED_A_CLAUSE,
                token=node.token
            )

        for branch in node.branches:
            if type(branch) is not ast.CondBranch:
                raise SemanticError(
                    error_code=ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE,
                    token=node.token,
                    expr_token=branch.token
                )

            self.visit(branch)
        if else_branch is not None:
            self.visit(else_branch)

    def visit_StructAssign(self, node: ast.StructAssign) -> DataType:
        struct_name_ast = node.struct_name_ast
        if struct_name_ast is None:
            struct_name_token = None
            raise SemanticError(
                error_code=ErrorCode.DS_EXPECTED_STRUCTURE_NAME,
                token=node.token,
                name_token=struct_name_token
            )

        struct_name_token = struct_name_ast.token

        if struct_name_token.type is not TokenType.ID \
                or struct_name_token.value in KEYWORDS:
            raise SemanticError(
                error_code=ErrorCode.DS_EXPECTED_STRUCTURE_NAME,
                token=node.token,
                name_token=struct_name_token
            )

        struct_name = struct_name_token.value

        if self.current_scope.lookup(struct_name, current_scope_only=True) is not None:
            if struct_name in BUILT_IN_PROCS:
                error_code = ErrorCode.BUILTIN_OR_IMPORTED_NAME
            else:
                error_code = ErrorCode.PREVIOUSLY_DEFINED_NAME

            raise SemanticError(
                error_code=error_code,
                token=struct_name_token
            )

        node.struct_name = struct_name

        if type(node.field_asts) != list:
            found_token = node.field_asts.token if node.field_asts is not None else None
            raise SemanticError(
                error_code=ErrorCode.DS_EXPECTED_FIELD_NAMES,
                token=node.token,
                found_token=found_token
            )

        field_names = []
        for field_ast in node.field_asts:
            self.visit(field_ast)
            field_token = field_ast.token
            field_name = field_token.value
            field_names.append(field_name)

        node.field_names = field_names

        extra_part_conut = len(node.extra_asts)
        if extra_part_conut > 0:
            raise SemanticError(
                error_code=ErrorCode.DS_POST_FIELD_NAMES,
                token=node.token,
                part_count=extra_part_conut
            )

        struct_class = StructDataFactory.create(struct_name, field_names)

        new_procs = [f'make-{struct_name}', f'{struct_name}?'] + [f'{struct_name}-{field}' for field in field_names]

        for idx, proc_name in enumerate(new_procs + [struct_name]):
            if idx == 0:
                proc_symbol = ProcSymbol(proc_name, [AmbiguousSymbol(field) for field in field_names])
            else:
                proc_symbol = ProcSymbol(proc_name, [AmbiguousSymbol('_')])

            if idx == 0:
                proc_symbol.expr = ast.StructMake(struct_class)
            elif idx == 1:
                proc_symbol.expr = ast.StructHuh(struct_class)
            else:
                proc_symbol.expr = ast.StructGet(struct_class)

            if self.current_scope.lookup(proc_name, current_scope_only=True) is not None:
                if proc_name in BUILT_IN_PROCS:
                    error_code = ErrorCode.BUILTIN_OR_IMPORTED_NAME
                else:
                    error_code = ErrorCode.PREVIOUSLY_DEFINED_NAME

                raise SemanticError(
                    error_code=error_code,
                    token=node.token
                )

            self.current_scope.define(proc_symbol)

        return struct_class

    def visit_StructMethod(self, node: ast.StructProc) -> None:
        raise IllegalStateError('Semantic analyzer should never have to visit a struct method.')

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

        else:
            call_stack = self.interpreter.call_stack
            scope = self.current_scope

            proc = call_stack.get(proc_name)
            proc_name = proc.value
            proc_symbol = scope.lookup(proc_name)

            if type(proc) is not Procedure:
                raise SemanticError(
                    error_code=ErrorCode.FC_EXPECTED_A_FUNCTION,
                    token=node.token,
                    proc_token=node.proc_token,
                    found_data=proc
                )

            while proc_symbol.type == 'AMBIGUOUS':
                scope = scope.enclosing_scope
                proc_name = proc_symbol.name
                proc_symbol = scope.lookup(proc_name)

        actual_params = node.actual_params

        return proc_symbol, actual_params

    def assert_actual_param_len(self, node_token: Token, proc_name: str,
                                formal_params_len: int, actual_params_len: int) -> None:
        received = actual_params_len
        if proc_name in BUILT_IN_PROCS.keys():
            built_in_proc = BUILT_IN_PROCS[proc_name]
            lower = built_in_proc.lower()
            upper = built_in_proc.upper()

            if upper is None:
                if lower <= received:
                    return
            else:
                if lower <= received <= upper:
                    return
        else:
            lower = formal_params_len
            upper = formal_params_len
            if formal_params_len == received:
                return

        raise SemanticError(
            error_code=ErrorCode.INCORRECT_ARGUMENT_COUNT,
            token=node_token,
            proc_name=proc_name,
            lower=lower,
            upper=upper,
            received=received
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

    def log_scope(self, msg: str) -> None:
        if C.SHOULD_LOG_SCOPE:
            print(msg)
