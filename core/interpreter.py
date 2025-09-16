"""Interpreter for KozakScript"""

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
    KozakReturn
)

from core.parser import KozakTypeCast

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

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
        else:
            raise TypeError(f'Unknown node type: {type(node).__name__}')

    def _eval_program(self, node):
        for stmt in node.statements:
            self.eval(stmt)

    def _eval_assign(self, node):
        value = self.eval(node.expr)
        self.env[node.name] = value

    def _eval_echo(self, node):
        value = self.eval(node.expr)
        if isinstance(value, bool):
            if value is True:
                print("Pravda")
            else:
                print("Nepravda")
        else:
            print(value)

    def _eval_number(self, node):
        return node.value

    def _eval_variable(self, node):
        if node.name in self.env:
            return self.env[node.name]
        raise NameError(f'Variable {node.name} is not defined')

    def _eval_binop(self, node):
        left = self.eval(node.left)
        right = self.eval(node.right)
        
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left / right
        elif node.op == '//':
            return left // right
        elif node.op == '^':
            return left ** right
        elif node.op == '^/':
            if right == 0:
                raise ValueError("Root exponent cannot be zero!")
            return left ** (1 / right)
        elif node.op == '&&':
            return left and right
        elif node.op == '||':
            return left or right
        else:
            raise ValueError(f'Unknown operator: {node.op}')

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
                raise TypeError(f"Cannot cast '{value}' to 'Chyslo'.")
        elif node.target_type == 'Ryadok':
            return str(value)
        elif node.target_type == 'Logika':
            if value in ('Pravda', 'Nepravda', True, False, 0, 1):
                return bool(value)
            raise TypeError(f"Cannot cast '{value}' to 'Logika'.")
        else:
            raise ValueError(f"Unknown type cast: {node.target_type}")
    
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
        
        if not func_def:
            raise NameError(f"Function '{node.name}' is not defined.")

        if len(node.arguments) != len(func_def.parameters):
            raise TypeError(f"Function '{node.name}' expected {len(func_def.parameters)} arguments, but got {len(node.arguments)}.")

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
