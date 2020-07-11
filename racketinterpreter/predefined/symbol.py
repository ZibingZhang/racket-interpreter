from __future__ import annotations
import typing as tp
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d
from racketinterpreter.predefined.base import BuiltInProc

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes.interpreting import Interpreter


class SymbolToString(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Symbol):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Boolean,
                given=param_value
            )

        result = d.String(str(param_value)[1:])
        return result


class SymbolSymEqualHuh(BuiltInProc):

    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Symbol):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Symbol,
                    given=param_value
                )

            evaluated_params.append(param_value)

        first_param_value = evaluated_params[0]

        result = d.Boolean(True)

        for param_value in evaluated_params:
            if param_value != first_param_value:
                result = d.Boolean(False)
                break

        return result


class SymbolHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.Symbol))
        return result
