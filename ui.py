from tkinter import *



class MainWindow:

    VERSION = "0.0"

    def __init__(self, root: Tk):

        self.root = root
        self.root.title("DE Computational Practicum, v. " + self.VERSION)
        self.root.resizable(True, True)
        self.root.geometry("360x360")


        frames = [None]*144
        colors = ['snow', 'dim gray', 'blue', 'cyan',
                  'pale green', 'forest green', 'yellow', 'bisque2',
                  'SlateBlue1', 'SeaGreen1', 'gold2', 'brown4',
                  'maroon1', 'magenta2', 'thistle4', 'khaki4']
        for i in range(12):
            for j in range(12):
                frames[i+j] = Frame(root, background=colors[(i+j)%12], width=10*3, height=10*3)
                frames[i+j].grid(row=i, column=j, sticky='nsew')
                root.grid_columnconfigure(j, weight=1)
                root.grid_rowconfigure(i, weight=1)






if __name__ == "__main__":
    root = Tk()
    window = MainWindow(root)
    window.root.mainloop()