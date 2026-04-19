"""Main.py file for the KozakScript programming language."""
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pygame')
import sys
import os
import re
import argparse
import json
import tempfile
from core.lexer import lex
from core.parser import Parser
from core.interpreter import Interpreter
from core.interpreter import RuntimeErrorKozak, ProgramExit
from core.dialect_messages import DialectMessages
from core.interpreter import DialectChecker



def extract_embedded_script():
    """Extract script from bundled executable"""
    if not getattr(sys, 'frozen', False):
        return None
    
    try:
        with open(sys.executable, 'rb') as f:
            content = f.read()
            
        marker_start = b"---KOZAK_PAYLOAD_START---"
        marker_end = b"---KOZAK_PAYLOAD_END---"
        
        if marker_start not in content:
            return None
        
        script_start = content.index(marker_start) + len(marker_start)
        
        if marker_end in content[script_start:]:
            script_end = content.index(marker_end, script_start)
        else:
            print("Warning: Could not find script end marker")
            return None
        
        script_data = content[script_start:script_end]
        script_data = script_data.strip()
        decoded = script_data.decode('utf-8', errors='replace')
        decoded = decoded.replace('\r\n', '\n').replace('\r', '\n')
        
        return decoded
        
    except Exception as e:
        print(f"Error extracting embedded script: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_bundled_data():
    """Extract additional data files from bundled executable"""
    try:
        with open(sys.executable, 'rb') as f:
            content = f.read()
            
            manifest_start = b"---DATA_MANIFEST_START---"
            manifest_end = b"---DATA_MANIFEST_END---"
            
            if manifest_start not in content:
                return None
            
            start_idx = content.index(manifest_start) + len(manifest_start)
            end_idx = content.index(manifest_end)
            manifest_json = content[start_idx:end_idx].strip().decode('utf-8')
            manifest = json.loads(manifest_json)
            
            data_files = []
            file_marker_start = b"---DATA_FILE_START---"
            file_marker_end = b"---DATA_FILE_END---"
            
            search_pos = 0
            for file_info in manifest:
                start = content.index(file_marker_start, search_pos) + len(file_marker_start)
                end = content.index(file_marker_end, start)
                
                file_content = content[start:end].strip()
                data_files.append({
                    'destination': file_info['destination'],
                    'content': file_content
                })
                
                search_pos = end + len(file_marker_end)
            
            return data_files
    except Exception as e:
        print(f"Warning: Could not extract bundled data: {e}")
        return None


def setup_bundled_data():
    """Extract bundled data files to temporary directory and set up paths"""
    data_files = extract_bundled_data()
    if not data_files:
        return None
    
    temp_dir = tempfile.mkdtemp(prefix="kozak_data_")
    print(f"Extracting bundled data to: {temp_dir}")
    
    for file_info in data_files:
        dest_path = os.path.join(temp_dir, file_info['destination'])
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        with open(dest_path, 'wb') as f:
            f.write(file_info['content'])
        
        print(f"  • Extracted: {file_info['destination']}")
    
    return temp_dir


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


def run_code(code, strict_dialect=False, data_dir=None):
    """Execute KozakScript code"""
    
    exit_code = 0
    
    original_dir = os.getcwd()
    if data_dir:
        os.chdir(data_dir)
    
    try:
        tokens = list(lex(code))
        kozak_parser = Parser(tokens, strict_dialect=strict_dialect)  
        ast = kozak_parser.parse()
        
        # ✅ Check for parser errors first
        if kozak_parser.errors:
            error_header = DialectMessages.get_message(
                'ERROR_HEADERS', 
                kozak_parser.detected_dialect or 'english'
            )
            print(error_header)
            
            for e in kozak_parser.errors:
                err = str(e)
                print_with_hint(err)

            if strict_dialect and kozak_parser.dialect_violations:
                print(f"\n🚫 Dialect Enforcement: Found {len(kozak_parser.dialect_violations)} violation(s)")
                print(f"   Detected dialect: {kozak_parser.detected_dialect}")
                
                if kozak_parser.detected_dialect == 'ukrainian_latin':
                    print("   Govory odnieyu movoyu, kozache! Nichogo ne rozumiyu!")
                elif kozak_parser.detected_dialect == 'ukrainian_cyrillic':
                    print("   Говори однією мовою, козаче! Нічого не розумію!")
                elif kozak_parser.detected_dialect == 'russian_latin':
                    print("   Govori na odnom yazyke, tovarisch! Nichego ne ponimayu!")
                elif kozak_parser.detected_dialect == 'russian_cyrillic':
                    print("   Говори на одном языке, товарищ! Ничего не понимаю")
                elif kozak_parser.detected_dialect == 'symbolic':
                    print("   PROTOCOL_VIOLATION: Mixed dialect tokens detected")
                else:
                    print("   Speak one language, pal! I don't understand!")
                
                print("   Tip: Use one dialect consistently throughout your program.")

            return 1, None  # ✅ Return dialect info
        
        # No errors, continue
        if strict_dialect and kozak_parser.detected_dialect:
            startup_msg = DialectMessages.get_message(
                'STARTUP_MESSAGES',
                kozak_parser.detected_dialect
            )
            print(startup_msg)

        interpreter = Interpreter(
            strict_dialect=strict_dialect,
            parent_dialect=kozak_parser.detected_dialect
        )
        
        interpreter.current_file_dir = data_dir if data_dir else os.getcwd()
        
        if kozak_parser.detected_dialect:
            checker = DialectChecker(kozak_parser.detected_dialect)
            checker.check(ast)
            if checker.errors:
                error_header = DialectMessages.get_message(
                    'ERROR_HEADERS',
                    kozak_parser.detected_dialect
                )
                print(error_header)
                for err in checker.errors:
                    print_with_hint(err)
                return 1, kozak_parser.detected_dialect
        try:
            interpreter.eval(ast)
            exit_code = interpreter.exit_code
            
            success_msg = DialectMessages.get_message(
                'SUCCESS_MESSAGES',
                kozak_parser.detected_dialect or 'english'
            )
            print(f"\n{success_msg}")
            
            exit_msg = DialectMessages.get_message(
                'EXIT_MESSAGES',
                kozak_parser.detected_dialect or 'english',
                code=exit_code
            )
            print(exit_msg)

        except ProgramExit as e:
            exit_code = e.code
            exit_msg = DialectMessages.get_message(
                'EXIT_MESSAGES',
                kozak_parser.detected_dialect or 'english',
                code=exit_code
            )
            print(f"\n{exit_msg}")
            
    except RuntimeErrorKozak as e:
        error_header = DialectMessages.get_message(
            'ERROR_HEADERS',
            getattr(kozak_parser, 'detected_dialect', None) or 'english'
        )
        print(error_header)
        print_with_hint(str(e))
        exit_code = 1
    except Exception as e:
        if detected_dialect == 'ukrainian_latin':
            print("Neperedbachena bida, kozache! An unexpected error occurred:")
        elif detected_dialect == 'russian_latin':
            print("Neozhydanaya beda, tovarisch! An unexpected error occurred:")
        elif detected_dialect == 'english':
            print("Unexpected error pal! An unexpected error occured:")
        elif detected_dialect == 'ukrainian_cyrillic':
            print("Непередбачена біда, козаче! Сталася несподівана помилка:")
        elif detected_dialect == 'russian_cyrillic':
            print("Неожиданная беда, товарищ! Случилась неожиданная ошибка:")
        elif detected_dialect == 'symbolic':
            print("PROGRAM TERMINATED WITH UNEXPECTED BEHAVIOR:")
        print_with_hint(str(e))
        exit_code = 1
    finally:
        if data_dir:
            os.chdir(original_dir)
    
    # ✅ Return both exit code and detected dialect
    detected = getattr(kozak_parser, 'detected_dialect', None) if 'kozak_parser' in locals() else None
    return exit_code, detected


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')

    embedded_script = extract_embedded_script()

    if embedded_script:
        data_dir = setup_bundled_data()
        if data_dir:
            print()
        
        exit_code, detected_dialect = run_code(embedded_script, strict_dialect=False, data_dir=data_dir)
        
        press_enter_msg = DialectMessages.get_message(
            'PRESS_ENTER_MESSAGES',
            detected_dialect
        )
        input(press_enter_msg)
        sys.exit(exit_code)
    
    # ✅ Normal mode - renamed to arg_parser
    arg_parser = argparse.ArgumentParser(
        description='KozakScript Interpreter - A multi-dialect programming language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py program.kozak                  # Run with dialect mixing allowed
  python main.py program.kozak --strict         # Enforce single dialect
  python main.py program.kozak -s               # Short form
        '''
    )
    arg_parser.add_argument('file', help='KozakScript file to execute (.kozak extension)')
    arg_parser.add_argument('--skip-strict', '-s', action='store_true',
                       help='Skip strict dialect mode (allow mixing dialects)')
    
    args = arg_parser.parse_args()
    exit_code = 0
    detected_dialect = None
    
    try:
        file_path = args.file

        if not file_path.endswith('.kozak'):
            if detected_dialect == 'ukrainian_latin':
                raise ValueError("Oy bida, Kozache! The file must have a '.kozak' extension.")
            elif detected_dialect == 'ukrainian_cyrillic':
                raise ValueError("Ой біда, козаче! Файл повинен мати розширення '.kozak'")
            elif detected_dialect == 'russian_latin':
                raise ValueError("Oy beda, tovarisch! The file must have a '.kozak' extension.")
            elif detected_dialect == 'russian_cyrillic':
                raise ValueError("Ой беда, товарищ! Файл должен иметь расширение '.kozak'")
            elif detected_dialect == 'symbolic':
                raise ValueError("ERROR: Invalid file extension. Expected '.kozak'")
            else:
                raise ValueError("Oh no, pal! The file must have a '.kozak' extension.")
            

        if not os.path.exists(file_path):
            if detected_dialect == 'ukrainian_latin':
                raise FileNotFoundError(f"Have I gone blind, or your file is gone, Kozache? \n'{file_path}' not found")
            elif detected_dialect == 'ukrainian_cyrillic':
                raise FileNotFoundError(f"Осліп я, чи твій файл зник, козаче? \n'{file_path}' не знайдено")
            elif detected_dialect == 'russian_latin':
                raise FileNotFoundError(f"Where has your file gone, tovarisch? \n'{file_path}' not found")
            elif detected_dialect == 'russian_cyrillic':
                raise FileNotFoundError(f"Куда твой файл подевался, товарищ? \n'{file_path}' не найден")
            elif detected_dialect == 'symbolic':
                raise FileNotFoundError(f"ERROR: File '{file_path}' not found")
            else:
                raise FileNotFoundError(f"File '{file_path}' not found, pal")            

        with open(file_path, 'r', encoding="utf-8") as f:
            code = f.read()

        exit_code, detected_dialect = run_code(code, strict_dialect=not args.skip_strict)
            
    except FileNotFoundError as e:
        exit_code = 1
    except Exception as e:
        if detected_dialect:
            error_header = DialectMessages.get_message(
                'ERROR_HEADERS',
                detected_dialect
            )
            print(error_header)
        print_with_hint(str(e))
        exit_code = 1

    # ✅ Use detected dialect for Press Enter message
    press_enter_msg = DialectMessages.get_message(
        'PRESS_ENTER_MESSAGES',
        detected_dialect 
    )
    input(press_enter_msg)
    sys.exit(exit_code)