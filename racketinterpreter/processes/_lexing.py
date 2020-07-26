import typing as tp
from racketinterpreter import errors as err
from racketinterpreter.classes import tokens as t
from racketinterpreter.processes._syntax import ParenthesesAnalyzer


# I have come to the realization that an apostrophe should be treated as a quote in the lexer, and it really should be
# up to the parser to create a symbol from that or whatever should be created following a quote. This, however, would
# constitute a ton of changes so I'll leave it for later
class Lexer:

    NON_ID_CHARS = ['"', "'", '`', '(', ')', '[', ']', '{', '}', '|', ';', '#']

    def __init__(self, text: str) -> None:
        self.text = text
        self._pos = 0
        self._current_char = self.text[self._pos]

        self._line_no = 1
        self._column = 1

        self.tokens = []
        self._current_token_idx = -1

        self.paren_analyzer = ParenthesesAnalyzer()

    def process(self) -> None:
        self._process_all_tokens()

    def get_next_token(self) -> tp.Optional[t.Token]:
        try:
            self._current_token_idx += 1
            token = self.tokens[self._current_token_idx]
            return token
        except IndexError as e:
            return None

    def peek_next_token(self, pos_ahead: int = 1) -> t.Token:
        try:
            token = self.tokens[self._current_token_idx + pos_ahead]
            return token
        except IndexError as e:
            return self.tokens[-1]

    def _process_all_tokens(self) -> None:
        """ Responsible for breaking apart text into tokens."""

        paren_analyzer = self.paren_analyzer

        while True:
            token = self._process_next_token()

            if token is None:
                token = t.Token(t.TokenType.EOF, None, self._line_no, self._column)
                self.tokens.append(token)

                paren_analyzer.reached_eof(token)
                break

            self.tokens.append(token)

            if token.type in [t.TokenType.LPAREN, t.TokenType.RPAREN]:
                paren_analyzer.received_paren(token)

    def _process_next_token(self, apostrophe_as_quote: bool = False) -> tp.Optional[t.Token]:
        token = None

        while self._current_char:
            try:
                self._skip_whitespace_or_comments()
            except err.ReachedEOF as e:
                break

            if (self._current_char.isdigit() or self._current_char == '.'
                    or (self._current_char == '-' and (self._peek().isdigit() or self._peek() == '.'))):
                token = self._number()
                break

            if self._current_char not in self.NON_ID_CHARS:
                token = self._identifier()
                break

            if self._current_char == '#':
                token = self._boolean()
                break

            if self._current_char == '"':
                token = self._string()
                break

            if self._current_char == "'":
                if apostrophe_as_quote:
                    raise err.LexerError(
                        error_code=err.ErrorCode.FEATURE_NOT_IMPLEMENTED,
                        token=t.Token(
                            type=t.TokenType.INVALID,
                            value="'",
                            line_no=self._line_no,
                            column=self._column
                        )
                    )
                else:
                    token = self._symbol()

                break

            if self._current_char in ['(', '{', '[']:
                token_type = t.TokenType.LPAREN
                value = self._current_char
                token = t.Token(
                    type=token_type,
                    value=value,
                    line_no=self._line_no,
                    column=self._column
                )
                self._advance()
                break

            if self._current_char in [')', '}', ']']:
                token_type = t.TokenType.RPAREN
                value = self._current_char
                token = t.Token(
                    type=token_type,
                    value=value,
                    line_no=self._line_no,
                    column=self._column
                )
                self._advance()
                break

            if self._current_char == '|':
                raise err.LexerError(
                    error_code=err.ErrorCode.FEATURE_NOT_IMPLEMENTED,
                    token=t.Token(
                        type=t.TokenType.INVALID,
                        value="''",
                        line_no=self._line_no,
                        column=self._column
                    )
                )

            raise err.IllegalStateError

        return token

    def _peek(self) -> tp.Optional[str]:
        pos = self._pos + 1
        if pos > len(self.text) - 1:
            return None
        else:
            return self.text[pos]

    def _advance(self) -> None:
        """Advance the 'pos' pointer and set the 'current_char' field."""
        if self._current_char == '\n':
            self._line_no += 1
            self._column = 0

        self._pos += 1
        if self._pos > len(self.text) - 1:
            self._current_char = None
        else:
            self._current_char = self.text[self._pos]
            self._column += 1

    def _boolean(self) -> t.Token:
        line_no = self._line_no
        column = self._column

        boolean = self._current_char
        self._advance()
        while self._current_char is not None and not self._current_char.isspace():
            current_char = self._current_char
            if current_char in ['"', "'", '`', '#']:
                boolean += self._current_char
                break
            elif current_char in ['(', ')', '{', '}', '[', ']']:
                break

            boolean += self._current_char
            self._advance()

            lowered = boolean.lower()
            if lowered not in '#true' and lowered not in '#false':
                break

        if self._current_char is None or boolean not in ['#T', '#t', '#true', '#F', '#f', '#false']:
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

    def _identifier(self, initial: str = '') -> t.Token:
        """Handles identifiers (including builtin functions)."""
        line_no = self._line_no
        column = self._column

        result = initial
        while self._current_char is not None and self._current_char not in self.NON_ID_CHARS \
                and not self._current_char.isspace():
            result += self._current_char
            self._advance()

        return t.Token(t.TokenType.ID, result, line_no, column)

    def _number(self) -> t.Token:
        """Return a number token from a number consumed from the input (or an ID if not a valid number)."""
        line_no = self._line_no
        column = self._column

        if self._current_char == '-':
            number = '-'
            self._advance()
        else:
            number = ''

        is_rational = False
        numerator = ''
        denominator = ''

        while (self._current_char is not None and not self._current_char.isspace()
               and self._current_char not in self.NON_ID_CHARS):
            if self._current_char == '/':
                is_rational = True
                numerator = number
                number += self._current_char
                self._advance()
                continue

            if is_rational:
                denominator += self._current_char

            number += self._current_char
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
        line_no = self._line_no
        column = self._column

        self._advance()

        string = ''
        while self._current_char is not None and self._current_char != '"':
            string += self._current_char
            self._advance()

        if self._current_char is None:
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
        line_no = self._line_no
        column = self._column

        self._advance()

        # skip whitespace / comments before the body of the symbol
        try:
            self._skip_whitespace_or_comments()
        except err.ReachedEOF as e:
            raise err.LexerError(
                error_code=err.ErrorCode.RS_SYMBOL_FOUND_EOF,
                token=t.Token(
                    type=t.TokenType.INVALID,
                    value="'",
                    line_no=line_no,
                    column=column
                )
            )

        current_char = self._current_char
        if (current_char.isdigit() or current_char == '.'
                or (self._current_char == '-' and (self._peek().isdigit() or self._peek() == '.'))):
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
        elif current_char in ['(', '{', '[']:
            list_abrv = t.Token(
                type=t.TokenType.LIST_ABRV,
                value="'",
                line_no=line_no,
                column=column
            )

            paren_analyzer = self.paren_analyzer
            paren_stack = paren_analyzer.paren_stack
            init_paren_stack_len = len(paren_stack)

            last_left_paren = left_paren = self._process_next_token(apostrophe_as_quote=True)
            list_abrv.children.append(left_paren)
            self.paren_analyzer.received_paren(left_paren)

            while len(paren_stack) > init_paren_stack_len:
                token = self._process_next_token(apostrophe_as_quote=True)

                if token is None:
                    self.paren_analyzer.reached_eof(last_left_paren)

                list_abrv.children.append(token)

                if token.type in [t.TokenType.LPAREN, t.TokenType.RPAREN]:
                    paren_analyzer.received_paren(token)

                if token.type is t.TokenType.LPAREN:
                    last_left_paren = token

            return list_abrv
        elif current_char in [')', '}', ']']:
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
        elif current_char == '|':
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

    def _skip_whitespace_or_comments(self):
        while self._current_char:
            if self._current_char.isspace():
                self._skip_whitespace()
                continue

            if self._current_char == ';':
                self._skip_line_comment()
                continue

            if self._current_char == '#' and self._peek() == ';':
                self._skip_block_comment()
                continue

            if self._current_char == '#' and self._peek() == '|':
                self._skip_multi_line_comment()
                continue

            break

        if self._current_char is None:
            raise err.ReachedEOF

    def _skip_whitespace(self) -> None:
        """Consume whitespace until next non-whitespace character."""
        while self._current_char is not None and self._current_char.isspace():
            self._advance()

    def _skip_line_comment(self) -> None:
        """Consume text until the next newline character."""
        while self._current_char is not None and self._current_char != '\n':
            self._advance()
        self._advance()

    def _skip_block_comment(self) -> None:
        self._advance()
        self._advance()

        if self._current_char.isspace():
            self._skip_whitespace()

        if self._current_char != '(':
            self._process_all_tokens()
        else:
            paren_analyzer = self.paren_analyzer
            paren_stack = paren_analyzer.paren_stack
            init_paren_stack_len = len(paren_stack)

            token = self._process_next_token()
            self.paren_analyzer.received_paren(token)

            try:
                while len(paren_stack) > init_paren_stack_len:
                    token = self._process_next_token()

                    if token.type in [t.TokenType.LPAREN, t.TokenType.RPAREN]:
                        self.paren_analyzer.received_paren(token)
                    elif token.type is t.TokenType.EOF:
                        self.paren_analyzer.reached_eof(token)
                        raise err.ReachedEOF

            except err.ReachedEOF as e:
                pass

    def _skip_multi_line_comment(self) -> None:
        self._advance()
        self._advance()

        line_no = self._line_no
        column = self._column

        while True:
            if self._current_char == '|':
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

            elif self._current_char is None:
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