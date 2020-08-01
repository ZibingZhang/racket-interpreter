import typing as tp
from racketinterpreter import constants
import racketinterpreter.classes.data as d
import racketinterpreter.classes.tokens as t
from racketinterpreter.processes import Interpreter
from racketinterpreter.processes import Lexer
from racketinterpreter.processes import Parser


class Util:

    @staticmethod
    def text_to_interpreter_result(
            text: str,
            should_log_scope: bool = False,
            should_log_stack: bool = False
    ) -> tp.Tuple[tp.List[d.Data], tp.List[tp.Tuple[bool, t.Token, d.Data, d.Data]]]:
        constants.set_globals(should_log_scope=should_log_scope, should_log_stack=should_log_stack)

        lexer = Lexer(text)
        lexer.process()
        parser = Parser(lexer)
        tree = parser.parse()

        interpreter = Interpreter()
        output, test_output = interpreter.interpret(tree)

        return output, test_output
