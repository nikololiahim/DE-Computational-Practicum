from math import *
import numpy as np


class Data:
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


class Solver:

    @staticmethod
    def _c(x: float, y: float) -> float:
        return ((1 - pow(y, 2)) / pow(y, 2)) * exp(pow(x, 2))

    def y_exact(self, x: float) -> float:
        return 1 / sqrt(exp(-pow(x, 2)) * self.C + 1)

    def y_prime(self, x: float, y: float) -> float:
        return x*y - x*pow(y, 3)

    def __init__(self, data):
        self.x0 = data["x0"]
        self.y0 = data["y0"]
        self.X = data["X"]
        self.N = int(data["N"])
        self.method = int(data["method"])
        self.C = self._c(self.x0, self.y0)
        self.step = abs(self.X-self.x0)/self.N

    def solve_exact(self) -> Data:
        x = self.x0
        s = self.step
        res = Data(self.N)
        for i in range(self.N):
            try:
                res.insert(i, (x, self.y_exact(x)))
            except:
                res.set_error(x)
                res.insert(x, np.NINF)
            x += s
        return res

    def solve_numerical(self) -> Data:
        if self.method == 1:
            return self._solve_euler()
        elif self.method == 2:
            return self._solve_improved_euler()
        elif self.method == 3:
            return self._solve_runge_kutta()
        else:
            return Data(self.N, zeros=True)

    def _solve_euler(self) -> Data:
        res = Data(self.N)
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        res.insert(0, (x, y))                # x0 = x0, y0 = y0
        for i in range(1, N):
            y = y + h*self.y_prime(x, y)     # next y
            x += h                           # next x
            res.insert(i, (x, y))
        return res

    def _solve_improved_euler(self) -> Data:
        res = Data(self.N)
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        res.insert(0, (x, y))
        for i in range(1, N):
            k1 = self.y_prime(x, y)
            k2 = self.y_prime(x + h, y + h*k1)
            y = y + (h/2)*(k1 + k2)
            x += h
            res.insert(i, (x, y))
        return res

    def _solve_runge_kutta(self) -> Data:
        res = Data(self.N)
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        res.insert(0, (x, y))
        for i in range(1, N):
            k1 = self.y_prime(x, y)
            k2 = self.y_prime(x + h/2, y + (h/2)*k1)
            k3 = self.y_prime(x + h/2, y + (h/2)*k2)
            k4 = self.y_prime(x + h, y + h*k3)
            y = y + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
            x += h
            res.insert(i, (x, y))
        return res

    def __str__(self):
        return f"{{x0: {self.x0},  " + \
               f"y0: {self.y0}, " + \
               f"N: {self.N}, " + \
               f"step: {self.step}, " + \
               f"C: {self.C}}}"


