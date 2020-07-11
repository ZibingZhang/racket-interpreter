if __name__ == '__main__':
    import os
    import sys

    sys.path.append(os.getcwd())

    from racketinterpreter import constants
    from racketinterpreter import errors as err
    from racketinterpreter.classes import stack
    from racketinterpreter.processes import Interpreter
    from racketinterpreter.processes import Lexer
    from racketinterpreter.processes import Parser


    class Interactive:
        """
        The ultimate goal is to have this be a class which you can pass code and receive responses immediately without
        having to run through the process of setting up an interpreter, it would have its own internal interpreter which
        you could reset and interact with.

        For now it behaves as an interactive session.
        """

        def __init__(self):
            self.interpreter = None

        def process(self, text):
            try:
                lexer = Lexer(text)
                lexer.process()
                parser = Parser(lexer)

                program = parser.parse()
                statements = program.statements

                lines = []
                for statement in statements:
                    result = self.interpreter.visit(statement)
                    if result is not None:
                        lines.append(result)

                return lines

            except err.Error as e:
                return [e.message[e.message.index(']')+2:]]

        def run(self):
            while True:
                self.interpreter = Interpreter()

                ar = stack.ActivationRecord(
                    name='global',
                    type=stack.ARType.PROGRAM,
                    nesting_level=1
                )

                with ar(self.interpreter):
                    with self.interpreter.semantic_analyzer(entering='PROGRAM'):
                        self.interpreter._define_builtin_procs()

                        while True:
                            text = input('> ')
                            if text.isspace():
                                pass
                            elif text in ['/reset', '/exit']:
                                break
                            else:
                                lines = self.process(text)
                                for line in lines:
                                    print(line)

                if text == '/exit':
                    break

    constants.set_globals(should_log_scope=False, should_log_stack=False)

    interactive = Interactive()
    interactive.run()
