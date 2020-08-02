from __future__ import annotations
import typing as tp
from racketinterpreter.classes import data as d
from racketinterpreter.classes import errors as err
from racketinterpreter.predefined._base import BuiltInProc

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.processes import Interpreter


class And(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        result = d.Boolean(True)

        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Boolean):
                raise err.ArgumentTypeError(
                    idx=idx,
                    expected=d.Boolean,
                    given=param_value
                )

            if param_value == d.Boolean(False):
                result = param_value
                break

        return result


class BooleanToString(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Boolean):
            raise err.ArgumentTypeError(
                expected=d.Boolean,
                given=param_value
            )

        result = d.String(str(param_value))
        return result


class BooleanSymEqualHuh(BuiltInProc):

    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Boolean):
                raise err.ArgumentTypeError(
                    idx=idx,
                    expected=d.Boolean,
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


class BooleanHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.Boolean))
        return result


class FalseHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.Boolean) and param_value == d.Boolean(False))
        return result


class Not(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Boolean):
            raise err.ArgumentTypeError(
                expected=d.Boolean,
                given=param_value
            )

        result = d.Boolean(not param_value.value)
        return result


class Or(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        result = d.Boolean(False)

        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Boolean):
                raise err.ArgumentTypeError(
                    idx=idx,
                    expected=d.Boolean,
                    given=param_value
                )

            if param_value == d.Boolean(True):
                result = param_value
                break

        return result
