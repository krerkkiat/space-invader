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

class SceneElement(pygame.sprite.DirtySprite):

    def __init__(self, scene):
        super().__init__()

        self._scene = scene

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
        super().__init__(scene)

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

    @property
    def game(self):
        return self._game

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
            print('Load complete going to nextScene')
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

class MainScene(Scene):
    def __init(self, game):
        super().__init__(game)
        print('MainScene initialize')

        self._scoreChart = None

    def loadData(self, preload):
        preload.isLoading = True
        try:
            fb.authenticate()
            print('Authenticate to Facebook complete')
            result = fb.get('/me')
            uid = result['id']
            name = result['name']
            
            # self._game._pilot = Pilot('100001868030396', 'Krerkkiat Chusap')

            # login to our server
            login_data = bytes('{"type":"action", "value":"login", "uid":"%s"}' % uid, 'utf-8')
            result = ConnectionManager.send(login_data)
            if ConnectionManager.isSuccessfulResponse(result):
                self._game._pilot = Pilot(uid, name, result['data']['score'], result['data']['wave'])
                print('Authenticate to our server complete')
            else:
                SceneManager.exit()

            # fetch local resource register data
            result = ConnectionManager.send('''{"type":"action","value":"get","target":"resource_register_data"}''')
            for key in result['data']:
                if key == 'surface':
                    self.regisSurfaces(result['data']['surface'])
            print('Local resource register data loaded')

            # get friend list
            result = fb.fql('SELECT uid FROM user WHERE is_app_user AND uid IN (SELECT uid2 FROM friend WHERE uid1 = me())')
            # insert some fake data
            # result.extend([{'uid':'100000533319275'}])

            friends_that_use_this_app = [entry['uid'] for entry in result]
            
            print(friends_that_use_this_app)

            data = bytes('{"type":"action","value":"get","target":"score_board","data":%s}' % anyjson.serialize(friends_that_use_this_app), 'utf-8')
            friends = ConnectionManager.send(data)
            print(friends)

        except Exception as e:
            print(e)
            SceneManager.exit()

        preload.isLoading = False

    def regisSurfaces(self, surfaces):
        for id_ in surfaces:
            for i in range(len(surfaces[id_])): 
                color_key = None
                convert_alpha = False
                if 'color_key' in surfaces[id_][i]:
                    color_key = tuple(surfaces[id_][i]['color_key'])
                if 'convert_alpha' in surfaces[id_][i]:
                    convert_alpha = True

                path = Config.assetsRoot + ',' + ','.join(surfaces[id_][i]['path'])
                SurfaceManager.register(id_, os.path.join(*path.split(',')), color_key=color_key, convert_alpha=convert_alpha)
        
    def run(self):
        SceneManager.goto(TestScene(self._game))
        for event in pygame.event.get():
            self._handleEvent(event)
        
        self.update()
        self.draw()
        self._clock.tick(Config.ticks)

    def update(self):
        super().update()

    def draw(self):
        pass

class LevelScene(Scene):
    pass

class SummaryScene(Scene):
    def __init__(self, game):
        pass

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

class TestScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        print('Init TestScene')

        self._background.fill(Config.colors['black'])
        self._elements.clear(self._canvas, self._background)

        self._generator = EnemyWaveGenerator(self, paths=[SpiralPath], seed=3)

        self._fleet = pygame.sprite.LayeredDirty()

        self._spaceShip = pygame.sprite.LayeredDirty()
        self._spaceShip.clear(self._canvas, self._background)
        self._spaceShipBullets = pygame.sprite.LayeredDirty()
        self._spaceShipBullets.clear(self._canvas, self._background)

        self._enemys = pygame.sprite.LayeredDirty()
        self._enemys.clear(self._canvas, self._background)
        self._enemyBullets = pygame.sprite.LayeredDirty()
        self._enemyBullets.clear(self._canvas, self._background)


        '''
        SurfaceManager.register('sh000', os.path.join(Config.assetsRoot, 'spaceship', 'arboris', 'arboris_left.png'), color_key=(255, 0, 255))
        SurfaceManager.register('sh000', os.path.join(Config.assetsRoot, 'spaceship', 'arboris', 'arboris_center.png'), color_key=(255, 0, 255))
        SurfaceManager.register('sh000', os.path.join(Config.assetsRoot, 'spaceship', 'arboris', 'arboris_right.png'), color_key=(255, 0, 255))
        SurfaceManager.register('sd000', os.path.join(Config.assetsRoot, 'spaceship', 'shield', 'shield_0.png'), color_key=(255, 0, 255))
        SurfaceManager.register('sd000', os.path.join(Config.assetsRoot, 'spaceship', 'shield', 'shield_1.png'), color_key=(255, 0, 255))
        SurfaceManager.register('wp000', os.path.join(Config.assetsRoot, 'bullet.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test_left.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test_right.png'), True)
        SurfaceManager.register('em000', os.path.join(Config.assetsRoot, 'enemy', 'test', 'test.png'), True)
        '''
        # bullet also use same id as weapon (because it represent only image)
        bullet = Bullet(self, 'bu000', 10, pygame.math.Vector2(0, -15))
        weapon = Weapon('wp000', 'TestWeapon', 10, 'bu000', 15, bullet)
        armor = Armor('am000', 'TestArmor', 5)
        shield = Shield('sd000', 'TestShield', 10, 2000, 10)
        engine = Engine('eg000', 'TestEngine', 70, 2, 2000)

        testship = SpaceShip(self, 'sh000', '100001868030396', 'TestShip', 50, weapon, armor, shield, engine)
        testship.velocity.x = 10
        testship.velocity.y = 10
        testship.rect.centerx = Config.windowWidth/2
        testship.rect.centery = Config.windowHeight - testship.rect.height - 110
        self._fleet.add(testship)

        self.addElement(testship)
        self.addEventListener(testship.handleEvent)
        
        self._enemys = self._generator.nextWave()
        for e in self._enemys:
            self.addElement(e)

        self._pilotBar = PilotBar(self, self._game._pilot)
        self.addElement(self._pilotBar)

        self.addElement(MessageBox(self, 'Test Text ^^', interval=1200))

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

        