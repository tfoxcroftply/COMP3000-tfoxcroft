# was originally handled by node_manager 
# communicates with bridge and receives node lora data

from asyncio import sleep, create_task, CancelledError
from datetime import datetime
from random import uniform

from components.types import ReturnData, DataBlock, NotificationType
from components.bridge import Bridge
from components.print import vprint

class NodeReceiver: # fixed typo
    def __init__(self, container) -> None:
        self.container = container
        self.bridge = Bridge(container) # bridge handles lora
        self._running = False
        self._pending_notify_id: int | None = None

    async def start_wait(self): # instead of running instantly, wait for time to become a multiple of the scan frequency.
        vprint("Scheduling startup of node data receiver loop.")

        message = "The node receiver loop is scheduled to start. Data recording currently inactive."
        notify_data: ReturnData = await self.container.notifications.add(message)
        if notify_data.success and notify_data.data != None:
            self._pending_notify_id = notify_data.data

        while not (datetime.now().minute % self.container.config.lora_scan_frequency == 0 and datetime.now().second == 0): # change later to not check every minute
            current_date = datetime.now()
            seconds_to_wait = 60 - current_date.second - current_date.microsecond / 1000000

            await sleep(seconds_to_wait)

        await self.container.notifications.delete(self._pending_notify_id)

    async def _record_data(self, data: list[DataBlock]) -> bool:
        one_failed = False
        for entry in data:
            found: ReturnData = await self.container.database.read_one("SELECT * FROM nodes WHERE hwid = ?",(entry.node_hwid,))
            if not found.success:
                continue

            if found.data == None:
                vprint("Reading contains data from unrecognised node. Discarding.")
                await self.container.notifications.add(f"Readings were received from an unrecognised node '{entry.node_hwid}'. Ensure it has been paired correctly.", NotificationType.WARN)
                continue

            currentDate = datetime.now()
            currentTime = int(currentDate.timestamp() - currentDate.second) # some readings were reading :01 before
            write: ReturnData = await self.container.database.write("INSERT into readings (timestamp, node_hwid, temp, hum) VALUES (?,?,?,?)", (currentTime, entry.node_hwid, entry.temp, entry.hum,))
            if not write.success:
                one_failed = True
                continue
            
            await self.container.node_manager.update_node_information(entry)
            await self.container.logs.update_log()


        if not one_failed:
            vprint("Recorded collected data successfully.")
            return True
        
        vprint("Error detected when recording data, some data may be missing.", error=True)
        return False

    async def _loop(self) -> None:
        await self.start_wait()

        vprint("Node data receiver loop started.")
        self.bridge.clear_collection()

        try:
            while (True):
                await sleep(self.container.config.lora_scan_frequency * 60) # change later to account for processing time otherwise it will drift

                vprint("Checking bridge module buffer for collected data.")
                collected_data: list[DataBlock] = self.bridge.read_collection()

                if self.container.config.debug and self.container.config.debug_create_reading:
                    nodeList: ReturnData = await self.container.node_manager.get_node_list()
                    if nodeList.success:
                        for node in nodeList.data:
                            if node["debug"] == 1:
                                collected_data.append(DataBlock(datetime.now().timestamp(), round(uniform(20.0, 22.0),2), 60.0, node["hwid"]))

                found_entries = len(collected_data)
                if found_entries > 0:
                    vprint(f"Found {found_entries} packet{"s" if found_entries > 1 else ""}, storing in database.")

                    await self._record_data(collected_data)
                    await self.container.thresholds.calculate_thresholds(collected_data)

                else:
                    vprint("No node data found in bridge buffer. Nothing was recorded.")

        except CancelledError:
            vprint("Exiting LoRa receiver loop.")

    async def start(self) -> None:
        if self._running: 
            vprint("Failed to start data receiver module. Module is already running.", error=True)
            return
        
        vprint("Starting data receiver module.")
        await self.bridge.start()
        create_task(self._loop())