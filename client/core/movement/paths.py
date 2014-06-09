import numpy as np

class SpiralPath:
    def __init__(self):
        self._x = []
        self._y = []

        clmax = 5
        x = 1
        theta = np.linspace(0, 2*np.pi, 100)+10*0.4*np.pi/clmax + 2*np.pi*x/clmax
        r = np.linspace(0, 600, 100)

        for x in ((r*np.cos(theta))+300)[30:90]:
            self._x.append(x)

        for y in (r*np.sin(theta))[30:90]:
            self._y.append(y)

    @property
    def length(self):
        return len(self._x)

    def x(self, pos):
        return self._x[pos]

    def xs(self):
        return self._x

    def y(self, pos):
        return self._y[pos]

    def ys(self):
        return self._y

    def xys(self):
        return zip(self._x, self._y)