import os
import time
# import json
import socket
import logging
import asyncore
import urllib.parse

import psycopg2
import anyjson

from config import Config

'''
# production code
# not use anymore because we can not run on heroku
# 
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

databaseConnection = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)'''

clients = dict()

logger = logging.getLogger('spaceinvader')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(Config.LOG_FILE)
fh.setLevel(Config.LOG_FILE_LEVEL)

ch = logging.StreamHandler()
ch.setLevel(Config.LOG_CONSOLE_LEVEL)

formatter = logging.Formatter(Config.LOG_FORMAT)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

dataRoot = 'data'

class SpaceInvaderServer(asyncore.dispatcher):

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', Config.PORT))
        self.listen(5)

    def handle_accepted(self, newSocket, address):
        logger.info("Connection from %s:%d accepted", address[0], address[1])
        clients[address] = ClientHandler(newSocket)

class ClientHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        address = self.getpeername()
        rawData = self.recv(8192)
        
        logger.info('[%s:%d] Received %d byte(s)', address[0], address[1], len(rawData))
        logger.debug('[%s:%d] data: %s', address[0], address[1], rawData)
        
        if rawData:
            # processing request message
            try:
                # q: why? i need to double decode this json text?
                # a: double json encode (encode json string)
                # msg = anyjson.deserialize(anyjson.deserialize(rawData.decode('utf-8')))
                msg = anyjson.deserialize(rawData.decode('utf-8'))
                if msg['type'] == 'action':
                    if msg['value'] == 'get':
                        if msg['target'] == 'resource_register_data':
                            target_file = open(os.path.join(dataRoot, 'resource_register_data.json'), 'r')
                            target_data = target_file.read()

                            out_msg = '''{"type":"response","to":"action","value":"get","target":"resource_register_data","status":"successful","data":%s}''' % target_data
                            logger.debug('[%s:%d] out going data: %s', address[0], address[1], out_msg)

                            self.out_buffer = self.encodeMessage(out_msg)
                    elif msg['value'] == 'login':
                        uid = msg['uid']
                        cur = databaseConnection.cursor()
                        cur.execute("SELECT id from pilot WHERE id=%s", (uid,))
                        row = cur.fetchone()
                        if row != None:
                            logger.info('[%s:%d] User login with id \'%s\'', address[0], address[1], row[0].rstrip())
                            
                            out_msg = '{"type":"response","to":"action","value":"login","status":"successful"}'
                            self.out_buffer = self.encodeMessage(out_msg)
                        else:
                            out_msg = '{"type":"response","to":"action","value":"login","status":"fail"}'
                            self.out_buffer = self.encodeMessage(out_msg)

            except Exception as e:
                logger.exception('[%s:%d] Something went wrong', address[0], address[1])
                self.out_buffer = self.encodeMessage('{"type":"info", "value":"error"}')
                return

    def handle_close(self):
        address = self.getpeername()
        logger.info("[%s:%d] Disconnected", address[0], address[1])
        clients.pop(address)
        self.close()

    def encodeMessage(self, msg):
        return bytes(msg, 'utf-8')
try:
    logger.info("Attemping to start server...")

    # development code
    databaseConnection = psycopg2.connect('dbname={} user={} password={}'.format(Config.DB_NAME, Config.DB_USER, Config.DB_PASSWORD))
    logger.info("Connected to database server")
    
    SpaceInvaderServer()
    logger.info("Server started at 127.0.0.1:%d", Config.PORT)
    asyncore.loop()
except KeyboardInterrupt as e:
    logger.info("Shutting down from KeyboardInterrupted")
    for client in clients:
        clients[client].close()
    logger.info("All client connections closed")

    databaseConnection.commit()
    logger.info("Database commited")
    databaseConnection.close()
    logger.info("Database connection closed")
    
except Exception as e:
    logger.exception('Something went wrong')
    logger.critical('Shutting down from unknow critical error: %s', e)
logger.info('Shutting down successful')
logging.shutdown()

'''
msg structure
{
    'type': 'action'
    'value': 'add',???
    'target': ['userdata', 'shipyard', 'shop', 'hangar']
    'id': <id>
    'data': [
        { 'columnName': 'value'}, ...
    ]
}

{
    'type': 'action'
    'value': 'get',
    'target': ['userdata', 'shipyard', 'shop', 'hangar', 'id']
    'id': 'all' or 'id'
}

{
    'type': 'action'
    'value': 'update',
    'target': ['userdata', 'shipyard', 'shop', 'hangar']
    'id': <id>
    'data': [
        { 'columnName': 'value'}, ...
    ]
}

{
    'type': 'action'
    'value': 'remove',
    'target': ['userdata', 'shipyard', 'shop', 'hangar']
    'id': <id>
}

{
    'type': 'action'
    'value': 'buy',
    'target': ['weapon', 'spaceship', 'armor', 'shield', 'engine']
    'id': <id>
}

{
    'type': 'action'
    'value': 'sell',
    'target': ['weapon', 'spaceship', 'armor', 'shield', 'engine']
    'id': <id>
}

{
    'type': 'info',
    'value': 'successful'
}

{
    'type': 'info',
    'value': 'error',
    'reason': 'bababa...'
}

get : response with data
update : return result
remove : return result
'''