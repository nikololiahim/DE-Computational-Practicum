from tkinter import *
from tkinter import messagebox
from solver import *
from plotter import *


class MainWindow:
    _VERSION = "3.0"
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
        self.frames = [[Frame()] * 12 for i in range(12)]
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
        errors_label = self._label(self.frames[6][1], text="Errors")

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
        names = ["x0", "y0", "X", "N"]
        for i in range(2, 6):
            self._label(self.frames[i][7], names[i - 2])
            self.frames[i][8] = Frame(self.root, background="bisque", bd=5)
            self.frames[i][8].grid(row=i, column=8, sticky=N + S + E + W, columnspan=3)
            self.__setattr__(names[i - 2] + "_entry", self._entry(self.frames[i][8]))

    # setting input fields to default values
    def _init_input_area(self):
        self.x0_entry.insert("0", "0")
        self.y0_entry.insert("0", "sqrt(1/2)")
        self.X_entry.insert("0", "3")
        self.N_entry.insert("0", "20")

    def _place_radiobox(self):
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

        # binding up and down arrow keys for scrolling through methods
        self.root.bind("<Up>", lambda event: self.move_up())
        self.root.bind("<Down>", lambda event: self.move_down())

        # binding 'Enter' key to 'Apply' button action
        self.root.bind("<Return>", lambda event: self.apply.invoke())

    def move_down(self):
        value = self.method_selected.get()
        self.method_selected.set(value + 1 if value < 3 else 1)

    def move_up(self):
        value = self.method_selected.get()
        self.method_selected.set(value - 1 if value > 1 else 3)

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
        if int(data["N"]) <= 0:
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
            error = [numerical_solution_and_error[1]]
            solutions = [exact_solution, numerical_solution]
            self.solution_plotter.redraw(solutions)
            self.error_plotter.redraw(error)
            self.solution_plotter.widget.bind("<Button-1>",
                                      lambda event: self.create_plot_in_a_new_window(solutions))
            self.error_plotter.widget.bind("<Button-1>",
                                   lambda event: self.create_plot_in_a_new_window(error))
        else:
            messagebox.showerror("Error", "Given data is invalid!")

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


if __name__ == "__main__":
    matplotlib.use("TkAgg")
    root = Tk()
    window = MainWindow(root)
    print(list(filter(lambda x: not x.startswith("_"), dir(window))))
    window.root.mainloop()