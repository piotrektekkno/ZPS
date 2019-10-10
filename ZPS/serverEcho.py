
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
class SimpleEcho(WebSocket):
    
    
    def handleMessage(self):
        # echo message back to client
        s_x = 800 
        s_y = 600
        y = json.loads(self.data)
        print(y["req_type"])

        if  y["req_type"] == "boardSize":
            print(y["x_size"])
            y["x_size"] = s_x
            y["y_size"] = s_y
            self.sendMessage(json.dumps(y))
        
        if  y["req_type"] == "myPosition":
            print(y)
            
            
        
    def handleConnected(self):
        print(self.address, 'connected')
        print('size')

    def handleClose(self):
        print(self.address, 'closed')

server = SimpleWebSocketServer('', 8000, SimpleEcho)
server.serveforever()