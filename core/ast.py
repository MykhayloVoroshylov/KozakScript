"""Abstract Syntax Tree for KozakScript"""

import dataclasses

@dataclasses.dataclass
class KozakIf:
    condition: object
    body: list
    else_if_parts: list = dataclasses.field(default_factory=list)
    else_part: object = None

@dataclasses.dataclass
class KozakWhile:
    condition: object
    body: list

@dataclasses.dataclass
class KozakUnaryOp:
    op: str
    target: object

@dataclasses.dataclass
class KozakFor:
    initialization: object
    condition: object
    step: object
    body: list

@dataclasses.dataclass
class KozakFunctionDef:
    name: str
    parameters: list
    body: list

@dataclasses.dataclass
class KozakFunctionCall:
    name: str
    arguments: list

@dataclasses.dataclass
class KozakReturn:
    value: object

@dataclasses.dataclass
class KozakEcho:
    expressions: list

@dataclasses.dataclass
class KozakBinOp:
    left: object
    op: str
    right: object

@dataclasses.dataclass
class KozakNumber:
    value: object

@dataclasses.dataclass
class KozakString:
    value: str

@dataclasses.dataclass
class KozakVariable:
    name: str

@dataclasses.dataclass
class KozakAssign:
    name: str
    expr: object

@dataclasses.dataclass
class KozakProgram:
    statements: list

@dataclasses.dataclass
class KozakInput:
    expr: object

@dataclasses.dataclass
class KozakBoolean:
    value: bool

@dataclasses.dataclass
class KozakComparisonOp:
    left: object
    op: str
    right: object

@dataclasses.dataclass
class KozakTypeCast:
    target_type: str
    expr: object

@dataclasses.dataclass
class KozakArray:
    elements: list

@dataclasses.dataclass
class KozakArrayIndex:
    array: object
    index: object

@dataclasses.dataclass
class KozakForEach:
    var_name: str
    array_expr: object
    body: list

@dataclasses.dataclass
class KozakClass:
    name: str
    methods: dict
    constructor: object = None

@dataclasses.dataclass
class KozakNewInstance:
    class_name: str                      # 1. Ім'я класу (обов'язково)
    arguments: list = dataclasses.field(default_factory=list) # 2. Аргументи конструктора (за замовчуванням [])
    # Ці поля буде заповнювати інтерпретатор, а не парсер
    class_def: object = None 
    properties: dict = dataclasses.field(default_factory=dict)

# Explicitly define Property Access nodes to ensure consistent field names
@dataclasses.dataclass
class KozakPropertyAccess:
    instance: object      # The expression that evaluates to the object (e.g., 'sobaka')
    property_name: str    # The name of the property (e.g., 'Bark')

@dataclasses.dataclass
class KozakPropertyAssign:
    instance: object      # The expression that evaluates to the object
    property_name: str    # The name of the property to assign to
    value: object         # The expression for the value being assigned
