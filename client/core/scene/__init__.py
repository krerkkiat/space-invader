import os
import sys
import random
import threading

import pygame
import anyjson

from config import Config
from core.pilot import *
from core.manager import *
from core.movement import *

class Scene:

    def __init__(self, game):
        self._parent = game

        self._eventListener = []
        self._elements = pygame.sprite.LayeredDirty()

        self._canvas = pygame.display.get_surface()
        self._background = pygame.Surface(self._canvas.get_size())
        self._clock = pygame.time.Clock()
        self._totalTimePassed = 0

    def redraw(self):
        self._canvas.blit(self._background, (0, 0))
        for ele in self._elements:
            ele.dirty = 1
        pygame.display.flip()

    @property
    def game(self):
        return self._parent

    def _handleEvent(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()                

        for listener in self._eventListener:
            listener(event)

    def loadData(self):
        raise NotImplementedError('Sub-class should overide this method')

    def run(self):
        raise NotImplementedError('Sub-class should overide this method')
        # self._loadData()

    def update(self):
        #raise NotImplementedError('Sub-class should overide this method')
        self._cycleTime = self._clock.tick(Config.ticks)
        self._totalTimePassed += self._cycleTime

        self._elements.update(self._cycleTime)
        
    def draw(self):
        raise NotImplementedError('Sub-class should overide this method')

    def addEventListener(self, listener):
        self._eventListener.append(listener)

    def removeEventListener(self, listener):
        self._eventListener.remove(listener)        

    def addElement(self, element, layer=0):
        self._elements.add(element, layer=layer)

class SceneElement(pygame.sprite.DirtySprite):

    def __init__(self, scene):
        super().__init__()

        self._scene = scene

    def _kill(self):
        self.onKill()

    def onKill(self):
        self.kill()

    def update(self, cycleTime):
        raise NotImplementedError('Sub-class should overide this method')
        
    @property
    def image(self):
        raise NotImplementedError('Sub-class should overide this method')

    @property
    def rect(self):
        raise NotImplementedError('Sub-class should overide this method')

    def handleEvent(self, event):
        raise NotImplementedError('Sub-class should overide this method')

# why i need to do this ?
# maybe ahh python dose not interprete MovingObject before SpaceShip need it
# from core.enemy import *
# from core.spaceship import *