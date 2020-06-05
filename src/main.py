from src.interpreter import Interpreter, InterpreterError
from src.lexer import Lexer, LexerError
from src.parser import Parser, ParserError


def main():
    while True:
        try:
            text = input('>>> ')
        except EOFError:
            break

        if not text:
            continue

        try:
            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
            for output in result:
                print(output)
        except (LexerError, ParserError, InterpreterError) as e:
            print(e)
        except NameError as e:
            print(f'Variable {e} is not defined.')


if __name__ == '__main__':
    main()
