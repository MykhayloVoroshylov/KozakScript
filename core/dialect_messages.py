"""Dialect-specific messages for KozakScript"""

class DialectMessages:
    FRIENDLY_TERMS = {
        'ukrainian_latin': 'kozache',
        'russian_latin': 'tovarishch',
        'english': 'pal',
        'symbolic': 'user',
        'ukrainian_cyrillic': 'козаче',
        'russian_cyrillic': 'товарищ'
    }

    STARTUP_MESSAGES = {
        'ukrainian_latin':"✓ Slava Ukraini! Using Ukrainian (Latin) dialect",
        'russian_latin': "✓ Zdravstvuy tovarisch! Using Russian (Latin) dialect",
        'english': "✓ Hello pal! Using English dialect",
        'symbolic': "✓ SYSTEM_READY! Symbolic dialect initialized",
        'ukrainian_cyrillic':"✓ Слава Україні! Використовується українська кирилиця",
        'russian_cyrillic': "✓ Здравствуй товарищ! Используется русская кириллица"
    }

    SUCCESS_MESSAGES = {
        'ukrainian_latin': "Program executed successfully, kozache!",
        'russian_latin': "Program executed successfully, tovarisch!",
        'english': "Program executed successfully, pal!",
        'symbolic': "EXECUTION_COMPLETE: NO_ERRORS_DETECTED",
        'ukrainian_cyrillic': "Програма виконана успішно, козаче!",
        'russian_cyrillic': "Программа выполнена успешно, товарищ!"
    }

    EXIT_MESSAGES = {
        'ukrainian_latin': "Program exited with code {code}, kozache!",
        'ukrainian_cyrillic': "Програма завершена з кодом {code}, козаче!",
        'russian_latin': "Program exited with code {code}, tovarisch!",
        'russian_cyrillic': "Программа завершена с кодом {code}, товарищ!",
        'english': "Program exited with code {code}, pal!",
        'symbolic': "PROCESS_TERMINATED: exit_code={code}"
    }

    ERROR_HEADERS = {
        'ukrainian_latin': "Bida, kozache! Errors found:",
        'ukrainian_cyrillic': "Біда, козаче! Знайдено помилки:",
        'russian_latin': "Beda, tovarisch! Errors found:",
        'russian_cyrillic': "Беда, товарищ! Найдены ошибки:",
        'english': "Oh no, pal! Errors found:",
        'symbolic': "ERROR: Exception detected:"
    }

    PRESS_ENTER_MESSAGES = {
        'ukrainian_latin': "\nPress Enter to exit, kozache...",
        'ukrainian_cyrillic': "\nНатисніть Enter для виходу, козаче...",
        'russian_latin': "\nPress Enter to exit, tovarisch...",
        'russian_cyrillic': "\nНажмите Enter для выхода, товарищ...",
        'english': "\nPress Enter to exit, pal...",
        'symbolic': "\nAWAITING_INPUT: Press Enter to terminate..."
    }

    BOOLEAN_STRINGS = {
    'ukrainian_cyrillic': {True: 'Правда', False: 'Неправда'},
    'russian_cyrillic': {True: 'Правда', False: 'Неправда'},
    'ukrainian_latin': {True: 'Pravda', False: 'Nepravda'},
    'russian_latin': {True: 'Pravda', False: 'Nepravda'},
    'english': {True: 'True', False: 'False'},
    'symbolic': {True: '1', False: '0'}
    }



    @staticmethod
    def get_message(category, dialect, **kwargs):
        messages = getattr(DialectMessages, category, {})
        message = messages.get(dialect, messages.get('english', ''))
        return message.format(**kwargs) if kwargs else message
    
    @staticmethod
    def get_boolean_string(value: bool, dialect: str) -> str:
        dialect = dialect or 'english'
        mapping = DialectMessages.BOOLEAN_STRINGS.get(dialect, DialectMessages.BOOLEAN_STRINGS['english'])
        return mapping[value]
    
    @staticmethod
    def friendly_term(dialect: str) -> str:
        return DialectMessages.FRIENDLY_TERMS.get(dialect or 'english', 'pal')