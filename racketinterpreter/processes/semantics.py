from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List, Any
from racketinterpreter import errors as err
from racketinterpreter.classes import ast
from racketinterpreter.classes import data as d
from racketinterpreter.classes import symbols as sym
from racketinterpreter.classes import tokens as t
from racketinterpreter.constants import C
from racketinterpreter.predefined import BUILT_IN_PROCS

if TYPE_CHECKING:
    from racketinterpreter.classes.data import DataType
    from racketinterpreter.processes import Interpreter


class SemanticAnalyzer(ast.ASTVisitor):
    # Not supported ASTs:
    # - StructMake
    # - StructHuh
    # - StructGet
    # - Program

    def __init__(self, interpreter: Interpreter) -> None:
        self.current_scope = None
        self.preprocessor = _Preprocessor(self)
        self.interpreter = interpreter

        self.call_dict = dict()

    def __call__(self, entering: str, **kwargs) -> SemanticAnalyzer:
        # TODO: make these an enum value?
        if entering not in ['PROGRAM', 'PROCEDURE']:
            raise err.IllegalStateError

        self.call_dict.update(entering=entering, **kwargs)

        return self

    def __enter__(self) -> None:
        call_dict = self.call_dict
        entering = call_dict.get('entering')

        if entering == 'PROGRAM':
            scope_name = 'global'
            scope_level = 1

        elif entering == 'PROCEDURE':
            proc_name = self.call_dict.get('proc_name')

            scope_name = proc_name
            scope_level = self.current_scope.scope_level + 1

        else:
            raise err.IllegalStateError

        self.log_scope('')
        self.log_scope(f'ENTER SCOPE: {scope_name}')
        scope = sym.ScopedSymbolTable(
            scope_name=scope_name,
            scope_level=scope_level,
            enclosing_scope=self.current_scope
        )
        self.current_scope = scope

        if entering == 'PROCEDURE':
            formal_params = self.call_dict.get('formal_params')
            for param in formal_params:
                self.current_scope.define(param)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            return

        exiting_scope = self.current_scope
        exiting_scope_name = exiting_scope.scope_name
        exiting = self.call_dict.get('entering')

        if exiting == 'PROGRAM':
            if exiting_scope is None or exiting_scope_name != 'global':
                raise err.IllegalStateError

        self.current_scope = exiting_scope.enclosing_scope

        self.log_scope('')
        self.log_scope(str(exiting_scope))
        self.log_scope(f'LEAVE SCOPE: {exiting_scope_name}')
        self.log_scope('')

        self.call_dict = dict()

    def visit(self, node: ast.AST) -> Any:
        if node.passed_semantic_analysis:
            return
        else:
            result = super().visit(node)
            node.passed_semantic_analysis = True
            return result

    def preprocess(self, node: ast.AST) -> None:
        self.preprocessor.visit(node)

    def log_scope(self, msg: str) -> None:
        if C.SHOULD_LOG_SCOPE:
            print(msg)

    def visit_Bool(self, node: ast.Bool) -> None:
        pass

    def visit_Dec(self, node: ast.Dec) -> None:
        pass

    def visit_Id(self, node: ast.Id) -> None:
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)

        if type(var_symbol) is sym.StructTypeSymbol:
            raise err.SemanticError(
                error_code=err.ErrorCode.USING_STRUCTURE_TYPE,
                token=node.token,
                name=var_symbol.name
            )

        if var_symbol is None:
            raise err.SemanticError(
                error_code=err.ErrorCode.USED_BEFORE_DEFINITION,
                token=node.token,
                name=var_name
            )

    def visit_Int(self, node: ast.Int) -> None:
        pass

    def visit_Rat(self, node: ast.Rat) -> None:
        pass

    def visit_Str(self, node: ast.Str) -> None:
        pass

    def visit_Sym(self, node: ast.Str) -> None:
        pass

    def visit_Cons(self, node: ast.Cons) -> None:
        exprs = node.exprs
        exprs_len = len(exprs)

        if exprs_len != 2:
            raise err.SemanticError(
                error_code=err.ErrorCode.CL_EXPECTED_TWO_ARGUMENTS,
                token=node.token,
                received=exprs_len
            )

        node.first = exprs[0]
        node.rest = exprs[1]

    def visit_Empty(self, node: ast.Cons) -> None:
        pass

    def visit_Cond(self, node: ast.Cond) -> None:
        branches_len = len(node.branches)
        else_branch = node.else_branch

        if branches_len == 0 and else_branch is None:
            raise err.SemanticError(
                error_code=err.ErrorCode.C_EXPECTED_A_CLAUSE,
                token=node.token
            )

        for branch in node.branches:
            if type(branch) is not ast.CondBranch:
                raise err.SemanticError(
                    error_code=err.ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE,
                    token=node.token,
                    expr_token=branch.token
                )

            self.visit(branch)
        if else_branch is not None:
            self.visit(else_branch)

    def visit_CondBranch(self, node: ast.CondBranch) -> None:
        exprs = node.exprs
        exprs_len = len(exprs)
        if exprs_len != 2:
            raise err.SemanticError(
                error_code=err.ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE,
                token=node.token,
                part_count=exprs_len
            )

        node.predicate = exprs[0]
        node.expr = exprs[1]

        predicate_token = node.predicate.token
        if predicate_token.type is t.TokenType.ID and predicate_token.value == t.Keyword.ELSE.value:
            raise err.SemanticError(
                error_code=err.ErrorCode.C_ELSE_NOT_LAST_CLAUSE,
                token=node.token
            )

        self.visit(node.predicate)
        self.visit(node.expr)

    def visit_CondElse(self, node: ast.CondElse) -> None:
        exprs = node.exprs
        exprs_len = len(exprs)
        if exprs_len != 1:
            raise err.SemanticError(
                error_code=err.ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE,
                token=node.token,
                part_count=exprs_len + 1
            )

        node.expr = node.exprs[0]

        self.visit(node.expr)

    def visit_IdAssign(self, node: ast.IdAssign) -> None:
        token = node.token
        exprs = node.exprs
        exprs_len = len(exprs)

        if len(exprs) == 0:
            raise RuntimeError

        if exprs_len != 0 and type(exprs[0]) is ast.Sym:
            # a little bit hacky..., not sure why Racket has this behavior
            raise err.SemanticError(
                error_code=err.ErrorCode.BUILTIN_OR_IMPORTED_NAME,
                token=t.Token(
                    type=t.TokenType.INVALID,
                    value='quote',
                    line_no=token.line_no,
                    column=token.column
                )
            )

        if exprs_len == 0 or type(exprs[0]) is not ast.Id \
                or exprs[0].value in t.KEYWORDS:
            next_token = exprs[0].token if exprs_len > 0 else None
            raise err.SemanticError(
                error_code=err.ErrorCode.D_EXPECTED_A_NAME,
                token=token,
                next_token=next_token
            )

        const_token = exprs[0].token
        const_name = const_token.value
        if exprs_len == 1:
            raise err.SemanticError(
                error_code=err.ErrorCode.D_V_MISSING_AN_EXPRESSION,
                token=token,
                name=const_name
            )
        elif exprs_len > 2:
            extra_count = exprs_len - 2
            raise err.SemanticError(
                error_code=err.ErrorCode.D_V_EXPECTED_ONE_EXPRESSION,
                token=token,
                extra_count=extra_count,
                name=const_name
            )
        elif type(exprs[1]) is ast.Id and exprs[1].value in t.KEYWORDS:
            keyword = exprs[1].value
            token = exprs[1].token
            if keyword == t.Keyword.COND.value:
                raise err.SemanticError(
                    error_code=err.ErrorCode.C_EXPECTED_OPEN_PARENTHESIS,
                    token=token
                )
            elif keyword == t.Keyword.DEFINE.value:
                raise err.SemanticError(
                    error_code=err.ErrorCode.D_EXPECTED_OPEN_PARENTHESIS,
                    token=token
                )
            elif keyword == t.Keyword.DEFINE_STRUCT.value:
                raise err.SemanticError(
                    error_code=err.ErrorCode.DS_EXPECTED_OPEN_PARENTHESIS,
                    token=token
                )
            elif keyword == t.Keyword.ELSE.value:
                raise err.SemanticError(
                    error_code=err.ErrorCode.E_NOT_ALLOWED,
                    token=token
                )
            else:
                raise err.IllegalStateError

        node.identifier = node.exprs[0].value
        node.expr = node.exprs[1]

        var_name = node.identifier
        var_symbol = sym.AmbiguousSymbol(var_name)

        if self.current_scope.lookup(var_name, current_scope_only=True) is not None:
            if var_name in BUILT_IN_PROCS:
                error_code = err.ErrorCode.BUILTIN_OR_IMPORTED_NAME
            else:
                error_code = err.ErrorCode.PREVIOUSLY_DEFINED_NAME

            raise err.SemanticError(
                error_code=error_code,
                token=const_token
            )

        self.visit(node.expr)

        self.current_scope.define(var_symbol)

    def visit_FormalParam(self, node: ast.FormalParam) -> None:
        token = node.token

        if token.type is not t.TokenType.ID or token.value in t.KEYWORDS:
            if node.param_for is ast.FormalParam.ParamFor.PROC_ASSIGN:
                error_code = err.ErrorCode.D_P_EXPECTED_A_VARIABLE
            elif node.param_for is ast.FormalParam.ParamFor.STRUCT_ASSIGN:
                error_code = err.ErrorCode.DS_EXPECTED_A_FIELD
            else:
                raise err.IllegalStateError

            raise err.SemanticError(
                error_code=error_code,
                token=token
            )

        node.name = node.ast.value

    def visit_ProcAssign(self, node: ast.ProcAssign) -> None:
        proc_name_expr = node.name_expr
        proc_name_token = proc_name_expr.token
        proc_name = proc_name_token.value
        proc_symbol = self.current_scope.lookup(proc_name, True)

        self.log_scope('')
        self.log_scope(f'ENTER SCOPE: {proc_name}')
        # scope for parameters
        proc_scope = sym.ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = proc_scope

        for var_symbol in proc_symbol.formal_params:
            self.current_scope.define(var_symbol)

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

        if proc_token is None or proc_token.type != t.TokenType.ID:
            raise err.SemanticError(
                error_code=err.ErrorCode.FC_EXPECTED_A_FUNCTION,
                token=node.token,
                proc_token=proc_token
            )

        node.original_proc_token = proc_token
        node.proc_token = proc_token
        node.proc_name = proc_token.value

        node.actual_params = node.exprs[1:]

        proc_token = node.proc_token
        proc_name = proc_token.value

        if proc_name in t.KEYWORDS:
            if proc_name == t.Keyword.DEFINE.value:
                raise err.SemanticError(
                    error_code=err.ErrorCode.D_NOT_TOP_LEVEL,
                    token=proc_token
                )
            elif proc_name == t.Keyword.DEFINE_STRUCT.value:
                raise err.SemanticError(
                    error_code=err.ErrorCode.DS_NOT_TOP_LEVEL,
                    token=proc_token
                )
            elif proc_name == t.Keyword.ELSE.value:
                raise err.SemanticError(
                    error_code=err.ErrorCode.E_NOT_ALLOWED,
                    token=proc_token
                )

        defined_proc = self.current_scope.lookup(proc_name)
        if defined_proc is None:
            raise err.SemanticError(
                error_code=err.ErrorCode.USED_BEFORE_DEFINITION,
                token=node.token,
                name=proc_name
            )

        for param in node.actual_params:
            self.visit(param)

    def visit_StructAssign(self, node: ast.StructAssign) -> DataType:
        struct_name_ast = node.struct_name_ast
        if struct_name_ast is None:
            struct_name_token = None
            raise err.SemanticError(
                error_code=err.ErrorCode.DS_EXPECTED_STRUCTURE_NAME,
                token=node.token,
                name_token=struct_name_token
            )

        struct_name_token = struct_name_ast.token

        if struct_name_token.type is not t.TokenType.ID \
                or struct_name_token.value in t.KEYWORDS:
            raise err.SemanticError(
                error_code=err.ErrorCode.DS_EXPECTED_STRUCTURE_NAME,
                token=node.token,
                name_token=struct_name_token
            )

        struct_name = struct_name_token.value

        if self.current_scope.lookup(struct_name, current_scope_only=True) is not None:
            if struct_name in BUILT_IN_PROCS:
                error_code = err.ErrorCode.BUILTIN_OR_IMPORTED_NAME
            else:
                error_code = err.ErrorCode.PREVIOUSLY_DEFINED_NAME

            raise err.SemanticError(
                error_code=error_code,
                token=struct_name_token
            )

        node.struct_name = struct_name

        if type(node.field_asts) != list:
            found_token = node.field_asts.token if node.field_asts is not None else None
            raise err.SemanticError(
                error_code=err.ErrorCode.DS_EXPECTED_FIELD_NAMES,
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
            raise err.SemanticError(
                error_code=err.ErrorCode.DS_POST_FIELD_NAMES,
                token=node.token,
                part_count=extra_part_conut
            )

        struct_class = d.StructDataFactory.create(struct_name, field_names)

        new_procs = [f'make-{struct_name}', f'{struct_name}?'] + [f'{struct_name}-{field}' for field in field_names]

        for idx, proc_name in enumerate(new_procs + [struct_name]):
            if idx == 0:
                proc_symbol = sym.ProcSymbol(proc_name, [sym.AmbiguousSymbol(field) for field in field_names])
            elif proc_name == struct_name:
                proc_symbol = sym.StructTypeSymbol(proc_name)
            else:
                proc_symbol = sym.ProcSymbol(proc_name, [sym.AmbiguousSymbol('_')])

            if idx == 0:
                proc_symbol.expr = ast.StructMake(struct_class)
            elif idx == 1:
                proc_symbol.expr = ast.StructHuh(struct_class)
            elif proc_name == struct_name:
                pass
            else:
                proc_symbol.expr = ast.StructGet(struct_class)

            if self.current_scope.lookup(proc_name, current_scope_only=True) is not None:
                if proc_name in BUILT_IN_PROCS:
                    error_code = err.ErrorCode.BUILTIN_OR_IMPORTED_NAME
                else:
                    error_code = err.ErrorCode.PREVIOUSLY_DEFINED_NAME

                raise err.SemanticError(
                    error_code=error_code,
                    token=node.token
                )

            self.current_scope.define(proc_symbol)

        return struct_class

    def visit_CheckExpect(self, node: ast.CheckExpect) -> None:
        exprs = node.exprs
        exprs_len = len(exprs)

        if exprs_len != 2:
            raise err.SemanticError(
                error_code=err.ErrorCode.CE_INCORRECT_ARGUMENT_COUNT,
                token=node.token,
                received=exprs_len
            )

        node.actual = exprs[0]
        node.expected = exprs[1]

    def get_proc_symbol_and_actual_params(self, node: ast.ProcCall) \
            -> Tuple[sym.ProcSymbol, List[ast.Expr]]:
        proc_name = node.proc_name
        proc_symbol = self.current_scope.lookup(proc_name)

        if proc_symbol.type == 'PROCEDURE':
            pass

        elif proc_symbol.type == 'STRUCTURE_TYPE':
            pass

        else:
            call_stack = self.interpreter.call_stack
            scope = self.current_scope

            proc = call_stack.get(proc_name)
            proc_name = proc.value
            proc_symbol = scope.lookup(proc_name)

            if type(proc) is not d.Procedure:
                raise err.SemanticError(
                    error_code=err.ErrorCode.FC_EXPECTED_A_FUNCTION,
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

    # TODO: move to interpreter?
    def assert_actual_param_len(self, node_token: t.Token, proc_name: str,
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

        raise err.SemanticError(
            error_code=err.ErrorCode.INCORRECT_ARGUMENT_COUNT,
            token=node_token,
            proc_name=proc_name,
            lower=lower,
            upper=upper,
            received=received
        )


class _Preprocessor(ast.ASTVisitor):
    # Not supported ASTs:
    # - Bool
    # - Dec
    # - Id
    # - Int
    # - Rat
    # - Str
    # - Sym
    # - Cons
    # - Cond
    # - CondBranch
    # - CondElse
    # - IdAssign
    # - FormalParam
    # - ProcAssign
    # - ProcCall
    # - StructAssign
    # - StructMake
    # - StructHuh
    # - StructGet
    # - CheckExpect
    # - Program

    def __init__(self, semantic_analyzer: SemanticAnalyzer) -> None:
        self.semantic_analyzer = semantic_analyzer

    def visit_ProcAssign(self, node: ast.ProcAssign) -> None:
        semantic_analyzer = self.semantic_analyzer

        proc_name_expr = node.name_expr
        proc_name_token = proc_name_expr.token if proc_name_expr else None
        if proc_name_token is None or proc_name_token.type is not t.TokenType.ID \
                or proc_name_token.value in t.KEYWORDS:
            raise err.SemanticError(
                error_code=err.ErrorCode.D_P_EXPECTED_FUNCTION_NAME,
                token=node.token,
                name_token=proc_name_token
            )

        exprs = node.exprs
        exprs_len = len(exprs)
        if exprs_len == 0:
            raise err.SemanticError(
                error_code=err.ErrorCode.D_P_MISSING_AN_EXPRESSION,
                token=node.token
            )
        elif exprs_len > 1:
            raise err.SemanticError(
                error_code=err.ErrorCode.D_P_EXPECTED_ONE_EXPRESSION,
                token=node.token,
                part_count=exprs_len - 1
            )

        proc_name = proc_name_token.value
        node.proc_name = proc_name
        node.expr = exprs[0]

        if semantic_analyzer.current_scope.lookup(proc_name, current_scope_only=True) is not None:
            if proc_name in BUILT_IN_PROCS:
                error_code = err.ErrorCode.BUILTIN_OR_IMPORTED_NAME
            else:
                error_code = err.ErrorCode.PREVIOUSLY_DEFINED_NAME

            raise err.SemanticError(
                error_code=error_code,
                token=proc_name_token
            )

        proc_symbol = sym.ProcSymbol(proc_name)

        semantic_analyzer.current_scope.define(proc_symbol)

        param_names = set()
        for param_node in node.formal_params:
            semantic_analyzer.visit(param_node)

            param_name = param_node.name

            if param_name in param_names:
                raise err.SemanticError(
                    error_code=err.ErrorCode.D_DUPLICATE_VARIABLE,
                    token=node.token,
                    name=param_name
                )

            var_symbol = sym.AmbiguousSymbol(param_name)
            proc_symbol.formal_params.append(var_symbol)
            param_names.add(param_name)
