import pygame

import anyjson
import fbconsole as fb

from config import Config
from core.ui import Table, Button
from core.pilot import Pilot
from core.scene import Scene
from core.scene.test import TestScene
from core.manager import SceneManager, ConnectionManager

class MainScene(Scene):
    def __init(self, game):
        super().__init__(game)

        self._scoreBoard = None

    def loadData(self, preload):
        preload.isLoading = True
        try: 
            self._createScoreBoard()
            self._createUI()
        except Exception as e:
            print(e)
            SceneManager.exit()

        preload.isLoading = False
        # SceneManager.goto(GameScene(self._parent, {}, 7))
        # SceneManager.call(TestScene(self._parent))

    def _createUI(self):
        def callBack():
            SceneManager.call(TestScene(self._parent))
        self._startBtn = Button(self, 'Start', callBack)
        self._startBtn.rect.right = Config.windowWidth
        self._startBtn.rect.bottom = Config.windowHeight
        self.addElement(self._startBtn)
        self.addEventListener(self._startBtn.handleEvent)

    def _createScoreBoard(self):
        # get friends list
        fb_result = fb.fql('SELECT uid, name FROM user WHERE is_app_user AND uid IN (SELECT uid2 FROM friend WHERE uid1 = me())')

        # insert me
        fb_result.extend([{'uid':self._parent._pilot.id, 'name':'You'}])       # Pornchanok id

        # insert some fake data
        fb_result.extend([{'uid':'100000533319275', 'name':'Pornchanok'}])       # Pornchanok id
        # fb_result.extend([{'uid':'247059255488681', 'name':'Test User #1'}])     # friend of Test User #1
        # fb_result.extend([{'uid':'252287594960325', 'name':'Test User #2'}])     # friend of Test User #2

        friends_that_use_this_app = [entry['uid'] for entry in fb_result]
        data = bytes('{"type":"action","value":"get","target":"score_board","data":%s}' % anyjson.serialize(friends_that_use_this_app), 'utf-8')
        result = ConnectionManager.send(data)
        if ConnectionManager.isSuccessfulResponse(result):
            self._friends = []
            # data = [d['name'] = fd['name'] for d in result['data'] for fd in fb_result if fd['uid'] == d['id']]
            data = []
            for d in result['data']:
                for fd in fb_result:
                    if fd['uid'] == d['id']:
                        d['name'] = fd['name']
                        data.append(d)
            for f in result['data']:
                self._friends.append(Pilot(f['id'], f['name'], f['score'], f['wave'], f['time']))

        w, h = (400, 600)
        rowData = [('', 'Name', 'Score', 'Wave')]
        rowData.extend([(str(i), pilot.name, str(pilot.bestScore), str(pilot.bestWave)) for i, pilot in enumerate(self._friends, 1)])
        columnWidth = [30, 200, 75, 75]
        self._scoreBoard = Table(self, w, h, rowData, columnWidth, title='Score board')
        self.addElement(self._scoreBoard)
        self.addEventListener(self._scoreBoard.handleEvent)

    def run(self):
        for event in pygame.event.get():
            self._handleEvent(event)
        
        self.update()
        self.draw()
        self._clock.tick(Config.ticks)

    def update(self):
        super().update()

    def draw(self):
        updatedRects = self._elements.draw(self._canvas)
        pygame.display.update(updatedRects)