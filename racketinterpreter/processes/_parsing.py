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

    def data(self) -> Union[ast.Bool, ast.Dec, ast.Int, ast.List, ast.Rat, ast.Str, ast.Sym]:
        """
        data: BOOLEAN
            | DECIMAL
            | INTEGER
            | LIST
            | RATIONAL
            | STRING
            | SYMBOL
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
        elif token.type is t.TokenType.QUOTE:
            self.eat(t.TokenType.QUOTE)

            next_token = self.current_token

            if next_token.type is t.TokenType.LPAREN:
                self.eat(t.TokenType.LPAREN)

                prims_stack = [[]]

                open_parens = 1
                while open_parens > 0:
                    curr_token = self.current_token
                    if curr_token.type is t.TokenType.EOF:
                        raise err.LexerError(
                            error_code=err.ErrorCode.RS_SYMBOL_FOUND_EOF,
                            token=t.Token(
                                type=t.TokenType.INVALID,
                                value="'",
                                line_no=curr_token.line_no,
                                column=curr_token.column
                            )
                        )

                    elif curr_token.type is t.TokenType.LPAREN:
                        open_parens += 1
                        self.eat(t.TokenType.LPAREN)

                        prims = []
                        prims_stack.append(prims)

                        continue

                    elif curr_token.type is t.TokenType.RPAREN:
                        open_parens -= 1
                        self.eat(t.TokenType.RPAREN)

                        if open_parens > 0:
                            expr = ast.List(token, prims_stack[-1])
                            prims_stack = prims_stack[:-1]
                            prims_stack[-1].append(expr)

                        continue

                    prims = prims_stack[-1]
                    if curr_token.type in [t.TokenType.BOOLEAN, t.TokenType.DECIMAL, t.TokenType.INTEGER,
                                           t.TokenType.RATIONAL, t.TokenType.STRING]:
                        prims.append(self.data())
                    elif curr_token.type is t.TokenType.NAME:
                        self.eat(t.TokenType.NAME)
                        name_token = t.Token(
                            type=t.TokenType.SYMBOL,
                            value=curr_token.value,
                            line_no=curr_token.line_no,
                            column=curr_token.column
                        )
                        prims.append(ast.Sym(name_token))
                    else:
                        raise err.IllegalStateError

                node = ast.List(token, prims_stack[0])
                return node
            elif next_token.type in [t.TokenType.BOOLEAN, t.TokenType.DECIMAL, t.TokenType.INTEGER,
                                     t.TokenType.RATIONAL, t.TokenType.STRING]:
                return self.data()
            elif next_token.type is t.TokenType.NAME:
                self.eat(t.TokenType.NAME)
                name_token = t.Token(
                    type=t.TokenType.SYMBOL,
                    value=next_token.value,
                    line_no=token.line_no,
                    column=token.column
                )
                return ast.Sym(name_token)
            else:
                raise err.IllegalStateError

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

        token = self.eat(t.TokenType.NAME)

        exprs = []
        while self.current_token.type is not t.TokenType.RPAREN:
            if self.current_token.type is t.TokenType.LPAREN:
                expr = self.cond_branch()
            else:
                expr = self.expr()
            exprs.append(expr)

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        node = ast.Cond(token, exprs)
        return node

    def expr(self) -> Union[ast.Bool, ast.Cond, ast.Dec, ast.Int, ast.Name, ast.ProcCall, ast.Rat, ast.Str, ast.Sym]:
        """
        expr: data
            | p-expr
            | ID
            | cond
            | list
        """
        if self.current_token.type is t.TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if next_token.value == t.Keyword.COND.value:
                node = self.cond()
            # elif next_token.value == t.Keyword.CONS.value:
            #     node = self.cons()
            else:
                node = self.p_expr()
            return node
        elif self.current_token.type is t.TokenType.NAME:
            token = self.current_token
            self.eat(t.TokenType.NAME)
            return ast.Name(token)
        # elif self.current_token.type is t.TokenType.LIST_ABRV:
        #     return self.list_abrv()
        else:
            return self.data()

    def name_assignment(self) -> ast.NameAssign:
        """name_assignment: LPAREN DEFINE expr* RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)

        self.eat(t.TokenType.NAME)

        exprs = []
        while self.current_token.type is not t.TokenType.RPAREN:
            expr = self.expr()
            exprs.append(expr)

        # closing right bracket
        self.eat(t.TokenType.RPAREN)

        return ast.NameAssign(left_paren_token, exprs)

    def procedure_assignment(self) -> ast.ProcAssign:
        """procedure_assignment: LPAREN DEFINE LPAREN expr* RPAREN expr* RPAREN"""
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)
        self.eat(t.TokenType.NAME)

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
        self.eat(t.TokenType.NAME)

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

    def assignment_statement(self) -> Union[ast.NameAssign, ast.ProcAssign, ast.StructAssign]:
        """
        assignment_statement: name_assignment
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
            return self.name_assignment()

    def check_expect(self) -> ast.CheckExpect:
        # opening left bracket
        left_paren_token = self.eat(t.TokenType.LPAREN)

        self.eat(t.TokenType.NAME)

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
        if current_token.type in [t.TokenType.BOOLEAN, t.TokenType.DECIMAL, t.TokenType.INTEGER, t.TokenType.QUOTE,
                                  t.TokenType.RATIONAL, t.TokenType.STRING, t.TokenType.NAME, t.TokenType.SYMBOL]:
            return self.expr()
        elif current_token.type is t.TokenType.LPAREN:
            next_token = self.lexer.peek_next_token()
            if (next_token.type is t.TokenType.NAME
                    and next_token.value in [t.Keyword.DEFINE.value, t.Keyword.DEFINE_STRUCT.value]):
                node = self.assignment_statement()
                return node
            elif next_token.type is t.TokenType.NAME and next_token.value == t.Keyword.CHECK_EXPECT.value:
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
