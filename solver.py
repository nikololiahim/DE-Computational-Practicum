from dataset import Dataset
from numpy import e, pi, power, exp, log, sin, cos, sqrt, NaN, float_, isnan, isinf, NINF, abs


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


class Solver:

    def validate(self):
        if self.y0 == 0.0:
            raise YAxisDomainException("Given value of y does not belong to the domain!")
        if self.X - self.x0 <= 0:
            raise IntervalException(f"Given [x0 ... X] interval doesn't exist!")
        if self.N <= 0:
            raise NumberOfStepsException("Given number of steps is invalid!")
        if self.N <= self.M:
            raise NumberOfStepsException(f"Given interval [{self.M} ... {self.N}] is invalid!")
        if isnan(self.C) or isinf(self.C):
            raise ConstantException("Value of constant is either too big or can't be calculated!")

    @staticmethod
    def _c(x0: float, y0: float) -> float_:
        return (1 / power(y0, 2) - 1) * exp(power(x0, 2))

    def y_exact_pos(self, x: float) -> float_:
        return 1 / sqrt(exp(-x*x) * self.C + 1)

    def y_exact_neg(self, x: float) -> float_:
        return - 1 / sqrt(exp(-x * x) * self.C + 1)

    def y_defined_at(self, x):
        return exp(-x * x) * self.C + 1 > 0

    @staticmethod
    def y_prime(x: float, y: float) -> float_:
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
            self.method_name = "Euler"
            self.method = self._next_euler
        elif self.method_code == 2:
            self.method_name = "Improved Euler"
            self.method = self._next_improved_euler
        else:
            self.method_name = "Runge-Kutta"
            self.method = self._next_runge_kutta

        # initializing datasets
        self.exact_solution = Dataset(self.N + 1).set_name("Exact Solution")
        self.numerical_solution = Dataset(self.N + 1).set_name(f"Numerical Solution ({self.method_name})\n"
                                                               f"{self.N} steps")

        self.local_error = Dataset(self.N + 1).set_name(f"Local Error ({self.method_name})\n"
                                                        f"{self.N} steps")
        self.local_error.set_axes_names("X", "Local Error")
        self.total_error = Dataset(self.N + 1 - self.M).set_name(f"Total Error ({self.method_name})")
        self.total_error.set_axes_names("Steps", "Max Error")

    def solve_exact(self) -> Dataset:
        x = self.x0
        s = self.step
        for i in range(self.N + 1):
            if not self.y_defined_at(x):
                raise XAxisDomainException(f"Function is not defined at {x}!")
            self.exact_solution.insert(i, (x, self.y_exact(x)))
            x += s
        return self.exact_solution

    def solve_numerical(self) -> tuple:
        self.calculate_numerical()
        self.get_total_error()
        return self.numerical_solution, self.local_error, self.total_error

    def calculate_numerical(self, write=True) -> float:
        _max_local_error = -1
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        if write:
            self.numerical_solution.insert(0, (x, y))
            self.local_error.insert(0, (x, 0))
        for i in range(1, N + 1):
            y = self.method(x, y, h)
            x += h
            y_exact = self.y_exact(x)
            error = y_exact - self.method(x, y_exact, h)
            _max_local_error = abs(error) if abs(error) > _max_local_error else _max_local_error
            if write:
                self.numerical_solution.insert(i, (x, y))
                self.local_error.insert(i, (x, error))
        return _max_local_error

    def _next_euler(self, x: float, y: float, h: float) -> float:
        return y + h * self.y_prime(x, y)

    def _next_improved_euler(self, x, y, h) -> float:
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h, y + h * k1)
        return y + (h / 2) * (k1 + k2)

    def _next_runge_kutta(self, x, y, h) -> float:
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h / 2, y + (h / 2) * k1)
        k3 = self.y_prime(x + h / 2, y + (h / 2) * k2)
        k4 = self.y_prime(x + h, y + h * k3)
        return y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    def get_total_error(self):
        # TODO: fix bug with the curve
        N = self.N
        for i in range(self.M, N + 1):
            self.N = i
            self.step = (self.X - self.x0) / self.N
            error = self.calculate_numerical()
            self.total_error.insert(i - self.M, (i, error))
        self.N = N
        self.step = (self.X - self.x0) / self.N
