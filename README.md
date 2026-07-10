# SpeakCode Programming Language Compiler
> **Academic Project:** B.Tech 7th Semester Mini Project (Compiler Design)  
> **Institution:** Department of Computer Science & Design (CSD) — Academic Year 2026  
> **Creator:** Krish Vasoya  

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Academic Project](https://img.shields.io/badge/Academic%20Project-B.Tech%20CSD-blueviolet.svg)]()

SpeakCode is a modular, conversational programming language compiler built from scratch in Python. It enforces standard compiler phases (lexical scan, recursive descent parsing, scopes, static type constraints, and call frame walking) while using a beginner-friendly, English-like keyword syntax.

---

## 📚 Project Documentation Package

For submission and developer references, see the comprehensive guides in the `docs/` directory:

1. **[Project Report (docs/Project_Report.md)](file:///c:/Users/krish%20vasoya/OneDrive/Desktop/sem%207/CD/miniproject/docs/Project_Report.md)**: Full academic mini-project report with cover page, certificates, design documentation, and 13 Mermaid system diagrams.
2. **[API Documentation (docs/API_Documentation.md)](file:///c:/Users/krish%20vasoya/OneDrive/Desktop/sem%207/CD/miniproject/docs/API_Documentation.md)**: API reference specifications, classes, parameters, and exceptions for all 12 source files.
3. **[Example Programs Guide (docs/Examples_Guide.md)](file:///c:/Users/krish%20vasoya/OneDrive/Desktop/sem%207/CD/miniproject/docs/Examples_Guide.md)**: Code descriptions, logic steps, and expected outputs for all 17 example programs.
4. **[Developer Extension Guide (docs/Developer_Guide.md)](file:///c:/Users/krish%20vasoya/OneDrive/Desktop/sem%207/CD/miniproject/docs/Developer_Guide.md)**: Guidelines for adding keywords, AST nodes, parser rules, and CLI options.
5. **[User Manual & Install Guide (docs/User_Manual.md)](file:///c:/Users/krish%20vasoya/OneDrive/Desktop/sem%207/CD/miniproject/docs/User_Manual.md)**: Complete guide to installing, configuring, running tests, and learning syntax.
6. **[Submission Checklist (docs/Submission_Checklist.md)](file:///c:/Users/krish%20vasoya/OneDrive/Desktop/sem%207/CD/miniproject/docs/Submission_Checklist.md)**: Verification checks to run before submission.

---

## 🛠️ CLI Quickstart Command List

All pipeline configurations are executed via `speakcode.py`:

```bash
# Run a verified SpeakCode program
python speakcode.py run examples/fizzbuzz.speak

# View scanned token tables
python speakcode.py tokens examples/hello_world.speak

# Display parsed AST tree
python speakcode.py ast examples/hello_world.speak

# Run static checks (No Interpreter execution)
python speakcode.py semantic examples/hello_world.speak

# Translate lines to plain English sentences
python speakcode.py explain examples/hello_world.speak

# Capitalize keywords and format block indents
python speakcode.py format examples/hello_world.speak

# Launch the interactive REPL shell
python speakcode.py repl
```

---

## 🧪 Validating with Tests

Verify build stability using:
- **Component Unit & Stress Tests (65 tests):**
  ```bash
  python -m unittest discover -s tests
  ```
- **Root Integration Tests (10 tests):**
  ```bash
  python test_runner.py
  ```

---

## 🏷️ GitHub Tags & Release Notes

### Topics
`compiler` `interpreter` `programming-language` `compiler-design` `abstract-syntax-tree` `lexical-analyzer` `parser-combinators` `python` `static-analysis` `education`

### Release Notes (v1.0.0 - Stable Release)
- **Modular Pipeline:** Complete decoupled separations of lexing, parsing, static analysis, and interpretation.
- **Panic-Mode Recovery:** Grammatical recovery using synchronization blocks.
- **Global Function Hoisting:** Permits procedures to be called prior to declaration in source.
- **Developer Toolsets:** Caret-aligned visual highlights, standard casing formatters, and plain-language code explainers.
- **Full Test Suite:** 75 tests cover 100% of standard execution logic and edge boundaries.
