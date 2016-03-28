import socket
from .. Response import JeevesResponse

class WebServer:

    def __init__(self, server_config):
        self.config = server_config

    def create_listener(self):
        self.listener = socket.socket()
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def serve_forever(self, loud=False):
        self.listener.bind((self.config.HOST, self.config.PORT))
        self.listener.listen(self.config.MAX_REQUESTS)
        if loud:
            print("Serving on port " + str(self.config.PORT))
        while True:
            client_connection, client_address = self.listener.accept()
            request = client_connection.recv(1024)
            if request == b"":
                continue
            parsed_request = ParsedRequest(request)
            if loud:
                print("Request received for URL: " + str(parsed_request.location))
            response = self.build_response(parsed_request)
            if loud:
                print("Response status: " + str(response.status))
            client_connection.sendall(response.complete_binary_response())
            client_connection.close()
            
    def build_response(self, request):
        if self.config.RESPONSE_TYPE == "jeeves":
            return JeevesResponse(request)
        else:
            return BasicResponse(request)

class ParsedRequest:
    def __init__(self, request):
        self.raw_request = request
        self.request_string = request.decode('utf-8')
        self.request_parts = self.request_string.split('\r\n')
        # Parse the first line since it's unique
        top_line = self.request_parts[0].split(" ")
        self.type = top_line[0]
        self.location = top_line[1]
        self.protocol = top_line[2]
        # Parse all the rest of the lines
        self.headers = {}
        for part in self.request_parts[1:]:
            if part != "":
                line = [x.strip() for x in part.split(":")]
                self.headers[line[0]] = line[1]

class BasicResponse:
    pass

if __name__ == "__main__":
    print("Worked")