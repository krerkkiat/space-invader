import pygame

from core.manager import *

class Config:

    @classmethod
    def init(class_):
        class_.host = '127.0.0.1'
        class_.port = 12200

        class_.assetsRoot = 'assets'
        class_.windowSize = class_.windowWidth, class_.windowHeight = (800, 700)
        class_.windowCaption = 'Space Invader'

        class_.ticks = 60

        class_.colors = dict()
        class_.colors['white'] = (255, 255, 255)
        class_.colors['black'] = (0, 0, 0)

        class_.colors['red'] = (255, 0, 0)
        class_.colors['green'] = (0, 255, 0)
        class_.colors['blue'] = (0, 0, 255)

        class_.colors['aquamarine'] = (127, 255, 212)

Config.init()