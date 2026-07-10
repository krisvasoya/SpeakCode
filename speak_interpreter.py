"""
SpeakCode Compiler - Tree-Walking Interpreter
Executes the verified AST representation of a SpeakCode program.
Tracks nested lexical environments, function frames, console I/O, and catches SPK105 runtime errors.

Dependencies:
    - speak_tokens.py (Position)
    - speak_ast.py (ASTNode and subclasses)
    - speak_errors.py (SpeakRuntimeError)
"""

import sys
from typing import Any, Dict, List, Optional
from speak_tokens import Position
from speak_errors import SpeakRuntimeError
from speak_ast import (
    ASTNode, ProgramNode, RememberNode, ChangeNode, SpeakNode, AskNode,
    IfNode, OtherwiseIfNode, OtherwiseNode, WhileNode, RepeatNode,
    FunctionDeclarationNode, FunctionCallNode, ReturnNode,
    BinaryExpressionNode, UnaryExpressionNode, LiteralNode, IdentifierNode, GroupingNode
)


def to_speak_string(val: Any) -> str:
    """Converts a Python runtime value into SpeakCode printable representation."""
    if val is True:
        return "true"
    if val is False:
        return "false"
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
    return str(val)


def coerce_input(val_str: str) -> Any:
    """Coerces console string inputs into numeric or boolean types if applicable."""
    cleaned = val_str.strip()
    if cleaned.lower() == "true":
        return True
    if cleaned.lower() == "false":
        return False
        
    try:
        return int(cleaned)
    except ValueError:
        pass
        
    try:
        return float(cleaned)
    except ValueError:
        pass
        
    return val_str


class ReturnException(Exception):
    """Custom control-flow exception to propagate function returns back to callers."""
    def __init__(self, value: Any) -> None:
        self.value = value
        super().__init__()


class Environment:
    """Represents a runtime variable binding environment with lexical nesting pointer."""

    def __init__(self, parent: Optional['Environment'] = None) -> None:
        self.parent = parent
        self.values: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        """Declares a variable in the active scope."""
        self.values[name] = value

    def lookup(self, name: str) -> Any:
        """Resolves a variable value recursively up parent scopes."""
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.lookup(name)
        raise KeyError(f"Variable '{name}' is not defined.")

    def update(self, name: str, value: Any) -> None:
        """Updates a variable value recursively up parent scopes."""
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            self.parent.update(name, value)
            return
        raise KeyError(f"Variable '{name}' is not defined.")

    def exists(self, name: str) -> bool:
        """Checks if a variable exists anywhere in the active scope chain."""
        if name in self.values:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False


class SpeakInterpreter:
    """
    AST Interpreter walking the tree using the AST Visitor Pattern interface.
    Runs statements and resolves expression values.
    """

    def __init__(self, source: str, filename: str = "<stdin>", debug: bool = False, trace: bool = False) -> None:
        self.source = source
        self.filename = filename
        self.debug = debug
        self.trace = trace
        
        # Scopes and execution details
        self.globals = Environment()
        self.environment = self.globals
        self.declared_functions: Dict[str, FunctionDeclarationNode] = {}
        self.scope_count = 1

    def error(self, message: str, position: Position, suggestion: Optional[str] = None) -> SpeakRuntimeError:
        """Creates a Position-tracked SpeakRuntimeError (SPK105)."""
        return SpeakRuntimeError("SPK105", message, position, self.source, suggestion)

    def evaluate(self, node: ASTNode) -> Any:
        """Helper to run expression nodes."""
        return node.accept(self)

    def execute(self, node: ASTNode) -> None:
        """Helper to run statement nodes."""
        node.accept(self)

    def interpret(self, program: ProgramNode) -> None:
        """Executes the complete SpeakCode Program Node."""
        try:
            # Pre-pass: Hoist global function declarations
            for stmt in program.statements:
                if isinstance(stmt, FunctionDeclarationNode):
                    self.declared_functions[stmt.name] = stmt
                    
            for stmt in program.statements:
                if not isinstance(stmt, FunctionDeclarationNode):
                    self.execute(stmt)
        except SpeakRuntimeError:
            raise
        except Exception as e:
            raise SpeakRuntimeError(
                error_code="SPK999",
                message=f"Internal Interpreter execution crash: {str(e)}",
                position=program.position,
                source=self.source
            )

    # ----------------------------------------------------------------------
    # VISITOR PATTERN IMPLEMENTATION
    # ----------------------------------------------------------------------
    def visit_program(self, node: ProgramNode) -> None:
        for stmt in node.statements:
            self.execute(stmt)

    def visit_remember(self, node: RememberNode) -> None:
        val = self.evaluate(node.expression)
        self.environment.define(node.variable_name, val)
        
        if self.trace:
            print(f"[Trace] Remember variable: {node.variable_name} = {repr(val)}")

    def visit_change(self, node: ChangeNode) -> None:
        val = self.evaluate(node.expression)
        self.environment.update(node.variable_name, val)
        
        if self.trace:
            print(f"[Trace] Change variable: {node.variable_name} to {repr(val)}")

    def visit_speak(self, node: SpeakNode) -> None:
        val = self.evaluate(node.expression)
        
        # Easter Egg
        if isinstance(val, str) and val.strip().lower().rstrip('?').rstrip('.') == "who made you":
            print("SpeakCode\nCreated by Krish Vasoya\n2026")
        else:
            print(to_speak_string(val))
            
        if self.trace:
            print(f"[Trace] Speak output: {repr(val)}")

    def visit_ask(self, node: AskNode) -> None:
        prompt_str = "> "
        if node.prompt_expr:
            prompt_val = self.evaluate(node.prompt_expr)
            prompt_str = to_speak_string(prompt_val)
            
        try:
            user_raw = input(prompt_str)
        except (KeyboardInterrupt, EOFError):
            print()
            user_raw = ""
            
        coerced = coerce_input(user_raw)
        
        if self.environment.exists(node.variable_name):
            self.environment.update(node.variable_name, coerced)
        else:
            self.environment.define(node.variable_name, coerced)
            
        if self.trace:
            print(f"[Trace] Ask input: {node.variable_name} = {repr(coerced)}")

    def visit_otherwise_if(self, node: OtherwiseIfNode) -> None:
        # Execution of this is routed via IfNode branches
        for stmt in node.body:
            self.execute(stmt)

    def visit_otherwise(self, node: OtherwiseNode) -> None:
        # Execution of this is routed via IfNode branches
        for stmt in node.body:
            self.execute(stmt)

    def visit_if(self, node: IfNode) -> None:
        cond_val = self.evaluate(node.condition)
        
        executed = False
        if cond_val:
            prev_env = self.environment
            self.environment = Environment(prev_env)
            self.scope_count += 1
            try:
                for stmt in node.then_branch:
                    self.execute(stmt)
            finally:
                self.environment = prev_env
            executed = True
        else:
            for elif_branch in node.otherwise_if_branches:
                elif_cond = self.evaluate(elif_branch.condition)
                if elif_cond:
                    prev_env = self.environment
                    self.environment = Environment(prev_env)
                    self.scope_count += 1
                    try:
                        self.execute(elif_branch)
                    finally:
                        self.environment = prev_env
                    executed = True
                    break
                    
        if not executed and node.otherwise_branch:
            prev_env = self.environment
            self.environment = Environment(prev_env)
            self.scope_count += 1
            try:
                self.execute(node.otherwise_branch)
            finally:
                self.environment = prev_env

    def visit_while(self, node: WhileNode) -> None:
        while True:
            cond_val = self.evaluate(node.condition)
            if not cond_val:
                break
                
            prev_env = self.environment
            self.environment = Environment(prev_env)
            self.scope_count += 1
            try:
                for stmt in node.body:
                    self.execute(stmt)
            finally:
                self.environment = prev_env

    def visit_repeat(self, node: RepeatNode) -> None:
        times_val = self.evaluate(node.count_expr)
        if not isinstance(times_val, int):
            raise self.error(
                message=f"Repeat loop count must evaluate to an integer, but got: {repr(times_val)}",
                position=node.count_expr.position,
                suggestion="Specify a valid integer count metrics."
            )
        if times_val < 0:
            raise self.error(
                message=f"Repeat count cannot be negative: {times_val}",
                position=node.count_expr.position,
                suggestion="Verify the count parameters simplify to a positive integer or zero."
            )
            
        for _ in range(times_val):
            prev_env = self.environment
            self.environment = Environment(prev_env)
            self.scope_count += 1
            try:
                for stmt in node.body:
                    self.execute(stmt)
            finally:
                self.environment = prev_env

    def visit_function_declaration(self, node: FunctionDeclarationNode) -> None:
        # Signatures hoisted globally, do nothing inside run-order traversal
        pass

    def visit_function_call(self, node: FunctionCallNode) -> Any:
        decl = self.declared_functions[node.name]
        arg_vals = [self.evaluate(arg) for arg in node.arguments]
        
        # Enter function environment (inherits from globals to keep lexical scoping rules)
        fun_env = Environment(self.globals)
        self.scope_count += 1
        
        for param, val in zip(decl.parameters, arg_vals):
            fun_env.define(param, val)
            
        if self.debug:
            print(f"[Debug] ENTER FUNCTION: {node.name}")
            print(f"[Debug] Arguments: " + ", ".join(f"{k}={repr(v)}" for k, v in zip(decl.parameters, arg_vals)))
            
        prev_env = self.environment
        self.environment = fun_env
        returned_val = None
        
        try:
            for stmt in decl.body:
                self.execute(stmt)
        except ReturnException as ret:
            returned_val = ret.value
        finally:
            self.environment = prev_env
            
        if self.debug:
            print(f"[Debug] RETURN from {node.name}: {repr(returned_val)}")
            
        if node.save_variable:
            self.environment.define(node.save_variable, returned_val)
            
        return returned_val

    def visit_return(self, node: ReturnNode) -> None:
        val = self.evaluate(node.expression)
        raise ReturnException(val)

    # ----------------------------------------------------------------------
    # EXPRESSION VISITING & ARITHMETIC LOGIC
    # ----------------------------------------------------------------------
    def visit_binary_expression(self, node: BinaryExpressionNode) -> Any:
        op = node.operator.lower()
        
        # Short-circuit logical checks
        if op == "and":
            left_val = self.evaluate(node.left)
            if not left_val:
                return False
            return self.evaluate(node.right)
            
        if op == "or":
            left_val = self.evaluate(node.left)
            if left_val:
                return True
            return self.evaluate(node.right)
            
        left_val = self.evaluate(node.left)
        right_val = self.evaluate(node.right)
        
        if op == "plus":
            if isinstance(left_val, str) or isinstance(right_val, str):
                return to_speak_string(left_val) + to_speak_string(right_val)
            return left_val + right_val
            
        if op == "minus":
            return left_val - right_val
        if op == "times":
            return left_val * right_val
            
        if op == "divided by":
            if right_val == 0:
                raise self.error("Division by zero error.", node.right.position, "Adjust divisor expression to be non-zero.")
            return left_val / right_val
            
        if op == "modulo":
            if right_val == 0:
                raise self.error("Modulo by zero error.", node.right.position, "Adjust divisor expression to be non-zero.")
            return left_val % right_val
            
        if op == "is same as":
            return left_val == right_val
        if op == "is different from":
            return left_val != right_val
            
        if op == "is above":
            return left_val > right_val
        if op == "is below":
            return left_val < right_val
        if op == "is at least":
            return left_val >= right_val
        if op == "is at most":
            return left_val <= right_val
            
        raise RuntimeError(f"Unknown binary operator logic: {op}")

    def visit_unary_expression(self, node: UnaryExpressionNode) -> Any:
        val = self.evaluate(node.expression)
        op = node.operator.lower()
        
        if op == "minus":
            return -val
        if op == "opposite of":
            return not val
            
        raise RuntimeError(f"Unknown unary operator logic: {op}")

    def visit_literal(self, node: LiteralNode) -> Any:
        return node.value

    def visit_identifier(self, node: IdentifierNode) -> Any:
        return self.environment.lookup(node.name)

    def visit_grouping(self, node: GroupingNode) -> Any:
        return self.evaluate(node.expression)
