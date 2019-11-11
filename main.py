from ui import *
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# from dataset import Dataset

from tkinter import *
from tkinter import messagebox

from plotter import *
from solver import *

matplotlib.use("TkAgg")

import numpy as np


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
        self.name = "Data"
        self.x_axis_name = "X"
        self.y_axis_name = "Y"

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

    def set_name(self, name):
        self.name = name
        return self

    def set_axes_names(self, xname, yname):
        self.x_axis_name = xname
        self.y_axis_name = yname

    def set_ylim(self, _min, _max):
        self.ymin = _min
        self.ymax = _max


from abc import abstractmethod

import numpy as np
from numpy import power, exp, sqrt


# from dataset import Dataset


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


class MainWindow:
    _VERSION = "6.0"
    _EULER = 1
    _IMPROVED_EULER = 2
    _RUNGE_KUTTA = 3
    _FONT = ("Consolas", 20)

    def _entry(self, root: Widget) -> Entry:
        entry = Entry(root, background="bisque", width=10, font=self._FONT)
        entry.pack(expand=True, fill=BOTH, side=RIGHT)
        return entry

    def _label(self, root: Widget, text: str) -> Label:
        label = Label(root, text=text, justify=RIGHT, font=self._FONT)
        label.pack(expand=True, fill=BOTH)
        return label

    def _place_root(self):
        self.root.title("DE Computational Practicum, v. " + self._VERSION)
        self.root.resizable(True, True)
        self.root.state('zoomed')

    def _place_frames(self):
        self.frames = [[Frame()] * 12 for _ in range(12)]
        for i in range(12):
            for j in range(12):
                self.frames[i][j] = Frame(self.root, background='linen', height=30, width=30)
                self.frames[i][j].grid(row=i, column=j, sticky=N + S + E + W)
                self.frames[i][j].bind("<Button-1>", lambda event: self.frames[i][j].focus_set())
                self.root.grid_columnconfigure(j, weight=1)
                self.root.grid_rowconfigure(i, weight=1)

    def _place_solution_area(self):
        # 'Solutions' label
        self.frames[1][1] = Frame(self.root, background="bisque2", bd=5)
        self.frames[1][1].grid(row=1, column=1, sticky=N + S + E + W, columnspan=5)
        self._label(self.frames[1][1], text="Solutions")

        # Solutions plot frame
        self.frames[2][1] = Frame(self.root, background="lightblue", bd=5)
        self.frames[2][1].grid(row=2, column=1, sticky=N + S + E + W, columnspan=5, rowspan=4)

    def _place_solution_plot(self):
        self.solution_plotter = Plotter(self.frames[2][1])
        self.solution_plotter.plot(Plotter.DEFAULT_DATA1)
        self.solution_plotter.plot(Plotter.DEFAULT_DATA2)
        self.solution_plotter.create_legend()
        self.solution_plotter. \
            widget.bind(
            "<Button-1>",
            lambda event: self._create_plot_in_a_new_window([Plotter.DEFAULT_DATA1,
                                                             Plotter.DEFAULT_DATA2])
        )

    def _place_error_area(self):
        # 'Errors' label frame
        self.frames[6][1] = Frame(self.root, background="bisque2", bd=5)
        self.frames[6][1].grid(row=6, column=1, sticky=N + S + E + W, columnspan=5)

        self.frames[6][1].grid_columnconfigure(0, weight=10)
        self.frames[6][1].grid_columnconfigure(1, weight=1)
        self.frames[6][1].grid_rowconfigure(0, weight=1)
        self.frames[6][1].grid_rowconfigure(1, weight=1)

        left = Label(self.frames[6][1], text="Errors", font=self._FONT)
        right = Frame(self.frames[6][1], bg="bisque2")
        left.grid(row=0, column=0, sticky=N + S + E + W, rowspan=2)
        right.grid(row=0, column=1, sticky=N + S + E + W, rowspan=2)

        # switch button
        self.switch = Button(right,
                             text="Switch to:\ntotal error",
                             font=("Consolas", 8),
                             bg="#EAB4A8",
                             bd=5, command=self._switch_error)
        self.switch.pack(expand=True, fill=BOTH)

        # Errors plot frame
        self.frames[7][1] = Frame(self.root, background="lightblue", bd=5)
        self.frames[7][1].grid(row=7, column=1, sticky=N + S + E + W, columnspan=5, rowspan=4)

    def _place_error_plot(self):
        self.error_plotter = Plotter(self.frames[7][1])
        self.error_plotter.plot(Plotter.DEFAULT_DATA1)
        self.error_plotter.create_legend()
        self.error_plotter. \
            widget.bind(
            "<Button-1>",
            lambda event: self._create_plot_in_a_new_window([Plotter.DEFAULT_DATA1])
        )

    def _place_input_area(self):
        names = ["x0", "y0", "X", "M", "N"]
        for i in range(1, 1 + len(names)):
            self._label(self.frames[i][7], names[i - 1])
            self.frames[i][8] = Frame(self.root, background="bisque", bd=5)
            self.frames[i][8].grid(row=i, column=8, sticky=N + S + E + W, columnspan=3)
            self.__setattr__(names[i - 1] + "_entry", self._entry(self.frames[i][8]))

    # setting input fields to default values
    def _init_input_area(self):
        self.x0_entry.insert("0", "0")
        self.y0_entry.insert("0", "sqrt(1/2)")
        self.X_entry.insert("0", "3")
        self.N_entry.insert("0", "200")
        self.M_entry.insert("0", "20")

    def _place_radiobox(self):
        self.method_selected = IntVar()
        method_names = ["Euler", "Improved Euler", "Runge-Kutta"]
        method_values = [self._EULER, self._IMPROVED_EULER, self._RUNGE_KUTTA]
        for i in range(7, 10):
            self.frames[i][8] = Frame(self.root, background="white", bd=5)
            self.frames[i][8].grid(row=i, column=7,
                                   sticky=N + S + E + W,
                                   columnspan=4)
            Radiobutton(self.frames[i][8],
                        text=method_names[i - 7],
                        variable=self.method_selected,
                        value=method_values[i - 7],
                        background='white',
                        font=self._FONT).pack(expand=True,
                                              anchor=W)

        self.method_selected.set(self._EULER)

    def _place_button(self):
        self.apply = Button(self.frames[10][10], text="Apply", command=self._solve, font=self._FONT)
        self.apply.pack(expand=True, fill=BOTH)

    def __init__(self, root: Tk):
        self.root = root
        self._place_root()
        self._place_frames()
        self._place_solution_area()
        self._place_solution_plot()
        self._place_error_area()
        self._place_error_plot()
        self._place_input_area()
        self._init_input_area()
        self._place_radiobox()
        self._place_button()

        # initializing attributes for error type switching
        self.error_flag = 1
        self.local_error = Plotter.DEFAULT_DATA1
        self.total_error = Plotter.DEFAULT_DATA2
        self.current_error = self.local_error

        # binding up and down arrow keys for scrolling through methods
        self.root.bind("<Up>", lambda event: self._move_up())
        self.root.bind("<Down>", lambda event: self._move_down())
        self.root.bind("<Right>", lambda event: self._switch_error())
        self.root.bind("<Left>", lambda event: self._switch_error())

        # binding 'Enter' key to 'Apply' button action
        self.root.bind("<Return>", lambda event: self.apply.invoke())

    # commands associated with widgets
    def _switch_error(self):
        if str(self.root.focus_get().__class__) != "<class 'tkinter.Entry'>":
            names = ["local", "total"]
            errors = [self.total_error, self.local_error]
            self.error_flag = ~self.error_flag
            self.switch.configure(text=f"Switch to:\n{names[self.error_flag]} error")
            self.current_error = errors[self.error_flag]
            self.error_plotter.redraw([self.current_error])

    def _move_down(self):
        value = self.method_selected.get()
        self.method_selected.set(value + 1 if value < 3 else 1)

    def _move_up(self):
        value = self.method_selected.get()
        self.method_selected.set(value - 1 if value > 1 else 3)

    def _gather_data(self):
        names = ["x0", "y0", "X", "N", "M"]
        data = dict()
        for i in names:
            try:
                data[i] = float(eval(getattr(self, i + "_entry").get()))
            except:
                messagebox.showerror("Input Error", "x0, y0, X or N have incorrect format!")
                break
        else:
            data['method'] = self.method_selected.get()
            return data
        return dict()

    def _solve(self):
        input_data = self._gather_data()
        try:
            solver = Solver(input_data)
            exact_solution = solver.solve_exact()
            numerical_solution_data = solver.solve_numerical()
        except NoDataException:
            pass
        except SolverException as exception:
            messagebox.showerror("Error", exception.strerror)
        else:
            solutions = [exact_solution, numerical_solution_data[0]]
            self.local_error = numerical_solution_data[1]
            self.total_error = numerical_solution_data[2]
            errors = [self.total_error, self.local_error]
            self.solution_plotter.redraw(solutions)
            self.error_plotter.redraw([errors[self.error_flag]])

            # rebinding the left mouse button to redraw the graph in a new window for the given data
            self._rebind(solutions, errors)

    def _create_plot_in_a_new_window(self, datasets: list):
        new_window = Toplevel(self.root)
        new_window.title("Plot")
        new_window.state("zoomed")
        plotter = Plotter(new_window)
        for i in range(len(datasets)):
            plotter.plot(Plotter.EMPTY_DATA)
        plotter.create_legend()
        plotter.redraw(datasets)
        toolbar = NavigationToolbar2Tk(plotter.canvas, new_window)
        toolbar.pack()

    def _rebind(self, solutions, errors):
        self.switch.focus_set()
        self.solution_plotter.widget.bind("<Button-1>",
                                          lambda event: self._create_plot_in_a_new_window(solutions))
        self.error_plotter.widget.bind("<Button-1>",
                                       lambda event: self._create_plot_in_a_new_window([errors[self.error_flag]]))


class Plotter:
    DEFAULT_DATA1 = Dataset(0).from_tuple((range(1, 9), [5, 6, 1, 3, 8, 9, 3, 5]))
    DEFAULT_DATA2 = Dataset(0).from_tuple((DEFAULT_DATA1.x_axis, DEFAULT_DATA1.x_axis))
    EMPTY_DATA = Dataset(1, zeros=True)

    def __init__(self, root):
        self.figure = Figure(figsize=(1, 1), dpi=100)
        self.figure.subplots_adjust(bottom=0.17, left=0.15)
        self.axes = self.figure.add_subplot(111)
        self.plots = []

        self.axes.minorticks_on()
        self.axes.grid(which="major")
        self.axes.grid(which="minor", linestyle=":")
        self._place(root)

    def plot(self, data: Dataset):
        plot, = self.axes.plot(data.x_axis, data.y_axis,
                               label=data.name)
        # marker='.',
        # markersize=5)
        self.plots.append(plot)
        self.canvas.draw()
        return plot

    def redraw(self, data: list):
        labels = []
        for i in range(len(self.plots)):
            self.plots[i].set_data(data[i].x_axis, data[i].y_axis)
            labels.append(data[i].name)
        self.legend = self.axes.legend(labels=labels, loc="upper left")
        self.axes.set_xlabel(data[0].x_axis_name, horizontalalignment="right", x=1.0)
        self.axes.set_ylabel(data[0].y_axis_name)

        self.axes.relim()

        if len(data) > 1:
            ymin, ymax = data[0].ymin, data[0].ymax
            offset = (ymax - ymin) / 10
            self.axes.set_ylim(ymin - offset, ymax + offset)
            self.axes.autoscale(axis="x")
        else:
            self.axes.autoscale()

        self.canvas.draw()

    def _place(self, where):
        self.canvas = FigureCanvasTkAgg(self.figure, where)
        self.canvas.draw()
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill="both", expand=True)

    def create_legend(self):
        self.legend = self.axes.legend(loc="upper left")


if __name__ == "__main__":
    root = Tk()
    window = MainWindow(root)
    window.root.mainloop()
