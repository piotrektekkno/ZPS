from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
import threading
import random

clients = []
clientCnt = [0]
globalObj = {}
globalObj["playerCount"] = 0
globalObj["bombId"] = 0
globalObj["actualExpBombUser"] =  "NA"
globalObj["kiledUser"] =  "NA"
timerIsStarted = 0
globalBombs = []
xRng = 20
yRng = 20

class GameServer(WebSocket):

      boardSizeX = 800
      boardSizeY = 600
      playerId = 0
      bombs = 5
      score = 0
      myNick = ""
      myUid = ""
      waitStp = 0

      def backGroundTasksPoints(self):

         if globalObj["actualExpBombUser"] ==  self.myUid and globalObj["kiledUser"] != self.myUid:
            score  = score + 1
            globalObj["actualExpBombUser"] = "NA"
            globalObj["kiledUser"] = "NA"
            print("Dobane punkty")

         bckgTskPt = threading.Timer(0.5, self.backGroundTasksPoints) 
         bckgTskPt.start()


      def backGroundTasksExplBoms(self):
         
         for bm in globalBombs:
            msgBomExplode = {}
            self.waitStp = self.waitStp - 1
            if bm["active"] == "yes":
               bm["toExplode"] =  bm["toExplode"] - 1

            if self.waitStp <= 0:
               globalObj["actualExpBombUser"]  = "NA"
               globalObj["kiledUser"] =  "NA"
               
            if bm["toExplode"] <= 0 and bm["active"] == "yes" and self.waitStp <= 0:
               bm["active"] = "no"
               msgBomExplode["msg_code"] = "Bomb exploded"
               msgBomExplode["x_range"] = bm["x_range"]
               msgBomExplode["y_range"] = bm["y_range"]
               msgBomExplode["bomb_uid"] = bm["bombId"]
               self.waitStp = 3
               globalObj["actualExpBombUser"] = bm["userId"] 
               for client in clients:
                  client.sendMessage(json.dumps(msgBomExplode))
               print("bomba wyb")
         bckgTsk = threading.Timer(1.0, self.backGroundTasksExplBoms) 
         bckgTsk.start()
         timerIsStarted = 1
         print("actual bombs cnt" + str(len(globalBombs)))

      

      def checkPlayer(self, msg):
         #print(msg)
         msgWelcome = {}
         if msg["uid"] == "":
            self.myUid = "ID" + str(globalObj["playerCount"])
            msgWelcome["msg_code"] = "welcome_msg"
            msgWelcome['size_x'] = self.boardSizeX
            msgWelcome["size_y"] = self.boardSizeY
            msgWelcome["client_uid"] = self.myUid
            msgWelcome["bombs_amount"] = self.bombs
            msgWelcome["current_score"] = self.score
            self.sendMessage(json.dumps(msgWelcome))
            globalObj["playerCount"] = globalObj["playerCount"] + 1
            self.myNick = msg["nick"]

      def resendPlayerPosition(self, msg):
         msgPosition = {}
         msgPosition["msg_code"] = "player_pos"
         msgPosition["nick"] = self.myNick
         msgPosition["x"] = msg["x"]
         msgPosition["y"] = msg["y"]

         for client in clients:
            if client != self:
               client.sendMessage(json.dumps(msgPosition))

      def resendBombIsPlanted(self, msg):
         msgPuttedBombPosition = {}
         msgPuttedBombPosition["msg_code"] = "Bomb has been planted"
         bomb_uid = "BID" + str(globalObj["bombId"]) + "_" + self.myUid
         msgPuttedBombPosition["bomb_uid"] = bomb_uid
         msgPuttedBombPosition["x"] = msg["x"]
         msgPuttedBombPosition["y"] = msg["y"]
         globalObj["bombId"] = globalObj["bombId"] + 1
         bmb = {}
         bmb["x_range"] = random.randint(1, xRng)
         bmb["y_range"] = random.randint(1, yRng)
         bmb["bombId"] = bomb_uid
         bmb["toExplode"] = msg["time_to_explode"]
         bmb["active"] = "yes"
         bmb["userId"] = self.myUid
         globalBombs.append(bmb)

         for client in clients:
            client.sendMessage(json.dumps(msgPuttedBombPosition))
         #print(msgPuttedBombPosition)
      

      def handleMessage(self):

         msgFromPlayer = json.loads(self.data)
         print(msgFromPlayer)

         if msgFromPlayer["msg_code"] == "connect":
            self.checkPlayer(msgFromPlayer)

         if msgFromPlayer["msg_code"] == "player_pos":
            self.resendPlayerPosition(msgFromPlayer)

         if msgFromPlayer["msg_code"] == "player_plant_bomb":
            self.resendBombIsPlanted(msgFromPlayer)

         if msgFromPlayer["msg_code"] == "bomb_killed_me":
            globalObj["kiledUser"] = selfmyUid
         #for client in clients:
         #   if client != self:
         #      client.sendMessage(self.address[0] + u' - ' + self.data)

      def handleConnected(self):
         if timerIsStarted == 0:
            self.backGroundTasksExplBoms()
            self.backGroundTasksPoints()
         print(self.address, 'connected')
         #for client in clients:
         #   client.sendMessage(self.address[0] + u' - connected')
         clients.append(self)

      def handleClose(self):
         clients.remove(self)
         print(self.address, 'closed')
         #for client in clients:
         #   client.sendMessage(self.address[0] + u' - disconnected')

server = SimpleWebSocketServer('', 8000, GameServer)
server.serveforever()