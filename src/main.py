from src import constants
from src.errors import InterpreterError, LexerError, ParserError, SemanticError
from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser
from src.semantics import SemanticAnalyzer


def main():
    constants.init(should_log_scope=False, should_log_stack=False)

    try:
        text = \
            """
            (and #t #t #f)
            ; (define (x a) (a 1))
            ; (define (y b) (add1 y))
            ; (x y)
            1
            """

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()

        semantic_analyzer = SemanticAnalyzer()
        try:
            semantic_analyzer.visit(tree)
        except SemanticError as e:
            print(e.message)
            return

        interpreter = Interpreter(tree)
        result = interpreter.interpret()

        print('')
        print('Output:')
        for output in result:
            print(f'     {output}')

    except (LexerError, ParserError, InterpreterError) as e:
        print(e.message)
        return


if __name__ == '__main__':
    main()
