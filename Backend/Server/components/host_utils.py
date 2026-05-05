# useful tools for the raspberry pi gateway

from os import path
from subprocess import run
from datetime import datetime

from components.print import vprint
from components.types import ReturnData

def get_host_type() -> str | None:
    path_name = "/proc/device-tree/model"
    if path.exists(path_name):
        try:
            with open(path_name) as f:
                model = f.read().strip()
            return model
        except Exception:
            vprint(f"Unable to identify host hardware.", error=True)
    return None

def is_host() -> bool:
    return get_host_type() is not None

def set_system_time(timestamp: int) -> ReturnData:
    # add validation
    if not is_host(): 
        vprint("Cannot restart system as it is running in a development environment.")
        return ReturnData()

    #timestamp = datetime.fromtimestamp(timestamp)
    time_result = run(["sudo", "timedatectl", "set-time", str(datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"))], check=True) # program has special permission for timedatectl
    if time_result.returncode != 0:
        vprint("Failed to set system time.")
        return ReturnData("Failed to set system time.")
    
    #restart_result = run(["sudo", "restart", "now"], check=True)
    #if restart_result.returncode != 0:
        #vprint("Failed to restart system.")
        #return ReturnData("Failed to restart system. Please restart manually.")
    
    return ReturnData(success=True)
