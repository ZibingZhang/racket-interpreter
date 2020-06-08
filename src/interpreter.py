from __future__ import annotations
from typing import TYPE_CHECKING, Any, List
from src.ast import ASTVisitor
from src.constants import C
from src.datatype import Boolean, Number, Procedure, String
from src.errors import ErrorCode, IllegalStateError, InterpreterError
from src.semantics import SemanticAnalyzer
from src.stack import ActivationRecord, ARType, CallStack
from src.token import Token, TokenType

if TYPE_CHECKING:
    from src.ast import AST, Const, ConstAssign, Num, Param, ProcAssign, ProcCall, Program
    from src.datatype import DataType


class Interpreter(ASTVisitor):

    def __init__(self, tree: AST) -> None:
        self.tree = tree
        self.call_stack = CallStack()

        self.semantic_analyzer = SemanticAnalyzer()
        self.semantic_analyzer.interpreter = self

    def visit_Bool(self, node: Num) -> Boolean:
        # 1. return boolean
        return Boolean(node.value)

    def visit_Num(self, node: Num) -> Number:
        # TODO: number factory when number types get more complex
        # 1. return number
        return Number(node.value)

    def visit_Str(self, node: Num) -> String:
        # 1. return string
        return String(node.value)

    def visit_Const(self, node: Const) -> DataType:
        # 1. lookup value of const
        # 2. return value
        var_name = node.value

        var_value = self.call_stack.get(var_name)

        return var_value

    def visit_ConstAssign(self, node: ConstAssign) -> None:
        # 1. perform semantic analysis on node
        #    a. ensure ID not already taken
        #    b. visit expr
        #    c. define symbol
        # 2. visit expr to get value of const (type DataType)
        # 3. assign value of const to const name
        self.semantic_analyzer.visit_ConstAssign(node)

        var_name = node.identifier
        var_value = self.visit(node.expr)

        ar = self.call_stack.peek()
        ar[var_name] = var_value

    def visit_Param(self, node: Param) -> None:
        # 1. should never visit param, raise error
        raise IllegalStateError('Interpreter should never have to visit a parameter.')

    def visit_ProcAssign(self, node: ProcAssign) -> None:
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
        self.semantic_analyzer.visit_ProcAssign(node)

        proc_name = node.identifier
        proc_value = Procedure(proc_name)

        ar = self.call_stack.peek()
        ar[proc_name] = proc_value

    def visit_ProcCall(self, node: ProcCall) -> DataType:
        # 1. perform semantic analysis on node
        #    a. is the proc built in
        #       #T 1. check number of actual args
        #       #F 1. ensure proc is defined
        #          2. ensure len of formal and actual params match if not ambiguous
        #          3. visit actual params
        # 2. is the proc built in
        #    #T 1. visit actual params
        #       2. evaluate result based on number and value of actual params
        #    #F 1.
        self.semantic_analyzer.visit_ProcCall(node)

        proc_token = node.token
        if Token.is_builtin_proc(proc_token):
            return self._visit_builtin_ProcCall(node)
        else:
            return self._visit_user_defined_ProcCall(node)

    def visit_Program(self, node: Program) -> List[DataType]:
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

    def interpret(self) -> Any:
        tree = self.tree
        return self.visit(tree)

    def log_stack(self, msg) -> None:
        if C.SHOULD_LOG_STACK:
            print(msg)

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
        for proc in C.BUILT_IN_PROCS:
            ar[proc] = Procedure(proc)

    def _visit_builtin_ProcCall(self, node: ProcCall) -> DataType:
        proc_token = node.token
        actual_params = node.actual_params

        if proc_token.type is TokenType.PLUS:
            if len(actual_params) == 0:
                result = Number(0)
            else:
                result = Number(0)
                for idx, param in enumerate(actual_params):
                    param_value = self.visit(param)

                    if not issubclass(type(param_value), Number):
                        self.builtin_proc_type_error(
                            proc_token=proc_token,
                            expected_type='Number',
                            param_value=param_value,
                            idx=idx
                        )

                    result += param_value
        elif proc_token.type is TokenType.MINUS:
            if len(actual_params) == 1:
                param = actual_params[0]
                param_value = self.visit(param)

                if not issubclass(type(param_value), Number):
                    self.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=0
                    )

                result = Number(-param_value)
            else:
                param_value = self.visit(actual_params[0])

                if not issubclass(type(param_value), Number):
                    self.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=0
                    )

                result = param_value
                params = actual_params[1:]
                for idx, param in enumerate(params):
                    param_value = self.visit(param)

                    if not issubclass(type(param_value), Number):
                        self.builtin_proc_type_error(
                            proc_token=proc_token,
                            expected_type='Number',
                            param_value=param_value,
                            idx=idx
                        )

                    result -= param_value
        elif proc_token.type is TokenType.MUL:
            if len(actual_params) == 0:
                result = Number(1)
            else:
                result = Number(1)
                for idx, param in enumerate(actual_params):
                    param_value = self.visit(param)

                    if not issubclass(type(param_value), Number):
                        self.builtin_proc_type_error(
                            proc_token=proc_token,
                            expected_type='Number',
                            param_value=param_value,
                            idx=idx
                        )

                    result *= param_value
        elif proc_token.type is TokenType.DIV:
            if len(actual_params) == 1:
                param = actual_params[0]
                param_value = self.visit(param)

                if not issubclass(type(param_value), Number):
                    self.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=0
                    )

                result = Number(-param_value)
            else:
                param_value = self.visit(actual_params[0])

                if not issubclass(type(param_value), Number):
                    self.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=0
                    )

                result = param_value
                params = actual_params[1:]
                for idx, param in enumerate(params):
                    param_value = self.visit(param)

                    if not issubclass(type(param_value), Number):
                        self.builtin_proc_type_error(
                            proc_token=proc_token,
                            expected_type='Number',
                            param_value=param_value,
                            idx=idx
                        )

                    result /= param_value
        elif proc_token.type is TokenType.EQUAL:
            if len(actual_params) == 1:
                param = actual_params[0]
                param_value = self.visit(param)

                if not issubclass(type(param_value), Number):
                    self.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=0
                    )

                result = Boolean(True)
            else:
                first_param_value = param_value = self.visit(actual_params[0])

                if not issubclass(type(param_value), Number):
                    self.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=0
                    )

                result = Boolean(True)
                params = actual_params[1:]
                for idx, param in enumerate(params):
                    param_value = self.visit(param)

                    if not issubclass(type(param_value), Number):
                        self.builtin_proc_type_error(
                            proc_token=proc_token,
                            expected_type='Number',
                            param_value=param_value,
                            idx=idx
                        )

                    result = result and first_param_value == param_value
        elif proc_token.type is TokenType.ID:
            proc_name = proc_token.value
            if proc_name == 'add1':
                param_value = self.visit(actual_params[0])

                if not issubclass(type(param_value), Number):
                    self.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=0
                    )

                result = param_value + Number(1)
            elif proc_name == 'and':
                result = Boolean(True)

                for idx, param in enumerate(actual_params):
                    param_value = self.visit(param)

                    if not issubclass(type(param_value), Boolean):
                        self.builtin_proc_type_error(
                            proc_token=proc_token,
                            expected_type='Boolean',
                            param_value=param_value,
                            idx=idx
                        )

                    result = result and param_value
            elif proc_name == 'if':
                boolean = self.visit(actual_params[0])
                if bool(boolean):
                    result = self.visit(actual_params[1])
                else:
                    result = self.visit(actual_params[2])
                return result
            elif proc_name in C.BUILT_IN_PROCS:
                raise NotImplementedError(f"Interpreter cannot handle builtin procedure '{proc_name}'")
            else:
                raise IllegalStateError(f"Procedure '{proc_name}' is not a builtin procedure.")
        else:
            raise IllegalStateError('Invalid operator should have been caught during semantic analysis.')

        return result

    def _visit_user_defined_ProcCall(self, node: ProcCall) -> DataType:
        proc_name = node.proc_name

        current_ar = self.call_stack.peek()
        ar = ActivationRecord(
            name=proc_name,
            type=ARType.PROCEDURE,
            nesting_level=current_ar.nesting_level + 1,
        )

        formal_params, actual_params, expr = self.semantic_analyzer.enter_proc(node)
        # TODO: also fix here
        # semantics edits node to represent what it acutally is?
        # separation of responsibility?
        if expr is None:
            result = self.visit(node)
            node.token = node.original_token
            return result

        self.log_stack('')
        self.log_stack(f'ENTER: PROCEDURE {proc_name}')
        self.log_stack(str(self.call_stack))

        for param_symbol, argument_node in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(argument_node)
        self.call_stack.push(ar)

        result = self.visit(expr)

        # node.token = node.original_token
        if node.token.value != node.original_token.value:
            print(node.token)
            print(node.original_token)

        self.semantic_analyzer.leave_proc(node)

        self.log_stack(f'LEAVE: PROCEDURE {proc_name}')
        self.log_stack(str(self.call_stack))
        self.log_stack('')

        self.call_stack.pop()

        return result
