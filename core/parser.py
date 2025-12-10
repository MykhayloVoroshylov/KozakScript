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
    KozakImport,
    KozakSuper,
    KozakDestructor
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
            'otrymaty_ryadok', 'otrymaty_stovpets', 'vstanovyty_na', 'Vidkrytyy', 'Zakrytyy', 'Zakhyshchenyy', 'Batko', 'Druh',
            'Znyshchyty'
        },
        'english': {
            'Chief', 'Print', 'Input', 'Return', 'Function', 'For', 'While',
            'True', 'False', 'Int', 'Float', 'Str', 'Bool',
            'If', 'Else_If', 'Else', 'Length', 'each', 'Class', 'Constructor',
            'new', 'this', 'Try', 'Catch', 'Finally', 'Throw', 'Exit', 'Import',
            'keys', 'values', 'has_key', 'remove_key',
            'append', 'insert', 'remove', 'pop', 'clear', 'slice',
            'contains', 'index_of', 'Write', 'Read', 'create_matrix', 'matrix_size', 'flatten', 'transpose',
            'get_row', 'get_col', 'set_at', 'Public', 'Private', 'Protected', 'Super', 'Friend', 'Destroy'
        },
        'russian': {
            'Ataman', 'Pechatat', 'Vvod', 'Vernut', 'Zadanie', 'Poka',
            'Chislo', 'DrobnoyeChislo', 'Stroka', 
            'Yesli', 'Ili_Yesli', 'Inache', 'dlinna', 'kazhdy', 'Klass', 'Tvorenye',
            'etot', 'Poprobuy', 'Poymat', 'Nakonets', 'Brosat', 'Vykhod', 'Importirovat',
            'znachennie', 'imeet_klyuch', 'udalit_klyuch',
            'dobavit', 'vstavit', 'udalit', 'vytaschit', 'ochistit', 'vyrezat',
            'soderzhit', 'index_znachenia', 'Zapisat', 'Chitat','sozdat_matritsu', 'razmer_matritsy', 'spluschit', 'transportirovat',
            'poluchit_stroku', 'poluchit_stolbets', 'ustanovit_na', 'Otkrytyy', 'Zakrytyy', 'Zashchishchennyy', 'Roditel', 'Drug',
            'Unichtozhit'
        },
        'symbolic': {
            '>>>', '!', '?', '<!', '$', '~~', '~`',
            '1!', '0!', 'i`**', 'f`**', 's`**', 'b`**',
            '??', '?!', '!!', '___', '::', '@', '@=',
            '+@', '->', '<<', '>>', '<>', '!!>', '<<<', '#',
            r'k{}', r'v{}', '?k', '-k',
            '+<', '+:', '-<', '-<!', '--<', '[..]',
            '?^', '?:', '=>', '=<', '@[]', '#[]', '[]>', '[]^', '[]->', '[]|', '[]:=', '++>', '-->', '##>', '^>', '<->', '@~'
        }
    }

    KEYWORD_TRANSLATIONS = {
        # Structure keywords
        'Hetman': {'ukrainian': 'Hetman', 'english': 'Chief', 'russian': 'Ataman', 'symbolic': '>>>'},
        'Spivaty': {'ukrainian': 'Spivaty', 'english': 'Print', 'russian': 'Pechatat', 'symbolic': '!'},
        'Slukhai': {'ukrainian': 'Slukhai', 'english': 'Input', 'russian': 'Vvod', 'symbolic': '?'},
        'Povernuty': {'ukrainian': 'Povernuty', 'english': 'Return', 'russian': 'Vernut', 'symbolic': '<!'},
        'Zavdannya': {'ukrainian': 'Zavdannya', 'english': 'Function', 'russian': 'Zadanie', 'symbolic': '$'},
        'Doki': {'ukrainian': 'Doki', 'english': 'While', 'russian': 'Poka', 'symbolic': '~`'},
        
        # Types
        'Chyslo': {'ukrainian': 'Chyslo', 'english': 'Int', 'russian': 'Chislo', 'symbolic': 'i`**'},
        'DroboveChyslo': {'ukrainian': 'DroboveChyslo', 'english': 'Float', 'russian': 'DrobnoyeChislo', 'symbolic': 'f`**'},
        'Ryadok': {'ukrainian': 'Ryadok', 'english': 'Str', 'russian': 'Stroka', 'symbolic': 's`**'},
        'Logika': {'ukrainian': 'Logika', 'english': 'Bool', 'russian': 'Logika', 'symbolic': 'b`**'},
        
        # Control flow
        'Yakscho': {'ukrainian': 'Yakscho', 'english': 'If', 'russian': 'Yesli', 'symbolic': '??'},
        'AboYakscho': {'ukrainian': 'Abo_Yakscho', 'english': 'Else_If', 'russian': 'Ili_Yesli', 'symbolic': '?!'},
        'Inakshe': {'ukrainian': 'Inakshe', 'english': 'Else', 'russian': 'Inache', 'symbolic': '!!'},
        
        # OOP
        'Klas': {'ukrainian': 'Klas', 'english': 'Class', 'russian': 'Klass', 'symbolic': '@'},
        'Tvir': {'ukrainian': 'Tvir', 'english': 'Constructor', 'russian': 'Tvorenye', 'symbolic': '@='},
        'NEW': {'ukrainian': 'novyy', 'english': 'new', 'russian': 'novyy', 'symbolic': '+@'},
        'THIS': {'ukrainian': 'tsey', 'english': 'this', 'russian': 'etot', 'symbolic': '->'},
        'SUPER': {'ukrainian': 'Batko', 'english': 'Super', 'russian': 'Roditel', 'symbolic': '^>'},
        'Destructor': {'ukrainian': 'Znyshchyty', 'english': 'Destructor', 'russian': 'Unichtozhit', 'symbolic': '@~'},

        # Access modifiers
        'PUBLIC': {'ukrainian': 'Vidkrytyy', 'english': 'Public', 'russian': 'Otkrytyy', 'symbolic': '++>'},
        'PRIVATE': {'ukrainian': 'Zakrytyy', 'english': 'Private', 'russian': 'Zakrytyy', 'symbolic': '-->'},
        'PROTECTED': {'ukrainian': 'Zakhyshchenyy', 'english': 'Protected', 'russian': 'Zashchishchennyy', 'symbolic': '##>'},
        'FRIEND': {'ukrainian': 'Druh', 'english': 'Friend', 'russian': 'Drug', 'symbolic': '<->'},
        
        # Exception handling
        'Sprobuy': {'ukrainian': 'Sprobuy', 'english': 'Try', 'russian': 'Poprobuy', 'symbolic': '<<'},
        'Piymat': {'ukrainian': 'Piymat', 'english': 'Catch', 'russian': 'Poymat', 'symbolic': '>>'},
        'Vkintsi': {'ukrainian': 'Vkintsi', 'english': 'Finally', 'russian': 'Nakonets', 'symbolic': '<>'},
        'Kydaty': {'ukrainian': 'Kydaty', 'english': 'Throw', 'russian': 'Brosat', 'symbolic': '!!>'},
        
        # Other
        'Vykhid': {'ukrainian': 'Vykhid', 'english': 'Exit', 'russian': 'Vykhod', 'symbolic': '<<<'},
        'Importuvaty': {'ukrainian': 'Importuvaty', 'english': 'Import', 'russian': 'Importirovat', 'symbolic': '#'},
        'KOZHEN': {'ukrainian': 'kozhen', 'english': 'each', 'russian': 'kazhdy', 'symbolic': '::'},
        'Dovzhyna': {'ukrainian': 'dovzhyna', 'english': 'length', 'russian': 'dlinna', 'symbolic': '___'},
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
    
    def get_keyword_translation(self, token_value, target_dialect):
        """Get the correct keyword for the target dialect"""
        for key, translations in self.KEYWORD_TRANSLATIONS.items():
            if token_value in translations.values():
                return translations.get(target_dialect, token_value)
        return None

    
    def check_dialect(self, token):
        """Check and enforce dialect consistency with helpful hints"""
        if not self.strict_dialect:
            return
        
        if token.value in self.SHARED_SLAVIC:
            if self.detected_dialect is None:
                return
            
            if self.detected_dialect in ('ukrainian', 'russian'):
                return
            else:
                correct_keyword = self.get_keyword_translation(token.value, self.detected_dialect)
                hint = ""
                if correct_keyword:
                    hint = f"\n     Hint: Replace '{token.value}' with '{correct_keyword}'"
                
                violation = (
                    f"  ⚠ Line {token.line}, col {token.column}: "
                    f"Using Slavic keyword '{token.value}' in {self.detected_dialect} program{hint}"
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
        
        # Skip tokens that aren't dialect-specific
        if token_dialect is None:
            return
        
        # First dialect-specific token sets the dialect
        if self.detected_dialect is None:
            self.detected_dialect = token_dialect
            return
        
        # Check for dialect mixing
        if self.detected_dialect != token_dialect:
            correct_keyword = self.get_keyword_translation(token.value, self.detected_dialect)
            hint = ""
            if correct_keyword:
                hint = f"\n     Hint: Replace '{token.value}' with '{correct_keyword}'"
            
            violation = (
                f"  ⚠ Line {token.line}, col {token.column}: "
                f"Using {token_dialect} keyword '{token.value}' in {self.detected_dialect} program{hint}"
            )
            self.dialect_violations.append(violation)
            self.errors.append(violation)

    
    def synchronize(self):
        """Skip tokens until we find a good recovery point"""
        if not self.is_at_end():
            self.advance()
        
        while not self.is_at_end():
            tok = self.peek()
            if not tok:
                return
            
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
            self.check_dialect(tok)
            type_hint = tok.value
            self.advance()
            var_name = self.expect('ID').value
            self.expect('OP')
            expr = self.or_expression()
            return KozakAssign(var_name, expr, type_hint)

        if tok.type == 'Yakscho':
            self.check_dialect(tok)
            return self.if_statement()
        elif tok.type == 'Doki':
            self.check_dialect(tok)
            return self.while_statement()
        elif tok.type == 'Dlya':
            self.check_dialect(tok)
            next_tok = self.peek_ahead(1)
            next_next_tok = self.peek_ahead(2)
            
            if next_tok and next_tok.type == 'ID' and next_next_tok and next_next_tok.type == 'KOZHEN':
                self.check_dialect(tok)
                return self.for_each_statement()
            else:
                self.check_dialect(tok)
                return self.for_statement()

        elif tok.type == 'Zavdannya':
            self.check_dialect(tok)
            return self.function_def()
        
        result = None

        if tok.type == 'Sprobuy':
            self.check_dialect(tok)
            return self.try_statement()
        elif tok.type == 'Kydaty':
            self.check_dialect(tok)
            return self.throw_statement()
        
        if tok.type == 'Vykhid':
            self.check_dialect(tok)
            return self.exit_statement()
        
        if tok.type == 'Importuvaty':
            self.check_dialect(tok)
            return self.import_statement()
        
        if tok.type == 'SUPER':
            self.check_dialect(tok)
            expr = self.factor()
            next_tok = self.peek()
            
            if isinstance(expr, KozakSuper):
                result = expr
            else:
                return self.error(tok, f"Unexpected super usage at line {tok.line}, column {tok.column}")


        elif tok.type in ('ID', 'THIS'):
            expr = self.factor()
            next_tok = self.peek()
            
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
            self.check_dialect(tok)
            result = self.echo()
        elif tok.type == 'Povernuty':
            self.check_dialect(tok)
            return self.return_statement()
        elif tok.type == 'Klas':
            self.check_dialect(tok)
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
            if self.peek() and self.peek().type == 'DOT':
                self.advance() 
                property_token = self.expect('ID')
                if property_token is None:
                    return None 

                expr = KozakPropertyAccess(
                    instance=expr,
                    property_name=property_token.value
                )

            
            elif self.peek() and self.peek().type == 'LBRACKET':
                self.advance()
                index_expr = self.or_expression()
                self.expect('RBRACKET')
                expr = KozakArrayIndex(expr, index_expr)

            
            elif self.peek() and self.peek().type == 'LPAREN':
                if isinstance(expr, KozakVariable):
                    self.advance() 
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
            operand = self.factor()  
            return KozakBinOp(KozakNumber(0), '-', operand)  
    
        if tok.type == 'OP' and tok.value == '+':
            self.advance()
            return self.factor()


        if tok.type == 'NUMBER':
            self.advance()
            return KozakNumber(tok.value)
        elif tok.type == 'Pravda':
            self.check_dialect(tok)
            self.advance()
            return KozakBoolean(True)
        elif tok.type == 'Nepravda':
            self.check_dialect(tok)
            self.advance()
            return KozakBoolean(False)
        elif tok.type == 'NEW':
            self.check_dialect(tok)
            self.advance()
            class_name = self.expect('ID').value
            if not class_name:
                return None 
            args = self.function_call_arguments()
            return KozakNewInstance(class_name, args)
        
        elif tok.type == 'SUPER':
            self.check_dialect(tok)
            self.advance()
            self.expect('DOT')
            method_name = self.expect('ID').value
            
            if self.peek() and self.peek().type == 'LPAREN':
                arguments = self.function_call_arguments()
                return KozakSuper(method_name, arguments)
            else:
                return self.error(tok, "Super must be followed by a method call")


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

            
            while self.peek() and self.peek().type == 'LBRACKET':
                self.advance()
                index_expr = self.or_expression()
                self.expect('RBRACKET')
                node = KozakDictionaryAccess(node, index_expr)
            while self.peek() and self.peek().type == 'DOT':
                self.advance()
                prop_name = self.expect('ID').value
                node = KozakPropertyAccess(node, prop_name)
                
                if self.peek() and self.peek().type == 'LPAREN':
                    arguments = self.function_call_arguments()
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
            return None  
        
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
        destructor = None
        method_access = {}
        field_access = {}
        friends = []
        friend_classes = []

        while self.peek() and self.peek().type != 'RBRACE':
            access_modifier = 'public'
            if self.peek().type in ('PUBLIC', 'PRIVATE', 'PROTECTED'):
                self.check_dialect(self.peek())
                access_modifier = self.peek().type.lower()
                self.advance()
            
            if self.peek().type == 'FRIEND':
                self.check_dialect(self.peek())
                self.advance()
                self.expect('COLON')
                friend_name = self.expect('ID').value
                friends.append(friend_name)
                
                while self.peek() and self.peek().type == 'COMMA':
                    self.advance()
                    friend_name = self.expect('ID').value
                    friends.append(friend_name)
                
                self.expect('SEMICOLON')
                continue

            if self.peek().type == 'FRIEND_CLASS':
                self.check_dialect(self.peek())
                self.advance()
                self.expect('COLON')
                
                friend_class_name = self.expect('ID').value
                friend_classes.append(friend_class_name)
                
                while self.peek() and self.peek().type == 'COMMA':
                    self.advance()
                    friend_class_name = self.expect('ID').value
                    friend_classes.append(friend_class_name)
                
                self.expect('SEMICOLON')
                continue


            if self.peek().type == 'Tvir':
                self.check_dialect(self.peek())
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

            elif self.peek().type == 'ID' and self.peek().value in ('Znyshchyty', 'Destructor', 'Unichtozhit', '@~'):
                self.check_dialect(self.peek())
                self.advance()
                self.expect('LPAREN')
                self.expect('RPAREN')
                self.expect('LBRACE')
                body = self.block()
                destructor = KozakDestructor(body)

            elif self.peek().type == 'Zavdannya':
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
        destructor=destructor, 
        parent_name=parent_name,
        field_access=field_access,
        method_access=method_access,
        friends=friends,
        friend_classes=friend_classes
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
        elif isinstance(target, KozakDictionaryAccess):
            return KozakPropertyAssign(target.dictionary, target.key, expr)
        elif isinstance(target, KozakVariable):
            return KozakAssign(target.name, expr)
    
    def parse_dictionary(self):
        self.expect('LBRACE')
        pairs = []
        
        if self.peek() and self.peek().type != 'RBRACE':
            key = self.or_expression()
            self.expect('COLON')
            value = self.or_expression()
            pairs.append((key, value))
            
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                if self.peek() and self.peek().type == 'RBRACE':
                    break
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