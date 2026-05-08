# KozakScript

![Version](https://img.shields.io/badge/version-0.9-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Core](https://img.shields.io/badge/core-Python%20%2B%20C%2B%2B-orange)
![Status](https://img.shields.io/badge/status-active_development-green)

**[Українська 🇺🇦](README.uk.md) | [Русский 🇷🇺](README.ru.md)**

KozakScript is an experimental multi-dialect programming language inspired by C++, Python, and Pascal.

The project was originally created as a fun and educational idea: a programming language that allows people to learn and write code using syntax and terminology closer to their native language. Over time, the project evolved beyond a simple prototype into a functional interpreted language with executable bundling support, multiple syntax dialects, and standalone application generation.

KozakScript currently supports:
- Ukrainian syntax
- Ukrainian Cyrillic syntax
- Russian syntax
- Russian Cyrillic syntax
- English syntax
- Symbolic syntax

The language is still under active development, and new features, syntax improvements, and modules are continuously being added.

---

# ✨ Features

- Multiple syntax dialects
- Standalone executable bundling
- Embedded runtime distribution
- No Python installation required for end users
- Syntax inspired by C++, Python, and Pascal
- Support for external asset embedding
- Experimental game module support
- Human-readable syntax design
- Cross-dialect language structure

---

# 🚀 Installation

Download the latest release and extract the files anywhere on your system.

No separate Python installation is required to run KozakScript programs or bundled executables.

---

# ▶️ Running Programs

Use the interpreter executable to run `.kozak` files:

```bash
KozakScriptInterpreter.exe path\to\program.kozak
```

Example:

```bash
KozakScriptInterpreter.exe hello.kozak
```

---

# 🧪 Syntax Examples

## Ukrainian (Latin)

```kozak
Hetman
Spivaty("Pryvit, svite!");
```

## Ukrainian (Cyrillic)

```kozak
Гетьман
Співати("Привіт, світе!");
```

## English

```kozak
Chief
Print("Hello World!");
```

## Russian (Latin)

```kozak
Ataman
Pechatat("Privet, mir!");
```

## Russian (Cyrillic)

```kozak
Атаман
Печатать("Привет, мир!");
```

## Symbolic

```kozak
>>>
!("Hello World!");
```

More examples can be found in:
- `Examples/`
- `test.kozak`
- `test_EN.kozak`
- `test_RU.kozak`
- `test_Sym.kozak`

---

# 📦 Bundling Executables

KozakScript includes a built-in bundler capable of packaging `.kozak` programs into standalone Windows executables.

Bundled applications:
- include the required runtime internally
- do not require Python installation
- can include additional assets and modules

## Basic Usage

```bash
kozak_bundler.exe my_program.kozak
```

---

## 📁 Adding Additional Files

You can embed external files into the final executable.

### Format

```bash
kozak_bundler.exe my_program.kozak --add-data source_path;destination_name
```

### Example

```bash
kozak_bundler.exe game.kozak --add-data config.json;config.json
```

Multiple files may be added:

```bash
kozak_bundler.exe game.kozak ^
--add-data config.json;config.json ^
--add-data assets/sprite.png;sprite.png ^
--add-data sounds/hit.wav;hit.wav
```

---

# 🌍 Supported Dialects

KozakScript currently supports multiple syntax systems designed to provide flexibility and accessibility for different users.

| Dialect | Writing System |
|---|---|
| Ukrainian | Latin |
| Ukrainian | Cyrillic |
| Russian | Latin |
| Russian | Cyrillic |
| English | Latin |
| Symbolic | Symbols |

Additional dialects may be added in future versions.

---

# 🚧 Project Status

KozakScript is currently in active development.

The language is functional and usable, but certain features, modules, and syntax elements may still change before version 1.0.

---

# 🤝 Contributing

Suggestions, ideas, and feedback are welcome.

If you encounter bugs or would like to propose improvements, please open a GitHub Issue.

---

# 🐛 Reporting Bugs

If you encounter any issues:
1. Open a GitHub Issue
2. Describe the problem
3. Include screenshots or error logs if possible
4. Provide the `.kozak` code that caused the issue

This helps improve the language and tooling for future releases.

---

# 📜 License

KozakScript is distributed under the MIT License.

This project bundles components from:
- Python
- Pygame

These components are distributed under their own respective licenses.

See:
- `LICENSE`
- `PYGAME_LGPL.txt.txt`
- `PYTHON_LICENSE.txt`

for additional information.
