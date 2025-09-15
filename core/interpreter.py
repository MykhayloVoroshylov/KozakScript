"""Interpreter for KozakScript"""

from core.ast import (
    KozakNumber,
    KozakVariable,
    KozakBinOp,
    KozakAssign,
    KozakProgram,
    KozakEcho,
    KozakString,
    KozakInput,
    KozakBoolean,
    KozakComparisonOp,
)

from core.parser import KozakTypeCast

class Interpreter:
    def __init__(self):
        self.env = {}

    def eval(self, node):
        if isinstance(node, KozakProgram):
            return self._eval_program(node)
        elif isinstance(node, KozakAssign):
            return self._eval_assign(node)
        elif isinstance(node, KozakEcho):
            return self._eval_echo(node)
        elif isinstance(node, KozakNumber):
            return self._eval_number(node)
        elif isinstance(node, KozakVariable):
            return self._eval_variable(node)
        elif isinstance(node, KozakBinOp):
            left = self.eval(node.left)
            right = self.eval(node.right)
            if node.op == '+':
                return left + right   # works for both int and str in Python
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
