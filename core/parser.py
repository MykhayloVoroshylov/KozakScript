"""Parser for KozakScript"""

from core.ast import (
    KozakNumber,
    KozakString,
    KozakComment,
    KozakVariable,
    KozakBinOp,
    KozakAssign,
    KozakProgram,
    KozakEcho,
    KozakInput,
    KozakBoolean,
    KozakComparisonOp
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def expect(self, token_type):
        tok = self.peek()
        if tok and tok.type == token_type:
            self.advance()
            return tok
        raise SyntaxError(f'Expected {token_type}, got {tok.type if tok else None}')

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
            return self.assignment()

        elif tok.type == 'Spivaty':
            return self.echo()
        
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
        left = self.factor()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*', '/'):
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






