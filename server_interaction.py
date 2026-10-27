from networking import client
from networking import server

def send_register(usr: str, passwd: str):
    if not usr or not passwd:
        return "ERROR:USERNAME_OR_PASS_EMPTY"

    command = f"REGISTER:{usr}:{passwd}"
    client.send_command(command)
def send_login(usr: str, passwd:str):
    if not usr or not passwd:
        return "ERROR:USERNAME_OR_PASS_EMPTY"

    command = f"LOGIN:{usr}:{passwd}"
    client.send_command(command)
