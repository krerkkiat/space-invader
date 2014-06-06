import io
import urllib.request

import pygame
import fbconsole as fb
from pygame.compat import as_bytes

from config import *

class Pilot:
    def __init__(self, id_, name, bestScore, bestWave, time):
        self._id = id_
        self._name = name
        self._score = 0
        self._wave = 0
        self._bestScore = bestScore
        self._bestWave = bestWave
        self._bestTime = time

        self._hangar = []
        self._inventory = []

        if self._name == None:
            result = fb.get('/me', {'fields':'name'})
            self._name = result['name']

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
    def bestScore(self):
        return self._bestScore
    @bestScore.setter
    def bestScore(self, value):
        self._bestScore = value

    @property
    def bestWave(self):
        return self._bestWave
    @bestWave.setter
    def bestWave(self, value):
        self._bestWave = value

    @property
    def bestTime(self):
        return self._bestTime
    @bestTime.setter
    def bestTime(self, value):
        self._bestTime = value
    

    @property
    def hangar(self):
        return self._hangar

    @property
    def inventory(self):
        return self._inventory
    