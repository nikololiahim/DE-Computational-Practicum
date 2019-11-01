from tkinter import *
from tkinter import messagebox

import matplotlib

matplotlib.use("TkAgg")
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

    @classmethod
    def entry(cls, root: Widget) -> Entry:
        entry = Entry(root, background="bisque", width=10, font=cls._FONT)
        entry.pack(expand=True, fill=BOTH, side=RIGHT)
        return entry

    @classmethod
    def label(cls, root: Widget, text: str) -> Label:
        label = Label(root, text=text, justify=RIGHT, font=cls._FONT)
        label.pack(expand=True, fill=BOTH)
        return label

    def __init__(self, root: Tk):
        # TODO: fix fonts and colors of labels

        self.root = root
        self.root.title("DE Computational Practicum, v. " + self._VERSION)
        self.root.resizable(True, True)
        self.root.state('zoomed')

        self.frames = [[None] * 12 for i in range(12)]
        # colors = ['snow', 'dim gray', 'blue', 'cyan',
        #           'pale green', 'forest green', 'yellow', 'bisque2',
        #           'SlateBlue1', 'SeaGreen1', 'gold2', 'brown4',
        #           'maroon1', 'magenta2', 'thistle4', 'khaki4']

        # building grid
        colors = ["white", "gray"]
        for i in range(12):
            for j in range(12):
                self.frames[i][j] = Frame(root, background='linen', height=30, width=30)
                self.frames[i][j].grid(row=i, column=j, sticky=N + S + E + W)
                root.grid_columnconfigure(j, weight=1)
                root.grid_rowconfigure(i, weight=1)

        # 'Solutions' label
        self.frames[1][1] = Frame(root, background="bisque", bd=5)
        self.frames[1][1].grid(row=1, column=1, sticky=N + S + E + W, columnspan=5)
        self.solution_label = self.label(self.frames[1][1], text="Solutions")

        # Solutions plot frame
        self.frames[2][1] = Frame(root, background="lightblue", bd=5)
        self.frames[2][1].grid(row=2, column=1, sticky=N + S + E + W, columnspan=5, rowspan=4)

        # Solutions plot
        # TODO: insert plotting widget for solutions
        self.solution = Figure(figsize=(4, 4), dpi=100)
        self.solution.add_subplot(111).plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        self.solution.add_subplot(111).plot([1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8])
        self.solution_canvas = FigureCanvasTkAgg(self.solution, self.frames[2][1])
        self.solution_canvas.draw()
        self.solution_plot = self.solution_canvas.get_tk_widget()
        self.solution_plot.pack(fill=BOTH, expand=True)
        self.solution_plot.bind("<Button-1>", lambda event: self.create_in_a_new_window(self.solution))

        # 'Errors' label frame
        self.frames[6][1] = Frame(root, background="bisque", bd=5)
        self.frames[6][1].grid(row=6, column=1, sticky=N + S + E + W, columnspan=5)
        self.errors_label = self.label(self.frames[6][1], text="Errors")

        # Errors plot frame
        self.frames[7][1] = Frame(root, background="lightblue", bd=5)
        self.frames[7][1].grid(row=7, column=1, sticky=N + S + E + W, columnspan=5, rowspan=4)

        # Errors plot
        # TODO: insert plotting widget for errors
        self.error = Figure(figsize=(4, 4), dpi=100)
        self.error.add_subplot(111).plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        self.error_canvas = FigureCanvasTkAgg(self.error, self.frames[7][1])
        self.error_canvas.draw()
        self.error_plot = self.error_canvas.get_tk_widget()
        self.error_plot.pack(fill=BOTH, expand=True)
        self.error_plot.bind("<Button-1>", lambda event: self.create_in_a_new_window(self.error))

        names = ["x0", "y0", "X", "N"]
        for i in range(2, 6):
            self.__setattr__(names[i - 2] + "_label", self.label(self.frames[i][7], names[i - 2]))
            self.frames[i][8] = Frame(root, background="bisque", bd=5)
            self.frames[i][8].grid(row=i, column=8, sticky=N + S + E + W, columnspan=3)
            self.__setattr__(names[i - 2] + "_entry", self.entry(self.frames[i][8]))

        # initializing values
        self.x0_entry.insert("0", "0")
        self.y0_entry.insert("0", "sqrt(1/2)")
        self.X_entry.insert("0", "3")
        self.N_entry.insert("0", "3*10**5")

        # laying out radio box
        self.method_selected = IntVar()
        method_names = ["Euler", "Improved Euler", "Runge-Kutta"]
        method_values = [self._EULER, self._IMPROVED_EULER, self._RUNGE_KUTTA]
        for i in range(7, 10):
            self.frames[i][8] = Frame(root, background="white", bd=5)
            self.frames[i][8].grid(row=i, column=7, sticky=N + S + E + W, columnspan=3)
            setattr(self, "method" + str(i - 6),
                    Radiobutton(self.frames[i][8],
                                text=method_names[i - 7],
                                variable=self.method_selected,
                                value=method_values[i - 7],
                                background='white',
                                font=self._FONT)
                    )
            getattr(self, "method" + str(i - 6)).pack(expand=True, anchor=W)

        self.method_selected.set(self._RUNGE_KUTTA)

        # laying out button
        self.apply = Button(self.frames[10][9], text="Apply", command=self.gather_data, font=self._FONT)
        self.apply.pack(expand=True, fill=BOTH)

        # binding 'Enter' key to 'Apply' button action
        self.root.bind("<Return>", lambda event: self.apply.invoke())

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

    def create_in_a_new_window(self, fig):
        new_window = Toplevel(self.root)
        new_window.title("Plot")
        new_window.state("zoomed")
        canvas = FigureCanvasTkAgg(fig, new_window)
        canvas.draw()
        plot = canvas.get_tk_widget()
        plot.pack(fill=BOTH, expand=True)


if __name__ == "__main__":
    root = Tk()
    window = MainWindow(root)
    window.root.mainloop()
