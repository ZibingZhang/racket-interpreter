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
    from racketinterpreter.classes import symbols as sym
    from racketinterpreter.classes.data import Data, Number


class Interpreter(ast.ASTVisitor):
    # Not supported ASTs:
    # - CondBranch
    # - CondElse
    # - FormalParam
    # - StructMake
    # - StructHuh
    # - StructGet

    def __init__(self) -> None:
        self.call_stack = stack.CallStack()

        self.preprocessor = _Preprocessor(self)
        self.semantic_analyzer = SemanticAnalyzer(self)

    def interpret(self, tree: ast.Program) -> Tuple[List[Data], List[Tuple[bool, t.Token, d.Data, d.Data]]]:
        return self.visit(tree)

    def preprocess(self, node: ast.AST) -> None:
        self.preprocessor.visit(node)

    def log_stack(self, msg: str) -> None:
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

    def visit_Sym(self, node: ast.Sym) -> d.Symbol:
        return d.Symbol(node.value)

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

    def visit_IdAssign(self, node: ast.IdAssign) -> None:
        self.semantic_analyzer.visit(node)

        var_name = node.identifier
        var_value = self.visit(node.expr)

        ar = self.call_stack.peek()
        ar[var_name] = var_value

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

        if proc_symbol.type == 'STRUCTURE_TYPE':
            raise err.InterpreterError(
                error_code=err.ErrorCode.USING_STRUCTURE_TYPE,
                token=node.token,
                name=proc_name
            )

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

        expr_type = type(expr)
        if proc_name in BUILT_IN_PROCS.keys():
            token = node.token
            line_no = token.line_no
            column = token.column
            node.proc_token = t.Token.create_proc(proc_name, line_no, column)

            result = self._visit_builtin_ProcCall(node)

            node.proc_token = node.original_proc_token
            return result
        elif issubclass(expr_type, ast.StructProc):
            evaluated_params = list(map(lambda param: self.visit(param), actual_params))
            if expr_type is ast.StructMake:
                data = expr.data_type()
                data.fields = evaluated_params
                return data
            elif expr_type is ast.StructHuh:
                result = d.Boolean(type(evaluated_params[0]) == expr.data_type)
                return result
            elif expr_type is ast.StructGet:
                # TODO: add check for type
                data_type_name = expr.data_type.__name__
                field = proc_name[len(data_type_name) + 1:]
                result = evaluated_params[0].fields[evaluated_params[0].field_names.index(field)]
                return result
            else:
                raise err.IllegalStateError
        else:
            result = self._visit_user_defined_ProcCall(proc_name, expr, formal_params, actual_params)
            return result

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

    def visit_CheckExpect(self, node: ast.CheckExpect) -> Tuple[bool, t.Token, d.Data, d.Data]:
        self.semantic_analyzer.visit(node)

        token = node.token
        actual = self.visit(node.actual)
        expected = self.visit(node.expected)

        error = actual != expected

        return error, token, actual, expected

    def visit_Program(self, node: ast.Program) -> Tuple[List[Data], List[Tuple[bool, t.Token, d.Data, d.Data]]]:
        ar = stack.ActivationRecord(
            name='global',
            type=stack.ARType.PROGRAM,
            nesting_level=1
        )

        with ar(self):
            self._define_builtin_procs()

            with self.semantic_analyzer(entering='PROGRAM'):
                definitions, expressions, tests = self._sort_program_statements(node.statements)

                for statement in definitions:
                    statement_type = type(statement)
                    if statement_type is ast.ProcAssign:
                        self.preprocess(statement)

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
        token = node.token
        proc_token = node.proc_token
        proc_name = proc_token.value
        actual_params = node.actual_params

        current_ar = self.call_stack.peek()
        ar = stack.ActivationRecord(
            name=proc_name,
            type=stack.ARType.PROCEDURE,
            nesting_level=current_ar.nesting_level + 1
        )

        with ar(self):
            return BUILT_IN_PROCS[proc_name].interpret(self, token, actual_params)

    def _visit_user_defined_ProcCall(self, proc_name: str, expr: ast.Expr,
                                     formal_params: List[sym.AmbiguousSymbol], actual_params: List[ast.Expr]) -> Data:
        current_ar = self.call_stack.peek()

        if current_ar.name == 'if':
            previous_ar = self.call_stack.peek(2)

            if previous_ar.name == proc_name:
                evaluated_params = list(map(self.visit, actual_params))
                for param, value in zip(formal_params, evaluated_params):
                    current_ar[param.name] = value

                raise err.TailEndRecursion

        ar = stack.ActivationRecord(
            name=proc_name,
            type=stack.ARType.PROCEDURE,
            nesting_level=current_ar.nesting_level + 1
        )

        with self.semantic_analyzer(
                entering='PROCEDURE',
                proc_name=proc_name,
                formal_params=formal_params
        ):
            for param_symbol, argument_node in zip(formal_params, actual_params):
                ar[param_symbol.name] = self.visit(argument_node)

            with ar(self):
                while True:
                    try:
                        result = self.visit(expr)
                    except err.TailEndRecursion as e:
                        pass
                    else:
                        break

        return result


class _Preprocessor(ast.ASTVisitor):
    # Not supported ASTs:
    # - Bool
    # - Dec
    # - Id
    # - Int
    # - Rat
    # - Str
    # - Sym
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

    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter

    def visit_ProcAssign(self, node: ast.ProcAssign) -> None:
        interpreter = self.interpreter

        interpreter.semantic_analyzer.preprocess(node)

        proc_name = node.proc_name
        proc_value = d.Procedure(proc_name)

        ar = interpreter.call_stack.peek()
        ar[proc_name] = proc_value
