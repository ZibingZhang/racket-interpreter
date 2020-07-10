from __future__ import annotations
from typing import TYPE_CHECKING, List
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d
from racketinterpreter.predefined.base import BuiltInProc

if TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes.interpreting import Interpreter


class StringAlphabeticHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.String,
                given=param_value
            )

        for char in param_value:
            if not char.isalpha():
                return d.Boolean(False)
        else:
            return d.Boolean(True)


class StringAppend(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.String:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.String):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.String,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.String('')

        for param in evaluated_params:
            result += param

        return result


class StringContainsHuh(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.String):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.String,
                    given=param_value
                )

            evaluated_params.append(param_value)

        substring = evaluated_params[0]
        containing_string = evaluated_params[1]
        result = substring in containing_string

        return d.Boolean(result)


class StringCopy(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.String,
                given=param_value
            )

        return param_value.copy()


class StringDowncase(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.String,
                given=param_value
            )

        return param_value.lower()


class StringIth(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        string = param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.String,
                given=param_value
            )

        index = param_value = interpreter.visit(actual_params[1])
        param_type = type(param_value)

        if not issubclass(param_type, d.Integer) and index >= 0:
            raise err.EvaluateBuiltinProcedureError(
                expected=d.NaturalNum,
                given=param_value
            )

        # TODO: string-ith: expected an exact integer in [0, 4) (i.e., less than the length of the given string) for the second argument, but received 10

        return string[index]


class StringHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.String))
        return result
