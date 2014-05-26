import socket
import asyncore
import threading

import json

def callback(data):
    print(data)

class TestClient(asyncore.dispatcher_with_send):

    def __init__(self, host, port, message):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.out_buffer = bytes(message, 'utf-8')    

    def handle_read(self):
        rawData = self.recv(8192)
        # print('Received {}'.format(rawData))
        data = rawData.decode('utf-8')
        msg = json.loads(data)
        # print(msg['data'])
        callback(msg['data'])
        
tc = TestClient('127.0.0.1', 12200, '''{"type":"action","value":"get","target":"resource_register_data"}''')
client = threading.Thread(target=asyncore.loop)
client.start()
s = input('>')
print(s)