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
    KozakReturn,
    KozakTypeCast,
    KozakArray,
    KozakArrayIndex,
    KozakForEach
)

from core.lexer import Token

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []

    def error(self, token, message):
        if token:
            self.errors.append(f"Error at line {token.line}, col {token.column}: {message}")
        else:
            self.errors.append(f"Error at unknown location: {message}")
        self.synchronize()
        return None


    def synchronize(self):
        # Move forward until we hit a “safe” token
        while not self.is_at_end():
            tok = self.peek()
            if not tok:
                return
            if self.previous() and self.previous().type == 'SEMICOLON':
                return
            if tok.type in ('HETMAN', 'IF', 'FOR', 'DLYA', 'WHILE', 'FUNCTION', 'VAR'):
                return
            self.advance()

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
        
        if token:
            return self.error(token, f"Expected {expected_type}, got {token.type} at line {token.line}, column {token.column}")
        else:
            return self.error(token, f"Expected {expected_type}, but found end of file.")

    def parse(self):
        if not (self.peek() and self.peek().type == 'Hetman'):
            # Ми знаємо, що це перша лінія, тому можна вказати її явно
            raise SyntaxError("Be respectful to Hetman: you should always declare him at the start! (line 1, column 1)")
        self.advance()

        statements = []
        while self.peek():
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return KozakProgram(statements)

    def statement(self, require_semicolon=True):
        while self.peek() and self.peek().type in ('SEMICOLON', 'RBRACE'):
            self.advance()
        
        tok = self.peek()
        if not tok:
            return None

        if tok.type == 'Yakscho':
            return self.if_statement()
        elif tok.type == 'Doki':
            return self.while_statement()
        elif tok.type == 'Dlya':
            next_tok = self.peek_ahead(1)
            next_next_tok = self.peek_ahead(2)
            
            # for-each loop: Dlya <ID> dorohoyu <expr> { ... }
            if next_tok and next_tok.type == 'ID' and next_next_tok and next_next_tok.type == 'DOROHOYU':
                return self.for_each_statement()
            else:
                # normal for loop: Dlya (<init; cond; step>) { ... }
                return self.for_statement()

        elif tok.type == 'Zavdannya':
            return self.function_def()
        
        result = None
        if tok.type == 'ID':
            next_tok = self.tokens[self.current_token_index + 1]
            if next_tok and next_tok.type == 'OP' and next_tok.value == ':=':
                result = self.assignment()
            elif next_tok and next_tok.type == 'OP' and next_tok.value in ('++', '--'):
                self.advance()
                self.advance()
                result = KozakUnaryOp(next_tok.value, KozakVariable(tok.value))
            elif next_tok and next_tok.type == 'LPAREN':
                result = self.function_call()
            else:
                return self.error(tok, f"Unexpected ID token in statement: '{tok.value}' at line {tok.line}, column {tok.column}")

        elif tok.type == 'Spivaty':
            result = self.echo()
        elif tok.type == 'Povernuty':
            return self.return_statement()
        else:
            return self.error(tok, f"Unexpected token in statement: '{tok.value}' at line {tok.line}, column {tok.column}")

        if result and require_semicolon and not isinstance(result, (KozakIf, KozakWhile, KozakFor, KozakFunctionDef)):
            self.expect('SEMICOLON')
            
        return result

    def assignment(self):
        name = self.expect('ID').value
        op = self.expect('OP')
        if op.value != ':=':
            return self.error(op, f"Expected ':=', got {op.value} at line {op.line}, column {op.column}")
        expr = self.or_expression()
        return KozakAssign(name, expr)

    def echo(self):
        self.expect('Spivaty')
        self.expect('LPAREN')
        expressions = []
        if self.peek().type != 'RPAREN':
            expressions.append(self.or_expression())
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                expressions.append(self.or_expression())
        self.expect('RPAREN')
        return KozakEcho(expressions)
        
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
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*', '/', '%'):
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
        elif tok.type == 'ID' or tok.type == 'Dovzhyna':
            name = tok.value
            self.advance()

            if self.peek() and self.peek().type == 'LPAREN':
                arguments = self.function_call_arguments()
                node = KozakFunctionCall(name, arguments)
                return node

            node = KozakVariable(name)
            while self.peek() and self.peek().type == 'LBRACKET':
                self.advance()
                index_expr = self.or_expression()
                self.expect('RBRACKET')
                node = KozakArrayIndex(node, index_expr)
            return node
        
        elif tok.type == 'LBRACKET':
            self.advance()
            elements = []
            if self.peek().type != 'RBRACKET':
                elements.append(self.or_expression())
                while self.peek() and self.peek().type == 'COMMA':
                    self.advance()
                    elements.append(self.or_expression())
            self.expect('RBRACKET')
            return KozakArray(elements)
            
        elif tok.type == 'LPAREN':
            self.advance()
            expr = self.or_expression()
            self.expect('RPAREN')
            return expr
        elif tok.type == 'STRING':
            self.advance()
            raw = tok.value
            if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                raw = raw[1:-1]
            return KozakString(raw)
        elif tok.type in ('Chyslo', 'Ryadok', 'Logika', 'DroboveChyslo'):
            return self.type_cast()
        elif tok.type == 'Slukhai':
            return self.input_expression()
        else:
            return self.error(tok, f"Unexpected token in factor: '{tok.value}' at line {tok.line}, column {tok.column}")
    
    def input_expression(self):
        self.expect('Slukhai')
        self.expect('LPAREN')
        prompt_expr = self.or_expression()
        self.expect('RPAREN')
        return KozakInput(prompt_expr)
    
    def type_cast(self):
        tok = self.expect(self.peek().type)
        self.expect('LPAREN')
        expr = self.or_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return KozakTypeCast(tok.type, expr)
    
    def if_statement(self):
        self.expect('Yakscho')
        self.expect('LPAREN')
        condition = self.or_expression()
        self.expect('RPAREN')
        self.expect('LBRACE')
        body = self.block()
        else_if_parts = []
        while self.peek() and self.peek().type == 'AboYakscho':
            self.advance()
            self.expect('LPAREN')
            else_if_condition = self.or_expression()
            self.expect('RPAREN')
            self.expect('LBRACE')
            else_if_body = self.block()
            else_if_parts.append((else_if_condition, else_if_body))

        else_part = None
        if self.peek() and self.peek().type == 'Inakshe':
            self.advance()
            self.expect('LBRACE')
            else_part = self.block()

        return KozakIf(condition, body, else_if_parts, else_part)
    
    def while_statement(self):
        self.expect('Doki')
        self.expect('LPAREN')
        condition = self.or_expression()
        self.expect('RPAREN')
        self.expect('LBRACE')
        body = self.block()
        return KozakWhile(condition, body)
    
    def for_statement(self):
        self.expect('Dlya')
        self.expect('LPAREN')
        initialization = self.assignment()
        self.expect('SEMICOLON')
        condition = self.or_expression()
        self.expect('SEMICOLON')
        step = self.statement(require_semicolon=False)
        self.expect('RPAREN')
        self.expect('LBRACE')
        body = self.block()
        return KozakFor(initialization, condition, step, body)
    
    def function_def(self):
        self.expect('Zavdannya')
        name = self.expect('ID').value
        self.expect('LPAREN')
        parameters = []
        if self.peek().type != 'RPAREN':
            parameters.append(self.expect('ID').value)
            while self.peek().type == 'COMMA':
                self.advance()
                parameters.append(self.expect('ID').value)
        self.expect('RPAREN')
        self.expect('LBRACE')
        body = self.block()
        return KozakFunctionDef(name, parameters, body)

    def function_call_arguments(self):
        self.expect('LPAREN')
        arguments = []
        if self.peek().type != 'RPAREN':
            arguments.append(self.or_expression())
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                if self.peek() and self.peek().type == 'RPAREN':
                    return self.error(self.peek(), f"Function arguments cannot have a trailing comma, kozache. (line {self.peek().line}, column {self.peek().column})")
                arguments.append(self.or_expression())
        
        self.expect('RPAREN')
        return arguments

    def function_call(self):
        name = self.expect('ID').value
        arguments = self.function_call_arguments()
        return KozakFunctionCall(name, arguments)
    
    def return_statement(self):
        self.expect('Povernuty')
        value = self.or_expression()
        self.expect('SEMICOLON')
        return KozakReturn(value)

    def block(self):
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        self.expect('RBRACE')
        return body
    def for_each_statement(self):
        self.expect('Dlya')
        var_name = self.expect('ID').value
        self.expect('DOROHOYU')
        array_expr = self.or_expression()
        self.expect('LBRACE')
        body = self.block()
        return KozakForEach(var_name, array_expr, body)
    
    def peek_ahead(self, n):
        index = self.current_token_index + n
        if index < len(self.tokens):
            return self.tokens[index]
        return None
    
    def is_at_end(self):
        tok = self.peek()
        return tok is None or getattr(tok, 'type', None) == 'EOF'
    
    def previous(self):
        if self.current_token_index - 1 >= 0:
            return self.tokens[self.current_token_index - 1]
        return None

