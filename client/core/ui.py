import os

import pygame

from config import *
from core.scene import *

class Table(SceneElement):

    def __init__(self, scene, width, height, rowData, columnWidth, rowHeight=30):
        '''Please put column name to rowData at 1st position'''
        super().__init__(scene)

        self._width = width
        self._height = height
        self._rowHeight = rowHeight
        self._columnWidth = columnWidth

        self._image = pygame.Surface((width, height))
        self._rect = self._image.get_rect()
        
        self._upBtn = pygame.sprite.DirtySprite()
        self._upBtn.image = SurfaceManager.get('upBtn')[0]
        self._upBtn.rect = self._upBtn.image.get_rect()
        self._upBtn.rect.centerx = width-10
        self._upBtn.rect.centery = 10

        self._downBtn =  pygame.sprite.DirtySprite()
        self._downBtn.image = SurfaceManager.get('downBtn')[0]
        self._downBtn.rect = self._downBtn.image.get_rect()
        self._downBtn.rect.centerx = width-10
        self._downBtn.rect.centery = 30

        self._dummyMouse = pygame.sprite.DirtySprite()
        self._dummyMouse.rect = pygame.Rect(0, 0, 10, 10)

        self._startRow = -1

        font = pygame.font.Font(os.path.join(Config.assetsRoot, 'font', 'TudorRose.otf'), 20)

        padding = 10
        # create rows
        self._rows = []
        for row in rowData[:]:
            row_surface = pygame.Surface((width-21, rowHeight))
            i = 0
            column_rect = pygame.Rect(0, 0, columnWidth[0], rowHeight)
            while i < len(row):
                column_surface = font.render(row[i], True, Config.colors['white'], None)
                t = column_surface.get_rect()
                t.width = columnWidth[i] - padding
                t.height = rowHeight
                column_rect.width = columnWidth[i]

                row_surface.blit(column_surface, (column_rect.left + padding, 0), t)
                column_rect.move_ip(columnWidth[i], 0)
                i += 1

            self._rows.append(row_surface)
        self._rowHeader = self._rows[0]
        self._rows = self._rows[1:]

        self._generateImage()

    def _generateImage(self):
        self._image.fill(Config.colors['black'])

        rect = pygame.Rect(1, 1-(self._rowHeight*self._startRow), self._width-20, self._rowHeight)
        for row in self._rows:
            self._image.blit(row, rect)
            rect.move_ip(0, self._rowHeight)

        self._image.blit(self._rowHeader, (1, 1))

        # header line
        pygame.draw.line(self._image, Config.colors['white'], (0, self._rowHeight - 1), (self._width - 20, self._rowHeight - 1), 1)
        # left line
        # pygame.draw.line(self._image, Config.colors['white'], (0, 0), (0, self._height), 1)
        # inner right line
        pygame.draw.line(self._image, Config.colors['white'], (self._width - 20, 0), (self._rect.width - 20, self._height), 1)
        # outer right line
        # pygame.draw.line(self._image, Config.colors['white'], (self._width - 1, 0), (self._rect.width - 1, self._height - 1), 1)
        # top line
        pygame.draw.line(self._image, Config.colors['white'], (0, 0), (self._width - 20, 0), 1)
        # bottom line
        pygame.draw.line(self._image, Config.colors['white'], (0, self._height - 1), (self._width - 20, self._height - 1), 1)

        # column lines
        i = 0
        start = 0
        while i < len(self._columnWidth):
            pygame.draw.line(self._image, Config.colors['white'], (start, 0), (start, self._height))
            start += self._columnWidth[i]
            i += 1

        self._image.blit(self._upBtn.image, self._upBtn.rect)
        self._image.blit(self._downBtn.image, self._downBtn.rect)

    def update(self, cycleTime):
        pass

    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        return self._rect

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            pass
        elif event.type == pygame.MOUSEMOTION:
            self._dummyMouse.rect.centerx = event.pos[0]
            self._dummyMouse.rect.centery = event.pos[1]

            if pygame.sprite.collide_rect(self._dummyMouse, self._upBtn):
                pass
            elif pygame.sprite.collide_rect(self._dummyMouse, self._downBtn):
                pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if self._upBtn.rect.move(self._rect.x, self._rect.y).collidepoint(pos):
                self._startRow += 1
                if self._startRow >= len(self._rows)-2:
                    self._startRow = len(self._rows)-2
                self._generateImage()
                self.dirty = 1
            elif self._downBtn.rect.move(self._rect.x, self._rect.y).collidepoint(pos):
                self._startRow -= 1
                if self._startRow <= -1:
                    self._startRow = -1
                self._generateImage()
                self.dirty = 1

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

        self._image = pygame.Surface((Config.windowWidth*2//5, 70))
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
        self._image = pygame.Surface((self._barWidth, 10))
        self._image.set_colorkey(Config.colors['black'])
        self._rect = self._image.get_rect()

        self._hpBar = pygame.Surface((self._barWidth, 3))
        self._hpBar.fill(Config.colors['red'])
        self._hpBarRect = self._hpBar.get_rect()
        self._hpBarRect.y += 2

        haveEnergy = getattr(self._thing, 'engine', False) 
        if haveEnergy:
            self._epBar = pygame.Surface((self._barWidth, 3))
            self._epBar.fill(Config.colors['blue'])
            self._epBarRect = self._epBar.get_rect()
            self._epBarRect.y += 5

    def update(self, cycleTime):
        # optimize from 
        # create surface every time that hp change
        # but now we fill every time instaed
        if self._thing.dirty:
            hp_width = (self._thing.hp / self._thing.maxHp)*self._barWidth
            self._hpBarRect.width = hp_width

            energy_width = 0
            haveEnergy = getattr(self._thing, 'engine', False) 
            if haveEnergy:
                energy_width = (self._thing.engine.energy / self._thing.engine.maxEnergy)*self._barWidth
                if energy_width > 0:
                    self._epBarRect.width = energy_width

            self._image.fill(Config.colors['black'])
            self._image.fill(Config.colors['red'], self._hpBarRect)
            if haveEnergy and energy_width > 0:
                self._image.fill(Config.colors['blue'], self._epBarRect)
            self.dirty = 1

    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        self._rect.left = self._thing.rect.left
        self._rect.bottom = self._thing.rect.top
        return self._rect