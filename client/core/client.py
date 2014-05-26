import socket
import asyncore
import threading

from config import *

class SpaceInvaderClient(asyncore.dispatcher):
    # observer design pattern

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self._observers = []

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((Config.host, Config.port))

    def handle_read(self):
        rawData = self.recv(8192)
        data = rawData.decode('utf-8')
        msg = json.loads(data)
        self.notify(message=msg)

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, message, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self, message)