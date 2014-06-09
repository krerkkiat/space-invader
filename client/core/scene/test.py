import pygame

from config import Config
from core.ui import MessageBox, ScoreBar, PilotBar
from core.enemy import EnemyWaveGenerator
from core.scene import Scene
from core.movement.paths import SpiralPath
from core.spaceship import SpaceShip
from core.spaceship.weapon import Weapon, Bullet
from core.spaceship.armor import Armor
from core.spaceship.shield import Shield
from core.spaceship.engine import Engine

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
        
        self._pilotBar = PilotBar(self, self._parent._pilot)
        self._scoreBar = ScoreBar(self, self._parent._pilot)
        self.addElement(self._pilotBar)
        self.addElement(self._scoreBar)

    def nextWave(self):
        self._parent._pilot.wave += 1
        self.addElement(MessageBox(self, 'Wave ' + str(self._parent._pilot.wave), interval=1000, position='middle', textPosition='center'))
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

        