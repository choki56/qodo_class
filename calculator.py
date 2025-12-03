#!/usr/bin/env python3
"""
Basic Calculator (safe AST-based evaluator)

Features:
- Supports +, -, *, /, parentheses, unary + and -
- Works as a REPL when run without arguments
- Can evaluate a single expression passed as CLI arguments

Usage:
  python calculator.py            # starts interactive mode
  python calculator.py "2 + 3*4"   # evaluates the expression and prints result

Notes:
- Division uses true division (/). Division by zero raises an error message.
- Only arithmetic expressions are allowed; any other Python constructs are rejected.
"""
from __future__ import annotations

import ast
import operator as op
import sys
from typing import Any

# Supported operators mapping
BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
}

UNARY_OPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}


def evaluate(expr: str) -> float:
    """Safely evaluate an arithmetic expression and return a float/int.

    Allowed syntax: numbers, parentheses, +, -, *, /, and unary +/-.
    """
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e.msg}") from None

    def _eval(n: ast.AST) -> Any:
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        # Numbers (Python 3.8+: Constant)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)):
                return n.value
            raise ValueError("Only numeric constants are allowed")
        # Binary operations
        if isinstance(n, ast.BinOp):
            left = _eval(n.left)
            right = _eval(n.right)
            op_type = type(n.op)
            if op_type not in BIN_OPS:
                raise ValueError("Unsupported operator")
            try:
                return BIN_OPS[op_type](left, right)
            except ZeroDivisionError:
                raise ZeroDivisionError("Division by zero") from None
        # Unary operations (+/-)
        if isinstance(n, ast.UnaryOp):
            operand = _eval(n.operand)
            op_type = type(n.op)
            if op_type not in UNARY_OPS:
                raise ValueError("Unsupported unary operator")
            return UNARY_OPS[op_type](operand)
        # Parentheses are represented implicitly by AST structure
        raise ValueError("Unsupported expression")

    return _eval(node)


def repl() -> None:
    print("Basic Calculator. Type 'exit' or Ctrl-D to quit.")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            print()
            break
        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break
        try:
            result = evaluate(line)
            # Print integers without .0
            if isinstance(result, float) and result.is_integer():
                print(int(result))
            else:
                print(result)
        except Exception as e:
            print(f"Error: {e}")


def main(argv: list[str]) -> int:
    if len(argv) == 0:
        repl()
        return 0
    expr = " ".join(argv)
    try:
        result = evaluate(expr)
        if isinstance(result, float) and result.is_integer():
            print(int(result))
        else:
            print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
