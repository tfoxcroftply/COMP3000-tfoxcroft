# was originally handled by node_manager 
# communicates with bridge and recieves node lora data

from asyncio import sleep, create_task, CancelledError
from components.bridge import Bridge
from components.print import vprint

class NodeReceiver: # fixed typo
    def __init__(self, container) -> None:
        self.container = container
        self.bridge = Bridge(container) # bridge handles lora
        self._running = False

    async def _loop(self) -> None:
        try:
            while (True): # no need for stop logic yet
                await sleep(self.container.config.lora_scan_frequency * 60)
        except CancelledError:
            vprint("Exiting LoRa reciever loop.")

    async def start(self) -> None:
        if self._running: 
            vprint("Failed to start data receiver module. Module is already running.", error=True)
            return
        
        vprint("Starting data receiver module.")
        await self.bridge.start()
        create_task(self._loop())

