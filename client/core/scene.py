import os
import sys
import random

import pygame

from config import Config
from core.pilot import *
from core.manager import *
from core.movement import *

class SceneElement(pygame.sprite.DirtySprite):

    def __init__(self):
        super().__init__()

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

class MovingObject(SceneElement):
    def __init__(self, scene):
        super().__init__()

        self._scene = scene
        self._velocity = pygame.math.Vector2()
        self._rect = None

    @property
    def velocity(self):
        return self._velocity

# why i need to do this ?
# maybe ahh python dose not interprete MovingObject before SpaceShip need it
from core.enemy import *
from core.spaceship import *

class Scene:

    def __init__(self, game):
        self._game = game

        self._eventListener = []
        self._elements = pygame.sprite.LayeredDirty()

        self._canvas = pygame.display.get_surface()
        self._background = pygame.Surface(self._canvas.get_size())
        self._clock = pygame.time.Clock()
        self._totalTimePassed = 0

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

    def _loadData(self):
        raise NotImplementedError('Sub-class should overide this method')

    def run(self):
        #raise NotImplementedError('Sub-class should overide this method')
        self._loadData()

    def update(self):
        #raise NotImplementedError('Sub-class should overide this method')
        cycleTime = self._clock.tick(Config.ticks)
        self._totalTimePassed += cycleTime

        self._elements.update(cycleTime)
        
    def draw(self):
        raise NotImplementedError('Sub-class should overide this method')

    def addEventListener(self, listener):
        self._eventListener.append(listener)

    def addElement(self, element, layer=0):
        self._elements.add(element, layer=layer)

class CreditScene(Scene):
    pass

class LoadingScene(Scene):
    pass

class MenuScene(Scene):
    pass

class MainMenuScene(MenuScene):
    pass

class LevelScene(Scene):
    pass

class TestScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self._background.fill(Config.colors['black'])
        self._elements.clear(self._canvas, self._background)

        self._fleet = pygame.sprite.LayeredDirty()

        self._spaceShip = pygame.sprite.LayeredDirty()
        self._spaceShip.clear(self._canvas, self._background)
        self._spaceShipBullets = pygame.sprite.LayeredDirty()
        self._spaceShipBullets.clear(self._canvas, self._background)

        self._enemys = pygame.sprite.LayeredDirty()
        self._enemys.clear(self._canvas, self._background)
        self._enemyBullets = pygame.sprite.LayeredDirty()
        self._enemyBullets.clear(self._canvas, self._background)

    def _loadData(self):
        SurfaceManager.register('sh000', os.path.join(Config.assetsRoot, 'spaceship', 'arboris', 'arboris_left.png'), colorkey=(255, 0, 255))
        SurfaceManager.register('sh000', os.path.join(Config.assetsRoot, 'spaceship', 'arboris', 'arboris_center.png'), colorkey=(255, 0, 255))
        SurfaceManager.register('sh000', os.path.join(Config.assetsRoot, 'spaceship', 'arboris', 'arboris_right.png'), colorkey=(255, 0, 255))
        SurfaceManager.register('sd000', os.path.join(Config.assetsRoot, 'spaceship', 'shield', 'shield_0.png'), colorkey=(255, 0, 255))
        SurfaceManager.register('sd000', os.path.join(Config.assetsRoot, 'spaceship', 'shield', 'shield_1.png'), colorkey=(255, 0, 255))
        SurfaceManager.register('wp000', os.path.join(Config.assetsRoot, 'bullet.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test_left.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test_right.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test.png'), True)

        pilot = Pilot('100001868030396', 'KC')
        # bullet also use same id as weapon (because it represent only image)
        bullet = Bullet(self, 'wp000', 10, pygame.math.Vector2(0, -15))
        weapon = Weapon('wp000', 'TestWeapon', bullet, 10, 15)
        armor = Armor('am000', 'TestArmor', 5)
        shield = Shield('sd000', 'TestShield', 2, 2000, 10)
        engine = Engine('eg000', 'TestEngine', 70, 2, 2000)

        testship = SpaceShip(self, 'sh000', '100001868030396', 'TestShip', 50, weapon, armor, shield, engine)
        testship.velocity.x = 10
        testship.velocity.y = 10
        testship.rect.centerx = Config.windowWidth/2
        testship.rect.centery = Config.windowHeight - testship.rect.height - 110
        self._fleet.add(testship)

        self.addElement(testship)
        self.addEventListener(testship.handleEvent)


        path = SpiralPath()
        for i in range(-1, -35, -5):
            m = Movement(path, i)
            tem = Enemy(self, 'em000', 'TestEnemy', 20, 10, 3, 200 + random.randint(1000, 2000), m)
            self.addElement(tem)
            self._enemys.add(tem)

        self._pilotBar = PilotBar(self, pilot)
        self.addElement(self._pilotBar)

    def run(self):
        super().run()

        while True:
            for event in pygame.event.get():
                self._handleEvent(event)
            self.update()
            self.draw()
            self._clock.tick(Config.ticks)

    def update(self):
        super().update()

        bulletHitEnemy = pygame.sprite.groupcollide(self._spaceShipBullets, self._enemys, True, False)
        for bullet in bulletHitEnemy:
            if len(bulletHitEnemy[bullet]) != 0:
                for enemy in bulletHitEnemy[bullet]:
                    enemy.onBulletHit(bullet)

        bulletHitSpaceShip = pygame.sprite.groupcollide(self._enemyBullets, self._fleet, True, False)
        for bullet in bulletHitSpaceShip:
            if len(bulletHitSpaceShip[bullet]) != 0:
                for spaceship in bulletHitSpaceShip[bullet]:
                    spaceship.onBulletHit(bullet)

    def draw(self):
        updatedRects = self._elements.draw(self._canvas)
        pygame.display.update(updatedRects)

        