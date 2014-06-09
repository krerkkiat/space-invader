from core.movement.paths import SpiralPath

class Movement:
    def __init__(self, path, start=0):
        self._path = path
        self._currentPos = start-1

    def move(self):
        self._currentPos += 1

        if self._currentPos >= self._path.length:
            self._currentPos = 0

        if self._currentPos >= 0:
            return (self._path.x(self._currentPos), self._path.y(self._currentPos))
        else:
            return (-100, -100)