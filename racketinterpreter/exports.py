from typing import List, Optional, Tuple
from racketinterpreter.errors import Error
from racketinterpreter.util import Util


class TestResult:

    def __init__(
            self,
            passed: bool,
            line_no: int,
            column: int,
            actual: str,
            expected: str
    ) -> None:
        self._passed = passed
        self._line_no = line_no
        self._column = column
        self._actual = actual
        self._expected = expected

    @property
    def passed(self) -> bool:
        return self._passed

    @property
    def line_no(self) -> int:
        return self._line_no

    @property
    def column(self) -> int:
        return self._column

    @property
    def actual(self) -> str:
        return self._actual

    @property
    def expected(self) -> str:
        return self._expected

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == 5:
            raise StopIteration

        result = {
            0: self.passed,
            1: self.line_no,
            2: self.column,
            3: self.actual,
            4: self.expected,
        }[self.index]

        self.index += 1

        return result


class Result:

    def __init__(
            self,
            output: Optional[List[str]] = None,
            error: bool = False,
            error_message: Optional[str] = None,
            tests: List[TestResult] = None
    ) -> None:
        self.output = output if output is not None else []
        self.error = error
        self.error_message = error_message
        self.tests = tests if tests is not None else []
        self.tests_run = len(self.tests)
        self.tests_passed = len([test for test in self.tests if test.passed])
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
                for passed, line_no, column, actual, expected in self.tests:
                    if not passed:
                        result += f'\n     [{line_no}:{column}] ' \
                                  f'Actual value {actual} differs from {expected}, the expected value.'

        return result


def interpret(code: str) -> Result:
    try:
        output, test_output = Util.text_to_interpreter_result(code)

        output = list(map(str, output))
        test_results = []
        for passed, token, actual, expected in test_output:
            test_result = TestResult(
                passed=passed,
                line_no=token.line_no,
                column=token.column,
                actual=str(actual),
                expected=str(expected)
            )
            test_results.append(test_result)

        return Result(
            output=output,
            tests=test_results
        )
    except Error as e:
        return Result(
            error=True,
            error_message=e.message
        )
