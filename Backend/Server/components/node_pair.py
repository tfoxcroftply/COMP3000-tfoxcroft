# handled by node_manager
# pairing sequence and websocket

import websockets
from asyncio import create_task, sleep, CancelledError
from time import time

from components.serial import NodeSerial
from components.print import vprint
from components.types import ReturnData

class NodePair:
    def __init__(self, container):
        self.container = container
        self._websocket_active: bool = False
        self._websocket = None
        self._pairing_active: bool = False # needs a check because multiple instances of the websocket handler can spawn
        self._serial_module = NodeSerial(container)
        self._serial_module.start("COM3", "tnn")
        self._last_activity: int = -1

    async def _pairing_sequence(self, websocket):
        # while true do print stuff from serial module command list
        if self._pairing_active: 
            await websocket.close()
            return

        try:
            await websocket.send("Connecting to serial.")

            self._pairing_active = True
            data: bool = self._serial_module.open_serial()
            if not data:
                await websocket.send("Error when opening serial.")
                vprint("Unable to start pairing sequence. Serial open command failed.", error=True)
                return
        
            success = await self._serial_module.attempt_connect()
            if not success:
                await websocket.send("Unable to start pairing sequence. No node detected.")
                vprint("Unable to start pairing sequence. No node detected.", error=True)
                return
            
            await websocket.send("Node connected successfully.")
            vprint("Node connected successfully.")
        except websockets.ConnectionClosed:
            vprint("Websocket closed by command.")
        except Exception as e:
            vprint(f"Websocket error. '{e}'", error=True)
        finally:
            self._pairing_active = False
            await websocket.close()

    def is_active(self) -> bool:
        return self._websocket_active

    async def connect(self) -> bool:
        if self._websocket_active or self._serial_module.is_serial_active():
            vprint("Websocket failed to open. Websocket or serial is already active and pending closure.", error=True)
            return
        
        try:        
            self._websocket_active = True
        
            self._serial_module.message_list = []
            self._last_activity = time()

            self._websocket = await websockets.serve(handler=self._pairing_sequence, host="127.0.0.1", port=self.container.config.websocket_port, origins=["http://localhost:5173"])
            vprint("Websocket listening.")

            try:
                while time() - self._last_activity < self.container.config.websocket_timeout:
                    await sleep(1)
                vprint("Websocket timed out.")
            except CancelledError:
                vprint("Websocket terminated due to request.")
            finally:
                vprint("Websocket closing.")
                self._websocket.close()

        finally:
            self._websocket_active = False

        return
    
