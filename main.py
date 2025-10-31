"""Main.py file for the KozakScript programming language."""

import sys
import os
import re
import argparse
from core.lexer import lex
from core.parser import Parser
from core.interpreter import Interpreter
from core.interpreter import RuntimeErrorKozak, ProgramExit

funny_hints = {
    r"Expected SEMICOLON": "Ay Kozache! Even borshch needs a spoon, your code needs a semicolon.",
    r"not defined": "Oy, Kozache! You try to ride a horse that is not there.",
    r"divide by zero": "Dividing by zero? Kozak magic cannot break math, sorry.",
    r"array index out of bounds": "You search for varenyky outside the pot, Kozache!",
    r"function '.*' is not defined": "Function not found! Maybe it went to war without telling you."
}

def print_with_hint(err: str):
    print(err)
    for pattern, hint in funny_hints.items():
        if re.search(pattern, err, re.IGNORECASE):
            print("Hint:", hint)
            break

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(
        description='KozakScript Interpreter - A multi-dialect programming language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py program.kozak                  # Run with dialect mixing allowed
  python main.py program.kozak --strict         # Enforce single dialect
  python main.py program.kozak -s               # Short form
        '''
    )
    parser.add_argument('file', help='KozakScript file to execute (.kozak extension)')
    parser.add_argument('--skip-strict', '-s', action='store_true',
                       help='Enforce strict dialect mode (no mixing dialects)')
    
    args = parser.parse_args()

    exit_code = 0
    
    try:
        
        file_path = args.file

        if len(sys.argv) < 2:
            raise ValueError("Ay Ay Ay, Kozache! You must provide a file to run. Example: python main.py my_program.kozak")

        file_path = sys.argv[1]

        if not file_path.endswith('.kozak'):
            raise ValueError("Oy bida, Kozache! The file must have a '.kozak' extension.")

        with open(file_path, 'r', encoding="utf-8") as f:
            code = f.read()

        tokens = list(lex(code))
        parser = Parser(tokens, strict_dialect=not args.skip_strict)
        ast = parser.parse()

        if parser.errors:
            print("Bida, kozache! Errors found:")
            for e in parser.errors:
                err = str(e)
                print_with_hint(err)

            if not args.skip_strict and parser.dialect_violations:
                print(f"\n🚫 Dialect Enforcement: Found {len(parser.dialect_violations)} violation(s)")
                print(f"   Detected dialect: {parser.detected_dialect}")
                print("   Govory odnieyu movoyu, kozache! Nichogo ne rozumiyu!")
                print("   Tip: Use one dialect consistently throughout your program.")

            exit_code = 1
        else:

            if not args.skip_strict and parser.detected_dialect:
                print(f"✓ Dialect check passed: Using {parser.detected_dialect} dialect")

            interpreter = Interpreter(
                strict_dialect=not args.skip_strict,
                parent_dialect=parser.detected_dialect
            )
            
            interpreter.current_file_dir = os.path.dirname(os.path.abspath(file_path))
            try:
                interpreter.eval(ast)
                exit_code = interpreter.exit_code
                print(f"Program executed successfully, kozache! \nProgram exited with code {exit_code}")
                if exit_code != 0:
                    raise ProgramExit(exit_code)
            except ProgramExit as e:
                exit_code = e.code
                print(f"Program exited with code {exit_code}, kozache!")
            
                    
        
    except RuntimeErrorKozak as e:
        print("Bida, kozache! Runtime error:")
        print_with_hint(str(e))
        exit_code = 1
        print(f"Error kozache! Program exited with code {exit_code}")
    except FileNotFoundError:
        print(f"Oslip ya, chy tviy file znyk, Kozache? The file '{file_path}' was not found")
        exit_code = 1
        print(f"Error kozache! Program exited with code {exit_code}")
    except Exception as e:
        print("Neperedbachena bida! An unexpected error occurred:")
        print_with_hint(str(e))
        exit_code = 1
        print(f"Error kozache! Program exited with code {exit_code}")

