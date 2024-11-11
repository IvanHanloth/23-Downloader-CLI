import typer
import sys
from typing_extensions import Annotated
from rich import print
from rich.progress import Progress
from utils.config import Config
from utils.console import Console
from utils.download import Downloader
from urllib import parse
import random

sys.argv = ["main.py", "download","-u", "https://app.send.hanloth.cn/download/PC/one/one.zip"]
app = typer.Typer()

@app.command("")
def version():
    """
    Show the version of the Application
    """
    print("Downloader CLI version: v0.1.0")
    
class DownloadInterface:
    def __init__(self,noStyle:bool):
        
        self.console=Console(noStyle)
        self.progress=Progress()
        self.progresses={}
        self.tasks=[]

    def download(self,urls:list,output:str,noConfig:bool):
        """
        Download a file from a URL
        """
        self.console.info(f"Downloading {len(urls)} file(s)...")
        # d=Downloader(onProgress=self.ProgressCallback,onError=self.ErrorCallback,onFinish=self.FinishCallback)
        d=Downloader()
        for url in urls:
            id=random.randint(100000,999999)
            filename=parse.urlparse(url).path.split("/")[-1]
            info={
                "id":id,
                "url":url,
                "file_name":filename,
                "directory":output,
                "config":{

                }
            }
            
            self.tasks.append(id)
            self.progresses[id] = self.progress.add_task("[red]Downloading...", total=100)
            
            d.start(info)


    def ErrorCallback(self,data):
        self.console.error("An error occurred while downloading the file.")

    def ProgressCallback(self,data):
        self.progress.update(data["id"], advance=data["progress"])

    def FinishCallback(self,data):
        print(data)
        

@app.command("download")
def download(
        url:Annotated[str, typer.Option("--url","-u",help="The URL to download")] = None,
        output:Annotated[str, typer.Option("--output-dir","-o",help="The output directory")] = None,
        listFile:Annotated[str, typer.Option("--list-file","-lf",help="The txt file path of a set of links, with one link per line.")] = None,
        noConfig:Annotated[bool, typer.Option("--no-config",help="Do not use the global configuration")] = False,
        noStyle:Annotated[bool, typer.Option("--no-style","-n",help="Do not use the beautify to output")] = False,
        ):
    """
    Download a file from a URL
    """
    console=Console(noStyle)
    d=DownloadInterface(noStyle)
    if not noConfig:
        Config.loadConfig()
    
    if (url is None and listFile is None) or (url and listFile):
        console.error("Please enter the URL or provide the list file path of a set of links.")
        return
    
    urls=[]
    if url:
        urls=[url]

    if listFile:
        try:
            with open(listFile,"r") as f:
                urls=f.readlines()
        except Exception:
            console.error("The file path is not correct.")
            return
    
    d.download(urls,output,noConfig)

@app.command("config")
def config():
    """
    Configure the CLI
    """
    print("Config command")
if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "--version":
        typer.run(version)
    else:
        app()
    # app()