import sys
from core.lexer import lex
from core.parser import Parser
from core.interpreter import Interpreter
from core.errors import KozakError, KozakSyntaxError

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            raise ValueError("Ay Ay Ay, Kozache! You must provide a file to run. Example: python main.py my_program.kozak")

        file_path = sys.argv[1]

        if not file_path.endswith('.kozak'):
            raise ValueError("Oy bida, Kozache! The file must have a '.kozak' extension.")

        code = open(file_path, 'r', encoding='utf-8').read()
        tokens = list(lex(code))
        parser = Parser(tokens)
        ast = parser.parse()
        print("Output:")

        interpreter = Interpreter()
        interpreter.eval(ast)

    except (KozakError) as e:
        # Handle aggregated syntax errors
        print(f"Bida, kozache! Errors found:{e}")
        #print(e)  # The parser already formats the errors in `self.errors`

    except KozakSyntaxError as e:
        print(f"Bida, kozache! Syntax error: {e}")


    except FileNotFoundError:
        print(f"Oslip ya, chy tviy file znyk, Kozache? The file '{file_path}' was not found")

    except Exception as e:
        print(f"Neperedbachena bida! An unexpected error occurred: {e}")
