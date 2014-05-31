import io
import urllib.request

import pygame
import fbconsole as fb
from pygame.compat import as_bytes

from config import *

class Pilot:
    def __init__(self, id_, name):
        self._id = id_
        self._name = name

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