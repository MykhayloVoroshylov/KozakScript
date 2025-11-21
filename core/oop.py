"""OOP support for KozakScript."""

class ClassDef:
    """Represents a class definition in KozakScript."""
    def __init__(self, name, methods, constructor=None, parent_class=None, field_access=None, method_access=None, friends=None):
        self.name = name
        self.methods = methods  # dict: method_name -> method_node
        self.constructor = constructor  # Node for Tvir (constructor) if exists
        self.parent_class = parent_class  # ClassDef of parent class if inheritance is used
        self.field_access = field_access or {} # dict: field_name -> access_level
        self.method_access = method_access or {} # dict: method_name -> access_level
        self.friends = friends or [] # list of friend function names

    def find_method(self, name):
        """Recursively search for a method in the class or its ancestors."""
        if name in self.methods:
            return self.methods[name]
        
        # Recurse up the inheritance chain
        if self.parent_class:
            return self.parent_class.find_method(name)
            
        return None
    
    def get_method_access(self, name):
        """Get the access level of a method"""
        if name in self.method_access:
            return self.method_access[name]
        
        if self.parent_class:
            return self.parent_class.get_method_access(name)
        
        return 'public'  # default
    
    def get_field_access(self, name):
        """Get the access level of a field"""
        if name in self.field_access:
            return self.field_access[name]
        
        if self.parent_class:
            return self.parent_class.get_field_access(name)
        
        return 'public'  # default
    
    def is_friend(self, function_name):
        """Check if a function is a friend of this class"""
        if function_name in self.friends:
            return True
        
        # Check parent class friends
        if self.parent_class:
            return self.parent_class.is_friend(function_name)
        
        return False


class Instance:
    """Represents an object instance."""
    def __init__(self, class_def, ):
        self.class_def = class_def
        self.fields = {}  # instance variables

    def get(self, name, calling_instance=None, calling_function=None):
        # First check instance fields
        if name in self.fields:
            access_level = self.class_def.get_field_access(name)
            
            if access_level == 'private':
                # Allow if calling function is a friend
                if calling_function and self.class_def.is_friend(calling_function):
                    return self.fields[name]
                
                if calling_instance is not self:
                    raise RuntimeError(f"Cannot access private field '{name}' of class {self.class_def.name}")
            
            elif access_level == 'protected':
                # Allow if calling function is a friend
                if calling_function and self.class_def.is_friend(calling_function):
                    return self.fields[name]
                
                if calling_instance is not None and not self._is_subclass_of(calling_instance.class_def):
                    raise RuntimeError(f"Cannot access protected field '{name}' of class {self.class_def.name}")
            
            return self.fields[name]

        
        method_node = self.class_def.find_method(name)

        if method_node:
            access_level = self.class_def.get_method_access(name)
            if access_level == 'private':
                if calling_instance is not self:
                    raise RuntimeError(f"Cannot access private method '{name}' of class {self.class_def.name}")
            elif access_level == 'protected':
                    if calling_instance is not None and not self._is_subclass_of(calling_instance.class_def):
                        raise RuntimeError(f"Cannot access protected method '{name}' of class {self.class_def.name}")
            return lambda *args: method_node.eval(self, *args)

        raise RuntimeError(f"Property or method '{name}' not found in instance of {self.class_def.name}")

    def set(self, name, value, calling_instance=None, calling_function=None):
        access_level = self.class_def.get_field_access(name)
        
        if access_level == 'private':
            # Allow if calling function is a friend
            if calling_function and self.class_def.is_friend(calling_function):
                self.fields[name] = value
                return
            
            if calling_instance is not self:
                raise RuntimeError(f"Cannot modify private field '{name}' of class {self.class_def.name}")
        
        elif access_level == 'protected':
            # Allow if calling function is a friend
            if calling_function and self.class_def.is_friend(calling_function):
                self.fields[name] = value
                return
            
            if calling_instance is not None and not self._is_subclass_of(calling_instance.class_def):
                raise RuntimeError(f"Cannot modify protected field '{name}' of class {self.class_def.name}")
        
        self.fields[name] = value
    
    def _is_subclass_of(self, other_class_def):
        """Check if this instance's class is a subclass of another class"""
        current = self.class_def
        while current:
            if current == other_class_def:
                return True
            current = current.parent_class
        return False


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
