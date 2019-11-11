from abc import abstractmethod

import numpy as np
from numpy import power, exp, sqrt

from dataset import Dataset


class SolverException(Exception):
    def __init__(self, msg):
        self.strerror = msg
        self.args = (msg,)


class YAxisDomainException(SolverException):
    def __init__(self, msg):
        super().__init__(msg)


class NoDataException(SolverException):
    def __init__(self, msg):
        super().__init__(msg)


class XAxisDomainException(SolverException):
    def __init__(self, msg):
        super().__init__(msg)


class IntervalException(SolverException):
    def __init__(self, msg):
        super().__init__(msg)


class NumberOfStepsException(SolverException):
    def __init__(self, msg):
        super().__init__(msg)


class ConstantException(SolverException):
    def __init__(self, msg):
        super().__init__(msg)


class NumericalMethod:
    name = "Method"

    def __init__(self, y_exact, y_prime):
        self.y_prime = y_prime
        self.y_exact = y_exact

    @abstractmethod
    def next(self, x, y, h):
        pass

    def calculate(self, x, y, N, h):
        _max_local_error = -1
        prev_g_error = 0
        numerical_solution = Dataset(N + 1).set_name(f"Numerical Solution ({self.name})\n{N} steps")
        local_error = Dataset(N + 1).set_name(f"Local Error ({self.name})\n{N} steps")
        local_error.set_axes_names("X", "Local Error")

        for i in range(N + 1):
            y_exact = self.y_exact(x)
            g_error = y_exact - y
            error = prev_g_error - g_error
            _max_local_error = np.abs(error) if np.abs(error) > _max_local_error else _max_local_error
            numerical_solution.insert(i, (x, y))
            local_error.insert(i, (x, error))
            y = self.next(x, y, h)
            x += h
            prev_g_error = g_error
        return _max_local_error, numerical_solution, local_error


class EulerMethod(NumericalMethod):
    name = "Euler"

    def __init__(self, y_exact, y_prime):
        super().__init__(y_exact, y_prime)

    def next(self, x, y, h):
        return y + h * self.y_prime(x, y)


class ImprovedEulerMethod(NumericalMethod):
    name = "Improved Euler"

    def __init__(self, y_exact, y_prime):
        super().__init__(y_exact, y_prime)

    def next(self, x, y, h):
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h, y + h * k1)
        return y + (h / 2) * (k1 + k2)


class RungeKuttaMethod(NumericalMethod):
    name = "Runge-Kutta"

    def __init__(self, y_exact, y_prime):
        super().__init__(y_exact, y_prime)

    def next(self, x, y, h):
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h / 2, y + (h / 2) * k1)
        k3 = self.y_prime(x + h / 2, y + (h / 2) * k2)
        k4 = self.y_prime(x + h, y + h * k3)
        return y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6



class Solver:

    def validate(self):
        if self.y0 == 0.0:
            raise YAxisDomainException("Given value of y does not belong to the domain!")
        if self.X - self.x0 <= 0:
            raise IntervalException(f"Given [x0 ... X] interval doesn't exist!")
        if self.N <= 0 or self.M <= 0:
            raise NumberOfStepsException("Given number of steps is invalid!")
        if self.N < self.M:
            raise NumberOfStepsException(f"Given interval [{self.M} ... {self.N}] is invalid!")
        if np.isnan(self.C) or np.isinf(self.C):
            raise ConstantException("Value of constant is either too big or can't be calculated!")

    @staticmethod
    def _c(x0: float, y0: float) -> np.float_:
        return (1 / power(y0, 2) - 1) * exp(power(x0, 2))

    def y_exact_pos(self, x: float) -> np.float_:
        return 1 / sqrt(exp(-x * x) * self.C + 1)

    def y_exact_neg(self, x: float) -> np.float_:
        return - 1 / sqrt(exp(-x * x) * self.C + 1)

    def y_defined_at(self, x):
        return exp(-x * x) * self.C + 1 > 0

    @staticmethod
    def y_prime(x: float, y: float) -> np.float_:
        return x * (y - power(y, 3))

    def __init__(self, data: dict):
        if not data:
            raise NoDataException("")
        self.x0 = data["x0"]
        self.y0 = data["y0"]
        self.X = data["X"]
        self.N = int(data["N"])
        self.M = int(data["M"])
        self.method_code = int(data["method"])
        self.C = self._c(self.x0, self.y0)
        self.validate()
        self.step = abs(self.X - self.x0) / self.N
        if self.y0 < 0:
            self.y_exact = lambda x: self.y_exact_neg(x)
        else:
            self.y_exact = lambda x: self.y_exact_pos(x)

        if self.method_code == 1:
            self.method = EulerMethod(self.y_exact, self.y_prime)
        elif self.method_code == 2:
            self.method = ImprovedEulerMethod(self.y_exact, self.y_prime)
        else:
            self.method = RungeKuttaMethod(self.y_exact, self.y_prime)

        # initializing datasets
        self.exact_solution = Dataset(self.N + 1).set_name("Exact Solution")
        self.total_error = Dataset(self.N + 1 - self.M).set_name(f"Total Error ({self.method.name})")
        self.total_error.set_axes_names("Steps", "Max Error")

    def solve_exact(self):
        x = self.x0
        s = self.step
        ymin = np.inf
        ymax = np.NINF
        for i in range(self.N + 1):
            if not self.y_defined_at(x):
                raise XAxisDomainException(f"Function is not defined at {x}!")
            y = self.y_exact(x)
            ymin = y if y < ymin else ymin
            ymax = y if y > ymax else ymax
            self.exact_solution.insert(i, (x, y))
            x += s
        self.exact_solution.set_ylim(ymin, ymax)
        return self.exact_solution

    def solve_numerical(self) -> tuple:
        numerical_solution, local_error = self.method.calculate(self.x0, self.y0, self.N, self.step)[1:]
        self._get_total_error()
        return numerical_solution, local_error, self.total_error

    def _get_total_error(self):
        N = self.N
        for i in range(self.M, N + 1):
            self.N = i
            self.step = (self.X - self.x0) / self.N
            error = self.method.calculate(x=self.x0, y=self.y0, N=self.N, h=self.step)[0]
            self.total_error.insert(i - self.M, (i, error))
        self.N = N
        self.step = (self.X - self.x0) / self.N
