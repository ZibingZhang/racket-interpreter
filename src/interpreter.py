from __future__ import annotations
import fractions as f
from typing import TYPE_CHECKING, Any, List, Union
from src.ast import ASTVisitor
from src.builtins import BUILT_IN_PROCS
from src.constants import C
from src.datatype import Boolean, InexactNumber, Integer, Procedure, Rational, String
from src.errors import ErrorCode, IllegalStateError, InterpreterError
from src.semantics import SemanticAnalyzer
from src.stack import ActivationRecord, ARType, CallStack
from src.symbol import AmbiguousSymbol
from src.token import Token

if TYPE_CHECKING:
    from src import ast
    from src.datatype import DataType, Number


class Interpreter(ASTVisitor):

    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree
        self.call_stack = CallStack()

        self.semantic_analyzer = SemanticAnalyzer()
        self.semantic_analyzer.interpreter = self

    def visit_Bool(self, node: ast.Bool) -> Boolean:
        # 1. return boolean
        return Boolean(node.value)

    def visit_Int(self, node: ast.Int) -> Number:
        # 1. return integer
        return Integer(node.value)

    def visit_Str(self, node: ast.Str) -> String:
        # 1. return string
        return String(node.value)

    def visit_Rat(self, node: ast.Rat) -> Union[Integer, Rational]:
        # 1. return rational number
        numerator = node.value[0]
        denominator = node.value[1]
        fraction = f.Fraction(numerator, denominator)
        if fraction.denominator == 1:
            return Integer(fraction.numerator)
        else:
            return Rational(fraction.numerator, fraction.denominator)

    def visit_Dec(self, node: ast.Dec) -> InexactNumber:
        # 1. return decimal
        return InexactNumber(node.value)

    def visit_Const(self, node: ast.Const) -> DataType:
        # 1. perform semantic analysis on node
        # 2. lookup value of const
        # 3. return value
        self.semantic_analyzer.visit(node)

        var_name = node.value

        var_value = self.call_stack.get(var_name)

        return var_value

    def visit_ConstAssign(self, node: ast.ConstAssign) -> None:
        # 1. perform semantic analysis on node
        #    a. ensure ID not already taken
        #    b. visit expr
        #    c. define symbol
        # 2. visit expr to get value of const (type DataType)
        # 3. assign value of const to const name
        self.semantic_analyzer.visit(node)

        var_name = node.identifier
        var_value = self.visit(node.expr)

        ar = self.call_stack.peek()
        ar[var_name] = var_value

    def visit_Param(self, node: ast.Param) -> None:
        # 1. should never visit param, raise error
        raise IllegalStateError('Interpreter should never have to visit a parameter.')

    def visit_ProcAssign(self, node: ast.ProcAssign) -> None:
        # 1. perform semantic analysis on node
        #    a. ensure ID not already taken
        #    b. define proc symbol
        #    c. create and enter new scope named after proc
        #    d. define all formal params
        #    e. visit proc expr
        #    f. leave scope
        #    g. assign node expr to proc expr (for when interpreter is executing proc call)
        # 2. use proc name to create Procedure (type DataType)
        # 3. assign Procedure to proc name
        self.semantic_analyzer.visit(node)

        proc_name = node.identifier
        proc_value = Procedure(proc_name)

        ar = self.call_stack.peek()
        ar[proc_name] = proc_value

    def visit_ProcCall(self, node: ast.ProcCall) -> DataType:
        # TODO: document this and the cond stuff down below
        # 1.
        self.semantic_analyzer.visit(node)

        proc_symbol, actual_params = self.semantic_analyzer.get_proc_symbol_and_actual_params(node)
        proc_name = proc_symbol.name
        expr = proc_symbol.expr
        formal_params = proc_symbol.formal_params

        formal_params_len = len(formal_params)
        actual_params_len = len(actual_params)
        self.semantic_analyzer.assert_actual_param_len(node.token, proc_name, formal_params_len, actual_params_len)

        if proc_name in BUILT_IN_PROCS.keys():
            old_token = node.token
            line_no = old_token.line_no
            column = old_token.column
            node.token = Token.create_proc(proc_name, line_no, column)

            result = self._visit_builtin_ProcCall(node)

            node.token = old_token
            return result
        else:
            return self._visit_user_defined_ProcCall(proc_name, expr, formal_params, actual_params)

    def visit_Program(self, node: ast.Program) -> List[DataType]:
        # 1. create global activation record
        # 2. define builtin procs
        # 3. create global scope in semantic analyzer
        # 4. visit each statement
        #    a. if result is not None, append to list of results
        # 5. leave global scope in semantic analyzer
        # 6. remove global activation record
        if C.SHOULD_LOG_SCOPE:
            print('')
        self.log_stack(f'ENTER: PROGRAM')

        ar = ActivationRecord(
            name='global',
            type=ARType.PROGRAM,
            nesting_level=1
        )
        self.call_stack.push(ar)

        self._define_builtin_procs()

        self.semantic_analyzer.enter_program()

        result = []
        for child_node in node.statements:
            value = self.visit(child_node)
            if value is not None:
                result.append(value)

        self.semantic_analyzer.leave_program()

        self.log_stack(f'LEAVE: PROGRAM')
        self.log_stack(str(self.call_stack))

        self.call_stack.pop()

        return result

    def visit_CondElse(self, node: ast.CondElse) -> None:
        raise IllegalStateError('Interpreter should never have to visit a cond else.')

    def visit_CondBranch(self, node: ast.CondBranch) -> None:
        raise IllegalStateError('Interpreter should never have to visit a cond branch.')

    def visit_Cond(self, node: ast.Cond) -> DataType:
        token = node.token

        idx = 0
        for idx, branch in enumerate(node.branches):
            predicate_result = self.visit(branch.predicate)

            if not issubclass(type(predicate_result), Boolean):
                self.builtin_proc_type_error(
                    proc_token=token,
                    expected_type="Boolean",
                    param_value=predicate_result,
                    idx=idx
                )

            if predicate_result:
                return self.visit(branch.expr)
        else_branch = node.else_branch
        if node.else_branch is not None:
            else_expr = else_branch.expr
            return self.visit(else_expr)

        self.error(
            error_code=ErrorCode.NO_COND_BRANCH,
            token=token,
            message='did not enter a branch',
            idx=idx
        )

    def interpret(self) -> Any:
        tree = self.tree
        return self.visit(tree)

    def log_stack(self, msg) -> None:
        if C.SHOULD_LOG_STACK:
            print(msg)

    def error(self, error_code: ErrorCode, token: Token, message: str, idx: int):
        raise InterpreterError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value}: {message}; idx={idx}; {token}.',
        )

    def builtin_proc_type_error(self, proc_token: Token, expected_type: str,
                                param_value: DataType, idx: int) -> None:
        error_code_msg = ErrorCode.ARGUMENT_TYPE.value
        msg = f"{error_code_msg}: procedure expected argument of type {expected_type}, " \
            f"received {param_value}; idx={idx}; {proc_token}."
        raise InterpreterError(
            error_code=ErrorCode.ARGUMENT_TYPE,
            token=proc_token,
            message=msg
        )

    def _define_builtin_procs(self):
        ar = self.call_stack.peek()
        for proc in BUILT_IN_PROCS:
            ar[proc] = Procedure(proc)

    def _visit_builtin_ProcCall(self, node: ast.ProcCall) -> DataType:
        proc_token = node.token
        proc_name = proc_token.value
        actual_params = node.actual_params

        return BUILT_IN_PROCS[proc_name].interpret(self, actual_params, proc_token)

    def _visit_user_defined_ProcCall(self, proc_name: str, expr: ast.Expr,
                                     formal_params: List[AmbiguousSymbol], actual_params: List[ast.Expr]) -> DataType:
        self.semantic_analyzer.enter_proc(proc_name, formal_params)

        current_ar = self.call_stack.peek()
        ar = ActivationRecord(
            name=proc_name,
            type=ARType.PROCEDURE,
            nesting_level=current_ar.nesting_level + 1,
        )

        self.log_stack('')
        self.log_stack(f'ENTER: PROCEDURE {proc_name}')
        self.log_stack(str(self.call_stack))

        for param_symbol, argument_node in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(argument_node)
        self.call_stack.push(ar)

        result = self.visit(expr)

        self.semantic_analyzer.leave_proc(proc_name)

        self.log_stack(f'LEAVE: PROCEDURE {proc_name}')
        self.log_stack(str(self.call_stack))
        self.log_stack('')

        self.call_stack.pop()

        return result
