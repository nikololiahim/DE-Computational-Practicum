from tkinter import *
from tkinter import messagebox
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from solver import *


class MainWindow:
    _VERSION = "1.0"
    _EULER = 1
    _IMPROVED_EULER = 2
    _RUNGE_KUTTA = 3
    _FONT = ("Consolas", 20)
    _DEFAULT_DATA = Data(0).from_tuple((range(1, 9), [5, 6, 1, 3, 8, 9, 3, 5]))

    @classmethod
    def _entry(cls, root: Widget) -> Entry:
        entry = Entry(root, background="bisque", width=10, font=cls._FONT)
        entry.pack(expand=True, fill=BOTH, side=RIGHT)
        return entry

    @classmethod
    def _label(cls, root: Widget, text: str) -> Label:
        label = Label(root, text=text, justify=RIGHT, font=cls._FONT)
        label.pack(expand=True, fill=BOTH)
        return label

    def _place_root(self):
        self.root.title("DE Computational Practicum, v. " + self._VERSION)
        self.root.resizable(True, True)
        self.root.state('zoomed')

    def _place_frames(self):
        self.frames = [[Frame()] * 12 for i in range(12)]
        # colors = ['snow', 'dim gray', 'blue', 'cyan',
        #           'pale green', 'forest green', 'yellow', 'bisque2',
        #           'SlateBlue1', 'SeaGreen1', 'gold2', 'brown4',
        #           'maroon1', 'magenta2', 'thistle4', 'khaki4']

        # building grid
        colors = ["white", "gray"]
        for i in range(12):
            for j in range(12):
                self.frames[i][j] = Frame(self.root, background='linen', height=30, width=30)
                self.frames[i][j].grid(row=i, column=j, sticky=N + S + E + W)
                self.root.grid_columnconfigure(j, weight=1)
                self.root.grid_rowconfigure(i, weight=1)

    def _place_solution_area(self):
        # 'Solutions' label
        self.frames[1][1] = Frame(self.root, background="bisque2", bd=5)
        self.frames[1][1].grid(row=1, column=1, sticky=N + S + E + W, columnspan=5)
        solution_label = self._label(self.frames[1][1], text="Solutions")

        # Solutions plot frame
        self.frames[2][1] = Frame(self.root, background="lightblue", bd=5)
        self.frames[2][1].grid(row=2, column=1, sticky=N + S + E + W, columnspan=5, rowspan=4)

    def _place_solution_plot(self):
        # Solutions plot
        # TODO: insert plotting widget for solutions
        self.solution = Figure(figsize=(2, 2), dpi=100)
        self.solution_axes = self.solution.add_subplot(111)
        self.solution_axes.minorticks_on()
        self.solution_axes.grid(which="major")
        self.solution_axes.grid(which="minor", linestyle=":")
        self.exact_solution_plot, = self.solution_axes.plot(self._DEFAULT_DATA.x_axis, self._DEFAULT_DATA.y_axis)
        self.numerical_solution_plot, = self.solution_axes.plot(self._DEFAULT_DATA.x_axis, self._DEFAULT_DATA.x_axis)

        data = (self._DEFAULT_DATA, Data(0).from_tuple((range(1, 9), range(1, 9))))
        self.solution_canvas = FigureCanvasTkAgg(self.solution, self.frames[2][1])
        self.solution_canvas.draw()
        self.solution_widget = self.solution_canvas.get_tk_widget()
        self.solution_widget.pack(fill=BOTH, expand=True)
        self.solution_widget.bind("<Button-1>", lambda event: self.create_plot_in_a_new_window(data))

    def _place_error_area(self):
        # 'Errors' label frame
        self.frames[6][1] = Frame(self.root, background="bisque2", bd=5)
        self.frames[6][1].grid(row=6, column=1, sticky=N + S + E + W, columnspan=5)
        errors_label = self._label(self.frames[6][1], text="Errors")

        # Errors plot frame
        self.frames[7][1] = Frame(self.root, background="lightblue", bd=5)
        self.frames[7][1].grid(row=7, column=1, sticky=N + S + E + W, columnspan=5, rowspan=4)

    def _place_error_plot(self):
        # Errors plot
        # TODO: insert plotting widget for errors
        self.error = Figure(figsize=(2, 2), dpi=100)
        self.error_axes = self.error.add_subplot(111)
        self.error_axes.minorticks_on()
        self.error_axes.grid(which="major")
        self.error_axes.grid(which="minor", linestyle=":")
        self.error_plot, = self.error_axes.plot(self._DEFAULT_DATA.x_axis, self._DEFAULT_DATA.y_axis)

        self.error_canvas = FigureCanvasTkAgg(self.error, self.frames[7][1])
        self.error_canvas.draw()
        self.error_widget = self.error_canvas.get_tk_widget()
        self.error_widget.pack(fill=BOTH, expand=True)
        self.error_widget.bind("<Button-1>", lambda event: self.create_plot_in_a_new_window([self._DEFAULT_DATA]))

    def _place_input_area(self):
        names = ["x0", "y0", "X", "N"]
        for i in range(2, 6):
            self._label(self.frames[i][7], names[i - 2])
            self.frames[i][8] = Frame(self.root, background="bisque", bd=5)
            self.frames[i][8].grid(row=i, column=8, sticky=N + S + E + W, columnspan=3)
            self.__setattr__(names[i - 2] + "_entry", self._entry(self.frames[i][8]))

    def _init_input_area(self):
        # initializing values
        self.x0_entry.insert("0", "0")
        self.y0_entry.insert("0", "sqrt(1/2)")
        self.X_entry.insert("0", "3")
        self.N_entry.insert("0", "1e5")

    def _place_radiobox(self):
        # laying out radio box
        self.method_selected = IntVar()
        method_names = ["Euler", "Improved Euler", "Runge-Kutta"]
        method_values = [self._EULER, self._IMPROVED_EULER, self._RUNGE_KUTTA]
        for i in range(7, 10):
            self.frames[i][8] = Frame(self.root, background="white", bd=5)
            self.frames[i][8].grid(row=i, column=7,
                                   sticky=N + S + E + W,
                                   columnspan=3)
            Radiobutton(self.frames[i][8],
                        text=method_names[i - 7],
                        variable=self.method_selected,
                        value=method_values[i - 7],
                        background='white',
                        font=self._FONT).pack(expand=True,
                                              anchor=W)

        self.method_selected.set(self._RUNGE_KUTTA)

    def _place_button(self):
        # laying out button
        self.apply = Button(self.frames[10][9], text="Apply", command=self.solve, font=self._FONT)
        self.apply.pack(expand=True, fill=BOTH)

    def __init__(self, root: Tk):
        # TODO: fix fonts and colors of labels

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

        # binding 'Enter' key to 'Apply' button action
        self.root.bind("<Return>", lambda event: self.apply.invoke())

    def draw_plot(self, axes, line, canvas, data: Data):
        line.set_data(data.x_axis, data.y_axis)
        axes.relim()
        axes.autoscale()
        canvas.draw()

    def gather_data(self):
        names = ["x0", "y0", "X", "N"]
        data = dict()
        for i in names:
            try:
                data[i] = float(eval(getattr(self, i + "_entry").get()))
            except:
                messagebox.showerror("Input Error", "x0, y0, X or N have incorrect format!")
                break
        else:
            data['method'] = self.method_selected.get()
            for i in data.keys():
                print(i, data[i])
            return data
        return dict()

    def valid(self, data):
        if data["y0"] <= 0.0:
            return False
        if data["x0"] >= data["X"]:
            return False
        if not data["N"].is_integer():
            return False
        if int(data["N"]) == 0:
            return False
        return True

    def solve(self):
        input_data = self.gather_data()
        if self.valid(input_data):
            solver = Solver(input_data)
            print(solver)
            exact_solution = solver.solve_exact()
            numerical_solution_and_error = solver.solve_numerical()
            numerical_solution = numerical_solution_and_error[0]
            approximation_error = numerical_solution_and_error[1]
            solutions = [exact_solution, numerical_solution]
            self.draw_plot(self.solution_axes, self.exact_solution_plot, self.solution_canvas, solutions[0])
            self.draw_plot(self.solution_axes, self.numerical_solution_plot, self.solution_canvas, solutions[1])
            self.draw_plot(self.error_axes, self.error_plot, self.error_canvas, approximation_error)
            self.solution_widget.bind("<Button-1>", lambda event: self.create_plot_in_a_new_window(solutions))
            self.error_widget.bind("<Button-1>", lambda event: self.create_plot_in_a_new_window([approximation_error]))
        else:
            messagebox.showerror("Error", "Given data is invalid!")

    def create_plot_in_a_new_window(self, datasets: list):
        new_window = Toplevel(self.root)
        new_window.title("Plot")
        new_window.state("zoomed")
        fig = Figure(figsize=(5, 5), dpi=100)
        axes = fig.add_subplot(111)
        axes.grid(which="major")
        axes.minorticks_on()
        axes.grid(which="minor", linestyle=":")
        for i in range(len(datasets)):
            axes.plot(datasets[i].x_axis, datasets[i].y_axis)
        canvas = FigureCanvasTkAgg(fig, new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.pack()


if __name__ == "__main__":
    matplotlib.use("TkAgg")
    root = Tk()
    window = MainWindow(root)
    print(list(filter(lambda x: not x.startswith("_"), dir(window))))
    window.root.mainloop()