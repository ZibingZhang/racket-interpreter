from enum import Enum
from string import Template
from racketinterpreter.classes import data as d
from racketinterpreter.classes import tokens as t


class ErrorCode(Enum):

    FEATURE_NOT_IMPLEMENTED = Template('what you are trying to do is valid, it is just not supported yet')

    BUILTIN_OR_IMPORTED_NAME = Template('$name: this name was defined in the language or a required library and cannot be re-defined')
    DIVISION_BY_ZERO = Template('/: division by zero')
    INCORRECT_ARGUMENT_COUNT = Template('$name: $expects, but $found')
    INCORRECT_ARGUMENT_TYPE = Template('$name: $expects, $given')
    PREVIOUSLY_DEFINED_NAME = Template('$name: this name was defined previously and cannot be re-defined')
    USED_BEFORE_DEFINITION = Template('$name is used here before its definition')
    USING_STRUCTURE_TYPE = Template('$name: structure type; do you mean make-$name')

    C_ALL_QUESTION_RESULTS_FALSE = Template('cond: all question results were false')
    C_ELSE_NOT_LAST_CLAUSE = Template("cond: found an else clause that isn't the last clause in its cond expression")
    C_EXPECTED_A_CLAUSE = Template("cond: expected a clause after cond, but nothing's there")
    C_EXPECTED_OPEN_PARENTHESIS = Template('cond: expected an open parenthesis before cond, but found none')
    C_EXPECTED_QUESTION_ANSWER_CLAUSE = Template('cond: expected a clause with a question and an answer, but $found')
    C_QUESTION_RESULT_NOT_BOOLEAN = Template('cond: question result is not true or false: $result')

    CE_INCORRECT_ARGUMENT_COUNT = Template('check-expect: $expects, but $found')

    D_DUPLICATE_VARIABLE = Template('define: found a variable that is used more than once: $name')
    D_EXPECTED_A_NAME = Template("define: expected a variable name, or a function name and its variables (in parentheses), but $found")
    D_EXPECTED_OPEN_PARENTHESIS = Template('define: expected an open parenthesis before define, but found none')
    D_NOT_TOP_LEVEL = Template('define: found a definition that is not at the top level')
    D_P_EXPECTED_A_VARIABLE = Template('define: expected a variable, but $found')
    D_P_EXPECTED_FUNCTION_NAME = Template('define: expected the name of the function, but $found')
    D_P_EXPECTED_ONE_EXPRESSION = Template('define: expected only one expression for the function body, but $found')
    D_P_MISSING_AN_EXPRESSION = Template("define: expected an expression for the function body, but nothing's there")
    D_V_EXPECTED_ONE_EXPRESSION = Template("define: expected only one expression after the variable name $name, but $found")
    D_V_MISSING_AN_EXPRESSION = Template("define: expected an expression after the variable name $name, but nothing's there")

    # define-struct: found a field name that is used more than once: a
    DS_EXPECTED_A_FIELD = Template('define-struct: expected a field name, but $found')
    DS_EXPECTED_FIELD_NAMES = Template('define-struct: expected at least one field name (in parentheses) after the structure name, but $found')
    DS_EXPECTED_OPEN_PARENTHESIS = Template('define-struct: expected an open parenthesis before define-struct, but found none')
    DS_EXPECTED_STRUCTURE_NAME = Template('define-struct: expected the structure name after define-struct, but $found')
    DS_NOT_TOP_LEVEL = Template('define-struct: found a definition that is not at the top level')
    DS_POST_FIELD_NAMES = Template('define-struct: expected nothing after the field names, but $found')

    E_NOT_ALLOWED = Template('else: not allowed here, because this is not a question in a clause')

    FC_EXPECTED_A_FUNCTION = Template('function-call: expected a function after the open parenthesis, but $found')

    RS_BAD_SYNTAX = Template('read-syntax: bad syntax `$text`')
    RS_EOF_IN_BLOCK_COMMENT = Template('read-syntax: end of file in `#|` comment')
    RS_EXPECTED_DOUBLE_QUOTE = Template('read-syntax: expected a closing `"`')
    RS_EXPECTED_RIGHT_PARENTHESIS = Template('read-syntax: expected a `$right_paren` to close `$left_paren`')
    RS_INCORRECT_RIGHT_PARENTHESIS = Template('read-syntax: expected `$correct_right_paren` to close preceding `$left_paren`, found instead `$incorrect_right_paren`')
    RS_SYMBOL_FOUND_EOF = Template('read-syntax: expected an element for quoting "\'", found end-of-file')
    RS_UNEXPECTED = Template('read-syntax: unexpected `$value`')
    RS_UNEXPECTED_EOF = Template('read-syntax: unexpected EOF')  # should hopefully never be raised
    RS_UNEXPECTED_RIGHT_PARENTHESIS = Template('read-syntax: unexpected `)`')
    RS_UNEXPECTED_TOKEN = Template('read-syntax: unexpected token `$token_value`')  # should hopefully never be raised


class Error(Exception):

    def __init__(self, error_code, token, **kwargs) -> None:
        self.error_code = error_code
        self.token = token
        self.line_no = token.line_no
        self.column = token.column

        self.message = f'[{self.line_no}:{self.column}] '

        template = error_code.value

        if error_code is ErrorCode.FEATURE_NOT_IMPLEMENTED:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.BUILTIN_OR_IMPORTED_NAME:
            name = token.value

            error_message = template.safe_substitute(name=name)

        elif error_code is ErrorCode.DIVISION_BY_ZERO:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.INCORRECT_ARGUMENT_COUNT:
            proc_name = kwargs.get('proc_name')
            lower = kwargs.get('lower')
            upper = kwargs.get('upper')
            received = kwargs.get('received')

            if received == 0:
                received = 'none'

            expects = 'expects'
            if upper is None:
                expects += f' at least {lower} argument{"s" if lower > 1 else ""}'
            else:
                expects += f' {"only " if lower == 1 else ""}{lower} argument{"s" if lower != 1 else ""}'

            found = f'found {received}'

            error_message = template.safe_substitute(name=proc_name, expects=expects, found=found)

        elif error_code is ErrorCode.INCORRECT_ARGUMENT_TYPE:
            data_type_to_string = {
                d.Boolean: 'boolean',
                d.Number: 'number',
                # d.Procedure, TODO: procedures will be much more complicated...
                d.String: 'string',
                d.Symbol: 'symbol',
                d.RealNumber: 'real',
                # d.InexactNumber, no functions should expect this type
                # d.ExactNumber, no functions should expect this type
                d.Rational: 'rational',  # no functions should expect this type... but apparently gcd should?
                d.Integer: 'integer'
            }

            name = kwargs.get('name')
            expected = kwargs.get('expected')
            given = kwargs.get('given')
            multiple_args = kwargs.get('multiple_args')

            expects = f'expects a {data_type_to_string[expected]}'
            if multiple_args:
                def to_ord(n):
                    return str(n) + {
                        1: 'st',
                        2: 'nd',
                        3: 'rd'
                    }.get(n if n < 20 else n % 10, 'th')

                idx = kwargs.get('idx') + 1

                expects += f' as {to_ord(idx)} argument'

            given = f'given {given}'

            error_message = template.safe_substitute(name=name, expects=expects, given=given)

        elif error_code is ErrorCode.PREVIOUSLY_DEFINED_NAME:
            name = token.value

            error_message = template.safe_substitute(name=name)

        elif error_code is ErrorCode.USED_BEFORE_DEFINITION:
            name = kwargs.get('name')
            error_message = template.safe_substitute(name=name)

        elif error_code is ErrorCode.USING_STRUCTURE_TYPE:
            name = kwargs.get('name')
            error_message = template.safe_substitute(name=name)

        elif error_code is ErrorCode.C_ALL_QUESTION_RESULTS_FALSE:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.C_ELSE_NOT_LAST_CLAUSE:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.C_EXPECTED_A_CLAUSE:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.C_EXPECTED_OPEN_PARENTHESIS:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.C_EXPECTED_QUESTION_ANSWER_CLAUSE:
            part_count = kwargs.get('part_count')
            expr_token = kwargs.get('expr_token')

            if part_count is not None:
                if part_count == 0:
                    found = 'found an empty part'
                elif part_count == 1:
                    found = 'found a clause with only one part'
                else:
                    found = f'found a clause with {part_count} parts'

            else:
                if expr_token is None or expr_token.type is t.TokenType.RPAREN:
                    found = "nothing's there"
                elif expr_token.type is t.TokenType.BOOLEAN:
                    found = 'found a boolean'
                elif expr_token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                    found = 'found a number'
                elif expr_token.type is t.TokenType.STRING:
                    found = 'found a string'
                elif expr_token.type is t.TokenType.ID:
                    found = 'found something else'
                else:
                    raise IllegalStateError

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.C_QUESTION_RESULT_NOT_BOOLEAN:
            result = kwargs.get('result')

            error_message = template.safe_substitute(result=result)

        elif error_code is ErrorCode.CE_INCORRECT_ARGUMENT_COUNT:
            received = kwargs.get('received')

            if received == 0:
                received = 'none'

            expects = f'expects {"only" if received > 2 else ""} 2 arguments'
            found = f'but found {"only" if received == 1 else ""} 1'

            error_message = template.safe_substitute(expects=expects, found=found)

        elif error_code is ErrorCode.D_DUPLICATE_VARIABLE:
            name = kwargs.get('name')

            error_message = template.safe_substitute(name=name)

        elif error_code is ErrorCode.D_EXPECTED_A_NAME:
            proc_token = kwargs.get('next_token')

            if proc_token is None or proc_token.type is t.TokenType.RPAREN:
                found = "nothing's there"
            elif proc_token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                found = 'found a number'
            elif proc_token.type is t.TokenType.BOOLEAN:
                found = 'found a boolean'
            elif proc_token.type is t.TokenType.STRING:
                found = 'found a string'
            elif proc_token.value in t.KEYWORDS:
                found = 'found a keyword'
            else:
                raise IllegalStateError

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.D_EXPECTED_OPEN_PARENTHESIS:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.D_NOT_TOP_LEVEL:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.D_P_EXPECTED_A_VARIABLE:
            if token.type is t.TokenType.BOOLEAN:
                found = 'found a boolean'
            elif token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                found = 'found a number'
            elif token.type is t.TokenType.STRING:
                found = 'found a string'
            elif token.type in [t.TokenType.LPAREN, t.TokenType.SYMBOL]:
                found = 'found a part'
            elif token.value in t.KEYWORDS:
                found = 'found a keyword'
            else:
                raise IllegalStateError

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.D_P_EXPECTED_FUNCTION_NAME:
            name_token = kwargs.get('name_token')

            if name_token is None:
                found = "nothing's there"
            elif name_token.type is t.TokenType.BOOLEAN:
                found = 'found a boolean'
            elif name_token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                found = 'found a number'
            elif name_token.type is t.TokenType.STRING:
                found = 'found a string'
            elif name_token.type in [t.TokenType.LPAREN, t.TokenType.SYMBOL]:
                found = 'found a part'
            elif name_token.value in t.KEYWORDS:
                found = 'found a keyword'
            else:
                raise IllegalStateError

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.D_P_EXPECTED_ONE_EXPRESSION:
            part_count = kwargs.get('part_count')
            plural = part_count > 1
            found = f'found {part_count} extra part{"s" if plural else ""}'

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.D_P_MISSING_AN_EXPRESSION:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.D_V_EXPECTED_ONE_EXPRESSION:
            name = kwargs.get('name')
            extra_count = kwargs.get('extra_count')

            plural = extra_count > 1
            found = f'found {extra_count} extra part{"s" if plural else ""}'

            error_message = template.safe_substitute(name=name, found=found)

        elif error_code is ErrorCode.D_V_MISSING_AN_EXPRESSION:
            name = kwargs.get('name')

            error_message = template.safe_substitute(name=name)

        elif error_code is ErrorCode.DS_EXPECTED_A_FIELD:
            if token.type is t.TokenType.BOOLEAN:
                found = 'found a boolean'
            elif token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                found = 'found a number'
            elif token.type is t.TokenType.STRING:
                found = 'found a string'
            elif token.type in [t.TokenType.LPAREN, t.TokenType.SYMBOL]:
                found = 'found a part'
            elif token.value in t.KEYWORDS:
                found = 'found a keyword'
            else:
                raise IllegalStateError

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.DS_EXPECTED_FIELD_NAMES:
            found_token = kwargs.get('found_token')

            if found_token is None:
                found = "nothing's there"
            elif found_token.type is t.TokenType.BOOLEAN:
                found = 'found a boolean'
            elif found_token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                found = 'found a number'
            elif found_token.type is t.TokenType.STRING:
                found = 'found a string'
            elif found_token.value in t.KEYWORDS:
                found = 'found a keyword'
            else:
                raise IllegalStateError

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.DS_EXPECTED_OPEN_PARENTHESIS:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.DS_EXPECTED_STRUCTURE_NAME:
            name_token = kwargs.get('name_token')
            if name_token is None:
                found = "nothing's there"
            elif name_token.type is t.TokenType.BOOLEAN:
                found = 'found a boolean'
            elif name_token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                found = 'found a number'
            elif name_token.type is t.TokenType.STRING:
                found = 'found a string'
            elif name_token.type in [t.TokenType.LPAREN, t.TokenType.SYMBOL]:
                found = 'found a part'
            elif name_token.value in t.KEYWORDS:
                found = 'found a keyword'
            else:
                raise IllegalStateError

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.DS_NOT_TOP_LEVEL:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.DS_POST_FIELD_NAMES:
            part_count = kwargs.get('part_count')

            found = f'found {part_count} extra part{"s" if part_count > 1 else ""}'

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.E_NOT_ALLOWED:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.FC_EXPECTED_A_FUNCTION:
            proc_token = kwargs.get('proc_token')
            if proc_token.type is t.TokenType.ID:
                found_data = kwargs.get('found_data')
                found_data_type = type(found_data)
                if issubclass(found_data_type, d.Boolean):
                    found_type = 'string'
                elif issubclass(found_data_type, d.Number):
                    found_type = 'number'
                elif issubclass(found_data_type, d.String):
                    found_type = 'boolean'
                elif issubclass(type(found_data_type), d.StructDataType):
                    struct_name = found_data_type.__name__
                    fields = found_data.fields
                    found_type = f'(make-{struct_name} {" ".join(map(str, fields))})'
                else:
                    raise IllegalStateError
            else:
                if proc_token is None:
                    found_type = None
                elif proc_token.type is t.TokenType.BOOLEAN:
                    found_type = 'boolean'
                elif proc_token.type in [t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.RATIONAL]:
                    found_type = 'number'
                elif proc_token.type is t.TokenType.STRING:
                    found_type = 'string'
                elif proc_token.type is t.TokenType.LPAREN:
                    found_type = 'part'
                else:
                    raise IllegalStateError

            found = "nothing's there" if found_type is None else f'found a {found_type}'

            error_message = template.safe_substitute(found=found)

        elif error_code is ErrorCode.RS_BAD_SYNTAX:
            text = kwargs.get('text')
            error_message = template.safe_substitute(text=text)

        elif error_code is ErrorCode.RS_EOF_IN_BLOCK_COMMENT:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.RS_EXPECTED_DOUBLE_QUOTE:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.RS_EXPECTED_RIGHT_PARENTHESIS:
            left_paren = kwargs.get('left_paren')
            right_paren = kwargs.get('right_paren')
            error_message = template.safe_substitute(left_paren=left_paren, right_paren=right_paren)

        elif error_code is ErrorCode.RS_INCORRECT_RIGHT_PARENTHESIS:
            left_paren = kwargs.get('left_paren')
            correct_right_paren = kwargs.get('correct_right_paren')
            incorrect_right_paren = kwargs.get('incorrect_right_paren')
            error_message = template.safe_substitute(
                left_paren=left_paren,
                correct_right_paren=correct_right_paren,
                incorrect_right_paren=incorrect_right_paren
            )

        elif error_code is ErrorCode.RS_SYMBOL_FOUND_EOF:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.RS_UNEXPECTED_RIGHT_PARENTHESIS:
            error_message = template.safe_substitute()

        elif error_code is ErrorCode.RS_UNEXPECTED_TOKEN:
            token_value = token.value
            error_message = template.safe_substitute(token_value=token_value)

        elif error_code is ErrorCode.RS_UNEXPECTED:
            value = kwargs.get('value')

            error_message = template.safe_substitute(value=value)

        elif error_code is ErrorCode.RS_UNEXPECTED_EOF:
            error_message = template.safe_substitute()

        else:
            raise IllegalStateError

        self.message += error_message


class PreLexerError(Error):

    pass


class LexerError(Error):

    pass


class ParserError(Error):

    pass


class SemanticError(Error):

    pass


class InterpreterError(Error):

    pass


class BuiltinProcedureError(Error):

    pass


class EvaluateBuiltinProcedureError(TypeError):

    def __init__(self, expected: d.DataType, given: d.Data, idx: int = None):
        self.expected = expected
        self.given = given
        self.idx = idx


class IllegalStateError(RuntimeError):

    pass


class TailEndRecursion(RuntimeError):

    pass
