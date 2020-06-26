from __future__ import annotations
import fractions as f
from typing import TYPE_CHECKING, Any, List, Tuple, Union
from racketinterpreter import errors as err
from racketinterpreter.classes import ast
from racketinterpreter.classes import data as d
from racketinterpreter.classes import stack as stack
from racketinterpreter.classes import tokens as t
from racketinterpreter.constants import C
from racketinterpreter.functions.predefined import BUILT_IN_PROCS
from racketinterpreter.processes.semantics import SemanticAnalyzer

if TYPE_CHECKING:
    import racketinterpreter.classes.symbol as sym
    from classes.data import Data, Number


class Interpreter(ast.ASTVisitor):

    def __init__(self, tree: ast.Program) -> None:
        self.tree = tree
        self.call_stack = stack.CallStack()

        self.semantic_analyzer = SemanticAnalyzer()
        self.semantic_analyzer.interpreter = self

    def interpret(self) -> Tuple[List[Data], List[Tuple[bool, t.Token, d.Data, d.Data]]]:
        tree = self.tree
        return self.visit(tree)

    def log_stack(self, msg) -> None:
        if C.SHOULD_LOG_STACK:
            print(msg)

    def visit_Bool(self, node: ast.Bool) -> d.Boolean:
        return d.Boolean(node.value)

    def visit_Dec(self, node: ast.Dec) -> d.InexactNumber:
        return d.InexactNumber(node.value)

    def visit_Id(self, node: ast.Id) -> Data:
        self.semantic_analyzer.visit(node)

        var_name = node.value

        var_value = self.call_stack.get(var_name)

        if issubclass(type(var_value), type):
            struct_name = var_name
            raise err.InterpreterError(
                error_code=err.ErrorCode.USING_STRUCTURE_TYPE,
                token=node.token,
                name=struct_name
            )

        return var_value

    def visit_Int(self, node: ast.Int) -> Number:
        return d.Integer(node.value)

    def visit_Rat(self, node: ast.Rat) -> Union[d.Integer, d.Rational]:
        numerator = node.value[0]
        denominator = node.value[1]
        fraction = f.Fraction(numerator, denominator)
        if fraction.denominator == 1:
            return d.Integer(fraction.numerator)
        else:
            return d.Rational(fraction.numerator, fraction.denominator)

    def visit_Str(self, node: ast.Str) -> d.String:
        return d.String(node.value)

    def visit_Cond(self, node: ast.Cond) -> Data:
        self.semantic_analyzer.visit(node)

        for idx, branch in enumerate(node.branches):
            predicate_result = self.visit(branch.predicate)

            if not issubclass(type(predicate_result), d.Boolean):
                raise err.InterpreterError(
                    error_code=err.ErrorCode.C_QUESTION_RESULT_NOT_BOOLEAN,
                    token=node.token,
                    result=predicate_result
                )

            if predicate_result:
                return self.visit(branch.expr)

        else_branch = node.else_branch
        if node.else_branch is not None:
            else_expr = else_branch.expr
            return self.visit(else_expr)
        else:
            raise err.InterpreterError(
                error_code=err.ErrorCode.C_ALL_QUESTION_RESULTS_FALSE,
                token=node.token
            )

    def visit_CondBranch(self, node: ast.CondBranch) -> None:
        raise err.IllegalStateError('Interpreter should never have to visit a cond branch.')

    def visit_CondElse(self, node: ast.CondElse) -> None:
        raise err.IllegalStateError('Interpreter should never have to visit a cond else.')

    def visit_IdAssign(self, node: ast.IdAssign) -> None:
        self.semantic_analyzer.visit(node)

        var_name = node.identifier
        var_value = self.visit(node.expr)

        ar = self.call_stack.peek()
        ar[var_name] = var_value

    def visit_FormalParam(self, node: ast.FormalParam) -> None:
        raise err.IllegalStateError('Interpreter should never have to visit a formal parameter.')

    def visit_ProcAssign(self, node: ast.ProcAssign) -> None:
        self.semantic_analyzer.visit(node)

        proc_name = node.proc_name
        proc_value = d.Procedure(proc_name)

        ar = self.call_stack.peek()
        ar[proc_name] = proc_value

    def visit_ProcCall(self, node: ast.ProcCall) -> Data:
        self.semantic_analyzer.visit(node)

        proc_symbol, actual_params = self.semantic_analyzer.get_proc_symbol_and_actual_params(node)
        proc_name = proc_symbol.name
        expr = proc_symbol.expr
        formal_params = proc_symbol.formal_params

        formal_params_len = len(formal_params)
        actual_params_len = len(actual_params)
        self.semantic_analyzer.assert_actual_param_len(
            node_token=node.token,
            proc_name=proc_name,
            formal_params_len=formal_params_len,
            actual_params_len=actual_params_len
        )

        if proc_name in BUILT_IN_PROCS.keys():
            old_token = node.token
            line_no = old_token.line_no
            column = old_token.column
            node.token = t.Token.create_proc(proc_name, line_no, column)

            try:
                result = self._visit_builtin_ProcCall(node)
            except ZeroDivisionError as e:
                raise err.InterpreterError(
                    error_code=err.ErrorCode.DIVISION_BY_ZERO,
                    token=node.token
                )

            node.token = old_token
            return result
        elif issubclass(type(expr), ast.StructProc):
            evaluated_params = list(map(lambda param: self.visit(param), actual_params))
            if type(expr) is ast.StructMake:
                data = expr.data_class()
                data.fields = evaluated_params
                return data
            elif type(expr) is ast.StructHuh:
                result = d.Boolean(type(evaluated_params[0]) == expr.data_class)
                return result
            elif type(expr) is ast.StructGet:
                # TODO: change data_class to datatype
                datatype_name = expr.data_class.__name__
                field = proc_name[len(datatype_name)+1:]
                result = evaluated_params[0].fields[evaluated_params[0].field_names.index(field)]
                return result
            else:
                raise err.IllegalStateError
        else:
            return self._visit_user_defined_ProcCall(proc_name, expr, formal_params, actual_params)

    def visit_StructAssign(self, node: ast.StructAssign):
        struct_class = self.semantic_analyzer.visit(node)

        struct_name = node.struct_name
        fields = node.field_names

        metaclass = struct_class.metaclass

        ar = self.call_stack.peek()
        ar[struct_name] = metaclass

        new_procs = ['make-' + struct_name, struct_name + '?'] + [f'{struct_name}-{field}' for field in fields]
        for proc_name in new_procs:
            ar[proc_name] = d.Procedure(proc_name)

    def visit_StructMake(self, node: ast.StructMake) -> None:
        raise err.IllegalStateError('Interpreter should never have to visit a struct make.')

    def visit_StructHuh(self, node: ast.StructMake) -> None:
        raise err.IllegalStateError('Interpreter should never have to visit a struct huh.')

    def visit_StructGet(self, node: ast.StructMake) -> None:
        raise err.IllegalStateError('Interpreter should never have to visit a struct get.')

    def visit_CheckExpect(self, node: ast.CheckExpect) -> Tuple[bool, t.Token, d.Data, d.Data]:
        self.semantic_analyzer.visit(node)

        token = node.token
        actual = self.visit(node.actual)
        expected = self.visit(node.expected)

        error = actual != expected

        return error, token, actual, expected

    def visit_Program(self, node: ast.Program) -> Tuple[List[Data], List[Tuple[bool, t.Token, d.Data, d.Data]]]:
        if C.SHOULD_LOG_SCOPE:
            print('')
        self.log_stack(f'ENTER: PROGRAM')

        ar = stack.ActivationRecord(
            name='global',
            type=stack.ARType.PROGRAM,
            nesting_level=1
        )
        self.call_stack.push(ar)
        self._define_builtin_procs()

        self.semantic_analyzer.enter_program()

        definitions, expressions, tests = self._sort_program_statements(node.statements)

        for statement in definitions:
            self.visit(statement)

        results = []
        for statement in expressions:
            result = self.visit(statement)
            results.append(result)

        test_results = []
        for statement in tests:
            test_result = self.visit(statement)
            test_results.append(test_result)

        self.semantic_analyzer.leave_program()

        self.call_stack.pop()

        self.log_stack(f'LEAVE: PROGRAM')
        self.log_stack(str(self.call_stack))

        return results, test_results

    def _sort_program_statements(self, statements) -> Tuple[List[ast.AST], List[ast.AST], List[ast.AST]]:
        definitions = []
        expressions = []
        tests = []

        for statement in statements:
            statement_type = type(statement)
            if statement_type in [ast.IdAssign, ast.ProcAssign, ast.StructAssign]:
                definitions.append(statement)
            elif statement_type is ast.CheckExpect:
                tests.append(statement)
            else:
                expressions.append(statement)

        return definitions, expressions, tests

    def _define_builtin_procs(self):
        ar = self.call_stack.peek()
        for proc in BUILT_IN_PROCS:
            ar[proc] = d.Procedure(proc)

    def _visit_builtin_ProcCall(self, node: ast.ProcCall) -> Data:
        proc_token = node.token
        proc_name = proc_token.value
        actual_params = node.actual_params

        return BUILT_IN_PROCS[proc_name].interpret(self, actual_params, proc_token)

    def _visit_user_defined_ProcCall(self, proc_name: str, expr: ast.Expr,
                                     formal_params: List[sym.AmbiguousSymbol], actual_params: List[ast.Expr]) -> Data:
        self.semantic_analyzer.enter_proc(proc_name, formal_params)

        current_ar = self.call_stack.peek()
        ar = stack.ActivationRecord(
            name=proc_name,
            type=stack.ARType.PROCEDURE,
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
