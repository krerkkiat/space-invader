from core.scene import Scene

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
        self._pilotBar = PilotBar(self, self._parent._pilot)
        self._scoreBar = ScoreBar(self. self._parent._pilot)
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