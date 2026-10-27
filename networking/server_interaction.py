from . import client
from . import server

#receives a response
def send_register(usr: str, passwd: str):
    if not usr or not passwd:
        return "ERROR:USERNAME_OR_PASS_EMPTY"

    command = f"REGISTER:{usr}:{passwd}"
    response = client.send_command(command)
    return response
#receives a response
def send_login(usr: str, passwd:str):
    if not usr or not passwd:
        return "ERROR:USERNAME_OR_PASS_EMPTY"

    command = f"LOGIN:{usr}:{passwd}"
    response = client.send_command(command)
    return response
