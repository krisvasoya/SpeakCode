# Contributing to SpeakCode

Thank you for your interest in contributing to SpeakCode! To maintain a clean and reliable compiler codebase, please adhere to the following guidelines.

---

## 1. Code Style and Standards
- **Python Version:** Python 3.10+ compatible.
- **Style Enforcements:** Follow PEP 8 guidelines.
- **Type Hints:** Enforce type hints on all function parameters and return types.
- **Documentation:** All public classes and methods must include docstrings outlining purpose, arguments, return values, and exceptions.

---

## 2. Extending the Language
When adding features (like a new loop keyword or data structure), you must update the components in order:
1. **Lexer:** `speak_tokens.py` and `speak_lexer.py`.
2. **AST:** `speak_ast.py`.
3. **Parser:** `speak_parser.py`.
4. **Semantic checks:** `speak_semantic.py`.
5. **Interpreter:** `speak_interpreter.py`.
6. **Documentation & Tools:** `speak_formatter.py` and `speak_explainer.py`.

---

## 3. Pull Request (PR) Lifecycle
1. **Fork the Repository:** Create a feature branch off of the `main` branch.
2. **Implement and Document:** Write clear commits describing the changes.
3. **Write Unit Tests:** Add unit tests to verify the changes inside the `tests/` directory.
4. **Verify Test Suites:** Ensure both the integration runner and unit test discover pass:
   ```bash
   python test_runner.py
   python -m unittest discover -s tests
   ```
5. **Format Your Source:** Format python files using your editor's auto-formatter (e.g. `black` or `autopep8`).
6. **Open PR:** Submit the PR detailing what the change does and verifying that all tests pass.
