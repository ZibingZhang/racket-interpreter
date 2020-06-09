from __future__ import annotations
import abc
from typing import TYPE_CHECKING, List, Optional
from src.datatype import Boolean, Number, String

if TYPE_CHECKING:
    from src.ast import AST
    from src.datatype import DataType
    from src.interpreter import Interpreter
    from src.token import Token


class BuiltInProc(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def lower() -> int:
        """Lower bound on number of params."""
        pass

    @staticmethod
    @abc.abstractmethod
    def upper() -> Optional[int]:
        """Upper bound on number of params (None indicates no bound)."""
        pass

    @staticmethod
    @abc.abstractmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> DataType:
        pass


class SymbolPlus(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> Number:
        if len(actual_params) == 0:
            result = Number(0)
        else:
            result = Number(0)
            for idx, param in enumerate(actual_params):
                param_value = interpreter.visit(param)

                if not issubclass(type(param_value), Number):
                    interpreter.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=idx
                    )

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
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> Number:
        if len(actual_params) == 1:
            param = actual_params[0]
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=0
                )

            result = Number(-param_value)
        else:
            param_value = interpreter.visit(actual_params[0])

            if not issubclass(type(param_value), Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=0
                )

            result = param_value
            params = actual_params[1:]
            for idx, param in enumerate(params):
                param_value = interpreter.visit(param)

                if not issubclass(type(param_value), Number):
                    interpreter.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=idx
                    )

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
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> Number:
        if len(actual_params) == 0:
            result = Number(1)
        else:
            result = Number(1)
            for idx, param in enumerate(actual_params):
                param_value = interpreter.visit(param)

                if not issubclass(type(param_value), Number):
                    interpreter.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=idx
                    )

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
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> Number:
        if len(actual_params) == 1:
            param = actual_params[0]
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=0
                )

            result = Number(-param_value)
        else:
            param_value = interpreter.visit(actual_params[0])

            if not issubclass(type(param_value), Number):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Number',
                    param_value=param_value,
                    idx=0
                )

            result = param_value
            params = actual_params[1:]
            for idx, param in enumerate(params):
                param_value = interpreter.visit(param)

                if not issubclass(type(param_value), Number):
                    interpreter.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=idx
                    )

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
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> Boolean:
        first_param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(first_param_value), Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=first_param_value,
                idx=0
            )

        result = Boolean(True)

        if len(actual_params) > 1:
            params = actual_params[1:]
            for idx, param in enumerate(params):
                param_value = interpreter.visit(param)

                if not issubclass(type(param_value), Number):
                    interpreter.builtin_proc_type_error(
                        proc_token=proc_token,
                        expected_type='Number',
                        param_value=param_value,
                        idx=idx
                    )

                if first_param_value != param_value:
                    result = Boolean(False)
                    break
        return result


class Add1(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 1

    @staticmethod
    def upper() -> Optional[int]:
        return 1

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> Number:
        param_value = interpreter.visit(actual_params[0])

        if not issubclass(type(param_value), Number):
            interpreter.builtin_proc_type_error(
                proc_token=proc_token,
                expected_type='Number',
                param_value=param_value,
                idx=0
            )

        result = param_value + Number(1)
        return result


class And(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 0

    @staticmethod
    def upper() -> Optional[int]:
        return None

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> Boolean:
        result = Boolean(True)

        for idx, param in enumerate(actual_params):
            param_value = interpreter.visit(param)

            if not issubclass(type(param_value), Boolean):
                interpreter.builtin_proc_type_error(
                    proc_token=proc_token,
                    expected_type='Boolean',
                    param_value=param_value,
                    idx=idx
                )

            if param_value == Boolean(False):
                result = param_value
                break
        return result


class If(BuiltInProc):

    @staticmethod
    def lower() -> int:
        return 3

    @staticmethod
    def upper() -> Optional[int]:
        return 3

    @staticmethod
    def interpret(interpreter: Interpreter, actual_params: List[AST], proc_token: Token) -> DataType:
        boolean = interpreter.visit(actual_params[0])
        if bool(boolean):
            result = interpreter.visit(actual_params[1])
        else:
            result = interpreter.visit(actual_params[2])
        return result


BUILT_IN_PROCS = {
    '+': SymbolPlus,
    '-': SymbolMinus,
    '*': SymbolMultiply,
    '/': SymbolDivide,
    '=': SymbolEqual,
    'add1': Add1,
    'and': And,
    'if': If
}
