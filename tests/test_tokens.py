"""
Unit tests for the Tokenization and Positioning system (speak_tokens.py).
"""

import unittest
from dataclasses import FrozenInstanceError
from speak_tokens import TokenType, Position, Token


class TestTokenSystem(unittest.TestCase):
    
    def test_position_tracking(self) -> None:
        """Verify Position attributes, string layouts, and unicode paths."""
        pos = Position("🌟_file.speak", 152, 9)
        self.assertEqual(pos.filename, "🌟_file.speak")
        self.assertEqual(pos.line, 152)
        self.assertEqual(pos.column, 9)
        self.assertIn("🌟_file.speak", str(pos))
        self.assertIn("line 152", str(pos))

    def test_token_immutability(self) -> None:
        """Verify Position and Token classes are frozen/immutable (FrozenInstanceError)."""
        pos = Position("immutability.speak", 1, 1)
        tok = Token(TokenType.REMEMBER, "Remember", pos)
        
        # Expect failures on reassignment
        with self.assertRaises(FrozenInstanceError):
            pos.line = 2  # type: ignore
            
        with self.assertRaises(FrozenInstanceError):
            tok.value = "Change"  # type: ignore

    def test_token_representations(self) -> None:
        """Verify Token representation formatting maps coordinates correctly."""
        pos = Position("test.speak", 3, 5)
        tok = Token(TokenType.NUMBER, "3.14", pos)
        
        # Verify str format
        self.assertIn("Token[NUMBER]", str(tok))
        self.assertIn("3.14", str(tok))
        self.assertIn("line 3, column 5", str(tok))

    def test_token_type_categories(self) -> None:
        """Verify key language terminal mappings inside TokenType Enum."""
        self.assertEqual(TokenType.REMEMBER.name, 'REMEMBER')
        self.assertEqual(TokenType.IS_SAME_AS.name, 'IS_SAME_AS')
        self.assertEqual(TokenType.EOF.name, 'EOF')


if __name__ == '__main__':
    unittest.main()
