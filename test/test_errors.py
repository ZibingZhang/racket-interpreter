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
        else:
            raise Exception

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

        text = \
            '''
                (define add1 1)
            '''
        self.expect_error(text, ErrorCode.BUILTIN_OR_IMPORTED_NAME)

    def test_div_by_zero(self) -> None:
        text = \
            '''
                (/ 0)
            '''
        self.expect_error(text, ErrorCode.DIVISION_BY_ZERO)

        text = \
            '''
                (/ 5 (add1 (sub1 0)))
            '''
        self.expect_error(text, ErrorCode.DIVISION_BY_ZERO)

    def test_incorrect_number_of_arguments(self) -> None:
        text = \
            '''
                (-)
            '''
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

        text = \
            '''
                (modulo 1)
            '''
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

        text = \
            '''
                (define (x a b) 1)
                (x 1 2 3)
            '''
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

    def test_undefined_name(self) -> None:
        text = \
            '''
                x
            '''
        self.expect_error(text, ErrorCode.USED_BEFORE_DEFINITION)

        text = \
            '''
                (x 1)
            '''
        self.expect_error(text, ErrorCode.USED_BEFORE_DEFINITION)

        text = \
            '''
                (define (x a b) y)
            '''
        self.expect_error(text, ErrorCode.USED_BEFORE_DEFINITION)

    def test_using_structure_type(self) -> None:
        text = \
            '''
                (define-struct s [])
                s
            '''
        self.expect_error(text, ErrorCode.USING_STRUCTURE_TYPE)

        text = \
            '''
                (define-struct s [])
                (+ s 1)
            '''
        self.expect_error(text, ErrorCode.USING_STRUCTURE_TYPE)

        text = \
            '''
                (define-struct s [])
                (define (x a b) s)
                (x 1 2)
            '''
        self.expect_error(text, ErrorCode.USING_STRUCTURE_TYPE)

    def test_cond_expressions(self) -> None:
        text = \
            '''
                (cond [else 1] [else 2])
            '''
        self.expect_error(text, ErrorCode.C_ELSE_NOT_LAST_CLAUSE)

        text = \
            '''
                (cond [1 1])
            '''
        self.expect_error(text, ErrorCode.C_QUESTION_RESULT_NOT_BOOLEAN)

        text = \
            '''
                (cond)
            '''
        self.expect_error(text, ErrorCode.C_EXPECTED_A_CLAUSE)

        text = \
            '''
                (cond 1)
            '''
        self.expect_error(text, ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE)

        text = \
            '''
                (cond [])
            '''
        self.expect_error(text, ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE)

        text = \
            '''
                (cond [#f 1])
            '''
        self.expect_error(text, ErrorCode.C_ALL_QUESTION_RESULTS_FALSE)

    def test_defining_variables(self) -> None:
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

    def test_defining_procedures(self) -> None:
        text = \
            '''
                (define () 1)
            '''
        self.expect_error(text, ErrorCode.D_P_EXPECTED_FUNCTION_NAME)

        text = \
            '''
                (define (x))
            '''
        self.expect_error(text, ErrorCode.D_P_MISSING_AN_EXPRESSION)

        text = \
            '''
                (define (x) 1 1)
            '''
        self.expect_error(text, ErrorCode.D_P_EXPECTED_ONE_EXPRESSION)

        text = \
            '''
                (define (x 1) 1)
            '''
        self.expect_error(text, ErrorCode.D_P_EXPECTED_A_VARIABLE)

    def test_defining_structures(self) -> None:
        text = \
            '''
                (define-struct x (1))
            '''
        self.expect_error(text, ErrorCode.DS_EXPECTED_A_FIELD)

        text = \
            '''
                (define-struct x)
            '''
        self.expect_error(text, ErrorCode.DS_EXPECTED_FIELD_NAMES)

        text = \
            '''
                (define-struct x () 1)
            '''
        self.expect_error(text, ErrorCode.DS_POST_FIELD_NAMES)

        text = \
            '''
                (define-struct 1 ())
            '''
        self.expect_error(text, ErrorCode.DS_EXPECTED_STRUCTURE_NAME)

    def test_function_call(self) -> None:
        text = \
            '''
                (1)
            '''
        self.expect_error(text, ErrorCode.FC_EXPECTED_A_FUNCTION)

    def test_invalid_booleans(self) -> None:
        text = \
            '''
                #tru
            '''
        self.expect_error(text, ErrorCode.RS_BAD_SYNTAX)


if __name__ == '__main__':
    unittest.main()
