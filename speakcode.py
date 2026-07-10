"""
SpeakCode Compiler - Developer Toolkit & Command Line Interface (CLI)
Coordinative entry point managing scanning, parsing, semantics checking,
formatting, explaining, and executing SpeakCode program streams.

Supported Commands:
    - run <file>       : Executes a verified program.
    - tokens <file>    : Displays the tokens table.
    - ast <file>       : Draws the ASCII AST tree representation.
    - semantic <file>  : Runs semantic verification.
    - debug <file>     : Displays verification checkpoints.
    - explain <file>   : Translates statements to plain English.
    - format <file>    : Re-normalizes code indentation/capitalization.
    - repl             : Launches an interactive multiline shell.
    - version          : Prints compiler versions and metadata.
    - help [cmd]       : Prints helpful usages.
"""

import os
import sys
import platform
from typing import List, Dict, Optional, Any
from speak_lexer import SpeakLexer, get_token_statistics
from speak_tokens import TokenType
from speak_parser import SpeakParser
from speak_semantic import SpeakSemanticAnalyzer
from speak_interpreter import SpeakInterpreter, to_speak_string
from speak_errors import SpeakError
from speak_explainer import SpeakExplainer
from speak_formatter import format_code
from speak_ast import FunctionDeclarationNode

LOGO = """
███████╗██████╗ ███████╗ █████╗ ██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔══██╗██║ ██╔╝
███████╗██████╔╝█████╗  ███████║█████╔╝ 
╚════██║██╔═══╝ ██╔══╝  ██╔══██║██╔═██╗ 
███████║██║     ███████╗██║  ██║██║  ██╗
╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
         SpeakCode Compiler v1.0.0
       "Programming Like Talking"
"""

VERSION_BANNER = """╔══════════════════════════════════════╗
║         SpeakCode Compiler           ║
║              Version 1.0             ║
║                                      ║
║ Programming Like Talking             ║
║                                      ║
║ Created by                           ║
║ Krish Vasoya                         ║
║ B.Tech CSD                           ║
║ Compiler Design Mini Project 2026    ║
╚══════════════════════════════════════╝"""

HELP_TEXTS = {
    "run": "Usage: speakcode run <file.speak>\nExecutes a verified SpeakCode program with semantic validation.",
    "tokens": "Usage: speakcode tokens <file.speak>\nDisplays every token matching Lexer rules in a formatted table.",
    "ast": "Usage: speakcode ast <file.speak>\nDisplays the AST (Abstract Syntax Tree) structure as an ASCII tree.",
    "semantic": "Usage: speakcode semantic <file.speak>\nValidates the program logically without executing it.",
    "debug": "Usage: speakcode debug <file.speak>\nPrints each compiler execution stage with state details.",
    "explain": "Usage: speakcode explain <file.speak>\nExplains the logic of every statement in plain English.",
    "format": "Usage: speakcode format <file.speak>\nStandardizes keyword capitalization and sets 4-space indentation.",
    "repl": "Usage: speakcode repl\nLaunches an interactive multiline shell.",
    "version": "Usage: speakcode version\nDisplays author credentials and version info."
}


def color(text: str, code: str) -> str:
    """Helper to apply ANSI terminal color codes unless --no-color is set."""
    if "--no-color" in sys.argv or os.environ.get("NO_COLOR"):
        return text
    return f"\033[{code}m{text}\033[0m"


def read_file(filepath: str) -> str:
    """Safely reads a file with UTF-8 encoding or exits."""
    if not os.path.exists(filepath):
        print(color(f"Error: File '{filepath}' not found.", "31"), file=sys.stderr)
        sys.exit(1)
    if not filepath.endswith('.speak'):
        print(color(f"Warning: File '{filepath}' does not have the expected '.speak' extension.", "33"), file=sys.stderr)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def run_file(filepath: str) -> None:
    """Runs lexical, parse, semantic, and interpreter stages for a file."""
    source = read_file(filepath)
    try:
        lexer = SpeakLexer(source, filepath)
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, filepath)
        program = parser.parse()
        if parser.errors:
            for err in parser.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
            
        analyzer = SpeakSemanticAnalyzer(source, filepath)
        analyzer.analyze(program)
        if analyzer.errors:
            for err in analyzer.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
            
        interpreter = SpeakInterpreter(source, filepath)
        interpreter.interpret(program)
    except SpeakError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def show_tokens(filepath: str) -> None:
    """Lexes a file and outputs a formatted table of tokens."""
    source = read_file(filepath)
    try:
        lexer = SpeakLexer(source, filepath)
        tokens = lexer.tokenize()
        
        # Draw table header
        header = f"{'Token Type':<25} | {'Lexeme':<25} | {'Line':<6} | {'Column':<6}"
        print(color(header, "34"))
        print(color("-" * 70, "90"))
        
        for t in tokens:
            # Color assignment based on Token category
            t_color = "0"
            if t.type.name.startswith("IS_") or t.type in [
                TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDED_BY, TokenType.MODULO, TokenType.OPPOSITE_OF
            ]:
                t_color = "35"  # Purple for operators
            elif t.type in [
                TokenType.REMEMBER, TokenType.CHANGE, TokenType.SPEAK, TokenType.ASK, TokenType.IF, TokenType.THEN,
                TokenType.OTHERWISE_IF, TokenType.OTHERWISE, TokenType.WHILE, TokenType.REPEAT, TokenType.TIMES,
                TokenType.TO_PERFORM, TokenType.FINISH_PERFORMANCE, TokenType.GIVE_BACK, TokenType.PERFORM,
                TokenType.FINISH_CHECKING, TokenType.FINISH_LOOPING, TokenType.AS, TokenType.TO, TokenType.WITH, TokenType.AND, TokenType.OR
            ]:
                t_color = "36"  # Cyan for keyword operations
            elif t.type == TokenType.STRING:
                t_color = "32"  # Green for string literals
            elif t.type in [TokenType.NUMBER, TokenType.TRUE, TokenType.FALSE]:
                t_color = "33"  # Yellow for numbers and booleans
                
            print(f"{color(t.type.name, t_color):<34} | {repr(t.value):<25} | {t.position.line:<6} | {t.position.column:<6}")
            
        # Display frequency metrics
        stats = get_token_statistics(tokens)
        print(color("-" * 70, "90"))
        print(color(f"Total Tokens Scanned: {len(tokens)}", "32"))
        print(color(f"Identifiers count   : {stats.get(TokenType.IDENTIFIER, 0)}", "34"))
    except SpeakError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def show_ast(filepath: str) -> None:
    """Parses a file and outputs a unicode tree drawing of the AST."""
    source = read_file(filepath)
    try:
        lexer = SpeakLexer(source, filepath)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source, filepath)
        program = parser.parse()
        
        if parser.errors:
            for err in parser.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
            
        print(program.pretty_print())
    except SpeakError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def run_semantic(filepath: str) -> None:
    """Runs semantic checks and prints diagnostic verification status."""
    source = read_file(filepath)
    try:
        lexer = SpeakLexer(source, filepath)
        tokens = lexer.tokenize()
        
        parser = SpeakParser(tokens, source, filepath)
        program = parser.parse()
        if parser.errors:
            for err in parser.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
            
        analyzer = SpeakSemanticAnalyzer(source, filepath)
        analyzer.analyze(program)
        
        if analyzer.errors:
            for err in analyzer.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
            
        print(color("✓ Passed", "32"))
    except SpeakError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def run_debug(filepath: str) -> None:
    """Executes each stage of compilation with status updates."""
    print(color("Reading Source ............ ", "34"), end="", flush=True)
    source = read_file(filepath)
    print(color("OK", "32"))

    try:
        print(color("Lexical Analysis .......... ", "34"), end="", flush=True)
        lexer = SpeakLexer(source, filepath)
        tokens = lexer.tokenize()
        print(color(f"OK ({len(tokens)} Tokens)", "32"))

        print(color("Parsing ................... ", "34"), end="", flush=True)
        parser = SpeakParser(tokens, source, filepath)
        program = parser.parse()
        if parser.errors:
            print(color("FAILED", "31"))
            for err in parser.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
        print(color("OK", "32"))

        print(color("Semantic Analysis ......... ", "34"), end="", flush=True)
        analyzer = SpeakSemanticAnalyzer(source, filepath)
        analyzer.analyze(program)
        if analyzer.errors:
            print(color("FAILED", "31"))
            for err in analyzer.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
        print(color("OK", "32"))

        print(color("Interpreter ............... ", "34"), end="", flush=True)
        print(color("OK", "32"))
        print(color("--- Output ---", "90"))
        
        interpreter = SpeakInterpreter(source, filepath, debug=True, trace=True)
        interpreter.interpret(program)
        
        print(color("--------------", "90"))
        print(color("Execution Complete", "32"))
    except SpeakError as e:
        print(color("FAILED", "31"))
        print(e, file=sys.stderr)
        sys.exit(1)


def explain_file(filepath: str) -> None:
    """Translates statements into plain English sentences."""
    source = read_file(filepath)
    try:
        lexer = SpeakLexer(source, filepath)
        tokens = lexer.tokenize()
        parser = SpeakParser(tokens, source, filepath)
        program = parser.parse()
        
        if parser.errors:
            for err in parser.errors:
                print(err, file=sys.stderr)
            sys.exit(1)
            
        explainer = SpeakExplainer()
        explanations = explainer.explain(program)
        
        print(color(f"=== Explanation: {filepath} ===", "34"))
        for line in explanations:
            print(line)
    except SpeakError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def format_file(filepath: str) -> None:
    """Formats code and saves changes back to the source file."""
    source = read_file(filepath)
    formatted = format_code(source)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted)
    print(color(f"File '{filepath}' formatted successfully.", "32"))


def run_repl() -> None:
    """Launches interactive checked REPL session supporting multi-line blocks."""
    print(color(LOGO, "32"))
    print(color("SpeakCode Interactive REPL (v1.0.0)", "34"))
    print(color("Type 'exit' to quit. End blocks with period '.' to execute.", "90"))
    
    analyzer = SpeakSemanticAnalyzer("", "<repl>")
    interpreter = SpeakInterpreter("", "<repl>")
    
    buffer = []
    block_depth = 0
    
    while True:
        try:
            # Multi-line block prompting indicator
            prompt = ".... " if block_depth > 0 else "> "
            line = input(prompt)
            
            if line.strip().lower() == "exit":
                break
                
            buffer.append(line)
            combined = "\n".join(buffer)
            
            # Simple boundary check for nested block depth
            trimmed = line.strip()
            if trimmed.startswith("If ") or trimmed.startswith("While ") or trimmed.startswith("Repeat ") or trimmed.startswith("To perform "):
                block_depth += 1
            if trimmed.startswith("Finish checking") or trimmed.startswith("Finish looping") or trimmed.startswith("Finish performance"):
                block_depth = max(0, block_depth - 1)
                
            # Execute block when depth is fully aligned and statements end with '.'
            if block_depth == 0:
                if not combined.strip():
                    buffer.clear()
                    continue
                    
                # Setup environments sources
                analyzer.source = combined
                interpreter.source = combined
                
                try:
                    # Tokenize and parse
                    lexer = SpeakLexer(combined, "<repl>")
                    tokens = lexer.tokenize()
                    parser = SpeakParser(tokens, combined, "<repl>")
                    program = parser.parse()
                    
                    if parser.errors:
                        # Fallback: check if standard single expression evaluation matches
                        try:
                            parser_expr = SpeakParser(tokens, combined, "<repl>")
                            expr = parser_expr.expression()
                            if parser_expr.peek().type == TokenType.EOF:
                                val = interpreter.evaluate(expr)
                                if val is not None:
                                    print(to_speak_string(val))
                                buffer.clear()
                                continue
                        except Exception:
                            pass
                            
                        # If expression fallback fails, print syntax errors
                        for err in parser.errors:
                            print(err, file=sys.stderr)
                        buffer.clear()
                        continue
                        
                    # Semantic analysis
                    analyzer.analyze(program)
                    if analyzer.errors:
                        for err in analyzer.errors:
                            print(err, file=sys.stderr)
                        buffer.clear()
                        continue
                        
                    # Hoist functions defined in REPL global space
                    for stmt in program.statements:
                        if isinstance(stmt, FunctionDeclarationNode):
                            interpreter.declared_functions[stmt.name] = stmt
                            
                    # Interpret statements
                    interpreter.interpret(program)
                    
                except SpeakError as e:
                    print(e, file=sys.stderr)
                buffer.clear()
                
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


def print_usage() -> None:
    """Outputs basic command line usages."""
    print(color(LOGO, "32"))
    print("Usage:")
    print("  speakcode run <file>       - Validate and execute a SpeakCode file.")
    print("  speakcode tokens <file>    - Scan and print formatted tokens table.")
    print("  speakcode ast <file>       - Parse and print ASCII tree layout.")
    print("  speakcode semantic <file>  - Verify semantic constraints.")
    print("  speakcode debug <file>     - Execute with compiler state diagnostics.")
    print("  speakcode explain <file>   - Generate plain English explanations.")
    print("  speakcode format <file>    - Format keyword cases and spaces.")
    print("  speakcode repl             - Launch multiline shell REPL.")
    print("  speakcode version          - Print version credentials.")
    print("  speakcode help [command]   - Get details on specific commands.")


def show_help(cmd: Optional[str] = None) -> None:
    """Outputs detailed help descriptions."""
    if cmd and cmd in HELP_TEXTS:
        print(color(f"\n--- Help: {cmd} ---", "34"))
        print(HELP_TEXTS[cmd])
    else:
        print_usage()


def main() -> None:
    """Coordinator dispatch main."""
    # Ensure stdout/stderr handles UTF-8 on Windows to prevent charmap encoding errors
    if sys.platform.startswith('win'):
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass
        if hasattr(sys.stderr, 'reconfigure'):
            try:
                sys.stderr.reconfigure(encoding='utf-8')
            except Exception:
                pass

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    
    if cmd == "run":
        if len(sys.argv) < 3:
            print(color("Error: Filename missing.", "31"))
            sys.exit(1)
        run_file(sys.argv[2])
    elif cmd == "tokens":
        if len(sys.argv) < 3:
            print(color("Error: Filename missing.", "31"))
            sys.exit(1)
        show_tokens(sys.argv[2])
    elif cmd == "ast":
        if len(sys.argv) < 3:
            print(color("Error: Filename missing.", "31"))
            sys.exit(1)
        show_ast(sys.argv[2])
    elif cmd == "semantic":
        if len(sys.argv) < 3:
            print(color("Error: Filename missing.", "31"))
            sys.exit(1)
        run_semantic(sys.argv[2])
    elif cmd == "debug":
        if len(sys.argv) < 3:
            print(color("Error: Filename missing.", "31"))
            sys.exit(1)
        run_debug(sys.argv[2])
    elif cmd == "explain":
        if len(sys.argv) < 3:
            print(color("Error: Filename missing.", "31"))
            sys.exit(1)
        explain_file(sys.argv[2])
    elif cmd == "format":
        if len(sys.argv) < 3:
            print(color("Error: Filename missing.", "31"))
            sys.exit(1)
        format_file(sys.argv[2])
    elif cmd == "repl":
        run_repl()
    elif cmd == "version":
        # Print details including Python versions
        print(color(LOGO, "32"))
        print(f"Version: 1.0.0")
        print(f"Author : Krish Vasoya")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python : {platform.python_version()}")
    elif cmd == "help":
        sub = sys.argv[2].lower() if len(sys.argv) > 2 else None
        show_help(sub)
    elif cmd in ["--help", "-h"]:
        show_help()
    else:
        print(color(f"Error: Unknown command '{cmd}'.", "31"))
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
