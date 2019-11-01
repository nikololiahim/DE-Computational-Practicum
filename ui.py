from tkinter import *
from tkinter import messagebox

from math import sqrt, pi, sin, cos, tan, exp



class MainWindow:

    VERSION = "1.0"
    EULER = 1
    IMPROVED_EULER = 2
    RUNGE_KUTTA = 3
    font = ("Consolas", 13)


    @classmethod
    def entry(cls, root: Widget) -> Entry:

        entry = Entry(root, background="bisque", width=10, font=cls.font)
        entry.pack(expand=True, fill=BOTH, side=RIGHT)
        return entry


    @classmethod
    def label(cls, root: Widget, text: str)-> Label:
        font = ("Consolas", 13)
        label = Label(root, text=text, justify=RIGHT, font=cls.font)
        label.pack(expand=True, fill=BOTH)
        return label


    def __init__(self, root: Tk):
        # TODO: fix fonts and colors of labels

        self.root = root
        self.root.title("DE Computational Practicum, v. " + self.VERSION)
        self.root.resizable(True, True)
        self.root.geometry("640x360")


        self.frames = [[None]*12 for i in range(12)]
        # colors = ['snow', 'dim gray', 'blue', 'cyan',
        #           'pale green', 'forest green', 'yellow', 'bisque2',
        #           'SlateBlue1', 'SeaGreen1', 'gold2', 'brown4',
        #           'maroon1', 'magenta2', 'thistle4', 'khaki4']

        # building grid
        colors = ["white", "gray"]
        for i in range(12):
            for j in range(12):
                self.frames[i][j] = Frame(root, background='linen', height=30, width=30)
                self.frames[i][j].grid(row=i, column=j, sticky=N+S+E+W)
                root.grid_columnconfigure(j, weight=1)
                root.grid_rowconfigure(i, weight=1)

        # 'Solutions' label
        self.frames[1][1] = Frame(root, background="bisque", bd=5)
        self.frames[1][1].grid(row=1, column=1, sticky=N+S+E+W, columnspan=5)
        self.solution_label = self.label(self.frames[1][1], text="Solutions")


        # Solutions plot frame
        self.frames[2][1] = Frame(root, background="pale green")
        self.frames[2][1].grid(row=2, column=1, sticky=N+S+E+W, columnspan=5, rowspan=4)

        # Solutions plot
        # TODO: insert plotting widget for solutions

        # 'Errors' label frame
        self.frames[6][1] = Frame(root, background="bisque", bd=5)
        self.frames[6][1].grid(row=6, column=1, sticky=N+S+E+W, columnspan=5)
        self.errors_label = self.label(self.frames[6][1], text="Errors")

        # Errors plot frame
        self.frames[7][1] = Frame(root, background="pale green")
        self.frames[7][1].grid(row=7, column=1, sticky=N+S+E+W, columnspan=5, rowspan=4)

        # Errors plot
        # TODO: insert plotting widget for errors


        names = ["x0", "y0", "X", "N"]
        for i in range(2, 6):
            self.__setattr__(names[i-2]+"_label", self.label(self.frames[i][7], names[i-2]))
            self.frames[i][8] = Frame(root, background="bisque", bd=5)
            self.frames[i][8].grid(row=i, column=8, sticky=N + S + E + W, columnspan=3)
            self.__setattr__(names[i-2]+"_entry", self.entry(self.frames[i][8]))

        # initializing values
        self.x0_entry.insert("0", "0")
        self.y0_entry.insert("0", "sqrt(1/2)")
        self.X_entry.insert("0", "3")
        self.N_entry.insert("0", "3*10**5")

        # laying out radio box
        self.method_selected = IntVar()
        method_names = ["Euler", "Improved Euler", "Runge-Kutta"]
        method_values = [self.EULER, self.IMPROVED_EULER, self.RUNGE_KUTTA]
        for i in range(7, 10):
            self.frames[i][8] = Frame(root, background="white", bd=5)
            self.frames[i][8].grid(row=i, column=7, sticky=N + S + E + W, columnspan=3)
            setattr(self, "method"+str(i-6),
                    Radiobutton(self.frames[i][8],
                                text=method_names[i-7],
                                variable=self.method_selected,
                                value=method_values[i-7],
                                background='white',
                                font=self.font)
                    )
            getattr(self, "method"+str(i-6)).pack(expand=True, anchor=W)

        self.method_selected.set(self.RUNGE_KUTTA)

        # laying out button
        self.apply = Button(self.frames[10][9], text="Apply", command=self.gather_data, font=self.font)
        self.apply.pack(expand=True, fill=BOTH)

        # binding 'Enter' key to 'Apply' button action
        self.root.bind("<Return>", lambda event: self.apply.invoke())


    def gather_data(self):
        names = ["x0", "y0", "X", "N"]
        data = dict()
        for i in names:
            try:
                data[i + "_entry"] =  eval(getattr(self, i + "_entry").get())
            except:
                messagebox.showerror("Input Error", "x0, y0, X or N have incorrect format!")
                break
        else:
            data['method'] = self.method_selected.get()
            for i in data.keys():
                print(i, data[i])
            return data
        return dict()



if __name__ == "__main__":
    root = Tk()
    window = MainWindow(root)
    window.root.mainloop()