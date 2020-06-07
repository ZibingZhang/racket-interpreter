from enum import Enum


class ErrorCode(Enum):

    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate identifier found'
    ARGUMENT_COUNT = 'Wrong number of arguments'
    NOT_A_PROCEDURE = 'Not a procedure'
    PROCEDURE_NOT_FOUND = 'Procedure not found'


class Error(Exception):

    def __init__(self, error_code=None, token=None, message=None) -> None:
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'[{self.__class__.__name__}] {message}'


class LexerError(Error):

    pass


class ParserError(Error):

    pass


class SemanticError(Error):

    pass


class InterpreterError(Error):

    pass

class IllegalStateError(RuntimeError):

    pass
