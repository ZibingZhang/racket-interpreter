from typing import List, Optional, Tuple
from racketinterpreter.errors import Error
from racketinterpreter.util import Util


class Result:

    def __init__(self,
                 output: Optional[List[str]] = None,
                 error: bool = False,
                 error_message: Optional[str] = None,
                 # passed, line_no, column, actual, expected
                 tests: Optional[List[Tuple[bool, int, int, str, str]]] = None) -> None:
        self.output = output if output is not None else []
        self.error = error
        self.error_message = error_message
        self.tests = tests if tests is not None else []
        self.tests_run = len(self.tests)
        self.tests_passed = len([test for test in self.tests if test[0] is False])
        self.tests_failed = self.tests_run - self.tests_passed

    def __str__(self) -> str:
        result = ''

        if self.error:
            result += 'Error:'
            result += f'\n     {self.error_message}'
            return result

        if len(self.output) > 0:
            result += 'Output:'
            for line in self.output:
                result += f'\n     {line}'

        if len(self.tests) > 0:
            if len(self.output) > 0:
                result += '\n\n'

            result += 'Test Results\n'
            result += '============\n'

            if self.tests_failed == 0:
                passed = self.tests_passed
                if passed == 1:
                    result += 'The test passed!'
                elif passed == 2:
                    result += 'Both tests passed!'
                else:
                    result += f'All {passed} tests passed!'

            else:
                if self.tests_passed == 0:
                    result += f'0 tests passed.\n\n'
                else:
                    result += f'{self.tests_failed} of the {self.tests_run} tests failed.\n\n'
                result += 'Check failures:'
                for error, line_no, column, actual, expected in self.tests:
                    if error:
                        result += f'\n     [{line_no}:{column}] ' \
                            f'Actual value {actual} differs from {expected}, the expected value.'

        return result


def interpret(code: str) -> Result:
    try:
        output, test_output = Util.text_to_interpreter_result(code)

        output = list(map(str, output))
        tests = []
        for test in test_output:
            tests.append((test[0], test[1].line_no, test[1].column, str(test[2]), str(test[3])))

        return Result(
            output=output,
            tests=tests
        )
    except Error as e:
        return Result(
            error=True,
            error_message=e.message
        )
