"""
SpeakCode Compiler - Source Code Formatter
Automatically normalizes keyword capitalization, trims whitespace,
and formats nested code block bodies to 4-space indentation.

Dependencies:
    - re (Standard Library)
"""

import re

KEYWORDS_REPLACE = {
    "remember": "Remember",
    "change": "Change",
    "speak": "Speak",
    "ask": "Ask",
    "if": "If",
    "then": "then",
    "otherwise if": "Otherwise if",
    "otherwise": "Otherwise",
    "finish checking": "Finish checking",
    "while": "While",
    "repeat": "Repeat",
    "times": "times",
    "finish looping": "Finish looping",
    "to perform": "To perform",
    "finish performance": "Finish performance",
    "give back": "Give back",
    "perform": "Perform",
    "with": "with",
    "and": "and",
    "as": "as",
    "to": "to",
    "divided by": "divided by",
    "modulo": "modulo",
    "opposite of": "opposite of",
    "is above": "is above",
    "is below": "is below",
    "is same as": "is same as",
    "is different from": "is different from",
    "is at least": "is at least",
    "is at most": "is at most",
    "true": "true",
    "false": "false"
}

# Sort keywords by length descending to match multi-word constructs first
SORTED_REPLS = sorted(KEYWORDS_REPLACE.items(), key=lambda x: len(x[0]), reverse=True)


def split_line(line: str) -> tuple[str, str]:
    """Splits a line of source code into code part and comment suffix (bounds safe)."""
    in_string = False
    i = 0
    while i < len(line):
        if line[i] == '"':
            # Handle string toggle and escape quotes checks
            if i > 0 and line[i - 1] == '\\':
                pass
            else:
                in_string = not in_string
        elif not in_string:
            if line[i] == '#':
                return line[:i], line[i:]
            if line[i:].startswith('note'):
                return line[:i], line[i:]
        i += 1
    return line, ""


def format_code_part(code: str) -> str:
    """Corrects keyword casings in non-string literal areas of a code line."""
    parts = []
    in_string = False
    current = []
    i = 0
    while i < len(code):
        if code[i] == '"':
            if in_string:
                current.append('"')
                parts.append((True, "".join(current)))
                current = []
                in_string = False
            else:
                if current:
                    parts.append((False, "".join(current)))
                current = ['"']
                in_string = True
        else:
            current.append(code[i])
        i += 1
    if current:
        parts.append((in_string, "".join(current)))
        
    formatted = []
    for is_str, val in parts:
        if is_str:
            formatted.append(val)
        else:
            temp = val
            temp = re.sub(r'[ \t]+', ' ', temp)
            for kw, target in SORTED_REPLS:
                pattern = r'\b' + re.escape(kw) + r'\b'
                temp = re.sub(pattern, target, temp, flags=re.IGNORECASE)
            formatted.append(temp)
    return "".join(formatted)


def format_code(source: str) -> str:
    """Formats the SpeakCode source code string."""
    lines = source.splitlines()
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        code_part, comment_part = split_line(line)
        trimmed_code = code_part.strip()
        
        if not trimmed_code:
            if comment_part:
                formatted_lines.append("    " * indent_level + comment_part.strip())
            else:
                formatted_lines.append("")
            continue
            
        formatted_code = format_code_part(trimmed_code)
        
        # Check block closures to dedent BEFORE writing the line
        is_closure = False
        for closure in ["Finish checking", "Finish looping", "Finish performance", "Otherwise", "Otherwise if"]:
            if formatted_code.startswith(closure):
                is_closure = True
                break
                
        current_indent = indent_level
        if is_closure:
            current_indent = max(0, indent_level - 1)
            if formatted_code.startswith("Finish"):
                indent_level = max(0, indent_level - 1)
                
        # Build final line
        space = "    " * current_indent
        comment_suffix = f" {comment_part.strip()}" if comment_part else ""
        formatted_lines.append(space + formatted_code + comment_suffix)
        
        # Check block openers to indent AFTER writing the line
        is_opener = False
        if (formatted_code.startswith("If") or 
            formatted_code.startswith("While") or 
            formatted_code.startswith("Repeat") or 
            formatted_code.startswith("To perform") or
            formatted_code.startswith("Otherwise") or
            formatted_code.startswith("Otherwise if")):
            is_opener = True
            
        if is_opener:
            if not (formatted_code.startswith("Otherwise") or formatted_code.startswith("Otherwise if")):
                indent_level += 1
                
    # Normalize double blank lines and trim edges
    result = "\n".join(formatted_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip() + "\n"
