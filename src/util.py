from src import constants
from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser
from src.syntax import ParenthesesAnalyzer


class Util:

    @staticmethod
    def text_to_result(text: str, should_log_scope: bool = False, should_log_stack: bool = False):
        constants.init(should_log_scope=should_log_scope, should_log_stack=should_log_stack)

        lexer = Lexer(text)
        paren_analyzer = ParenthesesAnalyzer(lexer)
        paren_analyzer.analyze()

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()

        interpreter = Interpreter(tree)
        result = interpreter.interpret()

        return result
