"""Lexer for KozakScript"""

import re
from collections import namedtuple

Token = namedtuple(typename='Token', field_names=['type', 'value','line', 'column'])

KEYWORDS = {
    #Ukrainian keywords KozakScript
    'Hetman': 'Hetman', #starting word
    'Spivaty': 'Spivaty', 
    'Slukhai': 'Slukhai',
    'Povernuty': 'Povernuty',
    'Zavdannya': 'Zavdannya',
    'Dlya': 'Dlya',
    'Doki': 'Doki', 
    'Pravda': 'Pravda', 
    'Nepravda': 'Nepravda',
    'Chyslo': 'Chyslo',
    'DroboveChyslo': 'DroboveChyslo',
    'Ryadok': 'Ryadok',
    'Logika': 'Logika',
    'Yakscho': 'Yakscho',
    'Abo_Yakscho': 'AboYakscho',
    'Inakshe': 'Inakshe',
    'dovzhyna': 'Dovzhyna',
    'kozhen': 'KOZHEN',
    'Klas': 'Klas',
    'Tvir': 'Tvir',
    'new': 'NEW',
    'this': 'THIS',
    'Sprobuy': 'Sprobuy',
    'Piymat': 'Piymat',          
    'Vkintsi': 'Vkintsi',        
    'Kydaty': 'Kydaty',
    'Vykhid' : 'Vykhid',
    'Importuvaty': 'Importuvaty',

    #English keywords KozakScript
    'Chief': 'Hetman', #starting word
    'Print': 'Spivaty',
    'Input': 'Slukhai',
    'Return': 'Povernuty',
    'Function': 'Zavdannya',
    'For': 'Dlya',
    'While': 'Doki',
    'True': 'Pravda',
    'False': 'Nepravda',
    'Int': 'Chyslo',
    'Float': 'DroboveChyslo',
    'Str': 'Ryadok',
    'Bool': 'Logika',
    'If': 'Yakscho',
    'Else_If': 'AboYakscho',
    'Else': 'Inakshe',
    'Length': 'Dovzhyna',
    'each': 'KOZHEN',
    'Class': 'Klas',
    'Constructor': 'Tvir',
    'novyy': 'NEW',
    'tsey': 'THIS',
    'Try': 'Sprobuy',
    'Catch': 'Piymat',
    'Finally': 'Vkintsi',
    'Throw': 'Kydaty',
    'Exit' : 'Vykhid',
    'Import': 'Importuvaty',

    #Russian keywords KozakScript
    'Ataman': 'Hetman',#starting word
    'Pechatat': 'Spivaty',
    'Vvod': 'Slukhai',
    'Vernut': 'Povernuty',
    'Zadanie': 'Zavdannya',
    'Dlya':'Dlya',
    'Poka':'Doki',
    'Pravda':'Pravda',
    'Nepravda':'Nepravda',
    'Chislo': 'Chyslo',
    'DrobnoyeChislo': 'DroboveChyslo',
    'Stroka': 'Ryadok',
    'Logika': 'Logika',
    'Yesli': 'Yakscho',
    'Ili_Yesli': 'AboYakscho',
    'Inache': 'Inakshe',
    'Dlinna': 'Dovzhyna',
    'Kazhdy': 'KOZHEN',
    'Klass': 'Klas',
    'Tvorenye': 'Tvir',
    'novyy': 'NEW',
    'etot': 'THIS',
    'Poprobuy': 'Sprobuy',
    'Poymat': 'Piymat',
    'Nakonets': 'Vkintsi',
    'Brosat': 'Kydaty',
    'Vykhod': 'Vykhid',
    'Importirovat': 'Importuvaty',


    #Symbolic dialect keywords KozakScript
    '>>>': 'Hetman', #starting word
    '!': 'Spivaty',
    '?': 'Slukhai',
    '<!': 'Povernuty',
    '$': 'Zavdannya',
    '~~': 'Dlya',
    '~`': 'Doki',
    '1!': 'Pravda',
    '0!': 'Nepravda',
    'i`**': 'Chyslo',
    'f`**': 'DroboveChyslo',
    's`**': 'Ryadok',
    'b`**': 'Logika',
    '??': 'Yakscho',
    '?!': 'AboYakscho',
    '!!': 'Inakshe',
    '___': 'Dovzhyna',
    '::': 'KOZHEN',
    '@': 'Klas',
    '@=': 'Tvir',
    '+@': 'NEW',
    '->': 'THIS',
    '<<': 'Sprobuy',
    '>>': 'Piymat',
    '<>': 'Vkintsi',
    '!!>': 'Kydaty',
    '<<<' : 'Vykhid',
    '#': 'Importuvaty',
    r'k{}': 'klyuchi_sym',
    r'v{}': 'znachennya_sym', 
    '?k': 'maye_klyuch_sym',
    '-k': 'vydalyty_klyuch_sym',
    
}

TOKEN_SPECIFICATION = [
    ('NUMBER', r'\d+(\.\d*)?'),
    ('STRING', r'"[^"]*"|\'[^\']*\''),
    ('MLCOMMENT', r'/\*.*?\*/'), 
    ('COMMENT', r'//[^\n]*'),
    ('SYMBOLIC_MULTI', r'>>>|<<<|1!|0!|!!>|!!|i`\*\*|f`\*\*|s`\*\*|b`\*\*|\+@|@=|~`|~~|\?\?|\?!|<!|-<!|___|\[\.\.\]|->|::|<<|>>|<>|=<|=>|\+<|\+:|\?\^|-<|-<!|--<|\?:|-<|--<|k\{\}|v\{\}|\?k|-k'),
    ('OP', r'\+\+|\%|--|&&|\|\||:=|==|!=|>=|<=|//|\^/|\^|[+\-*/=<>]+'),
    ('SYMBOLIC_SINGLE', r'[!?$@#]'),
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('DOT', r'\.'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),  
    ('RBRACE', r'\}'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
    ('COLON', r':'),
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
    ('MISMATCH', r'.'),
]

def lex(code):
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
    tok_re = re.compile(tok_regex, re.DOTALL)



    for match in re.finditer(tok_re, code):
        kind = match.lastgroup
        value = match.group()
        
        line_num = code[:match.start()].count('\n') + 1
        col_num = match.start() - code.rfind('\n', 0, match.start()) if '\n' in code[:match.start()] else match.start() + 1

        if kind in ('SKIP', 'NEWLINE', 'MLCOMMENT', 'COMMENT'):
            continue

        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
            yield Token(kind, value, line_num, col_num)
        elif kind in ('SYMBOLIC_MULTI', 'SYMBOLIC_SINGLE', 'ID'):
            mapped_type = KEYWORDS.get(value, 'ID')
            
            # For dictionary function symbols, yield as ID with the function name
            if value in ('k{}', 'v{}', '?k', '-k'):
                yield Token('ID', KEYWORDS[value], line_num, col_num)
            else:
                yield Token(mapped_type, value, line_num, col_num)

        elif kind == 'ID':
            yield Token(KEYWORDS.get(value, 'ID'), value, line_num, col_num)
        elif kind in ('LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET', 'SEMICOLON', 'COMMA', 'OP', 'STRING', 'DOT', 'COLON'):
            yield Token(kind, value, line_num, col_num)
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character, kozache: {value!r} at line {line_num}, column {col_num}')