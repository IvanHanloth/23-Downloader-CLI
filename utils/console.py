from rich import print
from rich.panel import Panel

class Console:
    def __init__(self,ifNoStyle:bool):
        self.ifNoStyle = ifNoStyle

    def error(self,msg:str):
        if self.ifNoStyle:
            print(f"Error: {msg}")
        else:
            print(Panel.fit(msg,title="Error",style="red",title_align="left"))

    def info(self,msg:str):
        if self.ifNoStyle:
            print(f"Info: {msg}")
        else:
            print(Panel.fit(msg,title="Info",style="cyan",title_align="left"))

    def warning(self,msg:str):
        if self.ifNoStyle:
            print(f"Warning: {msg}")
        else:
            print(Panel.fit(msg,title="Warning",style="yellow",title_align="left"))

    def success(self,msg:str):
        if self.ifNoStyle:
            print(f"Success: {msg}")
        else:
            print(Panel.fit(msg,title="Success",style="green",title_align="left"))