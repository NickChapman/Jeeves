from . WebServer.Config import ServerConfig

class JeevesResponse:
    def __init__(self, request):
        self.request = request
        self.response_body = self.get_requested_resource(ServerConfig.SERVER_ROOT + request.location)

    def get_requested_resource(self, resource_path):
        """LOADS FILES AND MANAGES THE STATUS"""
        try:
            resource = self.load_file_bytes(resource_path)
            self.status = "200 OK"
            return resource
        except FileNotFoundError:
            self.status = "404 Not Found"
            return b""
    
    def load_file_bytes(self, file):
        with open(file, 'rb') as f:
            contents = f.readlines()
            file_string = b''.join(contents)
            return file_string

    def complete_response(self):
        complete_response_string = b""
        complete_response_string += bytes(self.request.protocol + " ", "utf-8")
        complete_response_string += bytes(self.status, "utf-8")
        complete_response_string += bytes("\n" + "Content-type: text/html", "utf-8")
        complete_response_string += bytes("\n\n", "utf-8")
        complete_response_string += self.response_body
        return complete_response_string