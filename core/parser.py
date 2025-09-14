from core.ast import (
    KozakNumber,
    KozakString,
    KozakComment,
    KozakVariable,
    KozakBinOp,
    KozakAssign,
    KozakProgram,
    KozakEcho
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
            comment_text = tok.value
            self.advance()
            # normalize: strip // or /* */ if present
            if comment_text.startswith('//'):
                text = comment_text[2:].strip()
            elif comment_text.startswith('/*') and comment_text.endswith('*/'):
                text = comment_text[2:-2].strip()
            else:
                text = comment_text
            return KozakComment(text)


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
        expr = self.expression()
        return KozakAssign(name, expr)

    def echo(self):
        self.expect('Spivaty')
        self.expect('LPAREN')
        expr = self.expression()
        self.expect('RPAREN')
        return KozakEcho(expr)

    # ---- Expression grammar ----
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
        elif tok.type == 'ID':
            self.advance()
            return KozakVariable(tok.value)
        elif tok.type == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        elif tok.type == 'STRING':
            self.advance()
            raw = tok.value
            # remove both single and double quotes
            if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                raw = raw[1:-1]
            return KozakString(raw)


        else:
            raise SyntaxError(f"Unexpected token in factor: {tok}")
