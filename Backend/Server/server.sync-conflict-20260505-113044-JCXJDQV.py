from os.path import dirname, abspath
from asyncio import run, create_task, to_thread, sleep, get_running_loop
from time import time

# custom imports
from components.types import Container, DataTypeEnum
from components.database import Database
from components.data_utils import DataUtils
from components.api import Api
from components.node_manager import NodeManager
from components.thresholds import Thresholds
from components.logs import LogManager
from components.sms import SMS
from components.notifications import Notifications, NotificationType

from components.print import vprint, disable_print
from components.host_utils import is_host

import tests.unit_component.shared as shared

testing = True
testing_unit = True # false unit, true integration

async def main():
    vprint("Server starting.")
    container = Container()

    if testing:
        disable_print()

    async def run_tests(container): # change later, probably not reliable
        while not container.api.is_active():
            await sleep(0.1)

        await sleep(1)

        container.loop = get_running_loop()
        shared.container = container

        import pytest
        await to_thread(pytest.main,["tests/unit_component" if testing_unit else "tests/integration", "-s", "-v", "--tb=no"]) # -s for printing

    if not is_host():
        container.config.debug = True
        
    if container.config.debug == True: # separated as the config might have debug mode already enabled
        vprint("Debug mode enabled.")

    container.database = Database(container)
    await container.database.start(dirname(abspath(__file__)))

    container.data_utils = DataUtils(container)

    container.logs = LogManager(container)

    container.thresholds = Thresholds(container)

    container.notifications = Notifications(container)
    
    container.node_manager = NodeManager(container)
    await container.node_manager.start() # look into reducing startup delay if no devices are connected, maybe move it to the end

    container.sms = SMS(container)
    await container.sms.start()

    container.api = Api(container)
    api = create_task(container.api.start()) # blocking, run last

    if testing:
        create_task(run_tests(container))

    await api

  


if __name__ == "__main__":
    run(main())