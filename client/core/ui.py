import os

import pygame

from config import *

class PilotBar(pygame.sprite.DirtySprite):
    def __init__(self, scene, pilot):
        super().__init__()

        self._scene = scene
        self._pilot = pilot

        self._image = pygame.Surface((Config.windowWidth, 60))
        self._image.fill(Config.colors['white'])
        self._image.set_alpha(180)
        self._rect = self._image.get_rect()
        self._rect.left = 0
        self._rect.bottom = Config.windowHeight

        self._image.blit(self._pilot.profilePicture, (5, 5))

        font = pygame.font.Font(os.path.join(Config.assetsRoot, 'font', 'TudorRose.otf'), 20)
        
        pilot_txt = font.render('Pilot', True, Config.colors['black'], None)
        self._image.blit(pilot_txt, (60, 5))

        pilot_name_txt = font.render(self._pilot.name, True, Config.colors['black'], None)
        self._image.blit(pilot_name_txt, (60, 30))

    def update(self, cycleTime):
        pass

    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        return self._rect

class HealthBar(pygame.sprite.DirtySprite):
    def __init__(self, scene, thing, barWidth= 50):
        super().__init__()

        self._barWidth = barWidth

        self._scene = scene
        self._thing = thing
        self._image = pygame.Surface((50, 10))
        self._rect = self._image.get_rect()

    def update(self, cycleTime):
        if self._thing.dirty:
            # even if i use pygame.transform.scale()
            # it seem that it create new Surface for me T^T
            hp_width = (self._thing.hp / self._thing.maxHp)*self._barWidth
            hp_bar = pygame.Surface((hp_width, 3))
            hp_bar.fill(Config.colors['red'])
            hp_bar_rect = hp_bar.get_rect()
            hp_bar_rect.y += 2

            energy_width = 0
            haveEnergy = getattr(self._thing, 'engine', False) 
            if haveEnergy:
                energy_width = (self._thing.engine.energy / self._thing.engine.maxEnergy)*self._barWidth
                ep_bar = pygame.Surface((energy_width, 3))
                ep_bar.fill(Config.colors['blue'])
                ep_bar_rect = ep_bar.get_rect()
                ep_bar_rect.y += 5

            surface = pygame.Surface((max(hp_width, energy_width), 10))
            surface.set_colorkey(Config.colors['black'])
            surface.blit(hp_bar, hp_bar_rect)
            if haveEnergy:
                surface.blit(ep_bar, ep_bar_rect)

            self._image = surface
            self.dirty = 1

    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        self._rect.left = self._thing.rect.left
        self._rect.bottom = self._thing.rect.top
        return self._rect