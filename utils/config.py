import os
import platform
import json

class GlobalConfig:
    def __init__(self):
        self.loadDefaulConfig()
        self.loadConfig()

    def loadConfig(self):
        if os.path.exists("config.json"):
            with open("config.json","r") as f:
                data = json.load(f)
                self.download = data["download"]
                self.temp = data["temp"]
                self.proxy = data["proxy"]
                self.sys = data["sys"]
        else:
            self.loadDefaulConfig()
            self.saveConfig()

    def saveConfig(self):
        data = {
            "download": self.download,
            "temp": self.temp,
            "proxy": self.proxy,
            "sys": self.sys
        }
        with open("config.json","w") as f:
            json.dump(data,f,indent=4)

    def loadDefaulConfig(self):
        self.appInfo={
            "name": "23 Downloader CLI",
            "version": "0.1.0",
            "version_code": 10,
            "release_date": "2024/10/21"
        }
        self.sys={
            "platform": platform.system().lower(),
            "dark_mode": False
        }
        self.download={
            "path": "",
            "max_thread_count": 2,
            "max_download_count": 1,
            "add_number": True,
            "speed_limit": False,
            "speed_limit_in_mb": 10
        }
        self.temp={
            "download_window_pos": None,
            "update_json": None
        }
        self.settings={
            "no_style": False
        }
        self.proxy={
            "proxy_mode": 1,
            "auth_enable": False,
            "proxy_ip_addr": "",
            "proxy_port": 0,
            "auth_uname": "",
            "auth_passwd": ""
        }

    def resetConfig(self):
        self.loadDefaulConfig()
        self.saveConfig()
    
Config=GlobalConfig()