"""Main.py file for the KozakScript programming language."""

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


def extract_embedded_script():
    """Extract script from bundled executable"""
    if not getattr(sys, 'frozen', False):
        # Not running as a frozen executable, skip
        return None
    
    try:
        with open(sys.executable, 'rb') as f:
            content = f.read()
            
        marker_start = b"---KOZAK_PAYLOAD_START---"
        marker_end = b"---KOZAK_PAYLOAD_END---"
        
        # Check if this is a bundled executable
        if marker_start not in content:
            return None
        
        # Find script boundaries
        script_start = content.index(marker_start) + len(marker_start)
        
        if marker_end in content[script_start:]:
            script_end = content.index(marker_end, script_start)
        else:
            # If no end marker found, something is wrong
            print("Warning: Could not find script end marker")
            return None
        
        # Extract and decode script
        script_data = content[script_start:script_end]
        
        # Remove any leading/trailing whitespace and newlines
        script_data = script_data.strip()
        
        # Decode to UTF-8 string
        decoded = script_data.decode('utf-8', errors='replace')
        
        # Normalize line endings
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
                return None  # No bundled data
            
            # Extract manifest
            start_idx = content.index(manifest_start) + len(manifest_start)
            end_idx = content.index(manifest_end)
            manifest_json = content[start_idx:end_idx].strip().decode('utf-8')
            manifest = json.loads(manifest_json)
            
            # Extract data files
            data_files = []
            file_marker_start = b"---DATA_FILE_START---"
            file_marker_end = b"---DATA_FILE_END---"
            
            search_pos = 0
            for file_info in manifest:
                # Find next data file
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
    
    # Create a temporary directory for extracted files
    temp_dir = tempfile.mkdtemp(prefix="kozak_data_")
    print(f"Extracting bundled data to: {temp_dir}")
    
    for file_info in data_files:
        dest_path = os.path.join(temp_dir, file_info['destination'])
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Write the file
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
    
    # Change to data directory if provided
    original_dir = os.getcwd()
    if data_dir:
        os.chdir(data_dir)
    
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
            interpreter.current_file_dir = data_dir if data_dir else os.getcwd()
            
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
    finally:
        # Restore original directory
        if data_dir:
            os.chdir(original_dir)
    
    return exit_code


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')

    # Check if this is a bundled executable with embedded script
    embedded_script = extract_embedded_script()

    if embedded_script:
        
        # Extract bundled data files
        data_dir = setup_bundled_data()
        if data_dir:
            print()
        
        exit_code = run_code(embedded_script, strict_dialect=False, data_dir=data_dir)
        input("\nPress Enter to exit, kozache...")
        sys.exit(exit_code)
    # else:
    #     print("DEBUG: No embedded script found, running in normal mode")
    # if embedded_script:
    #     print("Running bundled KozakScript program...\n")
        
    #     # Extract bundled data files
    #     data_dir = setup_bundled_data()
    #     if data_dir:
    #         print()
        
    #     exit_code = run_code(embedded_script, strict_dialect=False, data_dir=data_dir)
    #     input("\nPress Enter to exit, kozache...")
    #     sys.exit(exit_code)

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