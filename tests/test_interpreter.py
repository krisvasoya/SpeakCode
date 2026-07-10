"""
Unit tests for the Tree-Walking Interpreter module (speak_interpreter.py).
Checks execution outcomes, stack scopes, recursion, mock input queries, and SPK105 runtime crashes.
"""

import unittest
from unittest.mock import patch
from speak_lexer import SpeakLexer
from speak_parser import SpeakParser
from speak_semantic import SpeakSemanticAnalyzer
from speak_interpreter import SpeakInterpreter
from speak_errors import SpeakRuntimeError


class TestSpeakInterpreter(unittest.TestCase):
    
    def test_variable_declarations_and_math(self) -> None:
        """Verify variable creation, arithmetic operations, and updates."""
        source = (
            "Remember 10 as x.\n"
            "Change x to x times 3.\n"
            "Change x to x modulo 7.\n"
            "Speak x."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        interpreter = SpeakInterpreter(source, "<test>")
        interpreter.interpret(program)
        
        # Verify result value is 10 * 3 % 7 = 30 % 7 = 2
        self.assertEqual(interpreter.environment.lookup("x"), 2)

    @patch('builtins.input', return_value="100")
    def test_mock_ask_input(self, mock_input) -> None:
        """Verify console Ask query reads from stdin and coerces type correctly."""
        source = "Ask \"Enter score: \" and save as score."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        interpreter = SpeakInterpreter(source, "<test>")
        interpreter.interpret(program)
        
        self.assertEqual(interpreter.environment.lookup("score"), 100)

    def test_conditionals_if_otherwise(self) -> None:
        """Verify conditional execution branches."""
        source = (
            "Remember 18 as age.\n"
            "Remember \"unknown\" as status.\n"
            "If age is below 18 then\n"
            "    Change status to \"minor\".\n"
            "Otherwise\n"
            "    Change status to \"adult\".\n"
            "Finish checking."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        interpreter = SpeakInterpreter(source, "<test>")
        interpreter.interpret(program)
        
        self.assertEqual(interpreter.environment.lookup("status"), "adult")

    def test_loops_while_and_repeat(self) -> None:
        """Verify while loop accumulation and repeat loop iteration counts."""
        source = (
            "Remember 0 as total.\n"
            "Remember 1 as i.\n"
            "While i is at most 5 repeat\n"
            "    Change total to total plus i.\n"
            "    Change i to i plus 1.\n"
            "Finish looping.\n"
            "\n"
            "Remember 0 as count.\n"
            "Repeat 10 times\n"
            "    Change count to count plus 1.\n"
            "Finish looping."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        interpreter = SpeakInterpreter(source, "<test>")
        interpreter.interpret(program)
        
        # total = 1+2+3+4+5 = 15
        self.assertEqual(interpreter.environment.lookup("total"), 15)
        # count = 10
        self.assertEqual(interpreter.environment.lookup("count"), 10)

    def test_nested_loops_and_scopes(self) -> None:
        """Verify nested loop scopes variables do not bleed out to parent scopes."""
        source = (
            "Remember 0 as outer_var.\n"
            "Repeat 2 times\n"
            "    Remember 5 as inner_var.\n"
            "    Change outer_var to outer_var plus inner_var.\n"
            "Finish looping."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        interpreter = SpeakInterpreter(source, "<test>")
        interpreter.interpret(program)
        
        self.assertEqual(interpreter.environment.lookup("outer_var"), 10)
        # inner_var must not bleed to global environment
        self.assertFalse(interpreter.environment.exists("inner_var"))

    def test_functions_declaration_and_recursion(self) -> None:
        """Verify function signatures execution and stack recursion parsing (Fibonacci sequence)."""
        source = (
            "To perform fib with n:\n"
            "    If n is at most 1 then\n"
            "        Give back n.\n"
            "    Finish checking.\n"
            "    Perform fib with n minus 1 and save as a.\n"
            "    Perform fib with n minus 2 and save as b.\n"
            "    Give back a plus b.\n"
            "Finish performance.\n"
            "\n"
            "Perform fib with 6 and save as result."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        interpreter = SpeakInterpreter(source, "<test>")
        interpreter.interpret(program)
        
        # fib(6) = 8
        self.assertEqual(interpreter.environment.lookup("result"), 8)

    def test_runtime_division_by_zero_error(self) -> None:
        """Verify that dividing by zero raises SpeakRuntimeError (SPK105)."""
        source = "Remember 10 divided by 0 as x."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        interpreter = SpeakInterpreter(source, "<test>")
        
        with self.assertRaises(SpeakRuntimeError) as context:
            interpreter.interpret(program)
            
        self.assertEqual(context.exception.error_code, "SPK105")
        self.assertIn("Division by zero error", str(context.exception))


if __name__ == '__main__':
    unittest.main()
