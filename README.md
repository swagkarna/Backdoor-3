# Backdoor
This is an advanced backdoor, created with python.

## Types of Commands:

  - Downloading / Uploading files.

  - Launching / Deleting / Reading file's content.

  - Send messages.

  - Get a Snap from the Webcam / Screenshot.

  - Get UserID + Processes running.

  - Removing / Adding to Startup.

  - Get user information: **Chrome Saved Passwords, System Specs, Public-IP**. 

  - Disable / Enable Task Manager.

  - Lock / Restart / Shutdown the System.

  - Trolling the user by playing music + showing messages.

---

## SFX Folder
This folder contains sfx's that are used **Only when activating trolling option**, if you don't plan to use it, you can delete the folder.

---

## Spyware
The spyware get's all the **Passwords Saved in Chrome** and the system details like: RAM, Processor, Type of machine, Public-IP, and using the report method
it returns all of this data.
With a little bit of knowledge you can make the spyware to send this data via EMAIL, and because this spyware is undetectable, you can find out a lot of Information about someone with this script. (Don't do that if the person doesn't know, because... ILLEGAL => [Hacking Crimes](https://www.pandasecurity.com/en/mediacenter/panda-security/types-of-cybercrime/)).

![image](https://user-images.githubusercontent.com/44588965/131255946-0ae5dfea-592f-43f5-a383-fafd5938ecf8.png)

---

## Usage
To use the backdoor, first go to the server.py script, and change the IP given to your **Private-IP** and you are good to go. Now you have a couple of options:

1) If the person you want to open this backdoor is within your local network the put your **Private-IP** in backdoor.py.
2) If they are outside your local network, you need to put your **Public-IP** and then go to **Outside Local Network** and read more.
3) The ports given in server.py and backdoor.py should match.
4) If you want to you can convert this backdoor to be executable using pyinstaller.

Now you should be good to go.
Start server.py and wait for the victim to open backdoor.py, when they launch it, you should get a connection.

---

## Outside Local Netork
To make sure that everything works, you will need to add one more setting.
In order to allow people outside you local network to connect to you, you need to enable IP-Forwarding in your router settings and forward your Public-IP to your Private-IP.
[See more data about IP Forwarding.](https://en.wikipedia.org/wiki/IP_routing)
