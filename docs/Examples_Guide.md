# SpeakCode Compiler - Example Programs Reference Guide

This document lists details, logical breakdowns, features demonstrated, and expected outputs for all 17 SpeakCode example programs under the `examples/` directory.

---

## 1. `hello_world.speak`
Basic introduction showing output operations.
- **Features Demonstrated:** `Speak` statements, String literal prints.
- **Code:**
  ```speakcode
  Speak "Hello, World!".
  Speak "SpeakCode is designed to read like simple English.".
  ```
- **Expected Output:**
  ```
  Hello, World!
  SpeakCode is designed to read like simple English.
  ```

---

## 2. `calculator.speak`
Interactive basic math calculations.
- **Features Demonstrated:** `Ask` inputs, mathematical operators, variable declarations.
- **Expected Output (Interactive):**
  ```
  Enter first number: 10
  Enter second number: 5
  Sum: 15
  Difference: 5
  Product: 50
  Quotient: 2
  ```

---

## 3. `student_result.speak`
Evaluates student marks to calculate overall pass/fail status.
- **Features Demonstrated:** `Remember` declarations, `If-Otherwise` conditionals, and comparisons.
- **Expected Output:**
  ```
  Student Name: Alice
  Total Marks: 245
  Average Marks: 81.66666666666667
  Result: PASSED WITH FIRST CLASS
  ```

---

## 4. `fibonacci.speak`
Generates the Fibonacci series of numbers.
- **Features Demonstrated:** `Repeat` loops, variable swapping, and print accumulations.
- **Expected Output:**
  ```
  Generating 10 Fibonacci numbers:
  0
  1
  1
  2
  3
  5
  8
  13
  21
  34
  ```

---

## 5. `factorial.speak`
Calculates the mathematical factorial of a number.
- **Features Demonstrated:** `While` conditional loop, arithmetic multiplication.
- **Expected Output:**
  ```
  Factorial of 5 is: 120
  ```

---

## 6. `guess_game.speak`
Interactive number guessing game.
- **Features Demonstrated:** `While` loop, `Ask` interactive input, comparison checks.
- **Expected Output (Interactive):**
  ```
  Guess my secret number (1 to 10): 5
  Too low! Try again.
  Guess my secret number (1 to 10): 8
  Too high! Try again.
  Guess my secret number (1 to 10): 7
  Correct! You guessed it in 3 attempts.
  ```

---

## 7. `banking_system.speak`
Simulates checking accounts and transactions.
- **Features Demonstrated:** Interactive menus, dynamic balance updates, numeric validation.
- **Expected Output (Interactive):**
  ```
  Current Balance: 1000
  Enter deposit amount: 500
  Deposit successful. New Balance: 1500
  Enter withdrawal amount: 200
  Withdrawal successful. New Balance: 1300
  ```

---

## 8. `atm_simulation.speak`
Simulates ATM pin verification with attempt limits.
- **Features Demonstrated:** Counter increments, logic loops, boolean flags.
- **Expected Output (Interactive):**
  ```
  Enter PIN: 1111
  Invalid PIN. Attempts remaining: 2
  Enter PIN: 1234
  PIN Verified. Welcome!
  ```

---

## 9. `voting_eligibility.speak`
Checks voting requirement conditions.
- **Features Demonstrated:** Compound logical conditions using `and` and `or`.
- **Expected Output (Interactive):**
  ```
  Enter age: 20
  Do you have a voter card? (yes/no): yes
  You are eligible to vote!
  ```

---

## 10. `library_management.speak`
Calculates library book return fines based on delay length.
- **Features Demonstrated:** Tiered pricing calculation using multiple `Otherwise if` blocks.
- **Expected Output (Interactive):**
  ```
  Enter days late: 8
  Fine calculated: 11
  ```

---

## 11. `shopping_bill.speak`
Applies retail discount brackets to item sums.
- **Features Demonstrated:** Conditional percentage math.
- **Expected Output (Interactive):**
  ```
  Enter bill amount: 150
  Discount: 15
  Total due: 135
  ```

---

## 12. `multiplication_table.speak`
Generates multiplication grids.
- **Features Demonstrated:** Nested loop iteration.
- **Expected Output:**
  ```
  Multiplication Table of 5:
  5 times 1 is 5
  5 times 2 is 10
  ...
  5 times 10 is 50
  ```

---

## 13. `average_calculator.speak`
Averages a series of user-entered numbers.
- **Features Demonstrated:** Accumulators inside logic loops.
- **Expected Output (Interactive):**
  ```
  How many numbers to average? 3
  Enter number: 10
  Enter number: 20
  Enter number: 30
  Average is: 20
  ```

---

## 14. `temperature_converter.speak`
Celsius/Fahrenheit temperature conversion scale calculations.
- **Features Demonstrated:** Mathematical formulas and floating-point divisions.
- **Expected Output (Interactive):**
  ```
  Enter Temp in Celsius: 37
  Temp in Fahrenheit: 98.6
  ```

---

## 15. `area_calculator.speak`
Computes areas of standard geometric shapes.
- **Features Demonstrated:** Branching menu loops.
- **Expected Output (Interactive):**
  ```
  Select Shape (1: Circle, 2: Rectangle): 1
  Enter radius: 7
  Area: 153.86
  ```

---

## 16. `fizzbuzz.speak`
Standard FizzBuzz interview exercise.
- **Features Demonstrated:** Modulo arithmetic operators inside `If` branches.
- **Expected Output:**
  ```
  1
  2
  Fizz
  4
  Buzz
  Fizz
  7
  8
  Fizz
  Buzz
  11
  Fizz
  13
  14
  FizzBuzz
  ```

---

## 17. `functions_demo.speak`
Demonstrates custom procedures and parameter scoping.
- **Features Demonstrated:** Global function signatures hoisting, local variables stack protection, parameter passing.
- **Code:**
  ```speakcode
  To perform square with n:
      Give back n times n.
  Finish performance.
  
  Remember 5 as x.
  Perform square with x and save as result.
  Speak "Square of " plus x plus " is " plus result.
  ```
- **Expected Output:**
  ```
  Square of 5 is 25
  ```
