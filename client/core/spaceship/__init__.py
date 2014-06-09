import pygame

from core.ui import *
from core.scene.summary import SummaryScene
from core.scene.elements import MovingObject

class Fleet:
    pass

class SpaceShip(MovingObject):
    '''Abstract class that represent a spaceship'''
    @classmethod
    def fromJSON(class_, obj):
        weapon = Weapon.fromJSON(obj['weapon'])
        armor = Armor.fromJSON(obj['armor'])
        shield = Shield.fromJSON(obj['shield'])
        engine = Engine.fromJSON(obj['engine'])

        return SpaceShip(obj['id'], obj['pilotId'], obj['name'], obj['hp'], weapon, armor, shield, engine)

    def __init__(self, scene,  id_, pilotId, name, hp, weapon, armor, shield, engine):
        super().__init__(scene)

        self._id = id_
        self._pilotId = pilotId
        self._name = name
        self._maxHp = hp
        self._hp = hp
        self._weapon = weapon
        self._armor = armor
        self._shield = shield
        self._engine = engine

        self._rect = SurfaceManager.get(self._id)[0].get_rect()

        self._movement_map = {
            ord('a'): (-1, 0),
            ord('d'): (1, 0),
            ord('w'): (0, -1),
            ord('s'): (0, 1)
        }

        self._anime = 0

        self._healthBar = HealthBar(scene, self)
        self._scene.addElement(self._healthBar, layer=3)

        self._shield.thing = self

    def update(self, cycleTime):
        '''Override from core.scene.SceneElement'''
        keys_pressed = pygame.key.get_pressed()
        self.move(keys_pressed)

        self._shield.update(cycleTime, self._engine)
        self._engine.update(cycleTime)
        self._healthBar.update(cycleTime)   # force update
        self.dirty = 1

    @property
    def image(self):
        surface = SurfaceManager.get(self._id)[self._anime+1]
        return surface

    @property
    def rect(self):
        '''Override from core.scene.SceneElement'''
        if self._anime != 0:
            rect = self.image.get_rect()
            rect.centerx = self._rect.centerx
            rect.centery = self._rect.centery
            return rect
        return self._rect

    def move(self, keys_pressed):
        move_vector = (0, 0)
        for m in (self._movement_map[key] for key in self._movement_map if keys_pressed[key]):
            move_vector = tuple(map(sum, zip(move_vector, m)))

        # normalize movement vector if necessary
        if sum(map(abs, move_vector)) == 2:
            move_vector = [p/1.4142 for p in move_vector]

        # apply speed to movement vector
        move_vector = [10*p for p in move_vector]

        # print(move_vector)
        self._rect.centerx += move_vector[0]
        self._rect.centery += move_vector[1]

        if self._rect.left <= 0:
            self._rect.left = 0
        if self._rect.top <= 0:
            self._rect.top = 0
        if self._rect.right >= Config.windowWidth:
            self._rect.right = Config.windowWidth
        if self._rect.bottom >= Config.windowHeight-70:
            self._rect.bottom = Config.windowHeight-70

    def handleEvent(self, event):
        '''Override from core.scene.SceneElement'''
        if event.type == pygame.KEYUP:
            if event.key == ord('a') or event.key == ord('d'):
                self._anime = 0
                self.dirty = 1
            elif event.key == ord('n'):
                # self._shield.isActivate = not self._shield.isActivate
                self._shield.isActivate = True
                if self._shield.isActivate:
                    self._scene.addElement(self._shield, layer=2)
                self._shield.dirty = 1
                self.dirty = 1
            elif event.key == ord('j'):     # inside event to delay fire
                b = self.fire()
                self._scene.addSpaceshipBullet(b)

    def fire(self):
        '''Return bullet from weapon.fire()'''
        bullet = self._weapon.fire()
        bullet.rect.centerx = self._rect.centerx
        bullet.rect.midbottom = self._rect.midtop
        return bullet

    def onBulletHit(self, bullet):
        '''Visitor disign pattern for bullet to update a spaceship'''
        bullet.visit(self)
        self.dirty = 1

        if self._hp <= 0:
            self.kill()
            self._healthBar.kill()
            SceneManager.ret()
            SceneManager.call(SummaryScene(self._scene.game))

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def weapon(self):
        return self._weapon

    @property
    def armor(self):
        return self._armor
    
    @property
    def shield(self):
        return self._shield

    @property
    def engine(self):
        return self._engine


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
    def firePower(self):
        return self._weapon.attack
    
    @property
    def defence(self):
        return self._armor.defence

    @property
    def energy(self):
        return self._engine.energy
    @energy.setter
    def energy(self, value):
        self._engine.energy = value
    
    @property
    def maxEnergy(self):
        return self._engine.maxEnergy
