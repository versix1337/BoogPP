# Boogpp Programming Language

**A Windows-centric systems programming language combining Python-like syntax with C++ performance.**

Boogpp is designed specifically for Windows system customization, with deep OS integration, built-in safety mechanisms, and automatic resilience features.

---

## 🚀 Quick Links

- **[Language Documentation](boogpp/README.md)** - Complete language guide and features
- **[Language Specification](boogpp/docs/LANGUAGE_SPEC.md)** - Detailed language spec
- **[Branch Organization](BRANCHES.md)** - Development workflow and branch structure
- **[Example Programs](boogpp/examples/)** - Working code examples

---

## 📋 Project Structure

```
BoogPP/
├── boogpp/                    # Main compiler and language implementation
│   ├── compiler/              # Compiler components
│   │   ├── lexer/            # Lexical analyzer
│   │   ├── parser/           # Parser and AST
│   │   ├── typechecker/      # Type system and checker
│   │   ├── safety/           # Safety enforcement
│   │   └── codegen/          # LLVM code generation
│   ├── examples/             # Example .bpp programs
│   ├── docs/                 # Documentation
│   ├── stdlib/               # Standard library
│   └── tests/                # Test suite
├── BRANCHES.md               # Branch organization guide
└── README.md                 # This file
```

---

## 🎯 Key Features

- **Python-like Syntax** - Clean, readable, whitespace-based syntax
- **C++ Performance** - Compiles to native machine code via LLVM
- **Safety by Default** - Built-in safety checks with SAFE/UNSAFE/CUSTOM modes
- **Windows-Centric** - Deep OS integration with minimal boilerplate
- **Built-in Resilience** - `try_chain` for automatic failover and retry logic

---

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/versix1337/BoogPP.git
cd BoogPP

# Install dependencies
pip install -r boogpp/requirements.txt

# Install compiler
pip install -e boogpp/
```

---

## 💻 Usage

```bash
# Compile a Boogpp program
boogpp build main.bpp -o output.exe

# Check syntax and safety
boogpp check main.bpp

# Show version
boogpp version
```

---

## 📝 Example

```boogpp
@safety_level(mode: SAFE)
module hello_world

import std.io

func main() -> i32:
    std.io.println("Hello from Boogpp!")
    return SUCCESS
```

---

## 🌳 Development Branches

This project uses an organized branching strategy:

- **`main`** - Latest stable release
- **`dev`** - Active development
- **`phase-1-foundation`** - Core foundation (Lexer, Parser, Safety)
- **`phase-2-advanced`** - Type system and code generation
- **Future phases** - Runtime, Windows API, Optimization, Tooling

See [BRANCHES.md](BRANCHES.md) for complete branch documentation.

---

## 📊 Current Status

**Version:** 2.0.0

**Implemented:**
- ✅ Lexer/Tokenizer
- ✅ Parser and AST
- ✅ Type Checker
- ✅ Safety System (Enhanced)
- ✅ LLVM Code Generator
- ✅ CLI Interface
- ✅ Example Programs

**In Progress:**
- 🚧 Runtime Library
- 🚧 Windows API Bindings
- 🚧 Standard Library

**Planned:**
- 📋 Debugger Integration
- 📋 IDE Support
- 📋 Package Manager

---

## 🤝 Contributing

Contributions are welcome! Please follow our branching strategy:

1. Fork the repository
2. Create a feature branch from `dev`
3. Make your changes
4. Submit a pull request to `dev`

See [BRANCHES.md](BRANCHES.md) for detailed workflow guidelines.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Issues**: https://github.com/versix1337/BoogPP/issues
- **Discussions**: https://github.com/versix1337/BoogPP/discussions

---

**Boogpp** - Write Windows system tools with Python-like simplicity and C++ performance.
