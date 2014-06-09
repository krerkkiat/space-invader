import pygame

from config import Config
from core.ui import Table, Button
from core.scene import Scene
from core.manager import SceneManager
from core.scene.preload import Preload

class SummaryScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self._background = pygame.display.get_surface()
        self._background.set_alpha(180)
        self._background.fill(Config.colors['black'])
        self._elements.clear(self._canvas, self._background)

        w, h = (200, 200)
        rowData = [('Score', 'Wave'), (str(self._parent._pilot.score), str(self._parent._pilot.wave))]
        columnWidth = [100, 100]
        self._scoreBoard = Table(self, w, h, rowData, columnWidth, title='Summary', line=False, button=False)
        self._scoreBoard.rect.centerx = Config.windowWidth//2
        self._scoreBoard.rect.centery = Config.windowHeight//2
        self.addElement(self._scoreBoard)

        def callBack():
            # SceneManager.call(MainScene(self._parent), Preload(self._parent))
            self._parent._pilot.update()
            SceneManager.ret(Preload(self._parent))
        self._btn = Button(self, 'Continue', callBack)
        self._btn.rect.right = self._scoreBoard.rect.right
        self._btn.rect.top = self._scoreBoard.rect.bottom
        self.addElement(self._btn)
        self.addEventListener(self._btn.handleEvent)

    def loadData(self):
        pass

    def run(self):
        for event in pygame.event.get():
            self._handleEvent(event)
        self.update()
        self.draw()
        self._clock.tick(Config.ticks)

    def update(self):
        super().update()

    def draw(self):
        updatedRects = self._elements.draw(self._canvas)
        pygame.display.update(updatedRects)