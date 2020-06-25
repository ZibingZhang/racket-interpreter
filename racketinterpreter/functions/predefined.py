from __future__ import annotations
import abc
import math
import time
from typing import TYPE_CHECKING, List, Optional
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d

if TYPE_CHECKING:
    from racketinterpreter.classes.ast import AST
    from processes.interpreter import Interpreter
    from classes.tokens import Token


# TODO: fix all these errors oops
class BuiltInProc(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def lower() -> int:
        """Lower bound on number of formal_params."""
        pass

    @staticmethod
    @abc.abstractmethod
    def upper() -> Optional[int]:
        """Upper bound on number of formal_params (None indicates no bound)."""
        pass

    @staticmethod
    @abc.abstractmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Data:
        pass


class If(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 3

    @staticmethod
    def upper() -> Optional[int]:
        return 3

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Data:
        boolean = interpreter.visit(actual_params[0])
        if bool(boolean):
            result = interpreter.visit(actual_params[1])
        else:
            result = interpreter.visit(actual_params[2])
        return result


class SymbolPlus(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        result = d.Integer(0)
        for param_value in evaluated_params:
            result += param_value

        return result


class SymbolMinus(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        if len(actual_params) == 1:
            result = -evaluated_params[0]
        else:
            result = evaluated_params[0]
            for param_value in evaluated_params[1:]:
                result -= param_value

        return result


class SymbolMultiply(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        result = d.Integer(1)
        for param_value in evaluated_params:
            if param_value == d.Integer(0):
                result = d.Integer(0)
                break

            result *= param_value

        return result


class SymbolDivide(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
                )

            if idx == 0 and len(actual_params) == 1 and param_value == d.Integer(0):
                raise err.BuiltinProcedureError(
                    error_code=err.ErrorCode.DIVISION_BY_ZERO,
                    token=proc_token
                )

            evaluated_params.append(param_value)

        if len(actual_params) == 1:
            result = d.Integer(1)/evaluated_params[0]
        else:
            result = evaluated_params[0]
            for param_value in evaluated_params[1:]:
                result /= param_value

        return result


class SymbolEqual(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        first_param_value = evaluated_params[0]

        result = d.Boolean(True)

        for param_value in evaluated_params:
            if first_param_value != param_value:
                result = d.Boolean(False)
                break

        return result


class SymbolLessThan(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
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


class SymbolGreaterThan(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
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


class SymbolLessEqualThan(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
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


class SymbolGreaterEqualThan(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=idx
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
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.RealNumber):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Real Number',
                param_value=param_value,
                idx=0
            )

        result = abs(param_value)
        return result


class Add1(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = param_value + d.Integer(1)
        return result


class Ceiling(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.RealNumber):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Real Number',
                param_value=param_value,
                idx=0
            )

        result = d.Integer(math.ceil(param_value.value))
        return result


class CurrentSeconds(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return 0

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        result = d.Integer(math.floor(time.time()))
        return result


class EvenHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Integer):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Integer',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(param_value.value % 2 == 0)
        return result


class ExactToInexact(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = d.InexactNumber(param_value.value)
        return result


class ExactHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(issubclass(type(param_value), d.ExactNumber))
        return result


class Exp(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = d.InexactNumber(math.exp(param_value.value))
        return result


class Floor(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.RealNumber):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Real Number',
                param_value=param_value,
                idx=0
            )

        result = d.Integer(math.floor(param_value.value))
        return result


class Gcd(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Integer:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Integer):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Integer',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        gcd = 0

        for param_value in evaluated_params:
            gcd = math.gcd(gcd, int(param_value))

        result = d.Integer(gcd)

        return result


class IntegerHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        result = d.Boolean(issubclass(type(param_value), d.Integer))
        return result


class Lcm(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Integer:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Integer):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Integer',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        lcm = 1

        for param_value in evaluated_params:
            lcm = abs(lcm * int(param_value)) // math.gcd(lcm, int(param_value))

        result = d.Integer(lcm)

        return result


class Log(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = d.InexactNumber(math.log(param_value.value))
        return result


class Max(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.RealNumber:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.RealNumber):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Real Number',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        result = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            if param_value > result:
                result = param_value

        return result


class Min(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.RealNumber:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.RealNumber):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Real Number',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        result = evaluated_params[0]

        for param_value in evaluated_params[1:]:
            if param_value < result:
                result = param_value

        return result


class Modulo(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 2

    @staticmethod
    def upper() -> Optional[int]:
        return 2

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Integer:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Integer):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Integer',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        number = int(evaluated_params[0])
        modulus = int(evaluated_params[1])
        remainder = number % modulus
        result = d.Integer(remainder)

        return result


class NegativeHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.RealNumber):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Real Number',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(param_value < d.Integer(0))
        return result


class NumberToString(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.String:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = d.String(str(param_value))
        return result


class NumberHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Data):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Any',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(issubclass(type(param_value), d.Number))
        return result


class OddHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Integer):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Integer',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(param_value.value % 2 == 1)
        return result


class PositiveHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.RealNumber):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Real Number',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(param_value > d.Integer(0))
        return result


class RationalHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Data):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Any',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(issubclass(type(param_value), d.Rational))
        return result


class RealHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Data):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Any',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(issubclass(type(param_value), d.RealNumber))
        return result


class Round(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Integer:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.RealNumber):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Real Number',
                param_value=param_value,
                idx=0
            )

        result = d.Integer(round(param_value.value))
        return result


class Sgn(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Integer:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.RealNumber):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Real Number',
                param_value=param_value,
                idx=0
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
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = param_value * param_value

        return result


class Sqrt(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        if param_value < d.Integer(0):
            raise NotImplementedError('Complex numbers not supported yet.')

        number = math.sqrt(param_value.value)
        result = d.InexactNumber(number)

        return result


class Sub1(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = param_value - d.Integer(1)
        return result


class ZeroHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(param_value == d.Integer(0))
        return result


class And(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        result = d.Boolean(True)

        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Boolean):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Boolean',
                    param_value=param_value,
                    idx=idx
                )

            if param_value == d.Boolean(False):
                result = param_value
                break

        return result


class BooleanToString(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.String:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Boolean):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Boolean',
                param_value=param_value,
                idx=0
            )

        result = d.String(str(param_value))
        return result


class BooleanSymbolEqualHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        evaluated_params = []
        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Boolean):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Boolean',
                    param_value=param_value,
                    idx=idx
                )

            evaluated_params.append(param_value)

        first_param_value = evaluated_params[0]

        result = d.Boolean(True)

        for param_value in evaluated_params:
            if first_param_value != param_value:
                result = d.Boolean(False)
                break

        return result


class BooleanHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Data):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Any',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(issubclass(type(param_value), d.Boolean))
        return result


class FalseHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Data):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Any',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(issubclass(type(param_value), d.Boolean) and param_value == d.Boolean(False))
        return result


class Not(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Boolean):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Boolean',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(not param_value.value)
        return result


class Or(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        result = d.Boolean(False)

        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), d.Boolean):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Boolean',
                    param_value=param_value,
                    idx=idx
                )

            if param_value == d.Boolean(True):
                result = param_value
                break

        return result


class StringHuh(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> d.Boolean:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), d.Data):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Any',
                param_value=param_value,
                idx=0
            )

        result = d.Boolean(issubclass(type(param_value), d.String))
        return result


BUILT_IN_PROCS = {
    # control flow
    'if': If,
    # numeric
    '+': SymbolPlus,
    '-': SymbolMinus,
    '*': SymbolMultiply,
    '/': SymbolDivide,
    '=': SymbolEqual,
    '<': SymbolLessThan,
    '>': SymbolGreaterThan,
    '<=': SymbolLessEqualThan,
    '>=': SymbolGreaterEqualThan,
    'abs': Abs,
    'add1': Add1,
    'ceiling': Ceiling,
    'current-seconds': CurrentSeconds,
    'even?': EvenHuh,
    'exact->inexact': ExactToInexact,
    'exact?': ExactHuh,
    'exp': Exp,
    'floor': Floor,
    'gcd': Gcd,
    'integer?': IntegerHuh,
    'lcm': Lcm,
    'log': Log,
    'max': Max,
    'min': Min,
    'modulo': Modulo,
    'negative?': NegativeHuh,
    'number->string': NumberToString,
    'number?': NumberHuh,
    'odd?': OddHuh,
    'positive?': PositiveHuh,
    'rational?': RationalHuh,
    'real?': RealHuh,
    'round': Round,
    'sgn': Sgn,
    'sqr': Sqr,
    'sqrt': Sqrt,  # cannot handle negative numbers for now
    'sub1': Sub1,
    'zero?': ZeroHuh,
    # boolean
    'and': And,
    'boolean->string': BooleanToString,
    'boolean=?': BooleanSymbolEqualHuh,
    'boolean?': BooleanHuh,
    'false?': FalseHuh,
    'not': Not,
    'or': Or,
    # string,
    # 'string-alphabetic?': StringAlphabeticHuh,
    # 'string-append': StringAppend,
    # 'string-contains?': StringContainsHuh,
    # 'string-downcase': StringDowncase,
    # 'string-ith': StringIth,
    # 'string-length': StringLength,
    # 'string-lower-case?': StringLowerCaseHuh,
    # 'string-numeric?': StringNumericHuh,
    # 'string-upcase': StringUpcase,
    # 'string-upper-case?': StringUpperCaseHuh,
    # 'string-whitespace': StringWhitespace,
    # 'string<=?': StringSymbolLessEqualHuh,
    # 'string<?': StringSymbolLessHuh,
    # 'string=?': StringSymbolEqualHuh,
    # 'string>=?': StringSymbolGreaterEqualHuh,
    # 'string>?': StringSymbolGreaterHuh,
    'string?': StringHuh,
    # 'substring': Substring
}