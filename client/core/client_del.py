import socket
import asyncore
import threading

import anyjson

from config import *

class SpaceInvaderClient(asyncore.dispatcher):
    # observer design pattern

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self._observers = []

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((Config.host, Config.port))

        self.out_buffer = bytes('''{"type":"action","value":"get","target":"resource_register_data"}''', 'utf-8')

    def handle_read(self):
        try:
            rawData = self.recv(8192)
            print('raw', rawData)
            data = rawData.decode('utf-8')
            print('data', data)
            if data:
                msg = anyjson.deserialize(data)
                print('client recved')
                prnt('msg', msg)
                self.notify(message=msg)
        except Exception as e:
            print(e)

    def setOutMessage(self, msg):
        self.out_buffer = bytes(msg, 'utf-8')

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