"""Abstract Syntax Tree for KozakScript"""

import dataclasses

@dataclasses.dataclass (slots=True)
class KozakIf:
    condition: object
    body: list
    else_if_parts: list = dataclasses.field(default_factory=list)
    else_part: object = None

@dataclasses.dataclass (slots=True)
class KozakWhile:
    condition: object
    body: list

@dataclasses.dataclass (slots=True)
class KozakUnaryOp:
    op: str
    target: object

@dataclasses.dataclass (slots=True)
class KozakFor:
    initialization: object
    condition: object
    step: object
    body: list

@dataclasses.dataclass (slots=True)
class KozakFunctionDef:
    name: str
    parameters: list
    body: list
    param_types: dict = dataclasses.field(default_factory=dict)
    return_type: str = None
    access_modifier: str = 'public'

@dataclasses.dataclass (slots=True)
class KozakFunctionCall:
    name: str
    arguments: list

@dataclasses.dataclass (slots=True)
class KozakReturn:
    value: object

@dataclasses.dataclass (slots=True)
class KozakEcho:
    expressions: list

@dataclasses.dataclass (slots=True)
class KozakBinOp:
    left: object
    op: str
    right: object

@dataclasses.dataclass (slots=True)
class KozakNumber:
    value: object

@dataclasses.dataclass (slots=True)
class KozakString:
    value: str

@dataclasses.dataclass (slots=True)
class KozakVariable:
    name: str

@dataclasses.dataclass (slots=True)
class KozakAssign:
    name: str
    expr: object
    type_hint: str = None

@dataclasses.dataclass (slots=True)
class KozakProgram:
    statements: list

@dataclasses.dataclass (slots=True)
class KozakInput:
    expr: object

@dataclasses.dataclass (slots=True)
class KozakBoolean:
    value: bool

@dataclasses.dataclass (slots=True)
class KozakComparisonOp:
    left: object
    op: str
    right: object

@dataclasses.dataclass (slots=True)
class KozakTypeCast:
    target_type: str
    expr: object

@dataclasses.dataclass (slots=True)
class KozakArray:
    elements: list

@dataclasses.dataclass (slots=True)
class KozakArrayIndex:
    array: object
    index: object

@dataclasses.dataclass (slots=True)
class KozakForEach:
    var_name: str
    array_expr: object
    body: list

@dataclasses.dataclass (slots=True)
class KozakClass:
    name: str
    methods: dict
    constructor: object = None
    parent_name: str = None
    field_access: dict = dataclasses.field(default_factory=dict)
    method_access: dict = dataclasses.field(default_factory=dict)
    friends: list = dataclasses.field(default_factory=list)
    friend_classes: list = dataclasses.field(default_factory=list)

@dataclasses.dataclass (slots=True)
class KozakNewInstance:
    class_name: str
    arguments: list = dataclasses.field(default_factory=list)
    class_def: object = None 
    properties: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass (slots=True)
class KozakPropertyAccess:
    instance: object
    property_name: str

@dataclasses.dataclass (slots=True)
class KozakPropertyAssign:
    instance: object
    property_name: str
    value: object

@dataclasses.dataclass (slots=True)
class KozakMethodCall:
    instance: object
    method_name: str
    arguments: list = dataclasses.field(default_factory=list)

@dataclasses.dataclass (slots=True)
class KozakDictionary:
    pairs: list 

@dataclasses.dataclass (slots=True)
class KozakDictionaryAccess:
    dictionary: object
    key: object

@dataclasses.dataclass (slots=True)
class KozakTry:
    try_body: list
    catch_clauses: list = dataclasses.field(default_factory=list)
    finally_body: list = None

@dataclasses.dataclass (slots=True)
class KozakThrow:
    message: object  

@dataclasses.dataclass (slots=True)
class KozakExit:
    code: object = None

@dataclasses.dataclass (slots=True)
class KozakImport:
    file_path: object

@dataclasses.dataclass (slots=True)
class KozakSuper:
    method_name: str
    arguments: list = dataclasses.field(default_factory=list)