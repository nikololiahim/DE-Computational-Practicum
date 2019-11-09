from tkinter import *
from tkinter import messagebox
from solver import *
from plotter import *

matplotlib.use("TkAgg")


class MainWindow:
    _VERSION = "5.0"
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
        colors = ["white", "gray"]
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
        self.solution_plotter.\
            widget.bind(
                "<Button-1>",
                lambda event: self.create_plot_in_a_new_window([Plotter.DEFAULT_DATA1,
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
                             bd=5, command=self.switch_error)
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
                lambda event: self.create_plot_in_a_new_window([Plotter.DEFAULT_DATA1])
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
        self.apply = Button(self.frames[10][10], text="Apply", command=self.solve, font=self._FONT)
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

        # initializing attributes for error type switching
        self.error_flag = 1
        self.local_error = Plotter.DEFAULT_DATA1
        self.total_error = Plotter.DEFAULT_DATA2
        self.current_error = self.local_error

        # binding up and down arrow keys for scrolling through methods
        self.root.bind("<Up>", lambda event: self.move_up())
        self.root.bind("<Down>", lambda event: self.move_down())
        self.root.bind("<Right>", lambda event: self.switch_error())
        self.root.bind("<Left>", lambda event: self.switch_error())

        # binding 'Enter' key to 'Apply' button action
        self.root.bind("<Return>", lambda event: self.apply.invoke())

    # commands associated with widgets
    def switch_error(self):
        if str(self.root.focus_get().__class__) != "<class 'tkinter.Entry'>":
            names = ["local", "total"]
            errors = [self.total_error, self.local_error]
            self.error_flag = ~self.error_flag
            self.switch.configure(text=f"Switch to:\n{names[self.error_flag]} error")
            self.current_error = errors[self.error_flag]
            self.error_plotter.redraw([self.current_error])

    def move_down(self):
        value = self.method_selected.get()
        self.method_selected.set(value + 1 if value < 3 else 1)

    def move_up(self):
        value = self.method_selected.get()
        self.method_selected.set(value - 1 if value > 1 else 3)

    def gather_data(self):
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

    def solve(self):
        input_data = self.gather_data()
        try:
            solver = Solver(input_data)
            exact_solution = solver.solve_exact()
        except NoDataException:
            pass
        except SolverException as exception:
            messagebox.showerror("Error", exception.strerror)
        else:
            numerical_solution_data = solver.solve_numerical()
            solutions = [exact_solution, numerical_solution_data[0]]
            self.local_error = numerical_solution_data[1]
            self.total_error = numerical_solution_data[2]
            self.solution_plotter.redraw(solutions)
            errors = [self.total_error, self.local_error]
            self.error_plotter.redraw([errors[self.error_flag]])
            self.switch.focus_set()

            # rebinding the left mouse button to redraw the graph in a new window for the given data
            self.solution_plotter.widget.bind("<Button-1>",
                                              lambda event: self.create_plot_in_a_new_window(solutions))
            self.error_plotter.widget.bind("<Button-1>",
                                           lambda event: self.create_plot_in_a_new_window([errors[self.error_flag]]))

    def create_plot_in_a_new_window(self, datasets: list):
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
