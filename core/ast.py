"""Abstract Syntax Tree for KozakScript"""

class KozakNumber:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"KozakNumber({self.value})"

class KozakString:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'KozakString({self.value!r})'

class KozakVariable:
    def __init__(self, name): self.name = name
    def __repr__(self): return f"KozakVariable({self.name})"

class KozakBinOp:
    def __init__(self, left, op, right):
        self.left, self.op, self.right = left, op, right
    def __repr__(self): return f"KozakBinOp({self.left}, {self.op}, {self.right})"

class KozakAssign:
    def __init__(self, name, expr):
        self.name, self.expr = name, expr
    def __repr__(self): return f"KozakAssign({self.name}, {self.expr})"

class KozakProgram:
    def __init__(self, statements): self.statements = statements
    def __repr__(self): return f"KozakProgram({self.statements})"

class KozakEcho:
    def __init__(self, expr): self.expr = expr
    def __repr__(self): return f"KozakEcho({self.expr})"

class KozakComment:
    def __init__(self, text): self.text = text
    def __repr__(self): return f"KozakComment({self.text!r})"

class KozakInput:
    def __init__(self, expr): self.expr = expr
    def __repr__(self): return f"KozakInput({self.expr})"

class KozakBoolean:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"KozakBoolean({self.value})"

class KozakComparisonOp:
    def __init__(self, left, op, right):
        self.left, self.op, self.right = left, op, right
    def __repr__(self): return f"KozakComparisonOp({self.left}, {self.op}, {self.right})"