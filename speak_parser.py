"""
SpeakCode Compiler - Syntactic Analyzer (Parser)
Converts a linear position-tracked token stream into an Abstract Syntax Tree (AST).
Provides syntax error collecting (SPK102), panic-mode recovery, and optional parse traces.

Dependencies:
    - speak_tokens.py (Token, TokenType, Position)
    - speak_ast.py (ASTNode subclasses)
    - speak_errors.py (SpeakSyntaxError)
"""

from typing import List, Optional, Tuple, Any
from speak_tokens import Token, TokenType, Position
from speak_errors import SpeakSyntaxError
from speak_ast import (
    ASTNode, StatementNode, ExpressionNode, ProgramNode, RememberNode, ChangeNode, SpeakNode, AskNode,
    IfNode, OtherwiseIfNode, OtherwiseNode, WhileNode, RepeatNode, FunctionDeclarationNode, FunctionCallNode,
    ReturnNode, BinaryExpressionNode, UnaryExpressionNode, LiteralNode, IdentifierNode, GroupingNode
)


class SpeakParser:
    """
    Syntactic analyzer for SpeakCode.
    Implements top-down recursive descent parsing with syntactic error synchronization.
    """

    def __init__(self, tokens: List[Token], source: str, filename: str = "<stdin>", debug: bool = False) -> None:
        """
        Initializes the parser state.

        Args:
            tokens: Scanned token stream from Lexer.
            source: Raw string content of the source code.
            filename: Source path name.
            debug: If True, prints parsing path calls.
        """
        self.tokens = tokens
        self.source = source
        self.filename = filename
        self.debug = debug
        self.pos = 0
        self.errors: List[SpeakSyntaxError] = []

    # ----------------------------------------------------------------------
    # SCANNER POINTER NAVIGATION METHODS
    # ----------------------------------------------------------------------
    def peek(self) -> Token:
        """Looks at the active token without advancing."""
        return self.tokens[self.pos]

    def previous(self) -> Token:
        """Looks at the consumed token immediately behind the cursor."""
        return self.tokens[self.pos - 1]

    def is_at_end(self) -> bool:
        """Checks if parser has hit the EOF boundary."""
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        """Consumes the active token and advances pointer."""
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        """Checks if active token matches a given type."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def match(self, token_types: List[TokenType]) -> bool:
        """Advances pointer if active token matches any of the types."""
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, error_message: str, suggestion: str) -> Token:
        """
        Consumes active token if type matches.
        Otherwise raises a SpeakSyntaxError.
        """
        if self.check(token_type):
            return self.advance()
        raise self.error(error_message, self.peek(), suggestion)

    def error(self, message: str, token: Token, suggestion: str) -> SpeakSyntaxError:
        """Creates a Position-tracked SpeakSyntaxError exception."""
        return SpeakSyntaxError(message, token.position, self.source, suggestion)

    def synchronize(self) -> None:
        """
        Panic-mode syntax error recovery sequence.
        Advances token index until a safe statement partition boundary is found.
        """
        if self.debug:
            print("[Parser Debug] Entering synchronize()")
            
        if self.check(TokenType.PERIOD):
            self.advance()
            return
            
        while not self.is_at_end():
            if self.previous().type == TokenType.PERIOD:
                return
                
            if self.peek().type in [
                TokenType.REMEMBER,
                TokenType.CHANGE,
                TokenType.SPEAK,
                TokenType.ASK,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.REPEAT,
                TokenType.TO_PERFORM,
                TokenType.PERFORM,
                TokenType.GIVE_BACK,
                TokenType.FINISH_CHECKING,
                TokenType.FINISH_LOOPING,
                TokenType.FINISH_PERFORMANCE,
                TokenType.EOF
            ]:
                return
                
            self.advance()

    # ----------------------------------------------------------------------
    # RECURSIVE DESCENT GRAMMAR PRODUCTIONS
    # ----------------------------------------------------------------------
    def parse(self) -> ProgramNode:
        """
        Parses program statements from start to EOF.
        Does not crash on syntax errors; accumulates them in self.errors.
        """
        if self.debug:
            print("[Parser Debug] Entering parse_program()")
            
        statements: List[StatementNode] = []
        start_pos = self.peek().position
        
        while not self.is_at_end():
            try:
                curr_pos = self.pos
                # Cast the returned statement to StatementNode
                stmt = self.statement()
                if isinstance(stmt, StatementNode):
                    statements.append(stmt)
            except SpeakSyntaxError as e:
                self.errors.append(e)
                self.synchronize()
                if self.pos == curr_pos and not self.is_at_end():
                    self.advance()
                
        if self.debug:
            print(f"[Parser Debug] Leaving parse_program() with {len(self.errors)} errors.")
            
        return ProgramNode(statements, start_pos)

    def statement(self) -> ASTNode:
        """Dispatches to specific statement grammar parsers."""
        if self.debug:
            print(f"[Parser Debug] Entering parse_statement() [Token: {self.peek()}]")
            
        try:
            if self.match([TokenType.REMEMBER]):
                return self.remember_statement()
            if self.match([TokenType.CHANGE]):
                return self.change_statement()
            if self.match([TokenType.SPEAK]):
                return self.speak_statement()
            if self.match([TokenType.ASK]):
                return self.ask_statement()
            if self.match([TokenType.IF]):
                return self.if_statement()
            if self.match([TokenType.WHILE]):
                return self.while_statement()
            if self.match([TokenType.REPEAT]):
                return self.repeat_statement()
            if self.match([TokenType.TO_PERFORM]):
                return self.fun_decl_statement()
            if self.match([TokenType.GIVE_BACK]):
                return self.return_statement()
            if self.match([TokenType.PERFORM]):
                return self.fun_call_statement()
                
            bad_tok = self.peek()
            raise self.error(
                message=f"Expected a statement starter instruction, but found '{bad_tok.value}'.",
                token=bad_tok,
                suggestion="Begin statement with a capitalized keyword (Remember, Change, Speak, Ask, If, While, Repeat, To perform, Perform, Give back)."
            )
        finally:
            if self.debug:
                print(f"[Parser Debug] Leaving parse_statement()")

    def remember_statement(self) -> RememberNode:
        """Parses: Remember <expr> as <ident>."""
        if self.debug:
            print("[Parser Debug] Entering remember_statement()")
            
        start_tok = self.previous()
        expr = self.expression()
        
        self.consume(TokenType.AS, "Expected keyword 'as' after expression in 'Remember' statement.",
                     "Use keyword 'as' to bind the value to a variable, e.g. Remember 10 as x.")
        
        ident_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name identifier.",
                                 "Specify a unique variable name to register.")
        
        self.consume(TokenType.PERIOD, "Expected period '.' at end of 'Remember' statement.",
                     "All statements must end with a terminating period character '.'")
                     
        return RememberNode(ident_tok.value, expr, start_tok.position)

    def change_statement(self) -> ChangeNode:
        """Parses: Change <ident> to <expr>."""
        if self.debug:
            print("[Parser Debug] Entering change_statement()")
            
        start_tok = self.previous()
        ident_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name identifier after 'Change'.",
                                 "Specify the name of the variable you want to update.")
        
        self.consume(TokenType.TO, "Expected keyword 'to' after variable identifier.",
                     "Use the 'to' keyword to introduce the update expression, e.g. Change x to 5.")
                     
        expr = self.expression()
        
        self.consume(TokenType.PERIOD, "Expected period '.' at end of 'Change' statement.",
                     "All statements must end with a terminating period character '.'")
                     
        return ChangeNode(ident_tok.value, expr, start_tok.position)

    def speak_statement(self) -> SpeakNode:
        """Parses: Speak <expr>."""
        if self.debug:
            print("[Parser Debug] Entering speak_statement()")
            
        start_tok = self.previous()
        expr = self.expression()
        
        self.consume(TokenType.PERIOD, "Expected period '.' at end of 'Speak' statement.",
                     "All statements must end with a terminating period character '.'")
                     
        return SpeakNode(expr, start_tok.position)

    def ask_statement(self) -> AskNode:
        """Parses: Ask (expr)? and save as <ident>."""
        if self.debug:
            print("[Parser Debug] Entering ask_statement()")
            
        start_tok = self.previous()
        prompt_expr: Optional[ExpressionNode] = None
        
        # Check prompt existence before key phrase
        if not self.check(TokenType.AND_SAVE_AS):
            prompt_expr = self.expression()
            
        self.consume(TokenType.AND_SAVE_AS, "Expected 'and save as' instruction phrase in 'Ask' statement.",
                     "Provide prompt text followed by 'and save as <variable>.' to hold user input.")
                     
        ident_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name identifier.",
                                 "Specify variable name to bind the input value to.")
                                 
        self.consume(TokenType.PERIOD, "Expected period '.' at end of 'Ask' statement.",
                     "All statements must end with a terminating period character '.'")
                     
        return AskNode(prompt_expr, ident_tok.value, start_tok.position)

    def parse_body(self, end_tokens: List[TokenType]) -> List[StatementNode]:
        """Parses nested statement lists until checking block closure boundaries."""
        body: List[StatementNode] = []
        while not self.is_at_end() and self.peek().type not in end_tokens:
            try:
                stmt = self.statement()
                if isinstance(stmt, StatementNode):
                    body.append(stmt)
            except SpeakSyntaxError as e:
                self.errors.append(e)
                self.synchronize()
                
        if self.is_at_end():
            ends_str = " or ".join(t.name.replace('_', ' ').capitalize() for t in end_tokens)
            raise self.error(
                message=f"Unexpected End-of-File reached. Expected block closure: '{ends_str}'.",
                token=self.peek(),
                suggestion=f"Close your block using matching words: {ends_str}."
            )
        return body

    def if_statement(self) -> IfNode:
        """Parses: If <expr> then ... (Otherwise if)? (Otherwise)? Finish checking."""
        if self.debug:
            print("[Parser Debug] Entering if_statement()")
            
        start_tok = self.previous()
        condition = self.expression()
        
        self.consume(TokenType.THEN, "Expected keyword 'then' after conditional expression.",
                     "Use the 'then' keyword to begin the conditional block.")
                     
        then_branch = self.parse_body([TokenType.OTHERWISE_IF, TokenType.OTHERWISE, TokenType.FINISH_CHECKING])
        
        otherwise_if_branches: List[OtherwiseIfNode] = []
        while self.match([TokenType.OTHERWISE_IF]):
            elif_pos = self.previous().position
            elif_cond = self.expression()
            self.consume(TokenType.THEN, "Expected keyword 'then' after otherwise if condition.",
                         "Use the keyword 'then' to begin the otherwise if block.")
            elif_body = self.parse_body([TokenType.OTHERWISE_IF, TokenType.OTHERWISE, TokenType.FINISH_CHECKING])
            otherwise_if_branches.append(OtherwiseIfNode(elif_cond, elif_body, elif_pos))
            
        otherwise_branch: Optional[OtherwiseNode] = None
        if self.match([TokenType.OTHERWISE]):
            else_pos = self.previous().position
            else_body = self.parse_body([TokenType.FINISH_CHECKING])
            otherwise_branch = OtherwiseNode(else_body, else_pos)
            
        self.consume(TokenType.FINISH_CHECKING, "Expected block closure phrase 'Finish checking'.",
                     "Every conditional block must end with 'Finish checking.'.")
        self.consume(TokenType.PERIOD, "Expected period '.' after 'Finish checking'.",
                     "All statements must end with a terminating period character '.'")
                     
        return IfNode(condition, then_branch, otherwise_if_branches, otherwise_branch, start_tok.position)

    def while_statement(self) -> WhileNode:
        """Parses: While <expr> repeat ... Finish looping."""
        if self.debug:
            print("[Parser Debug] Entering while_statement()")
            
        start_tok = self.previous()
        condition = self.expression()
        
        self.consume(TokenType.REPEAT, "Expected loop keyword 'repeat' after loop condition.",
                     "Use the 'repeat' keyword to begin the loop statement body.")
                     
        body = self.parse_body([TokenType.FINISH_LOOPING])
        
        self.consume(TokenType.FINISH_LOOPING, "Expected loop closure phrase 'Finish looping'.",
                     "Every loop block must end with 'Finish looping.'.")
        self.consume(TokenType.PERIOD, "Expected period '.' after 'Finish looping'.",
                     "All statements must end with a terminating period character '.'")
                     
        return WhileNode(condition, body, start_tok.position)

    def repeat_statement(self) -> RepeatNode:
        """Parses: Repeat <expr> times ... Finish looping."""
        if self.debug:
            print("[Parser Debug] Entering repeat_statement()")
            
        start_tok = self.previous()
        count_expr = self.unary()
        
        self.consume(TokenType.TIMES, "Expected loop keyword 'times' after count expression.",
                     "Use the 'times' keyword to begin the loop statement body.")
                     
        body = self.parse_body([TokenType.FINISH_LOOPING])
        
        self.consume(TokenType.FINISH_LOOPING, "Expected loop closure phrase 'Finish looping'.",
                     "Every loop block must end with 'Finish looping.'.")
        self.consume(TokenType.PERIOD, "Expected period '.' after 'Finish looping'.",
                     "All statements must end with a terminating period character '.'")
                     
        return RepeatNode(count_expr, body, start_tok.position)

    def fun_decl_statement(self) -> FunctionDeclarationNode:
        """Parses: To perform <name> (with a and b)?: ... Finish performance."""
        if self.debug:
            print("[Parser Debug] Entering fun_decl_statement()")
            
        start_tok = self.previous()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expected function name identifier after 'To perform'.",
                                "Specify the name of the function to declare.")
        params: List[str] = []
        
        if self.match([TokenType.WITH]):
            loop = True
            while loop:
                p_tok = self.consume(TokenType.IDENTIFIER, "Expected parameter variable name.",
                                     "Provide parameter names separated by 'and'.")
                params.append(p_tok.value)
                if self.match([TokenType.AND]):
                    continue
                else:
                    loop = False
                    
        self.consume(TokenType.COLON, "Expected colon ':' to close function header signature line.",
                     "All function signatures must end with a colon character ':'.")
                     
        body = self.parse_body([TokenType.FINISH_PERFORMANCE])
        
        self.consume(TokenType.FINISH_PERFORMANCE, "Expected function block closure 'Finish performance'.",
                     "Every function definition block must end with 'Finish performance.'.")
        self.consume(TokenType.PERIOD, "Expected period '.' after 'Finish performance'.",
                     "All statements must end with a terminating period character '.'")
                     
        return FunctionDeclarationNode(name_tok.value, params, body, start_tok.position)

    def return_statement(self) -> ReturnNode:
        """Parses: Give back <expr>."""
        if self.debug:
            print("[Parser Debug] Entering return_statement()")
            
        start_tok = self.previous()
        expr = self.expression()
        
        self.consume(TokenType.PERIOD, "Expected period '.' at end of 'Give back' statement.",
                     "All statements must end with a terminating period character '.'")
                     
        return ReturnNode(expr, start_tok.position)

    def fun_call_statement(self) -> FunctionCallNode:
        """Parses: Perform <name> (with args)? (and save as x)?"""
        if self.debug:
            print("[Parser Debug] Entering fun_call_statement()")
            
        start_tok = self.previous()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expected function name after 'Perform'.",
                                "Provide the name of the function to call.")
        args: List[ExpressionNode] = []
        
        if self.match([TokenType.WITH]):
            loop = True
            while loop:
                arg_expr = self.logical_not()  # Parse at logical_not to prevent AND separator collision
                if isinstance(arg_expr, ExpressionNode):
                    args.append(arg_expr)
                if self.match([TokenType.AND]):
                    continue
                else:
                    loop = False
                    
        save_var: Optional[str] = None
        if self.match([TokenType.AND_SAVE_AS]):
            s_tok = self.consume(TokenType.IDENTIFIER, "Expected variable name to save returned value to.",
                                 "Provide a variable name to store the call result.")
            save_var = s_tok.value
            
        self.consume(TokenType.PERIOD, "Expected period '.' at end of 'Perform' statement.",
                     "All statements must end with a terminating period character '.'")
                     
        return FunctionCallNode(name_tok.value, args, save_var, start_tok.position)

    # ----------------------------------------------------------------------
    # EXPRESSIONS PARSING (Operator Precedence Hierarchy)
    # ----------------------------------------------------------------------
    def expression(self) -> ExpressionNode:
        """Highest priority parser method - matches expressions."""
        expr = self.logical_or()
        # Cast explicitly to satisfy typing
        assert isinstance(expr, ExpressionNode)
        return expr

    def logical_or(self) -> ExpressionNode:
        """Parses Logical OR precedence level ('or')."""
        node = self.logical_and()
        while self.match([TokenType.OR]):
            op_tok = self.previous()
            right = self.logical_and()
            node = BinaryExpressionNode(node, op_tok.value, right, op_tok.position)
        return node

    def logical_and(self) -> ExpressionNode:
        """Parses Logical AND precedence level ('and')."""
        node = self.logical_not()
        while self.match([TokenType.AND]):
            op_tok = self.previous()
            right = self.logical_not()
            node = BinaryExpressionNode(node, op_tok.value, right, op_tok.position)
        return node

    def logical_not(self) -> ExpressionNode:
        """Parses Unary logical negation precedence level ('opposite of')."""
        if self.match([TokenType.OPPOSITE_OF]):
            op_tok = self.previous()
            expr = self.logical_not()
            return UnaryExpressionNode(op_tok.value, expr, op_tok.position)
        return self.comparison()

    def comparison(self) -> ExpressionNode:
        """Parses Comparison relational operators (is same as, is above, etc.)."""
        node = self.additive()
        if self.match([
            TokenType.IS_SAME_AS, TokenType.IS_DIFFERENT_FROM, TokenType.IS_ABOVE,
            TokenType.IS_BELOW, TokenType.IS_GTE, TokenType.IS_LTE
        ]):
            op_tok = self.previous()
            right = self.additive()
            node = BinaryExpressionNode(node, op_tok.value, right, op_tok.position)
        return node

    def additive(self) -> ExpressionNode:
        """Parses Additive precedence level ('plus', 'minus')."""
        node = self.multiplicative()
        while self.match([TokenType.PLUS, TokenType.MINUS]):
            op_tok = self.previous()
            right = self.multiplicative()
            node = BinaryExpressionNode(node, op_tok.value, right, op_tok.position)
        return node

    def multiplicative(self) -> ExpressionNode:
        """Parses Multiplicative precedence level ('times', 'divided by', 'modulo')."""
        node = self.unary()
        while self.match([TokenType.TIMES, TokenType.DIVIDED_BY, TokenType.MODULO]):
            op_tok = self.previous()
            right = self.unary()
            node = BinaryExpressionNode(node, op_tok.value, right, op_tok.position)
        return node

    def unary(self) -> ExpressionNode:
        """Parses Unary arithmetic negation precedence level ('minus')."""
        if self.match([TokenType.MINUS]):
            op_tok = self.previous()
            expr = self.unary()
            return UnaryExpressionNode(op_tok.value, expr, op_tok.position)
        return self.primary()

    def primary(self) -> ExpressionNode:
        """Lowest priority level - parses primary terms."""
        if self.match([TokenType.NUMBER]):
            tok = self.previous()
            val = float(tok.value) if '.' in tok.value else int(tok.value)
            return LiteralNode(val, tok.position)
            
        if self.match([TokenType.STRING]):
            tok = self.previous()
            return LiteralNode(tok.value, tok.position)
            
        if self.match([TokenType.TRUE]):
            return LiteralNode(True, self.previous().position)
            
        if self.match([TokenType.FALSE]):
            return LiteralNode(False, self.previous().position)
            
        if self.match([TokenType.IDENTIFIER]):
            tok = self.previous()
            return IdentifierNode(tok.value, tok.position)
            
        if self.match([TokenType.LPAREN]):
            start_tok = self.previous()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected closing parenthesis ')' after group expression.",
                         "Close your grouping expression with a matching right parenthesis ')'.")
            return GroupingNode(expr, start_tok.position)
            
        bad_tok = self.peek()
        if bad_tok.type == TokenType.EOF:
            raise self.error(
                message="Unexpected End-of-File reached. Expected value expression.",
                token=bad_tok,
                suggestion="Provide a valid number, string, boolean constant, variable name, or parenthesized sub-expression."
            )
        raise self.error(
            message=f"Expected value expression, but found '{bad_tok.value}'.",
            token=bad_tok,
            suggestion="Provide a valid number, string, boolean constant, variable name, or parenthesized sub-expression."
        )
