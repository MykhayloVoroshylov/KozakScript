"""Parser for KozakScript (error-collecting version)"""

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
    KozakTypeCast
)

from core.errors import KozakSyntaxError, KozakTypeError, KozakNameError 


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []

    # ---------- Utility helpers ----------
    def peek(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def advance(self):
        self.current_token_index += 1

    def previous(self):
        if self.current_token_index > 0:
            return self.tokens[self.current_token_index - 1]
        return None

    def is_at_end(self):
        return self.current_token_index >= len(self.tokens) or (self.peek() and self.peek().type == 'EOF')

    # ---------- Error handling / recovery ----------
    def error(self, token, message):
        line = token.line if token else "Unknown"
        column = token.column if token else "Unknown"
        self.errors.append(f"Error at line {line}, col {column}: {message}")
        self.synchronize()
        return None

    def synchronize(self):
        # Move forward until a 'safe' point — semicolon or start of next top-level statement
        while not self.is_at_end():
            prev = self.previous()
            if prev and prev.type == 'SEMICOLON':
                return
            current = self.peek()
            if current and current.type in ('Hetman', 'Yakscho', 'Doki', 'Dlya', 'Zavdannya', 'Spivaty', 'ID'):
                return
            self.advance()

    # ---------- Expect wrapper (does not raise immediately) ----------
    def expect(self, expected_type):
        token = self.peek()
        if token and token.type == expected_type:
            self.advance()
            return token

        if token:
            # record error and try to recover (synchronize moves us forward)
            self.error(token, f"Expected {expected_type}, got {token.type}")
            # DO NOT advance here — synchronize already moved the cursor.
            return None

        # end of file
        self.error(None, f"Expected {expected_type}, but found end of file.")
        return None

    # ---------- Entry point ----------
    def parse(self):
        # Check for Hetman at start — collect error rather than raise
        if not (self.peek() and self.peek().type == 'Hetman'):
            raise KozakSyntaxError("Be respectful to Hetman: you should always declare him at the start!")
        else:
            # consume Hetman
            self.advance()

        statements = []
        while self.peek() and not self.is_at_end():
            start_index = self.current_token_index
            stmt = self.statement()
            # statement may be None if an error occurred and we couldn't recover for that statement
            if stmt:
                statements.append(stmt)
            if self.current_token_index == start_index:
                self.advance()

        if self.errors:
            full_error_message = "Parsing errors found:\n" + "\n".join(self.errors)
            raise KozakSyntaxError(full_error_message)


        return KozakProgram(statements)

    # ---------- Statements ----------
    def statement(self, require_semicolon=True):
        # skip stray semicolons
        while self.peek() and self.peek().type == 'SEMICOLON':
            self.advance()

        tok = self.peek()
        if not tok:
            return None

        # skip comments (lexer may already filter but keep safe)
        if tok.type in ('COMMENT', 'MLCOMMENT'):
            self.advance()
            return None

        stmt = None

        # --- Function calls, assignments, unary ops ---
        if tok.type == 'ID':
            next_tok = self.tokens[self.current_token_index + 1] if self.current_token_index + 1 < len(self.tokens) else None
            if next_tok and next_tok.type == 'LPAREN':
                stmt = self.function_call()
            elif next_tok and next_tok.type == 'OP' and next_tok.value in ('++', '--'):
                # form: id ++ ;  (we consume ID and OP)
                self.advance()  # ID
                op_tok = self.peek()
                self.advance()  # OP
                stmt = KozakUnaryOp(op_tok.value, KozakVariable(tok.value))
            else:
                stmt = self.assignment()

        # --- Echo ---
        elif tok.type == 'Spivaty':
            stmt = self.echo()

        # --- If / While / For / Function Def (block statements no trailing semicolon) ---
        elif tok.type == 'Yakscho':
            return self.if_statement()
        elif tok.type == 'Doki':
            return self.while_statement()
        elif tok.type == 'Dlya':
            return self.for_statement()
        elif tok.type == 'Zavdannya':
            return self.function_def()

        # --- Return ---
        elif tok.type == 'Povernuty':
            stmt = self.return_statement()

        # --- Expression ---
        elif tok.type in ('LPAREN', 'NUMBER', 'STRING', 'Pravda', 'Nepravda', 'Slukhai', 'Chyslo', 'Ryadok', 'Logika', 'DroboveChyslo'):
            stmt = self.or_expression()

        else:
            return self.error(tok, f"Unexpected token {tok.type} ({tok.value!r}) at line {tok.line}, column {tok.column}")

        # If statement is a simple statement (not block), require semicolon
        # NOTE: KozakReturn is NOT in the exemption list → semicolon is required after return.
        if stmt and require_semicolon and not isinstance(stmt, (KozakIf, KozakWhile, KozakFor, KozakFunctionDef)):
            semi = self.peek()
            if not semi or semi.type != 'SEMICOLON':
                return self.error(tok, f"Missing ';' after statement at line {tok.line}, column {tok.column}")
            # consume semicolon
            self.advance()
        return stmt

    # ---------- Assign / Echo ----------
    def assignment(self):
        name_token = self.expect('ID')
        if name_token is None:
            return None
        name = name_token.value

        op = self.expect('OP')
        if op is None:
            return None
        if op.value != ':=':
            return self.error(op, f"Expected ':=', got {op.value}")

        expr = self.or_expression()
        if expr is None:
            return None
        return KozakAssign(name, expr)

    def echo(self):
        if self.expect('Spivaty') is None:
            return None
        if self.expect('LPAREN') is None:
            return None
        expressions = []
        if self.peek() and self.peek().type != 'RPAREN':
            expr = self.or_expression()
            if expr is None:
                return None
            expressions.append(expr)
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                if self.peek() and self.peek().type == 'RPAREN':
                    return self.error(self.peek(), "Function arguments cannot have a trailing comma, kozache.")
                expr = self.or_expression()
                if expr is None:
                    return None
                expressions.append(expr)
        if self.expect('RPAREN') is None:
            return None
        return KozakEcho(expressions)

    # ---------- Expressions ----------
    def or_expression(self):
        left = self.and_expression()
        if left is None:
            return None
        while self.peek() and self.peek().value == '||':
            op = self.expect('OP')
            if op is None:
                return None
            right = self.and_expression()
            if right is None:
                return None
            left = KozakBinOp(left, op.value, right)
        return left

    def and_expression(self):
        left = self.comparison()
        if left is None:
            return None
        while self.peek() and self.peek().value == '&&':
            op = self.expect('OP')
            if op is None:
                return None
            right = self.comparison()
            if right is None:
                return None
            left = KozakBinOp(left, op.value, right)
        return left

    def comparison(self):
        left = self.expression()
        if left is None:
            return None
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('==', '!=', '<', '>', '<=', '>='):
            op = self.expect('OP')
            if op is None:
                return None
            right = self.expression()
            if right is None:
                return None
            left = KozakComparisonOp(left, op.value, right)
        return left

    def expression(self):
        left = self.term()
        if left is None:
            return None
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('+', '-'):
            op = self.expect('OP')
            if op is None:
                return None
            right = self.term()
            if right is None:
                return None
            left = KozakBinOp(left, op.value, right)
        return left

    def term(self):
        left = self.exponent()
        if left is None:
            return None
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*', '/'):
            op = self.expect('OP')
            if op is None:
                return None
            right = self.exponent()
            if right is None:
                return None
            left = KozakBinOp(left, op.value, right)
        return left

    def exponent(self):
        left = self.factor()
        if left is None:
            return None
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('^', '^/'):
            op = self.expect('OP')
            if op is None:
                return None
            right = self.factor()
            if right is None:
                return None
            left = KozakBinOp(left, op.value, right)
        return left

    def factor(self):
        tok = self.peek()
        if not tok:
            return self.error(None, "Unexpected end of input in factor")

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
            # guard index access in tokens list
            next_tok = self.tokens[self.current_token_index + 1] if self.current_token_index + 1 < len(self.tokens) else None
            if next_tok and next_tok.type == 'LPAREN':
                return self.function_call()
            else:
                self.advance()
                return KozakVariable(tok.value)
        elif tok.type == 'LPAREN':
            self.advance()
            expr = self.or_expression()
            if expr is None:
                return None
            if self.expect('RPAREN') is None:
                return None
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
            return self.error(tok, f"Unexpected token in factor: {tok}")

    def input_expression(self):
        if self.expect('Slukhai') is None:
            return None
        if self.expect('LPAREN') is None:
            return None
        prompt_expr = self.or_expression()
        if prompt_expr is None:
            return None
        if self.expect('RPAREN') is None:
            return None
        return KozakInput(prompt_expr)

    def type_cast(self):
        # expect current token type (Chyslo / Ryadok / ...) then LPAREN expr RPAREN
        tok = self.peek()
        if not tok:
            return self.error(None, "Unexpected end in type cast")
        tok_consumed = self.expect(tok.type)
        if tok_consumed is None:
            return None
        if self.expect('LPAREN') is None:
            return None
        expr = self.or_expression()
        if expr is None:
            return None
        if self.expect('RPAREN') is None:
            return None
        return KozakTypeCast(tok_consumed.type, expr)

    # ---------- Control flow structures ----------
    def if_statement(self):
        if self.expect('Yakscho') is None:
            return None
        if self.expect('LPAREN') is None:
            return None
        condition = self.or_expression()
        if condition is None:
            return None
        if self.expect('RPAREN') is None:
            return None
        if self.expect('LBRACE') is None:
            return None
        body = self.block()
        if body is None:
            return None

        else_if_parts = []
        while self.peek() and self.peek().type == 'AboYakscho':
            if self.expect('AboYakscho') is None:
                return None
            if self.expect('LPAREN') is None:
                return None
            else_if_condition = self.or_expression()
            if else_if_condition is None:
                return None
            if self.expect('RPAREN') is None:
                return None
            if self.expect('LBRACE') is None:
                return None
            elif_body = self.block()
            if elif_body is None:
                return None
            else_if_parts.append((else_if_condition, elif_body))

        else_part = None
        if self.peek() and self.peek().type == 'Inakshe':
            if self.expect('Inakshe') is None:
                return None
            if self.expect('LBRACE') is None:
                return None
            else_part = self.block()
            if else_part is None:
                return None

        return KozakIf(condition, body, else_if_parts, else_part)

    def while_statement(self):
        if self.expect('Doki') is None:
            return None
        if self.expect('LPAREN') is None:
            return None
        condition = self.or_expression()
        if condition is None:
            return None
        if self.expect('RPAREN') is None:
            return None
        if self.expect('LBRACE') is None:
            return None
        body = self.block()
        if body is None:
            return None
        return KozakWhile(condition, body)

    def for_statement(self):
        if self.expect('Dlya') is None:
            return None
        if self.expect('LPAREN') is None:
            return None
        initialization = self.assignment()
        if initialization is None:
            return None
        if self.expect('SEMICOLON') is None:
            return None
        condition = self.or_expression()
        if condition is None:
            return None
        if self.expect('SEMICOLON') is None:
            return None
        step = self.parse_for_increment()
        if step is None:
            return None
        if self.expect('RPAREN') is None:
            return None
        if self.expect('LBRACE') is None:
            return None
        body = self.block()
        if body is None:
            return None
        return KozakFor(initialization, condition, step, body)

    def function_def(self):
        if self.expect('Zavdannya') is None:
            return None
        name_tok = self.expect('ID')
        if name_tok is None:
            return None
        name = name_tok.value
        if self.expect('LPAREN') is None:
            return None

        parameters = []
        if self.peek() and self.peek().type != 'RPAREN':
            param_tok = self.expect('ID')
            if param_tok is None:
                return None
            parameters.append(param_tok.value)
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                param_tok = self.expect('ID')
                if param_tok is None:
                    return None
                parameters.append(param_tok.value)
        if self.expect('RPAREN') is None:
            return None
        if self.expect('LBRACE') is None:
            return None
        body = self.block()
        if body is None:
            return None
        return KozakFunctionDef(name, parameters, body)

    def function_call(self):
        name_tok = self.expect('ID')
        if name_tok is None:
            return None
        name = name_tok.value
        if self.expect('LPAREN') is None:
            return None
        arguments = []
        if self.peek() and self.peek().type != 'RPAREN':
            arg = self.or_expression()
            if arg is None:
                return None
            arguments.append(arg)
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                if self.peek() and self.peek().type == 'RPAREN':
                    return self.error(self.peek(), "Function arguments cannot have a trailing comma, kozache.")
                arg = self.or_expression()
                if arg is None:
                    return None
                arguments.append(arg)
        if self.expect('RPAREN') is None:
            return None
        return KozakFunctionCall(name, arguments)

    def return_statement(self):
        if self.expect('Povernuty') is None:
            return None
        value = self.or_expression()
        if value is None:
            return None
        # semicolon is required by the caller (statement()), so don't consume it here
        return KozakReturn(value)

    def block(self):
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            stmt = self.statement()
            if stmt:
                body.append(stmt)
            else:
                # if we failed to parse a statement and hit RBRACE, break, else return None to indicate failure
                if self.peek() and self.peek().type == 'RBRACE':
                    break
                return None
        if self.expect('RBRACE') is None:
            return None
        return body

    def parse_for_increment(self):
        tok = self.peek()
        next_tok = self.tokens[self.current_token_index + 1] if self.current_token_index + 1 < len(self.tokens) else None

        # Unary increment/decrement
        if tok and tok.type == 'ID' and next_tok and next_tok.type == 'OP' and next_tok.value in ('++', '--'):
            self.advance()  # consume ID
            op_tok = self.expect('OP')
            if op_tok is None:
                return None
            return KozakUnaryOp(op_tok.value, KozakVariable(tok.value))

        # Assignment (:=)
        elif tok and tok.type == 'ID' and next_tok and next_tok.type == 'OP' and next_tok.value == ':=':
            return self.assignment()

        # Any other expression
        else:
            return self.or_expression()
