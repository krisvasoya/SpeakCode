# SpeakCode Programming Language - User Manual & Installation Guide

Welcome to **SpeakCode**! This manual introduces the language syntax, installation procedures, run commands, and tutorials for beginners.

---

## 1. Quick Installation & Setup Guide

### 1.1 Requirements
- **Operating System:** Windows, macOS, or Linux.
- **Python Runtime:** Python 3.10, 3.11, or 3.12 (highly recommended). No external libraries are needed.

### 1.2 Installation Steps
1. Download the repository source files to your workspace directory:
   ```bash
   c:\Users\krish vasoya\OneDrive\Desktop\sem 7\CD\miniproject
   ```
2. Open a command terminal (Command Prompt, PowerShell, or bash) and verify your Python version:
   ```bash
   python --version
   ```

### 1.3 Running Example Code
Execute an example program from the root workspace using the `run` command:
```bash
python speakcode.py run examples/hello_world.speak
```

### 1.4 Running the Test Suite
Ensure everything is working correctly by executing the test suites:
- Run integration tests:
  ```bash
  python test_runner.py
  ```
- Run unit test suites:
  ```bash
  python -m unittest discover -s tests
  ```

---

## 2. CLI Command Tool Reference

All compiler tasks are coordinated using `speakcode.py`:

| Command | Usage | Description |
|---|---|---|
| **`run`** | `python speakcode.py run <file>` | Semantic validates and interprets a source file. |
| **`tokens`** | `python speakcode.py tokens <file>` | Prints the scanned token table showing lines/columns. |
| **`ast`** | `python speakcode.py ast <file>` | Draws an ASCII tree structure of the parsing hierarchy. |
| **`semantic`** | `python speakcode.py semantic <file>` | Statically verifies variable scopes and expressions. |
| **`explain`** | `python speakcode.py explain <file>` | Translates source lines into plain English steps. |
| **`format`** | `python speakcode.py format <file>` | Casing correction and standard 4-space auto-indentation. |
| **`repl`** | `python speakcode.py repl` | Starts the interactive checked multiline console shell. |
| **`version`** | `python speakcode.py version` | Displays versions and platform descriptions. |

---

## 3. Programming in SpeakCode - Syntax Tutorial

SpeakCode is designed to look like writing simple English instructions. Follow these rules:

1. **Sentences end with a period (`.`)**: Every standalone instruction must end with a dot.
2. **Capitalization**: The first keyword of every statement is capitalized.

### 3.1 Variables
Variables must be declared before they are modified or accessed.
- **Declaration (`Remember`)**:
  ```speakcode
  Remember 10 as score.
  Remember "Krish" as player.
  ```
- **Assignment (`Change`)**:
  ```speakcode
  Change score to score plus 5.
  ```

### 3.2 Operators & Calculations
SpeakCode replaces symbols with written operators:
- **Arithmetic:** `plus`, `minus`, `times`, `divided by`, `modulo`
- **Comparisons:** `is same as` (`==`), `is different from` (`!=`), `is above` (`>`), `is below` (`<`), `is at least` (`>=`), `is at most` (`<=`)
- **Logical:** `and`, `or`, `opposite of` (`!`)

Example:
```speakcode
Remember (10 times 2) plus 5 as total.
```

### 3.3 Printing and Console Input
- **Console Output (`Speak`)**:
  ```speakcode
  Speak "Current Score: " plus score.
  ```
- **Console Input (`Ask`)**:
  ```speakcode
  Ask "Enter your name: " and save as user_name.
  Speak "Hello, " plus user_name.
  ```

### 3.4 Conditionals (`If-Otherwise`)
Decision blocks start with `If` and close with `Finish checking.`.
```speakcode
If score is above 100 then
    Speak "You won!".
Otherwise if score is same as 100 then
    Speak "Perfect Score!".
Otherwise
    Speak "Try again!".
Finish checking.
```

### 3.5 Loops (`While` and `Repeat`)
SpeakCode supports conditional loops and counted loops. Both end with `Finish looping.`.
- **`While` Loop:**
  ```speakcode
  Remember 1 as count.
  While count is at most 5 repeat
      Speak count.
      Change count to count plus 1.
  Finish looping.
  ```
- **`Repeat` Loop:**
  ```speakcode
  Repeat 3 times
      Speak "Hello!".
  Finish looping.
  ```

### 3.6 Custom Functions (`To perform`)
Declare reusable procedures using `To perform` blocks and exit with `Finish performance.`. Return values using `Give back`.
```speakcode
To perform add_one with val:
    Give back val plus 1.
Finish performance.

Remember 10 as starting_point.
Perform add_one with starting_point and save as next_point.
Speak next_point. # Outputs 11
```

---

## 4. Troubleshooting Guide

### 4.1 Missing Periods
- **Error:** `SPK102 (Syntax Error)`
- **Problem:** Forgetting the trailing `.` at the end of a statement.
- **Fix:** Append a period. E.g., change `Speak x` to `Speak x.`.

### 4.2 Capitalization Check
- **Error:** `SPK102 (Syntax Error) - Expected statement starter`
- **Problem:** Using lowercase keyword sentence openers (e.g., `remember 5 as x.`).
- **Fix:** Run the code formatter or capitalize the opener: `Remember 5 as x.`.

### 4.3 Type Mismatch
- **Error:** `SPK108 (Type Error) - Operator requires numeric operands`
- **Problem:** Attempting math calculations using strings and numbers (e.g., `"hello" minus 5.`).
- **Fix:** Keep calculations aligned to consistent types (addition `plus` allows string concatenation, but `minus`, `times`, and comparisons require compatible types).
