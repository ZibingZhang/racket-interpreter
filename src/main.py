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
            print(result)
        except (ParserError, LexerError) as e:
            print(e)


if __name__ == '__main__':
    main()
