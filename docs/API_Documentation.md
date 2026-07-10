# SpeakCode Compiler - Complete API Reference Manual

This document provides detailed API specifications, classes, methods, signatures, parameters, exceptions, and usage examples for every module of the SpeakCode compiler.

---

## 1. `compiler_info.py`
Provides global compiler metadata configuration constants.

- **Purpose:** Configuration manager.
- **Classes:** None
- **Global Variables:**
  - `LANGUAGE_NAME` (`"SpeakCode"`): Compiler name.
  - `COMPILER_VERSION` (`"1.0.0"`): Code release level.
  - `AUTHOR` (`"Krish Vasoya"`): Main designer.
  - `DEPARTMENT` (`"B.Tech CSD"`): Academic division.
  - `PROJECT_YEAR` (`2026`): Compilation build year.
  - `FILE_EXTENSION` (`".speak"`): File suffix.
  - `SOURCE_ENCODING` (`"utf-8"`): Stream reader encoding.
  - `DEFAULT_INDENTATION` (`"    "`): Target spaces indent level.
- **Usage Example:**
  ```python
  from compiler_info import LANGUAGE_NAME, COMPILER_VERSION
  print(f"Welcome to {LANGUAGE_NAME} v{COMPILER_VERSION}")
  ```

---

## 2. `constants.py`
Defines diagnostic validation error code identifiers.

- **Purpose:** Centralize diagnostic classification codes.
- **Classes:** None
- **Constants:**
  - `ERR_LEXICAL` (`"SPK101"`): Lexical scanner failure code.
  - `ERR_SYNTAX` (`"SPK102"`): Grammar parser violation code.
  - `ERR_SEM_DUPLICATE_DECL` (`"SPK103"`): Re-declaration check code.
  - `ERR_SEM_UNDEFINED_VAR` (`"SPK104"`): Variable definition verify code.
  - `ERR_RUN_MATH_BOUNDS` (`"SPK105"`): Division by zero check code.
  - `ERR_SEM_FUNCTION_MISMATCH` (`"SPK106"`): Call argument/signature size count check.
  - `ERR_SEM_RETURN_OUTSIDE_FUN` (`"SPK107"`): Scope checking for return placements.
  - `ERR_TYPE_MISMATCH` (`"SPK108"`): Static expression type check code.
  - `ERR_INTERNAL_CRASH` (`"SPK999"`): Uncaught system error code.
  - `ERROR_CATEGORY_NAMES` (dict): Maps codes to category headers.

---

## 3. `speak_tokens.py`
Declares the lexical structures and positions trackers.

- **Purpose:** Token structure models.
- **Classes:**
  - `Position`:
    - **Attributes:** `filename: str`, `line: int`, `column: int`.
    - **Methods:** `__str__()` -> returns `"filename:line:column"`.
  - `TokenType` (Enum): Holds 37 distinct keywords, literals, and symbol types.
  - `Token`:
    - **Attributes:** `type: TokenType`, `value: str`, `position: Position`.
    - **Methods:** `__repr__()` -> formats visual representation.
- **Usage Example:**
  ```python
  from speak_tokens import Token, TokenType, Position
  pos = Position("main.speak", 1, 5)
  tok = Token(TokenType.NUMBER, "10", pos)
  ```

---

## 4. `speak_errors.py`
System exceptions containing diagnostic details.

- **Purpose:** Standardize visual error formats with pointer carats.
- **Functions:**
  - `format_error(category, message, position, source, suggestion)`:
    - **Parameters:** `category: str`, `message: str`, `position: Position`, `source: str`, `suggestion: str`.
    - **Return Value:** `str` (formatted caret diagnostic string).
- **Exceptions Hierarchy:**
  - `SpeakError(Exception)`: Base compiler exception.
  - `SpeakLexerError(SpeakError)`: Scanner boundary issues (`SPK101`).
  - `SpeakSyntaxError(SpeakError)`: Grammatical issues (`SPK102`).
  - `SpeakSemanticError(SpeakError)`: Scope violations (`SPK103`, `SPK104`, `SPK106`, `SPK107`).
  - `SpeakRuntimeError(SpeakError)`: Arithmetic issues (`SPK105`).
  - `SpeakTypeError(SpeakSemanticError)`: Incompatible operations (`SPK108`).

---

## 5. `speak_ast.py`
Specifies structural program representations (nodes).

- **Purpose:** AST node dataclass tree node definitions.
- **Classes:**
  - `ASTNode` (Abstract): Interface outlining `accept`, `stringify`, `pretty_print`, and `to_dict`.
  - `StatementNode(ASTNode)` & `ExpressionNode(ASTNode)`: Categorization abstract base nodes.
  - **Concrete Nodes:** `ProgramNode`, `RememberNode`, `ChangeNode`, `SpeakNode`, `AskNode`, `OtherwiseIfNode`, `OtherwiseNode`, `IfNode`, `WhileNode`, `RepeatNode`, `FunctionDeclarationNode`, `FunctionCallNode`, `ReturnNode`, `BinaryExpressionNode`, `UnaryExpressionNode`, `LiteralNode`, `IdentifierNode`, `GroupingNode`.

---

## 6. `speak_lexer.py`
Module scan driver converting strings to token streams.

- **Purpose:** Scan and map characters to tokens.
- **Classes:**
  - `SpeakLexer`:
    - **Methods:**
      - `__init__(source, filename, debug)`
      - `tokenize() -> List[Token]`: Converts raw source string into a list of Tokens.
- **Usage Example:**
  ```python
  from speak_lexer import SpeakLexer
  lexer = SpeakLexer("Remember 10 as x.", "test.speak")
  tokens = lexer.tokenize()
  ```

---

## 7. `speak_parser.py`
Syntactic parser constructing ASTs with recovery.

- **Purpose:** Build AST trees and capture grammar errors.
- **Classes:**
  - `SpeakParser`:
    - **Methods:**
      - `__init__(tokens, source, filename, debug)`
      - `parse() -> ProgramNode`: Traverses token list. Collects errors in `self.errors`.
- **Usage Example:**
  ```python
  from speak_lexer import SpeakLexer
  from speak_parser import SpeakParser
  lexer = SpeakLexer("Remember 10 as x.", "test.speak")
  parser = SpeakParser(lexer.tokenize(), lexer.source, "test.speak")
  program = parser.parse()
  ```

---

## 8. `speak_semantic.py`
Static code analysis validating declarations, scoping, and type verification.

- **Purpose:** Static compiler pass checking program validity.
- **Classes:**
  - `FunctionSignature`: Holds function symbol data.
  - `Scope`: Scoping frames.
  - `SpeakSemanticAnalyzer`:
    - **Methods:**
      - `__init__(source, filename)`
      - `analyze(node: ASTNode) -> None`: Validates variable scope declarations, hoists function names, checks argument counts, and tracks types.
- **Usage Example:**
  ```python
  from speak_semantic import SpeakSemanticAnalyzer
  analyzer = SpeakSemanticAnalyzer(source_code)
  analyzer.analyze(program_ast)
  if analyzer.errors:
      print("Semantic analysis failed!")
  ```

---

## 9. `speak_interpreter.py`
Execution walker executing checked statements.

- **Purpose:** Execute verified program steps.
- **Classes:**
  - `Environment`: Stores live bindings with dynamic parent scope links.
  - `SpeakInterpreter`:
    - **Methods:**
      - `__init__(source, filename, debug, trace)`
      - `interpret(node: ASTNode) -> None`: Iterates over statements to update runtime values.
- **Usage Example:**
  ```python
  from speak_interpreter import SpeakInterpreter
  interpreter = SpeakInterpreter(source_code)
  interpreter.interpret(program_ast)
  ```

---

## 10. `speak_explainer.py`
Converts SpeakCode AST trees into user-friendly English documentation logs.

- **Purpose:** Explains AST node statements in clear English.
- **Classes:**
  - `SpeakExplainer`:
    - **Methods:**
      - `explain(node: ASTNode) -> List[str]`: Generates list of sentences explaining the code.
- **Usage Example:**
  ```python
  from speak_explainer import SpeakExplainer
  explainer = SpeakExplainer()
  explanations = explainer.explain(program_ast)
  for sentence in explanations:
      print(sentence)
  ```

---

## 11. `speak_formatter.py`
Whitespace formatting utility.

- **Purpose:** Apply visual standardization (casing and 4-space indents).
- **Functions:**
  - `format_code(source: str) -> str`: Normalizes indents and fixes keyword casings.
- **Usage Example:**
  ```python
  from speak_formatter import format_code
  formatted = format_code("remember  10  as  x.  ")
  print(formatted) # "Remember 10 as x.\n"
  ```

---

## 12. `speakcode.py`
Unified coordinator running CLI commands and multiline REPL.

- **Purpose:** Entry console manager.
- **Functions:**
  - `run_repl() -> None`: Starts interactive loop tracking block indentation depths.
  - `main() -> None`: Parses arguments (run, tokens, ast, format, repl, etc.) and runs the pipeline.
