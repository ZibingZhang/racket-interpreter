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
            ; (define (f a z) a)
            (define (s t z) (- t 6))
            (define (t u s) (u s 1))
            (t s 6)
            ; (t + 6)
            ; (t s 10)
            ; (t add1 6)
            ; (t f 10)
            ; (t f 10)
            
            ""
            
            (define (mul2 n) (* 2 n))
            
            (define (factorial n)
                (if (= n 0)
                    1
                    (* n (factorial (- n 1)))))
            (factorial 10)
            
            (define (r f) (f 5))
            
            (r factorial)
            (r add1)
            (r mul2)
            (r +)
            
            ; (define (zz zzz) zzzz)
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
