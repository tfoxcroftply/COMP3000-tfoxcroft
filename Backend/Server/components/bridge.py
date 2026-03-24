# for connecting pi to lora esp32
# managed by node_connection.py

from asyncio import sleep, CancelledError, create_task, Task, gather
from re import search
from time import time

from components.print import vprint
from components.serial import NodeSerial
from components.types import NotificationType, DataBlock, NodeSerialData

class Bridge:
    def __init__(self, container):
        self.container = container
        self.serial = NodeSerial(container)
        self._started: bool = False
        self._collection: list[DataBlock] = []
        self._current_loop: Task | None = None

    def read_collection(self) -> list[DataBlock]:
        collection = self._collection
        self._collection = []
        return collection
    
    def clear_collection(self) -> None:
        self._collection = []
        return
    
    def _parse_readings(self, hwid: str, input: str) -> DataBlock | None:
        # old bad regex t-?[0-9]+h[0-9]+b[0-9]+
        # t-?(\d+)h(\d+)b(\d+) perhaps replace - with 0 for positive values for fixed payload size

        found = search("t-?(\\d+)h(\\d+)b(\\d+)", input)
        if found is None: return None

        collection = found.groups()
        if len(collection) != 3: return None

        # validate the inputs later

        #print(collection)

        return DataBlock(int(time()), collection[0], collection[1], hwid) # time will probably be ignored
    
    async def _loop(self): # linked to self._started
        try:
            vprint("Starting bridge receiver loop.")
            while True:
                await sleep(self.container.config.bridge_refresh_speed)

                if not self.serial.send_command("tnh:ping:\n"): continue

                data: NodeSerialData = self.serial.receive_command()

                if data is None or not data.command.isdigit(): continue

                parsed_data: DataBlock | None = self._parse_readings(data.command, data.data)
                if not parsed_data: 
                    vprint("Node readings discarded due to invalid data.")
                    continue

                for index, entry in enumerate(self._collection):
                    if entry.node_hwid == parsed_data.node_hwid:
                        vprint("Replacing existing readings in bridge command buffer with newer data.")
                        self._collection[index] = parsed_data
                        break
                else:
                    vprint("Storing node readings in bridge buffer.")
                    self._collection.append(parsed_data)




        except CancelledError:
            vprint("Exiting bridge receiver loop.")

    async def _start_loop(self):
        if self._current_loop is not None:
            vprint("Existing bridge receiver loop found, restarting.")
            self._current_loop.cancel()
            await gather(self._current_loop) # wait for cancel just in case

        self._current_loop = create_task(self._loop())

    async def start(self, timeout: int | None = None) -> bool:
        vprint("Bridge module starting.")

        self.serial.start(self.container.config.bridge_port, "tnn") # changed from tnb to tnn

        for i in range(self.container.config.bridge_start_retries):
            if self.serial.connect():
                await self._start_loop()
                return True
            
            if self.container.config.bridge_disable_retries_in_debug and self.container.config.debug:
                break

            await sleep(1)
        
        await self.container.notifications.add("Bridge failed to connect!", NotificationType.ERROR)
        return False
        
    def is_connected(self) -> bool:
        return self.serial.serial.is_open # maybe add a better check inside serial.py
        
    async def _check_status(self) -> bool:
        if not (self._started and self.serial.is_serial_active()):
            self._started = False
            vprint("Bridge command failed. Bridge is disconnected.", error=True)
            vprint("Attempting to reconnect to bridge.")

            self._started = await self.start(5)
            if self._started:
                create_task(self._loop())
            #return False
        return True
        