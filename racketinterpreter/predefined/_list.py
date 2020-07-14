from __future__ import annotations
import typing as tp
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d
from racketinterpreter.predefined._base import BuiltInProc

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.processes import Interpreter


def _interpret_nth(interpreter: Interpreter, actual_params: tp.List[ast.AST], idx: int) -> d.Data:
    param_value = interpreter.visit(actual_params[0])
    param_type = type(param_value)

    if not issubclass(param_type, d.List) or len(param_value) <= idx:
        raise err.EvaluateBuiltinProcedureError(
            expected=d.List,
            given=param_value,
            min_length=idx+1,
            max_length=None
        )

    result = param_value[idx]
    return result


class Append(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.List:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.List):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.List,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.List([])

        for param in evaluated_params:
            result.extend(param)

        # TODO: append: last argument must be a list, but received 1
        return result


class Cons(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.List:
        first = interpreter.visit(actual_params[0])

        rest = param_value = interpreter.visit(actual_params[1])
        param_type = type(param_value)

        if not issubclass(param_type, d.List):
            raise err.EvaluateBuiltinProcedureError(
                error_code=err.ErrorCode.CL_EXPECTED_SECOND_ARGUMENT_LIST,
                arg1=first,
                arg2=rest
            )

        result = d.List([first] + list(rest))
        return result


class ConsHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = d.Boolean(is_list and len(param_value) > 0)
        return result


class Eighth(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 7)


class EmptyHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = d.Boolean(is_list and len(param_value) == 0)
        return result


class Fifth(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 4)


class First(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 0)


class Fourth(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 3)


class Length(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
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
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.List:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            evaluated_params.append(param_value)

        result = d.List(evaluated_params)
        return result


class ListHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)
        is_list = issubclass(param_type, d.List)

        result = d.Boolean(is_list)
        return result


class MakeList(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.List:
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
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Boolean:
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


class Rest(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.List:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List) or len(param_value) == 0:
            raise err.EvaluateBuiltinProcedureError(
                expected=d.List,
                given=param_value,
                min_length=1,
                max_length=None
            )

        result = param_value[1:]
        return result


class Reverse(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.List:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.List):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.List,
                given=param_value
            )

        result = param_value[::-1]
        return result


class Second(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 1)


class Seventh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 6)


class Sixth(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 5)


class Third(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        return _interpret_nth(interpreter, actual_params, 2)
