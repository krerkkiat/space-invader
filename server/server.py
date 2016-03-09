import os
import time
import socket
import logging
import asyncore
import urllib.parse

import psycopg2
import psycopg2.extras
import anyjson

from config import Config

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

    def handle_error(self):
        logger.exception('Something went wrong')

class ClientHandler(asyncore.dispatcher_with_send):

    def __init__(self, sock):
        super().__init__(sock)
        self._address = self.getpeername()
        self._dbConnection = psycopg2.connect('dbname={} user={} password={}'.format(Config.DB_NAME, Config.DB_USER, Config.DB_PASSWORD))
        logger.info('[%s:%d] Connected to database', self._address[0], self._address[1])

    def handle_read(self):
        out_msg = ''
        rawData = self.recv(8192)
        
        logger.info('[%s:%d] Received %d byte(s)', self._address[0], self._address[1], len(rawData))
        logger.debug('[%s:%d] incoming data: %s', self._address[0], self._address[1], rawData)
        
        if rawData:
            try:
                msg = anyjson.deserialize(rawData.decode('utf-8'))
                if msg['type'] == 'action':
                    if msg['value'] == 'get':
                        if msg['target'] == 'resource_register_data':
                            out_msg = self.handle_resource_register_data()
                        elif msg['target'] == 'score_board':
                            # expect list of uid
                            out_msg = self.handle_score_board(msg['data'])
                    elif msg['value'] == 'update':
                        if msg['target'] == 'user':
                            game_result = msg['game_result']
                            self.handle_update_user(game_result['id'], game_result['score'], game_result['wave'], game_result['time'])

                    elif msg['value'] == 'login':
                        out_msg = self.handle_login(msg['uid'])
            except Exception as e:
                logger.exception('[%s:%d] Something went wrong', self._address[0], self._address[1])
                self.out_buffer = self.encodeMessage('{"type":"info", "value":"error"}')
                return
        
        logger.debug('[%s:%d] out going data: %s', self._address[0], self._address[1], out_msg)
        self.out_buffer = self.encodeMessage(out_msg)
        
    def handle_resource_register_data(self):
        target_file = open(os.path.join(dataRoot, 'resource_register_data.json'), 'r')
        target_data = target_file.read()

        return '{"type":"response","to":"action","value":"get","target":"resource_register_data","status":"successful","data":%s}' % target_data
        
    def handle_update_user(self, uid, score, wave, time):
        cur = self._dbConnection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''UPDATE pilot SET score=%s, wave=%s, time=%s WHERE id=%s AND score<=%s'''
        cur.execute(query, (score, wave, time, uid, score))
        self._dbConnection.commit()

    def handle_login(self, uid):
        user = self.get_user(uid)
        out_msg = ''
        if user != None:
            hangar = self.get_hangar(uid)
            logger.info('[%s:%d] User login with id \'%s\'', self._address[0], self._address[1], user['id'])
            out_msg = '{"type":"response","to":"action","value":"login","status":"successful", "data":{"user":%s,"hangar":%s}}' % (anyjson.serialize(user), anyjson.serialize(hangar))
        else:
            # create new user
            self.create_user(uid)

            user = self.get_user(uid)
            hangar = self.get_hangar(uid)
            out_msg = '{"type":"response","to":"action","value":"login","status":"successful", "data":{"user":%s,"hangar":%s}}' % (anyjson.serialize(user), anyjson.serialize(hangar))
            
            logger.info('[%s:%d] New user created with id \'%s\'', self._address[0], self._address[1], uid)
        return out_msg

    def create_user(self, uid):
        cur = self._dbConnection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "INSERT INTO pilot (id, score, wave, money) VALUES (%s, 0, 0, 1000)"
        cur.execute(query, (uid,))
        # query = '''INSERT INTO hangar ("pilotId", "shipId", name, "weaponId", "armorId", "shieldId", "engineId") VALUES ('247059255488681', 'sh000', 'TS', 'wp000', 'am000', 'sd000', 'eg000')'''
        query = '''INSERT INTO hangar ("pilotId", "shipId", name, "weaponId", "armorId", "shieldId", "engineId") VALUES (%s, 'sh000', 'AAF-S-00', 'wp000', 'am000', 'sd000', 'eg000')'''
        cur.execute(query)

        self._dbConnection.commit()

    def handle_score_board(self, friends):
        users = self.get_score_board(friends)
        return '{"type":"response","to":"action","value":"get","target":"score_board","status":"successful", "data":%s}' % anyjson.serialize(users)

    def get_user(self, uid):
        query = "SELECT * FROM pilot WHERE id=%s;"
        cur = self._dbConnection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, (uid,))
        row = cur.fetchone()
        if row:
            row['id'] = row['id'].rstrip()
            return dict(row)
        else:
            return None

    def get_hangar(self, uid):
        query = 'SELECT * FROM "hangarData" WHERE "pilotId"=%s'
        cur = self._dbConnection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, (uid,))
        rows = cur.fetchall()
        return rows 

    def get_score_board(self, uids):
        cur = self._dbConnection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if len(uids) == 0:
            return []
        elif len(uids) > 1:
            query = "SELECT id, score, wave, time FROM pilot WHERE id IN %s ORDER BY score DESC, wave DESC;"
            cur.execute(query, (tuple(uids), ))
        elif len(uids) == 1:
            query = "SELECT id, score, wave, time FROM pilot WHERE id=%s ORDER BY score DESC, wave DESC;"
            cur.execute(query, tuple(uids))
        
        rows = cur.fetchall()

        users = []
        for row in rows:
            user = dict(row)
            user['id'] = user['id'].rstrip()
            users.append(user)

        return users        

    def handle_close(self):
        logger.info("[%s:%d] Disconnected", self._address[0], self._address[1])
        clients.pop(self._address)
        self.close()

        self._dbConnection.commit()
        logger.info('[%s:%d] Database commited', self._address[0], self._address[1])
        self._dbConnection.close()
        logger.info('[%s:%d] Database connection closed', self._address[0], self._address[1])

    def encodeMessage(self, msg):
        return bytes(msg, 'utf-8')

try:
    logger.info("Attemping to start server...")
    server = SpaceInvaderServer()
    logger.info("Server started at 127.0.0.1:%d", Config.PORT)
    asyncore.loop()
except KeyboardInterrupt as e:
    logger.info("Shutting down from KeyboardInterrupted")
    for client in clients:
        clients[client].close()
    server.close()
    logger.info("All client connections closed")
except asyncore.ExitNow as e:
    logger.info("Shutting down from asyncore.ExitNow")
    for client in clients:
        clients[client].close()
    server.close()
    logger.info("All client connections closed")
except Exception as e:
    logger.exception('Something went wrong')
    logger.critical('Shutting down from unknow critical error: %s:%s', e.reason, e)
logger.info('Shutting down successful')
logging.shutdown()

'''
messsage structure

when user login, server use this for response
'data': {
    'user': {
        'id':
        'score':
        'wave':
        'money':
        'lastestUseSpaceship': sid
    },
    'hangar': [
        {
            'sid':
            'name':
            'weapon': {} // getWeapon(weaponId) or getItem(type, id_)
            'armor': {} // bha bha
            'shield': {}
            'engine': {}
        }
    ],
    'inventory': [
        {
            'iid':
            'item': { } // each item data via getItem(type, id_) 
            'amount'
        }
    ]
}

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