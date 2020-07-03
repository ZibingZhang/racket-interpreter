from __future__ import annotations
import abc
import re
from typing import TYPE_CHECKING, List, Optional
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d

if TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes.interpreting import Interpreter


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
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Data:
        pass

    def interpret(self, interpreter: Interpreter, token: t.Token, actual_params: List[ast.AST]) -> d.Data:
        try:
            return self._interpret(
                interpreter=interpreter,
                token=token,
                actual_params=actual_params
            )
        except err.EvaluateBuiltinProcedureError as e:
            expected = e.expected
            given = e.given
            idx = e.idx

            error_code = err.ErrorCode.INCORRECT_ARGUMENT_TYPE
            name = self.derive_proc_name(self.__class__.__name__)
            multiple_args = len(actual_params) > 1

            raise err.BuiltinProcedureError(
                error_code=error_code,
                token=token,
                name=name,
                multiple_args=multiple_args,
                idx=idx,
                expected=expected,
                given=given
            )

    @staticmethod
    def derive_proc_name(class_name: str) -> str:
        symbols = {
            'Plus': '+',
            'Minus': '-',
            'Multiply': '*',
            'Divide': '/',
            'Equal': '=',
            'LessThan': '<',
            'Greater': '>',
            'LessEqualThan': '<=',
            'GreaterEqualThan': '>='
        }

        words = re.findall('[A-Z][^A-Z]*', class_name)
        proc_name = ''
        symbolic_word = False
        for word in words:
            if symbolic_word:
                proc_name += symbols[word]
                symbolic_word = False
                continue

            if word == 'Symbol':
                symbolic_word = True
            elif word == 'To':
                proc_name += '->'
            elif word == 'Huh':
                proc_name += '?'
            else:
                proc_name += word.lower()

        return proc_name
