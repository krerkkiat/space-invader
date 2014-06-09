import os

import pygame

from config import Config
from core.enemy import Enemy
from core.manager import SurfaceManager
from core.spaceship import SpaceShip
from core.scene.elements import MovingObject

class Weapon:
    '''Represent a weapon of the spaceship'''

    @classmethod
    def fromJSON(class_, obj):
        velocity = pygame.math.Vector2(0, -obj['bulletSpeed'])
        bullet = Bullet(obj['bulletId'], obj['attack'], velocity)
        return Weapon(obj['id'], obj['name'], obj['attack'], obj['bulletId'], obj['bulletSpeed'], bullet)
    
    def __init__(self, id_, name, attack, bulletId, bulletSpeed, bullet):
        self._id = id_
        self._name = name
        self._bullet = bullet
        self._attack = attack
        self._bulletId = bulletId
        self._bulletSpeed = bulletSpeed

    def fire(self):
        #raise NotImplementedError('Sub-class should overide this method')
        return Bullet.fromBullet(self._bullet)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def bullet(self):
        return self._bullet

    @property
    def attack(self):
        return self._attack

    @property
    def bulletSpeed(self):
        return self._bulletSpeed

class Bullet(MovingObject):
    '''Represent a bullet of weapon (visitor disign pattern)'''

    @classmethod
    def fromBullet(class_, bullet):
        return Bullet(bullet._scene, bullet.id, bullet.damage, bullet.velocity)

    def __init__(self, scene, id_, damage, velocity):
        super().__init__(scene)

        self._id = id_
        self._damage = damage
        self._velocity = velocity
        self._rect = SurfaceManager.get(self._id)[0].get_rect()

    def update(self, cycleTime):
        '''Override from core.scene.SceneElement'''
        self._rect.move_ip(self._velocity.x, self._velocity.y)
        if self._rect.y <= 0 or self._rect.y >= Config.windowHeight-60:
            self.kill()
        self.dirty = 1

    @property
    def id(self):
        return self._id

    @property
    def damage(self):
        return self._damage

    @property
    def image(self):
        '''Override from core.scene.SceneElement'''
        return SurfaceManager.get(self._id)[0]

    @property
    def rect(self):
        '''Override from core.scene.SceneElement'''
        return self._rect

    def handleEvent(self, event):
        '''Override from core.scene.SceneElement'''
        pass

    def visit(self, thing):
        #raise NotImplementedError('Sub-class should overide this method')
        if isinstance(thing, SpaceShip):
            if not thing.shield.isActivate:
                damage = (self._damage - thing.defence)
                thing.hp -= damage
                self._scene.addElement(Damage(self._scene, self._rect, damage, Config.colors['red']))
            else:
                thing.engine.energy -= thing.shield.hitDrainRate

                damage = 0
                self._scene.addElement(Damage(self._scene, self._rect, damage, Config.colors['red']))
        elif isinstance(thing, Enemy):
            damage = (self._damage - thing.defence)
            thing.hp -= damage
            self._scene.addElement(Damage(self._scene, self._rect, damage, Config.colors['blue']))

class Damage(MovingObject):
    def __init__(self, scene, position, damage, color):
        super().__init__(scene)

        font = pygame.font.Font(os.path.join(Config.assetsRoot, 'font', 'TudorRose.otf'), 40)
        self._image = font.render('{}'.format(damage), True, color, None)
        self._rect = self._image.get_rect()
        self._rect.centerx = position.centerx
        self._rect.centery = position.centery

        self._animeCycle = 0
        self._animeTimeout = 250

    def update(self, cycleTime):
        '''Override from core.scene.SceneElement'''
        self._animeCycle += cycleTime
        if self._animeCycle >= self._animeTimeout:
            self.kill()

        self._rect.y -= 5
        self.dirty = 1
        
    @property
    def image(self):
        '''Override from core.scene.SceneElement'''
        return self._image

    @property
    def rect(self):
        '''Override from core.scene.SceneElement'''
        return self._rect

    def handleEvent(self, event):
        '''Override from core.scene.SceneElement'''
        pass