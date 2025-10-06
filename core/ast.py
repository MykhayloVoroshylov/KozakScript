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
    class_name: str
    arguments: list = dataclasses.field(default_factory=list)
    class_def: object = None 
    properties: dict = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class KozakPropertyAccess:
    instance: object
    property_name: str

@dataclasses.dataclass
class KozakPropertyAssign:
    instance: object
    property_name: str
    value: object

@dataclasses.dataclass
class KozakDictionary:
    pairs: list
@dataclasses.dataclass
class KozakDictionaryAccess:
    dictionary: object
    key: object

