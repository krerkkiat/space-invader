import logging

class Config:
    
    @classmethod
    def init(class_):
        class_.DB_NAME = 'spaceInvader'
        class_.DB_USER = 'pilot'
        class_.DB_PASSWORD = 'pilot'

        class_.PORT = 12200

        class_.LOG_FILE = 'server.log'
        class_.LOG_FILE_LEVEL = logging.DEBUG
        class_.LOG_CONSOLE_LEVEL = logging.INFO
        class_.LOG_FORMAT = '%(asctime)s %(name)s [%(levelname)s] %(message)s'


Config.init()   # init Config