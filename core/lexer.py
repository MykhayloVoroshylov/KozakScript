"""Lexer for KozakScript"""

import re
from collections import namedtuple


Token = namedtuple(typename='Token', field_names=['type', 'value','line', 'column'])

KEYWORDS = {
    #Ukrainian (Latin) keywords KozakScript
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
    'novyy': 'NEW',
    'tsey': 'THIS',
    'Batko': 'SUPER', 
    'Sprobuy': 'Sprobuy',
    'Piymat': 'Piymat',          
    'Vkintsi': 'Vkintsi',        
    'Kydaty': 'Kydaty',
    'Vykhid' : 'Vykhid',
    'Importuvaty': 'Importuvaty',
    'Vidkrytyy': 'PUBLIC',
    'Zakrytyy': 'PRIVATE',
    'Zakhyshchenyy': 'PROTECTED',
    'Druh': 'FRIEND',
    'DruhKlas': 'FRIEND_CLASS',
    'Statychnyy': 'STATIC',

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
    'new': 'NEW',
    'this': 'THIS',
    'Super': 'SUPER', 
    'Try': 'Sprobuy',
    'Catch': 'Piymat',
    'Finally': 'Vkintsi',
    'Throw': 'Kydaty',
    'Exit' : 'Vykhid',
    'Import': 'Importuvaty',
    'Public': 'PUBLIC',
    'Private': 'PRIVATE',
    'Protected': 'PROTECTED',
    'Friend': 'FRIEND',
    'FriendClass': 'FRIEND_CLASS',
    'Static': 'STATIC',

    #Russian (Latin) keywords KozakScript
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
    'Roditel': 'SUPER', 
    'Poprobuy': 'Sprobuy',
    'Poymat': 'Piymat',
    'Nakonets': 'Vkintsi',
    'Brosat': 'Kydaty',
    'Vykhod': 'Vykhid',
    'Importirovat': 'Importuvaty',
    'Otkrytyy': 'PUBLIC',
    'Zakrytyy': 'PRIVATE',
    'Zashchishchennyy': 'PROTECTED',
    'Drug': 'FRIEND',
    'DrugKlass': 'FRIEND_CLASS',
    'Statichnyy': 'STATIC',

    #Ukrainian (Cyrillic) keywords KozakScript
    'Гетьман': 'Hetman', #starting word
    'Співати': 'Spivaty',
    'Слухай': 'Slukhai',
    'Повернути': 'Povernuty',
    'Завдання': 'Zavdannya',
    'Для': 'Dlya',
    'Доки': 'Doki',
    'Правда': 'Pravda',
    'Неправда': 'Nepravda',
    'Число': 'Chyslo',
    'ДробовеЧисло': 'DroboveChyslo',
    'Рядок': 'Ryadok',
    'Логіка': 'Logika',
    'Якщо': 'Yakscho',
    'Або_Якщо': 'AboYakscho',
    'Інакше': 'Inakshe',
    'довжина': 'Dovzhyna',
    'кожен': 'KOZHEN',
    'Клас': 'Klas',
    'Твір': 'Tvir',
    'новий': 'NEW',
    'цей': 'THIS',
    'Батько': 'SUPER',
    'Спробуй': 'Sprobuy',
    'Піймати': 'Piymat',
    'Вкінці': 'Vkintsi',
    'Кидати': 'Kydaty',
    'Вихід' : 'Vykhid',
    'Імпортувати': 'Importuvaty',
    'Відкритий': 'PUBLIC',
    'Закритий': 'PRIVATE',
    'Захищений': 'PROTECTED',
    'Друг': 'FRIEND',
    'ДругКлас': 'FRIEND_CLASS',
    'Статичний': 'STATIC',

    #Russian (Cyrillic) keywords KozakScript
    'Атаман': 'Hetman',#starting word
    'Печатать': 'Spivaty',
    'Ввод': 'Slukhai',
    'Вернуть': 'Povernuty',
    'Задание': 'Zavdannya',
    'Для':'Dlya',
    'Пока':'Doki',
    'Правда':'Pravda',
    'Неправда':'Nepravda',
    'Число': 'Chyslo', 
    'ДробноеЧисло': 'DroboveChyslo',
    'Строка': 'Ryadok',
    'Логика': 'Logika',
    'Если': 'Yakscho',
    'Или_Если': 'AboYakscho',
    'Иначе': 'Inakshe',
    'длинна': 'Dovzhyna',
    'каждый': 'KOZHEN',
    'Класс': 'Klas',
    'Творение': 'Tvir',
    'новый': 'NEW',
    'этот': 'THIS',
    'Родитель': 'SUPER',
    'Попробуй': 'Sprobuy',
    'Поймать': 'Piymat',
    'Наконец': 'Vkintsi',
    'Бросать': 'Kydaty',
    'Выход': 'Vykhid',
    'Импортировать': 'Importuvaty',
    'Открытый': 'PUBLIC',
    'Закрытый': 'PRIVATE',
    'Защищённый': 'PROTECTED',
    'Друг': 'FRIEND',
    'ДругКласс': 'FRIEND_CLASS',
    'Статичный': 'STATIC',

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
    '++>': 'PUBLIC',
    '-->': 'PRIVATE',
    '##>': 'PROTECTED',
    '^>': 'SUPER',
    '<->': 'FRIEND',
    '<=>': 'FRIEND_CLASS',
    '@@': 'STATIC',
    }

TOKEN_SPECIFICATION = [
    ('SYMBOLIC_MULTI', r'>>>|<<<|<->|<=>|##>|\+\+>|-->|\^>|1!|0!|!!>|!!|i`\*\*|f`\*\*|s`\*\*|b`\*\*|\+@|@=|@~|~`|~~|\?\?|\?!|<!|-<!|___|\[\.\.\]|->|::|<<|>>|<>|=<|=>|\+<|\+:|\?\^|-<|-<!|--<|\?:|-<|--<|k\{\}|v\{\}|\?k|-k|@\[\]|#\[\]|\[\]>|\[\]\^|\[\]->|\[\]\||\[\]:='),
    ('NUMBER', r'\d+(\.\d*)?'),
    ('STRING', r'"[^"]*"|\'[^\']*\''),
    ('MLCOMMENT', r'/\*.*?\*/'), 
    ('COMMENT', r'//[^\n]*'),
    ('OP', r'\+\+|\%|--|&&|\|\||:=|==|!=|>=|<=|//|\^/|\^|[+\-*/=<>]+'),
    ('SYMBOLIC_SINGLE', r'[!?$@#]'),
    ('ID', r'[^\W\d_][\w]*'),
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
DIALECT_STARTERS = {
        'Hetman': 'ukrainian_latin',
        'Chief': 'english',
        'Ataman': 'russian_latin',
        '>>>': 'symbolic',
        'Гетьман': 'ukrainian_cyrillic',
        'Атаман': 'russian_cyrillic'
    }

SHARED_SLAVIC = {
        'Dlya',
        'Pravda',
        'Nepravda',
        'Logika',
        'klyuchi',
        'novyy',
    }

SHARED_SLAVIC_CYRILLIC = {
        'Для',
        'Правда',
        'Неправда',
        'Число',
        'Друг',
    }


DIALECT_KEYWORDS = {
        'ukrainian_latin': {
            'Hetman', 'Spivaty', 'Slukhai', 'Povernuty', 'Zavdannya', 'Doki',
            'Chyslo', 'DroboveChyslo', 'Ryadok', 
            'Yakscho', 'Abo_Yakscho', 'Inakshe', 'dovzhyna', 'kozhen', 'Klas', 'Tvir',
            'tsey', 'Sprobuy', 'Piymat', 'Vkintsi', 'Kydaty', 'Vykhid', 'Importuvaty',
            'znachennya', 'maye_klyuch', 'vydalyty_klyuch',
            'dodaty', 'vstavyty', 'vydalyty', 'vyinyaty', 'ochystyty', 'vyrizaty',
            'mistyt', 'index_z', 'Zapysaty', 'Chytaty', 'stvoryty_matrytsyu', 'rozmir_matrytsi', 'splushchyty', 'transportuvaty',
            'otrymaty_ryadok', 'otrymaty_stovpets', 'vstanovyty_na', 'Vidkrytyy', 'Zakrytyy', 'Zakhyshchenyy', 'Batko', 'Druh',
            'Znyshchyty', 'Statychnyy'
        },
        'english': {
            'Chief', 'Print', 'Input', 'Return', 'Function', 'For', 'While',
            'True', 'False', 'Int', 'Float', 'Str', 'Bool',
            'If', 'Else_If', 'Else', 'Length', 'each', 'Class', 'Constructor',
            'new', 'this', 'Try', 'Catch', 'Finally', 'Throw', 'Exit', 'Import',
            'keys', 'values', 'has_key', 'remove_key',
            'append', 'insert', 'remove', 'pop', 'clear', 'slice',
            'contains', 'index_of', 'Write', 'Read', 'create_matrix', 'matrix_size', 'flatten', 'transpose',
            'get_row', 'get_col', 'set_at', 'Public', 'Private', 'Protected', 'Super', 'Friend', 'Destroy', 'Static'
        },
        'russian_latin': {
            'Ataman', 'Pechatat', 'Vvod', 'Vernut', 'Zadanie', 'Poka',
            'Chislo', 'DrobnoyeChislo', 'Stroka', 
            'Yesli', 'Ili_Yesli', 'Inache', 'dlinna', 'kazhdy', 'Klass', 'Tvorenye',
            'etot', 'Poprobuy', 'Poymat', 'Nakonets', 'Brosat', 'Vykhod', 'Importirovat',
            'znachennie', 'imeet_klyuch', 'udalit_klyuch',
            'dobavit', 'vstavit', 'udalit', 'vytaschit', 'ochistit', 'vyrezat',
            'soderzhit', 'index_znachenia', 'Zapisat', 'Chitat','sozdat_matritsu', 'razmer_matritsy', 'spluschit', 'transportirovat',
            'poluchit_stroku', 'poluchit_stolbets', 'ustanovit_na', 'Otkrytyy', 'Zakrytyy', 'Zashchishchennyy', 'Roditel', 'Drug',
            'Unichtozhit', 'Statichnyy'
        },
        'ukrainian_cyrillic': {
            'Гетьман', 'Співати', 'Слухай', 'Повернути', 'Завдання', 'Доки',
            'Число', 'ДробовеЧисло', 'Рядок',
            'Якщо', 'Або_Якщо', 'Інакше', 'довжина', 'кожен', 'Клас', 'Твір',
            'цей', 'Спробуй', 'Піймати', 'Вкінці', 'Кидати', 'Вихід', 'Імпортувати',
            'значення', 'має_ключ', 'видалити_ключ',
            'додати', 'вставити', 'видалити', 'вийняти', 'очистити', 'вирізати',
            'містить', 'індекс_значення', 'Записати', 'Читати', 'створити_матрицю', 'розмір_матриці', 'сплющити', 'транспонувати',
            'отримати_рядок', 'отримати_стовпець', 'встановити_на', 'Відкритий', 'Закритий', 'Захищений', 'Батько', 'Друг',
            'Знищити', 'Статичний'},

        'russian_cyrillic': {
            'Атаман', 'Печатать', 'Ввод', 'Вернуть', 'Задание', 'Пока',
            'Число', 'ДробноеЧисло', 'Строка',
            'Если', 'Или_Если', 'Иначе', 'длинна', 'каждый', 'Класс', 'Творение',
            'этот', 'Попробуй', 'Поймать', 'Наконец', 'Бросать', 'Выход', 'Импортировать',
            'значения', 'имеет_ключ', 'удалить_ключ',
            'добавить', 'вставить', 'удалить', 'вытаскивать', 'очистить', 'вырезать',
            'содержит', 'индекс_значения', 'Записать',  'Читать','создать_матрицу', 'размер_матрицы', 'сплющить', 'транспонировать',
            'получить_строку', 'получить_столбец', 'установить_на', 'Открытый', 'Закрытый', 'Защищённый', 'Родитель', 'Друг',
            'Уничтожить',  'Статичный'
        },
        'symbolic': {
            '>>>', '!', '?', '<!', '$', '~~', '~`',
            '1!', '0!', 'i`**', 'f`**', 's`**', 'b`**',
            '??', '?!', '!!', '___', '::', '@', '@=',
            '+@', '->', '<<', '>>', '<>', '!!>', '<<<', '#',
            r'k{}', r'v{}', '?k', '-k',
            '+<', '+:', '-<', '-<!', '--<', '[..]',
            '?^', '?:', '=>', '=<', '@[]', '#[]', '[]>', '[]^', '[]->', '[]|', '[]:=', '++>', '-->', '##>', '^>', '<->', '@~', '@@'
        }
    }

KEYWORD_TRANSLATIONS = {
        # Structure keywords
        'Hetman': {'ukrainian_latin': 'Hetman', 'english': 'Chief', 'russian_latin': 'Ataman', 'symbolic': '>>>', 'ukrainian_cyrillic': 'Гетьман', 'russian_cyrillic': 'Атаман'},
        'Spivaty': {'ukrainian_latin': 'Spivaty', 'english': 'Print', 'russian_latin': 'Pechatat', 'symbolic': '!', 'ukrainian_cyrillic': 'Співати', 'russian_cyrillic': 'Печатать'},
        'Slukhai': {'ukrainian_latin': 	'Slukhai' , 	'english':'Input','russian_latin':'Vvod','symbolic':'?','ukrainian_cyrillic':'Слухай','russian_cyrillic':'Ввод'},
        'Povernuty': {'ukrainian_latin': 	'Povernuty','english':'Return','russian_latin':'Vernut','symbolic':'<!',	'ukrainian_cyrillic':'Повернути','russian_cyrillic':'Вернуть'},
        'Zavdannya': {'ukrainian_latin': 	'Zavdannya' , 	'english':'Function','russian_latin':'Zadanie','symbolic':'$','ukrainian_cyrillic':'Завдання','russian_cyrillic':'Задание'},
        'Doki': {'ukrainian_latin': 	'Doki' , 	'english':'While','russian_latin':'Poka','symbolic':'~`','ukrainian_cyrillic':'Доки','russian_cyrillic':'Пока'},
        
        # Types
        'Chyslo': {'ukrainian_latin': 'Chyslo', 'english': 'Int', 'russian_latin': 'Chislo', 'symbolic': 'i`**', 'ukrainian_cyrillic':'Число','russian_cyrillic':'Число'},
        'DroboveChyslo': {'ukrainian_latin': 'DroboveChyslo', 'english': 'Float', 'russian_latin': 'DrobnoyeChislo', 'symbolic': 'f`**', 'ukrainian_cyrillic':'ДробовеЧисло','russian_cyrillic':'ДробноеЧисло'},
        'Ryadok': {'ukrainian_latin': 'Ryadok', 'english': 'Str', 'russian_latin': 'Stroka', 'symbolic': 's`**', 'ukrainian_cyrillic':'Рядок','russian_cyrillic':'Строка'},
        'Logika': {'ukrainian_latin': 	'Logika' , 	'english': 	'Bool' , 	'russian_latin' : 	'Logika' , 	'symbolic' : 	'b`**' , 	'ukrainian_cyrillic':'Логіка','russian_cyrillic':'Логика'},

        # Control flow
        'Yakscho': {'ukrainian_latin': 'Yakscho', 'english': 'If', 'russian_latin': 'Yesli', 'symbolic': '??', 'ukrainian_cyrillic':'Якщо','russian_cyrillic':'Если'},
        'AboYakscho': {'ukrainian_latin': 'Abo_Yakscho', 'english': 'Else_If', 'russian_latin': 'Ili_Yesli', 'symbolic': '?!', 'ukrainian_cyrillic':'Або_Якщо','russian_cyrillic':'Или_Если'},
        'Inakshe': {'ukrainian_latin': 'Inakshe', 'english': 'Else', 'russian_latin': 'Inache', 'symbolic': '!!', 'ukrainian_cyrillic':'Інакше','russian_cyrillic':'Иначе'},
        'Dovzhyna': {'ukrainian_latin': 'dovzhyna', 'english': 'Length', 'russian_latin': 'dlinna', 'symbolic': '___', 	'ukrainian_cyrillic':'довжина','russian_cyrillic':'длинна'},
        'KOZHEN': {'ukrainian_latin': 'kozhen', 'english': 'each', 'russian_latin': 'kazhdy', 'symbolic': '::', 'ukrainian_cyrillic':'кожен','russian_cyrillic':'каждый'},

        # OOP
        'Klas': {'ukrainian_latin': 'Klas', 'english': 'Class', 'russian_latin': 'Klass', 'symbolic': '@', 'ukrainian_cyrillic':'Клас','russian_cyrillic':'Класс'},
        'Tvir': {'ukrainian_latin': 'Tvir', 'english': 'Constructor', 'russian_latin': 'Tvorenye', 'symbolic': '@=', 'ukrainian_cyrillic':'Твір','russian_cyrillic':'Творение'},
        'NEW': {'ukrainian_latin': 'novyy', 'english': 'new', 'russian_latin': 'novyy', 'symbolic': '+@', 'ukrainian_cyrillic':'новий','russian_cyrillic':'новый'},
        'THIS': {'ukrainian_latin': 'tsey', 'english': 'this', 'russian_latin': 'etot', 'symbolic': '->', 	'ukrainian_cyrillic':'цей','russian_cyrillic':'этот'},
        'SUPER': {'ukrainian_latin': 	'Batko', 	'english': 	'Super', 	'russian_latin': 	'Roditel', 	'symbolic': '^>', 	'ukrainian_cyrillic':'Батько','russian_cyrillic':'Родитель'},
        'Destructor': {'ukrainian_latin': 	'Znyshchyty', 	'english': 	'Destructor', 	'russian_latin': 	'Unichtozhit', 	'symbolic': '@~', 'ukrainian_cyrillic':'Знищити','russian_cyrillic':'Уничтожить'},

        # Access modifiers
        'PUBLIC': {'ukrainian_latin': 'Vidkrytyy', 'english': 'Public', 'russian_latin': 'Otkrytyy', 'symbolic': '++>', 'ukrainian_cyrillic':'Відкритий','russian_cyrillic':'Открытый'},
        'PRIVATE': {'ukrainian_latin': 'Zakrytyy', 'english': 'Private', 'russian_latin': 'Zakrytyy', 'symbolic': '-->', 'ukrainian_cyrillic':'Закритий','russian_cyrillic':'Закрытый'},
        'PROTECTED': {'ukrainian_latin': 'Zakhyshchenyy', 'english': 'Protected', 'russian_latin': 'Zashchishchennyy', 'symbolic': '##>', 'ukrainian_cyrillic':'Захищений','russian_cyrillic':'Защищённый'},
        'FRIEND': {'ukrainian_latin': 'Druh', 'english': 'Friend', 'russian_latin': 'Drug', 'symbolic': '<->', 	'ukrainian_cyrillic':'Друг','russian_cyrillic':'Друг'},
        'STATIC': {'ukrainian_latin': 'Statychnyy', 'english': 'Static', 'russian_latin': 'Statichnyy', 'symbolic': '@@', 'ukrainian_cyrillic':'Статичний','russian_cyrillic':'Статичный'},

        # Exception handling
        'Sprobuy': {'ukrainian_latin': 'Sprobuy', 'english': 'Try', 'russian_latin': 'Poprobuy', 'symbolic': '<<', 'ukrainian_cyrillic':'Спробуй','russian_cyrillic':'Попробуй'},
        'Piymat': {'ukrainian_latin': 'Piymat', 'english': 'Catch', 'russian_latin': 'Poymat', 'symbolic': '>>', 'ukrainian_cyrillic':'Піймай','russian_cyrillic':'Поймай'},
        'Vkintsi': {'ukrainian_latin': 'Vkintsi', 'english': 'Finally', 'russian_latin': 'Nakonets', 'symbolic': '<>', 	'ukrainian_cyrillic':'Вкінці','russian_cyrillic':'Наконец'},
        'Kydaty': {'ukrainian_latin': 'Kydaty', 'english': 'Throw', 'russian_latin': 'Brosat', 'symbolic': '!>', 	'ukrainian_cyrillic':'Кидати','russian_cyrillic':'Бросать'},

        # Other
        'Vykhid': {'ukrainian_latin': 'Vykhid', 'english': 'Exit', 'russian_latin': 'Vykhod', 'symbolic': '<<<', 'ukrainian_cyrillic':'Вихід','russian_cyrillic':'Выход'},
        'Importuvaty': {'ukrainian_latin': 'Importuvaty', 'english': 'Import', 'russian_latin': 'Importirovat', 'symbolic': '#', 'ukrainian_cyrillic':'Імпортувати','russian_cyrillic':'Импортировать'},
        'KOZHEN': {'ukrainian_latin': 'kozhen', 'english': 'each', 'russian_latin': 'kazhdy', 'symbolic': '::', 'ukrainian_cyrillic':'кожен','russian_cyrillic':'каждый'},
        'Dovzhyna': {'ukrainian_latin': 'dovzhyna', 'english': 'length', 'russian_latin': 'dlinna', 'symbolic': '___', 'ukrainian_cyrillic':'довжина','russian_cyrillic':'длинна'},
    }



def lex(code):
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
    tok_re = re.compile(tok_regex, re.DOTALL)
    detected_dialect = None
    conflicts=[]


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
            if value in KEYWORDS:
                # ✅ FIX: Check if this is a shared keyword before checking for conflicts
                is_shared_slavic = value in SHARED_SLAVIC
                is_shared_cyrillic = value in SHARED_SLAVIC_CYRILLIC
                
                for dialect, words in DIALECT_KEYWORDS.items():
                    if value in words:
                        if detected_dialect is None:
                            detected_dialect = dialect
                        elif detected_dialect != dialect:
                            # ✅ FIX: Before adding conflict, check if it's a shared keyword
                            should_allow = False
                            
                            # Allow shared Latin Slavic keywords in Latin Slavic dialects
                            if is_shared_slavic:
                                if detected_dialect in ('ukrainian_latin', 'russian_latin') and \
                                   dialect in ('ukrainian_latin', 'russian_latin'):
                                    should_allow = True
                            
                            # Allow shared Cyrillic keywords in Cyrillic dialects
                            elif is_shared_cyrillic:
                                if detected_dialect in ('ukrainian_cyrillic', 'russian_cyrillic') and \
                                   dialect in ('ukrainian_cyrillic', 'russian_cyrillic'):
                                    should_allow = True
                            
                            # ✅ FIX: Only add to conflicts if not a shared keyword
                            if not should_allow:
                                conflicts.append((value, detected_dialect, dialect))
            
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

            raise SyntaxError(f'Unexpected character: {value!r} at line {line_num}, column {col_num}')
        if conflicts:
            raise SyntaxError(
                f"Mixed dialects: '{conflicts[0][0]}' from {conflicts[0][2]} inside {conflicts[0][1]}"
            )

