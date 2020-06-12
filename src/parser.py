from __future__ import annotations
from typing import TYPE_CHECKING
from src import ast
from src.errors import ErrorCode, ParserError
from src.token import Token, TokenType

if TYPE_CHECKING:
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

    def error_mismatched_paren(self, expected: str) -> None:
        token = self.current_token
        received = token.value
        error_code = ErrorCode.WRONG_CLOSING_PARENTHESIS
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f"{error_code.value}, expected '{expected}' but received '{received}: {token}"
        )

    def eat(self, token_type: TokenType) -> Token:
        """ Eat the current token and advance to the next one.

        Compare the current token to the passed type. If they
        match then 'eat' the current token and assign the next
        token to self.current_token, otherwise raise an
        exception.
        """
        if self.current_token.type is token_type:
            previous_token = self.current_token
            self.current_token = self.lexer.get_next_token()
            return previous_token
        else:
            self.error()

    def eat_right_paren(self, left_paren: Token) -> None:
        left_value = left_paren.value
        right_value = self.current_token.value
        if left_value == '(' and right_value != ')':
            self.error_mismatched_paren(')')
        elif left_value == '[' and right_value != ']':
            self.error_mismatched_paren(']')
        elif left_value == '{' and right_value != '}':
            self.error_mismatched_paren('}')

        self.eat(TokenType.RPAREN)

    def data(self) -> ast.AST:
        """
        data: INTEGER
            | BOOLEAN
            | STRING
        """
        token = self.current_token

        if token.type is TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return ast.Int(token)
        elif token.type is TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
            return ast.Bool(token)
        elif token.type is TokenType.STRING:
            self.eat(TokenType.STRING)
            return ast.Str(token)
        elif token.type is TokenType.RATIONAL:
            self.eat(TokenType.RATIONAL)
            return ast.Rat(token)
        elif token.type is TokenType.DECIMAL:
            self.eat(TokenType.DECIMAL)
            return ast.Dec(token)
        else:
            self.error()

    def term(self) -> ast.AST:
        """
        term: data
            | expr
            | const
            | proc
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

    def p_expr(self) -> ast.AST:
        """p-expr: LPAREN proc term* RPAREN"""
        # opening left bracket
        left_paren = self.eat(TokenType.LPAREN)
        op = self.current_token
        node = ast.ProcCall(op, [])
        if op.type is TokenType.ID:
            self.eat(TokenType.ID)
        else:
            self.error()

        while self.current_token.type != TokenType.RPAREN:
            node.append(self.term())

        # closing right bracket
        self.eat_right_paren(left_paren)

        return node

    def cond_else(self) -> ast.CondElse:
        """cond-else: LPAREN ELSE expr RPAREN"""
        # opening left bracket
        left_paren = self.eat(TokenType.LPAREN)

        self.eat(TokenType.ELSE)

        expr = self.expr()

        node = ast.CondElse(left_paren, expr)

        # closing right bracket
        self.eat_right_paren(left_paren)

        return node

    def cond_branch(self) -> ast.CondBranch:
        """cond-branch: LPAREN expr expr RPAREN"""
        # opening left bracket
        left_paren = self.eat(TokenType.LPAREN)

        predicate = self.expr()
        expr = self.expr()

        node = ast.CondBranch(left_paren, predicate, expr)

        # closing right bracket
        self.eat_right_paren(left_paren)

        return node

    def cond(self) -> ast.Cond:
        """cond: LPAREN COND cond-branch+ cond-else? RPAREN"""
        # opening left bracket
        left_paren = self.eat(TokenType.LPAREN)

        token = self.eat(TokenType.COND)

        branches = [self.cond_branch()]
        while self.current_token.type == TokenType.LPAREN and self.lexer.peek_next_token().type == TokenType.LPAREN:
            branch = self.cond_branch()
            branches.append(branch)

        else_branch = None
        if self.lexer.peek_next_token().type == TokenType.ELSE:
            else_branch = self.cond_else()

        # closing right bracket
        self.eat_right_paren(left_paren)

        node = ast.Cond(token, branches, else_branch)
        return node

    def expr(self) -> ast.AST:
        """
        expr: data
            | p-expr
            | const
        """
        if self.current_token.type is TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if next_token.type is TokenType.COND:
                node = self.cond()
            else:
                node = self.p_expr()
            return node
        elif self.current_token.type is TokenType.ID:
            token = self.current_token
            self.eat(TokenType.ID)
            return ast.Const(token)
        else:
            return self.data()

    def const(self) -> ast.Const:
        """const: ID"""
        node = ast.Const(self.current_token)
        self.eat(TokenType.ID)
        return node

    def constant_assignment(self) -> ast.ConstAssign:
        """constant_assignment: LPAREN DEFINE const expr RPAREN"""
        # opening left bracket
        left_paren = self.eat(TokenType.LPAREN)

        self.eat(TokenType.DEFINE)

        identifier = self.current_token
        self.eat(TokenType.ID)

        expr = self.expr()

        # closing right bracket
        self.eat_right_paren(left_paren)

        return ast.ConstAssign(identifier, expr)

    def procedure_assignment(self) -> ast.ProcAssign:
        """procedure_assignment: LPAREN DEFINE LPAREN const* RPAREN expr RPAREN"""
        # opening left bracket
        left_paren_1 = self.eat(TokenType.LPAREN)
        self.eat(TokenType.DEFINE)

        left_paren_2 = self.eat(TokenType.LPAREN)

        identifier = self.current_token
        self.eat(TokenType.ID)

        params = []
        while self.current_token.type is TokenType.ID:
            param = ast.Param(self.current_token)
            params.append(param)
            self.eat(TokenType.ID)

        self.eat_right_paren(left_paren_2)

        expr = self.expr()

        # closing right bracket
        self.eat_right_paren(left_paren_1)

        return ast.ProcAssign(identifier, params, expr)

    def assignment_statement(self) -> ast.AST:
        """
        assignment_statement: constant_assignment
                            | procedure_assignment
        """
        if self.lexer.peek_next_token(2).type is TokenType.LPAREN:
            return self.procedure_assignment()
        else:
            return self.constant_assignment()

    def statement(self) -> ast.AST:
        """
        statement: assignment_statement
                 | expr
                 | empty
        """
        current_token = self.current_token
        if current_token.type in [TokenType.BOOLEAN, TokenType.DECIMAL, TokenType.INTEGER, TokenType.RATIONAL, TokenType.STRING, TokenType.ID]:
            return self.expr()
        elif current_token.type is TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if next_token.type is TokenType.ID:
                node = self.expr()
                return node
            elif next_token.type is TokenType.DEFINE:
                node = self.assignment_statement()
                return node
            else:
                self.error(token=next_token)
        else:
            self.error(token=current_token)

    def program(self) -> ast.Program:
        """
        program : statement
                | statement compound_statement
        """
        statements = []

        while self.current_token.type != TokenType.EOF:
            statement = self.statement()
            statements.append(statement)

        return ast.Program(statements)

    def parse(self) -> ast.Program:
        node = self.program()
        current_token = self.current_token
        if current_token.type != TokenType.EOF:
            self.error(token=current_token)

        return node
