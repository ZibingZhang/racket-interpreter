from racketinterpreter import constants
from racketinterpreter.interpreter import Interpreter
from racketinterpreter.lexer import Lexer
from racketinterpreter.parsing import Parser
from racketinterpreter.syntax import ParenthesesAnalyzer


class Util:

    @staticmethod
    def text_to_result(text: str, should_log_scope: bool = False, should_log_stack: bool = False):
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
