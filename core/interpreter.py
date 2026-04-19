"""Interpreter for KozakScript"""
import random
import string
import sys 
import os
from core.parser import Parser
from core.modules.hash import HashModule
from core.modules.math_module import MathModule
from core.modules.game_module import GameModule
from core.lexer import KEYWORD_TRANSLATIONS
from core.dialect_messages import DialectMessages


from core import oop

from core.ast import (
    KozakNumber,
    KozakUnaryOp,
    KozakVariable,
    KozakBinOp,
    KozakAssign,
    KozakProgram,
    KozakEcho,
    KozakString,
    KozakInput,
    KozakBoolean,
    KozakComparisonOp,
    KozakIf,
    KozakWhile,
    KozakFor,
    KozakFunctionCall,
    KozakFunctionDef,
    KozakReturn,
    KozakArrayIndex,
    KozakArray,
    KozakTypeCast,
    KozakForEach,
    KozakClass,
    KozakNewInstance,
    KozakPropertyAccess,
    KozakPropertyAssign,
    KozakDictionary,
    KozakDictionaryAccess,
    KozakThrow,
    KozakTry,
    KozakExit,
    KozakImport,
    KozakSuper,
    KozakDestructor,

)

MODULE_NAME_TRANSLATIONS = {
    'game': 'game',
    'gra': 'game',
    'igra': 'game',
    'гра': 'game',
    'игра': 'game',

    'math': 'math',
    'matematyka': 'math', 
    'matematika': 'math', 
    'математика': 'math', 

    'hash': 'hash',
    'хеш': 'hash',
}
class DialectChecker:
    """Walks the AST before execution and reports all dialect violations up front."""

    # Mirror of GameModule.METHOD_DIALECTS — kept here to avoid instantiating pygame
    GAME_METHOD_DIALECTS = {
        'stvoryty_vikno': 'ukrainian_latin', 'vstanovyty_ikonku': 'ukrainian_latin',
        'onovyty': 'ukrainian_latin', 'vstanovyty_fps': 'ukrainian_latin',
        'zalyty': 'ukrainian_latin', 'namalyuvaty_pryamokutnyk': 'ukrainian_latin',
        'namalyuvaty_kolo': 'ukrainian_latin', 'namalyuvaty_liniyu': 'ukrainian_latin',
        'klavisha_natysnuta': 'ukrainian_latin', 'pozytsiya_myshi': 'ukrainian_latin',
        'mysha_natysnuta': 'ukrainian_latin', 'napysaty_tekst': 'ukrainian_latin',
        'zavantazhyty_zobrazhennya': 'ukrainian_latin', 'namalyuvaty_zobrazhennya': 'ukrainian_latin',
        'zavantazhyty_zvuk': 'ukrainian_latin', 'vidtvoryty_zvuk': 'ukrainian_latin',
        'zakryty': 'ukrainian_latin',

        'create_window': 'english', 'set_icon': 'english', 'update': 'english',
        'set_fps': 'english', 'fill': 'english', 'draw_rect': 'english',
        'draw_circle': 'english', 'draw_line': 'english', 'key_pressed': 'english',
        'mouse_position': 'english', 'mouse_pressed': 'english', 'draw_text': 'english',
        'load_image': 'english', 'draw_image': 'english', 'load_sound': 'english',
        'play_sound': 'english', 'close': 'english',

        'sozdat_okno': 'russian_latin', 'ustanovit_ikonku': 'russian_latin',
        'obnovit': 'russian_latin', 'ustanovit_fps': 'russian_latin',
        'zalit': 'russian_latin', 'narisovat_pryamougolnik': 'russian_latin',
        'narisovat_krug': 'russian_latin', 'narisovat_liniyu': 'russian_latin',
        'klavisha_nazhata': 'russian_latin', 'pozitsiya_myshi': 'russian_latin',
        'mysh_nazhata': 'russian_latin', 'napisat_tekst': 'russian_latin',
        'zagruzit_izobrazhenie': 'russian_latin', 'narisovat_izobrazhenie': 'russian_latin',
        'zagruzit_zvuk': 'russian_latin', 'vosproizvesti_zvuk': 'russian_latin',
        'zakryt': 'russian_latin',

        'створити_вікно': 'ukrainian_cyrillic', 'встановити_іконку': 'ukrainian_cyrillic',
        'оновити': 'ukrainian_cyrillic', 'встановити_фпс': 'ukrainian_cyrillic',
        'залити': 'ukrainian_cyrillic', 'намалювати_прямокутник': 'ukrainian_cyrillic',
        'намалювати_коло': 'ukrainian_cyrillic', 'намалювати_лінію': 'ukrainian_cyrillic',
        'клавіша_натиснута': 'ukrainian_cyrillic', 'позиція_миші': 'ukrainian_cyrillic',
        'миша_натиснута': 'ukrainian_cyrillic', 'написати_текст': 'ukrainian_cyrillic',
        'завантажити_зображення': 'ukrainian_cyrillic', 'намалювати_зображення': 'ukrainian_cyrillic',
        'завантажити_звук': 'ukrainian_cyrillic', 'відтворити_звук': 'ukrainian_cyrillic',
        'закрити': 'ukrainian_cyrillic',

        'создать_окно': 'russian_cyrillic', 'установить_иконку': 'russian_cyrillic',
        'обновить': 'russian_cyrillic', 'установить_фпс': 'russian_cyrillic',
        'залить': 'russian_cyrillic', 'нарисовать_прямоугольник': 'russian_cyrillic',
        'нарисовать_круг': 'russian_cyrillic', 'нарисовать_линию': 'russian_cyrillic',
        'клавиша_нажата': 'russian_cyrillic', 'позиция_мыши': 'russian_cyrillic',
        'мышь_нажата': 'russian_cyrillic', 'написать_текст': 'russian_cyrillic',
        'загрузить_изображение': 'russian_cyrillic', 'нарисовать_изображение': 'russian_cyrillic',
        'загрузить_звук': 'russian_cyrillic', 'воспроизвести_звук': 'russian_cyrillic',
        'закрыть': 'russian_cyrillic',
    }

    GAME_COLOUR_DIALECTS = {
        'ZELENYY': 'shared_latin', 'FIOLETOVYY': 'shared_latin',
        'CHORNYY': 'ukrainian_latin', 'BILYY': 'ukrainian_latin',
        'CHERVONYY': 'ukrainian_latin', 'SYNIY': 'ukrainian_latin',
        'ZHOVTYY': 'ukrainian_latin', 'POMARANCHEVYY': 'ukrainian_latin',
        'SIRYY': 'ukrainian_latin',
        'CHERNYY': 'russian_latin', 'BELYY': 'russian_latin',
        'KRASNYY': 'russian_latin', 'SINIY': 'russian_latin',
        'ZHELTYY': 'russian_latin', 'ORANZHEVYY': 'russian_latin',
        'SERYY': 'russian_latin',
        'ЧОРНИЙ': 'ukrainian_cyrillic', 'БІЛИЙ': 'ukrainian_cyrillic',
        'ЧЕРВОНИЙ': 'ukrainian_cyrillic', 'ЗЕЛЕНИЙ': 'ukrainian_cyrillic',
        'СИНІЙ': 'ukrainian_cyrillic', 'ЖОВТИЙ': 'ukrainian_cyrillic',
        'ПОМАРАНЧЕВИЙ': 'ukrainian_cyrillic', 'ФІОЛЕТОВИЙ': 'ukrainian_cyrillic',
        'СІРИЙ': 'ukrainian_cyrillic',
        'ЧЕРНЫЙ': 'russian_cyrillic', 'БЕЛЫЙ': 'russian_cyrillic',
        'КРАСНЫЙ': 'russian_cyrillic', 'ЗЕЛЕНЫЙ': 'russian_cyrillic',
        'СИНИЙ': 'russian_cyrillic', 'ЖЕЛТЫЙ': 'russian_cyrillic',
        'ОРАНЖЕВЫЙ': 'russian_cyrillic', 'ФИОЛЕТОВЫЙ': 'russian_cyrillic',
        'СЕРЫЙ': 'russian_cyrillic',
        'BLACK': 'english', 'WHITE': 'english', 'RED': 'english',
        'GREEN': 'english', 'BLUE': 'english', 'YELLOW': 'english',
        'ORANGE': 'english', 'PURPLE': 'english', 'GRAY': 'english',
    }

    def __init__(self, dialect):
        self.dialect = dialect
        self.effective = 'english' if dialect == 'symbolic' else dialect
        self.errors = []
        # Track which variable names refer to which module (populated on Import nodes)
        self._module_vars = {}  # var_name -> canonical module name e.g. 'game'

    def _is_allowed(self, required):
        if required == self.effective:
            return True
        if required == 'shared_latin' and self.effective in ('ukrainian_latin', 'russian_latin'):
            return True
        return False

    def check(self, node):
        """Recursively walk the AST and collect violations."""
        if node is None:
            return

        if isinstance(node, KozakProgram):
            for stmt in node.statements:
                self.check(stmt)

        elif isinstance(node, KozakImport):
            # Record which variable name maps to which module
            # node.file_path is a KozakString
            if isinstance(node.file_path, KozakString):
                alias = node.file_path.value          # e.g. "gra"
                canonical = MODULE_NAME_TRANSLATIONS.get(alias)
                if canonical:
                    # The variable name in env will be the alias the user typed
                    self._module_vars[alias] = canonical

        elif isinstance(node, KozakFunctionCall):
            # Covers gra.stvoryty_vikno(...) which the parser may emit as a
            # KozakFunctionCall with name "gra.stvoryty_vikno"
            if '.' in node.name:
                var_name, method = node.name.split('.', 1)
                canonical = self._module_vars.get(var_name)
                if canonical == 'game':
                    self._check_game_member(method, node.name)
            for arg in node.arguments:
                self.check(arg)

        elif isinstance(node, KozakPropertyAccess):
            # Covers gra.CHORNYY used as a value
            self._check_property_access(node)

        elif isinstance(node, KozakPropertyAssign):
            self._check_property_access(node)
            self.check(node.value)

        # --- Recurse into all container nodes ---
        elif isinstance(node, (KozakIf,)):
            self.check(node.condition)
            for s in node.body: self.check(s)
            for cond, body in node.else_if_parts:
                self.check(cond)
                for s in body: self.check(s)
            if node.else_part:
                for s in node.else_part: self.check(s)

        elif isinstance(node, KozakWhile):
            self.check(node.condition)
            for s in node.body: self.check(s)

        elif isinstance(node, KozakFor):
            self.check(node.initialization)
            self.check(node.condition)
            self.check(node.step)
            for s in node.body: self.check(s)

        elif isinstance(node, KozakForEach):
            self.check(node.array_expr)
            for s in node.body: self.check(s)

        elif isinstance(node, KozakFunctionDef):
            for s in node.body: self.check(s)

        elif isinstance(node, KozakReturn):
            self.check(node.value)

        elif isinstance(node, KozakEcho):
            for e in node.expressions: self.check(e)

        elif isinstance(node, KozakAssign):
            self.check(node.expr)

        elif isinstance(node, KozakBinOp):
            self.check(node.left)
            self.check(node.right)

        elif isinstance(node, KozakComparisonOp):
            self.check(node.left)
            self.check(node.right)

        elif isinstance(node, KozakUnaryOp):
            self.check(node.target)

        elif isinstance(node, KozakArray):
            for e in node.elements: self.check(e)

        elif isinstance(node, KozakDictionary):
            for k, v in node.pairs: self.check(v)

        elif isinstance(node, KozakTry):
            for s in node.try_body: self.check(s)
            for _, body in node.catch_clauses:
                for s in body: self.check(s)
            if node.finally_body:
                for s in node.finally_body: self.check(s)

        elif isinstance(node, KozakClass):
            for method in node.methods.values(): self.check(method)

        elif isinstance(node, KozakNewInstance):
            for a in node.arguments: self.check(a)

    def _check_property_access(self, node):
        """Check a property/method access on a module variable."""
        # node.instance is typically a KozakVariable
        if not isinstance(node.instance, KozakVariable):
            return
        var_name = node.instance.name
        canonical = self._module_vars.get(var_name)
        if canonical == 'game':
            self._check_game_member(node.property_name, f"{var_name}.{node.property_name}")

    def _check_game_member(self, member_name, full_name):
        """Validate a single game module member name against the dialect."""
        # Check methods
        required = self.GAME_METHOD_DIALECTS.get(member_name)
        if required is None:
            # Check colours
            required = self.GAME_COLOUR_DIALECTS.get(member_name)
        if required is None:
            return  # Unknown member — let runtime handle it

        if not self._is_allowed(required):
            friendly = DialectMessages.friendly_term(self.dialect)
            self.errors.append(
                f"Dialect violation: '{full_name}' belongs to the '{required}' dialect, "
                f"but your program uses '{self.dialect}', {friendly}."
            )

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class RuntimeErrorKozak(Exception):
    def __init__(self, message):
        super().__init__(message)

class ProgramExit(Exception):
    def __init__(self, code=0):
        self.code = code
        super().__init__(f"Program exited with code {code}")

class Interpreter:
    
    def __init__(self, strict_dialect=False, parent_dialect=None):
        self._term = DialectMessages.friendly_term(parent_dialect)
        self.scopes = [{}]
        self.env = {}
        self.functions = {}
        self.class_table = oop.ClassTable()
        self.classes = {} 
        self.exit_code = 0
        self.imported_files = set()
        self.current_file_dir = None
        self.strict_dialect = strict_dialect
        self.parent_dialect = parent_dialect
        self.modules = {
            "hash": HashModule(),
            "math": MathModule(),
            "game": GameModule(dialect=parent_dialect),
            # future modules to come.
        }
        self.globals = self.env
        self.scopes = [{}]
        self.type_constraints = {}
        self.current_function = None

    def _execute_function_body(self, body, local_env, function_name=None):
        """
        Executes a list of statements (a function body) in a given local environment.
        This is necessary for user-defined functions and methods/constructors.
        """
        original_env = self.env
        original_function = self.current_function
        merged_env = {**self.env, **local_env}
        self.env = merged_env
        self.current_function = function_name
        try:
            for stmt in body:
                self.eval(stmt)
            return None 
        except ReturnValue as e:
            return e.value
        finally:
            self.env = original_env
            self.current_function = original_function

    def eval(self, node):
        if isinstance(node, KozakProgram):
            return self._eval_program(node)
        elif isinstance(node, KozakClass):
            return self._eval_ClassNode(node)
        elif isinstance(node, KozakNewInstance):
            # This now reliably calls the correct, unique function defined below.
            return self.eval_NewInstanceNode(node)
        elif isinstance(node, KozakPropertyAccess):
            return self.eval_PropertyAccessNode(node)
        elif isinstance(node, KozakPropertyAssign):
            return self.eval_PropertyAssignNode(node)
        elif isinstance(node, KozakIf):
            return self._eval_if(node)
        elif isinstance(node, KozakWhile):
            return self._eval_while(node)
        elif isinstance(node, KozakFor):
            return self._eval_for(node)
        elif isinstance(node, KozakFunctionDef):
            return self._eval_function_def(node)
        elif isinstance(node, KozakFunctionCall):
            return self._eval_function_call(node)
        elif isinstance(node, KozakUnaryOp):
            return self._eval_unary_op(node)
        elif isinstance(node, KozakAssign):
            return self._eval_assign(node)
        elif isinstance(node, KozakEcho):
            return self._eval_echo(node)
        elif isinstance(node, KozakNumber):
            return self._eval_number(node)
        elif isinstance(node, KozakVariable):
            return self._eval_variable(node)
        elif isinstance(node, KozakBinOp):
            return self._eval_binop(node)
        elif isinstance(node, KozakString):
            return self._eval_string(node)
        elif isinstance(node, KozakInput):
            return self._eval_input(node)
        elif isinstance(node, KozakBoolean):
            return self._eval_boolean(node)
        elif isinstance(node, KozakComparisonOp):
            return self._eval_comparison_op(node)
        elif isinstance(node, KozakTypeCast):
            return self._eval_type_cast(node)
        elif isinstance(node, KozakReturn):
            return_value = self.eval(node.value) if node.value is not None else None
            raise ReturnValue(return_value)
        elif isinstance(node, KozakArray):
            return self._eval_array(node)
        elif isinstance(node, KozakArrayIndex):
            return self._eval_array_index(node)
        elif isinstance(node, KozakForEach):
            return self._eval_for_each(node)
        elif isinstance(node, KozakDictionary):
            return self._eval_dictionary(node)
        elif isinstance(node, KozakDictionaryAccess):
            return self._eval_dictionary_access(node)
        elif isinstance(node, KozakTry):
            return self._eval_try(node)
        elif isinstance(node, KozakThrow):
            return self._eval_throw(node)
        elif isinstance(node, KozakExit):
            return self._eval_exit(node)
        elif isinstance(node, KozakImport):
            return self._eval_import(node)
        elif isinstance(node, KozakSuper):
            return self._eval_super(node)
        else:
            raise RuntimeErrorKozak(f'Unknown node type: {type(node).__name__}')

    def _eval_program(self, node):
        for stmt in node.statements:
           # print(f"DEBUG: Evaluating {type(stmt).__name__}")
            self.eval(stmt)
        

    def _eval_assign(self, node):
        value = self.eval(node.expr)
        if node.type_hint:
            expected = self._normalize_type(node.type_hint)
            actual = type(value).__name__
            if not self._type_matches(actual, expected):
                raise RuntimeErrorKozak(
                    f"Type mismatch for '{node.name}': "
                    f"expected {expected}, got {actual}"
                )
            self.type_constraints[node.name] = expected

        elif node.name in self.type_constraints:
            expected = self.type_constraints[node.name]
            actual = type(value).__name__
            
            if not self._type_matches(actual, expected):
                raise RuntimeErrorKozak(
                    f"Cannot assign {actual} to {expected} variable '{node.name}'"
                )
        if self.current_function and node.name in self.globals and node.name not in locals().get('local_env', {}):
            self.globals[node.name] = value
        else:
            self.env[node.name] = value
    
    def _normalize_type(self, kozak_type):
        """Convert KozakScript type to Python type"""
        mapping = {
            'Chyslo': 'int',
            'DroboveChyslo': 'float',
            'Ryadok': 'str',
            'Logika': 'bool',
            'Число': 'int', 
            'ДробовеЧисло': 'float',
            'ДробноеЧисло': 'float',
            'Рядок': 'str',
            'Строка': 'str',
            'Логіка': 'bool',
            'Логика': 'bool'
        }
        return mapping.get(kozak_type, kozak_type)
    
    def _type_matches(self, actual, expected):
        """Check if actual type matches expected (with flexibility)"""
        if expected == actual:
            return True
        # Allow int where float expected
        if expected == 'float' and actual == 'int':
            return True
        return False

    def stringify(self, value):
        if isinstance(value, bool):
            return DialectMessages.get_boolean_string(value, self.parent_dialect)
        return str(value)

    def _eval_echo(self, node):
        values = []
        for expr in node.expressions:
            value = self.eval(expr)
            if isinstance(value, bool):
                values.append(DialectMessages.get_boolean_string(value, self.parent_dialect))
            else:
                values.append(value)
        print(*values)

    def _eval_number(self, node):
        return (node.value)

    def _eval_variable(self, node):
        if node.name in self.env:
            return self.env[node.name]
        # Check global functions table for variables that might be function references
        if node.name in self.functions:
             return self.functions[node.name]
        raise RuntimeErrorKozak(f'Variable {node.name} is not defined')

    def _eval_binop(self, node):
        left = self.eval(node.left)
        right = self.eval(node.right)
        
        if node.op == '+':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            elif isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            else:
                raise RuntimeErrorKozak(f"Unsupported operand types for +: '{type(left).__name__}' and '{type(right).__name__}'")
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            if right == 0:
                raise RuntimeErrorKozak(f"Cannot divide by zero, {self._term}.")
            return left / right
        elif node.op == '%':
            return left % right
        elif node.op == '//':
            return left // right
        elif node.op == '^':
            return left ** right
        elif node.op == '^/':
            if right == 0:
                raise RuntimeErrorKozak("Root exponent cannot be zero!")
            return left ** (1 / right)
        elif node.op == '&&':
            return left and right
        elif node.op == '||':
            return left or right
        else:
            raise RuntimeErrorKozak(f'Unknown operator: {node.op}')

    def _eval_string(self, node):
        return node.value

    def _eval_input(self, node):
        prompt_value = self.eval(node.expr)
        user_input = input(str(prompt_value))
        return user_input
    
    def _eval_boolean(self, node):
        return node.value

    def _eval_comparison_op(self, node):
        left = self.eval(node.left)
        right = self.eval(node.right)
        if node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            return left < right
        elif node.op == '>':
            return left > right
        elif node.op == '<=':
            return left <= right
        elif node.op == '>=':
            return left >= right
        
    def _eval_type_cast(self, node):
        value = self.eval(node.expr)
        
        if node.target_type == 'Chyslo':
            try:
                return int(value)
            except (ValueError, TypeError):
                raise RuntimeErrorKozak(f"Cannot cast '{value}' to 'Int'.")
        elif node.target_type == 'DroboveChyslo':
            try:
                return float(value)
            except (ValueError, TypeError):
                raise RuntimeErrorKozak(f"Cannot cast '{value}' to 'Float'.")
        elif node.target_type == 'Ryadok':
            return str(value)
        elif node.target_type == 'Logika':
            if isinstance(value, str):
                if value.lower() == 'pravda':
                    return True
                if value.lower() == 'nepravda':
                    return False
            return bool(value)
        else:
            raise RuntimeErrorKozak(f"Unknown type cast: {node.target_type}")
    
    def _eval_if(self, node):
        if self.eval(node.condition):
            for stmt in node.body:
                self.eval(stmt)
            return

        for else_if_condition, else_if_body in node.else_if_parts:
            if self.eval(else_if_condition):
                for stmt in else_if_body:
                    self.eval(stmt)
                return

        if node.else_part:
            for stmt in node.else_part:
                self.eval(stmt)

    def _eval_while(self, node):
        while self.eval(node.condition):
            for stmt in node.body:
                self.eval(stmt)

    def _eval_unary_op(self, node):
        if not isinstance(node.target, KozakVariable):
            raise RuntimeErrorKozak("Unary operators '++'/'--' only supported on simple variables.")
            
        var_name = node.target.name
        if var_name not in self.env:
             raise RuntimeErrorKozak(f'Variable {var_name} is not defined for unary operation.')

        current_value = self.env[var_name]
        
        if node.op == '++':
            if not isinstance(current_value, (int, float)):
                 raise RuntimeErrorKozak(f"Cannot increment non-numeric variable '{var_name}'.")
            self.env[var_name] = current_value + 1
        elif node.op == '--':
            if not isinstance(current_value, (int, float)):
                 raise RuntimeErrorKozak(f"Cannot decrement non-numeric variable '{var_name}'.")
            self.env[var_name] = current_value - 1
        else:
             raise RuntimeErrorKozak(f'Unknown unary operator: {node.op}')
        
    def _eval_for(self, node):
        self.eval(node.initialization)
        
        while self.eval(node.condition):
            for stmt in node.body:
                self.eval(stmt)
            self.eval(node.step)
    
    def _eval_function_def(self, node):
        self.functions[node.name] = node


    def _eval_function_call(self, node):

        if '.' in node.name:
            parts = node.name.split('.', 1)
            if len(parts) == 2:
                first_part, method_name = parts
                
                # Check if first_part is a module
                if first_part in self.modules:
                    module = self.modules[first_part]
                    if hasattr(module, method_name):
                        method = getattr(module, method_name)
                        evaluated_args = [self.eval(arg_node) for arg_node in node.arguments]
                        return method(*evaluated_args)
                    else:
                        raise RuntimeErrorKozak(f"Module '{first_part}' has no method '{method_name}', {self._term}.")


        if '.' in node.name:
            parts = node.name.split('.', 1)
            if len(parts) == 2:
                potential_class, method_name = parts
                
                # Check if this is a class name
                try:
                    class_def = self.class_table.get_class(potential_class)
                    
                    # Check if method is static
                    if method_name in class_def.static_methods:
                        method_def = class_def.static_methods[method_name]
                        evaluated_args = [self.eval(arg_node) for arg_node in node.arguments]
                        
                        if len(evaluated_args) != len(method_def.parameters):
                            raise RuntimeErrorKozak(
                                f"Static method '{method_name}' expected "
                                f"{len(method_def.parameters)} arguments, "
                                f"but got {len(evaluated_args)}"
                            )
                        
                        # Execute without 'this' context
                        local_env = {}
                        for param, arg_val in zip(method_def.parameters, evaluated_args):
                            local_env[param] = arg_val
                        
                        return self._execute_function_body(
                            method_def.body, 
                            local_env, 
                            function_name=method_name
                        )
                except:
                    pass  
        
        if node.name in ('Znyshchyty', 'Destructor', 'Unichtozhit', '@~', 'Знищити', 'Уничтожить'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'Destructor' expects exactly 1 argument, {self._term}.")
            obj = self.eval(node.arguments[0])
            if not isinstance(obj, oop.Instance):
                raise RuntimeErrorKozak(f"Can only destroy object instances, {self._term}.")
            obj.destroy(self)
            return None
        
        if node.name in ('Velyki', 'Upper', 'Zaglavnye', '^str', 'Великі', 'Заглавные'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'Upper' expects exactly 1 argument, {self._term}.")
            string = self.eval(node.arguments[0])
            if not isinstance(string, str):
                raise RuntimeErrorKozak(f"Argument for 'Upper' must be a string, {self._term}.")
            return string.upper()
        
        if node.name in ('Mali', 'Lower', 'Strochnye', '_str', 'Малі', 'Строчные'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'Lower' expects exactly 1 argument, {self._term}.")
            string = self.eval(node.arguments[0])
            if not isinstance(string, str):
                raise RuntimeErrorKozak(f"Argument for 'Lower' must be a string, {self._term}.")
            return string.lower()
        
        if node.name in ('Zaminyty', 'Replace', 'Zamenit', 'str->', 'Заменить', 'Замінити'):
            if len(node.arguments) != 3:
                raise RuntimeErrorKozak(f"Function 'Replace' expects exactly 3 arguments, {self._term}.")
            string = self.eval(node.arguments[0])
            old = self.eval(node.arguments[1])
            new = self.eval(node.arguments[2])
            if not isinstance(string, str):
                raise RuntimeErrorKozak(f"First argument for 'Replace' must be a string, {self._term}.")
            return string.replace(str(old), str(new))
        
        if node.name in ('Rozdilyty', 'Split', 'Razdelit', 'str//', 'Розділити', 'Разделить'):
            if len(node.arguments) not in (1,2):
                raise RuntimeErrorKozak(f"Function 'Split' expects 1 or 2 arguments, {self._term}.")
            string = self.eval(node.arguments[0])
            delimiter = self.eval(node.arguments[1]) if len(node.arguments) == 2 else ' '
            if not isinstance(string, str):
                raise RuntimeErrorKozak(f"First argument for 'Split' must be a string, {self._term}.")
            return string.split(str(delimiter))
        
        if node.name in ('Obrizaty', 'Strip', 'Obrezat', 'str--', 'Обрезать', 'Обрізати'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'strip' expects 1 argument, {self._term}.")
            string = self.eval(node.arguments[0])
            if not isinstance(string, str):
                raise RuntimeErrorKozak(f"Argument must be a string, {self._term}.")
            return string.strip()
        
        if node.name in ('znayty', 'find', 'nayti', 'str?','знайти', 'найти'):
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'find' expects 2 arguments (string, substring), {self._term}.")
            string = self.eval(node.arguments[0])
            substring = self.eval(node.arguments[1])
            if not isinstance(string, str):
                raise RuntimeErrorKozak(f"First argument must be a string, {self._term}.")
            return string.find(str(substring))
        
        if node.name in ('pidstrichka', 'substring', 'podstroka', 's[]', 'підстрічка', 'подстрока'):
            if len(node.arguments) not in (2, 3):
                raise RuntimeErrorKozak(f"Function 'substring' expects 2 or 3 arguments, {self._term}.")
            string = self.eval(node.arguments[0])
            start = self.eval(node.arguments[1])
            end = self.eval(node.arguments[2]) if len(node.arguments) == 3 else len(string)
            if not isinstance(string, str):
                raise RuntimeErrorKozak(f"First argument must be a string, {self._term}.")
            if not isinstance(start, int) or not isinstance(end, int):
                raise RuntimeErrorKozak(f"Indices must be integers, {self._term}.")
            return string[start:end]

                    
        if node.name in ('create_matrix', 'stvoryty_matrytsyu', 'sozdat_matritsu', '@[]', 'створити_матрицю', 'создать_матрицу'):
            if len(node.arguments) not in (2, 3):
                raise RuntimeErrorKozak(f"Function 'create_matrix' expects 2 or 3 arguments (rows, cols, [fill_value]), {self._term}.")
            
            rows = self.eval(node.arguments[0])
            cols = self.eval(node.arguments[1])
            fill_value = self.eval(node.arguments[2]) if len(node.arguments) == 3 else 0
            
            if not isinstance(rows, int) or not isinstance(cols, int):
                raise RuntimeErrorKozak(f"Rows and columns must be integers, {self._term}.")
            if rows <= 0 or cols <= 0:
                raise RuntimeErrorKozak(f"Matrix dimensions must be positive, {self._term}.")
            
            return [[fill_value for _ in range(cols)] for _ in range(rows)]
        
        # Get matrix dimensions
        if node.name in ('matrix_size', 'rozmir_matrytsi', 'razmer_matritsy', '#[]', 'розмір_матриці', 'размер_матрицы'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'matrix_size' expects 1 argument, {self._term}.")
            
            matrix = self.eval(node.arguments[0])
            if not isinstance(matrix, list):
                raise RuntimeErrorKozak(f"Argument must be an array, {self._term}.")
            
            if not matrix or not isinstance(matrix[0], list):
                return [len(matrix), 0]  # 1D array or empty
            
            return [len(matrix), len(matrix[0])]
        
        # Flatten a multidimensional array
        if node.name in ('flatten', 'splushchyty', 'spluschit', '[]>', 'сплющити', 'сплющить'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'flatten' expects 1 argument, {self._term}.")
            
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"Argument must be an array, {self._term}.")
            
            def flatten_recursive(lst):
                result = []
                for item in lst:
                    if isinstance(item, list):
                        result.extend(flatten_recursive(item))
                    else:
                        result.append(item)
                return result
            
            return flatten_recursive(arr)
        
        # Transpose a 2D matrix
        if node.name in ('transpose', 'transportuvaty', 'transportirovat', '[]^', 'транспортувати', 'транспортировать'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'transpose' expects 1 argument, {self._term}.")
            
            matrix = self.eval(node.arguments[0])
            if not isinstance(matrix, list) or not matrix:
                raise RuntimeErrorKozak(f"Argument must be a non-empty array, {self._term}.")
            
            if not all(isinstance(row, list) for row in matrix):
                raise RuntimeErrorKozak(f"Argument must be a 2D array, {self._term}.")
            
            # Check all rows have same length
            if not all(len(row) == len(matrix[0]) for row in matrix):
                raise RuntimeErrorKozak(f"All rows must have the same length for transpose, {self._term}.")
            
            return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
        
        # Get row from matrix
        if node.name in ('get_row', 'otrymaty_ryadok', 'poluchit_stroku', '[]->', 'отримати_рядок', 'получить_строку'):
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'get_row' expects 2 arguments (matrix, row_index), {self._term}.")
            
            matrix = self.eval(node.arguments[0])
            row_idx = self.eval(node.arguments[1])
            
            if not isinstance(matrix, list):
                raise RuntimeErrorKozak(f"First argument must be an array, {self._term}.")
            if not isinstance(row_idx, int):
                raise RuntimeErrorKozak(f"Row index must be an integer, {self._term}.")
            if row_idx < 0 or row_idx >= len(matrix):
                raise RuntimeErrorKozak(f"Row index out of bounds, {self._term}.")
            
            return matrix[row_idx]
        
        # Get column from matrix
        if node.name in ('get_col', 'otrymaty_stovpets', 'poluchit_stolbets', '[]|', 'отримати_стовпець', 'получить_столбец'):
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'get_col' expects 2 arguments (matrix, col_index), {self._term}.")
            
            matrix = self.eval(node.arguments[0])
            col_idx = self.eval(node.arguments[1])
            
            if not isinstance(matrix, list) or not matrix:
                raise RuntimeErrorKozak(f"First argument must be a non-empty array, {self._term}.")
            if not isinstance(col_idx, int):
                raise RuntimeErrorKozak(f"Column index must be an integer, {self._term}.")
            
            if not all(isinstance(row, list) for row in matrix):
                raise RuntimeErrorKozak(f"Argument must be a 2D array, {self._term}.")
            
            if col_idx < 0 or (matrix and col_idx >= len(matrix[0])):
                raise RuntimeErrorKozak(f"Column index out of bounds, {self._term}.")
            
            return [row[col_idx] for row in matrix]
        
        # Set value at position in multidimensional array
        if node.name in ('set_at', 'vstanovyty_na', 'ustanovit_na', '[]:=', "встановити_на", "установить_на"):
            if len(node.arguments) < 3:
                raise RuntimeErrorKozak(f"Function 'set_at' expects at least 3 arguments (array, indices..., value), {self._term}.")
            
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"First argument must be an array, {self._term}.")
            
            # All arguments except last are indices, last is the value
            indices = [self.eval(node.arguments[i]) for i in range(1, len(node.arguments) - 1)]
            value = self.eval(node.arguments[-1])
            
            # Navigate to the target position
            current = arr
            for i, idx in enumerate(indices[:-1]):
                if not isinstance(idx, int):
                    raise RuntimeErrorKozak(f"Index {i+1} must be an integer, {self._term}.")
                if idx < 0 or idx >= len(current):
                    raise RuntimeErrorKozak(f"Index {i+1} out of bounds, {self._term}.")
                current = current[idx]
            
            # Set the final value
            last_idx = indices[-1]
            if not isinstance(last_idx, int):
                raise RuntimeErrorKozak(f"Last index must be an integer, {self._term}.")
            if last_idx < 0 or last_idx >= len(current):
                raise RuntimeErrorKozak(f"Last index out of bounds, {self._term}.")
            
            current[last_idx] = value
            return None

        
        if node.name == 'remove_key' or node.name == 'vydalyty_klyuch' or node.name == 'udalit_klyuch' or node.name == 'vydalyty_klyuch_sym' or node.name == 'видалити_ключ' or node.name == 'удалить_ключ':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'remove_key' expects exactly 2 arguments (dictionary, key), {self._term}.")
            
            dictionary = self.eval(node.arguments[0])
            key = self.eval(node.arguments[1])
            
            return self._kozak_remove_key(dictionary, key)

        if node.name == 'insert' or node.name == 'vstavyty' or node.name == 'vstavit' or node.name == '+:' or node.name == 'вставити' or node.name == 'вставить':
            if len(node.arguments) != 3:
                raise RuntimeErrorKozak(f"Function 'insert' expects exactly 3 arguments, {self._term}.")
            arr = self.eval(node.arguments[0])
            index = self.eval(node.arguments[1])
            value = self.eval(node.arguments[2])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"First argument of 'insert' must be an array, {self._term}.")
            if not isinstance(index, int):
                raise RuntimeErrorKozak(f"Second argument of 'insert' must be an integer, {self._term}.")
            if index < 0 or index > len(arr):
                raise RuntimeErrorKozak(f"Array index out of bounds, {self._term}.")
            arr.insert(index, value)
            return None
        
        if node.name == 'append' or node.name == 'dodaty' or node.name == 'dobavit' or node.name == '+<' or node.name == 'додати' or node.name == 'добавить':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'append' expects exactly 2 arguments, {self._term}.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"First argument of 'append' must be an array, {self._term}.")
            arr.append(value)
            return None

        if node.name == 'index_of' or node.name == 'index_z' or node.name == 'index_znachenia' or node.name == '?:' or node.name == 'индекс_з' or node.name == 'индекс_значения':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'index_of' expects exactly 2 arguments, {self._term}.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"First argument of 'index_of' must be an array, {self._term}.")
            try:
                return arr.index(value)
            except ValueError:
                return -1

        if node.name == 'contains' or node.name == 'mistyt' or node.name == 'soderzhit' or node.name == '?^' or node.name == 'містить' or node.name == 'содержит':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'contains' expects exactly 2 arguments, {self._term}.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"First argument of 'contains' must be an array, {self._term}.")
            return value in arr

        if node.name == 'slice' or node.name == 'vyrizaty' or node.name == 'vyrezat' or node.name == '[..]' or node.name == 'вырезать' or node.name == 'вирізати':
            if len(node.arguments) not in (2, 3):
                raise RuntimeErrorKozak(f"Function 'slice' expects 2 or 3 arguments, {self._term}.")
            arr = self.eval(node.arguments[0])
            start = self.eval(node.arguments[1])
            end = self.eval(node.arguments[2]) if len(node.arguments) == 3 else None
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"First argument of 'slice' must be an array, {self._term}.")
            if not isinstance(start, int) or (end is not None and not isinstance(end, int)):
                raise RuntimeErrorKozak(f"Start and end arguments must be integers, {self._term}.")
            return arr[start:end]

        if node.name == 'clear' or node.name == 'ochystyty' or node.name == 'ochistit' or node.name == '--<' or node.name == 'очистити' or node.name == 'очистить':
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'clear' expects exactly 1 argument, {self._term}.")
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"Argument of 'clear' must be an array, {self._term}.")
            arr.clear()
            return None

        if node.name == 'pop' or node.name == 'vyinyaty' or node.name == 'vytaschit' or node.name == '-<!' or node.name == 'вийняти' or node.name == 'вытащить':
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'pop' expects exactly 1 argument, {self._term}.")
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"Argument of 'pop' must be an array, {self._term}.")
            if not arr:
                raise RuntimeErrorKozak(f"Cannot pop from empty array, {self._term}.")
            return arr.pop()

        if node.name == 'remove' or node.name == 'vydalyty' or node.name == 'udalit' or node.name == '-<' or node.name == 'видалити' or node.name == 'удалить':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'remove' expects exactly 2 arguments, {self._term}.")
            arr = self.eval(node.arguments[0])
            index = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak(f"First argument of 'remove' must be an array, {self._term}.")
            if not isinstance(index, int):
                raise RuntimeErrorKozak(f"Second argument of 'remove' must be an integer, {self._term}.")
            if index < 0 or index >= len(arr):
                raise RuntimeErrorKozak(f"Array index out of bounds, {self._term}.")
            arr.pop(index)
            return None

        
        if node.name in ('Zapysaty', 'Write', 'Zapisat', '=>', 'Записати', 'Записать'):
            if len(node.arguments) < 2 or len(node.arguments) > 3:
                raise RuntimeErrorKozak(f"Function 'Write' expects 2 or 3 arguments, {self._term}.")
            file_name = self.eval(node.arguments[0])
            content = self.eval(node.arguments[1])
            append_mode = False
            if len(node.arguments) == 3:
                append_mode = bool(self.eval(node.arguments[2]))
            
            if not isinstance(file_name, str):
                raise RuntimeErrorKozak(f"First argument for 'Write' (file name) must be a string, {self._term}.")
            
            mode = 'a' if append_mode else 'w'
            try:
                with open(file_name, mode, encoding='utf-8') as f:
                    f.write(str(content))
                return None
            except IOError as e:
                raise RuntimeErrorKozak(f"File writing error: {e}")


        if node.name in ('Chytaty', 'Read', 'Chitat', '=<'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'Read' expects exactly 1 argument, {self._term}.")
            file_name = self.eval(node.arguments[0])
            if not isinstance(file_name, str):
                raise RuntimeErrorKozak(f"Argument for 'Read' must be a string, {self._term}.")
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                raise RuntimeErrorKozak(f"File '{file_name}' not found, {self._term}.")
            except IOError as e:
                raise RuntimeErrorKozak(f"File reading error: {e}")


        if node.name in ('dovzhyna', 'length', 'dlinna', '___'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'length' expects exactly 1 argument, {self._term}.")
            arg = self.eval(node.arguments[0])
            if not isinstance(arg, (list, str, tuple)):
                raise RuntimeErrorKozak(f"Argument for 'length' must be an array or a string, {self._term}.")
            return len(arg)
        
        if node.name == 'randint':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'randint' expects exactly 2 arguments, {self._term}.")
            start = self.eval(node.arguments[0])
            end = self.eval(node.arguments[1])
            if not isinstance(start, int) or not isinstance(end, int):
                raise RuntimeErrorKozak(f"Arguments for 'randint' must be integers, {self._term}.")
            return random.randint(start, end)

        if node.name == 'klyuchi' or node.name == 'keys' or node.name == 'k{}' or node.name == 'klyuchi_sym':  # keys
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'keys' expects exactly 1 argument, {self._term}.")
            dictionary = self.eval(node.arguments[0])
            if not isinstance(dictionary, dict):
                raise RuntimeErrorKozak(f"Argument must be a dictionary, {self._term}.")
            return list(dictionary.keys())

        if node.name == 'znachennya' or node.name == 'values' or node.name=='znachennie' or node.name == 'znachennya_sym':  # values
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak(f"Function 'values' expects exactly 1 argument, {self._term}.")
            dictionary = self.eval(node.arguments[0])
            if not isinstance(dictionary, dict):
                raise RuntimeErrorKozak(f"Argument must be a dictionary, {self._term}.")
            return list(dictionary.values())

        if node.name == 'maye_klyuch' or node.name == 'has_key' or node.name == 'imeet_klyuch' or node.name == '?k':  # has_key
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak(f"Function 'has_key' expects exactly 2 arguments, {self._term}.")
            dictionary = self.eval(node.arguments[0])
            key = self.eval(node.arguments[1])
            if not isinstance(dictionary, dict):
                raise RuntimeErrorKozak(f"First argument must be a dictionary, {self._term}.")
            return key in dictionary
        # --- End built-in functions ---

        if '.' in node.name:
            try:
                # Припускаємо, що name має формат "instance_name.method_name"
                instance_name, method_name = node.name.split('.', 1)
            except ValueError:
                # Якщо формат складніший (наприклад, "a.b.c"), повертаємося до глобального пошуку
                pass 
            else:
                # 1. Обчислюємо аргументи, які передаються в метод
                evaluated_args = [self.eval(arg_node) for arg_node in node.arguments]

                # 2. Отримуємо змінну-екземпляр ('sobaka') з оточення
                if instance_name not in self.env:
                    raise RuntimeErrorKozak(f"Instance variable '{instance_name}' is not defined.")
                obj = self.env[instance_name]
                
                # Перевіряємо, чи є це об'єкт Instance
                if not isinstance(obj, oop.Instance):
                    raise RuntimeErrorKozak(f"Cannot call method '{method_name}' on non-object variable '{instance_name}'.")

                # 3. Знаходимо визначення методу у ClassDef
                method_def = obj.class_def.find_method(method_name)
                
                if not method_def or not isinstance(method_def, KozakFunctionDef):
                    raise RuntimeErrorKozak(f"Method '{method_name}' not found in class '{obj.class_def.name}'.")

                # CHECK ACCESS MODIFIERS FOR METHOD CALLS
                access_level = obj.class_def.get_method_access(method_name)
                calling_instance = None
                if 'this' in self.env and isinstance(self.env['this'], oop.Instance):
                    calling_instance = self.env['this']

                if access_level == 'private':
                    if calling_instance is not obj:
                        raise RuntimeErrorKozak(f"Cannot access private method '{method_name}' of class '{obj.class_def.name}'")
                elif access_level == 'protected':
                    if calling_instance is not None:
                        # Check if calling instance is same class or subclass
                        current = calling_instance.class_def
                        is_subclass = False
                        while current:
                            if current == obj.class_def:
                                is_subclass = True
                                break
                            current = current.parent_class
                        if not is_subclass:
                            raise RuntimeErrorKozak(f"Cannot access protected method '{method_name}' of class '{obj.class_def.name}'")
                    else:
                        # Called from outside any class context
                        raise RuntimeErrorKozak(f"Cannot access protected method '{method_name}' of class '{obj.class_def.name}'")



                # 4. Перевіряємо кількість аргументів
                if len(evaluated_args) != len(method_def.parameters):
                    raise RuntimeErrorKozak(f"Method '{method_name}' expected {len(method_def.parameters)} arguments, but got {len(evaluated_args)}.")

                # 5. Виконуємо метод (створюємо локальне оточення, встановлюємо 'this')
                local_env = {"this": obj}
                for param, arg_val in zip(method_def.parameters, evaluated_args):
                    local_env[param] = arg_val
                
                return self._execute_function_body(method_def.body, local_env, function_name=method_name)
        # --- КІНЕЦЬ ЛОГІКИ ДЛЯ ВИКЛИКУ МЕТОДУ ---

        # Existing user-defined function handling
        func_def = self.functions.get(node.name)
        if not func_def:
            raise RuntimeErrorKozak(f"Function '{node.name}' is not defined.")

        if len(node.arguments) != len(func_def.parameters):
            raise RuntimeErrorKozak(f"Function '{node.name}' expected {len(func_def.parameters)} arguments, but got {len(node.arguments)}.")

        evaluated_args = [self.eval(arg_node) for arg_node in node.arguments]
        
        local_env = {}
        for param, arg_val in zip(func_def.parameters, evaluated_args):
            local_env[param] = arg_val
        
        return self._execute_function_body(func_def.body, local_env, function_name=node.name)


    def _eval_array(self, node):
        return [self.eval(element) for element in node.elements]

    def _eval_array_index(self, node):
        array = self.eval(node.array)
        index = self.eval(node.index)
        
        if not isinstance(array, list):
            raise RuntimeErrorKozak("Only arrays can be indexed!")
        
        if not isinstance(index, int):
            raise RuntimeErrorKozak("Array index must be an integer!")

        if index < 0 or index >= len(array):
            raise RuntimeErrorKozak("Array index out of bounds!")

        #return array[index]
        return self._eval_dictionary_access(node)
    
    def _eval_for_each(self, node):
        array = self.eval(node.array_expr)
        if not isinstance(array, list):
            raise RuntimeErrorKozak(f"Can only iterate over arrays, {self._term}.")
        
        # Save original variable state if it exists, to be restored later
        original_var_value = self.env.get(node.var_name)
        is_new_var = node.var_name not in self.env
        
        for value in array:
            self.env[node.var_name] = value 
            for stmt in node.body:
                self.eval(stmt)
        
        # Clean up / restore
        if is_new_var:
             del self.env[node.var_name]
        elif original_var_value is not None:
             self.env[node.var_name] = original_var_value


    # --- Class and OOP methods (FIXED PROPERTY ACCESS NAMES) ---

    def _eval_ClassNode(self, node):
        """(KozakClass) Defines a class and stores it in the class_table."""
        # This is the correct method used by eval()
       # print(f"DEBUG: Defining class '{node.name}'")  # ← ADD THIS
       # print(f"DEBUG: Friend classes: {node.friend_classes}")  # ← ADD THIS

        parent_class_def = None

        if node.parent_name: 
            try:
                parent_class_def = self.class_table.get_class(node.parent_name)
            except Exception as e:
          #      print(f"DEBUG: Failed to get parent class: {e}")
                raise RuntimeErrorKozak(f"Parent class '{node.parent_name}' not defined for class '{node.name}'.")

        constructor = node.methods.get('Tvir')
        class_def = oop.ClassDef(
            name=node.name, 
            methods=node.methods, 
            constructor=constructor,
            destructor=node.destructor, 
            parent_class=parent_class_def,
            field_access=node.field_access,
            method_access=node.method_access,
            friends=node.friends,
            friend_classes=node.friend_classes
        )
        self.class_table.define_class(node.name, class_def)
       # print(f"DEBUG: Successfully registered class '{node.name}'")  # ← ADD THIS
       # print(f"DEBUG: Classes in table: {list(self.class_table.classes.keys())}")
        return class_def
    
    def eval_PropertyAccessNode(self, node):
        """(KozakPropertyAccess) Accesses a field or method on an object instance."""
        obj = self.eval(node.instance)
        from core.modules.math_module import MathModule
        from core.modules.hash import HashModule
        from core.modules.game_module import GameModule
        
        
        if isinstance(obj, (MathModule, HashModule, GameModule)):
                try:
                    attr = getattr(obj, node.property_name)
                except ValueError as e:
                    # __getattribute__ dialect guard raised this
                    obj._emergency_quit()
                    raise RuntimeErrorKozak(str(e))
                if not callable(attr):
                    return attr
                return attr
            
        
        if not isinstance(obj, oop.Instance):
            raise RuntimeErrorKozak(f"Cannot access property '{node.property_name}' on non-object of type {type(obj).__name__}")
        
        calling_instance = None
        if 'this' in self.env and isinstance(self.env['this'], oop.Instance):
            calling_instance = self.env['this']
        
        try:
            return obj.get(node.property_name, calling_instance, self.current_function)  # ← ADD current_function
        except RuntimeError as e:
            raise RuntimeErrorKozak(str(e))

    def eval_PropertyAssignNode(self, node):
        """(KozakPropertyAssign) Assigns a value to a field on an object instance OR dictionary key."""
        obj = self.eval(node.instance)
        value = self.eval(node.value)
        
        # Handle dictionary assignment
        if isinstance(obj, dict):
            key = self.eval(node.property_name) if hasattr(node.property_name, '__class__') and node.property_name.__class__.__name__.startswith('Kozak') else node.property_name
            obj[key] = value
            return value
        
        # Handle array assignment
        if isinstance(obj, list):
            if isinstance(node.property_name, int):
                index = node.property_name
            else:
                index = self.eval(node.property_name)
            
            if not isinstance(index, int):
                raise RuntimeErrorKozak("Array index must be an integer!")
            if index < 0 or index >= len(obj):
                raise RuntimeErrorKozak("Array index out of bounds!")
            obj[index] = value
            return value
        
        # Handle object property assignment
        if not isinstance(obj, oop.Instance):
            raise RuntimeErrorKozak(f"Cannot set property '{node.property_name}' on non-object of type {type(obj).__name__}")
        
        calling_instance = None
        if 'this' in self.env and isinstance(self.env['this'], oop.Instance):
            calling_instance = self.env['this']
        
        try:
            if isinstance(node.property_name, str):
                obj.set(node.property_name, value, calling_instance, self.current_function)  # ← ADD current_function
            else: 
                prop_name = self.eval(node.property_name)
                obj.set(str(prop_name), value, calling_instance, self.current_function)  # ← ADD current_function
        except RuntimeError as e:
            raise RuntimeErrorKozak(str(e))
        
        return value


    
    def eval_NewInstanceNode(self, node):
        """(KozakNewInstance) Creates a new object instance."""
        # NOTE: Assuming node.class_name is a string containing the class name
        # If your AST uses node.class_def (the ClassDef node itself), this line needs adjustment
       # print(f"DEBUG: Trying to create instance of '{node.class_name}'")  # ← ADD THIS
        #print(f"DEBUG: Available classes: {list(self.class_table.classes.keys())}")
        class_def = self.class_table.get_class(node.class_name) 
        
        if class_def is None:
            raise RuntimeErrorKozak(f"Class '{node.class_name}' not defined")

        instance = oop.Instance(class_def)

        constructor_def = class_def.constructor

        if not constructor_def and class_def.parent_class:
            constructor_def = class_def.parent_class.constructor

        if constructor_def:

            evaluated_args = [self.eval(arg_node) for arg_node in node.arguments]

            if len(evaluated_args) != len(constructor_def.parameters):
                raise RuntimeErrorKozak(f"Constructor for class '{class_def.name}' expected {len(constructor_def.parameters)} arguments, but got {len(evaluated_args)}.")

            # Set 'this' and argument parameters in the local scope
            local_env = {"this": instance} 
            for param, arg_val in zip(constructor_def.parameters, evaluated_args):
                local_env[param] = arg_val
            
            # Execute constructor body using the instance as 'this'
            self._execute_function_body(constructor_def.body, local_env, function_name='Tvir')
            
        return instance   
        

    def _eval_dictionary(self, node):
        result = {}
        for key_node, value_node in node.pairs:
            key = self.eval(key_node)
            # Convert key to hashable type if needed
            if isinstance(key, list):
                raise RuntimeErrorKozak(f"Cannot use array as dictionary key, {self._term}.")
            value = self.eval(value_node)
            result[key] = value
        return result

    def _eval_dictionary_access(self, node):
        dictionary = self.eval(node.dictionary)
        key = self.eval(node.key)
        
        # Handle both dictionaries and arrays
        if isinstance(dictionary, dict):
            if key not in dictionary:
                raise RuntimeErrorKozak(f"Key '{key}' not found in dictionary, {self._term}.")
            return dictionary[key]
        elif isinstance(dictionary, list):
            # Keep existing array indexing behavior
            if not isinstance(key, int):
                raise RuntimeErrorKozak("Array index must be an integer!")
            if key < 0 or key >= len(dictionary):
                raise RuntimeErrorKozak("Array index out of bounds!")
            return dictionary[key]
        else:
            raise RuntimeErrorKozak(f"Can only index arrays and dictionaries, {self._term}.")
    
    def _kozak_remove_key(self, dictionary, key):
        if not isinstance(dictionary, dict):
            raise RuntimeErrorKozak(f"remove_key() only works on dictionaries, {self._term}!")
        
        if key not in dictionary:
            raise RuntimeErrorKozak(f"Key '{key}' not found in dictionary for removal.")
            
        del dictionary[key]
        return None
    
    def _eval_try(self, node):
        exception_caught = None
        exception_value = None

        try:
            for stmt in node.try_body:
                self.eval(stmt)
        except ReturnValue as e:  # Don't catch returns - let them propagate!
            # Execute finally block first, then re-raise
            if node.finally_body:
                for stmt in node.finally_body:
                    self.eval(stmt)
            raise  # Re-raise the ReturnValue to propagate it up
            
        except RuntimeErrorKozak as e:
            exception_caught = True
            exception_value = str(e)

            if node.catch_clauses:
                exception_var, catch_body = node.catch_clauses[0]

                if exception_var:
                    original_value = self.env.get(exception_var)
                    self.env[exception_var] = exception_value

                try:
                    for stmt in catch_body:
                        self.eval(stmt)
                except ReturnValue as e:  # If catch block returns, let it propagate
                    if node.finally_body:
                        for stmt in node.finally_body:
                            self.eval(stmt)
                    raise
                
                finally: 
                    if exception_var:
                        if original_value is not None:
                            self.env[exception_var] = original_value
                        elif exception_var in self.env:
                            del self.env[exception_var]
            else:
                raise

        except Exception as e:
            exception_caught = True
            exception_value = str(e)
            if node.catch_clauses:
                exception_var, catch_body = node.catch_clauses[0]

                if exception_var:
                    original_value = self.env.get(exception_var)
                    self.env[exception_var] = exception_value
                
                try:
                    for stmt in catch_body:
                        self.eval(stmt)
                except ReturnValue as e:  # If catch block returns, let it propagate
                    if node.finally_body:
                        for stmt in node.finally_body:
                            self.eval(stmt)
                    raise
                
                finally:
                    if exception_var:
                        if original_value is not None:
                            self.env[exception_var] = original_value
                        elif exception_var in self.env:
                            del self.env[exception_var]
            else:
                raise

        finally:
            if node.finally_body:
                for stmt in node.finally_body:
                    self.eval(stmt)
        
        # Try block completed without returning - this is normal
        return None
    def _eval_throw(self, node):
        message = self.eval(node.message)
        raise RuntimeErrorKozak(str(message))
    
    def _eval_exit(self,node):
        if node.code is None:
            exit_code = 0
        else:
            exit_code = self.eval(node.code)

            if not isinstance(exit_code, int):
                try:
                    exit_code = int(exit_code)
                except (ValueError, TypeError):
                    raise RuntimeErrorKozak(f"Exit code must be an integer, got {type(exit_code).__name__}")
            
            if exit_code < 0 or exit_code > 255:
                raise RuntimeErrorKozak("Exit code must be between 0 and 255, {self._term}.")
        self.exit_code = exit_code
        raise ProgramExit(exit_code)
    
    def _eval_import(self, node):
        file_path = self.eval(node.file_path)

        if not isinstance(file_path, str):
            raise RuntimeErrorKozak(f"Import file path must be a string, got {type(file_path).__name__} {self._term}.")

        # Define these once, shared by both the alias path and the direct path below
        built_in_modules = {
            "hash": "core.modules.hash",
            "math": "core.modules.math_module",
            "game": "core.modules.game_module",
        }
        class_mapping = {
            "hash": "HashModule",
            "math": "MathModule",
            "game": "GameModule",
        }

        canonical_name = MODULE_NAME_TRANSLATIONS.get(file_path, None)

        if canonical_name and canonical_name in built_in_modules:
            module_path = built_in_modules[canonical_name]
            try:
                module = __import__(module_path, fromlist=[''])
                class_name = class_mapping.get(canonical_name)  # ← now defined
                if class_name and hasattr(module, class_name):
                    module_class = getattr(module, class_name)
                    module_instance = (
                        module_class(dialect=self.parent_dialect)
                        if canonical_name == "game"
                        else module_class()
                    )
                    self.modules[canonical_name] = module_instance
                    self.modules[file_path] = module_instance
                    self.env[file_path] = module_instance
                    return None
                else:
                    raise RuntimeErrorKozak(
                        f"Built-in module '{file_path}' missing '{class_name}' class, {self._term}."
                    )
            except RuntimeErrorKozak:
                raise  # don't swallow your own errors
            except Exception as e:
                raise RuntimeErrorKozak(
                    f"Failed to load built-in module '{file_path}', {self._term}: {e}"
                )

        if file_path in built_in_modules:
            module_path = built_in_modules[file_path]
            try:
                module = __import__(module_path, fromlist=[''])
                class_name = class_mapping.get(file_path)
                if class_name and hasattr(module, class_name):
                    module_class = getattr(module, class_name)
                    module_instance = (
                        module_class(dialect=self.parent_dialect)
                        if file_path == "game"
                        else module_class()
                    )
                    self.modules[file_path] = module_instance
                    self.env[file_path] = module_instance
                    return None
                else:
                    raise RuntimeErrorKozak(
                        f"Built-in module '{file_path}' missing '{class_name}' class, {self._term}."
                    )
            except RuntimeErrorKozak:
                raise
            except Exception as e:
                raise RuntimeErrorKozak(
                    f"Failed to load built-in module '{file_path}', {self._term}: {e}"
                )

    
        if self.current_file_dir:
            full_path = os.path.join(self.current_file_dir, file_path)
        else:
            full_path = file_path

        full_path = os.path.abspath(full_path)

        if full_path in self.imported_files:
            return None
        
        
        
        if not os.path.exists(full_path):
            raise RuntimeErrorKozak(f"Import file '{full_path}' not found, {self._term}.")
        
        if not full_path.endswith('.kozak'):
            raise RuntimeErrorKozak(f"Can only import .kozak files, got '{file_path}'.")
        
        self.imported_files.add(full_path)

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
        except IOError as e:
            raise RuntimeErrorKozak(f"Error reading import file '{full_path}': {e}")
        
        try:
            from core.parser import Parser
            from core.lexer import lex

            tokens = list(lex(code))
            parser = Parser(tokens, strict_dialect=self.strict_dialect)
            if self.strict_dialect and self.parent_dialect:
                parser.detected_dialect = self.parent_dialect
            ast = parser.parse()

            if parser.errors:
                error_messages = '\n'.join(parser.errors)
                raise RuntimeErrorKozak(f"Errors in imported file, {self._term} '{full_path}':\n{error_messages}")
        
        except SyntaxError as e:
            raise RuntimeErrorKozak(f"Syntax error in imported file '{full_path}': {e}")
        
        old_dir = self.current_file_dir
        self.current_file_dir = os.path.dirname(full_path)

        try:
            self.eval(ast)
        
        finally:
            self.current_file_dir = old_dir

        return None
    
    def _lookup_variable(self, name):
        # Search from innermost to outermost scope
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        if name in self.functions:
            return self.functions[name]
        raise RuntimeErrorKozak(f'Variable {name} is not defined')

    def import_module(self, name):
        if name in self.modules:
            return self.modules[name]
        raise RuntimeErrorKozak(f"Module '{name}' not found, {self._term}!")

    def _eval_super(self, node):
        """Handle super.method() calls"""
        # Check if we're inside a method context
        if 'this' not in self.env or not isinstance(self.env['this'], oop.Instance):
            raise RuntimeErrorKozak(f"'super' can only be used inside a class method, {self._term}.")
        
        current_instance = self.env['this']
        current_class = current_instance.class_def
        
        # Get the parent class
        if not current_class.parent_class:
            raise RuntimeErrorKozak(f"Class '{current_class.name}' has no parent class, {self._term}.")
        
        parent_class = current_class.parent_class
        
        # Find the method in the parent class
        method_def = parent_class.find_method(node.method_name)
        
        if not method_def:
            raise RuntimeErrorKozak(f"Method '{node.method_name}' not found in parent class '{parent_class.name}', {self._term}.")
        
        # Evaluate arguments
        evaluated_args = [self.eval(arg_node) for arg_node in node.arguments]
        
        # Check parameter count
        if len(evaluated_args) != len(method_def.parameters):
            raise RuntimeErrorKozak(
                f"Method '{node.method_name}' expected {len(method_def.parameters)} arguments, "
                f"but got {len(evaluated_args)}, {self._term}."
            )
        
        # Execute the parent's method with current instance as 'this'
        local_env = {"this": current_instance}
        for param, arg_val in zip(method_def.parameters, evaluated_args):
            local_env[param] = arg_val
        
        return self._execute_function_body(method_def.body, local_env, function_name=node.method_name)
