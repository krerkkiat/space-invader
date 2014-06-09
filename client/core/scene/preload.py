import os

import pygame

from config import Config
from core.scene import Scene
from core.manager import SceneManager

class Preload(Scene):
    def __init__(self, game, background=None, nextScene=None):
        super().__init__(game)

        if background == None:
            self._background.fill(Config.colors['black'])
        else:
            self._background = background
        self._nextScene = nextScene

        self._elements.clear(self._canvas, self._background)

        self._isLoading = True

        self._images = []

        font = pygame.font.Font(os.path.join(Config.assetsRoot, 'font', 'TudorRose.otf'), 40)
        self._images.append(font.render('Loading', True, Config.colors['white'], None))
        self._images.append(font.render('Loading.', True, Config.colors['white'], None))
        self._images.append(font.render('Loading..', True, Config.colors['white'], None))
        self._images.append(font.render('Loading...', True, Config.colors['white'], None))

        self._anime = 0
        self._animeCycle = 0
        self._animeInterval = 300

        self.dirty = 1

    @property
    def isLoading(self):
        return self._isLoading
    @isLoading.setter
    def isLoading(self, value):
        self._isLoading = value

    @property
    def nextScene(self):
        return self._nextScene
    @nextScene.setter
    def nextScene(self, value):
        self._nextScene = value

    def run(self):
        for event in pygame.event.get():
            self._handleEvent(event)
        self.update()
        self.draw()
        self._clock.tick(Config.ticks)

        if not self._isLoading:
            print('Load complete going to nextScene:', self._nextScene.__class__)
            if self._nextScene:
                self._nextScene.redraw()
            SceneManager.goto(self._nextScene)

    def update(self):
        super().update()

        self._animeCycle += self._cycleTime
        if self._animeCycle >= self._animeInterval:
            self._animeCycle = 0
            self._anime = (self._anime + 1) % len(self._images)
            self.dirty = 1

    def draw(self):
        if self.dirty == 1:
            img = self._images[self._anime]
            rect = img.get_rect()
            rect.left = 10
            rect.bottom = Config.windowHeight

            self._canvas.blit(self._background, (0, 0))
            self._canvas.blit(img, rect)
            pygame.display.flip()

            self.dirty = 0