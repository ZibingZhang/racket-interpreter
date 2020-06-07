from __future__ import annotations
from functools import reduce
from typing import TYPE_CHECKING, Any, List
from src.ast import ASTVisitor
from src.constants import C
from src.datatype import Boolean, Number, Procedure, String
from src.errors import IllegalStateError
from src.stack import ActivationRecord, ARType, CallStack
from src.token import Token, TokenType

if TYPE_CHECKING:
    from src.ast import AST, Const, ConstAssign, Num, Param, ProcAssign, ProcCall, Program
    from src.datatype import DataType


class Interpreter(ASTVisitor):

    def __init__(self, tree: AST) -> None:
        self.tree = tree
        self.call_stack = CallStack()

    def log_stack(self, msg) -> None:
        if C.SHOULD_LOG_STACK:
            print(msg)

    def interpret(self) -> Any:
        tree = self.tree
        return self.visit(tree)

    def visit_Bool(self, node: Num) -> Boolean:
        return Boolean(node.value)

    def visit_Num(self, node: Num) -> Number:
        return Number(node.value)

    def visit_Str(self, node: Num) -> String:
        return String(node.value)

    def visit_Const(self, node: Const) -> DataType:
        var_name = node.value

        var_value = self.call_stack.get(var_name)

        return var_value

    def visit_ConstAssign(self, node: ConstAssign) -> None:
        var_name = node.identifier
        var_value = self.visit(node.expr)

        ar = self.call_stack.peek()
        ar[var_name] = var_value

    def visit_Param(self, node: Param) -> None:
        raise IllegalStateError('Interpreter should never have to visit a parameter.')

    def visit_ProcAssign(self, node: ProcAssign) -> None:
        proc_name = node.identifier
        proc_value = Procedure(proc_name)

        ar = self.call_stack.peek()
        ar[proc_name] = proc_value

    def visit_ProcCall(self, node: ProcCall) -> DataType:
        proc_token = node.token
        if Token.is_builtin_proc(proc_token):
            return self._visit_builtin_ProcCall(node)
        else:
            return self._visit_user_defined_ProcCall(node)

    def _visit_builtin_ProcCall(self, node: ProcCall) -> DataType:
        proc_token = node.token

        # TODO: get rid of reduce and type check parameters
        if proc_token.type is TokenType.PLUS:
            if len(node.actual_params) == 0:
                return Number(0)
            else:
                initial = Number(0)
                iterable = node.actual_params
                result = reduce(lambda acc, x: acc + self.visit(x), iterable, initial)
        elif proc_token.type is TokenType.MINUS:
            if len(node.actual_params) == 1:
                result = Number(-self.visit(node.actual_params[0]))
            else:
                initial = self.visit(node.actual_params[0])
                iterable = node.actual_params[1:]
                result = reduce(lambda acc, x: acc - self.visit(x), iterable, initial)
        elif proc_token.type is TokenType.MUL:
            if len(node.actual_params) == 0:
                result = Number(1)
            else:
                initial = Number(1)
                iterable = node.actual_params
                result = reduce(lambda acc, x: acc * self.visit(x), iterable, initial)
        elif proc_token.type is TokenType.DIV:
            if len(node.actual_params) == 1:
                result = Number(1 / self.visit(node.actual_params[0]))
            else:
                initial = self.visit(node.actual_params[0])
                iterable = node.actual_params[1:]
                result = reduce(lambda acc, x: acc / self.visit(x), iterable, initial)
        elif proc_token.type is TokenType.ID:
            proc_name = proc_token.value
            if proc_name == 'add1':
                result = self.visit(node.actual_params[0]) + Number(1)
            elif proc_name in C.BUILT_IN_PROCS:
                raise NotImplementedError(f"Interpreter cannot handle builtin procedure '{proc_name}'")
            else:
                raise IllegalStateError(f"Procedure '{proc_name}' is not a builtin procedure.")
        else:
            raise IllegalStateError('Invalid operator should have been caught during semantic analysis.')

        return result

    def _visit_user_defined_ProcCall(self, node: ProcCall) -> DataType:
        proc_name = node.proc_name
        proc_symbol = node.proc_symbol

        ar = ActivationRecord(
            name=proc_name,
            type=ARType.PROCEDURE,
            nesting_level=proc_symbol.scope_level + 1,
        )

        formal_params = proc_symbol.formal_params
        actual_params = node.actual_params

        for param_symbol, argument_node in zip(formal_params, actual_params):
            ar[param_symbol.name] = self.visit(argument_node)

        self.call_stack.push(ar)

        self.log_stack('')
        self.log_stack(f'ENTER: PROCEDURE {proc_name}')
        self.log_stack(str(self.call_stack))

        result = self.visit(proc_symbol.block_ast)

        self.log_stack(f'LEAVE: PROCEDURE {proc_name}')
        self.log_stack(str(self.call_stack))
        self.log_stack('')

        self.call_stack.pop()

        return result

    def visit_Program(self, node: Program) -> List[DataType]:
        if C.SHOULD_LOG_SCOPE:
            print('')
        self.log_stack(f'ENTER: PROGRAM')

        ar = ActivationRecord(
            name='global',
            type=ARType.PROGRAM,
            nesting_level=1
        )
        self.call_stack.push(ar)

        result = []
        for child_node in node.statements:
            value = self.visit(child_node)
            if value is not None:
                result.append(value)

        self.log_stack(f'LEAVE: PROGRAM')
        self.log_stack(str(self.call_stack))

        self.call_stack.pop()

        return result
