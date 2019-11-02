from math import *


class Solver:

    @staticmethod
    def _c(x: float, y: float):
        return ( (1/(y*y)) - 1) * exp(x*x)

    def y_exact(self, x: float):
        return 1 / sqrt((exp(-x * x) * self.C + 1))

    def __init__(self, data):
        self.x0 = data["x0"]
        self.y0 = data["y0"]
        self.X = data["X"]
        self.N = data["N"]
        self.method = data["method"]
        self.C = self._c(self.x0, self.y0)
        self.step = abs(self.X-self.x0)/self.N

    def solve_exact(self) -> dict:
        x = self.x0
        X = self.X
        s = self.step
        res = dict()
        while x < X:
            try:
                res[x] = self.y_exact(x)
            except:
                res[x] = res[x-s]
            x += s
        return res


    def solve_numeric(self) -> dict:
        pass

    def _solve_euler(self) -> dict:
        pass

    def _solve_improved_euler(self) -> dict:
        pass

    def _solve_runge_kutta(self) -> dict:
        pass



