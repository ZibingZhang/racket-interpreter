from __future__ import annotations
from typing import TYPE_CHECKING
from src import ast
from src.token import Token, TokenType

if TYPE_CHECKING:
    from src.ast import AST, Program
    from src.lexer import Lexer


class ParserError(Exception):

    pass


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        # set current token to first taken from lexer
        self.current_token = self.lexer.get_next_token()

    def error(self) -> None:
        raise ParserError('Invalid syntax.')

    def eat(self, token_type: TokenType) -> None:
        """ Eat the current token and advance to the next one.

        Compare the current token to the passed type. If they
        match then 'eat' the current token and assign the next
        token to self.current_token, otherwise raise an
        exception.
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def term(self) -> AST:
        """term: NUMBER
               | expr
               | variable"""
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return ast.Num(token)
        elif token.type == TokenType.ID:
            self.eat(TokenType.ID)
            return ast.Var(token)
        elif token.type == TokenType.LPAREN:
            node = self.expr()
            return node
        else:
            self.error()

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
        node = ast.Func(op)
        if op.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV]:
            self.eat(op.type)
        else:
            self.error()

        # no arguments
        if self.current_token.type == TokenType.RPAREN:
            # closing right bracket
            self.eat(TokenType.RPAREN)
            if op.type in [TokenType.PLUS, TokenType.MUL]:
                return node

        while self.current_token.type != TokenType.RPAREN:
            if op.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV]:
                node.append(self.term())
            else:
                self.error()

        # closing right bracket
        self.eat(TokenType.RPAREN)

        return node

    def expr(self) -> AST:
        """
        expr: NUMBER
            | p-expr
            | variable
        """
        if self.current_token.type == TokenType.NUMBER:
            token = Token(TokenType.NUMBER, self.current_token.value)
            self.eat(TokenType.NUMBER)
            return ast.Num(token)
            # return self.current_token.value
        elif self.current_token.type == TokenType.LPAREN:
            node = self.p_expr()
            return node
        elif self.current_token.type == TokenType.ID:
            token = Token(TokenType.ID, self.current_token.value)
            self.eat(TokenType.ID)
            return ast.Var(token)
        else:
            self.error()

    def empty(self) -> AST:
        """empty: """
        return ast.NoOp()

    def variable(self):
        """variable: ID"""
        node = ast.Var(self.current_token)
        self.eat(TokenType.ID)
        return node

    def assignment_statement(self) -> AST:
        """assignment_statement: LPAREN DEFINE variable expr RPAREN"""
        # opening left bracket
        self.eat(TokenType.LPAREN)
        self.eat(TokenType.DEFINE)

        identifier = self.current_token.value
        self.eat(TokenType.ID)

        expr = self.expr()
        self.eat(TokenType.RPAREN)

        return ast.Define(identifier, expr)

    def statement(self) -> AST:
        """
        statement: assignment_statement
                 | expr
                 | empty
        """
        token = self.current_token
        if token.type in [TokenType.NUMBER, TokenType.ID]:
            node = self.expr()
            return node

        next_token = self.lexer.peek_next_token()
        if next_token.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV]:
            node = self.expr()
        elif next_token.type == TokenType.DEFINE:
            node = self.assignment_statement()
        else:
            node = self.empty()

        return node

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
