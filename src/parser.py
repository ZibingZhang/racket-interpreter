from __future__ import annotations
from typing import TYPE_CHECKING, Union
from src import ast
from src.errors import ErrorCode, ParserError
from src.token import Keyword, Token, TokenType

if TYPE_CHECKING:
    from src.lexer import Lexer


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        # set current token to first taken from lexer
        self.current_token = self.lexer.get_next_token()
        self.left_paren_stack = []

    def error_unexpected_token(self, token) -> None:
        if token.type is TokenType.EOF:
            raise ParserError(
                error_code=ErrorCode.RS_UNEXPECTED_EOF,
                token=token
            )
        else:
            raise ParserError(
                error_code=ErrorCode.RS_UNEXPECTED_TOKEN,
                token=token
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
            current_token = self.current_token
            self.error_unexpected_token(token=current_token)

    def data(self) -> Union[ast.Int, ast.Bool, ast.Str, ast.Rat, ast.Dec]:
        """
        data: INTEGER
            | BOOLEAN
            | STRING
        """
        current_token = self.current_token

        if current_token.type is TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return ast.Int(current_token)
        elif current_token.type is TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
            return ast.Bool(current_token)
        elif current_token.type is TokenType.STRING:
            self.eat(TokenType.STRING)
            return ast.Str(current_token)
        elif current_token.type is TokenType.RATIONAL:
            self.eat(TokenType.RATIONAL)
            return ast.Rat(current_token)
        elif current_token.type is TokenType.DECIMAL:
            self.eat(TokenType.DECIMAL)
            return ast.Dec(current_token)
        else:
            self.error_unexpected_token(token=current_token)

    def p_expr(self) -> ast.ProcCall:
        """p-expr: LPAREN expr* RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(TokenType.LPAREN)

        exprs = []
        while self.current_token.type != TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        node = ast.ProcCall(left_paren_token, exprs)

        # closing right bracket
        self.eat(TokenType.RPAREN)

        return node

    def cond_branch(self) -> ast.CondBranch:
        """cond-branch: p-expr"""
        # opening left bracket
        left_paren_token = self.eat(TokenType.LPAREN)

        exprs = []

        while self.current_token.type is not TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        node = ast.CondBranch(left_paren_token, exprs)

        # closing right bracket
        self.eat(TokenType.RPAREN)

        return node

    def cond(self) -> ast.Cond:
        """cond: LPAREN COND (cond-branch|data|ID|cond)* cond-else? RPAREN"""
        # opening left bracket
        self.eat(TokenType.LPAREN)

        token = self.eat(TokenType.ID)

        branches = []
        while self.current_token.type is not TokenType.RPAREN:
            if self.current_token.type is TokenType.LPAREN:
                expr = self.cond_branch()
            else:
                expr = self.expr()
            branches.append(expr)

        else_branch = None
        try:
            last_branch = branches[-1]
            first_expr = last_branch.exprs[0]
        except (AttributeError, IndexError) as e:
            pass
        else:
            token = first_expr.token
            if token.type is TokenType.ID and token.value == Keyword.ELSE.value:
                branches = branches[:-1]
                else_branch = ast.CondElse(last_branch.token, last_branch.exprs[1:])

        # closing right bracket
        self.eat(TokenType.RPAREN)

        node = ast.Cond(token, branches, else_branch)
        return node

    def expr(self) -> Union[ast.Bool, ast.Cond, ast.Dec, ast.Int,
                            ast.Id, ast.ProcCall, ast.Rat, ast.Str]:
        """
        expr: data
            | p-expr
            | ID
            | cond
        """
        if self.current_token.type is TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if next_token.value == Keyword.COND.value:
                node = self.cond()
            else:
                node = self.p_expr()
            return node
        elif self.current_token.type is TokenType.ID:
            token = self.current_token
            self.eat(TokenType.ID)
            return ast.Id(token)
        else:
            return self.data()

    def constant_assignment(self) -> ast.ConstAssign:
        """constant_assignment: LPAREN DEFINE expr* RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(TokenType.LPAREN)

        self.eat(TokenType.ID)

        actual_params = []
        while self.current_token.type is not TokenType.RPAREN:
            expr = self.expr()
            actual_params.append(expr)

        # closing right bracket
        self.eat(TokenType.RPAREN)

        # return ast.ConstAssign(name, expr)
        return ast.ConstAssign(left_paren_token, actual_params)

    def procedure_assignment(self) -> ast.ProcAssign:
        """procedure_assignment: LPAREN DEFINE LPAREN ID* RPAREN expr RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(TokenType.LPAREN)
        self.eat(TokenType.ID)

        self.eat(TokenType.LPAREN)

        name_expr = None
        if self.current_token.type is not TokenType.RPAREN:
            name_expr = self.expr()

        formal_params = []
        while self.current_token.type is not TokenType.RPAREN:
            expr = self.expr()
            param = ast.Param(expr, ast.Param.ParamFor.PROC_ASSIGN)
            formal_params.append(param)

        self.eat(TokenType.RPAREN)

        exprs = []
        while self.current_token.type is not TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        # closing right bracket
        self.eat(TokenType.RPAREN)

        return ast.ProcAssign(left_paren_token, name_expr, formal_params, exprs)

    def structure_assignment(self) -> ast.StructAssign:
        """structure_assignment: LPAREN DEFINE_STRUCT LPAREN ID* RPAREN RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(TokenType.LPAREN)
        self.eat(TokenType.ID)

        node = ast.StructAssign(left_paren_token)

        idx = 0
        while self.current_token.type is not TokenType.RPAREN:
            if idx == 0:
                node.struct_name_ast = self.expr()
            elif idx == 1:
                if self.current_token.type is TokenType.LPAREN:
                    self.eat(TokenType.LPAREN)

                    field_asts = []

                    while self.current_token.type is not TokenType.RPAREN:
                        expr = self.expr()
                        param = ast.Param(expr, ast.Param.ParamFor.STRUCT_ASSIGN)
                        field_asts.append(param)

                    node.field_asts = field_asts

                    self.eat(TokenType.RPAREN)

                else:
                    node.field_asts = self.expr()
            elif idx >= 2:
                expr = self.expr()
                node.extra_asts.append(expr)

            idx += 1


        # identifier = self.current_token
        # self.eat(TokenType.ID)
        #
        # self.eat(TokenType.LPAREN)
        #
        # fields = []
        # while self.current_token.type is TokenType.ID:
        #     fields.append(self.current_token.value)
        #     self.eat(TokenType.ID)
        #
        # self.eat(TokenType.RPAREN)

        # closing right bracket
        self.eat(TokenType.RPAREN)

        # return ast.StructAssign(identifier, fields)
        return node

    def assignment_statement(self) -> ast.AST:
        """
        assignment_statement: constant_assignment
                            | function_assignment
                            | structure_assignment
        """
        next_token = self.lexer.peek_next_token()
        next_next_token = self.lexer.peek_next_token(2)

        if next_token.value == Keyword.DEFINE_STRUCT.value:
            return self.structure_assignment()
        elif next_next_token.type is TokenType.LPAREN:
            return self.procedure_assignment()
        else:
            return self.constant_assignment()

    def statement(self) -> ast.AST:
        """
        statement: assignment_statement
                 | expr
        """
        current_token = self.current_token
        if current_token.type in [TokenType.BOOLEAN, TokenType.DECIMAL, TokenType.INTEGER,
                                  TokenType.RATIONAL, TokenType.STRING, TokenType.ID]:
            return self.expr()
        elif current_token.type is TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if next_token.type is TokenType.ID \
                    and next_token.value in [Keyword.DEFINE.value, Keyword.DEFINE_STRUCT.value]:
                node = self.assignment_statement()
                return node
            else:
                node = self.expr()
                return node
        else:
            self.error_unexpected_token(token=current_token)

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
        self.eat(TokenType.EOF)

        return node
