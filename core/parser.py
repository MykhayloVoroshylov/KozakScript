"""Parser for KozakScript"""

from core.ast import (
    KozakNumber,
    KozakString,
    KozakUnaryOp,
    KozakVariable,
    KozakBinOp,
    KozakAssign,
    KozakProgram,
    KozakEcho,
    KozakInput,
    KozakBoolean,
    KozakComparisonOp,
    KozakIf,
    KozakWhile,
    KozakFor,
    KozakFunctionCall,
    KozakFunctionDef,
    KozakReturn
)

import dataclasses


@dataclasses.dataclass
class KozakTypeCast:
    target_type: str
    expr: object

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def peek(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def advance(self):
        self.current_token_index += 1

    def expect(self, expected_type):
        token = self.peek()
        if token and token.type == expected_type:
            self.advance()
            return token
        raise SyntaxError(f"Expected {expected_type}, got {token.type}")

    def parse(self):
        if not (self.peek() and self.peek().type == 'Hetman'):
            raise SyntaxError("Be respectful to Hetman: you should always declare him at the start!")
        self.advance()  # consume Hetman

        statements = []
        while self.peek():
            statements.append(self.statement())
        return KozakProgram(statements)

    def statement(self):
        tok = self.peek()
        if not tok:
            return None

        if tok.type == 'COMMENT':
            self.advance()
            return None

        if tok.type == 'ID':
            if self.tokens[self.current_token_index + 1].value in ('++', '--'):
                var_name = self.expect('ID').value
                op_token = self.expect('OP').value
                return KozakUnaryOp(op_token, KozakVariable(var_name))
            next_tok = self.tokens[self.current_token_index + 1]
            if next_tok and next_tok.type == 'LPAREN':
                return self.function_call() 
            else:
                return self.assignment()


        elif tok.type == 'Spivaty':
            return self.echo()
        
        elif tok.type == 'Yakscho':
            return self.if_statement()
        
        elif tok.type == 'Doki':
            return self.while_statement()
        
        elif tok.type == 'Dlya':
            return self.for_statement()
        
        elif tok.type == 'Zavdannya':
            return self.function_def()
        
        elif tok.type == 'Povernuty':
            return self.return_statement()
        
        elif tok.type in ('LPAREN', 'NUMBER', 'STRING', 'Pravda', 'Nepravda'):
            return self.or_expression()

        else:
            raise SyntaxError(f"Unexpected token in statement: {tok}")

    def assignment(self):
        name = self.expect('ID').value
        op = self.expect('OP')
        if op.value != ':=':
            raise SyntaxError(f"Expected ':=', got {op.value}")
        expr = self.comparison()
        return KozakAssign(name, expr)

    def echo(self):
        self.expect('Spivaty')
        self.expect('LPAREN')
        tok = self.peek()
        if tok and tok.type == 'RPAREN':
            raise SyntaxError("Spivaty requires an expression to print!")
        expr = self.comparison()
        self.expect('RPAREN')
        return KozakEcho(expr)

    def comparison(self):
        left = self.expression()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('==', '!=', '<', '>', '<=', '>='):
            op = self.expect('OP').value
            right = self.expression()
            left = KozakComparisonOp(left, op, right)
        return left

    def expression(self):
        left = self.term()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('+', '-'):
            op = self.expect('OP').value
            right = self.term()
            left = KozakBinOp(left, op, right)
        return left

    def term(self):
        left = self.exponent()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*', '/'):
            op = self.expect('OP').value
            right = self.exponent()
            left = KozakBinOp(left, op, right)
        return left

    def exponent(self): 
        left = self.factor()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('^', '^/'):
            op = self.expect('OP').value
            right = self.factor()
            left = KozakBinOp(left, op, right)
        return left

    def factor(self):
        tok = self.peek()
        if tok.type == 'NUMBER':
            self.advance()
            return KozakNumber(tok.value)
        elif tok.type == 'Pravda':
            self.advance()
            return KozakBoolean(True)
        elif tok.type == 'Nepravda':
            self.advance()
            return KozakBoolean(False)
        elif tok.type == 'ID':
            self.advance()
            return KozakVariable(tok.value)
        elif tok.type == 'LPAREN':
            self.advance()
            expr = self.comparison()
            self.expect('RPAREN')
            return expr
        elif tok.type == 'STRING':
            self.advance()
            raw = tok.value
            if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                raw = raw[1:-1]
            return KozakString(raw)
        elif tok.type in ('Chyslo', 'Ryadok', 'Logika'):
            return self.type_cast()
            
        elif tok.type == 'Slukhai':
            return self.input_expression()

        else:
            raise SyntaxError(f"Unexpected token in factor: {tok}")
 
    def input_expression(self):
        self.expect('Slukhai')
        self.expect('LPAREN')
        tok = self.peek()
        if tok and tok.type == 'RPAREN':
            raise SyntaxError("Slukhai requires a prompt expression!")
        prompt_expr = self.comparison()
        self.expect('RPAREN')
        return KozakInput(prompt_expr)
    
    def type_cast(self):
        tok = self.expect(self.peek().type) 
        self.expect('LPAREN')
        expr = self.comparison()
        self.expect('RPAREN')
        return KozakTypeCast(tok.type, expr)
    
    def if_statement(self):
        self.expect('Yakscho')
        self.expect('LPAREN')
        condition = self.or_expression()
        self.expect('RPAREN')
        self.expect('LBRACE')
        
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        self.expect('RBRACE')
        
        else_if_parts = []
        while self.peek() and self.peek().type == 'AboYakscho':
            self.advance()
            self.expect('LPAREN')
            else_if_condition = self.or_expression()
            self.expect('RPAREN')
            self.expect('LBRACE')
            else_if_body = []
            while self.peek() and self.peek().type != 'RBRACE':
                stmt = self.statement()
                if stmt:
                    else_if_body.append(stmt)
            self.expect('RBRACE')
            else_if_parts.append((else_if_condition, else_if_body))

        else_part = None
        if self.peek() and self.peek().type == 'Inakshe':
            self.advance()
            self.expect('LBRACE')
            else_body = []
            while self.peek() and self.peek().type != 'RBRACE':
                stmt = self.statement()
                if stmt:
                    else_body.append(stmt)
            self.expect('RBRACE')
            else_part = else_body

        return KozakIf(condition, body, else_if_parts, else_part)
    
    def while_statement(self):
        self.expect('Doki')
        self.expect('LPAREN')
        condition = self.or_expression()
        self.expect('RPAREN')
        self.expect('LBRACE')

        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        self.expect('RBRACE')

        return KozakWhile(condition, body)

    def or_expression(self):
        left = self.and_expression()
        while self.peek() and self.peek().value == '||':
            op = self.expect('OP').value
            right = self.and_expression()
            left = KozakBinOp(left, op, right)
        return left
    
    def and_expression(self):
        left = self.comparison()
        while self.peek() and self.peek().value == '&&':
            op = self.expect('OP').value
            right = self.comparison()
            left = KozakBinOp(left, op, right)
        return left

    def for_statement(self):
        self.expect('Dlya')
        self.expect('LPAREN')

        initialization = self.assignment()
        self.expect('SEMICOLON')

        condition = self.or_expression()
        self.expect('SEMICOLON')

        step = self.statement()
        self.expect('RPAREN')
        self.expect('LBRACE')

        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        self.expect('RBRACE')

        return KozakFor(initialization, condition, step, body)
    
    def function_def(self):
        self.expect('Zavdannya')
        name = self.expect('ID').value
        self.expect('LPAREN')

        # ВИПРАВЛЕНО: Використовуємо новий метод для парсингу параметрів
        parameters = []
        if self.peek().type != 'RPAREN':
            parameters.append(self.expect('ID').value)
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                if self.peek().type == 'RPAREN':
                    raise SyntaxError("Trailing comma is not allowed, kozache.")
                parameters.append(self.expect('ID').value)
        self.expect('RPAREN')
        self.expect('LBRACE')

        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        self.expect('RBRACE')

        return KozakFunctionDef(name, parameters, body)

    
    def function_call(self):
        name = self.expect('ID').value
        self.expect('LPAREN')

        # ВИПРАВЛЕНО: Використовуємо новий метод для парсингу аргументів
        arguments = self._parse_comma_separated_list()

        self.expect('RPAREN')

        return KozakFunctionCall(name, arguments)


    
    def return_statement(self):
        self.expect('Povernuty')
        value = self.or_expression()
        return KozakReturn(value)
    
    def _parse_comma_separated_list(self):
        items = []
        if self.peek().type != 'RPAREN':
            items.append(self.or_expression())
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                if self.peek().type == 'RPAREN':
                    # Запобігаємо помилкам з комою в кінці списку
                    raise SyntaxError("Trailing comma is not allowed, kozache.")
                items.append(self.or_expression())
        return items

