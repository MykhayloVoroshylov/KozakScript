"""Lexer for KozakScript"""

import re
from collections import namedtuple

Token = namedtuple(typename='Token', field_names=['type', 'value', 'line', 'column'])


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

    line_num = 1
    line_start = 0

    for match in re.finditer(tok_re, code):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == 'NEWLINE':
            line_num += 1
            line_start = match.end()
            continue

        elif kind == 'SKIP' or kind in ('MLCOMMENT', 'COMMENT'):
            continue

        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)

        elif kind == 'ID':
            kind = KEYWORDS.get(value, 'ID')

        elif kind == 'STRING':
            pass  # keep quotes for parser

        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character {value!r} at line {line_num}, column {column}")

        yield Token(kind, value, line_num, column)
