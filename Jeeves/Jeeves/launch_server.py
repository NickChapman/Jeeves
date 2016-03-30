from JeevesServer.WebServer.WebServer import WebServer
from JeevesServer.WebServer.Config import ServerConfig

server = WebServer(ServerConfig)
server.create_listener()
server.serve_forever(True)