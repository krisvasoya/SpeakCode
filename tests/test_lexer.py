"""
Unit tests for the Lexical Analyzer module (speak_lexer.py).
"""

import unittest
from speak_lexer import SpeakLexer, get_token_statistics
from speak_tokens import TokenType, Position
from speak_errors import SpeakLexerError


class TestSpeakLexer(unittest.TestCase):
    
    def test_basic_tokens(self) -> None:
        """Verify standard variable declarations, strings, numbers, and statement ends."""
        source = 'Remember 3.14 as pi.'
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[0].type, TokenType.REMEMBER)
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].value, "3.14")
        self.assertEqual(tokens[2].type, TokenType.AS)
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].value, "pi")
        self.assertEqual(tokens[4].type, TokenType.PERIOD)
        self.assertEqual(tokens[5].type, TokenType.EOF)

    def test_comments_skipping(self) -> None:
        """Verify that comments starting with '#' and 'note' are skipped correctly."""
        source = (
            "# This is a hash comment\n"
            "Remember 10 as x.\n"
            "note: This is a note comment\n"
            "note This is another note comment\n"
            "Speak x."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        types = [t.type for t in tokens]
        self.assertIn(TokenType.REMEMBER, types)
        self.assertIn(TokenType.SPEAK, types)
        self.assertNotIn(TokenType.IDENTIFIER, [t.type for t in tokens if t.value.lower() == "note"])

    def test_multi_word_tokens(self) -> None:
        """Verify that multi-word keywords are matched as single composite tokens."""
        source = "To perform calculate with x and y: Finish performance."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        types = [t.type for t in tokens]
        self.assertEqual(types[0], TokenType.TO_PERFORM)
        self.assertEqual(types[1], TokenType.IDENTIFIER)
        self.assertEqual(types[2], TokenType.WITH)
        self.assertEqual(types[3], TokenType.IDENTIFIER)
        self.assertEqual(types[4], TokenType.AND)
        self.assertEqual(types[5], TokenType.IDENTIFIER)
        self.assertEqual(types[6], TokenType.COLON)
        self.assertEqual(types[7], TokenType.FINISH_PERFORMANCE)
        self.assertEqual(types[8], TokenType.PERIOD)
        self.assertEqual(types[9], TokenType.EOF)

    def test_line_column_tracking(self) -> None:
        """Verify line and column coordinates track correctly across newlines."""
        source = "Speak 5.\n  Speak 10."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        # First Speak: Line 1, Col 1
        self.assertEqual(tokens[0].position.line, 1)
        self.assertEqual(tokens[0].position.column, 1)
        
        # Second Speak: Line 2, Col 3
        self.assertEqual(tokens[3].position.line, 2)
        self.assertEqual(tokens[3].position.column, 3)

    def test_lexer_unexpected_character_error(self) -> None:
        """Verify that invalid character inputs raise SpeakLexerError (SPK101)."""
        source = "Remember 10 as x @."
        lexer = SpeakLexer(source, "<test>")
        
        with self.assertRaises(SpeakLexerError) as context:
            lexer.tokenize()
            
        self.assertEqual(context.exception.error_code, "SPK101")
        self.assertIn("Unexpected character '@'", str(context.exception))
        self.assertEqual(context.exception.position.line, 1)
        self.assertEqual(context.exception.position.column, 18)

    def test_lexer_unterminated_string_error(self) -> None:
        """Verify that unterminated double quote strings throw an SPK101 error."""
        source = 'Remember "hello as text.'
        lexer = SpeakLexer(source, "<test>")
        
        with self.assertRaises(SpeakLexerError) as context:
            lexer.tokenize()
            
        self.assertEqual(context.exception.error_code, "SPK101")
        self.assertIn("Unterminated string literal", str(context.exception))
        self.assertEqual(context.exception.position.line, 1)
        self.assertEqual(context.exception.position.column, 10)

    # ----------------------------------------------------------------------
    # NEW REFINED SCENARIOS
    # ----------------------------------------------------------------------
    def test_unicode_identifiers_and_literals(self) -> None:
        """Verify scanner supports Unicode identifiers and literal text."""
        source = 'Remember "🚀" as rocket_🚀.'
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].value, "🚀")
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].value, "rocket_🚀")

    def test_escape_sequences_in_string(self) -> None:
        """Verify backslash escape mapping (\\n, \\t, \\", \\\\) works inside strings."""
        source = 'Remember "line1\\nline2\\ttab\\\"quote\\\\slash" as text.'
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].value, 'line1\nline2\ttab"quote\\slash')

    def test_malformed_number_boundary_error(self) -> None:
        """Verify that direct identifier characters after numbers raise boundary validation errors."""
        source = "Remember 10abc as x."
        lexer = SpeakLexer(source, "<test>")
        
        with self.assertRaises(SpeakLexerError) as context:
            lexer.tokenize()
            
        self.assertEqual(context.exception.error_code, "SPK101")
        self.assertIn("Invalid numeric literal boundary", str(context.exception))
        self.assertEqual(context.exception.position.line, 1)
        self.assertEqual(context.exception.position.column, 10)  # boundary failure index

    def test_token_statistics_counting(self) -> None:
        """Verify token frequency collection returns correct counts."""
        source = "Remember 10 as x. Change x to 20."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        stats = get_token_statistics(tokens)
        self.assertEqual(stats[TokenType.REMEMBER], 1)
        self.assertEqual(stats[TokenType.CHANGE], 1)
        self.assertEqual(stats[TokenType.IDENTIFIER], 2)  # x, x
        self.assertEqual(stats[TokenType.NUMBER], 2)      # 10, 20


if __name__ == '__main__':
    unittest.main()
