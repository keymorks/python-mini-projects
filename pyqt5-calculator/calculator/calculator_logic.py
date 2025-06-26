from typing import List

class CalculatorLogic():
    def a(self, tokens: List[str]) -> float:
        result = self.b(tokens)
        while len(tokens) > 0 and tokens[0] in ("+", "-"):
            token = tokens.pop(0)
            right = self.b(tokens)
            if token == "+":
                result += right
            else:
                result -= right
        return result

    def b(self, tokens: List[str]) -> float:
        result = self.c(tokens)
        while len(tokens) > 0 and tokens[0] in ("*", "/"):
            token = tokens.pop(0)
            right = self.c(tokens)
            if token == "*":
                result *= right
            else:
                result /= right
        return result

    def c(self, tokens: List[str]) -> float:
        token = tokens.pop(0)
        if token == "(":
            result = self.a(tokens)
            tokens.pop(0)
        else:
            result = float(token)
        return result