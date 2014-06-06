import random

from core.scene import *
from core.movement import *

class EnemyWaveGenerator:
    def __init__(self, scene, paths, seed=None):
        self._scene =scene
        self._paths = paths
        self._seed = seed
        random.seed(seed)

    def nextWave(self):
        enemys = pygame.sprite.LayeredDirty()

        path_index = random.choice(range(len(self._paths)))

        path = self._paths[path_index]()
        for i in range(-1, -35, -5):
            m = Movement(path, i)
            tem = Enemy(self._scene, 'em000', 'TestEnemy', 20, 10, 3, 200 + random.randint(1000, 2000), 10, m)
            enemys.add(tem)

        return enemys

class Enemy(MovingObject):

    @classmethod
    def fromJSON(class_, obj):
        return Enemy(obj['id'], obj['name'], obj['attack'], obj['defence'], obj['fireInterval'], obj['score'], None)

    def __init__(self, scene, id_, name, maxHp, attack, defence, fireInterval, score, movement):
        super().__init__(scene)

        self._id = id_
        self._name = name
        self._maxHp = maxHp
        self._hp = maxHp
        self._attack = attack
        self._defence = defence

        self._score = score

        self._movement = movement

        self._rect = SurfaceManager.get(self._id)[0].get_rect()
        self._rect.x, self._rect.y = (-100, -100)

        self._animeInterval = 200
        self._animeCycle = 0
        self._anime = 0

        self._fireInterval = fireInterval
        self._fireCycle = 0

        self._moveInterval = 200
        self._moveCycle = 0

        self._healthBar = HealthBar(scene, self)
        self._scene.addElement(self._healthBar, layer=3)

    def update(self, cycleTime):
        '''Override from core.scene.SceneElement'''

        self._animeCycle += cycleTime
        if self._animeCycle >= self._animeInterval:
            self._animeCycle = 0
            self._anime = (self._anime + 1) % len(SurfaceManager.get(self._id))

            self.dirty = 1

        self._fireCycle += cycleTime
        if self._fireCycle >= self._fireInterval:
            self._fireCycle = 0
            b = self.fire()
            self._scene.addEnemyBullet(b)

        self._moveCycle += cycleTime
        if self._moveCycle >= self._moveInterval:
            self._moveCycle = 0
            self.move()

        self._healthBar.update(cycleTime)

    def move(self):
        x, y = self._movement.move()
        self._rect.x = x
        self._rect.y = y

    @property
    def image(self):
        '''Override from core.scene.SceneElement'''
        return SurfaceManager.get(self._id)[self._anime]

    @property
    def rect(self):
        '''Override from core.scene.SceneElement'''
        return self._rect

    def handleEvent(self, event):
        '''Override from core.scene.SceneElement'''
        pass

    def fire(self):
        b = Bullet(self._scene, 'bu000', 10, pygame.math.Vector2(0, 15))
        b.rect.centerx = self._rect.centerx
        b.rect.centery = self._rect.centery
        return b

    def onBulletHit(self, bullet):
        '''Visitor disign pattern for bullet to update an enemy'''
        bullet.visit(self)

        if self._hp <= 0:
            self.kill()
            self._healthBar.kill()

            self._scene.game._pilot.score += self._score
            print(self._scene.game._pilot.score)

        self.dirty = 1

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def hp(self):
        return self._hp
    @hp.setter
    def hp(self, value):
        self._hp = value

    @property
    def maxHp(self):
        return self._maxHp 

    @property
    def attack(self):
        return self._attack

    @property
    def defence(self):
        return self._defence
    
    @property
    def fireInterval(self):
        return self._fireInterval

    @property
    def score(self):
        return self._score

# why i need to do like this?
from core.spaceship import *