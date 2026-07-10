"""
SpeakCode Compiler - Static Semantic Analyzer
Validates the AST representation for logical rules (variable declarations, scopes,
function signature matches, type consistency, and return statements) before execution.

Dependencies:
    - speak_tokens.py (Position)
    - speak_ast.py (ASTNode and subclasses)
    - speak_errors.py (SpeakSemanticError, SpeakTypeError)
"""

from typing import List, Dict, Optional, Any, Union
from speak_tokens import Position
from speak_errors import SpeakSemanticError, SpeakTypeError, SpeakError
from speak_ast import (
    ASTNode, ProgramNode, RememberNode, ChangeNode, SpeakNode, AskNode,
    IfNode, OtherwiseIfNode, OtherwiseNode, WhileNode, RepeatNode,
    FunctionDeclarationNode, FunctionCallNode, ReturnNode,
    BinaryExpressionNode, UnaryExpressionNode, LiteralNode, IdentifierNode, GroupingNode
)


class FunctionSignature:
    """Stores metadata details about function headers (parameters list)."""
    
    def __init__(self, name: str, parameters: List[str], position: Position) -> None:
        self.name = name
        self.parameters = parameters
        self.position = position


class Scope:
    """
    Represents nested lexical scopes storing local variable types and function definitions.
    Implements parent-pointer scope resolution.
    """

    def __init__(self, parent: Optional['Scope'] = None) -> None:
        self.parent = parent
        self.variables: Dict[str, str] = {}  # Variable name -> Type string ("Number", "String", "Boolean", "Unknown")
        self.functions: Dict[str, FunctionSignature] = {}

    def define(self, name: str, var_type: str) -> None:
        """Binds a variable type in the current scope."""
        self.variables[name] = var_type

    def lookup(self, name: str) -> Optional[str]:
        """Resolves a variable type recursively up the scope chain."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def exists_locally(self, name: str) -> bool:
        """Checks if a variable is declared specifically in this scope."""
        return name in self.variables

    def define_function(self, name: str, sig: FunctionSignature) -> None:
        """Registers a function signature locally."""
        self.functions[name] = sig

    def lookup_function(self, name: str) -> Optional[FunctionSignature]:
        """Resolves a function signature recursively up the scope chain."""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.lookup_function(name)
        return None


class SpeakSemanticAnalyzer:
    """
    AST Semantic Analyzer implementing the AST Visitor Pattern interface.
    Validates logical correctness statically.
    """

    def __init__(self, source: str, filename: str = "<stdin>") -> None:
        self.source = source
        self.filename = filename
        self.errors: List[SpeakError] = []
        
        # Scope lifecycle tracking
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.is_inside_function = False
        self.scope_count = 1
        self.var_count = 0
        self.fun_count = 0

    def enter_scope(self) -> None:
        """Enters a new nested child scope context."""
        self.current_scope = Scope(self.current_scope)
        self.scope_count += 1

    def leave_scope(self) -> None:
        """Restores the parent scope context."""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def error(self, err: SpeakError) -> None:
        """Appends semantic violations without halting compiler passes."""
        self.errors.append(err)

    def analyze(self, node: ASTNode) -> None:
        """Top-level verification entry point."""
        self.errors.clear()
        self.visit(node)

    def visit(self, node: ASTNode) -> Any:
        """Routes visiting calls to node accept hooks."""
        return node.accept(self)

    # ----------------------------------------------------------------------
    # AST NODE VISITOR IMPLEMENTATION
    # ----------------------------------------------------------------------
    def visit_program(self, node: ProgramNode) -> None:
        # Pre-pass: Hoist function declarations globally
        for stmt in node.statements:
            if isinstance(stmt, FunctionDeclarationNode):
                if self.global_scope.lookup_function(stmt.name) is not None:
                    self.error(SpeakSemanticError(
                        error_code="SPK106",
                        message=f"Duplicate declaration of function name '{stmt.name}'.",
                        position=stmt.position,
                        source=self.source,
                        suggestion="Define function names uniquely."
                    ))
                else:
                    sig = FunctionSignature(stmt.name, stmt.parameters, stmt.position)
                    self.global_scope.define_function(stmt.name, sig)
                    self.fun_count += 1
                    
        # Main verification pass
        for stmt in node.statements:
            self.visit(stmt)

    def visit_remember(self, node: RememberNode) -> None:
        expr_type = self.visit(node.expression)
        
        # Check duplicate declaration in the active scope
        if self.current_scope.exists_locally(node.variable_name):
            self.error(SpeakSemanticError(
                error_code="SPK103",
                message=f"Variable '{node.variable_name}' is already defined in the current scope.",
                position=node.position,
                source=self.source,
                suggestion=f"Use a different name, or use 'Change {node.variable_name} to ...' to update its value instead of redefining it."
            ))
        else:
            self.current_scope.define(node.variable_name, expr_type)
            self.var_count += 1

    def visit_change(self, node: ChangeNode) -> None:
        expr_type = self.visit(node.expression)
        
        # Check variable exists in scope
        var_type = self.current_scope.lookup(node.variable_name)
        if var_type is None:
            self.error(SpeakSemanticError(
                error_code="SPK104",
                message=f"Variable '{node.variable_name}' is not defined. You must declare it first using Remember.",
                position=node.position,
                source=self.source,
                suggestion=f"Initialize the variable first using 'Remember <value> as {node.variable_name}.' before changing it."
            ))
        else:
            # Allow changes. In robust type checking, check if var_type matches expr_type.
            # But SpeakCode allows assignment variables updates since it's dynamically typed during runtime.
            pass

    def visit_speak(self, node: SpeakNode) -> None:
        self.visit(node.expression)

    def visit_ask(self, node: AskNode) -> None:
        if node.prompt_expr:
            self.visit(node.prompt_expr)
            
        # Register user variable locally if not already defined (automatic declaration support)
        if not self.current_scope.exists_locally(node.variable_name):
            self.current_scope.define(node.variable_name, "Unknown")
            self.var_count += 1

    def visit_otherwise_if(self, node: OtherwiseIfNode) -> None:
        cond_type = self.visit(node.condition)
        if cond_type not in ["Boolean", "Unknown"]:
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"Otherwise if conditional expression must evaluate to a boolean, but got type '{cond_type}'.",
                position=node.condition.position,
                source=self.source,
                suggestion="Modify conditional checks to simplify to true/false booleans."
            ))
            
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.leave_scope()

    def visit_otherwise(self, node: OtherwiseNode) -> None:
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.leave_scope()

    def visit_if(self, node: IfNode) -> None:
        cond_type = self.visit(node.condition)
        if cond_type not in ["Boolean", "Unknown"]:
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"If condition must evaluate to a boolean (true or false), but got type '{cond_type}'.",
                position=node.condition.position,
                source=self.source,
                suggestion="Ensure logical comparison is written. E.g. 'If x is above 10 then'."
            ))
            
        self.enter_scope()
        for stmt in node.then_branch:
            self.visit(stmt)
        self.leave_scope()
        
        for elif_node in node.otherwise_if_branches:
            self.visit(elif_node)
            
        if node.otherwise_branch:
            self.visit(node.otherwise_branch)

    def visit_while(self, node: WhileNode) -> None:
        cond_type = self.visit(node.condition)
        if cond_type not in ["Boolean", "Unknown"]:
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"While loop condition expression must evaluate to a boolean, but got type '{cond_type}'.",
                position=node.condition.position,
                source=self.source,
                suggestion="Use comparisons or boolean constants in loop checks."
            ))
            
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.leave_scope()

    def visit_repeat(self, node: RepeatNode) -> None:
        count_type = self.visit(node.count_expr)
        if count_type not in ["Number", "Unknown"]:
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"Repeat count loop expression must evaluate to a numeric value, but got type '{count_type}'.",
                position=node.count_expr.position,
                source=self.source,
                suggestion="Repeat loops require integer metrics. E.g. Repeat 5 times."
            ))
            
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.leave_scope()

    def visit_function_declaration(self, node: FunctionDeclarationNode) -> None:
        prev_inside = self.is_inside_function
        self.is_inside_function = True
        
        self.enter_scope()
        for param in node.parameters:
            self.current_scope.define(param, "Unknown")
            self.var_count += 1
            
        for stmt in node.body:
            self.visit(stmt)
            
        self.leave_scope()
        self.is_inside_function = prev_inside

    def visit_function_call(self, node: FunctionCallNode) -> None:
        sig = self.global_scope.lookup_function(node.name)
        if sig is None:
            self.error(SpeakSemanticError(
                error_code="SPK106",
                message=f"Function '{node.name}' has not been defined.",
                position=node.position,
                source=self.source,
                suggestion=f"Declare the function signature using: To perform {node.name}."
            ))
        else:
            if len(node.arguments) != len(sig.parameters):
                self.error(SpeakSemanticError(
                    error_code="SPK106",
                    message=f"Function '{node.name}' expects {len(sig.parameters)} parameter(s), but you provided {len(node.arguments)} argument(s).",
                    position=node.position,
                    source=self.source,
                    suggestion=f"Review the function definition and pass exactly {len(sig.parameters)} argument(s)."
                ))
                
        for arg in node.arguments:
            self.visit(arg)
            
        if node.save_variable:
            # Bind output locally if not registered
            if not self.current_scope.exists_locally(node.save_variable):
                self.current_scope.define(node.save_variable, "Unknown")
                self.var_count += 1

    def visit_return(self, node: ReturnNode) -> None:
        if not self.is_inside_function:
            self.error(SpeakSemanticError(
                error_code="SPK107",
                message="Return statement 'Give back' can only be used inside a performance definition block.",
                position=node.position,
                source=self.source,
                suggestion="Remove 'Give back' statement or wrap it inside To perform ... Finish performance."
            ))
        self.visit(node.expression)

    # ----------------------------------------------------------------------
    # EXPRESSIONS TYPE INFERENCE & VALIDATION
    # ----------------------------------------------------------------------
    def visit_binary_expression(self, node: BinaryExpressionNode) -> str:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.operator.lower()
        
        if op == "plus":
            # plus maps string concat (at least one string) or arithmetic addition (both numbers)
            if left_type == "String" or right_type == "String":
                return "String"
            if left_type == "Number" and right_type == "Number":
                return "Number"
            if left_type == "Unknown" or right_type == "Unknown":
                return "Unknown"
            
            # Mismatched addition types
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"Operator 'plus' cannot combine type '{left_type}' and '{right_type}'.",
                position=node.position,
                source=self.source,
                suggestion="Verify both expressions are numbers, or at least one is a string."
            ))
            return "Unknown"
            
        if op in ["minus", "times", "divided by", "modulo"]:
            if left_type in ["Number", "Unknown"] and right_type in ["Number", "Unknown"]:
                return "Number"
                
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"Operator '{op}' requires numeric operands, but got type '{left_type}' and '{right_type}'.",
                position=node.position,
                source=self.source,
                suggestion="Arithmetic operations require numeric values."
            ))
            return "Number"
            
        if op in ["and", "or"]:
            if left_type in ["Boolean", "Unknown"] and right_type in ["Boolean", "Unknown"]:
                return "Boolean"
                
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"Logical operator '{op}' requires boolean operands, but got type '{left_type}' and '{right_type}'.",
                position=node.position,
                source=self.source,
                suggestion="Combine logical conditions only."
            ))
            return "Boolean"
            
        if op in ["is same as", "is different from"]:
            return "Boolean"
            
        if op in ["is above", "is below", "is at least", "is at most"]:
            if left_type in ["Number", "Unknown"] and right_type in ["Number", "Unknown"]:
                return "Boolean"
                
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"Comparison operator '{op}' requires numeric values, but got type '{left_type}' and '{right_type}'.",
                position=node.position,
                source=self.source,
                suggestion="Compare numbers only."
            ))
            return "Boolean"
            
        return "Unknown"

    def visit_unary_expression(self, node: UnaryExpressionNode) -> str:
        expr_type = self.visit(node.expression)
        op = node.operator.lower()
        
        if op == "minus":
            if expr_type not in ["Number", "Unknown"]:
                self.error(SpeakTypeError(
                    error_code="SPK108",
                    message=f"Negation operator 'minus' requires a number, but got type '{expr_type}'.",
                    position=node.position,
                    source=self.source,
                    suggestion="Apply negative signs to numeric terms only."
                ))
            return "Number"
            
        if op == "opposite of":
            if expr_type not in ["Boolean", "Unknown"]:
                self.error(SpeakTypeError(
                    error_code="SPK108",
                    message=f"Logical negation 'opposite of' requires a boolean, but got type '{expr_type}'.",
                    position=node.position,
                    source=self.source,
                    suggestion="Apply opposite logic to booleans (true/false) only."
                ))
            return "Boolean"
            
        return "Unknown"

    def visit_literal(self, node: LiteralNode) -> str:
        val = node.value
        if isinstance(val, bool):
            return "Boolean"
        if isinstance(val, (int, float)):
            return "Number"
        if isinstance(val, str):
            return "String"
        return "Unknown"

    def visit_identifier(self, node: IdentifierNode) -> str:
        var_type = self.current_scope.lookup(node.name)
        if var_type is None:
            self.error(SpeakSemanticError(
                error_code="SPK104",
                message=f"Variable '{node.name}' has not been declared.",
                position=node.position,
                source=self.source,
                suggestion=f"Initialize the variable first using: Remember <value> as {node.name}."
            ))
            return "Unknown"
        return var_type

    def visit_grouping(self, node: GroupingNode) -> str:
        return self.visit(node.expression)
