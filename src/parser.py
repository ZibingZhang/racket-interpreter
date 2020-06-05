from __future__ import annotations
from typing import TYPE_CHECKING
from src import ast
from src.token import Token, TokenType

if TYPE_CHECKING:
    from src.ast import AST
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
        """term: NUMBER | expr | variable"""
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
        if op.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
        elif op.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
        elif op.type == TokenType.MUL:
            self.eat(TokenType.MUL)
        elif op.type == TokenType.DIV:
            self.eat(TokenType.DIV)
        else:
            self.error()

        # no arguments
        if self.current_token.type == TokenType.RPAREN:
            # closing right bracket
            self.eat(TokenType.RPAREN)
            if op.type == TokenType.PLUS:
                return node
            elif op.type == TokenType.MUL:
                return node

        while self.current_token.type in [TokenType.NUMBER, TokenType.LPAREN]:
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
        """
        if self.current_token.type == TokenType.NUMBER:
            token = Token(TokenType.NUMBER, self.current_token.value)
            return ast.Num(token)
            # return self.current_token.value
        elif self.current_token.type == TokenType.LPAREN:
            node = self.p_expr()
            return node
        else:
            self.error()

    def parse(self):
        return self.expr()
