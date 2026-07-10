"""
SpeakCode Compiler - Diagnostic Error Handling Module
Provides customized position-tracked exception types and visual diagnostics formatting.

Dependencies:
    - speak_tokens.py (Position)
    - constants.py (ERROR_CATEGORY_NAMES)
"""

from typing import Optional
from speak_tokens import Position
from constants import ERROR_CATEGORY_NAMES


def format_error(
    error_code: str,
    message: str,
    position: Position,
    source: str,
    suggestion: Optional[str] = None
) -> str:
    """
    Formulates a detailed diagnostic error report with code details and visual pointers.

    Args:
        error_code: Standard SpeakCode error code (e.g. SPK101, SPK102).
        message: Descriptive error reason.
        position: Position tracker object containing source coordinates.
        source: Full source string for extracting the context line.
        suggestion: Advice for correcting the issue.

    Returns:
        Formatted error visualization blocks.
    """
    error_type = ERROR_CATEGORY_NAMES.get(error_code, "Compiler Error")
    
    header = f"SpeakCode Compiler Error ({error_code}): {error_type}\n"
    meta = f"File   : {position.filename}\nLine   : {position.line}\nColumn : {position.column}\n\n"
    
    context = ""
    if source and position:
        lines = source.splitlines()
        line = position.line
        column = position.column
        
        # Guard: Line numbers within file bounds
        if 1 <= line <= len(lines):
            error_line = lines[line - 1]
            display_line = error_line.replace('\t', '    ')
            
            # Guard: Column bounds checking
            if 1 <= column <= len(error_line) + 1:
                offset = column - 1
                prefix = error_line[:offset]
                display_offset = len(prefix.replace('\t', '    '))
                pointer = ' ' * display_offset + '^'
            else:
                pointer = '^'
                
            context = f"    {display_line}\n    {pointer}\n"
            
    suggestion_str = ""
    if message:
        suggestion_str += f"Message   : {message}\n"
    if suggestion:
        suggestion_str += f"Suggestion: {suggestion}\n"
        
    return header + meta + context + suggestion_str


class SpeakError(Exception):
    """Base class for all SpeakCode diagnostic exceptions."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        position: Position,
        source: str,
        suggestion: Optional[str] = None
    ) -> None:
        self.error_code = error_code
        self.message = message
        self.position = position
        self.source = source
        self.suggestion = suggestion
        super().__init__(self.message)


class SpeakLexerError(SpeakError):
    """Lexical scanning exceptions (SPK101)."""
    
    def __init__(
        self,
        message: str,
        position: Position,
        source: str,
        suggestion: Optional[str] = None
    ) -> None:
        super().__init__("SPK101", message, position, source, suggestion)

    def __str__(self) -> str:
        return format_error(
            self.error_code,
            self.message,
            self.position,
            self.source,
            self.suggestion
        )


class SpeakSyntaxError(SpeakError):
    """Grammar parser syntactic exceptions (SPK102)."""
    
    def __init__(
        self,
        message: str,
        position: Position,
        source: str,
        suggestion: Optional[str] = None
    ) -> None:
        super().__init__("SPK102", message, position, source, suggestion)

    def __str__(self) -> str:
        return format_error(
            self.error_code,
            self.message,
            self.position,
            self.source,
            self.suggestion
        )


class SpeakSemanticError(SpeakError):
    """Static semantics check violations (SPK103, SPK104, SPK106, SPK107, SPK108)."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        position: Position,
        source: str,
        suggestion: Optional[str] = None
    ) -> None:
        super().__init__(error_code, message, position, source, suggestion)

    def __str__(self) -> str:
        return format_error(
            self.error_code,
            self.message,
            self.position,
            self.source,
            self.suggestion
        )


class SpeakRuntimeError(SpeakError):
    """Interpreter evaluation exceptions (e.g. division by zero bounds - SPK105)."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        position: Position,
        source: str,
        suggestion: Optional[str] = None
    ) -> None:
        super().__init__(error_code, message, position, source, suggestion)

    def __str__(self) -> str:
        return format_error(
            self.error_code,
            self.message,
            self.position,
            self.source,
            self.suggestion
        )


class SpeakTypeError(SpeakRuntimeError):
    """Semantic or evaluation type mismatch errors (SPK108)."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        position: Position,
        source: str,
        suggestion: Optional[str] = None
    ) -> None:
        super().__init__(error_code, message, position, source, suggestion)

    def __str__(self) -> str:
        return format_error(
            self.error_code,
            self.message,
            self.position,
            self.source,
            self.suggestion
        )
