"""
Unit tests for the Error Handling module (speak_errors.py).
"""

import unittest
from speak_tokens import Position
from speak_errors import (
    format_error,
    SpeakError,
    SpeakLexerError,
    SpeakSyntaxError,
    SpeakTypeError
)


class TestErrorSystem(unittest.TestCase):
    
    def test_format_error_unicode(self) -> None:
        """Verify error formatting supports UTF-8 Unicode source content."""
        source = "Remember \"🚀\" as rocket_🚀."
        pos = Position("rocket.speak", 1, 23)
        
        formatted = format_error(
            error_code="SPK102",
            message="Unmatched rocket symbol",
            position=pos,
            source=source,
            suggestion="Verify rocket symbols."
        )
        
        self.assertIn("rocket_🚀", formatted)
        self.assertIn("Message   : Unmatched rocket symbol", formatted)
        self.assertIn("Suggestion: Verify rocket symbols.", formatted)

    def test_format_error_out_of_bounds_line(self) -> None:
        """Verify compiler doesn't crash when formatting errors with invalid line index bounds."""
        source = "Single line of source."
        pos = Position("bounds.speak", 999, 1)  # Invalid line index
        
        formatted = format_error(
            error_code="SPK101",
            message="Line index out of bounds check",
            position=pos,
            source=source,
            suggestion=None
        )
        
        # Verify it still renders meta details without printing code pointer crash
        self.assertIn("SpeakCode Compiler Error (SPK101)", formatted)
        self.assertIn("Line   : 999", formatted)
        self.assertIn("Message   : Line index out of bounds check", formatted)
        self.assertNotIn("Single line of source", formatted)

    def test_format_error_out_of_bounds_column(self) -> None:
        """Verify compiler doesn't crash when formatting errors with invalid column bounds."""
        source = "Short line."
        pos = Position("bounds.speak", 1, 999)  # Column out of line length
        
        formatted = format_error(
            error_code="SPK101",
            message="Column index out of bounds check",
            position=pos,
            source=source,
            suggestion=None
        )
        
        self.assertIn("Short line.", formatted)
        self.assertIn("^", formatted)  # fallback caret pointer
        self.assertIn("Message   : Column index out of bounds check", formatted)

    def test_format_error_empty_source(self) -> None:
        """Verify formatter behavior when source code string is empty."""
        pos = Position("empty.speak", 1, 1)
        formatted = format_error(
            error_code="SPK102",
            message="Parsing empty file",
            position=pos,
            source="",
            suggestion="Write code."
        )
        
        self.assertIn("File   : empty.speak", formatted)
        self.assertIn("Message   : Parsing empty file", formatted)

    def test_class_hierarchy_and_properties(self) -> None:
        """Verify standard inheritance and property bindings of error classes."""
        pos = Position("hierarchy.speak", 12, 4)
        source = "Change x to 5."
        
        err = SpeakLexerError(
            message="Scanned bad terminal",
            position=pos,
            source=source,
            suggestion="Remove char"
        )
        
        self.assertIsInstance(err, SpeakError)
        self.assertEqual(err.error_code, "SPK101")
        self.assertEqual(err.position.line, 12)
        self.assertEqual(err.position.column, 4)
        self.assertIn("Message   : Scanned bad terminal", str(err))


if __name__ == '__main__':
    unittest.main()
