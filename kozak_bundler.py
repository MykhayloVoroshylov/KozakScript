import os
import sys
import shutil
import subprocess

# === CONFIGURATION ===
INTERPRETER_EXE = "main.exe"  # compiled interpreter
OUTPUT_FOLDER = "build_exe"
MARKER = b"---KOZAK_PAYLOAD_START---"

# === COLORS (for nice terminal look) ===
C = {
    "reset": "\033[0m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m"
}


def bundle(kozak_file, icon_file=None):
    """Bundle a .kozak script into a standalone executable"""
    if not os.path.exists(INTERPRETER_EXE):
        print(f"{C['red']}[ERROR]{C['reset']} Interpreter not found at: {INTERPRETER_EXE}")
        print(f"{C['yellow']}Hint: Compile main.py first using PyInstaller:{C['reset']}")
        print(f"  pyinstaller --onefile --name interpreter main.py")
        return False

    if not os.path.exists(kozak_file):
        print(f"{C['red']}[ERROR]{C['reset']} Script not found: {kozak_file}")
        return False

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(kozak_file))[0]
    output_exe = os.path.join(OUTPUT_FOLDER, base_name + ".exe")

    # Step 1 – Copy base interpreter
    print(f"{C['cyan']}→ Copying base interpreter...{C['reset']}")
    shutil.copy(INTERPRETER_EXE, output_exe)

    # Step 2 – Append script data
    print(f"{C['cyan']}→ Embedding script: {kozak_file}{C['reset']}")
    with open(output_exe, "ab") as exe, open(kozak_file, "rb") as script:
        exe.write(b"\n" + MARKER + b"\n")
        exe.write(script.read())

    print(f"{C['green']}✓ Bundled successfully:{C['reset']} {output_exe}")

    # Step 3 – Add icon (if provided)
    if icon_file:
        if not os.path.exists(icon_file):
            print(f"{C['yellow']}⚠ Icon not found: {icon_file}{C['reset']}")
        else:
            apply_icon(output_exe, icon_file)

    return True


def apply_icon(exe_path, icon_file):
    """Apply custom icon to executable"""
    print(f"{C['cyan']}→ Applying icon...{C['reset']}")
    
    # Try rcedit first (simplest)
    if shutil.which("rcedit"):
        try:
            subprocess.run(
                ["rcedit", exe_path, "--set-icon", icon_file],
                check=True,
                capture_output=True
            )
            print(f"{C['green']}✓ Icon applied successfully!{C['reset']}")
            return
        except subprocess.CalledProcessError as e:
            print(f"{C['yellow']}⚠ rcedit failed: {e}{C['reset']}")
    
    # Try ResourceHacker
    if shutil.which("ResourceHacker"):
        try:
            subprocess.run(
                ["ResourceHacker", "-open", exe_path, "-save", exe_path,
                 "-action", "addoverwrite", "-res", icon_file,
                 "-mask", "ICONGROUP,MAINICON,"],
                check=True,
                capture_output=True
            )
            print(f"{C['green']}✓ Icon applied successfully!{C['reset']}")
            return
        except subprocess.CalledProcessError as e:
            print(f"{C['yellow']}⚠ ResourceHacker failed: {e}{C['reset']}")
    
    print(f"{C['yellow']}⚠ Could not apply icon automatically.{C['reset']}")
    print(f"{C['cyan']}Install 'rcedit' or 'Resource Hacker' to use --icon feature.{C['reset']}")
    print(f"{C['cyan']}rcedit: https://github.com/electron/rcedit/releases{C['reset']}")


def main():
    print(f"{C['bold']}{C['green']}╔═══════════════════════════════════╗{C['reset']}")
    print(f"{C['bold']}{C['green']}║   KozakScript Bundler v1.0        ║{C['reset']}")
    print(f"{C['bold']}{C['green']}╚═══════════════════════════════════╝{C['reset']}")
    print()

    if len(sys.argv) < 2:
        print(f"{C['bold']}Usage:{C['reset']}")
        print(f"  python kozak_bundler.py <script.kozak> [--icon <icon.ico>]")
        print()
        print(f"{C['bold']}Examples:{C['reset']}")
        print(f"  python kozak_bundler.py hello.kozak")
        print(f"  python kozak_bundler.py game.kozak --icon logo.ico")
        sys.exit(1)

    kozak_file = None
    icon_file = None

    # Parse arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--icon":
            if i + 1 < len(sys.argv):
                icon_file = sys.argv[i + 1]
                i += 2
            else:
                print(f"{C['red']}[ERROR]{C['reset']} --icon requires a file path")
                sys.exit(1)
        elif arg.endswith(".kozak") or arg.endswith(".koz"):
            kozak_file = arg
            i += 1
        else:
            print(f"{C['yellow']}[WARNING]{C['reset']} Unknown argument: {arg}")
            i += 1

    if not kozak_file:
        print(f"{C['red']}[ERROR]{C['reset']} No .kozak file specified.")
        sys.exit(1)

    success = bundle(kozak_file, icon_file)
    
    if success:
        print()
        print(f"{C['green']}{C['bold']}═══════════════════════════════════{C['reset']}")
        print(f"{C['green']}🎉 Bundling complete, Kozache!{C['reset']}")
        print(f"{C['green']}{C['bold']}═══════════════════════════════════{C['reset']}")
        print(f"\n{C['cyan']}Your executable is ready to share!{C['reset']}")
    else:
        print()
        print(f"{C['red']}❌ Bundling failed. Fix errors above.{C['reset']}")
        sys.exit(1)


if __name__ == "__main__":
    main()