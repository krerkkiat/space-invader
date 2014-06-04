import os
import sys
import socket
import threading

import pygame
import fbconsole as fb

from config import Config
from core.scene import *
from core.pilot import Pilot
from core.manager import *

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

        LocalResourceManager.init()
        ConnectionManager.init()
        SceneManager.init()
           
    def run(self):
        SceneManager.call(MainScene(self), Preload(self))
        SceneManager.run()
        
if __name__ == '__main__':
    SpaceInvader().run()
        