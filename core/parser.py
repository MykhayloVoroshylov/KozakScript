"""Parser for KozakScript"""

import traceback

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
    KozakForEach,
    KozakClass,
    KozakNewInstance,
    KozakPropertyAccess,
    KozakPropertyAssign,
    KozakDictionary,
    KozakDictionaryAccess,
    KozakTry,
    KozakThrow,
    KozakExit,
    KozakImport
)

from core.lexer import Token

class Parser:
    DIALECT_STARTERS = {
        'Hetman': 'ukrainian',
        'Chief': 'english',
        'Ataman': 'russian',
        '>>>': 'symbolic'
    }

    SHARED_SLAVIC = {
        'Dlya',
        'Pravda',
        'Nepravda',
        'Logika',
        'klyuchi',
        'novyy'
    }

    DIALECT_KEYWORDS = {
        'ukrainian': {
            'Hetman', 'Spivaty', 'Slukhai', 'Povernuty', 'Zavdannya', 'Doki',
            'Chyslo', 'DroboveChyslo', 'Ryadok', 
            'Yakscho', 'Abo_Yakscho', 'Inakshe', 'dovzhyna', 'kozhen', 'Klas', 'Tvir',
            'tsey', 'Sprobuy', 'Piymat', 'Vkintsi', 'Kydaty', 'Vykhid', 'Importuvaty',
            'znachennya', 'maye_klyuch', 'vydalyty_klyuch',
            'dodaty', 'vstavyty', 'vydalyty', 'vyinyaty', 'ochystyty', 'vyrizaty',
            'mistyt', 'index_z', 'Zapysaty', 'Chytaty', 'stvoryty_matrytsyu', 'rozmir_matrytsi', 'splushchyty', 'transportuvaty',
            'otrymaty_ryadok', 'otrymaty_stovpets', 'vstanovyty_na', 'Vidkrytyy', 'Zakrytyy', 'Zakhyshchenyy'
        },
        'english': {
            'Chief', 'Print', 'Input', 'Return', 'Function', 'For', 'While',
            'True', 'False', 'Int', 'Float', 'Str', 'Bool',
            'If', 'Else_If', 'Else', 'Length', 'each', 'Class', 'Constructor',
            'new', 'this', 'Try', 'Catch', 'Finally', 'Throw', 'Exit', 'Import',
            'keys', 'values', 'has_key', 'remove_key',
            'append', 'insert', 'remove', 'pop', 'clear', 'slice',
            'contains', 'index_of', 'Write', 'Read', 'create_matrix', 'matrix_size', 'flatten', 'transpose',
            'get_row', 'get_col', 'set_at', 'Public', 'Private', 'Protected'
        },
        'russian': {
            'Ataman', 'Pechatat', 'Vvod', 'Vernut', 'Zadanie', 'Poka',
            'Chislo', 'DrobnoyeChislo', 'Stroka', 
            'Yesli', 'Ili_Yesli', 'Inache', 'dlinna', 'kazhdy', 'Klass', 'Tvorenye',
            'etot', 'Poprobuy', 'Poymat', 'Nakonets', 'Brosat', 'Vykhod', 'Importirovat',
            'znachennie', 'imeet_klyuch', 'udalit_klyuch',
            'dobavit', 'vstavit', 'udalit', 'vytaschit', 'ochistit', 'vyrezat',
            'soderzhit', 'index_znachenia', 'Zapisat', 'Chitat','sozdat_matritsu', 'razmer_matritsy', 'spluschit', 'transportirovat',
            'poluchit_stroku', 'poluchit_stolbets', 'ustanovit_na', 'Otkrytyy', 'Zakrytyy', 'Zashchishchennyy'
        },
        'symbolic': {
            '>>>', '!', '?', '<!', '$', '~~', '~`',
            '1!', '0!', 'i`**', 'f`**', 's`**', 'b`**',
            '??', '?!', '!!', '___', '::', '@', '@=',
            '+@', '->', '<<', '>>', '<>', '!!>', '<<<', '#',
            r'k{}', r'v{}', '?k', '-k',
            '+<', '+:', '-<', '-<!', '--<', '[..]',
            '?^', '?:', '=>', '=<', '@[]', '#[]', '[]>', '[]^', '[]->', '[]|', '[]:=', '++>', '-->', '##>'
        }
    }

    def __init__(self, tokens, strict_dialect=False):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = []
        self.strict_dialect = strict_dialect
        self.detected_dialect = None
        self.dialect_violations = []

    def error(self, token, message):
        if token:
            self.errors.append(f"Error at line {token.line}, col {token.column}: {message}")
        else:
            self.errors.append(f"Error at unknown location: {message}")
        self.synchronize()
        return None
    
    def check_dialect(self, token):
        """Check and enforce dialect consistency"""
        if not self.strict_dialect:
            return
        
        if token.value in self.SHARED_SLAVIC:
            if self.detected_dialect is None:
                return
            
            if self.detected_dialect in ('ukrainian', 'russian'):
                return
            else:
                violation = (
                    f"Dialect mixing at line {token.line}, col {token.column}: "
                    f"Using Slavic keyword '{token.value}' in {self.detected_dialect} program"
                )
                self.dialect_violations.append(violation)
                self.errors.append(violation)
                return
        
        # Determine which dialect this token belongs to
        token_dialect = None
        for dialect, keywords in self.DIALECT_KEYWORDS.items():
            if token.value in keywords:
                token_dialect = dialect
                break
        
        # Skip tokens that aren't dialect-specific (like numbers, strings, operators)
        if token_dialect is None:
            return
        
        # First dialect-specific token sets the dialect
        if self.detected_dialect is None:
            self.detected_dialect = token_dialect
            return
        
        # Check for dialect mixing
        if self.detected_dialect != token_dialect:
            violation = (
                f"Dialect mixing at line {token.line}, col {token.column}: "
                f"Using {token_dialect} keyword '{token.value}' in {self.detected_dialect} program"
            )
            self.dialect_violations.append(violation)
            self.errors.append(violation)
    
    def synchronize(self):
        """Skip tokens until we find a good recovery point"""
        # Just advance past the problematic token
        if not self.is_at_end():
            self.advance()
        
        # Keep advancing until we hit a statement boundary
        while not self.is_at_end():
            tok = self.peek()
            if not tok:
                return
            
            # Stop at these "safe" tokens that start new statements
            if tok.type in ('Zavdannya', 'Yakscho', 'Doki', 'Dlya', 'Klas', 'RBRACE', 'SEMICOLON'):
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
        stack = traceback.extract_stack()
        caller_info = stack[-2]
        
        if token:
            error_msg = (
            f"Expected {expected_type}, got {token.type} ('{token.value}') "
            f"at line {token.line}, column {token.column}\n"
            f"  Called from: {caller_info.filename}:{caller_info.lineno} "
            f"in {caller_info.name}()"
        )
            #print(f"DEBUG: {error_msg}")
            return self.error(token, error_msg)
        else:
            error_msg = (
            f"Expected {expected_type}, but found end of file.\n"
            f"  Called from: {caller_info.filename}:{caller_info.lineno} "
            f"in {caller_info.name}()"
            )

            return self.error(token, error_msg)

    def parse(self):
        first_token = self.peek()

        if not (first_token and first_token.type == 'Hetman'):
            raise SyntaxError("Be respectful to Hetman: you should always declare him at the start! (line 1, column 1)")
        

        if self.strict_dialect:
            starter_value = first_token.value
            if starter_value in self.DIALECT_STARTERS:
                self.detected_dialect = self.DIALECT_STARTERS[starter_value]

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
        
        if tok.type in ('Yakscho', 'Doki', 'Dlya', 'Zavdannya', 'Sprobuy', 
                     'Kydaty', 'Vykhid', 'Importuvaty', 'Spivaty', 'Klas', 'Povernuty'):
            self.check_dialect(tok)
        
        if tok.type in ('Chyslo', 'Ryadok', 'Logika', 'DroboveChyslo'):
            type_hint = tok.value
            self.advance()
            var_name = self.expect('ID').value
            self.expect('OP')
            expr = self.or_expression()
            return KozakAssign(var_name, expr, type_hint)

        if tok.type == 'Yakscho':
            return self.if_statement()
        elif tok.type == 'Doki':
            return self.while_statement()
        elif tok.type == 'Dlya':
            next_tok = self.peek_ahead(1)
            next_next_tok = self.peek_ahead(2)
            
            if next_tok and next_tok.type == 'ID' and next_next_tok and next_next_tok.type == 'KOZHEN':
                return self.for_each_statement()
            else:
                return self.for_statement()

        elif tok.type == 'Zavdannya':
            return self.function_def()
        
        result = None

        if tok.type == 'Sprobuy':
            return self.try_statement()
        elif tok.type == 'Kydaty':
            return self.throw_statement()
        
        if tok.type == 'Vykhid':
            return self.exit_statement()
        
        if tok.type == 'Importuvaty':
            return self.import_statement()

        if tok.type in ('ID', 'THIS'):
            expr = self.factor()
            next_tok = self.peek()#self.tokens[self.current_token_index + 1] if self.current_token_index + 1 < len(self.tokens) else None
            
            if next_tok and next_tok.type == 'OP' and next_tok.value == ':=':
                result = self.assignment_from_target(expr)
                if result is None:
                    return None
            elif next_tok and next_tok.type == 'OP' and next_tok.value in('++', '--'):
                if not isinstance(expr, KozakVariable):
                    return self.error(tok, f"Increment/decrement only works on simple variables, not on indexed or property access")
                self.advance()
                result = KozakUnaryOp(next_tok.value, expr)
            elif isinstance(expr, KozakFunctionCall):
                result = expr
            else:
                return self.error(tok, f"Unexpected expression in statement context at line {tok.line}, column {tok.column}")                
            
        elif tok.type == 'Spivaty':
            result = self.echo()
        elif tok.type == 'Povernuty':
            return self.return_statement()
        elif tok.type == 'Klas':
            return self.class_def()
        else:
            return self.error(tok, f"Unexpected token in statement: '{tok.value}' at line {tok.line}, column {tok.column}")
        
        
        if result and require_semicolon and not isinstance(result, (KozakIf, KozakWhile, KozakFor, KozakFunctionDef)):
            self.expect('SEMICOLON')
            
        return result
    
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

    def expression_or_call(self):
        """
        Handles array indexing, property access, and function calls.
        e.g., myVar[i], myObject.property, myFunction(a, b)
        """
        expr = self.primary_expression()
        if expr is None:
            return None

        while True:
            # Handle property access (DOT operator)
            if self.peek() and self.peek().type == 'DOT':
                self.advance() # Consume the DOT
                property_token = self.expect('ID')
                if property_token is None:
                    return None # Error handled in expect

                expr = KozakPropertyAccess(
                    instance=expr,
                    property_name=property_token.value
                )

            # Handle array indexing
            elif self.peek() and self.peek().type == 'LBRACKET':
                self.advance()
                index_expr = self.or_expression()
                self.expect('RBRACKET')
                expr = KozakArrayIndex(expr, index_expr)

            # Handle function call
            elif self.peek() and self.peek().type == 'LPAREN':
                if isinstance(expr, KozakVariable):
                    self.advance() # Consume LPAREN
                    arguments = self.argument_list()
                    self.expect('RPAREN')
                    expr = KozakFunctionCall(expr.name, arguments)
                else:
                    break
            else:
                break
            return expr

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

        if tok.type == 'OP' and tok.value == '-':
            self.advance()
            operand = self.factor()  # Recursively parse the operand
            return KozakBinOp(KozakNumber(0), '-', operand)  # Convert -x to 0 - x
    
    # Handle unary plus (just ignore it)
        if tok.type == 'OP' and tok.value == '+':
            self.advance()
            return self.factor()


        if tok.type == 'NUMBER':
            self.advance()
            return KozakNumber(tok.value)
        elif tok.type == 'Pravda':
            self.advance()
            return KozakBoolean(True)
        elif tok.type == 'Nepravda':
            self.advance()
            return KozakBoolean(False)
        elif tok.type == 'NEW':
            self.advance()
            class_name = self.expect('ID').value
            if not class_name:
                return None  # Error already recorded by expect()
            args = self.function_call_arguments()
            return KozakNewInstance(class_name, args)

        elif tok.type in ('ID', 'Dovzhyna', 'THIS'):
            self.check_dialect(tok)
            if tok.type == 'THIS':
                name = 'this'
            else: 
                name = tok.value
            self.advance()

            if self.peek() and self.peek().type == 'LPAREN':
                arguments = self.function_call_arguments()
                node = KozakFunctionCall(name, arguments)
            else:
                node = KozakVariable(name)    
                #return node

            
            while self.peek() and self.peek().type == 'LBRACKET':
                self.advance()
                index_expr = self.or_expression()
                self.expect('RBRACKET')
                node = KozakDictionaryAccess(node, index_expr)
            while self.peek() and self.peek().type == 'DOT':
                self.advance()
                prop_name = self.expect('ID').value
                node = KozakPropertyAccess(node, prop_name)
                
                # Check if this property access is followed by a method call
                if self.peek() and self.peek().type == 'LPAREN':
                    arguments = self.function_call_arguments()
                    # Convert property access to method call
                    if isinstance(node, KozakPropertyAccess) and isinstance(node.instance, KozakVariable):
                        node = KozakFunctionCall(f"{node.instance.name}.{node.property_name}", arguments)
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
        
        elif tok.type == 'LBRACE':
        # Check if this is a dictionary or a block
        # Look ahead to see if we have key:value syntax
            next_tok = self.peek_ahead(1)
            if next_tok and (next_tok.type in ('STRING', 'ID', 'NUMBER') or 
                            (self.peek_ahead(2) and self.peek_ahead(2).type == 'COLON')):
                return self.parse_dictionary()
            else:
                return self.error(tok, "Unexpected '{' in expression")

            
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
        self.expect_with_dialect_check('Slukhai')
        self.expect('LPAREN')
        prompt_expr = self.or_expression()
        self.expect('RPAREN')
        return KozakInput(prompt_expr)
    
    def type_cast(self):
        tok = self.expect(self.peek().type)
        self.check_dialect(tok)
        self.expect('LPAREN')
        expr = self.or_expression()
        self.expect('RPAREN')
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
        var_name = self.expect('ID').value
        if not var_name:
            return None
        op = self.expect('OP')
        if not op or op.value != ':=':
            return self.error(op, f"Expected ':=' in for loop initialization")
        init_expr = self.or_expression()
        initialization = KozakAssign(var_name, init_expr)
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
        self.expect('KOZHEN')
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
        return self.current_token_index >= len(self.tokens)
    
    def previous(self):
        if self.current_token_index > 0:
            return self.tokens[self.current_token_index - 1]
        return None
    
    def class_def(self):
        self.expect('Klas')
        class_name_token = self.expect('ID')
        if not class_name_token:
            return None  # Error already recorded by expect()
        
        class_name = class_name_token.value
        parent_name = None

        if self.peek() and self.peek().type == 'COLON':
            self.advance()
            parent_token = self.expect('ID')
            if not parent_token:
                return None
            parent_name = parent_token.value

        self.expect('LBRACE')

        methods = {}
        constructor = None
        method_access = {}
        field_access = {}

        while self.peek() and self.peek().type != 'RBRACE':
            # Constructors are written as Tvir(...)
            access_modifier = 'public'
            if self.peek().type in ('PUBLIC', 'PRIVATE', 'PROTECTED'):
                access_modifier = self.peek().type.lower()
                self.advance()

            if self.peek().type == 'Tvir':
                self.advance()
                self.expect('LPAREN')
                params = []
                if self.peek().type != 'RPAREN':
                    params.append(self.expect('ID').value)
                    while self.peek().type == 'COMMA':
                        self.advance()
                        params.append(self.expect('ID').value)
                self.expect('RPAREN')
                self.expect('LBRACE')
                body = self.block()
                constructor = KozakFunctionDef('Tvir', params, body)
                methods['Tvir'] = constructor

            elif self.peek().type == 'Zavdannya':
                # Regular method
                method = self.function_def_with_access(access_modifier)
                methods[method.name] = method
                method_access[method.name] = access_modifier
            
            elif self.peek().type in ('Chyslo', 'Ryadok', 'Logika', 'DroboveChyslo'):
                type_hint = self.peek().type
                self.advance()
                field_name = self.expect('ID').value
                field_access[field_name] = access_modifier
                self.expect('SEMICOLON')

            else:
                tok = self.peek()
                self.errors.append(f"Error at line {tok.line}, col {tok.column}: Unexpected token in class body: '{tok.value}'")
                self.advance()

        self.expect('RBRACE')
        return KozakClass(
        name=class_name, 
        methods=methods, 
        constructor=constructor, 
        parent_name=parent_name,
        field_access=field_access,
        method_access=method_access
        )
    
    def function_def_with_access(self, access_modifier='public'):
        """Parse function definition with access modifier already consumed"""
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
        return KozakFunctionDef(name, parameters, body, access_modifier=access_modifier)


    
    def assignment_from_target(self, target):
        """Handle assignment when we've already parsed the left-hand side"""
        op = self.expect('OP')
        if not op:
            return None
        if op.value != ':=':
            return self.error(op, f"Expected ':=', got {op.value}")

        expr = self.or_expression()

        if isinstance(target, KozakPropertyAccess):
            return KozakPropertyAssign(target.instance, target.property_name, expr)
        elif isinstance(target, KozakDictionaryAccess):  # ADD THIS
            # For dict[key] := value, we need special handling
            # We'll create a special assignment node
            return KozakPropertyAssign(target.dictionary, target.key, expr)
        elif isinstance(target, KozakVariable):
            return KozakAssign(target.name, expr)
    
    def parse_dictionary(self):
        self.expect('LBRACE')
        pairs = []
        
        if self.peek() and self.peek().type != 'RBRACE':
            # Parse first key:value pair
            key = self.or_expression()
            self.expect('COLON')
            value = self.or_expression()
            pairs.append((key, value))
            
            # Parse remaining pairs
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                if self.peek() and self.peek().type == 'RBRACE':
                    break  # Trailing comma
                key = self.or_expression()
                self.expect('COLON')
                value = self.or_expression()
                pairs.append((key, value))
        
        self.expect('RBRACE')
        return KozakDictionary(pairs)
    
    def try_statement(self):
        self.expect('Sprobuy')
        self.expect('LBRACE')
        try_body = self.block()

        catch_clauses = []

        while self.peek() and self.peek().type == 'Piymat':
            self.advance()
            self.expect('LPAREN')

            exception_var = None
            if self.peek() and self.peek().type == 'ID':
                exception_var = self.expect('ID').value
            
            self.expect('RPAREN')
            self.expect('LBRACE')
            catch_body = self.block()

            catch_clauses.append((exception_var, catch_body))

        finally_body = None
        if self.peek() and self.peek().type == 'Vkintsi':
            self.advance()
            self.expect('LBRACE')
            finally_body = self.block()

        return KozakTry(try_body, catch_clauses, finally_body)
    
    def throw_statement(self):
        self.expect('Kydaty')
        self.expect('LPAREN')
        message = self.or_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return KozakThrow(message)
    
    def exit_statement(self):
        self.expect('Vykhid')

        code = None
        if self.peek() and self.peek().type == 'LPAREN':
            self.expect('LPAREN')
            code = self.or_expression()
            self.expect('RPAREN')
        
        self.expect('SEMICOLON')
        return KozakExit(code)
    
    def import_statement(self):
        self.expect('Importuvaty')
        self.expect('LPAREN')
        file_path_expr = self.or_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return KozakImport(file_path_expr)
    
    def expect_with_dialect_check(self, expected_type):
        tok = self.peek()
        if tok and tok.type == expected_type:
            self.check_dialect(tok)
        return self.expect(expected_type)