from __future__ import annotations
from typing import TYPE_CHECKING, List
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d
from racketinterpreter.predefined.base import BuiltInProc

if TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes.interpreting import Interpreter


class ConsHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = is_list and len(param_value) > 0
        return d.Boolean(result)


class EmptyHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = is_list and len(param_value) == 0
        return d.Boolean(result)


class First(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Data:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List) or len(param_value) == 0:
            raise err.EvaluateBuiltinProcedureError(
                expected=d.ConsList,
                given=param_value
            )

        return param_value[0]


class Rest(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Data:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List) or len(param_value) == 0:
            raise err.EvaluateBuiltinProcedureError(
                expected=d.ConsList,
                given=param_value
            )

        return param_value[1:]
