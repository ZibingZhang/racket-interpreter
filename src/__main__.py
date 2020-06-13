from src import constants
from src.constants import C
from src.errors import InterpreterError, LexerError, ParserError, SemanticError
from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser


def main():
    constants.init(should_log_scope=False, should_log_stack=False)

    try:
        text = \
            """
            (zero? (add1 -1))
            """

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()

        interpreter = Interpreter(tree)
        result = interpreter.interpret()

        if C.SHOULD_LOG_SCOPE or C.SHOULD_LOG_STACK:
            print('')
        print('Output:')
        for output in result:
            print(f'     {output}')

    except (LexerError, ParserError, InterpreterError, SemanticError) as e:
        print(e.message)
        return


if __name__ == '__main__':
    main()
