import pygame

from core.manager import SurfaceManager

class Shield(pygame.sprite.DirtySprite):
    '''Repersent a spaceship's shield'''

    @classmethod
    def fromJSON(class_, obj):
        return Shield(obj['id'], obj['name'], obj['drainRate'], obj['hitDarinRate'])

    def __init__(self, id_, name, drainRate, drainRateInterval, hitDarinRate):
        super().__init__()

        self._id = id_
        self._thing = None
        self._name = name
        self._drainRate = drainRate
        self._drainRateInterval = drainRateInterval
        self._hitDrainRate = hitDarinRate
        self._isActivate = False

        self._image = SurfaceManager.get(self._id)[0]
        self._rect = self._image.get_rect()

        self._drainRateCycle = 0

        self._anime = 0
        self._animeCycle = 0
        self._animeInterval = 100

        self.dirty = 0

    def update(self, cycleTime, engine=None):
        if self._isActivate and engine:
            self._animeCycle += cycleTime
            if self._animeCycle >= self._animeInterval:
                self._animeCycle = 0
                self._anime = (self._anime+1)%len(SurfaceManager.get(self._id))

            self._drainRateCycle += cycleTime
            if self._drainRateCycle >= self._drainRateInterval:
                engine.energy -= self._drainRate

                self._drainRateCycle = 0

            if engine.energy <= 0:
                engine.energy = 0
                self._isActivate = False
                self.kill()
            self.dirty = 1

    @property
    def image(self):
        return SurfaceManager.get(self._id)[self._anime]

    @property
    def rect(self):
        self._rect = self.image.get_rect()
        self._rect.centerx = self._thing.rect.centerx
        self._rect.centery = self._thing.rect.centery
        return self._rect

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def drainRate(self):
        return self._drainRate

    @property
    def hitDrainRate(self):
        return self._hitDrainRate

    @property
    def isActivate(self):
        return self._isActivate
    @isActivate.setter
    def isActivate(self, value):
        self._isActivate = value

    @property
    def thing(self):
        return self._thing
    @thing.setter
    def thing(self, value):
        self._thing = value