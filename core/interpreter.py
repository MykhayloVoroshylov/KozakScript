"""Interpreter for KozakScript"""
import random
import sys 
import os
from core.parser import Parser
from core.modules.hash import HashModule


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
    KozakImport
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
            # future: "math": MathModule(), etc.
        }
        self.scopes = [{}]
        self.type_constraints = {}

    def _execute_function_body(self, body, local_env):
        """
        Executes a list of statements (a function body) in a given local environment.
        This is necessary for user-defined functions and methods/constructors.
        """
        original_env = self.env
        merged_env = {**self.env, **local_env}
        self.env = merged_env
        try:
            for stmt in body:
                self.eval(stmt)
            return None 
        except ReturnValue as e:
            return e.value
        finally:
            self.env = original_env

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
        else:
            raise RuntimeErrorKozak(f'Unknown node type: {type(node).__name__}')

    def _eval_program(self, node):
        for stmt in node.statements:
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
        
        self.env[node.name] = value
    
    def _normalize_type(self, kozak_type):
        """Convert KozakScript type to Python type"""
        mapping = {
            'Chyslo': 'int',
            'DroboveChyslo': 'float',
            'Ryadok': 'str',
            'Logika': 'bool'
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

    def _eval_echo(self, node):
        values = []
        for expr in node.expressions:
            value = self.eval(expr)
            if isinstance(value, bool):
                values.append("Pravda" if value else "Nepravda")
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
                raise RuntimeErrorKozak("Cannot divide by zero, kozache.")
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
                module_name, method_name = parts
                # Check if this is a module method call
                if module_name in self.modules:
                    module = self.modules[module_name]
                    if hasattr(module, method_name):
                        method = getattr(module, method_name)
                        evaluated_args = [self.eval(arg_node) for arg_node in node.arguments]
                        return method(*evaluated_args)
                    
        if node.name in ('create_matrix', 'stvoryty_matrytsyu', 'sozdat_matritsu', '@[]'):
            if len(node.arguments) not in (2, 3):
                raise RuntimeErrorKozak("Function 'create_matrix' expects 2 or 3 arguments (rows, cols, [fill_value]), kozache.")
            
            rows = self.eval(node.arguments[0])
            cols = self.eval(node.arguments[1])
            fill_value = self.eval(node.arguments[2]) if len(node.arguments) == 3 else 0
            
            if not isinstance(rows, int) or not isinstance(cols, int):
                raise RuntimeErrorKozak("Rows and columns must be integers, kozache.")
            if rows <= 0 or cols <= 0:
                raise RuntimeErrorKozak("Matrix dimensions must be positive, kozache.")
            
            return [[fill_value for _ in range(cols)] for _ in range(rows)]
        
        # Get matrix dimensions
        if node.name in ('matrix_size', 'rozmir_matrytsi', 'razmer_matritsy', '#[]'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'matrix_size' expects 1 argument, kozache.")
            
            matrix = self.eval(node.arguments[0])
            if not isinstance(matrix, list):
                raise RuntimeErrorKozak("Argument must be an array, kozache.")
            
            if not matrix or not isinstance(matrix[0], list):
                return [len(matrix), 0]  # 1D array or empty
            
            return [len(matrix), len(matrix[0])]
        
        # Flatten a multidimensional array
        if node.name in ('flatten', 'splushchyty', 'spluschit', '[]>'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'flatten' expects 1 argument, kozache.")
            
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("Argument must be an array, kozache.")
            
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
        if node.name in ('transpose', 'transportuvaty', 'transportirovat', '[]^'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'transpose' expects 1 argument, kozache.")
            
            matrix = self.eval(node.arguments[0])
            if not isinstance(matrix, list) or not matrix:
                raise RuntimeErrorKozak("Argument must be a non-empty array, kozache.")
            
            if not all(isinstance(row, list) for row in matrix):
                raise RuntimeErrorKozak("Argument must be a 2D array, kozache.")
            
            # Check all rows have same length
            if not all(len(row) == len(matrix[0]) for row in matrix):
                raise RuntimeErrorKozak("All rows must have the same length for transpose, kozache.")
            
            return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
        
        # Get row from matrix
        if node.name in ('get_row', 'otrymaty_ryadok', 'poluchit_stroku', '[]->'):
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'get_row' expects 2 arguments (matrix, row_index), kozache.")
            
            matrix = self.eval(node.arguments[0])
            row_idx = self.eval(node.arguments[1])
            
            if not isinstance(matrix, list):
                raise RuntimeErrorKozak("First argument must be an array, kozache.")
            if not isinstance(row_idx, int):
                raise RuntimeErrorKozak("Row index must be an integer, kozache.")
            if row_idx < 0 or row_idx >= len(matrix):
                raise RuntimeErrorKozak("Row index out of bounds, kozache.")
            
            return matrix[row_idx]
        
        # Get column from matrix
        if node.name in ('get_col', 'otrymaty_stovpets', 'poluchit_stolbets', '[]|'):
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'get_col' expects 2 arguments (matrix, col_index), kozache.")
            
            matrix = self.eval(node.arguments[0])
            col_idx = self.eval(node.arguments[1])
            
            if not isinstance(matrix, list) or not matrix:
                raise RuntimeErrorKozak("First argument must be a non-empty array, kozache.")
            if not isinstance(col_idx, int):
                raise RuntimeErrorKozak("Column index must be an integer, kozache.")
            
            if not all(isinstance(row, list) for row in matrix):
                raise RuntimeErrorKozak("Argument must be a 2D array, kozache.")
            
            if col_idx < 0 or (matrix and col_idx >= len(matrix[0])):
                raise RuntimeErrorKozak("Column index out of bounds, kozache.")
            
            return [row[col_idx] for row in matrix]
        
        # Set value at position in multidimensional array
        if node.name in ('set_at', 'vstanovyty_na', 'ustanovit_na', '[]:='):
            if len(node.arguments) < 3:
                raise RuntimeErrorKozak("Function 'set_at' expects at least 3 arguments (array, indices..., value), kozache.")
            
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument must be an array, kozache.")
            
            # All arguments except last are indices, last is the value
            indices = [self.eval(node.arguments[i]) for i in range(1, len(node.arguments) - 1)]
            value = self.eval(node.arguments[-1])
            
            # Navigate to the target position
            current = arr
            for i, idx in enumerate(indices[:-1]):
                if not isinstance(idx, int):
                    raise RuntimeErrorKozak(f"Index {i+1} must be an integer, kozache.")
                if idx < 0 or idx >= len(current):
                    raise RuntimeErrorKozak(f"Index {i+1} out of bounds, kozache.")
                current = current[idx]
            
            # Set the final value
            last_idx = indices[-1]
            if not isinstance(last_idx, int):
                raise RuntimeErrorKozak("Last index must be an integer, kozache.")
            if last_idx < 0 or last_idx >= len(current):
                raise RuntimeErrorKozak("Last index out of bounds, kozache.")
            
            current[last_idx] = value
            return None

        
        if node.name == 'remove_key' or node.name == 'vydalyty_klyuch' or node.name == 'udalit_klyuch' or node.name == 'vydalyty_klyuch_sym':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'remove_key' expects exactly 2 arguments (dictionary, key), kozache.")
            
            dictionary = self.eval(node.arguments[0])
            key = self.eval(node.arguments[1])
            
            return self._kozak_remove_key(dictionary, key)

        if node.name == 'insert' or node.name == 'vstavyty' or node.name == 'vstavit' or node.name == '+:':
            if len(node.arguments) != 3:
                raise RuntimeErrorKozak("Function 'insert' expects exactly 3 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            index = self.eval(node.arguments[1])
            value = self.eval(node.arguments[2])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'insert' must be an array, kozache.")
            if not isinstance(index, int):
                raise RuntimeErrorKozak("Second argument of 'insert' must be an integer, kozache.")
            if index < 0 or index > len(arr):
                raise RuntimeErrorKozak("Array index out of bounds, kozache.")
            arr.insert(index, value)
            return None
        
        if node.name == 'append' or node.name == 'dodaty' or node.name == 'dobavit' or node.name == '+<':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'append' expects exactly 2 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'append' must be an array, kozache.")
            arr.append(value)
            return None

        if node.name == 'index_of' or node.name == 'index_z' or node.name == 'index_znachenia' or node.name == '?:':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'index_of' expects exactly 2 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'index_of' must be an array, kozache.")
            try:
                return arr.index(value)
            except ValueError:
                return -1

        if node.name == 'contains' or node.name == 'mistyt' or node.name == 'soderzhit' or node.name == '?^':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'contains' expects exactly 2 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'contains' must be an array, kozache.")
            return value in arr

        if node.name == 'slice' or node.name == 'vyrizaty' or node.name == 'vyrezat' or node.name == '[..]':
            if len(node.arguments) not in (2, 3):
                raise RuntimeErrorKozak("Function 'slice' expects 2 or 3 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            start = self.eval(node.arguments[1])
            end = self.eval(node.arguments[2]) if len(node.arguments) == 3 else None
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'slice' must be an array, kozache.")
            if not isinstance(start, int) or (end is not None and not isinstance(end, int)):
                raise RuntimeErrorKozak("Start and end arguments must be integers, kozache.")
            return arr[start:end]

        if node.name == 'clear' or node.name == 'ochystyty' or node.name == 'ochistit' or node.name == '--<':
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'clear' expects exactly 1 argument, kozache.")
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("Argument of 'clear' must be an array, kozache.")
            arr.clear()
            return None

        if node.name == 'pop' or node.name == 'vyinyaty' or node.name == 'vytaschit' or node.name == '-<!':
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'pop' expects exactly 1 argument, kozache.")
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("Argument of 'pop' must be an array, kozache.")
            if not arr:
                raise RuntimeErrorKozak("Cannot pop from empty array, kozache.")
            return arr.pop()

        if node.name == 'remove' or node.name == 'vydalyty' or node.name == 'udalit' or node.name == '-<':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'remove' expects exactly 2 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            index = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'remove' must be an array, kozache.")
            if not isinstance(index, int):
                raise RuntimeErrorKozak("Second argument of 'remove' must be an integer, kozache.")
            if index < 0 or index >= len(arr):
                raise RuntimeErrorKozak("Array index out of bounds, kozache.")
            arr.pop(index)
            return None

        
        if node.name in ('Zapysaty', 'Write', 'Zapisat', '=>'):
            if len(node.arguments) < 2 or len(node.arguments) > 3:
                raise RuntimeErrorKozak("Function 'Zapysaty' expects 2 or 3 arguments, kozache.")
            file_name = self.eval(node.arguments[0])
            content = self.eval(node.arguments[1])
            append_mode = False
            if len(node.arguments) == 3:
                append_mode = bool(self.eval(node.arguments[2]))
            
            if not isinstance(file_name, str):
                raise RuntimeErrorKozak("First argument for 'Zapysaty' (file name) must be a string, kozache.")
            
            mode = 'a' if append_mode else 'w'
            try:
                with open(file_name, mode, encoding='utf-8') as f:
                    f.write(str(content))
                return None
            except IOError as e:
                raise RuntimeErrorKozak(f"File writing error: {e}")


        if node.name in ('Chytaty', 'Read', 'Chitat', '=<'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'Chytaty' expects exactly 1 argument, kozache.")
            file_name = self.eval(node.arguments[0])
            if not isinstance(file_name, str):
                raise RuntimeErrorKozak("Argument for 'Chytaty' must be a string, kozache.")
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                raise RuntimeErrorKozak(f"File '{file_name}' not found, kozache.")
            except IOError as e:
                raise RuntimeErrorKozak(f"File reading error: {e}")


        if node.name in ('dovzhyna', 'length', 'dlinna', '___'):
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'dovzhyna' expects exactly 1 argument, kozache.")
            arg = self.eval(node.arguments[0])
            if not isinstance(arg, (list, str, tuple)):
                raise RuntimeErrorKozak("Argument for 'dovzhyna must be an array or a string, kozache.")
            return len(arg)
        
        if node.name == 'randint':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'randint' expects exactly 2 arguments, kozache.")
            start = self.eval(node.arguments[0])
            end = self.eval(node.arguments[1])
            if not isinstance(start, int) or not isinstance(end, int):
                raise RuntimeErrorKozak("Arguments for 'randint' must be integers, kozache.")
            return random.randint(start, end)

        if node.name == 'klyuchi' or node.name == 'keys' or node.name == 'klyuchi_sym':  # keys
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'klyuchi' expects exactly 1 argument, kozache.")
            dictionary = self.eval(node.arguments[0])
            if not isinstance(dictionary, dict):
                raise RuntimeErrorKozak("Argument must be a dictionary, kozache.")
            return list(dictionary.keys())

        if node.name == 'znachennya' or node.name == 'values' or node.name=='znachennie' or node.name == 'znachennya_sym':  # values
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'znachennya' expects exactly 1 argument, kozache.")
            dictionary = self.eval(node.arguments[0])
            if not isinstance(dictionary, dict):
                raise RuntimeErrorKozak("Argument must be a dictionary, kozache.")
            return list(dictionary.values())

        if node.name == 'maye_klyuch' or node.name == 'has_key' or node.name == 'imeet_klyuch' or node.name == 'maye_klyuch_sym':  # has_key
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'maye_klyuch' expects exactly 2 arguments, kozache.")
            dictionary = self.eval(node.arguments[0])
            key = self.eval(node.arguments[1])
            if not isinstance(dictionary, dict):
                raise RuntimeErrorKozak("First argument must be a dictionary, kozache.")
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
                
                return self._execute_function_body(method_def.body, local_env)
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
        
        return self._execute_function_body(func_def.body, local_env)


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
            raise RuntimeErrorKozak("Can only iterate over arrays, kozache.")
        
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

        parent_class_def = None

        if node.parent_name: 
            try:
                parent_class_def = self.class_table.get_class(node.parent_name)
            except Exception:
                raise RuntimeErrorKozak(f"Parent class '{node.parent_name}' not defined for class '{node.name}'.")

        constructor = node.methods.get('Tvir')
        class_def = oop.ClassDef(
            name=node.name, 
            methods=node.methods, 
            constructor=constructor, 
            parent_class=parent_class_def,
            field_access=node.field_access,
            method_access=node.method_access
        )
        self.class_table.define_class(node.name, class_def)
        return class_def
    
    def eval_PropertyAccessNode(self, node):
        """(KozakPropertyAccess) Accesses a field or method on an object instance."""
        obj = self.eval(node.instance)
        
        if not isinstance(obj, oop.Instance):
            raise RuntimeErrorKozak(f"Cannot access property '{node.property_name}' on non-object of type {type(obj).__name__}")
        
        # Determine the calling context (are we accessing from within the same instance?)
        calling_instance = None
        # If we're inside a method and accessing 'this', we're in the same instance
        if 'this' in self.env and isinstance(self.env['this'], oop.Instance):
            calling_instance = self.env['this']
        
        try:
            return obj.get(node.property_name, calling_instance)
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
        
        # Determine calling context
        calling_instance = None
        if 'this' in self.env and isinstance(self.env['this'], oop.Instance):
            calling_instance = self.env['this']
        
        try:
            if isinstance(node.property_name, str):
                obj.set(node.property_name, value, calling_instance)
            else: 
                prop_name = self.eval(node.property_name)
                obj.set(str(prop_name), value, calling_instance)
        except RuntimeError as e:
            raise RuntimeErrorKozak(str(e))
        
        return value


    
    def eval_NewInstanceNode(self, node):
        """(KozakNewInstance) Creates a new object instance."""
        # NOTE: Assuming node.class_name is a string containing the class name
        # If your AST uses node.class_def (the ClassDef node itself), this line needs adjustment
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
            self._execute_function_body(constructor_def.body, local_env)
            
        return instance

    def eval_PropertyAccessNode(self, node):
        """(KozakPropertyAccess) Accesses a field or method on an object instance."""
        # FIX: Use 'instance' instead of 'object'
        obj = self.eval(node.instance)
        
        if not isinstance(obj, oop.Instance):
            raise RuntimeErrorKozak(f"Cannot access property '{node.property_name}' on non-object of type {type(obj).__name__}")
            
        # FIX: Use 'property_name' instead of 'prop_name'
        return obj.get(node.property_name) 

    def eval_PropertyAssignNode(self, node):
        """(KozakPropertyAssign) Assigns a value to a field on an object instance OR dictionary key."""
        obj = self.eval(node.instance)
        value = self.eval(node.value)
        
        # Handle dictionary assignment: dict[key] := value
        if isinstance(obj, dict):
            key = self.eval(node.property_name) if hasattr(node.property_name, '__class__') and node.property_name.__class__.__name__.startswith('Kozak') else node.property_name
            obj[key] = value
            return value
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
        if isinstance(node.property_name, str):
            obj.set(node.property_name, value)
        else: 
            prop_name = self.eval(node.property_name)
            obj.set(str(prop_name), value)
        return value
    
        

    def _eval_dictionary(self, node):
        result = {}
        for key_node, value_node in node.pairs:
            key = self.eval(key_node)
            # Convert key to hashable type if needed
            if isinstance(key, list):
                raise RuntimeErrorKozak("Cannot use array as dictionary key, kozache.")
            value = self.eval(value_node)
            result[key] = value
        return result

    def _eval_dictionary_access(self, node):
        dictionary = self.eval(node.dictionary)
        key = self.eval(node.key)
        
        # Handle both dictionaries and arrays
        if isinstance(dictionary, dict):
            if key not in dictionary:
                raise RuntimeErrorKozak(f"Key '{key}' not found in dictionary, kozache.")
            return dictionary[key]
        elif isinstance(dictionary, list):
            # Keep existing array indexing behavior
            if not isinstance(key, int):
                raise RuntimeErrorKozak("Array index must be an integer!")
            if key < 0 or key >= len(dictionary):
                raise RuntimeErrorKozak("Array index out of bounds!")
            return dictionary[key]
        else:
            raise RuntimeErrorKozak("Can only index arrays and dictionaries, kozache.")
    
    def _kozak_remove_key(self, dictionary, key):
        if not isinstance(dictionary, dict):
            raise RuntimeErrorKozak("remove_key() only works on dictionaries, kozache!")
        
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
                raise RuntimeErrorKozak("Exit code must be between 0 and 255, kozache.")
        self.exit_code = exit_code
        raise ProgramExit(exit_code)
    
    def _eval_import(self, node):
        file_path = self.eval(node.file_path)
        if not isinstance(file_path, str):
            raise RuntimeErrorKozak(f"Import file path must be a string, got{type(file_path).__name__} kozache.")
        built_in_modules = {
        "hash": "core.modules.hash"
        }

        if file_path in built_in_modules:
            module_path = built_in_modules[file_path]
            try:
                module = __import__(module_path, fromlist=[''])
                # Expecting class named e.g., HashModule
                class_name = ''.join(part.capitalize() for part in file_path.split('_')) + "Module"
                # Or, simpler — hardcode if you like:
                # from core.modules.hash_module import HashModule
                # module_instance = HashModule()
                if hasattr(module, "HashModule"):
                    module_instance = module.HashModule()
                    self.modules[file_path] = module_instance
                    self.env[file_path] = module_instance
                    return None
                else:
                    raise RuntimeErrorKozak(f"Built-in module '{file_path}' missing 'HashModule' class, kozache.")
            except Exception as e:
                raise RuntimeErrorKozak(f"Failed to load built-in module '{file_path}', kozache: {e}")

    
        if self.current_file_dir:
            full_path = os.path.join(self.current_file_dir, file_path)
        else:
            full_path = file_path

        full_path = os.path.abspath(full_path)

        if full_path in self.imported_files:
            return None
        
        
        
        if not os.path.exists(full_path):
            raise RuntimeErrorKozak(f"Import file '{full_path}' not found, kozache.")
        
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
                raise RuntimeErrorKozak(f"Errors in imported file, kozache '{full_path}':\n{error_messages}")
        
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
        raise RuntimeErrorKozak(f"Module '{name}' not found, kozache!")

