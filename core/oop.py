"""OOP support for KozakScript."""

class ClassDef:
    """Represents a class definition in KozakScript."""
    def __init__(self, name, methods, constructor=None, parent_class=None):
        self.name = name
        self.methods = methods  # dict: method_name -> method_node
        self.constructor = constructor  # Node for Tvir (constructor) if exists
        self.parent_class = parent_class  # ClassDef of parent class if inheritance is used

    def find_method(self, name):
        """Recursively search for a method in the class or its ancestors."""
        if name in self.methods:
            return self.methods[name]
        
        # Recurse up the inheritance chain
        if self.parent_class:
            return self.parent_class.find_method(name)
            
        return None

class Instance:
    """Represents an object instance."""
    def __init__(self, class_def):
        self.class_def = class_def
        self.fields = {}  # instance variables

    def get(self, name):
        # First check instance fields
        if name in self.fields:
            return self.fields[name]
        
        method_node = self.class_def.find_method(name)
        # Then check methods

        if method_node:
            return lambda *args: method_node.eval(self, *args)

        # if name in self.class_def.methods:
        #     method_node = self.class_def.methods[name]
        #     # Return a callable bound to this instance
        #     return lambda *args: method_node.eval(self, *args)
        raise RuntimeError(f"Property or method '{name}' not found in instance of {self.class_def.name}")

    def set(self, name, value):
        self.fields[name] = value

class ClassTable:
    """Stores all class definitions."""
    def __init__(self):
        self.classes = {}

    def define_class(self, name, class_def):
        self.classes[name] = class_def

    def get_class(self, name):
        if name not in self.classes:
            raise RuntimeError(f"Class '{name}' is not defined")
        return self.classes[name]
