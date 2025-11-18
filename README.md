# KozakScript

**[Українська 🇺🇦](README.uk.md) | [Русский 🇷🇺](README.ru.md)**

I am a coding enthusiast who decided to make my own programming language prototype. As a Ukrainian, I found it a fun idea, to make a language that reflects my culture, and can be used later, if needed, by professional programmers, or as a way for Ukrainian-speaking people to have an opportunity, which I personally never had: to learn programming with terms and words they are more familiar with, which is why I didn't stop on single HelloWorld program syntax, but went further to make the language actually functional.

The syntax is mostly similar to C++ and Python with a touch of Pascal. However it has its own unique features such as 4 supported dialects (Ukrainian, Russian, English and Symbolic). You can view the syntax examples in test.kozak file, or wait a bit: once I finish version 1.0, I will provide a .txt file with all the syntax rules, and possibly the YouTube videos explaining it. Additionally, you may find examples of programs in the "Examples" folder.

This is not a complete version yet — I am still improving it, adding new features, and fixing bugs. Most things are already functional and ready to use, so you can start having fun with it! :)

All the files labeled as "test" are used to test the features. Please don't modify it; you can create your own files for experimentation (or profesional development, if you wish to do so :) ).

---

## 🔧 Requirements

KozakScript used to require Python installed on the end-user machine, but no longer does. 

However, for bundling programs into `.exe` files, **ResourceHacker** is needed **only if you want to set a custom icon**.

### Requirements for Using the Bundler
- **ResourceHacker** (optional — needed only for setting custom icons)  
  Users must install it manually.

---

## ▶️ How to Run KozakScript Programs

### **Option 1 — Run with the Interpreter**
Use the provided interpreter to run any `.kozak` file:

KozakScriptInterpreter.exe path\to\file.kozak

Make sure the file has the `.kozak` extension.

### **Option 2 — Bundle into a Standalone Executable**
Use the built-in bundler to package your `.kozak` program into a standalone Windows `.exe`.

1. Place your `.kozak` file in the project folder.
2. Run the **Bundler** tool.
3. (Optional) If you want a custom icon, place `ResourceHacker.exe` in the bundler directory.

The resulting `.exe` is fully portable and does *not* require Python.

---

## 🧪 Example Code

Example code:

Hello World (Ukrainian Syntax):

```kozak
Hetman
Spivaty("Hello World!);
```
Hello World (English Syntax):

```kozak
Chief
Print("Hello World!);
```

Hello World (Russian Syntax):

```kozak
Ataman
Pechatat("Hello World!);
```

Hello World (Symbolic Syntax):

```kozak
>>>
!("Hello World!);
```

Check the `Examples` folder and `test.kozak`, `test_EN.kozak`, `test_RU.kozak`, `test_Sym.kozak` files for more syntax demonstrations for all dialects.

---

# 📦 Bundling

KozakScript includes a native C++ bundler that allows you to turn any `.kozak` file into a standalone Windows `.exe` application.

Python is **not required** for the bundled executable.

### 🔨 Basic Usage

```bash
kozak_bundler.exe my_program.kozak
```
### 🎨 Custom Icon

```bash
kozak_bundler.exe my_program.kozak --icon icon.ico
```

NOTE: You need to have RessourceHacker installed and in the same directory as the bundling files.

If ResourceHacker.exe is not found, the bundler will:

- show a help message explaining what to install

- ask if you want to continue without applying the icon. If you enter 'y' it will bundle with default icon, if you enter 'n' the bundling will stop.

### 📁 Adding Data

Format:
```bash
kozak_bundler.exe my_program --add-data source_path;destination_name
```
Example:
```bash
kozak_bundler.exe game.kozak --add-data config.json;config.json
```

You can supply multiple --add-data entries:
```bash
kozak_bundler.exe game.kozak --add-data config.json;config.json --add-data assets/sprite.png;sprite.png --add-data sounds/hit.wav;hit.wav
```

📌 Full Example Command
```bash
kozak_bundler.exe program.kozak --icon logo.ico --add-data settings.cfg;settings.cfg --add-data levels.dat;levels.dat
```
This will:

1. copy the interpreter

2. embed your .kozak script

3. embed assets and linked modules

4. embed additional data files

5. apply the custom icon (if ResourceHacker is installed)

6. produce a final .exe in the build_exe folder
---

## 🐛 Reporting Bugs

If you encounter any issues, please report them via **GitHub Issues** so they can be fixed in future updates. If you have any ideas on how can the language be improved (more functionality, more dialects, etc.), state it via **GitHub Issues** so that I can know and add if it is possible. Happy Coding, Kozache :)
