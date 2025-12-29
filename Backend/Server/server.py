import os
import time

# custom imports
from components.print import vPrint
from components.host_info import isHostValid,getHostType
from components.database import Database
from components.api import Api

debug = True

if __name__ == "__main__":
    vPrint("Server starting.")

    if not isHostValid() or debug == True:
        Debug = True
        vPrint("Development environment detected.")

    database = Database()
    database.start(os.path.dirname(os.path.abspath(__file__)))
    
    api = Api(database) # move to a dependency injection object
    api.start(80)

    while True:
        time.sleep(10) # logic loop

