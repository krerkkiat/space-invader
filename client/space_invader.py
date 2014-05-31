import os
import sys
import json
import socket
import threading

import pygame
import fbconsole as fb

from config import Config
from core.scene import TestScene
from core.client import SpaceInvaderClient
from core.registerer import Registerer
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
        
        fb.SERVER_PORT = 8088 # port 8080 which are default are conflict with PHP server of postgreSQL
        fb.AUTH_SCOPE = ['publish_stream']
        fb.authenticate()
        result = fb.get('/me')
        id_ = result['id']
        name = result['name']

        self._pilot = Pilot(id_, name)

        ConnectionManager.init()

        # login to our server
        login_data = bytes('{"type":"action", "value":"login", "uid":"%s"}' % self._pilot.id, 'utf-8')
        result = ConnectionManager.send(login_data)
        if not ConnectionManager.isSuccessfulResponse(result):
            sys.exit()

        # fetch local resource register data
        result = ConnectionManager.send('''{"type":"action","value":"get","target":"resource_register_data"}''')
        for key in result['data']:
            if key == 'surface':
                self.regisSurfaces(result['data']['surface'])
                
                    # SurfaceManager.register('sh000', os.path.join(Config.assetsRoot, 'spaceship', 'arboris', 'arboris_left.png'), color_key=(255, 0, 255))

        ConnectionManager.close()

    def regisSurfaces(self, surfaces):
        for id_ in surfaces:
            for i in range(len(surfaces[id_])): 
                color_key = None
                convert_alpha = False
                if 'color_key' in surfaces[id_][i]:
                    color_key = tuple(surfaces[id_][i]['color_key'])
                if 'convert_alpha' in surfaces[id_][i]:
                    convert_alpha = True

                path = Config.assetsRoot + ',' + ','.join(surfaces[id_][i]['path'])
                SurfaceManager.register(id_, os.path.join(*path.split(',')), color_key=color_key, convert_alpha=convert_alpha)
                
    def run(self):
        TestScene(self, self._pilot).run()

if __name__ == '__main__':
    pilot = None
    SpaceInvader().run()
        