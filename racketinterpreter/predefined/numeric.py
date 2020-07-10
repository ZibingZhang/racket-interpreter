from __future__ import annotations
import math
import time
from typing import TYPE_CHECKING, List, Optional
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d
from racketinterpreter.predefined.base import BuiltInProc

if TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes.interpreting import Interpreter


class SymbolMultiply(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Number):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Number,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.Integer(1)
        for param_value in evaluated_params:
            if param_value == d.Integer(0):
                result = d.Integer(0)
                break

            result *= param_value

        return result


class SymbolPlus(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Number):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Number,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.Integer(0)
        for param_value in evaluated_params:
            result = result + param_value

        return result


class SymbolMinus(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Number):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Number,
                    given=param_value
                )

            evaluated_params.append(param_value)

        if len(actual_params) == 1:
            result = -evaluated_params[0]
        else:
            result = evaluated_params[0]
            for param_value in evaluated_params[1:]:
                result -= param_value

        return result


class SymbolDivide(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Number):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Number,
                    given=param_value
                )

            if idx == 0 and len(actual_params) == 1 and param_value == d.Integer(0):
                raise err.BuiltinProcedureError(
                    error_code=err.ErrorCode.DIVISION_BY_ZERO,
                    token=token
                )

            evaluated_params.append(param_value)

        if len(actual_params) == 1:
            result = d.Integer(1)/evaluated_params[0]
        else:
            result = evaluated_params[0]
            for param_value in evaluated_params[1:]:
                result /= param_value

        return result


class SymbolLessThan(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.RealNum):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.RealNum,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.Boolean(True)
        prev_value = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            current_value = param_value
            if not prev_value < current_value:
                result = d.Boolean(False)
                break

            prev_value = current_value

        return result


class SymbolLessEqualThan(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.RealNum):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.RealNum,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.Boolean(True)
        prev_value = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            current_value = param_value
            if not prev_value <= current_value:
                result = d.Boolean(False)
                break

            prev_value = current_value

        return result


class SymbolEqual(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Number):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Number,
                    given=param_value
                )

            evaluated_params.append(param_value)

        first_param_value = evaluated_params[0]

        result = d.Boolean(True)

        for param_value in evaluated_params:
            if first_param_value != param_value:
                result = d.Boolean(False)
                break

        return result


class SymbolGreaterThan(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.RealNum):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.RealNum,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.Boolean(True)
        prev_value = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            current_value = param_value
            if not prev_value > current_value:
                result = d.Boolean(False)
                break

            prev_value = current_value

        return result


class SymbolGreaterEqualThan(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.RealNum):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.RealNum,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = d.Boolean(True)
        prev_value = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            current_value = param_value
            if not prev_value >= current_value:
                result = d.Boolean(False)
                break

            prev_value = current_value

        return result


class Abs(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.RealNum):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.RealNum,
                given=param_value
            )

        result = abs(param_value)
        return result


class Add1(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = param_value + d.Integer(1)
        return result


class Ceiling(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.RealNum):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.RealNum,
                given=param_value
            )

        result = d.Integer(math.ceil(param_value.value))
        return result


class CurrentSeconds(BuiltInProc):

    LOWER = 0
    UPPER = 0

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        result = d.Integer(math.floor(time.time()))
        return result


class EvenHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Integer):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Integer,
                given=param_value
            )

        result = d.Boolean(param_value.value % 2 == 0)
        return result


class ExactToInexact(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = d.InexactNum(param_value.value)
        return result


class ExactHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = d.Boolean(issubclass(type(param_value), d.ExactNum))
        return result


class Exp(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = d.InexactNum(math.exp(param_value.value))
        return result


class Floor(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.RealNum):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.RealNum,
                given=param_value
            )

        result = d.Integer(math.floor(param_value.value))
        return result


class Gcd(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Integer:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Integer):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Integer,
                    given=param_value
                )

            evaluated_params.append(param_value)

        gcd = 0

        for param_value in evaluated_params:
            gcd = math.gcd(gcd, int(param_value))

        result = d.Integer(gcd)

        return result


class IntegerHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.Integer))
        return result


class Lcm(BuiltInProc):

    LOWER = 0
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Integer:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Integer):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Integer,
                    given=param_value
                )

            evaluated_params.append(param_value)

        lcm = 1

        for param_value in evaluated_params:
            lcm = abs(lcm * int(param_value)) // math.gcd(lcm, int(param_value))

        result = d.Integer(lcm)

        return result


class Log(BuiltInProc):
    # TODO: should be 1 to 2

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = d.InexactNum(math.log(param_value.value))
        return result


class Max(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.RealNum:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.RealNum):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.RealNum,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            if param_value > result:
                result = param_value

        return result


class Min(BuiltInProc):

    LOWER = 1
    UPPER = None

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.RealNum:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.RealNum):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.RealNum,
                    given=param_value
                )

            evaluated_params.append(param_value)

        result = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            if param_value < result:
                result = param_value

        return result


class Modulo(BuiltInProc):

    LOWER = 2
    UPPER = 2

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Integer:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)
            param_type = type(param_value)

            if not issubclass(param_type, d.Integer):
                raise err.EvaluateBuiltinProcedureError(
                    idx=idx,
                    expected=d.Integer,
                    given=param_value
                )

            evaluated_params.append(param_value)

        number = int(evaluated_params[0])
        modulus = int(evaluated_params[1])
        remainder = number % modulus
        result = d.Integer(remainder)

        return result


class NegativeHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.RealNum):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.RealNum,
                given=param_value
            )

        result = d.Boolean(param_value < d.Integer(0))
        return result


class NumberToString(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.String:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = d.String(str(param_value))
        return result


class NumberHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.Number))
        return result


class OddHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Integer):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Integer,
                given=param_value
            )

        result = d.Boolean(param_value.value % 2 == 1)
        return result


class PositiveHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.RealNum):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.RealNum,
                given=param_value
            )

        result = d.Boolean(param_value > d.Integer(0))
        return result


class RationalNumHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.RationalNum))
        return result


class RealHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        result = d.Boolean(issubclass(param_type, d.RealNum))
        return result


class Round(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Integer:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.RealNum):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.RealNum,
                given=param_value
            )

        result = d.Integer(round(param_value.value))
        return result


class Sgn(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Integer:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.RealNum):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.RealNum,
                given=param_value
            )

        if param_value > d.Integer(0):
            result = d.Integer(1)
        elif param_value < d.Integer(0):
            result = d.Integer(-1)
        else:
            result = d.Integer(0)

        return result


class Sqr(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = param_value * param_value

        return result


class Sqrt(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        if param_value < d.Integer(0):
            raise NotImplementedError('Complex numbers not supported yet.')

        number = math.sqrt(param_value.value)
        result = d.InexactNum(number)

        return result


class Sub1(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Number:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = param_value - d.Integer(1)
        return result


class ZeroHuh(BuiltInProc):

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])
        param_type = type(param_value)

        if not issubclass(param_type, d.Number):
            raise err.EvaluateBuiltinProcedureError(
                expected=d.Number,
                given=param_value
            )

        result = d.Boolean(param_value == d.Integer(0))
        return result
