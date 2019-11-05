from ui import *


if __name__ == "__main__":
    root = Tk()
    window = MainWindow(root)
    print(list(filter(lambda x: not x.startswith("_"), dir(window))))
    window.root.mainloop()
