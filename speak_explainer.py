"""
SpeakCode Compiler - AST Explainer (Plain English Translator)
Walks the AST using the Visitor Pattern and generates beginner-friendly,
plain English descriptions explaining what each line of code does.

Dependencies:
    - speak_ast.py (ASTNode and subclasses)
"""

from typing import List
from speak_ast import (
    ASTNode, ProgramNode, RememberNode, ChangeNode, SpeakNode, AskNode,
    IfNode, OtherwiseIfNode, OtherwiseNode, WhileNode, RepeatNode,
    FunctionDeclarationNode, FunctionCallNode, ReturnNode
)


class SpeakExplainer:
    """
    Translates SpeakCode AST nodes into readable plain English instructions.
    """

    def explain(self, node: ASTNode) -> List[str]:
        """Entry point to walk the AST and collect string explanations."""
        return node.accept(self)

    def visit_program(self, node: ProgramNode) -> List[str]:
        lines = []
        for stmt in node.statements:
            lines.extend(stmt.accept(self))
        return lines

    def visit_remember(self, node: RememberNode) -> List[str]:
        return [f"Creates a variable named '{node.variable_name}' initialized with value: {node.expression.stringify()}."]

    def visit_change(self, node: ChangeNode) -> List[str]:
        return [f"Updates variable '{node.variable_name}' to store value: {node.expression.stringify()}."]

    def visit_speak(self, node: SpeakNode) -> List[str]:
        return [f"Outputs the expression '{node.expression.stringify()}' to the screen."]

    def visit_ask(self, node: AskNode) -> List[str]:
        prompt = f" showing prompt '{node.prompt_expr.stringify()}'" if node.prompt_expr else ""
        return [f"Asks the user for input{prompt} and saves the value to variable '{node.variable_name}'."]

    def visit_otherwise_if(self, node: OtherwiseIfNode) -> List[str]:
        lines = [f"Alternative check: if condition '{node.condition.stringify()}' is met, execute:"]
        for stmt in node.body:
            for line in stmt.accept(self):
                lines.append(f"    {line}")
        return lines

    def visit_otherwise(self, node: OtherwiseNode) -> List[str]:
        lines = ["Otherwise, if no previous conditions matched, execute:"]
        for stmt in node.body:
            for line in stmt.accept(self):
                lines.append(f"    {line}")
        return lines

    def visit_if(self, node: IfNode) -> List[str]:
        lines = [f"Conditional check: if condition '{node.condition.stringify()}' is met, execute:"]
        for stmt in node.then_branch:
            for line in stmt.accept(self):
                lines.append(f"    {line}")
        for branch in node.otherwise_if_branches:
            for line in branch.accept(self):
                lines.append(f"    {line}")
        if node.otherwise_branch:
            for line in node.otherwise_branch.accept(self):
                lines.append(f"    {line}")
        return lines

    def visit_while(self, node: WhileNode) -> List[str]:
        lines = [f"Loop: while condition '{node.condition.stringify()}' remains true, execute:"]
        for stmt in node.body:
            for line in stmt.accept(self):
                lines.append(f"    {line}")
        return lines

    def visit_repeat(self, node: RepeatNode) -> List[str]:
        lines = [f"Loop: repeat the following block exactly {node.count_expr.stringify()} times:"]
        for stmt in node.body:
            for line in stmt.accept(self):
                lines.append(f"    {line}")
        return lines

    def visit_function_declaration(self, node: FunctionDeclarationNode) -> List[str]:
        p_str = f" taking arguments: {', '.join(node.parameters)}" if node.parameters else ""
        lines = [f"Defines a function named '{node.name}'{p_str}:"]
        for stmt in node.body:
            for line in stmt.accept(self):
                lines.append(f"    {line}")
        return lines

    def visit_function_call(self, node: FunctionCallNode) -> List[str]:
        a_str = f" with arguments: {', '.join(a.stringify() for a in node.arguments)}" if node.arguments else ""
        save = f" and save result to variable '{node.save_variable}'" if node.save_variable else ""
        return [f"Calls function '{node.name}'{a_str}{save}."]

    def visit_return(self, node: ReturnNode) -> List[str]:
        return [f"Exits the current function and returns value: {node.expression.stringify()}."]
