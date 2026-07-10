# SpeakCode Compiler - Extension & Developer Guide

This document explains the steps to extend the SpeakCode compiler by introducing new keywords, AST nodes, parsing rules, semantic checks, and CLI commands.

---

## 1. Compiler Execution Flow Overview

When extending SpeakCode, keep the modular architecture in mind:

```
[Source String]
   │
   ▼ (speak_lexer.py) -> Add new keyword strings & TokenTypes
[Tokens Stream]
   │
   ▼ (speak_parser.py) -> Parse to new ASTNode (speak_ast.py)
[AST Trees]
   │
   ▼ (speak_semantic.py) -> Validate symbols and type rules
[Verified AST]
   │
   ▼ (speak_interpreter.py) -> Implement dynamic execution behavior
[Console / Env Output]
```

---

## 2. Guide: Adding a New Keyword (e.g., `Modulo`)

Suppose we want to add an explicit modulo keyword `remainder of` (matching `%`).

### Step A: Update `speak_tokens.py`
Add the new token type to the `TokenType` enum:
```python
class TokenType(Enum):
    # ...
    REMAINDER_OF = "REMAINDER_OF"
```

### Step B: Register the Lexeme in `speak_lexer.py`
Add the text keyword and its token type mapping to `KEYWORDS_MAP` (ensure correct sorting by length to avoid greediness issues):
```python
KEYWORDS_MAP = [
    # ...
    ("remainder of", TokenType.REMAINDER_OF),
    # ...
]
```

---

## 3. Guide: Adding a New AST Node

Suppose we want to add a `RepeatUntil` statement: `Repeat until <cond>: <body> Finish looping.`

### Step A: Declare the Node in `speak_ast.py`
Define the properties and serialization methods for the new node:
```python
@dataclass(frozen=True)
class RepeatUntilNode(StatementNode):
    condition: ExpressionNode
    body: List[StatementNode]
    position: Position

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_repeat_until(self)

    def stringify(self) -> str:
        body_str = "\n".join(s.stringify() for s in self.body)
        return f"Repeat until {self.condition.stringify()}:\n{body_str}\nFinish looping."

    def pretty_print(self, indent: int = 0) -> str:
        # Custom ASCII drawing logic
        return "Repeat Until Node"

    def to_dict(self) -> dict:
        return {
            "type": "RepeatUntilNode",
            "condition": self.condition.to_dict(),
            "body": [s.to_dict() for s in self.body],
            "position": {"line": self.position.line, "column": self.position.column}
        }
```

---

## 4. Guide: Adding a New Parser Rule

Now we teach the parser (`speak_parser.py`) how to process this new node.

### Step A: Add a Dispatch Switch in `statement()`
```python
    def statement(self) -> ASTNode:
        # ...
        if self.match([TokenType.REPEAT_UNTIL]):
            return self.repeat_until_statement()
        # ...
```

### Step B: Write the Parsing Logic Method
```python
    def repeat_until_statement(self) -> RepeatUntilNode:
        start_tok = self.previous() # Holds REPEAT_UNTIL token
        
        condition = self.expression()
        self.consume(TokenType.COLON, "Expected colon after condition.", "Use ':' to open the block.")
        body = self.parse_body([TokenType.FINISH_LOOPING])
        
        self.consume(TokenType.FINISH_LOOPING, "Expected block closure phrase 'Finish looping'.", "Close with Finish looping.")
        self.consume(TokenType.PERIOD, "Expected period.", "End statement with '.'")
        
        return RepeatUntilNode(condition, body, start_tok.position)
```

---

## 5. Guide: Adding a New Semantic Checking Rule

In `speak_semantic.py`, implement the visitor interface hook to validate symbols and types:

```python
    def visit_repeat_until(self, node: RepeatUntilNode) -> None:
        cond_type = self.visit(node.condition)
        if cond_type != "Boolean":
            self.error(SpeakTypeError(
                error_code="SPK108",
                message=f"Repeat until conditions require Boolean check types, but got '{cond_type}'.",
                position=node.condition.position,
                source=self.source,
                suggestion="Make sure the expression evaluates to true or false."
            ))
            
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.leave_scope()
```

---

## 6. Guide: Adding a New Interpreter Execution Rule

In `speak_interpreter.py`, execute the logic dynamically:

```python
    def visit_repeat_until(self, node: RepeatUntilNode) -> None:
        while not self.evaluate_bool(node.condition):
            try:
                for stmt in node.body:
                    self.execute(stmt)
            except ReturnException as ret:
                raise ret # Propagate return statements
```

---

## 7. Guide: Adding a New CLI Command

Suppose we want to add a `loc` command to count source lines of code: `python speakcode.py loc <file>`.

### Step A: Register the Command Usage in `speakcode.py`
Update `print_usage()` and `HELP_TEXTS` to document the new command:
```python
HELP_TEXTS = {
    # ...
    "loc": "loc <file.speak>     : Output line of code statistics.",
}
```

### Step B: Write the Action Function
```python
def count_lines(filepath: str) -> None:
    source = read_file(filepath)
    lines = source.splitlines()
    print(f"Total Lines of Code: {len(lines)}")
```

### Step C: Update CLI Entry Switch in `main()`
```python
    # ...
    elif cmd == "loc":
        if len(sys.argv) < 3:
            print("Error: Missing filepath. Usage: speakcode loc <file>")
            sys.exit(1)
        count_lines(sys.argv[2])
    # ...
```
