import os

import pygame

from config import *
from core.scene import *

class MessageBox(SceneElement):
    def __init__(self, scene, message, interval=0, padding=0, textPosition='left', position='bottom', image=None):
        super().__init__(scene)

        self._scene.addEventListener(self.handleEvent)

        self._message = message
        self._image = image

        self._animeCycle = 0
        self._animeInterval = interval

        # build message box
        width, height = (Config.windowWidth - 2*padding, Config.windowHeight//6)
        dummyRect = pygame.Rect(0, 0, width, height)
        self._image = pygame.Surface((width, height))
        self._image.set_alpha(180)
        self._image.fill(Config.colors['white'])
        self._rect = self._image.get_rect()

        if position == 'bottom':
            self._rect.left = padding
            self._rect.bottom = Config.windowHeight - padding
        elif position == 'middle':
            self._rect.left = padding
            self._rect.centery = Config.windowHeight//2
        elif position == 'top':
            self._rect.left = padding
            self._rect.top = padding

        font = pygame.font.Font(os.path.join(Config.assetsRoot, 'font', 'TudorRose.otf'), 20)
        message_surface = font.render(message, True, Config.colors['black'], None)
        message_rect = message_surface.get_rect()

        if textPosition == 'center':
            message_rect.centerx = dummyRect.centerx
            message_rect.centery = dummyRect.centery
        elif textPosition == 'left':
            message_rect.left = 100     # offset for image
            message_rect.top = 10

        self._image.blit(message_surface, message_rect)

        if image:
            self._image.blit(image, (10, 10))

    def update(self, cycleTime):
        if self._animeInterval > 0:
            self._animeCycle += cycleTime
            if self._animeCycle >= self._animeInterval:
                self._animeCycle = 0
                self.kill()
                self._scene.removeEventListener(self.handleEvent)

    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        return self._rect

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.kill()
                self._scene.removeEventListener(self.handleEvent)

class PilotBar(SceneElement):
    def __init__(self, scene, pilot):
        super().__init__(scene)

        self._pilot = pilot

        self._image = pygame.Surface((Config.windowWidth//3, 70))
        # self._image.fill(Config.colors['white'])
        self._image.set_alpha(180)
        self._rect = self._image.get_rect()
        self._rect.left = 0
        self._rect.bottom = Config.windowHeight

        pygame.draw.line(self._image, Config.colors['white'], (self._rect.width//8, 65), (self._rect.width, 65), 2)
        pygame.draw.line(self._image, Config.colors['white'], (0, 60), (self._rect.width * 2//3, 60), 2)

        self._image.blit(self._pilot.profilePicture, (5, 5))

        font = pygame.font.Font(os.path.join(Config.assetsRoot, 'font', 'TudorRose.otf'), 20)
        
        pilot_txt = font.render('Pilot', True, Config.colors['white'], None)
        self._image.blit(pilot_txt, (60, 5))

        pilot_name_txt = font.render(self._pilot.name, True, Config.colors['white'], None)
        self._image.blit(pilot_name_txt, (60, 30))

    def update(self, cycleTime):
        pass

    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        return self._rect

class HealthBar(SceneElement):
    def __init__(self, scene, thing, barWidth= 50):
        super().__init__(scene)

        self._barWidth = barWidth

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
                if energy_width > 0:    
                    ep_bar = pygame.Surface((energy_width, 3))
                    ep_bar.fill(Config.colors['blue'])
                    ep_bar_rect = ep_bar.get_rect()
                    ep_bar_rect.y += 5

            surface = pygame.Surface((max(hp_width, energy_width), 10))
            surface.set_colorkey(Config.colors['black'])
            surface.blit(hp_bar, hp_bar_rect)
            if haveEnergy and energy_width > 0:
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