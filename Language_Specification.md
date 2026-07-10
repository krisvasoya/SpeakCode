# SpeakCode Language Specification v1.0

SpeakCode is a conversational, educational interpreted programming language with a modular compiler front end, designed specifically to demonstrate the complete compiler pipeline. 

SpeakCode is built on one core philosophy: **"Programming should feel like giving natural instructions to another human."**

---

## 1. Language Philosophy & Design

Unlike conventional languages that rely on shorthand mathematical operators (`+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`) and syntax braces (`{}`), SpeakCode reads like simple English prose:
- **Capitalization**: The first word of every statement is capitalized.
- **Punctuation**: Every standalone sentence ends with a period (`.`).
- **Conversational Keywords**: Keywords like `Remember`, `Change`, `Speak`, `Ask`, and `Perform` are preferred over technical descriptors like `define`, `set`, `say`, `input`, and `call`.
- **Compound Closing Markers**: Blocks are closed using context-rich phrases like `Finish checking.` (for conditionals), `Finish looping.` (for loops), and `Finish performance.` (for functions).

---

## 2. EBNF Grammar

```ebnf
Program         ::= Statement* EOF
Statement       ::= RememberStmt | ChangeStmt | SpeakStmt | AskStmt | IfStmt | WhileStmt | RepeatStmt | FunDeclStmt | FunCallStmt | ReturnStmt

RememberStmt    ::= "Remember" Expression "as" IDENTIFIER "."
ChangeStmt      ::= "Change" IDENTIFIER "to" Expression "."
SpeakStmt       ::= "Speak" Expression "."
AskStmt         ::= "Ask" (Expression)? "and save as" IDENTIFIER "."

IfStmt          ::= "If" Expression "then" Statement* 
                    ("Otherwise if" Expression "then" Statement*)* 
                    ("Otherwise" Statement*)? 
                    "Finish checking" "."

WhileStmt       ::= "While" Expression "repeat" Statement* "Finish looping" "."
RepeatStmt      ::= "Repeat" Expression "times" Statement* "Finish looping" "."

FunDeclStmt     ::= "To perform" IDENTIFIER ("with" IDENTIFIER ("and" IDENTIFIER)*)? ":" Statement* "Finish performance" "."
ReturnStmt      ::= "Give back" Expression "."
FunCallStmt     ::= "Perform" IDENTIFIER ("with" Expression ("and" Expression)*)? ("and save as" IDENTIFIER)? "."

Expression      ::= LogicalOr
LogicalOr       ::= LogicalAnd ("or" LogicalAnd)*
LogicalAnd      ::= LogicalNot ("and" LogicalNot)*
LogicalNot      ::= "opposite of" LogicalNot | Comparison
Comparison      ::= Additive (ComparisonOp Additive)?
ComparisonOp    ::= "is same as" | "is different from" | "is above" | "is below" | "is at least" | "is at most"
Additive        ::= Multiplicative (AdditiveOp Multiplicative)*
AdditiveOp      ::= "plus" | "minus"
Multiplicative  ::= Unary (MultiplicativeOp Unary)*
MultiplicativeOp::= "times" | "divided by" | "modulo"
Unary           ::= "minus" Unary | Primary
Primary         ::= NUMBER | STRING | "true" | "false" | IDENTIFIER | "(" Expression ")"
```

---

## 3. Tokens & Lexicon

| Token Lexeme | Token Type | Description |
|---|---|---|
| `Remember` | `REMEMBER` | Variable declaration starter |
| `Change` | `CHANGE` | Variable modification starter |
| `Speak` | `SPEAK` | Console print starter |
| `Ask` | `ASK` | Console input starter |
| `If` | `IF` | Conditional starter |
| `Otherwise if` | `OTHERWISE_IF` | Else-if branch header |
| `Otherwise` | `OTHERWISE` | Else branch header |
| `While` | `WHILE` | While loop header |
| `Repeat` | `REPEAT` | Count loop header |
| `To perform` | `TO_PERFORM` | Function definition header |
| `Perform` | `PERFORM` | Function execution header |
| `Give back` | `GIVE_BACK` | Return value statement |
| `Finish checking` | `FINISH_CHECKING` | End of conditional block |
| `Finish looping` | `FINISH_LOOPING` | End of loop block |
| `Finish performance` | `FINISH_PERFORMANCE` | End of function block |
| `as` | `AS` | Binding indicator |
| `to` | `TO` | Assignment indicator |
| `then` | `THEN` | Conditional body indicator |
| `times` | `TIMES` | Count multiplier indicator / operator |
| `with` | `WITH` | Parameter list header |
| `and` | `AND` | Parameter separator / logical AND operator |
| `or` | `OR` | Logical OR operator |
| `and save as` | `AND_SAVE_AS` | Call binding result indicator |
| `opposite of` | `OPPOSITE_OF` | Unary logical NOT operator |
| `plus` | `PLUS` | Arithmetic addition / String concatenation |
| `minus` | `MINUS` | Arithmetic subtraction |
| `divided by` | `DIVIDED_BY` | Arithmetic division |
| `modulo` | `MODULO` | Arithmetic division remainder |
| `is same as` | `IS_SAME_AS` | Comparison equality (`==`) |
| `is different from` | `IS_DIFFERENT_FROM` | Comparison inequality (`!=`) |
| `is above` | `IS_ABOVE` | Comparison greater than (`>`) |
| `is below` | `IS_BELOW` | Comparison less than (`<`) |
| `is at least` | `IS_GTE` | Comparison greater or equal (`>=`) |
| `is at most` | `IS_LTE` | Comparison less or equal (`<=`) |
| `true` / `false` | `TRUE` / `FALSE` | Boolean literal values |
| `.` | `PERIOD` | Sentence terminal indicator |
| `:` | `COLON` | Block body indicator |
| `(` / `)` | `LPAREN` / `RPAREN` | Precedence parenthesized bounds |

---

## 4. Compiler pipeline

The SpeakCode engine is structured as a modular pipeline:

```
[Source Code (.speak)]
       │
       ▼
   [ Lexer ] ──(SPK101)──> Lexical errors
       │
   [Tokens]
       │
       ▼
  [ Parser ] ──(SPK102)──> Syntactic errors
       │
     [AST]
       │
       ▼
[ Semantic Analyzer ] ──(SPK103, 104, 106, 107, 108)──> Semantic verification errors
       │
  [Checked AST]
       │
       ▼
[ Interpreter ] ──(SPK105)──> Runtime execution errors
       │
       ▼
[Console Output]
```

1. **Lexical Analysis (Lexer)**: Performs character scan. Merges multi-word phrases to optimize subsequent parser steps and reduce lookup complexity.
2. **Syntactic Analysis (Parser)**: Follows operator precedence descending paths to structure statements and expressions into nodes.
3. **Static Analysis (Semantic Analyzer)**: Performs forward-declaration hoisting. Verifies variables are declared locally, scopes are bounded, functions are matches for signature counts, and catches basic literal division bounds.
4. **Execution (Interpreter)**: Runs evaluations recursively across AST branches using nested lexical parent environments.

---

## 5. Diagnostic Error Codes

SpeakCode maps logical exceptions to formal codes to assist compiler diagnostics.

* **`SPK101` (Lexical Error)**: Invalid numeric formatting or unexpected character.
* **`SPK102` (Syntax Error)**: Grammatical violations (missing periods, unmatched loops, missing colons).
* **`SPK103` (Semantic Error)**: Variable declared more than once in the same local scope.
* **`SPK104` (Semantic Error)**: Accessing or modifying a variable that has not been initialized.
* **`SPK105` (Runtime Error)**: Division or modulo bounds validation (dividing by zero).
* **`SPK106` (Semantic Error)**: Calling a function that is undefined or mismatching argument lengths.
* **`SPK107` (Semantic Error)**: Using `Give back` outside a function frame definition.
* **`SPK108` (Semantic/Type Error)**: Logical operators applied to non-booleans, or arithmetic applied to non-numbers.

---

## 6. Expression Operator Precedence

Precedence levels ordered from lowest to highest:

1. **Logical OR**: `or`
2. **Logical AND**: `and`
3. **Logical NOT**: `opposite of`
4. **Comparisons**: `is same as`, `is different from`, `is above`, `is below`, `is at least`, `is at most`
5. **Additive**: `plus`, `minus`
6. **Multiplicative**: `times`, `divided by`, `modulo`
7. **Unary Negation**: `minus`
8. **Primary terms**: numbers, strings, booleans, variables, groupings `(...)`

---

## 7. Sample Implementation

Below is a demonstration of procedure hoisting, variable scoping, and math operations:

```speakcode
note: Functions and hoisting demonstration in SpeakCode.

Speak "--- Functions Demo ---".

Remember 10 as x.
Remember 20 as y.

note: Call add_numbers which is declared further down!
Perform add_numbers with x and y and save as result.
Speak "Adding " plus x plus " and " plus y plus " gives: " plus result.

note: Declare the functions here.
To perform add_numbers with a and b:
    Remember a plus b as sum_val.
    Give back sum_val.
Finish performance.
```
