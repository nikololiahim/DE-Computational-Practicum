import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from solver import Dataset


class Plotter:
    DEFAULT_DATA1 = Dataset(0).from_tuple((range(1, 9), [5, 6, 1, 3, 8, 9, 3, 5]))
    DEFAULT_DATA2 = Dataset(0).from_tuple((DEFAULT_DATA1.x_axis, DEFAULT_DATA1.x_axis))
    EMPTY_DATA = Dataset(1, zeros=True)

    def __init__(self, root):
        self.figure = Figure(figsize=(2, 2), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.plots = []

        self.axes.minorticks_on()
        self.axes.grid(which="major")
        self.axes.grid(which="minor", linestyle=":")
        self._place(root)

    def plot(self, data: Dataset):
        plot, = self.axes.plot(data.x_axis, data.y_axis, label=data.name)
        self.plots.append(plot)
        self.canvas.draw()
        return plot

    def redraw(self, data: list):
        labels = []
        for i in range(len(self.plots)):
            self.plots[i].set_data(data[i].x_axis, data[i].y_axis)
            labels.append(data[i].name)
        self.legend = self.axes.legend(labels=labels, loc="upper left")
        self.axes.relim()
        self.axes.autoscale()
        self.canvas.draw()

    def _place(self, where):
        self.canvas = FigureCanvasTkAgg(self.figure, where)
        self.canvas.draw()
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(fill="both", expand=True)

    def create_legend(self):
        self.legend = self.axes.legend(loc="upper left")
