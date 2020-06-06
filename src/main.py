from src.interpreter import Interpreter, InterpreterError
from src.lexer import Lexer, LexerError
from src.parser import Parser, ParserError
from src.semantics import SemanticAnalyzer


def main():
    try:
        text = \
            """
            (define x -3)
            ; (define x 3)
            (define y "three")
            (define z #f)
            x y z
            
            (define (f a) a)
            """

        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()

        semantic_analyzer = SemanticAnalyzer()
        try:
            semantic_analyzer.visit(tree)
        except NameError as e:
            print(e)
            return

        print('')
        print(semantic_analyzer.sym_table)

        interpreter = Interpreter(tree)
        result = interpreter.interpret()

        print('')
        print('Run-time GLOBAL_MEMORY Contents:')
        for k, v in sorted(interpreter.GLOBAL_MEMORY.items()):
            print(f'{k:>10} = {v}')

        print('')
        print('Output:')
        for output in result:
            print(f'     {output}')

    except (LexerError, ParserError, InterpreterError) as e:
        print(e)
    # except NameError as e:
    #     print(e)


if __name__ == '__main__':
    main()
