from typing import Optional
from racketinterpreter import errors as err
from racketinterpreter.classes import tokens as t
from racketinterpreter.processes.syntax import ParenthesesAnalyzer


class Lexer:
    NON_ID_CHARS = ['"', "'", '`', '(', ')', '[', ']', '{', '}', '|', ';', '#']

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

        self.line_no = 1
        self.column = 1

        self.tokens = []
        # TODO: maybe change indexing
        self.token_idx = -1

    def process(self) -> None:
        paren_analyzer = ParenthesesAnalyzer()

        while True:
            token = self._get_next_token()
            self.tokens.append(token)

            if token.type in [t.TokenType.LPAREN, t.TokenType.RPAREN]:
                paren_analyzer.received_paren(token)
            elif token.type is t.TokenType.EOF:
                paren_analyzer.reached_eof(token)
                break

    def get_next_token(self) -> Optional[t.Token]:
        try:
            self.token_idx += 1
            token = self.tokens[self.token_idx]
            return token
        except IndexError as e:
            return None

    def peek_next_token(self, pos_ahead: int = 1) -> t.Token:
        try:
            token = self.tokens[self.token_idx + pos_ahead]
            return token
        except IndexError as e:
            raise err.IllegalStateError

    def _get_next_token(self) -> t.Token:
        """ Responsible for breaking apart text into tokens."""
        while self.current_char:
            if self.current_char.isspace():
                self._skip_whitespace()
                continue

            if self.current_char == ';':
                self._skip_line_comment()
                continue

            if self.current_char == '#' and self._peek() == '|':
                self._skip_block_comment()
                continue

            if self.current_char.isdigit() or self.current_char == '.' \
                    or (self.current_char == '-' and (self._peek().isdigit() or self._peek() == '.')):
                return self._number()

            if self.current_char not in self.NON_ID_CHARS:
                return self._identifier()

            if self.current_char == '#':
                return self._boolean()

            if self.current_char == '"':
                return self._string()

            if self.current_char == "'":
                return self._symbol()

            if self.current_char in ['(', '{', '[']:
                token_type = t.TokenType.LPAREN
                value = self.current_char
                token = t.Token(
                    type=token_type,
                    value=value,
                    line_no=self.line_no,
                    column=self.column
                )
                self._advance()
                return token

            if self.current_char in [')', '}', ']']:
                token_type = t.TokenType.RPAREN
                value = self.current_char
                token = t.Token(
                    type=token_type,
                    value=value,
                    line_no=self.line_no,
                    column=self.column
                )
                self._advance()
                return token

            raise err.IllegalStateError

        return t.Token(t.TokenType.EOF, None, self.line_no, self.column)

    def _peek(self) -> Optional[str]:
        pos = self.pos + 1
        if pos > len(self.text) - 1:
            return None
        else:
            return self.text[pos]

    def _advance(self) -> None:
        """Advance the 'pos' pointer and set the 'current_char' field."""
        if self.current_char == '\n':
            self.line_no += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def _boolean(self) -> t.Token:
        line_no = self.line_no
        column = self.column

        boolean = self.current_char
        self._advance()
        while self.current_char is not None and not self.current_char.isspace():
            current_char = self.current_char
            if current_char in ['"', "'", '`', '#']:
                boolean += self.current_char
                break
            elif current_char in ['(', ')', '{', '}', '[', ']']:
                break

            boolean += self.current_char
            self._advance()

            lowered = boolean.lower()
            if lowered not in '#true' and lowered not in '#false':
                break

        if self.current_char is None or boolean not in ['#T', '#t', '#true', '#F', '#f', '#false']:
            raise err.LexerError(
                error_code=err.ErrorCode.RS_BAD_SYNTAX,
                token=t.Token(
                    type=t.TokenType.INVALID,
                    value=boolean,
                    line_no=line_no,
                    column=column
                ),
                text=boolean
            )

        if boolean in ['#T', '#t', '#true']:
            return t.Token(
                type=t.TokenType.BOOLEAN,
                value=True,
                line_no=line_no,
                column=column
            )
        elif boolean in ['#F', '#f', '#false']:
            return t.Token(
                type=t.TokenType.BOOLEAN,
                value=False,
                line_no=line_no,
                column=column
            )

    def _number(self) -> t.Token:
        """Return a number token from a number consumed from the input (or an ID if not a valid number)."""
        line_no = self.line_no
        column = self.column

        if self.current_char == '-':
            number = '-'
            self._advance()
        else:
            number = ''

        is_rational = False
        numerator = ''
        denominator = ''

        while self.current_char is not None and not self.current_char.isspace() \
                and self.current_char not in self.NON_ID_CHARS:
            if self.current_char == '/':
                is_rational = True
                numerator = number
                number += self.current_char
                self._advance()
                continue

            if is_rational:
                denominator += self.current_char

            number += self.current_char
            self._advance()

        if is_rational:
            try:
                numerator = int(numerator)
                denominator = int(denominator)
            except ValueError:
                return t.Token(
                    type=t.TokenType.ID,
                    value=number,
                    line_no=line_no,
                    column=column
                )
            else:
                return t.Token(
                    type=t.TokenType.RATIONAL,
                    value=(numerator, denominator),
                    line_no=line_no,
                    column=column
                )
        else:
            try:
                number = int(number)
            except ValueError:
                try:
                    number = float(number)
                except ValueError:
                    return t.Token(
                        type=t.TokenType.ID,
                        value=number,
                        line_no=line_no,
                        column=column
                    )
                else:
                    return t.Token(
                        type=t.TokenType.DECIMAL,
                        value=number,
                        line_no=line_no,
                        column=column
                    )
            else:
                return t.Token(
                    type=t.TokenType.INTEGER,
                    value=number,
                    line_no=line_no,
                    column=column
                )

    def _string(self) -> t.Token:
        """Handles strings."""
        line_no = self.line_no
        column = self.column

        self._advance()

        string = ''
        while self.current_char is not None and self.current_char != '"':
            string += self.current_char
            self._advance()

        if self.current_char is None:
            raise err.LexerError(
                error_code=err.ErrorCode.RS_EXPECTED_DOUBLE_QUOTE,
                token=t.Token(
                    type=t.TokenType.INVALID,
                    value=string,
                    line_no=line_no,
                    column=column
                )
            )

        self._advance()

        return t.Token(
            type=t.TokenType.STRING,
            value=string,
            line_no=line_no,
            column=column
        )

    def _symbol(self) -> t.Token:
        """Handles symbols."""
        line_no = self.line_no
        column = self.column

        self._advance()

        while True:
            if self.current_char is None:
                raise err.LexerError(
                    error_code=err.ErrorCode.RS_SYMBOL_FOUND_EOF,
                    token=t.Token(
                        type=t.TokenType.INVALID,
                        value="'",
                        line_no=line_no,
                        column=column
                    )
                )
            elif self.current_char.isspace():
                self._skip_whitespace()
            elif self.current_char == ';':
                self._skip_line_comment()
            elif self.current_char == '#' and self._peek() == '|':
                self._skip_block_comment()
            else:
                break

        current_char = self.current_char
        if current_char.isdigit() or current_char == '.' \
                or (self.current_char == '-' and (self._peek().isdigit() or self._peek() == '.')):
            return self._number()
        elif current_char not in self.NON_ID_CHARS:
            token = self._identifier()
            return t.Token(
                type=t.TokenType.SYMBOL,
                value=f"'{token.value}",
                line_no=line_no,
                column=column
            )
        elif current_char == '#':
            return self._boolean()
        elif current_char == '"':
            return self._string()
        elif current_char in [')', '}', ']', '(', '{', '[']:
            raise err.LexerError(
                error_code=err.ErrorCode.RS_UNEXPECTED,
                token=t.Token(
                    type=t.TokenType.INVALID,
                    value=f"'{current_char}",
                    line_no=line_no,
                    column=column
                ),
                value=current_char
            )
        elif current_char == "'":
            raise err.LexerError(
                error_code=err.ErrorCode.FEATURE_NOT_IMPLEMENTED,
                token=t.Token(
                    type=t.TokenType.INVALID,
                    value="''",
                    line_no=line_no,
                    column=column
                )
            )
        else:
            raise err.IllegalStateError

    def _identifier(self, initial: str = '') -> t.Token:
        """Handles identifiers (including builtin functions)."""
        line_no = self.line_no
        column = self.column

        result = initial
        while self.current_char is not None and self.current_char not in self.NON_ID_CHARS \
                and not self.current_char.isspace():
            result += self.current_char
            self._advance()

        return t.Token(t.TokenType.ID, result, line_no, column)

    def _skip_whitespace(self) -> None:
        """Consume whitespace until next non-whitespace character."""
        while self.current_char is not None and self.current_char.isspace():
            self._advance()

    def _skip_line_comment(self) -> None:
        """Consume text until the next newline character."""
        while self.current_char is not None and self.current_char != '\n':
            self._advance()
        self._advance()

    def _skip_block_comment(self) -> None:
        self._advance()
        self._advance()

        line_no = self.line_no
        column = self.column

        while True:
            if self.current_char == '|':
                next_char = self._peek()
                if next_char == '#':
                    self._advance()
                    self._advance()
                    break
                elif next_char is None:
                    raise err.LexerError(
                        error_code=err.ErrorCode.RS_EOF_IN_BLOCK_COMMENT,
                        token=t.Token(
                            type=t.TokenType.INVALID,
                            value=None,
                            line_no=line_no,
                            column=column
                        )
                    )

            elif self.current_char is None:
                raise err.LexerError(
                    error_code=err.ErrorCode.RS_EOF_IN_BLOCK_COMMENT,
                    token=t.Token(
                        type=t.TokenType.INVALID,
                        value=None,
                        line_no=line_no,
                        column=column
                    )
                )

            self._advance()
