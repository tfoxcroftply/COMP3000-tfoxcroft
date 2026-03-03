# for connecting pi to lora esp32
# managed by node_connection.py

from components.print import vprint
from components.serial import NodeSerial
from components.types import NotificationType

class Bridge:
    def __init__(self, container):
        self.container = container
        self.serial = NodeSerial(container)
        self._started: bool = False

    async def start(self, timeout: int | None = None) -> bool:
        vprint("Bridge module starting.")
        self.serial.start(self.container.config.bridge_port, "tnn") # changed from tnb to tnn

        started = await self.serial.attempt_connect(timeout)
        if started:
            self._started = True
            return True
        
        await self.container.notifications.add("Bridge failed to connect!", NotificationType.ERROR)
        
    def is_connected(self) -> bool:
        return self._started
        
    async def _check_status(self) -> bool:
        if not (self._started and self.serial.is_serial_active()):
            self._started = False
            vprint("Bridge command failed. Bridge is disconnected.", error=True)
            vprint("Attempting to reconnect to bridge.")
            started = await self.start(5)
            if started:
                return True
            return False
        return True
        