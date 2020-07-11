from __future__ import annotations
import typing as tp
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d
from racketinterpreter.predefined.base import BuiltInProc

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes.interpreting import Interpreter


class ConsHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = d.Boolean(is_list and len(param_value) > 0)
        return result


class EmptyHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = d.Boolean(is_list and len(param_value) == 0)
        return result


class First(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Data:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List) or len(param_value) == 0:
            raise err.EvaluateBuiltinProcedureError(
                expected=d.ConsList,
                given=param_value
            )

        result = param_value[0]
        return result


class Length(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Data:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.List,
                given=param_value
            )

        result = d.NaturalNum(len(param_value))
        return result


class List(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.List:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            evaluated_params.append(param_value)

        result = d.List(evaluated_params)
        return result


class ListHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = d.Boolean(is_list)
        return result


class MakeList(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.List:
        count = param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Integer) or param_value < d.Integer(0):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.NaturalNum,
                given=param_value
            )

        data = interpreter.visit(actual_params[1])

        result = d.List(int(count) * [data])
        return result


class Member(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        item = interpreter.visit(actual_params[0])

        list_ = param_value = interpreter.visit(actual_params[1])
        param_type = type(param_value)

        if not issubclass(param_type, d.List):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.List,
                given=param_value
            )

        result = d.Boolean(item in list_)
        return result


class MemberHuh(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        item = interpreter.visit(actual_params[0])

        list_ = param_value = interpreter.visit(actual_params[1])
        param_type = type(param_value)

        if not issubclass(param_type, d.List):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.List,
                given=param_value
            )

        result = d.Boolean(item in list_)
        return result


class NullHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = d.Boolean(is_list and len(param_value) == 0)
        return result


class Rest(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.List:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List) or len(param_value) == 0:
            raise err.EvaluateBuiltinProcedureError(
                expected=d.ConsList,
                given=param_value
            )

        result = param_value[1:]
        return result


class Reverse(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.List:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.List,
                given=param_value
            )

        result = param_value[::-1]
        return result
