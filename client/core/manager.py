import sys
import socket
import threading

import pygame
import anyjson

from config import Config

class SceneManager:

    @classmethod
    def init(class_):
        class_.sceneStack = []
        class_.currentScene = None

    @classmethod
    def call(class_, scene, preload=None):
        class_.sceneStack.append(class_.currentScene)

        if preload:
            preload.nextScene = scene
            class_.currentScene = preload
            load_thread = threading.Thread(target=scene.loadData, args=(preload,))
            load_thread.start()
        else:
            class_.currentScene = scene

    @classmethod
    def ret(class_):
        class_.currentScene = class_.sceneStack.pop(len(class_.sceneStack)-1)

    @classmethod
    def goto(class_, scene):
        class_.currentScene = scene

    @classmethod
    def clear(class_):
        class_.sceneStack.clear()

    @classmethod
    def run(class_):
        while class_.currentScene:
            class_.currentScene.run()

    @classmethod
    def exit(class_):
        class_.currentScene = None
        pygame.quit()
        ConnectionManager.close()
        sys.exit()

class ConnectionManager:

    @classmethod
    def init(class_):
        class_._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        class_._socket.connect((Config.host, Config.port))

    @classmethod
    def send(class_, message):
        '''send and recv ??'''
        if type(message) == bytes:
            class_._socket.send(message)
        else:
            class_._socket.send(bytes(message, 'utf-8'))

        src = class_._socket.recv(8192).decode('utf-8')
        result = anyjson.deserialize(src)
        return result

    @classmethod
    def isSuccessfulResponse(class_, result):
        return result['type'] == 'response' and result['status'] == 'successful'

    @classmethod
    def close(class_):
        class_._socket.close()

class LocalResourceManager:
    '''Provide resource from assets root to object
    that require such as surface, sound, etc'''

    @classmethod
    def init(class_):
        '''Inintialize LocalResourceManager'''
        class_._resources = dict()

    @classmethod
    def register(class_, id_, file_):
        '''Register resource with id to LocalResourceManager._resources dict'''
        raise NotImplementedError('Sub-class should overide this method')

    @classmethod
    def get(class_, id_):
        '''Get resource from LocalResourceManager._resources dict'''
        return class_._resources[id_]

class Font(LocalResourceManager):
    def register(class_, id_, path):
        class_._resources[id_] = pygame.font.Font(path)

class SurfaceManager(LocalResourceManager):
    '''Provide resource of surface'''

    @classmethod
    def register(class_, id_, path, color_key=None, convert_alpha=False):
        if id_ not in class_._resources:
            class_._resources[id_] = list()

        sur = pygame.image.load(path)
        if color_key != None:
            sur.set_colorkey(color_key)

        if convert_alpha:
            class_._resources[id_].append(sur.convert_alpha())
        else:
            class_._resources[id_].append(sur.convert())

class MusicManager(LocalResourceManager):

    @classmethod
    def register(class_, id_, path):
        class_._resources[id_] = path

    @classmethod
    def loadToCurrentMusic(class_, id_):
        path = class_._resources[id_]
        pygame.mixer.music.load(path)

    @classmethod
    def playCurrentMusic(class_, id_):
        pygame.mixer.music.play(-1)

    @classmethod
    def pauseCurrentMusic(class_):
        pygame.mixer.music.pause()

    @classmethod
    def unpauseCurrentMusic(class_):
        pygame.mixer.music.unpause()

    @classmethod
    def stopCurrentMusic(class_):
        pygame.mixer.music.fadeout(900)

class SoundEffectManager(LocalResourceManager):

    @classmethod
    def register(class_, id_, path):
        class_._resources[id_] = pygame.mixer.Sound(path)
