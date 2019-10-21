from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json

clients = []

class GameServer(WebSocket):

      boardSizeX = 800
      boardSizeY = 600
      playerId = 0
      bombs = 5

      def checkPlayer(self, msg):
         print(msg)
         msgWelcome = {}
         if msg["uid"] == "":
            msgWelcome["msg_code"] = "welcome_msg"
            msgWelcome['size_x'] = self.boardSizeX
            msgWelcome["size_y"] = self.boardSizeY
            msgWelcome["client_uid"] = "ID" + str(self.playerId)
            msgWelcome["bombs_amount"] = 5
            msgWelcome["current_score"] = 0
            self.sendMessage(json.dumps(msgWelcome))
            self.playerId = self.playerId + 1;
         print("Working2")


      def handleMessage(self):

         msgFromPlayer = json.loads(self.data)
         print(msgFromPlayer)

         if msgFromPlayer["msg_code"] == "connect":
            self.checkPlayer(msgFromPlayer)

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