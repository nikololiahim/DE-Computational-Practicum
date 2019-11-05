from dataset import Dataset
from numpy import e, pi, power, exp, log, sin, cos, sqrt, NaN


class InvalidDataException(Exception):
    def __init__(self, arg):
        self.strerror = arg
        self.args = (arg,)


class Solver:

    @staticmethod
    def valid(data):
        if data["y0"] <= 0.0:
            return False
        if data["x0"] >= data["X"]:
            return False
        if not data["N"].is_integer():
            return False
        if int(data["N"]) <= 1:
            return False
        return True

    @staticmethod
    def _c(x: float, y: float) -> float:
        return (1/power(y, 2) - 1) * exp(power(x, 2))

    def y_exact(self, x: float) -> float:
        return 1 / sqrt(exp(-x*x) * self.C + 1)

    @staticmethod
    def y_prime(x: float, y: float) -> float:
        return x * (y - power(y, 3))

    def __init__(self, data):
        if not self.valid(data):
            raise InvalidDataException("Data you've given is invalid!")
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
                res.set_error(i)
                res.insert(i, (x, NaN))
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

