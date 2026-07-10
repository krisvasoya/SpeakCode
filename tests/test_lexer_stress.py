"""
Stress and Performance test suite for the SpeakCode Lexer.
Verifies tokenization limits on large inputs and evaluates scanner performance.
"""

import unittest
import time
from speak_lexer import SpeakLexer, get_token_statistics
from speak_tokens import TokenType


class TestLexerStress(unittest.TestCase):
    
    def test_large_input_stress_and_performance(self) -> None:
        """Stress test the lexer by scanning 10,000 lines of nested loop calls."""
        # Generate 10,000 lines of variable bindings and math calls
        lines = []
        for i in range(10000):
            lines.append(f"Remember {i} plus 10 as var_{i}.")
            lines.append(f"Speak var_{i} is same as {i + 10}.")
            
        large_source = "\n".join(lines)
        
        lexer = SpeakLexer(large_source, "stress_test.speak")
        
        start_time = time.perf_counter()
        tokens = lexer.tokenize()
        end_time = time.perf_counter()
        
        elapsed = end_time - start_time
        
        # Verify correctness
        self.assertGreater(len(tokens), 80000)
        self.assertEqual(tokens[-1].type, TokenType.EOF)
        
        # Output profiling results
        print(f"\n[Performance Profile] Scanned {len(lines)} lines ({len(tokens)} tokens) in {elapsed:.4f} seconds.")
        
        # Assert performance boundary (must complete within 0.8 seconds on standard run environments)
        self.assertLess(elapsed, 0.8)
        
        # Verify and display token statistics frequencies
        stats = get_token_statistics(tokens)
        self.assertIn(TokenType.REMEMBER, stats)
        self.assertEqual(stats[TokenType.REMEMBER], 10000)
        self.assertEqual(stats[TokenType.SPEAK], 10000)


if __name__ == '__main__':
    unittest.main()
