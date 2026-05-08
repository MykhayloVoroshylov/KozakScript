"""Dialect-specific messages for KozakScript"""
import re

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


    HINTS = {
        # Pattern key → per-dialect hint text
        'semicolon': {
            'ukrainian_latin':   "Pidkazka: Navit' borshch potrebuye lozhy, kozache! Tviy kod potrebuye krapku z komoyu.",
            'ukrainian_cyrillic':"Підказка: Навіть борщ потребує ложки, козаче! Твій код потребує крапку з комою.",
            'russian_latin':     "Podskazka: Dazhe borshch nuzhdayetsya v lozhke, tovarisch! Tvoy kod nuzhdayetsya v tochke s zapyatoy.",
            'russian_cyrillic':  "Подсказка: Даже борщ нуждается в ложке, товарищ! Твой код нуждается в точке с запятой.",
            'symbolic':          "SYNTAX_HINT: Terminator token ';' missing.",
            'english':           "Hint: Even borshch needs a spoon, pal! Your code needs a semicolon.",
        },
        'not_defined': {
            'ukrainian_latin':   "Pidkazka: Ty namahayesh'sya yikhaty na koni, yakoho nema, kozache!",
            'ukrainian_cyrillic':"Підказка: Ти намагаєшся їхати на коні, якого немає, козаче!",
            'russian_latin':     "Podskazka: Ty pytayesh'sya yekhat' na kone, kotorogo net, tovarisch!",
            'russian_cyrillic':  "Подсказка: Ты пытаешься ехать на коне, которого нет, товарищ!",
            'symbolic':          "REFERENCE_HINT: Identifier not found in scope.",
            'english':           "Hint: You're trying to ride a horse that isn't there, pal!",
        },
        'divide_by_zero': {
            'ukrainian_latin':   "Pidkazka: Dilenyya na nul'? Kozats'ka mahiya ne mozhe zlamaty matematyku, vybachay.",
            'ukrainian_cyrillic':"Підказка: Ділення на нуль? Козацька магія не може зламати математику, вибач.",
            'russian_latin':     "Podskazka: Deleniye na nul'? Kazatskaya magiya ne mozhet slomat' matematiku, izvini.",
            'russian_cyrillic':  "Подсказка: Деление на ноль? Казацкая магия не может сломать математику, извини.",
            'symbolic':          "MATH_HINT: Division by zero is undefined.",
            'english':           "Hint: Dividing by zero? Kozak magic cannot break math, sorry.",
        },
        'array_bounds': {
            'ukrainian_latin':   "Pidkazka: Ty shukayesh varennyky za mezhamy kastrulli, kozache!",
            'ukrainian_cyrillic':"Підказка: Ти шукаєш вареники за межами каструлі, козаче!",
            'russian_latin':     "Podskazka: Ty ishchesh' pel'meni za predelami kast ryuli, tovarisch!",
            'russian_cyrillic':  "Подсказка: Ты ищешь пельмени за пределами кастрюли, товарищ!",
            'symbolic':          "BOUNDS_HINT: Index exceeds array range.",
            'english':           "Hint: You're searching for varenyky outside the pot, pal!",
        },
        'function_not_defined': {
            'ukrainian_latin':   "Pidkazka: Funktsiyu ne znaydeno! Mozhlyvо, vona pishla na viynu bez poperedzhennya.",
            'ukrainian_cyrillic':"Підказка: Функцію не знайдено! Можливо, вона пішла на війну без попередження.",
            'russian_latin':     "Podskazka: Funktsiya ne naydena! Vozmozhno, ona ushla na voynu bez preduprezhdeniya.",
            'russian_cyrillic':  "Подсказка: Функция не найдена! Возможно, она ушла на войну без предупреждения.",
            'symbolic':          "REFERENCE_HINT: Function identifier not found in scope.",
            'english':           "Hint: Function not found! Maybe it went to war without telling you.",
        },
    }

    RUNTIME_ERRORS = {
        'variable_not_defined': {
            'ukrainian_latin':   "Zminnu '{name}' ne vyznacheno",
            'ukrainian_cyrillic':"Змінну '{name}' не визначено",
            'russian_latin':     "Peremennaya '{name}' ne opredelena",
            'russian_cyrillic':  "Переменная '{name}' не определена",
            'symbolic':          "UNDEFINED: '{name}'",
            'english':           "Variable '{name}' is not defined",
        },
        'divide_by_zero': {
            'ukrainian_latin':   "Ne mozhna dilyty na nul'",
            'ukrainian_cyrillic':"Не можна ділити на нуль",
            'russian_latin':     "Nel'zya delit' na nol'",
            'russian_cyrillic':  "Нельзя делить на ноль",
            'symbolic':          "MATH_ERROR: division_by_zero",
            'english':           "Cannot divide by zero",
        },
        'array_bounds': {
            'ukrainian_latin':   "Indeks masyvu za mezhamy",
            'ukrainian_cyrillic':"Індекс масиву за межами",
            'russian_latin':     "Indeks massiva vykhodit za granitsy",
            'russian_cyrillic':  "Индекс массива выходит за границы",
            'symbolic':          "ERROR: array_index_out_of_bounds",
            'english':           "Array index out of bounds",
        },
        'type_mismatch': {
            'ukrainian_latin':   "Neviddpovidnist' typiv dlya '{name}': ochikuvavsya {expected}, otrymano {actual}",
            'ukrainian_cyrillic':"Невідповідність типів для '{name}': очікувався {expected}, отримано {actual}",
            'russian_latin':     "Nesootvetstviye tipov dlya '{name}': ozhidalsya {expected}, polucheno {actual}",
            'russian_cyrillic':  "Несоответствие типов для '{name}': ожидался {expected}, получено {actual}",
            'symbolic':          "TYPE_ERROR: '{name}' expected={expected} got={actual}",
            'english':           "Type mismatch for '{name}': expected {expected}, got {actual}",
        },
    }

    @staticmethod
    def runtime_error(key: str, dialect: str, **kwargs) -> str:
        dialect = dialect or 'english'
        templates = DialectMessages.RUNTIME_ERRORS.get(key, {})
        template = templates.get(dialect, templates.get('english', key))
        return template.format(**kwargs) if kwargs else template

    # Maps regex patterns to hint keys — patterns always match English internal strings
    HINT_PATTERNS = {
        r"Expected SEMICOLON":      'semicolon',
        r"not defined":             'not_defined',
        r"divide by zero":          'divide_by_zero',
        r"array index out of bounds": 'array_bounds',
        r"function '.*' is not defined": 'function_not_defined',
    }

    @staticmethod
    def get_hint(error_text: str, dialect: str) -> str | None:
        """Return a localized hint for the given error text, or None if no hint matches."""
        dialect = dialect or 'english'
        for pattern, hint_key in DialectMessages.HINT_PATTERNS.items():
            if re.search(pattern, error_text, re.IGNORECASE):
                hints = DialectMessages.HINTS.get(hint_key, {})
                return hints.get(dialect, hints.get('english', ''))
        return None



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