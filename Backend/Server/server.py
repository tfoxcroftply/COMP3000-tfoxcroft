import os
import time

# custom imports
from components.container import Container

from components.database import Database
from components.api import Api
from components.node_manager import NodeManager

from components.print import vPrint
from components.host_info import isHostValid,getHostType

debug = True

if __name__ == "__main__":
    vPrint("Server starting.")

    container = Container()
    if isHostValid() == False or debug == True:
        container.config.debug = True
        vPrint("Debug mode enabled.")

    container.database = Database(container)
    container.database.start(os.path.dirname(os.path.abspath(__file__)))
    
    container.api = Api(container)
    container.api.start(80)

    container.node_manager = NodeManager(container)
    container.node_manager.start()

    while True:
        time.sleep(10) # logic loop here