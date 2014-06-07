import pygame

from core.ui import *
from core.scene import *
from core.enemy import *

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

class Armor:
    '''Represent an armor of the spaceship'''

    @classmethod
    def fromJSON(class_, obj):
        return Armor(obj['id'], obj['name'], obj['defence'])

    def __init__(self, id_, name, defence):
        self._id = id_
        self._name = name
        self._defence = defence

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def defence(self):
        return self._defence

class Shield(pygame.sprite.DirtySprite):
    '''Repersent a spaceship's shield'''

    @classmethod
    def fromJSON(class_, obj):
        return Shield(obj['id'], obj['name'], obj['drainRate'], obj['hitDarinRate'])

    def __init__(self, id_, name, drainRate, drainRateInterval, hitDarinRate):
        super().__init__()

        self._id = id_
        self._thing = None
        self._name = name
        self._drainRate = drainRate
        self._drainRateInterval = drainRateInterval
        self._hitDrainRate = hitDarinRate
        self._isActivate = False

        self._image = SurfaceManager.get(self._id)[0]
        self._rect = self._image.get_rect()

        self._drainRateCycle = 0

        self._anime = 0
        self._animeCycle = 0
        self._animeInterval = 100

        self.dirty = 0

    def update(self, cycleTime, engine=None):
        if self._isActivate and engine:
            self._animeCycle += cycleTime
            if self._animeCycle >= self._animeInterval:
                self._animeCycle = 0
                self._anime = (self._anime+1)%len(SurfaceManager.get(self._id))

            self._drainRateCycle += cycleTime
            if self._drainRateCycle >= self._drainRateInterval:
                engine.energy -= self._drainRate

                self._drainRateCycle = 0

            if engine.energy <= 0:
                engine.energy = 0
                self._isActivate = False
                self.kill()
            self.dirty = 1

    @property
    def image(self):
        return SurfaceManager.get(self._id)[self._anime]

    @property
    def rect(self):
        self._rect = self.image.get_rect()
        self._rect.centerx = self._thing.rect.centerx
        self._rect.centery = self._thing.rect.centery
        return self._rect

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def drainRate(self):
        return self._drainRate

    @property
    def hitDrainRate(self):
        return self._hitDrainRate

    @property
    def isActivate(self):
        return self._isActivate
    @isActivate.setter
    def isActivate(self, value):
        self._isActivate = value

    @property
    def thing(self):
        return self._thing
    @thing.setter
    def thing(self, value):
        self._thing = value

class Engine:
    '''Represent a spaceship's engine'''

    @classmethod
    def fromJSON(class_, obj):
        return Engine(obj['id'], obj['name'], obj['maxEnergy'], obj['regenerateRate'])

    def __init__(self, id_, name, maxEnergy, regenerateRate, regenerateInterval):
        self._id = id_
        self._name = name
        self._energy = maxEnergy
        self._maxEnergy = maxEnergy
        self._regenerateRate = regenerateRate
        self._regenerateInterval = regenerateInterval

        self._regenerateCycle = 0

    def update(self, cycleTime):
        self._regenerateCycle += cycleTime
        if self._regenerateCycle >= self._regenerateInterval:
            self._energy += self._regenerateRate
            if self._energy > self._maxEnergy:
                self._energy = self._maxEnergy

            self._regenerateCycle = 0

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def energy(self):
        return self._energy
    @energy.setter
    def energy(self, value):
        self._energy = value

    @property
    def maxEnergy(self):
        return self._maxEnergy

    @property
    def regenerateRate(self):
        return self._regenerateRate