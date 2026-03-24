# was originally handled by node_manager 
# communicates with bridge and recieves node lora data

from asyncio import sleep, create_task, CancelledError
from datetime import datetime

from components.types import ReturnData, DataBlock
from components.bridge import Bridge
from components.print import vprint

class NodeReceiver: # fixed typo
    def __init__(self, container) -> None:
        self.container = container
        self.bridge = Bridge(container) # bridge handles lora
        self._running = False

    async def start_wait(self): # instead of running instantly, wait for time to become a multiple of the scan frequency.
        vprint("Scheduling startup of node data receiver loop.")

        message = "The node receiver loop is scheduled to start. Data recording currently inactive."
        await self.container.notifications.add(message)

        while not (datetime.now().minute % self.container.config.lora_scan_frequency == 0 and datetime.now().second == 0): # change later to not check every minute
            current_date = datetime.now()
            seconds_to_wait = 60 - current_date.second - current_date.microsecond / 1000000

            await sleep(seconds_to_wait)

        await self.container.notifications.delete_by_string(message)

    async def record_data(self, data: list[DataBlock]) -> bool:
        one_failed = False
        for entry in data:
            write: ReturnData = await self.container.database.write("INSERT into readings (timestamp, node_hwid, temp, hum) VALUES (?,?,?,?)", (int(datetime.now().timestamp()), entry.node_hwid, entry.temperature, entry.humidity,))
            if not write.success:
                one_failed = True

        if not one_failed:
            vprint("Recorded collected data successfully.")
            return True
        
        vprint("Error detected when recording data, some data may be missing.", error=True)
        return False

    # id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER NOT NULL, node_hwid INTEGER NOT NULL, temp REAL, hum REAL,
    async def _loop(self) -> None:
        await self.start_wait()

        vprint("Node data receiver loop started.")
        self.bridge.clear_collection()

        if self.container.config.debug and self.container.config.debug_create_readings:
            for i in range(3):
                self.bridge._collection.append(DataBlock(datetime.now().timestamp(), 10.0 * i, 20.0, 11111111))

        try:
            while (True):
                await sleep(self.container.config.lora_scan_frequency * 60) # change later to account for processing time otherwise it will drift

                vprint("Checking bridge module buffer for collected data.")
                collected_data: list[DataBlock] = self.bridge.read_collection()

                found_entries = len(collected_data)
                if found_entries > 0:
                    vprint(f"Found {found_entries} packet{"s" if found_entries > 1 else ""}, storing in database.")

                    await self.record_data(collected_data)

                else:
                    vprint("No node data found in bridge buffer. Nothing was recorded.")

        except CancelledError:
            vprint("Exiting LoRa reciever loop.")

    async def start(self) -> None:
        if self._running: 
            vprint("Failed to start data receiver module. Module is already running.", error=True)
            return
        
        vprint("Starting data receiver module.")
        await self.bridge.start()
        create_task(self._loop())

