from __future__ import annotations
import unittest
from src import constants
from src.errors import Error, ErrorCode
from src.util import Util


class TestInterpreter(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        constants.init(should_log_scope=False, should_log_stack=False)

    def expect_error(self, text: str, error_code: ErrorCode) -> None:
        try:
            Util.text_to_result(text)
        except Error as e:
            self.assertEqual(e.error_code, error_code)

    def test_duplicate_naming(self) -> None:
        text = \
            '''
                (define x 1)
                (define (x a) 1)
            '''
        self.expect_error(text, ErrorCode.PREVIOUSLY_DEFINED_NAME)

        text = \
            '''
                (define make-x 1)
                (define-struct x ())
            '''
        self.expect_error(text, ErrorCode.PREVIOUSLY_DEFINED_NAME)

    def test_defining_constants(self) -> None:
        text = \
            '''
                (define "not a name" 1)
            '''
        self.expect_error(text, ErrorCode.D_EXPECTED_A_NAME)

        text = \
            '''
                (define x)
            '''
        self.expect_error(text, ErrorCode.D_V_MISSING_AN_EXPRESSION)

        text = \
            '''
                (define x define)
            '''
        self.expect_error(text, ErrorCode.D_V_EXPECTED_OPEN_PARENTHESIS)

        text = \
            '''
                (define x else)
            '''
        self.expect_error(text, ErrorCode.E_NOT_ALLOWED)

        text = \
            '''
                (define x 1 1)
            '''
        self.expect_error(text, ErrorCode.D_V_EXPECTED_ONE_EXPRESSION)

    def test_parentheses(self) -> None:
        text = \
            '''
                (
            '''
        self.expect_error(text, ErrorCode.RS_EXPECTED_RIGHT_PARENTHESIS)

        text = \
            '''
                )
            '''
        self.expect_error(text, ErrorCode.RS_UNEXPECTED_RIGHT_PARENTHESIS)

        text = \
            '''
                {)
            '''
        self.expect_error(text, ErrorCode.RS_INCORRECT_RIGHT_PARENTHESIS)


if __name__ == '__main__':
    unittest.main()
