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

class Scene:

    def __init__(self, game):
        self._game = game

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

class SummaryScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self._background = pygame.display.get_surface()
        self._background.set_alpha(180)
        self._background.fill(Config.colors['black'])
        self._elements.clear(self._canvas, self._background)

        w, h = (200, 200)
        rowData = [('Score', 'Wave'), (str(self._game._pilot.score), str(self._game._pilot.wave))]
        columnWidth = [100, 100]
        self._scoreBoard = Table(self, w, h, rowData, columnWidth, title='Summary', line=False, button=False)
        self._scoreBoard.rect.centerx = Config.windowWidth//2
        self._scoreBoard.rect.centery = Config.windowHeight//2
        self.addElement(self._scoreBoard)

        def callBack():
            # SceneManager.call(MainScene(self._game), Preload(self._game))
            self._game._pilot.update()
            SceneManager.ret(Preload(self._game))
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

# why i need to do this ?
# maybe ahh python dose not interprete MovingObject before SpaceShip need it
from core.enemy import *
from core.spaceship import *

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

class MainScene(Scene):
    def __init(self, game):
        super().__init__(game)

        self._scoreBoard = None

    def loadData(self, preload):
        preload.isLoading = True
        try: 
            self._createScoreBoard()
            self._createUI()
        except Exception as e:
            print(e)
            SceneManager.exit()

        preload.isLoading = False
        # SceneManager.goto(GameScene(self._game, {}, 7))
        # SceneManager.call(TestScene(self._game))

    def _createUI(self):
        def callBack():
            SceneManager.call(TestScene(self._game))
        self._startBtn = Button(self, 'Start', callBack)
        self._startBtn.rect.right = Config.windowWidth
        self._startBtn.rect.bottom = Config.windowHeight
        self.addElement(self._startBtn)
        self.addEventListener(self._startBtn.handleEvent)

    def _createScoreBoard(self):
        # get friends list
        fb_result = fb.fql('SELECT uid, name FROM user WHERE is_app_user AND uid IN (SELECT uid2 FROM friend WHERE uid1 = me())')

        # insert me
        fb_result.extend([{'uid':self._game._pilot.id, 'name':'You'}])       # Pornchanok id

        # insert some fake data
        fb_result.extend([{'uid':'100000533319275', 'name':'Pornchanok'}])       # Pornchanok id
        # fb_result.extend([{'uid':'247059255488681', 'name':'Test User #1'}])     # friend of Test User #1
        # fb_result.extend([{'uid':'252287594960325', 'name':'Test User #2'}])     # friend of Test User #2

        friends_that_use_this_app = [entry['uid'] for entry in fb_result]
        data = bytes('{"type":"action","value":"get","target":"score_board","data":%s}' % anyjson.serialize(friends_that_use_this_app), 'utf-8')
        result = ConnectionManager.send(data)
        if ConnectionManager.isSuccessfulResponse(result):
            self._friends = []
            # data = [d['name'] = fd['name'] for d in result['data'] for fd in fb_result if fd['uid'] == d['id']]
            data = []
            for d in result['data']:
                for fd in fb_result:
                    if fd['uid'] == d['id']:
                        d['name'] = fd['name']
                        data.append(d)
            for f in result['data']:
                self._friends.append(Pilot(f['id'], f['name'], f['score'], f['wave'], f['time']))

        w, h = (400, 600)
        rowData = [('', 'Name', 'Score', 'Wave')]
        rowData.extend([(str(i), pilot.name, str(pilot.bestScore), str(pilot.bestWave)) for i, pilot in enumerate(self._friends, 1)])
        columnWidth = [30, 200, 75, 75]
        self._scoreBoard = Table(self, w, h, rowData, columnWidth, title='Score board')
        self.addElement(self._scoreBoard)
        self.addEventListener(self._scoreBoard.handleEvent)

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

class GameScene(Scene):
    def __init__(self, game, spaceshipData, seed):
        super().__init__(game)

        self._background.fill(Config.colors['black'])
        self._elements.clear(self._canvas, self._background)

        self._enemyGenerator = EnemyWaveGenerator(self, paths=[SpiralPath], seed=seed)

        # sprite group for contain Sapceships
        self._spaceshipFleet = pygame.sprite.LayeredDirty()
        self._spaceshipFleet.clear(self._canvas, self._background)
        self._spaceshipFleetBullets = pygame.sprite.LayeredDirty()
        self._spaceshipFleetBullets.clear(self._canvas, self._background)

        # add spaceship
        spaceship = SpaceShip.fromJSON(spaceshipData)
        self._spaceshipFleet.add(spaceship)
        self.addElement(spaceship)
        self.addEventListener(spaceship.handleEvent)

        # sprite group for contain Enemy
        self._enemyWaveBullets = pygame.sprite.LayeredDirty()
        self._enemyWaveBullets.clear(self._canvas, self._background) 

        self._enemyWave = self._enemyGenerator.nextWave()
        for e in self._enemyWave:
            self.addElement(e)

        # add HUD
        self._pilotBar = PilotBar(self, self._game._pilot)
        self._scoreBar = ScoreBar(self. self._game._pilot)
        self.addElement(self._pilotBar)
        self.addElement(self._scoreBar)

    def addSpaceshipBullet(self, bullet):
        self._spaceshipFleetBullets.add(bullet)
        self.addElement(bullet)

    def addEnemyBullet(self, bullet):
        self._enemyWaveBullets.add(bullet)
        self.addElement(bullet)        

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

        bulletHitEnemy = pygame.sprite.groupcollide(self._spaceshipFleetBullets, self._enemyWave, True, False)
        for bullet in bulletHitEnemy:
            if len(bulletHitEnemy[bullet]) != 0:
                for enemy in bulletHitEnemy[bullet]:
                    enemy.onBulletHit(bullet)

        bulletHitSpaceShip = pygame.sprite.groupcollide(self._enemyWaveBullets, self._spaceshipFleet, True, False)
        for bullet in bulletHitSpaceShip:
            if len(bulletHitSpaceShip[bullet]) != 0:
                for spaceship in bulletHitSpaceShip[bullet]:
                    spaceship.onBulletHit(bullet)

    def draw(self):
        updatedRects = self._elements.draw(self._canvas)
        pygame.display.update(updatedRects)

class TestScene(Scene):
    def __init__(self, game):
        super().__init__(game)

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
        # edit: changed  , bullet use it own id
        bullet = Bullet(self, 'bu000', 10, pygame.math.Vector2(0, -15))
        weapon = Weapon('wp000', 'TestWeapon', 10, 'bu000', 15, bullet)
        armor = Armor('am000', 'TestArmor', 5)
        shield = Shield('sd000', 'TestShield', 10, 2000, 10)
        engine = Engine('eg000', 'TestEngine', 70, 2, 2000)

        testship = SpaceShip(self, 'sh000', '100001868030396', 'TestShip', 10, weapon, armor, shield, engine)
        testship.velocity.x = 10
        testship.velocity.y = 10
        testship.rect.centerx = Config.windowWidth/2
        testship.rect.centery = Config.windowHeight - testship.rect.height - 110
        self._fleet.add(testship)

        self.nextWave()

        self.addElement(testship)
        self.addEventListener(testship.handleEvent)
        
        self._pilotBar = PilotBar(self, self._game._pilot)
        self._scoreBar = ScoreBar(self, self._game._pilot)
        self.addElement(self._pilotBar)
        self.addElement(self._scoreBar)

    def nextWave(self):
        self._game._pilot.wave += 1
        self.addElement(MessageBox(self, 'Wave ' + str(self._game._pilot.wave), interval=1000, position='middle', textPosition='center'))
        self._enemys = self._generator.nextWave()
        for e in self._enemys:
            self.addElement(e)

    def addSpaceshipBullet(self, bullet):
        self._spaceShipBullets.add(bullet)
        self.addElement(bullet)

    def addEnemyBullet(self, bullet):
        self._enemyBullets.add(bullet)
        self.addElement(bullet)        

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

        if len(self._enemys) == 0:
            self.nextWave()

    def draw(self):
        updatedRects = self._elements.draw(self._canvas)
        pygame.display.update(updatedRects)

        