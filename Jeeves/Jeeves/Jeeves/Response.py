from . WebServer.Config import ServerConfig
import mimetypes
# We use OS to check if files exist
import os
# These next parts are for parsing a .p page
import subprocess
import string
import random


class JeevesResponse:
    def __init__(self, request):
        self.request = request
        self.response_body = self.get_requested_resource(ServerConfig.SERVER_ROOT + request.location)
        self.content_type = self.get_content_type(ServerConfig.SERVER_ROOT + request.location)

    def get_requested_resource(self, resource_path):
        """LOADS FILES AND MANAGES THE STATUS"""
        try:
            self.status = None
            resource = self.load_file_bytes(resource_path)
            if self.status is None:
                # If something happens elsewhere then the status will be handled there.
                # Otherwise everything was fine so we set it to ok here
                self.status = "200 OK"
            return resource
        except FileNotFoundError:
            self.status = "404 Not Found"
            return self.load_file_bytes(ServerConfig.SERVER_ROOT + "/404.html")
    
    def load_file_bytes(self, file):
        file_nanme, file_extension = os.path.splitext(file)
        if file_extension.lower() == ".p":
            return self.parse_jeeves_page(file)
        with open(file, 'rb') as f:
            contents = f.readlines()
            file_string = b''.join(contents)
            return file_string

    def get_content_type(self, file_path):
        file_name, file_extension = os.path.splitext(file_path)
        if not os.path.isfile(file_path):
            # We are going to serve the 404
            mime = "text/html"
        elif file_extension.lower() == ".p":
            mime = "text/html"
        else:
           mime = mimetypes.guess_type(file_path)[0]
        if mime is None:
            # We could not determine the MIME so default to text
            mime = "text/plain"
        return mime

    def parse_jeeves_page(self, file_path, additional_args = []):
        with open(file_path, "r") as f:
            file_string = ""
            for line in f.readlines():
                file_string += line
            token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(64))
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
            proc = subprocess.Popen(["python", token + ".py"] + additional_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            python_output = proc.communicate()[0].decode('utf-8')
            error = proc.communicate()[1].decode('utf-8')
            os.remove(token + ".py")
            if error != "":
                if ServerConfig.ERROR_REPORTING:
                    error_reporting_flag = "1"
                    error = error.replace(token + ".py", self.request.location)
                    error = self.fix_error_message_line_number(error, file_path)
                else:
                    error_reporting_flag = "0"
                self.status = "500 Internal Server Error"
                return self.parse_jeeves_page(ServerConfig.SERVER_ROOT + "/python_error.p", [error, error_reporting_flag])
            html_counter = 0
            while(token in python_output):
                python_output = python_output.replace(token, html_parts[html_counter], 1)
                html_counter += 1
            return bytes(python_output, 'utf-8')

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
                if error_code in line and i > false_line_number:
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