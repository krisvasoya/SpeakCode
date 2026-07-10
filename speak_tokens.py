"""
SpeakCode Compiler - Tokenization and Positioning System
Provides the Position tracking context, token types enumeration, and Token records.
This module defines the foundational grammar terminals and coordinates of compiler stages.

Dependencies:
    - dataclasses (Standard Library)
"""

from dataclasses import dataclass
from enum import Enum, unique


@dataclass(frozen=True)
class Position:
    """
    Tracks the source code coordinates of compiler items (Tokens and Errors).
    This class is immutable, making it safe for hoisting across multiple parser stages.
    """
    filename: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Position({repr(self.filename)}, line={self.line}, col={self.column})"

    def __str__(self) -> str:
        return f"File '{self.filename}', line {self.line}, column {self.column}"


@unique
class TokenType(Enum):
    """
    Enumeration of all valid lexical token categories inside SpeakCode.
    Structured into semantic groups for clarity and easy maintenance.
    """
    # ----------------------------------------------------
    # SECTION 1: CAPITALIZED STATEMENT & BLOCK STARTERS
    # ----------------------------------------------------
    REMEMBER = 'REMEMBER'                  # Variable declarations ('Remember')
    CHANGE = 'CHANGE'                      # Variable updates ('Change')
    SPEAK = 'SPEAK'                        # Standard stdout printing ('Speak')
    ASK = 'ASK'                            # Standard stdin querying ('Ask')
    IF = 'IF'                              # Conditional starter ('If')
    OTHERWISE_IF = 'OTHERWISE_IF'          # Else-if condition starter ('Otherwise if')
    OTHERWISE = 'OTHERWISE'                # Else fallback starter ('Otherwise')
    WHILE = 'WHILE'                        # Loop starter ('While')
    REPEAT = 'REPEAT'                      # Count loop starter ('Repeat')
    TO_PERFORM = 'TO_PERFORM'              # Function declaration ('To perform')
    PERFORM = 'PERFORM'                    # Function call ('Perform')
    GIVE_BACK = 'GIVE_BACK'                # Return statement ('Give back')
    FINISH_CHECKING = 'FINISH_CHECKING'    # Conditional block end ('Finish checking')
    FINISH_LOOPING = 'FINISH_LOOPING'      # Loop block end ('Finish looping')
    FINISH_PERFORMANCE = 'FINISH_PERFORMANCE' # Function block end ('Finish performance')

    # ----------------------------------------------------
    # SECTION 2: INNER STATEMENT STRUCTURE HELPERS
    # ----------------------------------------------------
    AS = 'AS'                              # Binding operator ('as')
    TO = 'TO'                              # Target identifier ('to')
    THEN = 'THEN'                          # Body block starter ('then')
    TIMES = 'TIMES'                        # Repeat loops counter marker ('times')
    WITH = 'WITH'                          # Parameters list header ('with')
    AND = 'AND'                            # Logical AND / Parameter separator ('and')
    OR = 'OR'                              # Logical OR ('or')
    AND_SAVE_AS = 'AND_SAVE_AS'            # Output return assignment ('and save as')

    # ----------------------------------------------------
    # SECTION 3: ARITHMETIC & LOGICAL OPERATORS
    # ----------------------------------------------------
    PLUS = 'PLUS'                          # Addition or Concatenation ('plus')
    MINUS = 'MINUS'                        # Subtraction or Negation ('minus')
    DIVIDED_BY = 'DIVIDED_BY'              # Arithmetic division ('divided by')
    MODULO = 'MODULO'                      # Arithmetic remainder ('modulo')
    OPPOSITE_OF = 'OPPOSITE_OF'            # Logical negation ('opposite of')

    # ----------------------------------------------------
    # SECTION 4: COMPARISON OPERATORS
    # ----------------------------------------------------
    IS_SAME_AS = 'IS_SAME_AS'              # Equality ('is same as')
    IS_DIFFERENT_FROM = 'IS_DIFFERENT_FROM' # Inequality ('is different from')
    IS_ABOVE = 'IS_ABOVE'                  # Greater than ('is above')
    IS_BELOW = 'IS_BELOW'                  # Less than ('is below')
    IS_GTE = 'IS_GTE'                      # Greater than or equal to ('is at least')
    IS_LTE = 'IS_LTE'                      # Less than or equal to ('is at most')

    # ----------------------------------------------------
    # SECTION 5: LITERAL VALUES & VARIABLE IDENTIFIERS
    # ----------------------------------------------------
    TRUE = 'TRUE'                          # Boolean true constant ('true')
    FALSE = 'FALSE'                        # Boolean false constant ('false')
    NUMBER = 'NUMBER'                      # Integers/Decimal floating point strings
    STRING = 'STRING'                      # Text data (wrapped in double quotes)
    IDENTIFIER = 'IDENTIFIER'              # Variable or performance names

    # ----------------------------------------------------
    # SECTION 6: DELIMITERS & PUNCTUATION
    # ----------------------------------------------------
    PERIOD = 'PERIOD'                      # Sentence final indicator ('.')
    COLON = 'COLON'                        # Block header closure (':')
    LPAREN = 'LPAREN'                      # Precedence group starter ('(')
    RPAREN = 'RPAREN'                      # Precedence group closure (')')
    
    # ----------------------------------------------------
    # SECTION 7: SPECIAL UTILITY TERMINALS
    # ----------------------------------------------------
    EOF = 'EOF'                            # End-of-file parser boundary


@dataclass(frozen=True)
class Token:
    """
    Immutable Token metadata block.
    Stores TokenType, original string value, and position details.
    """
    type: TokenType
    value: str
    position: Position

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, pos={self.position})"

    def __str__(self) -> str:
        return f"Token[{self.type.name}]: '{self.value}' ({self.position})"
