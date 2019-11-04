from math import *
import numpy as np
from abc import abstractmethod

class Dataset:
    def __init__(self, size: int, zeros=False):
        if not zeros:
            self.size = size
            self.x_axis = np.empty(size)
            self.y_axis = np.empty(size)
        else:
            self.size = size
            self.x_axis = np.zeros(size)
            self.y_axis = np.zeros(size)
        self.error = np.zeros(size)
        self.name = "Data"

    def from_tuple(self, iterable: tuple):
        self.__init__(len(iterable[0]))
        for i in range(self.size):
            self.x_axis[i] = iterable[0][i]
            self.y_axis[i] = iterable[1][i]
        return self

    def insert(self, index: int, value: tuple):
        if -1 < index < self.size:
            self.x_axis[index] = value[0]
            self.y_axis[index] = value[1]
        else:
            raise IndexError("Index is out of bounds!")

    def set_error(self, index: int):
        if -1 < index < self.size:
            self.error[index] = 1
        else:
            raise IndexError("Index is out of bounds!")

    def add_name(self, name):
        self.name = name
        return self


class Solver:

    @staticmethod
    def _c(x: float, y: float) -> float:
        return (1/pow(y, 2) - 1) * exp(pow(x, 2))

    def y_exact(self, x: float) -> float:
        return 1 / sqrt(exp(-pow(x, 2)) * self.C + 1)

    @staticmethod
    def y_prime(x: float, y: float) -> float:
        return x * (y - pow(y, 3))

    def __init__(self, data):
        self.x0 = data["x0"]
        self.y0 = data["y0"]
        self.X = data["X"]
        self.N = int(data["N"])
        self.method = int(data["method"])
        self.C = self._c(self.x0, self.y0)
        self.step = abs(self.X-self.x0)/self.N

    def solve_exact(self) -> Dataset:
        x = self.x0
        s = self.step
        res = Dataset(self.N)
        res.add_name("Exact Solution")
        for i in range(self.N):
            try:
                res.insert(i, (x, self.y_exact(x)))
            except:
                res.set_error(x)
                res.insert(x, np.NINF)
            x += s
        return res

    def solve_numerical(self) -> tuple:
        if self.method == 1:
            sol = self._solve_euler()
            method_name = "Euler"
            sol[0].add_name(f"Numerical solution ({method_name})")
            sol[1].add_name(f"Local Error ({method_name})")
            return sol
        elif self.method == 2:
            sol = self._solve_improved_euler()
            method_name = "Improved Euler"
            sol[0].add_name(f"Numerical solution ({method_name})")
            sol[1].add_name(f"Local Error ({method_name})")
            return sol
        elif self.method == 3:
            sol = self._solve_runge_kutta()
            method_name = "Runge-Kutta"
            sol[0].add_name(f"Numerical solution ({method_name})")
            sol[1].add_name(f"Local Error ({method_name})")
            return sol
        else:
            return Dataset(self.N, zeros=True), Dataset(self.N, zeros=True)

    def _next_euler(self, x: float, y: float, h: float) -> float:
        return y + h*self.y_prime(x, y)

    def _solve_euler(self) -> tuple:
        res = Dataset(self.N)
        errors = Dataset(self.N)
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        res.insert(0, (x, y))  # x0 = x0, y0 = y0
        errors.insert(0, (x, 0))
        for i in range(1, N):
            y = self._next_euler(x, y, h)     # next y
            x += h                            # next x
            y_exact = self.y_exact(x)
            error = y_exact - self._next_euler(x, y_exact, h)
            errors.insert(i, (x, error))
            res.insert(i, (x, y))

        return res, errors

    def _next_improved_euler(self, x, y, h):
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h, y + h * k1)
        return y + (h / 2) * (k1 + k2)

    def _solve_improved_euler(self) -> tuple:
        res = Dataset(self.N)
        errors = Dataset(self.N)
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        res.insert(0, (x, y))
        errors.insert(0, (x, 0))
        for i in range(1, N):
            y = self._next_improved_euler(x, y, h)
            y_exact = self.y_exact(x)
            error = y_exact - self._next_improved_euler(x, y_exact, h)
            x += h
            errors.insert(i, (x, error))
            res.insert(i, (x, y))
        return res, errors

    def _next_runge_kutta(self, x, y, h):
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h / 2, y + (h / 2) * k1)
        k3 = self.y_prime(x + h / 2, y + (h / 2) * k2)
        k4 = self.y_prime(x + h, y + h * k3)
        return y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    def _solve_runge_kutta(self) -> tuple:
        res = Dataset(self.N)
        errors = Dataset(self.N)
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        errors.insert(0, (x, 0))
        res.insert(0, (x, y))
        for i in range(1, N):
            y = self._next_runge_kutta(x, y, h)
            y_exact = self.y_exact(x)
            error = y_exact - self._next_runge_kutta(x, y_exact, h)
            x += h
            errors.insert(i, (x, error))
            res.insert(i, (x, y))
        return res, errors

    def __str__(self):
        return f"{{x0: {self.x0},  " + \
               f"y0: {self.y0}, " + \
               f"N: {self.N}, " + \
               f"step: {self.step}, " + \
               f"C: {self.C}}}"

