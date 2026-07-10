import unittest
import sys
from speak_lexer import SpeakLexer, TokenType
from speak_parser import SpeakParser
from speak_semantic import SpeakSemanticAnalyzer
from speak_interpreter import SpeakInterpreter
from speak_errors import SpeakLexerError, SpeakSyntaxError, SpeakSemanticError, SpeakRuntimeError, SpeakTypeError

class TestSpeakCodeRedesign(unittest.TestCase):
    def test_lexer_success(self):
        source = 'Remember 10 as age. Change age to age plus 1. Speak "Age: " plus age.'
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        
        types = [t.type for t in tokens]
        expected = [
            TokenType.REMEMBER, TokenType.NUMBER, TokenType.AS, TokenType.IDENTIFIER, TokenType.PERIOD,
            TokenType.CHANGE, TokenType.IDENTIFIER, TokenType.TO, TokenType.IDENTIFIER, TokenType.PLUS, TokenType.NUMBER, TokenType.PERIOD,
            TokenType.SPEAK, TokenType.STRING, TokenType.PLUS, TokenType.IDENTIFIER, TokenType.PERIOD,
            TokenType.EOF
        ]
        self.assertEqual(types, expected)

    def test_lexer_error_invalid_char(self):
        source = 'Remember x as @.'
        lexer = SpeakLexer(source)
        with self.assertRaises(SpeakLexerError):
            lexer.tokenize()

    def test_parser_success(self):
        source = 'Remember 5 as x. Speak x.'
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        self.assertEqual(len(program.statements), 2)

    def test_parser_error_missing_period(self):
        source = 'Remember 5 as x'
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        self.assertTrue(len(parser.errors) > 0)
        self.assertIn("Expected period '.'", str(parser.errors[0]))

    def test_semantic_duplicate_declaration(self):
        source = """
        Remember 10 as x.
        Remember 20 as x.
        """
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source)
        analyzer.analyze(program)
        self.assertTrue(len(analyzer.errors) > 0)
        self.assertIn("already defined in the current scope", str(analyzer.errors[0]))

    def test_semantic_undefined_variable(self):
        source = "Change y to 5."
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source)
        analyzer.analyze(program)
        self.assertTrue(len(analyzer.errors) > 0)
        self.assertIn("Variable 'y' is not defined", str(analyzer.errors[0]))

    def test_semantic_function_arg_mismatch(self):
        source = """
        To perform double with val:
            Give back val times 2.
        Finish performance.
        
        Perform double.
        """
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source)
        analyzer.analyze(program)
        self.assertTrue(len(analyzer.errors) > 0)
        self.assertIn("expects 1 parameter(s), but you provided 0 argument(s)", str(analyzer.errors[0]))

    def test_semantic_return_outside_function(self):
        source = "Give back 10."
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source)
        analyzer.analyze(program)
        self.assertTrue(len(analyzer.errors) > 0)
        self.assertIn("can only be used inside a performance definition block", str(analyzer.errors[0]))

    def test_semantic_static_type_checking(self):
        source = 'Remember 5 minus "hello" as x.'
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source)
        analyzer.analyze(program)
        self.assertTrue(len(analyzer.errors) > 0)
        self.assertIn("requires numeric operands", str(analyzer.errors[0]))

    def test_interpreter_functions_and_scoping(self):
        source = """
        To perform add_one with val:
            Give back val plus 1.
        Finish performance.
        
        Remember 10 as x.
        Perform add_one with x and save as y.
        """
        lexer = SpeakLexer(source)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source)
        program = parser.parse()
        
        analyzer = SpeakSemanticAnalyzer(source)
        analyzer.analyze(program)
        
        interpreter = SpeakInterpreter(source)
        interpreter.interpret(program)
        
        self.assertEqual(interpreter.environment.lookup("y"), 11)
        self.assertEqual(interpreter.environment.lookup("x"), 10)

if __name__ == "__main__":
    unittest.main()
