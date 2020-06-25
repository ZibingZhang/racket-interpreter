from typing import List, Optional
from racketinterpreter.errors import Error
from racketinterpreter.util import Util


class Result:

    def __init__(self,
                 output: Optional[List[str]] = None,
                 error: bool = False,
                 error_message: Optional[str] = None):
        self.output = output
        self.error = error
        self.error_message = error_message


def interpret(code: str) -> Result:
    try:
        output = list(map(str, Util.text_to_interpreter_result(code)))
        return Result(
            output=output
        )
    except Error as e:
        return Result(
            error=True,
            error_message=e.message
        )
