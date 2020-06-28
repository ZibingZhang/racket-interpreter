from __future__ import annotations
from typing import TYPE_CHECKING, Union
from racketinterpreter import errors as err
from racketinterpreter.classes import ast
from racketinterpreter.classes import tokens as t

if TYPE_CHECKING:
    from racketinterpreter.processes import Lexer


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        # set current token to first taken from lexer
        self.current_token = self.lexer.get_next_token()
        self.left_paren_stack = []

    def parse(self) -> ast.Program:
        node = self.program()
        self.eat(t.TokenType.EOF)

        return node

    def error_unexpected_token(self, token) -> None:
        if token.type is t.TokenType.EOF:
            raise err.ParserError(
                error_code=err.ErrorCode.RS_UNEXPECTED_EOF,
                token=token
            )
        else:
            raise err.ParserError(
                error_code=err.ErrorCode.RS_UNEXPECTED_TOKEN,
                token=token
            )

    def eat(self, token_type: t.TokenType) -> t.Token:
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

    def data(self) -> Union[ast.Bool, ast.Dec, ast.Int, ast.Rat, ast.Str, ast.Sym]:
        """
        data: INTEGER
            | BOOLEAN
            | STRING
        """
        token = self.current_token

        if token.type is t.TokenType.BOOLEAN:
            self.eat(t.TokenType.BOOLEAN)
            return ast.Bool(token)
        elif token.type is t.TokenType.DECIMAL:
            self.eat(t.TokenType.DECIMAL)
            return ast.Dec(token)
        elif token.type is t.TokenType.INTEGER:
            self.eat(t.TokenType.INTEGER)
            return ast.Int(token)
        elif token.type is t.TokenType.RATIONAL:
            self.eat(t.TokenType.RATIONAL)
            return ast.Rat(token)
        elif token.type is t.TokenType.STRING:
            self.eat(t.TokenType.STRING)
            return ast.Str(token)
        elif token.type is t.TokenType.SYMBOL:
            self.eat(t.TokenType.SYMBOL)
            return ast.Sym(token)
        else:
            self.error_unexpected_token(token=token)

    def p_expr(self) -> ast.ProcCall:
        """p-expr: LPAREN expr* RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)

        exprs = []
        while self.current_token.type != t.TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        node = ast.ProcCall(left_paren_token, exprs)

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        return node

    def cond_branch(self) -> ast.CondBranch:
        """cond-branch: p-expr"""
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)

        exprs = []

        while self.current_token.type is not t.TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        node = ast.CondBranch(left_paren_token, exprs)

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        return node

    def cond(self) -> ast.Cond:
        """cond: LPAREN COND (cond-branch|data|ID|cond)* cond-else? RPAREN"""
        # opening left bracket
        self.eat(t.TokenType.LPAREN)

        token = self.eat(t.TokenType.ID)

        branches = []
        while self.current_token.type is not t.TokenType.RPAREN:
            if self.current_token.type is t.TokenType.LPAREN:
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
            if token.type is t.TokenType.ID and token.value == t.Keyword.ELSE.value:
                branches = branches[:-1]
                else_branch = ast.CondElse(last_branch.token, last_branch.exprs[1:])

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        node = ast.Cond(token, branches, else_branch)
        return node

    def expr(self) -> Union[ast.Bool, ast.Cond, ast.Dec, ast.Int,
                            ast.Id, ast.ProcCall, ast.Rat, ast.Str, ast.Sym]:
        """
        expr: data
            | p-expr
            | ID
            | cond
        """
        if self.current_token.type is t.TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if next_token.value == t.Keyword.COND.value:
                node = self.cond()
            else:
                node = self.p_expr()
            return node
        elif self.current_token.type is t.TokenType.ID:
            token = self.current_token
            self.eat(t.TokenType.ID)
            return ast.Id(token)
        else:
            return self.data()

    def constant_assignment(self) -> ast.IdAssign:
        """constant_assignment: LPAREN DEFINE expr* RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)

        self.eat(t.TokenType.ID)

        actual_params = []
        while self.current_token.type is not t.TokenType.RPAREN:
            expr = self.expr()
            actual_params.append(expr)

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        return ast.IdAssign(left_paren_token, actual_params)

    def procedure_assignment(self) -> ast.ProcAssign:
        """procedure_assignment: LPAREN DEFINE LPAREN expr* RPAREN expr* RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)
        self.eat(t.TokenType.ID)

        self.eat(t.TokenType.LPAREN)

        name_expr = None
        if self.current_token.type is not t.TokenType.RPAREN:
            name_expr = self.expr()

        formal_params = []
        while self.current_token.type is not t.TokenType.RPAREN:
            expr = self.expr()
            param = ast.FormalParam(expr, ast.FormalParam.ParamFor.PROC_ASSIGN)
            formal_params.append(param)

        self.eat(t.TokenType.RPAREN)

        exprs = []
        while self.current_token.type is not t.TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        return ast.ProcAssign(left_paren_token, name_expr, formal_params, exprs)

    def structure_assignment(self) -> ast.StructAssign:
        """structure_assignment: LPAREN DEFINE_STRUCT LPAREN expr* RPAREN RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)
        self.eat(t.TokenType.ID)

        node = ast.StructAssign(left_paren_token)

        idx = 0
        while self.current_token.type is not t.TokenType.RPAREN:
            if idx == 0:
                node.struct_name_ast = self.expr()
            elif idx == 1:
                if self.current_token.type is t.TokenType.LPAREN:
                    self.eat(t.TokenType.LPAREN)

                    field_asts = []

                    while self.current_token.type is not t.TokenType.RPAREN:
                        expr = self.expr()
                        param = ast.FormalParam(expr, ast.FormalParam.ParamFor.STRUCT_ASSIGN)
                        field_asts.append(param)

                    node.field_asts = field_asts

                    self.eat(t.TokenType.RPAREN)

                else:
                    node.field_asts = self.expr()
            elif idx >= 2:
                expr = self.expr()
                node.extra_asts.append(expr)

            idx += 1

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        # return ast.StructAssign(identifier, fields)
        return node

    def assignment_statement(self) -> Union[ast.IdAssign, ast.ProcAssign, ast.StructAssign]:
        """
        assignment_statement: constant_assignment
                            | function_assignment
                            | structure_assignment
        """
        next_token = self.lexer.peek_next_token()
        next_next_token = self.lexer.peek_next_token(2)

        if next_token.value == t.Keyword.DEFINE_STRUCT.value:
            return self.structure_assignment()
        elif next_next_token.type is t.TokenType.LPAREN:
            return self.procedure_assignment()
        else:
            return self.constant_assignment()

    def check_expect(self) -> ast.CheckExpect:
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)

        self.eat(t.TokenType.ID)

        exprs = []
        while self.current_token.type is not t.TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        node = ast.CheckExpect(left_paren_token, exprs)
        return node

    def statement(self) -> ast.AST:
        """
        statement: assignment_statement
                 | expr
        """
        current_token = self.current_token
        if current_token.type in [t.TokenType.BOOLEAN, t.TokenType.DECIMAL, t.TokenType.INTEGER,
                                  t.TokenType.RATIONAL, t.TokenType.STRING, t.TokenType.ID, t.TokenType.SYMBOL]:
            return self.expr()
        elif current_token.type is t.TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if next_token.type is t.TokenType.ID \
                    and next_token.value in [t.Keyword.DEFINE.value, t.Keyword.DEFINE_STRUCT.value]:
                node = self.assignment_statement()
                return node
            elif next_token.type is t.TokenType.ID \
                    and next_token.value == t.Keyword.CHECK_EXPECT.value:
                node = self.check_expect()
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

        while self.current_token.type != t.TokenType.EOF:
            statement = self.statement()
            statements.append(statement)

        return ast.Program(statements)