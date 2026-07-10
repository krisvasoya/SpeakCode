"""
Unit tests for the SpeakCode Developer Toolkit CLI (speakcode.py).
Mocks command arguments, captures stdout streams, and verifies each CLI command.
"""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch
import speakcode


class TestSpeakCodeCLI(unittest.TestCase):

    def setUp(self) -> None:
        self.test_filename = "temp_cli_test.speak"
        self.test_content = "Remember 10 as score. Speak score."
        with open(self.test_filename, "w", encoding="utf-8") as f:
            f.write(self.test_content)

    def tearDown(self) -> None:
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_version(self, mock_stdout) -> None:
        """Verify 'speakcode version' command displays banner info."""
        with patch('sys.argv', ['speakcode', 'version']):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("1.0.0", output)
        self.assertIn("Krish Vasoya", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_help(self, mock_stdout) -> None:
        """Verify 'speakcode help' and sub-command help texts."""
        with patch('sys.argv', ['speakcode', 'help', 'run']):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("speakcode run", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_run(self, mock_stdout) -> None:
        """Verify 'speakcode run <file>' compiles, validates, and prints results."""
        with patch('sys.argv', ['speakcode', 'run', self.test_filename]):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertEqual(output.strip(), "10")

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_tokens(self, mock_stdout) -> None:
        """Verify 'speakcode tokens <file>' displays lexer tokens table."""
        with patch('sys.argv', ['speakcode', 'tokens', self.test_filename]):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("Token Type", output)
        self.assertIn("REMEMBER", output)
        self.assertIn("score", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_ast(self, mock_stdout) -> None:
        """Verify 'speakcode ast <file>' draws ASCII branches."""
        with patch('sys.argv', ['speakcode', 'ast', self.test_filename]):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("Program", output)
        self.assertIn("├── Remember", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_semantic(self, mock_stdout) -> None:
        """Verify 'speakcode semantic <file>' performs logical static reviews."""
        with patch('sys.argv', ['speakcode', 'semantic', self.test_filename]):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("Passed", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_debug(self, mock_stdout) -> None:
        """Verify 'speakcode debug <file>' traces stages validations."""
        with patch('sys.argv', ['speakcode', 'debug', self.test_filename]):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("Lexical Analysis", output)
        self.assertIn("Semantic Analysis", output)
        self.assertIn("Execution Complete", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_explain(self, mock_stdout) -> None:
        """Verify 'speakcode explain <file>' translates statements."""
        with patch('sys.argv', ['speakcode', 'explain', self.test_filename]):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("Creates a variable named", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_format(self, mock_stdout) -> None:
        """Verify 'speakcode format <file>' standardizes indentation and spacing."""
        unformatted = "remember   10   as   score.   "
        formatted_file = "temp_format.speak"
        with open(formatted_file, "w", encoding="utf-8") as f:
            f.write(unformatted)
            
        try:
            with patch('sys.argv', ['speakcode', 'format', formatted_file]):
                speakcode.main()
                
            with open(formatted_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            self.assertEqual(content, "Remember 10 as score.\n")
        finally:
            if os.path.exists(formatted_file):
                os.remove(formatted_file)

    @patch('builtins.input', side_effect=["Remember 5 as x.", "Speak x.", "exit"])
    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_repl(self, mock_stdout, mock_input) -> None:
        """Verify REPL shell command execution and environment retention."""
        with patch('sys.argv', ['speakcode', 'repl']):
            speakcode.main()
        output = mock_stdout.getvalue()
        self.assertIn("Interactive REPL", output)
        self.assertIn("5", output)


if __name__ == '__main__':
    unittest.main()
