from __future__ import annotations
import abc
import re
import typing as tp
from racketinterpreter import errors as err
from racketinterpreter.classes import data as d

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes import Interpreter


class BuiltInProc(abc.ABC):
    """A builtin procedure."""

    #: Lower bound on the number of arguments expected.
    LOWER = 1

    #: Upper bound on the number of arguments expected.
    UPPER = 1

    @staticmethod
    @abc.abstractmethod
    def _interpret(interpreter: Interpreter, actual_params: tp.List[ast.AST]) -> d.Data:
        pass

    def interpret(self, interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Data:
        try:
            return self._interpret(
                interpreter=interpreter,
                actual_params=actual_params
            )
        except err.EvaluateBuiltinProcedureError as e:
            error_code = e.error_code


            if error_code == err.ErrorCode.INCORRECT_ARGUMENT_TYPE:
                name = self.derive_proc_name(self.__class__.__name__)
                multiple_args = len(actual_params) > 1
                idx = e.idx
                expected = e.expected
                given = e.given

                min_length = max_length = None
                if expected is d.List:
                    min_length = e.kwargs.get('min_length')
                    max_length = e.kwargs.get('max_length')

                raise err.BuiltinProcedureError(
                    error_code=error_code,
                    token=token,
                    name=name,
                    multiple_args=multiple_args,
                    idx=idx,
                    expected=expected,
                    min_length=min_length,
                    max_length=max_length,
                    given=given
                )

            elif error_code == err.ErrorCode.DIVISION_BY_ZERO:
                raise err.BuiltinProcedureError(
                    error_code=error_code,
                    token=token
                )

            elif error_code == err.ErrorCode.CL_EXPECTED_SECOND_ARGUMENT_LIST:
                arg1 = e.kwargs.get('arg1')
                arg2 = e.kwargs.get('arg2')

                raise err.BuiltinProcedureError(
                    error_code=error_code,
                    token=token,
                    arg1=arg1,
                    arg2=arg2
                )

            else:
                raise err.IllegalStateError

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
            'GreaterEqualThan': '>=',
            'Star': '*'
        }

        words = re.findall('[A-Z][^A-Z]*', class_name)
        proc_name = ''
        symbolic_word = False
        for word in words:
            if symbolic_word:
                proc_name += symbols[word]
                symbolic_word = False
                continue

            if word == 'Sym':
                symbolic_word = True
            elif word == 'To':
                proc_name += '->'
            elif word == 'Huh':
                proc_name += '?'
            else:
                proc_name += word.lower()

        return proc_name
