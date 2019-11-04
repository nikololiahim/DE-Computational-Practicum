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
        self.error = np.zeros(size)
        self.name = "Data"

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

    def set_error(self, index: int):
        if -1 < index < self.size:
            self.error[index] = 1
        else:
            raise IndexError("Index is out of bounds!")

    def add_name(self, name):
        self.name = name
        return self
