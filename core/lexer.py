"""Lexer for KozakScript"""

import re
from collections import namedtuple

Token = namedtuple(typename='Token', field_names=['type', 'value'])

KEYWORDS = {
    'Hetman': 'Hetman', 
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
    'AboYakscho': 'AboYakscho',
    'Inakshe': 'Inakshe',
}

TOKEN_SPECIFICATION = [
    ('NUMBER', r'\d+(\.\d*)?'),
    ('STRING', r'"[^"]*"|\'[^\']*\''),
    ('MLCOMMENT', r'/\*.*?\*/'), 
    ('COMMENT', r'//[^\n]*'),
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('OP', r'\+\+|--|&&|\|\||:=|==|!=|>=|<=|//|\^/|\^|[+\-*/=<>]+'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),  
    ('RBRACE', r'\}'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
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

        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
            yield Token(kind, value)

        elif kind == 'ID':
            yield Token(KEYWORDS.get(value, 'ID'), value)

        elif kind in ('LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA'):
            yield Token(kind, value)

        elif kind in ('NEWLINE', 'SKIP'):
            continue

        elif kind in ('MLCOMMENT', 'COMMENT'):
            continue

        elif kind == 'OP':
            yield Token('OP', value)

        elif kind == 'STRING':
            yield Token('STRING', value)      

        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character, kozache: {value!r}')
