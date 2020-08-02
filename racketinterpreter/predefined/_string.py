from __future__ import annotations
import typing as tp
from racketinterpreter.classes import data as d
from racketinterpreter.classes import errors as err
from racketinterpreter.predefined._base import BuiltInProc

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.processes import Interpreter


class StringAlphabeticHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
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
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.String:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.String):
                raise err.ArgumentTypeError(
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
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.String):
                raise err.ArgumentTypeError(
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
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return param_value.copy()


class StringDowncase(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return param_value.lower()


class StringIth(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        string = param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        index = param_value = interpreter.visit(actual_params[1])
        param_type = type(param_value)

        if not issubclass(param_type, d.Integer) or index < d.Integer(0):
            message = f'string-ith: expected a natural number for the second argument, but received {index}'
            raise err.CustomBuiltinProcError(
                message=message
            )

        if index >= d.Integer(len(string)):
            message = f'string-ith: expected an exact integer [0, {len(string)}) '
            message += f'(i.e., less than the length of the given string) for the second argument, but received {index}'
            raise err.CustomBuiltinProcError(
                message=message
            )

        return string[index]


class StringLength(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.NaturalNum:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return d.NaturalNum(len(param_value))


class StringLowerCaseHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return param_value.islower()


class StringNumericHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return d.Boolean(param_value.isnumeric())


class StringUpcase(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return param_value.upper()


class StringUpperCaseHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return param_value.isupper()


class StringWhitespaceHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.String):
            raise err.ArgumentTypeError(
                expected=d.String,
                given=param_value
            )

        return d.Boolean(len(param_value) == 0) or param_value.isspace()


class StringHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.String))
        return result
