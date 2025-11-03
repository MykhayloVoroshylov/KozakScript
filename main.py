"""Main.py file for the KozakScript programming language."""

import sys
import os
import re
import argparse
from core.lexer import lex
from core.parser import Parser
from core.interpreter import Interpreter
from core.interpreter import RuntimeErrorKozak, ProgramExit


def extract_embedded_script():
    """Extract script from bundled executable"""
    try:
        with open(sys.executable, 'rb') as f:
            content = f.read()
            marker = b"---KOZAK_PAYLOAD_START---"
            if marker in content:
                script_start = content.index(marker) + len(marker)
                script_data = content[script_start:].strip()
                # Normalize line endings (Windows \r\n -> Unix \n)
                decoded = script_data.decode('utf-8')
                return decoded.replace('\r\n', '\n').replace('\r', '\n')
    except Exception as e:
        # Silently fail if not a bundled exe
        pass
    return None


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


def run_code(code, strict_dialect=False):
    """Execute KozakScript code"""
    exit_code = 0
    
    try:
        tokens = list(lex(code))
        parser = Parser(tokens, strict_dialect=strict_dialect)
        ast = parser.parse()

        if parser.errors:
            print("Bida, kozache! Errors found:")
            for e in parser.errors:
                err = str(e)
                print_with_hint(err)

            if strict_dialect and parser.dialect_violations:
                print(f"\n🚫 Dialect Enforcement: Found {len(parser.dialect_violations)} violation(s)")
                print(f"   Detected dialect: {parser.detected_dialect}")
                print("   Govory odnieyu movoyu, kozache! Nichogo ne rozumiyu!")
                print("   Tip: Use one dialect consistently throughout your program.")

            return 1
        else:
            if strict_dialect and parser.detected_dialect:
                print(f"✓ Dialect check passed: Using {parser.detected_dialect} dialect")

            interpreter = Interpreter(
                strict_dialect=strict_dialect,
                parent_dialect=parser.detected_dialect
            )
            
            # Set current directory for imports
            interpreter.current_file_dir = os.getcwd()
            
            try:
                interpreter.eval(ast)
                exit_code = interpreter.exit_code
                print(f"\nProgram executed successfully, kozache!")
                print(f"Program exited with code {exit_code}")
            except ProgramExit as e:
                exit_code = e.code
                print(f"\nProgram exited with code {exit_code}, kozache!")
                
    except RuntimeErrorKozak as e:
        print("Bida, kozache! Runtime error:")
        print_with_hint(str(e))
        exit_code = 1
    except Exception as e:
        print("Neperedbachena bida! An unexpected error occurred:")
        print_with_hint(str(e))
        exit_code = 1
    
    return exit_code


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')

    # Check if this is a bundled executable with embedded script
    embedded_script = extract_embedded_script()
    if embedded_script:
        print("Running bundled KozakScript program...\n")
        exit_code = run_code(embedded_script, strict_dialect=False)
        input("\nPress Enter to exit, kozache...")
        sys.exit(exit_code)

    # Normal mode: parse command line arguments
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
                       help='Skip strict dialect mode (allow mixing dialects)')
    
    args = parser.parse_args()

    exit_code = 0
    
    try:
        file_path = args.file

        if not file_path.endswith('.kozak'):
            raise ValueError("Oy bida, Kozache! The file must have a '.kozak' extension.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found")

        with open(file_path, 'r', encoding="utf-8") as f:
            code = f.read()

        # Run the code
        exit_code = run_code(code, strict_dialect=not args.skip_strict)
            
    except FileNotFoundError as e:
        print(f"Oslip ya, chy tviy file znyk, Kozache? {e}")
        exit_code = 1
    except Exception as e:
        print("Neperedbachena bida! An unexpected error occurred:")
        print_with_hint(str(e))
        exit_code = 1

    input("\nPress Enter to exit, kozache...")
    sys.exit(exit_code)