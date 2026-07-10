"""
Unit tests for the Syntactic Analyzer Parser module (speak_parser.py).
Checks grammar constructions, error collection, and recovery synchronization.
"""

import unittest
from speak_lexer import SpeakLexer
from speak_parser import SpeakParser
from speak_ast import (
    ProgramNode, RememberNode, ChangeNode, SpeakNode, AskNode,
    IfNode, WhileNode, RepeatNode, FunctionDeclarationNode, FunctionCallNode,
    ReturnNode, BinaryExpressionNode, UnaryExpressionNode, LiteralNode, IdentifierNode, GroupingNode
)


class TestSpeakParser(unittest.TestCase):
    
    def test_variable_declarations_and_assignment(self) -> None:
        """Verify parsing of Remember and Change statements."""
        source = "Remember 10 as x. Change x to x plus 5."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 2)
        self.assertIsInstance(program.statements[0], RememberNode)
        self.assertIsInstance(program.statements[1], ChangeNode)
        
        rem_node = program.statements[0]
        self.assertEqual(rem_node.variable_name, "x")
        self.assertIsInstance(rem_node.expression, LiteralNode)
        
        chg_node = program.statements[1]
        self.assertEqual(chg_node.variable_name, "x")
        self.assertIsInstance(chg_node.expression, BinaryExpressionNode)

    def test_speak_and_ask_statements(self) -> None:
        """Verify parsing of Speak and Ask console statement structures."""
        source = 'Ask "Enter name: " and save as user_name. Speak "Hello " plus user_name.'
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 2)
        self.assertIsInstance(program.statements[0], AskNode)
        self.assertIsInstance(program.statements[1], SpeakNode)
        
        ask_node = program.statements[0]
        self.assertEqual(ask_node.variable_name, "user_name")
        self.assertIsInstance(ask_node.prompt_expr, LiteralNode)

    def test_arithmetic_and_precedence(self) -> None:
        """Verify binary operator priorities (multiplication evaluated before addition)."""
        source = "Speak 5 plus 2 times 3."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        speak_node = program.statements[0]
        expr = speak_node.expression
        
        # 5 + (2 * 3) -> Root is PLUS
        self.assertIsInstance(expr, BinaryExpressionNode)
        self.assertEqual(expr.operator, "plus")
        self.assertIsInstance(expr.left, LiteralNode)
        self.assertIsInstance(expr.right, BinaryExpressionNode)
        self.assertEqual(expr.right.operator, "times")

    def test_parenthesized_grouping(self) -> None:
        """Verify that parentheses override standard operator precedence rules."""
        source = "Speak (5 plus 2) times 3."
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        speak_node = program.statements[0]
        expr = speak_node.expression
        
        # (5 + 2) * 3 -> Root is TIMES
        self.assertIsInstance(expr, BinaryExpressionNode)
        self.assertEqual(expr.operator, "times")
        self.assertIsInstance(expr.left, GroupingNode)
        self.assertIsInstance(expr.left.expression, BinaryExpressionNode)
        self.assertEqual(expr.left.expression.operator, "plus")

    def test_nested_ifs(self) -> None:
        """Verify parsing of nested If-Otherwise conditional blocks."""
        source = (
            "If x is above 10 then\n"
            "    If y is below 5 then\n"
            "        Speak 1.\n"
            "    Otherwise\n"
            "        Speak 2.\n"
            "    Finish checking.\n"
            "Finish checking."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 1)
        self.assertIsInstance(program.statements[0], IfNode)

    def test_loops_repeat_and_while(self) -> None:
        """Verify parsing of While condition loops and Repeat count loops."""
        source = (
            "While count is below 5 repeat\n"
            "    Change count to count plus 1.\n"
            "Finish looping.\n"
            "Repeat 3 times\n"
            "    Speak \"loop\".\n"
            "Finish looping."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 2)
        self.assertIsInstance(program.statements[0], WhileNode)
        self.assertIsInstance(program.statements[1], RepeatNode)

    def test_functions_declaration_and_call(self) -> None:
        """Verify function signatures and performance calls syntax."""
        source = (
            "To perform double with val:\n"
            "    Give back val times 2.\n"
            "Finish performance.\n"
            "Perform double with 10 and save as x."
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 2)
        self.assertIsInstance(program.statements[0], FunctionDeclarationNode)
        self.assertIsInstance(program.statements[1], FunctionCallNode)
        
        decl_node = program.statements[0]
        self.assertEqual(decl_node.name, "double")
        self.assertEqual(decl_node.parameters, ["val"])
        self.assertIsInstance(decl_node.body[0], ReturnNode)
        
        call_node = program.statements[1]
        self.assertEqual(call_node.name, "double")
        self.assertEqual(call_node.save_variable, "x")
        self.assertEqual(len(call_node.arguments), 1)

    def test_empty_program(self) -> None:
        """Verify parser can evaluate an empty string source safely."""
        source = ""
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), 0)

    def test_missing_period_syntax_error(self) -> None:
        """Verify that a missing statement period is reported as SPK102 syntax error."""
        source = "Remember 10 as x"
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        self.assertEqual(len(parser.errors), 1)
        self.assertEqual(parser.errors[0].error_code, "SPK102")
        self.assertIn("Expected period '.'", str(parser.errors[0]))

    def test_missing_closures_errors(self) -> None:
        """Verify error reporting for unclosed blocks (If, While, Function)."""
        scenarios = [
            ("If true then Speak 1.", "Finish checking"),
            ("While true repeat Speak 1.", "Finish looping"),
            ("To perform main: Speak 1.", "Finish performance")
        ]
        
        for source, closure_name in scenarios:
            lexer = SpeakLexer(source, "<test>")
            tokens = lexer.tokenize()
            
            parser = SpeakParser(tokens, source, "<test>")
            parser.parse()
            
            self.assertGreaterEqual(len(parser.errors), 1)
            self.assertIn(closure_name, str(parser.errors[0]))

    def test_unexpected_eof(self) -> None:
        """Verify parser reports syntax error on incomplete final expressions."""
        source = "Speak ("
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        parser.parse()
        
        self.assertGreaterEqual(len(parser.errors), 1)
        self.assertEqual(parser.errors[0].error_code, "SPK102")
        self.assertIn("Unexpected End-of-File", str(parser.errors[0]))

    def test_multiple_syntax_errors_recovery(self) -> None:
        """Verify parser panic-mode synchronization recovers from errors to continue parsing."""
        source = (
            "Remember 10 as x\n"  # Error: missing period
            "Change x to x plus 5.\n"  # Valid statement
            "Speak (.\n"  # Error: malformed expression
            "Speak x."  # Valid statement
        )
        lexer = SpeakLexer(source, "<test>")
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, "<test>")
        program = parser.parse()
        
        # Expecting exactly 2 syntax errors caught
        self.assertEqual(len(parser.errors), 2)
        # Verify it still parsed valid statements
        self.assertEqual(len(program.statements), 2)


if __name__ == '__main__':
    unittest.main()
