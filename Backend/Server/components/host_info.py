import os
from components.print import vPrint

def getHostType() -> str:
    Filename = "/proc/device-tree/model"
    if os.path.exists(Filename):
        try:
            with open(Filename) as f:
                model = f.read().strip()
            return model
        except Exception:
            vPrint("Unable to identify host type.")
    return "Unknown"

def isHostValid() -> bool:
    if getHostType() != "Unknown":
        return True
    return False