from math import *


class Solver:

    @staticmethod
    def c(x: float, y: float):
        return (1 / (y*y) - 1)*exp(x*x)

    @staticmethod
    def y(x: float, c: float):
        return 1 / (exp(-x * x) * c + 1)

    def __init__(self, data):
        self.x = data["x0"]
        self.y = data["y0"]
        self.X = data["X"]
        self.N = data["N"]
        self.method = data["method"]

    def solve_exact(self) -> dict:
        pass

    def solve_numeric(self) -> dict:
        pass
