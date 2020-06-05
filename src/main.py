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
            tree = parser.parse()
            interpreter = Interpreter(tree)
            result = interpreter.interpret()
            for output in result:
                print(output)
        except (LexerError, ParserError, InterpreterError) as e:
            print(e)
        except NameError as e:
            print(e)


if __name__ == '__main__':
    # main()
    from src.symbol import SymbolTableBuilder
    try:
        text = """
        (define a 6)
        (define b -6)
        (* a b)
        """
        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        sym_table_builder = SymbolTableBuilder()
        sym_table_builder.visit(tree)
        print('')
        print('Symbol Table contents:')
        print(sym_table_builder.sym_table)

        interpreter = Interpreter(tree)
        result = interpreter.interpret()

        print('')
        print('Run-time GLOBAL_MEMORY contents:')
        for k, v in sorted(interpreter.GLOBAL_MEMORY.items()):
            print('{} = {}'.format(k, v))

        print('')
        print('Output:')
        for output in result:
            print(output)

    except NameError as e:
        print(e)
