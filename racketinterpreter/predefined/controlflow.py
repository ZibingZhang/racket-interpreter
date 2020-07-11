from __future__ import annotations
import typing as tp
from racketinterpreter.classes import data as d
from racketinterpreter.predefined.base import BuiltInProc

if tp.TYPE_CHECKING:
    from racketinterpreter.classes import ast
    from racketinterpreter.classes import tokens as t
    from racketinterpreter.processes.interpreting import Interpreter


class If(BuiltInProc):

    LOWER = 3
    UPPER = 3

    @staticmethod
    def _interpret(interpreter: Interpreter, token: t.Token, actual_params: tp.List[ast.AST]) -> d.Data:
        boolean = interpreter.visit(actual_params[0])

        if bool(boolean):
            result = interpreter.visit(actual_params[1])
        else:
            result = interpreter.visit(actual_params[2])

        return result
