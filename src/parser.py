from __future__ import annotations
from typing import TYPE_CHECKING
from src import ast
from src.errors import ErrorCode, ParserError
from src.token import Token, TokenType

if TYPE_CHECKING:
    from src.ast import AST, Program
    from src.lexer import Lexer


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        # set current token to first taken from lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, error_code: ErrorCode = ErrorCode.UNEXPECTED_TOKEN,
              token: Token = None) -> None:
        token = self.current_token if token is None else token
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value}: {token}',
        )

    def eat(self, token_type: TokenType) -> None:
        """ Eat the current token and advance to the next one.

        Compare the current token to the passed type. If they
        match then 'eat' the current token and assign the next
        token to self.current_token, otherwise raise an
        exception.
        """
        if self.current_token.type is token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def data(self) -> AST:
        """
        data: NUMBER
            | BOOLEAN
            | STRING
        """
        token = self.current_token

        if token.type is TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return ast.Num(token)
        elif token.type is TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
            return ast.Bool(token)
        elif token.type is TokenType.STRING:
            self.eat(TokenType.STRING)
            return ast.Str(token)
        else:
            self.error()

    def term(self) -> AST:
        """
        term: data
            | expr
            | const
        """
        token = self.current_token

        if token.type is TokenType.ID:
            self.eat(TokenType.ID)
            return ast.Const(token)
        elif token.type is TokenType.LPAREN:
            node = self.expr()
            return node
        else:
            return self.data()

    def p_expr(self) -> AST:
        """
        p-expr: LPAREN PLUS term* RPAREN
              | LPAREN MUL term* RPAREN
              | LPAREN MINUS term+ RPAREN
              | LPAREN DIV term+ RPAREN
        """
        # opening left bracket
        self.eat(TokenType.LPAREN)
        op = self.current_token
        node = ast.ProcCall(op, [])
        if op.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV]:
            self.eat(op.type)
        elif op.type is TokenType.ID:
            self.eat(TokenType.ID)
        else:
            self.error()

        while self.current_token.type != TokenType.RPAREN:
            node.append(self.term())

        # closing right bracket
        self.eat(TokenType.RPAREN)

        return node

    def expr(self) -> AST:
        """
        expr: data
            | p-expr
            | const
        """
        if self.current_token.type is TokenType.LPAREN:
            node = self.p_expr()
            return node
        elif self.current_token.type is TokenType.ID:
            token = self.current_token
            self.eat(TokenType.ID)
            return ast.Const(token)
        else:
            return self.data()

    # def empty(self) -> AST:
    #     """empty: """
    #     return ast.NoOp()

    def const(self):
        """const: ID"""
        node = ast.Const(self.current_token)
        self.eat(TokenType.ID)
        return node

    def constant_assignment(self) -> AST:
        """constant_assignment: LPAREN DEFINE const expr RPAREN"""
        # opening left bracket
        self.eat(TokenType.LPAREN)

        self.eat(TokenType.DEFINE)

        identifier = self.current_token
        self.eat(TokenType.ID)

        expr = self.expr()

        # closing right bracket
        self.eat(TokenType.RPAREN)

        return ast.ConstAssign(identifier, expr)

    def function_assignment(self) -> AST:
        """function_assignment: LPAREN DEFINE LPAREN const* RPAREN expr RPAREN"""
        # opening left bracket
        self.eat(TokenType.LPAREN)
        self.eat(TokenType.DEFINE)

        self.eat(TokenType.LPAREN)

        identifier = self.current_token
        self.eat(TokenType.ID)

        param = ast.Param(self.current_token)
        params = [param]
        self.eat(TokenType.ID)
        while self.current_token.type is TokenType.ID:
            param = ast.Param(self.current_token)
            params.append(param)
            self.eat(TokenType.ID)

        self.eat(TokenType.RPAREN)

        expr = self.expr()

        # closing right bracket
        self.eat(TokenType.RPAREN)

        return ast.ProcAssign(identifier, params, expr)

    def assignment_statement(self) -> AST:
        """
        assignment_statement: constant_assignment
                            | function_assignment
        """
        if self.lexer.peek_next_token(2).type is TokenType.LPAREN:
            return self.function_assignment()
        else:
            return self.constant_assignment()

    def statement(self) -> AST:
        """
        statement: assignment_statement
                 | expr
                 | empty
        """
        token = self.current_token
        if token.type in [TokenType.NUMBER, TokenType.BOOLEAN, TokenType.STRING, TokenType.ID]:
            node = self.expr()
            return node

        next_token = self.lexer.peek_next_token()
        if next_token.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV, TokenType.ID]:
            node = self.expr()
            return node
        elif next_token.type is TokenType.DEFINE:
            node = self.assignment_statement()
            return node
        else:
            self.error()

    def program(self) -> Program:
        """
        program : statement
                | statement compound_statement
        """
        statements = []

        while self.current_token.type != TokenType.EOF:
            statement = self.statement()
            statements.append(statement)

        return ast.Program(statements)

    def parse(self) -> Program:
        node = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error()

        return node
