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
globalObj["timerIsStarted"] = 0
globalObj["newBombVal"] = 30
globalObj["newBombCntr"] = 5
globalObj["boardSizeX"] = 800
globalObj["boardSizeY"] = 600
globalObj["bSeq"] = 1

globalPlayersUid={}
globalPlayersScore={}
globalPlayersBombs={}
globalPlayersNicks={}

globalBombs = []
xRng = 20
yRng = 20

class GameServer(WebSocket):
   
      playerId = 0
      bombs = 5
      score = 0
      myNick = ""
      myUid = ""
      waitStp = 0

      def backGroundTasksPoints(self):

         if globalObj["actualExpBombUser"] ==  self.myUid and globalObj["kiledUser"] != self.myUid:
            self.score  = self.score + 1
            globalPlayersScore[self.myUid] = self.score
            globalObj["actualExpBombUser"] = "NA"
            globalObj["kiledUser"] = "NA"
            msgScore = {}
            msgScore["msg_code"] = "current score"
            msgScore["score"] = self.score
            self.sendMessage(json.dumps(msgScore))

         bckgTskPt = threading.Timer(0.1, self.backGroundTasksPoints) 
         bckgTskPt.start()


      def backGroundTasksAll(self):
         
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

               
         globalObj["newBombCntr"] =  globalObj["newBombCntr"] - 1
         print("newBombCntr" + str(globalObj["newBombCntr"]))
         if globalObj["newBombCntr"] <= 0:
            msgNewBombBox = {}
            msgNewBombBox["msg_code"] = "new_bomb_box"
            bid =  "BMB" + str(globalObj["bSeq"])
            msgNewBombBox["box_uid"] = bid
            msgNewBombBox["x"] = random.randint(1, globalObj["boardSizeX"])
            msgNewBombBox["y"] = random.randint(1, globalObj["boardSizeY"])
            globalObj["newBombCntr"] = globalObj["newBombVal"]
            globalObj["bSeq"] = globalObj["bSeq"] + 1
            globalObj[bid] = "ACT"
            print("Nowa bomba")
            for client in clients:
               client.sendMessage(json.dumps(msgNewBombBox))


         bckgTsk = threading.Timer(1.0, self.backGroundTasksAll) 
         bckgTsk.start()
         globalObj["timerIsStarted"] = 1
         print("actual bombs cnt" + str(len(globalBombs)))

      def checkPlayer(self, msg):
         #print(msg)
         msgWelcome = {}
         if msg["uid"] == "":
            self.myUid = "ID" + str(globalObj["playerCount"])
            msgWelcome["msg_code"] = "welcome_msg"
            msgWelcome['size_x'] = globalObj["boardSizeX"]
            msgWelcome["size_y"] = globalObj["boardSizeY"]
            msgWelcome["client_uid"]  = self.myUid
            msgWelcome["bombs_amount"] = self.bombs
            msgWelcome["current_score"] = self.score
            globalPlayersUid[self.myUid] = self.myUid
            globalPlayersScore[self.myUid] = self.score
            globalPlayersBombs[self.myUid] = self.bombs
            globalPlayersNicks[self.myUid] = self.myNick
            
            globalObj["playerCount"] = globalObj["playerCount"] + 1
            self.myNick = msg["nick"]
            
         if msg["uid"] != "" and globalPlayersUid[msg["uid"]] != "":
            msgWelcome["msg_code"] = "welcome_msg"
            msgWelcome['size_x'] = globalObj["boardSizeX"]
            msgWelcome["size_y"] = globalObj["boardSizeY"]
            self.myUid = globalPlayersUid[msg["uid"]]
            self.bombs = globalPlayersBombs[msg["uid"]]
            self.score = globalPlayersScore[msg["uid"]]
            msgWelcome["client_uid"]  = self.myUid
            msgWelcome["bombs_amount"] = self.bombs
            msgWelcome["current_score"] = self.score
            self.myNick = msg["nick"]
            
         self.sendMessage(json.dumps(msgWelcome))
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
         self.bombs = self.bombs - 1
         globalPlayersBombs[self.myUid] = self.bombs
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
            globalObj["kiledUser"] = self.myUid
            msgPosition = {}
            msgPosition["x"] = -100
            msgPosition["y"] = -100
            self.resendPlayerPosition(msgPosition)

         if msgFromPlayer["msg_code"] == "collected_new_box_bomb":
            bmbBoxid = msgFromPlayer["box_uid"]
            if globalObj[bmbBoxid] == "ACT":
               self.bombs = self.bombs + 1
               globalObj[bmbBoxid] = "NA"
               globalPlayersBombs[self.myUid] = self.bombs
               msgBombs = {}
               msgBombs["msg_code"] = "bomb_amount"
               msgBombs["amount"] = self.bombs
               self.sendMessage(json.dumps(msgBombs))

      def handleConnected(self):
         if globalObj["timerIsStarted"] == 0:
            self.backGroundTasksAll()
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