from src import constants
from src.constants import C
from src.interpreter import Interpreter, InterpreterError
from src.lexer import Lexer, LexerError
from src.parser import Parser, ParserError
from src.semantics import SemanticAnalyzer, SemanticError


def main():
    constants.init(should_log_scope=False, should_log_stack=True)

    try:
        text = \
            """
            (define x -3)
            ; (define x 3)
            (define y "three")
            ; (define z #f) )
            ; (add1 x) y z ; t
            
            (define (f x) y)
            ; (define f x)
            
            ; (define (r x) (r x))
            
            ; (f 1 2)
            ; (f  4 4 4 4 4)
            
            (f 1)
            
            ; (define (f x b) x)
            ; (define (g a c) a)
            ; (f 1)
            """

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        # print(tree.children)

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
