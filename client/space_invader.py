import os
import sys
import urllib
import socket
import threading

import pygame
import fbconsole as fb

from config import Config
from core.manager import *
from core.pilot import Pilot
from core.scene.main import MainScene
from core.scene.preload import Preload

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

    def loadData(self, preload):
        preload.isLoading = True
        try:
            fb.authenticate()
            print('Authenticating to Facebook...', end=' ')
            result = fb.get('/me', {'fields':'id,name'})
            user_id = result['id']
            user_name = result['name']
            print('Complete')
            
            # fake user data
            # user_id = '100001868030396'
            # user_name = 'Krerkkiat Chusap'
            # 
            # user_id = '252287594960325'
            # user_name = 'Test User #1'
            # 
            # user_id = '247059255488681'
            # user_name = 'Test User #2'

            # login to our server
            print('Authenticating to our server...', end=' ')
            login_data = bytes('{"type":"action", "value":"login", "uid":"%s"}' % user_id, 'utf-8')
            result = ConnectionManager.send(login_data)
            if ConnectionManager.isSuccessfulResponse(result):
                user = result['data']['user']
                hangar = result['data']['hangar']
                self._pilot = Pilot(user_id, user_name, user['score'], user['wave'], user['time'])
                print('Complete')
            else:
                print('Fail')
                SceneManager.exit()

            # fetch and register resource_register_data
            print('Loading resource register data...', end=' ')
            result = ConnectionManager.send('''{"type":"action","value":"get","target":"resource_register_data"}''')
            if ConnectionManager.isSuccessfulResponse(result):
                print('Complete')
                print('Registering resource register data...', end=' ')
                for key in result['data']:
                    if key == 'surface':
                        self.regisSurfaces(result['data']['surface'])
                    elif key == 'sound':
                        pass
                    elif key == 'background_music':
                        pass
                    elif key == 'background_image':
                        pass
                print('Complete')

            # register local surface
            print('Registering local resource register data...', end=' ')
            SurfaceManager.register('upBtn', os.path.join(Config.assetsRoot, 'ui', 'up_btn.png'), convert_alpha=True)
            SurfaceManager.register('downBtn', os.path.join(Config.assetsRoot, 'ui', 'down_btn.png'), convert_alpha=True)
            SurfaceManager.register('leftBtn', os.path.join(Config.assetsRoot, 'ui', 'left_btn.png'), convert_alpha=True)
            SurfaceManager.register('rightBtn', os.path.join(Config.assetsRoot, 'ui', 'right_btn.png'), convert_alpha=True)
            print('Complete')
        except urllib.error.URLError as e:
            print('[Error]: Can not connect to server:', e.reason, e)
            preload.nextScene = None
            SceneManager.exit()
        except Exception as e:
            print('[Error]: Unexpected exception:', e.reason, e)
            preload.nextScene = None
            SceneManager.exit()
        preload.isLoading = False

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
        preload = Preload(self)
        preload.nextScene = None
        SceneManager.currentScene = preload
        load_thread = threading.Thread(target=self.loadData, args=(preload,))
        load_thread.start()
        SceneManager.run()

        SceneManager.call(MainScene(self), preload)
        SceneManager.run()

if __name__ == '__main__':
    SpaceInvader().run()
        