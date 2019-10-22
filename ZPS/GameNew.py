from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json

clients = []
clientCnt = [0]
globalObj = {}
globalObj["playerCount"] = 0

class GameServer(WebSocket):

      boardSizeX = 800
      boardSizeY = 600
      playerId = 0
      bombs = 5
      score = 0
      myNick = ""

      def checkPlayer(self, msg):
         #print(msg)
         msgWelcome = {}
         if msg["uid"] == "":
            msgWelcome["msg_code"] = "welcome_msg"
            msgWelcome['size_x'] = self.boardSizeX
            msgWelcome["size_y"] = self.boardSizeY
            msgWelcome["client_uid"] = "ID" + str(globalObj["playerCount"])
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
      

      def handleMessage(self):

         msgFromPlayer = json.loads(self.data)
         print(msgFromPlayer)

         if msgFromPlayer["msg_code"] == "connect":
            self.checkPlayer(msgFromPlayer)

         if msgFromPlayer["msg_code"] == "player_pos":
            self.resendPlayerPosition(msgFromPlayer)

         #for client in clients:
         #   if client != self:
         #      client.sendMessage(self.address[0] + u' - ' + self.data)

      def handleConnected(self):
         print(self.address, 'connected')
         for client in clients:
            client.sendMessage(self.address[0] + u' - connected')
         clients.append(self)

      def handleClose(self):
         clients.remove(self)
         print(self.address, 'closed')
         for client in clients:
            client.sendMessage(self.address[0] + u' - disconnected')

server = SimpleWebSocketServer('', 8000, GameServer)
server.serveforever()