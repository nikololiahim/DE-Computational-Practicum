from dataset import Dataset
from numpy import e, pi, power, exp, log, sin, cos, sqrt, NaN, float_, isnan, isinf, NINF, abs


class SolverException(Exception):
    def __init__(self, msg):
        self.strerror = msg
        self.args = (msg,)


class YAxisDomainException(SolverException):
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
    _max_local_error = NINF

    def validate(self):
        if self.y0 == 0.0:
            raise YAxisDomainException("Given value of y does not belong to the domain!")
        if self.X - self.x0 <= 0:
            raise IntervalException(f"Given [{self.x0} ... {self.X}] interval doesn't exist!")
        if self.N <= 1:
            raise NumberOfStepsException("Given number of steps is invalid!")
        if isnan(self.C) or isinf(self.C):
            raise ConstantException("Value of constant is either too big or can't be calculated!")

    @staticmethod
    def _c(x: float, y: float) -> float_:
        return (1/power(y, 2) - 1) * exp(power(x, 2))

    def y_exact_pos(self, x: float) -> float_:
        return 1 / sqrt(exp(-x*x) * self.C + 1)

    def y_exact_neg(self, x: float) -> float_:
        return - 1 / sqrt(exp(-x * x) * self.C + 1)

    @staticmethod
    def y_prime(x: float, y: float) -> float_:
        return x * (y - power(y, 3))

    def __init__(self, data):
        self.x0 = data["x0"]
        self.y0 = data["y0"]
        self.X = data["X"]
        self.N = int(data["N"])
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
            self.method = self._solve_euler
        elif self.method_code == 2:
            self.method_name = "Improved Euler"
            self.method = self._solve_improved_euler
        else:
            self.method_name = "Runge-Kutta"
            self.method = self._solve_runge_kutta

        self.exact_solution = Dataset(self.N).add_name("Exact Solution")
        self.numerical_solution = Dataset(self.N).add_name(f"Numerical Solution ({self.method_name})")
        self.local_error = Dataset(self.N).add_name(f"Local Error ({self.method_name})")
        self.total_error = Dataset(self.N).add_name(f"Total Error ({self.method_name})")

    def solve_exact(self):
        x = self.x0
        s = self.step
        for i in range(self.N):
            try:
                self.exact_solution.insert(i, (x, self.y_exact(x)))
            except:
                self.exact_solution.insert(i, (x, NaN))
            x += s
        return self.exact_solution

    def solve_numerical(self):
        self.method()
        self._max_local_error = NINF
        self.get_total_error()
        return self.numerical_solution, self.local_error, self.total_error

    def _next_euler(self, x: float, y: float, h: float) -> float:
        return y + h*self.y_prime(x, y)

    def _solve_euler(self):
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        self.numerical_solution.insert(0, (x, y))  # x0 = x0, y0 = y0
        self.local_error.insert(0, (x, 0))
        for i in range(1, N):
            y = self._next_euler(x, y, h)     # next y
            x += h                            # next x
            y_exact = self.y_exact(x)
            error = y_exact - self._next_euler(x, y_exact, h)
            self._max_local_error = abs(error) if abs(error) > self._max_local_error else self._max_local_error
            self.numerical_solution.insert(i, (x, y))
            self.local_error.insert(i, (x, error))

    def _next_improved_euler(self, x, y, h):
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h, y + h * k1)
        return y + (h / 2) * (k1 + k2)

    def _solve_improved_euler(self):
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        self.numerical_solution.insert(0, (x, y))  # x0 = x0, y0 = y0
        self.local_error.insert(0, (x, 0))
        for i in range(1, N):
            y = self._next_improved_euler(x, y, h)  # next y
            x += h  # next x
            y_exact = self.y_exact(x)
            error = y_exact - self._next_improved_euler(x, y_exact, h)
            self._max_local_error = abs(error) if abs(error) > self._max_local_error else self._max_local_error
            self.numerical_solution.insert(i, (x, y))
            self.local_error.insert(i, (x, error))

    def _next_runge_kutta(self, x, y, h):
        k1 = self.y_prime(x, y)
        k2 = self.y_prime(x + h / 2, y + (h / 2) * k1)
        k3 = self.y_prime(x + h / 2, y + (h / 2) * k2)
        k4 = self.y_prime(x + h, y + h * k3)
        return y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    def _solve_runge_kutta(self):
        x = self.x0
        y = self.y0
        N = self.N
        h = self.step
        self.numerical_solution.insert(0, (x, y))  # x0 = x0, y0 = y0
        self.local_error.insert(0, (x, 0))
        for i in range(1, N):
            y = self._next_runge_kutta(x, y, h)  # next y
            x += h  # next x
            y_exact = self.y_exact(x)
            error = y_exact - self._next_runge_kutta(x, y_exact, h)
            self._max_local_error = abs(error) if abs(error) > self._max_local_error else self._max_local_error
            self.numerical_solution.insert(i, (x, y))
            self.local_error.insert(i, (x, error))

    def get_total_error(self):
        # TODO: fix bug with the curve
        N = self.N
        for i in range(2, N + 1):
            self.N = i
            self.method()
            error = self._max_local_error
            self.total_error.insert(i - 2, (i, error))
            self._max_local_error = NINF
        self.N = N

    def __str__(self):
        return f"{{x0: {self.x0},  " + \
               f"y0: {self.y0}, " + \
               f"N: {self.N}, " + \
               f"step: {self.step}, " + \
               f"C: {self.C}}}"

