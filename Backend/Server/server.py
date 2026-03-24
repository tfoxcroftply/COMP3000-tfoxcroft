from time import sleep
from os.path import dirname, abspath
from asyncio import run, create_task
from time import time

# custom imports
from components.types import Container, DataTypeEnum
from components.database import Database
from components.data_utils import DataUtils
from components.api import Api
from components.node_manager import NodeManager
from components.thresholds import Thresholds
from components.sms import SMS
from components.notifications import Notifications, NotificationType

from components.print import vprint
from components import host_info

testing = True

async def test(container): # change later, probably not reliable
    while not container.api.is_active():
        sleep(1)

async def main():
    vprint("Server starting.")
    container = Container()
    if not host_info.is_host_valid():
        container.config.debug = True
        
    if container.config.debug == True: # separated as the config might have debug mode already enabled
        vprint("Debug mode enabled.")

    container.database = Database(container)
    await container.database.start(dirname(abspath(__file__)))

    container.datautils = DataUtils(container)

    container.notifications = Notifications(container)
    
    container.node_manager = NodeManager(container)
    await container.node_manager.start() # look into reducing startup delay if no devices are connected, maybe move it to the end

    container.thresholds = Thresholds(container) # maybe remove later

    container.sms = SMS(container)
    container.sms.start()

    container.api = Api(container)

    if testing == True:
        create_task(test(container))

    await container.api.start() # blocking, run last

if __name__ == "__main__":
    run(main())