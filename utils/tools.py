import re
import os
import json
import random
import ctypes
import requests
import subprocess
from typing import Optional, Dict, List

from datetime import datetime
from requests.auth import HTTPProxyAuth

from utils.config import Config

def process_shorklink(url: str) -> str:
    req = requests.get(url, headers = get_header(), proxies = get_proxy(), auth = get_auth())
    
    return req.url

def get_header(header:dict={},cookie:dict={}):

    cookie_dict = {

    }

    cookie_dict.update(cookie)

    Default_Header={
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Cookie": ";".join([f"{key}={value}" for key, value in cookie_dict.items()]),
        "Sec-Ch-Ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }

    Default_Header.update(header)

    return Default_Header

def get_proxy():
    match Config.Proxy.proxy_mode:
        case Config.Type.PROXY_DISABLE:
            return {}
        
        case Config.Type.PROXY_FOLLOW:
            return None
        
        case Config.Type.PROXY_MANUAL:
            return {
                "http": f"{Config.Proxy.proxy_ip_addr}:{Config.Proxy.proxy_port}",
                "https": f"{Config.Proxy.proxy_ip_addr}:{Config.Proxy.proxy_port}"
            }

def get_auth():
    if Config.Proxy.auth_enable:
        return HTTPProxyAuth(Config.Proxy.auth_uname, Config.Proxy.auth_passwd)
    else:
        return None

def format_size(size: int):
    if size > 1024 * 1024:
        return "{:.1f} GB".format(size / 1024 / 1024)
    
    elif size > 1024:
        return "{:.1f} MB".format(size / 1024)
    
    else:
        return "{:.1f} KB".format(size)

def remove_files(path: str, name: List):
    for i in name:
        file_path = os.path.join(path, i)
        
        if os.path.exists(file_path):
            match Config.Sys.platform:
                case "windows":
                    ctypes.windll.kernel32.SetFileAttributesW(file_path, 128)
                    ctypes.windll.kernel32.DeleteFileW(file_path)

                case "linux" | "darwin":
                    os.remove(file_path)

# def check_update():
#     url = "https://api.scott-sloan.cn/Bili23-Downloader/getLatestVersion"

#     req = requests.get(url, headers = get_header(), proxies = get_proxy(), auth = get_auth(), timeout = 5)
#     req.encoding = "utf-8"

#     update_json = json.loads(req.text)

#     Config.Temp.update_json = update_json

def find_str(pattern: str, string: str):
    find = re.findall(pattern, string)
    
    if find:
        return find[0]
    else:
        return None

def get_cmd_output(cmd: str):
    # 获取命令输出
    process = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, text = True)

    return process.stdout

def get_current_time():
    return datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S")

def save_log(return_code: int, output: str):
    with open("error.log", "w", encoding = "utf-8") as f:
        f.write(f"时间：{get_current_time()} 返回值：{return_code}\n错误信息：\n{output}")

# def get_background_color():
#     if Config.Sys.dark_mode:
#         return wx.Colour(30, 30, 30)
#     else:
#         return "white"