import os
import time
import requests
from requests.adapters import HTTPAdapter
from typing import Optional

from utils.config import Config
from utils.tools import get_header, get_proxy, get_auth, format_size
from utils.thread import Thread, ThreadPool

class Downloader:
    def __init__(self, info):
        self.info = info

        self.init_utils()

    def init_utils(self):
        # 初始化变量
        self.total_size = 0
        self.completed_size = 0

        # 创建监听线程
        self.listen_thread = Thread(target = self.onListen, name = "ListenThread")

        # 创建持久化 Session
        self.session = requests.Session()

        # 出错重连机制
        self.session.mount("http://", HTTPAdapter(max_retries = 5))
        self.session.mount("https://", HTTPAdapter(max_retries = 5))
        
        self.ThreadPool = ThreadPool()

        # 初始化停止标志位，包含监听线程停止标志位和分片下载停止标志位
        self.stop_flag = False
        self.range_stop_flag = False
        self.finish_flag = False

        self.thread_info = {}
        self.thread_alive_count = 0
        
    def add_url(self, info: dict):
        path = os.path.join(Config.Download.path, info["file_name"])

        self.total_size = self.get_total_size(info["url"], info["referer_url"], path)
        
        # 音频文件较小，使用 2 线程下载
        chunk_list = self.get_chunk_list(self.total_size, Config.Download.max_thread_count)
        self.thread_alive_count += len(chunk_list)

        for index, chunk_list in enumerate(chunk_list):
            url, referer_url, temp = info["url"], info["referer_url"], info.copy()

            thread_id = f"{info['type']}_{info['id']}_{index + 1}"
            temp["chunk_list"] = chunk_list
            self.thread_info[thread_id] = temp

            self.download_id = info["id"]
            
            self.ThreadPool.submit(self.range_download, args = (thread_id, url, referer_url, path, chunk_list,))

    def start(self, info: dict):
        # 添加下载链接
        self.add_url(info)

        # 开启线程池和监听线程
        self.ThreadPool.start()
        self.listen_thread.start()

    def restart(self):
        # 重置停止线程标志位
        self.stop_flag = False
        self.range_stop_flag = False

        for key, entry in self.thread_info.items():
            path, chunk_list = os.path.join(Config.Download.path, entry["file_name"]), entry["chunk_list"]

            if chunk_list[0] >= chunk_list[1]:
                continue

            self.ThreadPool.submit(target = self.range_download, args = (key, self.info["url"], entry["referer_url"], path, chunk_list,))
            self.thread_alive_count += 1
        
        self.ThreadPool.start()

    def range_download(self, thread_id: str, url: str, referer_url: str, path: str, chunk_list: list):
        # 分片下载
        req = self.session.get(url, headers = get_header(referer_url, Config.User.sessdata, chunk_list), stream = True, proxies = get_proxy(), auth = get_auth(), timeout = 15)
        
        with open(path, "rb+") as f:
            start_time = time.time()
            chunk_size = 8192
            speed_limit = Config.Download.speed_limit_in_mb * 1024 * 1024
            f.seek(chunk_list[0])

            for chunk in req.iter_content(chunk_size = chunk_size):
                if chunk:
                    if self.range_stop_flag:
                        # 检测分片下载停止标志位
                        break

                    f.write(chunk)
                    f.flush()

                    self.completed_size += len(chunk)

                    self.thread_info[thread_id]["chunk_list"][0] += len(chunk)

                    if self.completed_size >= self.total_size:
                        # 下载完成，置停止分片下载标志位为 True，下载完成标志位为 True
                        self.range_stop_flag = True
                        self.finish_flag = True

                    # 计算执行时间
                    elapsed_time = time.time() - start_time
                    expected_time = chunk_size / (speed_limit / self.thread_alive_count)

                    if elapsed_time < 1 and Config.Download.speed_limit:
                        # 计算应暂停的时间，从而限制下载速度
                        time.sleep(max(0, expected_time - elapsed_time))

                    start_time = time.time()

        self.thread_alive_count -= 1

    def onListen(self):
        # 监听线程，负责监听下载进度
        while not self.stop_flag:
            temp_size = self.completed_size

            time.sleep(1)
            
            # 记录下载信息
            speed = self.format_speed((self.completed_size - temp_size) / 1024)

            info = {
                "progress": int(self.completed_size / self.total_size * 100),
                "speed": speed,
                "size": "{}/{}".format(format_size(self.completed_size / 1024), format_size(self.total_size / 1024)),
                "complete": format_size(self.completed_size / 1024),
                "raw_completed_size": self.completed_size
            }

            if self.stop_flag:
                # 检测停止标志位
                break

            if self.finish_flag:
                # 检测下载完成标志位
                self.stop_flag = True
                self.onFinished()
                break

    def onPause(self):
        # 暂停下载
        self.onStop()

    def onResume(self):
        # 恢复下载
        self.restart()

        # 启动监听线程
        self.listen_thread = Thread(target = self.onListen, name = "ListenThread")
        self.listen_thread.start()

    def onStop(self):
        # 停止下载
        self.range_stop_flag = True
        self.stop_flag = True

        self.ThreadPool.stop()
        self.session.close()

    def onFinished(self):
        # 下载完成，关闭所有线程
        self.stop_flag = True
    
    def get_total_size(self, url: str, referer_url: str, path: Optional[str] = None):
        req = self.session.head(url, headers = get_header(referer_url))

        total_size = int(req.headers["Content-Length"])

        # 当 path 不为空时，才创建本地空文件
        if path:
            with open(path, "wb") as f:
                # 使用 seek 方法，移动文件指针，快速有效，完美解决大文件创建耗时的问题
                f.seek(total_size - 1)
                f.write(b"\0")
        
        return total_size

    def get_chunk_list(self, total_size: int, thread_count: int) -> list:
        # 计算分片下载区间
        piece_size = int(total_size / thread_count)
        chunk_list = []

        for i in range(thread_count):
            start = i * piece_size + 1 if i != 0 else 0 
            end = (i + 1) * piece_size if i != thread_count - 1 else total_size

            chunk_list.append([start, end])

        return chunk_list

    def format_speed(self, speed: int) -> str:
        return "{:.1f} MB/s".format(speed / 1024) if speed > 1024 else "{:.1f} KB/s".format(speed) if speed > 0 else "0 KB/s"