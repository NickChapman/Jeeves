from Jeeves.WebServer.WebServer import WebServer
from Jeeves.WebServer.Config import ServerConfig

server = WebServer(ServerConfig)
server.create_listener()
server.serve_forever(True)