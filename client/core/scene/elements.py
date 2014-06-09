import pygame

from core.scene import SceneElement

class MovingObject(SceneElement):

    def __init__(self, scene):
        super().__init__(scene)

        self._velocity = pygame.math.Vector2()
        self._rect = None

    @property
    def velocity(self):
        return self._velocity