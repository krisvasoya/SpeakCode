"""
SpeakCode Compiler - Shared Constants and Diagnostic Identifiers
Centralizes error codes and diagnostic categorizations for uniform error handling.
"""

from typing import Final

# Diagnostic error identifiers
ERR_LEXICAL: Final[str] = "SPK101"
ERR_SYNTAX: Final[str] = "SPK102"
ERR_SEM_DUPLICATE_DECL: Final[str] = "SPK103"
ERR_SEM_UNDEFINED_VAR: Final[str] = "SPK104"
ERR_RUN_MATH_BOUNDS: Final[str] = "SPK105"
ERR_SEM_FUNCTION_MISMATCH: Final[str] = "SPK106"
ERR_SEM_RETURN_OUTSIDE_FUN: Final[str] = "SPK107"
ERR_TYPE_MISMATCH: Final[str] = "SPK108"
ERR_INTERNAL_CRASH: Final[str] = "SPK999"

# Human-readable mapping of error categories
ERROR_CATEGORY_NAMES = {
    ERR_LEXICAL: "Lexical Error",
    ERR_SYNTAX: "Syntax Error",
    ERR_SEM_DUPLICATE_DECL: "Semantic Error (Duplicate Symbol)",
    ERR_SEM_UNDEFINED_VAR: "Semantic Error (Undefined Variable)",
    ERR_RUN_MATH_BOUNDS: "Runtime Arithmetic Boundary Error",
    ERR_SEM_FUNCTION_MISMATCH: "Semantic Error (Function Mismatch)",
    ERR_SEM_RETURN_OUTSIDE_FUN: "Semantic Error (Invalid Control flow)",
    ERR_TYPE_MISMATCH: "Type Evaluation Error",
    ERR_INTERNAL_CRASH: "Internal Compiler Error"
}
