"""Interpreter for KozakScript"""
import random

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
    KozakForEach
)

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class RuntimeErrorKozak(Exception):
    def __init__(self, message):
        super().__init__(message)

class Interpreter:
    def __init__(self):
        self.env = {}
        self.functions = {} 


    def eval(self, node):
        if isinstance(node, KozakProgram):
            return self._eval_program(node)
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
            raise ReturnValue(self.eval(node.value))
        elif isinstance(node, KozakArray):
            return self._eval_array(node)
        elif isinstance(node, KozakArrayIndex):
            return self._eval_array_index(node)
        elif isinstance(node, KozakForEach):
            return self._eval_for_each(node)
        else:
            raise RuntimeErrorKozak(f'Unknown node type: {type(node).__name__}')

    def _eval_program(self, node):
        for stmt in node.statements:
            self.eval(stmt)

    def _eval_assign(self, node):
        value = self.eval(node.expr)
        self.env[node.name] = value

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
                raise RuntimeErrorKozak(f"Cannot cast '{value}' to 'Chyslo'.")
        elif node.target_type == 'DroboveChyslo':
            try:
                return float(value)
            except (ValueError, TypeError):
                raise RuntimeErrorKozak(f"Cannot cast '{value}' to 'DroboveChyslo'.")
        elif node.target_type == 'Ryadok':
            return str(value)
        elif node.target_type == 'Logika':
            if value in ('Pravda', 'Nepravda', True, False, 0, 1):
                return bool(value)
            raise RuntimeErrorKozak(f"Cannot cast '{value}' to 'Logika'.")
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
        var_name = node.target.name
        current_value = self.env[var_name]
        
        if node.op == '++':
            self.env[var_name] = current_value + 1
        elif node.op == '--':
            self.env[var_name] = current_value - 1
    
    def _eval_for(self, node):
        self.eval(node.initialization)
        
        while self.eval(node.condition):
            for stmt in node.body:
                self.eval(stmt)
            self.eval(node.step)
    
    def _eval_function_def(self, node):
        self.functions[node.name] = node

    def _eval_function_call(self, node):
        func_def = self.functions.get(node.name)

        if node.name == 'append':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'append' expects exactly 2 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'append' must be an array, kozache.")
            arr.append(value)
            return None
        
        if node.name == 'insert':
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

        if node.name == 'index_of':
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

        if node.name == 'contains':
            if len(node.arguments) != 2:
                raise RuntimeErrorKozak("Function 'contains' expects exactly 2 arguments, kozache.")
            arr = self.eval(node.arguments[0])
            value = self.eval(node.arguments[1])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("First argument of 'contains' must be an array, kozache.")
            return value in arr

        if node.name == 'slice':
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

        if node.name == 'clear':
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'clear' expects exactly 1 argument, kozache.")
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("Argument of 'clear' must be an array, kozache.")
            arr.clear()
            return None


        if node.name == 'pop':
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'pop' expects exactly 1 argument, kozache.")
            arr = self.eval(node.arguments[0])
            if not isinstance(arr, list):
                raise RuntimeErrorKozak("Argument of 'pop' must be an array, kozache.")
            if not arr:
                raise RuntimeErrorKozak("Cannot pop from empty array, kozache.")
            return arr.pop()

        if node.name == 'remove':
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

        
        if node.name == 'Zapysaty':
            if len(node.arguments) < 2 or len(node.arguments) > 3:
                raise RuntimeErrorKozak("Function 'Zapysaty' expects 2 or 3 arguments, kozache.")
            file_name = self.eval(node.arguments[0])
            content = self.eval(node.arguments[1])
            append_mode = False
            if len(node.arguments) == 3:
                append_mode = bool(self.eval(node.arguments[2]))
            mode = 'a' if append_mode else 'w'
            if not isinstance(file_name, str) or not isinstance(content, str):
                raise RuntimeErrorKozak("Arguments for 'Zapysaty' must be strings, kozache.")
            with open(file_name, mode, encoding='utf-8') as f:
                f.write(content)
            return None

        if node.name == 'Chytaty':
            if len(node.arguments) != 1:
                raise RuntimeErrorKozak("Function 'Chytaty' expects exactly 1 argument, kozache.")
            file_name = self.eval(node.arguments[0])
            if not isinstance(file_name, str):
                raise RuntimeErrorKozak("Argument for 'Chytaty' must be a string, kozache.")
            with open(file_name, 'r', encoding='utf-8') as f:
                return f.read()

        if node.name == 'dovzhyna':
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

        # Existing user-defined function handling
        if not func_def:
            raise RuntimeErrorKozak(f"Function '{node.name}' is not defined.")

        if len(node.arguments) != len(func_def.parameters):
            raise RuntimeErrorKozak(f"Function '{node.name}' expected {len(func_def.parameters)} arguments, but got {len(node.arguments)}.")

        original_env = self.env.copy()
        try:
            for param, arg_val in zip(func_def.parameters, node.arguments):
                self.env[param] = self.eval(arg_val)
            
            for stmt in func_def.body:
                self.eval(stmt)
            return None 
        except ReturnValue as e:
            return e.value 
        finally:
            self.env = original_env


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

        return array[index]
    
    def _eval_for_each(self, node):
        array = self.eval(node.array_expr)
        if not isinstance(array, list):
            raise RuntimeErrorKozak("Can only iterate over arrays, kozache.")
        for value in array:
            self.env[node.var_name] = value
            for stmt in node.body:
                self.eval(stmt)
