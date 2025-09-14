from core.lexer import lex
from core.parser import Parser
from core.interpreter import Interpreter

if __name__ == '__main__':
    code = open('test.kozak', 'r').read()

    tokens = list(lex(code))
    parser = Parser(tokens)
    ast = parser.parse()

    print("Output:")

    interpreter = Interpreter()
    interpreter.eval(ast)

