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