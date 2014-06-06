import pygame
import fbconsole as fb

class Config:

    @classmethod
    def init(class_):
        class_.host = 'localhost'
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
        class_.colors['gray'] = (128, 128, 128)
        class_.colors['darkGray'] = (169, 169, 169)

        fb.SERVER_PORT = 8088 # port 8080 which are default are conflict with PHP server of postgreSQL
        fb.APP_ID = '831118013571771'   # use Project 02 app
        fb.AUTH_SCOPE = ['publish_stream']

Config.init()
