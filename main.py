import ui
import solver



if __name__ == "__main__":
    from tkinter import *

    root = Tk()


    def clear():
        list = root.grid_slaves()
        for l in list:
            l.destroy()


    Label(root, text='Hello World!').grid(row=0)
    Button(root, text='Clear', command=clear).grid(row=1)

    root.mainloop()
