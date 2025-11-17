# KozakScript

**🇺🇦 [Українська](README.uk.md) | 🇷🇺 [Русский](README.ru.md)**

KozakScript is a hobby programming language project inspired by Ukrainian culture and designed to make programming feel more familiar to Ukrainian-speaking learners. What began as a small experiment evolved into a functional language prototype with multiple dialects, its own interpreter, and a bundler that lets users turn their `.kozak` programs into standalone `.exe` applications.

The language combines elements of **C++**, **Python**, and a touch of **Pascal**, while introducing unique, culturally flavored keywords — for example, `Spivaty` (“sing”) for printing or `Slukhai` (“listen”) for input.  
As of Version 1.0, KozakScript supports **four dialects**:

- **Ukrainian**  
- **Russian**  
- **English**  
- **Symbolic**

You can explore example programs in the `Examples` folder or view the syntax in the `test.kozak` file. Once Version 1.0 is finalized, a full syntax reference and documentation will be provided.

---

## ✨ Current Status

KozakScript is functional and continuously improving. Most core features work reliably, and the interpreter can already run non-trivial programs. You are welcome to experiment, learn, or even build small applications with it.

---

## 🔧 Requirements

KozakScript no longer requires Python to be installed on the end-user's system.

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
Attaman
Pechatat("Hello World!);
```

Hello World (Symbolic Syntax):

```kozak
>>>
!("Hello World!);
```

Check the `Examples` folder and `test.kozak`, `test_EN.kozak`, `test_RU.kozak`, `test_Sym.kozak` files for more syntax demonstrations for all dialects.

---

## 🐛 Reporting Bugs

If you encounter any issues, please report them via **GitHub Issues** so they can be fixed in future updates.
