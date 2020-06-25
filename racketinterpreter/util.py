from racketinterpreter import constants
from racketinterpreter.processes.interpreter import Interpreter
from racketinterpreter.processes.lexer import Lexer
from racketinterpreter.processes.syntax import ParenthesesAnalyzer
from racketinterpreter.processes.parse import Parser


class Util:

    @staticmethod
    def text_to_interpreter_result(text: str, should_log_scope: bool = False, should_log_stack: bool = False):
        constants.set_globals(should_log_scope=should_log_scope, should_log_stack=should_log_stack)

        lexer = Lexer(text)
        paren_analyzer = ParenthesesAnalyzer(lexer)
        paren_analyzer.analyze()

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()

        interpreter = Interpreter(tree)
        result = interpreter.interpret()

        return result
