from typing import Optional
from src.errors import LexerError
import src.token as t
from src.token import Token, TokenType


class Lexer:

    RESERVED_KEYWORDS = t.RESERVED_KEYWORDS
    NON_ID_CHARS = ['"', "'", '`', '(', ')', '[', ']', '{', '}', '|', ';', '#']

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

        self.line_no = 1
        self.column = 1

    def error(self) -> None:
        lexeme = self.current_char
        line_no = self.line_no
        column = self.column
        msg = f"Invalid character '{lexeme}' position={line_no}:{column}."
        raise LexerError(message=msg)

    def advance(self) -> None:
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

    def peek(self) -> Optional[str]:
        pos = self.pos + 1
        if pos > len(self.text) - 1:
            return None
        else:
            return self.text[pos]

    def boolean(self) -> Token:
        boolean = self.current_char
        self.advance()
        while self.current_char is not None and self.current_char.isalpha():
            boolean += self.current_char
            self.advance()

        if boolean in ['#T', '#t', '#true']:
            return Token(TokenType.BOOLEAN, True, self.line_no, self.column)
        elif boolean in ['#F', '#f', '#false']:
            return Token(TokenType.BOOLEAN, False, self.line_no, self.column)
        else:
            self.error()

    def number(self) -> Token:
        # TODO: Add in more number types
        # TODO: Recognize more than just positive and negative ints
        """Return a number token from a number consumed from the input."""
        if self.current_char == '-':
            number = '-'
            self.advance()
        else:
            number = ''

        while self.current_char is not None and not self.current_char.isspace() \
                and self.current_char not in self.NON_ID_CHARS:
            if self.current_char not in self.NON_ID_CHARS and not self.current_char.isdigit():
                return self.identifier(number)

            number += self.current_char
            self.advance()

        return Token(TokenType.NUMBER, float(number), self.line_no, self.column)

    def string(self) -> Token:
        """Handles strings."""
        self.advance()

        string = ''
        while self.current_char is not None and self.current_char != '"':
            string += self.current_char
            self.advance()
        self.advance()

        return Token(TokenType.STRING, string, self.line_no, self.column)

    def identifier(self, initial: str = '') -> Token:
        """Handles identifiers (including builtin functions)."""
        result = initial
        while self.current_char is not None and self.current_char not in self.NON_ID_CHARS \
                and not self.current_char.isspace():
            result += self.current_char
            self.advance()

        token_type = self.RESERVED_KEYWORDS.get(result, TokenType.ID)
        token_value = result if token_type is TokenType.ID else None
        return Token(token_type, token_value, self.line_no, self.column)

    def skip_whitespace(self) -> None:
        """Consume whitespace until next non-whitespace character."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_line_comment(self) -> None:
        """Consume text until the next newline character."""
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.advance()

    def get_next_token(self) -> Token:
        """ Responsible for breaking apart text into tokens."""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == ';':
                self.skip_line_comment()
                continue

            if self.current_char.isdigit() or (self.current_char == '-' and self.peek().isdigit()):
                return self.number()

            if self.current_char not in self.NON_ID_CHARS:
                return self.identifier()

            if self.current_char == '#':
                return self.boolean()

            if self.current_char == '"':
                return self.string()

            try:
                # get enum member by value
                token_type = TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-char lexeme as its value
                token = Token(
                    type=token_type,
                    value=token_type.value,
                    line_no=self.line_no,
                    column=self.column
                )
                self.advance()
                return token

        return Token(TokenType.EOF, None, self.line_no, self.column)

    def peek_next_token(self, pos_ahead: int = 1) -> Token:
        current_pos = self.pos
        current_char = self.current_char
        current_line_no = self.line_no
        current_column = self.column

        next_token = self.get_next_token()
        for _ in range(pos_ahead - 1):
            next_token = self.get_next_token()
            if next_token.type is TokenType.EOF:
                return Token(TokenType.EOF, None, self.line_no, self.column)

        self.pos = current_pos
        self.current_char = current_char
        self.line_no = current_line_no
        self.column = current_column

        return next_token
