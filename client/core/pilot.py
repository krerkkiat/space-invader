import io
import urllib.request

import pygame
import fbconsole as fb
from pygame.compat import as_bytes

from config import *

class Pilot:
    def __init__(self, id_, name, topScore, topWave):
        self._id = id_
        self._name = name
        self._score = 0
        self._wave = 0
        self._topScore = topScore
        self._topWave = topWave

        self._hangar = []
        self._inventory = []

        BytesIO = pygame.compat.get_BytesIO()
        self._profilePicture = pygame.Surface((50, 50))
        self._profilePicture.fill(Config.colors['blue'])
        profile_pic_url = fb.graph_url('/{uid}/picture'.format(uid=self._id))
        with urllib.request.urlopen(profile_pic_url) as raw_img:
            self._profilePicture = pygame.image.load(BytesIO(raw_img.read()))
        
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def profilePicture(self):
        return self._profilePicture

    @property
    def score(self):
        return self._score
    @score.setter
    def score(self, value):
        self._score = value
    
    @property
    def wave(self):
        return self._wave
    @wave.setter
    def wave(self, value):
        self._wave = value

    @property
    def topScore(self):
        return self._topScore
    @topScore.setter
    def topScore(self, value):
        self._topScore = value

    @property
    def topWave(self):
        return self._topWave
    @topWave.setter
    def topWave(self, value):
        self._topWave = value

    @property
    def hangar(self):
        return self._hangar

    @property
    def inventory(self):
        return self._inventory
    