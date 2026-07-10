"""
SpeakCode Compiler - Lexical Analyzer (Scanner)
Converts SpeakCode raw source code strings into a clean list of position-tracked Tokens.
Supports multi-word keywords, UTF-8 strings, escape sequences, and debug statistics.
"""

from typing import List, Dict
from speak_tokens import TokenType, Token, Position
from speak_errors import SpeakLexerError

# Sorted list of keywords from longest to shortest to ensure correct prefix matching
KEYWORDS_MAP = [
    ("finish checking", TokenType.FINISH_CHECKING),
    ("finish looping", TokenType.FINISH_LOOPING),
    ("finish performance", TokenType.FINISH_PERFORMANCE),
    ("to perform", TokenType.TO_PERFORM),
    ("give back", TokenType.GIVE_BACK),
    ("and save as", TokenType.AND_SAVE_AS),
    ("opposite of", TokenType.OPPOSITE_OF),
    ("is same as", TokenType.IS_SAME_AS),
    ("is different from", TokenType.IS_DIFFERENT_FROM),
    ("is at least", TokenType.IS_GTE),
    ("is at most", TokenType.IS_LTE),
    ("is above", TokenType.IS_ABOVE),
    ("is below", TokenType.IS_BELOW),
    ("otherwise if", TokenType.OTHERWISE_IF),
    ("otherwise", TokenType.OTHERWISE),
    ("remember", TokenType.REMEMBER),
    ("change", TokenType.CHANGE),
    ("speak", TokenType.SPEAK),
    ("ask", TokenType.ASK),
    ("if", TokenType.IF),
    ("while", TokenType.WHILE),
    ("repeat", TokenType.REPEAT),
    ("perform", TokenType.PERFORM),
    ("as", TokenType.AS),
    ("to", TokenType.TO),
    ("then", TokenType.THEN),
    ("times", TokenType.TIMES),
    ("with", TokenType.WITH),
    ("and", TokenType.AND),
    ("or", TokenType.OR),
    ("plus", TokenType.PLUS),
    ("minus", TokenType.MINUS),
    ("divided by", TokenType.DIVIDED_BY),
    ("modulo", TokenType.MODULO),
    ("true", TokenType.TRUE),
    ("false", TokenType.FALSE)
]

# Dispatch map to speed up scanning by indexing keywords by first character
KEYWORDS_BY_START: Dict[str, List] = {}
for kw_str, token_type in KEYWORDS_MAP:
    first_char = kw_str[0]
    if first_char not in KEYWORDS_BY_START:
        KEYWORDS_BY_START[first_char] = []
    KEYWORDS_BY_START[first_char].append((kw_str, token_type))


def is_identifier_char(char: str) -> bool:
    """
    Helper to check if character is part of a valid identifier name.
    Supports letters, digits, underscores, and Unicode/Emoji ranges (code points > 127).
    Rejects standard ASCII punctuation like '@' or '$'.
    """
    return char.isalnum() or char == '_' or ord(char) > 127


def is_identifier_start(char: str) -> bool:
    """Helper to check if character can start a valid identifier name."""
    if char.isdigit():
        return False
    return is_identifier_char(char)


class SpeakLexer:
    """
    Performs lexical scanning on SpeakCode source files.
    Extracts tokens, ignores comments and whitespace, and flags SPK101 lexical errors.
    """

    def __init__(self, source: str, filename: str = "<stdin>", debug: bool = False) -> None:
        """
        Initializes the lexer context.

        Args:
            source: Raw string content of the source code.
            filename: Path name of the executing file.
            debug: If True, prints character scanning logs to standard output.
        """
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.debug = debug

    def is_at_end(self) -> bool:
        """Checks if the scanner cursor has reached the end of the source string."""
        return self.pos >= len(self.source)

    def peek(self) -> str:
        """Returns the character at the current cursor index without advancing."""
        if self.is_at_end():
            return '\0'
        return self.source[self.pos]

    def peek_next(self) -> str:
        """Returns the character immediately after the current cursor without advancing."""
        if self.pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.pos + 1]

    def advance(self) -> str:
        """
        Consumes the current character and moves the scanner cursor forward.
        Updates line and column coordinates.
        """
        char = self.source[self.pos]
        self.pos += 1
        
        if self.debug:
            print(f"[Lexer Debug] Consumed character '{repr(char)}' at Line {self.line}, Col {self.column}")
            
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def skip_whitespace_and_comments(self) -> None:
        """Skips non-semantic layout elements including whitespaces, tabs, and comments."""
        while not self.is_at_end():
            char = self.peek()
            
            # Skip spaces, tabs, newlines
            if char in [' ', '\t', '\r', '\n']:
                self.advance()
                continue
                
            # Check comment starts ('#' or case-insensitive 'note')
            if self.is_comment_start():
                if self.debug:
                    print(f"[Lexer Debug] Skipping comment starting at Line {self.line}, Col {self.column}")
                # Skip characters until newline or end of file
                while not self.is_at_end() and self.peek() not in ['\n', '\r']:
                    self.advance()
                continue
                
            break

    def is_comment_start(self) -> bool:
        """
        Determines if the scanner cursor is positioned at a comment starter block.
        Scans in place (O(1)) without allocating remainder substrings.
        """
        if self.is_at_end():
            return False
            
        char = self.source[self.pos]
        if char == '#':
            return True
            
        # Match 'note' case-insensitively
        if self.pos + 4 > len(self.source):
            return False
            
        n = self.source[self.pos]
        o = self.source[self.pos + 1]
        t = self.source[self.pos + 2]
        e = self.source[self.pos + 3]
        
        if (n == 'n' or n == 'N') and (o == 'o' or o == 'O') and (t == 't' or t == 'T') and (e == 'e' or e == 'E'):
            # Match boundary for 'note:' or 'note '
            if self.pos + 4 == len(self.source):
                return True
            next_char = self.source[self.pos + 4]
            if next_char in [':', ' ', '\t', '\r', '\n']:
                return True
                
        return False

    def match_keyword_at_pos(self, keyword: str) -> bool:
        """
        Checks if the specified keyword matches at the current position index
        case-insensitively, respecting word boundaries.
        """
        length = len(keyword)
        if self.pos + length > len(self.source):
            return False
            
        slice_str = self.source[self.pos : self.pos + length]
        if slice_str.lower() != keyword.lower():
            return False
            
        # Guarantee word boundary check
        if self.pos + length < len(self.source):
            next_char = self.source[self.pos + length]
            if next_char.isalnum() or next_char == '_':
                return False
                
        return True

    def scan_string(self, start_line: int, start_col: int) -> Token:
        """
        Consumes string literal bounds wrapped in double quotes.
        Supports escape sequences: \\n (newline), \\t (tab), \\" (quote), \\\\ (backslash).
        Flags SPK101 lexical errors if string is unterminated at EOF.
        """
        self.advance()  # Consume starting quote
        chars = []
        
        while not self.is_at_end() and self.peek() != '"':
            # Handle escapes if present
            if self.peek() == '\\':
                self.advance()  # Consume escape backslash
                if self.is_at_end():
                    break
                esc = self.peek()
                if esc == 'n':
                    chars.append('\n')
                    self.advance()
                elif esc == 't':
                    chars.append('\t')
                    self.advance()
                elif esc == '"':
                    chars.append('"')
                    self.advance()
                elif esc == '\\':
                    chars.append('\\')
                    self.advance()
                else:
                    # Keep raw unknown escaped character
                    chars.append(self.advance())
            else:
                chars.append(self.advance())
                
        if self.is_at_end():
            raise SpeakLexerError(
                message="Unterminated string literal. Expected closing double-quote mark '\"'.",
                position=Position(self.filename, start_line, start_col),
                source=self.source,
                suggestion="Close the string literal by adding a double quote at the end of your string."
            )
            
        self.advance()  # Consume ending quote
        return Token(TokenType.STRING, "".join(chars), Position(self.filename, start_line, start_col))

    def scan_number(self, start_line: int, start_col: int) -> Token:
        """
        Scans numeric literals. Supports both integers and decimal floating points.
        Also asserts boundary check to reject numbers immediately followed by alphabetic characters.
        """
        chars = []
        
        while not self.is_at_end() and self.peek().isdigit():
            chars.append(self.advance())
            
        # Check decimal fraction (dot followed by digit, e.g. 3.14 vs 5.)
        if self.peek() == '.' and self.peek_next().isdigit():
            chars.append(self.advance())  # Consume '.'
            while not self.is_at_end() and self.peek().isdigit():
                chars.append(self.advance())
                
        # Validate that number does not lead directly into an identifier (e.g. 10abc)
        if not self.is_at_end() and (self.peek().isalpha() or self.peek() == '_'):
            bad_char = self.peek()
            raise SpeakLexerError(
                message=f"Invalid numeric literal boundary. Number followed directly by identifier character '{bad_char}'.",
                position=Position(self.filename, start_line, start_col),
                source=self.source,
                suggestion="Insert space between the numeric literal and identifier."
            )
            
        val_str = "".join(chars)
        return Token(TokenType.NUMBER, val_str, Position(self.filename, start_line, start_col))

    def scan_identifier(self, start_line: int, start_col: int) -> Token:
        """Scans user-defined identifiers (alphanumeric sequences and underscores)."""
        chars = []
        while not self.is_at_end() and is_identifier_char(self.peek()):
            chars.append(self.advance())
            
        val_str = "".join(chars)
        return Token(TokenType.IDENTIFIER, val_str, Position(self.filename, start_line, start_col))

    def tokenize(self) -> List[Token]:
        """
        Executes scanning over the complete source string.
        Returns a position-tracked list of Tokens ending in TokenType.EOF.
        """
        tokens: List[Token] = []
        
        while not self.is_at_end():
            self.skip_whitespace_and_comments()
            if self.is_at_end():
                break
                
            start_line = self.line
            start_col = self.column
            char = self.peek()
            
            # 1. Check double quote string literal starts
            if char == '"':
                tokens.append(self.scan_string(start_line, start_col))
                continue
                
            # 2. Check numeric literal starts
            if char.isdigit():
                tokens.append(self.scan_number(start_line, start_col))
                continue
                
            # 3. Check exact multi-word and single-word keywords using character dispatching
            char_lower = char.lower()
            matched_keyword = False
            if char_lower in KEYWORDS_BY_START:
                for kw_str, token_type in KEYWORDS_BY_START[char_lower]:
                    if self.match_keyword_at_pos(kw_str):
                        kw_len = len(kw_str)
                        lexeme_value = self.source[self.pos : self.pos + kw_len]
                        for _ in range(kw_len):
                            self.advance()
                        tokens.append(Token(token_type, lexeme_value, Position(self.filename, start_line, start_col)))
                        matched_keyword = True
                        break
            
            if matched_keyword:
                continue
                
            # 4. Check punctuation markers
            if char == '.':
                self.advance()
                tokens.append(Token(TokenType.PERIOD, ".", Position(self.filename, start_line, start_col)))
                continue
            if char == ':':
                self.advance()
                tokens.append(Token(TokenType.COLON, ":", Position(self.filename, start_line, start_col)))
                continue
            if char == '(':
                self.advance()
                tokens.append(Token(TokenType.LPAREN, "(", Position(self.filename, start_line, start_col)))
                continue
            if char == ')':
                self.advance()
                tokens.append(Token(TokenType.RPAREN, ")", Position(self.filename, start_line, start_col)))
                continue
                
            # 5. Check user-defined identifiers (variables, functions)
            if is_identifier_start(char):
                tokens.append(self.scan_identifier(start_line, start_col))
                continue
                
            # 6. Raise Lexer Exception on unexpected characters
            bad_char = self.advance()
            raise SpeakLexerError(
                message=f"Unexpected character '{bad_char}' found in program source.",
                position=Position(self.filename, start_line, start_col),
                source=self.source,
                suggestion="Remove the character, check keyword capitalization rules, or verify string quotation marks."
            )
            
        # Append EOF marker
        tokens.append(Token(TokenType.EOF, "", Position(self.filename, self.line, self.column)))
        return tokens


def get_token_statistics(tokens: List[Token]) -> Dict[TokenType, int]:
    """
    Computes frequency statistics for a list of tokens.

    Args:
        tokens: Evaluated list of Tokens.

    Returns:
        Dictionary mapping TokenType to count frequencies.
    """
    stats: Dict[TokenType, int] = {}
    for t in tokens:
        stats[t.type] = stats.get(t.type, 0) + 1
    return stats
