from __future__ import annotations
from typing import TYPE_CHECKING
from src.ast import ASTVisitor
from src.symbol import ScopedSymbolTable, ConstSymbol, FuncSymbol
from src.token import TokenType

if TYPE_CHECKING:
    from src.ast import Func, FuncAssign, Num, ConstAssign, Const, NoOp, Program
    from src.token import Token


class SemanticAnalyzerException(Exception):
    pass


class SemanticAnalyzer(ASTVisitor):

    def __init__(self):
        self.current_scope = None

    def arg_count_error(self, op: Token, received: int, lower: int = None, upper: int = None):
        if lower is None and upper is None:
            msg = f'Error: operator \'{op.value}\' has incorrect number of arguments.'
            raise SemanticAnalyzerException(msg)
        elif lower is not None and upper is None:
            msg = f'Error: operator \'{op.value}\' expected at least {lower} arguments, received {received}.'
            raise SemanticAnalyzerException(msg)
        elif lower is None and upper is not None:
            msg = f'Error: operator \'{op.value}\' expected at most {upper} arguments, received {received}.'
            raise SemanticAnalyzerException(msg)
        elif lower is not None and upper is not None and lower != upper:
            msg = f'Error: operator \'{op.value}\' expected at between {lower} and {upper} arguments, received {received}.'
            raise SemanticAnalyzerException(msg)
        elif lower is not None and upper is not None and lower == upper:
            msg = f'Error: operator \'{op.value}\' expected {lower} arguments, received {received}.'
            raise SemanticAnalyzerException(msg)
        else:
            raise SemanticAnalyzerException()

    def unsupported_op_error(self, op):
        msg = f'Error: {op.value} is not a supported operation.'
        raise SemanticAnalyzerException(msg)


    def visit_Func(self, node: Func) -> None:
        op = node.op
        args_len = len(node.nodes)
        if op.type == TokenType.PLUS:
            pass
        elif op.type == TokenType.MINUS:
            if args_len == 0:
                self.arg_count_error(op=op, received=args_len, lower=1)
        elif op.type == TokenType.MUL:
            pass
        elif op.type == TokenType.DIV:
            if args_len == 0:
                self.arg_count_error(op=op, received=args_len, lower=1)
        elif op.type == TokenType.ID:
            if op.value == 'add1':
                if args_len != 1:
                    self.arg_count_error(op=op, received=args_len, lower=1, upper=1)
            else:
                self.unsupported_op_error(op)
        else:
            self.unsupported_op_error(op)

        for arg in node.nodes:
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
            raise NameError(f'Error: \'{var_name}\' was defined previously and cannot be re-defined.')

        self.current_scope.define(var_symb)

    def visit_FuncAssign(self, node: FuncAssign) -> None:
        func_name = node.identifier
        func_symbol = FuncSymbol(func_name)
        self.current_scope.define(func_symbol)

        print('')
        print(f'ENTER SCOPE: {func_name}')
        # scope for parameters and
        func_scope = ScopedSymbolTable(
            scope_name=func_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = func_scope

        # insert parameters into the procedure scope
        for param in node.params:
            param_name = param.const_node.value
            var_symbol = ConstSymbol(param_name)
            self.current_scope.define(var_symbol)
            func_symbol.params.append(var_symbol)

        self.visit(node.expr)

        print('')
        print(func_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print(f'LEAVE SCOPE: {func_name}')
        print('')

    def visit_Const(self, node: Const) -> None:
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise NameError(f'Error: Symbol(constant) not found \'{var_name}\'.')

    def visit_NoOp(self, node: NoOp) -> None:
        pass

    def visit_Program(self, node: Program) -> None:
        print('ENTER SCOPE: global')
        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = global_scope

        for child_node in node.children:
            self.visit(child_node)

        print('')
        print(global_scope)

        self.current_scope = self.current_scope.enclosing_scope
        print('LEAVE SCOPE: global')
