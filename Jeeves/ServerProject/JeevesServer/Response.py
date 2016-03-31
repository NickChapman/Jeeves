# We use mimetypes to determine the content type to send back
import mimetypes
# We use OS to check if files exist
import os
# Subprocess is used to run a page
import subprocess
# String and random are used for token generation
import string
import random
# We use pickle to pass the headers to the pages
import pickle

from . WebServer.Config import ServerConfig

class JeevesResponse:
    def __init__(self, request):
        self.request = request
        self.response_body = self.get_requested_resource(ServerConfig.SERVER_ROOT + request.location)
        self.content_type = self.get_content_type(ServerConfig.SERVER_ROOT + request.location)

    def get_requested_resource(self, file_path):
        """Determines which type of resource is being loaded and attempts to procure it
        Does minimal status handling but allows special
        resource managers to set the status at a lower level
        @param file_path: The path to the resource to load whether it's a file or directory
        """
        if not (os.path.exists(file_path) or os.path.lexists(file_path)):
            return self.load_404()
        elif os.path.isfile(file_path):
            self.status = None
            resource = self.load_file_bytes(file_path)
            if self.status is None:
                # If something happens elsewhere then the status will be handled there.
                # Otherwise everything was fine so we set it to ok here
                self.status = "200 OK"
            return resource
        elif os.path.isdir(file_path):
            return self.load_directory(file_path)
        else:
            # A strange error has occurred so we'll send a 500
            return self.load_500()
    def load_file_bytes(self, file):
        file_name, file_extension = os.path.splitext(file)
        if file_extension.lower() == ".pyp":
            return self.parse_jeeves_page(file)
        with open(file, 'rb') as f:
            contents = f.readlines()
            file_string = b''.join(contents)
            return file_string

    def load_403(self, requested_file_path):
        """Loads a 403 forbidden page for the requested resource"""
        self.status = "403 Forbidden"
        return self.parse_jeeves_page(ServerConfig.SERVER_ROOT + "/403.pyp", self.request.location)

    def load_404(self):
        """ Returns a generic 404 page """
        self.status = "404 Not Found"
        return self.load_file_bytes(ServerConfig.SERVER_ROOT + "/404.pyp")

    def load_500(self):
        """ Returns a generic 500 page with no error information """
        return self.load_file_bytes(ServerConfig.SERVER_ROOT + "/500.pyp")

    def load_directory(self, file_path):
        """Attempts to load a directory's index file"""
        # Check first for index.pyp
        if os.path.isfile(file_path + "index.pyp"):
            return self.get_requested_resource(file_path + "index.pyp")
        elif os.path.isfile(file_path + "index.html"):
            return self.get_requested_resource(file_path + "index.html")
        elif ServerConfig.LIST_DIRECTORY_CONTENTS:
            return self.list_directory_contents(file_path)
        else:
            return self.load_403(file_path)

    def list_directory_contents(self, file_path):
        """Returns html with a list of the directory contents as links"""
        files = os.listdir(file_path)
        html = "<h1>" + self.request.location + " contains the following:</h1><ul>\n"
        for file in files:
            html += "<li><a href=\"" + file + "\">" + file + "</a></li>\n"
        html += "</ul>"
        self.status = "200 OK"
        return bytes(html, "utf-8")

    def get_content_type(self, file_path):
        file_name, file_extension = os.path.splitext(file_path)
        if not os.path.isfile(file_path) or self.status == "404 Not Found":
            # We are going to serve the 404
            mime = "text/html"
        elif self.status != "200 OK":
            # Whatever we're returning is an HTML error page
            mime = "text/html"
        elif os.path.isdir(file_path):
            # We're either returning the directory listing or an error
            mime = "text/html"
        elif file_extension.lower() == ".pyp":
            mime = "text/html"
        else:
           mime = mimetypes.guess_type(file_path)[0]
        if mime is None:
            # We could not determine the MIME so default to text
            mime = "text/plain"
        return mime

    def parse_jeeves_page(self, file_path, *additional_args):
        additional_args = list(additional_args)
        with open(file_path, "r") as f:
            file_string = ""
            for line in f.readlines():
                file_string += line
            token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(64))
            if "import RequestHeaders" in file_string:
                file_string = self.pass_request_headers_to_page(file_string, token)
            file_pieces = file_string.split("<?")
            python_parts = []
            html_parts = []
            for piece in file_pieces:
                if "?>" in piece:
                    split_line = piece.split("?>")
                    html_parts.append(split_line[0])
                    python_parts.append("\nprint(\"" + token + "\", end=\"\")\n",)
                    python_parts.append(split_line[1])
                else:
                    python_parts.append(piece)
            python_string = ""
            for part in python_parts:
                python_string += part
            temp = open("./" + token + ".py", "w")
            temp.write(python_string)
            temp.close()
            proc = subprocess.run(["python3", token + ".py"] + additional_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            python_output = proc.stdout.decode('utf-8')
            error = proc.stderr.decode('utf-8')
            self.cleanup(token)
            if error != "":
                if ServerConfig.ERROR_REPORTING:
                    error_reporting_flag = "1"
                    error = error.replace(token + ".py", self.request.location)
                    error = self.fix_error_message_line_number(error, file_path)
                else:
                    error_reporting_flag = "0"
                self.status = "500 Internal Server Error"
                return self.parse_jeeves_page(ServerConfig.SERVER_ROOT + "/500.pyp", error, error_reporting_flag)
            html_counter = 0
            while(token in python_output):
                python_output = python_output.replace(token, html_parts[html_counter], 1)
                html_counter += 1
            return bytes(python_output, 'utf-8')

    def cleanup(self, token):
        """Deletes all of the files while serving this response
        @param token: This response's unique token
        """
        os.remove(token + ".py")
        if os.path.isfile(token + ".headers"):
            os.remove(token + ".headers")

    def pass_request_headers_to_page(self, file_string, token):
        """Alters the file_string so that the request headers are available
        @param file_string: The original file_string
        @param token: This response's unique token
        """
        # Serialize and write the headers to file
        with open(token + ".headers", "wb") as header_file:
            pickle.dump(self.request.headers, header_file)
        import_code = "import pickle\nwith open(\"" + token + ".headers\", \"rb\") as f:\n\tRequestHeaders=pickle.load(f)"
        file_string = file_string.replace("import RequestHeaders", import_code)
        return file_string

    def fix_error_message_line_number(self, error_message, file_path):
        # This could be refactored to use some fancy regex if I knew that
        error_parts = error_message.split(", line ", 1)
        if error_parts[1].find(",") != -1:
            error_code_starts_at = min(error_parts[1].find(" "), error_parts[1].find(","))
        else:
            error_code_starts_at = error_parts[1].find(" ")
        error_code_ends_at = error_parts[1].find("^")
        error_code = error_parts[1][error_code_starts_at:error_code_ends_at]
        # Check for discussion of <module>
        if "module" in error_code:
            error_code = error_code[error_code.find(">") + 1:].strip()
            error_code = error_code[:error_code.find("\r")].strip()
        else:
            error_code = error_code[:error_code.find("\r")].strip()
        false_line_number = int(error_parts[1][:error_code_starts_at])
        real_line_number_for_error = 0
        with open(file_path, "r") as f:
            line_found = False
            files_lines = f.readlines()
            for i, line in enumerate(files_lines):
                if error_code in line and i >= false_line_number:
                    real_line_number_for_error = i + 1
                    line_found = True
                    break
            if not line_found:
                for i, line in enumerate(files_lines):
                    if error_code in line:
                        real_line_number_for_error = i + 1
                        line_found = True
                        break
        error_parts[1] = str(real_line_number_for_error) + error_parts[1][error_code_starts_at:]
        # check for the word "in" because errors without it have wonky formats
        if not ", in" in error_parts[1]:
            error_parts[1] = error_parts[1][:error_parts[1].find(" ")] + "\r\n" + error_parts[1][error_parts[1].find(" ") + 1:]
        error_message = error_parts[0] + ", line " + error_parts[1]
        return error_message

    def complete_binary_response(self):
        complete_response_string = b""
        complete_response_string += bytes(self.request.protocol + " ", "utf-8")
        complete_response_string += bytes(self.status, "utf-8")
        complete_response_string += bytes("\n" + "Content-type:" + self.content_type, "utf-8")
        complete_response_string += bytes("\n\n", "utf-8")
        complete_response_string += self.response_body
        return complete_response_string