from src.token import Token, TokenType


class LexerError(Exception):

    pass


class Lexer:

    RESERVED_KEYWORDS = {
        'define': Token(TokenType.DEFINE, None)
    }

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self) -> None:
        raise LexerError('Invalid character.')

    def advance(self) -> None:
        """Advance the 'pos' pointer and set the 'current_char' field."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def number(self) -> Token:
        # TODO: Add in more number types
        # TODO: Recognize more than just positive and negative ints
        """Return a number token from a number consumed from the input."""
        if self.current_char == '-':
            number = '-'
            self.advance()
        else:
            number = ''

        while self.current_char is not None and self.current_char.isdigit():
            number += self.current_char
            self.advance()

        return Token(TokenType.NUMBER, float(number))

    def boolean(self) -> Token:
        boolean = self.current_char
        self.advance()
        while self.current_char is not None and self.current_char.isalpha():
            boolean += self.current_char
            self.advance()

        if boolean in ['#T', '#t', '#true']:
            return Token(TokenType.BOOLEAN, True)
        elif boolean in ['#F', '#f', '#false']:
            return Token(TokenType.BOOLEAN, False)
        else:
            self.error()

    def string(self) -> Token:
        self.advance()

        string = ''
        while self.current_char is not None and self.current_char != '"':
            string += self.current_char
            self.advance()
        self.advance()

        return Token(TokenType.STRING, string)

    def identifier(self) -> Token:
        """Handles identifiers and reserved keywords."""
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token = self.RESERVED_KEYWORDS.get(result, Token(TokenType.ID, result))
        return token

    def skip_whitespace(self) -> None:
        """Consume whitespace until next non-whitespace character."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_line_comment(self) -> None:
        """Consume text until the next newline character."""
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.advance()

    def peek(self):
        pos = self.pos + 1
        if pos > len(self.text) - 1:
            return None
        else:
            return self.text[pos]

    def get_next_token(self) -> Token:
        """ Responsible for breaking apart text into tokens."""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == ';':
                self.skip_line_comment()
                continue

            if self.current_char.isalpha():
                return self.identifier()

            if self.current_char.isdigit() or (self.current_char == '-' and self.peek().isdigit()):
                return self.number()

            if self.current_char == '#':
                return self.boolean()

            if self.current_char == '"':
                return self.string()

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, self.current_char)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, self.current_char)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MUL, self.current_char)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIV, self.current_char)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, self.current_char)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, self.current_char)

            self.error()

        return Token(TokenType.EOF, None)

    def peek_next_token(self, pos_ahead: int = 1) -> Token:
        current_pos = self.pos
        current_char = self.current_char

        next_token = self.get_next_token()
        for _ in range(pos_ahead - 1):
            next_token = self.get_next_token()
            if next_token.type == TokenType.EOF:
                return Token(TokenType.EOF, None)

        self.pos = current_pos
        self.current_char = current_char

        return next_token
