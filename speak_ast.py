"""
SpeakCode Compiler - Abstract Syntax Tree (AST) Definition
Defines the strongly typed, immutable dataclass AST nodes representing SpeakCode terminals.
Implements serialization to_dict(), serialization formatting stringify(),
and visually aligned recursive pretty_print() tree drawer.

Dependencies:
    - dataclasses (Standard Library)
    - speak_tokens.py (Position)
"""

from dataclasses import dataclass
from typing import Any, List, Optional
from speak_tokens import Position


class ASTNode:
    """Base class for all Abstract Syntax Tree (AST) nodes."""
    
    def accept(self, visitor: Any) -> Any:
        """Visitor pattern traversal entry point hook."""
        raise NotImplementedError()

    def stringify(self) -> str:
        """Formats the AST node back into equivalent SpeakCode source code."""
        raise NotImplementedError()

    def pretty_print(self, indent: int = 0) -> str:
        """Draws the AST node recursively in ASCII directory-style branches."""
        raise NotImplementedError()

    def to_dict(self) -> dict:
        """Serializes the AST node recursively into standard dictionaries for verification."""
        raise NotImplementedError()


class StatementNode(ASTNode):
    """Abstract base class for all statement nodes in SpeakCode."""
    position: Position


class ExpressionNode(ASTNode):
    """Abstract base class for all expression nodes in SpeakCode."""
    position: Position


@dataclass(frozen=True)
class ProgramNode(ASTNode):
    """Root program node containing statements list."""
    statements: List[StatementNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_program(self)

    def stringify(self) -> str:
        return "\n".join(s.stringify() for s in self.statements)

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Program"]
        for idx, stmt in enumerate(self.statements):
            is_last = (idx == len(self.statements) - 1)
            marker = "└── " if is_last else "├── "
            stmt_lines = stmt.pretty_print(indent + 1).splitlines()
            if stmt_lines:
                lines.append(marker + stmt_lines[0])
                for line in stmt_lines[1:]:
                    prefix = "    " if is_last else "│   "
                    lines.append(prefix + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "ProgramNode",
            "statements": [s.to_dict() for s in self.statements],
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class RememberNode(StatementNode):
    """Variable declaration node: Remember <expression> as <variable_name>."""
    variable_name: str
    expression: ExpressionNode
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_remember(self)

    def stringify(self) -> str:
        return f"Remember {self.expression.stringify()} as {self.variable_name}."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Remember"]
        lines.append("├── Identifier : " + self.variable_name)
        expr_lines = self.expression.pretty_print(indent + 1).splitlines()
        if expr_lines:
            lines.append("└── " + expr_lines[0])
            for line in expr_lines[1:]:
                lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "RememberNode",
            "variable_name": self.variable_name,
            "expression": self.expression.to_dict(),
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class ChangeNode(StatementNode):
    """Variable modification node: Change <variable_name> to <expression>."""
    variable_name: str
    expression: ExpressionNode
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_change(self)

    def stringify(self) -> str:
        return f"Change {self.variable_name} to {self.expression.stringify()}."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Change"]
        lines.append("├── Identifier : " + self.variable_name)
        expr_lines = self.expression.pretty_print(indent + 1).splitlines()
        if expr_lines:
            lines.append("└── " + expr_lines[0])
            for line in expr_lines[1:]:
                lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "ChangeNode",
            "variable_name": self.variable_name,
            "expression": self.expression.to_dict(),
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class SpeakNode(StatementNode):
    """Standard console printing node: Speak <expression>."""
    expression: ExpressionNode
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_speak(self)

    def stringify(self) -> str:
        return f"Speak {self.expression.stringify()}."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Speak"]
        expr_lines = self.expression.pretty_print(indent + 1).splitlines()
        if expr_lines:
            lines.append("└── " + expr_lines[0])
            for line in expr_lines[1:]:
                lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "SpeakNode",
            "expression": self.expression.to_dict(),
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class AskNode(StatementNode):
    """Standard console querying node: Ask (prompt_expr)? and save as <variable_name>."""
    prompt_expr: Optional[ExpressionNode]
    variable_name: str
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_ask(self)

    def stringify(self) -> str:
        prompt = f"{self.prompt_expr.stringify()} " if self.prompt_expr else ""
        return f"Ask {prompt}and save as {self.variable_name}."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Ask"]
        if self.prompt_expr:
            p_lines = self.prompt_expr.pretty_print(indent + 1).splitlines()
            if p_lines:
                lines.append("├── Prompt: " + p_lines[0])
                for line in p_lines[1:]:
                    lines.append("│   " + line)
        lines.append("└── Identifier : " + self.variable_name)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "AskNode",
            "prompt_expr": self.prompt_expr.to_dict() if self.prompt_expr else None,
            "variable_name": self.variable_name,
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class OtherwiseIfNode(StatementNode):
    """Branch conditional sub-node inside If statement frames."""
    condition: ExpressionNode
    body: List[StatementNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_otherwise_if(self)

    def stringify(self) -> str:
        body_str = "\n".join(s.stringify() for s in self.body)
        return f"Otherwise if {self.condition.stringify()} then\n{body_str}"

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Otherwise If"]
        cond_lines = self.condition.pretty_print(indent + 1).splitlines()
        if cond_lines:
            lines.append("├── Condition")
            lines.append("│   └── " + cond_lines[0])
            for line in cond_lines[1:]:
                lines.append("│       " + line)
        lines.append("└── Body")
        for idx, stmt in enumerate(self.body):
            is_last = (idx == len(self.body) - 1)
            prefix = "    └── " if is_last else "    ├── "
            stmt_lines = stmt.pretty_print(indent + 1).splitlines()
            if stmt_lines:
                lines.append(prefix + stmt_lines[0])
                for line in stmt_lines[1:]:
                    sub_prefix = "        " if is_last else "    │   "
                    lines.append(sub_prefix + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "OtherwiseIfNode",
            "condition": self.condition.to_dict(),
            "body": [s.to_dict() for s in self.body],
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class OtherwiseNode(StatementNode):
    """Else fallback branch sub-node inside If statement frames."""
    body: List[StatementNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_otherwise(self)

    def stringify(self) -> str:
        body_str = "\n".join(s.stringify() for s in self.body)
        return f"Otherwise\n{body_str}"

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Otherwise"]
        for idx, stmt in enumerate(self.body):
            is_last = (idx == len(self.body) - 1)
            prefix = "└── " if is_last else "├── "
            stmt_lines = stmt.pretty_print(indent + 1).splitlines()
            if stmt_lines:
                lines.append(prefix + stmt_lines[0])
                for line in stmt_lines[1:]:
                    sub_prefix = "    " if is_last else "│   "
                    lines.append(sub_prefix + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "OtherwiseNode",
            "body": [s.to_dict() for s in self.body],
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class IfNode(StatementNode):
    """Conditional block statement node mapping positive, else-if, and else branches."""
    condition: ExpressionNode
    then_branch: List[StatementNode]
    otherwise_if_branches: List[OtherwiseIfNode]
    otherwise_branch: Optional[OtherwiseNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_if(self)

    def stringify(self) -> str:
        elif_str = "".join("\n" + o.stringify() for o in self.otherwise_if_branches)
        else_str = f"\n{self.otherwise_branch.stringify()}" if self.otherwise_branch else ""
        then_str = "\n".join(s.stringify() for s in self.then_branch)
        return f"If {self.condition.stringify()} then\n{then_str}{elif_str}{else_str}\nFinish checking."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["If"]
        cond_lines = self.condition.pretty_print(indent + 1).splitlines()
        if cond_lines:
            lines.append("├── Condition")
            lines.append("│   └── " + cond_lines[0])
            for line in cond_lines[1:]:
                lines.append("│       " + line)
        
        lines.append("├── Then Body")
        for idx, stmt in enumerate(self.then_branch):
            is_last = (idx == len(self.then_branch) - 1 and not self.otherwise_if_branches and not self.otherwise_branch)
            prefix = "│   └── " if is_last else "│   ├── "
            stmt_lines = stmt.pretty_print(indent + 1).splitlines()
            if stmt_lines:
                lines.append(prefix + stmt_lines[0])
                for line in stmt_lines[1:]:
                    sub_prefix = "│       " if is_last else "│   │   "
                    lines.append(sub_prefix + line)
                    
        for idx, elif_branch in enumerate(self.otherwise_if_branches):
            is_last = (idx == len(self.otherwise_if_branches) - 1 and not self.otherwise_branch)
            prefix = "└── " if is_last else "├── "
            elif_lines = elif_branch.pretty_print(indent + 1).splitlines()
            if elif_lines:
                lines.append(prefix + elif_lines[0])
                for line in elif_lines[1:]:
                    sub_prefix = "    " if is_last else "│   "
                    lines.append(sub_prefix + line)
                    
        if self.otherwise_branch:
            else_lines = self.otherwise_branch.pretty_print(indent + 1).splitlines()
            if else_lines:
                lines.append("└── " + else_lines[0])
                for line in else_lines[1:]:
                    lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "IfNode",
            "condition": self.condition.to_dict(),
            "then_branch": [s.to_dict() for s in self.then_branch],
            "otherwise_if_branches": [o.to_dict() for o in self.otherwise_if_branches],
            "otherwise_branch": self.otherwise_branch.to_dict() if self.otherwise_branch else None,
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class WhileNode(StatementNode):
    """Conditional loop block: While <condition> repeat."""
    condition: ExpressionNode
    body: List[StatementNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_while(self)

    def stringify(self) -> str:
        body_str = "\n".join(s.stringify() for s in self.body)
        return f"While {self.condition.stringify()} repeat\n{body_str}\nFinish looping."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["While"]
        cond_lines = self.condition.pretty_print(indent + 1).splitlines()
        if cond_lines:
            lines.append("├── Condition")
            lines.append("│   └── " + cond_lines[0])
            for line in cond_lines[1:]:
                lines.append("│       " + line)
        lines.append("└── Loop Body")
        for idx, stmt in enumerate(self.body):
            is_last = (idx == len(self.body) - 1)
            prefix = "    └── " if is_last else "    ├── "
            stmt_lines = stmt.pretty_print(indent + 1).splitlines()
            if stmt_lines:
                lines.append(prefix + stmt_lines[0])
                for line in stmt_lines[1:]:
                    sub_prefix = "        " if is_last else "    │   "
                    lines.append(sub_prefix + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "WhileNode",
            "condition": self.condition.to_dict(),
            "body": [s.to_dict() for s in self.body],
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class RepeatNode(StatementNode):
    """Fixed count loop block: Repeat <count_expr> times."""
    count_expr: ExpressionNode
    body: List[StatementNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_repeat(self)

    def stringify(self) -> str:
        body_str = "\n".join(s.stringify() for s in self.body)
        return f"Repeat {self.count_expr.stringify()} times\n{body_str}\nFinish looping."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Repeat"]
        cnt_lines = self.count_expr.pretty_print(indent + 1).splitlines()
        if cnt_lines:
            lines.append("├── Count")
            lines.append("│   └── " + cnt_lines[0])
            for line in cnt_lines[1:]:
                lines.append("│       " + line)
        lines.append("└── Loop Body")
        for idx, stmt in enumerate(self.body):
            is_last = (idx == len(self.body) - 1)
            prefix = "    └── " if is_last else "    ├── "
            stmt_lines = stmt.pretty_print(indent + 1).splitlines()
            if stmt_lines:
                lines.append(prefix + stmt_lines[0])
                for line in stmt_lines[1:]:
                    sub_prefix = "        " if is_last else "    │   "
                    lines.append(sub_prefix + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "RepeatNode",
            "count_expr": self.count_expr.to_dict(),
            "body": [s.to_dict() for s in self.body],
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class FunctionDeclarationNode(StatementNode):
    """Custom performance signature block definition node."""
    name: str
    parameters: List[str]
    body: List[StatementNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_function_declaration(self)

    def stringify(self) -> str:
        p_str = " with " + " and ".join(self.parameters) if self.parameters else ""
        body_str = "\n".join(s.stringify() for s in self.body)
        return f"To perform {self.name}{p_str}:\n{body_str}\nFinish performance."

    def pretty_print(self, indent: int = 0) -> str:
        lines = [f"To Perform: {self.name}"]
        if self.parameters:
            lines.append("├── Parameters")
            for param in self.parameters:
                lines.append("│   └── " + param)
        lines.append("└── Body")
        for idx, stmt in enumerate(self.body):
            is_last = (idx == len(self.body) - 1)
            prefix = "    └── " if is_last else "    ├── "
            stmt_lines = stmt.pretty_print(indent + 1).splitlines()
            if stmt_lines:
                lines.append(prefix + stmt_lines[0])
                for line in stmt_lines[1:]:
                    sub_prefix = "        " if is_last else "    │   "
                    lines.append(sub_prefix + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "FunctionDeclarationNode",
            "name": self.name,
            "parameters": self.parameters,
            "body": [s.to_dict() for s in self.body],
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class FunctionCallNode(StatementNode):
    """Performance execution invocation node."""
    name: str
    arguments: List[ExpressionNode]
    save_variable: Optional[str]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_function_call(self)

    def stringify(self) -> str:
        a_str = " with " + " and ".join(a.stringify() for a in self.arguments) if self.arguments else ""
        s_str = f" and save as {self.save_variable}" if self.save_variable else ""
        return f"Perform {self.name}{a_str}{s_str}."

    def pretty_print(self, indent: int = 0) -> str:
        lines = [f"Perform: {self.name}"]
        if self.save_variable:
            lines.append("├── Save To: " + self.save_variable)
        if self.arguments:
            lines.append("└── Arguments")
            for idx, arg in enumerate(self.arguments):
                is_last = (idx == len(self.arguments) - 1)
                prefix = "    └── " if is_last else "    ├── "
                arg_lines = arg.pretty_print(indent + 1).splitlines()
                if arg_lines:
                    lines.append(prefix + arg_lines[0])
                    for line in arg_lines[1:]:
                        sub_prefix = "        " if is_last else "    │   "
                        lines.append(sub_prefix + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "FunctionCallNode",
            "name": self.name,
            "arguments": [a.to_dict() for a in self.arguments],
            "save_variable": self.save_variable,
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class ReturnNode(StatementNode):
    """Exit function frames with value: Give back <expression>."""
    expression: ExpressionNode
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_return(self)

    def stringify(self) -> str:
        return f"Give back {self.expression.stringify()}."

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Give Back"]
        expr_lines = self.expression.pretty_print(indent + 1).splitlines()
        if expr_lines:
            lines.append("└── " + expr_lines[0])
            for line in expr_lines[1:]:
                lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "ReturnNode",
            "expression": self.expression.to_dict(),
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class BinaryExpressionNode(ExpressionNode):
    """Arithmetic or logical binary operations (plus, minus, or, etc.)."""
    left: ExpressionNode
    operator: str
    right: ExpressionNode
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_binary_expression(self)

    def stringify(self) -> str:
        return f"({self.left.stringify()} {self.operator} {self.right.stringify()})"

    def pretty_print(self, indent: int = 0) -> str:
        lines = [f"BinaryExpr ({self.operator.upper()})"]
        left_lines = self.left.pretty_print(indent + 1).splitlines()
        if left_lines:
            lines.append("├── Left: " + left_lines[0])
            for line in left_lines[1:]:
                lines.append("│   " + line)
        right_lines = self.right.pretty_print(indent + 1).splitlines()
        if right_lines:
            lines.append("└── Right: " + right_lines[0])
            for line in right_lines[1:]:
                lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "BinaryExpressionNode",
            "left": self.left.to_dict(),
            "operator": self.operator,
            "right": self.right.to_dict(),
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class UnaryExpressionNode(ExpressionNode):
    """Arithmetic negation (minus) or logical NOT (opposite of) unary operators."""
    operator: str
    expression: ExpressionNode
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_unary_expression(self)

    def stringify(self) -> str:
        return f"({self.operator} {self.expression.stringify()})"

    def pretty_print(self, indent: int = 0) -> str:
        lines = [f"UnaryExpr ({self.operator.upper()})"]
        expr_lines = self.expression.pretty_print(indent + 1).splitlines()
        if expr_lines:
            lines.append("└── Expression: " + expr_lines[0])
            for line in expr_lines[1:]:
                lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "UnaryExpressionNode",
            "operator": self.operator,
            "expression": self.expression.to_dict(),
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class LiteralNode(ExpressionNode):
    """Literal values: numbers, string, true, false constants."""
    value: Any
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_literal(self)

    def stringify(self) -> str:
        if isinstance(self.value, str):
            return f'"{self.value}"'
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        return str(self.value)

    def pretty_print(self, indent: int = 0) -> str:
        return f"Literal : {repr(self.value)}"

    def to_dict(self) -> dict:
        return {
            "type": "LiteralNode",
            "value": self.value,
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class IdentifierNode(ExpressionNode):
    """Variable identifier terminal node."""
    name: str
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_identifier(self)

    def stringify(self) -> str:
        return self.name

    def pretty_print(self, indent: int = 0) -> str:
        return f"Identifier : {self.name}"

    def to_dict(self) -> dict:
        return {
            "type": "IdentifierNode",
            "name": self.name,
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }


@dataclass(frozen=True)
class GroupingNode(ExpressionNode):
    """Grouping context enclosing inner expressions inside parentheses (expr)."""
    expression: ExpressionNode
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_grouping(self)

    def stringify(self) -> str:
        return f"({self.expression.stringify()})"

    def pretty_print(self, indent: int = 0) -> str:
        lines = ["Grouping"]
        expr_lines = self.expression.pretty_print(indent + 1).splitlines()
        if expr_lines:
            lines.append("└── " + expr_lines[0])
            for line in expr_lines[1:]:
                lines.append("    " + line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "GroupingNode",
            "expression": self.expression.to_dict(),
            "position": {
                "filename": self.position.filename,
                "line": self.position.line,
                "column": self.position.column
            }
        }
