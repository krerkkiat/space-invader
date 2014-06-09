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