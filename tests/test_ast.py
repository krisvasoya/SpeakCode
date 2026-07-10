"""
Unit tests for the Abstract Syntax Tree (AST) modules (speak_ast.py).
Checks node immutability, pretty_print layout formats, to_dict serialization, and accept visitor hooks.
"""

import unittest
from dataclasses import FrozenInstanceError
from speak_tokens import Position
from speak_ast import (
    ProgramNode, RememberNode, ChangeNode, SpeakNode, AskNode,
    IfNode, OtherwiseIfNode, OtherwiseNode, WhileNode, RepeatNode,
    FunctionDeclarationNode, FunctionCallNode, ReturnNode,
    BinaryExpressionNode, UnaryExpressionNode, LiteralNode, IdentifierNode, GroupingNode
)


class MockVisitor:
    """Mock visitor for verifying visitor pattern routing hooks."""
    def __init__(self) -> None:
        self.visited = []

    def visit_program(self, node: ProgramNode) -> str:
        self.visited.append("program")
        return "program_val"

    def visit_remember(self, node: RememberNode) -> str:
        self.visited.append("remember")
        return "remember_val"

    def visit_change(self, node: ChangeNode) -> str:
        self.visited.append("change")
        return "change_val"

    def visit_speak(self, node: SpeakNode) -> str:
        self.visited.append("speak")
        return "speak_val"

    def visit_ask(self, node: AskNode) -> str:
        self.visited.append("ask")
        return "ask_val"

    def visit_otherwise_if(self, node: OtherwiseIfNode) -> str:
        self.visited.append("otherwise_if")
        return "otherwise_if_val"

    def visit_otherwise(self, node: OtherwiseNode) -> str:
        self.visited.append("otherwise")
        return "otherwise_val"

    def visit_if(self, node: IfNode) -> str:
        self.visited.append("if")
        return "if_val"

    def visit_while(self, node: WhileNode) -> str:
        self.visited.append("while")
        return "while_val"

    def visit_repeat(self, node: RepeatNode) -> str:
        self.visited.append("repeat")
        return "repeat_val"

    def visit_function_declaration(self, node: FunctionDeclarationNode) -> str:
        self.visited.append("function_declaration")
        return "function_declaration_val"

    def visit_function_call(self, node: FunctionCallNode) -> str:
        self.visited.append("function_call")
        return "function_call_val"

    def visit_return(self, node: ReturnNode) -> str:
        self.visited.append("return")
        return "return_val"

    def visit_binary_expression(self, node: BinaryExpressionNode) -> str:
        self.visited.append("binary_expression")
        return "binary_expression_val"

    def visit_unary_expression(self, node: UnaryExpressionNode) -> str:
        self.visited.append("unary_expression")
        return "unary_expression_val"

    def visit_literal(self, node: LiteralNode) -> str:
        self.visited.append("literal")
        return "literal_val"

    def visit_identifier(self, node: IdentifierNode) -> str:
        self.visited.append("identifier")
        return "identifier_val"

    def visit_grouping(self, node: GroupingNode) -> str:
        self.visited.append("grouping")
        return "grouping_val"


class TestSpeakAST(unittest.TestCase):
    
    def setUp(self) -> None:
        self.pos = Position("test.speak", 1, 1)

    def test_node_immutability(self) -> None:
        """Verify AST nodes are frozen dataclasses and cannot be modified after construction."""
        lit = LiteralNode(42, self.pos)
        rem = RememberNode("x", lit, self.pos)
        
        with self.assertRaises(FrozenInstanceError):
            rem.variable_name = "y"  # type: ignore

    def test_visitor_routing(self) -> None:
        """Verify that accept(visitor) routes correctly to corresponding visitor visits."""
        visitor = MockVisitor()
        lit = LiteralNode(42, self.pos)
        rem = RememberNode("x", lit, self.pos)
        
        ret_val = rem.accept(visitor)
        self.assertEqual(ret_val, "remember_val")
        self.assertEqual(visitor.visited, ["remember"])

    def test_stringify_formats(self) -> None:
        """Verify that stringify prints SpeakCode code strings matching rules."""
        pos = self.pos
        lit = LiteralNode(10, pos)
        rem = RememberNode("marks", lit, pos)
        
        # Verify remember layout stringify
        self.assertEqual(rem.stringify(), "Remember 10 as marks.")
        
        # Verify binary expression groupings stringify
        ident = IdentifierNode("marks", pos)
        bin_expr = BinaryExpressionNode(ident, "plus", LiteralNode(5, pos), pos)
        self.assertEqual(bin_expr.stringify(), "(marks plus 5)")

    def test_pretty_print_layout(self) -> None:
        """Verify visual branch formatting structure."""
        pos = self.pos
        lit = LiteralNode(90, pos)
        rem = RememberNode("marks", lit, pos)
        prog = ProgramNode([rem], pos)
        
        pretty = prog.pretty_print()
        self.assertIn("Program", pretty)
        self.assertIn("└── Remember", pretty)
        self.assertIn("    ├── Identifier : marks", pretty)
        self.assertIn("    └── Literal : 90", pretty)

    def test_to_dict_serialization(self) -> None:
        """Verify recursive serialization details."""
        pos = self.pos
        lit = LiteralNode(True, pos)
        rem = RememberNode("flag", lit, pos)
        
        d = rem.to_dict()
        self.assertEqual(d["type"], "RememberNode")
        self.assertEqual(d["variable_name"], "flag")
        self.assertEqual(d["expression"]["type"], "LiteralNode")
        self.assertEqual(d["expression"]["value"], True)
        self.assertEqual(d["position"]["line"], 1)


if __name__ == '__main__':
    unittest.main()
