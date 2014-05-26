import asyncore
import threading

import pygame
import fbconsole as fb

from config import Config
from core.scene import TestScene
from core.client import SpaceInvaderClient
from core.registerer import Registerer 

class SpaceInvader:
    def __init__(self):
        # init pygame
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.mixer.init()
        pygame.key.set_repeat(1, 30)
        pygame.mouse.set_visible(1)

        pygame.display.set_mode(Config.windowSize)

        # pygame.display.set_mode(Config.windowSize, pygame.FULLSCREEN)

        # fullscreen with current resolution
        # screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
        # Config.windowSize = Config.windowWidth, Config.windowHeight = screen.get_size()

        pygame.display.set_caption(Config.windowCaption)
        
        icon = pygame.Surface((1,1))
        icon.set_alpha(0)
        pygame.display.set_icon(icon)
        
        fb.SERVER_PORT = 8088 # port 8080 which are default are conflict with PHP server of postgreSQL
        fb.AUTH_SCOPE = ['publish_stream']
        fb.authenticate()

        self.client = SpaceInvaderClient()
        self.clientThread = threading.Thread(target=asyncore.loop)
        self.clientThread.start()

        registerer = Registerer(self.client)

    def run(self):
        TestScene(self).run()

if __name__ == '__main__':
    SpaceInvader().run()
        