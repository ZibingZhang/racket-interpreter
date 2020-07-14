from __future__ import annotations
import unittest
from racketinterpreter.errors import Error, ErrorCode
from racketinterpreter.util import Util


class TestErrors(unittest.TestCase):

    def expect_error(self, text: str, error_code: ErrorCode) -> None:
        try:
            Util.text_to_interpreter_result(text)
        except Error as e:
            self.assertEqual(error_code, e.error_code)
        else:
            raise Exception('No error raised.')

    def test_general_builtin_or_imported_name(self):
        text = '(define + 1)'
        self.expect_error(text, ErrorCode.BUILTIN_OR_IMPORTED_NAME)

        text = '(define (add1 a b) b)'
        self.expect_error(text, ErrorCode.BUILTIN_OR_IMPORTED_NAME)

        text = '(define-struct boolean [])'
        self.expect_error(text, ErrorCode.BUILTIN_OR_IMPORTED_NAME)

    def test_general_division_by_zero(self):
        text = '(/ 0)'
        self.expect_error(text, ErrorCode.DIVISION_BY_ZERO)

        text = '(/ (add1 (sub1 (- 4/2 (/ 9 4.5)))))'
        self.expect_error(text, ErrorCode.DIVISION_BY_ZERO)

    def test_general_incorrect_argument_count(self):
        text = '(/ )'
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

        text = '(/ )'
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

        text = '(add1 1 2)'
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

        text = '(define (x a b) 5) (x 1)'
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

        text = '(define (x a b) 5) (x 1 2 3)'
        self.expect_error(text, ErrorCode.INCORRECT_ARGUMENT_COUNT)

        text = '(define x 1) (define x 2)'
        self.expect_error(text, ErrorCode.PREVIOUSLY_DEFINED_NAME)

    def test_general_previously_defined_name(self):
        text = '(define x 1) (define (x) 2)'
        self.expect_error(text, ErrorCode.PREVIOUSLY_DEFINED_NAME)

        text = '(define make-x 1) (define-struct x [])'
        self.expect_error(text, ErrorCode.PREVIOUSLY_DEFINED_NAME)

    def test_general_used_before_definition(self):
        text = 'x'
        self.expect_error(text, ErrorCode.USED_BEFORE_DEFINITION)

        text = '(x  1)'
        self.expect_error(text, ErrorCode.USED_BEFORE_DEFINITION)

    def test_general_using_structure_type(self):
        text = '(define-struct x []) (x 1)'
        self.expect_error(text, ErrorCode.USING_STRUCTURE_TYPE)

        text = '(define-struct x []) x'
        self.expect_error(text, ErrorCode.USING_STRUCTURE_TYPE)

        text = '(define-struct x []) (define (y) x)'
        self.expect_error(text, ErrorCode.USING_STRUCTURE_TYPE)

    def test_cond_all_question_results_false(self):
        text = '(cond [#f 1])'
        self.expect_error(text, ErrorCode.C_ALL_QUESTION_RESULTS_FALSE)

        text = '(cond [(= 1 2) 3] [#f 1])'
        self.expect_error(text, ErrorCode.C_ALL_QUESTION_RESULTS_FALSE)

    def test_cond_else_not_last_clause(self):
        text = '(cond [else 1] [#t 1])'
        self.expect_error(text, ErrorCode.C_ELSE_NOT_LAST_CLAUSE)

        text = '(cond [else 1] [else 1])'
        self.expect_error(text, ErrorCode.C_ELSE_NOT_LAST_CLAUSE)

    def test_cond_expected_a_clause(self):
        text = '(cond)'
        self.expect_error(text, ErrorCode.C_EXPECTED_A_CLAUSE)

    def test_cond_expected_open_parenthesis(self):
        text = '(define x cond)'
        self.expect_error(text, ErrorCode.C_EXPECTED_OPEN_PARENTHESIS)

    def test_cond_expected_question_answer_clause(self):
        text = '(cond 1)'
        self.expect_error(text, ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE)

        text = '(cond #t)'
        self.expect_error(text, ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE)

        text = '(cond "a")'
        self.expect_error(text, ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE)

        text = '(define-struct s []) (define x (make-s)) (cond x)'
        self.expect_error(text, ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE)

    def test_cond_question_result_not_boolean(self):
        text = '(cond [1 1])'
        self.expect_error(text, ErrorCode.C_QUESTION_RESULT_NOT_BOOLEAN)

        text = '(cond ["a" 1])'
        self.expect_error(text, ErrorCode.C_QUESTION_RESULT_NOT_BOOLEAN)

        text = '(define-struct s []) (define x (make-s)) (cond [x 1])'
        self.expect_error(text, ErrorCode.C_QUESTION_RESULT_NOT_BOOLEAN)

    def test_cons_list_expected_second_argument_list(self):
        text = '(cons 1 2)'
        self.expect_error(text, ErrorCode.CL_EXPECTED_SECOND_ARGUMENT_LIST)

        text = "(cons 1 'a)"
        self.expect_error(text, ErrorCode.CL_EXPECTED_SECOND_ARGUMENT_LIST)

        text = "(cons 1 (cons 2 (cons 3 4)))"
        self.expect_error(text, ErrorCode.CL_EXPECTED_SECOND_ARGUMENT_LIST)

    def test_define_duplicate_variable(self):
        text = '(define (x a a) a)'
        self.expect_error(text, ErrorCode.D_DUPLICATE_VARIABLE)

    def test_define_expected_a_name(self):
        text = '(define 1)'
        self.expect_error(text, ErrorCode.D_EXPECTED_A_NAME)

        text = '(define #t)'
        self.expect_error(text, ErrorCode.D_EXPECTED_A_NAME)

        text = '(define "a")'
        self.expect_error(text, ErrorCode.D_EXPECTED_A_NAME)

    def test_define_expected_open_parenthesis(self):
        text = '(define x define)'
        self.expect_error(text, ErrorCode.D_EXPECTED_OPEN_PARENTHESIS)

    def test_define_not_top_level(self):
        text = '(define x (define y 1))'
        self.expect_error(text, ErrorCode.D_NOT_TOP_LEVEL)

        text = '(cond [(define x 1) 1])'
        self.expect_error(text, ErrorCode.D_NOT_TOP_LEVEL)

        text = '(define-struct x [a]) (make-x (define y 1))'
        self.expect_error(text, ErrorCode.D_NOT_TOP_LEVEL)

    def test_define_procedure_expected_a_variable(self):
        text = '(define (x 1) 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_A_VARIABLE)

        text = '(define (x #t) 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_A_VARIABLE)

        text = '(define (x "a") 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_A_VARIABLE)

        text = '(define (x define) 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_A_VARIABLE)

    def test_define_procedure_expected_function_name(self):
        text = '(define (1) 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_FUNCTION_NAME)

        text = '(define (#t) 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_FUNCTION_NAME)

        text = '(define ("a") 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_FUNCTION_NAME)

    def test_define_procedure_expected_one_expression(self):
        text = '(define (x) 1 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_ONE_EXPRESSION)

        text = '(define (x) 1 1 1 1 1 1)'
        self.expect_error(text, ErrorCode.D_P_EXPECTED_ONE_EXPRESSION)

    def test_define_procedure_missing_an_expression(self):
        text = '(define (x))'
        self.expect_error(text, ErrorCode.D_P_MISSING_AN_EXPRESSION)

    def test_define_variable_expected_one_expression(self):
        text = '(define x 1 1)'
        self.expect_error(text, ErrorCode.D_V_EXPECTED_ONE_EXPRESSION)

        text = '(define x 1 1 1 1 1 1 1)'
        self.expect_error(text, ErrorCode.D_V_EXPECTED_ONE_EXPRESSION)

    def test_define_variable_missing_an_expression(self):
        text = '(define x)'
        self.expect_error(text, ErrorCode.D_V_MISSING_AN_EXPRESSION)

    def test_define_struct_expected_a_field(self):
        text = '(define-struct x [1])'
        self.expect_error(text, ErrorCode.DS_EXPECTED_A_FIELD)

        text = '(define-struct x [#t])'
        self.expect_error(text, ErrorCode.DS_EXPECTED_A_FIELD)

        text = '(define-struct x ["a"])'
        self.expect_error(text, ErrorCode.DS_EXPECTED_A_FIELD)

        text = '(define-struct x [define])'
        self.expect_error(text, ErrorCode.DS_EXPECTED_A_FIELD)

    def test_define_struct_expected_field_names(self):
        text = '(define-struct x)'
        self.expect_error(text, ErrorCode.DS_EXPECTED_FIELD_NAMES)

    def test_define_struct_expected_open_parenthesis(self):
        text = '(define x define-struct)'
        self.expect_error(text, ErrorCode.DS_EXPECTED_OPEN_PARENTHESIS)

    def test_define_struct_expected_structure_name(self):
        text = '(define-struct)'
        self.expect_error(text, ErrorCode.DS_EXPECTED_STRUCTURE_NAME)

    def test_define_struct_not_top_level(self):
        text = '(define x (define-struct y 1))'
        self.expect_error(text, ErrorCode.DS_NOT_TOP_LEVEL)

        text = '(cond [(define-struct x 1) 1])'
        self.expect_error(text, ErrorCode.DS_NOT_TOP_LEVEL)

        text = '(define-struct x [a]) (make-x (define-struct y 1))'
        self.expect_error(text, ErrorCode.DS_NOT_TOP_LEVEL)

    def test_define_struct_post_field_names(self):
        text = '(define-struct x [] 1)'
        self.expect_error(text, ErrorCode.DS_POST_FIELD_NAMES)

    def test_else_not_allowed(self):
        text = '(define x else)'
        self.expect_error(text, ErrorCode.E_NOT_ALLOWED)

    def test_function_call_expected_a_function(self):
        text = '(1)'
        self.expect_error(text, ErrorCode.FC_EXPECTED_A_FUNCTION)

        text = '(#t)'
        self.expect_error(text, ErrorCode.FC_EXPECTED_A_FUNCTION)

        text = '("a")'
        self.expect_error(text, ErrorCode.FC_EXPECTED_A_FUNCTION)

        text = '(define-struct s []) (define x (make-s)) (x)'
        self.expect_error(text, ErrorCode.FC_EXPECTED_A_FUNCTION)

    def test_read_syntax_bad_syntax(self):
        text = '#tru'
        self.expect_error(text, ErrorCode.RS_BAD_SYNTAX)

        text = '#falsey'
        self.expect_error(text, ErrorCode.RS_BAD_SYNTAX)

        text = '#ft['
        self.expect_error(text, ErrorCode.RS_BAD_SYNTAX)

    def test_read_syntax_eof_in_block_comment(self):
        text = '#|'
        self.expect_error(text, ErrorCode.RS_EOF_IN_BLOCK_COMMENT)

        text = '#| | # #|'
        self.expect_error(text, ErrorCode.RS_EOF_IN_BLOCK_COMMENT)

    def test_read_syntax_expected_double_quote(self):
        text = '"a'
        self.expect_error(text, ErrorCode.RS_EXPECTED_DOUBLE_QUOTE)

        text = '(define x "a)'
        self.expect_error(text, ErrorCode.RS_EXPECTED_DOUBLE_QUOTE)

    def test_read_syntax_expected_right_parenthesis(self):
        text = '('
        self.expect_error(text, ErrorCode.RS_EXPECTED_RIGHT_PARENTHESIS)

        text = '(define x 1'
        self.expect_error(text, ErrorCode.RS_EXPECTED_RIGHT_PARENTHESIS)

    def test_read_syntax_incorrect_right_parenthesis(self):
        text = '(]'
        self.expect_error(text, ErrorCode.RS_INCORRECT_RIGHT_PARENTHESIS)

        text = '(define x 1}'
        self.expect_error(text, ErrorCode.RS_INCORRECT_RIGHT_PARENTHESIS)

    # ideally should be unable to trigger this error
    # def test_read_syntax_unexpected_eof(self):
    #     pass

    def test_read_syntax_unexpected_right_parenthesis(self):
        text = ']'
        self.expect_error(text, ErrorCode.RS_UNEXPECTED_RIGHT_PARENTHESIS)

        text = '(define x 1))'
        self.expect_error(text, ErrorCode.RS_UNEXPECTED_RIGHT_PARENTHESIS)

    # ideally should be unable to trigger error
    # def test_read_syntax_unexpected_token(self):
    #     pass
