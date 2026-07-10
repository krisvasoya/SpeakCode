"""
Unit tests for the Semantic Analyzer module (speak_semantic.py).
Checks scope nesting, variable bindings, function validation, and type compatibility.
"""

import unittest
from speak_lexer import SpeakLexer
from speak_parser import SpeakParser
from speak_semantic import SpeakSemanticAnalyzer
from speak_errors import SpeakSemanticError, SpeakTypeError


class TestSpeakSemantic(unittest.TestCase):
    
    def test_valid_program(self) -> None:
        """Verify that a logically valid program passes semantic checks with 0 errors."""
        source = (
            "Remember 10 as age.\n"
            "If age is above 18 then\n"
            "    Remember \"Adult\" as status.\n"
            "    Speak status.\n"
            "Finish checking."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 0)

    def test_undefined_variable_error(self) -> None:
        """Verify that accessing an undeclared variable throws SPK104."""
        source = "Speak x."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 1)
        self.assertEqual(analyzer.errors[0].error_code, "SPK104")
        self.assertIn("Variable 'x' has not been declared", str(analyzer.errors[0]))

    def test_duplicate_variable_error(self) -> None:
        """Verify that redefining a variable in the same local scope throws SPK103."""
        source = "Remember 10 as x. Remember 20 as x."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 1)
        self.assertEqual(analyzer.errors[0].error_code, "SPK103")
        self.assertIn("already defined in the current scope", str(analyzer.errors[0]))

    def test_shadowing_allowed_in_child_scope(self) -> None:
        """Verify that variable shadowing is allowed in nested scopes."""
        source = (
            "Remember 10 as x.\n"
            "If true then\n"
            "    Remember 20 as x. # Shadowing allowed here\n"
            "Finish checking."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 0)

    def test_duplicate_function_declaration(self) -> None:
        """Verify that duplicate global function declarations throw SPK106."""
        source = (
            "To perform greet:\n"
            "    Speak \"hello\".\n"
            "Finish performance.\n"
            "To perform greet:\n"
            "    Speak \"hi\".\n"
            "Finish performance."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 1)
        self.assertEqual(analyzer.errors[0].error_code, "SPK106")
        self.assertIn("Duplicate declaration of function name 'greet'", str(analyzer.errors[0]))

    def test_undefined_function_call(self) -> None:
        """Verify that calling an undeclared function throws SPK106."""
        source = "Perform calculate."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 1)
        self.assertEqual(analyzer.errors[0].error_code, "SPK106")
        self.assertIn("Function 'calculate' has not been defined", str(analyzer.errors[0]))

    def test_wrong_argument_count(self) -> None:
        """Verify that parameter count mismatches throw SPK106."""
        source = (
            "To perform add with a and b:\n"
            "    Give back a plus b.\n"
            "Finish performance.\n"
            "Perform add with 10."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 1)
        self.assertEqual(analyzer.errors[0].error_code, "SPK106")
        self.assertIn("expects 2 parameter(s), but you provided 1", str(analyzer.errors[0]))

    def test_return_outside_function(self) -> None:
        """Verify that using Give back globally throws SPK107."""
        source = "Give back 5."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 1)
        self.assertEqual(analyzer.errors[0].error_code, "SPK107")
        self.assertIn("can only be used inside a performance definition block", str(analyzer.errors[0]))

    def test_type_mismatches_operations(self) -> None:
        """Verify type checking (Number times String, Boolean and Number) throws SPK108."""
        scenarios = [
            ("Speak 5 times \"hello\".", "SPK108"),
            ("Speak true and 10.", "SPK108"),
            ("If 42 then Speak 1. Finish checking.", "SPK108")
        ]
        
        for source, err_code in scenarios:
            lexer = SpeakLexer(source, "<test>")
            tokens = lexer.tokenize()
            
            parser = SpeakParser(tokens, source, "<test>")
            program = parser.parse()
            
            analyzer = SpeakSemanticAnalyzer(source, "<test>")
            analyzer.analyze(program)
            
            self.assertGreaterEqual(len(analyzer.errors), 1)
            self.assertEqual(analyzer.errors[0].error_code, err_code)

    def test_recursion_allowed(self) -> None:
        """Verify recursive function declarations are allowed dynamically without loops block errors."""
        source = (
            "To perform fib with n:\n"
            "    If n is at most 1 then\n"
            "        Give back n.\n"
            "    Finish checking.\n"
            "    Perform fib with n minus 1 and save as f1.\n"
            "    Perform fib with n minus 2 and save as f2.\n"
            "    Give back f1 plus f2.\n"
            "Finish performance."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        self.assertEqual(len(analyzer.errors), 0)

    def test_multiple_semantic_errors(self) -> None:
        """Verify panic recovery aggregates multiple errors rather than halting on first."""
        source = (
            "Speak x.\n"             # Error 1: Undefined variable x (SPK104)
            "Remember 10 as y.\n"
            "Remember 20 as y.\n"    # Error 2: Duplicate variable y (SPK103)
            "Give back y."           # Error 3: Return outside function (SPK107)
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source, "<test>")
        analyzer.analyze(program)
        
        # Should collect exactly 3 semantic issues
        self.assertEqual(len(analyzer.errors), 3)
        self.assertEqual(analyzer.errors[0].error_code, "SPK104")
        self.assertEqual(analyzer.errors[1].error_code, "SPK103")
        self.assertEqual(analyzer.errors[2].error_code, "SPK107")


if __name__ == '__main__':
    unittest.main()
