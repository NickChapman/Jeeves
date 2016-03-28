from . WebServer.Config import ServerConfig
import mimetypes
# We use OS to check if files exist
import os


class JeevesResponse:
    def __init__(self, request):
        self.request = request
        self.response_body = self.get_requested_resource(ServerConfig.SERVER_ROOT + request.location)
        self.content_type = self.get_content_type(ServerConfig.SERVER_ROOT + request.location)

    def get_requested_resource(self, resource_path):
        """LOADS FILES AND MANAGES THE STATUS"""
        try:
            resource = self.load_file_bytes(resource_path)
            self.status = "200 OK"
            return resource
        except FileNotFoundError:
            self.status = "404 Not Found"
            return self.load_file_bytes(ServerConfig.SERVER_ROOT + "/404.html")
    
    def load_file_bytes(self, file):
        with open(file, 'rb') as f:
            contents = f.readlines()
            file_string = b''.join(contents)
            return file_string

    def get_content_type(self, file_path):
        if not os.path.isfile(file_path):
            # We are going to serve the 404
            mime = "text/html"
        mime = mimetypes.guess_type(file_path)[0]
        if mime is None:
            # We could not determine the MIME so default to text
            mime = "text/plain"
        return mime

    def complete_binary_response(self):
        complete_response_string = b""
        complete_response_string += bytes(self.request.protocol + " ", "utf-8")
        complete_response_string += bytes(self.status, "utf-8")
        complete_response_string += bytes("\n" + "Content-type:" + self.content_type, "utf-8")
        complete_response_string += bytes("\n\n", "utf-8")
        complete_response_string += self.response_body
        return complete_response_string